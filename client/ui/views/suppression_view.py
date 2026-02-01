"""Suppression list management view."""
import logging
import tkinter as tk
from tkinter import filedialog
from typing import Optional
import ttkbootstrap as ttk
from ttkbootstrap.constants import *

from core.api_client import ApiClient
from ui.widgets.data_table import DataTable

logger = logging.getLogger(__name__)


class SuppressionView(ttk.Frame):
    """Suppression list management view."""

    def __init__(self, parent, app=None, api: ApiClient = None, **kwargs):
        super().__init__(parent, **kwargs)

        self.app = app
        self.api = api

        self._create_widgets()

    def _create_widgets(self) -> None:
        """Create view widgets."""
        # Header
        header = ttk.Frame(self)
        header.pack(fill=X, pady=(0, 15))

        ttk.Label(
            header,
            text="Suppression List",
            font=("Segoe UI", 14, "bold")
        ).pack(side=LEFT)

        # Actions
        actions = ttk.Frame(header)
        actions.pack(side=RIGHT)

        ttk.Button(
            actions,
            text="+ Add Email",
            bootstyle="success",
            command=self._on_add
        ).pack(side=LEFT, padx=5)

        ttk.Button(
            actions,
            text="Import",
            bootstyle="outline-primary",
            command=self._on_import
        ).pack(side=LEFT, padx=5)

        ttk.Button(
            actions,
            text="Export",
            bootstyle="outline-secondary",
            command=self._on_export
        ).pack(side=LEFT, padx=5)

        # Check email section
        check_frame = ttk.LabelFrame(self, text="Check Email", padding=10)
        check_frame.pack(fill=X, pady=(0, 15))

        check_row = ttk.Frame(check_frame)
        check_row.pack(fill=X)

        self.check_var = tk.StringVar()
        ttk.Entry(
            check_row,
            textvariable=self.check_var,
            width=40
        ).pack(side=LEFT, padx=(0, 10))

        ttk.Button(
            check_row,
            text="Check",
            bootstyle="info",
            command=self._on_check
        ).pack(side=LEFT)

        self.check_result = ttk.Label(
            check_frame,
            text="",
            font=("Segoe UI", 9)
        )
        self.check_result.pack(anchor=W, pady=(10, 0))

        # Suppression table
        columns = [
            {"id": "id", "text": "ID", "width": 0},
            {"id": "email", "text": "Email Address", "width": 300, "anchor": "w"},
            {"id": "scope", "text": "Scope", "width": 100, "anchor": "center"},
            {"id": "source", "text": "Source", "width": 100, "anchor": "center"},
            {"id": "reason", "text": "Reason", "width": 200, "anchor": "w"},
            {"id": "created", "text": "Added", "width": 120, "anchor": "center"},
        ]

        self.table = DataTable(
            self,
            columns=columns,
            show_search=True,
            on_select=self._on_select
        )
        self.table.pack(fill=BOTH, expand=True)

        # Bottom info
        bottom = ttk.Frame(self)
        bottom.pack(fill=X, pady=(10, 0))

        self.count_label = ttk.Label(
            bottom,
            text="",
            font=("Segoe UI", 9),
            bootstyle="secondary"
        )
        self.count_label.pack(side=LEFT)

        self.remove_btn = ttk.Button(
            bottom,
            text="Remove from List",
            bootstyle="danger-outline",
            command=self._on_remove,
            state="disabled"
        )
        self.remove_btn.pack(side=RIGHT)

        # Info
        info_frame = ttk.Frame(self)
        info_frame.pack(fill=X, pady=(10, 0))

        ttk.Label(
            info_frame,
            text="Emails in suppression list will not receive any campaign emails",
            font=("Segoe UI", 9),
            bootstyle="secondary"
        ).pack(side=LEFT)

    def refresh(self) -> None:
        """Refresh suppression list."""
        if not self.api:
            return

        try:
            entries = self.api.get_suppression_list()
            data = []
            for e in entries:
                created = e.created_at.strftime("%Y-%m-%d %H:%M") if e.created_at else ""
                data.append({
                    "id": e.suppression_id,
                    "email": e.email,
                    "scope": e.scope.value,
                    "source": e.source.value,
                    "reason": e.reason or "",
                    "created": created
                })
            self.table.set_data(data)
            self.count_label.configure(text=f"{len(entries)} suppressed emails")

            if self.app:
                self.app.set_status(f"Loaded {len(entries)} suppression entries")

        except Exception as e:
            logger.error(f"Error loading suppression list: {e}")
            if self.app:
                self.app.set_status(f"Error: {str(e)}")

    def _on_select(self, entry_id: str) -> None:
        """Handle selection."""
        self.remove_btn.configure(state="normal")

    def _on_add(self) -> None:
        """Add email to suppression list."""
        dialog = AddSuppressionDialog(self, self.api)
        self.wait_window(dialog)
        if dialog.result:
            self.refresh()

    def _on_check(self) -> None:
        """Check if email is suppressed."""
        email = self.check_var.get().strip()
        if not email:
            return

        try:
            is_suppressed = self.api.check_suppression(email)
            if is_suppressed:
                self.check_result.configure(
                    text=f"\u2717 {email} IS suppressed",
                    bootstyle="danger"
                )
            else:
                self.check_result.configure(
                    text=f"\u2713 {email} is NOT suppressed",
                    bootstyle="success"
                )
        except Exception as e:
            self.check_result.configure(
                text=f"Error: {str(e)}",
                bootstyle="danger"
            )

    def _on_remove(self) -> None:
        """Remove from suppression list."""
        selected = self.table.get_selected()
        if not selected:
            return

        email = selected.get("email", "")
        if self.app and self.app.ask_confirmation(
            "Remove from Suppression",
            f"Remove {email} from suppression list?"
        ):
            if self.app:
                self.app.show_info("Note", "Removal from suppression list via API is not implemented")

    def _on_import(self) -> None:
        """Import suppression list from CSV."""
        filepath = filedialog.askopenfilename(
            filetypes=[("CSV files", "*.csv"), ("Text files", "*.txt")]
        )
        if filepath:
            try:
                count = 0
                with open(filepath, 'r') as f:
                    for line in f:
                        email = line.strip()
                        if email and '@' in email:
                            try:
                                self.api.add_to_suppression(email, scope="Global", reason="Imported")
                                count += 1
                            except Exception:
                                pass

                if self.app:
                    self.app.show_info("Import Complete", f"Imported {count} emails")
                self.refresh()
            except Exception as e:
                if self.app:
                    self.app.show_error("Import Error", str(e))

    def _on_export(self) -> None:
        """Export suppression list."""
        filepath = filedialog.asksaveasfilename(
            defaultextension=".csv",
            filetypes=[("CSV files", "*.csv")]
        )
        if filepath:
            try:
                entries = self.api.get_suppression_list()
                with open(filepath, 'w') as f:
                    f.write("Email,Scope,Source,Reason,Created\n")
                    for e in entries:
                        created = e.created_at.strftime("%Y-%m-%d") if e.created_at else ""
                        f.write(f"{e.email},{e.scope.value},{e.source.value},{e.reason or ''},{created}\n")

                if self.app:
                    self.app.set_status(f"Exported {len(entries)} entries to {filepath}")
            except Exception as e:
                if self.app:
                    self.app.show_error("Export Error", str(e))


