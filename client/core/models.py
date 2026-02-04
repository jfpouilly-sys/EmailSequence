"""Data models matching the .NET API DTOs."""
from dataclasses import dataclass, field
from datetime import datetime, time
from enum import Enum
from typing import Optional, Dict, List
from uuid import UUID


class CampaignStatus(str, Enum):
    """Campaign status enum."""
    DRAFT = "Draft"
    ACTIVE = "Active"
    PAUSED = "Paused"
    COMPLETED = "Completed"
    CANCELLED = "Cancelled"


class UserRole(str, Enum):
    """User role enum."""
    ADMIN = "Admin"
    MANAGER = "Manager"
    USER = "User"


class ContactStatus(str, Enum):
    """Contact engagement status."""
    PENDING = "Pending"
    IN_PROGRESS = "InProgress"
    COMPLETED = "Completed"
    REPLIED = "Replied"
    UNSUBSCRIBED = "Unsubscribed"
    BOUNCED = "Bounced"
    SKIPPED = "Skipped"


class UnsubscribeScope(str, Enum):
    """Unsubscribe scope."""
    GLOBAL = "Global"
    CAMPAIGN = "Campaign"


class UnsubscribeSource(str, Enum):
    """How email was suppressed."""
    MANUAL = "Manual"
    REPLY = "Reply"
    BOUNCE = "Bounce"
    COMPLAINT = "Complaint"
    IMPORT = "Import"


class DeliveryMode(str, Enum):
    """Email delivery method for attachments."""
    ATTACHMENT = "Attachment"
    LINK = "Link"


class ABTestElement(str, Enum):
    """A/B test variables."""
    SUBJECT = "Subject"
    BODY = "Body"
    SEND_TIME = "SendTime"


class ABTestStatus(str, Enum):
    """A/B test state."""
    DRAFT = "Draft"
    RUNNING = "Running"
    COMPLETED = "Completed"


@dataclass
class LoginResponse:
    """Response from login endpoint."""
    token: str
    username: str
    email: str
    role: UserRole
    expires_at: datetime
    user_id: Optional[str] = None

    @classmethod
    def from_dict(cls, data: dict) -> 'LoginResponse':
        return cls(
            token=data['token'],
            username=data['username'],
            email=data['email'],
            role=UserRole(data['role']),
            expires_at=datetime.fromisoformat(data['expiresAt'].replace('Z', '+00:00')),
            user_id=data.get('userId')
        )


@dataclass
class User:
    """User model."""
    user_id: str
    username: str
    email: str
    role: UserRole
    full_name: Optional[str] = None
    is_active: bool = True
    created_at: Optional[datetime] = None
    last_login: Optional[datetime] = None

    @classmethod
    def from_dict(cls, data: dict) -> 'User':
        return cls(
            user_id=data.get('userId', ''),
            username=data['username'],
            email=data['email'],
            role=UserRole(data['role']),
            full_name=data.get('fullName'),
            is_active=data.get('isActive', True),
            created_at=datetime.fromisoformat(data['createdAt'].replace('Z', '+00:00')) if data.get('createdAt') else None,
            last_login=datetime.fromisoformat(data['lastLogin'].replace('Z', '+00:00')) if data.get('lastLogin') else None
        )


@dataclass
class Campaign:
    """Campaign model."""
    campaign_id: str
    name: str
    campaign_ref: str
    status: CampaignStatus
    description: Optional[str] = None
    owner_user_id: Optional[str] = None
    contact_list_id: Optional[str] = None
    inter_email_delay_minutes: int = 5
    sequence_step_delay_days: int = 3
    sending_window_start: Optional[str] = "09:00"
    sending_window_end: Optional[str] = "17:00"
    sending_days: str = "Monday,Tuesday,Wednesday,Thursday,Friday"
    randomization_minutes: int = 15
    daily_send_limit: int = 100
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    total_contacts: int = 0
    emails_sent: int = 0
    response_rate: float = 0.0

    @classmethod
    def from_dict(cls, data: dict) -> 'Campaign':
        return cls(
            campaign_id=str(data.get('campaignId', '')),
            name=data['name'],
            campaign_ref=data.get('campaignRef', ''),
            status=CampaignStatus(data.get('status', 'Draft')),
            description=data.get('description'),
            owner_user_id=str(data['ownerUserId']) if data.get('ownerUserId') else None,
            contact_list_id=str(data['contactListId']) if data.get('contactListId') else None,
            inter_email_delay_minutes=data.get('interEmailDelayMinutes', 5),
            sequence_step_delay_days=data.get('sequenceStepDelayDays', 3),
            sending_window_start=data.get('sendingWindowStart', '09:00:00'),
            sending_window_end=data.get('sendingWindowEnd', '17:00:00'),
            sending_days=data.get('sendingDays', 'Monday,Tuesday,Wednesday,Thursday,Friday'),
            randomization_minutes=data.get('randomizationMinutes', 15),
            daily_send_limit=data.get('dailySendLimit', 100),
            start_date=datetime.fromisoformat(data['startDate'].replace('Z', '+00:00')) if data.get('startDate') else None,
            end_date=datetime.fromisoformat(data['endDate'].replace('Z', '+00:00')) if data.get('endDate') else None,
            created_at=datetime.fromisoformat(data['createdAt'].replace('Z', '+00:00')) if data.get('createdAt') else None,
            updated_at=datetime.fromisoformat(data['updatedAt'].replace('Z', '+00:00')) if data.get('updatedAt') else None,
            total_contacts=data.get('totalContacts', 0),
            emails_sent=data.get('emailsSent', 0),
            response_rate=data.get('responseRate', 0.0)
        )


