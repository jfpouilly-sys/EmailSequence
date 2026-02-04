"""Dashboard view for Lead Generator Standalone."""

import tkinter as tk
from tkinter import ttk
from typing import TYPE_CHECKING

from ui.theme import FONTS, COLORS
from ui.widgets.progress_card import ProgressCard
from ui.widgets.data_table import DataTable
from services.report_service import ReportService
from services.campaign_service import CampaignService

if TYPE_CHECKING:
    from ui.app import MainApplication


class DashboardView(ttk.Frame):
    """Dashboard overview view."""

    def __init__(self, parent, app: 'MainApplication'):
        super().__init__(parent)
        self.app = app
        self.report_service = ReportService()
        self.campaign_service = CampaignService()

        self._create_widgets()
        self.refresh()

        # Auto-refresh every 30 seconds
        self._schedule_refresh()

    def _create_widgets(self) -> None:
        """Create dashboard widgets."""
        # Title
        title = ttk.Label(self, text="Dashboard", font=FONTS['heading'])
        title.pack(anchor='w', pady=(0, 20))

        # KPI Cards
        cards_frame = ttk.Frame(self)
        cards_frame.pack(fill=tk.X, pady=(0, 20))

        self.active_campaigns_card = ProgressCard(
            cards_frame,
            title="Active Campaigns",
            value="0",
            color="primary"
        )
        self.active_campaigns_card.pack(side=tk.LEFT, padx=(0, 10), fill=tk.X, expand=True)

        self.total_contacts_card = ProgressCard(
            cards_frame,
            title="Total Contacts",
            value="0",
            color="info"
        )
        self.total_contacts_card.pack(side=tk.LEFT, padx=10, fill=tk.X, expand=True)

        self.emails_sent_card = ProgressCard(
            cards_frame,
            title="Emails Sent (30d)",
            value="0",
            color="success"
        )
        self.emails_sent_card.pack(side=tk.LEFT, padx=10, fill=tk.X, expand=True)

        self.response_rate_card = ProgressCard(
            cards_frame,
            title="Response Rate",
            value="0%",
            color="warning"
        )
        self.response_rate_card.pack(side=tk.LEFT, padx=(10, 0), fill=tk.X, expand=True)

        # Active Campaigns Table
        campaigns_frame = ttk.LabelFrame(self, text="Active Campaigns")
        campaigns_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10))

        columns = [
            {'key': 'name', 'label': 'Campaign', 'width': 200},
            {'key': 'campaign_ref', 'label': 'Reference', 'width': 100},
            {'key': 'contacts', 'label': 'Contacts', 'width': 80, 'anchor': 'center'},
            {'key': 'sent', 'label': 'Sent', 'width': 80, 'anchor': 'center'},
            {'key': 'responded', 'label': 'Responded', 'width': 80, 'anchor': 'center'},
            {'key': 'progress', 'label': 'Progress', 'width': 100, 'anchor': 'center'},
            {'key': 'status', 'label': 'Status', 'width': 80, 'anchor': 'center'},
        ]

        self.campaigns_table = DataTable(
            campaigns_frame,
            columns=columns,
            on_double_click=self._on_campaign_double_click,
            show_search=False,
            height=8
        )
        self.campaigns_table.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Quick Actions
        actions_frame = ttk.Frame(self)
        actions_frame.pack(fill=tk.X)

        ttk.Button(
            actions_frame,
            text="New Campaign",
            command=self._new_campaign
        ).pack(side=tk.LEFT, padx=(0, 10))

        ttk.Button(
            actions_frame,
            text="Import Contacts",
            command=self._import_contacts
        ).pack(side=tk.LEFT)

        # Worker controls
        worker_frame = ttk.Frame(actions_frame)
        worker_frame.pack(side=tk.RIGHT)

        self.start_worker_btn = ttk.Button(
            worker_frame,
            text="Start Worker",
            command=self._start_worker
        )
        self.start_worker_btn.pack(side=tk.LEFT, padx=(0, 5))

        self.stop_worker_btn = ttk.Button(
            worker_frame,
            text="Stop Worker",
            command=self._stop_worker,
            state='disabled'
        )
        self.stop_worker_btn.pack(side=tk.LEFT)

    def refresh(self) -> None:
        """Refresh dashboard data."""
        # Get stats
        stats = self.report_service.get_dashboard_stats()

        # Update cards
        self.active_campaigns_card.set_value(stats['active_campaigns'])
        self.total_contacts_card.set_value(stats['total_contacts'])
        self.emails_sent_card.set_value(stats['emails_sent_30d'])
        self.response_rate_card.set_value(f"{stats['response_rate']:.1f}%")

        # Get active campaigns
        campaigns = self.campaign_service.get_all_campaigns(status_filter='Active')
        campaign_data = []

        for campaign in campaigns:
            stats = campaign.stats or {}
            total = stats.get('total_contacts', 0)
            sent = stats.get('emails_sent', 0)
            responded = stats.get('responded', 0)

            progress = f"{(sent / total * 100):.0f}%" if total > 0 else "0%"

            campaign_data.append({
                'id': campaign.campaign_id,
                'name': campaign.name,
                'campaign_ref': campaign.campaign_ref,
                'contacts': total,
                'sent': sent,
                'responded': responded,
                'progress': progress,
                'status': campaign.status
            })

        self.campaigns_table.set_data(campaign_data)

        # Update worker buttons
        if self.app.worker:
            status = self.app.worker.get_status()
            if status['running'] and not status['paused']:
                self.start_worker_btn.configure(state='disabled')
                self.stop_worker_btn.configure(state='normal')
            else:
                self.start_worker_btn.configure(state='normal')
                self.stop_worker_btn.configure(state='disabled')

    def _schedule_refresh(self) -> None:
        """Schedule automatic refresh."""
        self.after(30000, self._auto_refresh)

    def _auto_refresh(self) -> None:
        """Auto-refresh callback."""
        if self.winfo_exists():
            self.refresh()
            self._schedule_refresh()

    def _on_campaign_double_click(self, item: dict) -> None:
        """Handle campaign double-click."""
        self.app._show_view('campaigns')

    def _new_campaign(self) -> None:
        """Open new campaign wizard."""
        self.app._show_view('campaigns')

    def _import_contacts(self) -> None:
        """Open contacts view for import."""
        self.app._show_view('contacts')

    def _start_worker(self) -> None:
        """Start the email worker."""
        if self.app.worker:
            self.app.worker.start()
            self.refresh()

    def _stop_worker(self) -> None:
        """Stop the email worker."""
        if self.app.worker:
            self.app.worker.stop()
            self.refresh()
