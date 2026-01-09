"""
Teacher Workflow Components

This module provides reusable UI components for implementing the standardized
teacher management workflow template across all teacher-related operations.
"""

from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
                            QComboBox, QPushButton, QMessageBox, QDialog, QTextEdit)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QColor
from typing import Optional, Dict, Any, Callable

from school_system.gui.base.base_window import BaseWindow
from school_system.gui.dialogs.confirm_dialog import ConfirmationDialog
from school_system.gui.base.widgets import ModernButton, ModernInput
from school_system.gui.windows.teacher_window.teacher_validation import TeacherValidator, ValidationResult
from school_system.services.teacher_service import TeacherService
from school_system.config.logging import logger


class TeacherOperationPreviewDialog(QDialog):
    """Preview dialog showing summary of changes before execution."""
    
    def __init__(self, operation_type: str, teacher_data: dict, parent=None):
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
        
        # Add teacher details
        for key, value in teacher_data.items():
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


class TeacherOperationWorkflow(QWidget):
    """
    Base class for implementing standardized teacher management workflows.
    
    This class implements the core TEACHER MANAGEMENT FLOW template with:
    - Trigger Action: Open operation window with pre-loaded context
    - Input Selection: Mandatory fields with dropdowns/autocomplete
    - Data Entry: Core attributes with dynamic UI hints
    - System Validation: Asynchronous checks with visual feedback
    - Confirmation: Preview modal with impact summary
    - Execution: Atomic transactions with audit logging
    - Post-Action: UI feedback with undo capability
    
    All teacher operations (create, update, delete) inherit from this base class
    to ensure consistency and maintainability.
    """
    
    operation_completed = pyqtSignal(bool, str)  # success, message
    
    def __init__(self, operation_type: str, parent: BaseWindow = None):
        """
        Initialize the teacher operation workflow.
        
        Args:
            operation_type: Type of operation (e.g., "Create Teacher", "Update Teacher")
            parent: Parent window for modal dialogs and context
        """
        super().__init__(parent)
        self.operation_type = operation_type
        self.parent_window = parent
        self.teacher_service = TeacherService()
        self.validator = TeacherValidator()
        
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
        elif field_type == "textarea":
            input_field = QTextEdit(self)
            input_field.setPlaceholderText(placeholder)
            input_field.setMaximumHeight(100)
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
        # if hasattr(self, 'teacher_id_input'):
        #     results['teacher_id'] = self.validator.validate_teacher_id(self.teacher_id_input.text())
        
        return results
    
    def show_confirmation_dialog(self, summary_data: dict) -> bool:
        """Show confirmation dialog with operation preview."""
        preview_dialog = TeacherOperationPreviewDialog(
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


class TeacherCreationWorkflow(TeacherOperationWorkflow):
    """Standardized workflow for teacher creation."""
    
    def __init__(self, parent: BaseWindow = None):
        super().__init__("Create Teacher", parent)
        self._setup_creation_form()
    
    def _setup_creation_form(self):
        """Setup the teacher creation form."""
        # Teacher ID
        self.add_field("Teacher ID", "text", "Enter teacher ID (e.g., TC1234)", True)
        
        # Name
        self.add_field("Name", "text", "Enter teacher name", True)
        
        # Department
        self.add_field("Department", "text", "Enter department (e.g., Mathematics, Science)", True)
        
        # Action buttons
        self.add_action_button("Clear", "secondary", self._clear_form)
        self.add_action_button("Create Teacher", "primary", self._on_create_teacher)
    
    def _clear_form(self):
        """Clear the form."""
        if hasattr(self, 'teacher_id_input'):
            self.teacher_id_input.clear()
        if hasattr(self, 'name_input'):
            self.name_input.clear()
        if hasattr(self, 'department_input'):
            self.department_input.clear()
    
    def _on_create_teacher(self):
        """Handle teacher creation with full workflow."""
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
            'Teacher ID': self.teacher_id_input.text(),
            'Name': self.name_input.text(),
            'Department': self.department_input.text()
        }
        
        # Show confirmation
        if not self.show_confirmation_dialog(summary_data):
            return
        
        # Execute operation
        try:
            teacher_data = {
                'teacher_id': self.teacher_id_input.text(),
                'teacher_name': self.name_input.text(),
                'department': self.department_input.text()
            }
            
            teacher = self.teacher_service.create_teacher(teacher_data)
            
            # Show success
            self.show_success_feedback(
                f"Teacher created successfully with ID: {teacher.teacher_id}"
            )
            
            # Track operation for undo
            if self.parent_window and hasattr(self.parent_window, '_track_operation'):
                self.parent_window._track_operation('create', {
                    'teacher_id': teacher.teacher_id,
                    'teacher_name': teacher.teacher_name,
                    'department': teacher.department
                })
            
            # Clear form
            self._clear_form()
            
        except Exception as e:
            self.show_error_feedback(f"Failed to create teacher: {str(e)}")
    
    def _validate_creation_fields(self) -> Dict[str, ValidationResult]:
        """Validate all creation fields."""
        results = {}
        
        if hasattr(self, 'teacher_id_input'):
            results['teacher_id'] = self.validator.validate_teacher_id(
                self.teacher_id_input.text()
            )
        
        if hasattr(self, 'name_input'):
            results['name'] = self.validator.validate_teacher_name(
                self.name_input.text()
            )
        
        if hasattr(self, 'department_input'):
            results['department'] = self.validator.validate_department(
                self.department_input.text()
            )
        
        return results


