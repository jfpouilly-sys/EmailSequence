"""REST API client for communicating with the .NET backend."""
import logging
from typing import Any, Dict, List, Optional, TypeVar, Type
from io import BytesIO

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

from .auth import AuthManager
from .exceptions import (
    ApiError, AuthenticationError, AuthorizationError,
    NotFoundError, ValidationError, ConnectionError, ServerError, TokenExpiredError
)
from .models import (
    LoginResponse, User, Campaign, Contact, ContactList,
    EmailStep, Attachment, SuppressionEntry, MailAccount,
    ABTest, OverallStatistics, CampaignStatistics
)

logger = logging.getLogger(__name__)

T = TypeVar('T')


class ApiClient:
    """HTTP client for the Lead Generator .NET API."""

    def __init__(self, base_url: str, timeout: int = 30, retry_attempts: int = 3):
        self.base_url = base_url.rstrip('/')
        self.timeout = timeout
        self.auth = AuthManager()

        self.session = requests.Session()
        retry_strategy = Retry(
            total=retry_attempts,
            backoff_factor=0.5,
            status_forcelist=[502, 503, 504],
        )
        adapter = HTTPAdapter(max_retries=retry_strategy)
        self.session.mount("http://", adapter)
        self.session.mount("https://", adapter)

    def _get_headers(self) -> Dict[str, str]:
        """Get request headers with auth token if available."""
        headers = {
            "Content-Type": "application/json",
            "Accept": "application/json",
        }
        if self.auth.token:
            headers["Authorization"] = f"Bearer {self.auth.token}"
        return headers

    def _handle_response(self, response: requests.Response) -> Any:
        """Handle API response and raise appropriate exceptions."""
        try:
            if response.status_code == 204:
                return None

            if response.status_code == 401:
                raise AuthenticationError(
                    "Authentication required or token expired",
                    details=response.text
                )

            if response.status_code == 403:
                raise AuthorizationError(
                    "Access denied - insufficient permissions",
                    details=response.text
                )

            if response.status_code == 404:
                raise NotFoundError(
                    "Resource not found",
                    details=response.text
                )

            if response.status_code == 400:
                try:
                    error_data = response.json()
                    message = error_data.get('message', 'Validation failed')
                except Exception:
                    message = response.text or 'Validation failed'
                raise ValidationError(message, details=response.text)

            if response.status_code >= 500:
                raise ServerError(
                    f"Server error: {response.status_code}",
                    status_code=response.status_code,
                    details=response.text
                )

            if not response.ok:
                raise ApiError(
                    f"Request failed with status {response.status_code}",
                    status_code=response.status_code,
                    details=response.text
                )

            if response.content:
                return response.json()
            return None

        except requests.exceptions.JSONDecodeError:
            if response.ok:
                return response.text
            raise ApiError(
                f"Invalid JSON response: {response.status_code}",
                status_code=response.status_code,
                details=response.text
            )

    def _request(
        self,
        method: str,
        endpoint: str,
        data: Optional[Dict] = None,
        params: Optional[Dict] = None,
        files: Optional[Dict] = None
    ) -> Any:
        """Make an HTTP request to the API."""
        url = f"{self.base_url}{endpoint}"
        headers = self._get_headers()

        if files:
            headers.pop("Content-Type", None)

        try:
            response = self.session.request(
                method=method,
                url=url,
                headers=headers,
                json=data if not files else None,
                data=data if files else None,
                params=params,
                files=files,
                timeout=self.timeout
            )
            return self._handle_response(response)

        except requests.exceptions.ConnectionError as e:
            logger.error(f"Connection error: {e}")
            raise ConnectionError(
                "Failed to connect to server. Please check your network connection.",
                details=str(e)
            )
        except requests.exceptions.Timeout as e:
            logger.error(f"Request timeout: {e}")
            raise ConnectionError(
                "Request timed out. Please try again.",
                details=str(e)
            )
        except requests.exceptions.RequestException as e:
            logger.error(f"Request error: {e}")
            raise ApiError(f"Request failed: {str(e)}")

    def get(self, endpoint: str, params: Optional[Dict] = None) -> Any:
        """Make a GET request."""
        return self._request("GET", endpoint, params=params)

    def post(self, endpoint: str, data: Optional[Dict] = None, files: Optional[Dict] = None) -> Any:
        """Make a POST request."""
        return self._request("POST", endpoint, data=data, files=files)

    def put(self, endpoint: str, data: Optional[Dict] = None) -> Any:
        """Make a PUT request."""
        return self._request("PUT", endpoint, data=data)

    def delete(self, endpoint: str) -> Any:
        """Make a DELETE request."""
        return self._request("DELETE", endpoint)

    # Authentication endpoints
    def login(self, username: str, password: str) -> LoginResponse:
        """Authenticate user and get JWT token."""
        data = {"username": username, "password": password}
        response = self.post("/api/auth/login", data)
        login_response = LoginResponse.from_dict(response)
        self.auth.login(login_response)
        return login_response

    def logout(self) -> None:
        """Logout and clear authentication."""
        self.auth.logout()

    def change_password(self, current_password: str, new_password: str) -> bool:
        """Change current user's password."""
        data = {"currentPassword": current_password, "newPassword": new_password}
        self.post("/api/auth/change-password", data)
        return True

    def get_current_user(self) -> User:
        """Get current authenticated user info."""
        response = self.get("/api/auth/me")
        return User.from_dict(response)

    # Health & Version endpoints
    def health_check(self) -> bool:
        """Check if API is healthy."""
        try:
            self.get("/health")
            return True
        except Exception:
            return False

    def get_version(self) -> Dict[str, Any]:
        """Get API version information."""
        return self.get("/api/version")

    # Campaign endpoints
    def get_campaigns(self, only_mine: bool = True) -> List[Campaign]:
        """Get list of campaigns."""
        params = {"onlyMine": str(only_mine).lower()}
        response = self.get("/api/campaigns", params=params)
        return [Campaign.from_dict(c) for c in response] if response else []

    def get_campaign(self, campaign_id: str) -> Campaign:
        """Get campaign by ID."""
        response = self.get(f"/api/campaigns/{campaign_id}")
        return Campaign.from_dict(response)

    def create_campaign(
        self,
        name: str,
        description: Optional[str] = None,
        contact_list_id: Optional[str] = None,
        **kwargs
    ) -> Campaign:
        """Create a new campaign."""
        data = {
            "name": name,
            "description": description,
            "contactListId": contact_list_id,
            **kwargs
        }
        data = {k: v for k, v in data.items() if v is not None}
        response = self.post("/api/campaigns", data)
        return Campaign.from_dict(response)

    def update_campaign(self, campaign_id: str, **kwargs) -> bool:
        """Update an existing campaign."""
        data = {k: v for k, v in kwargs.items() if v is not None}
        self.put(f"/api/campaigns/{campaign_id}", data)
        return True

    def delete_campaign(self, campaign_id: str) -> bool:
        """Delete a campaign (Admin only)."""
        self.delete(f"/api/campaigns/{campaign_id}")
        return True

    def activate_campaign(self, campaign_id: str) -> bool:
        """Activate a campaign."""
        self.post(f"/api/campaigns/{campaign_id}/activate")
        return True

    def pause_campaign(self, campaign_id: str) -> bool:
        """Pause a campaign."""
        self.post(f"/api/campaigns/{campaign_id}/pause")
        return True

    # Contact List endpoints
    def get_contact_lists(self) -> List[ContactList]:
        """Get all contact lists."""
        response = self.get("/api/contactlists")
        return [ContactList.from_dict(cl) for cl in response] if response else []

    def get_contact_list(self, list_id: str) -> ContactList:
        """Get contact list by ID."""
        response = self.get(f"/api/contactlists/{list_id}")
        return ContactList.from_dict(response)

    def create_contact_list(self, name: str, description: Optional[str] = None) -> ContactList:
        """Create a new contact list."""
        data = {"name": name, "description": description}
        response = self.post("/api/contactlists", data)
        return ContactList.from_dict(response)

    # Contact endpoints
    def get_contacts(self, list_id: str) -> List[Contact]:
        """Get contacts in a list."""
        response = self.get(f"/api/contacts/list/{list_id}")
        return [Contact.from_dict(c) for c in response] if response else []

    def get_contact(self, contact_id: str) -> Contact:
        """Get contact by ID."""
        response = self.get(f"/api/contacts/{contact_id}")
        return Contact.from_dict(response)

    def create_contact(
        self,
        list_id: str,
        email: str,
        first_name: str,
        last_name: str,
        company: str,
        **kwargs
    ) -> Contact:
        """Create a new contact."""
        data = {
            "listId": list_id,
            "email": email,
            "firstName": first_name,
            "lastName": last_name,
            "company": company,
            **kwargs
        }
        response = self.post("/api/contacts", data)
        return Contact.from_dict(response)

    def update_contact(self, contact_id: str, **kwargs) -> bool:
        """Update an existing contact."""
        self.put(f"/api/contacts/{contact_id}", kwargs)
        return True

    def delete_contact(self, contact_id: str) -> bool:
        """Delete a contact."""
        self.delete(f"/api/contacts/{contact_id}")
        return True

    def import_contacts(self, list_id: str, csv_file: BytesIO, filename: str = "contacts.csv") -> Dict[str, Any]:
        """Import contacts from CSV file."""
        files = {"file": (filename, csv_file, "text/csv")}
        response = self.post(f"/api/contacts/import/{list_id}", files=files)
        return response

    # Email Step endpoints
    def get_campaign_steps(self, campaign_id: str) -> List[EmailStep]:
        """Get email steps for a campaign."""
        response = self.get(f"/api/campaigns/{campaign_id}/steps")
        return [EmailStep.from_dict(s) for s in response] if response else []

    def create_email_step(
        self,
        campaign_id: str,
        step_number: int,
        subject: str,
        body: str,
        delay_days: int = 0
    ) -> EmailStep:
        """Create a new email step."""
        data = {
            "campaignId": campaign_id,
            "stepNumber": step_number,
            "subject": subject,
            "body": body,
            "delayDays": delay_days
        }
        response = self.post(f"/api/campaigns/{campaign_id}/steps", data)
        return EmailStep.from_dict(response)

    def update_email_step(self, step_id: str, **kwargs) -> bool:
        """Update an email step."""
        self.put(f"/api/emailsteps/{step_id}", kwargs)
        return True

    def delete_email_step(self, step_id: str) -> bool:
        """Delete an email step."""
        self.delete(f"/api/emailsteps/{step_id}")
        return True

    # Attachment endpoints
    def get_step_attachments(self, step_id: str) -> List[Attachment]:
        """Get attachments for an email step."""
        response = self.get(f"/api/emailsteps/{step_id}/attachments")
        return [Attachment.from_dict(a) for a in response] if response else []

    def add_attachment(
        self,
        step_id: str,
        file: BytesIO,
        filename: str,
        delivery_mode: str = "Attachment"
    ) -> Attachment:
        """Add attachment to an email step."""
        files = {"file": (filename, file)}
        data = {"deliveryMode": delivery_mode}
        response = self.post(f"/api/emailsteps/{step_id}/attachments", data=data, files=files)
        return Attachment.from_dict(response)

    # Report endpoints
    def get_overall_statistics(self, only_mine: bool = True) -> OverallStatistics:
        """Get overall statistics."""
        params = {"onlyMine": str(only_mine).lower()}
        response = self.get("/api/reports/overall", params=params)
        return OverallStatistics.from_dict(response)

    def get_campaign_statistics(self, campaign_id: str) -> CampaignStatistics:
        """Get campaign-specific statistics."""
        response = self.get(f"/api/reports/campaign/{campaign_id}")
        return CampaignStatistics.from_dict(response)

    # Suppression endpoints
    def get_suppression_list(self) -> List[SuppressionEntry]:
        """Get suppression list."""
        response = self.get("/api/suppression")
        return [SuppressionEntry.from_dict(s) for s in response] if response else []

    def check_suppression(self, email: str, campaign_id: Optional[str] = None) -> bool:
        """Check if email is suppressed."""
        params = {}
        if campaign_id:
            params["campaignId"] = campaign_id
        response = self.get(f"/api/suppression/check/{email}", params=params)
        return response.get("isSuppressed", False)

    def add_to_suppression(
        self,
        email: str,
        scope: str = "Global",
        campaign_id: Optional[str] = None,
        reason: Optional[str] = None
    ) -> None:
        """Add email to suppression list."""
        data = {
            "email": email,
            "scope": scope,
            "campaignId": campaign_id,
            "reason": reason
        }
        data = {k: v for k, v in data.items() if v is not None}
        self.post("/api/suppression", data)

    # User Management endpoints (Admin)
    def get_users(self) -> List[User]:
        """Get all users (Admin only)."""
        response = self.get("/api/users")
        return [User.from_dict(u) for u in response] if response else []

    def create_user(
        self,
        username: str,
        email: str,
        password: str,
        role: str = "User",
        full_name: Optional[str] = None
    ) -> User:
        """Create a new user (Admin only)."""
        data = {
            "username": username,
            "email": email,
            "password": password,
            "role": role,
            "fullName": full_name
        }
        data = {k: v for k, v in data.items() if v is not None}
        response = self.post("/api/users", data)
        return User.from_dict(response)

    def update_user(self, user_id: str, **kwargs) -> bool:
        """Update a user (Admin only)."""
        self.put(f"/api/users/{user_id}", kwargs)
        return True

    # Mail Account endpoints (Admin)
    def get_mail_accounts(self) -> List[MailAccount]:
        """Get all mail accounts (Admin only)."""
        response = self.get("/api/mailaccounts")
        return [MailAccount.from_dict(m) for m in response] if response else []

    def create_mail_account(
        self,
        email_address: str,
        display_name: str,
        daily_limit: int = 100,
        hourly_limit: int = 20
    ) -> MailAccount:
        """Create a mail account (Admin only)."""
        data = {
            "emailAddress": email_address,
            "displayName": display_name,
            "dailyLimit": daily_limit,
            "hourlyLimit": hourly_limit
        }
        response = self.post("/api/mailaccounts", data)
        return MailAccount.from_dict(response)

    def update_mail_account(self, account_id: str, **kwargs) -> bool:
        """Update a mail account (Admin only)."""
        self.put(f"/api/mailaccounts/{account_id}", kwargs)
        return True
