"""Dialog Windows

Custom dialog windows for user interactions.
"""

import customtkinter as ctk
from typing import Optional, Dict, List, Callable
from tkinter import StringVar


class ConfirmationDialog(ctk.CTkToplevel):
    """Modal confirmation dialog for destructive actions."""

    def __init__(
        self,
        parent,
        title: str,
        message: str,
        confirm_text: str = "Confirm",
        cancel_text: str = "Cancel",
        danger: bool = False
    ):
        """Initialize confirmation dialog.

        Args:
            parent: Parent window
            title: Dialog title
            message: Confirmation message
            confirm_text: Text for confirm button
            cancel_text: Text for cancel button
            danger: If True, confirm button is red
        """
        super().__init__(parent)

        self.result = False

        # Window configuration
        self.title(title)
        self.geometry("400x200")
        self.resizable(False, False)

        # Make modal
        self.transient(parent)
        self.grab_set()

        # Center on parent
        self.update_idletasks()
        x = parent.winfo_x() + (parent.winfo_width() - 400) // 2
        y = parent.winfo_y() + (parent.winfo_height() - 200) // 2
        self.geometry(f"+{x}+{y}")

        # Configure grid
        self.grid_columnconfigure(0, weight=1)

        # Message label
        message_label = ctk.CTkLabel(
            self,
            text=message,
            wraplength=350,
            font=("Arial", 12)
        )
        message_label.grid(row=0, column=0, pady=(30, 20), padx=20)

        # Button frame
        button_frame = ctk.CTkFrame(self, fg_color="transparent")
        button_frame.grid(row=1, column=0, pady=(0, 20))

        # Cancel button
        cancel_btn = ctk.CTkButton(
            button_frame,
            text=cancel_text,
            command=self._on_cancel,
            width=120,
            fg_color="gray"
        )
        cancel_btn.pack(side="left", padx=5)

        # Confirm button
        confirm_color = "#EF4444" if danger else "#3B82F6"
        confirm_btn = ctk.CTkButton(
            button_frame,
            text=confirm_text,
            command=self._on_confirm,
            width=120,
            fg_color=confirm_color
        )
        confirm_btn.pack(side="left", padx=5)

        # Bind Enter and Escape
        self.bind('<Return>', lambda e: self._on_confirm())
        self.bind('<Escape>', lambda e: self._on_cancel())

    def _on_confirm(self) -> None:
        """Handle confirm button click."""
        self.result = True
        self.destroy()

    def _on_cancel(self) -> None:
        """Handle cancel button click."""
        self.result = False
        self.destroy()

    def get_result(self) -> bool:
        """Show dialog and return result.

        Returns:
            True if confirmed, False if cancelled
        """
        self.wait_window()
        return self.result


