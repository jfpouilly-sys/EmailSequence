"""Contacts Frame

Contact management with table, filters, and detail panel.
"""

import customtkinter as ctk
from tkinter import filedialog
from gui.components.contact_table import ContactTable
from gui.components.status_badge import StatusBadge
from gui.dialogs import ConfirmationDialog, CSVImportDialog, InfoDialog, ProgressDialog
import pandas as pd
from typing import Optional, Dict, List


class ContactsFrame(ctk.CTkFrame):
    """Contact management with table and detail panel."""

    SYSTEM_FIELDS = ['title', 'first_name', 'last_name', 'email', 'company', 'status']

    STATUS_OPTIONS = ['All Statuses', 'pending', 'sent', 'followup_1', 'followup_2',
                      'followup_3', 'replied', 'bounced', 'opted_out', 'completed']

    def __init__(self, parent, app):
        """Initialize contacts frame.

        Args:
            parent: Parent widget
            app: Main application instance
        """
        super().__init__(parent, fg_color="transparent")

        self.app = app
        self.gui_config = app.gui_config
        self.contacts_df: Optional[pd.DataFrame] = None
        self.selected_contact: Optional[Dict] = None

        # Configure grid
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(2, weight=2)  # Table row
        self.grid_rowconfigure(3, weight=1)  # Detail panel row

        # Create components
        self.create_header()
        self.create_toolbar()
        self.create_contact_table()
        self.create_detail_panel()

        # Load contacts
        self.load_contacts()

    def create_header(self) -> None:
        """Create header with title."""
        title_label = ctk.CTkLabel(
            self,
            text="CONTACTS",
            font=("Arial Bold", 24),
            anchor="w"
        )
        title_label.grid(row=0, column=0, sticky="w", pady=(10, 20), padx=20)

    def create_toolbar(self) -> None:
        """Create toolbar with buttons and filters."""
        toolbar = ctk.CTkFrame(self, fg_color="transparent")
        toolbar.grid(row=1, column=0, sticky="ew", padx=20, pady=(0, 10))
        toolbar.grid_columnconfigure(4, weight=1)

        # Add Contact button
        add_btn = ctk.CTkButton(
            toolbar,
            text="+ Add Contact",
            command=self.on_add_contact,
            width=120,
            height=32
        )
        add_btn.grid(row=0, column=0, padx=(0, 5))

        # Import CSV button
        import_btn = ctk.CTkButton(
            toolbar,
            text="📥 Import CSV",
            command=self.on_import_csv,
            width=120,
            height=32,
            fg_color="gray"
        )
        import_btn.grid(row=0, column=1, padx=5)

        # Export button
        export_btn = ctk.CTkButton(
            toolbar,
            text="📤 Export",
            command=self.on_export,
            width=100,
            height=32,
            fg_color="gray"
        )
        export_btn.grid(row=0, column=2, padx=5)

        # Delete Selected button
        delete_btn = ctk.CTkButton(
            toolbar,
            text="🗑 Delete Selected",
            command=self.on_delete_selected,
            width=140,
            height=32,
            fg_color="#EF4444",
            hover_color="#DC2626"
        )
        delete_btn.grid(row=0, column=3, padx=5)

        # Filter dropdown
        filter_label = ctk.CTkLabel(toolbar, text="Filter:", font=("Arial", 11))
        filter_label.grid(row=0, column=4, padx=(20, 5), sticky="e")

        self.filter_var = ctk.StringVar(value="All Statuses")
        filter_menu = ctk.CTkOptionMenu(
            toolbar,
            variable=self.filter_var,
            values=self.STATUS_OPTIONS,
            command=self.on_filter_change,
            width=150
        )
        filter_menu.grid(row=0, column=5, padx=5)

        # Search box
        search_label = ctk.CTkLabel(toolbar, text="Search:", font=("Arial", 11))
        search_label.grid(row=0, column=6, padx=(10, 5))

        self.search_var = ctk.StringVar()
        self.search_var.trace('w', lambda *args: self.on_search_change())
        search_entry = ctk.CTkEntry(
            toolbar,
            textvariable=self.search_var,
            placeholder_text="Search...",
            width=200
        )
        search_entry.grid(row=0, column=7, padx=5)

    def create_contact_table(self) -> None:
        """Create contact table."""
        table_frame = ctk.CTkFrame(self)
        table_frame.grid(row=2, column=0, sticky="nsew", padx=20, pady=(0, 10))
        table_frame.grid_columnconfigure(0, weight=1)
        table_frame.grid_rowconfigure(0, weight=1)

        # Define columns
        columns = [
            {'id': 'title', 'text': 'Title', 'width': 60, 'minwidth': 50},
            {'id': 'first_name', 'text': 'First Name', 'width': 120, 'minwidth': 80},
            {'id': 'last_name', 'text': 'Last Name', 'width': 120, 'minwidth': 80},
            {'id': 'email', 'text': 'Email', 'width': 200, 'minwidth': 150},
            {'id': 'company', 'text': 'Company', 'width': 150, 'minwidth': 100},
            {'id': 'status', 'text': 'Status', 'width': 120, 'minwidth': 80, 'type': 'status'}
        ]

        self.table = ContactTable(
            table_frame,
            columns=columns,
            on_select=self.on_row_select,
            show_checkboxes=True
        )
        self.table.grid(row=0, column=0, sticky="nsew")

    def create_detail_panel(self) -> None:
        """Create detail panel for editing selected contact."""
        detail_frame = ctk.CTkFrame(self)
        detail_frame.grid(row=3, column=0, sticky="nsew", padx=20, pady=(0, 20))
        detail_frame.grid_columnconfigure((0, 1, 2, 3), weight=1)

        # Title
        title_label = ctk.CTkLabel(
            detail_frame,
            text="CONTACT DETAILS (select a contact above)",
            font=("Arial Bold", 14),
            anchor="w"
        )
        title_label.grid(row=0, column=0, columnspan=4, sticky="w", padx=15, pady=(15, 10))

        # Input fields
        row = 1

        # Title field
        ctk.CTkLabel(detail_frame, text="Title:", font=("Arial", 11)).grid(
            row=row, column=0, sticky="w", padx=(15, 5), pady=5
        )
        self.title_var = ctk.StringVar()
        title_menu = ctk.CTkOptionMenu(
            detail_frame,
            variable=self.title_var,
            values=["Mr", "Ms", "Mrs", "Dr", "Prof"],
            width=100
        )
        title_menu.grid(row=row, column=0, sticky="e", padx=5, pady=5)

        # First name
        ctk.CTkLabel(detail_frame, text="First:", font=("Arial", 11)).grid(
            row=row, column=1, sticky="w", padx=(15, 5), pady=5
        )
        self.first_var = ctk.StringVar()
        first_entry = ctk.CTkEntry(detail_frame, textvariable=self.first_var, width=150)
        first_entry.grid(row=row, column=1, sticky="e", padx=5, pady=5)

        # Last name
        ctk.CTkLabel(detail_frame, text="Last:", font=("Arial", 11)).grid(
            row=row, column=2, sticky="w", padx=(15, 5), pady=5
        )
        self.last_var = ctk.StringVar()
        last_entry = ctk.CTkEntry(detail_frame, textvariable=self.last_var, width=150)
        last_entry.grid(row=row, column=2, sticky="e", padx=5, pady=5)

        row += 1

        # Email
        ctk.CTkLabel(detail_frame, text="Email:", font=("Arial", 11)).grid(
            row=row, column=0, sticky="w", padx=(15, 5), pady=5
        )
        self.email_var = ctk.StringVar()
        email_entry = ctk.CTkEntry(detail_frame, textvariable=self.email_var, width=250)
        email_entry.grid(row=row, column=0, columnspan=2, sticky="e", padx=5, pady=5)

        # Company
        ctk.CTkLabel(detail_frame, text="Company:", font=("Arial", 11)).grid(
            row=row, column=2, sticky="w", padx=(15, 5), pady=5
        )
        self.company_var = ctk.StringVar()
        company_entry = ctk.CTkEntry(detail_frame, textvariable=self.company_var, width=200)
        company_entry.grid(row=row, column=2, columnspan=2, sticky="e", padx=5, pady=5)

        row += 1

        # Status display
        status_label = ctk.CTkLabel(
            detail_frame,
            text="Status:",
            font=("Arial", 11)
        )
        status_label.grid(row=row, column=0, sticky="w", padx=(15, 5), pady=10)

        self.status_badge = StatusBadge(detail_frame, status='pending', show_text=True)
        self.status_badge.grid(row=row, column=0, sticky="e", padx=5, pady=10)

        # Buttons
        button_frame = ctk.CTkFrame(detail_frame, fg_color="transparent")
        button_frame.grid(row=row, column=1, columnspan=3, sticky="e", padx=15, pady=10)

        save_btn = ctk.CTkButton(
            button_frame,
            text="💾 Save Changes",
            command=self.on_save_contact,
            width=140,
            fg_color="#10B981"
        )
        save_btn.pack(side="left", padx=5)

        reset_btn = ctk.CTkButton(
            button_frame,
            text="↻ Reset Status",
            command=self.on_reset_status,
            width=120,
            fg_color="gray"
        )
        reset_btn.pack(side="left", padx=5)

        optout_btn = ctk.CTkButton(
            button_frame,
            text="⛔ Mark Opted-Out",
            command=self.on_mark_optout,
            width=140,
            fg_color="#EF4444"
        )
        optout_btn.pack(side="left", padx=5)

    def load_contacts(self, filter_status: str = None, search: str = None) -> None:
        """Load contacts from Excel file.

        Args:
            filter_status: Status to filter by
            search: Search string
        """
        try:
            contacts_file = self.gui_config.get_campaign_contacts_file()

            if not contacts_file.exists():
                # Create empty DataFrame with required columns
                self.contacts_df = pd.DataFrame(columns=self.SYSTEM_FIELDS)
                self.table.load_data([])
                return

            # Load Excel file
            self.contacts_df = pd.read_excel(contacts_file)

            # Apply filters
            filtered_df = self.contacts_df

            if filter_status and filter_status != "All Statuses":
                filtered_df = filtered_df[filtered_df['status'] == filter_status]

            if search:
                search_lower = search.lower()
                mask = (
                    filtered_df['first_name'].str.lower().str.contains(search_lower, na=False) |
                    filtered_df['last_name'].str.lower().str.contains(search_lower, na=False) |
                    filtered_df['email'].str.lower().str.contains(search_lower, na=False) |
                    filtered_df['company'].str.lower().str.contains(search_lower, na=False)
                )
                filtered_df = filtered_df[mask]

            # Convert to list of dicts for table
            contacts_list = filtered_df.to_dict('records')
            self.table.load_data(contacts_list)

            # Update status
            self.app.update_status_bar(
                message=f"Loaded {len(contacts_list)} contacts"
            )

        except Exception as e:
            print(f"Error loading contacts: {e}")
            InfoDialog.show(self, "Error", f"Failed to load contacts:\n{str(e)}")

    def on_row_select(self, contact: Dict) -> None:
        """Handle row selection.

        Args:
            contact: Selected contact dictionary
        """
        self.selected_contact = contact

        # Populate detail panel
        self.title_var.set(contact.get('title', 'Mr'))
        self.first_var.set(contact.get('first_name', ''))
        self.last_var.set(contact.get('last_name', ''))
        self.email_var.set(contact.get('email', ''))
        self.company_var.set(contact.get('company', ''))

        status = contact.get('status', 'pending')
        self.status_badge.update_status(status)

    def on_filter_change(self, value: str) -> None:
        """Handle filter dropdown change.

        Args:
            value: Selected filter value
        """
        self.load_contacts(
            filter_status=value,
            search=self.search_var.get()
        )

    def on_search_change(self) -> None:
        """Handle search box change."""
        self.load_contacts(
            filter_status=self.filter_var.get(),
            search=self.search_var.get()
        )

    def on_add_contact(self) -> None:
        """Handle Add Contact button click."""
        # Clear detail panel for new entry
        self.selected_contact = None
        self.title_var.set('Mr')
        self.first_var.set('')
        self.last_var.set('')
        self.email_var.set('')
        self.company_var.set('')
        self.status_badge.update_status('pending')

    def on_save_contact(self) -> None:
        """Handle Save Changes button click."""
        if not self.email_var.get():
            InfoDialog.show(self, "Validation Error", "Email is required.")
            return

        try:
            # Create contact dict
            contact = {
                'title': self.title_var.get(),
                'first_name': self.first_var.get(),
                'last_name': self.last_var.get(),
                'email': self.email_var.get(),
                'company': self.company_var.get(),
                'status': self.status_badge.get_status()
            }

            # Update or add to dataframe
            if self.selected_contact:
                # Update existing
                mask = self.contacts_df['email'] == self.selected_contact['email']
                for key, value in contact.items():
                    self.contacts_df.loc[mask, key] = value
            else:
                # Add new
                self.contacts_df = pd.concat([
                    self.contacts_df,
                    pd.DataFrame([contact])
                ], ignore_index=True)

            # Save to file
            contacts_file = self.gui_config.get_campaign_contacts_file()
            self.contacts_df.to_excel(contacts_file, index=False)

            # Reload table
            self.load_contacts()

            InfoDialog.show(self, "Success", "Contact saved successfully.")

        except Exception as e:
            InfoDialog.show(self, "Error", f"Failed to save contact:\n{str(e)}")

    def on_reset_status(self) -> None:
        """Handle Reset Status button click."""
        self.status_badge.update_status('pending')

    def on_mark_optout(self) -> None:
        """Handle Mark Opted-Out button click."""
        self.status_badge.update_status('opted_out')

    def on_delete_selected(self) -> None:
        """Handle Delete Selected button click."""
        selected = self.table.get_selected_rows()

        if not selected:
            InfoDialog.show(self, "No Selection", "Please select contacts to delete.")
            return

        # Confirm deletion
        dialog = ConfirmationDialog(
            self,
            "Delete Contacts",
            f"Delete {len(selected)} selected contact(s)?",
            confirm_text="Delete",
            cancel_text="Cancel",
            danger=True
        )

        if not dialog.get_result():
            return

        try:
            # Remove from dataframe
            self.contacts_df = self.contacts_df[~self.contacts_df['email'].isin(selected)]

            # Save to file
            contacts_file = self.gui_config.get_campaign_contacts_file()
            self.contacts_df.to_excel(contacts_file, index=False)

            # Clear selection and reload
            self.table.clear_selection()
            self.load_contacts()

            InfoDialog.show(self, "Success", f"{len(selected)} contact(s) deleted.")

        except Exception as e:
            InfoDialog.show(self, "Error", f"Failed to delete contacts:\n{str(e)}")

    def on_import_csv(self) -> None:
        """Handle Import CSV button click."""
        # Open file dialog
        filename = filedialog.askopenfilename(
            title="Select CSV File",
            filetypes=[("CSV files", "*.csv"), ("All files", "*.*")]
        )

        if not filename:
            return

        try:
            # Read CSV
            csv_df = pd.read_csv(filename)
            csv_columns = list(csv_df.columns)

            # Show mapping dialog
            dialog = CSVImportDialog(self, csv_columns, self.SYSTEM_FIELDS)
            mapping = dialog.get_mapping()

            if not mapping:
                return

            # Map columns
            import_data = {}
            for csv_col, system_field in mapping.items():
                import_data[system_field] = csv_df[csv_col]

            # Add default status if not mapped
            if 'status' not in import_data:
                import_data['status'] = 'pending'

            # Create dataframe
            import_df = pd.DataFrame(import_data)

            # Append to existing contacts
            self.contacts_df = pd.concat([self.contacts_df, import_df], ignore_index=True)

            # Remove duplicates by email
            self.contacts_df = self.contacts_df.drop_duplicates(subset=['email'], keep='first')

            # Save to file
            contacts_file = self.gui_config.get_campaign_contacts_file()
            self.contacts_df.to_excel(contacts_file, index=False)

            # Reload
            self.load_contacts()

            InfoDialog.show(self, "Success", f"Imported {len(import_df)} contacts.")

        except Exception as e:
            InfoDialog.show(self, "Import Error", f"Failed to import CSV:\n{str(e)}")

    def on_export(self) -> None:
        """Handle Export button click."""
        # Open save dialog
        filename = filedialog.asksaveasfilename(
            title="Export Contacts",
            defaultextension=".xlsx",
            filetypes=[("Excel files", "*.xlsx"), ("CSV files", "*.csv"), ("All files", "*.*")]
        )

        if not filename:
            return

        try:
            if filename.endswith('.csv'):
                self.contacts_df.to_csv(filename, index=False)
            else:
                self.contacts_df.to_excel(filename, index=False)

            InfoDialog.show(self, "Success", f"Exported {len(self.contacts_df)} contacts.")

        except Exception as e:
            InfoDialog.show(self, "Export Error", f"Failed to export:\n{str(e)}")
