"""Progress/KPI card widget for Lead Generator Standalone."""

import tkinter as tk
from tkinter import ttk
from typing import Optional, Union

from ui.theme import COLORS, FONTS


class ProgressCard(ttk.Frame):
    """A card widget displaying a KPI value with optional progress."""

    def __init__(
        self,
        parent,
        title: str,
        value: Union[str, int, float] = "0",
        subtitle: Optional[str] = None,
        progress: Optional[float] = None,
        color: str = "primary",
        **kwargs
    ):
        """
        Initialize ProgressCard.

        Args:
            parent: Parent widget
            title: Card title
            value: Main value to display
            subtitle: Optional subtitle/description
            progress: Optional progress value (0-100)
            color: Color scheme ('primary', 'success', 'warning', 'danger', 'info')
        """
        super().__init__(parent, **kwargs)

        self._title = title
        self._value = value
        self._subtitle = subtitle
        self._progress = progress
        self._color = color

        self._create_widgets()

    def _create_widgets(self) -> None:
        """Create card widgets."""
        self.configure(padding=15)

        # Configure grid
        self.grid_columnconfigure(0, weight=1)

        # Title
        self.title_label = ttk.Label(
            self,
            text=self._title,
            font=FONTS['small'],
            foreground=COLORS['secondary']
        )
        self.title_label.grid(row=0, column=0, sticky='w')

        # Value
        self.value_label = ttk.Label(
            self,
            text=str(self._value),
            font=('Segoe UI', 24, 'bold'),
            foreground=COLORS.get(self._color, COLORS['primary'])
        )
        self.value_label.grid(row=1, column=0, sticky='w', pady=(5, 0))

        # Subtitle
        if self._subtitle:
            self.subtitle_label = ttk.Label(
                self,
                text=self._subtitle,
                font=FONTS['small'],
                foreground=COLORS['secondary']
            )
            self.subtitle_label.grid(row=2, column=0, sticky='w', pady=(2, 0))

        # Progress bar
        if self._progress is not None:
            self.progress_bar = ttk.Progressbar(
                self,
                length=200,
                mode='determinate',
                value=self._progress
            )
            self.progress_bar.grid(row=3, column=0, sticky='ew', pady=(10, 0))

    def set_value(self, value: Union[str, int, float]) -> None:
        """Update the main value."""
        self._value = value
        self.value_label.configure(text=str(value))

    def set_subtitle(self, subtitle: str) -> None:
        """Update the subtitle."""
        if hasattr(self, 'subtitle_label'):
            self.subtitle_label.configure(text=subtitle)
        else:
            self._subtitle = subtitle
            self.subtitle_label = ttk.Label(
                self,
                text=subtitle,
                font=FONTS['small'],
                foreground=COLORS['secondary']
            )
            self.subtitle_label.grid(row=2, column=0, sticky='w', pady=(2, 0))

    def set_progress(self, progress: float) -> None:
        """Update the progress value."""
        if hasattr(self, 'progress_bar'):
            self._progress = progress
            self.progress_bar['value'] = progress

    def get_value(self) -> Union[str, int, float]:
        """Get current value."""
        return self._value
