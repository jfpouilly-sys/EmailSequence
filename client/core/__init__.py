"""Core module for Lead Generator Python client."""
from .api_client import ApiClient
from .auth import AuthManager
from .models import (
    User, Campaign, Contact, ContactList, EmailStep,
    LoginResponse, CampaignStatus, UserRole
)
from .exceptions import (
    ApiError, AuthenticationError, AuthorizationError,
    NotFoundError, ValidationError, ConnectionError
)

__all__ = [
    'ApiClient', 'AuthManager',
    'User', 'Campaign', 'Contact', 'ContactList', 'EmailStep',
    'LoginResponse', 'CampaignStatus', 'UserRole',
    'ApiError', 'AuthenticationError', 'AuthorizationError',
    'NotFoundError', 'ValidationError', 'ConnectionError'
]
