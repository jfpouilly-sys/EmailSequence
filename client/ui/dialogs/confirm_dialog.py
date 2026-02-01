"""Confirmation and message dialogs."""
import tkinter as tk
from typing import Optional
import ttkbootstrap as ttk
from ttkbootstrap.constants import *


class ConfirmDialog(ttk.Toplevel):
    """Custom confirmation dialog."""

    def __init__(
        self,
        parent,
        title: str = "Confirm",
        message: str = "Are you sure?",
        confirm_text: str = "Yes",
        cancel_text: str = "No",
        icon: str = "question",  # question, warning, error, info
        **kwargs
    ):
        super().__init__(parent, **kwargs)

        self.result = False

        self.title(title)
        self.geometry("400x180")
        self.resizable(False, False)

        self._create_widgets(message, confirm_text, cancel_text, icon)

        # Center on parent
        self.update_idletasks()
        if parent:
            x = parent.winfo_rootx() + (parent.winfo_width() - 400) // 2
            y = parent.winfo_rooty() + (parent.winfo_height() - 180) // 2
            self.geometry(f"+{x}+{y}")

        self.transient(parent)
        self.grab_set()

        # Handle close button
        self.protocol("WM_DELETE_WINDOW", self._on_cancel)

    def _create_widgets(self, message: str, confirm_text: str, cancel_text: str, icon: str) -> None:
        """Create dialog widgets."""
        main = ttk.Frame(self, padding=20)
        main.pack(fill=BOTH, expand=True)

        # Icon and message
        content = ttk.Frame(main)
        content.pack(fill=BOTH, expand=True)

        # Icon
        icons = {
            "question": "\u2753",
            "warning": "\u26A0",
            "error": "\u2718",
            "info": "\u2139"
        }
        colors = {
            "question": "primary",
            "warning": "warning",
            "error": "danger",
            "info": "info"
        }

        icon_label = ttk.Label(
            content,
            text=icons.get(icon, "\u2753"),
            font=("Segoe UI", 36),
            bootstyle=colors.get(icon, "primary")
        )
        icon_label.pack(side=LEFT, padx=(0, 20))

        # Message
        msg_label = ttk.Label(
            content,
            text=message,
            font=("Segoe UI", 11),
            wraplength=280,
            justify=LEFT
        )
        msg_label.pack(side=LEFT, fill=BOTH, expand=True)

        # Buttons
        btn_frame = ttk.Frame(main)
        btn_frame.pack(fill=X, pady=(20, 0))

        cancel_btn = ttk.Button(
            btn_frame,
            text=cancel_text,
            bootstyle="secondary",
            command=self._on_cancel,
            width=10
        )
        cancel_btn.pack(side=RIGHT, padx=5)

        confirm_style = "danger" if icon == "warning" else "primary"
        confirm_btn = ttk.Button(
            btn_frame,
            text=confirm_text,
            bootstyle=confirm_style,
            command=self._on_confirm,
            width=10
        )
        confirm_btn.pack(side=RIGHT)
        confirm_btn.focus_set()

        # Keyboard bindings
        self.bind("<Return>", lambda e: self._on_confirm())
        self.bind("<Escape>", lambda e: self._on_cancel())

    def _on_confirm(self) -> None:
        """Handle confirm action."""
        self.result = True
        self.destroy()

    def _on_cancel(self) -> None:
        """Handle cancel action."""
        self.result = False
        self.destroy()


class MessageDialog(ttk.Toplevel):
    """Simple message dialog."""

    def __init__(
        self,
        parent,
        title: str = "Message",
        message: str = "",
        icon: str = "info",  # info, warning, error, success
        **kwargs
    ):
        super().__init__(parent, **kwargs)

        self.title(title)
        self.geometry("400x150")
        self.resizable(False, False)

        self._create_widgets(message, icon)

        # Center on parent
        self.update_idletasks()
        if parent:
            x = parent.winfo_rootx() + (parent.winfo_width() - 400) // 2
            y = parent.winfo_rooty() + (parent.winfo_height() - 150) // 2
            self.geometry(f"+{x}+{y}")

        self.transient(parent)
        self.grab_set()

    def _create_widgets(self, message: str, icon: str) -> None:
        """Create dialog widgets."""
        main = ttk.Frame(self, padding=20)
        main.pack(fill=BOTH, expand=True)

        # Icon and message
        content = ttk.Frame(main)
        content.pack(fill=BOTH, expand=True)

        icons = {
            "info": "\u2139",
            "warning": "\u26A0",
            "error": "\u2718",
            "success": "\u2714"
        }
        colors = {
            "info": "info",
            "warning": "warning",
            "error": "danger",
            "success": "success"
        }

        icon_label = ttk.Label(
            content,
            text=icons.get(icon, "\u2139"),
            font=("Segoe UI", 36),
            bootstyle=colors.get(icon, "info")
        )
        icon_label.pack(side=LEFT, padx=(0, 20))

        msg_label = ttk.Label(
            content,
            text=message,
            font=("Segoe UI", 11),
            wraplength=280,
            justify=LEFT
        )
        msg_label.pack(side=LEFT, fill=BOTH, expand=True)

        # OK button
        btn_frame = ttk.Frame(main)
        btn_frame.pack(fill=X, pady=(20, 0))

        ok_btn = ttk.Button(
            btn_frame,
            text="OK",
            bootstyle="primary",
            command=self.destroy,
            width=10
        )
        ok_btn.pack(side=RIGHT)
        ok_btn.focus_set()

        self.bind("<Return>", lambda e: self.destroy())
        self.bind("<Escape>", lambda e: self.destroy())


def show_confirm(parent, title: str, message: str, **kwargs) -> bool:
    """Show confirmation dialog and return result."""
    dialog = ConfirmDialog(parent, title=title, message=message, **kwargs)
    parent.wait_window(dialog)
    return dialog.result


def show_error(parent, title: str, message: str) -> None:
    """Show error message dialog."""
    dialog = MessageDialog(parent, title=title, message=message, icon="error")
    parent.wait_window(dialog)


def show_info(parent, title: str, message: str) -> None:
    """Show info message dialog."""
    dialog = MessageDialog(parent, title=title, message=message, icon="info")
    parent.wait_window(dialog)


def show_warning(parent, title: str, message: str) -> None:
    """Show warning message dialog."""
    dialog = MessageDialog(parent, title=title, message=message, icon="warning")
    parent.wait_window(dialog)


def show_success(parent, title: str, message: str) -> None:
    """Show success message dialog."""
    dialog = MessageDialog(parent, title=title, message=message, icon="success")
    parent.wait_window(dialog)