class CSVImportDialog(ctk.CTkToplevel):
    """Column mapping dialog for CSV import."""

    def __init__(
        self,
        parent,
        csv_columns: List[str],
        system_fields: List[str]
    ):
        """Initialize CSV import dialog.

        Args:
            parent: Parent window
            csv_columns: List of CSV column names
            system_fields: List of system field names
        """
        super().__init__(parent)

        self.csv_columns = csv_columns
        self.system_fields = ['(skip)'] + system_fields
        self.mapping: Optional[Dict[str, str]] = None
        self.dropdowns: Dict[str, ctk.CTkOptionMenu] = {}

        # Window configuration
        self.title("CSV Import - Map Columns")
        self.geometry("600x500")

        # Make modal
        self.transient(parent)
        self.grab_set()

        # Center on parent
        self.update_idletasks()
        x = parent.winfo_x() + (parent.winfo_width() - 600) // 2
        y = parent.winfo_y() + (parent.winfo_height() - 500) // 2
        self.geometry(f"+{x}+{y}")

        # Configure grid
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)

        # Instructions
        instructions = ctk.CTkLabel(
            self,
            text="Map CSV columns to system fields:",
            font=("Arial Bold", 13)
        )
        instructions.grid(row=0, column=0, pady=(20, 10), padx=20, sticky="w")

        # Scrollable frame for mappings
        scroll_frame = ctk.CTkScrollableFrame(self, width=560, height=300)
        scroll_frame.grid(row=1, column=0, pady=10, padx=20, sticky="nsew")
        scroll_frame.grid_columnconfigure(1, weight=1)

        # Create mapping rows
        for i, csv_col in enumerate(csv_columns):
            # CSV column label
            csv_label = ctk.CTkLabel(
                scroll_frame,
                text=csv_col,
                font=("Arial", 11),
                width=200,
                anchor="w"
            )
            csv_label.grid(row=i, column=0, pady=5, padx=(10, 5), sticky="w")

            # Arrow
            arrow_label = ctk.CTkLabel(scroll_frame, text="→", font=("Arial", 14))
            arrow_label.grid(row=i, column=1, pady=5, padx=5)

            # System field dropdown
            var = StringVar(value=self._auto_match_field(csv_col))
            dropdown = ctk.CTkOptionMenu(
                scroll_frame,
                variable=var,
                values=self.system_fields,
                width=200
            )
            dropdown.grid(row=i, column=2, pady=5, padx=(5, 10), sticky="e")

            self.dropdowns[csv_col] = var

        # Button frame
        button_frame = ctk.CTkFrame(self, fg_color="transparent")
        button_frame.grid(row=2, column=0, pady=20)

        # Cancel button
        cancel_btn = ctk.CTkButton(
            button_frame,
            text="Cancel",
            command=self._on_cancel,
            width=120,
            fg_color="gray"
        )
        cancel_btn.pack(side="left", padx=5)

        # Import button
        import_btn = ctk.CTkButton(
            button_frame,
            text="Import",
            command=self._on_import,
            width=120
        )
        import_btn.pack(side="left", padx=5)

    def _auto_match_field(self, csv_column: str) -> str:
        """Auto-match CSV column to system field.

        Args:
            csv_column: CSV column name

        Returns:
            Best matching system field or '(skip)'
        """
        csv_lower = csv_column.lower()

        # Common mappings
        mappings = {
            'email': 'email',
            'e-mail': 'email',
            'mail': 'email',
            'first': 'first_name',
            'firstname': 'first_name',
            'prenom': 'first_name',
            'prénom': 'first_name',
            'last': 'last_name',
            'lastname': 'last_name',
            'surname': 'last_name',
            'nom': 'last_name',
            'title': 'title',
            'titre': 'title',
            'civilite': 'title',
            'civilité': 'title',
            'company': 'company',
            'société': 'company',
            'societe': 'company',
            'organization': 'company',
            'status': 'status',
            'statut': 'status'
        }

        for key, field in mappings.items():
            if key in csv_lower and field in self.system_fields:
                return field

        return '(skip)'

    def _on_import(self) -> None:
        """Handle import button click."""
        # Build mapping dictionary
        self.mapping = {}
        for csv_col, var in self.dropdowns.items():
            system_field = var.get()
            if system_field != '(skip)':
                self.mapping[csv_col] = system_field

        self.destroy()

    def _on_cancel(self) -> None:
        """Handle cancel button click."""
        self.mapping = None
        self.destroy()

    def get_mapping(self) -> Optional[Dict[str, str]]:
        """Show dialog and return mapping.

        Returns:
            Dictionary mapping CSV columns to system fields, or None if cancelled
        """
        self.wait_window()
        return self.mapping


