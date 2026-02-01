"""Template editor view with merge tags and preview."""
import logging
import tkinter as tk
from typing import Optional
import ttkbootstrap as ttk
from ttkbootstrap.constants import *
from ttkbootstrap.scrolled import ScrolledText

from core.api_client import ApiClient
from services.template_service import TemplateService
from ui.widgets.merge_tag_picker import MergeTagPicker, MergeTagButton

logger = logging.getLogger(__name__)


class TemplateEditorView(ttk.Frame):
    """Template editor with merge tags and live preview."""

    def __init__(self, parent, app=None, api: ApiClient = None, **kwargs):
        super().__init__(parent, **kwargs)

        self.app = app
        self.api = api
        self.template_service = TemplateService()

        self._create_widgets()

    def _create_widgets(self) -> None:
        """Create view widgets."""
        # Main paned window
        paned = ttk.PanedWindow(self, orient=HORIZONTAL)
        paned.pack(fill=BOTH, expand=True)

        # Left: Editor
        editor_frame = ttk.Frame(paned)
        paned.add(editor_frame, weight=2)

        self._create_editor(editor_frame)

        # Right: Preview and Merge Tags
        right_frame = ttk.Frame(paned)
        paned.add(right_frame, weight=1)

        self._create_right_panel(right_frame)

    def _create_editor(self, parent) -> None:
        """Create template editor section."""
        # Subject
        subject_frame = ttk.LabelFrame(parent, text="Subject Line", padding=10)
        subject_frame.pack(fill=X, pady=(0, 10))

        subject_row = ttk.Frame(subject_frame)
        subject_row.pack(fill=X)

        self.subject_var = tk.StringVar()
        self.subject_entry = ttk.Entry(
            subject_row,
            textvariable=self.subject_var,
            font=("Segoe UI", 11)
        )
        self.subject_entry.pack(side=LEFT, fill=X, expand=True, padx=(0, 10))

        MergeTagButton(
            subject_row,
            on_insert=lambda tag: self._insert_tag_subject(tag),
            text="Insert"
        ).pack(side=RIGHT)

        # Body
        body_frame = ttk.LabelFrame(parent, text="Email Body", padding=10)
        body_frame.pack(fill=BOTH, expand=True)

        toolbar = ttk.Frame(body_frame)
        toolbar.pack(fill=X, pady=(0, 10))

        MergeTagButton(
            toolbar,
            on_insert=lambda tag: self._insert_tag_body(tag),
            text="Insert Merge Tag"
        ).pack(side=LEFT)

        ttk.Button(
            toolbar,
            text="Preview",
            bootstyle="outline-info",
            command=self._update_preview
        ).pack(side=RIGHT)

        # Body text
        self.body_text = ScrolledText(
            body_frame,
            wrap=tk.WORD,
            font=("Consolas", 10),
            height=20
        )
        self.body_text.pack(fill=BOTH, expand=True)

        # Bind for auto-preview
        self.body_text.bind("<KeyRelease>", self._on_content_change)
        self.subject_entry.bind("<KeyRelease>", self._on_content_change)

        # Validation
        validation_frame = ttk.Frame(parent)
        validation_frame.pack(fill=X, pady=(10, 0))

        self.validation_label = ttk.Label(
            validation_frame,
            text="",
            font=("Segoe UI", 9)
        )
        self.validation_label.pack(side=LEFT)

    def _create_right_panel(self, parent) -> None:
        """Create right panel with preview and merge tags."""
        # Preview
        preview_frame = ttk.LabelFrame(parent, text="Live Preview", padding=10)
        preview_frame.pack(fill=BOTH, expand=True, pady=(0, 10))

        # Preview subject
        ttk.Label(
            preview_frame,
            text="Subject:",
            font=("Segoe UI", 9, "bold")
        ).pack(anchor=W)

        self.preview_subject = ttk.Label(
            preview_frame,
            text="",
            font=("Segoe UI", 10),
            wraplength=300
        )
        self.preview_subject.pack(anchor=W, pady=(0, 15))

        ttk.Separator(preview_frame).pack(fill=X, pady=10)

        # Preview body
        ttk.Label(
            preview_frame,
            text="Body:",
            font=("Segoe UI", 9, "bold")
        ).pack(anchor=W)

        preview_scroll = ttk.Frame(preview_frame)
        preview_scroll.pack(fill=BOTH, expand=True)

        self.preview_body = ScrolledText(
            preview_scroll,
            wrap=tk.WORD,
            font=("Segoe UI", 9),
            height=15,
            state="disabled"
        )
        self.preview_body.pack(fill=BOTH, expand=True)

        # Merge tag picker
        picker_frame = ttk.LabelFrame(parent, text="Available Tags", padding=10)
        picker_frame.pack(fill=X)

        self.tag_picker = MergeTagPicker(
            picker_frame,
            on_insert=self._on_tag_insert,
            show_preview=False
        )
        self.tag_picker.pack(fill=X)

        # Fallback values
        fallback_frame = ttk.LabelFrame(parent, text="Fallback Values", padding=10)
        fallback_frame.pack(fill=X, pady=(10, 0))

        ttk.Label(
            fallback_frame,
            text="Set default values for empty fields:",
            font=("Segoe UI", 9),
            bootstyle="secondary"
        ).pack(anchor=W, pady=(0, 10))

        # FirstName fallback
        fb_row = ttk.Frame(fallback_frame)
        fb_row.pack(fill=X, pady=2)
        ttk.Label(fb_row, text="{{FirstName}}:", width=15).pack(side=LEFT)
        self.fb_firstname = tk.StringVar(value="there")
        ttk.Entry(fb_row, textvariable=self.fb_firstname, width=20).pack(side=LEFT)

        # Company fallback
        fb_row2 = ttk.Frame(fallback_frame)
        fb_row2.pack(fill=X, pady=2)
        ttk.Label(fb_row2, text="{{Company}}:", width=15).pack(side=LEFT)
        self.fb_company = tk.StringVar(value="your company")
        ttk.Entry(fb_row2, textvariable=self.fb_company, width=20).pack(side=LEFT)

    def _insert_tag_subject(self, tag: str) -> None:
        """Insert tag into subject field."""
        current = self.subject_var.get()
        cursor_pos = self.subject_entry.index(tk.INSERT)
        new_value = current[:cursor_pos] + tag + current[cursor_pos:]
        self.subject_var.set(new_value)
        self._update_preview()

    def _insert_tag_body(self, tag: str) -> None:
        """Insert tag into body text."""
        self.body_text.insert(tk.INSERT, tag)
        self._update_preview()

    def _on_tag_insert(self, tag: str) -> None:
        """Handle tag insert from picker."""
        # Insert into body by default
        self._insert_tag_body(tag)

    def _on_content_change(self, event=None) -> None:
        """Handle content change for auto-preview."""
        # Debounce preview updates
        if hasattr(self, '_preview_after_id'):
            self.after_cancel(self._preview_after_id)
        self._preview_after_id = self.after(300, self._update_preview)

    def _update_preview(self) -> None:
        """Update the preview panel."""
        subject = self.subject_var.get()
        body = self.body_text.get("1.0", "end-1c")

        # Set fallback values
        self.template_service.clear_fallbacks()
        self.template_service.set_fallback("{{FirstName}}", self.fb_firstname.get())
        self.template_service.set_fallback("{{Company}}", self.fb_company.get())

        # Render with sample data
        rendered_subject = self.template_service.preview_template(subject)
        rendered_body = self.template_service.preview_template(body)

        # Update preview
        self.preview_subject.configure(text=rendered_subject)

        self.preview_body.configure(state="normal")
        self.preview_body.delete("1.0", tk.END)
        self.preview_body.insert("1.0", rendered_body)
        self.preview_body.configure(state="disabled")

        # Validate
        self._validate_template(subject + " " + body)

    def _validate_template(self, content: str) -> None:
        """Validate template for unknown tags."""
        is_valid, unknown_tags = self.template_service.validate_template(content)

        if is_valid:
            self.validation_label.configure(
                text="\u2713 Template is valid",
                bootstyle="success"
            )
        else:
            self.validation_label.configure(
                text=f"\u26A0 Unknown tags: {', '.join(unknown_tags)}",
                bootstyle="warning"
            )

    def refresh(self) -> None:
        """Refresh view."""
        self._update_preview()

    def get_template(self) -> dict:
        """Get current template content."""
        return {
            "subject": self.subject_var.get(),
            "body": self.body_text.get("1.0", "end-1c")
        }

    def set_template(self, subject: str = "", body: str = "") -> None:
        """Set template content."""
        self.subject_var.set(subject)
        self.body_text.delete("1.0", tk.END)
        self.body_text.insert("1.0", body)
        self._update_preview()

    def clear(self) -> None:
        """Clear template."""
        self.set_template("", "")
