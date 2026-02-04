"""Contact list view for Lead Generator Standalone."""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from typing import TYPE_CHECKING, Optional

from ui.theme import FONTS
from ui.widgets.data_table import DataTable
from services.contact_service import ContactService
from services.csv_service import CSVService

if TYPE_CHECKING:
    from ui.app import MainApplication


class ContactListView(ttk.Frame):
    """Contact lists and contacts management view."""

    def __init__(self, parent, app: 'MainApplication'):
        super().__init__(parent)
        self.app = app
        self.contact_service = ContactService()
        self.csv_service = CSVService()
        self._selected_list = None
        self._selected_contact = None

        self._create_widgets()
        self.refresh_lists()

    def _create_widgets(self) -> None:
        """Create view widgets."""
        # Main paned window
        paned = ttk.PanedWindow(self, orient=tk.HORIZONTAL)
        paned.pack(fill=tk.BOTH, expand=True)

        # Left panel - Lists
        left_frame = ttk.Frame(paned, width=250)
        paned.add(left_frame, weight=1)

        ttk.Label(left_frame, text="Contact Lists", font=FONTS['subheading']).pack(anchor='w', pady=(0, 10))

        # Lists listbox
        list_frame = ttk.Frame(left_frame)
        list_frame.pack(fill=tk.BOTH, expand=True)

        self.lists_listbox = tk.Listbox(list_frame, selectmode=tk.SINGLE)
        self.lists_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.lists_listbox.bind('<<ListboxSelect>>', self._on_list_select)

        scrollbar = ttk.Scrollbar(list_frame, orient=tk.VERTICAL, command=self.lists_listbox.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.lists_listbox.configure(yscrollcommand=scrollbar.set)

        # List buttons
        list_btn_frame = ttk.Frame(left_frame)
        list_btn_frame.pack(fill=tk.X, pady=(10, 0))

        ttk.Button(list_btn_frame, text="New List", command=self._new_list).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(list_btn_frame, text="Delete List", command=self._delete_list).pack(side=tk.LEFT)

        # Right panel - Contacts
        right_frame = ttk.Frame(paned)
        paned.add(right_frame, weight=3)

        # Header
        header = ttk.Frame(right_frame)
        header.pack(fill=tk.X, pady=(0, 10))

        self.contacts_title = ttk.Label(header, text="Select a list", font=FONTS['subheading'])
        self.contacts_title.pack(side=tk.LEFT)

        btn_frame = ttk.Frame(header)
        btn_frame.pack(side=tk.RIGHT)

        ttk.Button(btn_frame, text="Import CSV", command=self._import_csv).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(btn_frame, text="Export CSV", command=self._export_csv).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(btn_frame, text="Add Contact", command=self._add_contact).pack(side=tk.LEFT)

        # Contacts table
        columns = [
            {'key': 'first_name', 'label': 'First Name', 'width': 100},
            {'key': 'last_name', 'label': 'Last Name', 'width': 100},
            {'key': 'email', 'label': 'Email', 'width': 200},
            {'key': 'company', 'label': 'Company', 'width': 150},
            {'key': 'position', 'label': 'Position', 'width': 120},
        ]

        self.contacts_table = DataTable(
            right_frame,
            columns=columns,
            on_select=self._on_contact_select,
            on_double_click=self._on_contact_double_click,
            show_search=True,
            height=15
        )
        self.contacts_table.pack(fill=tk.BOTH, expand=True, pady=(0, 10))

        # Contact actions
        contact_btn_frame = ttk.Frame(right_frame)
        contact_btn_frame.pack(fill=tk.X)

        self.edit_contact_btn = ttk.Button(contact_btn_frame, text="Edit", command=self._edit_contact, state='disabled')
        self.edit_contact_btn.pack(side=tk.LEFT, padx=(0, 5))

        self.delete_contact_btn = ttk.Button(contact_btn_frame, text="Delete", command=self._delete_contact, state='disabled')
        self.delete_contact_btn.pack(side=tk.LEFT)

    def refresh_lists(self) -> None:
        """Refresh contact lists."""
        self.lists_listbox.delete(0, tk.END)
        lists = self.contact_service.get_all_lists()

        for contact_list in lists:
            self.lists_listbox.insert(tk.END, f"{contact_list.name} ({contact_list.contact_count})")
            # Store list object reference
            self.lists_listbox.itemconfig(tk.END, {'list_id': contact_list.list_id})

        # Store lists for reference
        self._lists = lists

    def refresh_contacts(self) -> None:
        """Refresh contacts for selected list."""
        if not self._selected_list:
            self.contacts_table.set_data([])
            return

        contacts = self.contact_service.get_contacts(self._selected_list.list_id)
        data = []
        for contact in contacts:
            data.append({
                'id': contact.contact_id,
                'first_name': contact.first_name,
                'last_name': contact.last_name,
                'email': contact.email,
                'company': contact.company,
                'position': contact.position or ''
            })
        self.contacts_table.set_data(data)

    def _on_list_select(self, event) -> None:
        """Handle list selection."""
        selection = self.lists_listbox.curselection()
        if selection:
            idx = selection[0]
            if idx < len(self._lists):
                self._selected_list = self._lists[idx]
                self.contacts_title.configure(text=f"Contacts in '{self._selected_list.name}'")
                self.refresh_contacts()

    def _on_contact_select(self, item: dict) -> None:
        """Handle contact selection."""
        self._selected_contact = item
        self.edit_contact_btn.configure(state='normal')
        self.delete_contact_btn.configure(state='normal')

    def _on_contact_double_click(self, item: dict) -> None:
        """Handle contact double-click."""
        self._edit_contact()

    def _new_list(self) -> None:
        """Create new contact list."""
        from tkinter import simpledialog
        name = simpledialog.askstring("New List", "List Name:")
        if name:
            try:
                self.contact_service.create_list(name)
                self.refresh_lists()
            except Exception as e:
                messagebox.showerror("Error", str(e))

    def _delete_list(self) -> None:
        """Delete selected list."""
        if not self._selected_list:
            return

        if messagebox.askyesno("Delete", f"Delete list '{self._selected_list.name}' and all its contacts?"):
            try:
                self.contact_service.delete_list(self._selected_list.list_id)
                self._selected_list = None
                self.refresh_lists()
                self.contacts_table.set_data([])
            except Exception as e:
                messagebox.showerror("Error", str(e))

    def _import_csv(self) -> None:
        """Import contacts from CSV."""
        if not self._selected_list:
            messagebox.showwarning("Warning", "Select a contact list first")
            return

        file_path = filedialog.askopenfilename(
            title="Select CSV File",
            filetypes=[("CSV Files", "*.csv"), ("All Files", "*.*")]
        )

        if file_path:
            try:
                from ui.dialogs.csv_import_wizard import CSVImportWizard
                wizard = CSVImportWizard(self.winfo_toplevel(), file_path, self._selected_list.list_id)
                if wizard.result:
                    self.refresh_lists()
                    self.refresh_contacts()
            except ImportError:
                # Simple fallback import
                self._simple_import(file_path)

    def _simple_import(self, file_path: str) -> None:
        """Simple CSV import without wizard."""
        try:
            headers, preview, total = self.csv_service.read_csv_preview(file_path)
            mapping = self.csv_service.auto_map_fields(headers)

            imported, errors = self.csv_service.import_csv(
                file_path,
                self._selected_list.list_id,
                mapping
            )

            self.refresh_lists()
            self.refresh_contacts()
            messagebox.showinfo("Import Complete", f"Imported {imported} contacts\n{len(errors)} errors")
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def _export_csv(self) -> None:
        """Export contacts to CSV."""
        if not self._selected_list:
            messagebox.showwarning("Warning", "Select a contact list first")
            return

        file_path = filedialog.asksaveasfilename(
            title="Export to CSV",
            defaultextension=".csv",
            filetypes=[("CSV Files", "*.csv")]
        )

        if file_path:
            try:
                count = self.csv_service.export_csv(self._selected_list.list_id, file_path)
                messagebox.showinfo("Export Complete", f"Exported {count} contacts")
            except Exception as e:
                messagebox.showerror("Error", str(e))

    def _add_contact(self) -> None:
        """Add new contact."""
        if not self._selected_list:
            messagebox.showwarning("Warning", "Select a contact list first")
            return

        # Simple dialog for now
        from tkinter import simpledialog
        email = simpledialog.askstring("New Contact", "Email Address:")
        if email:
            try:
                self.contact_service.create_contact(self._selected_list.list_id, {
                    'email': email,
                    'first_name': '',
                    'last_name': '',
                    'company': ''
                })
                self.refresh_lists()
                self.refresh_contacts()
            except Exception as e:
                messagebox.showerror("Error", str(e))

    def _edit_contact(self) -> None:
        """Edit selected contact."""
        if not self._selected_contact:
            return
        messagebox.showinfo("Edit", f"Edit contact: {self._selected_contact.get('email')}")

    def _delete_contact(self) -> None:
        """Delete selected contact."""
        if not self._selected_contact:
            return

        if messagebox.askyesno("Delete", f"Delete contact '{self._selected_contact.get('email')}'?"):
            try:
                self.contact_service.delete_contact(self._selected_contact['id'])
                self._selected_contact = None
                self.refresh_lists()
                self.refresh_contacts()
                self.edit_contact_btn.configure(state='disabled')
                self.delete_contact_btn.configure(state='disabled')
            except Exception as e:
                messagebox.showerror("Error", str(e))
