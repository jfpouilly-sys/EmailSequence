"""Unsubscribe detection logic for Lead Generator Standalone."""

import logging
import re
from datetime import datetime, timedelta
from typing import Optional, List, Tuple

from core.database import get_db, get_setting
from core.models import OutlookEmail
from services.suppression_service import SuppressionService
from outlook.outlook_service import OutlookService
from outlook.reply_detector import ReplyDetector

logger = logging.getLogger(__name__)

# Default unsubscribe keywords
DEFAULT_KEYWORDS_EN = ['UNSUBSCRIBE', 'STOP', 'REMOVE', 'OPT OUT', 'OPT-OUT']
DEFAULT_KEYWORDS_FR = ['DÉSINSCRIRE', 'DÉSINSCRIPTION', 'STOP', 'ARRÊTER', 'SUPPRIMER']


class UnsubscribeDetector:
    """Detects unsubscribe requests in emails."""

    def __init__(self, outlook_service: Optional[OutlookService] = None):
        self.outlook = outlook_service or OutlookService()
        self.db = get_db()
        self.suppression_service = SuppressionService()
        self.reply_detector = ReplyDetector(self.outlook)
        self._load_keywords()

    def _load_keywords(self) -> None:
        """Load unsubscribe keywords from settings."""
        # English keywords
        en_setting = get_setting('unsubscribe_keywords_en')
        if en_setting:
            self.keywords_en = [k.strip().upper() for k in en_setting.split(',')]
        else:
            self.keywords_en = DEFAULT_KEYWORDS_EN

        # French keywords
        fr_setting = get_setting('unsubscribe_keywords_fr')
        if fr_setting:
            self.keywords_fr = [k.strip().upper() for k in fr_setting.split(',')]
        else:
            self.keywords_fr = DEFAULT_KEYWORDS_FR

        # Combined keywords
        self.all_keywords = self.keywords_en + self.keywords_fr

    def scan_for_unsubscribes(self, since_hours: int = 24) -> List[Tuple[str, Optional[int]]]:
        """
        Scan configured folders for unsubscribe requests.

        Args:
            since_hours: Only scan emails received in the last N hours

        Returns:
            List of (email_address, campaign_id) tuples for detected unsubscribes
        """
        since = datetime.now() - timedelta(hours=since_hours)
        detected_unsubs = []

        # Get folders to scan
        folders_setting = get_setting('scan_folders', 'Inbox,Unsubscribe')
        folders = [f.strip() for f in folders_setting.split(',')]

        for folder in folders:
            try:
                emails = self.outlook.get_unread_emails(folder_name=folder, since=since)

                for email in emails:
                    if self.contains_unsubscribe_keyword(email.subject, email.body):
                        result = self.process_unsubscribe(
                            email.sender_email,
                            self.reply_detector.extract_campaign_ref(email.subject)
                        )
                        if result:
                            detected_unsubs.append(result)
                            # Mark email as read
                            self.outlook.mark_as_read(email.entry_id)

            except Exception as e:
                logger.warning(f"Error scanning folder {folder}: {e}")
                continue

        logger.info(f"Unsubscribe scan found {len(detected_unsubs)} requests")
        return detected_unsubs

    def contains_unsubscribe_keyword(
        self,
        subject: Optional[str] = None,
        body: Optional[str] = None
    ) -> bool:
        """
        Check if subject or body contains unsubscribe keywords.

        Args:
            subject: Email subject line
            body: Email body text

        Returns:
            True if unsubscribe keyword found
        """
        # Combine and normalize text
        text = ''
        if subject:
            text += subject.upper() + ' '
        if body:
            # Only check first 500 chars of body for performance
            text += body[:500].upper()

        # Check for keywords
        for keyword in self.all_keywords:
            if keyword in text:
                return True

        return False

    def process_unsubscribe(
        self,
        email_address: str,
        campaign_ref: Optional[str] = None
    ) -> Optional[Tuple[str, Optional[int]]]:
        """
        Process an unsubscribe request.

        Args:
            email_address: Email address requesting unsubscribe
            campaign_ref: Optional campaign reference

        Returns:
            Tuple of (email_address, campaign_id) if processed, None if already suppressed
        """
        if not email_address:
            return None

        email_address = email_address.lower().strip()

        # Check if already suppressed
        if self.suppression_service.is_suppressed(email_address):
            logger.debug(f"Email {email_address} already in suppression list")
            return None

        # Get campaign ID from reference
        campaign_id = None
        if campaign_ref:
            row = self.db.fetchone(
                "SELECT campaign_id FROM campaigns WHERE campaign_ref = ?",
                (campaign_ref,)
            )
            if row:
                campaign_id = row['campaign_id']

        # Add to suppression list
        self.suppression_service.add_to_suppression(
            email=email_address,
            source='EmailReply',
            scope='Global',
            campaign_id=campaign_id,
            reason='Unsubscribe keyword detected in email reply'
        )

        logger.info(f"Processed unsubscribe for {email_address}")
        return (email_address, campaign_id)

    def get_unsubscribe_keywords(self) -> dict:
        """Get current unsubscribe keywords."""
        return {
            'en': self.keywords_en,
            'fr': self.keywords_fr
        }

    def update_keywords(self, keywords_en: List[str], keywords_fr: List[str]) -> None:
        """Update unsubscribe keywords."""
        from core.database import set_setting

        # Update settings
        set_setting('unsubscribe_keywords_en', ','.join(keywords_en))
        set_setting('unsubscribe_keywords_fr', ','.join(keywords_fr))

        # Reload keywords
        self._load_keywords()

        logger.info("Updated unsubscribe keywords")
