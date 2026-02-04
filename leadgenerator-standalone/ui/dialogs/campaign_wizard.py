"""Campaign creation wizard for Lead Generator Standalone."""

import tkinter as tk
from tkinter import ttk, messagebox
from typing import Optional

from ui.theme import FONTS
from services.campaign_service import CampaignService
from services.contact_service import ContactService


class CampaignWizard(tk.Toplevel):
    """Campaign creation wizard dialog."""

    def __init__(self, parent):
        super().__init__(parent)
        self.title("New Campaign")
        self.campaign_service = CampaignService()
        self.contact_service = ContactService()
        self.result = None

        self._current_step = 1
        self._campaign_data = {}

        # Make modal
        self.transient(parent)
        self.grab_set()

        self.geometry("500x400")
        self.resizable(False, False)

        self._create_widgets()
        self._show_step_1()

        self.wait_window()

    def _create_widgets(self) -> None:
        """Create wizard widgets."""
        # Step indicator
        self.step_frame = ttk.Frame(self)
        self.step_frame.pack(fill=tk.X, padx=20, pady=10)

        self.step_labels = []
        for i, text in enumerate(["1. Details", "2. Contact List", "3. Review"], 1):
            label = ttk.Label(self.step_frame, text=text)
            label.pack(side=tk.LEFT, padx=10)
            self.step_labels.append(label)

        ttk.Separator(self, orient=tk.HORIZONTAL).pack(fill=tk.X)

        # Content area
        self.content_frame = ttk.Frame(self)
        self.content_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)

        # Navigation buttons
        nav_frame = ttk.Frame(self)
        nav_frame.pack(fill=tk.X, padx=20, pady=10)

        self.cancel_btn = ttk.Button(nav_frame, text="Cancel", command=self.destroy)
        self.cancel_btn.pack(side=tk.LEFT)

        self.next_btn = ttk.Button(nav_frame, text="Next", command=self._next_step)
        self.next_btn.pack(side=tk.RIGHT)

        self.back_btn = ttk.Button(nav_frame, text="Back", command=self._prev_step, state='disabled')
        self.back_btn.pack(side=tk.RIGHT, padx=(0, 10))

    def _update_step_indicators(self) -> None:
        """Update step indicator styles."""
        for i, label in enumerate(self.step_labels, 1):
            if i == self._current_step:
                label.configure(font=('Segoe UI', 10, 'bold'))
            else:
                label.configure(font=('Segoe UI', 10))

    def _show_step_1(self) -> None:
        """Show step 1: Campaign details."""
        self._current_step = 1
        self._update_step_indicators()
        self._clear_content()

        ttk.Label(self.content_frame, text="Campaign Details", font=FONTS['subheading']).pack(anchor='w', pady=(0, 20))

        # Name
        ttk.Label(self.content_frame, text="Campaign Name:").pack(anchor='w', pady=(0, 5))
        self.name_var = tk.StringVar(value=self._campaign_data.get('name', ''))
        ttk.Entry(self.content_frame, textvariable=self.name_var, width=50).pack(anchor='w', pady=(0, 15))

        # Description
        ttk.Label(self.content_frame, text="Description (optional):").pack(anchor='w', pady=(0, 5))
        self.desc_text = tk.Text(self.content_frame, width=50, height=5)
        self.desc_text.pack(anchor='w')
        if self._campaign_data.get('description'):
            self.desc_text.insert('1.0', self._campaign_data['description'])

        self.back_btn.configure(state='disabled')
        self.next_btn.configure(text="Next")

    def _show_step_2(self) -> None:
        """Show step 2: Select contact list."""
        # Save step 1 data
        self._campaign_data['name'] = self.name_var.get()
        self._campaign_data['description'] = self.desc_text.get('1.0', tk.END).strip()

        if not self._campaign_data['name']:
            messagebox.showwarning("Validation", "Campaign name is required")
            return

        self._current_step = 2
        self._update_step_indicators()
        self._clear_content()

        ttk.Label(self.content_frame, text="Select Contact List", font=FONTS['subheading']).pack(anchor='w', pady=(0, 20))

        # Load contact lists
        lists = self.contact_service.get_all_lists()

        if not lists:
            ttk.Label(self.content_frame, text="No contact lists available.\nCreate a list first in the Contacts section.").pack(anchor='w')
            self.next_btn.configure(state='disabled')
        else:
            self.list_var = tk.IntVar(value=self._campaign_data.get('contact_list_id', 0))

            for contact_list in lists:
                rb = ttk.Radiobutton(
                    self.content_frame,
                    text=f"{contact_list.name} ({contact_list.contact_count} contacts)",
                    variable=self.list_var,
                    value=contact_list.list_id
                )
                rb.pack(anchor='w', pady=2)

            if self.list_var.get() == 0 and lists:
                self.list_var.set(lists[0].list_id)

            self.next_btn.configure(state='normal')

        self.back_btn.configure(state='normal')
        self.next_btn.configure(text="Next")

    def _show_step_3(self) -> None:
        """Show step 3: Review and create."""
        # Save step 2 data
        if hasattr(self, 'list_var'):
            self._campaign_data['contact_list_id'] = self.list_var.get()

        self._current_step = 3
        self._update_step_indicators()
        self._clear_content()

        ttk.Label(self.content_frame, text="Review Campaign", font=FONTS['subheading']).pack(anchor='w', pady=(0, 20))

        # Get contact list name
        list_name = "None"
        if self._campaign_data.get('contact_list_id'):
            contact_list = self.contact_service.get_list(self._campaign_data['contact_list_id'])
            if contact_list:
                list_name = f"{contact_list.name} ({contact_list.contact_count} contacts)"

        # Display summary
        summary = f"""
Name: {self._campaign_data.get('name', '')}

Description: {self._campaign_data.get('description', '') or '(none)'}

Contact List: {list_name}

The campaign will be created as a Draft.
You can add email steps and then activate it.
        """

        ttk.Label(self.content_frame, text=summary, justify=tk.LEFT).pack(anchor='w')

        self.back_btn.configure(state='normal')
        self.next_btn.configure(text="Create Campaign")

    def _clear_content(self) -> None:
        """Clear content frame."""
        for widget in self.content_frame.winfo_children():
            widget.destroy()

    def _next_step(self) -> None:
        """Go to next step or create campaign."""
        if self._current_step == 1:
            self._show_step_2()
        elif self._current_step == 2:
            self._show_step_3()
        elif self._current_step == 3:
            self._create_campaign()

    def _prev_step(self) -> None:
        """Go to previous step."""
        if self._current_step == 2:
            self._show_step_1()
        elif self._current_step == 3:
            self._show_step_2()

    def _create_campaign(self) -> None:
        """Create the campaign."""
        try:
            campaign = self.campaign_service.create_campaign(self._campaign_data)
            self.result = campaign
            messagebox.showinfo("Success", f"Campaign '{campaign.name}' created successfully!\nReference: {campaign.campaign_ref}")
            self.destroy()
        except Exception as e:
            messagebox.showerror("Error", str(e))
