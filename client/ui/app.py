"""Main application window with sidebar navigation."""
import logging
import tkinter as tk
from typing import Optional, Callable, Dict, Type
import ttkbootstrap as ttk
from ttkbootstrap.constants import *

from core.api_client import ApiClient
from core.models import UserRole
from .theme import ThemeManager

logger = logging.getLogger(__name__)


class App(ttk.Window):
    """Main application window."""

    def __init__(
        self,
        api_client: ApiClient,
        theme: str = "cosmo",
        title: str = "Lead Generator",
        width: int = 1400,
        height: int = 900,
        min_width: int = 1200,
        min_height: int = 700
    ):
        super().__init__(title=title, themename=theme)

        self.api = api_client
        self.theme_manager = ThemeManager(theme)

        # Window configuration
        self.geometry(f"{width}x{height}")
        self.minsize(min_width, min_height)

        # Center window on screen
        self.update_idletasks()
        x = (self.winfo_screenwidth() - width) // 2
        y = (self.winfo_screenheight() - height) // 2
        self.geometry(f"+{x}+{y}")

        # State
        self._current_view: Optional[ttk.Frame] = None
        self._views: Dict[str, Type] = {}
        self._view_instances: Dict[str, ttk.Frame] = {}
        self._sidebar_buttons: Dict[str, ttk.Button] = {}
        self._on_logout_callback: Optional[Callable] = None

        # Build UI
        self._create_layout()
        self._create_sidebar()
        self._create_content_area()
        self._create_status_bar()

        # Register default views
        self._register_default_views()

        # Protocol handlers
        self.protocol("WM_DELETE_WINDOW", self._on_close)

    def _create_layout(self) -> None:
        """Create main layout containers."""
        # Main container
        self.main_container = ttk.Frame(self)
        self.main_container.pack(fill=BOTH, expand=True)

        # Sidebar (left)
        self.sidebar = ttk.Frame(self.main_container, width=250, bootstyle="dark")
        self.sidebar.pack(side=LEFT, fill=Y)
        self.sidebar.pack_propagate(False)

        # Content area (right)
        self.content_container = ttk.Frame(self.main_container)
        self.content_container.pack(side=LEFT, fill=BOTH, expand=True)

    def _create_sidebar(self) -> None:
        """Create sidebar with navigation."""
        # Logo/Title area
        title_frame = ttk.Frame(self.sidebar, bootstyle="dark")
        title_frame.pack(fill=X, pady=(20, 30))

        title_label = ttk.Label(
            title_frame,
            text="Lead Generator",
            font=("Segoe UI", 14, "bold"),
            bootstyle="inverse-dark"
        )
        title_label.pack(padx=20)

        # User info area
        self.user_frame = ttk.Frame(self.sidebar, bootstyle="dark")
        self.user_frame.pack(fill=X, padx=15, pady=(0, 20))

        self.user_label = ttk.Label(
            self.user_frame,
            text="Not logged in",
            font=("Segoe UI", 9),
            bootstyle="inverse-dark"
        )
        self.user_label.pack(anchor=W)

        self.role_label = ttk.Label(
            self.user_frame,
            text="",
            font=("Segoe UI", 8),
            bootstyle="inverse-dark"
        )
        self.role_label.pack(anchor=W)

        ttk.Separator(self.sidebar, bootstyle="dark").pack(fill=X, padx=15, pady=10)

        # Navigation buttons container
        self.nav_container = ttk.Frame(self.sidebar, bootstyle="dark")
        self.nav_container.pack(fill=BOTH, expand=True, padx=10)

        # Bottom buttons
        self.bottom_nav = ttk.Frame(self.sidebar, bootstyle="dark")
        self.bottom_nav.pack(fill=X, side=BOTTOM, padx=10, pady=20)

        # Settings button
        self._add_nav_button(
            "settings",
            "Settings",
            "settings_view",
            parent=self.bottom_nav,
            icon="\u2699"
        )

        # Logout button
        logout_btn = ttk.Button(
            self.bottom_nav,
            text="\u2190 Logout",
            bootstyle="outline-danger",
            command=self._on_logout
        )
        logout_btn.pack(fill=X, pady=5)

    def _add_nav_button(
        self,
        key: str,
        text: str,
        view_name: str,
        parent: ttk.Frame = None,
        icon: str = "",
        admin_only: bool = False,
        manager_only: bool = False
    ) -> ttk.Button:
        """Add a navigation button to sidebar."""
        container = parent or self.nav_container

        display_text = f"{icon} {text}" if icon else text

        btn = ttk.Button(
            container,
            text=display_text,
            bootstyle="dark",
            command=lambda: self.show_view(view_name)
        )
        btn.pack(fill=X, pady=2)

        self._sidebar_buttons[key] = {
            "button": btn,
            "view": view_name,
            "admin_only": admin_only,
            "manager_only": manager_only
        }

        return btn

    def _create_content_area(self) -> None:
        """Create main content area."""
        # Header
        self.header = ttk.Frame(self.content_container)
        self.header.pack(fill=X, padx=20, pady=15)

        self.header_title = ttk.Label(
            self.header,
            text="Dashboard",
            font=("Segoe UI", 20, "bold")
        )
        self.header_title.pack(side=LEFT)

        # Refresh button
        self.refresh_btn = ttk.Button(
            self.header,
            text="\u21BB Refresh",
            bootstyle="outline-primary",
            command=self._on_refresh
        )
        self.refresh_btn.pack(side=RIGHT)

        ttk.Separator(self.content_container).pack(fill=X, padx=20)

        # Content frame
        self.content_frame = ttk.Frame(self.content_container)
        self.content_frame.pack(fill=BOTH, expand=True, padx=20, pady=15)

    def _create_status_bar(self) -> None:
        """Create status bar at bottom."""
        self.status_bar = ttk.Frame(self.content_container, bootstyle="secondary")
        self.status_bar.pack(fill=X, side=BOTTOM)

        self.status_label = ttk.Label(
            self.status_bar,
            text="Ready",
            font=("Segoe UI", 9),
            bootstyle="inverse-secondary",
            padding=(10, 3)
        )
        self.status_label.pack(side=LEFT)

        self.connection_label = ttk.Label(
            self.status_bar,
            text="\u25CF Connected",
            font=("Segoe UI", 9),
            bootstyle="inverse-secondary",
            foreground="green",
            padding=(10, 3)
        )
        self.connection_label.pack(side=RIGHT)

    def _register_default_views(self) -> None:
        """Register default navigation items."""
        # Main navigation
        self._add_nav_button("dashboard", "Dashboard", "dashboard_view", icon="\u2302")
        self._add_nav_button("campaigns", "Campaigns", "campaign_list_view", icon="\u2709")
        self._add_nav_button("contacts", "Contacts", "contact_list_view", icon="\u263A")
        self._add_nav_button("templates", "Templates", "template_editor_view", icon="\u2630")
        self._add_nav_button("reports", "Reports", "reports_view", icon="\u2637")

        ttk.Separator(self.nav_container, bootstyle="dark").pack(fill=X, pady=10)

        # Admin navigation
        self._add_nav_button(
            "users", "Users", "user_management_view",
            icon="\u263B", admin_only=True
        )
        self._add_nav_button(
            "mail_accounts", "Mail Accounts", "mail_accounts_view",
            icon="\u2709", admin_only=True
        )
        self._add_nav_button(
            "suppression", "Suppression List", "suppression_view",
            icon="\u2717", manager_only=True
        )

    def register_view(self, name: str, view_class: Type) -> None:
        """Register a view class."""
        self._views[name] = view_class

    def show_view(self, view_name: str, **kwargs) -> None:
        """Show a registered view."""
        if view_name not in self._views:
            logger.warning(f"View '{view_name}' not registered")
            self.set_status(f"View not available: {view_name}")
            return

        # Hide current view
        if self._current_view:
            self._current_view.pack_forget()

        # Get or create view instance
        if view_name not in self._view_instances:
            view_class = self._views[view_name]
            self._view_instances[view_name] = view_class(
                self.content_frame,
                app=self,
                api=self.api,
                **kwargs
            )

        view = self._view_instances[view_name]
        view.pack(fill=BOTH, expand=True)
        self._current_view = view

        # Update header
        title = view_name.replace("_view", "").replace("_", " ").title()
        self.header_title.configure(text=title)

        # Update button states
        self._update_nav_button_states(view_name)

        # Refresh view if it has a refresh method
        if hasattr(view, 'refresh'):
            view.refresh()

    def _update_nav_button_states(self, active_view: str) -> None:
        """Update navigation button styles."""
        for key, info in self._sidebar_buttons.items():
            btn = info["button"]
            if info["view"] == active_view:
                btn.configure(bootstyle="primary")
            else:
                btn.configure(bootstyle="dark")

    def update_user_info(self, username: str, role: UserRole) -> None:
        """Update sidebar user info."""
        self.user_label.configure(text=username)
        self.role_label.configure(text=role.value)

        # Update button visibility based on role
        for key, info in self._sidebar_buttons.items():
            btn = info["button"]
            if info["admin_only"] and role != UserRole.ADMIN:
                btn.pack_forget()
            elif info["manager_only"] and role not in (UserRole.ADMIN, UserRole.MANAGER):
                btn.pack_forget()
            else:
                btn.pack(fill=X, pady=2)

    def set_status(self, message: str) -> None:
        """Update status bar message."""
        self.status_label.configure(text=message)

    def set_connection_status(self, connected: bool) -> None:
        """Update connection status indicator."""
        if connected:
            self.connection_label.configure(
                text="\u25CF Connected",
                foreground="green"
            )
        else:
            self.connection_label.configure(
                text="\u25CB Disconnected",
                foreground="red"
            )

    def set_logout_callback(self, callback: Callable) -> None:
        """Set callback for logout action."""
        self._on_logout_callback = callback

    def _on_logout(self) -> None:
        """Handle logout button click."""
        if self._on_logout_callback:
            self._on_logout_callback()

    def _on_refresh(self) -> None:
        """Handle refresh button click."""
        if self._current_view and hasattr(self._current_view, 'refresh'):
            self.set_status("Refreshing...")
            self._current_view.refresh()
            self.set_status("Ready")

    def _on_close(self) -> None:
        """Handle window close."""
        logger.info("Application closing")
        self.destroy()

    def show_loading(self, message: str = "Loading...") -> None:
        """Show loading indicator."""
        self.set_status(message)
        self.update_idletasks()

    def hide_loading(self) -> None:
        """Hide loading indicator."""
        self.set_status("Ready")

    def show_error(self, title: str, message: str) -> None:
        """Show error dialog."""
        from tkinter import messagebox
        messagebox.showerror(title, message, parent=self)

    def show_info(self, title: str, message: str) -> None:
        """Show info dialog."""
        from tkinter import messagebox
        messagebox.showinfo(title, message, parent=self)

    def ask_confirmation(self, title: str, message: str) -> bool:
        """Show confirmation dialog."""
        from tkinter import messagebox
        return messagebox.askyesno(title, message, parent=self)

    def clear_view_cache(self) -> None:
        """Clear cached view instances."""
        for view in self._view_instances.values():
            view.destroy()
        self._view_instances.clear()
        self._current_view = None
