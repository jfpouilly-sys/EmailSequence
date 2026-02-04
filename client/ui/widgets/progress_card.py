"""Progress and KPI card widgets."""
import tkinter as tk
from typing import Optional, Union
import ttkbootstrap as ttk
from ttkbootstrap.constants import *


class ProgressCard(ttk.Frame):
    """A card showing progress with value and percentage."""

    def __init__(
        self,
        parent,
        title: str = "",
        value: int = 0,
        max_value: int = 100,
        unit: str = "",
        show_percentage: bool = True,
        color: str = "primary",
        **kwargs
    ):
        super().__init__(parent, padding=15, bootstyle="light", **kwargs)

        self.title = title
        self.max_value = max_value
        self.unit = unit
        self.show_percentage = show_percentage
        self.color = color

        self._create_widgets()
        self.set_value(value)

    def _create_widgets(self) -> None:
        """Create card widgets."""
        # Title
        self.title_label = ttk.Label(
            self,
            text=self.title,
            font=("Segoe UI", 10),
            bootstyle="secondary"
        )
        self.title_label.pack(anchor=W)

        # Value
        self.value_label = ttk.Label(
            self,
            text="0",
            font=("Segoe UI", 24, "bold")
        )
        self.value_label.pack(anchor=W, pady=(5, 10))

        # Progress bar
        self.progress = ttk.Progressbar(
            self,
            length=200,
            mode="determinate",
            bootstyle=self.color
        )
        self.progress.pack(fill=X)

        # Percentage label
        if self.show_percentage:
            self.percent_label = ttk.Label(
                self,
                text="0%",
                font=("Segoe UI", 9),
                bootstyle="secondary"
            )
            self.percent_label.pack(anchor=E, pady=(5, 0))

    def set_value(self, value: int) -> None:
        """Set the current value."""
        # Update value label
        if self.unit:
            self.value_label.configure(text=f"{value:,} {self.unit}")
        else:
            self.value_label.configure(text=f"{value:,}")

        # Update progress bar
        if self.max_value > 0:
            percentage = min(100, (value / self.max_value) * 100)
            self.progress.configure(value=percentage)

            if self.show_percentage:
                self.percent_label.configure(text=f"{percentage:.1f}%")

    def set_max(self, max_value: int) -> None:
        """Set the maximum value."""
        self.max_value = max_value


class KPICard(ttk.Frame):
    """A key performance indicator card."""

    def __init__(
        self,
        parent,
        title: str = "",
        value: Union[int, float, str] = 0,
        subtitle: str = "",
        icon: str = "",
        color: str = "primary",
        format_type: str = "number",  # number, percentage, currency
        **kwargs
    ):
        super().__init__(parent, padding=20, bootstyle="light", **kwargs)

        self.format_type = format_type
        self.color = color

        self._create_widgets(title, subtitle, icon)
        self.set_value(value)

    def _create_widgets(self, title: str, subtitle: str, icon: str) -> None:
        """Create card widgets."""
        # Header with icon
        header = ttk.Frame(self)
        header.pack(fill=X)

        if icon:
            icon_label = ttk.Label(
                header,
                text=icon,
                font=("Segoe UI", 20),
                bootstyle=self.color
            )
            icon_label.pack(side=LEFT, padx=(0, 10))

        # Title
        self.title_label = ttk.Label(
            header,
            text=title,
            font=("Segoe UI", 11),
            bootstyle="secondary"
        )
        self.title_label.pack(side=LEFT, anchor=S)

        # Value
        self.value_label = ttk.Label(
            self,
            text="0",
            font=("Segoe UI", 32, "bold"),
            bootstyle=self.color
        )
        self.value_label.pack(anchor=W, pady=(10, 5))

        # Subtitle
        if subtitle:
            self.subtitle_label = ttk.Label(
                self,
                text=subtitle,
                font=("Segoe UI", 9),
                bootstyle="secondary"
            )
            self.subtitle_label.pack(anchor=W)

    def set_value(self, value: Union[int, float, str]) -> None:
        """Set the KPI value."""
        if isinstance(value, str):
            formatted = value
        elif self.format_type == "percentage":
            formatted = f"{value:.1f}%"
        elif self.format_type == "currency":
            formatted = f"${value:,.2f}"
        elif isinstance(value, float):
            formatted = f"{value:,.1f}"
        else:
            formatted = f"{value:,}"

        self.value_label.configure(text=formatted)

    def set_subtitle(self, text: str) -> None:
        """Update subtitle text."""
        if hasattr(self, 'subtitle_label'):
            self.subtitle_label.configure(text=text)


class KPICardGrid(ttk.Frame):
    """A grid of KPI cards."""

    def __init__(self, parent, columns: int = 4, **kwargs):
        super().__init__(parent, **kwargs)

        self.columns = columns
        self.cards: dict = {}

        self.grid_columnconfigure(tuple(range(columns)), weight=1, uniform="kpi")

    def add_card(
        self,
        key: str,
        title: str,
        value: Union[int, float, str] = 0,
        subtitle: str = "",
        icon: str = "",
        color: str = "primary",
        format_type: str = "number"
    ) -> KPICard:
        """Add a KPI card to the grid."""
        row = len(self.cards) // self.columns
        col = len(self.cards) % self.columns

        card = KPICard(
            self,
            title=title,
            value=value,
            subtitle=subtitle,
            icon=icon,
            color=color,
            format_type=format_type
        )
        card.grid(row=row, column=col, sticky="nsew", padx=5, pady=5)

        self.cards[key] = card
        return card

    def update_card(self, key: str, value: Union[int, float, str]) -> None:
        """Update a card's value."""
        if key in self.cards:
            self.cards[key].set_value(value)

    def get_card(self, key: str) -> Optional[KPICard]:
        """Get a card by key."""
        return self.cards.get(key)
