"""Custom exceptions for the Lead Generator client."""
from typing import Optional


class ApiError(Exception):
    """Base exception for API errors."""

    def __init__(self, message: str, status_code: Optional[int] = None, details: Optional[str] = None):
        super().__init__(message)
        self.message = message
        self.status_code = status_code
        self.details = details

    def __str__(self) -> str:
        if self.status_code:
            return f"[{self.status_code}] {self.message}"
        return self.message


class AuthenticationError(ApiError):
    """Raised when authentication fails (401)."""

    def __init__(self, message: str = "Authentication failed", details: Optional[str] = None):
        super().__init__(message, status_code=401, details=details)


class AuthorizationError(ApiError):
    """Raised when user lacks permission (403)."""

    def __init__(self, message: str = "Access denied", details: Optional[str] = None):
        super().__init__(message, status_code=403, details=details)


class NotFoundError(ApiError):
    """Raised when resource is not found (404)."""

    def __init__(self, message: str = "Resource not found", details: Optional[str] = None):
        super().__init__(message, status_code=404, details=details)


class ValidationError(ApiError):
    """Raised when request validation fails (400)."""

    def __init__(self, message: str = "Validation failed", details: Optional[str] = None):
        super().__init__(message, status_code=400, details=details)


class ConnectionError(ApiError):
    """Raised when connection to API fails."""

    def __init__(self, message: str = "Failed to connect to server", details: Optional[str] = None):
        super().__init__(message, status_code=None, details=details)


class TokenExpiredError(AuthenticationError):
    """Raised when JWT token has expired."""

    def __init__(self, message: str = "Session expired, please login again"):
        super().__init__(message)


class ServerError(ApiError):
    """Raised when server returns 5xx error."""

    def __init__(self, message: str = "Server error occurred", status_code: int = 500, details: Optional[str] = None):
        super().__init__(message, status_code=status_code, details=details)
