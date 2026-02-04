"""Settings view for Lead Generator Standalone."""

import tkinter as tk
from tkinter import ttk, messagebox
from typing import TYPE_CHECKING

from ui.theme import FONTS
from core.database import get_setting, set_setting, get_db

if TYPE_CHECKING:
    from ui.app import MainApplication


class SettingsView(ttk.Frame):
    """Application settings view."""

    def __init__(self, parent, app: 'MainApplication'):
        super().__init__(parent)
        self.app = app

        self._create_widgets()
        self._load_settings()

    def _create_widgets(self) -> None:
        """Create view widgets."""
        # Header
        ttk.Label(self, text="Settings", font=FONTS['heading']).pack(anchor='w', pady=(0, 20))

        # Create notebook for sections
        notebook = ttk.Notebook(self)
        notebook.pack(fill=tk.BOTH, expand=True)

        # Mail Account Tab
        mail_frame = ttk.Frame(notebook, padding=20)
        notebook.add(mail_frame, text="Mail Account")
        self._create_mail_section(mail_frame)

        # Sending Tab
        sending_frame = ttk.Frame(notebook, padding=20)
        notebook.add(sending_frame, text="Sending")
        self._create_sending_section(sending_frame)

        # Outlook Tab
        outlook_frame = ttk.Frame(notebook, padding=20)
        notebook.add(outlook_frame, text="Outlook")
        self._create_outlook_section(outlook_frame)

        # About Tab
        about_frame = ttk.Frame(notebook, padding=20)
        notebook.add(about_frame, text="About")
        self._create_about_section(about_frame)

        # Save button
        ttk.Button(self, text="Save Settings", command=self._save_settings).pack(anchor='e', pady=(20, 0))

    def _create_mail_section(self, parent) -> None:
        """Create mail account settings."""
        row = 0

        ttk.Label(parent, text="Email Address:").grid(row=row, column=0, sticky='w', pady=5)
        self.email_var = tk.StringVar()
        ttk.Entry(parent, textvariable=self.email_var, width=40).grid(row=row, column=1, sticky='w', pady=5)
        row += 1

        ttk.Label(parent, text="Display Name:").grid(row=row, column=0, sticky='w', pady=5)
        self.display_name_var = tk.StringVar()
        ttk.Entry(parent, textvariable=self.display_name_var, width=40).grid(row=row, column=1, sticky='w', pady=5)
        row += 1

        ttk.Label(parent, text="Daily Limit:").grid(row=row, column=0, sticky='w', pady=5)
        self.daily_limit_var = tk.IntVar(value=50)
        ttk.Spinbox(parent, from_=1, to=500, textvariable=self.daily_limit_var, width=10).grid(row=row, column=1, sticky='w', pady=5)
        row += 1

        ttk.Label(parent, text="Hourly Limit:").grid(row=row, column=0, sticky='w', pady=5)
        self.hourly_limit_var = tk.IntVar(value=10)
        ttk.Spinbox(parent, from_=1, to=100, textvariable=self.hourly_limit_var, width=10).grid(row=row, column=1, sticky='w', pady=5)

    def _create_sending_section(self, parent) -> None:
        """Create sending defaults settings."""
        row = 0

        ttk.Label(parent, text="Sending Window:").grid(row=row, column=0, sticky='w', pady=5)
        window_frame = ttk.Frame(parent)
        window_frame.grid(row=row, column=1, sticky='w', pady=5)

        self.window_start_var = tk.StringVar(value="09:00")
        ttk.Entry(window_frame, textvariable=self.window_start_var, width=8).pack(side=tk.LEFT)
        ttk.Label(window_frame, text="to").pack(side=tk.LEFT, padx=5)
        self.window_end_var = tk.StringVar(value="17:00")
        ttk.Entry(window_frame, textvariable=self.window_end_var, width=8).pack(side=tk.LEFT)
        row += 1

        ttk.Label(parent, text="Inter-Email Delay (min):").grid(row=row, column=0, sticky='w', pady=5)
        self.email_delay_var = tk.IntVar(value=30)
        ttk.Spinbox(parent, from_=1, to=120, textvariable=self.email_delay_var, width=10).grid(row=row, column=1, sticky='w', pady=5)
        row += 1

        ttk.Label(parent, text="Step Delay (days):").grid(row=row, column=0, sticky='w', pady=5)
        self.step_delay_var = tk.IntVar(value=3)
        ttk.Spinbox(parent, from_=1, to=30, textvariable=self.step_delay_var, width=10).grid(row=row, column=1, sticky='w', pady=5)
        row += 1

        ttk.Label(parent, text="Randomization (min):").grid(row=row, column=0, sticky='w', pady=5)
        self.randomization_var = tk.IntVar(value=15)
        ttk.Spinbox(parent, from_=0, to=60, textvariable=self.randomization_var, width=10).grid(row=row, column=1, sticky='w', pady=5)

    def _create_outlook_section(self, parent) -> None:
        """Create Outlook settings."""
        row = 0

        ttk.Label(parent, text="Scan Interval (sec):").grid(row=row, column=0, sticky='w', pady=5)
        self.scan_interval_var = tk.IntVar(value=60)
        ttk.Spinbox(parent, from_=30, to=300, textvariable=self.scan_interval_var, width=10).grid(row=row, column=1, sticky='w', pady=5)
        row += 1

        ttk.Label(parent, text="Scan Folders:").grid(row=row, column=0, sticky='w', pady=5)
        self.scan_folders_var = tk.StringVar(value="Inbox,Unsubscribe")
        ttk.Entry(parent, textvariable=self.scan_folders_var, width=40).grid(row=row, column=1, sticky='w', pady=5)
        row += 1

        ttk.Label(parent, text="Unsubscribe Keywords (EN):").grid(row=row, column=0, sticky='w', pady=5)
        self.unsub_en_var = tk.StringVar()
        ttk.Entry(parent, textvariable=self.unsub_en_var, width=60).grid(row=row, column=1, sticky='w', pady=5)
        row += 1

        ttk.Label(parent, text="Unsubscribe Keywords (FR):").grid(row=row, column=0, sticky='w', pady=5)
        self.unsub_fr_var = tk.StringVar()
        ttk.Entry(parent, textvariable=self.unsub_fr_var, width=60).grid(row=row, column=1, sticky='w', pady=5)

    def _create_about_section(self, parent) -> None:
        """Create about section."""
        ttk.Label(parent, text="Lead Generator Standalone", font=FONTS['heading']).pack(anchor='w')
        ttk.Label(parent, text="Version 1.0.0").pack(anchor='w', pady=(5, 20))

        ttk.Label(parent, text="Single-user desktop application for email marketing campaigns.").pack(anchor='w')
        ttk.Label(parent, text="").pack(anchor='w')
        ttk.Label(parent, text="Features:").pack(anchor='w', pady=(10, 5))
        ttk.Label(parent, text="  - Campaign management with email sequences").pack(anchor='w')
        ttk.Label(parent, text="  - Contact lists with CSV import/export").pack(anchor='w')
        ttk.Label(parent, text="  - Outlook integration for sending emails").pack(anchor='w')
        ttk.Label(parent, text="  - Reply and unsubscribe detection").pack(anchor='w')
        ttk.Label(parent, text="  - Suppression list management").pack(anchor='w')
        ttk.Label(parent, text="  - Basic reporting").pack(anchor='w')

        # Migration section
        ttk.Separator(parent, orient=tk.HORIZONTAL).pack(fill=tk.X, pady=20)
        ttk.Label(parent, text="Migration", font=FONTS['subheading']).pack(anchor='w')
        ttk.Label(parent, text="Export data for migration to multi-user version:").pack(anchor='w', pady=(5, 10))
        ttk.Button(parent, text="Export Data for Migration", command=self._show_migration).pack(anchor='w')

    def _load_settings(self) -> None:
        """Load current settings."""
        # Mail account
        db = get_db()
        account = db.fetchone("SELECT * FROM mail_account WHERE is_active = 1 LIMIT 1")
        if account:
            self.email_var.set(account['email_address'] or '')
            self.display_name_var.set(account['display_name'] or '')
            self.daily_limit_var.set(account['daily_limit'] or 50)
            self.hourly_limit_var.set(account['hourly_limit'] or 10)

        # Load from settings table
        self.scan_interval_var.set(int(get_setting('outlook_scan_interval_seconds', 60)))
        self.scan_folders_var.set(get_setting('scan_folders', 'Inbox,Unsubscribe'))
        self.unsub_en_var.set(get_setting('unsubscribe_keywords_en', 'UNSUBSCRIBE,STOP,REMOVE,OPT OUT,OPT-OUT'))
        self.unsub_fr_var.set(get_setting('unsubscribe_keywords_fr', 'DÉSINSCRIRE,DÉSINSCRIPTION,STOP,ARRÊTER,SUPPRIMER'))

    def _save_settings(self) -> None:
        """Save settings."""
        try:
            db = get_db()

            # Save mail account
            email = self.email_var.get().strip()
            if email:
                # Check if account exists
                existing = db.fetchone("SELECT account_id FROM mail_account WHERE email_address = ?", (email,))
                if existing:
                    db.execute("""
                        UPDATE mail_account
                        SET display_name = ?, daily_limit = ?, hourly_limit = ?
                        WHERE email_address = ?
                    """, (self.display_name_var.get(), self.daily_limit_var.get(),
                          self.hourly_limit_var.get(), email))
                else:
                    db.execute("""
                        INSERT INTO mail_account (email_address, display_name, daily_limit, hourly_limit)
                        VALUES (?, ?, ?, ?)
                    """, (email, self.display_name_var.get(), self.daily_limit_var.get(),
                          self.hourly_limit_var.get()))

            # Save other settings
            set_setting('outlook_scan_interval_seconds', self.scan_interval_var.get())
            set_setting('scan_folders', self.scan_folders_var.get())
            set_setting('unsubscribe_keywords_en', self.unsub_en_var.get())
            set_setting('unsubscribe_keywords_fr', self.unsub_fr_var.get())

            messagebox.showinfo("Success", "Settings saved")
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def _show_migration(self) -> None:
        """Show migration dialog."""
        try:
            from ui.dialogs.migration_dialog import MigrationDialog
            MigrationDialog(self.winfo_toplevel())
        except ImportError:
            messagebox.showinfo("Migration", "Migration export not yet implemented")
