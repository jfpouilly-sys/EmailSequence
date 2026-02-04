"""Reports view with charts and exports."""
import logging
import tkinter as tk
from tkinter import filedialog
from typing import Optional
import ttkbootstrap as ttk
from ttkbootstrap.constants import *

from core.api_client import ApiClient
from ui.widgets.chart_widget import ChartWidget
from ui.widgets.progress_card import KPICardGrid

logger = logging.getLogger(__name__)


class ReportsView(ttk.Frame):
    """Reports and analytics view."""

    def __init__(self, parent, app=None, api: ApiClient = None, **kwargs):
        super().__init__(parent, **kwargs)

        self.app = app
        self.api = api

        self._create_widgets()

    def _create_widgets(self) -> None:
        """Create view widgets."""
        # Header
        header = ttk.Frame(self)
        header.pack(fill=X, pady=(0, 15))

        ttk.Label(
            header,
            text="Analytics Dashboard",
            font=("Segoe UI", 14, "bold")
        ).pack(side=LEFT)

        # Period selector
        period_frame = ttk.Frame(header)
        period_frame.pack(side=RIGHT)

        ttk.Label(period_frame, text="Period:").pack(side=LEFT, padx=(0, 5))

        self.period_var = tk.StringVar(value="Last 30 Days")
        period_combo = ttk.Combobox(
            period_frame,
            textvariable=self.period_var,
            values=["Last 7 Days", "Last 30 Days", "Last 90 Days", "All Time"],
            state="readonly",
            width=15
        )
        period_combo.pack(side=LEFT)
        period_combo.bind("<<ComboboxSelected>>", lambda e: self.refresh())

        # KPI Cards
        self.kpi_grid = KPICardGrid(self, columns=4)
        self.kpi_grid.pack(fill=X, pady=(0, 20))

        self.kpi_grid.add_card(
            "campaigns",
            title="Total Campaigns",
            value=0,
            icon="\u2709",
            color="primary"
        )

        self.kpi_grid.add_card(
            "emails",
            title="Emails Sent",
            value=0,
            icon="\u2192",
            color="success"
        )

        self.kpi_grid.add_card(
            "contacts",
            title="Total Contacts",
            value=0,
            icon="\u263A",
            color="info"
        )

        self.kpi_grid.add_card(
            "response",
            title="Avg Response Rate",
            value="0%",
            icon="\u2713",
            color="warning",
            format_type="percentage"
        )

        # Charts row
        charts_frame = ttk.Frame(self)
        charts_frame.pack(fill=BOTH, expand=True)

        # Left chart - Campaign status distribution
        left_chart = ttk.LabelFrame(charts_frame, text="Campaign Status", padding=10)
        left_chart.pack(side=LEFT, fill=BOTH, expand=True, padx=(0, 10))

        self.status_chart = ChartWidget(left_chart, figsize=(5, 4))
        self.status_chart.pack(fill=BOTH, expand=True)

        # Right chart - Email activity
        right_chart = ttk.LabelFrame(charts_frame, text="Email Activity", padding=10)
        right_chart.pack(side=LEFT, fill=BOTH, expand=True)

        self.activity_chart = ChartWidget(right_chart, figsize=(5, 4))
        self.activity_chart.pack(fill=BOTH, expand=True)

        # Bottom section
        bottom = ttk.Frame(self)
        bottom.pack(fill=X, pady=(20, 0))

        # Export buttons
        export_frame = ttk.LabelFrame(bottom, text="Export Reports", padding=10)
        export_frame.pack(fill=X)

        ttk.Button(
            export_frame,
            text="Export Summary (CSV)",
            bootstyle="outline-primary",
            command=self._on_export_csv
        ).pack(side=LEFT, padx=5)

        ttk.Button(
            export_frame,
            text="Export Summary (PDF)",
            bootstyle="outline-primary",
            command=self._on_export_pdf
        ).pack(side=LEFT, padx=5)

        ttk.Button(
            export_frame,
            text="Export All Campaigns",
            bootstyle="outline-secondary",
            command=self._on_export_all
        ).pack(side=LEFT, padx=5)

    def refresh(self) -> None:
        """Refresh reports data."""
        if not self.api:
            return

        try:
            # Get overall stats
            stats = self.api.get_overall_statistics(only_mine=False)

            # Update KPIs
            self.kpi_grid.update_card("campaigns", stats.total_campaigns)
            self.kpi_grid.update_card("emails", stats.total_emails_sent)
            self.kpi_grid.update_card("contacts", stats.total_contacts)

            # Get campaigns for detailed stats
            campaigns = self.api.get_campaigns(only_mine=False)

            # Calculate response rate
            if campaigns:
                total_sent = sum(c.emails_sent for c in campaigns)
                if total_sent > 0:
                    avg_response = sum(c.response_rate * c.emails_sent for c in campaigns) / total_sent
                else:
                    avg_response = 0
            else:
                avg_response = 0

            self.kpi_grid.update_card("response", avg_response)

            # Update status chart
            status_counts = {}
            for c in campaigns:
                status = c.status.value
                status_counts[status] = status_counts.get(status, 0) + 1

            if status_counts:
                self.status_chart.draw_status_distribution(status_counts, "Campaign Status Distribution")
            else:
                self.status_chart.clear()

            # Update activity chart (mock data for now)
            labels = ["Sent", "Pending", "Replied", "Bounced"]
            values = [stats.total_emails_sent, stats.total_contacts - stats.total_emails_sent, 0, 0]
            self.activity_chart.draw_bar_chart(
                labels=labels,
                values=values,
                title="Email Status Breakdown",
                color="#007bff"
            )

            if self.app:
                self.app.set_status("Reports updated")

        except Exception as e:
            logger.error(f"Error refreshing reports: {e}")
            if self.app:
                self.app.set_status(f"Error: {str(e)}")

    def _on_export_csv(self) -> None:
        """Export summary to CSV."""
        filepath = filedialog.asksaveasfilename(
            defaultextension=".csv",
            filetypes=[("CSV files", "*.csv")],
            initialfilename="report_summary.csv"
        )
        if filepath:
            try:
                stats = self.api.get_overall_statistics()
                import csv
                with open(filepath, 'w', newline='') as f:
                    writer = csv.writer(f)
                    writer.writerow(["Metric", "Value"])
                    writer.writerow(["Total Campaigns", stats.total_campaigns])
                    writer.writerow(["Active Campaigns", stats.active_campaigns])
                    writer.writerow(["Total Emails Sent", stats.total_emails_sent])
                    writer.writerow(["Total Contacts", stats.total_contacts])

                if self.app:
                    self.app.set_status(f"Exported to {filepath}")
            except Exception as e:
                if self.app:
                    self.app.show_error("Export Error", str(e))

    def _on_export_pdf(self) -> None:
        """Export summary to PDF."""
        filepath = filedialog.asksaveasfilename(
            defaultextension=".pdf",
            filetypes=[("PDF files", "*.pdf")],
            initialfilename="report_summary.pdf"
        )
        if filepath:
            try:
                from fpdf import FPDF
                stats = self.api.get_overall_statistics()

                pdf = FPDF()
                pdf.add_page()
                pdf.set_font("Arial", "B", 16)
                pdf.cell(0, 10, "Lead Generator Summary Report", ln=True)

                pdf.set_font("Arial", "", 12)
                pdf.ln(10)
                pdf.cell(0, 8, f"Total Campaigns: {stats.total_campaigns}", ln=True)
                pdf.cell(0, 8, f"Active Campaigns: {stats.active_campaigns}", ln=True)
                pdf.cell(0, 8, f"Total Emails Sent: {stats.total_emails_sent}", ln=True)
                pdf.cell(0, 8, f"Total Contacts: {stats.total_contacts}", ln=True)

                pdf.output(filepath)

                if self.app:
                    self.app.set_status(f"Exported to {filepath}")
            except ImportError:
                if self.app:
                    self.app.show_error("Error", "fpdf2 is required for PDF export")
            except Exception as e:
                if self.app:
                    self.app.show_error("Export Error", str(e))

    def _on_export_all(self) -> None:
        """Export all campaigns data."""
        filepath = filedialog.asksaveasfilename(
            defaultextension=".csv",
            filetypes=[("CSV files", "*.csv")],
            initialfilename="all_campaigns.csv"
        )
        if filepath:
            try:
                campaigns = self.api.get_campaigns(only_mine=False)
                import csv
                with open(filepath, 'w', newline='') as f:
                    writer = csv.writer(f)
                    writer.writerow([
                        "Reference", "Name", "Status", "Total Contacts",
                        "Emails Sent", "Response Rate", "Created"
                    ])
                    for c in campaigns:
                        created = c.created_at.strftime("%Y-%m-%d") if c.created_at else ""
                        writer.writerow([
                            c.campaign_ref, c.name, c.status.value,
                            c.total_contacts, c.emails_sent,
                            f"{c.response_rate:.1f}%", created
                        ])

                if self.app:
                    self.app.set_status(f"Exported {len(campaigns)} campaigns to {filepath}")
            except Exception as e:
                if self.app:
                    self.app.show_error("Export Error", str(e))
