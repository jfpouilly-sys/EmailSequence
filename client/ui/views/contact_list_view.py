"""Contact list view with import functionality."""
import logging
import tkinter as tk
from tkinter import filedialog
from typing import Optional
import ttkbootstrap as ttk
from ttkbootstrap.constants import *

from core.api_client import ApiClient
from core.models import Contact, ContactList
from ui.widgets.data_table import DataTable

logger = logging.getLogger(__name__)


class ContactListView(ttk.Frame):
    """Contact management view."""

    def __init__(self, parent, app=None, api: ApiClient = None, **kwargs):
        super().__init__(parent, **kwargs)

        self.app = app
        self.api = api
        self._contact_lists = []
        self._current_list_id = None

        self._create_widgets()

    def _create_widgets(self) -> None:
        """Create view widgets."""
        # Header
        header = ttk.Frame(self)
        header.pack(fill=X, pady=(0, 15))

        # List selector
        list_frame = ttk.Frame(header)
        list_frame.pack(side=LEFT)

        ttk.Label(list_frame, text="Contact List:").pack(side=LEFT, padx=(0, 5))

        self.list_var = tk.StringVar()
        self.list_combo = ttk.Combobox(
            list_frame,
            textvariable=self.list_var,
            state="readonly",
            width=30
        )
        self.list_combo.pack(side=LEFT)
        self.list_combo.bind("<<ComboboxSelected>>", self._on_list_change)

        ttk.Button(
            list_frame,
            text="+ New List",
            bootstyle="outline-primary",
            command=self._on_new_list
        ).pack(side=LEFT, padx=(10, 0))

        # Actions
        actions = ttk.Frame(header)
        actions.pack(side=RIGHT)

        ttk.Button(
            actions,
            text="Import CSV",
            bootstyle="success",
            command=self._on_import
        ).pack(side=LEFT, padx=5)

        ttk.Button(
            actions,
            text="Export CSV",
            bootstyle="outline-primary",
            command=self._on_export
        ).pack(side=LEFT, padx=5)

        # Contacts table
        columns = [
            {"id": "id", "text": "ID", "width": 0},
            {"id": "name", "text": "Name", "width": 180, "anchor": "w"},
            {"id": "email", "text": "Email", "width": 220, "anchor": "w"},
            {"id": "company", "text": "Company", "width": 150, "anchor": "w"},
            {"id": "position", "text": "Position", "width": 120, "anchor": "w"},
            {"id": "status", "text": "Status", "width": 100, "anchor": "center"},
            {"id": "source", "text": "Source", "width": 100, "anchor": "w"},
        ]

        self.table = DataTable(
            self,
            columns=columns,
            show_search=True,
            on_select=self._on_select,
            on_double_click=self._on_edit
        )
        self.table.pack(fill=BOTH, expand=True)

        # Bottom actions
        bottom = ttk.Frame(self)
        bottom.pack(fill=X, pady=(10, 0))

        ttk.Button(
            bottom,
            text="+ Add Contact",
            bootstyle="success-outline",
            command=self._on_add
        ).pack(side=LEFT, padx=5)

        self.edit_btn = ttk.Button(
            bottom,
            text="Edit",
            bootstyle="primary-outline",
            command=self._on_edit_click,
            state="disabled"
        )
        self.edit_btn.pack(side=LEFT, padx=5)

        self.delete_btn = ttk.Button(
            bottom,
            text="Delete",
            bootstyle="danger-outline",
            command=self._on_delete,
            state="disabled"
        )
        self.delete_btn.pack(side=LEFT, padx=5)

    def refresh(self) -> None:
        """Refresh view data."""
        self._load_lists()

    def _load_lists(self) -> None:
        """Load contact lists."""
        if not self.api:
            return

        try:
            self._contact_lists = self.api.get_contact_lists()
            names = [cl.name for cl in self._contact_lists]
            self.list_combo['values'] = names

            if names and not self.list_var.get():
                self.list_var.set(names[0])
                self._on_list_change(None)
            elif self._current_list_id:
                self._load_contacts()

        except Exception as e:
            logger.error(f"Error loading contact lists: {e}")

    def _on_list_change(self, event) -> None:
        """Handle list selection change."""
        list_name = self.list_var.get()
        contact_list = next((cl for cl in self._contact_lists if cl.name == list_name), None)
        if contact_list:
            self._current_list_id = contact_list.list_id
            self._load_contacts()

    def _load_contacts(self) -> None:
        """Load contacts for current list."""
        if not self.api or not self._current_list_id:
            return

        try:
            contacts = self.api.get_contacts(self._current_list_id)
            data = []
            for c in contacts:
                data.append({
                    "id": c.contact_id,
                    "name": f"{c.first_name} {c.last_name}",
                    "email": c.email,
                    "company": c.company,
                    "position": c.position or "",
                    "status": c.status.value,
                    "source": c.source or ""
                })
            self.table.set_data(data)

            if self.app:
                self.app.set_status(f"Loaded {len(contacts)} contacts")

        except Exception as e:
            logger.error(f"Error loading contacts: {e}")

    def _on_select(self, contact_id: str) -> None:
        """Handle contact selection."""
        self.edit_btn.configure(state="normal")
        self.delete_btn.configure(state="normal")

    def _on_new_list(self) -> None:
        """Create new contact list."""
        dialog = NewListDialog(self, self.api)
        self.wait_window(dialog)
        if dialog.result:
            self._load_lists()
            self.list_var.set(dialog.result)
            self._on_list_change(None)

    def _on_import(self) -> None:
        """Import contacts from CSV."""
        if not self._current_list_id:
            if self.app:
                self.app.show_error("Error", "Please select a contact list first")
            return

        from ui.dialogs.csv_import_wizard import CsvImportWizard
        dialog = CsvImportWizard(self, self.api, self._current_list_id)
        self.wait_window(dialog)
        if dialog.result:
            self._load_contacts()

    def _on_export(self) -> None:
        """Export contacts to CSV."""
        if not self._current_list_id:
            return

        filepath = filedialog.asksaveasfilename(
            defaultextension=".csv",
            filetypes=[("CSV files", "*.csv")]
        )
        if filepath:
            try:
                contacts = self.api.get_contacts(self._current_list_id)
                from services.csv_service import CsvService
                service = CsvService()
                data = service.export_contacts_to_csv(contacts)
                with open(filepath, 'wb') as f:
                    f.write(data.read())
                if self.app:
                    self.app.set_status(f"Exported {len(contacts)} contacts to {filepath}")
            except Exception as e:
                if self.app:
                    self.app.show_error("Error", str(e))

    def _on_add(self) -> None:
        """Add new contact."""
        if not self._current_list_id:
            return

        dialog = ContactFormDialog(self, self.api, self._current_list_id)
        self.wait_window(dialog)
        if dialog.result:
            self._load_contacts()

    def _on_edit_click(self) -> None:
        """Edit selected contact."""
        contact_id = self.table.get_selected_id()
        if contact_id:
            self._on_edit(contact_id)

    def _on_edit(self, contact_id: str) -> None:
        """Edit contact."""
        dialog = ContactFormDialog(self, self.api, self._current_list_id, contact_id=contact_id)
        self.wait_window(dialog)
        if dialog.result:
            self._load_contacts()

    def _on_delete(self) -> None:
        """Delete selected contact."""
        contact_id = self.table.get_selected_id()
        selected = self.table.get_selected()
        if not contact_id or not selected:
            return

        if self.app and self.app.ask_confirmation(
            "Delete Contact",
            f"Delete {selected.get('email')}?"
        ):
            try:
                self.api.delete_contact(contact_id)
                self._load_contacts()
            except Exception as e:
                if self.app:
                    self.app.show_error("Error", str(e))


