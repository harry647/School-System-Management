"""
User Validation Helpers

This module provides reusable validation components for user-related operations,
ensuring consistency, data integrity, and user-friendly feedback.
"""

from PyQt6.QtWidgets import QLabel, QWidget, QHBoxLayout
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QColor
from typing import Optional, Tuple

from school_system.utils.validation_utils import ValidationUtils
from school_system.services.auth_service import AuthService


class ValidationResult:
    """Container for validation results with detailed feedback."""

    def __init__(self, is_valid: bool = True, message: str = "", field: str = ""):
        self.is_valid = is_valid
        self.message = message
        self.field = field

    @property
    def error_message(self):
        """Backward compatibility property for error_message."""
        return self.message


class UserValidator:
    """Centralized validator for user operations with real-time validation."""
    
    def __init__(self):
        self.auth_service = AuthService()
    
    def validate_username(self, username: str) -> ValidationResult:
        """Validate username format and uniqueness."""
        if not username:
            return ValidationResult(False, "Username is required", "username")
        
        # Check format
        if not ValidationUtils.validate_username(username):
            return ValidationResult(
                False, 
                "Username must be 3-20 characters and can only contain letters, numbers, and underscores",
                "username"
            )
        
        # Check uniqueness (case-insensitive)
        existing_user = self.auth_service.get_user_by_username(username)
        if existing_user:
            return ValidationResult(
                False, 
                f"Username '{username}' already exists",
                "username"
            )
        
        return ValidationResult(True, "Username is valid", "username")
    
    def validate_password(self, password: str) -> ValidationResult:
        """Validate password strength."""
        if not password:
            return ValidationResult(False, "Password is required", "password")
        
        if len(password) < 8:
            return ValidationResult(
                False,
                "Password must be at least 8 characters long",
                "password"
            )
        
        # Check for minimum complexity
        if not ValidationUtils.validate_password_strength(password):
            return ValidationResult(
                False,
                "Password must contain at least one uppercase letter, one lowercase letter, and one number",
                "password"
            )
        
        return ValidationResult(True, "Password is valid", "password")
    
    def validate_role(self, role: str) -> ValidationResult:
        """Validate user role."""
        if not role:
            return ValidationResult(False, "Role is required", "role")
        
        valid_roles = ["student", "librarian", "admin"]
        if role.lower() not in valid_roles:
            return ValidationResult(
                False,
                f"Role must be one of: {', '.join(valid_roles)}",
                "role"
            )
        
        return ValidationResult(True, "Role is valid", "role")
    
    def validate_user_exists(self, username: str) -> ValidationResult:
        """Validate that a user exists."""
        if not username:
            return ValidationResult(False, "Username is required", "username")

        existing_user = self.auth_service.get_user_by_username(username)
        if not existing_user:
            return ValidationResult(
                False,
                f"User '{username}' does not exist",
                "username"
            )

        return ValidationResult(True, "User exists", "username")

    def validate_role_update(self, username: str, new_role: str) -> ValidationResult:
        """Validate role update for an existing user."""
        # Validate that user exists
        user_result = self.validate_user_exists(username)
        if not user_result.is_valid:
            return user_result

        # Validate new role
        role_result = self.validate_role(new_role)
        if not role_result.is_valid:
            return role_result

        # Check if user is trying to change their own role (might need special permissions)
        # For now, just return success
        return ValidationResult(True, "Role update validation passed", "role_update")

    def validate_user_creation(self, username: str, password: str,
                              confirm_password: str, role: str) -> ValidationResult:
        """Validate complete user creation data."""
        # Validate username
        username_result = self.validate_username(username)
        if not username_result.is_valid:
            return username_result

        # Validate password
        password_result = self.validate_password(password)
        if not password_result.is_valid:
            return password_result

        # Validate password confirmation
        if password != confirm_password:
            return ValidationResult(
                False,
                "Passwords do not match",
                "confirm_password"
            )

        # Validate role
        role_result = self.validate_role(role)
        if not role_result.is_valid:
            return role_result

        return ValidationResult(True, "All validation passed", "user_creation")


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
