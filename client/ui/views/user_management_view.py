"""User management view (Admin only)."""
import logging
import tkinter as tk
from typing import Optional
import ttkbootstrap as ttk
from ttkbootstrap.constants import *

from core.api_client import ApiClient
from core.models import UserRole
from ui.widgets.data_table import DataTable

logger = logging.getLogger(__name__)


class UserManagementView(ttk.Frame):
    """User management view for administrators."""

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
            text="User Management",
            font=("Segoe UI", 14, "bold")
        ).pack(side=LEFT)

        ttk.Button(
            header,
            text="+ Add User",
            bootstyle="success",
            command=self._on_add
        ).pack(side=RIGHT)

        # Users table
        columns = [
            {"id": "id", "text": "ID", "width": 0},
            {"id": "username", "text": "Username", "width": 150, "anchor": "w"},
            {"id": "email", "text": "Email", "width": 200, "anchor": "w"},
            {"id": "full_name", "text": "Full Name", "width": 150, "anchor": "w"},
            {"id": "role", "text": "Role", "width": 100, "anchor": "center"},
            {"id": "status", "text": "Status", "width": 80, "anchor": "center"},
            {"id": "last_login", "text": "Last Login", "width": 120, "anchor": "center"},
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
            text="Edit User",
            bootstyle="primary-outline",
            command=self._on_edit_click,
            state="disabled"
        )
        self.edit_btn.pack(side=LEFT, padx=5)

        self.reset_pwd_btn = ttk.Button(
            bottom,
            text="Reset Password",
            bootstyle="warning-outline",
            command=self._on_reset_password,
            state="disabled"
        )
        self.reset_pwd_btn.pack(side=LEFT, padx=5)

        self.toggle_btn = ttk.Button(
            bottom,
            text="Deactivate",
            bootstyle="danger-outline",
            command=self._on_toggle_status,
            state="disabled"
        )
        self.toggle_btn.pack(side=LEFT, padx=5)

    def refresh(self) -> None:
        """Refresh users list."""
        if not self.api:
            return

        try:
            users = self.api.get_users()
            data = []
            for u in users:
                last_login = u.last_login.strftime("%Y-%m-%d %H:%M") if u.last_login else "-"
                data.append({
                    "id": u.user_id,
                    "username": u.username,
                    "email": u.email,
                    "full_name": u.full_name or "",
                    "role": u.role.value,
                    "status": "Active" if u.is_active else "Inactive",
                    "last_login": last_login
                })
            self.table.set_data(data)

            if self.app:
                self.app.set_status(f"Loaded {len(users)} users")

        except Exception as e:
            logger.error(f"Error loading users: {e}")
            if self.app:
                self.app.set_status(f"Error: {str(e)}")

    def _on_select(self, user_id: str) -> None:
        """Handle user selection."""
        self.edit_btn.configure(state="normal")
        self.reset_pwd_btn.configure(state="normal")
        self.toggle_btn.configure(state="normal")

        selected = self.table.get_selected()
        if selected:
            status = selected.get("status", "")
            if status == "Active":
                self.toggle_btn.configure(text="Deactivate")
            else:
                self.toggle_btn.configure(text="Activate")

    def _on_add(self) -> None:
        """Add new user."""
        dialog = UserFormDialog(self, self.api)
        self.wait_window(dialog)
        if dialog.result:
            self.refresh()

    def _on_edit_click(self) -> None:
        """Edit selected user."""
        user_id = self.table.get_selected_id()
        if user_id:
            self._on_edit(user_id)

    def _on_edit(self, user_id: str) -> None:
        """Edit user."""
        dialog = UserFormDialog(self, self.api, user_id=user_id)
        self.wait_window(dialog)
        if dialog.result:
            self.refresh()

    def _on_reset_password(self) -> None:
        """Reset user password."""
        user_id = self.table.get_selected_id()
        selected = self.table.get_selected()
        if not user_id or not selected:
            return

        dialog = ResetPasswordDialog(self, self.api, user_id, selected.get("username", ""))
        self.wait_window(dialog)

    def _on_toggle_status(self) -> None:
        """Toggle user active status."""
        user_id = self.table.get_selected_id()
        selected = self.table.get_selected()
        if not user_id or not selected:
            return

        current_status = selected.get("status", "") == "Active"
        action = "deactivate" if current_status else "activate"

        if self.app and self.app.ask_confirmation(
            f"{action.title()} User",
            f"Are you sure you want to {action} {selected.get('username')}?"
        ):
            try:
                self.api.update_user(user_id, isActive=not current_status)
                self.refresh()
            except Exception as e:
                if self.app:
                    self.app.show_error("Error", str(e))


