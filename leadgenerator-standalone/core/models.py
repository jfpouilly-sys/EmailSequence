"""Data models for Lead Generator Standalone."""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional, List
from enum import Enum


class CampaignStatus(str, Enum):
    DRAFT = "Draft"
    ACTIVE = "Active"
    PAUSED = "Paused"
    COMPLETED = "Completed"
    ARCHIVED = "Archived"


class ContactStatus(str, Enum):
    PENDING = "Pending"
    IN_PROGRESS = "InProgress"
    RESPONDED = "Responded"
    COMPLETED = "Completed"
    BOUNCED = "Bounced"
    UNSUBSCRIBED = "Unsubscribed"
    OPTED_OUT = "OptedOut"
    PAUSED = "Paused"


class EmailStatus(str, Enum):
    SENT = "Sent"
    FAILED = "Failed"
    BOUNCED = "Bounced"


class QueueStatus(str, Enum):
    PENDING = "Pending"
    SENDING = "Sending"
    SENT = "Sent"
    FAILED = "Failed"
    SKIPPED = "Skipped"


class SuppressionScope(str, Enum):
    GLOBAL = "Global"
    CAMPAIGN = "Campaign"


class SuppressionSource(str, Enum):
    EMAIL_REPLY = "EmailReply"
    MANUAL = "Manual"
    BOUNCE = "Bounce"
    COMPLAINT = "Complaint"


@dataclass
class ContactList:
    """Contact list model."""
    list_id: Optional[int] = None
    name: str = ""
    description: Optional[str] = None
    custom1_label: Optional[str] = None
    custom2_label: Optional[str] = None
    custom3_label: Optional[str] = None
    custom4_label: Optional[str] = None
    custom5_label: Optional[str] = None
    custom6_label: Optional[str] = None
    custom7_label: Optional[str] = None
    custom8_label: Optional[str] = None
    custom9_label: Optional[str] = None
    custom10_label: Optional[str] = None
    created_at: Optional[str] = None
    updated_at: Optional[str] = None
    contact_count: int = 0  # Computed field

    def get_custom_labels(self) -> dict:
        """Get dictionary of custom field labels."""
        return {
            f"custom{i}": getattr(self, f"custom{i}_label")
            for i in range(1, 11)
            if getattr(self, f"custom{i}_label")
        }


@dataclass
class Contact:
    """Contact model."""
    contact_id: Optional[int] = None
    list_id: int = 0
    title: Optional[str] = None
    first_name: str = ""
    last_name: str = ""
    email: str = ""
    company: str = ""
    position: Optional[str] = None
    phone: Optional[str] = None
    linkedin_url: Optional[str] = None
    source: Optional[str] = None
    custom1: Optional[str] = None
    custom2: Optional[str] = None
    custom3: Optional[str] = None
    custom4: Optional[str] = None
    custom5: Optional[str] = None
    custom6: Optional[str] = None
    custom7: Optional[str] = None
    custom8: Optional[str] = None
    custom9: Optional[str] = None
    custom10: Optional[str] = None
    created_at: Optional[str] = None
    updated_at: Optional[str] = None

    @property
    def full_name(self) -> str:
        """Get full name."""
        parts = []
        if self.title:
            parts.append(self.title)
        if self.first_name:
            parts.append(self.first_name)
        if self.last_name:
            parts.append(self.last_name)
        return " ".join(parts)

    def get_custom_field(self, index: int) -> Optional[str]:
        """Get custom field by index (1-10)."""
        if 1 <= index <= 10:
            return getattr(self, f"custom{index}")
        return None


