"""Settings view for application configuration."""
import logging
import tkinter as tk
from typing import Optional
import ttkbootstrap as ttk
from ttkbootstrap.constants import *

from core.api_client import ApiClient
from ui.theme import ThemeManager

logger = logging.getLogger(__name__)


class SettingsView(ttk.Frame):
    """Application settings view."""

    def __init__(self, parent, app=None, api: ApiClient = None, **kwargs):
        super().__init__(parent, **kwargs)

        self.app = app
        self.api = api

        self._create_widgets()

    def _create_widgets(self) -> None:
        """Create view widgets."""
        # Connection settings
        conn_frame = ttk.LabelFrame(self, text="Connection Settings", padding=15)
        conn_frame.pack(fill=X, pady=(0, 15))

        # API URL
        url_row = ttk.Frame(conn_frame)
        url_row.pack(fill=X, pady=5)

        ttk.Label(url_row, text="API URL:", width=15).pack(side=LEFT)
        self.url_var = tk.StringVar(value=self.api.base_url if self.api else "")
        ttk.Entry(url_row, textvariable=self.url_var, width=40).pack(side=LEFT, padx=(0, 10))

        ttk.Button(
            url_row,
            text="Test Connection",
            bootstyle="info-outline",
            command=self._test_connection
        ).pack(side=LEFT)

        # Connection status
        status_row = ttk.Frame(conn_frame)
        status_row.pack(fill=X, pady=5)

        ttk.Label(status_row, text="Status:", width=15).pack(side=LEFT)
        self.conn_status = ttk.Label(
            status_row,
            text="Not tested",
            font=("Segoe UI", 10)
        )
        self.conn_status.pack(side=LEFT)

        # Theme settings
        theme_frame = ttk.LabelFrame(self, text="Appearance", padding=15)
        theme_frame.pack(fill=X, pady=(0, 15))

        theme_row = ttk.Frame(theme_frame)
        theme_row.pack(fill=X, pady=5)

        ttk.Label(theme_row, text="Theme:", width=15).pack(side=LEFT)
        self.theme_var = tk.StringVar(value="cosmo")
        theme_combo = ttk.Combobox(
            theme_row,
            textvariable=self.theme_var,
            values=ThemeManager.AVAILABLE_THEMES,
            state="readonly",
            width=20
        )
        theme_combo.pack(side=LEFT)
        theme_combo.bind("<<ComboboxSelected>>", self._on_theme_change)

        # Theme preview
        preview_frame = ttk.Frame(theme_frame)
        preview_frame.pack(fill=X, pady=(10, 0))

        ttk.Label(preview_frame, text="Preview:", width=15).pack(side=LEFT)

        preview_btns = ttk.Frame(preview_frame)
        preview_btns.pack(side=LEFT)

        for style in ["primary", "success", "warning", "danger", "info"]:
            ttk.Button(
                preview_btns,
                text=style.title(),
                bootstyle=style,
                width=8
            ).pack(side=LEFT, padx=2)

        # Session settings
        session_frame = ttk.LabelFrame(self, text="Session", padding=15)
        session_frame.pack(fill=X, pady=(0, 15))

        if self.api and self.api.auth.user:
            user = self.api.auth.user
            ttk.Label(
                session_frame,
                text=f"Logged in as: {user.username}",
                font=("Segoe UI", 10)
            ).pack(anchor=W)

            ttk.Label(
                session_frame,
                text=f"Role: {user.role.value}",
                font=("Segoe UI", 10)
            ).pack(anchor=W, pady=(5, 0))

            ttk.Label(
                session_frame,
                text=f"Email: {user.email}",
                font=("Segoe UI", 10)
            ).pack(anchor=W, pady=(5, 0))

            # Change password button
            ttk.Button(
                session_frame,
                text="Change Password",
                bootstyle="outline-warning",
                command=self._on_change_password
            ).pack(anchor=W, pady=(15, 0))

        # About section
        about_frame = ttk.LabelFrame(self, text="About", padding=15)
        about_frame.pack(fill=X)

        ttk.Label(
            about_frame,
            text="Lead Generator",
            font=("Segoe UI", 12, "bold")
        ).pack(anchor=W)

        ttk.Label(
            about_frame,
            text="Digital Marketing Campaign Tool",
            font=("Segoe UI", 10)
        ).pack(anchor=W)

        ttk.Label(
            about_frame,
            text="Python Tkinter Client v1.0.0",
            font=("Segoe UI", 9),
            bootstyle="secondary"
        ).pack(anchor=W, pady=(10, 0))

        ttk.Label(
            about_frame,
            text="Connects to .NET 8 REST API Backend",
            font=("Segoe UI", 9),
            bootstyle="secondary"
        ).pack(anchor=W)

    def _test_connection(self) -> None:
        """Test API connection."""
        self.conn_status.configure(text="Testing...", bootstyle="warning")
        self.update_idletasks()

        try:
            if self.api.health_check():
                version_info = self.api.get_version()
                version = version_info.get('version', 'Unknown') if version_info else 'Unknown'
                self.conn_status.configure(
                    text=f"\u2713 Connected (API v{version})",
                    bootstyle="success"
                )
                if self.app:
                    self.app.set_connection_status(True)
            else:
                self.conn_status.configure(
                    text="\u2717 Connection failed",
                    bootstyle="danger"
                )
                if self.app:
                    self.app.set_connection_status(False)
        except Exception as e:
            self.conn_status.configure(
                text=f"\u2717 Error: {str(e)[:30]}...",
                bootstyle="danger"
            )
            if self.app:
                self.app.set_connection_status(False)

    def _on_theme_change(self, event) -> None:
        """Handle theme change."""
        theme = self.theme_var.get()
        if self.app and hasattr(self.app, 'theme_manager'):
            self.app.theme_manager.change_theme(theme)
            if self.app:
                self.app.set_status(f"Theme changed to {theme}")

    def _on_change_password(self) -> None:
        """Open change password dialog."""
        dialog = ChangePasswordDialog(self, self.api)
        self.wait_window(dialog)

    def refresh(self) -> None:
        """Refresh settings view."""
        pass


