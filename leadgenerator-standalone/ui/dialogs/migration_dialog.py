"""Migration export dialog for Lead Generator Standalone."""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from typing import List

from ui.theme import FONTS
from services.campaign_service import CampaignService
from migration.exporter import export_to_json


class MigrationDialog(tk.Toplevel):
    """Dialog for exporting data for migration to multi-user version."""

    def __init__(self, parent):
        super().__init__(parent)
        self.title("Export for Migration")
        self.campaign_service = CampaignService()

        # Make modal
        self.transient(parent)
        self.grab_set()

        self.geometry("500x400")
        self.resizable(False, False)

        self._create_widgets()
        self._load_campaigns()

        self.wait_window()

    def _create_widgets(self) -> None:
        """Create dialog widgets."""
        # Header
        ttk.Label(self, text="Export Data for Migration", font=FONTS['heading']).pack(padx=20, pady=(20, 10))

        ttk.Label(self, text="Export your data for migration to the multi-user version.\nSelect campaigns to export or export all data.", wraplength=450).pack(padx=20, pady=(0, 20))

        # Options
        self.export_all_var = tk.BooleanVar(value=True)
        ttk.Radiobutton(self, text="Export all data", variable=self.export_all_var, value=True, command=self._toggle_selection).pack(anchor='w', padx=20)

        ttk.Radiobutton(self, text="Export selected campaigns:", variable=self.export_all_var, value=False, command=self._toggle_selection).pack(anchor='w', padx=20, pady=(10, 5))

        # Campaign list
        list_frame = ttk.Frame(self)
        list_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=(0, 10))

        self.campaign_listbox = tk.Listbox(list_frame, selectmode=tk.MULTIPLE, height=8)
        self.campaign_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.campaign_listbox.configure(state='disabled')

        scrollbar = ttk.Scrollbar(list_frame, orient=tk.VERTICAL, command=self.campaign_listbox.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.campaign_listbox.configure(yscrollcommand=scrollbar.set)

        # Progress
        self.progress = ttk.Progressbar(self, mode='indeterminate')
        self.status_label = ttk.Label(self, text="")

        # Buttons
        btn_frame = ttk.Frame(self)
        btn_frame.pack(pady=20)

        ttk.Button(btn_frame, text="Export", command=self._export).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="Cancel", command=self.destroy).pack(side=tk.LEFT, padx=5)

    def _load_campaigns(self) -> None:
        """Load campaigns into listbox."""
        campaigns = self.campaign_service.get_all_campaigns()
        self._campaigns = campaigns

        for campaign in campaigns:
            self.campaign_listbox.insert(tk.END, f"{campaign.campaign_ref} - {campaign.name}")

    def _toggle_selection(self) -> None:
        """Toggle campaign selection based on export option."""
        if self.export_all_var.get():
            self.campaign_listbox.configure(state='disabled')
            self.campaign_listbox.selection_clear(0, tk.END)
        else:
            self.campaign_listbox.configure(state='normal')

    def _export(self) -> None:
        """Perform export."""
        # Get output path
        file_path = filedialog.asksaveasfilename(
            title="Save Export File",
            defaultextension=".json",
            filetypes=[("JSON Files", "*.json")]
        )

        if not file_path:
            return

        # Get campaign IDs if not exporting all
        campaign_ids = None
        if not self.export_all_var.get():
            selection = self.campaign_listbox.curselection()
            if selection:
                campaign_ids = [self._campaigns[i].campaign_id for i in selection]
            else:
                messagebox.showwarning("Warning", "Please select at least one campaign")
                return

        # Show progress
        self.progress.pack(fill=tk.X, padx=20)
        self.progress.start()
        self.status_label.configure(text="Exporting...")
        self.status_label.pack(padx=20)
        self.update()

        try:
            export_to_json(file_path, campaign_ids)

            self.progress.stop()
            self.progress.pack_forget()
            self.status_label.configure(text="Export complete!")

            messagebox.showinfo("Success", f"Data exported to:\n{file_path}\n\nUse this file to import into the multi-user version.")

        except Exception as e:
            self.progress.stop()
            self.status_label.configure(text=f"Error: {e}")
            messagebox.showerror("Error", str(e))
