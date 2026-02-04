"""Reply detection logic for Lead Generator Standalone."""

import logging
import re
from datetime import datetime, timedelta
from typing import Optional, List, Tuple

from core.database import get_db
from core.models import Contact, OutlookEmail
from outlook.outlook_service import OutlookService

logger = logging.getLogger(__name__)

# Pattern to extract campaign reference from subject
CAMPAIGN_REF_PATTERN = re.compile(r'ISIT-\d{6}')


class ReplyDetector:
    """Detects and processes reply emails."""

    def __init__(self, outlook_service: Optional[OutlookService] = None):
        self.outlook = outlook_service or OutlookService()
        self.db = get_db()

    def scan_for_replies(self, since_hours: int = 24) -> List[Tuple[OutlookEmail, Contact, int]]:
        """
        Scan inbox for replies and update contact statuses.

        Args:
            since_hours: Only scan emails received in the last N hours

        Returns:
            List of (email, contact, campaign_id) tuples for detected replies
        """
        since = datetime.now() - timedelta(hours=since_hours)
        detected_replies = []

        # Get unread emails
        emails = self.outlook.get_unread_emails(folder_name='Inbox', since=since)

        for email in emails:
            result = self._process_email(email)
            if result:
                detected_replies.append((email, result[0], result[1]))

        logger.info(f"Reply scan found {len(detected_replies)} replies")
        return detected_replies

    def _process_email(self, email: OutlookEmail) -> Optional[Tuple[Contact, int]]:
        """
        Process a single email to check if it's a reply.

        Returns:
            Tuple of (Contact, campaign_id) if reply detected, None otherwise
        """
        # Try to match sender to a contact
        contact = self.match_email_to_contact(email.sender_email)
        if not contact:
            return None

        # Try to extract campaign reference from subject
        campaign_id = self._get_campaign_from_email(email, contact)
        if not campaign_id:
            return None

        # Update contact status to Responded
        self._update_contact_responded(campaign_id, contact.contact_id)

        # Mark email as read (optional)
        self.outlook.mark_as_read(email.entry_id)

        logger.info(f"Reply detected from {email.sender_email} for campaign {campaign_id}")
        return (contact, campaign_id)

    def match_email_to_contact(self, sender_email: str) -> Optional[Contact]:
        """
        Match an email sender to a contact in the database.

        Args:
            sender_email: Sender email address

        Returns:
            Contact if found, None otherwise
        """
        if not sender_email:
            return None

        sender_email = sender_email.lower().strip()

        # Query for matching contact
        query = """
            SELECT * FROM contacts
            WHERE email = ?
            LIMIT 1
        """
        row = self.db.fetchone(query, (sender_email,))

        if row:
            return Contact(
                contact_id=row['contact_id'],
                list_id=row['list_id'],
                first_name=row['first_name'],
                last_name=row['last_name'],
                email=row['email'],
                company=row['company']
            )

        return None

    def extract_campaign_ref(self, subject: str) -> Optional[str]:
        """
        Extract campaign reference from email subject.

        Args:
            subject: Email subject line

        Returns:
            Campaign reference (e.g., ISIT-250001) if found, None otherwise
        """
        if not subject:
            return None

        match = CAMPAIGN_REF_PATTERN.search(subject)
        if match:
            return match.group(0)

        return None

    def _get_campaign_from_email(self, email: OutlookEmail, contact: Contact) -> Optional[int]:
        """
        Determine which campaign this reply is for.

        First tries to extract from subject, then falls back to finding
        the most recent active campaign for this contact.
        """
        # Try to get from subject
        campaign_ref = self.extract_campaign_ref(email.subject)
        if campaign_ref:
            row = self.db.fetchone(
                "SELECT campaign_id FROM campaigns WHERE campaign_ref = ?",
                (campaign_ref,)
            )
            if row:
                return row['campaign_id']

        # Fallback: find most recent active campaign for this contact
        query = """
            SELECT cc.campaign_id
            FROM campaign_contacts cc
            JOIN campaigns c ON cc.campaign_id = c.campaign_id
            WHERE cc.contact_id = ?
              AND c.status IN ('Active', 'Paused')
              AND cc.status IN ('Pending', 'InProgress')
            ORDER BY cc.last_email_sent_at DESC
            LIMIT 1
        """
        row = self.db.fetchone(query, (contact.contact_id,))
        if row:
            return row['campaign_id']

        # Last resort: any campaign this contact is in
        query = """
            SELECT campaign_id FROM campaign_contacts
            WHERE contact_id = ?
            ORDER BY created_at DESC
            LIMIT 1
        """
        row = self.db.fetchone(query, (contact.contact_id,))
        if row:
            return row['campaign_id']

        return None

    def _update_contact_responded(self, campaign_id: int, contact_id: int) -> None:
        """Update contact status to Responded."""
        self.db.execute("""
            UPDATE campaign_contacts
            SET status = 'Responded',
                responded_at = datetime('now'),
                updated_at = datetime('now')
            WHERE campaign_id = ? AND contact_id = ?
        """, (campaign_id, contact_id))

        # Skip any pending queue items for this contact
        self.db.execute("""
            UPDATE email_queue
            SET status = 'Skipped', error_message = 'Contact responded'
            WHERE campaign_id = ? AND contact_id = ? AND status = 'Pending'
        """, (campaign_id, contact_id))
