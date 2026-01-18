"""Main orchestrator for email sequences."""
import os
import time
import logging
from datetime import datetime
from typing import Optional

from .config import Config
from .contact_tracker import ContactTracker
from .outlook_manager import OutlookManager
from .template_engine import TemplateEngine


class SequenceEngine:
    """Main orchestrator for email sequences."""

    def __init__(self, config: Config):
        """
        Initialize with config.
        Create instances of ContactTracker, OutlookManager, TemplateEngine.
        Set up logging to config.log_file.

        Args:
            config: Configuration object
        """
        self.config = config

        # Initialize components
        self.tracker = ContactTracker(config.contacts_file)
        self.outlook = OutlookManager()
        self.template_engine = TemplateEngine(config.templates_folder)

        # Set up logging
        self._setup_logging()

    def _setup_logging(self) -> None:
        """Configure logging to file and console."""
        # Create logs directory if needed
        log_dir = os.path.dirname(self.config.log_file)
        if log_dir and not os.path.exists(log_dir):
            os.makedirs(log_dir)

        # Configure logging
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(self.config.log_file),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)

    def start_sequence(self, sequence_id: Optional[str] = None) -> dict:
        """
        Send initial emails to all pending contacts.

        Args:
            sequence_id: Optional ID for this run.
                        Defaults to "seq_YYYYMMDD_HHMMSS"

        Returns:
            {
                "sent": int,
                "failed": int,
                "errors": list[str]
            }
        """
        if sequence_id is None:
            sequence_id = f"seq_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

        self.logger.info(f"Starting sequence: {sequence_id}")

        # Get pending contacts
        pending = self.tracker.get_pending_contacts()

        if len(pending) == 0:
            self.logger.info("No pending contacts found")
            return {"sent": 0, "failed": 0, "errors": []}

        self.logger.info(f"Found {len(pending)} pending contacts")

        sent_count = 0
        failed_count = 0
        errors = []

        for _, contact in pending.iterrows():
            try:
                # Render email template
                html_body = self.template_engine.render(
                    'initial',
                    contact.to_dict(),
                    self.config.sender_name
                )

                # Send email with configured send mode
                result = self.outlook.send_email(
                    to=contact['email'],
                    subject=self.config.default_subject,
                    html_body=html_body,
                    dry_run=self.config.dry_run,
                    send_mode=self.config.default_send_mode,
                    defer_hours=self.config.default_defer_hours,
                    msg_folder=self.config.msg_output_folder
                )

                if result['success']:
                    # Update contact status
                    updates = {
                        'status': 'sent',
                        'sequence_id': sequence_id,
                        'initial_sent_date': result['sent_time'],
                        'last_contact_date': result['sent_time'],
                        'followup_count': 0,
                        'conversation_id': result['conversation_id']
                    }

                    self.tracker.update_contact(contact['email'], updates)

                    sent_count += 1
                    self.logger.info(f"Sent initial email to: {contact['email']}")

                    # Wait between sends (spam prevention)
                    if not self.config.dry_run:
                        time.sleep(self.config.send_delay_seconds)

                else:
                    # Mark as bounced
                    self.tracker.update_contact(
                        contact['email'],
                        {'status': 'bounced'}
                    )

                    failed_count += 1
                    error_msg = f"Failed to send to {contact['email']}: {result['error']}"
                    errors.append(error_msg)
                    self.logger.warning(error_msg)

            except Exception as e:
                failed_count += 1
                error_msg = f"Error sending to {contact['email']}: {str(e)}"
                errors.append(error_msg)
                self.logger.error(error_msg)

        self.logger.info(f"Sequence complete: {sent_count} sent, {failed_count} failed")

        return {
            "sent": sent_count,
            "failed": failed_count,
            "errors": errors
        }

    def check_replies(self) -> dict:
        """
        Scan inbox and update contacts who have replied.

        Returns:
            {
                "replies_found": int,
                "contacts_updated": list[str]  # email addresses
            }
        """
        self.logger.info("Checking for replies...")

        # Get contacts that are in active sequence
        active_statuses = ['sent', 'followup_1', 'followup_2', 'followup_3']
        all_contacts = self.tracker.get_all_contacts()
        active_contacts = all_contacts[all_contacts['status'].isin(active_statuses)]

        if len(active_contacts) == 0:
            self.logger.info("No active contacts to check")
            return {"replies_found": 0, "contacts_updated": []}

        # Get list of email addresses
        contact_emails = active_contacts['email'].tolist()

        # Scan inbox
        replies = self.outlook.get_recent_replies(
            known_contacts=contact_emails,
            days_back=self.config.inbox_scan_days
        )

        contacts_updated = []

        for reply in replies:
            sender_email = reply['sender_email']

            # Get the contact
            contact = self.tracker.get_contact_by_email(sender_email)

            if contact and contact['status'] in active_statuses:
                # Update to replied status
                updates = {
                    'status': 'replied',
                    'replied_date': reply['received_time']
                }

                self.tracker.update_contact(sender_email, updates)
                contacts_updated.append(sender_email)

                self.logger.info(
                    f"Reply detected from: {sender_email} "
                    f"(received: {reply['received_time']})"
                )

        self.logger.info(f"Found {len(contacts_updated)} replies")

        return {
            "replies_found": len(contacts_updated),
            "contacts_updated": contacts_updated
        }

    def send_followups(self) -> dict:
        """
        Send follow-up emails to non-responders.

        Returns:
            {
                "sent": int,
                "failed": int,
                "completed": int,  # Contacts who reached max followups
                "errors": list[str]
            }
        """
        # First, check for replies to ensure status is current
        self.check_replies()

        self.logger.info("Checking for contacts needing follow-up...")

        # Get contacts needing follow-up
        needs_followup = self.tracker.get_contacts_needing_followup(
            self.config.followup_delays
        )

        if len(needs_followup) == 0:
            self.logger.info("No contacts need follow-up at this time")
            return {"sent": 0, "failed": 0, "completed": 0, "errors": []}

        self.logger.info(f"Found {len(needs_followup)} contacts needing follow-up")

        sent_count = 0
        failed_count = 0
        completed_count = 0
        errors = []

        for _, contact in needs_followup.iterrows():
            try:
                # Determine which follow-up to send
                followup_count = int(contact['followup_count']) if contact['followup_count'] else 0
                next_followup = followup_count + 1

                # Check if we've reached max follow-ups
                if next_followup > self.config.max_followups:
                    # Mark as completed
                    self.tracker.update_contact(
                        contact['email'],
                        {'status': 'completed'}
                    )
                    completed_count += 1
                    self.logger.info(
                        f"Contact {contact['email']} reached max follow-ups, "
                        "marking as completed"
                    )
                    continue

                # Determine template name
                template_name = f"followup_{next_followup}"

                # Render email template
                html_body = self.template_engine.render(
                    template_name,
                    contact.to_dict(),
                    self.config.sender_name
                )

                # Send email with SAME subject line to maintain thread
                result = self.outlook.send_email(
                    to=contact['email'],
                    subject=self.config.default_subject,
                    html_body=html_body,
                    dry_run=self.config.dry_run,
                    send_mode=self.config.default_send_mode,
                    defer_hours=self.config.default_defer_hours,
                    msg_folder=self.config.msg_output_folder
                )

                if result['success']:
                    # Determine new status
                    new_status = f"followup_{next_followup}"

                    # Check if this was the last follow-up
                    if next_followup >= self.config.max_followups:
                        new_status = 'completed'
                        completed_count += 1

                    # Update contact
                    updates = {
                        'status': new_status,
                        'last_contact_date': result['sent_time'],
                        'followup_count': next_followup
                    }

                    self.tracker.update_contact(contact['email'], updates)

                    sent_count += 1
                    self.logger.info(
                        f"Sent {template_name} to: {contact['email']}"
                    )

                    # Wait between sends
                    if not self.config.dry_run:
                        time.sleep(self.config.send_delay_seconds)

                else:
                    # Mark as bounced
                    self.tracker.update_contact(
                        contact['email'],
                        {'status': 'bounced'}
                    )

                    failed_count += 1
                    error_msg = f"Failed to send to {contact['email']}: {result['error']}"
                    errors.append(error_msg)
                    self.logger.warning(error_msg)

            except Exception as e:
                failed_count += 1
                error_msg = f"Error sending to {contact['email']}: {str(e)}"
                errors.append(error_msg)
                self.logger.error(error_msg)

        self.logger.info(
            f"Follow-up complete: {sent_count} sent, {failed_count} failed, "
            f"{completed_count} completed"
        )

        return {
            "sent": sent_count,
            "failed": failed_count,
            "completed": completed_count,
            "errors": errors
        }

    def get_status_report(self) -> dict:
        """
        Generate summary of current sequence status.

        Returns:
            {
                "total_contacts": int,
                "by_status": {
                    "pending": int,
                    "sent": int,
                    "followup_1": int,
                    "followup_2": int,
                    "followup_3": int,
                    "replied": int,
                    "bounced": int,
                    "completed": int,
                    "opted_out": int
                },
                "reply_rate": float,
                "sequence_id": str,
                "last_activity": datetime
            }
        """
        all_contacts = self.tracker.get_all_contacts()

        # Count by status
        status_counts = all_contacts['status'].value_counts().to_dict()

        # Initialize all possible statuses
        by_status = {
            'pending': 0,
            'sent': 0,
            'followup_1': 0,
            'followup_2': 0,
            'followup_3': 0,
            'replied': 0,
            'bounced': 0,
            'completed': 0,
            'opted_out': 0
        }

        # Update with actual counts
        for status, count in status_counts.items():
            if status in by_status:
                by_status[status] = count

        # Calculate reply rate
        total_contacted = (
            by_status['sent'] +
            by_status['followup_1'] +
            by_status['followup_2'] +
            by_status['followup_3'] +
            by_status['replied'] +
            by_status['completed']
        )

        if total_contacted > 0:
            reply_rate = by_status['replied'] / total_contacted
        else:
            reply_rate = 0.0

        # Get most recent sequence_id
        sequence_ids = all_contacts['sequence_id'].dropna().unique()
        sequence_id = sequence_ids[-1] if len(sequence_ids) > 0 else None

        # Get last activity date
        date_columns = ['initial_sent_date', 'last_contact_date', 'replied_date']
        all_dates = []
        for col in date_columns:
            dates = all_contacts[col].dropna()
            all_dates.extend(dates.tolist())

        last_activity = max(all_dates) if all_dates else None

        return {
            "total_contacts": len(all_contacts),
            "by_status": by_status,
            "reply_rate": reply_rate,
            "sequence_id": sequence_id,
            "last_activity": last_activity
        }

    def run_full_cycle(self) -> dict:
        """
        Execute complete cycle: check replies → send follow-ups.
        This is what Task Scheduler should call.

        Returns combined results from check_replies() and send_followups().
        """
        self.logger.info("Running full cycle...")

        # Check for replies
        reply_results = self.check_replies()

        # Send follow-ups
        followup_results = self.send_followups()

        # Combine results
        combined = {
            "replies_found": reply_results['replies_found'],
            "contacts_updated": reply_results['contacts_updated'],
            "followups_sent": followup_results['sent'],
            "followups_failed": followup_results['failed'],
            "completed": followup_results['completed'],
            "errors": followup_results['errors']
        }

        self.logger.info("Full cycle complete")

        return combined

    def send_single_email(
        self,
        email: str,
        template_name: str = 'initial',
        send_mode: str = None,
        defer_hours: int = None,
        msg_folder: str = None
    ) -> dict:
        """
        Send a single email to a specific contact with custom options.
        Useful for GUI-based manual sends.

        Args:
            email: Contact email address
            template_name: Template to use ('initial', 'followup_1', etc.)
            send_mode: Override default send mode ('send', 'msg_file', 'defer')
            defer_hours: Override default defer hours
            msg_folder: Override default msg folder

        Returns:
            {
                "success": bool,
                "error": str | None,
                "msg_file_path": str | None
            }
        """
        # Get contact
        contact = self.tracker.get_contact_by_email(email)
        if not contact:
            return {
                "success": False,
                "error": f"Contact not found: {email}",
                "msg_file_path": None
            }

        # Use config defaults if not specified
        if send_mode is None:
            send_mode = self.config.default_send_mode
        if defer_hours is None:
            defer_hours = self.config.default_defer_hours
        if msg_folder is None:
            msg_folder = self.config.msg_output_folder

        try:
            # Render template
            html_body = self.template_engine.render(
                template_name,
                contact,
                self.config.sender_name
            )

            # Send email
            result = self.outlook.send_email(
                to=email,
                subject=self.config.default_subject,
                html_body=html_body,
                dry_run=False,
                send_mode=send_mode,
                defer_hours=defer_hours,
                msg_folder=msg_folder
            )

            if result['success']:
                self.logger.info(
                    f"Sent {template_name} to {email} (mode: {send_mode})"
                )

            return {
                "success": result['success'],
                "error": result.get('error'),
                "msg_file_path": result.get('msg_file_path')
            }

        except Exception as e:
            error_msg = f"Error sending to {email}: {str(e)}"
            self.logger.error(error_msg)
            return {
                "success": False,
                "error": error_msg,
                "msg_file_path": None
            }
