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


class SendOptionsDialog(ctk.CTkToplevel):
    """Dialog for choosing email sending options."""

    def __init__(
        self,
        parent,
        title: str = "Email Sending Options",
        default_mode: str = "send",
        default_defer_hours: int = 1,
        msg_folder: str = "msg_files"
    ):
        """Initialize send options dialog.

        Args:
            parent: Parent window
            title: Dialog title
            default_mode: Default send mode ("send", "msg_file", "defer")
            default_defer_hours: Default hours to defer
            msg_folder: Default .msg folder path
        """
        super().__init__(parent)

        self.result: Optional[Dict] = None

        # Window configuration
        self.title(title)
        self.geometry("500x300")
        self.resizable(False, False)

        # Make modal
        self.transient(parent)
        self.grab_set()

        # Center on parent
        self.update_idletasks()
        x = parent.winfo_x() + (parent.winfo_width() - 500) // 2
        y = parent.winfo_y() + (parent.winfo_height() - 300) // 2
        self.geometry(f"+{x}+{y}")

        # Configure grid
        self.grid_columnconfigure(0, weight=1)

        # Instructions
        instructions = ctk.CTkLabel(
            self,
            text="Choose how to send the email:",
            font=("Arial Bold", 13)
        )
        instructions.grid(row=0, column=0, pady=(20, 10), padx=20, sticky="w")

        # Send mode radio buttons
        self.mode_var = StringVar(value=default_mode)

        radio_frame = ctk.CTkFrame(self, fg_color="transparent")
        radio_frame.grid(row=1, column=0, pady=10, padx=40, sticky="w")

        send_radio = ctk.CTkRadioButton(
            radio_frame,
            text="Send Immediately - Send via Outlook now",
            variable=self.mode_var,
            value="send",
            font=("Arial", 11)
        )
        send_radio.pack(anchor="w", pady=5)

        msg_radio = ctk.CTkRadioButton(
            radio_frame,
            text="Save as .msg File - Create .msg file for manual review",
            variable=self.mode_var,
            value="msg_file",
            font=("Arial", 11)
        )
        msg_radio.pack(anchor="w", pady=5)

        defer_radio = ctk.CTkRadioButton(
            radio_frame,
            text="Defer Send - Schedule for later delivery",
            variable=self.mode_var,
            value="defer",
            font=("Arial", 11)
        )
        defer_radio.pack(anchor="w", pady=5)

        # Options frame
        options_frame = ctk.CTkFrame(self, fg_color="transparent")
        options_frame.grid(row=2, column=0, pady=10, padx=40, sticky="ew")
        options_frame.grid_columnconfigure(1, weight=1)

        # Defer hours
        defer_label = ctk.CTkLabel(
            options_frame,
            text="Defer hours:",
            font=("Arial", 11)
        )
        defer_label.grid(row=0, column=0, pady=5, padx=(0, 10), sticky="w")

        self.defer_var = StringVar(value=str(default_defer_hours))
        defer_entry = ctk.CTkEntry(
            options_frame,
            textvariable=self.defer_var,
            width=80
        )
        defer_entry.grid(row=0, column=1, pady=5, sticky="w")

        # .msg folder
        msg_label = ctk.CTkLabel(
            options_frame,
            text=".msg folder:",
            font=("Arial", 11)
        )
        msg_label.grid(row=1, column=0, pady=5, padx=(0, 10), sticky="w")

        self.msg_folder_var = StringVar(value=msg_folder)
        msg_entry = ctk.CTkEntry(
            options_frame,
            textvariable=self.msg_folder_var,
            width=300
        )
        msg_entry.grid(row=1, column=1, pady=5, sticky="w")

        # Button frame
        button_frame = ctk.CTkFrame(self, fg_color="transparent")
        button_frame.grid(row=3, column=0, pady=20)

        # Cancel button
        cancel_btn = ctk.CTkButton(
            button_frame,
            text="Cancel",
            command=self._on_cancel,
            width=120,
            fg_color="gray"
        )
        cancel_btn.pack(side="left", padx=5)

        # Send/Save button
        send_btn = ctk.CTkButton(
            button_frame,
            text="Send/Save",
            command=self._on_send,
            width=120
        )
        send_btn.pack(side="left", padx=5)

        # Bind Enter and Escape
        self.bind('<Return>', lambda e: self._on_send())
        self.bind('<Escape>', lambda e: self._on_cancel())

    def _on_send(self) -> None:
        """Handle send/save button click."""
        mode = self.mode_var.get()

        # Validate defer hours
        defer_hours = 1
        if mode == "defer":
            try:
                defer_hours = int(self.defer_var.get())
                if defer_hours < 0:
                    InfoDialog.show(self, "Invalid Input", "Defer hours must be positive.")
                    return
            except ValueError:
                InfoDialog.show(self, "Invalid Input", "Defer hours must be a number.")
                return

        self.result = {
            "mode": mode,
            "defer_hours": defer_hours,
            "msg_folder": self.msg_folder_var.get()
        }
        self.destroy()

    def _on_cancel(self) -> None:
        """Handle cancel button click."""
        self.result = None
        self.destroy()

    def get_result(self) -> Optional[Dict]:
        """Show dialog and return result.

        Returns:
            Dict with mode, defer_hours, msg_folder or None if cancelled
        """
        self.wait_window()
        return self.result
