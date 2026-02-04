"""Campaign list view."""
import logging
import tkinter as tk
from typing import Optional
import ttkbootstrap as ttk
from ttkbootstrap.constants import *

from core.api_client import ApiClient
from core.models import CampaignStatus
from ui.widgets.data_table import DataTable

logger = logging.getLogger(__name__)


class CampaignListView(ttk.Frame):
    """Campaign list with filters and actions."""

    def __init__(self, parent, app=None, api: ApiClient = None, **kwargs):
        super().__init__(parent, **kwargs)

        self.app = app
        self.api = api

        self._create_widgets()

    def _create_widgets(self) -> None:
        """Create view widgets."""
        # Header with filters
        header = ttk.Frame(self)
        header.pack(fill=X, pady=(0, 15))

        # Status filter
        filter_frame = ttk.Frame(header)
        filter_frame.pack(side=LEFT)

        ttk.Label(filter_frame, text="Status:").pack(side=LEFT, padx=(0, 5))

        self.status_var = tk.StringVar(value="All")
        status_combo = ttk.Combobox(
            filter_frame,
            textvariable=self.status_var,
            values=["All", "Active", "Paused", "Draft", "Completed", "Cancelled"],
            state="readonly",
            width=12
        )
        status_combo.pack(side=LEFT)
        status_combo.bind("<<ComboboxSelected>>", lambda e: self._apply_filter())

        # Show my campaigns only
        self.my_campaigns_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(
            filter_frame,
            text="My campaigns only",
            variable=self.my_campaigns_var,
            command=self.refresh
        ).pack(side=LEFT, padx=(20, 0))

        # Action buttons
        actions = ttk.Frame(header)
        actions.pack(side=RIGHT)

        ttk.Button(
            actions,
            text="+ New Campaign",
            bootstyle="success",
            command=self._on_new_campaign
        ).pack(side=LEFT, padx=5)

        # Campaigns table
        columns = [
            {"id": "id", "text": "ID", "width": 0},
            {"id": "ref", "text": "Reference", "width": 120, "anchor": "w"},
            {"id": "name", "text": "Campaign Name", "width": 250, "anchor": "w"},
            {"id": "status", "text": "Status", "width": 100, "anchor": "center"},
            {"id": "contacts", "text": "Contacts", "width": 80, "anchor": "center"},
            {"id": "sent", "text": "Sent", "width": 80, "anchor": "center"},
            {"id": "response", "text": "Response", "width": 80, "anchor": "center"},
            {"id": "created", "text": "Created", "width": 100, "anchor": "center"},
        ]

        self.table = DataTable(
            self,
            columns=columns,
            show_search=True,
            on_select=self._on_select,
            on_double_click=self._on_double_click
        )
        self.table.pack(fill=BOTH, expand=True)

        # Bottom actions
        bottom = ttk.Frame(self)
        bottom.pack(fill=X, pady=(10, 0))

        self.selected_label = ttk.Label(
            bottom,
            text="Select a campaign",
            font=("Segoe UI", 9),
            bootstyle="secondary"
        )
        self.selected_label.pack(side=LEFT)

        self.delete_btn = ttk.Button(
            bottom,
            text="Delete",
            bootstyle="danger-outline",
            command=self._on_delete,
            state="disabled"
        )
        self.delete_btn.pack(side=RIGHT, padx=5)

        self.pause_btn = ttk.Button(
            bottom,
            text="Pause",
            bootstyle="warning-outline",
            command=self._on_pause,
            state="disabled"
        )
        self.pause_btn.pack(side=RIGHT, padx=5)

        self.activate_btn = ttk.Button(
            bottom,
            text="Activate",
            bootstyle="success-outline",
            command=self._on_activate,
            state="disabled"
        )
        self.activate_btn.pack(side=RIGHT, padx=5)

        self.edit_btn = ttk.Button(
            bottom,
            text="Edit",
            bootstyle="primary-outline",
            command=self._on_edit,
            state="disabled"
        )
        self.edit_btn.pack(side=RIGHT, padx=5)

    def refresh(self) -> None:
        """Refresh campaign list."""
        if not self.api:
            return

        try:
            only_mine = self.my_campaigns_var.get()
            campaigns = self.api.get_campaigns(only_mine=only_mine)

            data = []
            for c in campaigns:
                created = c.created_at.strftime("%Y-%m-%d") if c.created_at else ""
                data.append({
                    "id": c.campaign_id,
                    "ref": c.campaign_ref,
                    "name": c.name,
                    "status": c.status.value,
                    "contacts": str(c.total_contacts),
                    "sent": str(c.emails_sent),
                    "response": f"{c.response_rate:.1f}%",
                    "created": created
                })

            self.table.set_data(data)
            self._apply_filter()

            if self.app:
                self.app.set_status(f"Loaded {len(campaigns)} campaigns")

        except Exception as e:
            logger.error(f"Error loading campaigns: {e}")
            if self.app:
                self.app.set_status(f"Error: {str(e)}")

    def _apply_filter(self) -> None:
        """Apply status filter."""
        status = self.status_var.get()
        if status == "All":
            return

        data = self.table.get_data()
        filtered = [row for row in data if row.get("status") == status]
        self.table.set_data(filtered)

    def _on_select(self, campaign_id: str) -> None:
        """Handle campaign selection."""
        selected = self.table.get_selected()
        if selected:
            self.selected_label.configure(text=f"Selected: {selected.get('name', '')}")
            self.edit_btn.configure(state="normal")

            status = selected.get("status", "")
            if status == "Active":
                self.activate_btn.configure(state="disabled")
                self.pause_btn.configure(state="normal")
            elif status in ["Paused", "Draft"]:
                self.activate_btn.configure(state="normal")
                self.pause_btn.configure(state="disabled")
            else:
                self.activate_btn.configure(state="disabled")
                self.pause_btn.configure(state="disabled")

            # Only admin can delete
            if self.api and self.api.auth.is_admin():
                self.delete_btn.configure(state="normal")

    def _on_double_click(self, campaign_id: str) -> None:
        """Handle double-click to open campaign."""
        if self.app:
            self.app.show_view("campaign_detail_view", campaign_id=campaign_id)

    def _on_new_campaign(self) -> None:
        """Create new campaign."""
        dialog = CampaignFormDialog(self, self.api)
        self.wait_window(dialog)
        if dialog.result:
            self.refresh()

    def _on_edit(self) -> None:
        """Edit selected campaign."""
        campaign_id = self.table.get_selected_id()
        if campaign_id and self.app:
            self.app.show_view("campaign_detail_view", campaign_id=campaign_id)

    def _on_activate(self) -> None:
        """Activate selected campaign."""
        campaign_id = self.table.get_selected_id()
        if campaign_id and self.api:
            try:
                self.api.activate_campaign(campaign_id)
                self.refresh()
                if self.app:
                    self.app.set_status("Campaign activated")
            except Exception as e:
                if self.app:
                    self.app.show_error("Error", str(e))

    def _on_pause(self) -> None:
        """Pause selected campaign."""
        campaign_id = self.table.get_selected_id()
        if campaign_id and self.api:
            try:
                self.api.pause_campaign(campaign_id)
                self.refresh()
                if self.app:
                    self.app.set_status("Campaign paused")
            except Exception as e:
                if self.app:
                    self.app.show_error("Error", str(e))

    def _on_delete(self) -> None:
        """Delete selected campaign."""
        campaign_id = self.table.get_selected_id()
        selected = self.table.get_selected()
        if not campaign_id or not selected:
            return

        if self.app:
            confirm = self.app.ask_confirmation(
                "Delete Campaign",
                f"Are you sure you want to delete '{selected.get('name')}'?"
            )
            if confirm:
                try:
                    self.api.delete_campaign(campaign_id)
                    self.refresh()
                    self.app.set_status("Campaign deleted")
                except Exception as e:
                    self.app.show_error("Error", str(e))


