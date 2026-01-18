"""Progress Card Component

Metric display card with icon, value, label, and optional progress bar.
"""

import customtkinter as ctk
from typing import Optional


class ProgressCard(ctk.CTkFrame):
    """Metric card widget for dashboard display."""

    def __init__(
        self,
        master,
        title: str,
        value: str = "0",
        icon: str = "●",
        show_progress: bool = False,
        progress_value: float = 0.0,
        **kwargs
    ):
        """Initialize progress card.

        Args:
            master: Parent widget
            title: Card title/label
            value: Main value to display
            icon: Icon/emoji to show
            show_progress: Whether to show progress bar
            progress_value: Progress value (0.0 to 1.0)
            **kwargs: Additional frame arguments
        """
        # Set default styling
        kwargs.setdefault('corner_radius', 10)
        kwargs.setdefault('border_width', 2)
        kwargs.setdefault('border_color', '#3B82F6')

        super().__init__(master, **kwargs)

        self.title = title
        self.show_progress = show_progress

        # Configure grid
        self.grid_columnconfigure(0, weight=1)

        # Icon label
        self.icon_label = ctk.CTkLabel(
            self,
            text=icon,
            font=("Arial", 24)
        )
        self.icon_label.grid(row=0, column=0, pady=(15, 5))

        # Value label
        self.value_label = ctk.CTkLabel(
            self,
            text=value,
            font=("Arial Bold", 32)
        )
        self.value_label.grid(row=1, column=0, pady=(0, 5))

        # Title label
        self.title_label = ctk.CTkLabel(
            self,
            text=title.upper(),
            font=("Arial", 11),
            text_color="gray"
        )
        self.title_label.grid(row=2, column=0, pady=(0, 10))

        # Progress bar (optional)
        if show_progress:
            self.progress_bar = ctk.CTkProgressBar(
                self,
                width=100,
                height=8
            )
            self.progress_bar.set(progress_value)
            self.progress_bar.grid(row=3, column=0, pady=(0, 15), padx=20, sticky="ew")
        else:
            self.progress_bar = None

    def update_value(self, value: str) -> None:
        """Update the main value display.

        Args:
            value: New value to display
        """
        self.value_label.configure(text=value)

    def update_progress(self, progress: float) -> None:
        """Update progress bar value.

        Args:
            progress: Progress value (0.0 to 1.0)
        """
        if self.progress_bar:
            self.progress_bar.set(max(0.0, min(1.0, progress)))

    def update_all(self, value: str, progress: Optional[float] = None) -> None:
        """Update both value and progress.

        Args:
            value: New value to display
            progress: New progress value (0.0 to 1.0)
        """
        self.update_value(value)
        if progress is not None and self.progress_bar:
            self.update_progress(progress)

    def set_border_color(self, color: str) -> None:
        """Change border color.

        Args:
            color: Hex color string
        """
        self.configure(border_color=color)


class MetricCard(ctk.CTkFrame):
    """Simple metric card without progress bar."""

    def __init__(
        self,
        master,
        title: str,
        value: str = "0",
        subtitle: str = "",
        **kwargs
    ):
        """Initialize metric card.

        Args:
            master: Parent widget
            title: Card title
            value: Main value
            subtitle: Optional subtitle text
            **kwargs: Additional frame arguments
        """
        kwargs.setdefault('corner_radius', 8)
        kwargs.setdefault('fg_color', ("#E5E7EB", "#374151"))

        super().__init__(master, **kwargs)

        # Title
        self.title_label = ctk.CTkLabel(
            self,
            text=title,
            font=("Arial", 11),
            text_color="gray"
        )
        self.title_label.pack(pady=(10, 5))

        # Value
        self.value_label = ctk.CTkLabel(
            self,
            text=value,
            font=("Arial Bold", 28)
        )
        self.value_label.pack(pady=5)

        # Subtitle (optional)
        if subtitle:
            self.subtitle_label = ctk.CTkLabel(
                self,
                text=subtitle,
                font=("Arial", 10),
                text_color="gray"
            )
            self.subtitle_label.pack(pady=(0, 10))
        else:
            self.subtitle_label = None

    def update_value(self, value: str, subtitle: str = None) -> None:
        """Update card value and optional subtitle.

        Args:
            value: New value
            subtitle: New subtitle (optional)
        """
        self.value_label.configure(text=value)
        if subtitle and self.subtitle_label:
            self.subtitle_label.configure(text=subtitle)
