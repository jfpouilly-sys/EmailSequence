"""Merge tag picker widget for Lead Generator Standalone."""

import tkinter as tk
from tkinter import ttk
from typing import Optional, Callable, Dict, List

from services.template_service import TemplateService


class MergeTagPicker(ttk.LabelFrame):
    """Widget for selecting and inserting merge tags."""

    def __init__(
        self,
        parent,
        on_tag_selected: Optional[Callable[[str], None]] = None,
        custom_labels: Optional[Dict[str, str]] = None,
        **kwargs
    ):
        """
        Initialize MergeTagPicker.

        Args:
            parent: Parent widget
            on_tag_selected: Callback when a tag is selected (receives tag like {{FirstName}})
            custom_labels: Dict mapping custom field keys to labels
        """
        super().__init__(parent, text="Merge Tags", **kwargs)

        self.on_tag_selected = on_tag_selected
        self.custom_labels = custom_labels or {}
        self.template_service = TemplateService()

        self._create_widgets()

    def _create_widgets(self) -> None:
        """Create picker widgets."""
        # Get available tags
        tags = self.template_service.get_available_merge_tags()

        # Create button grid for each category
        row = 0
        for category, tag_list in tags.items():
            # Category label
            cat_label = ttk.Label(self, text=category, font=('Segoe UI', 9, 'bold'))
            cat_label.grid(row=row, column=0, columnspan=4, sticky='w', pady=(10, 5), padx=5)
            row += 1

            # Tag buttons
            col = 0
            for tag in tag_list:
                # Get display label
                display_label = tag
                if tag.startswith('Custom') and tag in self.custom_labels:
                    custom_label = self.custom_labels.get(tag)
                    if custom_label:
                        display_label = f"{tag} ({custom_label})"

                btn = ttk.Button(
                    self,
                    text=display_label,
                    width=15,
                    command=lambda t=tag: self._on_tag_click(t)
                )
                btn.grid(row=row, column=col, padx=2, pady=2, sticky='ew')

                col += 1
                if col >= 4:
                    col = 0
                    row += 1

            if col != 0:
                row += 1

        # Configure column weights
        for i in range(4):
            self.grid_columnconfigure(i, weight=1)

    def _on_tag_click(self, tag: str) -> None:
        """Handle tag button click."""
        tag_text = f"{{{{{tag}}}}}"  # Double braces for merge tag format
        if self.on_tag_selected:
            self.on_tag_selected(tag_text)

    def set_custom_labels(self, labels: Dict[str, str]) -> None:
        """Update custom field labels and rebuild."""
        self.custom_labels = labels
        # Clear and rebuild
        for widget in self.winfo_children():
            widget.destroy()
        self._create_widgets()