class ProgressDialog(ctk.CTkToplevel):
    """Non-blocking progress dialog for long operations."""

    def __init__(
        self,
        parent,
        title: str,
        total: int = 100,
        cancelable: bool = False,
        on_cancel: Optional[Callable] = None
    ):
        """Initialize progress dialog.

        Args:
            parent: Parent window
            title: Dialog title
            total: Total number of steps
            cancelable: Whether user can cancel operation
            on_cancel: Callback when cancelled
        """
        super().__init__(parent)

        self.total = max(1, total)
        self.current = 0
        self.cancelled = False
        self.on_cancel = on_cancel

        # Window configuration
        self.title(title)
        self.geometry("400x180")
        self.resizable(False, False)

        # Make modal
        self.transient(parent)

        # Center on parent
        self.update_idletasks()
        x = parent.winfo_x() + (parent.winfo_width() - 400) // 2
        y = parent.winfo_y() + (parent.winfo_height() - 180) // 2
        self.geometry(f"+{x}+{y}")

        # Configure grid
        self.grid_columnconfigure(0, weight=1)

        # Message label
        self.message_label = ctk.CTkLabel(
            self,
            text="Processing...",
            font=("Arial", 12)
        )
        self.message_label.grid(row=0, column=0, pady=(30, 10), padx=20)

        # Progress bar
        self.progress_bar = ctk.CTkProgressBar(self, width=350)
        self.progress_bar.set(0)
        self.progress_bar.grid(row=1, column=0, pady=10, padx=25)

        # Progress label
        self.progress_label = ctk.CTkLabel(
            self,
            text="0%",
            font=("Arial", 10),
            text_color="gray"
        )
        self.progress_label.grid(row=2, column=0, pady=(0, 10))

        # Cancel button (optional)
        if cancelable:
            cancel_btn = ctk.CTkButton(
                self,
                text="Cancel",
                command=self._on_cancel,
                width=100,
                fg_color="gray"
            )
            cancel_btn.grid(row=3, column=0, pady=(0, 20))

        # Prevent closing with X button if not cancelable
        if not cancelable:
            self.protocol("WM_DELETE_WINDOW", lambda: None)

    def update(self, current: int, message: str = "") -> None:
        """Update progress.

        Args:
            current: Current step number
            message: Status message
        """
        self.current = current
        progress = min(1.0, current / self.total)

        self.progress_bar.set(progress)
        self.progress_label.configure(text=f"{int(progress * 100)}%")

        if message:
            self.message_label.configure(text=message)

        self.update_idletasks()

    def increment(self, message: str = "") -> None:
        """Increment progress by one step.

        Args:
            message: Status message
        """
        self.update(self.current + 1, message)

    def _on_cancel(self) -> None:
        """Handle cancel button click."""
        self.cancelled = True
        if self.on_cancel:
            self.on_cancel()
        self.destroy()

    def is_cancelled(self) -> bool:
        """Check if operation was cancelled.

        Returns:
            True if cancelled
        """
        return self.cancelled

    def close(self) -> None:
        """Close dialog."""
        if not self.cancelled:
            self.destroy()


class InfoDialog(ctk.CTkToplevel):
    """Simple information dialog."""

    def __init__(self, parent, title: str, message: str):
        """Initialize info dialog.

        Args:
            parent: Parent window
            title: Dialog title
            message: Information message
        """
        super().__init__(parent)

        # Window configuration
        self.title(title)
        self.geometry("400x150")
        self.resizable(False, False)

        # Make modal
        self.transient(parent)
        self.grab_set()

        # Center on parent
        self.update_idletasks()
        x = parent.winfo_x() + (parent.winfo_width() - 400) // 2
        y = parent.winfo_y() + (parent.winfo_height() - 150) // 2
        self.geometry(f"+{x}+{y}")

        # Message
        message_label = ctk.CTkLabel(
            self,
            text=message,
            wraplength=350,
            font=("Arial", 12)
        )
        message_label.pack(pady=(30, 20), padx=20)

        # OK button
        ok_btn = ctk.CTkButton(
            self,
            text="OK",
            command=self.destroy,
            width=100
        )
        ok_btn.pack(pady=(0, 20))

        # Bind Enter and Escape
        self.bind('<Return>', lambda e: self.destroy())
        self.bind('<Escape>', lambda e: self.destroy())

    @staticmethod
    def show(parent, title: str, message: str) -> None:
        """Show info dialog (static method).

        Args:
            parent: Parent window
            title: Dialog title
            message: Information message
        """
        dialog = InfoDialog(parent, title, message)
        dialog.wait_window()


