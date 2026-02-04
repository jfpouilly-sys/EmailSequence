"""Suppression list management service for Lead Generator Standalone."""

import logging
from datetime import datetime
from typing import List, Optional

from core.database import get_db
from core.models import SuppressionEntry, SuppressionScope, SuppressionSource
from core.exceptions import ValidationError, SuppressionError

logger = logging.getLogger(__name__)


class SuppressionService:
    """Service for managing the suppression (unsubscribe) list."""

    def __init__(self):
        self.db = get_db()

    def is_suppressed(self, email: str) -> bool:
        """Check if an email is in the suppression list."""
        query = "SELECT 1 FROM suppression_list WHERE email = ? LIMIT 1"
        row = self.db.fetchone(query, (email.lower(),))
        return row is not None

    def get_suppression_list(
        self,
        scope: Optional[str] = None,
        campaign_id: Optional[int] = None,
        limit: int = 1000,
        offset: int = 0
    ) -> List[SuppressionEntry]:
        """Get suppression list entries."""
        conditions = []
        params = []

        if scope:
            conditions.append("scope = ?")
            params.append(scope)

        if campaign_id:
            conditions.append("campaign_id = ?")
            params.append(campaign_id)

        where_clause = f"WHERE {' AND '.join(conditions)}" if conditions else ""

        query = f"""
            SELECT * FROM suppression_list
            {where_clause}
            ORDER BY created_at DESC
            LIMIT ? OFFSET ?
        """
        params.extend([limit, offset])

        rows = self.db.fetchall(query, tuple(params))
        return [self._row_to_entry(row) for row in rows]

    def get_suppression_count(self) -> int:
        """Get total count of suppressed emails."""
        row = self.db.fetchone("SELECT COUNT(*) as count FROM suppression_list")
        return row['count'] if row else 0

    def add_to_suppression(
        self,
        email: str,
        source: str,
        scope: str = SuppressionScope.GLOBAL.value,
        campaign_id: Optional[int] = None,
        reason: Optional[str] = None
    ) -> SuppressionEntry:
        """
        Add an email to the suppression list.

        Args:
            email: Email address to suppress
            source: Source of suppression (EmailReply, Manual, Bounce, Complaint)
            scope: Scope of suppression (Global, Campaign)
            campaign_id: Campaign ID if scope is Campaign
            reason: Optional reason for suppression
        """
        email = email.lower().strip()
        if not email:
            raise ValidationError("Email is required")

        # Validate source
        valid_sources = [s.value for s in SuppressionSource]
        if source not in valid_sources:
            raise ValidationError(f"Invalid source. Must be one of: {valid_sources}")

        # Validate scope
        valid_scopes = [s.value for s in SuppressionScope]
        if scope not in valid_scopes:
            raise ValidationError(f"Invalid scope. Must be one of: {valid_scopes}")

        # Check if already suppressed
        if self.is_suppressed(email):
            logger.debug(f"Email {email} already in suppression list")
            # Return existing entry
            return self.get_entry(email)

        # Insert entry
        self.db.execute("""
            INSERT INTO suppression_list (email, scope, source, campaign_id, reason)
            VALUES (?, ?, ?, ?, ?)
        """, (email, scope, source, campaign_id, reason))

        # Update campaign_contacts if exists
        self._update_campaign_contacts(email, campaign_id)

        logger.info(f"Added {email} to suppression list (source: {source})")
        return self.get_entry(email)

    def remove_from_suppression(self, email: str) -> None:
        """Remove an email from the suppression list."""
        email = email.lower().strip()

        if not self.is_suppressed(email):
            raise SuppressionError(f"Email {email} is not in suppression list")

        self.db.execute("DELETE FROM suppression_list WHERE email = ?", (email,))
        logger.info(f"Removed {email} from suppression list")

    def get_entry(self, email: str) -> Optional[SuppressionEntry]:
        """Get a specific suppression entry by email."""
        query = "SELECT * FROM suppression_list WHERE email = ?"
        row = self.db.fetchone(query, (email.lower(),))
        if row:
            return self._row_to_entry(row)
        return None

    def import_suppression_list(
        self,
        emails: List[str],
        source: str = SuppressionSource.MANUAL.value
    ) -> int:
        """
        Import multiple emails to suppression list.

        Returns:
            Number of emails added (duplicates are skipped)
        """
        added = 0
        for email in emails:
            email = email.lower().strip()
            if not email:
                continue

            if not self.is_suppressed(email):
                try:
                    self.db.execute("""
                        INSERT INTO suppression_list (email, scope, source)
                        VALUES (?, 'Global', ?)
                    """, (email, source))
                    added += 1
                except Exception as e:
                    logger.warning(f"Failed to add {email} to suppression list: {e}")

        logger.info(f"Imported {added} emails to suppression list")
        return added

    def export_suppression_list(self, file_path: str) -> int:
        """
        Export suppression list to a file.

        Returns:
            Number of emails exported
        """
        entries = self.get_suppression_list(limit=100000)

        with open(file_path, 'w', encoding='utf-8') as f:
            f.write("email,scope,source,reason,created_at\n")
            for entry in entries:
                reason = (entry.reason or '').replace(',', ';')
                f.write(f"{entry.email},{entry.scope},{entry.source},{reason},{entry.created_at}\n")

        logger.info(f"Exported {len(entries)} suppression entries to {file_path}")
        return len(entries)

    def search_suppression_list(self, query: str, limit: int = 100) -> List[SuppressionEntry]:
        """Search suppression list by email pattern."""
        search_term = f"%{query}%"
        sql = """
            SELECT * FROM suppression_list
            WHERE email LIKE ?
            ORDER BY created_at DESC
            LIMIT ?
        """
        rows = self.db.fetchall(sql, (search_term, limit))
        return [self._row_to_entry(row) for row in rows]

    def _update_campaign_contacts(self, email: str, campaign_id: Optional[int] = None) -> None:
        """Update campaign_contacts status when email is suppressed."""
        if campaign_id:
            # Update specific campaign
            self.db.execute("""
                UPDATE campaign_contacts
                SET status = 'Unsubscribed', updated_at = datetime('now')
                WHERE contact_id IN (SELECT contact_id FROM contacts WHERE email = ?)
                  AND campaign_id = ?
                  AND status NOT IN ('Completed', 'Responded')
            """, (email, campaign_id))
        else:
            # Update all campaigns
            self.db.execute("""
                UPDATE campaign_contacts
                SET status = 'Unsubscribed', updated_at = datetime('now')
                WHERE contact_id IN (SELECT contact_id FROM contacts WHERE email = ?)
                  AND status NOT IN ('Completed', 'Responded')
            """, (email,))

        # Also skip any pending queue items
        self.db.execute("""
            UPDATE email_queue
            SET status = 'Skipped', error_message = 'Contact unsubscribed'
            WHERE contact_id IN (SELECT contact_id FROM contacts WHERE email = ?)
              AND status = 'Pending'
        """, (email,))

    def _row_to_entry(self, row) -> SuppressionEntry:
        """Convert database row to SuppressionEntry model."""
        return SuppressionEntry(
            email=row['email'],
            scope=row['scope'],
            source=row['source'],
            campaign_id=row['campaign_id'],
            reason=row['reason'],
            created_at=row['created_at']
        )
