"""Main Application Window

Email Sequence Manager GUI - Main window with sidebar navigation.
"""

import customtkinter as ctk
from typing import Optional
import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from gui.config import GUIConfig


class MainApp(ctk.CTk):
    """Main application window with sidebar navigation."""

    def __init__(self, config_path: str = "gui_config.yaml"):
        """Initialize main window.

        Args:
            config_path: Path to GUI configuration file
        """
        super().__init__()

        # Load configuration
        self.gui_config = GUIConfig(config_path)

        # Set up window
        self.title("Email Sequence Manager")
        width = self.gui_config.get('appearance.window_width', 1200)
        height = self.gui_config.get('appearance.window_height', 800)
        self.geometry(f"{width}x{height}")

        # Set minimum size
        self.minsize(900, 600)

        # Configure grid
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)

        # Current frame reference
        self.current_frame: Optional[ctk.CTkFrame] = None
        self.current_frame_name: str = ""

        # Create UI components
        self.create_sidebar()
        self.create_content_area()
        self.create_status_bar()

        # Navigate to dashboard by default
        self.navigate_to("dashboard")

        # Handle window close
        self.protocol("WM_DELETE_WINDOW", self.on_close)

        # Start minimized if configured
        if self.gui_config.get('behavior.start_minimized', False):
            self.iconify()

    def create_sidebar(self) -> None:
        """Create left sidebar with navigation buttons."""
        sidebar_width = self.gui_config.get('appearance.sidebar_width', 200)

        # Sidebar frame
        self.sidebar = ctk.CTkFrame(self, width=sidebar_width, corner_radius=0)
        self.sidebar.grid(row=0, column=0, sticky="nsew")
        self.sidebar.grid_rowconfigure(7, weight=1)  # Spacer row

        # Logo/Title
        logo_label = ctk.CTkLabel(
            self.sidebar,
            text="Email Sequence\nManager",
            font=("Arial Bold", 16),
            text_color="#3B82F6"
        )
        logo_label.grid(row=0, column=0, pady=(20, 30), padx=20)

        # Navigation buttons
        self.nav_buttons = {}

        nav_items = [
            ("dashboard", "🏠 Dashboard", 1),
            ("contacts", "👥 Contacts", 2),
            ("sequence", "▶️  Sequence", 3),
            ("templates", "📝 Templates", 4),
            ("logs", "📋 Logs", 5),
            ("settings", "⚙️  Settings", 6),
        ]

        for frame_name, label, row in nav_items:
            btn = ctk.CTkButton(
                self.sidebar,
                text=label,
                command=lambda f=frame_name: self.navigate_to(f),
                width=sidebar_width - 40,
                height=40,
                font=("Arial", 12),
                anchor="w",
                fg_color="transparent",
                text_color="gray",
                hover_color="#1F2937"
            )
            btn.grid(row=row, column=0, pady=5, padx=20, sticky="ew")
            self.nav_buttons[frame_name] = btn

        # Version label at bottom
        version_label = ctk.CTkLabel(
            self.sidebar,
            text="v1.0.0-20260119",
            font=("Arial", 9),
            text_color="gray"
        )
        version_label.grid(row=8, column=0, pady=(0, 10))

    def create_content_area(self) -> None:
        """Create main content area container."""
        self.content_container = ctk.CTkFrame(self, corner_radius=0)
        self.content_container.grid(row=0, column=1, sticky="nsew", padx=0, pady=0)
        self.content_container.grid_rowconfigure(0, weight=1)
        self.content_container.grid_columnconfigure(0, weight=1)

    def create_status_bar(self) -> None:
        """Create bottom status bar."""
        self.status_bar = ctk.CTkFrame(self, height=30, corner_radius=0, fg_color="#1F2937")
        self.status_bar.grid(row=1, column=0, columnspan=2, sticky="ew")
        self.status_bar.grid_columnconfigure(1, weight=1)

        # Status message
        self.status_message = ctk.CTkLabel(
            self.status_bar,
            text="Ready",
            font=("Arial", 10),
            anchor="w"
        )
        self.status_message.grid(row=0, column=0, padx=10, sticky="w")

        # Right side info
        self.status_info = ctk.CTkLabel(
            self.status_bar,
            text="",
            font=("Arial", 10),
            anchor="e"
        )
        self.status_info.grid(row=0, column=1, padx=10, sticky="e")

    def navigate_to(self, frame_name: str) -> None:
        """Switch content area to specified frame.

        Args:
            frame_name: Name of frame to display
        """
        # Don't reload if already on this frame
        if frame_name == self.current_frame_name:
            return

        # Destroy current frame
        if self.current_frame:
            self.current_frame.destroy()

        # Update button highlighting
        for name, btn in self.nav_buttons.items():
            if name == frame_name:
                btn.configure(fg_color="#3B82F6", text_color="white")
            else:
                btn.configure(fg_color="transparent", text_color="gray")

        # Create new frame
        try:
            if frame_name == "dashboard":
                from gui.frames.dashboard import DashboardFrame
                self.current_frame = DashboardFrame(self.content_container, self)
            elif frame_name == "contacts":
                from gui.frames.contacts import ContactsFrame
                self.current_frame = ContactsFrame(self.content_container, self)
            elif frame_name == "sequence":
                from gui.frames.sequence import SequenceFrame
                self.current_frame = SequenceFrame(self.content_container, self)
            elif frame_name == "templates":
                from gui.frames.templates import TemplatesFrame
                self.current_frame = TemplatesFrame(self.content_container, self)
            elif frame_name == "logs":
                from gui.frames.logs import LogsFrame
                self.current_frame = LogsFrame(self.content_container, self)
            elif frame_name == "settings":
                from gui.frames.settings import SettingsFrame
                self.current_frame = SettingsFrame(self.content_container, self)
            else:
                # Fallback to placeholder
                self.current_frame = ctk.CTkFrame(self.content_container)
                label = ctk.CTkLabel(
                    self.current_frame,
                    text=f"{frame_name.title()} (Coming Soon)",
                    font=("Arial", 24)
                )
                label.pack(expand=True)

            # Display frame
            self.current_frame.grid(row=0, column=0, sticky="nsew", padx=0, pady=0)
            self.current_frame_name = frame_name

        except Exception as e:
            print(f"Error loading frame {frame_name}: {e}")
            # Show error frame
            self.current_frame = ctk.CTkFrame(self.content_container)
            error_label = ctk.CTkLabel(
                self.current_frame,
                text=f"Error loading {frame_name}\n{str(e)}",
                font=("Arial", 14),
                text_color="red"
            )
            error_label.pack(expand=True)
            self.current_frame.grid(row=0, column=0, sticky="nsew")

    def update_status_bar(
        self,
        message: str = None,
        outlook_status: bool = None,
        last_sync: str = None
    ) -> None:
        """Update bottom status bar.

        Args:
            message: Status message
            outlook_status: Outlook connection status
            last_sync: Last sync timestamp
        """
        if message:
            self.status_message.configure(text=message)

        # Build right side info
        info_parts = []
        if outlook_status is not None:
            status_text = "Outlook: Connected" if outlook_status else "Outlook: Disconnected"
            info_parts.append(status_text)
        if last_sync:
            info_parts.append(f"Last sync: {last_sync}")

        if info_parts:
            self.status_info.configure(text=" | ".join(info_parts))

    def show_notification(self, title: str, message: str) -> None:
        """Show system notification if enabled.

        Args:
            title: Notification title
            message: Notification message
        """
        if not self.gui_config.get('behavior.show_notifications', True):
            return

        try:
            # On Linux, use notify-send if available
            if sys.platform.startswith('linux'):
                os.system(f'notify-send "{title}" "{message}"')
            # On Windows, would use win10toast or similar
            # For now, just print
            print(f"Notification: {title} - {message}")
        except Exception as e:
            print(f"Error showing notification: {e}")

    def on_close(self) -> None:
        """Handle window close event."""
        minimize_to_tray = self.gui_config.get('behavior.minimize_to_tray', False)

        if minimize_to_tray:
            # Minimize instead of closing
            self.iconify()
        else:
            # Confirm and exit
            from gui.dialogs import ConfirmationDialog
            dialog = ConfirmationDialog(
                self,
                "Exit Application",
                "Are you sure you want to exit Email Sequence Manager?",
                confirm_text="Exit",
                cancel_text="Cancel"
            )
            if dialog.get_result():
                self.quit()

    def reload_frame(self) -> None:
        """Reload current frame (useful after settings changes)."""
        current = self.current_frame_name
        self.current_frame_name = ""  # Force reload
        self.navigate_to(current)


def main():
    """Run the application."""
    # Set appearance
    ctk.set_appearance_mode("dark")
    ctk.set_default_color_theme("blue")

    # Create and run app
    app = MainApp()
    app.mainloop()


if __name__ == "__main__":
    main()
