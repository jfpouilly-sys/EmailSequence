"""Tests for database module."""

import os
import sys
import tempfile
import unittest

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.database import Database, init_database, get_setting, set_setting, generate_campaign_ref


class TestDatabase(unittest.TestCase):
    """Test cases for database operations."""

    def setUp(self):
        """Set up test database."""
        self.temp_db = tempfile.NamedTemporaryFile(suffix='.db', delete=False)
        self.temp_db.close()
        Database.set_path(self.temp_db.name)
        Database._instance = None  # Reset singleton
        init_database(self.temp_db.name)

    def tearDown(self):
        """Clean up test database."""
        db = Database.get_instance()
        db.close()
        Database._instance = None
        os.unlink(self.temp_db.name)

    def test_init_database(self):
        """Test database initialization creates tables."""
        db = Database.get_instance()

        # Check that tables exist
        tables = db.fetchall(
            "SELECT name FROM sqlite_master WHERE type='table'"
        )
        table_names = [t['name'] for t in tables]

        self.assertIn('settings', table_names)
        self.assertIn('contact_lists', table_names)
        self.assertIn('contacts', table_names)
        self.assertIn('campaigns', table_names)
        self.assertIn('email_steps', table_names)

    def test_get_set_setting(self):
        """Test get and set settings."""
        # Default value
        value = get_setting('test_key', 'default')
        self.assertEqual(value, 'default')

        # Set and get
        set_setting('test_key', 'test_value')
        value = get_setting('test_key')
        self.assertEqual(value, 'test_value')

        # Update
        set_setting('test_key', 'new_value')
        value = get_setting('test_key')
        self.assertEqual(value, 'new_value')

    def test_generate_campaign_ref(self):
        """Test campaign reference generation."""
        ref1 = generate_campaign_ref()
        ref2 = generate_campaign_ref()

        # Check format
        self.assertTrue(ref1.startswith('ISIT-'))
        self.assertEqual(len(ref1), 11)

        # Check sequential
        num1 = int(ref1[-4:])
        num2 = int(ref2[-4:])
        self.assertEqual(num2, num1 + 1)


class TestContactService(unittest.TestCase):
    """Test cases for contact service."""

    def setUp(self):
        """Set up test database."""
        self.temp_db = tempfile.NamedTemporaryFile(suffix='.db', delete=False)
        self.temp_db.close()
        Database.set_path(self.temp_db.name)
        Database._instance = None
        init_database(self.temp_db.name)

    def tearDown(self):
        """Clean up test database."""
        db = Database.get_instance()
        db.close()
        Database._instance = None
        os.unlink(self.temp_db.name)

    def test_create_contact_list(self):
        """Test creating a contact list."""
        from services.contact_service import ContactService

        service = ContactService()
        contact_list = service.create_list("Test List", "Test description")

        self.assertIsNotNone(contact_list)
        self.assertIsNotNone(contact_list.list_id)
        self.assertEqual(contact_list.name, "Test List")
        self.assertEqual(contact_list.description, "Test description")

    def test_create_contact(self):
        """Test creating a contact."""
        from services.contact_service import ContactService

        service = ContactService()
        contact_list = service.create_list("Test List")

        contact = service.create_contact(contact_list.list_id, {
            'first_name': 'John',
            'last_name': 'Doe',
            'email': 'john@example.com',
            'company': 'Acme Inc'
        })

        self.assertIsNotNone(contact)
        self.assertEqual(contact.first_name, 'John')
        self.assertEqual(contact.email, 'john@example.com')

    def test_duplicate_contact(self):
        """Test duplicate contact detection."""
        from services.contact_service import ContactService
        from core.exceptions import DuplicateContactError

        service = ContactService()
        contact_list = service.create_list("Test List")

        # Create first contact
        service.create_contact(contact_list.list_id, {
            'first_name': 'John',
            'last_name': 'Doe',
            'email': 'john@example.com',
            'company': 'Acme'
        })

        # Try to create duplicate
        with self.assertRaises(DuplicateContactError):
            service.create_contact(contact_list.list_id, {
                'first_name': 'Jane',
                'last_name': 'Doe',
                'email': 'JOHN@example.com',  # Same email, different case
                'company': 'Other'
            })


if __name__ == '__main__':
    unittest.main()
