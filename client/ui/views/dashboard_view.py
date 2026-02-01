"""Dashboard view with KPIs and active campaigns."""
import logging
import tkinter as tk
from typing import Optional
import ttkbootstrap as ttk
from ttkbootstrap.constants import *

from core.api_client import ApiClient
from core.models import Campaign, CampaignStatus
from ui.widgets.progress_card import KPICard, KPICardGrid
from ui.widgets.data_table import DataTable
from ui.widgets.status_badge import StatusBadge

logger = logging.getLogger(__name__)


class DashboardView(ttk.Frame):
    """Dashboard view with KPIs and campaign overview."""

    def __init__(self, parent, app=None, api: ApiClient = None, **kwargs):
        super().__init__(parent, **kwargs)

        self.app = app
        self.api = api

        self._create_widgets()

    def _create_widgets(self) -> None:
        """Create dashboard widgets."""
        # KPI Cards
        kpi_frame = ttk.Frame(self)
        kpi_frame.pack(fill=X, pady=(0, 20))

        self.kpi_grid = KPICardGrid(kpi_frame, columns=4)
        self.kpi_grid.pack(fill=X)

        self.kpi_grid.add_card(
            "active_campaigns",
            title="Active Campaigns",
            value=0,
            icon="\u2709",
            color="primary"
        )

        self.kpi_grid.add_card(
            "total_contacts",
            title="Total Contacts",
            value=0,
            icon="\u263A",
            color="info"
        )

        self.kpi_grid.add_card(
            "emails_sent",
            title="Emails Sent (30d)",
            value=0,
            icon="\u2192",
            color="success"
        )

        self.kpi_grid.add_card(
            "response_rate",
            title="Response Rate",
            value="0%",
            icon="\u2713",
            color="warning",
            format_type="percentage"
        )

        # Active Campaigns Section
        campaigns_header = ttk.Frame(self)
        campaigns_header.pack(fill=X, pady=(10, 10))

        ttk.Label(
            campaigns_header,
            text="Active Campaigns",
            font=("Segoe UI", 14, "bold")
        ).pack(side=LEFT)

        ttk.Button(
            campaigns_header,
            text="View All",
            bootstyle="link",
            command=self._on_view_all_campaigns
        ).pack(side=RIGHT)

        # Campaigns table
        columns = [
            {"id": "id", "text": "ID", "width": 0, "anchor": "w"},  # Hidden
            {"id": "ref", "text": "Reference", "width": 120, "anchor": "w"},
            {"id": "name", "text": "Campaign Name", "width": 250, "anchor": "w"},
            {"id": "status", "text": "Status", "width": 100, "anchor": "center"},
            {"id": "contacts", "text": "Contacts", "width": 100, "anchor": "center"},
            {"id": "sent", "text": "Emails Sent", "width": 100, "anchor": "center"},
            {"id": "progress", "text": "Progress", "width": 100, "anchor": "center"},
        ]

        self.campaigns_table = DataTable(
            self,
            columns=columns,
            show_search=False,
            on_double_click=self._on_campaign_double_click
        )
        self.campaigns_table.pack(fill=BOTH, expand=True)

        # Quick actions
        actions_frame = ttk.Frame(self)
        actions_frame.pack(fill=X, pady=(15, 0))

        ttk.Label(
            actions_frame,
            text="Quick Actions",
            font=("Segoe UI", 12, "bold")
        ).pack(side=LEFT)

        ttk.Button(
            actions_frame,
            text="+ New Campaign",
            bootstyle="success-outline",
            command=self._on_new_campaign
        ).pack(side=RIGHT, padx=5)

        ttk.Button(
            actions_frame,
            text="Import Contacts",
            bootstyle="primary-outline",
            command=self._on_import_contacts
        ).pack(side=RIGHT, padx=5)

    def refresh(self) -> None:
        """Refresh dashboard data."""
        if not self.api:
            return

        try:
            # Get statistics
            stats = self.api.get_overall_statistics(only_mine=True)

            # Update KPI cards
            self.kpi_grid.update_card("active_campaigns", stats.active_campaigns)
            self.kpi_grid.update_card("total_contacts", stats.total_contacts)
            self.kpi_grid.update_card("emails_sent", stats.total_emails_sent)

            # Calculate response rate
            campaigns = self.api.get_campaigns(only_mine=True)
            total_sent = sum(c.emails_sent for c in campaigns)
            if total_sent > 0:
                response_rate = sum(c.response_rate * c.emails_sent for c in campaigns) / total_sent
            else:
                response_rate = 0
            self.kpi_grid.update_card("response_rate", response_rate)

            # Update active campaigns table
            active_campaigns = [c for c in campaigns if c.status == CampaignStatus.ACTIVE]
            self._update_campaigns_table(active_campaigns)

            if self.app:
                self.app.set_status(f"Dashboard updated - {len(active_campaigns)} active campaigns")

        except Exception as e:
            logger.error(f"Error refreshing dashboard: {e}")
            if self.app:
                self.app.set_status(f"Error: {str(e)}")

    def _update_campaigns_table(self, campaigns: list) -> None:
        """Update campaigns table with data."""
        data = []
        for c in campaigns:
            progress = 0
            if c.total_contacts > 0:
                progress = (c.emails_sent / c.total_contacts) * 100

            data.append({
                "id": c.campaign_id,
                "ref": c.campaign_ref,
                "name": c.name,
                "status": c.status.value,
                "contacts": str(c.total_contacts),
                "sent": str(c.emails_sent),
                "progress": f"{progress:.0f}%"
            })

        self.campaigns_table.set_data(data)

    def _on_view_all_campaigns(self) -> None:
        """Navigate to campaigns list."""
        if self.app:
            self.app.show_view("campaign_list_view")

    def _on_campaign_double_click(self, campaign_id: str) -> None:
        """Handle campaign double-click."""
        if self.app:
            self.app.show_view("campaign_detail_view", campaign_id=campaign_id)

    def _on_new_campaign(self) -> None:
        """Create new campaign."""
        if self.app:
            self.app.show_view("campaign_list_view")

    def _on_import_contacts(self) -> None:
        """Open contact import."""
        if self.app:
            self.app.show_view("contact_list_view")
