"""CSV import wizard dialog."""
import logging
import tkinter as tk
from tkinter import filedialog
from typing import Optional, Dict, List
import ttkbootstrap as ttk
from ttkbootstrap.constants import *
from ttkbootstrap.tableview import Tableview

from core.api_client import ApiClient
from services.csv_service import CsvService, FieldMapping

logger = logging.getLogger(__name__)


class CsvImportWizard(ttk.Toplevel):
    """3-step CSV import wizard."""

    def __init__(self, parent, api: ApiClient, list_id: str):
        super().__init__(parent)

        self.api = api
        self.list_id = list_id
        self.result = None
        self.csv_service = CsvService()

        self.title("Import Contacts from CSV")
        self.geometry("700x550")
        self.resizable(False, False)

        self.current_step = 1

        self._create_widgets()

        self.transient(parent)
        self.grab_set()

    def _create_widgets(self) -> None:
        """Create wizard widgets."""
        # Header with steps
        header = ttk.Frame(self, padding=15)
        header.pack(fill=X)

        self.step_labels = []
        for i, text in enumerate(["Upload File", "Map Fields", "Review & Import"], 1):
            frame = ttk.Frame(header)
            frame.pack(side=LEFT, expand=True)

            circle = ttk.Label(
                frame,
                text=str(i),
                font=("Segoe UI", 12, "bold"),
                width=3,
                anchor="center"
            )
            circle.pack()

            label = ttk.Label(
                frame,
                text=text,
                font=("Segoe UI", 9)
            )
            label.pack()

            self.step_labels.append((circle, label))

        ttk.Separator(self).pack(fill=X)

        # Content area
        self.content = ttk.Frame(self, padding=20)
        self.content.pack(fill=BOTH, expand=True)

        # Step frames
        self.step1_frame = ttk.Frame(self.content)
        self.step2_frame = ttk.Frame(self.content)
        self.step3_frame = ttk.Frame(self.content)

        self._create_step1()
        self._create_step2()
        self._create_step3()

        # Footer with navigation
        ttk.Separator(self).pack(fill=X)

        footer = ttk.Frame(self, padding=15)
        footer.pack(fill=X)

        self.cancel_btn = ttk.Button(
            footer,
            text="Cancel",
            bootstyle="secondary",
            command=self.destroy
        )
        self.cancel_btn.pack(side=LEFT)

        self.next_btn = ttk.Button(
            footer,
            text="Next \u2192",
            bootstyle="primary",
            command=self._next_step
        )
        self.next_btn.pack(side=RIGHT)

        self.back_btn = ttk.Button(
            footer,
            text="\u2190 Back",
            bootstyle="outline-secondary",
            command=self._prev_step
        )
        self.back_btn.pack(side=RIGHT, padx=(0, 10))

        self._update_step_display()

    def _create_step1(self) -> None:
        """Create step 1: File upload."""
        ttk.Label(
            self.step1_frame,
            text="Select CSV File",
            font=("Segoe UI", 14, "bold")
        ).pack(anchor=W, pady=(0, 15))

        # File selection
        file_frame = ttk.Frame(self.step1_frame)
        file_frame.pack(fill=X, pady=(0, 15))

        self.file_var = tk.StringVar()
        self.file_entry = ttk.Entry(
            file_frame,
            textvariable=self.file_var,
            state="readonly",
            width=50
        )
        self.file_entry.pack(side=LEFT, fill=X, expand=True, padx=(0, 10))

        ttk.Button(
            file_frame,
            text="Browse...",
            bootstyle="outline-primary",
            command=self._browse_file
        ).pack(side=LEFT)

        # Preview
        self.preview_frame = ttk.LabelFrame(self.step1_frame, text="Preview", padding=10)
        self.preview_frame.pack(fill=BOTH, expand=True)

        self.preview_text = tk.Text(
            self.preview_frame,
            height=15,
            state="disabled",
            font=("Consolas", 9)
        )
        self.preview_text.pack(fill=BOTH, expand=True)

        # Info
        ttk.Label(
            self.step1_frame,
            text="Supported format: CSV with header row",
            font=("Segoe UI", 9),
            bootstyle="secondary"
        ).pack(anchor=W, pady=(10, 0))

    def _create_step2(self) -> None:
        """Create step 2: Field mapping."""
        ttk.Label(
            self.step2_frame,
            text="Map CSV Columns to Contact Fields",
            font=("Segoe UI", 14, "bold")
        ).pack(anchor=W, pady=(0, 15))

        # Mapping grid
        self.mapping_frame = ttk.Frame(self.step2_frame)
        self.mapping_frame.pack(fill=BOTH, expand=True)

        # Headers
        header_frame = ttk.Frame(self.mapping_frame)
        header_frame.pack(fill=X, pady=(0, 5))

        ttk.Label(header_frame, text="CSV Column", font=("Segoe UI", 10, "bold"), width=25).pack(side=LEFT)
        ttk.Label(header_frame, text="\u2192", width=3).pack(side=LEFT)
        ttk.Label(header_frame, text="Contact Field", font=("Segoe UI", 10, "bold"), width=25).pack(side=LEFT)

        ttk.Separator(self.mapping_frame).pack(fill=X, pady=5)

        # Scrollable mapping list
        canvas_frame = ttk.Frame(self.mapping_frame)
        canvas_frame.pack(fill=BOTH, expand=True)

        self.mapping_canvas = tk.Canvas(canvas_frame, highlightthickness=0)
        scrollbar = ttk.Scrollbar(canvas_frame, orient=VERTICAL, command=self.mapping_canvas.yview)
        self.mapping_list = ttk.Frame(self.mapping_canvas)

        self.mapping_canvas.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side=RIGHT, fill=Y)
        self.mapping_canvas.pack(side=LEFT, fill=BOTH, expand=True)

        self.mapping_canvas.create_window((0, 0), window=self.mapping_list, anchor="nw")
        self.mapping_list.bind("<Configure>", lambda e: self.mapping_canvas.configure(
            scrollregion=self.mapping_canvas.bbox("all")
        ))

        self.mapping_combos: Dict[str, ttk.Combobox] = {}

        # Auto-detect button
        ttk.Button(
            self.step2_frame,
            text="Auto-Detect Mappings",
            bootstyle="info-outline",
            command=self._auto_detect_mappings
        ).pack(anchor=W, pady=(10, 0))

    def _create_step3(self) -> None:
        """Create step 3: Review and import."""
        ttk.Label(
            self.step3_frame,
            text="Review and Import",
            font=("Segoe UI", 14, "bold")
        ).pack(anchor=W, pady=(0, 15))

        # Summary
        self.summary_frame = ttk.LabelFrame(self.step3_frame, text="Import Summary", padding=10)
        self.summary_frame.pack(fill=X, pady=(0, 15))

        self.summary_labels = {}
        for key, text in [
            ("total", "Total rows:"),
            ("valid", "Valid rows:"),
            ("invalid", "Invalid rows:"),
            ("duplicates", "Duplicate emails:")
        ]:
            row = ttk.Frame(self.summary_frame)
            row.pack(fill=X, pady=2)
            ttk.Label(row, text=text, width=20).pack(side=LEFT)
            lbl = ttk.Label(row, text="0")
            lbl.pack(side=LEFT)
            self.summary_labels[key] = lbl

        # Validation issues
        self.issues_frame = ttk.LabelFrame(self.step3_frame, text="Validation Issues", padding=10)
        self.issues_frame.pack(fill=BOTH, expand=True)

        self.issues_text = tk.Text(
            self.issues_frame,
            height=10,
            state="disabled",
            font=("Consolas", 9)
        )
        self.issues_text.pack(fill=BOTH, expand=True)

    def _browse_file(self) -> None:
        """Browse for CSV file."""
        filepath = filedialog.askopenfilename(
            filetypes=[("CSV files", "*.csv"), ("All files", "*.*")]
        )
        if filepath:
            self.file_var.set(filepath)
            self._load_preview(filepath)

    def _load_preview(self, filepath: str) -> None:
        """Load and preview CSV file."""
        try:
            self.csv_service.read_csv(file_path=filepath)
            preview = self.csv_service.get_preview(rows=5)

            # Show preview
            self.preview_text.configure(state="normal")
            self.preview_text.delete("1.0", tk.END)

            if preview:
                # Header
                headers = list(preview[0].keys())
                self.preview_text.insert(tk.END, " | ".join(headers) + "\n")
                self.preview_text.insert(tk.END, "-" * 60 + "\n")

                # Rows
                for row in preview:
                    values = [str(v)[:20] for v in row.values()]
                    self.preview_text.insert(tk.END, " | ".join(values) + "\n")

                self.preview_text.insert(tk.END, f"\n... {self.csv_service.get_row_count()} total rows")

            self.preview_text.configure(state="disabled")

        except Exception as e:
            self.preview_text.configure(state="normal")
            self.preview_text.delete("1.0", tk.END)
            self.preview_text.insert(tk.END, f"Error loading file: {str(e)}")
            self.preview_text.configure(state="disabled")

    def _populate_mappings(self) -> None:
        """Populate mapping dropdowns."""
        # Clear existing
        for widget in self.mapping_list.winfo_children():
            widget.destroy()
        self.mapping_combos.clear()

        columns = self.csv_service.get_columns()
        contact_fields = [
            ("-- Skip --", ""),
            ("Email *", "email"),
            ("First Name *", "first_name"),
            ("Last Name *", "last_name"),
            ("Company *", "company"),
            ("Title", "title"),
            ("Position", "position"),
            ("Phone", "phone"),
            ("LinkedIn", "linkedin_url"),
            ("Source", "source"),
        ]
        # Add custom fields
        for i in range(1, 11):
            contact_fields.append((f"Custom {i}", f"custom{i}"))

        for col in columns:
            row = ttk.Frame(self.mapping_list)
            row.pack(fill=X, pady=2)

            ttk.Label(row, text=col, width=25, anchor=W).pack(side=LEFT)
            ttk.Label(row, text="\u2192", width=3).pack(side=LEFT)

            combo = ttk.Combobox(
                row,
                values=[f[0] for f in contact_fields],
                state="readonly",
                width=22
            )
            combo.set("-- Skip --")
            combo.pack(side=LEFT)

            self.mapping_combos[col] = combo

        # Auto-detect
        self._auto_detect_mappings()

    def _auto_detect_mappings(self) -> None:
        """Auto-detect field mappings."""
        mappings = self.csv_service.auto_detect_mappings()

        field_to_display = {
            "email": "Email *",
            "first_name": "First Name *",
            "last_name": "Last Name *",
            "company": "Company *",
            "title": "Title",
            "position": "Position",
            "phone": "Phone",
            "linkedin_url": "LinkedIn",
            "source": "Source",
        }
        for i in range(1, 11):
            field_to_display[f"custom{i}"] = f"Custom {i}"

        for mapping in mappings:
            if mapping.csv_column in self.mapping_combos:
                display = field_to_display.get(mapping.contact_field, "-- Skip --")
                self.mapping_combos[mapping.csv_column].set(display)

    def _get_current_mappings(self) -> List[FieldMapping]:
        """Get current field mappings from UI."""
        display_to_field = {
            "Email *": "email",
            "First Name *": "first_name",
            "Last Name *": "last_name",
            "Company *": "company",
            "Title": "title",
            "Position": "position",
            "Phone": "phone",
            "LinkedIn": "linkedin_url",
            "Source": "source",
        }
        for i in range(1, 11):
            display_to_field[f"Custom {i}"] = f"custom{i}"

        mappings = []
        for col, combo in self.mapping_combos.items():
            display = combo.get()
            if display != "-- Skip --":
                field = display_to_field.get(display, "")
                if field:
                    is_custom = field.startswith("custom")
                    custom_idx = int(field[6:]) if is_custom else None
                    mappings.append(FieldMapping(
                        csv_column=col,
                        contact_field=field,
                        is_custom=is_custom,
                        custom_index=custom_idx
                    ))

        return mappings

    def _validate_and_show_summary(self) -> None:
        """Validate data and show summary."""
        mappings = self._get_current_mappings()
        self.csv_service.set_mappings(mappings)
        result = self.csv_service.validate()

        # Update summary
        self.summary_labels["total"].configure(text=str(result.total_rows))
        self.summary_labels["valid"].configure(
            text=str(result.valid_rows),
            bootstyle="success" if result.valid_rows > 0 else "secondary"
        )
        self.summary_labels["invalid"].configure(
            text=str(result.invalid_rows),
            bootstyle="danger" if result.invalid_rows > 0 else "secondary"
        )

        # Show issues
        self.issues_text.configure(state="normal")
        self.issues_text.delete("1.0", tk.END)

        if result.warnings:
            self.issues_text.insert(tk.END, "Warnings:\n")
            for warning in result.warnings:
                self.issues_text.insert(tk.END, f"  \u26A0 {warning}\n")
            self.issues_text.insert(tk.END, "\n")

        if result.errors:
            self.issues_text.insert(tk.END, "Errors (first 20):\n")
            for error in result.errors[:20]:
                self.issues_text.insert(tk.END, f"  Row {error['row']}: {error['error']}\n")

        if not result.warnings and not result.errors:
            self.issues_text.insert(tk.END, "\u2713 No validation issues found!")

        self.issues_text.configure(state="disabled")

    def _update_step_display(self) -> None:
        """Update UI for current step."""
        # Hide all step frames
        self.step1_frame.pack_forget()
        self.step2_frame.pack_forget()
        self.step3_frame.pack_forget()

        # Show current step
        if self.current_step == 1:
            self.step1_frame.pack(fill=BOTH, expand=True)
            self.back_btn.configure(state="disabled")
            self.next_btn.configure(text="Next \u2192")
        elif self.current_step == 2:
            self.step2_frame.pack(fill=BOTH, expand=True)
            self.back_btn.configure(state="normal")
            self.next_btn.configure(text="Next \u2192")
            self._populate_mappings()
        else:
            self.step3_frame.pack(fill=BOTH, expand=True)
            self.back_btn.configure(state="normal")
            self.next_btn.configure(text="Import")
            self._validate_and_show_summary()

        # Update step indicators
        for i, (circle, label) in enumerate(self.step_labels, 1):
            if i < self.current_step:
                circle.configure(bootstyle="success")
                label.configure(bootstyle="success")
            elif i == self.current_step:
                circle.configure(bootstyle="primary")
                label.configure(bootstyle="primary")
            else:
                circle.configure(bootstyle="secondary")
                label.configure(bootstyle="secondary")

    def _next_step(self) -> None:
        """Go to next step or import."""
        if self.current_step == 1:
            if not self.file_var.get():
                from tkinter import messagebox
                messagebox.showerror("Error", "Please select a CSV file", parent=self)
                return
            self.current_step = 2
        elif self.current_step == 2:
            # Validate mappings
            mappings = self._get_current_mappings()
            if not any(m.contact_field == "email" for m in mappings):
                from tkinter import messagebox
                messagebox.showerror("Error", "Email field mapping is required", parent=self)
                return
            self.current_step = 3
        else:
            # Do import
            self._do_import()
            return

        self._update_step_display()

    def _prev_step(self) -> None:
        """Go to previous step."""
        if self.current_step > 1:
            self.current_step -= 1
            self._update_step_display()

    def _do_import(self) -> None:
        """Perform the import."""
        try:
            # Get CSV as bytes
            csv_bytes = self.csv_service.to_csv_bytes()

            # Import via API
            result = self.api.import_contacts(self.list_id, csv_bytes, "import.csv")

            from tkinter import messagebox
            count = result.get('count', 0)
            messagebox.showinfo(
                "Import Complete",
                f"Successfully imported {count} contacts",
                parent=self
            )

            self.result = True
            self.destroy()

        except Exception as e:
            from tkinter import messagebox
            messagebox.showerror("Import Error", str(e), parent=self)
