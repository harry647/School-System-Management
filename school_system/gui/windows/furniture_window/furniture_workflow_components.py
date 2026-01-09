"""
Furniture Workflow Components

This module provides reusable UI components for implementing the standardized
furniture management workflow template across all furniture-related operations.
"""

from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
                            QComboBox, QPushButton, QMessageBox, QDialog)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QColor
from typing import Optional, Dict, Any, Callable

from school_system.gui.base.base_window import BaseWindow
from school_system.gui.dialogs.confirm_dialog import ConfirmationDialog
from school_system.gui.base.widgets import ModernButton, ModernInput
from school_system.gui.windows.furniture_window.furniture_validation import FurnitureValidator, ValidationResult
from school_system.services.furniture_service import FurnitureService
from school_system.config.logging import logger


class FurnitureOperationPreviewDialog(QDialog):
    """Preview dialog showing summary of changes before execution."""
    
    def __init__(self, operation_type: str, furniture_data: dict, parent=None):
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
        
        # Add furniture details
        for key, value in furniture_data.items():
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


class FurnitureOperationWorkflow(QWidget):
    """
    Base class for implementing standardized furniture management workflows.
    
    This class implements the core FURNITURE MANAGEMENT FLOW template with:
    - Trigger Action: Open operation window with pre-loaded context
    - Input Selection: Mandatory fields with dropdowns/autocomplete
    - Data Entry: Core attributes with dynamic UI hints
    - System Validation: Asynchronous checks with visual feedback
    - Confirmation: Preview modal with impact summary
    - Execution: Atomic transactions with audit logging
    - Post-Action: UI feedback with undo capability
    
    All furniture operations (create, update, delete) inherit from this base class
    to ensure consistency and maintainability.
    """
    
    operation_completed = pyqtSignal(bool, str)  # success, message
    
    def __init__(self, operation_type: str, parent: BaseWindow = None):
        """
        Initialize the furniture operation workflow.
        
        Args:
            operation_type: Type of operation (e.g., "Create Chair", "Update Locker")
            parent: Parent window for modal dialogs and context
        """
        super().__init__(parent)
        self.operation_type = operation_type
        self.parent_window = parent
        self.furniture_service = FurnitureService()
        self.validator = FurnitureValidator()
        
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
        # if hasattr(self, 'chair_id_input'):
        #     results['chair_id'] = self.validator.validate_furniture_id(self.chair_id_input.text(), "chair")
        
        return results
    
    def show_confirmation_dialog(self, summary_data: dict) -> bool:
        """Show confirmation dialog with operation preview."""
        preview_dialog = FurnitureOperationPreviewDialog(
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


class ChairCreationWorkflow(FurnitureOperationWorkflow):
    """Standardized workflow for chair creation."""
    
    def __init__(self, parent: BaseWindow = None):
        super().__init__("Create Chair", parent)
        self._setup_creation_form()
    
    def _setup_creation_form(self):
        """Setup the chair creation form."""
        # Chair ID
        self.add_field("Chair ID", "text", "Enter chair ID (e.g., CH1234)", True)
        
        # Location
        self.add_field("Location", "text", "Enter location (e.g., Classroom A)", True)
        
        # Form
        self.add_field("Form", "text", "Enter form (e.g., Form 1)", True)
        
        # Color
        self.add_field("Color", "text", "Enter color", True)
        self.color_input.setText("Black")
        
        # Condition
        self.add_field("Condition", "dropdown", "Select condition", True)
        self.condition_input.addItems(["Good", "Fair", "Needs Repair", "Poor"])
        
        # Action buttons
        self.add_action_button("Clear", "secondary", self._clear_form)
        self.add_action_button("Create Chair", "primary", self._on_create_chair)
    
    def _clear_form(self):
        """Clear the form."""
        if hasattr(self, 'chair_id_input'):
            self.chair_id_input.clear()
        if hasattr(self, 'location_input'):
            self.location_input.clear()
        if hasattr(self, 'form_input'):
            self.form_input.clear()
        if hasattr(self, 'color_input'):
            self.color_input.setText("Black")
        if hasattr(self, 'condition_input'):
            self.condition_input.setCurrentIndex(0)
    
    def _on_create_chair(self):
        """Handle chair creation with full workflow."""
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
            'Chair ID': self.chair_id_input.text(),
            'Location': self.location_input.text(),
            'Form': self.form_input.text(),
            'Color': self.color_input.text(),
            'Condition': self.condition_input.currentText()
        }
        
        # Show confirmation
        if not self.show_confirmation_dialog(summary_data):
            return
        
        # Execute operation
        try:
            chair_data = {
                'chair_id': self.chair_id_input.text(),
                'location': self.location_input.text(),
                'form': self.form_input.text(),
                'color': self.color_input.text(),
                'cond': self.condition_input.currentText(),
                'assigned': 0
            }
            
            chair = self.furniture_service.create_chair(chair_data)
            
            # Show success
            self.show_success_feedback(
                f"Chair created successfully with ID: {chair.chair_id}"
            )
            
            # Clear form
            self._clear_form()
            
        except Exception as e:
            self.show_error_feedback(f"Failed to create chair: {str(e)}")
    
    def _validate_creation_fields(self) -> Dict[str, ValidationResult]:
        """Validate all creation fields."""
        results = {}
        
        if hasattr(self, 'chair_id_input'):
            results['chair_id'] = self.validator.validate_furniture_id(
                self.chair_id_input.text(), "chair"
            )
        
        if hasattr(self, 'location_input'):
            results['location'] = self.validator.validate_location(
                self.location_input.text()
            )
        
        if hasattr(self, 'form_input'):
            results['form'] = self.validator.validate_form(
                self.form_input.text()
            )
        
        if hasattr(self, 'color_input'):
            results['color'] = self.validator.validate_color(
                self.color_input.text()
            )
        
        if hasattr(self, 'condition_input'):
            results['condition'] = self.validator.validate_condition(
                self.condition_input.currentText()
            )
        
        return results


