"""CSV import/export service for Lead Generator Standalone."""

import csv
import logging
import re
from pathlib import Path
from typing import List, Dict, Tuple, Optional, Any

import pandas as pd

from core.database import get_db
from core.exceptions import CSVImportError, ValidationError
from services.contact_service import ContactService

logger = logging.getLogger(__name__)


# Common column name mappings for auto-detection (English and French)
COLUMN_MAPPINGS = {
    # Title
    'title': 'title',
    'titre': 'title',
    'civilité': 'title',
    'civilite': 'title',
    'salutation': 'title',
    'prefix': 'title',

    # First Name
    'first_name': 'first_name',
    'firstname': 'first_name',
    'first name': 'first_name',
    'prénom': 'first_name',
    'prenom': 'first_name',
    'given_name': 'first_name',

    # Last Name
    'last_name': 'last_name',
    'lastname': 'last_name',
    'last name': 'last_name',
    'nom': 'last_name',
    'family_name': 'last_name',
    'surname': 'last_name',

    # Email
    'email': 'email',
    'e-mail': 'email',
    'email_address': 'email',
    'emailaddress': 'email',
    'mail': 'email',
    'courriel': 'email',
    'adresse email': 'email',

    # Company
    'company': 'company',
    'company_name': 'company',
    'companyname': 'company',
    'société': 'company',
    'societe': 'company',
    'entreprise': 'company',
    'organization': 'company',
    'organisation': 'company',
    'org': 'company',

    # Position/Title
    'position': 'position',
    'job_title': 'position',
    'jobtitle': 'position',
    'job title': 'position',
    'fonction': 'position',
    'poste': 'position',
    'role': 'position',
    'titre du poste': 'position',

    # Phone
    'phone': 'phone',
    'telephone': 'phone',
    'téléphone': 'phone',
    'phone_number': 'phone',
    'phonenumber': 'phone',
    'mobile': 'phone',
    'tel': 'phone',

    # LinkedIn
    'linkedin': 'linkedin_url',
    'linkedin_url': 'linkedin_url',
    'linkedinurl': 'linkedin_url',
    'linkedin url': 'linkedin_url',
    'linkedin profile': 'linkedin_url',

    # Source
    'source': 'source',
    'lead_source': 'source',
    'origine': 'source',
}

# Standard fields for import
STANDARD_FIELDS = [
    'title', 'first_name', 'last_name', 'email', 'company',
    'position', 'phone', 'linkedin_url', 'source'
]

# Custom fields
CUSTOM_FIELDS = [f'custom{i}' for i in range(1, 11)]


