"""Mail accounts management view (Admin only)."""
import logging
import tkinter as tk
from typing import Optional
import ttkbootstrap as ttk
from ttkbootstrap.constants import *

from core.api_client import ApiClient
from ui.widgets.data_table import DataTable

logger = logging.getLogger(__name__)


class MailAccountsView(ttk.Frame):
    """Mail accounts management view for administrators."""

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
            text="Mail Accounts",
            font=("Segoe UI", 14, "bold")
        ).pack(side=LEFT)

        ttk.Button(
            header,
            text="+ Add Account",
            bootstyle="success",
            command=self._on_add
        ).pack(side=RIGHT)

        # Accounts table
        columns = [
            {"id": "id", "text": "ID", "width": 0},
            {"id": "email", "text": "Email Address", "width": 250, "anchor": "w"},
            {"id": "display_name", "text": "Display Name", "width": 150, "anchor": "w"},
            {"id": "status", "text": "Status", "width": 80, "anchor": "center"},
            {"id": "daily_limit", "text": "Daily Limit", "width": 80, "anchor": "center"},
            {"id": "hourly_limit", "text": "Hourly Limit", "width": 80, "anchor": "center"},
            {"id": "sent_today", "text": "Sent Today", "width": 80, "anchor": "center"},
            {"id": "warmup", "text": "Warmup", "width": 80, "anchor": "center"},
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

        self.edit_btn = ttk.Button(
            bottom,
            text="Edit Account",
            bootstyle="primary-outline",
            command=self._on_edit_click,
            state="disabled"
        )
        self.edit_btn.pack(side=LEFT, padx=5)

        self.warmup_btn = ttk.Button(
            bottom,
            text="Toggle Warmup",
            bootstyle="info-outline",
            command=self._on_toggle_warmup,
            state="disabled"
        )
        self.warmup_btn.pack(side=LEFT, padx=5)

        self.toggle_btn = ttk.Button(
            bottom,
            text="Deactivate",
            bootstyle="danger-outline",
            command=self._on_toggle_status,
            state="disabled"
        )
        self.toggle_btn.pack(side=LEFT, padx=5)

        # Info panel
        info_frame = ttk.LabelFrame(self, text="Warmup Information", padding=10)
        info_frame.pack(fill=X, pady=(15, 0))

        ttk.Label(
            info_frame,
            text="Warmup Mode: Gradually increases sending volume over 22 days",
            font=("Segoe UI", 9)
        ).pack(anchor=W)

        ttk.Label(
            info_frame,
            text="Schedule: Day 1-5: 20% | Day 6-10: 40% | Day 11-15: 60% | Day 16-20: 80% | Day 21+: 100%",
            font=("Segoe UI", 9),
            bootstyle="secondary"
        ).pack(anchor=W, pady=(5, 0))

    def refresh(self) -> None:
        """Refresh accounts list."""
        if not self.api:
            return

        try:
            accounts = self.api.get_mail_accounts()
            data = []
            for a in accounts:
                data.append({
                    "id": a.account_id,
                    "email": a.email_address,
                    "display_name": a.display_name,
                    "status": "Active" if a.is_active else "Inactive",
                    "daily_limit": str(a.daily_limit),
                    "hourly_limit": str(a.hourly_limit),
                    "sent_today": str(a.emails_sent_today),
                    "warmup": f"Day {a.warmup_day}" if a.warmup_enabled else "Off"
                })
            self.table.set_data(data)

            if self.app:
                self.app.set_status(f"Loaded {len(accounts)} mail accounts")

        except Exception as e:
            logger.error(f"Error loading accounts: {e}")
            if self.app:
                self.app.set_status(f"Error: {str(e)}")

    def _on_select(self, account_id: str) -> None:
        """Handle account selection."""
        self.edit_btn.configure(state="normal")
        self.warmup_btn.configure(state="normal")
        self.toggle_btn.configure(state="normal")

        selected = self.table.get_selected()
        if selected:
            status = selected.get("status", "")
            if status == "Active":
                self.toggle_btn.configure(text="Deactivate")
            else:
                self.toggle_btn.configure(text="Activate")

    def _on_add(self) -> None:
        """Add new mail account."""
        dialog = MailAccountDialog(self, self.api)
        self.wait_window(dialog)
        if dialog.result:
            self.refresh()

    def _on_edit_click(self) -> None:
        """Edit selected account."""
        account_id = self.table.get_selected_id()
        if account_id:
            self._on_edit(account_id)

    def _on_edit(self, account_id: str) -> None:
        """Edit mail account."""
        dialog = MailAccountDialog(self, self.api, account_id=account_id)
        self.wait_window(dialog)
        if dialog.result:
            self.refresh()

    def _on_toggle_warmup(self) -> None:
        """Toggle warmup mode."""
        account_id = self.table.get_selected_id()
        selected = self.table.get_selected()
        if not account_id or not selected:
            return

        warmup_enabled = selected.get("warmup", "") != "Off"

        try:
            self.api.update_mail_account(
                account_id,
                warmupEnabled=not warmup_enabled,
                warmupDay=0 if warmup_enabled else 1
            )
            self.refresh()
        except Exception as e:
            if self.app:
                self.app.show_error("Error", str(e))

    def _on_toggle_status(self) -> None:
        """Toggle account active status."""
        account_id = self.table.get_selected_id()
        selected = self.table.get_selected()
        if not account_id or not selected:
            return

        is_active = selected.get("status", "") == "Active"

        try:
            self.api.update_mail_account(account_id, isActive=not is_active)
            self.refresh()
        except Exception as e:
            if self.app:
                self.app.show_error("Error", str(e))


class MailAccountDialog(ttk.Toplevel):
    """Dialog for creating/editing mail accounts."""

    def __init__(self, parent, api: ApiClient, account_id: str = None):
        super().__init__(parent)

        self.api = api
        self.account_id = account_id
        self.result = None

        self.title("New Mail Account" if not account_id else "Edit Mail Account")
        self.geometry("450x350")
        self.resizable(False, False)

        self._create_widgets()

        if account_id:
            self._load_account()

        self.transient(parent)
        self.grab_set()

    def _create_widgets(self) -> None:
        """Create form widgets."""
        main = ttk.Frame(self, padding=20)
        main.pack(fill=BOTH, expand=True)

        # Email
        ttk.Label(main, text="Email Address *").pack(anchor=W, pady=(0, 5))
        self.email_var = tk.StringVar()
        self.email_entry = ttk.Entry(main, textvariable=self.email_var, width=45)
        self.email_entry.pack(fill=X, pady=(0, 10))

        # Display Name
        ttk.Label(main, text="Display Name *").pack(anchor=W, pady=(0, 5))
        self.name_var = tk.StringVar()
        ttk.Entry(main, textvariable=self.name_var, width=45).pack(fill=X, pady=(0, 10))

        # Limits frame
        limits_frame = ttk.Frame(main)
        limits_frame.pack(fill=X, pady=(0, 10))

        # Daily Limit
        left = ttk.Frame(limits_frame)
        left.pack(side=LEFT, fill=X, expand=True, padx=(0, 10))
        ttk.Label(left, text="Daily Limit").pack(anchor=W)
        self.daily_var = tk.StringVar(value="100")
        ttk.Entry(left, textvariable=self.daily_var).pack(fill=X)

        # Hourly Limit
        right = ttk.Frame(limits_frame)
        right.pack(side=LEFT, fill=X, expand=True)
        ttk.Label(right, text="Hourly Limit").pack(anchor=W)
        self.hourly_var = tk.StringVar(value="20")
        ttk.Entry(right, textvariable=self.hourly_var).pack(fill=X)

        # Warmup
        self.warmup_var = tk.BooleanVar(value=False)
        ttk.Checkbutton(
            main,
            text="Enable Warmup Mode",
            variable=self.warmup_var
        ).pack(anchor=W, pady=(10, 0))

        # Buttons
        btn_frame = ttk.Frame(main)
        btn_frame.pack(fill=X, pady=(20, 0))

        ttk.Button(btn_frame, text="Cancel", bootstyle="secondary", command=self.destroy).pack(side=RIGHT, padx=5)
        ttk.Button(btn_frame, text="Save", bootstyle="primary", command=self._on_save).pack(side=RIGHT)

    def _load_account(self) -> None:
        """Load account data."""
        try:
            accounts = self.api.get_mail_accounts()
            account = next((a for a in accounts if a.account_id == self.account_id), None)
            if account:
                self.email_var.set(account.email_address)
                self.name_var.set(account.display_name)
                self.daily_var.set(str(account.daily_limit))
                self.hourly_var.set(str(account.hourly_limit))
                self.warmup_var.set(account.warmup_enabled)
                self.email_entry.configure(state="disabled")
        except Exception as e:
            logger.error(f"Error loading account: {e}")

    def _on_save(self) -> None:
        """Save account."""
        email = self.email_var.get().strip()
        name = self.name_var.get().strip()

        if not email or not name:
            from tkinter import messagebox
            messagebox.showerror("Error", "Email and display name are required", parent=self)
            return

        try:
            if self.account_id:
                self.api.update_mail_account(
                    self.account_id,
                    displayName=name,
                    dailyLimit=int(self.daily_var.get()),
                    hourlyLimit=int(self.hourly_var.get()),
                    warmupEnabled=self.warmup_var.get()
                )
            else:
                self.api.create_mail_account(
                    email_address=email,
                    display_name=name,
                    daily_limit=int(self.daily_var.get()),
                    hourly_limit=int(self.hourly_var.get())
                )

            self.result = True
            self.destroy()

        except Exception as e:
            from tkinter import messagebox
            messagebox.showerror("Error", str(e), parent=self)
