"""Main application window for Lead Generator Standalone."""

import logging
import tkinter as tk
from tkinter import ttk, messagebox
from typing import Dict, Any, Optional

try:
    import ttkbootstrap as ttkb
    from ttkbootstrap.constants import *
    TTKBOOTSTRAP_AVAILABLE = True
except ImportError:
    TTKBOOTSTRAP_AVAILABLE = False

from ui.theme import THEME_NAME, WINDOW_SIZES, COLORS, FONTS
from core.worker import get_worker, EmailWorker
from outlook.outlook_service import OutlookService

logger = logging.getLogger(__name__)


class MainApplication:
    """Main application window."""

    def __init__(self, config: Dict[str, Any]):
        """
        Initialize the main application.

        Args:
            config: Application configuration dictionary
        """
        self.config = config
        self.worker: Optional[EmailWorker] = None
        self._current_view = None

        self._create_window()
        self._create_styles()
        self._create_menu()
        self._create_layout()
        self._setup_worker()

        # Show dashboard by default
        self._show_view('dashboard')

    def _create_window(self) -> None:
        """Create the main window."""
        if TTKBOOTSTRAP_AVAILABLE:
            self.root = ttkb.Window(themename=THEME_NAME)
        else:
            self.root = tk.Tk()

        self.root.title("Lead Generator Standalone")
        width, height = WINDOW_SIZES['main']
        self.root.geometry(f"{width}x{height}")
        self.root.minsize(800, 600)

        # Center window
        self.root.update_idletasks()
        x = (self.root.winfo_screenwidth() - width) // 2
        y = (self.root.winfo_screenheight() - height) // 2
        self.root.geometry(f"+{x}+{y}")

        # Handle close
        self.root.protocol("WM_DELETE_WINDOW", self._on_close)

    def _create_styles(self) -> None:
        """Create custom styles."""
        style = ttk.Style()

        # Navigation button style
        style.configure('Nav.TButton', font=FONTS['body'], padding=(20, 10))

        # Card frame style
        style.configure('Card.TFrame', background='white')

    def _create_menu(self) -> None:
        """Create the menu bar."""
        self.menubar = tk.Menu(self.root)
        self.root.config(menu=self.menubar)

        # File menu
        file_menu = tk.Menu(self.menubar, tearoff=0)
        file_menu.add_command(label="New Campaign", command=lambda: self._show_view('campaigns'))
        file_menu.add_command(label="Import Contacts", command=lambda: self._show_view('contacts'))
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self._on_close)
        self.menubar.add_cascade(label="File", menu=file_menu)

        # View menu
        view_menu = tk.Menu(self.menubar, tearoff=0)
        view_menu.add_command(label="Dashboard", command=lambda: self._show_view('dashboard'))
        view_menu.add_command(label="Campaigns", command=lambda: self._show_view('campaigns'))
        view_menu.add_command(label="Contacts", command=lambda: self._show_view('contacts'))
        view_menu.add_command(label="Templates", command=lambda: self._show_view('templates'))
        view_menu.add_command(label="Suppression List", command=lambda: self._show_view('suppression'))
        view_menu.add_command(label="Reports", command=lambda: self._show_view('reports'))
        self.menubar.add_cascade(label="View", menu=view_menu)

        # Tools menu
        tools_menu = tk.Menu(self.menubar, tearoff=0)
        tools_menu.add_command(label="Settings", command=lambda: self._show_view('settings'))
        tools_menu.add_command(label="Migration Export", command=self._show_migration_dialog)
        self.menubar.add_cascade(label="Tools", menu=tools_menu)

        # Help menu
        help_menu = tk.Menu(self.menubar, tearoff=0)
        help_menu.add_command(label="About", command=self._show_about)
        self.menubar.add_cascade(label="Help", menu=help_menu)

    def _create_layout(self) -> None:
        """Create the main layout."""
        # Main container
        self.main_container = ttk.Frame(self.root)
        self.main_container.pack(fill=tk.BOTH, expand=True)

        # Sidebar navigation
        self.sidebar = ttk.Frame(self.main_container, width=200)
        self.sidebar.pack(side=tk.LEFT, fill=tk.Y, padx=0, pady=0)
        self.sidebar.pack_propagate(False)

        self._create_sidebar()

        # Content area
        self.content_frame = ttk.Frame(self.main_container)
        self.content_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Status bar
        self._create_status_bar()

    def _create_sidebar(self) -> None:
        """Create the sidebar navigation."""
        # App title
        title_frame = ttk.Frame(self.sidebar)
        title_frame.pack(fill=tk.X, padx=10, pady=20)

        title_label = ttk.Label(
            title_frame,
            text="Lead Generator",
            font=('Segoe UI', 14, 'bold')
        )
        title_label.pack()

        subtitle_label = ttk.Label(
            title_frame,
            text="Standalone Edition",
            font=('Segoe UI', 9),
            foreground=COLORS['secondary']
        )
        subtitle_label.pack()

        ttk.Separator(self.sidebar, orient=tk.HORIZONTAL).pack(fill=tk.X, padx=10, pady=10)

        # Navigation buttons
        nav_items = [
            ('dashboard', 'Dashboard'),
            ('campaigns', 'Campaigns'),
            ('contacts', 'Contacts'),
            ('templates', 'Templates'),
            ('suppression', 'Suppression List'),
            ('reports', 'Reports'),
            ('settings', 'Settings'),
        ]

        self.nav_buttons = {}
        for view_name, label in nav_items:
            btn = ttk.Button(
                self.sidebar,
                text=label,
                style='Nav.TButton',
                command=lambda v=view_name: self._show_view(v)
            )
            btn.pack(fill=tk.X, padx=10, pady=2)
            self.nav_buttons[view_name] = btn

    def _create_status_bar(self) -> None:
        """Create the status bar."""
        self.status_bar = ttk.Frame(self.root)
        self.status_bar.pack(side=tk.BOTTOM, fill=tk.X)

        ttk.Separator(self.status_bar, orient=tk.HORIZONTAL).pack(fill=tk.X)

        status_content = ttk.Frame(self.status_bar)
        status_content.pack(fill=tk.X, padx=10, pady=5)

        # Outlook status
        self.outlook_status = ttk.Label(
            status_content,
            text="Outlook: Checking...",
            font=FONTS['small']
        )
        self.outlook_status.pack(side=tk.LEFT)

        # Worker status
        self.worker_status = ttk.Label(
            status_content,
            text="Worker: Stopped",
            font=FONTS['small']
        )
        self.worker_status.pack(side=tk.LEFT, padx=(20, 0))

        # Next email info
        self.next_email_label = ttk.Label(
            status_content,
            text="",
            font=FONTS['small']
        )
        self.next_email_label.pack(side=tk.RIGHT)

        # Check Outlook status
        self.root.after(1000, self._update_status)

    def _setup_worker(self) -> None:
        """Setup the background worker."""
        self.worker = get_worker(self.config)

        # Set callbacks
        self.worker.on_email_sent = self._on_email_sent
        self.worker.on_reply_detected = self._on_reply_detected
        self.worker.on_unsubscribe_detected = self._on_unsubscribe_detected
        self.worker.on_error = self._on_worker_error
        self.worker.on_status_changed = self._on_worker_status_changed

    def _show_view(self, view_name: str) -> None:
        """Show a specific view."""
        # Clear current content
        for widget in self.content_frame.winfo_children():
            widget.destroy()

        # Update nav button states (visual feedback)
        for name, btn in self.nav_buttons.items():
            if name == view_name:
                btn.state(['pressed'])
            else:
                btn.state(['!pressed'])

        # Load view
        try:
            if view_name == 'dashboard':
                from ui.views.dashboard_view import DashboardView
                self._current_view = DashboardView(self.content_frame, self)
            elif view_name == 'campaigns':
                from ui.views.campaign_list_view import CampaignListView
                self._current_view = CampaignListView(self.content_frame, self)
            elif view_name == 'contacts':
                from ui.views.contact_list_view import ContactListView
                self._current_view = ContactListView(self.content_frame, self)
            elif view_name == 'templates':
                from ui.views.template_editor_view import TemplateEditorView
                self._current_view = TemplateEditorView(self.content_frame, self)
            elif view_name == 'suppression':
                from ui.views.suppression_view import SuppressionView
                self._current_view = SuppressionView(self.content_frame, self)
            elif view_name == 'reports':
                from ui.views.reports_view import ReportsView
                self._current_view = ReportsView(self.content_frame, self)
            elif view_name == 'settings':
                from ui.views.settings_view import SettingsView
                self._current_view = SettingsView(self.content_frame, self)
            else:
                # Placeholder for unknown views
                ttk.Label(
                    self.content_frame,
                    text=f"View: {view_name}",
                    font=FONTS['heading']
                ).pack(pady=50)

            self._current_view.pack(fill=tk.BOTH, expand=True)

        except ImportError as e:
            logger.warning(f"View not available: {view_name} - {e}")
            ttk.Label(
                self.content_frame,
                text=f"View '{view_name}' is not yet implemented",
                font=FONTS['body']
            ).pack(pady=50)

    def _update_status(self) -> None:
        """Update status bar information."""
        # Outlook status
        outlook = OutlookService()
        if outlook.is_outlook_running():
            self.outlook_status.configure(text="Outlook: Connected", foreground='green')
        else:
            self.outlook_status.configure(text="Outlook: Not Available", foreground='red')

        # Worker status
        if self.worker:
            status = self.worker.get_status()
            if status['running'] and not status['paused']:
                self.worker_status.configure(text="Worker: Running", foreground='green')
            elif status['paused']:
                self.worker_status.configure(text="Worker: Paused", foreground='orange')
            else:
                self.worker_status.configure(text="Worker: Stopped", foreground='gray')

        # Schedule next update
        self.root.after(10000, self._update_status)

    def _show_migration_dialog(self) -> None:
        """Show migration export dialog."""
        try:
            from ui.dialogs.migration_dialog import MigrationDialog
            MigrationDialog(self.root)
        except ImportError:
            messagebox.showinfo("Migration", "Migration dialog not yet implemented")

    def _show_about(self) -> None:
        """Show about dialog."""
        messagebox.showinfo(
            "About Lead Generator Standalone",
            "Lead Generator Standalone\n"
            "Version 1.0.0\n\n"
            "Single-user desktop application for\n"
            "email marketing campaigns.\n\n"
            "Powered by Python + ttkbootstrap"
        )

    def _on_email_sent(self, campaign_id: int, contact_id: int) -> None:
        """Handle email sent callback."""
        logger.info(f"Email sent: campaign={campaign_id}, contact={contact_id}")
        # Refresh current view if it's dashboard or campaigns
        if hasattr(self._current_view, 'refresh'):
            self.root.after(100, self._current_view.refresh)

    def _on_reply_detected(self, campaign_id: int, contact_id: int) -> None:
        """Handle reply detected callback."""
        logger.info(f"Reply detected: campaign={campaign_id}, contact={contact_id}")
        if hasattr(self._current_view, 'refresh'):
            self.root.after(100, self._current_view.refresh)

    def _on_unsubscribe_detected(self, email: str) -> None:
        """Handle unsubscribe detected callback."""
        logger.info(f"Unsubscribe detected: {email}")
        if hasattr(self._current_view, 'refresh'):
            self.root.after(100, self._current_view.refresh)

    def _on_worker_error(self, message: str) -> None:
        """Handle worker error callback."""
        logger.error(f"Worker error: {message}")

    def _on_worker_status_changed(self, status: str) -> None:
        """Handle worker status change."""
        if status == 'Running':
            self.worker_status.configure(text="Worker: Running", foreground='green')
        elif status == 'Paused':
            self.worker_status.configure(text="Worker: Paused", foreground='orange')
        else:
            self.worker_status.configure(text="Worker: Stopped", foreground='gray')

    def _on_close(self) -> None:
        """Handle application close."""
        # Stop worker
        if self.worker:
            self.worker.stop()

        self.root.destroy()

    def run(self) -> None:
        """Run the application main loop."""
        logger.info("Starting Lead Generator Standalone UI")
        self.root.mainloop()