class ChangePasswordDialog(ttk.Toplevel):
    """Dialog for changing password."""

    def __init__(self, parent, api: ApiClient):
        super().__init__(parent)

        self.api = api

        self.title("Change Password")
        self.geometry("400x250")
        self.resizable(False, False)

        self._create_widgets()
        self.transient(parent)
        self.grab_set()

    def _create_widgets(self) -> None:
        """Create dialog widgets."""
        main = ttk.Frame(self, padding=20)
        main.pack(fill=BOTH, expand=True)

        # Current password
        ttk.Label(main, text="Current Password *").pack(anchor=W, pady=(0, 5))
        self.current_var = tk.StringVar()
        ttk.Entry(main, textvariable=self.current_var, show="\u2022", width=40).pack(fill=X, pady=(0, 10))

        # New password
        ttk.Label(main, text="New Password *").pack(anchor=W, pady=(0, 5))
        self.new_var = tk.StringVar()
        ttk.Entry(main, textvariable=self.new_var, show="\u2022", width=40).pack(fill=X, pady=(0, 10))

        # Confirm password
        ttk.Label(main, text="Confirm New Password *").pack(anchor=W, pady=(0, 5))
        self.confirm_var = tk.StringVar()
        ttk.Entry(main, textvariable=self.confirm_var, show="\u2022", width=40).pack(fill=X, pady=(0, 10))

        # Buttons
        btn_frame = ttk.Frame(main)
        btn_frame.pack(fill=X, pady=(15, 0))

        ttk.Button(btn_frame, text="Cancel", bootstyle="secondary", command=self.destroy).pack(side=RIGHT, padx=5)
        ttk.Button(btn_frame, text="Change", bootstyle="primary", command=self._on_change).pack(side=RIGHT)

    def _on_change(self) -> None:
        """Change password."""
        current = self.current_var.get()
        new = self.new_var.get()
        confirm = self.confirm_var.get()

        if not all([current, new, confirm]):
            from tkinter import messagebox
            messagebox.showerror("Error", "All fields are required", parent=self)
            return

        if new != confirm:
            from tkinter import messagebox
            messagebox.showerror("Error", "New passwords do not match", parent=self)
            return

        try:
            self.api.change_password(current, new)
            from tkinter import messagebox
            messagebox.showinfo("Success", "Password changed successfully", parent=self)
            self.destroy()
        except Exception as e:
            from tkinter import messagebox
            messagebox.showerror("Error", str(e), parent=self)
