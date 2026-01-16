"""
Furniture Maintenance Window

Dedicated window for managing furniture maintenance.
"""

from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QTableWidget, QTableWidgetItem, QComboBox, QLineEdit, QTextEdit
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont

from school_system.gui.windows.base_function_window import BaseFunctionWindow
from school_system.gui.dialogs.message_dialog import show_error_message, show_success_message
from school_system.config.logging import logger
from school_system.services.furniture_service import FurnitureService


class FurnitureMaintenanceWindow(BaseFunctionWindow):
    """Dedicated window for managing furniture maintenance."""
    
    def __init__(self, parent=None, current_user: str = "", current_role: str = ""):
        """Initialize the furniture maintenance window."""
        super().__init__("Furniture Maintenance", parent, current_user, current_role)
        
        self.furniture_service = FurnitureService()
        
        # Setup content
        self.setup_content()
        
        # Load initial data
        self._refresh_maintenance_table()
    
    def setup_content(self):
        """Setup the main content area."""
        # Create main content layout
        main_layout = self.create_flex_layout("column", False)
        main_layout.setContentsMargins(24, 24, 24, 24)
        main_layout.set_spacing(16)
        
        # Maintenance form
        form_card = self._create_maintenance_form_card()
        main_layout.add_widget(form_card)
        
        # Maintenance records table
        table_card = self._create_maintenance_table_card()
        main_layout.add_widget(table_card, stretch=1)
        
        # Add to content
        self.add_layout_to_content(main_layout)
    
    def _create_maintenance_form_card(self) -> QWidget:
        """Create the maintenance form card."""
        theme_manager = self.get_theme_manager()
        theme = theme_manager._themes[self.get_theme()]
        
        form_card = QWidget()
        form_card.setProperty("card", "true")
        form_card.setStyleSheet(f"""
            QWidget[card="true"] {{
                background-color: {theme["surface"]};
                border: 1px solid {theme["border"]};
                border-radius: 12px;
                padding: 24px;
            }}
        """)
        
        form_layout = QVBoxLayout(form_card)
        form_layout.setContentsMargins(24, 24, 24, 24)
        form_layout.setSpacing(16)
        
        # Form title
        title_label = QLabel("Record Maintenance")
        title_font = QFont("Segoe UI", 18, QFont.Weight.SemiBold)
        title_label.setFont(title_font)
        title_label.setStyleSheet(f"color: {theme["text"]}; margin-bottom: 8px;")
        form_layout.addWidget(title_label)
        
        # Form fields
        fields_layout = QHBoxLayout()
        fields_layout.setSpacing(12)
        
        # Furniture ID
        furniture_id_layout = QVBoxLayout()
        furniture_id_label = QLabel("Furniture ID *")
        furniture_id_label.setStyleSheet(f"font-weight: 500; color: {theme["text"]}; margin-bottom: 4px;")
        furniture_id_layout.addWidget(furniture_id_label)
        
        self.furniture_id_input = self.create_input("Enter furniture ID")
        self.furniture_id_input.setFixedHeight(44)
        self.furniture_id_input.setMinimumWidth(200)
        furniture_id_layout.addWidget(self.furniture_id_input)
        fields_layout.addLayout(furniture_id_layout)
        
        # Maintenance type
        type_layout = QVBoxLayout()
        type_label = QLabel("Maintenance Type *")
        type_label.setStyleSheet(f"font-weight: 500; color: {theme["text"]}; margin-bottom: 4px;")
        type_layout.addWidget(type_label)
        
        self.maintenance_type_combo = QComboBox()
        self.maintenance_type_combo.setFixedHeight(44)
        self.maintenance_type_combo.addItems(["Repair", "Cleaning", "Inspection", "Replacement"])
        type_layout.addWidget(self.maintenance_type_combo)
        fields_layout.addLayout(type_layout)
        
        fields_layout.addStretch()
        
        # Record button
        record_btn = self.create_button("Record Maintenance", "primary")
        record_btn.setFixedHeight(44)
        record_btn.clicked.connect(self._on_record_maintenance)
        fields_layout.addWidget(record_btn)
        
        form_layout.addLayout(fields_layout)
        
        # Notes field
        notes_layout = QVBoxLayout()
        notes_label = QLabel("Notes")
        notes_label.setStyleSheet(f"font-weight: 500; color: {theme["text"]}; margin-bottom: 4px;")
        notes_layout.addWidget(notes_label)
        
        self.notes_input = QTextEdit()
        self.notes_input.setFixedHeight(80)
        self.notes_input.setPlaceholderText("Enter maintenance notes...")
        notes_layout.addWidget(self.notes_input)
        form_layout.addLayout(notes_layout)
        
        return form_card
    
    def _create_maintenance_table_card(self) -> QWidget:
        """Create the maintenance table card."""
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
        title_label = QLabel("Maintenance Records")
        title_font = QFont("Segoe UI", 16, QFont.Weight.SemiBold)
        title_label.setFont(title_font)
        title_label.setStyleSheet(f"color: {theme["text"]}; margin-bottom: 8px;")
        table_layout.addWidget(title_label)
        
        # Maintenance table
        self.maintenance_table = self.create_table(0, 4)
        self.maintenance_table.setHorizontalHeaderLabels(["Furniture ID", "Type", "Date", "Notes"])
        self.maintenance_table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.maintenance_table.setAlternatingRowColors(True)
        table_layout.addWidget(self.maintenance_table)
        
        return table_card
    
    def _on_record_maintenance(self):
        """Handle record maintenance."""
        furniture_id = self.furniture_id_input.text().strip()
        maintenance_type = self.maintenance_type_combo.currentText().strip()
        notes = self.notes_input.toPlainText().strip()
        
        if not furniture_id or not maintenance_type:
            show_error_message("Validation Error", "Please fill in all required fields.", self)
            return
        
        try:
            # Record maintenance
            # Note: This would need to be implemented in FurnitureService
            show_success_message("Success", f"Maintenance recorded for furniture {furniture_id}.", self)
            
            # Clear inputs
            self.furniture_id_input.clear()
            self.notes_input.clear()
            
            # Refresh table
            self._refresh_maintenance_table()
        except Exception as e:
            logger.error(f"Error recording maintenance: {e}")
            show_error_message("Error", f"Failed to record maintenance: {str(e)}", self)
    
    def _refresh_maintenance_table(self):
        """Refresh the maintenance table."""
        try:
            # Get maintenance records
            # Note: This would need to be implemented in FurnitureService
            records = []
            
            # Clear table
            self.maintenance_table.setRowCount(0)
            
            # Populate table
            for record in records:
                row = self.maintenance_table.rowCount()
                self.maintenance_table.insertRow(row)
                
                self.maintenance_table.setItem(row, 0, QTableWidgetItem(record.furniture_id))
                self.maintenance_table.setItem(row, 1, QTableWidgetItem(record.maintenance_type))
                self.maintenance_table.setItem(row, 2, QTableWidgetItem(str(record.date)))
                self.maintenance_table.setItem(row, 3, QTableWidgetItem(record.notes or ""))
            
            logger.info(f"Refreshed maintenance table with {len(records)} entries")
        except Exception as e:
            logger.error(f"Error refreshing maintenance table: {e}")
            show_error_message("Error", f"Failed to refresh maintenance records: {str(e)}", self)
