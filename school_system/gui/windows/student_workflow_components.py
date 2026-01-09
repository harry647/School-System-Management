"""
Student Workflow Components

This module provides reusable UI components for implementing the standardized
student management workflow template across all student-related operations.
"""

from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
                            QComboBox, QPushButton, QMessageBox, QDialog)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QColor
from typing import Optional, Dict, Any, Callable

from school_system.gui.base.base_window import BaseWindow
from school_system.gui.dialogs.confirm_dialog import ConfirmationDialog
from school_system.gui.base.widgets import ModernButton, ModernInput
from school_system.gui.windows.student_validation import StudentValidator, ValidationResult
from school_system.services.student_service import StudentService
from school_system.config.logging import logger


class StudentOperationPreviewDialog(QDialog):
    """Preview dialog showing summary of changes before execution."""
    
    def __init__(self, operation_type: str, student_data: dict, parent=None):
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
        
        # Add student details
        for key, value in student_data.items():
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


class StudentOperationWorkflow(QWidget):
    """
    Base class for implementing standardized student management workflows.
    
    This class implements the core STUDENT MANAGEMENT FLOW template with:
    - Trigger Action: Open operation window with pre-loaded context
    - Input Selection: Mandatory fields with dropdowns/autocomplete
    - Data Entry: Core attributes with dynamic UI hints
    - System Validation: Asynchronous checks with visual feedback
    - Confirmation: Preview modal with impact summary
    - Execution: Atomic transactions with audit logging
    - Post-Action: UI feedback with undo capability
    
    All student operations (create, update, delete) inherit from this base class
    to ensure consistency and maintainability.
    """
    
    operation_completed = pyqtSignal(bool, str)  # success, message
    
    def __init__(self, operation_type: str, parent: BaseWindow = None):
        """
        Initialize the student operation workflow.
        
        Args:
            operation_type: Type of operation (e.g., "Create Student", "Update Student")
            parent: Parent window for modal dialogs and context
        """
        super().__init__(parent)
        self.operation_type = operation_type
        self.parent_window = parent
        self.student_service = StudentService()
        self.validator = StudentValidator()
        
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
        # if hasattr(self, 'student_id_input'):
        #     results['student_id'] = self.validator.validate_student_id(self.student_id_input.text())
        
        return results
    
    def show_confirmation_dialog(self, summary_data: dict) -> bool:
        """Show confirmation dialog with operation preview."""
        preview_dialog = StudentOperationPreviewDialog(
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


class StudentCreationWorkflow(StudentOperationWorkflow):
    """Standardized workflow for student creation."""
    
    def __init__(self, parent: BaseWindow = None):
        super().__init__("Create Student", parent)
        self._setup_creation_form()
    
    def _setup_creation_form(self):
        """Setup the student creation form."""
        # Admission Number
        self.add_field("Admission Number", "text", "Enter admission number", True)
        
        # Name
        self.add_field("Name", "text", "Enter student name", True)
        
        # Stream
        self.add_field("Stream", "text", "Enter stream (e.g., Science, Arts)", True)
        
        # Action buttons
        self.add_action_button("Clear", "secondary", self._clear_form)
        self.add_action_button("Create Student", "primary", self._on_create_student)
    
    def _clear_form(self):
        """Clear the form."""
        if hasattr(self, 'admission_number_input'):
            self.admission_number_input.clear()
        if hasattr(self, 'name_input'):
            self.name_input.clear()
        if hasattr(self, 'stream_input'):
            self.stream_input.clear()
    
    def _on_create_student(self):
        """Handle student creation with full workflow."""
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
            'Admission Number': self.admission_number_input.text(),
            'Name': self.name_input.text(),
            'Stream': self.stream_input.text()
        }
        
        # Show confirmation
        if not self.show_confirmation_dialog(summary_data):
            return
        
        # Execute operation
        try:
            student_data = {
                'admission_number': self.admission_number_input.text(),
                'name': self.name_input.text(),
                'stream': self.stream_input.text()
            }
            
            student = self.student_service.create_student(student_data)
            
            # Show success
            self.show_success_feedback(
                f"Student created successfully with ID: {student.student_id}"
            )
            
            # Clear form
            self._clear_form()
            
        except Exception as e:
            self.show_error_feedback(f"Failed to create student: {str(e)}")
    
    def _validate_creation_fields(self) -> Dict[str, ValidationResult]:
        """Validate all creation fields."""
        results = {}
        
        if hasattr(self, 'admission_number_input'):
            results['admission_number'] = self.validator.validate_student_id(
                self.admission_number_input.text()
            )
        
        if hasattr(self, 'name_input'):
            results['name'] = self.validator.validate_student_name(
                self.name_input.text()
            )
        
        if hasattr(self, 'stream_input'):
            results['stream'] = self.validator.validate_stream(
                self.stream_input.text()
            )
        
        return results


