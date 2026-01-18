"""Settings Frame

Application configuration and settings.
"""

import customtkinter as ctk
from tkinter import filedialog
from gui.dialogs import ConfirmationDialog, InfoDialog
from pathlib import Path
import os


class SettingsFrame(ctk.CTkScrollableFrame):
    """Settings configuration frame."""

    def __init__(self, parent, app):
        """Initialize settings frame.

        Args:
            parent: Parent widget
            app: Main application instance
        """
        super().__init__(parent, fg_color="transparent")

        self.app = app
        self.gui_config = app.gui_config

        # Configure grid
        self.grid_columnconfigure(0, weight=1)

        # Create sections
        self.create_header()
        self.create_paths_section()
        self.create_appearance_section()
        self.create_email_settings()
        self.create_behavior_section()
        self.create_outlook_section()
        self.create_action_buttons()

        # Load current settings
        self.load_settings()

    def create_header(self) -> None:
        """Create header with title."""
        title_label = ctk.CTkLabel(
            self,
            text="SETTINGS",
            font=("Arial Bold", 24),
            anchor="w"
        )
        title_label.grid(row=0, column=0, sticky="w", pady=(10, 20), padx=20)

    def create_paths_section(self) -> None:
        """Create paths configuration section."""
        paths_frame = ctk.CTkFrame(self)
        paths_frame.grid(row=1, column=0, sticky="ew", padx=20, pady=(0, 20))
        paths_frame.grid_columnconfigure(1, weight=1)

        # Title
        title = ctk.CTkLabel(
            paths_frame,
            text="PATHS",
            font=("Arial Bold", 14),
            anchor="w"
        )
        title.grid(row=0, column=0, columnspan=3, sticky="w", padx=15, pady=(15, 10))

        # Project folder
        row = 1
        ctk.CTkLabel(paths_frame, text="Project folder:", font=("Arial", 11)).grid(
            row=row, column=0, sticky="w", padx=(15, 10), pady=5
        )
        self.project_folder_var = ctk.StringVar()
        folder_entry = ctk.CTkEntry(paths_frame, textvariable=self.project_folder_var)
        folder_entry.grid(row=row, column=1, sticky="ew", padx=5, pady=5)
        browse_btn = ctk.CTkButton(
            paths_frame,
            text="Browse",
            command=lambda: self.browse_folder(self.project_folder_var),
            width=80
        )
        browse_btn.grid(row=row, column=2, padx=(5, 15), pady=5)

        # Python executable
        row += 1
        ctk.CTkLabel(paths_frame, text="Python executable:", font=("Arial", 11)).grid(
            row=row, column=0, sticky="w", padx=(15, 10), pady=5
        )
        self.python_exe_var = ctk.StringVar()
        python_entry = ctk.CTkEntry(paths_frame, textvariable=self.python_exe_var)
        python_entry.grid(row=row, column=1, sticky="ew", padx=5, pady=5)
        browse_python_btn = ctk.CTkButton(
            paths_frame,
            text="Browse",
            command=lambda: self.browse_file(self.python_exe_var),
            width=80
        )
        browse_python_btn.grid(row=row, column=2, padx=(5, 15), pady=5)

        # Contacts file
        row += 1
        ctk.CTkLabel(paths_frame, text="Contacts file:", font=("Arial", 11)).grid(
            row=row, column=0, sticky="w", padx=(15, 10), pady=5
        )
        self.contacts_file_var = ctk.StringVar()
        contacts_entry = ctk.CTkEntry(paths_frame, textvariable=self.contacts_file_var)
        contacts_entry.grid(row=row, column=1, sticky="ew", padx=5, pady=5)
        browse_contacts_btn = ctk.CTkButton(
            paths_frame,
            text="Browse",
            command=lambda: self.browse_file(self.contacts_file_var, [("Excel files", "*.xlsx")]),
            width=80
        )
        browse_contacts_btn.grid(row=row, column=2, padx=(5, 15), pady=5)

        # Templates folder
        row += 1
        ctk.CTkLabel(paths_frame, text="Templates folder:", font=("Arial", 11)).grid(
            row=row, column=0, sticky="w", padx=(15, 10), pady=(5, 15)
        )
        self.templates_folder_var = ctk.StringVar()
        templates_entry = ctk.CTkEntry(paths_frame, textvariable=self.templates_folder_var)
        templates_entry.grid(row=row, column=1, sticky="ew", padx=5, pady=(5, 15))
        browse_templates_btn = ctk.CTkButton(
            paths_frame,
            text="Browse",
            command=lambda: self.browse_folder(self.templates_folder_var),
            width=80
        )
        browse_templates_btn.grid(row=row, column=2, padx=(5, 15), pady=(5, 15))

    def create_appearance_section(self) -> None:
        """Create appearance settings section."""
        appear_frame = ctk.CTkFrame(self)
        appear_frame.grid(row=2, column=0, sticky="ew", padx=20, pady=(0, 20))
        appear_frame.grid_columnconfigure(1, weight=1)

        # Title
        title = ctk.CTkLabel(
            appear_frame,
            text="APPEARANCE",
            font=("Arial Bold", 14),
            anchor="w"
        )
        title.grid(row=0, column=0, columnspan=2, sticky="w", padx=15, pady=(15, 10))

        # Theme
        row = 1
        theme_frame = ctk.CTkFrame(appear_frame, fg_color="transparent")
        theme_frame.grid(row=row, column=0, columnspan=2, sticky="w", padx=15, pady=5)

        ctk.CTkLabel(theme_frame, text="Theme:", font=("Arial", 11)).pack(side="left", padx=(0, 20))

        self.theme_var = ctk.StringVar(value="dark")
        for theme in ["Dark", "Light", "System"]:
            radio = ctk.CTkRadioButton(
                theme_frame,
                text=theme,
                variable=self.theme_var,
                value=theme.lower(),
                command=self.on_theme_change
            )
            radio.pack(side="left", padx=10)

        # Color scheme
        row += 1
        ctk.CTkLabel(appear_frame, text="Color scheme:", font=("Arial", 11)).grid(
            row=row, column=0, sticky="w", padx=15, pady=(10, 15)
        )
        self.color_var = ctk.StringVar(value="blue")
        color_menu = ctk.CTkOptionMenu(
            appear_frame,
            variable=self.color_var,
            values=["Blue", "Green", "Dark-Blue"],
            width=150
        )
        color_menu.grid(row=row, column=1, sticky="w", padx=5, pady=(10, 15))

    def create_email_settings(self) -> None:
        """Create email settings section."""
        email_frame = ctk.CTkFrame(self)
        email_frame.grid(row=3, column=0, sticky="ew", padx=20, pady=(0, 20))
        email_frame.grid_columnconfigure(1, weight=1)

        # Title
        title = ctk.CTkLabel(
            email_frame,
            text="EMAIL SETTINGS",
            font=("Arial Bold", 14),
            anchor="w"
        )
        title.grid(row=0, column=0, columnspan=2, sticky="w", padx=15, pady=(15, 10))

        # Sender name
        row = 1
        ctk.CTkLabel(email_frame, text="Sender name:", font=("Arial", 11)).grid(
            row=row, column=0, sticky="w", padx=15, pady=5
        )
        self.sender_name_var = ctk.StringVar()
        sender_entry = ctk.CTkEntry(email_frame, textvariable=self.sender_name_var, width=250)
        sender_entry.grid(row=row, column=1, sticky="w", padx=5, pady=5)

        # Default subject
        row += 1
        ctk.CTkLabel(email_frame, text="Default subject:", font=("Arial", 11)).grid(
            row=row, column=0, sticky="w", padx=15, pady=5
        )
        self.default_subject_var = ctk.StringVar()
        subject_entry = ctk.CTkEntry(email_frame, textvariable=self.default_subject_var, width=300)
        subject_entry.grid(row=row, column=1, sticky="w", padx=5, pady=5)

        # Delay between sends
        row += 1
        delay_frame = ctk.CTkFrame(email_frame, fg_color="transparent")
        delay_frame.grid(row=row, column=0, columnspan=2, sticky="w", padx=15, pady=5)

        ctk.CTkLabel(delay_frame, text="Delay between sends:", font=("Arial", 11)).pack(side="left", padx=(0, 10))
        self.send_delay_var = ctk.StringVar(value="5")
        delay_entry = ctk.CTkEntry(delay_frame, textvariable=self.send_delay_var, width=80)
        delay_entry.pack(side="left", padx=5)
        ctk.CTkLabel(delay_frame, text="seconds", font=("Arial", 11)).pack(side="left", padx=5)

        # Inbox scan depth
        row += 1
        scan_frame = ctk.CTkFrame(email_frame, fg_color="transparent")
        scan_frame.grid(row=row, column=0, columnspan=2, sticky="w", padx=15, pady=(5, 15))

        ctk.CTkLabel(scan_frame, text="Inbox scan depth:", font=("Arial", 11)).pack(side="left", padx=(0, 10))
        self.scan_depth_var = ctk.StringVar(value="30")
        scan_entry = ctk.CTkEntry(scan_frame, textvariable=self.scan_depth_var, width=80)
        scan_entry.pack(side="left", padx=5)
        ctk.CTkLabel(scan_frame, text="days", font=("Arial", 11)).pack(side="left", padx=5)

    def create_behavior_section(self) -> None:
        """Create behavior settings section."""
        behavior_frame = ctk.CTkFrame(self)
        behavior_frame.grid(row=4, column=0, sticky="ew", padx=20, pady=(0, 20))
        behavior_frame.grid_columnconfigure(0, weight=1)

        # Title
        title = ctk.CTkLabel(
            behavior_frame,
            text="BEHAVIOR",
            font=("Arial Bold", 14),
            anchor="w"
        )
        title.grid(row=0, column=0, sticky="w", padx=15, pady=(15, 10))

        # Checkboxes
        self.confirm_send_var = ctk.BooleanVar(value=True)
        confirm_check = ctk.CTkCheckBox(
            behavior_frame,
            text="Confirm before sending emails",
            variable=self.confirm_send_var,
            font=("Arial", 11)
        )
        confirm_check.grid(row=1, column=0, sticky="w", padx=15, pady=2)

        self.show_notifications_var = ctk.BooleanVar(value=True)
        notif_check = ctk.CTkCheckBox(
            behavior_frame,
            text="Show system notifications",
            variable=self.show_notifications_var,
            font=("Arial", 11)
        )
        notif_check.grid(row=2, column=0, sticky="w", padx=15, pady=2)

        self.minimize_tray_var = ctk.BooleanVar(value=True)
        tray_check = ctk.CTkCheckBox(
            behavior_frame,
            text="Minimize to system tray",
            variable=self.minimize_tray_var,
            font=("Arial", 11)
        )
        tray_check.grid(row=3, column=0, sticky="w", padx=15, pady=2)

        self.start_minimized_var = ctk.BooleanVar(value=False)
        start_min_check = ctk.CTkCheckBox(
            behavior_frame,
            text="Start minimized",
            variable=self.start_minimized_var,
            font=("Arial", 11)
        )
        start_min_check.grid(row=4, column=0, sticky="w", padx=15, pady=(2, 15))

    def create_outlook_section(self) -> None:
        """Create Outlook connection section."""
        outlook_frame = ctk.CTkFrame(self)
        outlook_frame.grid(row=5, column=0, sticky="ew", padx=20, pady=(0, 20))
        outlook_frame.grid_columnconfigure(0, weight=1)

        # Title
        title = ctk.CTkLabel(
            outlook_frame,
            text="OUTLOOK CONNECTION",
            font=("Arial Bold", 14),
            anchor="w"
        )
        title.grid(row=0, column=0, sticky="w", padx=15, pady=(15, 10))

        # Status
        status_frame = ctk.CTkFrame(outlook_frame, fg_color="#1F2937")
        status_frame.grid(row=1, column=0, sticky="ew", padx=15, pady=(0, 10))

        self.outlook_status_label = ctk.CTkLabel(
            status_frame,
            text="Status: ○ Not connected",
            font=("Arial", 12),
            anchor="w"
        )
        self.outlook_status_label.grid(row=0, column=0, sticky="w", padx=15, pady=10)

        # Buttons
        button_frame = ctk.CTkFrame(outlook_frame, fg_color="transparent")
        button_frame.grid(row=2, column=0, sticky="w", padx=15, pady=(0, 15))

        test_btn = ctk.CTkButton(
            button_frame,
            text="Test Connection",
            command=self.on_test_connection,
            width=140
        )
        test_btn.pack(side="left", padx=(0, 10))

        reconnect_btn = ctk.CTkButton(
            button_frame,
            text="Reconnect",
            command=self.on_reconnect,
            width=120,
            fg_color="gray"
        )
        reconnect_btn.pack(side="left")

    def create_action_buttons(self) -> None:
        """Create action buttons."""
        button_frame = ctk.CTkFrame(self, fg_color="transparent")
        button_frame.grid(row=6, column=0, sticky="ew", padx=20, pady=(0, 20))

        save_btn = ctk.CTkButton(
            button_frame,
            text="💾 Save Settings",
            command=self.on_save_settings,
            width=150,
            fg_color="#10B981"
        )
        save_btn.pack(side="left", padx=5)

        reset_btn = ctk.CTkButton(
            button_frame,
            text="↩ Reset to Defaults",
            command=self.on_reset_defaults,
            width=150,
            fg_color="gray"
        )
        reset_btn.pack(side="left", padx=5)

        export_btn = ctk.CTkButton(
            button_frame,
            text="📤 Export Config",
            command=self.on_export_config,
            width=150,
            fg_color="#3B82F6"
        )
        export_btn.pack(side="left", padx=5)

    def load_settings(self) -> None:
        """Load current settings from config."""
        # Paths
        self.project_folder_var.set(self.gui_config.get('paths.project_folder', ''))
        self.python_exe_var.set(self.gui_config.get('paths.python_executable', 'python3'))
        self.contacts_file_var.set(self.gui_config.get('paths.contacts_file', 'contacts.xlsx'))
        self.templates_folder_var.set(self.gui_config.get('paths.templates_folder', 'templates'))

        # Appearance
        self.theme_var.set(self.gui_config.get('appearance.theme', 'dark'))
        self.color_var.set(self.gui_config.get('appearance.color_scheme', 'blue'))

        # Email settings (these would come from main config.yaml)
        self.sender_name_var.set("Jean-François")
        self.default_subject_var.set("Partnership Opportunity - ISIT")

        # Behavior
        self.confirm_send_var.set(self.gui_config.get('behavior.confirm_before_send', True))
        self.show_notifications_var.set(self.gui_config.get('behavior.show_notifications', True))
        self.minimize_tray_var.set(self.gui_config.get('behavior.minimize_to_tray', True))
        self.start_minimized_var.set(self.gui_config.get('behavior.start_minimized', False))

    def on_theme_change(self) -> None:
        """Handle theme change."""
        theme = self.theme_var.get()
        ctk.set_appearance_mode(theme)

    def browse_folder(self, var: ctk.StringVar) -> None:
        """Browse for folder.

        Args:
            var: StringVar to update with selected path
        """
        folder = filedialog.askdirectory(initialdir=var.get() or os.path.expanduser("~"))
        if folder:
            var.set(folder)

    def browse_file(self, var: ctk.StringVar, filetypes: list = None) -> None:
        """Browse for file.

        Args:
            var: StringVar to update with selected path
            filetypes: File type filters
        """
        if filetypes is None:
            filetypes = [("All files", "*.*")]

        filename = filedialog.askopenfilename(
            initialdir=os.path.dirname(var.get()) if var.get() else os.path.expanduser("~"),
            filetypes=filetypes
        )
        if filename:
            var.set(filename)

    def on_save_settings(self) -> None:
        """Handle Save Settings button."""
        try:
            # Update paths
            self.gui_config.set('paths.project_folder', self.project_folder_var.get())
            self.gui_config.set('paths.python_executable', self.python_exe_var.get())
            self.gui_config.set('paths.contacts_file', self.contacts_file_var.get())
            self.gui_config.set('paths.templates_folder', self.templates_folder_var.get())

            # Update appearance
            self.gui_config.set('appearance.theme', self.theme_var.get())
            self.gui_config.set('appearance.color_scheme', self.color_var.get())

            # Update behavior
            self.gui_config.set('behavior.confirm_before_send', self.confirm_send_var.get())
            self.gui_config.set('behavior.show_notifications', self.show_notifications_var.get())
            self.gui_config.set('behavior.minimize_to_tray', self.minimize_tray_var.get())
            self.gui_config.set('behavior.start_minimized', self.start_minimized_var.get())

            # Save to file
            self.gui_config.save()

            InfoDialog.show(self, "Success", "Settings saved successfully.")

            # Validate paths
            validation = self.gui_config.validate_paths()
            missing = [k for k, v in validation.items() if not v]
            if missing:
                InfoDialog.show(
                    self,
                    "Path Warning",
                    f"Some paths do not exist:\n{', '.join(missing)}\n\n"
                    "Please create these directories/files."
                )

        except Exception as e:
            InfoDialog.show(self, "Error", f"Failed to save settings:\n{str(e)}")

    def on_reset_defaults(self) -> None:
        """Handle Reset to Defaults button."""
        dialog = ConfirmationDialog(
            self,
            "Reset Settings",
            "Reset all settings to default values?",
            confirm_text="Reset",
            danger=True
        )

        if dialog.get_result():
            self.gui_config.reset_to_defaults()
            self.load_settings()
            InfoDialog.show(self, "Success", "Settings reset to defaults.")

    def on_export_config(self) -> None:
        """Handle Export Config button."""
        filename = filedialog.asksaveasfilename(
            defaultextension=".yaml",
            filetypes=[("YAML files", "*.yaml"), ("All files", "*.*")]
        )

        if filename:
            if self.gui_config.export_config(filename):
                InfoDialog.show(self, "Success", "Configuration exported successfully.")
            else:
                InfoDialog.show(self, "Error", "Failed to export configuration.")

    def on_test_connection(self) -> None:
        """Handle Test Connection button."""
        # TODO: Implement Outlook connection test
        self.outlook_status_label.configure(text="Status: ● Connected")
        InfoDialog.show(
            self,
            "Test Connection",
            "Outlook connection test will be implemented.\n\n"
            "For now, this is a UI demonstration."
        )

    def on_reconnect(self) -> None:
        """Handle Reconnect button."""
        # TODO: Implement Outlook reconnection
        InfoDialog.show(
            self,
            "Reconnect",
            "Outlook reconnection will be implemented.\n\n"
            "For now, this is a UI demonstration."
        )
