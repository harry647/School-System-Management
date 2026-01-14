"""
Add Student Window

Dedicated window for adding new students.
"""

from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QLineEdit, QComboBox, QFrame
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont

from school_system.gui.windows.base_function_window import BaseFunctionWindow
from school_system.gui.dialogs.message_dialog import show_error_message, show_success_message
from school_system.config.logging import logger
from school_system.services.student_service import StudentService
from school_system.gui.windows.student_window.student_validation import StudentValidator


class AddStudentWindow(BaseFunctionWindow):
    """Dedicated window for adding new students."""
    
    student_added = pyqtSignal()
    
    def __init__(self, parent=None, current_user: str = "", current_role: str = ""):
        """Initialize the add student window."""
        super().__init__("Add New Student", parent, current_user, current_role)
        
        self.student_service = StudentService()
        self.validator = StudentValidator()
        
        # Setup content
        self.setup_content()
    
    def setup_content(self):
        """Setup the add student form."""
        # Create main content layout
        main_layout = self.create_flex_layout("column", False)
        main_layout.setContentsMargins(24, 24, 24, 24)
        main_layout.set_spacing(24)
        
        # Form card
        form_card = self._create_form_card()
        main_layout.add_widget(form_card)
        
        # Add to content
        self.add_layout_to_content(main_layout)
    
    def _create_form_card(self) -> QWidget:
        """Create the student form card."""
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
        title_label = QLabel("Student Information")
        title_font = QFont("Segoe UI", 18, QFont.Weight.SemiBold)
        title_label.setFont(title_font)
        title_label.setStyleSheet(f"color: {theme["text"]}; margin-bottom: 8px;")
        form_layout.addWidget(title_label)
        
        # Student ID field
        id_layout = QVBoxLayout()
        id_label = QLabel("Student ID *")
        id_label.setStyleSheet(f"font-weight: 500; color: {theme["text"]}; margin-bottom: 4px;")
        id_layout.addWidget(id_label)
        
        self.student_id_input = self.create_input("Enter student ID")
        self.student_id_input.setFixedHeight(44)
        id_layout.addWidget(self.student_id_input)
        form_layout.addLayout(id_layout)
        
        # Name field
        name_layout = QVBoxLayout()
        name_label = QLabel("Full Name *")
        name_label.setStyleSheet(f"font-weight: 500; color: {theme["text"]}; margin-bottom: 4px;")
        name_layout.addWidget(name_label)
        
        self.name_input = self.create_input("Enter full name")
        self.name_input.setFixedHeight(44)
        name_layout.addWidget(self.name_input)
        form_layout.addLayout(name_layout)
        
        # Stream field
        stream_layout = QVBoxLayout()
        stream_label = QLabel("Stream *")
        stream_label.setStyleSheet(f"font-weight: 500; color: {theme["text"]}; margin-bottom: 4px;")
        stream_layout.addWidget(stream_label)
        
        self.stream_input = QComboBox()
        self.stream_input.setFixedHeight(44)
        self.stream_input.addItems(["Science", "Arts", "Commerce"])
        self.stream_input.setEditable(True)
        stream_layout.addWidget(self.stream_input)
        form_layout.addLayout(stream_layout)
        
        form_layout.addStretch()
        
        # Action buttons
        button_layout = QHBoxLayout()
        button_layout.setSpacing(12)
        
        cancel_btn = self.create_button("Cancel", "outline")
        cancel_btn.clicked.connect(self.close)
        button_layout.addWidget(cancel_btn)
        
        button_layout.addStretch()
        
        save_btn = self.create_button("Save Student", "primary")
        save_btn.clicked.connect(self._on_save_student)
        button_layout.addWidget(save_btn)
        
        form_layout.addLayout(button_layout)
        
        return form_card
    
    def _on_save_student(self):
        """Handle save student button click."""
        # Get form data
        student_id = self.student_id_input.text().strip()
        name = self.name_input.text().strip()
        stream = self.stream_input.currentText().strip()
        
        # Validate
        if not student_id or not name or not stream:
            show_error_message("Validation Error", "Please fill in all required fields.", self)
            return
        
        try:
            # Create student
            student_data = {
                "student_id": student_id,
                "name": name,
                "stream": stream
            }
            
            self.student_service.create_student(student_data)
            show_success_message("Success", f"Student {student_id} added successfully.", self)
            
            # Emit signal and close
            self.student_added.emit()
            self.close()
            
        except Exception as e:
            logger.error(f"Error adding student: {e}")
            show_error_message("Error", f"Failed to add student: {str(e)}", self)
