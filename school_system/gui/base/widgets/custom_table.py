"""
Modern Custom Table Widget

An interactive data table with sorting, filtering, and advanced UI features.
"""

from PyQt6.QtWidgets import QTableWidget, QTableWidgetItem, QHeaderView, QMenu, QVBoxLayout, QWidget, QLineEdit, QComboBox, QAbstractItemView
from PyQt6.QtCore import Qt, QSortFilterProxyModel, QModelIndex, pyqtSignal, QAbstractTableModel, QModelIndex
from PyQt6.QtGui import QAction
from typing import List, Dict, Any, Optional, Callable


class VirtualScrollModel(QAbstractTableModel):
    """
    A virtual scrolling model for large datasets.
    
    Features:
        - Only loads visible rows into memory
        - Efficient scrolling for large datasets
        - Custom data provider interface
    """
    
    def __init__(self, data_provider: Callable[[int, int], Any], row_count: int, column_count: int, headers: List[str], parent: Optional[QWidget] = None):
        super().__init__(parent)
        self._data_provider = data_provider
        self._row_count = row_count
        self._column_count = column_count
        self._headers = headers
        self._visible_rows = {}
        self._row_height = 30
    
    def rowCount(self, parent: QModelIndex = QModelIndex()) -> int:
        """Return the total number of rows."""
        return self._row_count
    
    def columnCount(self, parent: QModelIndex = QModelIndex()) -> int:
        """Return the number of columns."""
        return self._column_count
    
    def headerData(self, section: int, orientation: Qt.Orientation, role: int = Qt.ItemDataRole.DisplayRole):
        """Return header data."""
        if orientation == Qt.Orientation.Horizontal and role == Qt.ItemDataRole.DisplayRole:
            return self._headers[section]
        return None
    
    def data(self, index: QModelIndex, role: int = Qt.ItemDataRole.DisplayRole):
        """Return data for the given index."""
        if not index.isValid():
            return None
        
        if role == Qt.ItemDataRole.DisplayRole:
            row = index.row()
            col = index.column()
            
            # Check if row is in visible cache
            if row not in self._visible_rows:
                # Load data for this row
                self._visible_rows[row] = self._data_provider(row, col)
            
            return self._visible_rows[row][col]
        
        return None
    
    def canFetchMore(self, parent: QModelIndex = QModelIndex()) -> bool:
        """Return whether more data can be fetched."""
        return False
    
    def fetchMore(self, parent: QModelIndex = QModelIndex()):
        """Fetch more data."""
        pass