class NewListDialog(ttk.Toplevel):
    """Dialog for creating new contact list."""

    def __init__(self, parent, api: ApiClient):
        super().__init__(parent)

        self.api = api
        self.result = None

        self.title("New Contact List")
        self.geometry("400x200")
        self.resizable(False, False)

        self._create_widgets()
        self.transient(parent)
        self.grab_set()

    def _create_widgets(self) -> None:
        """Create dialog widgets."""
        main = ttk.Frame(self, padding=20)
        main.pack(fill=BOTH, expand=True)

        ttk.Label(main, text="List Name *").pack(anchor=W, pady=(0, 5))
        self.name_var = tk.StringVar()
        ttk.Entry(main, textvariable=self.name_var, width=40).pack(fill=X, pady=(0, 15))

        ttk.Label(main, text="Description").pack(anchor=W, pady=(0, 5))
        self.desc_var = tk.StringVar()
        ttk.Entry(main, textvariable=self.desc_var, width=40).pack(fill=X, pady=(0, 15))

        btn_frame = ttk.Frame(main)
        btn_frame.pack(fill=X, pady=(15, 0))

        ttk.Button(btn_frame, text="Cancel", bootstyle="secondary", command=self.destroy).pack(side=RIGHT, padx=5)
        ttk.Button(btn_frame, text="Create", bootstyle="primary", command=self._on_create).pack(side=RIGHT)

    def _on_create(self) -> None:
        """Create the list."""
        name = self.name_var.get().strip()
        if not name:
            return

        try:
            self.api.create_contact_list(name, self.desc_var.get().strip() or None)
            self.result = name
            self.destroy()
        except Exception as e:
            from tkinter import messagebox
            messagebox.showerror("Error", str(e), parent=self)


