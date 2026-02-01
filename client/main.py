#!/usr/bin/env python3
"""
Lead Generator - Python Tkinter Client
Digital Marketing Campaign Tool

Entry point for the application.
"""
import logging
import sys
import os
from pathlib import Path

# Add client directory to path for imports
sys.path.insert(0, str(Path(__file__).parent))

import yaml
import ttkbootstrap as ttk
from ttkbootstrap.constants import *

from core.api_client import ApiClient
from core.models import LoginResponse
from ui.app import App
from ui.views.login_view import LoginView
from ui.views.dashboard_view import DashboardView
from ui.views.campaign_list_view import CampaignListView
from ui.views.campaign_detail_view import CampaignDetailView
from ui.views.contact_list_view import ContactListView
from ui.views.template_editor_view import TemplateEditorView
from ui.views.reports_view import ReportsView
from ui.views.user_management_view import UserManagementView
from ui.views.mail_accounts_view import MailAccountsView
from ui.views.suppression_view import SuppressionView
from ui.views.settings_view import SettingsView


def setup_logging(config: dict) -> None:
    """Configure logging based on config with multiple handlers."""
    from logging.handlers import RotatingFileHandler

    log_config = config.get('logging', {})
    log_level = getattr(logging, log_config.get('level', 'INFO').upper(), logging.INFO)
    log_dir = Path(log_config.get('directory', 'logs/gui'))
    max_bytes = log_config.get('max_bytes', 10485760)
    backup_count = log_config.get('backup_count', 10)
    log_format = log_config.get('format', '%(asctime)s [%(levelname)s] %(name)s: %(message)s')
    date_format = log_config.get('date_format', '%Y-%m-%d %H:%M:%S')

    # Create log directory
    log_dir.mkdir(parents=True, exist_ok=True)

    # Create formatter
    formatter = logging.Formatter(log_format, datefmt=date_format)

    # Root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(log_level)

    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(log_level)
    console_handler.setFormatter(formatter)
    root_logger.addHandler(console_handler)

    # Main log file (all messages)
    main_log = log_dir / log_config.get('main_log', 'gui.log')
    main_handler = RotatingFileHandler(
        main_log, maxBytes=max_bytes, backupCount=backup_count, encoding='utf-8'
    )
    main_handler.setLevel(log_level)
    main_handler.setFormatter(formatter)
    root_logger.addHandler(main_handler)

    # Error log file (errors only)
    error_log = log_dir / log_config.get('error_log', 'gui-errors.log')
    error_handler = RotatingFileHandler(
        error_log, maxBytes=max_bytes, backupCount=backup_count, encoding='utf-8'
    )
    error_handler.setLevel(logging.ERROR)
    error_handler.setFormatter(formatter)
    root_logger.addHandler(error_handler)

    # API calls log (separate logger)
    api_logger = logging.getLogger('api_calls')
    api_log = log_dir / log_config.get('api_log', 'api-calls.log')
    api_handler = RotatingFileHandler(
        api_log, maxBytes=max_bytes, backupCount=backup_count, encoding='utf-8'
    )
    api_handler.setLevel(logging.DEBUG)
    api_handler.setFormatter(logging.Formatter(
        '%(asctime)s | %(levelname)s | %(message)s', datefmt=date_format
    ))
    api_logger.addHandler(api_handler)

    logging.info(f"=== Lead Generator GUI Logging Initialized ===")
    logging.info(f"Log directory: {log_dir.absolute()}")
    logging.info(f"Log level: {logging.getLevelName(log_level)}")


def load_config() -> dict:
    """Load configuration from config.yaml."""
    config_path = Path(__file__).parent / 'config.yaml'

    if config_path.exists():
        with open(config_path, 'r', encoding='utf-8') as f:
            return yaml.safe_load(f)

    # Default config
    return {
        'api': {
            'base_url': 'http://localhost:5000',
            'timeout': 30,
            'retry_attempts': 3
        },
        'ui': {
            'theme': 'cosmo',
            'window_width': 1400,
            'window_height': 900
        },
        'logging': {
            'level': 'INFO'
        }
    }


