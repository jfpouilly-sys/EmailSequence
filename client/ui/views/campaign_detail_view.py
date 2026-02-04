"""Campaign detail view with tabs."""
import logging
import tkinter as tk
from typing import Optional
import ttkbootstrap as ttk
from ttkbootstrap.constants import *

from core.api_client import ApiClient
from core.models import Campaign, EmailStep, CampaignStatus
from ui.widgets.data_table import DataTable
from ui.widgets.status_badge import StatusBadge
from ui.widgets.chart_widget import ChartWidget

logger = logging.getLogger(__name__)


class CampaignDetailView(ttk.Frame):
    """Campaign detail view with tabs for different aspects."""

    def __init__(self, parent, app=None, api: ApiClient = None, campaign_id: str = None, **kwargs):
        super().__init__(parent, **kwargs)

        self.app = app
        self.api = api
        self.campaign_id = campaign_id
        self.campaign: Optional[Campaign] = None

        self._create_widgets()

    def _create_widgets(self) -> None:
        """Create view widgets."""
        # Header
        header = ttk.Frame(self)
        header.pack(fill=X, pady=(0, 15))

        # Back button
        ttk.Button(
            header,
            text="\u2190 Back",
            bootstyle="link",
            command=self._on_back
        ).pack(side=LEFT)

        # Campaign name
        self.name_label = ttk.Label(
            header,
            text="Campaign",
            font=("Segoe UI", 16, "bold")
        )
        self.name_label.pack(side=LEFT, padx=(10, 0))

        # Status badge
        self.status_badge = StatusBadge(header, status="Draft")
        self.status_badge.pack(side=LEFT, padx=(15, 0))

        # Action buttons
        actions = ttk.Frame(header)
        actions.pack(side=RIGHT)

        self.activate_btn = ttk.Button(
            actions,
            text="Activate",
            bootstyle="success",
            command=self._on_activate
        )
        self.activate_btn.pack(side=LEFT, padx=5)

        self.pause_btn = ttk.Button(
            actions,
            text="Pause",
            bootstyle="warning",
            command=self._on_pause
        )
        self.pause_btn.pack(side=LEFT, padx=5)

        # Notebook for tabs
        self.notebook = ttk.Notebook(self)
        self.notebook.pack(fill=BOTH, expand=True)

        # Overview tab
        self.overview_tab = ttk.Frame(self.notebook, padding=15)
        self.notebook.add(self.overview_tab, text="Overview")
        self._create_overview_tab()

        # Sequence tab
        self.sequence_tab = ttk.Frame(self.notebook, padding=15)
        self.notebook.add(self.sequence_tab, text="Email Sequence")
        self._create_sequence_tab()

        # Contacts tab
        self.contacts_tab = ttk.Frame(self.notebook, padding=15)
        self.notebook.add(self.contacts_tab, text="Contacts")
        self._create_contacts_tab()

        # Reports tab
        self.reports_tab = ttk.Frame(self.notebook, padding=15)
        self.notebook.add(self.reports_tab, text="Reports")
        self._create_reports_tab()

    def _create_overview_tab(self) -> None:
        """Create overview tab content."""
        # Info section
        info_frame = ttk.LabelFrame(self.overview_tab, text="Campaign Information", padding=15)
        info_frame.pack(fill=X, pady=(0, 15))

        # Reference
        row1 = ttk.Frame(info_frame)
        row1.pack(fill=X, pady=3)
        ttk.Label(row1, text="Reference:", width=15, anchor=W).pack(side=LEFT)
        self.ref_label = ttk.Label(row1, text="-")
        self.ref_label.pack(side=LEFT)

        # Description
        row2 = ttk.Frame(info_frame)
        row2.pack(fill=X, pady=3)
        ttk.Label(row2, text="Description:", width=15, anchor=W).pack(side=LEFT)
        self.desc_label = ttk.Label(row2, text="-", wraplength=400)
        self.desc_label.pack(side=LEFT)

        # Created
        row3 = ttk.Frame(info_frame)
        row3.pack(fill=X, pady=3)
        ttk.Label(row3, text="Created:", width=15, anchor=W).pack(side=LEFT)
        self.created_label = ttk.Label(row3, text="-")
        self.created_label.pack(side=LEFT)

        # Stats section
        stats_frame = ttk.LabelFrame(self.overview_tab, text="Statistics", padding=15)
        stats_frame.pack(fill=X, pady=(0, 15))

        stats_grid = ttk.Frame(stats_frame)
        stats_grid.pack(fill=X)

        for i, (label, key) in enumerate([
            ("Total Contacts", "contacts"),
            ("Emails Sent", "sent"),
            ("Replies", "replies"),
            ("Response Rate", "rate")
        ]):
            col = ttk.Frame(stats_grid)
            col.pack(side=LEFT, expand=True, fill=X, padx=10)

            ttk.Label(
                col,
                text=label,
                font=("Segoe UI", 9),
                bootstyle="secondary"
            ).pack()

            lbl = ttk.Label(
                col,
                text="0",
                font=("Segoe UI", 20, "bold")
            )
            lbl.pack()
            setattr(self, f"stat_{key}_label", lbl)

        # Settings section
        settings_frame = ttk.LabelFrame(self.overview_tab, text="Sending Settings", padding=15)
        settings_frame.pack(fill=X)

        settings = [
            ("Daily Send Limit:", "daily_limit"),
            ("Email Delay:", "delay"),
            ("Sending Window:", "window"),
            ("Sending Days:", "days"),
        ]

        for label, key in settings:
            row = ttk.Frame(settings_frame)
            row.pack(fill=X, pady=3)
            ttk.Label(row, text=label, width=20, anchor=W).pack(side=LEFT)
            lbl = ttk.Label(row, text="-")
            lbl.pack(side=LEFT)
            setattr(self, f"setting_{key}_label", lbl)

    def _create_sequence_tab(self) -> None:
        """Create sequence tab content."""
        # Header
        header = ttk.Frame(self.sequence_tab)
        header.pack(fill=X, pady=(0, 15))

        ttk.Label(
            header,
            text="Email Sequence Steps",
            font=("Segoe UI", 12, "bold")
        ).pack(side=LEFT)

        ttk.Button(
            header,
            text="+ Add Step",
            bootstyle="success-outline",
            command=self._on_add_step
        ).pack(side=RIGHT)

        # Steps list
        columns = [
            {"id": "id", "text": "ID", "width": 0},
            {"id": "step", "text": "Step", "width": 60, "anchor": "center"},
            {"id": "subject", "text": "Subject", "width": 300, "anchor": "w"},
            {"id": "delay", "text": "Delay (days)", "width": 100, "anchor": "center"},
            {"id": "status", "text": "Status", "width": 80, "anchor": "center"},
        ]

        self.steps_table = DataTable(
            self.sequence_tab,
            columns=columns,
            show_search=False,
            on_double_click=self._on_edit_step
        )
        self.steps_table.pack(fill=BOTH, expand=True)

        # Bottom actions
        bottom = ttk.Frame(self.sequence_tab)
        bottom.pack(fill=X, pady=(10, 0))

        ttk.Button(
            bottom,
            text="Edit Step",
            bootstyle="primary-outline",
            command=self._on_edit_step_click
        ).pack(side=LEFT, padx=5)

        ttk.Button(
            bottom,
            text="Delete Step",
            bootstyle="danger-outline",
            command=self._on_delete_step
        ).pack(side=LEFT, padx=5)

    def _create_contacts_tab(self) -> None:
        """Create contacts tab content."""
        columns = [
            {"id": "id", "text": "ID", "width": 0},
            {"id": "name", "text": "Name", "width": 200, "anchor": "w"},
            {"id": "email", "text": "Email", "width": 250, "anchor": "w"},
            {"id": "company", "text": "Company", "width": 150, "anchor": "w"},
            {"id": "status", "text": "Status", "width": 100, "anchor": "center"},
            {"id": "last_email", "text": "Last Email", "width": 120, "anchor": "center"},
        ]

        self.contacts_table = DataTable(
            self.contacts_tab,
            columns=columns,
            show_search=True
        )
        self.contacts_table.pack(fill=BOTH, expand=True)

    def _create_reports_tab(self) -> None:
        """Create reports tab content."""
        # Chart
        chart_frame = ttk.LabelFrame(self.reports_tab, text="Campaign Progress", padding=10)
        chart_frame.pack(fill=BOTH, expand=True)

        self.chart = ChartWidget(chart_frame, figsize=(8, 4))
        self.chart.pack(fill=BOTH, expand=True)

        # Export buttons
        export_frame = ttk.Frame(self.reports_tab)
        export_frame.pack(fill=X, pady=(15, 0))

        ttk.Button(
            export_frame,
            text="Export CSV",
            bootstyle="outline-primary",
            command=self._on_export_csv
        ).pack(side=LEFT, padx=5)

        ttk.Button(
            export_frame,
            text="Export PDF",
            bootstyle="outline-primary",
            command=self._on_export_pdf
        ).pack(side=LEFT, padx=5)

    def refresh(self, campaign_id: str = None) -> None:
        """Refresh campaign data."""
        if campaign_id:
            self.campaign_id = campaign_id

        if not self.api or not self.campaign_id:
            return

        try:
            # Load campaign
            self.campaign = self.api.get_campaign(self.campaign_id)

            # Update header
            self.name_label.configure(text=self.campaign.name)
            self.status_badge.set_status(self.campaign.status.value)

            # Update buttons
            if self.campaign.status == CampaignStatus.ACTIVE:
                self.activate_btn.configure(state="disabled")
                self.pause_btn.configure(state="normal")
            else:
                self.activate_btn.configure(state="normal")
                self.pause_btn.configure(state="disabled")

            # Update overview
            self._update_overview()

            # Load steps
            self._load_steps()

            # Load stats
            self._load_stats()

            if self.app:
                self.app.set_status(f"Loaded campaign: {self.campaign.name}")

        except Exception as e:
            logger.error(f"Error loading campaign: {e}")
            if self.app:
                self.app.show_error("Error", str(e))

    def _update_overview(self) -> None:
        """Update overview tab."""
        if not self.campaign:
            return

        self.ref_label.configure(text=self.campaign.campaign_ref)
        self.desc_label.configure(text=self.campaign.description or "-")
        created = self.campaign.created_at.strftime("%Y-%m-%d %H:%M") if self.campaign.created_at else "-"
        self.created_label.configure(text=created)

        self.setting_daily_limit_label.configure(text=str(self.campaign.daily_send_limit))
        self.setting_delay_label.configure(text=f"{self.campaign.inter_email_delay_minutes} minutes")
        self.setting_window_label.configure(
            text=f"{self.campaign.sending_window_start} - {self.campaign.sending_window_end}"
        )
        self.setting_days_label.configure(text=self.campaign.sending_days)

    def _load_steps(self) -> None:
        """Load email sequence steps."""
        try:
            steps = self.api.get_campaign_steps(self.campaign_id)
            data = []
            for s in steps:
                data.append({
                    "id": s.step_id,
                    "step": str(s.step_number),
                    "subject": s.subject,
                    "delay": str(s.delay_days),
                    "status": "Active" if s.is_active else "Inactive"
                })
            self.steps_table.set_data(data)
        except Exception as e:
            logger.error(f"Error loading steps: {e}")

    def _load_stats(self) -> None:
        """Load campaign statistics."""
        try:
            stats = self.api.get_campaign_statistics(self.campaign_id)

            self.stat_contacts_label.configure(text=str(stats.total_contacts))
            self.stat_sent_label.configure(text=str(stats.emails_sent))
            self.stat_replies_label.configure(text=str(stats.replies))
            self.stat_rate_label.configure(text=f"{stats.response_rate:.1f}%")

            # Update chart
            self.chart.draw_progress_chart(
                completed=stats.emails_sent,
                remaining=stats.emails_pending,
                title="Email Progress"
            )
        except Exception as e:
            logger.error(f"Error loading stats: {e}")

    def _on_back(self) -> None:
        """Go back to campaign list."""
        if self.app:
            self.app.show_view("campaign_list_view")

    def _on_activate(self) -> None:
        """Activate campaign."""
        if self.api and self.campaign_id:
            try:
                self.api.activate_campaign(self.campaign_id)
                self.refresh()
            except Exception as e:
                if self.app:
                    self.app.show_error("Error", str(e))

    def _on_pause(self) -> None:
        """Pause campaign."""
        if self.api and self.campaign_id:
            try:
                self.api.pause_campaign(self.campaign_id)
                self.refresh()
            except Exception as e:
                if self.app:
                    self.app.show_error("Error", str(e))

    def _on_add_step(self) -> None:
        """Add new email step."""
        dialog = EmailStepDialog(self, self.api, self.campaign_id)
        self.wait_window(dialog)
        if dialog.result:
            self._load_steps()

    def _on_edit_step_click(self) -> None:
        """Edit selected step."""
        step_id = self.steps_table.get_selected_id()
        if step_id:
            self._on_edit_step(step_id)

    def _on_edit_step(self, step_id: str) -> None:
        """Edit email step."""
        dialog = EmailStepDialog(self, self.api, self.campaign_id, step_id=step_id)
        self.wait_window(dialog)
        if dialog.result:
            self._load_steps()

    def _on_delete_step(self) -> None:
        """Delete selected step."""
        step_id = self.steps_table.get_selected_id()
        if not step_id:
            return

        if self.app and self.app.ask_confirmation("Delete Step", "Are you sure?"):
            try:
                self.api.delete_email_step(step_id)
                self._load_steps()
            except Exception as e:
                if self.app:
                    self.app.show_error("Error", str(e))

    def _on_export_csv(self) -> None:
        """Export report to CSV."""
        from tkinter import filedialog
        filepath = filedialog.asksaveasfilename(
            defaultextension=".csv",
            filetypes=[("CSV files", "*.csv")]
        )
        if filepath:
            try:
                from services.report_service import ReportService
                service = ReportService(self.api)
                data = service.export_campaign_report_csv(self.campaign_id)
                with open(filepath, 'wb') as f:
                    f.write(data.read())
                if self.app:
                    self.app.set_status(f"Exported to {filepath}")
            except Exception as e:
                if self.app:
                    self.app.show_error("Error", str(e))

    def _on_export_pdf(self) -> None:
        """Export report to PDF."""
        from tkinter import filedialog
        filepath = filedialog.asksaveasfilename(
            defaultextension=".pdf",
            filetypes=[("PDF files", "*.pdf")]
        )
        if filepath:
            try:
                from services.report_service import ReportService
                service = ReportService(self.api)
                data = service.export_campaign_report_pdf(self.campaign_id)
                with open(filepath, 'wb') as f:
                    f.write(data.read())
                if self.app:
                    self.app.set_status(f"Exported to {filepath}")
            except Exception as e:
                if self.app:
                    self.app.show_error("Error", str(e))