@dataclass
class Campaign:
    """Campaign model."""
    campaign_id: Optional[int] = None
    name: str = ""
    description: Optional[str] = None
    campaign_ref: str = ""
    contact_list_id: Optional[int] = None
    status: str = CampaignStatus.DRAFT.value
    inter_email_delay_minutes: int = 30
    sequence_step_delay_days: int = 3
    sending_window_start: str = "09:00"
    sending_window_end: str = "17:00"
    sending_days: str = "Mon,Tue,Wed,Thu,Fri"
    randomization_minutes: int = 15
    daily_send_limit: int = 50
    start_date: Optional[str] = None
    end_date: Optional[str] = None
    created_at: Optional[str] = None
    updated_at: Optional[str] = None
    # Computed fields
    steps: List['EmailStep'] = field(default_factory=list)
    stats: Optional[dict] = None
    contact_list_name: Optional[str] = None

    def get_sending_days_list(self) -> List[str]:
        """Get list of sending days."""
        return [day.strip() for day in self.sending_days.split(",")]


@dataclass
class EmailStep:
    """Email step (sequence) model."""
    step_id: Optional[int] = None
    campaign_id: int = 0
    step_number: int = 1
    subject_template: str = ""
    body_template: str = ""
    delay_days: int = 0
    is_active: bool = True
    created_at: Optional[str] = None
    updated_at: Optional[str] = None
    # Computed fields
    attachments: List['Attachment'] = field(default_factory=list)


@dataclass
class Attachment:
    """Attachment model."""
    attachment_id: Optional[int] = None
    step_id: int = 0
    file_name: str = ""
    file_path: str = ""
    file_size: int = 0
    mime_type: Optional[str] = None
    created_at: Optional[str] = None


@dataclass
class CampaignContact:
    """Campaign contact (tracking) model."""
    campaign_id: int = 0
    contact_id: int = 0
    status: str = ContactStatus.PENDING.value
    current_step: int = 0
    last_email_sent_at: Optional[str] = None
    next_email_scheduled_at: Optional[str] = None
    responded_at: Optional[str] = None
    created_at: Optional[str] = None
    updated_at: Optional[str] = None
    # Computed fields
    contact: Optional[Contact] = None


@dataclass
class EmailLog:
    """Email log model."""
    log_id: Optional[int] = None
    campaign_id: Optional[int] = None
    contact_id: Optional[int] = None
    step_id: Optional[int] = None
    subject: Optional[str] = None
    sent_at: Optional[str] = None
    status: str = EmailStatus.SENT.value
    error_message: Optional[str] = None
    outlook_entry_id: Optional[str] = None
    # Computed fields
    contact_name: Optional[str] = None
    contact_email: Optional[str] = None


@dataclass
class SuppressionEntry:
    """Suppression list entry model."""
    email: str = ""
    scope: str = SuppressionScope.GLOBAL.value
    source: str = SuppressionSource.MANUAL.value
    campaign_id: Optional[int] = None
    reason: Optional[str] = None
    created_at: Optional[str] = None


@dataclass
class QueuedEmail:
    """Queued email model."""
    queue_id: Optional[int] = None
    campaign_id: int = 0
    contact_id: int = 0
    step_id: int = 0
    scheduled_at: str = ""
    status: str = QueueStatus.PENDING.value
    attempts: int = 0
    last_attempt_at: Optional[str] = None
    error_message: Optional[str] = None
    created_at: Optional[str] = None
    # Computed fields
    contact: Optional[Contact] = None
    step: Optional[EmailStep] = None
    campaign: Optional[Campaign] = None


@dataclass
class MailAccount:
    """Mail account model."""
    account_id: Optional[int] = None
    email_address: str = ""
    display_name: Optional[str] = None
    daily_limit: int = 50
    hourly_limit: int = 10
    current_daily_count: int = 0
    last_count_reset: Optional[str] = None
    is_active: bool = True
    created_at: Optional[str] = None


@dataclass
class OutlookEmail:
    """Outlook email message model (for inbox scanning)."""
    entry_id: str = ""
    sender_email: str = ""
    sender_name: Optional[str] = None
    subject: str = ""
    body: str = ""
    received_at: str = ""
    is_read: bool = False