class StudentUpdateWorkflow(StudentOperationWorkflow):
    """Standardized workflow for student updates."""
    
    def __init__(self, parent: BaseWindow = None):
        super().__init__("Update Student", parent)
        self._setup_update_form()
    
    def _setup_update_form(self):
        """Setup the student update form."""
        # Student ID (for lookup)
        self.add_field("Student ID", "text", "Enter student ID to update", True)
        
        # Name
        self.add_field("New Name", "text", "Enter new name (leave blank to keep current)", False)
        
        # Stream
        self.add_field("New Stream", "text", "Enter new stream (leave blank to keep current)", False)
        
        # Action buttons
        self.add_action_button("Clear", "secondary", self._clear_form)
        self.add_action_button("Update Student", "primary", self._on_update_student)
    
    def _clear_form(self):
        """Clear the form."""
        if hasattr(self, 'student_id_input'):
            self.student_id_input.clear()
        if hasattr(self, 'new_name_input'):
            self.new_name_input.clear()
        if hasattr(self, 'new_stream_input'):
            self.new_stream_input.clear()
    
    def _on_update_student(self):
        """Handle student update with full workflow."""
        # Validate student ID
        student_id = self.student_id_input.text() if hasattr(self, 'student_id_input') else ""
        
        if not student_id:
            self.show_error_feedback("Student ID is required")
            return
        
        # Check if student exists
        student = self.student_service.get_student_by_id(student_id)
        if not student:
            self.show_error_feedback("Student not found")
            return
        
        # Prepare update data
        update_data = {}
        
        if hasattr(self, 'new_name_input') and self.new_name_input.text():
            name_validation = self.validator.validate_student_name(self.new_name_input.text())
            if not name_validation.is_valid:
                self.show_error_feedback(name_validation.message)
                return
            update_data['name'] = self.new_name_input.text()
        
        if hasattr(self, 'new_stream_input') and self.new_stream_input.text():
            stream_validation = self.validator.validate_stream(self.new_stream_input.text())
            if not stream_validation.is_valid:
                self.show_error_feedback(stream_validation.message)
                return
            update_data['stream'] = self.new_stream_input.text()
        
        if not update_data:
            self.show_error_feedback("Please provide at least one field to update")
            return
        
        # Prepare summary data
        summary_data = {
            'Student ID': student_id,
            'Current Name': student.name,
            'Current Stream': student.stream or "N/A"
        }
        
        if 'name' in update_data:
            summary_data['New Name'] = update_data['name']
        if 'stream' in update_data:
            summary_data['New Stream'] = update_data['stream']
        
        # Show confirmation
        if not self.show_confirmation_dialog(summary_data):
            return
        
        # Execute operation
        try:
            updated_student = self.student_service.update_student(student_id, update_data)
            
            if updated_student:
                self.show_success_feedback("Student updated successfully")
                self._clear_form()
            else:
                self.show_error_feedback("Failed to update student")
                
        except Exception as e:
            self.show_error_feedback(f"Failed to update student: {str(e)}")


class StudentDeletionWorkflow(StudentOperationWorkflow):
    """Standardized workflow for student deletion."""
    
    def __init__(self, parent: BaseWindow = None):
        super().__init__("Delete Student", parent)
        self._setup_deletion_form()
    
    def _setup_deletion_form(self):
        """Setup the student deletion form."""
        # Student ID
        self.add_field("Student ID", "text", "Enter student ID to delete", True)
        
        # Reason for deletion
        self.add_field("Reason for Deletion", "text", "Brief reason for deletion", True)
        
        # Action button
        self.add_action_button("Delete Student", "danger", self._on_delete_student)
    
    def _on_delete_student(self):
        """Handle student deletion with full workflow."""
        # Validate student ID
        student_id = self.student_id_input.text() if hasattr(self, 'student_id_input') else ""
        
        if not student_id:
            self.show_error_feedback("Student ID is required")
            return
        
        # Check if student exists
        student = self.student_service.get_student_by_id(student_id)
        if not student:
            self.show_error_feedback("Student not found")
            return
        
        # Get reason
        reason = self.reason_for_deletion_input.text() if hasattr(self, 'reason_for_deletion_input') else ""
        
        if not reason:
            self.show_error_feedback("Reason for deletion is required")
            return
        
        # Prepare summary data
        summary_data = {
            'Student ID': student_id,
            'Student Name': student.name,
            'Stream': student.stream or "N/A",
            'Reason for Deletion': reason
        }
        
        # Show confirmation with warning
        confirm_dialog = ConfirmationDialog(
            title="Confirm Deletion",
            message=f"<b>Warning:</b> This action cannot be undone.<br><br>Are you sure you want to delete student {student_id} - {student.name}?",
            parent=self.parent_window,
            confirm_text="Delete Permanently",
            cancel_text="Cancel",
            rich_text=True
        )
        
        if confirm_dialog.exec() != QDialog.DialogCode.Accepted:
            return
        
        # Execute operation
        try:
            success = self.student_service.delete_student(student_id)
            
            if success:
                self.show_success_feedback("Student deleted successfully")
                
                # Log the deletion with reason
                logger.info(f"Student {student_id} deleted. Reason: {reason}")
                
                # Clear form
                if hasattr(self, 'student_id_input'):
                    self.student_id_input.clear()
                if hasattr(self, 'reason_for_deletion_input'):
                    self.reason_for_deletion_input.clear()
            else:
                self.show_error_feedback("Failed to delete student")
                
        except Exception as e:
            self.show_error_feedback(f"Failed to delete student: {str(e)}")


class StudentWorkflowManager:
    """Manager for coordinating between different student workflows."""
    
    def __init__(self, parent_window: BaseWindow):
        self.parent_window = parent_window
        self.current_workflow = None
        self.workflow_stack = []
    
    def start_workflow(self, workflow_type: str):
        """Start a new student workflow."""
        # Clean up previous workflow if any
        if self.current_workflow:
            self.workflow_stack.append(self.current_workflow)
            self.current_workflow.setVisible(False)
        
        # Create new workflow
        if workflow_type == "create":
            self.current_workflow = StudentCreationWorkflow(self.parent_window)
        elif workflow_type == "update":
            self.current_workflow = StudentUpdateWorkflow(self.parent_window)
        elif workflow_type == "delete":
            self.current_workflow = StudentDeletionWorkflow(self.parent_window)
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