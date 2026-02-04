"""Campaign list view for Lead Generator Standalone."""

import tkinter as tk
from tkinter import ttk, messagebox
from typing import TYPE_CHECKING, Optional

from ui.theme import FONTS
from ui.widgets.data_table import DataTable
from services.campaign_service import CampaignService
from core.models import CampaignStatus

if TYPE_CHECKING:
    from ui.app import MainApplication


class CampaignListView(ttk.Frame):
    """Campaign list and management view."""

    def __init__(self, parent, app: 'MainApplication'):
        super().__init__(parent)
        self.app = app
        self.campaign_service = CampaignService()
        self._selected_campaign = None

        self._create_widgets()
        self.refresh()

    def _create_widgets(self) -> None:
        """Create view widgets."""
        # Header
        header_frame = ttk.Frame(self)
        header_frame.pack(fill=tk.X, pady=(0, 10))

        ttk.Label(header_frame, text="Campaigns", font=FONTS['heading']).pack(side=tk.LEFT)

        ttk.Button(
            header_frame,
            text="New Campaign",
            command=self._new_campaign
        ).pack(side=tk.RIGHT)

        # Filters
        filter_frame = ttk.Frame(self)
        filter_frame.pack(fill=tk.X, pady=(0, 10))

        ttk.Label(filter_frame, text="Status:").pack(side=tk.LEFT, padx=(0, 5))

        self.status_var = tk.StringVar(value="All")
        status_combo = ttk.Combobox(
            filter_frame,
            textvariable=self.status_var,
            values=["All", "Draft", "Active", "Paused", "Completed", "Archived"],
            state='readonly',
            width=15
        )
        status_combo.pack(side=tk.LEFT)
        status_combo.bind('<<ComboboxSelected>>', lambda e: self.refresh())

        # Campaigns table
        columns = [
            {'key': 'name', 'label': 'Campaign Name', 'width': 200},
            {'key': 'campaign_ref', 'label': 'Reference', 'width': 100},
            {'key': 'status', 'label': 'Status', 'width': 80, 'anchor': 'center'},
            {'key': 'contacts', 'label': 'Contacts', 'width': 80, 'anchor': 'center'},
            {'key': 'progress', 'label': 'Progress', 'width': 100, 'anchor': 'center'},
            {'key': 'created', 'label': 'Created', 'width': 100},
        ]

        self.table = DataTable(
            self,
            columns=columns,
            on_select=self._on_select,
            on_double_click=self._on_double_click,
            show_search=True,
            height=15
        )
        self.table.pack(fill=tk.BOTH, expand=True, pady=(0, 10))

        # Actions
        actions_frame = ttk.Frame(self)
        actions_frame.pack(fill=tk.X)

        self.edit_btn = ttk.Button(
            actions_frame,
            text="Edit",
            command=self._edit_campaign,
            state='disabled'
        )
        self.edit_btn.pack(side=tk.LEFT, padx=(0, 5))

        self.duplicate_btn = ttk.Button(
            actions_frame,
            text="Duplicate",
            command=self._duplicate_campaign,
            state='disabled'
        )
        self.duplicate_btn.pack(side=tk.LEFT, padx=(0, 5))

        self.delete_btn = ttk.Button(
            actions_frame,
            text="Delete",
            command=self._delete_campaign,
            state='disabled'
        )
        self.delete_btn.pack(side=tk.LEFT, padx=(0, 20))

        # Campaign status actions
        self.activate_btn = ttk.Button(
            actions_frame,
            text="Activate",
            command=self._activate_campaign,
            state='disabled'
        )
        self.activate_btn.pack(side=tk.LEFT, padx=(0, 5))

        self.pause_btn = ttk.Button(
            actions_frame,
            text="Pause",
            command=self._pause_campaign,
            state='disabled'
        )
        self.pause_btn.pack(side=tk.LEFT, padx=(0, 5))

        self.complete_btn = ttk.Button(
            actions_frame,
            text="Complete",
            command=self._complete_campaign,
            state='disabled'
        )
        self.complete_btn.pack(side=tk.LEFT)

    def refresh(self) -> None:
        """Refresh campaign list."""
        status_filter = self.status_var.get()
        if status_filter == "All":
            status_filter = None

        campaigns = self.campaign_service.get_all_campaigns(status_filter=status_filter)

        data = []
        for campaign in campaigns:
            stats = campaign.stats or {}
            total = stats.get('total_contacts', 0)
            sent = stats.get('emails_sent', 0)
            progress = f"{(sent / total * 100):.0f}%" if total > 0 else "0%"

            data.append({
                'id': campaign.campaign_id,
                'name': campaign.name,
                'campaign_ref': campaign.campaign_ref,
                'status': campaign.status,
                'contacts': total,
                'progress': progress,
                'created': campaign.created_at[:10] if campaign.created_at else ''
            })

        self.table.set_data(data)
        self._update_button_states()

    def _on_select(self, item: dict) -> None:
        """Handle row selection."""
        self._selected_campaign = item
        self._update_button_states()

    def _on_double_click(self, item: dict) -> None:
        """Handle row double-click."""
        self._edit_campaign()

    def _update_button_states(self) -> None:
        """Update action button states based on selection."""
        if self._selected_campaign:
            status = self._selected_campaign.get('status', '')

            self.edit_btn.configure(state='normal')
            self.duplicate_btn.configure(state='normal')

            # Delete only for non-active
            if status != 'Active':
                self.delete_btn.configure(state='normal')
            else:
                self.delete_btn.configure(state='disabled')

            # Activate for Draft/Paused
            if status in ['Draft', 'Paused']:
                self.activate_btn.configure(state='normal')
            else:
                self.activate_btn.configure(state='disabled')

            # Pause for Active
            if status == 'Active':
                self.pause_btn.configure(state='normal')
            else:
                self.pause_btn.configure(state='disabled')

            # Complete for Active/Paused
            if status in ['Active', 'Paused']:
                self.complete_btn.configure(state='normal')
            else:
                self.complete_btn.configure(state='disabled')
        else:
            # Disable all when nothing selected
            for btn in [self.edit_btn, self.duplicate_btn, self.delete_btn,
                        self.activate_btn, self.pause_btn, self.complete_btn]:
                btn.configure(state='disabled')

    def _new_campaign(self) -> None:
        """Create new campaign."""
        try:
            from ui.dialogs.campaign_wizard import CampaignWizard
            wizard = CampaignWizard(self.winfo_toplevel())
            if wizard.result:
                self.refresh()
        except ImportError:
            # Simple fallback dialog
            self._simple_new_campaign()

    def _simple_new_campaign(self) -> None:
        """Simple new campaign dialog."""
        from tkinter import simpledialog
        name = simpledialog.askstring("New Campaign", "Campaign Name:")
        if name:
            try:
                self.campaign_service.create_campaign({'name': name})
                self.refresh()
                messagebox.showinfo("Success", f"Campaign '{name}' created")
            except Exception as e:
                messagebox.showerror("Error", str(e))

    def _edit_campaign(self) -> None:
        """Edit selected campaign."""
        if not self._selected_campaign:
            return
        # For now, show simple edit - could open detail view
        try:
            from ui.views.campaign_detail_view import CampaignDetailView
            # Switch to detail view
            self._show_detail_view(self._selected_campaign['id'])
        except ImportError:
            messagebox.showinfo("Edit", f"Edit campaign: {self._selected_campaign['name']}")

    def _show_detail_view(self, campaign_id: int) -> None:
        """Show campaign detail view."""
        # This would typically switch to a detail view
        # For now, just refresh
        self.refresh()

    def _duplicate_campaign(self) -> None:
        """Duplicate selected campaign."""
        if not self._selected_campaign:
            return

        if messagebox.askyesno("Duplicate", f"Duplicate campaign '{self._selected_campaign['name']}'?"):
            try:
                new_campaign = self.campaign_service.duplicate_campaign(self._selected_campaign['id'])
                self.refresh()
                messagebox.showinfo("Success", f"Campaign duplicated as '{new_campaign.name}'")
            except Exception as e:
                messagebox.showerror("Error", str(e))

    def _delete_campaign(self) -> None:
        """Delete selected campaign."""
        if not self._selected_campaign:
            return

        if messagebox.askyesno("Delete", f"Delete campaign '{self._selected_campaign['name']}'?\nThis cannot be undone."):
            try:
                self.campaign_service.delete_campaign(self._selected_campaign['id'])
                self._selected_campaign = None
                self.refresh()
            except Exception as e:
                messagebox.showerror("Error", str(e))

    def _activate_campaign(self) -> None:
        """Activate selected campaign."""
        if not self._selected_campaign:
            return

        if messagebox.askyesno("Activate", f"Activate campaign '{self._selected_campaign['name']}'?\nEmails will start sending."):
            try:
                self.campaign_service.activate_campaign(self._selected_campaign['id'])
                self.refresh()
                messagebox.showinfo("Success", "Campaign activated")
            except Exception as e:
                messagebox.showerror("Error", str(e))

    def _pause_campaign(self) -> None:
        """Pause selected campaign."""
        if not self._selected_campaign:
            return

        try:
            self.campaign_service.pause_campaign(self._selected_campaign['id'])
            self.refresh()
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def _complete_campaign(self) -> None:
        """Complete selected campaign."""
        if not self._selected_campaign:
            return

        if messagebox.askyesno("Complete", f"Mark campaign '{self._selected_campaign['name']}' as completed?"):
            try:
                self.campaign_service.complete_campaign(self._selected_campaign['id'])
                self.refresh()
            except Exception as e:
                messagebox.showerror("Error", str(e))
