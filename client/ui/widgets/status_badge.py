"""Status badge widget for displaying colored status indicators."""
import tkinter as tk
from typing import Optional, Dict
import ttkbootstrap as ttk
from ttkbootstrap.constants import *


class StatusBadge(ttk.Label):
    """A colored badge for displaying status."""

    # Status to style mapping
    STATUS_STYLES = {
        # Campaign statuses
        "Active": ("success", "\u25CF"),
        "Paused": ("warning", "\u25D0"),
        "Draft": ("secondary", "\u25CB"),
        "Completed": ("info", "\u2714"),
        "Cancelled": ("danger", "\u2718"),

        # Contact statuses
        "Pending": ("secondary", "\u25CB"),
        "InProgress": ("primary", "\u25D0"),
        "Replied": ("success", "\u2709"),
        "Unsubscribed": ("warning", "\u2717"),
        "Bounced": ("danger", "\u26A0"),
        "Skipped": ("secondary", "\u2192"),

        # General statuses
        "Success": ("success", "\u2714"),
        "Error": ("danger", "\u2718"),
        "Warning": ("warning", "\u26A0"),
        "Info": ("info", "\u2139"),

        # Connection statuses
        "Connected": ("success", "\u25CF"),
        "Disconnected": ("danger", "\u25CB"),
        "Connecting": ("warning", "\u25D0"),
    }

    def __init__(
        self,
        parent,
        status: str = "",
        show_icon: bool = True,
        custom_styles: Optional[Dict[str, tuple]] = None,
        **kwargs
    ):
        """
        Initialize StatusBadge.

        Args:
            parent: Parent widget
            status: Initial status text
            show_icon: Whether to show status icon
            custom_styles: Custom status -> (style, icon) mapping
        """
        self.show_icon = show_icon
        self.custom_styles = custom_styles or {}

        super().__init__(parent, **kwargs)

        if status:
            self.set_status(status)

    def set_status(self, status: str) -> None:
        """Set the badge status."""
        # Get style and icon
        style_info = self.custom_styles.get(status) or self.STATUS_STYLES.get(status)

        if style_info:
            style, icon = style_info
            text = f"{icon} {status}" if self.show_icon else status
            self.configure(
                text=text,
                bootstyle=style,
                padding=(8, 2)
            )
        else:
            # Default styling for unknown status
            self.configure(
                text=status,
                bootstyle="secondary",
                padding=(8, 2)
            )

    def get_status(self) -> str:
        """Get current status text (without icon)."""
        text = self.cget("text")
        # Remove icon if present
        for status_info in list(self.STATUS_STYLES.values()) + list(self.custom_styles.values()):
            icon = status_info[1]
            if text.startswith(icon):
                return text[len(icon):].strip()
        return text


class StatusBadgeFrame(ttk.Frame):
    """A frame containing a label and status badge."""

    def __init__(
        self,
        parent,
        label: str = "Status:",
        status: str = "",
        **kwargs
    ):
        super().__init__(parent, **kwargs)

        self.label = ttk.Label(
            self,
            text=label,
            font=("Segoe UI", 9)
        )
        self.label.pack(side=LEFT, padx=(0, 5))

        self.badge = StatusBadge(self, status=status)
        self.badge.pack(side=LEFT)

    def set_status(self, status: str) -> None:
        """Set the badge status."""
        self.badge.set_status(status)

    def get_status(self) -> str:
        """Get current status."""
        return self.badge.get_status()