class ContactFormDialog(ttk.Toplevel):
    """Dialog for creating/editing contacts."""

    def __init__(self, parent, api: ApiClient, list_id: str, contact_id: str = None):
        super().__init__(parent)

        self.api = api
        self.list_id = list_id
        self.contact_id = contact_id
        self.result = None

        self.title("New Contact" if not contact_id else "Edit Contact")
        self.geometry("500x500")

        self._create_widgets()

        if contact_id:
            self._load_contact()

        self.transient(parent)
        self.grab_set()

    def _create_widgets(self) -> None:
        """Create form widgets."""
        main = ttk.Frame(self, padding=20)
        main.pack(fill=BOTH, expand=True)

        # Email
        ttk.Label(main, text="Email *").pack(anchor=W, pady=(0, 5))
        self.email_var = tk.StringVar()
        ttk.Entry(main, textvariable=self.email_var, width=50).pack(fill=X, pady=(0, 10))

        # Name row
        name_frame = ttk.Frame(main)
        name_frame.pack(fill=X, pady=(0, 10))

        left = ttk.Frame(name_frame)
        left.pack(side=LEFT, fill=X, expand=True, padx=(0, 5))
        ttk.Label(left, text="First Name *").pack(anchor=W)
        self.first_var = tk.StringVar()
        ttk.Entry(left, textvariable=self.first_var).pack(fill=X)

        right = ttk.Frame(name_frame)
        right.pack(side=LEFT, fill=X, expand=True, padx=(5, 0))
        ttk.Label(right, text="Last Name *").pack(anchor=W)
        self.last_var = tk.StringVar()
        ttk.Entry(right, textvariable=self.last_var).pack(fill=X)

        # Company
        ttk.Label(main, text="Company *").pack(anchor=W, pady=(0, 5))
        self.company_var = tk.StringVar()
        ttk.Entry(main, textvariable=self.company_var, width=50).pack(fill=X, pady=(0, 10))

        # Position
        ttk.Label(main, text="Position").pack(anchor=W, pady=(0, 5))
        self.position_var = tk.StringVar()
        ttk.Entry(main, textvariable=self.position_var, width=50).pack(fill=X, pady=(0, 10))

        # Phone
        ttk.Label(main, text="Phone").pack(anchor=W, pady=(0, 5))
        self.phone_var = tk.StringVar()
        ttk.Entry(main, textvariable=self.phone_var, width=50).pack(fill=X, pady=(0, 10))

        # Source
        ttk.Label(main, text="Source").pack(anchor=W, pady=(0, 5))
        self.source_var = tk.StringVar()
        ttk.Entry(main, textvariable=self.source_var, width=50).pack(fill=X, pady=(0, 15))

        # Buttons
        btn_frame = ttk.Frame(main)
        btn_frame.pack(fill=X, pady=(15, 0))

        ttk.Button(btn_frame, text="Cancel", bootstyle="secondary", command=self.destroy).pack(side=RIGHT, padx=5)
        ttk.Button(btn_frame, text="Save", bootstyle="primary", command=self._on_save).pack(side=RIGHT)

    def _load_contact(self) -> None:
        """Load contact data."""
        try:
            contact = self.api.get_contact(self.contact_id)
            self.email_var.set(contact.email)
            self.first_var.set(contact.first_name)
            self.last_var.set(contact.last_name)
            self.company_var.set(contact.company)
            self.position_var.set(contact.position or "")
            self.phone_var.set(contact.phone or "")
            self.source_var.set(contact.source or "")
        except Exception as e:
            logger.error(f"Error loading contact: {e}")

    def _on_save(self) -> None:
        """Save contact."""
        email = self.email_var.get().strip()
        first = self.first_var.get().strip()
        last = self.last_var.get().strip()
        company = self.company_var.get().strip()

        if not all([email, first, last, company]):
            from tkinter import messagebox
            messagebox.showerror("Error", "Please fill required fields", parent=self)
            return

        try:
            kwargs = {}
            if self.position_var.get().strip():
                kwargs['position'] = self.position_var.get().strip()
            if self.phone_var.get().strip():
                kwargs['phone'] = self.phone_var.get().strip()
            if self.source_var.get().strip():
                kwargs['source'] = self.source_var.get().strip()

            if self.contact_id:
                self.api.update_contact(
                    self.contact_id,
                    email=email,
                    firstName=first,
                    lastName=last,
                    company=company,
                    **kwargs
                )
            else:
                self.api.create_contact(
                    list_id=self.list_id,
                    email=email,
                    first_name=first,
                    last_name=last,
                    company=company,
                    **kwargs
                )

            self.result = True
            self.destroy()

        except Exception as e:
            from tkinter import messagebox
            messagebox.showerror("Error", str(e), parent=self)
