"""Sortable data table widget for Lead Generator Standalone."""

import tkinter as tk
from tkinter import ttk
from typing import List, Dict, Any, Optional, Callable


class DataTable(ttk.Frame):
    """A sortable, searchable Treeview-based data table."""

    def __init__(
        self,
        parent,
        columns: List[Dict[str, Any]],
        on_select: Optional[Callable[[Any], None]] = None,
        on_double_click: Optional[Callable[[Any], None]] = None,
        show_search: bool = True,
        height: int = 15,
        **kwargs
    ):
        """
        Initialize DataTable.

        Args:
            parent: Parent widget
            columns: List of column definitions, each with:
                     - 'key': Column key/id
                     - 'label': Display label
                     - 'width': Optional width in pixels
                     - 'anchor': Optional text alignment (w, center, e)
            on_select: Callback when row is selected
            on_double_click: Callback when row is double-clicked
            show_search: Whether to show search box
            height: Number of rows to display
        """
        super().__init__(parent, **kwargs)

        self.columns = columns
        self.on_select = on_select
        self.on_double_click = on_double_click
        self._data: List[Dict[str, Any]] = []
        self._sort_column = None
        self._sort_reverse = False

        self._create_widgets(show_search, height)

    def _create_widgets(self, show_search: bool, height: int) -> None:
        """Create table widgets."""
        # Search frame
        if show_search:
            search_frame = ttk.Frame(self)
            search_frame.pack(fill=tk.X, pady=(0, 5))

            ttk.Label(search_frame, text="Search:").pack(side=tk.LEFT, padx=(0, 5))
            self.search_var = tk.StringVar()
            self.search_var.trace('w', self._on_search)
            search_entry = ttk.Entry(search_frame, textvariable=self.search_var, width=30)
            search_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)

            clear_btn = ttk.Button(search_frame, text="Clear", width=6,
                                   command=lambda: self.search_var.set(''))
            clear_btn.pack(side=tk.LEFT, padx=(5, 0))

        # Treeview with scrollbars
        tree_frame = ttk.Frame(self)
        tree_frame.pack(fill=tk.BOTH, expand=True)

        # Create treeview
        column_keys = [col['key'] for col in self.columns]
        self.tree = ttk.Treeview(tree_frame, columns=column_keys, show='headings', height=height)

        # Configure columns
        for col in self.columns:
            key = col['key']
            label = col.get('label', key)
            width = col.get('width', 100)
            anchor = col.get('anchor', 'w')

            self.tree.heading(key, text=label, command=lambda c=key: self._sort_by_column(c))
            self.tree.column(key, width=width, anchor=anchor)

        # Scrollbars
        vsb = ttk.Scrollbar(tree_frame, orient=tk.VERTICAL, command=self.tree.yview)
        hsb = ttk.Scrollbar(tree_frame, orient=tk.HORIZONTAL, command=self.tree.xview)
        self.tree.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)

        # Grid layout
        self.tree.grid(row=0, column=0, sticky='nsew')
        vsb.grid(row=0, column=1, sticky='ns')
        hsb.grid(row=1, column=0, sticky='ew')

        tree_frame.grid_rowconfigure(0, weight=1)
        tree_frame.grid_columnconfigure(0, weight=1)

        # Bind events
        self.tree.bind('<<TreeviewSelect>>', self._on_select)
        self.tree.bind('<Double-1>', self._on_double_click)

    def set_data(self, data: List[Dict[str, Any]]) -> None:
        """Set table data."""
        self._data = data
        self._refresh_display()

    def get_selected_item(self) -> Optional[Dict[str, Any]]:
        """Get the currently selected item."""
        selection = self.tree.selection()
        if selection:
            item_id = selection[0]
            idx = int(item_id)
            if 0 <= idx < len(self._data):
                return self._data[idx]
        return None

    def get_selected_items(self) -> List[Dict[str, Any]]:
        """Get all selected items."""
        items = []
        for item_id in self.tree.selection():
            try:
                idx = int(item_id)
                if 0 <= idx < len(self._data):
                    items.append(self._data[idx])
            except (ValueError, IndexError):
                continue
        return items

    def clear_selection(self) -> None:
        """Clear current selection."""
        self.tree.selection_remove(self.tree.selection())

    def refresh(self) -> None:
        """Refresh the table display."""
        self._refresh_display()

    def _refresh_display(self) -> None:
        """Refresh the treeview with current data."""
        # Clear existing items
        for item in self.tree.get_children():
            self.tree.delete(item)

        # Filter data if search is active
        if hasattr(self, 'search_var'):
            search_term = self.search_var.get().lower()
            if search_term:
                filtered_data = self._filter_data(search_term)
            else:
                filtered_data = self._data
        else:
            filtered_data = self._data

        # Sort if needed
        if self._sort_column:
            filtered_data = sorted(
                filtered_data,
                key=lambda x: str(x.get(self._sort_column, '')).lower(),
                reverse=self._sort_reverse
            )

        # Insert rows
        for idx, row in enumerate(filtered_data):
            values = [row.get(col['key'], '') for col in self.columns]
            self.tree.insert('', 'end', iid=str(idx), values=values)

    def _filter_data(self, search_term: str) -> List[Dict[str, Any]]:
        """Filter data based on search term."""
        filtered = []
        for row in self._data:
            for col in self.columns:
                value = str(row.get(col['key'], '')).lower()
                if search_term in value:
                    filtered.append(row)
                    break
        return filtered

    def _sort_by_column(self, column: str) -> None:
        """Sort table by column."""
        if self._sort_column == column:
            self._sort_reverse = not self._sort_reverse
        else:
            self._sort_column = column
            self._sort_reverse = False

        self._refresh_display()

    def _on_search(self, *args) -> None:
        """Handle search input."""
        self._refresh_display()

    def _on_select(self, event) -> None:
        """Handle selection event."""
        if self.on_select:
            item = self.get_selected_item()
            if item:
                self.on_select(item)

    def _on_double_click(self, event) -> None:
        """Handle double-click event."""
        if self.on_double_click:
            item = self.get_selected_item()
            if item:
                self.on_double_click(item)
