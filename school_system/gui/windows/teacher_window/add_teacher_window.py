"""
Add Teacher Window

Dedicated window for adding new teachers.
"""

from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QLineEdit, QComboBox
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont

from school_system.gui.windows.base_function_window import BaseFunctionWindow
from school_system.gui.dialogs.message_dialog import show_error_message, show_success_message
from school_system.config.logging import logger
from school_system.services.teacher_service import TeacherService


class AddTeacherWindow(BaseFunctionWindow):
    """Dedicated window for adding new teachers."""
    
    teacher_added = pyqtSignal()
    
    def __init__(self, parent=None, current_user: str = "", current_role: str = ""):
        """Initialize the add teacher window."""
        super().__init__("Add New Teacher", parent, current_user, current_role)
        
        self.teacher_service = TeacherService()
        
        # Setup content
        self.setup_content()
    
    def setup_content(self):
        """Setup the add teacher form."""
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
        title_label = QLabel("Teacher Information")
        title_font = QFont("Segoe UI", 18, QFont.Weight.Medium)
        title_label.setFont(title_font)
        title_label.setStyleSheet(f"color: {theme['text']}; margin-bottom: 8px;")
        form_layout.addWidget(title_label)
        
        # Teacher ID field
        id_layout = QVBoxLayout()
        id_label = QLabel("Teacher ID *")
        id_label.setStyleSheet(f"font-weight: 500; color: {theme['text']}; margin-bottom: 4px;")
        id_layout.addWidget(id_label)
        
        self.teacher_id_input = self.create_input("Enter teacher ID")
        self.teacher_id_input.setFixedHeight(44)
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
        
        # Email field
        email_layout = QVBoxLayout()
        email_label = QLabel("Email")
        email_label.setStyleSheet(f"font-weight: 500; color: {theme['text']}; margin-bottom: 4px;")
        email_layout.addWidget(email_label)
        
        self.email_input = self.create_input("Enter email address")
        self.email_input.setFixedHeight(44)
        email_layout.addWidget(self.email_input)
        form_layout.addLayout(email_layout)
        
        # Phone field
        phone_layout = QVBoxLayout()
        phone_label = QLabel("Phone")
        phone_label.setStyleSheet(f"font-weight: 500; color: {theme['text']}; margin-bottom: 4px;")
        phone_layout.addWidget(phone_label)
        
        self.phone_input = self.create_input("Enter phone number")
        self.phone_input.setFixedHeight(44)
        phone_layout.addWidget(self.phone_input)
        form_layout.addLayout(phone_layout)
        
        form_layout.addStretch()
        
        # Action buttons
        button_layout = QHBoxLayout()
        button_layout.setSpacing(12)
        
        cancel_btn = self.create_button("Cancel", "outline")
        cancel_btn.clicked.connect(self.close)
        button_layout.addWidget(cancel_btn)
        
        button_layout.addStretch()
        
        save_btn = self.create_button("Save Teacher", "primary")
        save_btn.clicked.connect(self._on_save_teacher)
        button_layout.addWidget(save_btn)
        
        form_layout.addLayout(button_layout)
        
        return form_card
    
    def _on_save_teacher(self):
        """Handle save teacher button click."""
        # Get form data
        teacher_id = self.teacher_id_input.text().strip()
        name = self.name_input.text().strip()
        department = self.department_input.text().strip()
        email = self.email_input.text().strip()
        phone = self.phone_input.text().strip()
        
        # Validate
        if not teacher_id or not name:
            show_error_message("Validation Error", "Please fill in all required fields (Teacher ID, Name).", self)
            return
        
        try:
            # Create teacher
            teacher_data = {
                "teacher_id": teacher_id,
                "name": name,
                "department": department if department else None,
                "email": email if email else None,
                "phone": phone if phone else None
            }
            
            self.teacher_service.create_teacher(teacher_data)
            show_success_message("Success", f"Teacher {teacher_id} added successfully.", self)
            
            # Emit signal and close
            self.teacher_added.emit()
            self.close()
            
        except Exception as e:
            logger.error(f"Error adding teacher: {e}")
            show_error_message("Error", f"Failed to add teacher: {str(e)}", self)
