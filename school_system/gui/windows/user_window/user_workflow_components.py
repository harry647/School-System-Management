"""
User Workflow Components

This module provides reusable UI components for implementing the standardized
user management workflow template across all user-related operations.
"""

from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
                            QComboBox, QPushButton, QMessageBox, QDialog)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QColor
from typing import Optional, Dict, Any, Callable

from school_system.gui.base.base_window import BaseWindow
from school_system.gui.dialogs.confirm_dialog import ConfirmationDialog
from school_system.gui.base.widgets import ModernButton, ModernInput
from school_system.gui.windows.user_window.user_validation import UserValidator, ValidationResult
from school_system.services.auth_service import AuthService
from school_system.config.logging import logger


class UserOperationPreviewDialog(QDialog):
    """Preview dialog showing summary of changes before execution."""
    
    def __init__(self, operation_type: str, user_data: dict, parent=None):
        super().__init__(parent)
        self.setWindowTitle(f"Confirm {operation_type}")
        self.setMinimumSize(400, 300)
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(15, 15, 15, 15)
        layout.setSpacing(10)
        
        # Title
        title_label = QLabel(f"<h3>{operation_type} Preview</h3>")
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title_label)
        
        # Summary content
        summary_widget = QWidget()
        summary_layout = QVBoxLayout(summary_widget)
        summary_layout.setSpacing(8)
        
        # Add user details
        for key, value in user_data.items():
            if value:  # Only show non-empty fields
                field_label = QLabel(f"<b>{key.replace('_', ' ').title()}:</b> {value}")
                field_label.setWordWrap(True)
                summary_layout.addWidget(field_label)
        
        layout.addWidget(summary_widget)
        
        # Impact message
        impact_label = QLabel("<i>Please review the changes before confirming.</i>")
        impact_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        impact_label.setStyleSheet("color: #666;")
        layout.addWidget(impact_label)
        
        # Buttons
        button_layout = QHBoxLayout()
        button_layout.setSpacing(10)
        
        confirm_button = ModernButton("Confirm", self)
        confirm_button.set_custom_style("#4CAF50", "#45a049", "#3d8b40")
        confirm_button.clicked.connect(self.accept)
        
        cancel_button = ModernButton("Cancel", self)
        cancel_button.set_custom_style("#F44336", "#e53935", "#d32f2f")
        cancel_button.clicked.connect(self.reject)
        
        button_layout.addStretch()
        button_layout.addWidget(confirm_button)
        button_layout.addWidget(cancel_button)
        button_layout.addStretch()
        
        layout.addLayout(button_layout)


