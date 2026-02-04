"""CSV import/export service using pandas."""
import logging
from typing import List, Dict, Any, Optional, Tuple
from io import BytesIO, StringIO
from dataclasses import dataclass

import pandas as pd

from core.models import Contact

logger = logging.getLogger(__name__)


@dataclass
class FieldMapping:
    """Mapping between CSV column and contact field."""
    csv_column: str
    contact_field: str
    is_custom: bool = False
    custom_index: Optional[int] = None


@dataclass
class ValidationResult:
    """Result of CSV validation."""
    is_valid: bool
    total_rows: int
    valid_rows: int
    invalid_rows: int
    errors: List[Dict[str, Any]]
    warnings: List[str]


class CsvService:
    """Service for CSV import/export operations."""

    # Standard field mappings (CSV header -> Contact field)
    STANDARD_FIELD_NAMES = {
        "email": ["email", "e-mail", "email address", "courriel"],
        "first_name": ["first name", "firstname", "first", "prenom", "pr\u00e9nom"],
        "last_name": ["last name", "lastname", "last", "surname", "nom", "nom de famille"],
        "company": ["company", "organization", "organisation", "entreprise", "soci\u00e9t\u00e9"],
        "title": ["title", "salutation", "civilit\u00e9"],
        "position": ["position", "job title", "role", "titre", "poste", "fonction"],
        "phone": ["phone", "telephone", "mobile", "t\u00e9l\u00e9phone", "tel"],
        "linkedin_url": ["linkedin", "linkedin url", "linkedin profile"],
        "source": ["source", "lead source", "origine"],
    }

    def __init__(self):
        self._current_df: Optional[pd.DataFrame] = None
        self._field_mappings: List[FieldMapping] = []

    def read_csv(
        self,
        file_path: Optional[str] = None,
        file_content: Optional[bytes] = None,
        encoding: str = "utf-8"
    ) -> pd.DataFrame:
        """Read CSV file and return DataFrame."""
        try:
            if file_path:
                self._current_df = pd.read_csv(file_path, encoding=encoding)
            elif file_content:
                self._current_df = pd.read_csv(
                    BytesIO(file_content),
                    encoding=encoding
                )
            else:
                raise ValueError("Either file_path or file_content must be provided")

            # Clean column names
            self._current_df.columns = [
                str(col).strip().lower() for col in self._current_df.columns
            ]

            logger.info(f"Loaded CSV with {len(self._current_df)} rows and {len(self._current_df.columns)} columns")
            return self._current_df

        except UnicodeDecodeError:
            # Try with different encoding
            if encoding != "latin-1":
                return self.read_csv(file_path, file_content, encoding="latin-1")
            raise

    def get_columns(self) -> List[str]:
        """Get column names from current DataFrame."""
        if self._current_df is None:
            return []
        return list(self._current_df.columns)

    def get_preview(self, rows: int = 5) -> List[Dict[str, Any]]:
        """Get preview of first N rows."""
        if self._current_df is None:
            return []
        return self._current_df.head(rows).to_dict('records')

    def auto_detect_mappings(self) -> List[FieldMapping]:
        """Auto-detect field mappings based on column names."""
        if self._current_df is None:
            return []

        mappings = []
        columns = self.get_columns()
        used_fields = set()

        for col in columns:
            col_lower = col.lower().strip()

            # Check standard fields
            for field, aliases in self.STANDARD_FIELD_NAMES.items():
                if col_lower in aliases and field not in used_fields:
                    mappings.append(FieldMapping(
                        csv_column=col,
                        contact_field=field,
                        is_custom=False
                    ))
                    used_fields.add(field)
                    break
            else:
                # Check for custom field pattern
                for i in range(1, 11):
                    if f"custom{i}" in col_lower or f"custom {i}" in col_lower:
                        mappings.append(FieldMapping(
                            csv_column=col,
                            contact_field=f"custom{i}",
                            is_custom=True,
                            custom_index=i
                        ))
                        break

        self._field_mappings = mappings
        return mappings

    def set_mappings(self, mappings: List[FieldMapping]) -> None:
        """Set field mappings manually."""
        self._field_mappings = mappings

    def validate(self) -> ValidationResult:
        """Validate the current DataFrame with current mappings."""
        if self._current_df is None:
            return ValidationResult(
                is_valid=False,
                total_rows=0,
                valid_rows=0,
                invalid_rows=0,
                errors=[{"row": 0, "error": "No data loaded"}],
                warnings=[]
            )

        errors = []
        warnings = []
        valid_rows = 0
        invalid_rows = 0

        # Check required fields
        email_mapping = next(
            (m for m in self._field_mappings if m.contact_field == "email"),
            None
        )

        if not email_mapping:
            return ValidationResult(
                is_valid=False,
                total_rows=len(self._current_df),
                valid_rows=0,
                invalid_rows=len(self._current_df),
                errors=[{"row": 0, "error": "Email field mapping is required"}],
                warnings=[]
            )

        # Validate each row
        for idx, row in self._current_df.iterrows():
            row_errors = []

            # Check email
            email = str(row.get(email_mapping.csv_column, "")).strip()
            if not email or email == "nan":
                row_errors.append("Missing email address")
            elif "@" not in email:
                row_errors.append(f"Invalid email format: {email}")

            if row_errors:
                invalid_rows += 1
                errors.append({
                    "row": idx + 2,  # +2 for 1-indexed and header row
                    "error": "; ".join(row_errors)
                })
            else:
                valid_rows += 1

        # Check for potential issues
        if valid_rows < len(self._current_df) * 0.9:
            warnings.append(f"More than 10% of rows have validation errors")

        # Check for duplicates
        if email_mapping:
            duplicates = self._current_df[email_mapping.csv_column].duplicated().sum()
            if duplicates > 0:
                warnings.append(f"{duplicates} duplicate email addresses found")

        return ValidationResult(
            is_valid=len(errors) == 0,
            total_rows=len(self._current_df),
            valid_rows=valid_rows,
            invalid_rows=invalid_rows,
            errors=errors[:100],  # Limit errors shown
            warnings=warnings
        )

    def to_contacts_data(self) -> List[Dict[str, Any]]:
        """Convert DataFrame to list of contact dictionaries."""
        if self._current_df is None or not self._field_mappings:
            return []

        contacts = []
        for _, row in self._current_df.iterrows():
            contact_data = {}
            custom_fields = {}

            for mapping in self._field_mappings:
                value = str(row.get(mapping.csv_column, "")).strip()
                if value and value != "nan":
                    if mapping.is_custom:
                        custom_fields[f"custom{mapping.custom_index}"] = value
                    else:
                        contact_data[mapping.contact_field] = value

            if custom_fields:
                contact_data["customFields"] = custom_fields

            if contact_data.get("email"):
                contacts.append(contact_data)

        return contacts

    def to_csv_bytes(self) -> BytesIO:
        """Export current DataFrame to CSV bytes."""
        if self._current_df is None:
            return BytesIO()

        output = BytesIO()
        self._current_df.to_csv(output, index=False, encoding="utf-8")
        output.seek(0)
        return output

    def export_contacts_to_csv(self, contacts: List[Contact]) -> BytesIO:
        """Export list of contacts to CSV."""
        data = []
        for contact in contacts:
            row = {
                "Email": contact.email,
                "First Name": contact.first_name,
                "Last Name": contact.last_name,
                "Company": contact.company,
                "Title": contact.title or "",
                "Position": contact.position or "",
                "Phone": contact.phone or "",
                "LinkedIn": contact.linkedin_url or "",
                "Source": contact.source or "",
                "Status": contact.status.value,
            }
            # Add custom fields
            for i in range(1, 11):
                key = f"custom{i}"
                row[f"Custom{i}"] = contact.custom_fields.get(key, "")

            data.append(row)

        df = pd.DataFrame(data)
        output = BytesIO()
        df.to_csv(output, index=False, encoding="utf-8")
        output.seek(0)
        return output

    def get_row_count(self) -> int:
        """Get number of rows in current DataFrame."""
        return len(self._current_df) if self._current_df is not None else 0

    def clear(self) -> None:
        """Clear current data and mappings."""
        self._current_df = None
        self._field_mappings = []