class TeacherUpdateWorkflow(TeacherOperationWorkflow):
    """Standardized workflow for teacher updates."""
    
    def __init__(self, parent: BaseWindow = None):
        super().__init__("Update Teacher", parent)
        self._setup_update_form()
    
    def _setup_update_form(self):
        """Setup the teacher update form."""
        # Teacher ID (for lookup)
        self.add_field("Teacher ID", "text", "Enter teacher ID to update", True)
        
        # Name
        self.add_field("New Name", "text", "Enter new name (leave blank to keep current)", False)
        
        # Department
        self.add_field("New Department", "text", "Enter new department (leave blank to keep current)", False)
        
        # Action buttons
        self.add_action_button("Clear", "secondary", self._clear_form)
        self.add_action_button("Update Teacher", "primary", self._on_update_teacher)
    
    def _clear_form(self):
        """Clear the form."""
        if hasattr(self, 'teacher_id_input'):
            self.teacher_id_input.clear()
        if hasattr(self, 'new_name_input'):
            self.new_name_input.clear()
        if hasattr(self, 'new_department_input'):
            self.new_department_input.clear()
    
    def _on_update_teacher(self):
        """Handle teacher update with full workflow."""
        # Validate teacher ID
        teacher_id = self.teacher_id_input.text() if hasattr(self, 'teacher_id_input') else ""
        
        if not teacher_id:
            self.show_error_feedback("Teacher ID is required")
            return
        
        # Check if teacher exists
        teacher = self.teacher_service.get_teacher_by_id(teacher_id)
        if not teacher:
            self.show_error_feedback("Teacher not found")
            return
        
        # Prepare update data
        update_data = {}
        
        if hasattr(self, 'new_name_input') and self.new_name_input.text():
            name_validation = self.validator.validate_teacher_name(self.new_name_input.text())
            if not name_validation.is_valid:
                self.show_error_feedback(name_validation.message)
                return
            update_data['teacher_name'] = self.new_name_input.text()
        
        if hasattr(self, 'new_department_input') and self.new_department_input.text():
            department_validation = self.validator.validate_department(self.new_department_input.text())
            if not department_validation.is_valid:
                self.show_error_feedback(department_validation.message)
                return
            update_data['department'] = self.new_department_input.text()
        
        if not update_data:
            self.show_error_feedback("Please provide at least one field to update")
            return
        
        # Prepare summary data
        summary_data = {
            'Teacher ID': teacher_id,
            'Current Name': teacher.teacher_name,
            'Current Department': getattr(teacher, 'department', 'N/A')
        }
        
        if 'teacher_name' in update_data:
            summary_data['New Name'] = update_data['teacher_name']
        if 'department' in update_data:
            summary_data['New Department'] = update_data['department']
        
        # Show confirmation
        if not self.show_confirmation_dialog(summary_data):
            return
        
        # Execute operation
        try:
            updated_teacher = self.teacher_service.update_teacher(teacher_id, update_data)
            
            if updated_teacher:
                self.show_success_feedback("Teacher updated successfully")
                
                # Track operation for undo
                if self.parent_window and hasattr(self.parent_window, '_track_operation'):
                    self.parent_window._track_operation('update', {
                        'teacher_id': teacher_id,
                        'old_data': {
                            'teacher_name': teacher.teacher_name,
                            'department': getattr(teacher, 'department', '')
                        },
                        'new_data': update_data
                    })
                
                self._clear_form()
            else:
                self.show_error_feedback("Failed to update teacher")
            
        except Exception as e:
            self.show_error_feedback(f"Failed to update teacher: {str(e)}")


