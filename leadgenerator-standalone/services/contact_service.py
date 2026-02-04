"""Contact management service for Lead Generator Standalone."""

import logging
from datetime import datetime
from typing import List, Optional, Dict, Any

from core.database import get_db
from core.models import Contact, ContactList
from core.exceptions import ValidationError, DuplicateContactError, DatabaseError

logger = logging.getLogger(__name__)


class ContactService:
    """Service for managing contacts and contact lists."""

    def __init__(self):
        self.db = get_db()

    # Contact List Methods

    def get_all_lists(self) -> List[ContactList]:
        """Get all contact lists with contact counts."""
        query = """
            SELECT cl.*,
                   (SELECT COUNT(*) FROM contacts c WHERE c.list_id = cl.list_id) as contact_count
            FROM contact_lists cl
            ORDER BY cl.name
        """
        rows = self.db.fetchall(query)
        return [self._row_to_contact_list(row) for row in rows]

    def get_list(self, list_id: int) -> Optional[ContactList]:
        """Get a contact list by ID."""
        query = """
            SELECT cl.*,
                   (SELECT COUNT(*) FROM contacts c WHERE c.list_id = cl.list_id) as contact_count
            FROM contact_lists cl
            WHERE cl.list_id = ?
        """
        row = self.db.fetchone(query, (list_id,))
        if row:
            return self._row_to_contact_list(row)
        return None

    def create_list(
        self,
        name: str,
        description: Optional[str] = None,
        custom_labels: Optional[Dict[str, str]] = None
    ) -> ContactList:
        """Create a new contact list."""
        if not name:
            raise ValidationError("List name is required")

        custom_labels = custom_labels or {}

        query = """
            INSERT INTO contact_lists (
                name, description,
                custom1_label, custom2_label, custom3_label, custom4_label, custom5_label,
                custom6_label, custom7_label, custom8_label, custom9_label, custom10_label
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """
        params = (
            name, description,
            custom_labels.get('custom1'), custom_labels.get('custom2'),
            custom_labels.get('custom3'), custom_labels.get('custom4'),
            custom_labels.get('custom5'), custom_labels.get('custom6'),
            custom_labels.get('custom7'), custom_labels.get('custom8'),
            custom_labels.get('custom9'), custom_labels.get('custom10')
        )

        cursor = self.db.execute(query, params)
        list_id = cursor.lastrowid

        logger.info(f"Created contact list '{name}' with ID {list_id}")
        return self.get_list(list_id)

    def update_list(
        self,
        list_id: int,
        name: Optional[str] = None,
        description: Optional[str] = None,
        custom_labels: Optional[Dict[str, str]] = None
    ) -> ContactList:
        """Update a contact list."""
        contact_list = self.get_list(list_id)
        if not contact_list:
            raise ValidationError(f"Contact list {list_id} not found")

        updates = []
        params = []

        if name is not None:
            updates.append("name = ?")
            params.append(name)

        if description is not None:
            updates.append("description = ?")
            params.append(description)

        if custom_labels:
            for i in range(1, 11):
                key = f"custom{i}"
                if key in custom_labels:
                    updates.append(f"{key}_label = ?")
                    params.append(custom_labels[key])

        if updates:
            updates.append("updated_at = datetime('now')")
            params.append(list_id)

            query = f"UPDATE contact_lists SET {', '.join(updates)} WHERE list_id = ?"
            self.db.execute(query, tuple(params))
            logger.info(f"Updated contact list {list_id}")

        return self.get_list(list_id)

    def delete_list(self, list_id: int) -> None:
        """Delete a contact list and all its contacts."""
        self.db.execute("DELETE FROM contact_lists WHERE list_id = ?", (list_id,))
        logger.info(f"Deleted contact list {list_id}")

    # Contact Methods

    def get_contacts(self, list_id: int, limit: int = 1000, offset: int = 0) -> List[Contact]:
        """Get contacts in a list."""
        query = """
            SELECT * FROM contacts
            WHERE list_id = ?
            ORDER BY last_name, first_name
            LIMIT ? OFFSET ?
        """
        rows = self.db.fetchall(query, (list_id, limit, offset))
        return [self._row_to_contact(row) for row in rows]

    def get_contact(self, contact_id: int) -> Optional[Contact]:
        """Get a contact by ID."""
        query = "SELECT * FROM contacts WHERE contact_id = ?"
        row = self.db.fetchone(query, (contact_id,))
        if row:
            return self._row_to_contact(row)
        return None

    def get_contact_by_email(self, list_id: int, email: str) -> Optional[Contact]:
        """Get a contact by email in a specific list."""
        query = "SELECT * FROM contacts WHERE list_id = ? AND email = ?"
        row = self.db.fetchone(query, (list_id, email.lower()))
        if row:
            return self._row_to_contact(row)
        return None

    def create_contact(self, list_id: int, contact_data: Dict[str, Any]) -> Contact:
        """Create a new contact."""
        email = contact_data.get('email', '').strip().lower()

        if not email:
            raise ValidationError("Email is required")

        # Check for duplicate
        if self.check_duplicate(list_id, email):
            raise DuplicateContactError(email, list_id)

        query = """
            INSERT INTO contacts (
                list_id, title, first_name, last_name, email, company, position,
                phone, linkedin_url, source,
                custom1, custom2, custom3, custom4, custom5,
                custom6, custom7, custom8, custom9, custom10
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """
        params = (
            list_id,
            contact_data.get('title'),
            contact_data.get('first_name', ''),
            contact_data.get('last_name', ''),
            email,
            contact_data.get('company', ''),
            contact_data.get('position'),
            contact_data.get('phone'),
            contact_data.get('linkedin_url'),
            contact_data.get('source'),
            contact_data.get('custom1'),
            contact_data.get('custom2'),
            contact_data.get('custom3'),
            contact_data.get('custom4'),
            contact_data.get('custom5'),
            contact_data.get('custom6'),
            contact_data.get('custom7'),
            contact_data.get('custom8'),
            contact_data.get('custom9'),
            contact_data.get('custom10'),
        )

        cursor = self.db.execute(query, params)
        contact_id = cursor.lastrowid

        logger.info(f"Created contact '{email}' with ID {contact_id}")
        return self.get_contact(contact_id)

    def update_contact(self, contact_id: int, contact_data: Dict[str, Any]) -> Contact:
        """Update a contact."""
        contact = self.get_contact(contact_id)
        if not contact:
            raise ValidationError(f"Contact {contact_id} not found")

        # If email is being changed, check for duplicate
        new_email = contact_data.get('email', '').strip().lower()
        if new_email and new_email != contact.email:
            if self.check_duplicate(contact.list_id, new_email):
                raise DuplicateContactError(new_email, contact.list_id)

        updates = []
        params = []

        field_mapping = {
            'title': 'title', 'first_name': 'first_name', 'last_name': 'last_name',
            'email': 'email', 'company': 'company', 'position': 'position',
            'phone': 'phone', 'linkedin_url': 'linkedin_url', 'source': 'source',
            'custom1': 'custom1', 'custom2': 'custom2', 'custom3': 'custom3',
            'custom4': 'custom4', 'custom5': 'custom5', 'custom6': 'custom6',
            'custom7': 'custom7', 'custom8': 'custom8', 'custom9': 'custom9',
            'custom10': 'custom10'
        }

        for data_key, db_field in field_mapping.items():
            if data_key in contact_data:
                value = contact_data[data_key]
                if data_key == 'email' and value:
                    value = value.strip().lower()
                updates.append(f"{db_field} = ?")
                params.append(value)

        if updates:
            updates.append("updated_at = datetime('now')")
            params.append(contact_id)

            query = f"UPDATE contacts SET {', '.join(updates)} WHERE contact_id = ?"
            self.db.execute(query, tuple(params))
            logger.info(f"Updated contact {contact_id}")

        return self.get_contact(contact_id)

    def delete_contact(self, contact_id: int) -> None:
        """Delete a contact."""
        self.db.execute("DELETE FROM contacts WHERE contact_id = ?", (contact_id,))
        logger.info(f"Deleted contact {contact_id}")

    def search_contacts(self, list_id: int, query: str, limit: int = 100) -> List[Contact]:
        """Search contacts by name, email, or company."""
        search_term = f"%{query}%"
        sql = """
            SELECT * FROM contacts
            WHERE list_id = ?
              AND (first_name LIKE ? OR last_name LIKE ? OR email LIKE ? OR company LIKE ?)
            ORDER BY last_name, first_name
            LIMIT ?
        """
        rows = self.db.fetchall(sql, (list_id, search_term, search_term, search_term, search_term, limit))
        return [self._row_to_contact(row) for row in rows]

    def check_duplicate(self, list_id: int, email: str) -> bool:
        """Check if a contact with the given email exists in the list."""
        query = "SELECT 1 FROM contacts WHERE list_id = ? AND email = ? LIMIT 1"
        row = self.db.fetchone(query, (list_id, email.lower()))
        return row is not None

    def get_contact_count(self, list_id: int) -> int:
        """Get total contact count for a list."""
        query = "SELECT COUNT(*) as count FROM contacts WHERE list_id = ?"
        row = self.db.fetchone(query, (list_id,))
        return row['count'] if row else 0

    def get_all_contacts_by_email(self, email: str) -> List[Contact]:
        """Get all contacts with the given email across all lists."""
        query = "SELECT * FROM contacts WHERE email = ?"
        rows = self.db.fetchall(query, (email.lower(),))
        return [self._row_to_contact(row) for row in rows]

    # Helper methods

    def _row_to_contact_list(self, row) -> ContactList:
        """Convert database row to ContactList model."""
        return ContactList(
            list_id=row['list_id'],
            name=row['name'],
            description=row['description'],
            custom1_label=row['custom1_label'],
            custom2_label=row['custom2_label'],
            custom3_label=row['custom3_label'],
            custom4_label=row['custom4_label'],
            custom5_label=row['custom5_label'],
            custom6_label=row['custom6_label'],
            custom7_label=row['custom7_label'],
            custom8_label=row['custom8_label'],
            custom9_label=row['custom9_label'],
            custom10_label=row['custom10_label'],
            created_at=row['created_at'],
            updated_at=row['updated_at'],
            contact_count=row['contact_count'] if 'contact_count' in row.keys() else 0
        )

    def _row_to_contact(self, row) -> Contact:
        """Convert database row to Contact model."""
        return Contact(
            contact_id=row['contact_id'],
            list_id=row['list_id'],
            title=row['title'],
            first_name=row['first_name'],
            last_name=row['last_name'],
            email=row['email'],
            company=row['company'],
            position=row['position'],
            phone=row['phone'],
            linkedin_url=row['linkedin_url'],
            source=row['source'],
            custom1=row['custom1'],
            custom2=row['custom2'],
            custom3=row['custom3'],
            custom4=row['custom4'],
            custom5=row['custom5'],
            custom6=row['custom6'],
            custom7=row['custom7'],
            custom8=row['custom8'],
            custom9=row['custom9'],
            custom10=row['custom10'],
            created_at=row['created_at'],
            updated_at=row['updated_at']
        )
