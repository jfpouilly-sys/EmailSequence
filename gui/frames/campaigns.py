"""Campaigns Frame

Campaign management with create, delete, import, export, and template library.
"""

import customtkinter as ctk
from tkinter import filedialog
from gui.dialogs import ConfirmationDialog, InfoDialog
from src.campaign_manager import CampaignManager
from pathlib import Path
import zipfile
import shutil
from typing import Optional


class CampaignsFrame(ctk.CTkFrame):
    """Campaign management interface."""

    def __init__(self, parent, app):
        """Initialize campaigns frame.

        Args:
            parent: Parent widget
            app: Main application instance
        """
        super().__init__(parent, fg_color="transparent")

        self.app = app
        self.campaign_mgr = CampaignManager()
        self.selected_campaign = None

        # Configure grid
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(2, weight=1)

        # Create components
        self.create_header()
        self.create_toolbar()
        self.create_campaigns_list()
        self.create_templates_library()

        # Load campaigns
        self.load_campaigns()

    def create_header(self) -> None:
        """Create header with title."""
        title_label = ctk.CTkLabel(
            self,
            text="CAMPAIGN MANAGEMENT",
            font=("Arial Bold", 24),
            anchor="w"
        )
        title_label.grid(row=0, column=0, sticky="w", pady=(10, 20), padx=20)

    def create_toolbar(self) -> None:
        """Create toolbar with buttons."""
        toolbar = ctk.CTkFrame(self, fg_color="transparent")
        toolbar.grid(row=1, column=0, sticky="ew", padx=20, pady=(0, 10))

        # New Campaign button
        new_btn = ctk.CTkButton(
            toolbar,
            text="+ New Campaign",
            command=self.on_new_campaign,
            width=140,
            height=32,
            fg_color="#10B981"
        )
        new_btn.grid(row=0, column=0, padx=(0, 5))

        # Import Campaign button
        import_btn = ctk.CTkButton(
            toolbar,
            text="📥 Import Campaign",
            command=self.on_import_campaign,
            width=150,
            height=32,
            fg_color="gray"
        )
        import_btn.grid(row=0, column=1, padx=5)

        # Export Campaign button
        export_btn = ctk.CTkButton(
            toolbar,
            text="📤 Export Campaign",
            command=self.on_export_campaign,
            width=150,
            height=32,
            fg_color="gray"
        )
        export_btn.grid(row=0, column=2, padx=5)

        # Delete Campaign button
        delete_btn = ctk.CTkButton(
            toolbar,
            text="🗑 Delete Campaign",
            command=self.on_delete_campaign,
            width=150,
            height=32,
            fg_color="#EF4444",
            hover_color="#DC2626"
        )
        delete_btn.grid(row=0, column=3, padx=5)

    def create_campaigns_list(self) -> None:
        """Create campaigns list."""
        # Frame for campaigns list
        list_frame = ctk.CTkFrame(self)
        list_frame.grid(row=2, column=0, sticky="nsew", padx=20, pady=(0, 10))
        list_frame.grid_columnconfigure(0, weight=1)
        list_frame.grid_rowconfigure(1, weight=1)

        # Title
        title = ctk.CTkLabel(
            list_frame,
            text="MY CAMPAIGNS",
            font=("Arial Bold", 14),
            anchor="w"
        )
        title.grid(row=0, column=0, sticky="w", padx=15, pady=(15, 10))

        # Scrollable frame for campaign cards
        self.campaigns_scroll = ctk.CTkScrollableFrame(list_frame, fg_color="transparent")
        self.campaigns_scroll.grid(row=1, column=0, sticky="nsew", padx=10, pady=(0, 10))
        self.campaigns_scroll.grid_columnconfigure(0, weight=1)

    def create_templates_library(self) -> None:
        """Create templates library section."""
        library_frame = ctk.CTkFrame(self)
        library_frame.grid(row=3, column=0, sticky="ew", padx=20, pady=(0, 20))
        library_frame.grid_columnconfigure(0, weight=1)

        # Title
        title = ctk.CTkLabel(
            library_frame,
            text="TEMPLATES LIBRARY",
            font=("Arial Bold", 14),
            anchor="w"
        )
        title.grid(row=0, column=0, sticky="w", padx=15, pady=(15, 10))

        # Description
        desc = ctk.CTkLabel(
            library_frame,
            text="Shared templates that can be copied to any campaign",
            font=("Arial", 11),
            text_color="gray",
            anchor="w"
        )
        desc.grid(row=1, column=0, sticky="w", padx=15, pady=(0, 10))

        # Buttons
        btn_frame = ctk.CTkFrame(library_frame, fg_color="transparent")
        btn_frame.grid(row=2, column=0, sticky="w", padx=15, pady=(0, 15))

        browse_btn = ctk.CTkButton(
            btn_frame,
            text="📁 Browse Library",
            command=self.on_browse_library,
            width=140
        )
        browse_btn.pack(side="left", padx=(0, 5))

        add_btn = ctk.CTkButton(
            btn_frame,
            text="+ Add Template",
            command=self.on_add_to_library,
            width=140,
            fg_color="gray"
        )
        add_btn.pack(side="left", padx=5)

    def load_campaigns(self) -> None:
        """Load and display all campaigns."""
        # Clear existing campaign cards
        for widget in self.campaigns_scroll.winfo_children():
            widget.destroy()

        # Get campaigns
        campaigns = self.campaign_mgr.list_campaigns()
        active_campaign = self.campaign_mgr.get_active_campaign()

        if not campaigns:
            # Show empty state
            empty_label = ctk.CTkLabel(
                self.campaigns_scroll,
                text="No campaigns yet. Click '+ New Campaign' to create one.",
                font=("Arial", 12),
                text_color="gray"
            )
            empty_label.grid(row=0, column=0, pady=50)
            return

        # Create campaign cards
        for idx, campaign in enumerate(campaigns):
            self.create_campaign_card(campaign, idx, is_active=(campaign.name == active_campaign))

    def create_campaign_card(self, campaign, row: int, is_active: bool = False) -> None:
        """Create a campaign card."""
        # Card frame
        card = ctk.CTkFrame(
            self.campaigns_scroll,
            fg_color="#2B2B2B" if not is_active else "#10B981",
            corner_radius=8
        )
        card.grid(row=row, column=0, sticky="ew", pady=5, padx=5)
        card.grid_columnconfigure(0, weight=1)

        # Campaign name
        name_label = ctk.CTkLabel(
            card,
            text=campaign.name,
            font=("Arial Bold", 14),
            anchor="w"
        )
        name_label.grid(row=0, column=0, sticky="w", padx=15, pady=(15, 5))

        # Active badge
        if is_active:
            active_badge = ctk.CTkLabel(
                card,
                text="● ACTIVE",
                font=("Arial Bold", 11),
                text_color="#FFFFFF"
            )
            active_badge.grid(row=0, column=1, sticky="e", padx=15, pady=(15, 5))

        # Campaign info
        info = campaign.to_dict()
        contacts_count = info.get('contacts_count', 0)
        info_text = f"{contacts_count} contacts"

        info_label = ctk.CTkLabel(
            card,
            text=info_text,
            font=("Arial", 11),
            text_color="gray",
            anchor="w"
        )
        info_label.grid(row=1, column=0, columnspan=2, sticky="w", padx=15, pady=(0, 10))

        # Buttons
        btn_frame = ctk.CTkFrame(card, fg_color="transparent")
        btn_frame.grid(row=2, column=0, columnspan=2, sticky="ew", padx=15, pady=(0, 15))

        if not is_active:
            activate_btn = ctk.CTkButton(
                btn_frame,
                text="✓ Activate",
                command=lambda c=campaign: self.on_activate_campaign(c),
                width=100,
                height=28,
                fg_color="#3B82F6"
            )
            activate_btn.pack(side="left", padx=(0, 5))

        open_btn = ctk.CTkButton(
            btn_frame,
            text="📂 Open Folder",
            command=lambda c=campaign: self.on_open_folder(c),
            width=110,
            height=28,
            fg_color="gray"
        )
        open_btn.pack(side="left", padx=5)

    def on_new_campaign(self) -> None:
        """Handle New Campaign button click."""
        from gui.dialogs import CreateCampaignDialog

        dialog = CreateCampaignDialog(self, self.campaign_mgr)
        result = dialog.get_result()

        if result:
            self.load_campaigns()
            InfoDialog.show(self, "Success", f"Campaign '{result['name']}' created successfully!")

    def on_activate_campaign(self, campaign) -> None:
        """Activate a campaign."""
        success = self.campaign_mgr.set_active_campaign(campaign.name)

        if success:
            self.load_campaigns()
            InfoDialog.show(self, "Success", f"Campaign '{campaign.name}' is now active.")
            # Notify app to reload with new campaign
            if hasattr(self.app, 'reload_active_campaign'):
                self.app.reload_active_campaign()
        else:
            InfoDialog.show(self, "Error", "Failed to activate campaign.")

    def on_delete_campaign(self) -> None:
        """Handle Delete Campaign button click."""
        campaigns = self.campaign_mgr.list_campaigns()

        if not campaigns:
            InfoDialog.show(self, "No Campaigns", "No campaigns to delete.")
            return

        # Show selection dialog
        from gui.dialogs import SelectCampaignDialog

        dialog = SelectCampaignDialog(
            self,
            "Select Campaign to Delete",
            campaigns,
            "Delete"
        )
        selected = dialog.get_result()

        if not selected:
            return

        # Confirm deletion
        confirm = ConfirmationDialog(
            self,
            "Delete Campaign",
            f"Are you sure you want to delete '{selected.name}'?\n\nThis will delete all contacts, templates, and logs.",
            confirm_text="Delete",
            danger=True
        )

        if confirm.get_result():
            success = self.campaign_mgr.delete_campaign(selected.name)
            if success:
                self.load_campaigns()
                InfoDialog.show(self, "Success", f"Campaign '{selected.name}' deleted.")
            else:
                InfoDialog.show(self, "Error", "Failed to delete campaign.")

    def on_import_campaign(self) -> None:
        """Handle Import Campaign button click."""
        filename = filedialog.askopenfilename(
            title="Import Campaign",
            filetypes=[("ZIP files", "*.zip"), ("All files", "*.*")]
        )

        if not filename:
            return

        try:
            success = self.campaign_mgr.import_campaign(filename)
            if success:
                self.load_campaigns()
                InfoDialog.show(self, "Success", "Campaign imported successfully!")
            else:
                InfoDialog.show(self, "Error", "Failed to import campaign.")
        except Exception as e:
            InfoDialog.show(self, "Error", f"Failed to import campaign:\n{str(e)}")

    def on_export_campaign(self) -> None:
        """Handle Export Campaign button click."""
        campaigns = self.campaign_mgr.list_campaigns()

        if not campaigns:
            InfoDialog.show(self, "No Campaigns", "No campaigns to export.")
            return

        # Show selection dialog
        from gui.dialogs import SelectCampaignDialog

        dialog = SelectCampaignDialog(
            self,
            "Select Campaign to Export",
            campaigns,
            "Export"
        )
        selected = dialog.get_result()

        if not selected:
            return

        # Choose save location
        filename = filedialog.asksaveasfilename(
            title="Export Campaign",
            defaultextension=".zip",
            initialfile=f"{selected.name}.zip",
            filetypes=[("ZIP files", "*.zip")]
        )

        if not filename:
            return

        try:
            success = self.campaign_mgr.export_campaign(selected.name, filename)
            if success:
                InfoDialog.show(self, "Success", f"Campaign exported to:\n{filename}")
            else:
                InfoDialog.show(self, "Error", "Failed to export campaign.")
        except Exception as e:
            InfoDialog.show(self, "Error", f"Failed to export campaign:\n{str(e)}")

    def on_open_folder(self, campaign) -> None:
        """Open campaign folder in file explorer."""
        import subprocess
        import sys

        folder_path = campaign.folder_path

        try:
            if sys.platform == 'win32':
                subprocess.run(['explorer', str(folder_path)])
            elif sys.platform == 'darwin':
                subprocess.run(['open', str(folder_path)])
            else:
                subprocess.run(['xdg-open', str(folder_path)])
        except Exception as e:
            InfoDialog.show(self, "Error", f"Failed to open folder:\n{str(e)}")

    def on_browse_library(self) -> None:
        """Browse templates library."""
        library_path = Path("templates_library")

        if not library_path.exists():
            library_path.mkdir(parents=True, exist_ok=True)

        import subprocess
        import sys

        try:
            if sys.platform == 'win32':
                subprocess.run(['explorer', str(library_path.absolute())])
            elif sys.platform == 'darwin':
                subprocess.run(['open', str(library_path.absolute())])
            else:
                subprocess.run(['xdg-open', str(library_path.absolute())])
        except Exception as e:
            InfoDialog.show(self, "Error", f"Failed to open library:\n{str(e)}")

    def on_add_to_library(self) -> None:
        """Add template to library."""
        filename = filedialog.askopenfilename(
            title="Select Template File",
            filetypes=[("HTML files", "*.html"), ("All files", "*.*")]
        )

        if not filename:
            return

        try:
            library_path = Path("templates_library")
            library_path.mkdir(parents=True, exist_ok=True)

            # Copy file to library
            source = Path(filename)
            dest = library_path / source.name

            shutil.copy2(source, dest)

            InfoDialog.show(
                self,
                "Success",
                f"Template '{source.name}' added to library!"
            )
        except Exception as e:
            InfoDialog.show(self, "Error", f"Failed to add template:\n{str(e)}")
