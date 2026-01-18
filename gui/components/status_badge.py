"""Status Badge Component

Visual indicator for contact status with color coding.
"""

import customtkinter as ctk
from typing import Optional


class StatusBadge(ctk.CTkFrame):
    """Color-coded status indicator widget."""

    STATUS_COLORS = {
        'pending': ('#808080', '○'),      # Gray circle
        'sent': ('#3B82F6', '●'),         # Blue dot
        'followup_1': ('#F97316', '●'),   # Orange dot
        'followup_2': ('#F97316', '●'),   # Orange dot
        'followup_3': ('#F97316', '●'),   # Orange dot
        'replied': ('#10B981', '✓'),      # Green checkmark
        'bounced': ('#EF4444', '✗'),      # Red X
        'opted_out': ('#000000', '⛔'),    # Black stop sign
        'completed': ('#8B5CF6', '◆'),    # Purple diamond
        'paused': ('#FBBF24', '⏸'),      # Yellow pause
        'error': ('#DC2626', '⚠')         # Red warning
    }

    def __init__(
        self,
        master,
        status: str = 'pending',
        show_text: bool = True,
        **kwargs
    ):
        """Initialize status badge.

        Args:
            master: Parent widget
            status: Status value (pending, sent, replied, etc.)
            show_text: Whether to show status text label
            **kwargs: Additional frame arguments
        """
        super().__init__(master, fg_color="transparent", **kwargs)

        self.status = status
        self.show_text = show_text

        # Create icon label
        self.icon_label = ctk.CTkLabel(
            self,
            text="",
            font=("Arial", 14),
            width=20
        )
        self.icon_label.pack(side="left", padx=(0, 5))

        # Create text label if needed
        if show_text:
            self.text_label = ctk.CTkLabel(
                self,
                text="",
                font=("Arial", 11)
            )
            self.text_label.pack(side="left")

        self.update_status(status)

    def update_status(self, status: str) -> None:
        """Update badge to show new status.

        Args:
            status: New status value
        """
        self.status = status

        # Get color and icon
        color, icon = self.STATUS_COLORS.get(
            status,
            self.STATUS_COLORS['pending']
        )

        # Update icon
        self.icon_label.configure(text=icon, text_color=color)

        # Update text if shown
        if self.show_text:
            # Format status text (e.g., 'followup_1' -> 'Follow-up 1')
            display_text = status.replace('_', ' ').title()
            if 'Followup' in display_text:
                display_text = display_text.replace('Followup', 'Follow-up')

            self.text_label.configure(text=display_text)

    def get_status(self) -> str:
        """Get current status value.

        Returns:
            Current status string
        """
        return self.status


class StatusIndicator(ctk.CTkLabel):
    """Simple status indicator (just icon, no frame)."""

    def __init__(self, master, status: str = 'pending', **kwargs):
        """Initialize status indicator.

        Args:
            master: Parent widget
            status: Initial status
            **kwargs: Additional label arguments
        """
        super().__init__(master, text="", font=("Arial", 12), **kwargs)
        self.update_status(status)

    def update_status(self, status: str) -> None:
        """Update indicator icon and color.

        Args:
            status: New status value
        """
        color, icon = StatusBadge.STATUS_COLORS.get(
            status,
            StatusBadge.STATUS_COLORS['pending']
        )
        self.configure(text=icon, text_color=color)