class TeacherDeletionWorkflow(TeacherOperationWorkflow):
    """Standardized workflow for teacher deletion."""
    
    def __init__(self, parent: BaseWindow = None):
        super().__init__("Delete Teacher", parent)
        self._setup_deletion_form()
    
    def _setup_deletion_form(self):
        """Setup the teacher deletion form."""
        # Teacher ID
        self.add_field("Teacher ID", "text", "Enter teacher ID to delete", True)
        
        # Reason for deletion
        self.add_field("Reason for Deletion", "text", "Brief reason for deletion", True)
        
        # Action button
        self.add_action_button("Delete Teacher", "danger", self._on_delete_teacher)
    
    def _on_delete_teacher(self):
        """Handle teacher deletion with full workflow."""
        # Validate teacher ID
        teacher_id = self.teacher_id_input.text() if hasattr(self, 'teacher_id_input') else ""
        
        if not teacher_id:
            self.show_error_feedback("Teacher ID is required")
            return
        
        # Check if teacher exists
        teacher = self.teacher_service.get_teacher_by_id(teacher_id)
        if not teacher:
            self.show_error_feedback("Teacher not found")
            return
        
        # Get reason
        reason = self.reason_for_deletion_input.text() if hasattr(self, 'reason_for_deletion_input') else ""
        
        if not reason:
            self.show_error_feedback("Reason for deletion is required")
            return
        
        # Prepare summary data
        summary_data = {
            'Teacher ID': teacher_id,
            'Teacher Name': teacher.teacher_name,
            'Department': getattr(teacher, 'department', 'N/A'),
            'Reason for Deletion': reason
        }
        
        # Show confirmation with warning
        confirm_dialog = ConfirmationDialog(
            title="Confirm Deletion",
            message=f"<b>Warning:</b> This action cannot be undone.<br><br>Are you sure you want to delete teacher {teacher_id} - {teacher.teacher_name}?",
            parent=self.parent_window,
            confirm_text="Delete Permanently",
            cancel_text="Cancel",
            rich_text=True
        )
        
        if confirm_dialog.exec() != QDialog.DialogCode.Accepted:
            return
        
        # Execute operation
        try:
            # Store teacher data for potential undo
            teacher_data = {
                'teacher_id': teacher.teacher_id,
                'teacher_name': teacher.teacher_name,
                'department': getattr(teacher, 'department', '')
            }
            
            success = self.teacher_service.delete_teacher(teacher_id)
            
            if success:
                self.show_success_feedback("Teacher deleted successfully")
                
                # Track operation for undo
                if self.parent_window and hasattr(self.parent_window, '_track_operation'):
                    self.parent_window._track_operation('delete', teacher_data)
                
                # Log the deletion with reason
                logger.info(f"Teacher {teacher_id} deleted. Reason: {reason}")
                
                # Clear form
                if hasattr(self, 'teacher_id_input'):
                    self.teacher_id_input.clear()
                if hasattr(self, 'reason_for_deletion_input'):
                    self.reason_for_deletion_input.clear()
            else:
                self.show_error_feedback("Failed to delete teacher")
            
        except Exception as e:
            self.show_error_feedback(f"Failed to delete teacher: {str(e)}")


class TeacherWorkflowManager:
    """Manager for coordinating between different teacher workflows."""
    
    def __init__(self, parent_window: BaseWindow):
        self.parent_window = parent_window
        self.current_workflow = None
        self.workflow_stack = []
    
    def start_workflow(self, workflow_type: str):
        """Start a new teacher workflow."""
        # Clean up previous workflow if any
        if self.current_workflow:
            self.workflow_stack.append(self.current_workflow)
            self.current_workflow.setVisible(False)
        
        # Create new workflow
        if workflow_type == "create":
            self.current_workflow = TeacherCreationWorkflow(self.parent_window)
        elif workflow_type == "update":
            self.current_workflow = TeacherUpdateWorkflow(self.parent_window)
        elif workflow_type == "delete":
            self.current_workflow = TeacherDeletionWorkflow(self.parent_window)
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