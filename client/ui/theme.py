"""Theme configuration for ttkbootstrap."""
import ttkbootstrap as ttk
from ttkbootstrap.constants import *
from typing import Dict, Any


class ThemeManager:
    """Manages application theming with ttkbootstrap."""

    # Available themes that work well for business apps
    AVAILABLE_THEMES = [
        "cosmo",      # Clean, modern (default for Windows 11 look)
        "flatly",     # Flat design
        "litera",     # Clean, readable
        "minty",      # Fresh, green accents
        "pulse",      # Vibrant
        "sandstone",  # Warm, earthy
        "united",     # Ubuntu-inspired
        "yeti",       # Friendly, accessible
        "morph",      # Morphism style
        "journal",    # Newspaper style
        "darkly",     # Dark theme
        "cyborg",     # Dark, high contrast
        "vapor",      # Vaporwave dark
        "superhero",  # Dark blue theme
        "solar",      # Solarized dark
    ]

    DEFAULT_THEME = "cosmo"

    def __init__(self, initial_theme: str = None):
        self._current_theme = initial_theme or self.DEFAULT_THEME
        self._style: ttk.Style = None

    @property
    def current_theme(self) -> str:
        return self._current_theme

    def apply_theme(self, root: ttk.Window, theme: str = None) -> None:
        """Apply theme to the application window."""
        if theme:
            self._current_theme = theme

        self._style = ttk.Style(theme=self._current_theme)
        self._configure_custom_styles()

    def change_theme(self, theme: str) -> None:
        """Change the current theme."""
        if theme in self.AVAILABLE_THEMES:
            self._current_theme = theme
            if self._style:
                self._style.theme_use(theme)
                self._configure_custom_styles()

    def _configure_custom_styles(self) -> None:
        """Configure custom widget styles."""
        if not self._style:
            return

        # Custom style for sidebar buttons
        self._style.configure(
            "Sidebar.TButton",
            font=("Segoe UI", 10),
            padding=(20, 10),
        )

        # Custom style for KPI cards
        self._style.configure(
            "KPI.TFrame",
            padding=15,
        )

        self._style.configure(
            "KPIValue.TLabel",
            font=("Segoe UI", 24, "bold"),
        )

        self._style.configure(
            "KPILabel.TLabel",
            font=("Segoe UI", 10),
        )

        # Custom style for headers
        self._style.configure(
            "Header.TLabel",
            font=("Segoe UI", 16, "bold"),
        )

        self._style.configure(
            "SubHeader.TLabel",
            font=("Segoe UI", 12),
        )

        # Custom style for form labels
        self._style.configure(
            "Form.TLabel",
            font=("Segoe UI", 10),
            padding=(0, 5),
        )

        # Status badge styles
        for status, color in [
            ("Active", "success"),
            ("Paused", "warning"),
            ("Draft", "secondary"),
            ("Completed", "info"),
            ("Cancelled", "danger"),
        ]:
            self._style.configure(
                f"Status{status}.TLabel",
                font=("Segoe UI", 9),
                padding=(8, 2),
            )

    def get_colors(self) -> Dict[str, str]:
        """Get current theme colors."""
        if not self._style:
            return {}

        return {
            "primary": self._style.colors.primary,
            "secondary": self._style.colors.secondary,
            "success": self._style.colors.success,
            "info": self._style.colors.info,
            "warning": self._style.colors.warning,
            "danger": self._style.colors.danger,
            "light": self._style.colors.light,
            "dark": self._style.colors.dark,
            "bg": self._style.colors.bg,
            "fg": self._style.colors.fg,
            "selectbg": self._style.colors.selectbg,
            "selectfg": self._style.colors.selectfg,
            "border": self._style.colors.border,
            "inputfg": self._style.colors.inputfg,
            "inputbg": self._style.colors.inputbg,
        }

    def is_dark_theme(self) -> bool:
        """Check if current theme is dark."""
        dark_themes = ["darkly", "cyborg", "vapor", "superhero", "solar"]
        return self._current_theme in dark_themes

    @classmethod
    def get_light_themes(cls) -> list:
        """Get list of light themes."""
        return [t for t in cls.AVAILABLE_THEMES if t not in
                ["darkly", "cyborg", "vapor", "superhero", "solar"]]

    @classmethod
    def get_dark_themes(cls) -> list:
        """Get list of dark themes."""
        return ["darkly", "cyborg", "vapor", "superhero", "solar"]
