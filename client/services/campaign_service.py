"""Campaign business logic service."""
import logging
from typing import List, Optional, Callable
from dataclasses import dataclass

from core.api_client import ApiClient
from core.models import Campaign, EmailStep, CampaignStatus, CampaignStatistics

logger = logging.getLogger(__name__)


@dataclass
class CreateCampaignRequest:
    """Request data for creating a campaign."""
    name: str
    description: Optional[str] = None
    contact_list_id: Optional[str] = None
    inter_email_delay_minutes: int = 5
    sequence_step_delay_days: int = 3
    sending_window_start: str = "09:00"
    sending_window_end: str = "17:00"
    sending_days: str = "Monday,Tuesday,Wednesday,Thursday,Friday"
    randomization_minutes: int = 15
    daily_send_limit: int = 100


class CampaignService:
    """Service for campaign operations."""

    def __init__(self, api_client: ApiClient):
        self.api = api_client

    def get_all_campaigns(self, only_mine: bool = True) -> List[Campaign]:
        """Get all campaigns."""
        return self.api.get_campaigns(only_mine=only_mine)

    def get_campaign(self, campaign_id: str) -> Campaign:
        """Get campaign by ID."""
        return self.api.get_campaign(campaign_id)

    def create_campaign(self, request: CreateCampaignRequest) -> Campaign:
        """Create a new campaign."""
        return self.api.create_campaign(
            name=request.name,
            description=request.description,
            contact_list_id=request.contact_list_id,
            interEmailDelayMinutes=request.inter_email_delay_minutes,
            sequenceStepDelayDays=request.sequence_step_delay_days,
            sendingWindowStart=request.sending_window_start,
            sendingWindowEnd=request.sending_window_end,
            sendingDays=request.sending_days,
            randomizationMinutes=request.randomization_minutes,
            dailySendLimit=request.daily_send_limit
        )

    def update_campaign(
        self,
        campaign_id: str,
        name: Optional[str] = None,
        description: Optional[str] = None,
        **kwargs
    ) -> bool:
        """Update an existing campaign."""
        update_data = {}
        if name is not None:
            update_data['name'] = name
        if description is not None:
            update_data['description'] = description
        update_data.update(kwargs)
        return self.api.update_campaign(campaign_id, **update_data)

    def delete_campaign(self, campaign_id: str) -> bool:
        """Delete a campaign (Admin only)."""
        return self.api.delete_campaign(campaign_id)

    def activate_campaign(self, campaign_id: str) -> bool:
        """Activate a campaign."""
        logger.info(f"Activating campaign {campaign_id}")
        return self.api.activate_campaign(campaign_id)

    def pause_campaign(self, campaign_id: str) -> bool:
        """Pause a campaign."""
        logger.info(f"Pausing campaign {campaign_id}")
        return self.api.pause_campaign(campaign_id)

    def get_campaign_statistics(self, campaign_id: str) -> CampaignStatistics:
        """Get campaign statistics."""
        return self.api.get_campaign_statistics(campaign_id)

    # Email Steps
    def get_email_steps(self, campaign_id: str) -> List[EmailStep]:
        """Get email steps for a campaign."""
        return self.api.get_campaign_steps(campaign_id)

    def create_email_step(
        self,
        campaign_id: str,
        step_number: int,
        subject: str,
        body: str,
        delay_days: int = 0
    ) -> EmailStep:
        """Create a new email step."""
        return self.api.create_email_step(
            campaign_id=campaign_id,
            step_number=step_number,
            subject=subject,
            body=body,
            delay_days=delay_days
        )

    def update_email_step(
        self,
        step_id: str,
        subject: Optional[str] = None,
        body: Optional[str] = None,
        delay_days: Optional[int] = None
    ) -> bool:
        """Update an email step."""
        update_data = {}
        if subject is not None:
            update_data['subject'] = subject
        if body is not None:
            update_data['body'] = body
        if delay_days is not None:
            update_data['delayDays'] = delay_days
        return self.api.update_email_step(step_id, **update_data)

    def delete_email_step(self, step_id: str) -> bool:
        """Delete an email step."""
        return self.api.delete_email_step(step_id)

    def get_active_campaigns_count(self) -> int:
        """Get count of active campaigns."""
        campaigns = self.get_all_campaigns()
        return sum(1 for c in campaigns if c.status == CampaignStatus.ACTIVE)

    def get_campaigns_by_status(self, status: CampaignStatus) -> List[Campaign]:
        """Get campaigns filtered by status."""
        campaigns = self.get_all_campaigns()
        return [c for c in campaigns if c.status == status]
