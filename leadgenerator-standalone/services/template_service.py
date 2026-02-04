"""Template management service for Lead Generator Standalone."""

import logging
import os
import re
import shutil
import mimetypes
from pathlib import Path
from typing import List, Optional, Dict, Any

from core.database import get_db
from core.models import EmailStep, Attachment, Contact, Campaign
from core.exceptions import ValidationError, TemplateError

logger = logging.getLogger(__name__)

# Merge tag patterns
MERGE_TAG_PATTERN = re.compile(r'\{\{(\w+)\}\}')

# Supported merge tags
MERGE_TAGS = {
    # Contact fields
    'Title': lambda c, **_: c.title or '',
    'FirstName': lambda c, **_: c.first_name or '',
    'LastName': lambda c, **_: c.last_name or '',
    'FullName': lambda c, **_: c.full_name or '',
    'Email': lambda c, **_: c.email or '',
    'Company': lambda c, **_: c.company or '',
    'Position': lambda c, **_: c.position or '',
    'Phone': lambda c, **_: c.phone or '',

    # Custom fields
    'Custom1': lambda c, **_: c.custom1 or '',
    'Custom2': lambda c, **_: c.custom2 or '',
    'Custom3': lambda c, **_: c.custom3 or '',
    'Custom4': lambda c, **_: c.custom4 or '',
    'Custom5': lambda c, **_: c.custom5 or '',
    'Custom6': lambda c, **_: c.custom6 or '',
    'Custom7': lambda c, **_: c.custom7 or '',
    'Custom8': lambda c, **_: c.custom8 or '',
    'Custom9': lambda c, **_: c.custom9 or '',
    'Custom10': lambda c, **_: c.custom10 or '',

    # Campaign fields
    'CampaignRef': lambda _, campaign=None, **__: campaign.campaign_ref if campaign else '',
    'UnsubscribeText': lambda **_: 'To unsubscribe, reply with "UNSUBSCRIBE" in the subject line.',
}


