"""Template editor view for Lead Generator Standalone."""

import tkinter as tk
from tkinter import ttk, messagebox
from typing import TYPE_CHECKING, Optional

from ui.theme import FONTS
from ui.widgets.merge_tag_picker import MergeTagPicker
from services.campaign_service import CampaignService
from services.template_service import TemplateService

if TYPE_CHECKING:
    from ui.app import MainApplication


class TemplateEditorView(ttk.Frame):
    """Email template editor view."""

    def __init__(self, parent, app: 'MainApplication'):
        super().__init__(parent)
        self.app = app
        self.campaign_service = CampaignService()
        self.template_service = TemplateService()
        self._selected_step = None

        self._create_widgets()
        self.refresh_campaigns()

    def _create_widgets(self) -> None:
        """Create view widgets."""
        # Main paned window
        paned = ttk.PanedWindow(self, orient=tk.HORIZONTAL)
        paned.pack(fill=tk.BOTH, expand=True)

        # Left panel - Campaign/Step tree
        left_frame = ttk.Frame(paned, width=250)
        paned.add(left_frame, weight=1)

        ttk.Label(left_frame, text="Campaigns & Steps", font=FONTS['subheading']).pack(anchor='w', pady=(0, 10))

        # Treeview for campaigns and steps
        tree_frame = ttk.Frame(left_frame)
        tree_frame.pack(fill=tk.BOTH, expand=True)

        self.tree = ttk.Treeview(tree_frame, show='tree')
        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.tree.bind('<<TreeviewSelect>>', self._on_tree_select)

        scrollbar = ttk.Scrollbar(tree_frame, orient=tk.VERTICAL, command=self.tree.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.tree.configure(yscrollcommand=scrollbar.set)

        # Step buttons
        btn_frame = ttk.Frame(left_frame)
        btn_frame.pack(fill=tk.X, pady=(10, 0))

        ttk.Button(btn_frame, text="Add Step", command=self._add_step).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(btn_frame, text="Delete Step", command=self._delete_step).pack(side=tk.LEFT)

        # Right panel - Editor
        right_frame = ttk.Frame(paned)
        paned.add(right_frame, weight=3)

        # Subject
        ttk.Label(right_frame, text="Subject Line:", font=FONTS['subheading']).pack(anchor='w', pady=(0, 5))
        self.subject_var = tk.StringVar()
        self.subject_entry = ttk.Entry(right_frame, textvariable=self.subject_var, width=80)
        self.subject_entry.pack(fill=tk.X, pady=(0, 10))

        # Body editor frame
        body_frame = ttk.Frame(right_frame)
        body_frame.pack(fill=tk.BOTH, expand=True)

        # Body editor
        editor_frame = ttk.Frame(body_frame)
        editor_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        ttk.Label(editor_frame, text="Email Body:", font=FONTS['subheading']).pack(anchor='w', pady=(0, 5))

        text_frame = ttk.Frame(editor_frame)
        text_frame.pack(fill=tk.BOTH, expand=True)

        self.body_text = tk.Text(text_frame, wrap=tk.WORD, font=('Consolas', 10))
        self.body_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        body_scroll = ttk.Scrollbar(text_frame, orient=tk.VERTICAL, command=self.body_text.yview)
        body_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        self.body_text.configure(yscrollcommand=body_scroll.set)

        # Merge tag picker
        tags_frame = ttk.Frame(body_frame, width=200)
        tags_frame.pack(side=tk.RIGHT, fill=tk.Y, padx=(10, 0))

        self.tag_picker = MergeTagPicker(
            tags_frame,
            on_tag_selected=self._insert_tag
        )
        self.tag_picker.pack(fill=tk.BOTH, expand=True)

        # Preview and Save buttons
        action_frame = ttk.Frame(right_frame)
        action_frame.pack(fill=tk.X, pady=(10, 0))

        ttk.Button(action_frame, text="Preview", command=self._preview).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(action_frame, text="Save", command=self._save).pack(side=tk.LEFT)

        # Delay setting
        delay_frame = ttk.Frame(action_frame)
        delay_frame.pack(side=tk.RIGHT)

        ttk.Label(delay_frame, text="Delay (days):").pack(side=tk.LEFT, padx=(0, 5))
        self.delay_var = tk.IntVar(value=0)
        ttk.Spinbox(delay_frame, from_=0, to=30, textvariable=self.delay_var, width=5).pack(side=tk.LEFT)

    def refresh_campaigns(self) -> None:
        """Refresh campaign tree."""
        # Clear tree
        for item in self.tree.get_children():
            self.tree.delete(item)

        # Load campaigns
        campaigns = self.campaign_service.get_all_campaigns()

        for campaign in campaigns:
            # Add campaign node
            campaign_id = self.tree.insert('', 'end', text=f"{campaign.name} [{campaign.campaign_ref}]")

            # Add step nodes
            steps = self.template_service.get_steps(campaign.campaign_id)
            for step in steps:
                self.tree.insert(
                    campaign_id, 'end',
                    text=f"Step {step.step_number}: {step.subject_template[:30]}...",
                    values=(step.step_id,)
                )

    def _on_tree_select(self, event) -> None:
        """Handle tree selection."""
        selection = self.tree.selection()
        if not selection:
            return

        item = selection[0]
        values = self.tree.item(item, 'values')

        if values:
            # It's a step
            step_id = int(values[0])
            self._load_step(step_id)
        else:
            # It's a campaign - clear editor
            self._clear_editor()

    def _load_step(self, step_id: int) -> None:
        """Load step into editor."""
        step = self.template_service.get_step(step_id)
        if step:
            self._selected_step = step
            self.subject_var.set(step.subject_template)
            self.body_text.delete('1.0', tk.END)
            self.body_text.insert('1.0', step.body_template)
            self.delay_var.set(step.delay_days)

    def _clear_editor(self) -> None:
        """Clear editor fields."""
        self._selected_step = None
        self.subject_var.set('')
        self.body_text.delete('1.0', tk.END)
        self.delay_var.set(0)

    def _insert_tag(self, tag: str) -> None:
        """Insert merge tag at cursor position."""
        self.body_text.insert(tk.INSERT, tag)
        self.body_text.focus_set()

    def _add_step(self) -> None:
        """Add new step to selected campaign."""
        selection = self.tree.selection()
        if not selection:
            messagebox.showwarning("Warning", "Select a campaign first")
            return

        # Find the campaign
        item = selection[0]
        parent = self.tree.parent(item)
        campaign_item = parent if parent else item

        # Get campaign ID from text (parse from reference)
        campaign_text = self.tree.item(campaign_item, 'text')
        # Find the campaign by name
        campaigns = self.campaign_service.get_all_campaigns()
        campaign = None
        for c in campaigns:
            if f"[{c.campaign_ref}]" in campaign_text:
                campaign = c
                break

        if not campaign:
            messagebox.showerror("Error", "Campaign not found")
            return

        # Get next step number
        steps = self.template_service.get_steps(campaign.campaign_id)
        next_num = len(steps) + 1

        try:
            self.template_service.create_step(
                campaign.campaign_id,
                next_num,
                f"Step {next_num} Subject",
                "Your email body here...",
                3  # Default delay
            )
            self.refresh_campaigns()
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def _delete_step(self) -> None:
        """Delete selected step."""
        if not self._selected_step:
            messagebox.showwarning("Warning", "Select a step first")
            return

        if messagebox.askyesno("Delete", "Delete this step?"):
            try:
                self.template_service.delete_step(self._selected_step.step_id)
                self._clear_editor()
                self.refresh_campaigns()
            except Exception as e:
                messagebox.showerror("Error", str(e))

    def _preview(self) -> None:
        """Preview template with sample data."""
        subject = self.subject_var.get()
        body = self.body_text.get('1.0', tk.END)

        rendered_subject = self.template_service.render_preview(subject)
        rendered_body = self.template_service.render_preview(body)

        # Show preview dialog
        preview_window = tk.Toplevel(self)
        preview_window.title("Template Preview")
        preview_window.geometry("600x400")

        ttk.Label(preview_window, text="Subject:", font=FONTS['subheading']).pack(anchor='w', padx=10, pady=(10, 5))
        ttk.Label(preview_window, text=rendered_subject).pack(anchor='w', padx=10)

        ttk.Label(preview_window, text="Body:", font=FONTS['subheading']).pack(anchor='w', padx=10, pady=(10, 5))

        body_text = tk.Text(preview_window, wrap=tk.WORD, height=15)
        body_text.pack(fill=tk.BOTH, expand=True, padx=10, pady=(0, 10))
        body_text.insert('1.0', rendered_body)
        body_text.configure(state='disabled')

        ttk.Button(preview_window, text="Close", command=preview_window.destroy).pack(pady=10)

    def _save(self) -> None:
        """Save current step."""
        if not self._selected_step:
            messagebox.showwarning("Warning", "No step selected")
            return

        try:
            self.template_service.update_step(self._selected_step.step_id, {
                'subject_template': self.subject_var.get(),
                'body_template': self.body_text.get('1.0', tk.END).strip(),
                'delay_days': self.delay_var.get()
            })
            messagebox.showinfo("Success", "Step saved")
            self.refresh_campaigns()
        except Exception as e:
            messagebox.showerror("Error", str(e))
