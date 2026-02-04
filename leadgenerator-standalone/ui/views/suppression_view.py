"""Suppression list view for Lead Generator Standalone."""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog, simpledialog
from typing import TYPE_CHECKING

from ui.theme import FONTS
from ui.widgets.data_table import DataTable
from services.suppression_service import SuppressionService

if TYPE_CHECKING:
    from ui.app import MainApplication


class SuppressionView(ttk.Frame):
    """Suppression (unsubscribe) list view."""

    def __init__(self, parent, app: 'MainApplication'):
        super().__init__(parent)
        self.app = app
        self.suppression_service = SuppressionService()
        self._selected_entry = None

        self._create_widgets()
        self.refresh()

    def _create_widgets(self) -> None:
        """Create view widgets."""
        # Header
        header = ttk.Frame(self)
        header.pack(fill=tk.X, pady=(0, 10))

        ttk.Label(header, text="Suppression List", font=FONTS['heading']).pack(side=tk.LEFT)

        # Stats
        self.count_label = ttk.Label(header, text="0 entries")
        self.count_label.pack(side=tk.RIGHT)

        # Table
        columns = [
            {'key': 'email', 'label': 'Email', 'width': 250},
            {'key': 'scope', 'label': 'Scope', 'width': 80, 'anchor': 'center'},
            {'key': 'source', 'label': 'Source', 'width': 100, 'anchor': 'center'},
            {'key': 'reason', 'label': 'Reason', 'width': 200},
            {'key': 'created_at', 'label': 'Added', 'width': 100},
        ]

        self.table = DataTable(
            self,
            columns=columns,
            on_select=self._on_select,
            show_search=True,
            height=18
        )
        self.table.pack(fill=tk.BOTH, expand=True, pady=(0, 10))

        # Actions
        actions_frame = ttk.Frame(self)
        actions_frame.pack(fill=tk.X)

        ttk.Button(actions_frame, text="Add Email", command=self._add_email).pack(side=tk.LEFT, padx=(0, 5))

        self.remove_btn = ttk.Button(actions_frame, text="Remove", command=self._remove_email, state='disabled')
        self.remove_btn.pack(side=tk.LEFT, padx=(0, 20))

        ttk.Button(actions_frame, text="Import CSV", command=self._import_csv).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(actions_frame, text="Export CSV", command=self._export_csv).pack(side=tk.LEFT)

    def refresh(self) -> None:
        """Refresh suppression list."""
        entries = self.suppression_service.get_suppression_list(limit=5000)
        count = self.suppression_service.get_suppression_count()

        data = []
        for entry in entries:
            data.append({
                'email': entry.email,
                'scope': entry.scope,
                'source': entry.source,
                'reason': entry.reason or '',
                'created_at': entry.created_at[:10] if entry.created_at else ''
            })

        self.table.set_data(data)
        self.count_label.configure(text=f"{count} entries")

    def _on_select(self, item: dict) -> None:
        """Handle selection."""
        self._selected_entry = item
        self.remove_btn.configure(state='normal')

    def _add_email(self) -> None:
        """Add email to suppression list."""
        email = simpledialog.askstring("Add to Suppression", "Email address:")
        if email:
            try:
                self.suppression_service.add_to_suppression(
                    email=email,
                    source='Manual',
                    scope='Global'
                )
                self.refresh()
            except Exception as e:
                messagebox.showerror("Error", str(e))

    def _remove_email(self) -> None:
        """Remove email from suppression list."""
        if not self._selected_entry:
            return

        email = self._selected_entry['email']
        if messagebox.askyesno("Remove", f"Remove '{email}' from suppression list?"):
            try:
                self.suppression_service.remove_from_suppression(email)
                self._selected_entry = None
                self.remove_btn.configure(state='disabled')
                self.refresh()
            except Exception as e:
                messagebox.showerror("Error", str(e))

    def _import_csv(self) -> None:
        """Import emails from CSV."""
        file_path = filedialog.askopenfilename(
            title="Import Suppression List",
            filetypes=[("CSV Files", "*.csv"), ("Text Files", "*.txt"), ("All Files", "*.*")]
        )

        if file_path:
            try:
                # Read emails from file
                emails = []
                with open(file_path, 'r', encoding='utf-8') as f:
                    for line in f:
                        email = line.strip().lower()
                        if email and '@' in email:
                            emails.append(email)

                if emails:
                    added = self.suppression_service.import_suppression_list(emails)
                    self.refresh()
                    messagebox.showinfo("Import Complete", f"Added {added} emails")
                else:
                    messagebox.showwarning("Warning", "No valid emails found in file")
            except Exception as e:
                messagebox.showerror("Error", str(e))

    def _export_csv(self) -> None:
        """Export suppression list to CSV."""
        file_path = filedialog.asksaveasfilename(
            title="Export Suppression List",
            defaultextension=".csv",
            filetypes=[("CSV Files", "*.csv")]
        )

        if file_path:
            try:
                count = self.suppression_service.export_suppression_list(file_path)
                messagebox.showinfo("Export Complete", f"Exported {count} entries")
            except Exception as e:
                messagebox.showerror("Error", str(e))
