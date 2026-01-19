"""Dashboard Frame

Overview screen with metrics, quick actions, and recent activity.
"""

import customtkinter as ctk
from gui.components.progress_card import ProgressCard, MetricCard
from gui.dialogs import ConfirmationDialog, InfoDialog
from datetime import datetime
from pathlib import Path
import os


class DashboardFrame(ctk.CTkScrollableFrame):
    """Dashboard with metrics, quick actions, and activity feed."""

    def __init__(self, parent, app):
        """Initialize dashboard frame.

        Args:
            parent: Parent widget
            app: Main application instance
        """
        super().__init__(parent, fg_color="transparent")

        self.app = app
        self.gui_config = app.gui_config

        # Configure grid
        self.grid_columnconfigure((0, 1, 2, 3), weight=1)

        # Create header
        self.create_header()

        # Create metric cards
        self.create_metric_cards()

        # Create quick actions
        self.create_quick_actions()

        # Create activity feed and status
        self.create_bottom_section()

        # Start auto-refresh if enabled
        auto_refresh = self.gui_config.get('behavior.auto_refresh_seconds', 0)
        if auto_refresh > 0:
            self.schedule_refresh(auto_refresh * 1000)

    def create_header(self) -> None:
        """Create header with title and refresh button."""
        header_frame = ctk.CTkFrame(self, fg_color="transparent")
        header_frame.grid(row=0, column=0, columnspan=4, sticky="ew", pady=(10, 20), padx=20)
        header_frame.grid_columnconfigure(0, weight=1)

        # Title
        title_label = ctk.CTkLabel(
            header_frame,
            text="DASHBOARD",
            font=("Arial Bold", 24),
            anchor="w"
        )
        title_label.grid(row=0, column=0, sticky="w")

        # Refresh button
        refresh_btn = ctk.CTkButton(
            header_frame,
            text="🔄 Refresh",
            command=self.refresh_data,
            width=120,
            height=32
        )
        refresh_btn.grid(row=0, column=1, sticky="e")

    def create_metric_cards(self) -> None:
        """Create top row of metric cards."""
        # Get metrics data
        metrics = self.get_metrics()

        # Create cards
        self.pending_card = ProgressCard(
            self,
            title="PENDING",
            value=str(metrics['pending']),
            icon="○",
            show_progress=True,
            progress_value=0
        )
        self.pending_card.grid(row=1, column=0, padx=10, pady=10, sticky="ew")

        self.sent_card = ProgressCard(
            self,
            title="SENT",
            value=str(metrics['sent']),
            icon="●",
            show_progress=False,
            border_color="#3B82F6"
        )
        self.sent_card.grid(row=1, column=1, padx=10, pady=10, sticky="ew")

        self.replied_card = ProgressCard(
            self,
            title="REPLIED",
            value=str(metrics['replied']),
            icon="✓",
            show_progress=False,
            border_color="#10B981"
        )
        self.replied_card.grid(row=1, column=2, padx=10, pady=10, sticky="ew")

        reply_rate = metrics['reply_rate']
        self.rate_card = ProgressCard(
            self,
            title="REPLY RATE",
            value=f"{reply_rate}%",
            icon="📊",
            show_progress=True,
            progress_value=reply_rate / 100,
            border_color="#8B5CF6"
        )
        self.rate_card.grid(row=1, column=3, padx=10, pady=10, sticky="ew")

    def create_quick_actions(self) -> None:
        """Create quick action buttons."""
        actions_frame = ctk.CTkFrame(self, fg_color="transparent")
        actions_frame.grid(row=2, column=0, columnspan=4, sticky="ew", pady=20, padx=20)
        actions_frame.grid_columnconfigure((0, 1, 2), weight=1)

        # Section title
        title_label = ctk.CTkLabel(
            actions_frame,
            text="QUICK ACTIONS",
            font=("Arial Bold", 14),
            anchor="w"
        )
        title_label.grid(row=0, column=0, columnspan=3, sticky="w", pady=(0, 10))

        # Action buttons
        start_btn = ctk.CTkButton(
            actions_frame,
            text="▶ START\nSEQUENCE",
            command=self.on_start_sequence,
            height=70,
            font=("Arial Bold", 13),
            fg_color="#10B981",
            hover_color="#059669"
        )
        start_btn.grid(row=1, column=0, padx=5, sticky="ew")

        check_btn = ctk.CTkButton(
            actions_frame,
            text="🔍 CHECK\nREPLIES",
            command=self.on_check_replies,
            height=70,
            font=("Arial Bold", 13),
            fg_color="#3B82F6",
            hover_color="#2563EB"
        )
        check_btn.grid(row=1, column=1, padx=5, sticky="ew")

        followup_btn = ctk.CTkButton(
            actions_frame,
            text="↻ SEND\nFOLLOW-UPS",
            command=self.on_send_followups,
            height=70,
            font=("Arial Bold", 13),
            fg_color="#F97316",
            hover_color="#EA580C"
        )
        followup_btn.grid(row=1, column=2, padx=5, sticky="ew")

    def create_bottom_section(self) -> None:
        """Create activity feed and sequence status section."""
        # Container frame
        bottom_frame = ctk.CTkFrame(self, fg_color="transparent")
        bottom_frame.grid(row=3, column=0, columnspan=4, sticky="nsew", padx=20, pady=(0, 20))
        bottom_frame.grid_columnconfigure(0, weight=2)
        bottom_frame.grid_columnconfigure(1, weight=1)

        # Recent Activity
        activity_frame = ctk.CTkFrame(bottom_frame)
        activity_frame.grid(row=0, column=0, sticky="nsew", padx=(0, 10))
        activity_frame.grid_columnconfigure(0, weight=1)
        activity_frame.grid_rowconfigure(1, weight=1)

        activity_title = ctk.CTkLabel(
            activity_frame,
            text="RECENT ACTIVITY",
            font=("Arial Bold", 14),
            anchor="w"
        )
        activity_title.grid(row=0, column=0, sticky="w", padx=15, pady=(15, 10))

        # Activity list (scrollable textbox)
        self.activity_text = ctk.CTkTextbox(
            activity_frame,
            height=200,
            font=("Courier", 11),
            wrap="word"
        )
        self.activity_text.grid(row=1, column=0, sticky="nsew", padx=15, pady=(0, 15))

        # Sequence Status
        status_frame = ctk.CTkFrame(bottom_frame)
        status_frame.grid(row=0, column=1, sticky="nsew")
        status_frame.grid_columnconfigure(0, weight=1)

        status_title = ctk.CTkLabel(
            status_frame,
            text="SEQUENCE STATUS",
            font=("Arial Bold", 14),
            anchor="w"
        )
        status_title.grid(row=0, column=0, sticky="w", padx=15, pady=(15, 10))

        # Status details
        sequence_info = self.get_sequence_status()

        info_labels = [
            f"Current: {sequence_info['id']}",
            f"Status: {sequence_info['status']}",
            f"Started: {sequence_info['started']}",
            f"Total contacts: {sequence_info['total']}"
        ]

        for i, text in enumerate(info_labels):
            label = ctk.CTkLabel(
                status_frame,
                text=text,
                font=("Arial", 12),
                anchor="w"
            )
            label.grid(row=i+1, column=0, sticky="w", padx=15, pady=2)

        # Next action
        next_frame = ctk.CTkFrame(status_frame, fg_color="#1F2937")
        next_frame.grid(row=5, column=0, sticky="ew", padx=15, pady=(15, 15))

        next_label = ctk.CTkLabel(
            next_frame,
            text=sequence_info['next_action'],
            font=("Arial", 11),
            text_color="#FBBF24"
        )
        next_label.pack(pady=10, padx=10)

        # Load activity
        self.load_activity()

    def get_metrics(self) -> dict:
        """Get dashboard metrics from campaign contacts file.

        Returns:
            Dictionary with metric values
        """
        try:
            # Check if campaign is selected
            current_campaign = self.gui_config.get_current_campaign()
            if not current_campaign:
                return {
                    'pending': 0,
                    'sent': 0,
                    'replied': 0,
                    'reply_rate': 0
                }

            # Load campaign contacts and calculate metrics
            contacts_file = self.gui_config.get_campaign_contacts_file()

            if contacts_file.exists():
                import pandas as pd
                df = pd.read_excel(contacts_file)

                pending = len(df[df['status'] == 'pending'])
                sent = len(df[df['status'].isin(['sent', 'followup_1', 'followup_2', 'followup_3'])])
                replied = len(df[df['status'] == 'replied'])

                total_contacted = sent + replied
                reply_rate = int((replied / total_contacted * 100)) if total_contacted > 0 else 0

                return {
                    'pending': pending,
                    'sent': sent,
                    'replied': replied,
                    'reply_rate': reply_rate
                }
        except Exception as e:
            print(f"Error loading metrics: {e}")

        # Return defaults if error
        return {
            'pending': 0,
            'sent': 0,
            'replied': 0,
            'reply_rate': 0
        }

    def get_sequence_status(self) -> dict:
        """Get current sequence status.

        Returns:
            Dictionary with sequence information
        """
        # This would read from sequence state file or database
        # For now, return placeholder data
        return {
            'id': 'seq_' + datetime.now().strftime('%Y%m%d'),
            'status': 'Ready',
            'started': 'Not started',
            'total': 0,
            'next_action': 'No scheduled actions'
        }

    def load_activity(self) -> None:
        """Load recent activity from centralized logs."""
        self.activity_text.delete("1.0", "end")

        try:
            # Read centralized log file
            logs_folder = self.gui_config.get_logs_path()
            log_file = logs_folder / 'sequence.log'

            if log_file.exists():
                # Read last 20 lines
                with open(log_file, 'r') as f:
                    lines = f.readlines()
                    recent_lines = lines[-20:] if len(lines) > 20 else lines

                # Display in reverse order (newest first)
                for line in reversed(recent_lines):
                    self.activity_text.insert("1.0", line)
            else:
                self.activity_text.insert("1.0", "No activity logged yet.\n")

        except Exception as e:
            self.activity_text.insert("1.0", f"Error loading activity: {e}\n")

        # Disable editing
        self.activity_text.configure(state="disabled")

    def refresh_data(self) -> None:
        """Refresh all dashboard data."""
        # Update metrics
        metrics = self.get_metrics()
        self.pending_card.update_value(str(metrics['pending']))
        self.sent_card.update_value(str(metrics['sent']))
        self.replied_card.update_value(str(metrics['replied']))
        self.rate_card.update_all(f"{metrics['reply_rate']}%", metrics['reply_rate'] / 100)

        # Reload activity
        self.load_activity()

        # Update status bar
        self.app.update_status_bar(
            message=f"Dashboard refreshed at {datetime.now().strftime('%H:%M:%S')}"
        )

    def schedule_refresh(self, interval_ms: int) -> None:
        """Schedule automatic refresh.

        Args:
            interval_ms: Refresh interval in milliseconds
        """
        self.refresh_data()
        self.after(interval_ms, lambda: self.schedule_refresh(interval_ms))

    def on_start_sequence(self) -> None:
        """Handle Start Sequence button click."""
        if self.gui_config.get('behavior.confirm_before_send', True):
            dialog = ConfirmationDialog(
                self,
                "Start Sequence",
                "Start sending initial emails to all pending contacts?",
                confirm_text="Start",
                cancel_text="Cancel"
            )
            if not dialog.get_result():
                return

        # TODO: Call sequence engine to start sequence
        InfoDialog.show(
            self,
            "Start Sequence",
            "Sequence functionality will be connected to the backend engine.\n\n"
            "For now, this is a UI demonstration."
        )

    def on_check_replies(self) -> None:
        """Handle Check Replies button click."""
        # TODO: Call sequence engine to check replies
        InfoDialog.show(
            self,
            "Check Replies",
            "Checking inbox for replies...\n\n"
            "This will be connected to the Outlook integration."
        )

    def on_send_followups(self) -> None:
        """Handle Send Follow-ups button click."""
        if self.gui_config.get('behavior.confirm_before_send', True):
            dialog = ConfirmationDialog(
                self,
                "Send Follow-ups",
                "Send follow-up emails to all eligible contacts?",
                confirm_text="Send",
                cancel_text="Cancel"
            )
            if not dialog.get_result():
                return

        # TODO: Call sequence engine to send follow-ups
        InfoDialog.show(
            self,
            "Send Follow-ups",
            "Follow-up functionality will be connected to the backend engine.\n\n"
            "For now, this is a UI demonstration."
        )