@dataclass
class ContactList:
    """Contact list model."""
    list_id: str
    name: str
    description: Optional[str] = None
    owner_user_id: Optional[str] = None
    custom_field_labels: Dict[str, str] = field(default_factory=dict)
    contact_count: int = 0
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    @classmethod
    def from_dict(cls, data: dict) -> 'ContactList':
        return cls(
            list_id=str(data.get('listId', '')),
            name=data['name'],
            description=data.get('description'),
            owner_user_id=str(data['ownerUserId']) if data.get('ownerUserId') else None,
            custom_field_labels=data.get('customFieldLabels', {}),
            contact_count=data.get('contactCount', 0),
            created_at=datetime.fromisoformat(data['createdAt'].replace('Z', '+00:00')) if data.get('createdAt') else None,
            updated_at=datetime.fromisoformat(data['updatedAt'].replace('Z', '+00:00')) if data.get('updatedAt') else None
        )


@dataclass
class Contact:
    """Contact model."""
    contact_id: str
    list_id: str
    email: str
    first_name: str
    last_name: str
    company: str
    title: Optional[str] = None
    position: Optional[str] = None
    phone: Optional[str] = None
    linkedin_url: Optional[str] = None
    source: Optional[str] = None
    custom_fields: Dict[str, Optional[str]] = field(default_factory=dict)
    status: ContactStatus = ContactStatus.PENDING
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    @classmethod
    def from_dict(cls, data: dict) -> 'Contact':
        return cls(
            contact_id=str(data.get('contactId', '')),
            list_id=str(data.get('listId', '')),
            email=data['email'],
            first_name=data.get('firstName', ''),
            last_name=data.get('lastName', ''),
            company=data.get('company', ''),
            title=data.get('title'),
            position=data.get('position'),
            phone=data.get('phone'),
            linkedin_url=data.get('linkedInUrl'),
            source=data.get('source'),
            custom_fields=data.get('customFields', {}),
            status=ContactStatus(data.get('status', 'Pending')),
            created_at=datetime.fromisoformat(data['createdAt'].replace('Z', '+00:00')) if data.get('createdAt') else None,
            updated_at=datetime.fromisoformat(data['updatedAt'].replace('Z', '+00:00')) if data.get('updatedAt') else None
        )

    @property
    def full_name(self) -> str:
        return f"{self.first_name} {self.last_name}".strip()


@dataclass
class EmailStep:
    """Email sequence step model."""
    step_id: str
    campaign_id: str
    step_number: int
    subject: str
    body: str
    delay_days: int = 0
    is_active: bool = True
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    @classmethod
    def from_dict(cls, data: dict) -> 'EmailStep':
        return cls(
            step_id=str(data.get('stepId', '')),
            campaign_id=str(data.get('campaignId', '')),
            step_number=data.get('stepNumber', 1),
            subject=data.get('subject', ''),
            body=data.get('body', ''),
            delay_days=data.get('delayDays', 0),
            is_active=data.get('isActive', True),
            created_at=datetime.fromisoformat(data['createdAt'].replace('Z', '+00:00')) if data.get('createdAt') else None,
            updated_at=datetime.fromisoformat(data['updatedAt'].replace('Z', '+00:00')) if data.get('updatedAt') else None
        )


@dataclass
class Attachment:
    """Email attachment model."""
    attachment_id: str
    step_id: str
    file_name: str
    file_size: int
    delivery_mode: DeliveryMode = DeliveryMode.ATTACHMENT
    download_token: Optional[str] = None
    download_count: int = 0

    @classmethod
    def from_dict(cls, data: dict) -> 'Attachment':
        return cls(
            attachment_id=str(data.get('attachmentId', '')),
            step_id=str(data.get('stepId', '')),
            file_name=data.get('fileName', ''),
            file_size=data.get('fileSize', 0),
            delivery_mode=DeliveryMode(data.get('deliveryMode', 'Attachment')),
            download_token=data.get('downloadToken'),
            download_count=data.get('downloadCount', 0)
        )