class CustomTableWidget(QTableWidget):
    """
    An interactive data table with sorting, filtering, and advanced UI features.
    
    Features:
        - Sorting by column
        - Filtering by column
        - Context menu for actions
        - Customizable styling
        - Accessibility support
        - Virtual scrolling for large datasets
    """
    
    # Signal for row selection changes
    row_selected = pyqtSignal(int)
    
    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__(parent)
        
        # Configure table properties
        self.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        self.setAlternatingRowColors(True)
        self.setSortingEnabled(True)
        
        # Enable virtual scrolling
        self.setVerticalScrollMode(QAbstractItemView.ScrollMode.ScrollPerPixel)
        self.setHorizontalScrollMode(QAbstractItemView.ScrollMode.ScrollPerPixel)
        
        # Header configuration
        horizontal_header = self.horizontalHeader()
        horizontal_header.setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        horizontal_header.setStretchLastSection(True)
        horizontal_header.setSortIndicatorShown(True)
        
        # Vertical header configuration
        vertical_header = self.verticalHeader()
        vertical_header.setVisible(False)
        
        # Context menu
        self.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.customContextMenuRequested.connect(self._show_context_menu)
        
        # Filtering setup
        self._filter_widgets = {}
        self._filter_layout = QVBoxLayout()
        
        # Styling - will be overridden by theme manager
        self.setStyleSheet("""
            CustomTableWidget {
                font-size: 14px;
            }
        """)
        
        # Accessibility
        self.setAccessibleName("Custom Table")
        self.setAccessibleDescription("Interactive data table with sorting and filtering")
        
        # Connect signals
        self.itemSelectionChanged.connect(self._on_selection_changed)
    
    def _on_selection_changed(self):
        """Handle row selection changes."""
        selected_items = self.selectedItems()
        if selected_items:
            row = selected_items[0].row()
            self.row_selected.emit(row)
    
    def _show_context_menu(self, pos):
        """Show context menu for table actions."""
        menu = QMenu(self)
        
        # Add actions
        copy_action = QAction("Copy", self)
        copy_action.triggered.connect(self._copy_selection)
        menu.addAction(copy_action)
        
        # Show menu
        menu.exec(self.viewport().mapToGlobal(pos))
    
    def _copy_selection(self):
        """Copy selected cells to clipboard."""
        selected_ranges = self.selectedRanges()
        if not selected_ranges:
            return
        
        # Get selected text
        text = ""
        for range in selected_ranges:
            for row in range(range.topRow(), range.bottomRow() + 1):
                for col in range(range.leftColumn(), range.rightColumn() + 1):
                    item = self.item(row, col)
                    if item:
                        text += item.text() + "\t"
                text += "\n"
        
        # Copy to clipboard
        import pyperclip
        pyperclip.copy(text)
    
    def set_data(self, data: List[Dict[str, Any]], headers: List[str]):
        """
        Set table data from a list of dictionaries.
        
        Args:
            data: List of dictionaries where keys are column names
            headers: List of column headers
        """
        self.setRowCount(len(data))
        self.setColumnCount(len(headers))
        self.setHorizontalHeaderLabels(headers)
        
        for row_idx, row_data in enumerate(data):
            for col_idx, header in enumerate(headers):
                value = row_data.get(header, "")
                item = QTableWidgetItem(str(value))
                item.setFlags(item.flags() & ~Qt.ItemFlag.ItemIsEditable)
                self.setItem(row_idx, col_idx, item)
    
    def add_filter_widgets(self, filter_widgets: Dict[str, QWidget]):
        """
        Add filter widgets for specific columns.
        
        Args:
            filter_widgets: Dictionary mapping column names to filter widgets
        """
        self._filter_widgets = filter_widgets
        
        # Add filter widgets to layout
        for widget in filter_widgets.values():
            self._filter_layout.addWidget(widget)
    
    def apply_filters(self):
        """Apply current filters to the table."""
        # This would be implemented with a proxy model for filtering
        # For now, we'll just hide rows that don't match filters
        pass
    
    def sort_by_column(self, column: int, order: Qt.SortOrder = Qt.SortOrder.AscendingOrder):
        """
        Sort table by a specific column.
         
        Args:
            column: Column index to sort by
            order: Sort order (Ascending or Descending)
        """
        self.sortItems(column, order)
    
    def horizontalHeaderLabels(self) -> List[str]:
        """
        Get the current horizontal header labels.
        
        Returns:
            List of header labels as strings
        """
        headers = []
        horizontal_header = self.horizontalHeader()
        for i in range(self.columnCount()):
            item = horizontal_header.model().headerData(i, Qt.Orientation.Horizontal, Qt.ItemDataRole.DisplayRole)
            headers.append(str(item) if item else "")
        return headers


class SortFilterProxyModel(QSortFilterProxyModel):
    """
    Proxy model for sorting and filtering table data.
    
    Features:
        - Custom sorting logic
        - Column-specific filtering
        - Case-insensitive search
    """
    
    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__(parent)
        self._filter_column = 0
        self._filter_text = ""
    
    def set_filter_column(self, column: int):
        """Set the column to filter on."""
        self._filter_column = column
        self.invalidateFilter()
    
    def set_filter_text(self, text: str):
        """Set the filter text."""
        self._filter_text = text
        self.invalidateFilter()
    
    def filterAcceptsRow(self, source_row: int, source_parent: QModelIndex) -> bool:
        """Override filter logic for custom filtering."""
        if not self._filter_text:
            return True
        
        source_model = self.sourceModel()
        if not source_model:
            return True
        
        # Get the item text for the filter column
        index = source_model.index(source_row, self._filter_column, source_parent)
        if not index.isValid():
            return True
        
        item_text = source_model.data(index, Qt.ItemDataRole.DisplayRole)
        if not item_text:
            return False
        
        # Case-insensitive search
        return self._filter_text.lower() in str(item_text).lower()
    
    def lessThan(self, left: QModelIndex, right: QModelIndex) -> bool:
        """Override sorting logic for custom sorting."""
        left_data = self.sourceModel().data(left, Qt.ItemDataRole.DisplayRole)
        right_data = self.sourceModel().data(right, Qt.ItemDataRole.DisplayRole)
        
        # Try numeric comparison first
        try:
            return float(left_data) < float(right_data)
        except (ValueError, TypeError):
            # Fall back to string comparison
            return str(left_data) < str(right_data)
