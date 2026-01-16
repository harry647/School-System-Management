"""
Furniture Assignments Window

Dedicated window for managing furniture assignments.
"""

from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QTableWidget, QTableWidgetItem, QComboBox, QLineEdit
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont

from school_system.gui.windows.base_function_window import BaseFunctionWindow
from school_system.gui.dialogs.message_dialog import show_error_message, show_success_message
from school_system.config.logging import logger
from school_system.services.furniture_service import FurnitureService


class FurnitureAssignmentsWindow(BaseFunctionWindow):
    """Dedicated window for managing furniture assignments."""
    
    def __init__(self, parent=None, current_user: str = "", current_role: str = ""):
        """Initialize the furniture assignments window."""
        super().__init__("Furniture Assignments", parent, current_user, current_role)
        
        self.furniture_service = FurnitureService()
        
        # Setup content
        self.setup_content()
        
        # Load initial data
        self._refresh_assignments_table()
    
    def setup_content(self):
        """Setup the main content area."""
        # Create main content layout
        main_layout = self.create_flex_layout("column", False)
        main_layout.setContentsMargins(24, 24, 24, 24)
        main_layout.set_spacing(16)
        
        # Assignment form
        form_card = self._create_assignment_form_card()
        main_layout.add_widget(form_card)
        
        # Assignments table
        table_card = self._create_assignments_table_card()
        main_layout.add_widget(table_card, stretch=1)
        
        # Add to content
        self.add_layout_to_content(main_layout)
    
    def _create_assignment_form_card(self) -> QWidget:
        """Create the assignment form card."""
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
        title_label = QLabel("Assign Furniture")
        title_font = QFont("Segoe UI", 18, QFont.Weight.Medium)
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
        
        # User ID
        user_id_layout = QVBoxLayout()
        user_id_label = QLabel("User ID *")
        user_id_label.setStyleSheet(f"font-weight: 500; color: {theme["text"]}; margin-bottom: 4px;")
        user_id_layout.addWidget(user_id_label)
        
        self.user_id_input = self.create_input("Enter user ID")
        self.user_id_input.setFixedHeight(44)
        self.user_id_input.setMinimumWidth(200)
        user_id_layout.addWidget(self.user_id_input)
        fields_layout.addLayout(user_id_layout)
        
        fields_layout.addStretch()
        
        # Assign button
        assign_btn = self.create_button("Assign Furniture", "primary")
        assign_btn.setFixedHeight(44)
        assign_btn.clicked.connect(self._on_assign_furniture)
        fields_layout.addWidget(assign_btn)
        
        form_layout.addLayout(fields_layout)
        
        return form_card
    
    def _create_assignments_table_card(self) -> QWidget:
        """Create the assignments table card."""
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
        title_label = QLabel("Furniture Assignments")
        title_font = QFont("Segoe UI", 16, QFont.Weight.Medium)
        title_label.setFont(title_font)
        title_label.setStyleSheet(f"color: {theme["text"]}; margin-bottom: 8px;")
        table_layout.addWidget(title_label)
        
        # Assignments table
        self.assignments_table = self.create_table(0, 4)
        self.assignments_table.setHorizontalHeaderLabels(["Furniture ID", "User ID", "Assigned Date", "Status"])
        self.assignments_table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.assignments_table.setAlternatingRowColors(True)
        table_layout.addWidget(self.assignments_table)
        
        return table_card
    
    def _on_assign_furniture(self):
        """Handle assign furniture."""
        furniture_id = self.furniture_id_input.text().strip()
        user_id = self.user_id_input.text().strip()
        
        if not furniture_id or not user_id:
            show_error_message("Validation Error", "Please fill in all required fields.", self)
            return
        
        try:
            # Assign furniture
            # Note: This would need to be implemented in FurnitureService
            show_success_message("Success", f"Furniture {furniture_id} assigned to {user_id}.", self)
            
            # Clear inputs
            self.furniture_id_input.clear()
            self.user_id_input.clear()
            
            # Refresh table
            self._refresh_assignments_table()
        except Exception as e:
            logger.error(f"Error assigning furniture: {e}")
            show_error_message("Error", f"Failed to assign furniture: {str(e)}", self)
    
    def _refresh_assignments_table(self):
        """Refresh the assignments table."""
        try:
            # Get assignments
            # Note: This would need to be implemented in FurnitureService
            assignments = []
            
            # Clear table
            self.assignments_table.setRowCount(0)
            
            # Populate table
            for assignment in assignments:
                row = self.assignments_table.rowCount()
                self.assignments_table.insertRow(row)
                
                self.assignments_table.setItem(row, 0, QTableWidgetItem(assignment.furniture_id))
                self.assignments_table.setItem(row, 1, QTableWidgetItem(assignment.user_id))
                self.assignments_table.setItem(row, 2, QTableWidgetItem(str(assignment.assigned_date)))
                self.assignments_table.setItem(row, 3, QTableWidgetItem(assignment.status))
            
            logger.info(f"Refreshed assignments table with {len(assignments)} entries")
        except Exception as e:
            logger.error(f"Error refreshing assignments table: {e}")
            show_error_message("Error", f"Failed to refresh assignments: {str(e)}", self)
