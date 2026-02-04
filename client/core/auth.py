"""Authentication and token management."""
import logging
from datetime import datetime, timedelta
from typing import Optional, Callable
import keyring

from .models import LoginResponse, UserRole

logger = logging.getLogger(__name__)

KEYRING_SERVICE = "LeadGenerator"
KEYRING_TOKEN_KEY = "jwt_token"
KEYRING_USER_KEY = "current_user"


class AuthManager:
    """Manages authentication state and token storage."""

    def __init__(self):
        self._token: Optional[str] = None
        self._user: Optional[LoginResponse] = None
        self._on_session_expired: Optional[Callable[[], None]] = None

    @property
    def token(self) -> Optional[str]:
        """Get the current JWT token."""
        return self._token

    @property
    def user(self) -> Optional[LoginResponse]:
        """Get the current logged-in user info."""
        return self._user

    @property
    def is_authenticated(self) -> bool:
        """Check if user is currently authenticated."""
        if not self._token or not self._user:
            return False
        return not self.is_token_expired

    @property
    def is_token_expired(self) -> bool:
        """Check if the token has expired."""
        if not self._user:
            return True
        return datetime.now(self._user.expires_at.tzinfo) >= self._user.expires_at

    @property
    def user_role(self) -> Optional[UserRole]:
        """Get the current user's role."""
        return self._user.role if self._user else None

    def is_admin(self) -> bool:
        """Check if current user is an admin."""
        return self.user_role == UserRole.ADMIN

    def is_manager_or_admin(self) -> bool:
        """Check if current user is a manager or admin."""
        return self.user_role in (UserRole.ADMIN, UserRole.MANAGER)

    def set_on_session_expired(self, callback: Callable[[], None]) -> None:
        """Set callback to be called when session expires."""
        self._on_session_expired = callback

    def login(self, response: LoginResponse) -> None:
        """Store login response and token."""
        self._token = response.token
        self._user = response
        self._save_to_keyring()
        logger.info(f"User {response.username} logged in successfully")

    def logout(self) -> None:
        """Clear authentication state."""
        username = self._user.username if self._user else "Unknown"
        self._token = None
        self._user = None
        self._clear_keyring()
        logger.info(f"User {username} logged out")

    def refresh_token(self, new_token: str, expires_at: datetime) -> None:
        """Update token after refresh."""
        self._token = new_token
        if self._user:
            self._user = LoginResponse(
                token=new_token,
                username=self._user.username,
                email=self._user.email,
                role=self._user.role,
                expires_at=expires_at,
                user_id=self._user.user_id
            )
        self._save_to_keyring()
        logger.debug("Token refreshed successfully")

    def check_session(self) -> bool:
        """Check if session is still valid, trigger callback if expired."""
        if self.is_token_expired:
            if self._on_session_expired:
                self._on_session_expired()
            return False
        return True

    def get_time_until_expiry(self) -> Optional[timedelta]:
        """Get time remaining until token expires."""
        if not self._user:
            return None
        now = datetime.now(self._user.expires_at.tzinfo)
        return self._user.expires_at - now

    def try_restore_session(self) -> bool:
        """Try to restore session from keyring."""
        try:
            token = keyring.get_password(KEYRING_SERVICE, KEYRING_TOKEN_KEY)
            if token:
                logger.debug("Found stored token, but session restore requires re-login")
                return False
        except Exception as e:
            logger.warning(f"Failed to read from keyring: {e}")
        return False

    def _save_to_keyring(self) -> None:
        """Save token to system keyring for secure storage."""
        if not self._token:
            return
        try:
            keyring.set_password(KEYRING_SERVICE, KEYRING_TOKEN_KEY, self._token)
            logger.debug("Token saved to keyring")
        except Exception as e:
            logger.warning(f"Failed to save token to keyring: {e}")

    def _clear_keyring(self) -> None:
        """Clear stored token from keyring."""
        try:
            keyring.delete_password(KEYRING_SERVICE, KEYRING_TOKEN_KEY)
            logger.debug("Token cleared from keyring")
        except keyring.errors.PasswordDeleteError:
            pass
        except Exception as e:
            logger.warning(f"Failed to clear keyring: {e}")