@dataclass
class SuppressionEntry:
    """Suppression list entry model."""
    suppression_id: str
    email: str
    scope: UnsubscribeScope
    source: UnsubscribeSource
    campaign_id: Optional[str] = None
    reason: Optional[str] = None
    created_at: Optional[datetime] = None

    @classmethod
    def from_dict(cls, data: dict) -> 'SuppressionEntry':
        return cls(
            suppression_id=str(data.get('suppressionId', '')),
            email=data['email'],
            scope=UnsubscribeScope(data.get('scope', 'Global')),
            source=UnsubscribeSource(data.get('source', 'Manual')),
            campaign_id=str(data['campaignId']) if data.get('campaignId') else None,
            reason=data.get('reason'),
            created_at=datetime.fromisoformat(data['createdAt'].replace('Z', '+00:00')) if data.get('createdAt') else None
        )


@dataclass
class MailAccount:
    """Mail account model."""
    account_id: str
    email_address: str
    display_name: str
    is_active: bool = True
    daily_limit: int = 100
    hourly_limit: int = 20
    warmup_enabled: bool = False
    warmup_day: int = 0
    emails_sent_today: int = 0
    emails_sent_this_hour: int = 0

    @classmethod
    def from_dict(cls, data: dict) -> 'MailAccount':
        return cls(
            account_id=str(data.get('accountId', '')),
            email_address=data['emailAddress'],
            display_name=data.get('displayName', ''),
            is_active=data.get('isActive', True),
            daily_limit=data.get('dailyLimit', 100),
            hourly_limit=data.get('hourlyLimit', 20),
            warmup_enabled=data.get('warmupEnabled', False),
            warmup_day=data.get('warmupDay', 0),
            emails_sent_today=data.get('emailsSentToday', 0),
            emails_sent_this_hour=data.get('emailsSentThisHour', 0)
        )


@dataclass
class ABTest:
    """A/B test model."""
    test_id: str
    campaign_id: str
    step_id: str
    name: str
    element: ABTestElement
    variant_a: str
    variant_b: str
    status: ABTestStatus = ABTestStatus.DRAFT
    split_percentage: int = 50
    variant_a_sent: int = 0
    variant_b_sent: int = 0
    variant_a_opens: int = 0
    variant_b_opens: int = 0
    winner: Optional[str] = None

    @classmethod
    def from_dict(cls, data: dict) -> 'ABTest':
        return cls(
            test_id=str(data.get('testId', '')),
            campaign_id=str(data.get('campaignId', '')),
            step_id=str(data.get('stepId', '')),
            name=data.get('name', ''),
            element=ABTestElement(data.get('element', 'Subject')),
            variant_a=data.get('variantA', ''),
            variant_b=data.get('variantB', ''),
            status=ABTestStatus(data.get('status', 'Draft')),
            split_percentage=data.get('splitPercentage', 50),
            variant_a_sent=data.get('variantASent', 0),
            variant_b_sent=data.get('variantBSent', 0),
            variant_a_opens=data.get('variantAOpens', 0),
            variant_b_opens=data.get('variantBOpens', 0),
            winner=data.get('winner')
        )


@dataclass
class OverallStatistics:
    """Overall statistics model."""
    total_campaigns: int = 0
    active_campaigns: int = 0
    total_emails_sent: int = 0
    total_contacts: int = 0

    @classmethod
    def from_dict(cls, data: dict) -> 'OverallStatistics':
        return cls(
            total_campaigns=data.get('totalCampaigns', 0),
            active_campaigns=data.get('activeCampaigns', 0),
            total_emails_sent=data.get('totalEmailsSent', 0),
            total_contacts=data.get('totalContacts', 0)
        )


@dataclass
class CampaignStatistics:
    """Campaign-specific statistics model."""
    campaign_id: str
    total_contacts: int = 0
    emails_sent: int = 0
    emails_pending: int = 0
    replies: int = 0
    unsubscribes: int = 0
    bounces: int = 0
    response_rate: float = 0.0
    completion_rate: float = 0.0

    @classmethod
    def from_dict(cls, data: dict) -> 'CampaignStatistics':
        return cls(
            campaign_id=str(data.get('campaignId', '')),
            total_contacts=data.get('totalContacts', 0),
            emails_sent=data.get('emailsSent', 0),
            emails_pending=data.get('emailsPending', 0),
            replies=data.get('replies', 0),
            unsubscribes=data.get('unsubscribes', 0),
            bounces=data.get('bounces', 0),
            response_rate=data.get('responseRate', 0.0),
            completion_rate=data.get('completionRate', 0.0)
        )