class TemplateService:
    """Service for managing email templates and steps."""

    def __init__(self, attachments_path: str = 'data/files'):
        self.db = get_db()
        self.attachments_path = Path(attachments_path)
        self.attachments_path.mkdir(parents=True, exist_ok=True)

    # Step CRUD Methods

    def get_steps(self, campaign_id: int) -> List[EmailStep]:
        """Get all steps for a campaign."""
        query = """
            SELECT * FROM email_steps
            WHERE campaign_id = ?
            ORDER BY step_number
        """
        rows = self.db.fetchall(query, (campaign_id,))
        steps = []
        for row in rows:
            step = self._row_to_step(row)
            step.attachments = self.get_attachments(step.step_id)
            steps.append(step)
        return steps

    def get_step(self, step_id: int) -> Optional[EmailStep]:
        """Get a step by ID with attachments."""
        query = "SELECT * FROM email_steps WHERE step_id = ?"
        row = self.db.fetchone(query, (step_id,))

        if not row:
            return None

        step = self._row_to_step(row)
        step.attachments = self.get_attachments(step_id)
        return step

    def create_step(
        self,
        campaign_id: int,
        step_number: int,
        subject: str,
        body: str,
        delay_days: int = 0
    ) -> EmailStep:
        """Create a new email step."""
        if not subject:
            raise ValidationError("Subject is required")
        if not body:
            raise ValidationError("Body is required")

        # Check for duplicate step number
        existing = self.db.fetchone(
            "SELECT 1 FROM email_steps WHERE campaign_id = ? AND step_number = ?",
            (campaign_id, step_number)
        )
        if existing:
            raise ValidationError(f"Step {step_number} already exists")

        cursor = self.db.execute("""
            INSERT INTO email_steps (campaign_id, step_number, subject_template, body_template, delay_days)
            VALUES (?, ?, ?, ?, ?)
        """, (campaign_id, step_number, subject, body, delay_days))

        step_id = cursor.lastrowid
        logger.info(f"Created step {step_number} for campaign {campaign_id}")
        return self.get_step(step_id)

    def update_step(self, step_id: int, data: Dict[str, Any]) -> EmailStep:
        """Update an email step."""
        step = self.get_step(step_id)
        if not step:
            raise ValidationError(f"Step {step_id} not found")

        updates = []
        params = []

        field_mapping = {
            'subject_template': 'subject_template',
            'body_template': 'body_template',
            'delay_days': 'delay_days',
            'is_active': 'is_active'
        }

        for data_key, db_field in field_mapping.items():
            if data_key in data:
                updates.append(f"{db_field} = ?")
                value = data[data_key]
                if data_key == 'is_active':
                    value = 1 if value else 0
                params.append(value)

        if updates:
            updates.append("updated_at = datetime('now')")
            params.append(step_id)

            query = f"UPDATE email_steps SET {', '.join(updates)} WHERE step_id = ?"
            self.db.execute(query, tuple(params))
            logger.info(f"Updated step {step_id}")

        return self.get_step(step_id)

    def delete_step(self, step_id: int) -> None:
        """Delete an email step and its attachments."""
        step = self.get_step(step_id)
        if not step:
            raise ValidationError(f"Step {step_id} not found")

        # Delete attachment files
        for attachment in step.attachments:
            self._delete_attachment_file(attachment.file_path)

        self.db.execute("DELETE FROM email_steps WHERE step_id = ?", (step_id,))
        logger.info(f"Deleted step {step_id}")

    def reorder_steps(self, campaign_id: int, step_ids_in_order: List[int]) -> None:
        """Reorder steps within a campaign."""
        for idx, step_id in enumerate(step_ids_in_order, start=1):
            # Use a temporary negative number to avoid unique constraint violation
            self.db.execute(
                "UPDATE email_steps SET step_number = ? WHERE step_id = ? AND campaign_id = ?",
                (-idx, step_id, campaign_id)
            )

        # Convert negative to positive
        for idx, step_id in enumerate(step_ids_in_order, start=1):
            self.db.execute(
                "UPDATE email_steps SET step_number = ? WHERE step_id = ? AND campaign_id = ?",
                (idx, step_id, campaign_id)
            )

        logger.info(f"Reordered steps for campaign {campaign_id}")

    # Attachment Methods

    def get_attachments(self, step_id: int) -> List[Attachment]:
        """Get all attachments for a step."""
        query = "SELECT * FROM attachments WHERE step_id = ? ORDER BY file_name"
        rows = self.db.fetchall(query, (step_id,))
        return [self._row_to_attachment(row) for row in rows]

    def add_attachment(self, step_id: int, file_path: str) -> Attachment:
        """Add an attachment to a step (copies file to storage)."""
        source_path = Path(file_path)
        if not source_path.exists():
            raise ValidationError(f"File not found: {file_path}")

        # Get file info
        file_name = source_path.name
        file_size = source_path.stat().st_size
        mime_type, _ = mimetypes.guess_type(str(source_path))

        # Generate unique destination path
        dest_dir = self.attachments_path / str(step_id)
        dest_dir.mkdir(parents=True, exist_ok=True)
        dest_path = dest_dir / file_name

        # Handle filename collision
        counter = 1
        while dest_path.exists():
            name, ext = os.path.splitext(file_name)
            dest_path = dest_dir / f"{name}_{counter}{ext}"
            counter += 1

        # Copy file
        shutil.copy2(source_path, dest_path)

        # Save to database
        cursor = self.db.execute("""
            INSERT INTO attachments (step_id, file_name, file_path, file_size, mime_type)
            VALUES (?, ?, ?, ?, ?)
        """, (step_id, dest_path.name, str(dest_path), file_size, mime_type))

        attachment_id = cursor.lastrowid
        logger.info(f"Added attachment '{file_name}' to step {step_id}")

        return self._get_attachment(attachment_id)

    def remove_attachment(self, attachment_id: int) -> None:
        """Remove an attachment."""
        attachment = self._get_attachment(attachment_id)
        if not attachment:
            raise ValidationError(f"Attachment {attachment_id} not found")

        # Delete file
        self._delete_attachment_file(attachment.file_path)

        # Remove from database
        self.db.execute("DELETE FROM attachments WHERE attachment_id = ?", (attachment_id,))
        logger.info(f"Removed attachment {attachment_id}")

    def _get_attachment(self, attachment_id: int) -> Optional[Attachment]:
        """Get an attachment by ID."""
        query = "SELECT * FROM attachments WHERE attachment_id = ?"
        row = self.db.fetchone(query, (attachment_id,))
        if row:
            return self._row_to_attachment(row)
        return None

    def _delete_attachment_file(self, file_path: str) -> None:
        """Delete an attachment file if it exists."""
        try:
            path = Path(file_path)
            if path.exists():
                path.unlink()
        except Exception as e:
            logger.warning(f"Failed to delete attachment file {file_path}: {e}")

    # Merge Tag Methods

    def apply_merge_tags(
        self,
        template: str,
        contact: Contact,
        campaign: Optional[Campaign] = None
    ) -> str:
        """Apply merge tags to a template string."""
        def replace_tag(match):
            tag_name = match.group(1)
            if tag_name in MERGE_TAGS:
                try:
                    return str(MERGE_TAGS[tag_name](contact, campaign=campaign))
                except Exception as e:
                    logger.warning(f"Error applying merge tag {tag_name}: {e}")
                    return ''
            return match.group(0)  # Return original if tag not found

        return MERGE_TAG_PATTERN.sub(replace_tag, template)

    def get_available_merge_tags(self) -> Dict[str, List[str]]:
        """Get categorized list of available merge tags."""
        return {
            'Contact': ['Title', 'FirstName', 'LastName', 'FullName', 'Email', 'Company', 'Position', 'Phone'],
            'Custom': ['Custom1', 'Custom2', 'Custom3', 'Custom4', 'Custom5',
                       'Custom6', 'Custom7', 'Custom8', 'Custom9', 'Custom10'],
            'Campaign': ['CampaignRef', 'UnsubscribeText']
        }

    def validate_template(self, template: str) -> List[str]:
        """
        Validate a template and return list of unknown tags.

        Returns:
            List of unknown merge tag names
        """
        unknown_tags = []
        for match in MERGE_TAG_PATTERN.finditer(template):
            tag_name = match.group(1)
            if tag_name not in MERGE_TAGS:
                unknown_tags.append(tag_name)
        return unknown_tags

    def render_preview(
        self,
        template: str,
        contact: Optional[Contact] = None,
        campaign: Optional[Campaign] = None
    ) -> str:
        """
        Render a template preview with sample or provided data.

        If no contact is provided, uses sample data.
        """
        if contact is None:
            # Create sample contact
            contact = Contact(
                title="Mr.",
                first_name="John",
                last_name="Doe",
                email="john.doe@example.com",
                company="Acme Corp",
                position="CEO",
                phone="+1 555-1234",
                custom1="Value 1",
                custom2="Value 2",
                custom3="Value 3"
            )

        if campaign is None:
            campaign = Campaign(
                campaign_ref="ISIT-250001"
            )

        return self.apply_merge_tags(template, contact, campaign)

    # Helper Methods

    def _row_to_step(self, row) -> EmailStep:
        """Convert database row to EmailStep model."""
        return EmailStep(
            step_id=row['step_id'],
            campaign_id=row['campaign_id'],
            step_number=row['step_number'],
            subject_template=row['subject_template'],
            body_template=row['body_template'],
            delay_days=row['delay_days'],
            is_active=bool(row['is_active']),
            created_at=row['created_at'],
            updated_at=row['updated_at']
        )

    def _row_to_attachment(self, row) -> Attachment:
        """Convert database row to Attachment model."""
        return Attachment(
            attachment_id=row['attachment_id'],
            step_id=row['step_id'],
            file_name=row['file_name'],
            file_path=row['file_path'],
            file_size=row['file_size'],
            mime_type=row['mime_type'],
            created_at=row['created_at']
        )
