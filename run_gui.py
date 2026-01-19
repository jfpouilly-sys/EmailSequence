#!/usr/bin/env python3
"""Email Sequence Manager - GUI Entry Point

Launch the graphical user interface for the Email Sequence Manager.

Version: 1.0.0-20260119
"""

__version__ = "1.0.0-20260119"

import sys
import os

# Add current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import customtkinter as ctk
from gui.app import MainApp


def main():
    """Run the Email Sequence Manager GUI application."""
    # Set appearance mode and theme
    ctk.set_appearance_mode("dark")
    ctk.set_default_color_theme("blue")

    # Create and run application
    try:
        app = MainApp()
        app.mainloop()
    except KeyboardInterrupt:
        print("\nApplication interrupted by user")
        sys.exit(0)
    except Exception as e:
        print(f"Error running application: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
