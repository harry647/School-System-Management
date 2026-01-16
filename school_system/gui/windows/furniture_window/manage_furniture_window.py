"""
Manage Furniture Window

Dedicated window for managing furniture items.
"""

from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QTableWidget, QTableWidgetItem, QComboBox, QLineEdit
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont

from school_system.gui.windows.base_function_window import BaseFunctionWindow
from school_system.gui.dialogs.message_dialog import show_error_message, show_success_message
from school_system.config.logging import logger
from school_system.services.furniture_service import FurnitureService


class ManageFurnitureWindow(BaseFunctionWindow):
    """Dedicated window for managing furniture items."""
    
    def __init__(self, parent=None, current_user: str = "", current_role: str = ""):
        """Initialize the manage furniture window."""
        super().__init__("Manage Furniture", parent, current_user, current_role)
        
        self.furniture_service = FurnitureService()
        
        # Setup content
        self.setup_content()
        
        # Load initial data
        self._refresh_furniture_table()
    
    def setup_content(self):
        """Setup the main content area."""
        # Create main content layout
        main_layout = self.create_flex_layout("column", False)
        main_layout.set_margins(24, 24, 24, 24)
        main_layout.set_spacing(16)
        
        # Action bar
        action_bar = self._create_action_bar()
        main_layout.add_widget(action_bar)
        
        # Furniture table
        furniture_card = self._create_furniture_table()
        main_layout.add_widget(furniture_card, stretch=1)
        
        # Add to content
        self.add_layout_to_content(main_layout)
    
    def _create_action_bar(self) -> QWidget:
        """Create the action bar."""
        theme_manager = self.get_theme_manager()
        theme = theme_manager._themes[self.get_theme()]
        
        action_card = QWidget()
        action_card.setProperty("card", "true")
        action_card.setFixedHeight(80)
        action_card.setStyleSheet(f"""
            QWidget[card="true"] {{
                background-color: {theme["surface"]};
                border: 1px solid {theme["border"]};
                border-radius: 12px;
                padding: 16px;
            }}
        """)
        
        action_layout = QHBoxLayout(action_card)
        action_layout.setContentsMargins(16, 16, 16, 16)
        action_layout.setSpacing(12)
        
        # Search box
        self.search_box = self.create_search_box("Search furniture...")
        self.search_box.setMinimumWidth(300)
        self.search_box.search_text_changed.connect(self._on_search)
        action_layout.addWidget(self.search_box)
        
        # Type filter
        self.type_filter = QComboBox()
        self.type_filter.addItem("All Types")
        self.type_filter.addItems(["Chair", "Locker", "Desk", "Table"])
        self.type_filter.setMinimumWidth(150)
        self.type_filter.currentTextChanged.connect(self._on_filter_changed)
        action_layout.addWidget(self.type_filter)
        
        action_layout.addStretch()
        
        # Action buttons
        add_btn = self.create_button("➕ Add Furniture", "primary")
        add_btn.clicked.connect(self._on_add_furniture)
        action_layout.addWidget(add_btn)
        
        refresh_btn = self.create_button("🔄 Refresh", "outline")
        refresh_btn.clicked.connect(self._refresh_furniture_table)
        action_layout.addWidget(refresh_btn)
        
        return action_card
    
    def _create_furniture_table(self) -> QWidget:
        """Create the furniture table card."""
        theme_manager = self.get_theme_manager()
        theme = theme_manager._themes[self.get_theme()]
        
        table_card = QWidget()
        table_card.setProperty("card", "true")
        table_card.setStyleSheet(f"""
            QWidget[card="true"] {{
                background-color: {theme["surface"]};
                border: 1px solid {theme["border"]};
                border-radius: 12px;
                padding: 24px;
            }}
        """)
        
        table_layout = QVBoxLayout(table_card)
        table_layout.setContentsMargins(0, 0, 0, 0)
        table_layout.setSpacing(12)
        
        # Table title
        title_label = QLabel("Furniture List")
        title_font = QFont("Segoe UI", 16, QFont.Weight.Medium)
        title_label.setFont(title_font)
        title_label.setStyleSheet(f"color: {theme["text"]}; margin-bottom: 8px;")
        table_layout.addWidget(title_label)
        
        # Furniture table
        self.furniture_table = self.create_table(0, 5)
        self.furniture_table.setHorizontalHeaderLabels(["Furniture ID", "Type", "Location", "Status", "Assigned To"])
        self.furniture_table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.furniture_table.setAlternatingRowColors(True)
        table_layout.addWidget(self.furniture_table)
        
        return table_card
    
    def _refresh_furniture_table(self):
        """Refresh the furniture table."""
        try:
            # Get furniture items
            furniture_items = self.furniture_service.get_all_furniture()
            
            # Apply filter
            type_filter = self.type_filter.currentText()
            if type_filter != "All Types":
                furniture_items = [f for f in furniture_items if f.type == type_filter]
            
            # Clear table
            self.furniture_table.setRowCount(0)
            
            # Populate table
            for item in furniture_items:
                row = self.furniture_table.rowCount()
                self.furniture_table.insertRow(row)
                
                self.furniture_table.setItem(row, 0, QTableWidgetItem(item.furniture_id))
                self.furniture_table.setItem(row, 1, QTableWidgetItem(item.type))
                self.furniture_table.setItem(row, 2, QTableWidgetItem(item.location or ""))
                self.furniture_table.setItem(row, 3, QTableWidgetItem(item.status or "Available"))
                self.furniture_table.setItem(row, 4, QTableWidgetItem(item.assigned_to or ""))
            
            logger.info(f"Refreshed furniture table with {len(furniture_items)} items")
        except Exception as e:
            logger.error(f"Error refreshing furniture table: {e}")
            show_error_message("Error", f"Failed to refresh furniture: {str(e)}", self)
    
    def _on_search(self, text: str):
        """Handle search text change."""
        for row in range(self.furniture_table.rowCount()):
            match = False
            for col in range(5):
                item = self.furniture_table.item(row, col)
                if item and text.lower() in item.text().lower():
                    match = True
                    break
            self.furniture_table.setRowHidden(row, not match)
    
    def _on_filter_changed(self, text: str):
        """Handle filter change."""
        self._refresh_furniture_table()
    
    def _on_add_furniture(self):
        """Handle add furniture."""
        show_error_message("Info", "Add furniture functionality will be implemented here.", self)
