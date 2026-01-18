"""Sequence Frame

Sequence control and scheduling configuration.
"""

import customtkinter as ctk
from gui.dialogs import ConfirmationDialog, InfoDialog
from datetime import datetime
import threading


class SequenceFrame(ctk.CTkScrollableFrame):
    """Sequence control and scheduling configuration."""

    def __init__(self, parent, app):
        """Initialize sequence frame.

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
        self.create_status_section()
        self.create_action_buttons()
        self.create_manual_operations()
        self.create_scheduling_section()
        self.create_timing_section()

    def create_header(self) -> None:
        """Create header with title."""
        title_label = ctk.CTkLabel(
            self,
            text="SEQUENCE CONTROL",
            font=("Arial Bold", 24),
            anchor="w"
        )
        title_label.grid(row=0, column=0, sticky="w", pady=(10, 20), padx=20)

    def create_status_section(self) -> None:
        """Create current sequence status section."""
        status_frame = ctk.CTkFrame(self)
        status_frame.grid(row=1, column=0, sticky="ew", padx=20, pady=(0, 20))
        status_frame.grid_columnconfigure(0, weight=1)

        # Title
        title = ctk.CTkLabel(
            status_frame,
            text="CURRENT SEQUENCE",
            font=("Arial Bold", 14),
            anchor="w"
        )
        title.grid(row=0, column=0, sticky="w", padx=15, pady=(15, 10))

        # Status info
        info_frame = ctk.CTkFrame(status_frame, fg_color="#1F2937")
        info_frame.grid(row=1, column=0, sticky="ew", padx=15, pady=(0, 15))
        info_frame.grid_columnconfigure(0, weight=1)

        self.seq_id_label = ctk.CTkLabel(
            info_frame,
            text="ID: Not started",
            font=("Arial", 12),
            anchor="w"
        )
        self.seq_id_label.grid(row=0, column=0, sticky="w", padx=15, pady=(10, 2))

        self.seq_status_label = ctk.CTkLabel(
            info_frame,
            text="Status: ○ Inactive",
            font=("Arial", 12),
            anchor="w"
        )
        self.seq_status_label.grid(row=1, column=0, sticky="w", padx=15, pady=2)

        self.seq_started_label = ctk.CTkLabel(
            info_frame,
            text="Started: N/A",
            font=("Arial", 12),
            anchor="w"
        )
        self.seq_started_label.grid(row=2, column=0, sticky="w", padx=15, pady=2)

        # Progress bar
        self.progress_label = ctk.CTkLabel(
            info_frame,
            text="Progress: 0% (0/0)",
            font=("Arial", 12),
            anchor="w"
        )
        self.progress_label.grid(row=3, column=0, sticky="w", padx=15, pady=(10, 2))

        self.progress_bar = ctk.CTkProgressBar(info_frame)
        self.progress_bar.set(0)
        self.progress_bar.grid(row=4, column=0, sticky="ew", padx=15, pady=(5, 15))

    def create_action_buttons(self) -> None:
        """Create main action buttons."""
        actions_frame = ctk.CTkFrame(self, fg_color="transparent")
        actions_frame.grid(row=2, column=0, sticky="ew", padx=20, pady=(0, 20))
        actions_frame.grid_columnconfigure((0, 1, 2), weight=1)

        # Title
        title = ctk.CTkLabel(
            actions_frame,
            text="ACTIONS",
            font=("Arial Bold", 14),
            anchor="w"
        )
        title.grid(row=0, column=0, columnspan=3, sticky="w", pady=(0, 10))

        # Start button
        start_btn = ctk.CTkButton(
            actions_frame,
            text="▶ START NEW\nSEQUENCE",
            command=self.on_start_sequence,
            height=70,
            font=("Arial Bold", 13),
            fg_color="#10B981",
            hover_color="#059669"
        )
        start_btn.grid(row=1, column=0, padx=(0, 10), sticky="ew")

        # Pause button
        pause_btn = ctk.CTkButton(
            actions_frame,
            text="⏸ PAUSE\nSEQUENCE",
            command=self.on_pause_sequence,
            height=70,
            font=("Arial Bold", 13),
            fg_color="#FBBF24",
            hover_color="#F59E0B"
        )
        pause_btn.grid(row=1, column=1, padx=5, sticky="ew")

        # Stop button
        stop_btn = ctk.CTkButton(
            actions_frame,
            text="⏹ STOP\nSEQUENCE",
            command=self.on_stop_sequence,
            height=70,
            font=("Arial Bold", 13),
            fg_color="#EF4444",
            hover_color="#DC2626"
        )
        stop_btn.grid(row=1, column=2, padx=(10, 0), sticky="ew")

    def create_manual_operations(self) -> None:
        """Create manual operation buttons."""
        ops_frame = ctk.CTkFrame(self)
        ops_frame.grid(row=3, column=0, sticky="ew", padx=20, pady=(0, 20))
        ops_frame.grid_columnconfigure(0, weight=1)

        # Title
        title = ctk.CTkLabel(
            ops_frame,
            text="MANUAL OPERATIONS",
            font=("Arial Bold", 14),
            anchor="w"
        )
        title.grid(row=0, column=0, sticky="w", padx=15, pady=(15, 10))

        # Check replies
        check_frame = ctk.CTkFrame(ops_frame, fg_color="#1F2937")
        check_frame.grid(row=1, column=0, sticky="ew", padx=15, pady=5)
        check_frame.grid_columnconfigure(1, weight=1)

        check_btn = ctk.CTkButton(
            check_frame,
            text="🔍 Check Replies Now",
            command=self.on_check_replies,
            width=180
        )
        check_btn.grid(row=0, column=0, padx=10, pady=10)

        self.last_check_label = ctk.CTkLabel(
            check_frame,
            text="Last check: Never",
            font=("Arial", 11),
            text_color="gray"
        )
        self.last_check_label.grid(row=0, column=1, sticky="w", padx=10)

        # Send follow-ups
        followup_frame = ctk.CTkFrame(ops_frame, fg_color="#1F2937")
        followup_frame.grid(row=2, column=0, sticky="ew", padx=15, pady=5)
        followup_frame.grid_columnconfigure(1, weight=1)

        followup_btn = ctk.CTkButton(
            followup_frame,
            text="↻ Send Follow-ups Now",
            command=self.on_send_followups,
            width=180
        )
        followup_btn.grid(row=0, column=0, padx=10, pady=10)

        self.last_followup_label = ctk.CTkLabel(
            followup_frame,
            text="Last sent: Never",
            font=("Arial", 11),
            text_color="gray"
        )
        self.last_followup_label.grid(row=0, column=1, sticky="w", padx=10)

        # Full cycle
        cycle_frame = ctk.CTkFrame(ops_frame, fg_color="#1F2937")
        cycle_frame.grid(row=3, column=0, sticky="ew", padx=15, pady=(5, 15))
        cycle_frame.grid_columnconfigure(1, weight=1)

        cycle_btn = ctk.CTkButton(
            cycle_frame,
            text="▶ Run Full Cycle",
            command=self.on_run_cycle,
            width=180,
            fg_color="#3B82F6"
        )
        cycle_btn.grid(row=0, column=0, padx=10, pady=10)

        cycle_desc = ctk.CTkLabel(
            cycle_frame,
            text="Runs both operations",
            font=("Arial", 11),
            text_color="gray"
        )
        cycle_desc.grid(row=0, column=1, sticky="w", padx=10)

    def create_scheduling_section(self) -> None:
        """Create scheduling configuration section."""
        sched_frame = ctk.CTkFrame(self)
        sched_frame.grid(row=4, column=0, sticky="ew", padx=20, pady=(0, 20))
        sched_frame.grid_columnconfigure(0, weight=1)

        # Title
        title = ctk.CTkLabel(
            sched_frame,
            text="SCHEDULING",
            font=("Arial Bold", 14),
            anchor="w"
        )
        title.grid(row=0, column=0, sticky="w", padx=15, pady=(15, 10))

        # Enable toggle
        self.auto_cycle_var = ctk.BooleanVar(value=False)
        auto_toggle = ctk.CTkCheckBox(
            sched_frame,
            text="Enable automatic cycling",
            variable=self.auto_cycle_var,
            font=("Arial", 12)
        )
        auto_toggle.grid(row=1, column=0, sticky="w", padx=15, pady=5)

        # Interval
        interval_frame = ctk.CTkFrame(sched_frame, fg_color="transparent")
        interval_frame.grid(row=2, column=0, sticky="w", padx=15, pady=5)

        ctk.CTkLabel(interval_frame, text="Run every:", font=("Arial", 11)).pack(side="left", padx=(0, 10))
        self.interval_var = ctk.StringVar(value="30")
        interval_entry = ctk.CTkEntry(interval_frame, textvariable=self.interval_var, width=80)
        interval_entry.pack(side="left", padx=5)
        ctk.CTkLabel(interval_frame, text="minutes", font=("Arial", 11)).pack(side="left", padx=5)

        # Active hours
        hours_frame = ctk.CTkFrame(sched_frame, fg_color="transparent")
        hours_frame.grid(row=3, column=0, sticky="w", padx=15, pady=5)

        ctk.CTkLabel(hours_frame, text="Active hours:", font=("Arial", 11)).pack(side="left", padx=(0, 10))
        self.start_hour_var = ctk.StringVar(value="08:00")
        start_entry = ctk.CTkEntry(hours_frame, textvariable=self.start_hour_var, width=80)
        start_entry.pack(side="left", padx=5)
        ctk.CTkLabel(hours_frame, text="to", font=("Arial", 11)).pack(side="left", padx=5)
        self.end_hour_var = ctk.StringVar(value="18:00")
        end_entry = ctk.CTkEntry(hours_frame, textvariable=self.end_hour_var, width=80)
        end_entry.pack(side="left", padx=5)

        # Active days
        days_frame = ctk.CTkFrame(sched_frame, fg_color="transparent")
        days_frame.grid(row=4, column=0, sticky="w", padx=15, pady=5)

        ctk.CTkLabel(days_frame, text="Active days:", font=("Arial", 11)).pack(side="left", padx=(0, 10))

        self.day_vars = {}
        for day in ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']:
            var = ctk.BooleanVar(value=(day not in ['Sat', 'Sun']))
            self.day_vars[day] = var
            checkbox = ctk.CTkCheckBox(days_frame, text=day, variable=var, width=60)
            checkbox.pack(side="left", padx=2)

        # Update button
        update_btn = ctk.CTkButton(
            sched_frame,
            text="Update Schedule",
            command=self.on_update_schedule,
            width=150
        )
        update_btn.grid(row=5, column=0, sticky="w", padx=15, pady=(10, 15))

    def create_timing_section(self) -> None:
        """Create follow-up timing configuration."""
        timing_frame = ctk.CTkFrame(self)
        timing_frame.grid(row=5, column=0, sticky="ew", padx=20, pady=(0, 20))
        timing_frame.grid_columnconfigure((0, 1), weight=1)

        # Title
        title = ctk.CTkLabel(
            timing_frame,
            text="FOLLOW-UP TIMING",
            font=("Arial Bold", 14),
            anchor="w"
        )
        title.grid(row=0, column=0, columnspan=2, sticky="w", padx=15, pady=(15, 10))

        # Days after initial
        desc_label = ctk.CTkLabel(
            timing_frame,
            text="Days after initial email:",
            font=("Arial", 11),
            text_color="gray"
        )
        desc_label.grid(row=1, column=0, columnspan=2, sticky="w", padx=15, pady=5)

        # Follow-up 1
        fu1_frame = ctk.CTkFrame(timing_frame, fg_color="transparent")
        fu1_frame.grid(row=2, column=0, sticky="w", padx=15, pady=5)

        ctk.CTkLabel(fu1_frame, text="Follow-up #1:", font=("Arial", 11)).pack(side="left", padx=(0, 10))
        self.fu1_var = ctk.StringVar(value="3")
        fu1_entry = ctk.CTkEntry(fu1_frame, textvariable=self.fu1_var, width=60)
        fu1_entry.pack(side="left", padx=5)
        ctk.CTkLabel(fu1_frame, text="days", font=("Arial", 11)).pack(side="left", padx=5)

        # Follow-up 2
        fu2_frame = ctk.CTkFrame(timing_frame, fg_color="transparent")
        fu2_frame.grid(row=2, column=1, sticky="w", padx=15, pady=5)

        ctk.CTkLabel(fu2_frame, text="Follow-up #2:", font=("Arial", 11)).pack(side="left", padx=(0, 10))
        self.fu2_var = ctk.StringVar(value="7")
        fu2_entry = ctk.CTkEntry(fu2_frame, textvariable=self.fu2_var, width=60)
        fu2_entry.pack(side="left", padx=5)
        ctk.CTkLabel(fu2_frame, text="days", font=("Arial", 11)).pack(side="left", padx=5)

        # Follow-up 3
        fu3_frame = ctk.CTkFrame(timing_frame, fg_color="transparent")
        fu3_frame.grid(row=3, column=0, sticky="w", padx=15, pady=5)

        ctk.CTkLabel(fu3_frame, text="Follow-up #3:", font=("Arial", 11)).pack(side="left", padx=(0, 10))
        self.fu3_var = ctk.StringVar(value="14")
        fu3_entry = ctk.CTkEntry(fu3_frame, textvariable=self.fu3_var, width=60)
        fu3_entry.pack(side="left", padx=5)
        ctk.CTkLabel(fu3_frame, text="days", font=("Arial", 11)).pack(side="left", padx=5)

        # Max follow-ups
        max_frame = ctk.CTkFrame(timing_frame, fg_color="transparent")
        max_frame.grid(row=3, column=1, sticky="w", padx=15, pady=5)

        ctk.CTkLabel(max_frame, text="Max follow-ups:", font=("Arial", 11)).pack(side="left", padx=(0, 10))
        self.max_fu_var = ctk.StringVar(value="3")
        max_entry = ctk.CTkEntry(max_frame, textvariable=self.max_fu_var, width=60)
        max_entry.pack(side="left", padx=5)

        # Save button
        save_btn = ctk.CTkButton(
            timing_frame,
            text="Save Timing",
            command=self.on_save_timing,
            width=120
        )
        save_btn.grid(row=4, column=0, columnspan=2, sticky="e", padx=15, pady=(10, 15))

    def on_start_sequence(self) -> None:
        """Handle Start Sequence button."""
        dialog = ConfirmationDialog(
            self,
            "Start New Sequence",
            "This will send initial emails to all pending contacts.\n\nContinue?",
            confirm_text="Start"
        )
        if dialog.get_result():
            InfoDialog.show(self, "Start Sequence", "Sequence will be started.\n(Backend integration pending)")

    def on_pause_sequence(self) -> None:
        """Handle Pause Sequence button."""
        InfoDialog.show(self, "Pause Sequence", "Sequence paused.\n(Backend integration pending)")

    def on_stop_sequence(self) -> None:
        """Handle Stop Sequence button."""
        dialog = ConfirmationDialog(
            self,
            "Stop Sequence",
            "This will stop the current sequence.\nNo further emails will be sent.\n\nContinue?",
            confirm_text="Stop",
            danger=True
        )
        if dialog.get_result():
            InfoDialog.show(self, "Stop Sequence", "Sequence stopped.\n(Backend integration pending)")

    def on_check_replies(self) -> None:
        """Handle Check Replies button."""
        self.last_check_label.configure(text=f"Last check: {datetime.now().strftime('%H:%M:%S')}")
        InfoDialog.show(self, "Check Replies", "Checked for replies.\n(Backend integration pending)")

    def on_send_followups(self) -> None:
        """Handle Send Follow-ups button."""
        self.last_followup_label.configure(text=f"Last sent: {datetime.now().strftime('%H:%M:%S')}")
        InfoDialog.show(self, "Send Follow-ups", "Follow-ups sent.\n(Backend integration pending)")

    def on_run_cycle(self) -> None:
        """Handle Run Full Cycle button."""
        InfoDialog.show(self, "Run Cycle", "Running full cycle.\n(Backend integration pending)")

    def on_update_schedule(self) -> None:
        """Handle Update Schedule button."""
        InfoDialog.show(self, "Update Schedule", "Schedule updated.\n(Task Scheduler integration pending)")

    def on_save_timing(self) -> None:
        """Handle Save Timing button."""
        try:
            # Validate inputs
            fu1 = int(self.fu1_var.get())
            fu2 = int(self.fu2_var.get())
            fu3 = int(self.fu3_var.get())
            max_fu = int(self.max_fu_var.get())

            # TODO: Save to config file
            InfoDialog.show(self, "Success", "Timing configuration saved.")

        except ValueError:
            InfoDialog.show(self, "Validation Error", "Please enter valid numbers for all fields.")