class UserFormDialog(ttk.Toplevel):
    """Dialog for creating/editing users."""

    def __init__(self, parent, api: ApiClient, user_id: str = None):
        super().__init__(parent)

        self.api = api
        self.user_id = user_id
        self.result = None

        self.title("New User" if not user_id else "Edit User")
        self.geometry("450x400")
        self.resizable(False, False)

        self._create_widgets()

        if user_id:
            self._load_user()

        self.transient(parent)
        self.grab_set()

    def _create_widgets(self) -> None:
        """Create form widgets."""
        main = ttk.Frame(self, padding=20)
        main.pack(fill=BOTH, expand=True)

        # Username
        ttk.Label(main, text="Username *").pack(anchor=W, pady=(0, 5))
        self.username_var = tk.StringVar()
        self.username_entry = ttk.Entry(main, textvariable=self.username_var, width=40)
        self.username_entry.pack(fill=X, pady=(0, 10))

        # Email
        ttk.Label(main, text="Email *").pack(anchor=W, pady=(0, 5))
        self.email_var = tk.StringVar()
        ttk.Entry(main, textvariable=self.email_var, width=40).pack(fill=X, pady=(0, 10))

        # Full Name
        ttk.Label(main, text="Full Name").pack(anchor=W, pady=(0, 5))
        self.name_var = tk.StringVar()
        ttk.Entry(main, textvariable=self.name_var, width=40).pack(fill=X, pady=(0, 10))

        # Role
        ttk.Label(main, text="Role *").pack(anchor=W, pady=(0, 5))
        self.role_var = tk.StringVar(value="User")
        role_combo = ttk.Combobox(
            main,
            textvariable=self.role_var,
            values=["Admin", "Manager", "User"],
            state="readonly",
            width=37
        )
        role_combo.pack(fill=X, pady=(0, 10))

        # Password (only for new users)
        if not self.user_id:
            ttk.Label(main, text="Password *").pack(anchor=W, pady=(0, 5))
            self.password_var = tk.StringVar()
            ttk.Entry(main, textvariable=self.password_var, show="\u2022", width=40).pack(fill=X, pady=(0, 10))

            ttk.Label(
                main,
                text="Min 8 characters, uppercase, and numbers required",
                font=("Segoe UI", 8),
                bootstyle="secondary"
            ).pack(anchor=W)

        # Buttons
        btn_frame = ttk.Frame(main)
        btn_frame.pack(fill=X, pady=(20, 0))

        ttk.Button(btn_frame, text="Cancel", bootstyle="secondary", command=self.destroy).pack(side=RIGHT, padx=5)
        ttk.Button(btn_frame, text="Save", bootstyle="primary", command=self._on_save).pack(side=RIGHT)

    def _load_user(self) -> None:
        """Load user data."""
        try:
            users = self.api.get_users()
            user = next((u for u in users if u.user_id == self.user_id), None)
            if user:
                self.username_var.set(user.username)
                self.email_var.set(user.email)
                self.name_var.set(user.full_name or "")
                self.role_var.set(user.role.value)
                self.username_entry.configure(state="disabled")
        except Exception as e:
            logger.error(f"Error loading user: {e}")

    def _on_save(self) -> None:
        """Save user."""
        username = self.username_var.get().strip()
        email = self.email_var.get().strip()
        role = self.role_var.get()

        if not username or not email:
            from tkinter import messagebox
            messagebox.showerror("Error", "Username and email are required", parent=self)
            return

        try:
            if self.user_id:
                self.api.update_user(
                    self.user_id,
                    email=email,
                    role=role,
                    fullName=self.name_var.get().strip() or None
                )
            else:
                password = self.password_var.get()
                if not password:
                    from tkinter import messagebox
                    messagebox.showerror("Error", "Password is required", parent=self)
                    return

                self.api.create_user(
                    username=username,
                    email=email,
                    password=password,
                    role=role,
                    full_name=self.name_var.get().strip() or None
                )

            self.result = True
            self.destroy()

        except Exception as e:
            from tkinter import messagebox
            messagebox.showerror("Error", str(e), parent=self)


class ResetPasswordDialog(ttk.Toplevel):
    """Dialog for resetting user password."""

    def __init__(self, parent, api: ApiClient, user_id: str, username: str):
        super().__init__(parent)

        self.api = api
        self.user_id = user_id

        self.title(f"Reset Password - {username}")
        self.geometry("400x200")
        self.resizable(False, False)

        self._create_widgets()
        self.transient(parent)
        self.grab_set()

    def _create_widgets(self) -> None:
        """Create dialog widgets."""
        main = ttk.Frame(self, padding=20)
        main.pack(fill=BOTH, expand=True)

        ttk.Label(main, text="New Password *").pack(anchor=W, pady=(0, 5))
        self.password_var = tk.StringVar()
        ttk.Entry(main, textvariable=self.password_var, show="\u2022", width=40).pack(fill=X, pady=(0, 10))

        ttk.Label(main, text="Confirm Password *").pack(anchor=W, pady=(0, 5))
        self.confirm_var = tk.StringVar()
        ttk.Entry(main, textvariable=self.confirm_var, show="\u2022", width=40).pack(fill=X, pady=(0, 10))

        btn_frame = ttk.Frame(main)
        btn_frame.pack(fill=X, pady=(15, 0))

        ttk.Button(btn_frame, text="Cancel", bootstyle="secondary", command=self.destroy).pack(side=RIGHT, padx=5)
        ttk.Button(btn_frame, text="Reset", bootstyle="warning", command=self._on_reset).pack(side=RIGHT)

    def _on_reset(self) -> None:
        """Reset the password."""
        password = self.password_var.get()
        confirm = self.confirm_var.get()

        if not password:
            from tkinter import messagebox
            messagebox.showerror("Error", "Password is required", parent=self)
            return

        if password != confirm:
            from tkinter import messagebox
            messagebox.showerror("Error", "Passwords do not match", parent=self)
            return

        try:
            self.api.update_user(self.user_id, password=password)
            from tkinter import messagebox
            messagebox.showinfo("Success", "Password has been reset", parent=self)
            self.destroy()
        except Exception as e:
            from tkinter import messagebox
            messagebox.showerror("Error", str(e), parent=self)
