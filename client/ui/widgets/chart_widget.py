"""Chart widget using matplotlib embedded in Tkinter."""
import tkinter as tk
from typing import List, Dict, Any, Optional, Tuple
import ttkbootstrap as ttk
from ttkbootstrap.constants import *

try:
    import matplotlib
    matplotlib.use('TkAgg')
    from matplotlib.figure import Figure
    from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
    import matplotlib.pyplot as plt
    MATPLOTLIB_AVAILABLE = True
except ImportError:
    MATPLOTLIB_AVAILABLE = False


class ChartWidget(ttk.Frame):
    """Widget for displaying charts using matplotlib."""

    def __init__(
        self,
        parent,
        figsize: Tuple[float, float] = (6, 4),
        show_toolbar: bool = False,
        **kwargs
    ):
        """
        Initialize ChartWidget.

        Args:
            parent: Parent widget
            figsize: Figure size in inches (width, height)
            show_toolbar: Whether to show matplotlib navigation toolbar
        """
        super().__init__(parent, **kwargs)

        self.figsize = figsize
        self.show_toolbar = show_toolbar

        if not MATPLOTLIB_AVAILABLE:
            self._show_no_matplotlib()
            return

        self._create_figure()

    def _show_no_matplotlib(self) -> None:
        """Show message when matplotlib is not available."""
        ttk.Label(
            self,
            text="Charts require matplotlib.\nInstall with: pip install matplotlib",
            font=("Segoe UI", 10),
            bootstyle="secondary",
            justify="center"
        ).pack(expand=True)

    def _create_figure(self) -> None:
        """Create matplotlib figure and canvas."""
        self.figure = Figure(figsize=self.figsize, dpi=100)
        self.figure.set_facecolor('white')

        self.canvas = FigureCanvasTkAgg(self.figure, self)
        self.canvas_widget = self.canvas.get_tk_widget()
        self.canvas_widget.pack(fill=BOTH, expand=True)

        if self.show_toolbar:
            self.toolbar = NavigationToolbar2Tk(self.canvas, self)
            self.toolbar.update()
            self.toolbar.pack(side=BOTTOM, fill=X)

    def clear(self) -> None:
        """Clear the figure."""
        if not MATPLOTLIB_AVAILABLE:
            return
        self.figure.clear()
        self.canvas.draw()

    def draw_bar_chart(
        self,
        labels: List[str],
        values: List[float],
        title: str = "",
        xlabel: str = "",
        ylabel: str = "",
        color: str = "#007bff",
        horizontal: bool = False
    ) -> None:
        """Draw a bar chart."""
        if not MATPLOTLIB_AVAILABLE:
            return

        self.figure.clear()
        ax = self.figure.add_subplot(111)

        if horizontal:
            ax.barh(labels, values, color=color)
            ax.set_xlabel(ylabel)
            ax.set_ylabel(xlabel)
        else:
            ax.bar(labels, values, color=color)
            ax.set_xlabel(xlabel)
            ax.set_ylabel(ylabel)

        if title:
            ax.set_title(title, fontweight='bold')

        self.figure.tight_layout()
        self.canvas.draw()

    def draw_pie_chart(
        self,
        labels: List[str],
        values: List[float],
        title: str = "",
        colors: Optional[List[str]] = None,
        show_percentage: bool = True
    ) -> None:
        """Draw a pie chart."""
        if not MATPLOTLIB_AVAILABLE:
            return

        self.figure.clear()
        ax = self.figure.add_subplot(111)

        autopct = '%1.1f%%' if show_percentage else None

        if colors:
            ax.pie(values, labels=labels, colors=colors, autopct=autopct, startangle=90)
        else:
            ax.pie(values, labels=labels, autopct=autopct, startangle=90)

        if title:
            ax.set_title(title, fontweight='bold')

        ax.axis('equal')
        self.figure.tight_layout()
        self.canvas.draw()

    def draw_line_chart(
        self,
        x_values: List[Any],
        y_values: List[float],
        title: str = "",
        xlabel: str = "",
        ylabel: str = "",
        color: str = "#007bff",
        marker: str = "o"
    ) -> None:
        """Draw a line chart."""
        if not MATPLOTLIB_AVAILABLE:
            return

        self.figure.clear()
        ax = self.figure.add_subplot(111)

        ax.plot(x_values, y_values, color=color, marker=marker, linewidth=2)

        if title:
            ax.set_title(title, fontweight='bold')
        ax.set_xlabel(xlabel)
        ax.set_ylabel(ylabel)

        ax.grid(True, alpha=0.3)
        self.figure.tight_layout()
        self.canvas.draw()

    def draw_multi_line_chart(
        self,
        x_values: List[Any],
        series: Dict[str, List[float]],
        title: str = "",
        xlabel: str = "",
        ylabel: str = "",
        colors: Optional[Dict[str, str]] = None
    ) -> None:
        """Draw a multi-line chart."""
        if not MATPLOTLIB_AVAILABLE:
            return

        self.figure.clear()
        ax = self.figure.add_subplot(111)

        for name, values in series.items():
            color = colors.get(name) if colors else None
            ax.plot(x_values, values, label=name, color=color, marker='o', linewidth=2)

        if title:
            ax.set_title(title, fontweight='bold')
        ax.set_xlabel(xlabel)
        ax.set_ylabel(ylabel)

        ax.legend()
        ax.grid(True, alpha=0.3)
        self.figure.tight_layout()
        self.canvas.draw()

    def draw_donut_chart(
        self,
        labels: List[str],
        values: List[float],
        title: str = "",
        colors: Optional[List[str]] = None,
        center_text: str = ""
    ) -> None:
        """Draw a donut chart."""
        if not MATPLOTLIB_AVAILABLE:
            return

        self.figure.clear()
        ax = self.figure.add_subplot(111)

        wedges, texts, autotexts = ax.pie(
            values,
            labels=labels,
            colors=colors,
            autopct='%1.1f%%',
            startangle=90,
            pctdistance=0.75
        )

        # Draw center circle for donut effect
        center_circle = plt.Circle((0, 0), 0.5, fc='white')
        ax.add_artist(center_circle)

        if center_text:
            ax.text(0, 0, center_text, ha='center', va='center', fontsize=14, fontweight='bold')

        if title:
            ax.set_title(title, fontweight='bold')

        ax.axis('equal')
        self.figure.tight_layout()
        self.canvas.draw()

    def draw_progress_chart(
        self,
        completed: float,
        remaining: float,
        title: str = "Progress",
        completed_label: str = "Completed",
        remaining_label: str = "Remaining"
    ) -> None:
        """Draw a progress donut chart."""
        total = completed + remaining
        percentage = (completed / total * 100) if total > 0 else 0

        self.draw_donut_chart(
            labels=[completed_label, remaining_label],
            values=[completed, remaining],
            title=title,
            colors=['#28a745', '#e9ecef'],
            center_text=f"{percentage:.0f}%"
        )

    def draw_status_distribution(
        self,
        status_counts: Dict[str, int],
        title: str = "Status Distribution"
    ) -> None:
        """Draw a status distribution chart with standard colors."""
        if not MATPLOTLIB_AVAILABLE:
            return

        status_colors = {
            'Active': '#28a745',
            'Paused': '#ffc107',
            'Draft': '#6c757d',
            'Completed': '#17a2b8',
            'Cancelled': '#dc3545',
            'Pending': '#6c757d',
            'InProgress': '#007bff',
            'Replied': '#28a745',
            'Unsubscribed': '#ffc107',
            'Bounced': '#dc3545',
            'Skipped': '#6c757d',
        }

        labels = list(status_counts.keys())
        values = list(status_counts.values())
        colors = [status_colors.get(s, '#6c757d') for s in labels]

        self.draw_pie_chart(
            labels=labels,
            values=values,
            title=title,
            colors=colors
        )

    def save(self, filepath: str, dpi: int = 150) -> None:
        """Save chart to file."""
        if not MATPLOTLIB_AVAILABLE:
            return
        self.figure.savefig(filepath, dpi=dpi, bbox_inches='tight')
