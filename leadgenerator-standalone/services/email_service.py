"""Email queue management service for Lead Generator Standalone."""

import logging
import random
from datetime import datetime, timedelta
from typing import List, Optional, Dict, Any

from core.database import get_db
from core.models import QueuedEmail, QueueStatus, ContactStatus, Campaign, Contact, EmailStep
from core.exceptions import ValidationError

logger = logging.getLogger(__name__)


class EmailService:
    """Service for managing email queue and sending logic."""

    def __init__(self):
        self.db = get_db()

    def get_pending_emails(self, limit: int = 10) -> List[QueuedEmail]:
        """
        Get pending emails ready to be sent.

        Returns emails scheduled for now or earlier, ordered by scheduled time.
        """
        query = """
            SELECT eq.*,
                   c.first_name, c.last_name, c.email as contact_email, c.company,
                   c.title, c.position, c.phone, c.linkedin_url, c.source,
                   c.custom1, c.custom2, c.custom3, c.custom4, c.custom5,
                   c.custom6, c.custom7, c.custom8, c.custom9, c.custom10,
                   es.step_number, es.subject_template, es.body_template, es.delay_days,
                   cam.name as campaign_name, cam.campaign_ref,
                   cam.inter_email_delay_minutes, cam.randomization_minutes
            FROM email_queue eq
            JOIN contacts c ON eq.contact_id = c.contact_id
            JOIN email_steps es ON eq.step_id = es.step_id
            JOIN campaigns cam ON eq.campaign_id = cam.campaign_id
            WHERE eq.status = 'Pending'
              AND eq.scheduled_at <= datetime('now')
              AND cam.status = 'Active'
            ORDER BY eq.scheduled_at
            LIMIT ?
        """
        rows = self.db.fetchall(query, (limit,))
        return [self._row_to_queued_email(row) for row in rows]

    def get_queue_by_campaign(self, campaign_id: int) -> List[QueuedEmail]:
        """Get all queue items for a campaign."""
        query = """
            SELECT eq.*, c.first_name, c.last_name, c.email as contact_email
            FROM email_queue eq
            JOIN contacts c ON eq.contact_id = c.contact_id
            WHERE eq.campaign_id = ?
            ORDER BY eq.scheduled_at DESC
        """
        rows = self.db.fetchall(query, (campaign_id,))
        return [self._row_to_queued_email(row) for row in rows]

    def mark_email_sending(self, queue_id: int) -> None:
        """Mark an email as currently being sent."""
        self.db.execute("""
            UPDATE email_queue
            SET status = 'Sending', last_attempt_at = datetime('now'), attempts = attempts + 1
            WHERE queue_id = ?
        """, (queue_id,))

    def mark_email_sent(self, queue_id: int, outlook_entry_id: Optional[str] = None) -> None:
        """Mark an email as successfully sent."""
        # Update queue
        self.db.execute("""
            UPDATE email_queue
            SET status = 'Sent', last_attempt_at = datetime('now')
            WHERE queue_id = ?
        """, (queue_id,))

        # Get queue item details
        queue_item = self._get_queue_item(queue_id)
        if not queue_item:
            return

        # Log the email
        self.db.execute("""
            INSERT INTO email_logs (campaign_id, contact_id, step_id, subject, status, outlook_entry_id)
            VALUES (?, ?, ?, ?, 'Sent', ?)
        """, (queue_item.campaign_id, queue_item.contact_id, queue_item.step_id,
              queue_item.step.subject_template if queue_item.step else '', outlook_entry_id))

        # Update campaign contact status
        self.db.execute("""
            UPDATE campaign_contacts
            SET status = 'InProgress',
                current_step = current_step + 1,
                last_email_sent_at = datetime('now'),
                updated_at = datetime('now')
            WHERE campaign_id = ? AND contact_id = ?
        """, (queue_item.campaign_id, queue_item.contact_id))

        logger.info(f"Email sent for queue {queue_id}")

    def mark_email_failed(self, queue_id: int, error_message: str) -> None:
        """Mark an email as failed."""
        # Get queue item
        queue_item = self._get_queue_item(queue_id)

        # Check if max attempts reached
        max_attempts = 3
        if queue_item and queue_item.attempts >= max_attempts:
            self.db.execute("""
                UPDATE email_queue
                SET status = 'Failed', error_message = ?, last_attempt_at = datetime('now')
                WHERE queue_id = ?
            """, (error_message, queue_id))

            # Log the failure
            self.db.execute("""
                INSERT INTO email_logs (campaign_id, contact_id, step_id, subject, status, error_message)
                VALUES (?, ?, ?, ?, 'Failed', ?)
            """, (queue_item.campaign_id, queue_item.contact_id, queue_item.step_id,
                  queue_item.step.subject_template if queue_item.step else '', error_message))

            logger.error(f"Email permanently failed for queue {queue_id}: {error_message}")
        else:
            # Revert to pending for retry
            self.db.execute("""
                UPDATE email_queue
                SET status = 'Pending', error_message = ?, last_attempt_at = datetime('now')
                WHERE queue_id = ?
            """, (error_message, queue_id))

            logger.warning(f"Email failed for queue {queue_id}, will retry: {error_message}")

    def mark_email_skipped(self, queue_id: int, reason: str) -> None:
        """Mark an email as skipped."""
        self.db.execute("""
            UPDATE email_queue
            SET status = 'Skipped', error_message = ?
            WHERE queue_id = ?
        """, (reason, queue_id))

        logger.info(f"Email skipped for queue {queue_id}: {reason}")

    def schedule_next_step(self, campaign_id: int, contact_id: int) -> Optional[int]:
        """
        Schedule the next step email for a contact.

        Returns queue_id if scheduled, None if no more steps.
        """
        # Get campaign and contact info
        campaign_row = self.db.fetchone("""
            SELECT * FROM campaigns WHERE campaign_id = ?
        """, (campaign_id,))

        if not campaign_row or campaign_row['status'] != 'Active':
            return None

        # Get current step for contact
        cc_row = self.db.fetchone("""
            SELECT current_step FROM campaign_contacts
            WHERE campaign_id = ? AND contact_id = ?
        """, (campaign_id, contact_id))

        if not cc_row:
            return None

        current_step = cc_row['current_step']

        # Get next step
        next_step_row = self.db.fetchone("""
            SELECT * FROM email_steps
            WHERE campaign_id = ? AND step_number > ? AND is_active = 1
            ORDER BY step_number
            LIMIT 1
        """, (campaign_id, current_step))

        if not next_step_row:
            # No more steps - mark contact as completed
            self.db.execute("""
                UPDATE campaign_contacts
                SET status = 'Completed', updated_at = datetime('now')
                WHERE campaign_id = ? AND contact_id = ?
            """, (campaign_id, contact_id))
            return None

        # Calculate send time
        delay_days = next_step_row['delay_days'] or campaign_row['sequence_step_delay_days']
        scheduled_at = datetime.now() + timedelta(days=delay_days)

        # Apply randomization
        randomization = campaign_row['randomization_minutes']
        if randomization:
            random_minutes = random.randint(-randomization, randomization)
            scheduled_at += timedelta(minutes=random_minutes)

        # Create queue entry
        cursor = self.db.execute("""
            INSERT INTO email_queue (campaign_id, contact_id, step_id, scheduled_at, status)
            VALUES (?, ?, ?, ?, 'Pending')
        """, (campaign_id, contact_id, next_step_row['step_id'], scheduled_at.isoformat()))

        # Update campaign_contact
        self.db.execute("""
            UPDATE campaign_contacts
            SET next_email_scheduled_at = ?, updated_at = datetime('now')
            WHERE campaign_id = ? AND contact_id = ?
        """, (scheduled_at.isoformat(), campaign_id, contact_id))

        logger.info(f"Scheduled step {next_step_row['step_number']} for contact {contact_id}")
        return cursor.lastrowid

    def process_queue_item(self, queued_email: QueuedEmail) -> bool:
        """
        Process a queue item - check if it should be sent.

        Returns True if email should be sent, False if should be skipped.
        """
        # Check suppression list
        suppressed = self.db.fetchone("""
            SELECT 1 FROM suppression_list WHERE email = ?
        """, (queued_email.contact.email if queued_email.contact else '',))

        if suppressed:
            self.mark_email_skipped(queued_email.queue_id, "Contact is in suppression list")
            return False

        # Check contact status in campaign
        cc_row = self.db.fetchone("""
            SELECT status FROM campaign_contacts
            WHERE campaign_id = ? AND contact_id = ?
        """, (queued_email.campaign_id, queued_email.contact_id))

        if cc_row and cc_row['status'] in ['Responded', 'Completed', 'Unsubscribed', 'OptedOut', 'Bounced']:
            self.mark_email_skipped(queued_email.queue_id, f"Contact status is {cc_row['status']}")
            return False

        return True

    def calculate_send_time(
        self,
        base_time: datetime,
        randomization_minutes: int,
        sending_window_start: str = "09:00",
        sending_window_end: str = "17:00"
    ) -> datetime:
        """
        Calculate actual send time with randomization and business hours.
        """
        # Apply randomization
        if randomization_minutes:
            random_offset = random.randint(-randomization_minutes, randomization_minutes)
            base_time += timedelta(minutes=random_offset)

        # Parse window times
        start_hour, start_min = map(int, sending_window_start.split(':'))
        end_hour, end_min = map(int, sending_window_end.split(':'))

        # Adjust to be within sending window
        if base_time.hour < start_hour or (base_time.hour == start_hour and base_time.minute < start_min):
            # Before window - move to start
            base_time = base_time.replace(hour=start_hour, minute=start_min)
        elif base_time.hour > end_hour or (base_time.hour == end_hour and base_time.minute > end_min):
            # After window - move to next day
            base_time = base_time.replace(hour=start_hour, minute=start_min)
            base_time += timedelta(days=1)

        return base_time

    def get_queue_stats(self) -> Dict[str, int]:
        """Get overall queue statistics."""
        query = """
            SELECT status, COUNT(*) as count
            FROM email_queue
            GROUP BY status
        """
        rows = self.db.fetchall(query)

        stats = {'pending': 0, 'sending': 0, 'sent': 0, 'failed': 0, 'skipped': 0}
        for row in rows:
            status = row['status'].lower()
            if status in stats:
                stats[status] = row['count']

        return stats

    def clear_old_queue_items(self, days: int = 30) -> int:
        """Remove completed/failed/skipped queue items older than specified days."""
        cutoff = (datetime.now() - timedelta(days=days)).isoformat()
        cursor = self.db.execute("""
            DELETE FROM email_queue
            WHERE status IN ('Sent', 'Failed', 'Skipped')
              AND created_at < ?
        """, (cutoff,))
        count = cursor.rowcount
        logger.info(f"Cleared {count} old queue items")
        return count

    # Helper Methods

    def _get_queue_item(self, queue_id: int) -> Optional[QueuedEmail]:
        """Get a queue item by ID."""
        query = """
            SELECT eq.*,
                   c.first_name, c.last_name, c.email as contact_email,
                   es.subject_template, es.body_template
            FROM email_queue eq
            LEFT JOIN contacts c ON eq.contact_id = c.contact_id
            LEFT JOIN email_steps es ON eq.step_id = es.step_id
            WHERE eq.queue_id = ?
        """
        row = self.db.fetchone(query, (queue_id,))
        if row:
            return self._row_to_queued_email(row)
        return None

    def _row_to_queued_email(self, row) -> QueuedEmail:
        """Convert database row to QueuedEmail model."""
        qe = QueuedEmail(
            queue_id=row['queue_id'],
            campaign_id=row['campaign_id'],
            contact_id=row['contact_id'],
            step_id=row['step_id'],
            scheduled_at=row['scheduled_at'],
            status=row['status'],
            attempts=row['attempts'],
            last_attempt_at=row['last_attempt_at'],
            error_message=row['error_message'],
            created_at=row['created_at']
        )

        # Add contact if available
        if 'contact_email' in row.keys() and row['contact_email']:
            qe.contact = Contact(
                contact_id=row['contact_id'],
                first_name=row['first_name'] if 'first_name' in row.keys() else '',
                last_name=row['last_name'] if 'last_name' in row.keys() else '',
                email=row['contact_email'],
                company=row['company'] if 'company' in row.keys() else '',
                title=row['title'] if 'title' in row.keys() else None,
                position=row['position'] if 'position' in row.keys() else None,
                phone=row['phone'] if 'phone' in row.keys() else None,
                linkedin_url=row['linkedin_url'] if 'linkedin_url' in row.keys() else None,
                source=row['source'] if 'source' in row.keys() else None,
                custom1=row['custom1'] if 'custom1' in row.keys() else None,
                custom2=row['custom2'] if 'custom2' in row.keys() else None,
                custom3=row['custom3'] if 'custom3' in row.keys() else None,
                custom4=row['custom4'] if 'custom4' in row.keys() else None,
                custom5=row['custom5'] if 'custom5' in row.keys() else None,
                custom6=row['custom6'] if 'custom6' in row.keys() else None,
                custom7=row['custom7'] if 'custom7' in row.keys() else None,
                custom8=row['custom8'] if 'custom8' in row.keys() else None,
                custom9=row['custom9'] if 'custom9' in row.keys() else None,
                custom10=row['custom10'] if 'custom10' in row.keys() else None,
            )

        # Add step if available
        if 'subject_template' in row.keys() and row['subject_template']:
            qe.step = EmailStep(
                step_id=row['step_id'],
                campaign_id=row['campaign_id'],
                step_number=row['step_number'] if 'step_number' in row.keys() else 1,
                subject_template=row['subject_template'],
                body_template=row['body_template'] if 'body_template' in row.keys() else '',
                delay_days=row['delay_days'] if 'delay_days' in row.keys() else 0
            )

        # Add campaign info if available
        if 'campaign_name' in row.keys():
            qe.campaign = Campaign(
                campaign_id=row['campaign_id'],
                name=row['campaign_name'],
                campaign_ref=row['campaign_ref'] if 'campaign_ref' in row.keys() else '',
                inter_email_delay_minutes=row['inter_email_delay_minutes'] if 'inter_email_delay_minutes' in row.keys() else 30,
                randomization_minutes=row['randomization_minutes'] if 'randomization_minutes' in row.keys() else 15
            )

        return qe