class CampaignDialog(ctk.CTkToplevel):
    """Dialog for creating or selecting campaigns."""

    def __init__(self, parent, campaign_manager, current_campaign: Optional[str] = None):
        """Initialize campaign dialog.

        Args:
            parent: Parent window
            campaign_manager: CampaignManager instance
            current_campaign: Currently selected campaign name
        """
        super().__init__(parent)

        self.campaign_manager = campaign_manager
        self.selected_campaign = current_campaign
        self.result = None

        # Window configuration
        self.title("Campaign Manager")
        self.geometry("600x450")
        self.resizable(False, False)

        # Make modal
        self.transient(parent)
        self.grab_set()

        # Center on parent
        self.update_idletasks()
        x = parent.winfo_x() + (parent.winfo_width() - 600) // 2
        y = parent.winfo_y() + (parent.winfo_height() - 450) // 2
        self.geometry(f"+{x}+{y}")

        # Configure grid
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)

        # Create UI
        self._create_header()
        self._create_campaign_list()
        self._create_actions()
        self._create_buttons()

        # Load campaigns
        self.refresh_campaigns()

    def _create_header(self) -> None:
        """Create header."""
        header_frame = ctk.CTkFrame(self, fg_color="transparent")
        header_frame.grid(row=0, column=0, sticky="ew", padx=20, pady=(20, 10))

        title = ctk.CTkLabel(
            header_frame,
            text="Select or Create Campaign",
            font=("Arial Bold", 16)
        )
        title.pack(side="left")

    def _create_campaign_list(self) -> None:
        """Create campaign list."""
        list_frame = ctk.CTkFrame(self)
        list_frame.grid(row=1, column=0, sticky="nsew", padx=20, pady=10)
        list_frame.grid_columnconfigure(0, weight=1)
        list_frame.grid_rowconfigure(0, weight=1)

        # Scrollable frame for campaigns
        self.campaigns_frame = ctk.CTkScrollableFrame(list_frame, width=540, height=250)
        self.campaigns_frame.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)
        self.campaigns_frame.grid_columnconfigure(0, weight=1)

    def _create_actions(self) -> None:
        """Create action buttons."""
        actions_frame = ctk.CTkFrame(self, fg_color="transparent")
        actions_frame.grid(row=2, column=0, sticky="ew", padx=20, pady=10)

        # New campaign name entry
        ctk.CTkLabel(actions_frame, text="New Campaign:").pack(side="left", padx=(0, 10))
        
        self.new_campaign_var = StringVar()
        self.new_campaign_entry = ctk.CTkEntry(
            actions_frame,
            textvariable=self.new_campaign_var,
            placeholder_text="campaign_name",
            width=250
        )
        self.new_campaign_entry.pack(side="left", padx=5)

        # Create button
        create_btn = ctk.CTkButton(
            actions_frame,
            text="+ Create",
            command=self.on_create_campaign,
            width=100,
            fg_color="#10B981"
        )
        create_btn.pack(side="left", padx=5)

        # Delete button
        delete_btn = ctk.CTkButton(
            actions_frame,
            text="Delete",
            command=self.on_delete_campaign,
            width=100,
            fg_color="#EF4444"
        )
        delete_btn.pack(side="left", padx=5)

    def _create_buttons(self) -> None:
        """Create dialog buttons."""
        button_frame = ctk.CTkFrame(self, fg_color="transparent")
        button_frame.grid(row=3, column=0, pady=(0, 20))

        cancel_btn = ctk.CTkButton(
            button_frame,
            text="Cancel",
            command=self.on_cancel,
            width=120,
            fg_color="gray"
        )
        cancel_btn.pack(side="left", padx=5)

        select_btn = ctk.CTkButton(
            button_frame,
            text="Select Campaign",
            command=self.on_select,
            width=150
        )
        select_btn.pack(side="left", padx=5)

    def refresh_campaigns(self) -> None:
        """Refresh campaign list."""
        # Clear existing
        for widget in self.campaigns_frame.winfo_children():
            widget.destroy()

        # Get campaigns
        campaigns = self.campaign_manager.list_campaigns()

        if not campaigns:
            no_campaigns_label = ctk.CTkLabel(
                self.campaigns_frame,
                text="No campaigns yet. Create one below.",
                font=("Arial", 12),
                text_color="gray"
            )
            no_campaigns_label.pack(pady=50)
            return

        # Display campaigns
        for i, campaign_name in enumerate(campaigns):
            campaign = self.campaign_manager.get_campaign(campaign_name)
            config = campaign.get_config()
            
            # Campaign frame
            camp_frame = ctk.CTkFrame(
                self.campaigns_frame,
                fg_color=("#E5E7EB", "#374151") if campaign_name == self.selected_campaign else "transparent"
            )
            camp_frame.grid(row=i, column=0, sticky="ew", padx=5, pady=5)
            camp_frame.grid_columnconfigure(0, weight=1)

            # Campaign name
            name_label = ctk.CTkLabel(
                camp_frame,
                text=campaign_name,
                font=("Arial Bold", 13),
                anchor="w"
            )
            name_label.grid(row=0, column=0, sticky="w", padx=15, pady=(10, 2))

            # Campaign details
            created = config.get('campaign', {}).get('created', 'Unknown')
            status = config.get('campaign', {}).get('status', 'unknown')
            
            details_text = f"Created: {created} | Status: {status.title()}"
            details_label = ctk.CTkLabel(
                camp_frame,
                text=details_text,
                font=("Arial", 10),
                text_color="gray",
                anchor="w"
            )
            details_label.grid(row=1, column=0, sticky="w", padx=15, pady=(0, 10))

            # Select button
            select_btn = ctk.CTkButton(
                camp_frame,
                text="Select" if campaign_name != self.selected_campaign else "✓ Current",
                command=lambda name=campaign_name: self.select_campaign(name),
                width=100,
                height=28,
                fg_color="#3B82F6" if campaign_name != self.selected_campaign else "#10B981"
            )
            select_btn.grid(row=0, column=1, rowspan=2, padx=15, pady=10)

    def select_campaign(self, name: str) -> None:
        """Select a campaign.

        Args:
            name: Campaign name
        """
        self.selected_campaign = name
        self.refresh_campaigns()

    def on_create_campaign(self) -> None:
        """Handle create campaign."""
        name = self.new_campaign_var.get().strip()
        
        if not name:
            InfoDialog.show(self, "Validation Error", "Please enter a campaign name.")
            return

        # Validate name (no special characters)
        import re
        if not re.match(r'^[a-zA-Z0-9_-]+$', name):
            InfoDialog.show(
                self,
                "Validation Error",
                "Campaign name can only contain letters, numbers, hyphens, and underscores."
            )
            return

        if self.campaign_manager.campaign_exists(name):
            InfoDialog.show(self, "Error", f"Campaign '{name}' already exists.")
            return

        # Create campaign
        try:
            self.campaign_manager.create_campaign(name, sample_contacts=True)
            self.selected_campaign = name
            self.new_campaign_var.set("")
            self.refresh_campaigns()
            InfoDialog.show(
                self,
                "Success",
                f"Campaign '{name}' created with 3 sample contacts."
            )
        except Exception as e:
            InfoDialog.show(self, "Error", f"Failed to create campaign:\n{str(e)}")

    def on_delete_campaign(self) -> None:
        """Handle delete campaign."""
        if not self.selected_campaign:
            InfoDialog.show(self, "No Selection", "Please select a campaign to delete.")
            return

        # Confirm deletion
        confirm = ConfirmationDialog(
            self,
            "Delete Campaign",
            f"Delete campaign '{self.selected_campaign}'?\n\nThis will permanently delete all contacts, templates, and configuration.",
            confirm_text="Delete",
            danger=True
        )

        if not confirm.get_result():
            return

        # Delete campaign
        try:
            self.campaign_manager.delete_campaign(self.selected_campaign)
            self.selected_campaign = None
            self.refresh_campaigns()
            InfoDialog.show(self, "Success", "Campaign deleted successfully.")
        except Exception as e:
            InfoDialog.show(self, "Error", f"Failed to delete campaign:\n{str(e)}")

    def on_select(self) -> None:
        """Handle select button."""
        if not self.selected_campaign:
            InfoDialog.show(self, "No Selection", "Please select a campaign.")
            return

        self.result = self.selected_campaign
        self.destroy()

    def on_cancel(self) -> None:
        """Handle cancel button."""
        self.result = None
        self.destroy()

    def get_result(self) -> Optional[str]:
        """Show dialog and return selected campaign.

        Returns:
            Selected campaign name or None
        """
        self.wait_window()
        return self.result
