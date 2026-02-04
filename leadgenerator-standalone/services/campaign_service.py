"""Campaign management service for Lead Generator Standalone."""

import logging
from datetime import datetime, timedelta
from typing import List, Optional, Dict, Any

from core.database import get_db, generate_campaign_ref
from core.models import Campaign, EmailStep, CampaignContact, CampaignStatus, ContactStatus
from core.exceptions import ValidationError, CampaignError

logger = logging.getLogger(__name__)


class CampaignService:
    """Service for managing campaigns and campaign contacts."""

    def __init__(self):
        self.db = get_db()

    # Campaign CRUD Methods

    def get_all_campaigns(self, status_filter: Optional[str] = None) -> List[Campaign]:
        """Get all campaigns, optionally filtered by status."""
        if status_filter:
            query = """
                SELECT c.*, cl.name as contact_list_name
                FROM campaigns c
                LEFT JOIN contact_lists cl ON c.contact_list_id = cl.list_id
                WHERE c.status = ?
                ORDER BY c.created_at DESC
            """
            rows = self.db.fetchall(query, (status_filter,))
        else:
            query = """
                SELECT c.*, cl.name as contact_list_name
                FROM campaigns c
                LEFT JOIN contact_lists cl ON c.contact_list_id = cl.list_id
                ORDER BY c.created_at DESC
            """
            rows = self.db.fetchall(query)

        campaigns = []
        for row in rows:
            campaign = self._row_to_campaign(row)
            campaign.stats = self.get_campaign_stats(campaign.campaign_id)
            campaigns.append(campaign)

        return campaigns

    def get_campaign(self, campaign_id: int) -> Optional[Campaign]:
        """Get a campaign by ID with steps and stats."""
        query = """
            SELECT c.*, cl.name as contact_list_name
            FROM campaigns c
            LEFT JOIN contact_lists cl ON c.contact_list_id = cl.list_id
            WHERE c.campaign_id = ?
        """
        row = self.db.fetchone(query, (campaign_id,))

        if not row:
            return None

        campaign = self._row_to_campaign(row)
        campaign.steps = self._get_campaign_steps(campaign_id)
        campaign.stats = self.get_campaign_stats(campaign_id)

        return campaign

    def create_campaign(self, data: Dict[str, Any]) -> Campaign:
        """Create a new campaign."""
        name = data.get('name', '').strip()
        if not name:
            raise ValidationError("Campaign name is required")

        # Generate campaign reference
        campaign_ref = generate_campaign_ref()

        query = """
            INSERT INTO campaigns (
                name, description, campaign_ref, contact_list_id, status,
                inter_email_delay_minutes, sequence_step_delay_days,
                sending_window_start, sending_window_end, sending_days,
                randomization_minutes, daily_send_limit, start_date, end_date
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """
        params = (
            name,
            data.get('description'),
            campaign_ref,
            data.get('contact_list_id'),
            CampaignStatus.DRAFT.value,
            data.get('inter_email_delay_minutes', 30),
            data.get('sequence_step_delay_days', 3),
            data.get('sending_window_start', '09:00'),
            data.get('sending_window_end', '17:00'),
            data.get('sending_days', 'Mon,Tue,Wed,Thu,Fri'),
            data.get('randomization_minutes', 15),
            data.get('daily_send_limit', 50),
            data.get('start_date'),
            data.get('end_date')
        )

        cursor = self.db.execute(query, params)
        campaign_id = cursor.lastrowid

        logger.info(f"Created campaign '{name}' with ref {campaign_ref}")
        return self.get_campaign(campaign_id)

    def update_campaign(self, campaign_id: int, data: Dict[str, Any]) -> Campaign:
        """Update a campaign."""
        campaign = self.get_campaign(campaign_id)
        if not campaign:
            raise ValidationError(f"Campaign {campaign_id} not found")

        # Only allow updates if campaign is Draft or Paused
        if campaign.status not in [CampaignStatus.DRAFT.value, CampaignStatus.PAUSED.value]:
            raise CampaignError(f"Cannot update campaign in {campaign.status} status")

        updates = []
        params = []

        field_mapping = {
            'name': 'name',
            'description': 'description',
            'contact_list_id': 'contact_list_id',
            'inter_email_delay_minutes': 'inter_email_delay_minutes',
            'sequence_step_delay_days': 'sequence_step_delay_days',
            'sending_window_start': 'sending_window_start',
            'sending_window_end': 'sending_window_end',
            'sending_days': 'sending_days',
            'randomization_minutes': 'randomization_minutes',
            'daily_send_limit': 'daily_send_limit',
            'start_date': 'start_date',
            'end_date': 'end_date'
        }

        for data_key, db_field in field_mapping.items():
            if data_key in data:
                updates.append(f"{db_field} = ?")
                params.append(data[data_key])

        if updates:
            updates.append("updated_at = datetime('now')")
            params.append(campaign_id)

            query = f"UPDATE campaigns SET {', '.join(updates)} WHERE campaign_id = ?"
            self.db.execute(query, tuple(params))
            logger.info(f"Updated campaign {campaign_id}")

        return self.get_campaign(campaign_id)

    def delete_campaign(self, campaign_id: int) -> None:
        """Delete a campaign and all related data."""
        campaign = self.get_campaign(campaign_id)
        if not campaign:
            raise ValidationError(f"Campaign {campaign_id} not found")

        if campaign.status == CampaignStatus.ACTIVE.value:
            raise CampaignError("Cannot delete an active campaign. Pause it first.")

        self.db.execute("DELETE FROM campaigns WHERE campaign_id = ?", (campaign_id,))
        logger.info(f"Deleted campaign {campaign_id}")

    def duplicate_campaign(self, campaign_id: int, new_name: Optional[str] = None) -> Campaign:
        """Duplicate a campaign with its steps."""
        campaign = self.get_campaign(campaign_id)
        if not campaign:
            raise ValidationError(f"Campaign {campaign_id} not found")

        # Create new campaign
        new_data = {
            'name': new_name or f"{campaign.name} (Copy)",
            'description': campaign.description,
            'contact_list_id': campaign.contact_list_id,
            'inter_email_delay_minutes': campaign.inter_email_delay_minutes,
            'sequence_step_delay_days': campaign.sequence_step_delay_days,
            'sending_window_start': campaign.sending_window_start,
            'sending_window_end': campaign.sending_window_end,
            'sending_days': campaign.sending_days,
            'randomization_minutes': campaign.randomization_minutes,
            'daily_send_limit': campaign.daily_send_limit,
        }

        new_campaign = self.create_campaign(new_data)

        # Duplicate steps
        for step in campaign.steps:
            self._create_step(
                new_campaign.campaign_id,
                step.step_number,
                step.subject_template,
                step.body_template,
                step.delay_days
            )

        logger.info(f"Duplicated campaign {campaign_id} to {new_campaign.campaign_id}")
        return self.get_campaign(new_campaign.campaign_id)

    # Campaign Lifecycle Methods

    def activate_campaign(self, campaign_id: int) -> Campaign:
        """Activate a campaign and populate email queue."""
        campaign = self.get_campaign(campaign_id)
        if not campaign:
            raise ValidationError(f"Campaign {campaign_id} not found")

        if campaign.status not in [CampaignStatus.DRAFT.value, CampaignStatus.PAUSED.value]:
            raise CampaignError(f"Cannot activate campaign in {campaign.status} status")

        if not campaign.contact_list_id:
            raise CampaignError("Campaign must have a contact list assigned")

        if not campaign.steps:
            raise CampaignError("Campaign must have at least one email step")

        # Get first active step
        first_step = next((s for s in campaign.steps if s.is_active), None)
        if not first_step:
            raise CampaignError("Campaign must have at least one active email step")

        # Get contacts not in suppression list
        valid_contacts = self._get_valid_contacts(campaign_id)

        if not valid_contacts:
            raise CampaignError("No valid contacts to send to (all suppressed or no contacts)")

        # Populate campaign_contacts and email_queue
        now = datetime.now().isoformat()

        for contact_id in valid_contacts:
            # Create or update campaign_contact entry
            self.db.execute("""
                INSERT INTO campaign_contacts (campaign_id, contact_id, status, current_step, created_at)
                VALUES (?, ?, 'Pending', 0, datetime('now'))
                ON CONFLICT(campaign_id, contact_id) DO UPDATE SET
                    status = 'Pending',
                    current_step = 0,
                    updated_at = datetime('now')
            """, (campaign_id, contact_id))

            # Schedule first email
            self._schedule_email(campaign_id, contact_id, first_step.step_id, now)

        # Update campaign status
        self.db.execute("""
            UPDATE campaigns
            SET status = ?, start_date = datetime('now'), updated_at = datetime('now')
            WHERE campaign_id = ?
        """, (CampaignStatus.ACTIVE.value, campaign_id))

        logger.info(f"Activated campaign {campaign_id} with {len(valid_contacts)} contacts")
        return self.get_campaign(campaign_id)

    def pause_campaign(self, campaign_id: int) -> Campaign:
        """Pause an active campaign."""
        campaign = self.get_campaign(campaign_id)
        if not campaign:
            raise ValidationError(f"Campaign {campaign_id} not found")

        if campaign.status != CampaignStatus.ACTIVE.value:
            raise CampaignError("Can only pause an active campaign")

        self.db.execute("""
            UPDATE campaigns
            SET status = ?, updated_at = datetime('now')
            WHERE campaign_id = ?
        """, (CampaignStatus.PAUSED.value, campaign_id))

        # Update pending queue items
        self.db.execute("""
            UPDATE email_queue
            SET status = 'Skipped', error_message = 'Campaign paused'
            WHERE campaign_id = ? AND status = 'Pending'
        """, (campaign_id,))

        logger.info(f"Paused campaign {campaign_id}")
        return self.get_campaign(campaign_id)

    def complete_campaign(self, campaign_id: int) -> Campaign:
        """Mark a campaign as completed."""
        campaign = self.get_campaign(campaign_id)
        if not campaign:
            raise ValidationError(f"Campaign {campaign_id} not found")

        self.db.execute("""
            UPDATE campaigns
            SET status = ?, end_date = datetime('now'), updated_at = datetime('now')
            WHERE campaign_id = ?
        """, (CampaignStatus.COMPLETED.value, campaign_id))

        # Update pending queue items
        self.db.execute("""
            UPDATE email_queue
            SET status = 'Skipped', error_message = 'Campaign completed'
            WHERE campaign_id = ? AND status = 'Pending'
        """, (campaign_id,))

        logger.info(f"Completed campaign {campaign_id}")
        return self.get_campaign(campaign_id)

    def archive_campaign(self, campaign_id: int) -> Campaign:
        """Archive a campaign."""
        campaign = self.get_campaign(campaign_id)
        if not campaign:
            raise ValidationError(f"Campaign {campaign_id} not found")

        if campaign.status == CampaignStatus.ACTIVE.value:
            raise CampaignError("Cannot archive an active campaign. Complete it first.")

        self.db.execute("""
            UPDATE campaigns
            SET status = ?, updated_at = datetime('now')
            WHERE campaign_id = ?
        """, (CampaignStatus.ARCHIVED.value, campaign_id))

        logger.info(f"Archived campaign {campaign_id}")
        return self.get_campaign(campaign_id)

    # Statistics Methods

    def get_campaign_stats(self, campaign_id: int) -> Dict[str, int]:
        """Get campaign statistics."""
        stats = {
            'total_contacts': 0,
            'pending': 0,
            'in_progress': 0,
            'responded': 0,
            'completed': 0,
            'bounced': 0,
            'unsubscribed': 0,
            'opted_out': 0,
            'paused': 0,
            'emails_sent': 0,
            'emails_failed': 0
        }

        # Contact status counts
        query = """
            SELECT status, COUNT(*) as count
            FROM campaign_contacts
            WHERE campaign_id = ?
            GROUP BY status
        """
        rows = self.db.fetchall(query, (campaign_id,))

        for row in rows:
            status = row['status'].lower().replace(' ', '_')
            if status == 'inprogress':
                status = 'in_progress'
            if status in stats:
                stats[status] = row['count']
            stats['total_contacts'] += row['count']

        # Email counts
        email_query = """
            SELECT status, COUNT(*) as count
            FROM email_logs
            WHERE campaign_id = ?
            GROUP BY status
        """
        email_rows = self.db.fetchall(email_query, (campaign_id,))

        for row in email_rows:
            if row['status'] == 'Sent':
                stats['emails_sent'] = row['count']
            elif row['status'] == 'Failed':
                stats['emails_failed'] = row['count']

        return stats

    def get_campaign_contacts(
        self,
        campaign_id: int,
        status_filter: Optional[str] = None,
        limit: int = 100,
        offset: int = 0
    ) -> List[CampaignContact]:
        """Get contacts for a campaign with their status."""
        if status_filter:
            query = """
                SELECT cc.*, c.first_name, c.last_name, c.email, c.company
                FROM campaign_contacts cc
                JOIN contacts c ON cc.contact_id = c.contact_id
                WHERE cc.campaign_id = ? AND cc.status = ?
                ORDER BY c.last_name, c.first_name
                LIMIT ? OFFSET ?
            """
            rows = self.db.fetchall(query, (campaign_id, status_filter, limit, offset))
        else:
            query = """
                SELECT cc.*, c.first_name, c.last_name, c.email, c.company
                FROM campaign_contacts cc
                JOIN contacts c ON cc.contact_id = c.contact_id
                WHERE cc.campaign_id = ?
                ORDER BY c.last_name, c.first_name
                LIMIT ? OFFSET ?
            """
            rows = self.db.fetchall(query, (campaign_id, limit, offset))

        return [self._row_to_campaign_contact(row) for row in rows]

    def update_contact_status(
        self,
        campaign_id: int,
        contact_id: int,
        status: str,
        responded_at: Optional[str] = None
    ) -> None:
        """Update a campaign contact's status."""
        updates = ["status = ?", "updated_at = datetime('now')"]
        params = [status]

        if responded_at:
            updates.append("responded_at = ?")
            params.append(responded_at)

        params.extend([campaign_id, contact_id])

        self.db.execute(f"""
            UPDATE campaign_contacts
            SET {', '.join(updates)}
            WHERE campaign_id = ? AND contact_id = ?
        """, tuple(params))

    # Helper Methods

    def _get_campaign_steps(self, campaign_id: int) -> List[EmailStep]:
        """Get all steps for a campaign."""
        query = """
            SELECT * FROM email_steps
            WHERE campaign_id = ?
            ORDER BY step_number
        """
        rows = self.db.fetchall(query, (campaign_id,))
        return [self._row_to_step(row) for row in rows]

    def _create_step(
        self,
        campaign_id: int,
        step_number: int,
        subject: str,
        body: str,
        delay_days: int = 0
    ) -> int:
        """Create an email step."""
        cursor = self.db.execute("""
            INSERT INTO email_steps (campaign_id, step_number, subject_template, body_template, delay_days)
            VALUES (?, ?, ?, ?, ?)
        """, (campaign_id, step_number, subject, body, delay_days))
        return cursor.lastrowid

    def _get_valid_contacts(self, campaign_id: int) -> List[int]:
        """Get contact IDs not in suppression list."""
        campaign = self.get_campaign(campaign_id)
        if not campaign or not campaign.contact_list_id:
            return []

        query = """
            SELECT c.contact_id
            FROM contacts c
            WHERE c.list_id = ?
              AND c.email NOT IN (SELECT email FROM suppression_list)
        """
        rows = self.db.fetchall(query, (campaign.contact_list_id,))
        return [row['contact_id'] for row in rows]

    def _schedule_email(
        self,
        campaign_id: int,
        contact_id: int,
        step_id: int,
        scheduled_at: str
    ) -> int:
        """Schedule an email in the queue."""
        cursor = self.db.execute("""
            INSERT INTO email_queue (campaign_id, contact_id, step_id, scheduled_at, status)
            VALUES (?, ?, ?, ?, 'Pending')
        """, (campaign_id, contact_id, step_id, scheduled_at))
        return cursor.lastrowid

    def _row_to_campaign(self, row) -> Campaign:
        """Convert database row to Campaign model."""
        return Campaign(
            campaign_id=row['campaign_id'],
            name=row['name'],
            description=row['description'],
            campaign_ref=row['campaign_ref'],
            contact_list_id=row['contact_list_id'],
            status=row['status'],
            inter_email_delay_minutes=row['inter_email_delay_minutes'],
            sequence_step_delay_days=row['sequence_step_delay_days'],
            sending_window_start=row['sending_window_start'],
            sending_window_end=row['sending_window_end'],
            sending_days=row['sending_days'],
            randomization_minutes=row['randomization_minutes'],
            daily_send_limit=row['daily_send_limit'],
            start_date=row['start_date'],
            end_date=row['end_date'],
            created_at=row['created_at'],
            updated_at=row['updated_at'],
            contact_list_name=row['contact_list_name'] if 'contact_list_name' in row.keys() else None
        )

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

    def _row_to_campaign_contact(self, row) -> CampaignContact:
        """Convert database row to CampaignContact model."""
        from core.models import Contact

        cc = CampaignContact(
            campaign_id=row['campaign_id'],
            contact_id=row['contact_id'],
            status=row['status'],
            current_step=row['current_step'],
            last_email_sent_at=row['last_email_sent_at'],
            next_email_scheduled_at=row['next_email_scheduled_at'],
            responded_at=row['responded_at'],
            created_at=row['created_at'],
            updated_at=row['updated_at']
        )

        # Add contact info if available
        if 'first_name' in row.keys():
            cc.contact = Contact(
                contact_id=row['contact_id'],
                first_name=row['first_name'],
                last_name=row['last_name'],
                email=row['email'],
                company=row['company'] if 'company' in row.keys() else ''
            )

        return cc
