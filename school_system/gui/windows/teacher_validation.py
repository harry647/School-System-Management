"""
Teacher Validation Helpers

This module provides reusable validation components for teacher-related operations,
ensuring consistency, data integrity, and user-friendly feedback.
"""

from PyQt6.QtWidgets import QLabel, QWidget, QHBoxLayout
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QColor
from typing import Optional, Tuple

from school_system.utils.validation_utils import ValidationUtils
from school_system.services.teacher_service import TeacherService


class ValidationResult:
    """Container for validation results with detailed feedback."""
    
    def __init__(self, is_valid: bool = True, message: str = "", field: str = ""):
        self.is_valid = is_valid
        self.message = message
        self.field = field


class TeacherValidator:
    """Centralized validator for teacher operations with real-time validation."""
    
    def __init__(self):
        self.teacher_service = TeacherService()
    
    def validate_teacher_id(self, teacher_id: str) -> ValidationResult:
        """Validate teacher ID format and uniqueness."""
        if not teacher_id:
            return ValidationResult(False, "Teacher ID is required", "teacher_id")
        
        # Check format
        if not ValidationUtils.validate_teacher_id(teacher_id):
            return ValidationResult(
                False, 
                "Teacher ID must be 2-4 letters followed by 4-6 digits (e.g., TC1234)",
                "teacher_id"
            )
        
        # Check uniqueness (case-insensitive)
        existing_teacher = self.teacher_service.get_teacher_by_id(teacher_id)
        if existing_teacher:
            return ValidationResult(
                False, 
                f"Teacher ID '{teacher_id}' already exists",
                "teacher_id"
            )
        
        return ValidationResult(True, "Teacher ID is valid", "teacher_id")
    
    def validate_teacher_name(self, name: str) -> ValidationResult:
        """Validate teacher name format."""
        if not name:
            return ValidationResult(False, "Name is required", "name")
        
        if not ValidationUtils.validate_name(name):
            return ValidationResult(
                False,
                "Name can only contain letters, spaces, hyphens, and apostrophes",
                "name"
            )
        
        return ValidationResult(True, "Name is valid", "name")
    
    def validate_department(self, department: str) -> ValidationResult:
        """Validate department format."""
        if not department:
            return ValidationResult(False, "Department is required", "department")
        
        # Basic validation - department should be alphabetic with optional spaces
        if not ValidationUtils.validate_alphabetic(department.replace(" ", "")):
            return ValidationResult(
                False,
                "Department can only contain letters and spaces",
                "department"
            )
        
        return ValidationResult(True, "Department is valid", "department")
    
    def validate_subject_id(self, subject_id: str) -> ValidationResult:
        """Validate subject ID format."""
        if not subject_id:
            return ValidationResult(False, "Subject ID is required", "subject_id")
        
        # Basic validation - subject ID should be alphanumeric
        if not ValidationUtils.validate_alphanumeric(subject_id):
            return ValidationResult(
                False,
                "Subject ID can only contain letters and numbers",
                "subject_id"
            )
        
        return ValidationResult(True, "Subject ID is valid", "subject_id")
    
    def validate_class_id(self, class_id: str) -> ValidationResult:
        """Validate class ID format."""
        if not class_id:
            return ValidationResult(False, "Class ID is required", "class_id")
        
        # Basic validation - class ID should be alphanumeric
        if not ValidationUtils.validate_alphanumeric(class_id):
            return ValidationResult(
                False,
                "Class ID can only contain letters and numbers",
                "class_id"
            )
        
        return ValidationResult(True, "Class ID is valid", "class_id")
    
    def validate_availability_days(self, days: str) -> ValidationResult:
        """Validate availability days format."""
        if not days:
            return ValidationResult(False, "Availability days are required", "days")
        
        # Check if days are in valid format (comma-separated weekdays)
        valid_days = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
        day_list = [d.strip() for d in days.split(",")]
        
        for day in day_list:
            if day not in valid_days:
                return ValidationResult(
                    False,
                    f"'{day}' is not a valid day. Use: {', '.join(valid_days)}",
                    "days"
                )
        
        return ValidationResult(True, "Availability days are valid", "days")
    
    def validate_availability_hours(self, hours: str) -> ValidationResult:
        """Validate availability hours format."""
        if not hours:
            return ValidationResult(False, "Availability hours are required", "hours")
        
        # Basic validation - should be in format like "8:00-16:00"
        if not ValidationUtils.validate_time_range(hours):
            return ValidationResult(
                False,
                "Hours should be in format HH:MM-HH:MM (e.g., 8:00-16:00)",
                "hours"
            )
        
        return ValidationResult(True, "Availability hours are valid", "hours")
    
    def validate_performance_score(self, score: str) -> ValidationResult:
        """Validate performance score."""
        if not score:
            return ValidationResult(False, "Performance score is required", "score")
        
        try:
            score_int = int(score)
            if score_int < 0 or score_int > 100:
                return ValidationResult(
                    False,
                    "Performance score must be between 0 and 100",
                    "score"
                )
        except ValueError:
            return ValidationResult(
                False,
                "Performance score must be a valid integer",
                "score"
            )
        
        return ValidationResult(True, "Performance score is valid", "score")


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