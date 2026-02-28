"""
Edit Teacher Window

Dedicated window for editing existing teachers.
"""

from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QLineEdit
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont

from school_system.gui.windows.base_function_window import BaseFunctionWindow
from school_system.gui.dialogs.message_dialog import show_error_message, show_success_message
from school_system.config.logging import logger
from school_system.services.teacher_service import TeacherService


class EditTeacherWindow(BaseFunctionWindow):
    """Dedicated window for editing existing teachers."""
    
    teacher_updated = pyqtSignal()
    
    def __init__(self, teacher_id: str, parent=None, current_user: str = "", current_role: str = ""):
        """Initialize the edit teacher window."""
        super().__init__(f"Edit Teacher - {teacher_id}", parent, current_user, current_role)
        
        self.teacher_id = teacher_id
        self.teacher_service = TeacherService()
        
        # Setup content
        self.setup_content()
        
        # Load teacher data
        self._load_teacher_data()
    
    def setup_content(self):
        """Setup the edit teacher form."""
        # Create main content layout
        main_layout = self.create_flex_layout("column", False)
        main_layout.set_margins(24, 24, 24, 24)
        main_layout.set_spacing(24)
        
        # Form card
        form_card = self._create_form_card()
        main_layout.add_widget(form_card)
        
        # Add to content
        self.add_layout_to_content(main_layout)
    
    def _create_form_card(self) -> QWidget:
        """Create the teacher form card."""
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
        form_layout.setSpacing(20)
        
        # Form title
        title_label = QLabel("Edit Teacher Information")
        title_font = QFont("Segoe UI", 18, QFont.Weight.Medium)
        title_label.setFont(title_font)
        title_label.setStyleSheet(f"color: {theme['text']}; margin-bottom: 8px;")
        form_layout.addWidget(title_label)
        
        # Teacher ID field (read-only)
        id_layout = QVBoxLayout()
        id_label = QLabel("Teacher ID")
        id_label.setStyleSheet(f"font-weight: 500; color: {theme['text']}; margin-bottom: 4px;")
        id_layout.addWidget(id_label)
        
        self.teacher_id_input = self.create_input("Teacher ID")
        self.teacher_id_input.setFixedHeight(44)
        self.teacher_id_input.setReadOnly(True)
        id_layout.addWidget(self.teacher_id_input)
        form_layout.addLayout(id_layout)
        
        # Name field
        name_layout = QVBoxLayout()
        name_label = QLabel("Full Name *")
        name_label.setStyleSheet(f"font-weight: 500; color: {theme['text']}; margin-bottom: 4px;")
        name_layout.addWidget(name_label)
        
        self.name_input = self.create_input("Enter full name")
        self.name_input.setFixedHeight(44)
        name_layout.addWidget(self.name_input)
        form_layout.addLayout(name_layout)
        
        # Department field
        dept_layout = QVBoxLayout()
        dept_label = QLabel("Department")
        dept_label.setStyleSheet(f"font-weight: 500; color: {theme['text']}; margin-bottom: 4px;")
        dept_layout.addWidget(dept_label)
        
        self.department_input = self.create_input("Enter department")
        self.department_input.setFixedHeight(44)
        dept_layout.addWidget(self.department_input)
        form_layout.addLayout(dept_layout)
        
        
        form_layout.addStretch()
        
        # Action buttons
        button_layout = QHBoxLayout()
        button_layout.setSpacing(12)
        
        cancel_btn = self.create_button("Cancel", "outline")
        cancel_btn.clicked.connect(self.close)
        button_layout.addWidget(cancel_btn)
        
        button_layout.addStretch()
        
        save_btn = self.create_button("Update Teacher", "primary")
        save_btn.clicked.connect(self._on_update_teacher)
        button_layout.addWidget(save_btn)
        
        form_layout.addLayout(button_layout)
        
        return form_card
    
    def _load_teacher_data(self):
        """Load teacher data into the form."""
        try:
            teacher = self.teacher_service.get_teacher_by_id(self.teacher_id)
            if teacher:
                self.teacher_id_input.setText(teacher.teacher_id)
                self.name_input.setText(teacher.teacher_name)
                self.department_input.setText(teacher.department or "")
        except Exception as e:
            logger.error(f"Error loading teacher data: {e}")
            show_error_message("Error", f"Failed to load teacher data: {str(e)}", self)
    
    def _on_update_teacher(self):
        """Handle update teacher button click."""
        # Get form data
        name = self.name_input.text().strip()
        department = self.department_input.text().strip()
        
        # Validate
        if not name:
            show_error_message("Validation Error", "Please fill in all required fields (Name).", self)
            return
        
        try:
            # Update teacher
            teacher_data = {
                "teacher_id": self.teacher_id,
                "name": name,
                "department": department if department else None
            }
            
            self.teacher_service.update_teacher(self.teacher_id, teacher_data)
            show_success_message("Success", f"Teacher {self.teacher_id} updated successfully.", self)
            
            # Emit signal and close
            self.teacher_updated.emit()
            self.close()
            
        except Exception as e:
            logger.error(f"Error updating teacher: {e}")
            show_error_message("Error", f"Failed to update teacher: {str(e)}", self)