class LockerCreationWorkflow(FurnitureOperationWorkflow):
    """Standardized workflow for locker creation."""
    
    def __init__(self, parent: BaseWindow = None):
        super().__init__("Create Locker", parent)
        self._setup_creation_form()
    
    def _setup_creation_form(self):
        """Setup the locker creation form."""
        # Locker ID
        self.add_field("Locker ID", "text", "Enter locker ID (e.g., LK1234)", True)
        
        # Location
        self.add_field("Location", "text", "Enter location (e.g., Hallway B)", True)
        
        # Form
        self.add_field("Form", "text", "Enter form (e.g., Form 2)", True)
        
        # Color
        self.add_field("Color", "text", "Enter color", True)
        self.color_input.setText("Black")
        
        # Condition
        self.add_field("Condition", "dropdown", "Select condition", True)
        self.condition_input.addItems(["Good", "Fair", "Needs Repair", "Poor"])
        
        # Action buttons
        self.add_action_button("Clear", "secondary", self._clear_form)
        self.add_action_button("Create Locker", "primary", self._on_create_locker)
    
    def _clear_form(self):
        """Clear the form."""
        if hasattr(self, 'locker_id_input'):
            self.locker_id_input.clear()
        if hasattr(self, 'location_input'):
            self.location_input.clear()
        if hasattr(self, 'form_input'):
            self.form_input.clear()
        if hasattr(self, 'color_input'):
            self.color_input.setText("Black")
        if hasattr(self, 'condition_input'):
            self.condition_input.setCurrentIndex(0)
    
    def _on_create_locker(self):
        """Handle locker creation with full workflow."""
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
            'Locker ID': self.locker_id_input.text(),
            'Location': self.location_input.text(),
            'Form': self.form_input.text(),
            'Color': self.color_input.text(),
            'Condition': self.condition_input.currentText()
        }
        
        # Show confirmation
        if not self.show_confirmation_dialog(summary_data):
            return
        
        # Execute operation
        try:
            locker_data = {
                'locker_id': self.locker_id_input.text(),
                'location': self.location_input.text(),
                'form': self.form_input.text(),
                'color': self.color_input.text(),
                'cond': self.condition_input.currentText(),
                'assigned': 0
            }
            
            locker = self.furniture_service.create_locker(locker_data)
            
            # Show success
            self.show_success_feedback(
                f"Locker created successfully with ID: {locker.locker_id}"
            )
            
            # Clear form
            self._clear_form()
            
        except Exception as e:
            self.show_error_feedback(f"Failed to create locker: {str(e)}")
    
    def _validate_creation_fields(self) -> Dict[str, ValidationResult]:
        """Validate all creation fields."""
        results = {}
        
        if hasattr(self, 'locker_id_input'):
            results['locker_id'] = self.validator.validate_furniture_id(
                self.locker_id_input.text(), "locker"
            )
        
        if hasattr(self, 'location_input'):
            results['location'] = self.validator.validate_location(
                self.location_input.text()
            )
        
        if hasattr(self, 'form_input'):
            results['form'] = self.validator.validate_form(
                self.form_input.text()
            )
        
        if hasattr(self, 'color_input'):
            results['color'] = self.validator.validate_color(
                self.color_input.text()
            )
        
        if hasattr(self, 'condition_input'):
            results['condition'] = self.validator.validate_condition(
                self.condition_input.currentText()
            )
        
        return results


