"""Merge tag picker widget for template editing."""
import tkinter as tk
from typing import List, Callable, Optional
import ttkbootstrap as ttk
from ttkbootstrap.constants import *

from services.template_service import TemplateService, MergeTag


class MergeTagPicker(ttk.Frame):
    """Widget for selecting and inserting merge tags into templates."""

    def __init__(
        self,
        parent,
        on_insert: Optional[Callable[[str], None]] = None,
        show_preview: bool = True,
        **kwargs
    ):
        """
        Initialize MergeTagPicker.

        Args:
            parent: Parent widget
            on_insert: Callback when tag is selected for insertion
            show_preview: Whether to show tag preview
        """
        super().__init__(parent, **kwargs)

        self.on_insert = on_insert
        self.template_service = TemplateService()

        self._create_widgets(show_preview)
        self._load_tags()

    def _create_widgets(self, show_preview: bool) -> None:
        """Create picker widgets."""
        # Header
        header = ttk.Label(
            self,
            text="Merge Tags",
            font=("Segoe UI", 11, "bold")
        )
        header.pack(anchor=W, pady=(0, 10))

        # Category selector
        cat_frame = ttk.Frame(self)
        cat_frame.pack(fill=X, pady=(0, 10))

        ttk.Label(cat_frame, text="Category:").pack(side=LEFT, padx=(0, 5))

        self.category_var = tk.StringVar(value="All")
        categories = ["All"] + self.template_service.get_categories()

        self.category_combo = ttk.Combobox(
            cat_frame,
            textvariable=self.category_var,
            values=categories,
            state="readonly",
            width=15
        )
        self.category_combo.pack(side=LEFT)
        self.category_combo.bind("<<ComboboxSelected>>", self._on_category_change)

        # Tags list with scrollbar
        list_frame = ttk.Frame(self)
        list_frame.pack(fill=BOTH, expand=True)

        scrollbar = ttk.Scrollbar(list_frame)
        scrollbar.pack(side=RIGHT, fill=Y)

        self.tag_listbox = tk.Listbox(
            list_frame,
            height=10,
            selectmode=tk.SINGLE,
            yscrollcommand=scrollbar.set,
            font=("Segoe UI", 9)
        )
        self.tag_listbox.pack(fill=BOTH, expand=True)
        scrollbar.config(command=self.tag_listbox.yview)

        self.tag_listbox.bind("<<ListboxSelect>>", self._on_tag_select)
        self.tag_listbox.bind("<Double-1>", self._on_tag_double_click)

        # Preview area
        if show_preview:
            preview_frame = ttk.LabelFrame(self, text="Preview", padding=10)
            preview_frame.pack(fill=X, pady=(10, 0))

            self.tag_label = ttk.Label(
                preview_frame,
                text="Select a tag",
                font=("Consolas", 10)
            )
            self.tag_label.pack(anchor=W)

            self.preview_label = ttk.Label(
                preview_frame,
                text="",
                font=("Segoe UI", 9),
                bootstyle="secondary"
            )
            self.preview_label.pack(anchor=W, pady=(5, 0))

        # Insert button
        self.insert_btn = ttk.Button(
            self,
            text="Insert Tag",
            bootstyle="primary",
            command=self._on_insert_click
        )
        self.insert_btn.pack(fill=X, pady=(10, 0))

    def _load_tags(self) -> None:
        """Load merge tags into listbox."""
        self.tag_listbox.delete(0, tk.END)

        category = self.category_var.get()
        if category == "All":
            tags = self.template_service.get_all_merge_tags()
        else:
            tags = self.template_service.get_merge_tags_by_category(category)

        self._current_tags = tags
        for tag in tags:
            self.tag_listbox.insert(tk.END, f"{tag.label} - {tag.tag}")

    def _on_category_change(self, event) -> None:
        """Handle category selection change."""
        self._load_tags()

    def _on_tag_select(self, event) -> None:
        """Handle tag selection."""
        selection = self.tag_listbox.curselection()
        if selection:
            idx = selection[0]
            tag = self._current_tags[idx]

            if hasattr(self, 'tag_label'):
                self.tag_label.configure(text=tag.tag)
                # Show sample value
                sample = self._get_sample_value(tag)
                self.preview_label.configure(text=f"Example: {sample}")

    def _on_tag_double_click(self, event) -> None:
        """Handle tag double-click to insert."""
        self._on_insert_click()

    def _on_insert_click(self) -> None:
        """Handle insert button click."""
        selection = self.tag_listbox.curselection()
        if selection and self.on_insert:
            idx = selection[0]
            tag = self._current_tags[idx]
            self.on_insert(tag.tag)

    def _get_sample_value(self, tag: MergeTag) -> str:
        """Get sample value for a tag."""
        samples = {
            "{{FirstName}}": "John",
            "{{LastName}}": "Doe",
            "{{Email}}": "john.doe@example.com",
            "{{Company}}": "Acme Corporation",
            "{{Title}}": "Mr.",
            "{{Position}}": "Sales Director",
            "{{Phone}}": "+1 555-123-4567",
            "{{SenderName}}": "Jane Smith",
            "{{SenderEmail}}": "jane.smith@company.com",
            "{{CampaignName}}": "Q1 Outreach",
            "{{CampaignRef}}": "ISIT-250001",
        }

        if tag.tag in samples:
            return samples[tag.tag]
        elif "Custom" in tag.tag:
            return f"Custom Value {tag.tag[-3:-2]}"
        return "(sample value)"

    def get_selected_tag(self) -> Optional[str]:
        """Get currently selected tag string."""
        selection = self.tag_listbox.curselection()
        if selection:
            idx = selection[0]
            return self._current_tags[idx].tag
        return None


class MergeTagButton(ttk.Menubutton):
    """A dropdown button for quick merge tag insertion."""

    def __init__(
        self,
        parent,
        on_insert: Callable[[str], None],
        text: str = "Insert Tag",
        **kwargs
    ):
        super().__init__(parent, text=text, bootstyle="outline-primary", **kwargs)

        self.on_insert = on_insert
        self.template_service = TemplateService()

        self._create_menu()

    def _create_menu(self) -> None:
        """Create dropdown menu with tags."""
        self.menu = tk.Menu(self, tearoff=0)
        self.configure(menu=self.menu)

        # Group by category
        for category in self.template_service.get_categories():
            submenu = tk.Menu(self.menu, tearoff=0)
            self.menu.add_cascade(label=category, menu=submenu)

            for tag in self.template_service.get_merge_tags_by_category(category):
                submenu.add_command(
                    label=f"{tag.label} ({tag.tag})",
                    command=lambda t=tag.tag: self.on_insert(t)
                )
