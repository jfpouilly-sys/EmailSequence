"""Attachment picker widget for Lead Generator Standalone."""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from typing import List, Optional, Callable
from pathlib import Path

from core.models import Attachment


class AttachmentPicker(ttk.LabelFrame):
    """Widget for selecting and managing file attachments."""

    def __init__(
        self,
        parent,
        attachments: Optional[List[Attachment]] = None,
        on_change: Optional[Callable[[List[Attachment]], None]] = None,
        max_size_mb: float = 10.0,
        **kwargs
    ):
        """
        Initialize AttachmentPicker.

        Args:
            parent: Parent widget
            attachments: Initial list of attachments
            on_change: Callback when attachments change
            max_size_mb: Maximum file size in MB
        """
        super().__init__(parent, text="Attachments", **kwargs)

        self.attachments = attachments or []
        self.on_change = on_change
        self.max_size_mb = max_size_mb
        self._pending_files: List[str] = []  # New files not yet saved

        self._create_widgets()
        self._refresh_list()

    def _create_widgets(self) -> None:
        """Create picker widgets."""
        # Listbox for attachments
        list_frame = ttk.Frame(self)
        list_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        self.listbox = tk.Listbox(list_frame, height=4, selectmode=tk.SINGLE)
        self.listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        scrollbar = ttk.Scrollbar(list_frame, orient=tk.VERTICAL, command=self.listbox.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.listbox.configure(yscrollcommand=scrollbar.set)

        # Buttons
        btn_frame = ttk.Frame(self)
        btn_frame.pack(fill=tk.X, padx=5, pady=5)

        self.add_btn = ttk.Button(btn_frame, text="Add File", command=self._add_file)
        self.add_btn.pack(side=tk.LEFT, padx=(0, 5))

        self.remove_btn = ttk.Button(btn_frame, text="Remove", command=self._remove_file)
        self.remove_btn.pack(side=tk.LEFT)

        # Info label
        self.info_label = ttk.Label(self, text="", font=('Segoe UI', 8))
        self.info_label.pack(fill=tk.X, padx=5, pady=(0, 5))

    def _refresh_list(self) -> None:
        """Refresh the attachment list display."""
        self.listbox.delete(0, tk.END)

        total_size = 0

        # Existing attachments
        for att in self.attachments:
            size_kb = att.file_size / 1024
            self.listbox.insert(tk.END, f"{att.file_name} ({size_kb:.1f} KB)")
            total_size += att.file_size

        # Pending files
        for file_path in self._pending_files:
            path = Path(file_path)
            size = path.stat().st_size if path.exists() else 0
            size_kb = size / 1024
            self.listbox.insert(tk.END, f"* {path.name} ({size_kb:.1f} KB)")
            total_size += size

        # Update info label
        total_mb = total_size / (1024 * 1024)
        count = len(self.attachments) + len(self._pending_files)
        self.info_label.configure(text=f"{count} file(s), {total_mb:.2f} MB total")

    def _add_file(self) -> None:
        """Add a file attachment."""
        file_path = filedialog.askopenfilename(
            title="Select File",
            filetypes=[
                ("All Files", "*.*"),
                ("Documents", "*.pdf *.doc *.docx *.xls *.xlsx *.ppt *.pptx"),
                ("Images", "*.jpg *.jpeg *.png *.gif"),
                ("Archives", "*.zip *.rar *.7z")
            ]
        )

        if file_path:
            # Check file size
            path = Path(file_path)
            size_mb = path.stat().st_size / (1024 * 1024)

            if size_mb > self.max_size_mb:
                messagebox.showwarning(
                    "File Too Large",
                    f"File size ({size_mb:.1f} MB) exceeds maximum ({self.max_size_mb} MB)"
                )
                return

            # Add to pending files
            self._pending_files.append(file_path)
            self._refresh_list()
            self._notify_change()

    def _remove_file(self) -> None:
        """Remove selected file."""
        selection = self.listbox.curselection()
        if not selection:
            return

        idx = selection[0]
        existing_count = len(self.attachments)

        if idx < existing_count:
            # Remove existing attachment
            self.attachments.pop(idx)
        else:
            # Remove pending file
            pending_idx = idx - existing_count
            self._pending_files.pop(pending_idx)

        self._refresh_list()
        self._notify_change()

    def _notify_change(self) -> None:
        """Notify of attachment changes."""
        if self.on_change:
            self.on_change(self.attachments)

    def get_attachments(self) -> List[Attachment]:
        """Get current attachments."""
        return self.attachments

    def get_pending_files(self) -> List[str]:
        """Get pending file paths (not yet saved)."""
        return self._pending_files

    def set_attachments(self, attachments: List[Attachment]) -> None:
        """Set attachments list."""
        self.attachments = attachments
        self._pending_files = []
        self._refresh_list()

    def clear_pending(self) -> None:
        """Clear pending files (after save)."""
        self._pending_files = []
        self._refresh_list()