class UserOperationWorkflow(QWidget):
    """
    Base class for implementing standardized user management workflows.
    
    This class implements the core USER MANAGEMENT FLOW template with:
    - Trigger Action: Open operation window with pre-loaded context
    - Input Selection: Mandatory fields with dropdowns/autocomplete
    - Data Entry: Core attributes with dynamic UI hints
    - System Validation: Asynchronous checks with visual feedback
    - Confirmation: Preview modal with impact summary
    - Execution: Atomic transactions with audit logging
    - Post-Action: UI feedback with undo capability
    
    All user operations (create, update, delete) inherit from this base class
    to ensure consistency and maintainability.
    """
    
    operation_completed = pyqtSignal(bool, str)  # success, message
    
    def __init__(self, operation_type: str, parent: BaseWindow = None):
        """
        Initialize the user operation workflow.
        
        Args:
            operation_type: Type of operation (e.g., "Create User", "Update User")
            parent: Parent window for modal dialogs and context
        """
        super().__init__(parent)
        self.operation_type = operation_type
        self.parent_window = parent
        self.auth_service = AuthService()
        self.validator = UserValidator()
        
        # Setup UI
        self._setup_ui()
    
    def _setup_ui(self):
        """Setup the base workflow UI."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(10)
        
        # Operation title
        self.title_label = QLabel(f"<h2>{self.operation_type}</h2>")
        self.title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.title_label)
        
        # Form container
        self.form_container = QWidget()
        self.form_layout = QVBoxLayout(self.form_container)
        self.form_layout.setSpacing(10)
        layout.addWidget(self.form_container)
        
        # Action buttons
        self.button_container = QWidget()
        self.button_layout = QHBoxLayout(self.button_container)
        self.button_layout.setSpacing(10)
        layout.addWidget(self.button_container)
    
    def add_field(self, label_text: str, field_type: str = "text", 
                 placeholder: str = "", required: bool = True) -> QWidget:
        """Add a form field to the workflow."""
        field_widget = QWidget()
        field_layout = QVBoxLayout(field_widget)
        field_layout.setContentsMargins(0, 0, 0, 0)
        field_layout.setSpacing(5)
        
        # Label
        label = QLabel(label_text)
        if required:
            label.setText(f"{label_text} <span style='color: red;'>*</span>")
        field_layout.addWidget(label)
        
        # Input field
        if field_type == "text":
            input_field = ModernInput(placeholder, self)
        elif field_type == "dropdown":
            input_field = QComboBox(self)
            input_field.setPlaceholderText(placeholder)
        elif field_type == "password":
            input_field = ModernInput(placeholder, self)
            input_field.setEchoMode(QLineEdit.EchoMode.Password)
        else:
            input_field = ModernInput(placeholder, self)
        
        field_layout.addWidget(input_field)
        self.form_layout.addWidget(field_widget)
        
        # Store reference
        field_name = label_text.lower().replace(" ", "_")
        setattr(self, f"{field_name}_input", input_field)
        
        return field_widget
    
    def add_action_button(self, text: str, button_type: str = "primary", 
                        callback: Callable = None) -> ModernButton:
        """Add an action button to the workflow."""
        button = ModernButton(text, self)
        
        if button_type == "primary":
            button.set_custom_style("#4CAF50", "#45a049", "#3d8b40")
        elif button_type == "secondary":
            button.set_custom_style("#2196F3", "#1e88e5", "#1976d2")
        elif button_type == "danger":
            button.set_custom_style("#F44336", "#e53935", "#d32f2f")
        
        if callback:
            button.clicked.connect(callback)
        
        self.button_layout.addWidget(button)
        return button
    
    def validate_all_fields(self) -> Dict[str, ValidationResult]:
        """Validate all fields in the workflow."""
        results = {}
        
        # This should be implemented by subclasses based on their specific fields
        # Example implementation:
        # if hasattr(self, 'username_input'):
        #     results['username'] = self.validator.validate_username(self.username_input.text())
        
        return results
    
    def show_confirmation_dialog(self, summary_data: dict) -> bool:
        """Show confirmation dialog with operation preview."""
        preview_dialog = UserOperationPreviewDialog(
            self.operation_type, summary_data, self.parent_window
        )
        return preview_dialog.exec() == QDialog.DialogCode.Accepted
    
    def execute_operation(self) -> bool:
        """Execute the operation (to be implemented by subclasses)."""
        raise NotImplementedError("Subclasses must implement execute_operation")
    
    def show_success_feedback(self, message: str):
        """Show success feedback to the user."""
        if self.parent_window:
            from school_system.gui.dialogs.message_dialog import show_success_message
            show_success_message("Success", message, self.parent_window)
        
        self.operation_completed.emit(True, message)
    
    def show_error_feedback(self, message: str):
        """Show error feedback to the user."""
        if self.parent_window:
            from school_system.gui.dialogs.message_dialog import show_error_message
            show_error_message("Error", message, self.parent_window)
        
        self.operation_completed.emit(False, message)


class UserCreationWorkflow(UserOperationWorkflow):
    """Standardized workflow for user creation."""
    
    def __init__(self, parent: BaseWindow = None):
        super().__init__("Create User", parent)
        self._setup_creation_form()
    
    def _setup_creation_form(self):
        """Setup the user creation form."""
        # Username
        self.add_field("Username", "text", "Enter username", True)
        
        # Password
        self.add_field("Password", "password", "Enter password", True)
        
        # Role
        role_field = self.add_field("Role", "dropdown", "Select user role", True)
        if hasattr(self, 'role_input'):
            self.role_input.addItems(["student", "librarian", "admin"])
        
        # Action buttons
        self.add_action_button("Clear", "secondary", self._clear_form)
        self.add_action_button("Create User", "primary", self._on_create_user)
    
    def _clear_form(self):
        """Clear the form."""
        if hasattr(self, 'username_input'):
            self.username_input.clear()
        if hasattr(self, 'password_input'):
            self.password_input.clear()
        if hasattr(self, 'role_input'):
            self.role_input.setCurrentIndex(-1)
    
    def _on_create_user(self):
        """Handle user creation with full workflow."""
        # Validate all fields
        validation_results = self._validate_creation_fields()
        
        # Check if all validations passed
        all_valid = all(result.is_valid for result in validation_results.values())
        
        if not all_valid:
            # Show first error
            first_error = next(result for result in validation_results.values() if not result.is_valid)
            self.show_error_feedback(first_error.message)
            return
        
        # Prepare summary data
        summary_data = {
            'Username': self.username_input.text(),
            'Role': self.role_input.currentText()
        }
        
        # Show confirmation
        if not self.show_confirmation_dialog(summary_data):
            return
        
        # Execute operation
        try:
            user_data = {
                'username': self.username_input.text(),
                'password': self.password_input.text(),
                'role': self.role_input.currentText()
            }
            
            user = self.auth_service.create_user(
                user_data['username'], 
                user_data['password'], 
                user_data['role']
            )
            
            # Show success
            self.show_success_feedback(
                f"User created successfully: {user.username}"
            )
            
            # Track operation for undo
            if self.parent_window and hasattr(self.parent_window, '_track_operation'):
                self.parent_window._track_operation('create', {
                    'username': user.username,
                    'password': user_data['password'],
                    'role': user_data['role']
                })
            
            # Clear form
            self._clear_form()
            
        except Exception as e:
            self.show_error_feedback(f"Failed to create user: {str(e)}")
    
    def _validate_creation_fields(self) -> Dict[str, ValidationResult]:
        """Validate all creation fields."""
        results = {}
        
        if hasattr(self, 'username_input'):
            results['username'] = self.validator.validate_username(
                self.username_input.text()
            )
        
        if hasattr(self, 'password_input'):
            results['password'] = self.validator.validate_password(
                self.password_input.text()
            )
        
        if hasattr(self, 'role_input'):
            results['role'] = self.validator.validate_role(
                self.role_input.currentText()
            )
        
        return results


class UserUpdateWorkflow(UserOperationWorkflow):
    """Standardized workflow for user updates."""
    
    def __init__(self, parent: BaseWindow = None):
        super().__init__("Update User Role", parent)
        self._setup_update_form()
    
    def _setup_update_form(self):
        """Setup the user update form."""
        # Username (for lookup)
        self.add_field("Username", "text", "Enter username to update", True)
        
        # New Role
        role_field = self.add_field("New Role", "dropdown", "Select new role", True)
        if hasattr(self, 'new_role_input'):
            self.new_role_input.addItems(["student", "librarian", "admin"])
        
        # Action buttons
        self.add_action_button("Clear", "secondary", self._clear_form)
        self.add_action_button("Update Role", "primary", self._on_update_user)
    
    def _clear_form(self):
        """Clear the form."""
        if hasattr(self, 'username_input'):
            self.username_input.clear()
        if hasattr(self, 'new_role_input'):
            self.new_role_input.setCurrentIndex(-1)
    
    def _on_update_user(self):
        """Handle user update with full workflow."""
        # Validate username
        username = self.username_input.text() if hasattr(self, 'username_input') else ""
        
        if not username:
            self.show_error_feedback("Username is required")
            return
        
        # Check if user exists
        user = self.auth_service.get_user_by_username(username)
        if not user:
            self.show_error_feedback("User not found")
            return
        
        # Validate new role
        new_role = self.new_role_input.currentText() if hasattr(self, 'new_role_input') else ""
        
        if not new_role:
            self.show_error_feedback("New role is required")
            return
        
        role_validation = self.validator.validate_role(new_role)
        if not role_validation.is_valid:
            self.show_error_feedback(role_validation.message)
            return
        
        # Prepare summary data
        summary_data = {
            'Username': username,
            'Current Role': user.role,
            'New Role': new_role
        }
        
        # Show confirmation
        if not self.show_confirmation_dialog(summary_data):
            return
        
        # Execute operation
        try:
            success = self.auth_service.update_user_role(username, new_role)
            
            if success:
                self.show_success_feedback("User role updated successfully")
                
                # Track operation for undo
                if self.parent_window and hasattr(self.parent_window, '_track_operation'):
                    self.parent_window._track_operation('update', {
                        'username': username,
                        'old_role': user.role,
                        'new_role': new_role
                    })
                
                self._clear_form()
            else:
                self.show_error_feedback("Failed to update user role")
            
        except Exception as e:
            self.show_error_feedback(f"Failed to update user role: {str(e)}")


class UserDeletionWorkflow(UserOperationWorkflow):
    """Standardized workflow for user deletion."""
    
    def __init__(self, parent: BaseWindow = None):
        super().__init__("Delete User", parent)
        self._setup_deletion_form()
    
    def _setup_deletion_form(self):
        """Setup the user deletion form."""
        # Username
        self.add_field("Username", "text", "Enter username to delete", True)
        
        # Reason for deletion
        self.add_field("Reason for Deletion", "text", "Brief reason for deletion", True)
        
        # Action button
        self.add_action_button("Delete User", "danger", self._on_delete_user)
    
    def _on_delete_user(self):
        """Handle user deletion with full workflow."""
        # Validate username
        username = self.username_input.text() if hasattr(self, 'username_input') else ""
        
        if not username:
            self.show_error_feedback("Username is required")
            return
        
        # Check if user exists
        user = self.auth_service.get_user_by_username(username)
        if not user:
            self.show_error_feedback("User not found")
            return
        
        # Store user data for potential undo
        user_data = {
            'username': user.username,
            'password': 'default_password',  # We can't retrieve the actual password for security reasons
            'role': user.role
        }
        
        # Get reason
        reason = self.reason_for_deletion_input.text() if hasattr(self, 'reason_for_deletion_input') else ""
        
        if not reason:
            self.show_error_feedback("Reason for deletion is required")
            return
        
        # Prepare summary data
        summary_data = {
            'Username': username,
            'Current Role': user.role,
            'Reason for Deletion': reason
        }
        
        # Show confirmation with warning
        confirm_dialog = ConfirmationDialog(
            title="Confirm Deletion",
            message=f"<b>Warning:</b> This action cannot be undone.<br><br>Are you sure you want to delete user {username} with role {user.role}?",
            parent=self.parent_window,
            confirm_text="Delete Permanently",
            cancel_text="Cancel",
            rich_text=True
        )
        
        if confirm_dialog.exec() != QDialog.DialogCode.Accepted:
            return
        
        # Execute operation
        try:
            # Call the actual delete_user method
            success = self.auth_service.delete_user(username)
            
            if success:
                # Show success
                self.show_success_feedback("User deleted successfully")
                
                # Track operation for undo
                if self.parent_window and hasattr(self.parent_window, '_track_operation'):
                    self.parent_window._track_operation('delete', user_data)
                
                # Log the deletion with reason
                logger.info(f"User {username} deleted. Reason: {reason}")
                
                # Clear form
                if hasattr(self, 'username_input'):
                    self.username_input.clear()
                if hasattr(self, 'reason_for_deletion_input'):
                    self.reason_for_deletion_input.clear()
            else:
                self.show_error_feedback("Failed to delete user")
            
        except Exception as e:
            self.show_error_feedback(f"Failed to delete user: {str(e)}")


class UserWorkflowManager:
    """Manager for coordinating between different user workflows."""
    
    def __init__(self, parent_window: BaseWindow):
        self.parent_window = parent_window
        self.current_workflow = None
        self.workflow_stack = []
    
    def start_workflow(self, workflow_type: str):
        """Start a new user workflow."""
        # Clean up previous workflow if any
        if self.current_workflow:
            self.workflow_stack.append(self.current_workflow)
            self.current_workflow.setVisible(False)
        
        # Create new workflow
        if workflow_type == "create":
            self.current_workflow = UserCreationWorkflow(self.parent_window)
        elif workflow_type == "update":
            self.current_workflow = UserUpdateWorkflow(self.parent_window)
        elif workflow_type == "delete":
            self.current_workflow = UserDeletionWorkflow(self.parent_window)
        else:
            raise ValueError(f"Unknown workflow type: {workflow_type}")
        
        # Add to parent window
        self.parent_window.add_widget_to_content(self.current_workflow, stretch=1, name=f"{workflow_type}_workflow")
        
        return self.current_workflow
    
    def end_current_workflow(self):
        """End the current workflow and restore previous one."""
        if self.current_workflow:
            self.current_workflow.setVisible(False)
            self.current_workflow.deleteLater()
            
            if self.workflow_stack:
                self.current_workflow = self.workflow_stack.pop()
                self.current_workflow.setVisible(True)
            else:
                self.current_workflow = None
    
    def get_current_workflow(self):
        """Get the current active workflow."""
        return self.current_workflow