class EmailStepDialog(ttk.Toplevel):
    """Dialog for creating/editing email steps."""

    def __init__(self, parent, api: ApiClient, campaign_id: str, step_id: str = None):
        super().__init__(parent)

        self.api = api
        self.campaign_id = campaign_id
        self.step_id = step_id
        self.result = None

        self.title("New Email Step" if not step_id else "Edit Email Step")
        self.geometry("600x500")

        self._create_widgets()

        if step_id:
            self._load_step()

        self.transient(parent)
        self.grab_set()

    def _create_widgets(self) -> None:
        """Create dialog widgets."""
        main = ttk.Frame(self, padding=20)
        main.pack(fill=BOTH, expand=True)

        # Step number
        row1 = ttk.Frame(main)
        row1.pack(fill=X, pady=(0, 15))
        ttk.Label(row1, text="Step Number:").pack(side=LEFT)
        self.step_var = tk.StringVar(value="1")
        ttk.Entry(row1, textvariable=self.step_var, width=10).pack(side=LEFT, padx=10)

        ttk.Label(row1, text="Delay (days):").pack(side=LEFT, padx=(20, 0))
        self.delay_var = tk.StringVar(value="0")
        ttk.Entry(row1, textvariable=self.delay_var, width=10).pack(side=LEFT, padx=10)

        # Subject
        ttk.Label(main, text="Subject *").pack(anchor=W, pady=(0, 5))
        self.subject_var = tk.StringVar()
        ttk.Entry(main, textvariable=self.subject_var, width=60).pack(fill=X, pady=(0, 15))

        # Body
        ttk.Label(main, text="Email Body *").pack(anchor=W, pady=(0, 5))
        self.body_text = tk.Text(main, height=12, wrap=tk.WORD)
        self.body_text.pack(fill=BOTH, expand=True, pady=(0, 15))

        # Merge tags hint
        ttk.Label(
            main,
            text="Available tags: {{FirstName}}, {{Company}}, {{Custom1}}, etc.",
            font=("Segoe UI", 9),
            bootstyle="secondary"
        ).pack(anchor=W)

        # Buttons
        btn_frame = ttk.Frame(main)
        btn_frame.pack(fill=X, pady=(15, 0))

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

    def _load_step(self) -> None:
        """Load existing step data."""
        try:
            steps = self.api.get_campaign_steps(self.campaign_id)
            step = next((s for s in steps if s.step_id == self.step_id), None)
            if step:
                self.step_var.set(str(step.step_number))
                self.delay_var.set(str(step.delay_days))
                self.subject_var.set(step.subject)
                self.body_text.insert("1.0", step.body)
        except Exception as e:
            logger.error(f"Error loading step: {e}")

    def _on_save(self) -> None:
        """Save email step."""
        subject = self.subject_var.get().strip()
        body = self.body_text.get("1.0", "end-1c").strip()

        if not subject or not body:
            from tkinter import messagebox
            messagebox.showerror("Error", "Subject and body are required", parent=self)
            return

        try:
            if self.step_id:
                self.api.update_email_step(
                    self.step_id,
                    subject=subject,
                    body=body,
                    delay_days=int(self.delay_var.get())
                )
            else:
                self.api.create_email_step(
                    campaign_id=self.campaign_id,
                    step_number=int(self.step_var.get()),
                    subject=subject,
                    body=body,
                    delay_days=int(self.delay_var.get())
                )

            self.result = True
            self.destroy()

        except Exception as e:
            from tkinter import messagebox
            messagebox.showerror("Error", str(e), parent=self)
