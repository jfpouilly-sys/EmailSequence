"""Contact business logic service."""
import logging
from typing import List, Optional, Dict, Any
from io import BytesIO

from core.api_client import ApiClient
from core.models import Contact, ContactList, ContactStatus

logger = logging.getLogger(__name__)


class ContactService:
    """Service for contact operations."""

    def __init__(self, api_client: ApiClient):
        self.api = api_client

    # Contact List operations
    def get_all_contact_lists(self) -> List[ContactList]:
        """Get all contact lists."""
        return self.api.get_contact_lists()

    def get_contact_list(self, list_id: str) -> ContactList:
        """Get contact list by ID."""
        return self.api.get_contact_list(list_id)

    def create_contact_list(self, name: str, description: Optional[str] = None) -> ContactList:
        """Create a new contact list."""
        return self.api.create_contact_list(name=name, description=description)

    # Contact operations
    def get_contacts(self, list_id: str) -> List[Contact]:
        """Get contacts in a list."""
        return self.api.get_contacts(list_id)

    def get_contact(self, contact_id: str) -> Contact:
        """Get contact by ID."""
        return self.api.get_contact(contact_id)

    def create_contact(
        self,
        list_id: str,
        email: str,
        first_name: str,
        last_name: str,
        company: str,
        title: Optional[str] = None,
        position: Optional[str] = None,
        phone: Optional[str] = None,
        linkedin_url: Optional[str] = None,
        source: Optional[str] = None,
        custom_fields: Optional[Dict[str, str]] = None
    ) -> Contact:
        """Create a new contact."""
        kwargs = {}
        if title:
            kwargs['title'] = title
        if position:
            kwargs['position'] = position
        if phone:
            kwargs['phone'] = phone
        if linkedin_url:
            kwargs['linkedInUrl'] = linkedin_url
        if source:
            kwargs['source'] = source
        if custom_fields:
            kwargs['customFields'] = custom_fields

        return self.api.create_contact(
            list_id=list_id,
            email=email,
            first_name=first_name,
            last_name=last_name,
            company=company,
            **kwargs
        )

    def update_contact(
        self,
        contact_id: str,
        email: Optional[str] = None,
        first_name: Optional[str] = None,
        last_name: Optional[str] = None,
        company: Optional[str] = None,
        **kwargs
    ) -> bool:
        """Update an existing contact."""
        update_data = {}
        if email is not None:
            update_data['email'] = email
        if first_name is not None:
            update_data['firstName'] = first_name
        if last_name is not None:
            update_data['lastName'] = last_name
        if company is not None:
            update_data['company'] = company
        update_data.update(kwargs)
        return self.api.update_contact(contact_id, **update_data)

    def delete_contact(self, contact_id: str) -> bool:
        """Delete a contact."""
        return self.api.delete_contact(contact_id)

    def import_contacts_from_csv(
        self,
        list_id: str,
        csv_data: BytesIO,
        filename: str = "contacts.csv"
    ) -> Dict[str, Any]:
        """Import contacts from CSV file."""
        return self.api.import_contacts(list_id, csv_data, filename)

    def search_contacts(self, list_id: str, query: str) -> List[Contact]:
        """Search contacts by name, email, or company."""
        contacts = self.get_contacts(list_id)
        query_lower = query.lower()
        return [
            c for c in contacts
            if query_lower in c.email.lower()
            or query_lower in c.first_name.lower()
            or query_lower in c.last_name.lower()
            or query_lower in c.company.lower()
        ]

    def get_contacts_by_status(self, list_id: str, status: ContactStatus) -> List[Contact]:
        """Get contacts filtered by status."""
        contacts = self.get_contacts(list_id)
        return [c for c in contacts if c.status == status]

    def get_total_contacts_count(self) -> int:
        """Get total count of all contacts across all lists."""
        lists = self.get_all_contact_lists()
        return sum(cl.contact_count for cl in lists)
