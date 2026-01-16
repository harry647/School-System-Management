"""
Ream Management Window

Dedicated window for managing student ream entries.
"""

from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QTableWidget, QTableWidgetItem, QLineEdit, QComboBox
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont

from school_system.gui.windows.base_function_window import BaseFunctionWindow
from school_system.gui.dialogs.message_dialog import show_error_message, show_success_message
from school_system.config.logging import logger
from school_system.services.student_service import StudentService
from school_system.database.repositories.student_repo import ReamEntryRepository


class ReamManagementWindow(BaseFunctionWindow):
    """Dedicated window for managing student ream entries."""
    
    def __init__(self, parent=None, current_user: str = "", current_role: str = ""):
        """Initialize the ream management window."""
        super().__init__("Ream Management", parent, current_user, current_role)
        
        self.student_service = StudentService()
        self.ream_repo = ReamEntryRepository()
        
        # Setup content
        self.setup_content()
        
        # Load initial data
        self._refresh_ream_table()
    
    def setup_content(self):
        """Setup the main content area."""
        # Create main content layout
        main_layout = self.create_flex_layout("column", False)
        main_layout.setContentsMargins(24, 24, 24, 24)
        main_layout.set_spacing(16)
        
        # Add ream section
        add_card = self._create_add_ream_card()
        main_layout.add_widget(add_card)
        
        # Ream entries table
        table_card = self._create_ream_table_card()
        main_layout.add_widget(table_card, stretch=1)
        
        # Add to content
        self.add_layout_to_content(main_layout)
    
    def _create_add_ream_card(self) -> QWidget:
        """Create the add ream entry card."""
        theme_manager = self.get_theme_manager()
        theme = theme_manager._themes[self.get_theme()]
        
        card = QWidget()
        card.setProperty("card", "true")
        card.setStyleSheet(f"""
            QWidget[card="true"] {{
                background-color: {theme["surface"]};
                border: 1px solid {theme["border"]};
                border-radius: 12px;
                padding: 24px;
            }}
        """)
        
        layout = QVBoxLayout(card)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(16)
        
        # Title
        title_label = QLabel("Add Ream Entry")
        title_font = QFont("Segoe UI", 16, QFont.Weight.Medium)
        title_label.setFont(title_font)
        title_label.setStyleSheet(f"color: {theme["text"]};")
        layout.addWidget(title_label)
        
        # Form fields
        form_layout = QHBoxLayout()
        form_layout.setSpacing(12)
        
        # Student ID
        student_id_label = QLabel("Student ID:")
        student_id_label.setStyleSheet(f"font-weight: 500; color: {theme["text"]};")
        form_layout.addWidget(student_id_label)
        
        self.student_id_input = self.create_input("Enter student ID")
        self.student_id_input.setFixedHeight(44)
        self.student_id_input.setMinimumWidth(200)
        form_layout.addWidget(self.student_id_input)
        
        # Reams count
        reams_label = QLabel("Reams Count:")
        reams_label.setStyleSheet(f"font-weight: 500; color: {theme["text"]};")
        form_layout.addWidget(reams_label)
        
        self.reams_input = self.create_input("Enter reams count")
        self.reams_input.setFixedHeight(44)
        self.reams_input.setMinimumWidth(150)
        form_layout.addWidget(self.reams_input)
        
        form_layout.addStretch()
        
        # Add button
        add_btn = self.create_button("Add Ream Entry", "primary")
        add_btn.clicked.connect(self._on_add_ream)
        form_layout.addWidget(add_btn)
        
        layout.addLayout(form_layout)
        
        return card
    
    def _create_ream_table_card(self) -> QWidget:
        """Create the ream entries table card."""
        theme_manager = self.get_theme_manager()
        theme = theme_manager._themes[self.get_theme()]
        
        card = QWidget()
        card.setProperty("card", "true")
        card.setStyleSheet(f"""
            QWidget[card="true"] {{
                background-color: {theme["surface"]};
                border: 1px solid {theme["border"]};
                border-radius: 12px;
                padding: 24px;
            }}
        """)
        
        layout = QVBoxLayout(card)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(12)
        
        # Table title
        title_label = QLabel("Ream Entries")
        title_font = QFont("Segoe UI", 16, QFont.Weight.Medium)
        title_label.setFont(title_font)
        title_label.setStyleSheet(f"color: {theme["text"]}; margin-bottom: 8px;")
        layout.addWidget(title_label)
        
        # Ream entries table
        self.ream_table = self.create_table(0, 4)
        self.ream_table.setHorizontalHeaderLabels(["Student ID", "Student Name", "Reams Count", "Date Added"])
        self.ream_table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.ream_table.setAlternatingRowColors(True)
        layout.addWidget(self.ream_table)
        
        return card
    
    def _on_add_ream(self):
        """Handle add ream entry."""
        student_id = self.student_id_input.text().strip()
        reams_text = self.reams_input.text().strip()
        
        if not student_id or not reams_text:
            show_error_message("Validation Error", "Please fill in all fields.", self)
            return
        
        try:
            reams_count = int(reams_text)
            if reams_count <= 0:
                raise ValueError("Reams count must be positive")
            
            # Add ream entry
            self.ream_repo.add_ream_entry(student_id, reams_count)
            show_success_message("Success", f"Added {reams_count} reams for student {student_id}.", self)
            
            # Clear inputs
            self.student_id_input.clear()
            self.reams_input.clear()
            
            # Refresh table
            self._refresh_ream_table()
            
        except ValueError as e:
            show_error_message("Validation Error", f"Invalid reams count: {str(e)}", self)
        except Exception as e:
            logger.error(f"Error adding ream entry: {e}")
            show_error_message("Error", f"Failed to add ream entry: {str(e)}", self)
    
    def _refresh_ream_table(self):
        """Refresh the ream entries table."""
        try:
            entries = self.ream_repo.get_all_ream_entries()
            
            # Clear table
            self.ream_table.setRowCount(0)
            
            # Populate table
            for entry in entries:
                row = self.ream_table.rowCount()
                self.ream_table.insertRow(row)
                
                # Get student name
                try:
                    student = self.student_service.get_student_by_id(entry.student_id)
                    student_name = student.name if student else "Unknown"
                except:
                    student_name = "Unknown"
                
                self.ream_table.setItem(row, 0, QTableWidgetItem(entry.student_id))
                self.ream_table.setItem(row, 1, QTableWidgetItem(student_name))
                self.ream_table.setItem(row, 2, QTableWidgetItem(str(entry.reams_count)))
                self.ream_table.setItem(row, 3, QTableWidgetItem(str(entry.date_added)))
            
            logger.info(f"Refreshed ream table with {len(entries)} entries")
        except Exception as e:
            logger.error(f"Error refreshing ream table: {e}")
            show_error_message("Error", f"Failed to refresh ream entries: {str(e)}", self)