class CampaignFormDialog(ttk.Toplevel):
    """Dialog for creating/editing campaigns."""

    def __init__(self, parent, api: ApiClient, campaign_id: Optional[str] = None):
        super().__init__(parent)

        self.api = api
        self.campaign_id = campaign_id
        self.result = None

        self.title("New Campaign" if not campaign_id else "Edit Campaign")
        self.geometry("500x600")
        self.resizable(False, False)

        self._create_widgets()

        if campaign_id:
            self._load_campaign()

        self.transient(parent)
        self.grab_set()

    def _create_widgets(self) -> None:
        """Create dialog widgets."""
        main = ttk.Frame(self, padding=20)
        main.pack(fill=BOTH, expand=True)

        # Name
        ttk.Label(main, text="Campaign Name *").pack(anchor=W, pady=(0, 5))
        self.name_var = tk.StringVar()
        ttk.Entry(main, textvariable=self.name_var, width=50).pack(fill=X, pady=(0, 15))

        # Description
        ttk.Label(main, text="Description").pack(anchor=W, pady=(0, 5))
        self.desc_text = tk.Text(main, height=3, width=50)
        self.desc_text.pack(fill=X, pady=(0, 15))

        # Contact List
        ttk.Label(main, text="Contact List").pack(anchor=W, pady=(0, 5))
        self.list_var = tk.StringVar()
        self.list_combo = ttk.Combobox(
            main,
            textvariable=self.list_var,
            state="readonly",
            width=47
        )
        self.list_combo.pack(fill=X, pady=(0, 15))
        self._load_contact_lists()

        # Sending settings
        settings_frame = ttk.LabelFrame(main, text="Sending Settings", padding=10)
        settings_frame.pack(fill=X, pady=(0, 15))

        # Daily limit
        row1 = ttk.Frame(settings_frame)
        row1.pack(fill=X, pady=5)
        ttk.Label(row1, text="Daily Send Limit:").pack(side=LEFT)
        self.daily_limit_var = tk.StringVar(value="100")
        ttk.Entry(row1, textvariable=self.daily_limit_var, width=10).pack(side=RIGHT)

        # Email delay
        row2 = ttk.Frame(settings_frame)
        row2.pack(fill=X, pady=5)
        ttk.Label(row2, text="Delay Between Emails (min):").pack(side=LEFT)
        self.delay_var = tk.StringVar(value="5")
        ttk.Entry(row2, textvariable=self.delay_var, width=10).pack(side=RIGHT)

        # Sending window
        row3 = ttk.Frame(settings_frame)
        row3.pack(fill=X, pady=5)
        ttk.Label(row3, text="Sending Window:").pack(side=LEFT)
        self.end_var = tk.StringVar(value="17:00")
        ttk.Entry(row3, textvariable=self.end_var, width=8).pack(side=RIGHT)
        ttk.Label(row3, text=" to ").pack(side=RIGHT)
        self.start_var = tk.StringVar(value="09:00")
        ttk.Entry(row3, textvariable=self.start_var, width=8).pack(side=RIGHT)

        # Buttons
        btn_frame = ttk.Frame(main)
        btn_frame.pack(fill=X, pady=(20, 0))

        ttk.Button(
            btn_frame,
            text="Cancel",
            bootstyle="secondary",
            command=self.destroy
        ).pack(side=RIGHT, padx=5)

        ttk.Button(
            btn_frame,
            text="Save",
            bootstyle="primary",
            command=self._on_save
        ).pack(side=RIGHT)

    def _load_contact_lists(self) -> None:
        """Load contact lists for dropdown."""
        try:
            lists = self.api.get_contact_lists()
            self._contact_lists = {cl.name: cl.list_id for cl in lists}
            self.list_combo['values'] = list(self._contact_lists.keys())
        except Exception:
            self._contact_lists = {}

    def _load_campaign(self) -> None:
        """Load existing campaign data."""
        try:
            campaign = self.api.get_campaign(self.campaign_id)
            self.name_var.set(campaign.name)
            self.desc_text.insert("1.0", campaign.description or "")
            self.daily_limit_var.set(str(campaign.daily_send_limit))
            self.delay_var.set(str(campaign.inter_email_delay_minutes))
            self.start_var.set(campaign.sending_window_start or "09:00")
            self.end_var.set(campaign.sending_window_end or "17:00")
        except Exception as e:
            logger.error(f"Error loading campaign: {e}")

    def _on_save(self) -> None:
        """Save campaign."""
        name = self.name_var.get().strip()
        if not name:
            return

        description = self.desc_text.get("1.0", "end-1c").strip()
        list_name = self.list_var.get()
        list_id = self._contact_lists.get(list_name) if list_name else None

        try:
            if self.campaign_id:
                self.api.update_campaign(
                    self.campaign_id,
                    name=name,
                    description=description,
                    contactListId=list_id,
                    dailySendLimit=int(self.daily_limit_var.get()),
                    interEmailDelayMinutes=int(self.delay_var.get()),
                    sendingWindowStart=self.start_var.get(),
                    sendingWindowEnd=self.end_var.get()
                )
            else:
                self.api.create_campaign(
                    name=name,
                    description=description,
                    contact_list_id=list_id,
                    dailySendLimit=int(self.daily_limit_var.get()),
                    interEmailDelayMinutes=int(self.delay_var.get()),
                    sendingWindowStart=self.start_var.get(),
                    sendingWindowEnd=self.end_var.get()
                )

            self.result = True
            self.destroy()

        except Exception as e:
            from tkinter import messagebox
            messagebox.showerror("Error", str(e), parent=self)
