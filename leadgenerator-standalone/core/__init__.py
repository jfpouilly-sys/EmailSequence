"""Core module for Lead Generator Standalone."""

from .database import Database, get_db, init_database, get_setting, set_setting, generate_campaign_ref
from .models import (
    Contact, ContactList, Campaign, EmailStep, Attachment,
    CampaignContact, EmailLog, SuppressionEntry, QueuedEmail
)
from .exceptions import (
    LeadGeneratorError, DatabaseError, ValidationError, OutlookError,
    DuplicateContactError, SuppressionError, CampaignError
)

__all__ = [
    'Database', 'get_db', 'init_database', 'get_setting', 'set_setting', 'generate_campaign_ref',
    'Contact', 'ContactList', 'Campaign', 'EmailStep', 'Attachment',
    'CampaignContact', 'EmailLog', 'SuppressionEntry', 'QueuedEmail',
    'LeadGeneratorError', 'DatabaseError', 'ValidationError', 'OutlookError',
    'DuplicateContactError', 'SuppressionError', 'CampaignError'
]
