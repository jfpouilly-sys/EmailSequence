"""Custom exceptions for Lead Generator Standalone."""


class LeadGeneratorError(Exception):
    """Base exception for Lead Generator."""
    pass


class DatabaseError(LeadGeneratorError):
    """Database operation error."""
    pass


class ValidationError(LeadGeneratorError):
    """Data validation error."""
    pass


class OutlookError(LeadGeneratorError):
    """Outlook integration error."""
    pass


class DuplicateContactError(ValidationError):
    """Duplicate contact detected."""

    def __init__(self, email: str, list_id: int):
        self.email = email
        self.list_id = list_id
        super().__init__(f"Contact with email '{email}' already exists in list {list_id}")


class SuppressionError(LeadGeneratorError):
    """Suppression list error."""
    pass


class CampaignError(LeadGeneratorError):
    """Campaign operation error."""
    pass


class TemplateError(LeadGeneratorError):
    """Template processing error."""
    pass


class CSVImportError(LeadGeneratorError):
    """CSV import error."""

    def __init__(self, message: str, row_number: int = None, field: str = None):
        self.row_number = row_number
        self.field = field
        if row_number:
            message = f"Row {row_number}: {message}"
        if field:
            message = f"{message} (field: {field})"
        super().__init__(message)


class WorkerError(LeadGeneratorError):
    """Background worker error."""
    pass
