"""Sortable and filterable data table widget."""
import tkinter as tk
from typing import List, Dict, Any, Optional, Callable, Tuple
import ttkbootstrap as ttk
from ttkbootstrap.constants import *
from ttkbootstrap.tableview import Tableview


class DataTable(ttk.Frame):
    """A sortable, filterable data table based on Treeview."""

    def __init__(
        self,
        parent,
        columns: List[Dict[str, Any]],
        show_search: bool = True,
        show_scrollbar: bool = True,
        row_height: int = 25,
        on_select: Optional[Callable[[str], None]] = None,
        on_double_click: Optional[Callable[[str], None]] = None,
        **kwargs
    ):
        """
        Initialize DataTable.

        Args:
            parent: Parent widget
            columns: List of column definitions with keys: 'id', 'text', 'width', 'anchor'
            show_search: Whether to show search/filter box
            show_scrollbar: Whether to show scrollbars
            row_height: Height of each row
            on_select: Callback when row is selected
            on_double_click: Callback when row is double-clicked
        """
        super().__init__(parent, **kwargs)

        self.columns = columns
        self.on_select = on_select
        self.on_double_click = on_double_click
        self._data: List[Dict[str, Any]] = []
        self._filtered_data: List[Dict[str, Any]] = []
        self._sort_column: Optional[str] = None
        self._sort_reverse: bool = False

        self._create_widgets(show_search, show_scrollbar)
        self._setup_bindings()

    def _create_widgets(self, show_search: bool, show_scrollbar: bool) -> None:
        """Create table widgets."""
        # Search bar
        if show_search:
            search_frame = ttk.Frame(self)
            search_frame.pack(fill=X, pady=(0, 10))

            ttk.Label(search_frame, text="Search:").pack(side=LEFT, padx=(0, 5))

            self.search_var = tk.StringVar()
            self.search_var.trace("w", self._on_search_change)

            self.search_entry = ttk.Entry(
                search_frame,
                textvariable=self.search_var,
                width=30
            )
            self.search_entry.pack(side=LEFT, fill=X, expand=True)

            clear_btn = ttk.Button(
                search_frame,
                text="Clear",
                bootstyle="outline-secondary",
                command=self._clear_search,
                width=6
            )
            clear_btn.pack(side=LEFT, padx=(5, 0))

        # Table container
        table_frame = ttk.Frame(self)
        table_frame.pack(fill=BOTH, expand=True)

        # Create Treeview
        column_ids = [col['id'] for col in self.columns]

        self.tree = ttk.Treeview(
            table_frame,
            columns=column_ids,
            show="headings",
            bootstyle="primary"
        )

        # Configure columns
        for col in self.columns:
            self.tree.heading(
                col['id'],
                text=col['text'],
                command=lambda c=col['id']: self._on_sort(c)
            )
            self.tree.column(
                col['id'],
                width=col.get('width', 100),
                anchor=col.get('anchor', 'w'),
                minwidth=col.get('minwidth', 50)
            )

        # Scrollbars
        if show_scrollbar:
            y_scroll = ttk.Scrollbar(
                table_frame,
                orient=VERTICAL,
                command=self.tree.yview
            )
            y_scroll.pack(side=RIGHT, fill=Y)
            self.tree.configure(yscrollcommand=y_scroll.set)

            x_scroll = ttk.Scrollbar(
                table_frame,
                orient=HORIZONTAL,
                command=self.tree.xview
            )
            x_scroll.pack(side=BOTTOM, fill=X)
            self.tree.configure(xscrollcommand=x_scroll.set)

        self.tree.pack(fill=BOTH, expand=True)

        # Row count label
        self.count_label = ttk.Label(
            self,
            text="0 items",
            font=("Segoe UI", 9)
        )
        self.count_label.pack(anchor=W, pady=(5, 0))

    def _setup_bindings(self) -> None:
        """Set up event bindings."""
        self.tree.bind("<<TreeviewSelect>>", self._on_tree_select)
        self.tree.bind("<Double-1>", self._on_tree_double_click)

    def set_data(self, data: List[Dict[str, Any]]) -> None:
        """Set table data."""
        self._data = data
        self._filtered_data = data.copy()
        self._refresh_display()

    def get_data(self) -> List[Dict[str, Any]]:
        """Get current data."""
        return self._data

    def get_selected(self) -> Optional[Dict[str, Any]]:
        """Get selected row data."""
        selection = self.tree.selection()
        if not selection:
            return None

        item_id = selection[0]
        values = self.tree.item(item_id, 'values')
        if values:
            column_ids = [col['id'] for col in self.columns]
            return dict(zip(column_ids, values))
        return None

    def get_selected_id(self) -> Optional[str]:
        """Get ID of selected row (first column value)."""
        selection = self.tree.selection()
        if selection:
            values = self.tree.item(selection[0], 'values')
            if values:
                return str(values[0])
        return None

    def clear_selection(self) -> None:
        """Clear current selection."""
        self.tree.selection_remove(self.tree.selection())

    def refresh(self) -> None:
        """Refresh the display."""
        self._refresh_display()

    def _refresh_display(self) -> None:
        """Refresh table display with current filtered/sorted data."""
        # Clear existing items
        for item in self.tree.get_children():
            self.tree.delete(item)

        # Insert filtered data
        column_ids = [col['id'] for col in self.columns]
        for row in self._filtered_data:
            values = [row.get(col_id, "") for col_id in column_ids]
            self.tree.insert("", END, values=values)

        # Update count
        total = len(self._data)
        filtered = len(self._filtered_data)
        if filtered == total:
            self.count_label.configure(text=f"{total} items")
        else:
            self.count_label.configure(text=f"{filtered} of {total} items")

    def _on_search_change(self, *args) -> None:
        """Handle search text change."""
        query = self.search_var.get().lower()
        if not query:
            self._filtered_data = self._data.copy()
        else:
            self._filtered_data = [
                row for row in self._data
                if any(query in str(v).lower() for v in row.values())
            ]

        if self._sort_column:
            self._apply_sort()

        self._refresh_display()

    def _clear_search(self) -> None:
        """Clear search box."""
        self.search_var.set("")

    def _on_sort(self, column: str) -> None:
        """Handle column header click for sorting."""
        if self._sort_column == column:
            self._sort_reverse = not self._sort_reverse
        else:
            self._sort_column = column
            self._sort_reverse = False

        self._apply_sort()
        self._refresh_display()

    def _apply_sort(self) -> None:
        """Apply current sort settings."""
        if not self._sort_column:
            return

        def sort_key(row: Dict) -> Any:
            value = row.get(self._sort_column, "")
            # Try numeric sort if possible
            try:
                return float(value)
            except (ValueError, TypeError):
                return str(value).lower()

        self._filtered_data.sort(key=sort_key, reverse=self._sort_reverse)

    def _on_tree_select(self, event) -> None:
        """Handle row selection."""
        if self.on_select:
            selected_id = self.get_selected_id()
            if selected_id:
                self.on_select(selected_id)

    def _on_tree_double_click(self, event) -> None:
        """Handle row double-click."""
        if self.on_double_click:
            selected_id = self.get_selected_id()
            if selected_id:
                self.on_double_click(selected_id)

    def add_row(self, row: Dict[str, Any]) -> None:
        """Add a new row to the table."""
        self._data.append(row)
        self._filtered_data.append(row)
        self._refresh_display()

    def update_row(self, id_value: str, new_data: Dict[str, Any]) -> None:
        """Update a row by its ID (first column)."""
        id_col = self.columns[0]['id']
        for i, row in enumerate(self._data):
            if str(row.get(id_col, "")) == id_value:
                self._data[i].update(new_data)
                break
        self._on_search_change()

    def delete_row(self, id_value: str) -> None:
        """Delete a row by its ID (first column)."""
        id_col = self.columns[0]['id']
        self._data = [
            row for row in self._data
            if str(row.get(id_col, "")) != id_value
        ]
        self._on_search_change()
