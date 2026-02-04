"""CSV import wizard dialog for Lead Generator Standalone."""

import tkinter as tk
from tkinter import ttk, messagebox
from typing import Dict, List, Optional

from ui.theme import FONTS
from services.csv_service import CSVService


class CSVImportWizard(tk.Toplevel):
    """3-step CSV import wizard dialog."""

    def __init__(self, parent, file_path: str, list_id: int):
        super().__init__(parent)
        self.title("Import CSV")
        self.file_path = file_path
        self.list_id = list_id
        self.csv_service = CSVService()
        self.result = None

        self._current_step = 1
        self._headers: List[str] = []
        self._preview_data: List[List[str]] = []
        self._total_count = 0
        self._field_mapping: Dict[str, str] = {}

        # Make modal
        self.transient(parent)
        self.grab_set()

        self.geometry("700x500")
        self.resizable(True, True)

        self._create_widgets()
        self._load_preview()

    def _create_widgets(self) -> None:
        """Create wizard widgets."""
        # Step indicator
        self.step_frame = ttk.Frame(self)
        self.step_frame.pack(fill=tk.X, padx=20, pady=10)

        self.step_labels = []
        for i, text in enumerate(["1. Preview", "2. Map Fields", "3. Import"], 1):
            label = ttk.Label(self.step_frame, text=text)
            label.pack(side=tk.LEFT, padx=10)
            self.step_labels.append(label)

        ttk.Separator(self, orient=tk.HORIZONTAL).pack(fill=tk.X)

        # Content area
        self.content_frame = ttk.Frame(self)
        self.content_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)

        # Navigation buttons
        nav_frame = ttk.Frame(self)
        nav_frame.pack(fill=tk.X, padx=20, pady=10)

        self.cancel_btn = ttk.Button(nav_frame, text="Cancel", command=self.destroy)
        self.cancel_btn.pack(side=tk.LEFT)

        self.next_btn = ttk.Button(nav_frame, text="Next", command=self._next_step)
        self.next_btn.pack(side=tk.RIGHT)

        self.back_btn = ttk.Button(nav_frame, text="Back", command=self._prev_step, state='disabled')
        self.back_btn.pack(side=tk.RIGHT, padx=(0, 10))

        self._show_step_1()

    def _update_step_indicators(self) -> None:
        """Update step indicator styles."""
        for i, label in enumerate(self.step_labels, 1):
            if i == self._current_step:
                label.configure(font=('Segoe UI', 10, 'bold'))
            else:
                label.configure(font=('Segoe UI', 10))

    def _load_preview(self) -> None:
        """Load CSV preview data."""
        try:
            self._headers, self._preview_data, self._total_count = \
                self.csv_service.read_csv_preview(self.file_path, max_rows=5)
            self._field_mapping = self.csv_service.auto_map_fields(self._headers)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to read CSV: {e}")
            self.destroy()

    def _show_step_1(self) -> None:
        """Show step 1: Preview."""
        self._current_step = 1
        self._update_step_indicators()
        self._clear_content()

        ttk.Label(self.content_frame, text="CSV Preview", font=FONTS['subheading']).pack(anchor='w', pady=(0, 10))
        ttk.Label(self.content_frame, text=f"File: {self.file_path}").pack(anchor='w')
        ttk.Label(self.content_frame, text=f"Total rows: {self._total_count}").pack(anchor='w', pady=(0, 10))

        # Preview table
        tree = ttk.Treeview(self.content_frame, columns=self._headers, show='headings', height=6)

        for header in self._headers:
            tree.heading(header, text=header)
            tree.column(header, width=100)

        for row in self._preview_data:
            tree.insert('', 'end', values=row)

        tree.pack(fill=tk.BOTH, expand=True)

        self.back_btn.configure(state='disabled')
        self.next_btn.configure(text="Next")

    def _show_step_2(self) -> None:
        """Show step 2: Field mapping."""
        self._current_step = 2
        self._update_step_indicators()
        self._clear_content()

        ttk.Label(self.content_frame, text="Map Fields", font=FONTS['subheading']).pack(anchor='w', pady=(0, 10))

        # Scrollable mapping area
        canvas = tk.Canvas(self.content_frame)
        scrollbar = ttk.Scrollbar(self.content_frame, orient=tk.VERTICAL, command=canvas.yview)
        mapping_frame = ttk.Frame(canvas)

        canvas.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        canvas.create_window((0, 0), window=mapping_frame, anchor='nw')

        # Field options
        field_options = [
            '(ignore)', 'title', 'first_name', 'last_name', 'email', 'company',
            'position', 'phone', 'linkedin_url', 'source',
            'custom1', 'custom2', 'custom3', 'custom4', 'custom5',
            'custom6', 'custom7', 'custom8', 'custom9', 'custom10'
        ]

        self._mapping_vars = {}
        for i, header in enumerate(self._headers):
            ttk.Label(mapping_frame, text=f"{header}:").grid(row=i, column=0, sticky='w', pady=2, padx=(0, 10))

            var = tk.StringVar()
            combo = ttk.Combobox(mapping_frame, textvariable=var, values=field_options, state='readonly', width=20)
            combo.grid(row=i, column=1, sticky='w', pady=2)

            # Set auto-detected mapping
            if header in self._field_mapping:
                var.set(self._field_mapping[header])
            else:
                var.set('(ignore)')

            self._mapping_vars[header] = var

        mapping_frame.update_idletasks()
        canvas.configure(scrollregion=canvas.bbox('all'))

        self.back_btn.configure(state='normal')
        self.next_btn.configure(text="Import")

    def _show_step_3(self) -> None:
        """Show step 3: Import progress and results."""
        self._current_step = 3
        self._update_step_indicators()
        self._clear_content()

        ttk.Label(self.content_frame, text="Importing...", font=FONTS['subheading']).pack(anchor='w', pady=(0, 10))

        self.progress = ttk.Progressbar(self.content_frame, mode='indeterminate')
        self.progress.pack(fill=tk.X, pady=10)
        self.progress.start()

        self.status_label = ttk.Label(self.content_frame, text="Processing...")
        self.status_label.pack(anchor='w')

        self.back_btn.configure(state='disabled')
        self.next_btn.configure(state='disabled')

        # Run import
        self.after(100, self._do_import)

    def _do_import(self) -> None:
        """Perform the actual import."""
        # Build mapping from vars
        mapping = {}
        for header, var in self._mapping_vars.items():
            value = var.get()
            if value != '(ignore)':
                mapping[header] = value

        try:
            imported, errors = self.csv_service.import_csv(
                self.file_path,
                self.list_id,
                mapping
            )

            self.progress.stop()
            self.progress.pack_forget()

            # Show results
            self.status_label.configure(text=f"Import complete!")

            result_text = f"Successfully imported: {imported}\n"
            if errors:
                result_text += f"Errors/Skipped: {len(errors)}\n\n"
                result_text += "First few errors:\n"
                for err in errors[:5]:
                    result_text += f"  Row {err['row']}: {err['error']}\n"

            ttk.Label(self.content_frame, text=result_text, justify=tk.LEFT).pack(anchor='w', pady=10)

            self.result = {'imported': imported, 'errors': errors}
            self.next_btn.configure(text="Close", state='normal', command=self.destroy)

        except Exception as e:
            self.progress.stop()
            self.status_label.configure(text=f"Error: {e}")
            self.next_btn.configure(text="Close", state='normal', command=self.destroy)

    def _clear_content(self) -> None:
        """Clear content frame."""
        for widget in self.content_frame.winfo_children():
            widget.destroy()

    def _next_step(self) -> None:
        """Go to next step."""
        if self._current_step == 1:
            self._show_step_2()
        elif self._current_step == 2:
            self._show_step_3()

    def _prev_step(self) -> None:
        """Go to previous step."""
        if self._current_step == 2:
            self._show_step_1()
        elif self._current_step == 3:
            self._show_step_2()
