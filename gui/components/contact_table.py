"""Contact Table Component

Sortable, filterable table widget for displaying contacts.
"""

import customtkinter as ctk
from tkinter import ttk
from typing import List, Dict, Callable, Optional, Any
from gui.components.status_badge import StatusIndicator


class ContactTable(ctk.CTkFrame):
    """Reusable table widget for displaying and managing contacts."""

    def __init__(
        self,
        master,
        columns: List[Dict[str, Any]],
        on_select: Optional[Callable] = None,
        show_checkboxes: bool = True,
        **kwargs
    ):
        """Initialize contact table.

        Args:
            master: Parent widget
            columns: List of column definitions
                     [{'id': 'name', 'text': 'Name', 'width': 150}, ...]
            on_select: Callback when row is selected (receives row data)
            show_checkboxes: Whether to show selection checkboxes
            **kwargs: Additional frame arguments
        """
        super().__init__(master, **kwargs)

        self.columns = columns
        self.on_select = on_select
        self.show_checkboxes = show_checkboxes
        self.contacts_data: List[Dict[str, Any]] = []
        self.selected_rows: set = set()

        # Configure grid
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # Create treeview with scrollbar
        self._create_treeview()

    def _create_treeview(self) -> None:
        """Create treeview widget with columns and scrollbar."""
        # Create container frame
        tree_frame = ctk.CTkFrame(self)
        tree_frame.grid(row=0, column=0, sticky="nsew", padx=5, pady=5)
        tree_frame.grid_columnconfigure(0, weight=1)
        tree_frame.grid_rowconfigure(0, weight=1)

        # Create treeview
        column_ids = [col['id'] for col in self.columns]

        # Add checkbox column if needed
        if self.show_checkboxes:
            display_columns = ['checkbox'] + column_ids
        else:
            display_columns = column_ids

        self.tree = ttk.Treeview(
            tree_frame,
            columns=display_columns,
            show='headings',
            selectmode='browse',
            height=15
        )

        # Configure checkbox column
        if self.show_checkboxes:
            self.tree.heading('checkbox', text='☐')
            self.tree.column('checkbox', width=30, minwidth=30, stretch=False)

        # Configure other columns
        for col in self.columns:
            self.tree.heading(
                col['id'],
                text=col['text'],
                command=lambda c=col['id']: self._sort_by_column(c)
            )
            self.tree.column(
                col['id'],
                width=col.get('width', 100),
                minwidth=col.get('minwidth', 50),
                stretch=col.get('stretch', True)
            )

        # Scrollbar
        scrollbar = ttk.Scrollbar(tree_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)

        # Grid layout
        self.tree.grid(row=0, column=0, sticky="nsew")
        scrollbar.grid(row=0, column=1, sticky="ns")

        # Bind selection event
        self.tree.bind('<<TreeviewSelect>>', self._on_row_select)
        self.tree.bind('<Button-1>', self._on_click)

        # Style configuration
        style = ttk.Style()
        style.theme_use('default')

        # Configure colors for dark theme
        style.configure(
            "Treeview",
            background="#2B2B2B",
            foreground="white",
            fieldbackground="#2B2B2B",
            borderwidth=0
        )
        style.configure(
            "Treeview.Heading",
            background="#1F1F1F",
            foreground="white",
            borderwidth=1
        )
        style.map('Treeview', background=[('selected', '#3B82F6')])

    def load_data(self, contacts: List[Dict[str, Any]]) -> None:
        """Load contacts into table.

        Args:
            contacts: List of contact dictionaries
        """
        self.contacts_data = contacts
        self.refresh()

    def refresh(self) -> None:
        """Refresh table display with current data."""
        # Clear existing items
        for item in self.tree.get_children():
            self.tree.delete(item)

        # Add contacts
        for contact in self.contacts_data:
            values = []

            # Checkbox column
            if self.show_checkboxes:
                email = contact.get('email', '')
                checkbox = '☑' if email in self.selected_rows else '☐'
                values.append(checkbox)

            # Data columns
            for col in self.columns:
                col_id = col['id']
                value = contact.get(col_id, '')

                # Format value based on column type
                if col.get('type') == 'status':
                    # For status, we'll show the icon
                    from gui.components.status_badge import StatusBadge
                    _, icon = StatusBadge.STATUS_COLORS.get(value, ('', '○'))
                    value = f"{icon} {value.replace('_', ' ').title()}"

                values.append(value)

            # Insert row with email as identifier
            self.tree.insert(
                '',
                'end',
                iid=contact.get('email', ''),
                values=values,
                tags=(contact.get('email', ''),)
            )

    def _sort_by_column(self, col_id: str) -> None:
        """Sort table by column.

        Args:
            col_id: Column identifier to sort by
        """
        # Get column index
        col_index = next(
            (i for i, col in enumerate(self.columns) if col['id'] == col_id),
            0
        )

        # Sort contacts data
        reverse = getattr(self, f'_sort_{col_id}_reverse', False)
        self.contacts_data.sort(
            key=lambda x: str(x.get(col_id, '')).lower(),
            reverse=reverse
        )

        # Toggle sort direction for next click
        setattr(self, f'_sort_{col_id}_reverse', not reverse)

        # Refresh display
        self.refresh()

    def _on_row_select(self, event) -> None:
        """Handle row selection.

        Args:
            event: Selection event
        """
        selected = self.tree.selection()
        if selected and self.on_select:
            email = selected[0]
            # Find contact data
            contact = next(
                (c for c in self.contacts_data if c.get('email') == email),
                None
            )
            if contact:
                self.on_select(contact)

    def _on_click(self, event) -> None:
        """Handle click events (for checkbox column).

        Args:
            event: Click event
        """
        if not self.show_checkboxes:
            return

        # Get clicked region
        region = self.tree.identify_region(event.x, event.y)
        if region != 'cell':
            return

        # Get clicked column
        column = self.tree.identify_column(event.x)
        if column != '#1':  # Not checkbox column
            return

        # Get clicked row
        row_id = self.tree.identify_row(event.y)
        if not row_id:
            return

        # Toggle selection
        if row_id in self.selected_rows:
            self.selected_rows.remove(row_id)
        else:
            self.selected_rows.add(row_id)

        # Refresh to update checkboxes
        self.refresh()

    def get_selected_rows(self) -> List[str]:
        """Get list of selected row emails.

        Returns:
            List of email addresses for selected rows
        """
        return list(self.selected_rows)

    def clear_selection(self) -> None:
        """Clear all row selections."""
        self.selected_rows.clear()
        self.refresh()

    def filter_data(self, filter_func: Callable[[Dict], bool]) -> None:
        """Filter displayed contacts.

        Args:
            filter_func: Function that returns True for contacts to show
        """
        # This would need to maintain original data and filtered view
        # For simplicity, we'll just reload
        pass

    def get_selected_contact(self) -> Optional[Dict[str, Any]]:
        """Get currently selected contact.

        Returns:
            Contact dictionary or None
        """
        selected = self.tree.selection()
        if not selected:
            return None

        email = selected[0]
        return next(
            (c for c in self.contacts_data if c.get('email') == email),
            None
        )
