"""Confirmation dialog for Lead Generator Standalone."""

import tkinter as tk
from tkinter import ttk


class ConfirmDialog(tk.Toplevel):
    """Simple confirmation dialog."""

    def __init__(self, parent, title: str, message: str):
        super().__init__(parent)
        self.title(title)
        self.result = False

        # Make modal
        self.transient(parent)
        self.grab_set()

        # Content
        ttk.Label(self, text=message, wraplength=300).pack(padx=20, pady=20)

        # Buttons
        btn_frame = ttk.Frame(self)
        btn_frame.pack(pady=(0, 20))

        ttk.Button(btn_frame, text="Yes", command=self._on_yes).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="No", command=self._on_no).pack(side=tk.LEFT, padx=5)

        # Center window
        self.geometry("350x150")
        self.resizable(False, False)

        # Wait for dialog
        self.wait_window()

    def _on_yes(self):
        self.result = True
        self.destroy()

    def _on_no(self):
        self.result = False
        self.destroy()
