"""Campaign detail view for Lead Generator Standalone."""

import tkinter as tk
from tkinter import ttk, messagebox
from typing import TYPE_CHECKING, Optional

from ui.theme import FONTS
from services.campaign_service import CampaignService
from services.template_service import TemplateService
from core.models import Campaign

if TYPE_CHECKING:
    from ui.app import MainApplication


class CampaignDetailView(ttk.Frame):
    """Campaign detail and editing view."""

    def __init__(self, parent, app: 'MainApplication', campaign_id: Optional[int] = None):
        super().__init__(parent)
        self.app = app
        self.campaign_service = CampaignService()
        self.template_service = TemplateService()
        self.campaign_id = campaign_id
        self.campaign: Optional[Campaign] = None

        self._create_widgets()
        if campaign_id:
            self.load_campaign(campaign_id)

    def _create_widgets(self) -> None:
        """Create view widgets."""
        # Header
        header = ttk.Frame(self)
        header.pack(fill=tk.X, pady=(0, 10))

        self.title_label = ttk.Label(header, text="Campaign Details", font=FONTS['heading'])
        self.title_label.pack(side=tk.LEFT)

        ttk.Button(header, text="Save", command=self._save).pack(side=tk.RIGHT, padx=(5, 0))
        ttk.Button(header, text="Back", command=self._go_back).pack(side=tk.RIGHT)

        # Notebook for tabs
        self.notebook = ttk.Notebook(self)
        self.notebook.pack(fill=tk.BOTH, expand=True)

        # Overview tab
        self.overview_frame = ttk.Frame(self.notebook, padding=10)
        self.notebook.add(self.overview_frame, text="Overview")
        self._create_overview_tab()

        # Sequence tab
        self.sequence_frame = ttk.Frame(self.notebook, padding=10)
        self.notebook.add(self.sequence_frame, text="Sequence")
        self._create_sequence_tab()

        # Settings tab
        self.settings_frame = ttk.Frame(self.notebook, padding=10)
        self.notebook.add(self.settings_frame, text="Settings")
        self._create_settings_tab()

    def _create_overview_tab(self) -> None:
        """Create overview tab content."""
        # Name
        ttk.Label(self.overview_frame, text="Name:").grid(row=0, column=0, sticky='w', pady=5)
        self.name_var = tk.StringVar()
        ttk.Entry(self.overview_frame, textvariable=self.name_var, width=50).grid(row=0, column=1, sticky='w', pady=5)

        # Description
        ttk.Label(self.overview_frame, text="Description:").grid(row=1, column=0, sticky='nw', pady=5)
        self.description_text = tk.Text(self.overview_frame, width=50, height=3)
        self.description_text.grid(row=1, column=1, sticky='w', pady=5)

        # Reference (read-only)
        ttk.Label(self.overview_frame, text="Reference:").grid(row=2, column=0, sticky='w', pady=5)
        self.ref_label = ttk.Label(self.overview_frame, text="")
        self.ref_label.grid(row=2, column=1, sticky='w', pady=5)

        # Status
        ttk.Label(self.overview_frame, text="Status:").grid(row=3, column=0, sticky='w', pady=5)
        self.status_label = ttk.Label(self.overview_frame, text="")
        self.status_label.grid(row=3, column=1, sticky='w', pady=5)

    def _create_sequence_tab(self) -> None:
        """Create sequence tab content."""
        ttk.Label(self.sequence_frame, text="Email sequence steps will appear here.").pack(pady=20)

    def _create_settings_tab(self) -> None:
        """Create settings tab content."""
        # Sending window
        ttk.Label(self.settings_frame, text="Sending Window:").grid(row=0, column=0, sticky='w', pady=5)

        window_frame = ttk.Frame(self.settings_frame)
        window_frame.grid(row=0, column=1, sticky='w', pady=5)

        self.window_start_var = tk.StringVar(value="09:00")
        ttk.Entry(window_frame, textvariable=self.window_start_var, width=8).pack(side=tk.LEFT)
        ttk.Label(window_frame, text="to").pack(side=tk.LEFT, padx=5)
        self.window_end_var = tk.StringVar(value="17:00")
        ttk.Entry(window_frame, textvariable=self.window_end_var, width=8).pack(side=tk.LEFT)

        # Daily limit
        ttk.Label(self.settings_frame, text="Daily Send Limit:").grid(row=1, column=0, sticky='w', pady=5)
        self.daily_limit_var = tk.IntVar(value=50)
        ttk.Spinbox(self.settings_frame, from_=1, to=500, textvariable=self.daily_limit_var, width=10).grid(row=1, column=1, sticky='w', pady=5)

    def load_campaign(self, campaign_id: int) -> None:
        """Load campaign data."""
        self.campaign = self.campaign_service.get_campaign(campaign_id)
        if self.campaign:
            self.title_label.configure(text=f"Campaign: {self.campaign.name}")
            self.name_var.set(self.campaign.name)
            self.description_text.delete('1.0', tk.END)
            if self.campaign.description:
                self.description_text.insert('1.0', self.campaign.description)
            self.ref_label.configure(text=self.campaign.campaign_ref)
            self.status_label.configure(text=self.campaign.status)
            self.window_start_var.set(self.campaign.sending_window_start)
            self.window_end_var.set(self.campaign.sending_window_end)
            self.daily_limit_var.set(self.campaign.daily_send_limit)

    def _save(self) -> None:
        """Save campaign changes."""
        if not self.campaign:
            return

        try:
            data = {
                'name': self.name_var.get(),
                'description': self.description_text.get('1.0', tk.END).strip(),
                'sending_window_start': self.window_start_var.get(),
                'sending_window_end': self.window_end_var.get(),
                'daily_send_limit': self.daily_limit_var.get()
            }
            self.campaign_service.update_campaign(self.campaign.campaign_id, data)
            messagebox.showinfo("Success", "Campaign saved")
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def _go_back(self) -> None:
        """Go back to campaign list."""
        self.app._show_view('campaigns')
