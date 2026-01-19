"""Contact database management using Excel."""
import os
import time
import logging
import pandas as pd
from datetime import datetime
from typing import Optional


class ContactTracker:
    """Manage contact database in Excel file."""

    REQUIRED_COLUMNS = [
        'title', 'first_name', 'last_name', 'email', 'company',
        'status', 'sequence_id', 'initial_sent_date', 'last_contact_date',
        'followup_count', 'conversation_id', 'replied_date', 'notes'
    ]

    def __init__(self, excel_path: str):
        """
        Load Excel file into pandas DataFrame.
        Create file with headers if it doesn't exist.
        Validate required columns exist.

        Args:
            excel_path: Path to Excel file

        Raises:
            ValueError: If required columns are missing
        """
        self.excel_path = excel_path
        self._df: Optional[pd.DataFrame] = None
        self.logger = logging.getLogger(__name__)

        if not os.path.exists(excel_path):
            # Create new file with required columns
            self.logger.info(f"[FILE CREATE] Creating new contacts file: {os.path.abspath(excel_path)}")
            self._df = pd.DataFrame(columns=self.REQUIRED_COLUMNS)
            self.save()
        else:
            # Load existing file
            abs_path = os.path.abspath(excel_path)
            self.logger.info(f"[FILE READ] Loading contacts from: {abs_path}")
            self._df = pd.read_excel(excel_path)
            self.logger.info(f"[FILE READ] Loaded {len(self._df)} contacts from {abs_path}")
            self._validate_columns()

    def _validate_columns(self) -> None:
        """Validate that all required columns exist."""
        missing = set(self.REQUIRED_COLUMNS) - set(self._df.columns)
        if missing:
            raise ValueError(
                f"Excel file is missing required columns: {', '.join(missing)}\n"
                f"Required columns: {', '.join(self.REQUIRED_COLUMNS)}"
            )

    def get_all_contacts(self) -> pd.DataFrame:
        """Return all contacts as DataFrame."""
        return self._df.copy()

    def get_pending_contacts(self) -> pd.DataFrame:
        """Return contacts with status='pending'."""
        result = self._df[self._df['status'] == 'pending'].copy()
        self.logger.debug(f"[QUERY] Found {len(result)} pending contacts")
        return result

    def get_contacts_needing_followup(self, followup_delays: list[int]) -> pd.DataFrame:
        """
        Return contacts eligible for follow-up based on:
        - status in ['sent', 'followup_1', 'followup_2']
        - followup_count < len(followup_delays)
        - days since last_contact_date >= appropriate delay from followup_delays

        Args:
            followup_delays: List of delays in days for each follow-up

        Returns:
            DataFrame of contacts needing follow-up
        """
        eligible_statuses = ['sent', 'followup_1', 'followup_2', 'followup_3']

        # Filter by status and followup_count
        mask = (
            self._df['status'].isin(eligible_statuses) &
            (self._df['followup_count'] < len(followup_delays))
        )

        candidates = self._df[mask].copy()

        # Check timing for each candidate
        needs_followup = []
        for _, contact in candidates.iterrows():
            followup_count = int(contact['followup_count']) if pd.notna(contact['followup_count']) else 0

            if followup_count >= len(followup_delays):
                continue

            # Get the delay for the next follow-up
            next_delay = followup_delays[followup_count]

            # Check if enough days have passed
            if pd.notna(contact['last_contact_date']):
                last_contact = pd.to_datetime(contact['last_contact_date'])
                days_since = (datetime.now() - last_contact).days

                if days_since >= next_delay:
                    needs_followup.append(contact)

        if needs_followup:
            return pd.DataFrame(needs_followup)
        else:
            return pd.DataFrame(columns=self._df.columns)

    def update_contact(self, email: str, updates: dict) -> bool:
        """
        Update a contact's fields by email address.

        Args:
            email: Contact's email address (case-insensitive match)
            updates: Dict of column->value to update

        Returns:
            True if contact found and updated, False if not found.

        Automatically saves to Excel after update.
        """
        # Case-insensitive email match
        mask = self._df['email'].str.lower() == email.lower()

        if not mask.any():
            self.logger.warning(f"[UPDATE] Contact not found: {email}")
            return False

        # Log update
        update_fields = ', '.join(f"{k}={v}" for k, v in updates.items())
        self.logger.info(f"[UPDATE] Updating contact {email}: {update_fields}")

        # Update fields
        for column, value in updates.items():
            if column in self._df.columns:
                self._df.loc[mask, column] = value

        self.save()
        return True

    def add_contact(self, contact_data: dict) -> bool:
        """
        Add a new contact row.
        Validates required fields: first_name, last_name, email.
        Sets status='pending' if not provided.
        Returns False if email already exists.

        Args:
            contact_data: Dictionary with contact information

        Returns:
            True if added successfully, False if email exists
        """
        # Validate required fields
        required = ['first_name', 'last_name', 'email']
        for field in required:
            if field not in contact_data or not contact_data[field]:
                raise ValueError(f"Required field missing: {field}")

        # Check for duplicate email
        email = contact_data['email']
        if (self._df['email'].str.lower() == email.lower()).any():
            self.logger.warning(f"[ADD] Duplicate email, contact not added: {email}")
            return False

        # Set defaults
        if 'status' not in contact_data:
            contact_data['status'] = 'pending'

        self.logger.info(
            f"[ADD] Adding new contact: {contact_data.get('first_name')} "
            f"{contact_data.get('last_name')} <{email}> (status: {contact_data['status']})"
        )

        # Add missing columns with None
        for col in self.REQUIRED_COLUMNS:
            if col not in contact_data:
                contact_data[col] = None

        # Add row using pd.concat instead of append
        new_row = pd.DataFrame([contact_data])
        self._df = pd.concat([self._df, new_row], ignore_index=True)

        self.save()
        return True

    def save(self) -> None:
        """
        Save current DataFrame to Excel file.
        Retries once if file is locked.
        """
        abs_path = os.path.abspath(self.excel_path)
        try:
            self.logger.info(f"[FILE WRITE] Saving {len(self._df)} contacts to: {abs_path}")
            self._df.to_excel(self.excel_path, index=False, engine='openpyxl')
            file_size = os.path.getsize(self.excel_path)
            self.logger.info(f"[FILE WRITE] Successfully saved to {abs_path} ({file_size} bytes)")
        except PermissionError:
            # File might be open in Excel - wait and retry once
            self.logger.warning(f"[FILE WRITE] File locked, retrying in 5 seconds: {abs_path}")
            time.sleep(5)
            try:
                self._df.to_excel(self.excel_path, index=False, engine='openpyxl')
                self.logger.info(f"[FILE WRITE] Successfully saved on retry to: {abs_path}")
            except PermissionError:
                self.logger.error(f"[FILE WRITE] Failed to save, file is locked: {abs_path}")
                raise PermissionError(
                    f"Cannot save to {self.excel_path} - file is locked.\n"
                    "Please close the file in Excel and try again."
                )

    def get_contact_by_email(self, email: str) -> Optional[dict]:
        """
        Return contact as dict or None if not found.

        Args:
            email: Email address (case-insensitive)

        Returns:
            Contact dictionary or None
        """
        mask = self._df['email'].str.lower() == email.lower()

        if not mask.any():
            return None

        # Get first matching row and convert to dict
        contact = self._df[mask].iloc[0].to_dict()
        return contact
