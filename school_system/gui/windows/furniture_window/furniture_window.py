"""
Furniture management window for the School System Management application.

This module provides the furniture management interface for admin users (admin and librarian roles).
Implements standardized, user-centric workflows for all furniture-related services with consistency,
validation, and system integrity following the FURNITURE MANAGEMENT FLOW template.
"""

from PyQt6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QLabel, QLineEdit, QPushButton, 
                            QHBoxLayout, QComboBox, QTabWidget, QTableWidget, QTableWidgetItem, 
                            QTextEdit, QSizePolicy, QMessageBox, QDialog, QMenu)
from PyQt6.QtCore import Qt, pyqtSignal, QTimer
from PyQt6.QtGui import QAction
from typing import Callable, Optional
from datetime import datetime

from school_system.gui.base.base_window import BaseWindow
from school_system.gui.dialogs.message_dialog import show_error_message, show_success_message
from school_system.gui.dialogs.confirm_dialog import ConfirmationDialog
from school_system.config.logging import logger
from school_system.services.furniture_service import FurnitureService
from school_system.core.exceptions import DatabaseException, ValidationError
from school_system.gui.windows.furniture_window.furniture_validation import FurnitureValidator, ValidationResult, FieldValidator
from school_system.gui.windows.furniture_window.furniture_workflow_components import (
    FurnitureWorkflowManager, ChairCreationWorkflow,
    LockerCreationWorkflow, FurnitureUpdateWorkflow, FurnitureDeletionWorkflow
)


