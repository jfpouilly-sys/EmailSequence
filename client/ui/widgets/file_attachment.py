"""File attachment widget with delivery mode selection."""
import tkinter as tk
from tkinter import filedialog
from typing import List, Optional, Callable, Tuple
from dataclasses import dataclass
import os
import ttkbootstrap as ttk
from ttkbootstrap.constants import *


@dataclass
class AttachmentItem:
    """Represents an attachment."""
    file_path: str
    file_name: str
    file_size: int
    delivery_mode: str  # "Attachment" or "Link"


class FileAttachmentWidget(ttk.Frame):
    """Widget for managing file attachments with delivery mode selection."""

    MAX_FILE_SIZE = 25 * 1024 * 1024  # 25 MB

    def __init__(
        self,
        parent,
        on_change: Optional[Callable[[List[AttachmentItem]], None]] = None,
        max_files: int = 5,
        allowed_extensions: Optional[List[str]] = None,
        **kwargs
    ):
        """
        Initialize FileAttachmentWidget.

        Args:
            parent: Parent widget
            on_change: Callback when attachments change
            max_files: Maximum number of attachments
            allowed_extensions: List of allowed file extensions (e.g., ['.pdf', '.docx'])
        """
        super().__init__(parent, **kwargs)

        self.on_change = on_change
        self.max_files = max_files
        self.allowed_extensions = allowed_extensions or [
            '.pdf', '.docx', '.xlsx', '.pptx', '.doc', '.xls', '.ppt',
            '.jpg', '.jpeg', '.png', '.gif', '.zip', '.txt'
        ]

        self.attachments: List[AttachmentItem] = []
        self._create_widgets()

    def _create_widgets(self) -> None:
        """Create widget components."""
        # Header
        header = ttk.Frame(self)
        header.pack(fill=X, pady=(0, 10))

        ttk.Label(
            header,
            text="Attachments",
            font=("Segoe UI", 11, "bold")
        ).pack(side=LEFT)

        ttk.Label(
            header,
            text=f"(max {self.max_files} files)",
            font=("Segoe UI", 9),
            bootstyle="secondary"
        ).pack(side=LEFT, padx=(10, 0))

        # Attachments list
        self.list_frame = ttk.Frame(self)
        self.list_frame.pack(fill=BOTH, expand=True)

        # Add button
        add_frame = ttk.Frame(self)
        add_frame.pack(fill=X, pady=(10, 0))

        self.add_btn = ttk.Button(
            add_frame,
            text="+ Add File",
            bootstyle="outline-primary",
            command=self._on_add_click
        )
        self.add_btn.pack(side=LEFT)

        # Delivery mode info
        info_frame = ttk.LabelFrame(self, text="Delivery Mode Info", padding=10)
        info_frame.pack(fill=X, pady=(15, 0))

        ttk.Label(
            info_frame,
            text="\u2022 Attachment: File sent directly with email (no tracking)",
            font=("Segoe UI", 9),
            bootstyle="secondary"
        ).pack(anchor=W)

        ttk.Label(
            info_frame,
            text="\u2022 Link: Download link with click tracking (internal network only)",
            font=("Segoe UI", 9),
            bootstyle="secondary"
        ).pack(anchor=W)

        # Warning for Link mode
        self.warning_frame = ttk.Frame(info_frame)
        self.warning_frame.pack(fill=X, pady=(10, 0))

        ttk.Label(
            self.warning_frame,
            text="\u26A0 Warning: Link mode only works on internal network",
            font=("Segoe UI", 9, "bold"),
            bootstyle="warning"
        ).pack(anchor=W)

        self.warning_frame.pack_forget()  # Hidden by default

    def _on_add_click(self) -> None:
        """Handle add file button click."""
        if len(self.attachments) >= self.max_files:
            return

        filetypes = [("All supported", " ".join(f"*{ext}" for ext in self.allowed_extensions))]
        filetypes.extend([(ext.upper()[1:] + " files", f"*{ext}") for ext in self.allowed_extensions[:5]])
        filetypes.append(("All files", "*.*"))

        file_path = filedialog.askopenfilename(
            title="Select file to attach",
            filetypes=filetypes
        )

        if file_path:
            self._add_file(file_path)

    def _add_file(self, file_path: str) -> None:
        """Add a file as attachment."""
        # Validate file
        if not os.path.exists(file_path):
            self._show_error("File not found")
            return

        file_size = os.path.getsize(file_path)
        if file_size > self.MAX_FILE_SIZE:
            self._show_error(f"File too large (max {self.MAX_FILE_SIZE // 1024 // 1024} MB)")
            return

        ext = os.path.splitext(file_path)[1].lower()
        if ext not in self.allowed_extensions:
            self._show_error(f"File type not allowed: {ext}")
            return

        # Create attachment
        attachment = AttachmentItem(
            file_path=file_path,
            file_name=os.path.basename(file_path),
            file_size=file_size,
            delivery_mode="Attachment"
        )

        self.attachments.append(attachment)
        self._refresh_list()
        self._notify_change()

    def _refresh_list(self) -> None:
        """Refresh the attachments list display."""
        # Clear existing items
        for widget in self.list_frame.winfo_children():
            widget.destroy()

        if not self.attachments:
            ttk.Label(
                self.list_frame,
                text="No attachments added",
                font=("Segoe UI", 9),
                bootstyle="secondary"
            ).pack(pady=20)
            self.warning_frame.pack_forget()
            return

        # Show each attachment
        has_link_mode = False
        for i, att in enumerate(self.attachments):
            frame = self._create_attachment_row(i, att)
            frame.pack(fill=X, pady=2)
            if att.delivery_mode == "Link":
                has_link_mode = True

        # Update add button state
        if len(self.attachments) >= self.max_files:
            self.add_btn.configure(state="disabled")
        else:
            self.add_btn.configure(state="normal")

        # Show/hide warning
        if has_link_mode:
            self.warning_frame.pack(fill=X, pady=(10, 0))
        else:
            self.warning_frame.pack_forget()

    def _create_attachment_row(self, index: int, attachment: AttachmentItem) -> ttk.Frame:
        """Create a row for an attachment."""
        frame = ttk.Frame(self.list_frame, bootstyle="light", padding=5)

        # File info
        info_frame = ttk.Frame(frame)
        info_frame.pack(side=LEFT, fill=X, expand=True)

        ttk.Label(
            info_frame,
            text=attachment.file_name,
            font=("Segoe UI", 9, "bold")
        ).pack(anchor=W)

        size_str = self._format_size(attachment.file_size)
        ttk.Label(
            info_frame,
            text=size_str,
            font=("Segoe UI", 8),
            bootstyle="secondary"
        ).pack(anchor=W)

        # Delivery mode selector
        mode_frame = ttk.Frame(frame)
        mode_frame.pack(side=LEFT, padx=10)

        mode_var = tk.StringVar(value=attachment.delivery_mode)

        ttk.Radiobutton(
            mode_frame,
            text="Attachment",
            variable=mode_var,
            value="Attachment",
            command=lambda: self._on_mode_change(index, mode_var.get())
        ).pack(side=LEFT)

        ttk.Radiobutton(
            mode_frame,
            text="Link",
            variable=mode_var,
            value="Link",
            command=lambda: self._on_mode_change(index, mode_var.get())
        ).pack(side=LEFT, padx=(10, 0))

        # Remove button
        remove_btn = ttk.Button(
            frame,
            text="\u2716",
            bootstyle="outline-danger",
            width=3,
            command=lambda: self._on_remove(index)
        )
        remove_btn.pack(side=RIGHT)

        return frame

    def _on_mode_change(self, index: int, mode: str) -> None:
        """Handle delivery mode change."""
        self.attachments[index].delivery_mode = mode
        self._refresh_list()
        self._notify_change()

    def _on_remove(self, index: int) -> None:
        """Handle remove attachment."""
        del self.attachments[index]
        self._refresh_list()
        self._notify_change()

    def _format_size(self, size: int) -> str:
        """Format file size for display."""
        if size < 1024:
            return f"{size} B"
        elif size < 1024 * 1024:
            return f"{size / 1024:.1f} KB"
        else:
            return f"{size / 1024 / 1024:.1f} MB"

    def _notify_change(self) -> None:
        """Notify callback of changes."""
        if self.on_change:
            self.on_change(self.attachments.copy())

    def _show_error(self, message: str) -> None:
        """Show error message."""
        from tkinter import messagebox
        messagebox.showerror("Attachment Error", message)

    def get_attachments(self) -> List[AttachmentItem]:
        """Get list of attachments."""
        return self.attachments.copy()

    def clear(self) -> None:
        """Clear all attachments."""
        self.attachments.clear()
        self._refresh_list()
        self._notify_change()

    def set_attachments(self, attachments: List[AttachmentItem]) -> None:
        """Set attachments from list."""
        self.attachments = attachments.copy()
        self._refresh_list()