class AddSuppressionDialog(ttk.Toplevel):
    """Dialog for adding email to suppression list."""

    def __init__(self, parent, api: ApiClient):
        super().__init__(parent)

        self.api = api
        self.result = None

        self.title("Add to Suppression List")
        self.geometry("400x250")
        self.resizable(False, False)

        self._create_widgets()
        self.transient(parent)
        self.grab_set()

    def _create_widgets(self) -> None:
        """Create dialog widgets."""
        main = ttk.Frame(self, padding=20)
        main.pack(fill=BOTH, expand=True)

        # Email
        ttk.Label(main, text="Email Address *").pack(anchor=W, pady=(0, 5))
        self.email_var = tk.StringVar()
        ttk.Entry(main, textvariable=self.email_var, width=45).pack(fill=X, pady=(0, 10))

        # Scope
        ttk.Label(main, text="Scope").pack(anchor=W, pady=(0, 5))
        self.scope_var = tk.StringVar(value="Global")
        scope_combo = ttk.Combobox(
            main,
            textvariable=self.scope_var,
            values=["Global", "Campaign"],
            state="readonly",
            width=42
        )
        scope_combo.pack(fill=X, pady=(0, 10))

        # Reason
        ttk.Label(main, text="Reason").pack(anchor=W, pady=(0, 5))
        self.reason_var = tk.StringVar()
        ttk.Entry(main, textvariable=self.reason_var, width=45).pack(fill=X, pady=(0, 10))

        # Buttons
        btn_frame = ttk.Frame(main)
        btn_frame.pack(fill=X, pady=(15, 0))

        ttk.Button(btn_frame, text="Cancel", bootstyle="secondary", command=self.destroy).pack(side=RIGHT, padx=5)
        ttk.Button(btn_frame, text="Add", bootstyle="primary", command=self._on_add).pack(side=RIGHT)

    def _on_add(self) -> None:
        """Add to suppression list."""
        email = self.email_var.get().strip()
        if not email or '@' not in email:
            from tkinter import messagebox
            messagebox.showerror("Error", "Please enter a valid email address", parent=self)
            return

        try:
            self.api.add_to_suppression(
                email=email,
                scope=self.scope_var.get(),
                reason=self.reason_var.get().strip() or None
            )
            self.result = True
            self.destroy()
        except Exception as e:
            from tkinter import messagebox
            messagebox.showerror("Error", str(e), parent=self)
