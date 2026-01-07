"""
Furniture Validation Helpers

This module provides reusable validation components for furniture-related operations,
ensuring consistency, data integrity, and user-friendly feedback.
"""

from PyQt6.QtWidgets import QLabel, QWidget, QHBoxLayout
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QColor
from typing import Optional, Tuple

from school_system.utils.validation_utils import ValidationUtils
from school_system.services.furniture_service import FurnitureService


class ValidationResult:
    """Container for validation results with detailed feedback."""
    
    def __init__(self, is_valid: bool = True, message: str = "", field: str = ""):
        self.is_valid = is_valid
        self.message = message
        self.field = field


class FurnitureValidator:
    """Centralized validator for furniture operations with real-time validation."""
    
    def __init__(self):
        self.furniture_service = FurnitureService()
    
    def validate_furniture_id(self, furniture_id: str, furniture_type: str) -> ValidationResult:
        """Validate furniture ID format and uniqueness."""
        if not furniture_id:
            return ValidationResult(False, f"{furniture_type.capitalize()} ID is required", f"{furniture_type}_id")
        
        # Check format
        if not ValidationUtils.validate_furniture_id(furniture_id):
            return ValidationResult(
                False, 
                f"{furniture_type.capitalize()} ID must be 2-4 letters followed by 4-6 digits (e.g., CH1234)",
                f"{furniture_type}_id"
            )
        
        # Check uniqueness (case-insensitive)
        if furniture_type.lower() == "chair":
            existing_furniture = self.furniture_service.get_chair_by_id(furniture_id)
        else:
            existing_furniture = self.furniture_service.get_locker_by_id(furniture_id)
            
        if existing_furniture:
            return ValidationResult(
                False, 
                f"{furniture_type.capitalize()} ID '{furniture_id}' already exists",
                f"{furniture_type}_id"
            )
        
        return ValidationResult(True, f"{furniture_type.capitalize()} ID is valid", f"{furniture_type}_id")
    
    def validate_location(self, location: str) -> ValidationResult:
        """Validate location format."""
        if not location:
            return ValidationResult(False, "Location is required", "location")
        
        # Basic validation - location should be alphanumeric with optional spaces and hyphens
        if not ValidationUtils.validate_location(location):
            return ValidationResult(
                False,
                "Location can only contain letters, numbers, spaces, and hyphens",
                "location"
            )
        
        return ValidationResult(True, "Location is valid", "location")
    
    def validate_form(self, form: str) -> ValidationResult:
        """Validate form format."""
        if not form:
            return ValidationResult(False, "Form is required", "form")
        
        # Basic validation - form should be alphanumeric
        if not ValidationUtils.validate_form(form):
            return ValidationResult(
                False,
                "Form can only contain letters, numbers, and spaces",
                "form"
            )
        
        return ValidationResult(True, "Form is valid", "form")
    
    def validate_color(self, color: str) -> ValidationResult:
        """Validate color format."""
        if not color:
            return ValidationResult(False, "Color is required", "color")
        
        # Basic validation - color should be alphabetic
        if not ValidationUtils.validate_color(color):
            return ValidationResult(
                False,
                "Color can only contain letters and spaces",
                "color"
            )
        
        return ValidationResult(True, "Color is valid", "color")
    
    def validate_condition(self, condition: str) -> ValidationResult:
        """Validate condition selection."""
        if not condition:
            return ValidationResult(False, "Condition is required", "condition")
        
        valid_conditions = ["Good", "Fair", "Needs Repair", "Poor"]
        if condition not in valid_conditions:
            return ValidationResult(
                False,
                f"Condition must be one of: {', '.join(valid_conditions)}",
                "condition"
            )
        
        return ValidationResult(True, "Condition is valid", "condition")


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