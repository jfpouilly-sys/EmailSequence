"""Login view for authentication."""
import logging
import tkinter as tk
from typing import Callable, Optional
import ttkbootstrap as ttk
from ttkbootstrap.constants import *

from core.api_client import ApiClient
from core.exceptions import AuthenticationError, ConnectionError

logger = logging.getLogger(__name__)


class LoginView(ttk.Frame):
    """Login form view."""

    def __init__(
        self,
        parent,
        api: ApiClient,
        on_login_success: Optional[Callable] = None,
        **kwargs
    ):
        super().__init__(parent, **kwargs)

        self.api = api
        self.on_login_success = on_login_success

        self._create_widgets()
        self._center_content()

    def _create_widgets(self) -> None:
        """Create login form widgets."""
        # Center container
        self.center_frame = ttk.Frame(self)
        self.center_frame.place(relx=0.5, rely=0.5, anchor="center")

        # Logo/Title
        title_frame = ttk.Frame(self.center_frame)
        title_frame.pack(pady=(0, 30))

        ttk.Label(
            title_frame,
            text="Lead Generator",
            font=("Segoe UI", 28, "bold"),
            bootstyle="primary"
        ).pack()

        ttk.Label(
            title_frame,
            text="Digital Marketing Campaign Tool",
            font=("Segoe UI", 11),
            bootstyle="secondary"
        ).pack(pady=(5, 0))

        # Login card
        card = ttk.Frame(self.center_frame, padding=40)
        card.pack()

        # Card header
        ttk.Label(
            card,
            text="Sign In",
            font=("Segoe UI", 16, "bold")
        ).pack(anchor=W, pady=(0, 20))

        # Username field
        username_frame = ttk.Frame(card)
        username_frame.pack(fill=X, pady=(0, 15))

        ttk.Label(
            username_frame,
            text="Username",
            font=("Segoe UI", 10)
        ).pack(anchor=W, pady=(0, 5))

        self.username_var = tk.StringVar()
        self.username_entry = ttk.Entry(
            username_frame,
            textvariable=self.username_var,
            font=("Segoe UI", 11),
            width=35
        )
        self.username_entry.pack(fill=X)
        self.username_entry.focus_set()

        # Password field
        password_frame = ttk.Frame(card)
        password_frame.pack(fill=X, pady=(0, 20))

        ttk.Label(
            password_frame,
            text="Password",
            font=("Segoe UI", 10)
        ).pack(anchor=W, pady=(0, 5))

        self.password_var = tk.StringVar()
        self.password_entry = ttk.Entry(
            password_frame,
            textvariable=self.password_var,
            font=("Segoe UI", 11),
            width=35,
            show="\u2022"
        )
        self.password_entry.pack(fill=X)

        # Error message
        self.error_var = tk.StringVar()
        self.error_label = ttk.Label(
            card,
            textvariable=self.error_var,
            font=("Segoe UI", 9),
            bootstyle="danger",
            wraplength=300
        )
        self.error_label.pack(fill=X, pady=(0, 15))

        # Login button
        self.login_btn = ttk.Button(
            card,
            text="Sign In",
            bootstyle="primary",
            command=self._on_login,
            width=20
        )
        self.login_btn.pack(pady=(0, 15))

        # Loading indicator
        self.loading_frame = ttk.Frame(card)

        self.loading_label = ttk.Label(
            self.loading_frame,
            text="Signing in...",
            font=("Segoe UI", 9)
        )
        self.loading_label.pack(side=LEFT, padx=(0, 10))

        self.progress = ttk.Progressbar(
            self.loading_frame,
            mode="indeterminate",
            length=100
        )
        self.progress.pack(side=LEFT)

        # Connection status
        self.status_frame = ttk.Frame(card)
        self.status_frame.pack(pady=(20, 0))

        self.connection_label = ttk.Label(
            self.status_frame,
            text="",
            font=("Segoe UI", 9),
            bootstyle="secondary"
        )
        self.connection_label.pack()

        # Bindings
        self.username_entry.bind("<Return>", lambda e: self.password_entry.focus_set())
        self.password_entry.bind("<Return>", lambda e: self._on_login())

        # Check connection on load
        self.after(500, self._check_connection)

    def _center_content(self) -> None:
        """Center content on resize."""
        self.bind("<Configure>", self._on_resize)

    def _on_resize(self, event) -> None:
        """Handle window resize."""
        pass  # Content is already centered with place()

    def _check_connection(self) -> None:
        """Check API connection status."""
        self.connection_label.configure(text="Checking connection...")

        def check():
            try:
                if self.api.health_check():
                    self.connection_label.configure(
                        text="\u25CF Connected to server",
                        bootstyle="success"
                    )
                else:
                    self.connection_label.configure(
                        text="\u25CB Cannot connect to server",
                        bootstyle="danger"
                    )
            except Exception:
                self.connection_label.configure(
                    text="\u25CB Cannot connect to server",
                    bootstyle="danger"
                )

        self.after(100, check)

    def _on_login(self) -> None:
        """Handle login button click."""
        username = self.username_var.get().strip()
        password = self.password_var.get()

        # Validate input
        if not username:
            self._show_error("Please enter your username")
            self.username_entry.focus_set()
            return

        if not password:
            self._show_error("Please enter your password")
            self.password_entry.focus_set()
            return

        # Show loading state
        self._set_loading(True)
        self._clear_error()

        # Perform login in after to allow UI update
        self.after(100, lambda: self._do_login(username, password))

    def _do_login(self, username: str, password: str) -> None:
        """Perform login request."""
        try:
            response = self.api.login(username, password)
            logger.info(f"Login successful for user: {username}")

            self._set_loading(False)

            if self.on_login_success:
                self.on_login_success(response)

        except AuthenticationError as e:
            logger.warning(f"Login failed for user {username}: {e}")
            self._set_loading(False)
            self._show_error("Invalid username or password")
            self.password_var.set("")
            self.password_entry.focus_set()

        except ConnectionError as e:
            logger.error(f"Connection error during login: {e}")
            self._set_loading(False)
            self._show_error("Cannot connect to server. Please check your network connection.")

        except Exception as e:
            logger.error(f"Unexpected error during login: {e}")
            self._set_loading(False)
            self._show_error(f"An error occurred: {str(e)}")

    def _set_loading(self, loading: bool) -> None:
        """Set loading state."""
        if loading:
            self.login_btn.configure(state="disabled")
            self.username_entry.configure(state="disabled")
            self.password_entry.configure(state="disabled")
            self.loading_frame.pack(pady=(0, 15))
            self.progress.start(10)
        else:
            self.login_btn.configure(state="normal")
            self.username_entry.configure(state="normal")
            self.password_entry.configure(state="normal")
            self.loading_frame.pack_forget()
            self.progress.stop()

    def _show_error(self, message: str) -> None:
        """Show error message."""
        self.error_var.set(message)

    def _clear_error(self) -> None:
        """Clear error message."""
        self.error_var.set("")

    def reset(self) -> None:
        """Reset the login form."""
        self.username_var.set("")
        self.password_var.set("")
        self._clear_error()
        self._set_loading(False)
        self.username_entry.focus_set()