class FurnitureUpdateWorkflow(FurnitureOperationWorkflow):
    """Standardized workflow for furniture updates."""
    
    def __init__(self, parent: BaseWindow = None):
        super().__init__("Update Furniture", parent)
        self._setup_update_form()
    
    def _setup_update_form(self):
        """Setup the furniture update form."""
        # Furniture Type
        self.add_field("Furniture Type", "dropdown", "Select furniture type", True)
        self.furniture_type_input.addItems(["chair", "locker"])
        
        # Furniture ID
        self.add_field("Furniture ID", "text", "Enter furniture ID to update", True)
        
        # New Location
        self.add_field("New Location", "text", "Enter new location (leave blank to keep current)", False)
        
        # New Condition
        self.add_field("New Condition", "dropdown", "Select new condition", False)
        self.new_condition_input.addItems(["", "Good", "Fair", "Needs Repair", "Poor"])
        
        # Action buttons
        self.add_action_button("Clear", "secondary", self._clear_form)
        self.add_action_button("Update Furniture", "primary", self._on_update_furniture)
    
    def _clear_form(self):
        """Clear the form."""
        if hasattr(self, 'furniture_type_input'):
            self.furniture_type_input.setCurrentIndex(0)
        if hasattr(self, 'furniture_id_input'):
            self.furniture_id_input.clear()
        if hasattr(self, 'new_location_input'):
            self.new_location_input.clear()
        if hasattr(self, 'new_condition_input'):
            self.new_condition_input.setCurrentIndex(0)
    
    def _on_update_furniture(self):
        """Handle furniture update with full workflow."""
        # Validate furniture type and ID
        furniture_type = self.furniture_type_input.currentText() if hasattr(self, 'furniture_type_input') else ""
        furniture_id = self.furniture_id_input.text() if hasattr(self, 'furniture_id_input') else ""
        
        if not furniture_type or not furniture_id:
            self.show_error_feedback("Furniture type and ID are required")
            return
        
        # Check if furniture exists
        if furniture_type == "chair":
            furniture = self.furniture_service.get_chair_by_id(furniture_id)
        else:
            furniture = self.furniture_service.get_locker_by_id(furniture_id)
            
        if not furniture:
            self.show_error_feedback(f"{furniture_type.capitalize()} not found")
            return
        
        # Prepare update data
        update_data = {}
        
        if hasattr(self, 'new_location_input') and self.new_location_input.text():
            location_validation = self.validator.validate_location(self.new_location_input.text())
            if not location_validation.is_valid:
                self.show_error_feedback(location_validation.message)
                return
            update_data['location'] = self.new_location_input.text()
        
        if hasattr(self, 'new_condition_input') and self.new_condition_input.currentText():
            condition_validation = self.validator.validate_condition(self.new_condition_input.currentText())
            if not condition_validation.is_valid:
                self.show_error_feedback(condition_validation.message)
                return
            update_data['cond'] = self.new_condition_input.currentText()
        
        if not update_data:
            self.show_error_feedback("Please provide at least one field to update")
            return
        
        # Prepare summary data
        summary_data = {
            'Furniture Type': furniture_type.capitalize(),
            'Furniture ID': furniture_id,
            'Current Location': furniture.location or "N/A",
            'Current Condition': furniture.cond or "N/A"
        }
        
        if 'location' in update_data:
            summary_data['New Location'] = update_data['location']
        if 'cond' in update_data:
            summary_data['New Condition'] = update_data['cond']
        
        # Show confirmation
        if not self.show_confirmation_dialog(summary_data):
            return
        
        # Execute operation
        try:
            if furniture_type == "chair":
                updated_furniture = self.furniture_service.update_chair(furniture_id, update_data)
            else:
                updated_furniture = self.furniture_service.update_locker(furniture_id, update_data)
            
            if updated_furniture:
                self.show_success_feedback(f"{furniture_type.capitalize()} updated successfully")
                self._clear_form()
            else:
                self.show_error_feedback(f"Failed to update {furniture_type}")
            
        except Exception as e:
            self.show_error_feedback(f"Failed to update {furniture_type}: {str(e)}")