class FurnitureWindow(BaseWindow):
    """Furniture management window for admin users with standardized workflows."""

    def __init__(self, parent: QMainWindow, current_user: str, current_role: str):
        """
        Initialize the furniture window with standardized workflow management.

        Args:
            parent: The parent window
            current_user: The current logged-in username
            current_role: The current user's role
        """
        super().__init__("School System - Furniture Management", parent)

        self.parent = parent
        self.current_user = current_user
        self.current_role = current_role
        self.furniture_service = FurnitureService()
        self.validator = FurnitureValidator()
        
        # Initialize workflow manager
        self.workflow_manager = FurnitureWorkflowManager(self)

        # Check if user has admin privileges
        if self.current_role not in ["admin", "librarian"]:
            show_error_message("Access Denied", "You do not have permission to access furniture management.", self)
            self.close()
            return

        # Set minimum size
        self.setMinimumSize(1200, 800)

        # Initialize UI
        self._setup_widgets()
        
        # Setup undo functionality
        self._setup_undo_system()
        
        # Track last operations for undo
        self.last_operation = None
        self.undo_timer = None
        self.undo_stack = []
        
        # Add undo action to menu
        self._add_undo_action()

    def _setup_widgets(self):
        """Setup the furniture management widgets."""
        # Create tab widget for different sections
        tab_widget = QTabWidget()
        self.add_widget_to_content(tab_widget)

        # Furniture Management Tab
        furniture_tab = self._create_furniture_management_tab()
        tab_widget.addTab(furniture_tab, "Furniture Management")

        # Furniture Assignment Tab
        assignment_tab = self._create_assignment_tab()
        tab_widget.addTab(assignment_tab, "Furniture Assignment")

        # Maintenance Tab
        maintenance_tab = self._create_maintenance_tab()
        tab_widget.addTab(maintenance_tab, "Maintenance")

        # Statistics Tab
        statistics_tab = self._create_statistics_tab()
        tab_widget.addTab(statistics_tab, "Statistics & Reports")

    def _setup_undo_system(self):
        """Setup the undo system for furniture operations."""
        # Initialize undo stack and timer
        self.undo_stack = []
        self.undo_timer = None
    
    def _add_undo_action(self):
        """Add undo action to the menu bar."""
        # Get or create menu bar
        menu_bar = self.menuBar()
        if not menu_bar:
            menu_bar = self.create_menu_bar()
        
        # Add Edit menu if it doesn't exist
        edit_menu = menu_bar.findChild(QMenu, "edit_menu")
        if not edit_menu:
            edit_menu = menu_bar.addMenu("Edit")
            edit_menu.setObjectName("edit_menu")
        
        # Add Undo action
        undo_action = QAction("Undo Last Operation", self)
        undo_action.setShortcut("Ctrl+Z")
        undo_action.setEnabled(False)  # Initially disabled
        undo_action.triggered.connect(self._on_undo_operation)
        edit_menu.addAction(undo_action)
        
        # Store reference
        self.undo_action = undo_action
    
    def _on_undo_operation(self):
        """Handle undo operation."""
        if self.undo_stack:
            last_operation = self.undo_stack.pop()
            
            try:
                # Attempt to undo the operation
                if last_operation['type'] == 'create':
                    # Undo create by deleting
                    if last_operation['data']['furniture_type'] == 'chair':
                        self.furniture_service.delete_chair(last_operation['data']['furniture_id'])
                    else:
                        self.furniture_service.delete_locker(last_operation['data']['furniture_id'])
                    show_success_message("Undo Successful",
                                        f"{last_operation['data']['furniture_type'].capitalize()} creation undone: {last_operation['data']['furniture_id']}", self)
                elif last_operation['type'] == 'delete':
                    # Undo delete by recreating
                    furniture_data = last_operation['data']['furniture_data']
                    if furniture_data['furniture_type'] == 'chair':
                        self.furniture_service.create_chair(furniture_data)
                    else:
                        self.furniture_service.create_locker(furniture_data)
                    show_success_message("Undo Successful",
                                        f"{furniture_data['furniture_type'].capitalize()} deletion undone: {furniture_data['furniture_id']}", self)
                
                # Refresh table
                self._refresh_furniture_table()
                
                # Update undo action state
                if self.undo_action:
                    self.undo_action.setEnabled(len(self.undo_stack) > 0)
                
            except Exception as e:
                show_error_message("Undo Failed",
                                  f"Failed to undo operation: {str(e)}", self)
    
    def _track_operation(self, operation_type: str, operation_data: dict):
        """Track an operation for potential undo."""
        # Add to undo stack (limit to last 10 operations)
        self.undo_stack.append({
            'type': operation_type,
            'data': operation_data,
            'timestamp': datetime.now().isoformat()
        })
        
        # Limit stack size
        if len(self.undo_stack) > 10:
            self.undo_stack.pop(0)
        
        # Enable undo action
        if self.undo_action:
            self.undo_action.setEnabled(True)
        
        # Start undo timer (5 seconds)
        if self.undo_timer:
            self.undo_timer.stop()
        
        self.undo_timer = QTimer(self)
        self.undo_timer.timeout.connect(self._clear_undo_stack)
        self.undo_timer.start(5000)  # 5 seconds
    
    def _clear_undo_stack(self):
        """Clear the undo stack after timeout."""
        self.undo_stack.clear()
        if hasattr(self, 'undo_action') and self.undo_action:
            self.undo_action.setEnabled(False)
        if hasattr(self, 'undo_timer') and self.undo_timer:
            self.undo_timer.stop()

    def _create_furniture_management_tab(self) -> QWidget:
        """Create the furniture management tab with standardized workflows."""
        tab = QWidget()
        layout = self.create_flex_layout("column", False)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.set_spacing(15)

        # Create Chair Section - Using Standardized Workflow
        create_chair_section = self.create_card("Create New Chair",
                                               "Use the form below to create a new chair record")
        create_chair_workflow = ChairCreationWorkflow(self)
        create_chair_workflow.operation_completed.connect(self._handle_operation_completed)
        create_chair_section.layout.addWidget(create_chair_workflow)
        layout.add_widget(create_chair_section)

        # Create Locker Section - Using Standardized Workflow
        create_locker_section = self.create_card("Create New Locker",
                                               "Use the form below to create a new locker record")
        create_locker_workflow = LockerCreationWorkflow(self)
        create_locker_workflow.operation_completed.connect(self._handle_operation_completed)
        create_locker_section.layout.addWidget(create_locker_workflow)
        layout.add_widget(create_locker_section)

        # Update Furniture Section - Using Standardized Workflow
        update_section = self.create_card("Update Furniture",
                                          "Update existing furniture information")
        update_workflow = FurnitureUpdateWorkflow(self)
        update_workflow.operation_completed.connect(self._handle_operation_completed)
        update_section.layout.addWidget(update_workflow)
        layout.add_widget(update_section)

        # Delete Furniture Section - Using Standardized Workflow
        delete_section = self.create_card("Delete Furniture",
                                          "Permanently remove furniture from the system")
        delete_workflow = FurnitureDeletionWorkflow(self)
        delete_workflow.operation_completed.connect(self._handle_operation_completed)
        delete_section.layout.addWidget(delete_workflow)
        layout.add_widget(delete_section)

        # View Furniture Section
        view_section = self.create_card("View Furniture", "Browse and search existing furniture records")
        view_form = QWidget()
        view_layout = self.create_flex_layout("column", False)
        view_layout.set_spacing(10)

        # Search box with real-time validation
        self.search_box = self.create_search_box("Search furniture...")
        self.search_box.search_text_changed.connect(self._on_search_furniture)
        view_layout.add_widget(self.search_box)

        # Furniture type filter
        furniture_type_filter_label = QLabel("Filter by Type:")
        view_layout.add_widget(furniture_type_filter_label)
        self.furniture_type_filter_combo = QComboBox()
        self.furniture_type_filter_combo.addItems(["all", "chair", "locker"])
        self.furniture_type_filter_combo.currentTextChanged.connect(self._on_search_furniture)
        view_layout.add_widget(self.furniture_type_filter_combo)

        # Refresh button
        refresh_button = self.create_button("Refresh Furniture", "secondary")
        refresh_button.clicked.connect(self._refresh_furniture_table)
        view_layout.add_widget(refresh_button)

        # Furniture table with enhanced features
        self.furniture_table = self.create_table(0, 8)  # Added column for undo
        self.furniture_table.setHorizontalHeaderLabels(["Type", "ID", "Location", "Form", "Color", "Condition", "Assigned", "Actions", ""])
        view_layout.add_widget(self.furniture_table)

        view_form.setLayout(view_layout._layout)
        view_section.layout.addWidget(view_form)
        layout.add_widget(view_section)

        tab.setLayout(layout._layout)
        return tab

    def _create_assignment_tab(self) -> QWidget:
        """Create the furniture assignment tab."""
        tab = QWidget()
        layout = self.create_flex_layout("column", False)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.set_spacing(15)

        # Assign Chair Section
        chair_assignment_section = self.create_card("Assign Chair to Student", "")
        chair_assignment_form = QWidget()
        chair_assignment_layout = self.create_flex_layout("column", False)
        chair_assignment_layout.set_spacing(10)

        # Student ID
        chair_student_id_label = QLabel("Student ID:")
        chair_assignment_layout.add_widget(chair_student_id_label)
        self.chair_student_id_input = self.create_input("Enter student ID")
        chair_assignment_layout.add_widget(self.chair_student_id_input)

        # Chair ID
        chair_id_label = QLabel("Chair ID:")
        chair_assignment_layout.add_widget(chair_id_label)
        self.chair_id_input = self.create_input("Enter chair ID")
        chair_assignment_layout.add_widget(self.chair_id_input)

        # Assign button
        assign_chair_button = self.create_button("Assign Chair", "primary")
        assign_chair_button.clicked.connect(self._on_assign_chair)
        chair_assignment_layout.add_widget(assign_chair_button)

        chair_assignment_form.setLayout(chair_assignment_layout._layout)
        chair_assignment_section.layout.addWidget(chair_assignment_form)
        layout.add_widget(chair_assignment_section)

        # Assign Locker Section
        locker_assignment_section = self.create_card("Assign Locker to Student", "")
        locker_assignment_form = QWidget()
        locker_assignment_layout = self.create_flex_layout("column", False)
        locker_assignment_layout.set_spacing(10)

        # Student ID
        locker_student_id_label = QLabel("Student ID:")
        locker_assignment_layout.add_widget(locker_student_id_label)
        self.locker_student_id_input = self.create_input("Enter student ID")
        locker_assignment_layout.add_widget(self.locker_student_id_input)

        # Locker ID
        locker_id_label = QLabel("Locker ID:")
        locker_assignment_layout.add_widget(locker_id_label)
        self.locker_id_input = self.create_input("Enter locker ID")
        locker_assignment_layout.add_widget(self.locker_id_input)

        # Assign button
        assign_locker_button = self.create_button("Assign Locker", "primary")
        assign_locker_button.clicked.connect(self._on_assign_locker)
        locker_assignment_layout.add_widget(assign_locker_button)

        locker_assignment_form.setLayout(locker_assignment_layout._layout)
        locker_assignment_section.layout.addWidget(locker_assignment_form)
        layout.add_widget(locker_assignment_section)

        # Reassign Furniture Section
        reassign_section = self.create_card("Reassign Furniture", "")
        reassign_form = QWidget()
        reassign_layout = self.create_flex_layout("column", False)
        reassign_layout.set_spacing(10)

        # Furniture Type
        reassign_type_label = QLabel("Furniture Type:")
        reassign_layout.add_widget(reassign_type_label)
        self.reassign_type_combo = QComboBox()
        self.reassign_type_combo.addItems(["chair", "locker"])
        reassign_layout.add_widget(self.reassign_type_combo)

        # Student ID
        reassign_student_id_label = QLabel("Student ID:")
        reassign_layout.add_widget(reassign_student_id_label)
        self.reassign_student_id_input = self.create_input("Enter student ID")
        reassign_layout.add_widget(self.reassign_student_id_input)

        # New Furniture ID
        reassign_furniture_id_label = QLabel("New Furniture ID:")
        reassign_layout.add_widget(reassign_furniture_id_label)
        self.reassign_furniture_id_input = self.create_input("Enter new furniture ID")
        reassign_layout.add_widget(self.reassign_furniture_id_input)

        # Reassign button
        reassign_button = self.create_button("Reassign Furniture", "secondary")
        reassign_button.clicked.connect(self._on_reassign_furniture)
        reassign_layout.add_widget(reassign_button)

        reassign_form.setLayout(reassign_layout._layout)
        reassign_section.layout.addWidget(reassign_form)
        layout.add_widget(reassign_section)

        # View Assignments Section
        assignments_section = self.create_card("View Furniture Assignments", "")
        assignments_form = QWidget()
        assignments_layout = self.create_flex_layout("column", False)
        assignments_layout.set_spacing(10)

        # Refresh button
        refresh_assignments_button = self.create_button("Refresh Assignments", "secondary")
        refresh_assignments_button.clicked.connect(self._refresh_assignments_table)
        assignments_layout.add_widget(refresh_assignments_button)

        # Assignments table
        self.assignments_table = self.create_table(0, 5)
        self.assignments_table.setHorizontalHeaderLabels(["Type", "Student ID", "Furniture ID", "Assigned Date", "Actions"])
        assignments_layout.add_widget(self.assignments_table)

        assignments_form.setLayout(assignments_layout._layout)
        assignments_section.layout.addWidget(assignments_form)
        layout.add_widget(assignments_section)

        tab.setLayout(layout._layout)
        return tab

    def _create_maintenance_tab(self) -> QWidget:
        """Create the maintenance tab."""
        tab = QWidget()
        layout = self.create_flex_layout("column", False)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.set_spacing(15)

        # Report Maintenance Section
        maintenance_section = self.create_card("Report Maintenance Issue", "")
        maintenance_form = QWidget()
        maintenance_layout = self.create_flex_layout("column", False)
        maintenance_layout.set_spacing(10)

        # Furniture Type
        maintenance_type_label = QLabel("Furniture Type:")
        maintenance_layout.add_widget(maintenance_type_label)
        self.maintenance_type_combo = QComboBox()
        self.maintenance_type_combo.addItems(["chair", "locker"])
        maintenance_layout.add_widget(self.maintenance_type_combo)

        # Furniture ID
        maintenance_id_label = QLabel("Furniture ID:")
        maintenance_layout.add_widget(maintenance_id_label)
        self.maintenance_id_input = self.create_input("Enter furniture ID")
        maintenance_layout.add_widget(self.maintenance_id_input)

        # Issue Description
        issue_label = QLabel("Issue Description:")
        maintenance_layout.add_widget(issue_label)
        self.issue_description_input = QTextEdit()
        self.issue_description_input.setMaximumHeight(100)
        maintenance_layout.add_widget(self.issue_description_input)

        # Report button
        report_button = self.create_button("Report Issue", "primary")
        report_button.clicked.connect(self._on_report_maintenance)
        maintenance_layout.add_widget(report_button)

        maintenance_form.setLayout(maintenance_layout._layout)
        maintenance_section.layout.addWidget(maintenance_form)
        layout.add_widget(maintenance_section)

        # Update Location Section
        location_section = self.create_card("Update Furniture Location", "")
        location_form = QWidget()
        location_layout = self.create_flex_layout("column", False)
        location_layout.set_spacing(10)

        # Furniture Type
        location_type_label = QLabel("Furniture Type:")
        location_layout.add_widget(location_type_label)
        self.location_type_combo = QComboBox()
        self.location_type_combo.addItems(["chair", "locker"])
        location_layout.add_widget(self.location_type_combo)

        # Furniture ID
        location_id_label = QLabel("Furniture ID:")
        location_layout.add_widget(location_id_label)
        self.location_id_input = self.create_input("Enter furniture ID")
        location_layout.add_widget(self.location_id_input)

        # New Location
        new_location_label = QLabel("New Location:")
        location_layout.add_widget(new_location_label)
        self.new_location_input = self.create_input("Enter new location")
        location_layout.add_widget(self.new_location_input)

        # Update button
        update_location_button = self.create_button("Update Location", "secondary")
        update_location_button.clicked.connect(self._on_update_location)
        location_layout.add_widget(update_location_button)

        location_form.setLayout(location_layout._layout)
        location_section.layout.addWidget(location_form)
        layout.add_widget(location_section)

        tab.setLayout(layout._layout)
        return tab

    def _create_statistics_tab(self) -> QWidget:
        """Create the statistics and reports tab."""
        tab = QWidget()
        layout = self.create_flex_layout("column", False)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.set_spacing(15)

        # Statistics Section
        stats_section = self.create_card("Furniture Statistics", "")
        stats_form = QWidget()
        stats_layout = self.create_flex_layout("column", False)
        stats_layout.set_spacing(10)

        # Generate statistics button
        generate_stats_button = self.create_button("Generate Statistics", "primary")
        generate_stats_button.clicked.connect(self._on_generate_statistics)
        stats_layout.add_widget(generate_stats_button)

        # Statistics display
        self.statistics_display = QTextEdit()
        self.statistics_display.setReadOnly(True)
        stats_layout.add_widget(self.statistics_display)

        stats_form.setLayout(stats_layout._layout)
        stats_section.layout.addWidget(stats_form)
        layout.add_widget(stats_section)

        # Condition Analysis Section
        condition_section = self.create_card("Condition Analysis", "")
        condition_form = QWidget()
        condition_layout = self.create_flex_layout("column", False)
        condition_layout.set_spacing(10)

        # Generate condition analysis button
        generate_condition_button = self.create_button("Analyze Conditions", "primary")
        generate_condition_button.clicked.connect(self._on_analyze_conditions)
        condition_layout.add_widget(generate_condition_button)

        # Condition analysis display
        self.condition_display = QTextEdit()
        self.condition_display.setReadOnly(True)
        condition_layout.add_widget(self.condition_display)

        condition_form.setLayout(condition_layout._layout)
        condition_section.layout.addWidget(condition_form)
        layout.add_widget(condition_section)

        # Inventory Report Section
        inventory_section = self.create_card("Inventory Report", "")
        inventory_form = QWidget()
        inventory_layout = self.create_flex_layout("column", False)
        inventory_layout.set_spacing(10)

        # Generate inventory report button
        generate_inventory_button = self.create_button("Generate Inventory Report", "primary")
        generate_inventory_button.clicked.connect(self._on_generate_inventory_report)
        inventory_layout.add_widget(generate_inventory_button)

        # Inventory report display
        self.inventory_display = QTextEdit()
        self.inventory_display.setReadOnly(True)
        inventory_layout.add_widget(self.inventory_display)

        inventory_form.setLayout(inventory_layout._layout)
        inventory_section.layout.addWidget(inventory_form)
        layout.add_widget(inventory_section)

        tab.setLayout(layout._layout)
        return tab

    def _handle_operation_completed(self, success: bool, message: str):
        """
        Handle completion of furniture operations with appropriate feedback and state updates.
        
        This method serves as the central callback for all furniture workflow operations,
        ensuring consistent post-operation behavior including table refreshes,
        user notifications, and undo tracking.
        
        Args:
            success: Boolean indicating if the operation was successful
            message: Descriptive message about the operation result
        """
        if success:
            # Refresh the furniture table to show latest data
            self._refresh_furniture_table()
            
            # Show appropriate success message based on operation type
            if "created" in message.lower():
                show_success_message("Success", message, self)
                # Track creation for potential undo (5-second window)
                # Furniture ID can be extracted from message for undo tracking
                if "chair" in message.lower():
                    chair_id = message.split("ID: ")[1].strip()
                    self._track_operation("create", {
                        'type': 'create',
                        'furniture_type': 'chair',
                        'furniture_id': chair_id
                    })
                elif "locker" in message.lower():
                    locker_id = message.split("ID: ")[1].strip()
                    self._track_operation("create", {
                        'type': 'create',
                        'furniture_type': 'locker',
                        'furniture_id': locker_id
                    })
            elif "updated" in message.lower():
                show_success_message("Success", message, self)
                # Track update for potential undo
            elif "deleted" in message.lower():
                show_success_message("Success", message, self)
                # Track deletion for potential undo
        else:
            # Show error message for failed operations
            show_error_message("Error", message, self)

    def _on_search_furniture(self, query: str = ""):
        """Handle furniture search."""
        try:
            furniture_type = self.furniture_type_filter_combo.currentText()
            results = self.furniture_service.search_furniture(query, furniture_type)
            self._populate_furniture_table(results)
        except Exception as e:
            show_error_message("Error", f"Search failed: {str(e)}", self)

    def _refresh_furniture_table(self):
        """Refresh the furniture table."""
        try:
            # Get all furniture items
            chairs = self.furniture_service.get_all_chairs()
            lockers = self.furniture_service.get_all_lockers()
            all_furniture = chairs + lockers
            self._populate_furniture_table(all_furniture)
        except Exception as e:
            show_error_message("Error", f"Failed to refresh furniture: {str(e)}", self)

    def _populate_furniture_table(self, furniture_items):
        """Populate the furniture table with data and enhanced features."""
        self.furniture_table.setRowCount(0)
        
        for item in furniture_items:
            row_position = self.furniture_table.rowCount()
            self.furniture_table.insertRow(row_position)
            
            # Determine type and ID
            if hasattr(item, 'chair_id'):
                furniture_type = "Chair"
                furniture_id = str(item.chair_id)
            else:
                furniture_type = "Locker"
                furniture_id = str(item.locker_id)

            self.furniture_table.setItem(row_position, 0, QTableWidgetItem(furniture_type))
            self.furniture_table.setItem(row_position, 1, QTableWidgetItem(furniture_id))
            self.furniture_table.setItem(row_position, 2, QTableWidgetItem(item.location or ""))
            self.furniture_table.setItem(row_position, 3, QTableWidgetItem(item.form or ""))
            self.furniture_table.setItem(row_position, 4, QTableWidgetItem(item.color or ""))
            self.furniture_table.setItem(row_position, 5, QTableWidgetItem(item.cond or ""))
            self.furniture_table.setItem(row_position, 6, QTableWidgetItem("Yes" if item.assigned else "No"))
            
            # Add action buttons container
            action_widget = QWidget()
            action_layout = QHBoxLayout(action_widget)
            action_layout.setContentsMargins(0, 0, 0, 0)
            action_layout.setSpacing(5)

            # View button
            view_button = self.create_button("View", "secondary")
            view_button.clicked.connect(lambda _, it=item: self._view_furniture_details(it))
            action_layout.addWidget(view_button)

            # Edit button
            edit_button = self.create_button("Edit", "primary")
            edit_button.clicked.connect(lambda _, it=item: self._start_edit_workflow(it))
            action_layout.addWidget(edit_button)

            # Delete button
            delete_button = self.create_button("Delete", "danger")
            delete_button.clicked.connect(lambda _, it=item: self._start_delete_workflow(it))
            action_layout.addWidget(delete_button)

            self.furniture_table.setCellWidget(row_position, 7, action_widget)
            
            # Add undo placeholder (will be populated if undo is available)
            undo_button = self.create_button("Undo", "secondary")
            undo_button.setVisible(False)  # Initially hidden
            self.furniture_table.setCellWidget(row_position, 8, undo_button)

    def _start_edit_workflow(self, furniture_item):
        """Start the edit workflow for a specific furniture item."""
        try:
            # Determine furniture type
            if hasattr(furniture_item, 'chair_id'):
                furniture_type = "chair"
                furniture_id = furniture_item.chair_id
            else:
                furniture_type = "locker"
                furniture_id = furniture_item.locker_id
            
            # Create update workflow and pre-populate with furniture data
            update_workflow = FurnitureUpdateWorkflow(self)
            update_workflow.operation_completed.connect(self._handle_operation_completed)
            
            # Pre-populate the furniture type and ID fields
            if hasattr(update_workflow, 'furniture_type_input'):
                update_workflow.furniture_type_input.setCurrentText(furniture_type)
                update_workflow.furniture_type_input.setEnabled(False)
            
            if hasattr(update_workflow, 'furniture_id_input'):
                update_workflow.furniture_id_input.setText(str(furniture_id))
                update_workflow.furniture_id_input.setReadOnly(True)
            
            # Show the workflow
            self.workflow_manager.start_workflow("update")
            
        except Exception as e:
            show_error_message("Error", f"Failed to start edit workflow: {str(e)}", self)

    def _start_delete_workflow(self, furniture_item):
        """Start the delete workflow for a specific furniture item."""
        try:
            # Determine furniture type
            if hasattr(furniture_item, 'chair_id'):
                furniture_type = "chair"
                furniture_id = furniture_item.chair_id
            else:
                furniture_type = "locker"
                furniture_id = furniture_item.locker_id
            
            # Create delete workflow and pre-populate with furniture data
            delete_workflow = FurnitureDeletionWorkflow(self)
            delete_workflow.operation_completed.connect(self._handle_operation_completed)
            
            # Pre-populate the furniture type and ID fields
            if hasattr(delete_workflow, 'furniture_type_input'):
                delete_workflow.furniture_type_input.setCurrentText(furniture_type)
                delete_workflow.furniture_type_input.setEnabled(False)
            
            if hasattr(delete_workflow, 'furniture_id_input'):
                delete_workflow.furniture_id_input.setText(str(furniture_id))
                delete_workflow.furniture_id_input.setReadOnly(True)
            
            # Show the workflow
            self.workflow_manager.start_workflow("delete")
            
        except Exception as e:
            show_error_message("Error", f"Failed to start delete workflow: {str(e)}", self)

    def _view_furniture_details(self, furniture_item):
        """View detailed information about a furniture item."""
        try:
            # Determine furniture type
            if hasattr(furniture_item, 'chair_id'):
                furniture_type = "Chair"
                furniture_id = furniture_item.chair_id
            else:
                furniture_type = "Locker"
                furniture_id = furniture_item.locker_id
            
            details = f"{furniture_type} Details:\n\nID: {furniture_id}\nLocation: {furniture_item.location}\nForm: {furniture_item.form}\nColor: {furniture_item.color}\nCondition: {furniture_item.cond}\nAssigned: {'Yes' if furniture_item.assigned else 'No'}"
            show_success_message(f"{furniture_type} Details", details, self)
        except Exception as e:
            show_error_message("Error", f"Failed to view furniture details: {str(e)}", self)

    # Event handlers for Furniture Assignment
    def _on_assign_chair(self):
        """Handle assign chair button click."""
        try:
            student_id = self.chair_student_id_input.text().strip()
            chair_id = self.chair_id_input.text().strip()

            if not student_id or not chair_id:
                show_error_message("Validation Error", "Student ID and Chair ID are required", self)
                return

            # Check if chair exists and is available
            chair = self.furniture_service.get_chair_by_id(chair_id)
            if not chair:
                show_error_message("Error", "Chair not found", self)
                return
            if chair.assigned:
                show_error_message("Error", "Chair is already assigned", self)
                return

            assignment_data = {
                'student_id': student_id,
                'chair_id': chair_id,
                'assigned_date': None  # Will be set automatically
            }

            assignment = self.furniture_service.create_chair_assignment(assignment_data)
            show_success_message("Success", f"Chair assigned successfully to student {student_id}", self)
            self._refresh_assignments_table()
            self._refresh_furniture_table()
            
            # Clear form
            self.chair_student_id_input.clear()
            self.chair_id_input.clear()

        except Exception as e:
            show_error_message("Error", f"An error occurred: {str(e)}", self)

    def _on_assign_locker(self):
        """Handle assign locker button click."""
        try:
            student_id = self.locker_student_id_input.text().strip()
            locker_id = self.locker_id_input.text().strip()

            if not student_id or not locker_id:
                show_error_message("Validation Error", "Student ID and Locker ID are required", self)
                return

            # Check if locker exists and is available
            locker = self.furniture_service.get_locker_by_id(locker_id)
            if not locker:
                show_error_message("Error", "Locker not found", self)
                return
            if locker.assigned:
                show_error_message("Error", "Locker is already assigned", self)
                return

            assignment_data = {
                'student_id': student_id,
                'locker_id': locker_id,
                'assigned_date': None  # Will be set automatically
            }

            assignment = self.furniture_service.create_locker_assignment(assignment_data)
            show_success_message("Success", f"Locker assigned successfully to student {student_id}", self)
            self._refresh_assignments_table()
            self._refresh_furniture_table()
            
            # Clear form
            self.locker_student_id_input.clear()
            self.locker_id_input.clear()

        except Exception as e:
            show_error_message("Error", f"An error occurred: {str(e)}", self)

    def _on_reassign_furniture(self):
        """Handle reassign furniture button click."""
        try:
            furniture_type = self.reassign_type_combo.currentText()
            student_id = self.reassign_student_id_input.text().strip()
            new_furniture_id = self.reassign_furniture_id_input.text().strip()

            if not furniture_type or not student_id or not new_furniture_id:
                show_error_message("Validation Error", "All fields are required", self)
                return

            success = self.furniture_service.reassign_furniture(student_id, new_furniture_id, furniture_type)
            if success:
                show_success_message("Success", f"{furniture_type.capitalize()} reassigned successfully", self)
                self._refresh_assignments_table()
                self._refresh_furniture_table()
            else:
                show_error_message("Error", f"Failed to reassign {furniture_type}", self)

        except Exception as e:
            show_error_message("Error", f"An error occurred: {str(e)}", self)

    def _on_report_maintenance(self):
        """Handle report maintenance button click."""
        try:
            furniture_type = self.maintenance_type_combo.currentText()
            furniture_id = self.maintenance_id_input.text().strip()
            issue = self.issue_description_input.toPlainText().strip()

            if not issue:
                show_error_message("Error", "Please describe the issue", self)
                return

            success = self.furniture_service.report_maintenance_issue(furniture_id, furniture_type, issue)
            if success:
                show_success_message("Success", "Maintenance issue reported successfully", self)
                self._refresh_furniture_table()
                
                # Clear form
                self.maintenance_id_input.clear()
                self.issue_description_input.clear()
            else:
                show_error_message("Error", "Failed to report maintenance issue", self)

        except Exception as e:
            show_error_message("Error", f"An error occurred: {str(e)}", self)

    def _on_update_location(self):
        """Handle update location button click."""
        try:
            furniture_type = self.location_type_combo.currentText()
            furniture_id = self.location_id_input.text().strip()
            new_location = self.new_location_input.text().strip()

            if not furniture_type or not furniture_id or not new_location:
                show_error_message("Validation Error", "All fields are required", self)
                return

            success = self.furniture_service.update_furniture_location(furniture_id, furniture_type, new_location)
            if success:
                show_success_message("Success", "Location updated successfully", self)
                self._refresh_furniture_table()
                
                # Clear form
                self.location_id_input.clear()
                self.new_location_input.clear()
            else:
                show_error_message("Error", "Failed to update location", self)

        except Exception as e:
            show_error_message("Error", f"An error occurred: {str(e)}", self)

    def _refresh_assignments_table(self):
        """Refresh the assignments table."""
        try:
            chair_assignments = self.furniture_service.get_all_chair_assignments()
            locker_assignments = self.furniture_service.get_all_locker_assignments()
            all_assignments = chair_assignments + locker_assignments
            
            self.assignments_table.setRowCount(0)
            
            for assignment in all_assignments:
                row_position = self.assignments_table.rowCount()
                self.assignments_table.insertRow(row_position)
                
                # Determine type
                if hasattr(assignment, 'chair_id'):
                    furniture_type = "Chair"
                    furniture_id = str(assignment.chair_id)
                else:
                    furniture_type = "Locker"
                    furniture_id = str(assignment.locker_id)

                self.assignments_table.setItem(row_position, 0, QTableWidgetItem(furniture_type))
                self.assignments_table.setItem(row_position, 1, QTableWidgetItem(str(assignment.student_id)))
                self.assignments_table.setItem(row_position, 2, QTableWidgetItem(furniture_id))
                self.assignments_table.setItem(row_position, 3, QTableWidgetItem(assignment.assigned_date or ""))
                
                # Add delete button
                delete_button = self.create_button("Delete", "danger")
                delete_button.clicked.connect(lambda _, a=assignment: self._on_delete_assignment(a))
                self.assignments_table.setCellWidget(row_position, 4, delete_button)

        except Exception as e:
            show_error_message("Error", f"Failed to refresh assignments: {str(e)}", self)

    def _on_delete_assignment(self, assignment):
        """Handle delete assignment action."""
        try:
            if hasattr(assignment, 'chair_id'):
                success = self.furniture_service.delete_chair_assignment(assignment.student_id)
            else:
                success = self.furniture_service.delete_locker_assignment(assignment.student_id)

            if success:
                show_success_message("Success", "Assignment deleted successfully", self)
                self._refresh_assignments_table()
                self._refresh_furniture_table()
            else:
                show_error_message("Error", "Failed to delete assignment", self)

        except Exception as e:
            show_error_message("Error", f"An error occurred: {str(e)}", self)

    def _on_generate_statistics(self):
        """Handle generate statistics button click."""
        try:
            stats = self.furniture_service.get_furniture_statistics()
            
            stats_text = "Furniture Statistics:\n\n"
            stats_text += f"Total Chairs: {stats.get('total_chairs', 0)}\n"
            stats_text += f"Assigned Chairs: {stats.get('assigned_chairs', 0)}\n"
            stats_text += f"Available Chairs: {stats.get('available_chairs', 0)}\n"
            stats_text += f"Chairs Needing Repair: {stats.get('chairs_needing_repair', 0)}\n\n"
            
            stats_text += f"Total Lockers: {stats.get('total_lockers', 0)}\n"
            stats_text += f"Assigned Lockers: {stats.get('assigned_lockers', 0)}\n"
            stats_text += f"Available Lockers: {stats.get('available_lockers', 0)}\n"
            stats_text += f"Lockers Needing Repair: {stats.get('lockers_needing_repair', 0)}\n\n"
            
            stats_text += f"Total Furniture: {stats.get('total_furniture', 0)}\n"
            stats_text += f"Assigned Furniture: {stats.get('assigned_furniture', 0)}\n"
            stats_text += f"Available Furniture: {stats.get('available_furniture', 0)}\n"
            stats_text += f"Furniture Needing Repair: {stats.get('furniture_needing_repair', 0)}\n"

            self.statistics_display.setText(stats_text)

        except Exception as e:
            show_error_message("Error", f"Failed to generate statistics: {str(e)}", self)

    def _on_analyze_conditions(self):
        """Handle analyze conditions button click."""
        try:
            analysis = self.furniture_service.analyze_furniture_condition()
            
            analysis_text = "Furniture Condition Analysis:\n\n"
            
            # Chair conditions
            analysis_text += "Chairs:\n"
            for condition, count in analysis.get('chairs', {}).items():
                analysis_text += f"  {condition}: {count}\n"
            
            # Locker conditions
            analysis_text += "\nLockers:\n"
            for condition, count in analysis.get('lockers', {}).items():
                analysis_text += f"  {condition}: {count}\n"
            
            # Overall conditions
            analysis_text += "\nOverall:\n"
            for condition, count in analysis.get('overall', {}).items():
                analysis_text += f"  {condition}: {count}\n"

            self.condition_display.setText(analysis_text)

        except Exception as e:
            show_error_message("Error", f"Failed to analyze conditions: {str(e)}", self)

    def _on_generate_inventory_report(self):
        """Handle generate inventory report button click."""
        try:
            report = self.furniture_service.generate_inventory_report()
            
            report_text = f"Furniture Inventory Report\n"
            report_text += f"Generated: {report.get('generated_at', '')}\n"
            report_text += f"Total Items: {report.get('total_items', 0)}\n\n"
            
            # Summary statistics
            summary = report.get('summary', {})
            report_text += "Summary:\n"
            report_text += f"  Total Chairs: {summary.get('total_chairs', 0)}\n"
            report_text += f"  Total Lockers: {summary.get('total_lockers', 0)}\n\n"
            
            # Locations
            report_text += "Inventory by Location:\n"
            for location, items in report.get('locations', {}).items():
                report_text += f"\n{location}:\n"
                report_text += f"  Chairs: {len(items.get('chairs', []))}\n"
                report_text += f"  Lockers: {len(items.get('lockers', []))}\n"

            self.inventory_display.setText(report_text)

        except Exception as e:
            show_error_message("Error", f"Failed to generate inventory report: {str(e)}", self)