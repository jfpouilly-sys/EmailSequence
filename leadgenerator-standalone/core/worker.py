"""Background worker for email processing in Lead Generator Standalone."""

import logging
import threading
import time
from datetime import datetime
from typing import Callable, Optional, Dict, Any, List

from core.database import get_db, get_setting
from core.models import QueuedEmail, Campaign
from core.exceptions import WorkerError
from services.email_service import EmailService
from services.template_service import TemplateService
from services.suppression_service import SuppressionService
from outlook.outlook_service import OutlookService
from outlook.reply_detector import ReplyDetector
from outlook.unsub_detector import UnsubscribeDetector

logger = logging.getLogger(__name__)


class EmailWorker:
    """Background worker for processing email queue and scanning for replies."""

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or {}
        self.db = get_db()
        self.email_service = EmailService()
        self.template_service = TemplateService()
        self.suppression_service = SuppressionService()

        # Outlook services
        self.outlook_service = OutlookService()
        self.reply_detector = ReplyDetector(self.outlook_service)
        self.unsub_detector = UnsubscribeDetector(self.outlook_service)

        # Worker state
        self._running = False
        self._paused = False
        self._thread: Optional[threading.Thread] = None
        self._lock = threading.Lock()

        # Callbacks for UI updates
        self.on_email_sent: Optional[Callable[[int, int], None]] = None
        self.on_reply_detected: Optional[Callable[[int, int], None]] = None
        self.on_unsubscribe_detected: Optional[Callable[[str], None]] = None
        self.on_error: Optional[Callable[[str], None]] = None
        self.on_status_changed: Optional[Callable[[str], None]] = None

        # Configuration
        self._scan_interval = int(get_setting('outlook_scan_interval_seconds', 60))
        self._batch_size = 10  # Emails to process per cycle

    def start(self) -> bool:
        """Start the background worker thread."""
        if self._running:
            logger.warning("Worker already running")
            return True

        # Initialize Outlook
        if not self.outlook_service.initialize():
            logger.warning("Outlook not available - worker will run without sending")

        self._running = True
        self._paused = False
        self._thread = threading.Thread(target=self._main_loop, daemon=True)
        self._thread.start()

        logger.info("Email worker started")
        self._notify_status("Running")
        return True

    def stop(self) -> None:
        """Stop the background worker."""
        self._running = False
        if self._thread and self._thread.is_alive():
            self._thread.join(timeout=5)

        self.outlook_service.cleanup()
        logger.info("Email worker stopped")
        self._notify_status("Stopped")

    def pause(self) -> None:
        """Pause the worker (stop processing but keep thread alive)."""
        self._paused = True
        logger.info("Email worker paused")
        self._notify_status("Paused")

    def resume(self) -> None:
        """Resume a paused worker."""
        self._paused = False
        logger.info("Email worker resumed")
        self._notify_status("Running")

    def is_running(self) -> bool:
        """Check if worker is running."""
        return self._running and not self._paused

    def get_status(self) -> Dict[str, Any]:
        """Get current worker status."""
        return {
            'running': self._running,
            'paused': self._paused,
            'outlook_available': self.outlook_service.is_outlook_running(),
            'queue_stats': self.email_service.get_queue_stats()
        }

    def _main_loop(self) -> None:
        """Main worker loop."""
        last_scan_time = datetime.min
        cycle_count = 0

        while self._running:
            try:
                if self._paused:
                    time.sleep(1)
                    continue

                cycle_count += 1

                # Process email queue
                self._process_queue()

                # Scan for replies and unsubscribes periodically
                now = datetime.now()
                if (now - last_scan_time).total_seconds() >= self._scan_interval:
                    self._scan_inbox()
                    last_scan_time = now

                # Sleep between cycles
                time.sleep(5)

            except Exception as e:
                logger.error(f"Worker error: {e}")
                self._notify_error(str(e))
                time.sleep(10)  # Wait longer on error

    def _process_queue(self) -> None:
        """Process pending emails from the queue."""
        if not self.outlook_service.is_outlook_running():
            return

        # Get pending emails
        pending_emails = self.email_service.get_pending_emails(limit=self._batch_size)

        for queued_email in pending_emails:
            if not self._running or self._paused:
                break

            try:
                self._send_email(queued_email)
            except Exception as e:
                logger.error(f"Error sending email {queued_email.queue_id}: {e}")
                self.email_service.mark_email_failed(queued_email.queue_id, str(e))
                self._notify_error(f"Failed to send email: {e}")

    def _send_email(self, queued_email: QueuedEmail) -> None:
        """Send a single email from the queue."""
        # Check if should be sent (suppression, contact status, etc.)
        if not self.email_service.process_queue_item(queued_email):
            return

        # Check campaign sending window
        if not self._is_within_sending_window(queued_email.campaign):
            logger.debug(f"Outside sending window for campaign {queued_email.campaign_id}")
            return

        # Mark as sending
        self.email_service.mark_email_sending(queued_email.queue_id)

        # Prepare email content
        contact = queued_email.contact
        step = queued_email.step
        campaign = queued_email.campaign

        if not contact or not step:
            self.email_service.mark_email_failed(queued_email.queue_id, "Missing contact or step data")
            return

        # Apply merge tags
        subject = self.template_service.apply_merge_tags(step.subject_template, contact, campaign)
        body = self.template_service.apply_merge_tags(step.body_template, contact, campaign)

        # Get attachments
        attachments = []
        step_with_attachments = self.template_service.get_step(step.step_id)
        if step_with_attachments:
            attachments = [a.file_path for a in step_with_attachments.attachments]

        # Send email via Outlook
        entry_id = self.outlook_service.send_email(
            to=contact.email,
            subject=subject,
            body=body,
            attachments=attachments if attachments else None
        )

        # Mark as sent
        self.email_service.mark_email_sent(queued_email.queue_id, entry_id)

        # Schedule next step
        self.email_service.schedule_next_step(queued_email.campaign_id, queued_email.contact_id)

        # Notify callback
        if self.on_email_sent:
            self.on_email_sent(queued_email.campaign_id, queued_email.contact_id)

        logger.info(f"Email sent to {contact.email} (campaign {campaign.campaign_ref if campaign else queued_email.campaign_id})")

    def _scan_inbox(self) -> None:
        """Scan inbox for replies and unsubscribes."""
        if not self.outlook_service.is_outlook_running():
            return

        try:
            # Scan for replies
            replies = self.reply_detector.scan_for_replies(since_hours=24)
            for email, contact, campaign_id in replies:
                if self.on_reply_detected:
                    self.on_reply_detected(campaign_id, contact.contact_id)

            # Scan for unsubscribes
            unsubs = self.unsub_detector.scan_for_unsubscribes(since_hours=24)
            for email_address, campaign_id in unsubs:
                if self.on_unsubscribe_detected:
                    self.on_unsubscribe_detected(email_address)

        except Exception as e:
            logger.error(f"Error scanning inbox: {e}")
            self._notify_error(f"Inbox scan error: {e}")

    def _is_within_sending_window(self, campaign: Optional[Campaign]) -> bool:
        """Check if current time is within campaign's sending window."""
        if not campaign:
            return True

        now = datetime.now()

        # Check day of week
        day_abbrev = now.strftime('%a')
        sending_days = campaign.get_sending_days_list()
        if day_abbrev not in sending_days:
            return False

        # Check time window
        try:
            start_hour, start_min = map(int, campaign.sending_window_start.split(':'))
            end_hour, end_min = map(int, campaign.sending_window_end.split(':'))

            current_minutes = now.hour * 60 + now.minute
            start_minutes = start_hour * 60 + start_min
            end_minutes = end_hour * 60 + end_min

            return start_minutes <= current_minutes <= end_minutes
        except (ValueError, AttributeError):
            return True  # Default to sending if window parsing fails

    def _notify_status(self, status: str) -> None:
        """Notify status change via callback."""
        if self.on_status_changed:
            try:
                self.on_status_changed(status)
            except Exception as e:
                logger.warning(f"Status callback error: {e}")

    def _notify_error(self, message: str) -> None:
        """Notify error via callback."""
        if self.on_error:
            try:
                self.on_error(message)
            except Exception as e:
                logger.warning(f"Error callback error: {e}")


# Singleton instance
_worker_instance: Optional[EmailWorker] = None


def get_worker(config: Optional[Dict[str, Any]] = None) -> EmailWorker:
    """Get or create the singleton worker instance."""
    global _worker_instance
    if _worker_instance is None:
        _worker_instance = EmailWorker(config)
    return _worker_instance
