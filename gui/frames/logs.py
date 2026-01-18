"""Logs Frame

Activity history and log viewer.
"""

import customtkinter as ctk
from gui.dialogs import ConfirmationDialog, InfoDialog
from pathlib import Path
import os
from datetime import datetime, timedelta


class LogsFrame(ctk.CTkFrame):
    """Log viewer with filtering and search."""

    LOG_LEVELS = ['All Levels', 'DEBUG', 'INFO', 'WARNING', 'ERROR']
    DATE_FILTERS = ['Today', 'Last 7 Days', 'Last 30 Days', 'All']

    LEVEL_COLORS = {
        'DEBUG': '#6B7280',
        'INFO': '#FFFFFF',
        'WARNING': '#FBBF24',
        'ERROR': '#EF4444'
    }

    def __init__(self, parent, app):
        """Initialize logs frame.

        Args:
            parent: Parent widget
            app: Main application instance
        """
        super().__init__(parent, fg_color="transparent")

        self.app = app
        self.gui_config = app.gui_config
        self.all_logs = []

        # Configure grid
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(2, weight=1)

        # Create components
        self.create_header()
        self.create_toolbar()
        self.create_log_viewer()
        self.create_statistics()

        # Load logs
        self.load_logs()

        # Start auto-refresh
        self.schedule_refresh(5000)  # Refresh every 5 seconds

    def create_header(self) -> None:
        """Create header with title."""
        header_frame = ctk.CTkFrame(self, fg_color="transparent")
        header_frame.grid(row=0, column=0, sticky="ew", pady=(10, 20), padx=20)
        header_frame.grid_columnconfigure(1, weight=1)

        title_label = ctk.CTkLabel(
            header_frame,
            text="LOGS",
            font=("Arial Bold", 24),
            anchor="w"
        )
        title_label.grid(row=0, column=0, sticky="w")

        # Log file info
        self.file_info_label = ctk.CTkLabel(
            header_frame,
            text="Log file: sequence.log",
            font=("Arial", 11),
            text_color="gray"
        )
        self.file_info_label.grid(row=0, column=1, sticky="e", padx=(0, 20))

    def create_toolbar(self) -> None:
        """Create toolbar with filters and actions."""
        toolbar = ctk.CTkFrame(self, fg_color="transparent")
        toolbar.grid(row=1, column=0, sticky="ew", padx=20, pady=(0, 10))
        toolbar.grid_columnconfigure(5, weight=1)

        # Level filter
        ctk.CTkLabel(toolbar, text="Filter:", font=("Arial", 11)).grid(
            row=0, column=0, sticky="w", padx=(0, 5)
        )

        self.level_var = ctk.StringVar(value="All Levels")
        level_menu = ctk.CTkOptionMenu(
            toolbar,
            variable=self.level_var,
            values=self.LOG_LEVELS,
            command=lambda x: self.filter_logs(),
            width=120
        )
        level_menu.grid(row=0, column=1, padx=5)

        # Date filter
        ctk.CTkLabel(toolbar, text="Date:", font=("Arial", 11)).grid(
            row=0, column=2, sticky="w", padx=(15, 5)
        )

        self.date_var = ctk.StringVar(value="Today")
        date_menu = ctk.CTkOptionMenu(
            toolbar,
            variable=self.date_var,
            values=self.DATE_FILTERS,
            command=lambda x: self.filter_logs(),
            width=120
        )
        date_menu.grid(row=0, column=3, padx=5)

        # Search box
        self.search_var = ctk.StringVar()
        self.search_var.trace('w', lambda *args: self.filter_logs())
        search_entry = ctk.CTkEntry(
            toolbar,
            textvariable=self.search_var,
            placeholder_text="🔍 Search logs...",
            width=200
        )
        search_entry.grid(row=0, column=4, padx=(15, 5))

        # Action buttons
        open_btn = ctk.CTkButton(
            toolbar,
            text="📂 Open Folder",
            command=self.on_open_folder,
            width=120,
            height=32,
            fg_color="gray"
        )
        open_btn.grid(row=0, column=6, padx=5)

        clear_btn = ctk.CTkButton(
            toolbar,
            text="🗑 Clear Logs",
            command=self.on_clear_logs,
            width=120,
            height=32,
            fg_color="#EF4444"
        )
        clear_btn.grid(row=0, column=7, padx=5)

    def create_log_viewer(self) -> None:
        """Create log viewer textbox."""
        viewer_frame = ctk.CTkFrame(self)
        viewer_frame.grid(row=2, column=0, sticky="nsew", padx=20, pady=(0, 10))
        viewer_frame.grid_columnconfigure(0, weight=1)
        viewer_frame.grid_rowconfigure(0, weight=1)

        # Log textbox
        self.log_text = ctk.CTkTextbox(
            viewer_frame,
            font=("Courier", 10),
            wrap="none"
        )
        self.log_text.grid(row=0, column=0, sticky="nsew", padx=15, pady=15)

        # Auto-scroll checkbox
        self.auto_scroll_var = ctk.BooleanVar(value=True)
        auto_scroll_check = ctk.CTkCheckBox(
            viewer_frame,
            text="Auto-scroll",
            variable=self.auto_scroll_var,
            font=("Arial", 10)
        )
        auto_scroll_check.place(relx=1.0, rely=1.0, anchor="se", x=-20, y=-20)

    def create_statistics(self) -> None:
        """Create statistics panel."""
        stats_frame = ctk.CTkFrame(self)
        stats_frame.grid(row=3, column=0, sticky="ew", padx=20, pady=(0, 20))
        stats_frame.grid_columnconfigure((0, 1, 2, 3), weight=1)

        title = ctk.CTkLabel(
            stats_frame,
            text="LOG STATISTICS",
            font=("Arial Bold", 12),
            anchor="w"
        )
        title.grid(row=0, column=0, columnspan=4, sticky="w", padx=15, pady=(10, 5))

        # Stats labels
        self.stats_labels = {}

        stats = [
            ("Today", "entries", 0),
            ("Errors", "errors", 1),
            ("Warnings", "warnings", 2),
            ("Emails", "emails", 3)
        ]

        for label_text, key, col in stats:
            stat_label = ctk.CTkLabel(
                stats_frame,
                text=f"{label_text}: 0",
                font=("Arial", 11),
                anchor="w"
            )
            stat_label.grid(row=1, column=col, sticky="w", padx=15, pady=(5, 10))
            self.stats_labels[key] = stat_label

    def load_logs(self) -> None:
        """Load logs from file."""
        self.all_logs = []

        try:
            logs_folder = self.gui_config.get_absolute_path('logs_folder')
            log_file = logs_folder / 'sequence.log'

            if log_file.exists():
                with open(log_file, 'r', encoding='utf-8') as f:
                    self.all_logs = f.readlines()

                # Update file info
                size_kb = log_file.stat().st_size / 1024
                self.file_info_label.configure(
                    text=f"Log file: sequence.log | Size: {size_kb:.1f} KB"
                )
            else:
                self.file_info_label.configure(text="Log file: sequence.log | Not found")

        except Exception as e:
            print(f"Error loading logs: {e}")

        # Apply filters
        self.filter_logs()

    def filter_logs(self) -> None:
        """Apply filters and update display."""
        filtered_logs = self.all_logs.copy()

        # Level filter
        level_filter = self.level_var.get()
        if level_filter != "All Levels":
            filtered_logs = [
                line for line in filtered_logs
                if f"| {level_filter} |" in line
            ]

        # Date filter
        date_filter = self.date_var.get()
        if date_filter != "All":
            today = datetime.now().date()
            if date_filter == "Today":
                date_str = today.strftime("%Y-%m-%d")
                filtered_logs = [
                    line for line in filtered_logs
                    if date_str in line
                ]
            elif date_filter == "Last 7 Days":
                cutoff = today - timedelta(days=7)
                filtered_logs = [
                    line for line in filtered_logs
                    if self._is_recent(line, cutoff)
                ]
            elif date_filter == "Last 30 Days":
                cutoff = today - timedelta(days=30)
                filtered_logs = [
                    line for line in filtered_logs
                    if self._is_recent(line, cutoff)
                ]

        # Search filter
        search_text = self.search_var.get().lower()
        if search_text:
            filtered_logs = [
                line for line in filtered_logs
                if search_text in line.lower()
            ]

        # Update display
        self.display_logs(filtered_logs)

        # Update statistics
        self.update_statistics()

    def _is_recent(self, log_line: str, cutoff_date: datetime.date) -> bool:
        """Check if log line is after cutoff date.

        Args:
            log_line: Log line text
            cutoff_date: Cutoff date

        Returns:
            True if line is recent
        """
        try:
            # Extract date from line (assumes format: YYYY-MM-DD HH:MM:SS)
            date_str = log_line.split('|')[0].strip().split()[0]
            log_date = datetime.strptime(date_str, "%Y-%m-%d").date()
            return log_date >= cutoff_date
        except:
            return True

    def display_logs(self, logs: list) -> None:
        """Display filtered logs.

        Args:
            logs: List of log lines to display
        """
        self.log_text.configure(state="normal")
        self.log_text.delete("1.0", "end")

        # Insert logs with color coding
        for line in logs:
            # Determine color based on level
            color = "#FFFFFF"
            for level, level_color in self.LEVEL_COLORS.items():
                if f"| {level} |" in line:
                    color = level_color
                    break

            self.log_text.insert("end", line)

        # Auto-scroll to end if enabled
        if self.auto_scroll_var.get():
            self.log_text.see("end")

        self.log_text.configure(state="disabled")

    def update_statistics(self) -> None:
        """Update statistics display."""
        today = datetime.now().date().strftime("%Y-%m-%d")

        # Count entries today
        today_entries = len([l for l in self.all_logs if today in l])

        # Count errors
        errors = len([l for l in self.all_logs if "| ERROR |" in l])

        # Count warnings
        warnings = len([l for l in self.all_logs if "| WARNING |" in l])

        # Count email-related entries
        emails = len([l for l in self.all_logs if "email" in l.lower() or "sent" in l.lower()])

        # Update labels
        self.stats_labels['entries'].configure(text=f"Today: {today_entries}")
        self.stats_labels['errors'].configure(text=f"Errors: {errors}")
        self.stats_labels['warnings'].configure(text=f"Warnings: {warnings}")
        self.stats_labels['emails'].configure(text=f"Emails: {emails}")

    def schedule_refresh(self, interval_ms: int) -> None:
        """Schedule automatic log refresh.

        Args:
            interval_ms: Refresh interval in milliseconds
        """
        self.load_logs()
        self.after(interval_ms, lambda: self.schedule_refresh(interval_ms))

    def on_open_folder(self) -> None:
        """Handle Open Folder button."""
        try:
            logs_folder = self.gui_config.get_absolute_path('logs_folder')

            if not logs_folder.exists():
                logs_folder.mkdir(parents=True, exist_ok=True)

            # Open folder in file explorer
            if os.name == 'nt':  # Windows
                os.startfile(logs_folder)
            elif os.name == 'posix':  # Linux/Mac
                os.system(f'xdg-open "{logs_folder}"')

        except Exception as e:
            InfoDialog.show(self, "Error", f"Failed to open folder:\n{str(e)}")

    def on_clear_logs(self) -> None:
        """Handle Clear Logs button."""
        dialog = ConfirmationDialog(
            self,
            "Clear Logs",
            "This will permanently delete all log entries.\n\nContinue?",
            confirm_text="Clear",
            cancel_text="Cancel",
            danger=True
        )

        if not dialog.get_result():
            return

        try:
            logs_folder = self.gui_config.get_absolute_path('logs_folder')
            log_file = logs_folder / 'sequence.log'

            if log_file.exists():
                log_file.unlink()

            # Reload
            self.load_logs()

            InfoDialog.show(self, "Success", "Logs cleared successfully.")

        except Exception as e:
            InfoDialog.show(self, "Error", f"Failed to clear logs:\n{str(e)}")