class CSVService:
    """Service for CSV import/export operations."""

    def __init__(self):
        self.contact_service = ContactService()

    def read_csv_preview(
        self,
        file_path: str,
        max_rows: int = 5
    ) -> Tuple[List[str], List[List[str]], int]:
        """
        Read CSV file and return preview data.

        Returns:
            Tuple of (headers, preview_rows, total_count)
        """
        file_path = Path(file_path)
        if not file_path.exists():
            raise CSVImportError(f"File not found: {file_path}")

        try:
            # Detect encoding
            encoding = self._detect_encoding(file_path)

            # Read with pandas for robust handling
            df = pd.read_csv(file_path, encoding=encoding, nrows=max_rows + 1)

            headers = list(df.columns)
            preview_rows = df.head(max_rows).fillna('').values.tolist()

            # Count total rows
            with open(file_path, 'r', encoding=encoding) as f:
                total_count = sum(1 for _ in f) - 1  # Subtract header row

            return headers, preview_rows, total_count

        except Exception as e:
            logger.error(f"Error reading CSV: {e}")
            raise CSVImportError(f"Failed to read CSV file: {e}")

    def auto_map_fields(self, csv_headers: List[str]) -> Dict[str, str]:
        """
        Auto-detect field mappings from CSV headers.

        Returns:
            Dict mapping CSV header to field name
        """
        mappings = {}

        for header in csv_headers:
            # Normalize header for matching
            normalized = header.lower().strip()
            normalized = re.sub(r'[_\-\s]+', ' ', normalized)

            # Direct match
            if normalized in COLUMN_MAPPINGS:
                mappings[header] = COLUMN_MAPPINGS[normalized]
            # Check without spaces/underscores
            elif normalized.replace(' ', '') in COLUMN_MAPPINGS:
                mappings[header] = COLUMN_MAPPINGS[normalized.replace(' ', '')]
            # Partial match for common patterns
            else:
                for pattern, field in COLUMN_MAPPINGS.items():
                    if pattern in normalized or normalized in pattern:
                        if header not in mappings:
                            mappings[header] = field
                        break

        return mappings

    def import_csv(
        self,
        file_path: str,
        list_id: int,
        field_mapping: Dict[str, str],
        custom_labels: Optional[Dict[str, str]] = None,
        skip_duplicates: bool = True
    ) -> Tuple[int, List[Dict[str, Any]]]:
        """
        Import contacts from CSV file.

        Args:
            file_path: Path to CSV file
            list_id: ID of contact list to import into
            field_mapping: Dict mapping CSV headers to field names
            custom_labels: Optional dict of custom field labels
            skip_duplicates: Whether to skip duplicate emails

        Returns:
            Tuple of (imported_count, errors_list)
        """
        file_path = Path(file_path)
        if not file_path.exists():
            raise CSVImportError(f"File not found: {file_path}")

        # Verify list exists
        contact_list = self.contact_service.get_list(list_id)
        if not contact_list:
            raise CSVImportError(f"Contact list {list_id} not found")

        # Update custom labels if provided
        if custom_labels:
            self.contact_service.update_list(list_id, custom_labels=custom_labels)

        try:
            encoding = self._detect_encoding(file_path)
            df = pd.read_csv(file_path, encoding=encoding)
        except Exception as e:
            raise CSVImportError(f"Failed to read CSV file: {e}")

        imported_count = 0
        errors = []

        # Reverse mapping: field_name -> csv_header
        reverse_mapping = {v: k for k, v in field_mapping.items()}

        for row_idx, row in df.iterrows():
            row_num = row_idx + 2  # Account for 0-index and header row

            try:
                contact_data = self._row_to_contact_data(row, field_mapping, reverse_mapping)

                # Validate required fields
                if not contact_data.get('email'):
                    errors.append({
                        'row': row_num,
                        'error': 'Email is required',
                        'data': dict(row)
                    })
                    continue

                # Check for duplicate
                if skip_duplicates and self.contact_service.check_duplicate(list_id, contact_data['email']):
                    errors.append({
                        'row': row_num,
                        'error': 'Duplicate email (skipped)',
                        'data': dict(row)
                    })
                    continue

                # Create contact
                self.contact_service.create_contact(list_id, contact_data)
                imported_count += 1

            except Exception as e:
                errors.append({
                    'row': row_num,
                    'error': str(e),
                    'data': dict(row)
                })

        logger.info(f"CSV import completed: {imported_count} imported, {len(errors)} errors")
        return imported_count, errors

    def export_csv(
        self,
        list_id: int,
        file_path: str,
        fields: Optional[List[str]] = None,
        include_custom: bool = True
    ) -> int:
        """
        Export contacts to CSV file.

        Args:
            list_id: ID of contact list to export
            file_path: Path for output file
            fields: Optional list of specific fields to include
            include_custom: Whether to include custom fields

        Returns:
            Number of contacts exported
        """
        contact_list = self.contact_service.get_list(list_id)
        if not contact_list:
            raise ValidationError(f"Contact list {list_id} not found")

        contacts = self.contact_service.get_contacts(list_id, limit=100000)

        if not contacts:
            # Create empty file with headers
            with open(file_path, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerow(self._get_export_headers(contact_list, fields, include_custom))
            return 0

        # Build rows
        rows = []
        headers = self._get_export_headers(contact_list, fields, include_custom)

        for contact in contacts:
            row = []
            for header in headers:
                field = self._header_to_field(header, contact_list)
                value = getattr(contact, field, '') or ''
                row.append(value)
            rows.append(row)

        # Write CSV
        with open(file_path, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(headers)
            writer.writerows(rows)

        logger.info(f"Exported {len(contacts)} contacts to {file_path}")
        return len(contacts)

    def _detect_encoding(self, file_path: Path) -> str:
        """Detect file encoding."""
        encodings = ['utf-8', 'utf-8-sig', 'latin-1', 'cp1252', 'iso-8859-1']

        for encoding in encodings:
            try:
                with open(file_path, 'r', encoding=encoding) as f:
                    f.read(1024)
                return encoding
            except (UnicodeDecodeError, LookupError):
                continue

        return 'utf-8'  # Default fallback

    def _row_to_contact_data(
        self,
        row: pd.Series,
        field_mapping: Dict[str, str],
        reverse_mapping: Dict[str, str]
    ) -> Dict[str, Any]:
        """Convert CSV row to contact data dict."""
        contact_data = {}

        for csv_header, field_name in field_mapping.items():
            if csv_header in row.index:
                value = row[csv_header]
                # Handle NaN values
                if pd.isna(value):
                    value = None
                else:
                    value = str(value).strip() if value else None
                contact_data[field_name] = value

        return contact_data

    def _get_export_headers(
        self,
        contact_list: Any,
        fields: Optional[List[str]],
        include_custom: bool
    ) -> List[str]:
        """Get headers for CSV export."""
        if fields:
            return fields

        headers = ['Title', 'First Name', 'Last Name', 'Email', 'Company',
                   'Position', 'Phone', 'LinkedIn', 'Source']

        if include_custom:
            for i in range(1, 11):
                label = getattr(contact_list, f'custom{i}_label', None)
                if label:
                    headers.append(label)
                else:
                    headers.append(f'Custom {i}')

        return headers

    def _header_to_field(self, header: str, contact_list: Any) -> str:
        """Map export header to field name."""
        mapping = {
            'Title': 'title',
            'First Name': 'first_name',
            'Last Name': 'last_name',
            'Email': 'email',
            'Company': 'company',
            'Position': 'position',
            'Phone': 'phone',
            'LinkedIn': 'linkedin_url',
            'Source': 'source',
        }

        if header in mapping:
            return mapping[header]

        # Check custom fields
        for i in range(1, 11):
            label = getattr(contact_list, f'custom{i}_label', None)
            if label and header == label:
                return f'custom{i}'
            if header == f'Custom {i}':
                return f'custom{i}'

        return header.lower().replace(' ', '_')