class LeadGeneratorApp:
    """Main application controller."""

    def __init__(self, config: dict):
        self.config = config
        self.logger = logging.getLogger(__name__)

        # Initialize API client
        api_config = config.get('api', {})
        self.api = ApiClient(
            base_url=api_config.get('base_url', 'http://localhost:5000'),
            timeout=api_config.get('timeout', 30),
            retry_attempts=api_config.get('retry_attempts', 3)
        )

        # UI config
        ui_config = config.get('ui', {})
        self.theme = ui_config.get('theme', 'cosmo')
        self.window_width = ui_config.get('window_width', 1400)
        self.window_height = ui_config.get('window_height', 900)

        # Windows
        self.login_window = None
        self.main_app = None

    def run(self) -> None:
        """Start the application."""
        self.logger.info("Starting Lead Generator application")
        self.show_login()

    def show_login(self) -> None:
        """Show the login window."""
        self.login_window = ttk.Window(
            title="Lead Generator - Login",
            themename=self.theme,
            size=(500, 500),
            resizable=(False, False)
        )

        # Center window
        self.login_window.update_idletasks()
        x = (self.login_window.winfo_screenwidth() - 500) // 2
        y = (self.login_window.winfo_screenheight() - 500) // 2
        self.login_window.geometry(f"+{x}+{y}")

        # Create login view
        login_view = LoginView(
            self.login_window,
            api=self.api,
            on_login_success=self.on_login_success
        )
        login_view.pack(fill=BOTH, expand=True)

        self.login_window.mainloop()

    def on_login_success(self, response: LoginResponse) -> None:
        """Handle successful login."""
        self.logger.info(f"User {response.username} logged in")

        # Close login window
        if self.login_window:
            self.login_window.destroy()
            self.login_window = None

        # Show main application
        self.show_main_app(response)

    def show_main_app(self, login_response: LoginResponse) -> None:
        """Show the main application window."""
        self.main_app = App(
            api_client=self.api,
            theme=self.theme,
            width=self.window_width,
            height=self.window_height
        )

        # Register views
        self.main_app.register_view("dashboard_view", DashboardView)
        self.main_app.register_view("campaign_list_view", CampaignListView)
        self.main_app.register_view("campaign_detail_view", CampaignDetailView)
        self.main_app.register_view("contact_list_view", ContactListView)
        self.main_app.register_view("template_editor_view", TemplateEditorView)
        self.main_app.register_view("reports_view", ReportsView)
        self.main_app.register_view("user_management_view", UserManagementView)
        self.main_app.register_view("mail_accounts_view", MailAccountsView)
        self.main_app.register_view("suppression_view", SuppressionView)
        self.main_app.register_view("settings_view", SettingsView)

        # Update user info in sidebar
        self.main_app.update_user_info(login_response.username, login_response.role)

        # Set logout callback
        self.main_app.set_logout_callback(self.on_logout)

        # Set session expired callback
        self.api.auth.set_on_session_expired(self.on_session_expired)

        # Show dashboard
        self.main_app.show_view("dashboard_view")

        # Start main loop
        self.main_app.mainloop()

    def on_logout(self) -> None:
        """Handle logout."""
        self.logger.info("User logging out")

        # Logout from API
        self.api.logout()

        # Close main app
        if self.main_app:
            self.main_app.destroy()
            self.main_app = None

        # Show login again
        self.show_login()

    def on_session_expired(self) -> None:
        """Handle session expiration."""
        self.logger.warning("Session expired")

        if self.main_app:
            self.main_app.show_error(
                "Session Expired",
                "Your session has expired. Please log in again."
            )
            self.on_logout()


def main():
    """Main entry point."""
    # Load configuration
    config = load_config()

    # Setup logging
    setup_logging(config)

    logger = logging.getLogger(__name__)
    logger.info("Lead Generator client starting...")

    try:
        # Create and run application
        app = LeadGeneratorApp(config)
        app.run()

    except Exception as e:
        logger.exception(f"Fatal error: {e}")
        sys.exit(1)

    logger.info("Application closed")


if __name__ == "__main__":
    main()