class FurnitureDeletionWorkflow(FurnitureOperationWorkflow):
    """Standardized workflow for furniture deletion."""
    
    def __init__(self, parent: BaseWindow = None):
        super().__init__("Delete Furniture", parent)
        self._setup_deletion_form()
    
    def _setup_deletion_form(self):
        """Setup the furniture deletion form."""
        # Furniture Type
        self.add_field("Furniture Type", "dropdown", "Select furniture type", True)
        self.furniture_type_input.addItems(["chair", "locker"])
        
        # Furniture ID
        self.add_field("Furniture ID", "text", "Enter furniture ID to delete", True)
        
        # Reason for deletion
        self.add_field("Reason for Deletion", "text", "Brief reason for deletion", True)
        
        # Action button
        self.add_action_button("Delete Furniture", "danger", self._on_delete_furniture)
    
    def _on_delete_furniture(self):
        """Handle furniture deletion with full workflow."""
        # Validate furniture type and ID
        furniture_type = self.furniture_type_input.currentText() if hasattr(self, 'furniture_type_input') else ""
        furniture_id = self.furniture_id_input.text() if hasattr(self, 'furniture_id_input') else ""
        
        if not furniture_type or not furniture_id:
            self.show_error_feedback("Furniture type and ID are required")
            return
        
        # Check if furniture exists
        if furniture_type == "chair":
            furniture = self.furniture_service.get_chair_by_id(furniture_id)
        else:
            furniture = self.furniture_service.get_locker_by_id(furniture_id)
            
        if not furniture:
            self.show_error_feedback(f"{furniture_type.capitalize()} not found")
            return
        
        # Get reason
        reason = self.reason_for_deletion_input.text() if hasattr(self, 'reason_for_deletion_input') else ""
        
        if not reason:
            self.show_error_feedback("Reason for deletion is required")
            return
        
        # Prepare summary data
        summary_data = {
            f'{furniture_type.capitalize()} ID': furniture_id,
            'Location': furniture.location or "N/A",
            'Form': furniture.form or "N/A",
            'Condition': furniture.cond or "N/A",
            'Reason for Deletion': reason
        }
        
        # Show confirmation with warning
        confirm_dialog = ConfirmationDialog(
            title="Confirm Deletion",
            message=f"<b>Warning:</b> This action cannot be undone.<br><br>Are you sure you want to delete {furniture_type} {furniture_id}?",
            parent=self.parent_window,
            confirm_text="Delete Permanently",
            cancel_text="Cancel",
            rich_text=True
        )
        
        if confirm_dialog.exec() != QDialog.DialogCode.Accepted:
            return
        
        # Execute operation
        try:
            if furniture_type == "chair":
                success = self.furniture_service.delete_chair(furniture_id)
            else:
                success = self.furniture_service.delete_locker(furniture_id)
            
            if success:
                self.show_success_feedback(f"{furniture_type.capitalize()} deleted successfully")
                
                # Log the deletion with reason
                logger.info(f"{furniture_type.capitalize()} {furniture_id} deleted. Reason: {reason}")
                
                # Clear form
                if hasattr(self, 'furniture_type_input'):
                    self.furniture_type_input.setCurrentIndex(0)
                if hasattr(self, 'furniture_id_input'):
                    self.furniture_id_input.clear()
                if hasattr(self, 'reason_for_deletion_input'):
                    self.reason_for_deletion_input.clear()
            else:
                self.show_error_feedback(f"Failed to delete {furniture_type}")
            
        except Exception as e:
            self.show_error_feedback(f"Failed to delete {furniture_type}: {str(e)}")


class FurnitureWorkflowManager:
    """Manager for coordinating between different furniture workflows."""
    
    def __init__(self, parent_window: BaseWindow):
        self.parent_window = parent_window
        self.current_workflow = None
        self.workflow_stack = []
    
    def start_workflow(self, workflow_type: str):
        """Start a new furniture workflow."""
        # Clean up previous workflow if any
        if self.current_workflow:
            self.workflow_stack.append(self.current_workflow)
            self.current_workflow.setVisible(False)
        
        # Create new workflow
        if workflow_type == "create_chair":
            self.current_workflow = ChairCreationWorkflow(self.parent_window)
        elif workflow_type == "create_locker":
            self.current_workflow = LockerCreationWorkflow(self.parent_window)
        elif workflow_type == "update":
            self.current_workflow = FurnitureUpdateWorkflow(self.parent_window)
        elif workflow_type == "delete":
            self.current_workflow = FurnitureDeletionWorkflow(self.parent_window)
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