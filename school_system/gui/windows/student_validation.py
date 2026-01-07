"""
Student Validation Helpers

This module provides reusable validation components for student-related operations,
ensuring consistency, data integrity, and user-friendly feedback.
"""

from PyQt6.QtWidgets import QLabel, QWidget, QHBoxLayout
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QColor
from typing import Optional, Tuple

from school_system.utils.validation_utils import ValidationUtils
from school_system.services.student_service import StudentService


class ValidationResult:
    """Container for validation results with detailed feedback."""
    
    def __init__(self, is_valid: bool = True, message: str = "", field: str = ""):
        self.is_valid = is_valid
        self.message = message
        self.field = field


class StudentValidator:
    """Centralized validator for student operations with real-time validation."""
    
    def __init__(self):
        self.student_service = StudentService()
    
    def validate_student_id(self, student_id: str) -> ValidationResult:
        """Validate student ID format and uniqueness."""
        if not student_id:
            return ValidationResult(False, "Student ID is required", "student_id")
        
        # Check format
        if not ValidationUtils.validate_student_id(student_id):
            return ValidationResult(
                False, 
                "Student ID must be 2-4 letters followed by 4-6 digits (e.g., ST1234)",
                "student_id"
            )
        
        # Check uniqueness (case-insensitive)
        existing_student = self.student_service.get_student_by_id(student_id)
        if existing_student:
            return ValidationResult(
                False, 
                f"Student ID '{student_id}' already exists",
                "student_id"
            )
        
        return ValidationResult(True, "Student ID is valid", "student_id")
    
    def validate_student_name(self, name: str) -> ValidationResult:
        """Validate student name format."""
        if not name:
            return ValidationResult(False, "Name is required", "name")
        
        if not ValidationUtils.validate_name(name):
            return ValidationResult(
                False,
                "Name can only contain letters, spaces, hyphens, and apostrophes",
                "name"
            )
        
        return ValidationResult(True, "Name is valid", "name")
    
    def validate_stream(self, stream: str) -> ValidationResult:
        """Validate stream format."""
        if not stream:
            return ValidationResult(False, "Stream is required", "stream")
        
        # Basic validation - stream should be alphabetic with optional spaces
        if not ValidationUtils.validate_alphabetic(stream.replace(" ", "")):
            return ValidationResult(
                False,
                "Stream can only contain letters and spaces",
                "stream"
            )
        
        return ValidationResult(True, "Stream is valid", "stream")
    
    def validate_age(self, dob: str) -> ValidationResult:
        """Validate student age based on date of birth."""
        if not dob:
            return ValidationResult(False, "Date of Birth is required", "dob")
        
        if not ValidationUtils.validate_date(dob):
            return ValidationResult(
                False,
                "Date of Birth must be in YYYY-MM-DD format",
                "dob"
            )
        
        # Calculate age (basic implementation)
        # In a real system, this would use proper date calculations
        try:
            from datetime import datetime
            birth_date = datetime.strptime(dob, "%Y-%m-%d")
            today = datetime.now()
            age = today.year - birth_date.year - ((today.month, today.day) < (birth_date.month, birth_date.day))
            
            # School age range: 5-18 years
            if age < 5 or age > 18:
                return ValidationResult(
                    False,
                    f"Student must be between 5-18 years old (calculated age: {age})",
                    "dob"
                )
            
        except Exception as e:
            return ValidationResult(
                False,
                f"Invalid date format: {str(e)}",
                "dob"
            )
        
        return ValidationResult(True, "Date of Birth is valid", "dob")


class ValidationFeedbackWidget(QWidget):
    """Visual feedback widget for validation results."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.layout = QHBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.setSpacing(5)
        
        self.icon_label = QLabel(self)
        self.icon_label.setFixedSize(16, 16)
        self.message_label = QLabel(self)
        self.message_label.setStyleSheet("font-size: 12px;")
        
        self.layout.addWidget(self.icon_label)
        self.layout.addWidget(self.message_label)
        
        self.setVisible(False)
    
    def show_validation_result(self, result: ValidationResult):
        """Display validation result with appropriate visual feedback."""
        if result.is_valid:
            # Green checkmark
            self.icon_label.setStyleSheet("""
                QLabel {
                    background-color: #4CAF50;
                    border-radius: 8px;
                    color: white;
                    font-weight: bold;
                }
            """)
            self.icon_label.setText("✓")
            self.message_label.setText(result.message)
            self.message_label.setStyleSheet("color: #4CAF50;")
        else:
            # Red warning
            self.icon_label.setStyleSheet("""
                QLabel {
                    background-color: #F44336;
                    border-radius: 8px;
                    color: white;
                    font-weight: bold;
                }
            """)
            self.icon_label.setText("!")
            self.message_label.setText(result.message)
            self.message_label.setStyleSheet("color: #F44336;")
        
        self.setVisible(True)
    
    def clear(self):
        """Clear the validation feedback."""
        self.setVisible(False)


class FieldValidator(QWidget):
    """Reusable field validator with real-time validation."""
    
    validation_changed = pyqtSignal(ValidationResult)
    
    def __init__(self, field_name: str, validator_func, parent=None):
        super().__init__(parent)
        self.field_name = field_name
        self.validator_func = validator_func
        self.feedback_widget = ValidationFeedbackWidget(self)
        
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        layout.addStretch()
        layout.addWidget(self.feedback_widget)
    
    def validate(self, value: str):
        """Validate the field value and show feedback."""
        result = self.validator_func(value)
        self.feedback_widget.show_validation_result(result)
        self.validation_changed.emit(result)
        return result
    
    def clear(self):
        """Clear validation feedback."""
        self.feedback_widget.clear()
