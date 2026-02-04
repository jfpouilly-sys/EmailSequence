"""Status badge widget for Lead Generator Standalone."""

import tkinter as tk
from tkinter import ttk
from typing import Optional

from ui.theme import STATUS_COLORS


class StatusBadge(ttk.Frame):
    """A colored badge showing status."""

    def __init__(
        self,
        parent,
        status: str = "",
        size: str = "normal",
        **kwargs
    ):
        """
        Initialize StatusBadge.

        Args:
            parent: Parent widget
            status: Status text to display
            size: Badge size ('small', 'normal', 'large')
        """
        super().__init__(parent, **kwargs)

        self._status = status
        self._size = size

        self._create_widget()

    def _create_widget(self) -> None:
        """Create the badge widget."""
        # Determine style based on status
        style = STATUS_COLORS.get(self._status, 'secondary')

        # Font size based on badge size
        font_sizes = {'small': 8, 'normal': 9, 'large': 11}
        font_size = font_sizes.get(self._size, 9)

        # Padding based on size
        paddings = {'small': (3, 1), 'normal': (6, 2), 'large': (10, 4)}
        padx, pady = paddings.get(self._size, (6, 2))

        # Create label with style
        self.label = ttk.Label(
            self,
            text=self._status,
            style=f'{style}.TLabel',
            padding=(padx, pady),
            font=('Segoe UI', font_size)
        )
        self.label.pack()

    def set_status(self, status: str) -> None:
        """Update the status."""
        self._status = status
        self.label.configure(text=status)

        # Update style
        style = STATUS_COLORS.get(status, 'secondary')
        self.label.configure(style=f'{style}.TLabel')

    def get_status(self) -> str:
        """Get current status."""
        return self._status
