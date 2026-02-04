"""Reports view for Lead Generator Standalone."""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from typing import TYPE_CHECKING, Optional

from ui.theme import FONTS
from ui.widgets.progress_card import ProgressCard
from ui.widgets.data_table import DataTable
from services.campaign_service import CampaignService
from services.report_service import ReportService

if TYPE_CHECKING:
    from ui.app import MainApplication


class ReportsView(ttk.Frame):
    """Reports and analytics view."""

    def __init__(self, parent, app: 'MainApplication'):
        super().__init__(parent)
        self.app = app
        self.campaign_service = CampaignService()
        self.report_service = ReportService()
        self._selected_campaign_id = None

        self._create_widgets()
        self._load_campaigns()

    def _create_widgets(self) -> None:
        """Create view widgets."""
        # Header
        header = ttk.Frame(self)
        header.pack(fill=tk.X, pady=(0, 10))

        ttk.Label(header, text="Reports", font=FONTS['heading']).pack(side=tk.LEFT)

        # Campaign selector
        selector_frame = ttk.Frame(header)
        selector_frame.pack(side=tk.RIGHT)

        ttk.Label(selector_frame, text="Campaign:").pack(side=tk.LEFT, padx=(0, 5))
        self.campaign_var = tk.StringVar()
        self.campaign_combo = ttk.Combobox(
            selector_frame,
            textvariable=self.campaign_var,
            state='readonly',
            width=40
        )
        self.campaign_combo.pack(side=tk.LEFT)
        self.campaign_combo.bind('<<ComboboxSelected>>', self._on_campaign_selected)

        # Stats cards
        cards_frame = ttk.Frame(self)
        cards_frame.pack(fill=tk.X, pady=(0, 20))

        self.total_card = ProgressCard(cards_frame, title="Total Contacts", value="0", color="info")
        self.total_card.pack(side=tk.LEFT, padx=(0, 10), fill=tk.X, expand=True)

        self.sent_card = ProgressCard(cards_frame, title="Emails Sent", value="0", color="success")
        self.sent_card.pack(side=tk.LEFT, padx=10, fill=tk.X, expand=True)

        self.responded_card = ProgressCard(cards_frame, title="Responded", value="0", color="primary")
        self.responded_card.pack(side=tk.LEFT, padx=10, fill=tk.X, expand=True)

        self.bounced_card = ProgressCard(cards_frame, title="Bounced", value="0", color="danger")
        self.bounced_card.pack(side=tk.LEFT, padx=10, fill=tk.X, expand=True)

        self.unsub_card = ProgressCard(cards_frame, title="Unsubscribed", value="0", color="warning")
        self.unsub_card.pack(side=tk.LEFT, padx=(10, 0), fill=tk.X, expand=True)

        # Email log table
        log_frame = ttk.LabelFrame(self, text="Email Log")
        log_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10))

        columns = [
            {'key': 'sent_at', 'label': 'Date', 'width': 120},
            {'key': 'contact_name', 'label': 'Contact', 'width': 150},
            {'key': 'contact_email', 'label': 'Email', 'width': 200},
            {'key': 'subject', 'label': 'Subject', 'width': 200},
            {'key': 'status', 'label': 'Status', 'width': 80, 'anchor': 'center'},
        ]

        self.log_table = DataTable(
            log_frame,
            columns=columns,
            show_search=True,
            height=12
        )
        self.log_table.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Export button
        ttk.Button(self, text="Export Report", command=self._export_report).pack(anchor='e')

    def _load_campaigns(self) -> None:
        """Load campaigns into selector."""
        campaigns = self.campaign_service.get_all_campaigns()

        self._campaigns = campaigns
        values = [f"{c.campaign_ref} - {c.name}" for c in campaigns]
        self.campaign_combo['values'] = values

        if values:
            self.campaign_combo.current(0)
            self._on_campaign_selected(None)

    def _on_campaign_selected(self, event) -> None:
        """Handle campaign selection."""
        idx = self.campaign_combo.current()
        if idx >= 0 and idx < len(self._campaigns):
            campaign = self._campaigns[idx]
            self._selected_campaign_id = campaign.campaign_id
            self._load_report(campaign.campaign_id)

    def _load_report(self, campaign_id: int) -> None:
        """Load report for campaign."""
        report = self.report_service.get_campaign_report(campaign_id)

        if not report:
            return

        stats = report.get('stats', {})

        # Update cards
        self.total_card.set_value(stats.get('total', 0))
        self.sent_card.set_value(stats.get('emails_sent', 0))
        self.responded_card.set_value(stats.get('responded', 0))
        self.bounced_card.set_value(stats.get('bounced', 0))
        self.unsub_card.set_value(stats.get('unsubscribed', 0))

        # Load email logs
        logs = self.report_service.get_email_logs(campaign_id=campaign_id, days=365)

        data = []
        for log in logs:
            data.append({
                'sent_at': log.sent_at[:16] if log.sent_at else '',
                'contact_name': log.contact_name or '',
                'contact_email': log.contact_email or '',
                'subject': log.subject or '',
                'status': log.status
            })

        self.log_table.set_data(data)

    def _export_report(self) -> None:
        """Export report to CSV."""
        if not self._selected_campaign_id:
            messagebox.showwarning("Warning", "Select a campaign first")
            return

        file_path = filedialog.asksaveasfilename(
            title="Export Report",
            defaultextension=".csv",
            filetypes=[("CSV Files", "*.csv")]
        )

        if file_path:
            try:
                self.report_service.export_campaign_report(self._selected_campaign_id, file_path)
                messagebox.showinfo("Success", f"Report exported to {file_path}")
            except Exception as e:
                messagebox.showerror("Error", str(e))
