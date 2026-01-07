"""
Teacher management window for the School System Management application.

This module provides the teacher management interface for admin users (admin and librarian roles).
Implements standardized, user-centric workflows for all teacher-related services with consistency,
validation, and system integrity following the TEACHER MANAGEMENT FLOW template.
"""

from PyQt6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QLabel, QLineEdit, QPushButton,
                            QHBoxLayout, QComboBox, QTabWidget, QTableWidget, QTableWidgetItem,
                            QTextEdit, QSizePolicy, QFileDialog, QMessageBox, QDialog, QMenu)
from PyQt6.QtCore import Qt, pyqtSignal, QTimer
from PyQt6.QtGui import QAction
from typing import Callable, Optional
from datetime import datetime

from school_system.gui.base.base_window import BaseWindow
from school_system.gui.dialogs.message_dialog import show_error_message, show_success_message
from school_system.gui.dialogs.confirm_dialog import ConfirmationDialog
from school_system.config.logging import logger
from school_system.services.teacher_service import TeacherService
from school_system.core.exceptions import DatabaseException, ValidationError
from school_system.gui.windows.teacher_validation import TeacherValidator, ValidationResult, FieldValidator
from school_system.gui.windows.teacher_workflow_components import (
    TeacherWorkflowManager, TeacherCreationWorkflow,
    TeacherUpdateWorkflow, TeacherDeletionWorkflow
)


class TeacherWindow(BaseWindow):
    """Teacher management window for admin users with standardized workflows."""

    def __init__(self, parent: QMainWindow, current_user: str, current_role: str):
        """
        Initialize the teacher window with standardized workflow management.

        Args:
            parent: The parent window
            current_user: The current logged-in username
            current_role: The current user's role
        """
        super().__init__("School System - Teacher Management", parent)

        self.parent = parent
        self.current_user = current_user
        self.current_role = current_role
        self.teacher_service = TeacherService()
        self.validator = TeacherValidator()
        
        # Initialize workflow manager
        self.workflow_manager = TeacherWorkflowManager(self)

        # Check if user has admin privileges
        if self.current_role not in ["admin", "librarian"]:
            show_error_message("Access Denied", "You do not have permission to access teacher management.", self)
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
        """Setup the teacher management widgets."""
        # Create tab widget for different sections
        tab_widget = QTabWidget()
        self.add_widget_to_content(tab_widget)

        # Teacher Management Tab
        teacher_tab = self._create_teacher_management_tab()
        tab_widget.addTab(teacher_tab, "Teacher Management")

        # Subject & Class Assignment Tab
        assignment_tab = self._create_assignment_tab()
        tab_widget.addTab(assignment_tab, "Subject & Class Assignment")

        # Performance & Qualifications Tab
        performance_tab = self._create_performance_tab()
        tab_widget.addTab(performance_tab, "Performance & Qualifications")

        # Notifications & Communication Tab
        notifications_tab = self._create_notifications_tab()
        tab_widget.addTab(notifications_tab, "Notifications & Communication")

        # Import/Export Tab
        import_export_tab = self._create_import_export_tab()
        tab_widget.addTab(import_export_tab, "Import/Export")

        # Reports & Analytics Tab
        reports_tab = self._create_reports_tab()
        tab_widget.addTab(reports_tab, "Reports & Analytics")

    def _setup_undo_system(self):
        """Setup the undo system for teacher operations."""
        # This will be implemented with proper undo functionality
        pass
    
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
                    teacher_id = last_operation['data']['teacher_id']
                    self.teacher_service.delete_teacher(teacher_id)
                    show_success_message("Undo Successful",
                                        f"Teacher creation undone: {teacher_id}", self)
                elif last_operation['type'] == 'delete':
                    # Undo delete by recreating
                    teacher_data = last_operation['data']
                    self.teacher_service.create_teacher(teacher_data)
                    show_success_message("Undo Successful",
                                        f"Teacher deletion undone: {teacher_data['teacher_id']}", self)
                elif last_operation['type'] == 'update':
                    # Undo update by reverting to old data
                    operation_data = last_operation['data']
                    teacher_id = operation_data['teacher_id']
                    old_data = operation_data['old_data']
                    
                    # Revert to old data
                    self.teacher_service.update_teacher(teacher_id, old_data)
                    show_success_message("Undo Successful",
                                        f"Teacher update undone: {teacher_id}", self)
                
                # Refresh table
                self._refresh_teachers_table()
                
                # Update undo action state
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
        self.undo_action.setEnabled(True)
        
        # Start undo timer (5 seconds)
        if self.undo_timer:
            self.undo_timer.stop()
        
        self.undo_timer = QTimer(self)
        self.undo_timer.timeout.connect(self._clear_undo_stack)
        self.undo_timer.start(5000)  # 5 seconds
        
        # Log the operation for audit purposes
        if operation_type == 'create':
            logger.info(f"Teacher created: {operation_data.get('teacher_id', 'Unknown')}")
        elif operation_type == 'update':
            logger.info(f"Teacher updated: {operation_data.get('teacher_id', 'Unknown')}")
        elif operation_type == 'delete':
            logger.info(f"Teacher deleted: {operation_data.get('teacher_id', 'Unknown')}")
    
    def _clear_undo_stack(self):
        """Clear the undo stack after timeout."""
        self.undo_stack.clear()
        if self.undo_action:
            self.undo_action.setEnabled(False)
        if self.undo_timer:
            self.undo_timer.stop()

    def _create_teacher_management_tab(self) -> QWidget:
        """Create the teacher management tab with standardized workflows."""
        tab = QWidget()
        layout = self.create_flex_layout("column", False)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.set_spacing(15)

        # Create Teacher Section - Using Standardized Workflow
        create_section = self.create_card("Create New Teacher",
                                        "Use the form below to create a new teacher record")
        create_workflow = TeacherCreationWorkflow(self)
        create_workflow.operation_completed.connect(self._handle_operation_completed)
        create_section.layout.addWidget(create_workflow)
        layout.add_widget(create_section)

        # Update Teacher Section - Using Standardized Workflow
        update_section = self.create_card("Update Teacher",
                                        "Update existing teacher information")
        update_workflow = TeacherUpdateWorkflow(self)
        update_workflow.operation_completed.connect(self._handle_operation_completed)
        update_section.layout.addWidget(update_workflow)
        layout.add_widget(update_section)

        # Delete Teacher Section - Using Standardized Workflow
        delete_section = self.create_card("Delete Teacher",
                                        "Permanently remove a teacher from the system")
        delete_workflow = TeacherDeletionWorkflow(self)
        delete_workflow.operation_completed.connect(self._handle_operation_completed)
        delete_section.layout.addWidget(delete_workflow)
        layout.add_widget(delete_section)

        # View Teachers Section
        view_section = self.create_card("View Teachers", "Browse and search existing teacher records")
        view_form = QWidget()
        view_layout = self.create_flex_layout("column", False)
        view_layout.set_spacing(10)

        # Search box with real-time validation
        self.search_box = self.create_search_box("Search teachers...")
        self.search_box.search_text_changed.connect(self._on_search_teachers)
        view_layout.add_widget(self.search_box)

        # Refresh button
        refresh_button = self.create_button("Refresh Teachers", "secondary")
        refresh_button.clicked.connect(self._refresh_teachers_table)
        view_layout.add_widget(refresh_button)

        # Teachers table with enhanced features
        self.teachers_table = self.create_table(0, 5)  # Added column for undo
        self.teachers_table.setHorizontalHeaderLabels(["Teacher ID", "Name", "Department", "Actions", ""])
        view_layout.add_widget(self.teachers_table)

        view_form.setLayout(view_layout._layout)
        view_section.layout.addWidget(view_form)
        layout.add_widget(view_section)

        tab.setLayout(layout._layout)
        return tab

    def _create_assignment_tab(self) -> QWidget:
        """Create the subject and class assignment tab."""
        tab = QWidget()
        layout = self.create_flex_layout("column", False)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.set_spacing(15)

        # Assign Subject Section
        subject_section = self.create_card("Assign Subject to Teacher", "")
        subject_form = QWidget()
        subject_layout = self.create_flex_layout("column", False)
        subject_layout.set_spacing(10)

        # Teacher ID
        subject_teacher_id_label = QLabel("Teacher ID:")
        subject_layout.add_widget(subject_teacher_id_label)
        self.assign_subject_teacher_id_input = self.create_input("Enter teacher ID")
        subject_layout.add_widget(self.assign_subject_teacher_id_input)

        # Subject ID
        subject_id_label = QLabel("Subject ID:")
        subject_layout.add_widget(subject_id_label)
        self.assign_subject_id_input = self.create_input("Enter subject ID")
        subject_layout.add_widget(self.assign_subject_id_input)

        # Assign subject button
        assign_subject_button = self.create_button("Assign Subject", "primary")
        assign_subject_button.clicked.connect(self._on_assign_subject)
        subject_layout.add_widget(assign_subject_button)

        subject_form.setLayout(subject_layout._layout)
        subject_section.layout.addWidget(subject_form)
        layout.add_widget(subject_section)

        # Assign Class Section
        class_section = self.create_card("Assign Class to Teacher", "")
        class_form = QWidget()
        class_layout = self.create_flex_layout("column", False)
        class_layout.set_spacing(10)

        # Teacher ID
        class_teacher_id_label = QLabel("Teacher ID:")
        class_layout.add_widget(class_teacher_id_label)
        self.assign_class_teacher_id_input = self.create_input("Enter teacher ID")
        class_layout.add_widget(self.assign_class_teacher_id_input)

        # Class ID
        class_id_label = QLabel("Class ID:")
        class_layout.add_widget(class_id_label)
        self.assign_class_id_input = self.create_input("Enter class ID")
        class_layout.add_widget(self.assign_class_id_input)

        # Assign class button
        assign_class_button = self.create_button("Assign Class", "secondary")
        assign_class_button.clicked.connect(self._on_assign_class)
        class_layout.add_widget(assign_class_button)

        class_form.setLayout(class_layout._layout)
        class_section.layout.addWidget(class_form)
        layout.add_widget(class_section)

        # Update Availability Section
        availability_section = self.create_card("Update Teacher Availability", "")
        availability_form = QWidget()
        availability_layout = self.create_flex_layout("column", False)
        availability_layout.set_spacing(10)

        # Teacher ID
        availability_teacher_id_label = QLabel("Teacher ID:")
        availability_layout.add_widget(availability_teacher_id_label)
        self.update_availability_teacher_id_input = self.create_input("Enter teacher ID")
        availability_layout.add_widget(self.update_availability_teacher_id_input)

        # Availability Days
        availability_days_label = QLabel("Availability Days (comma separated):")
        availability_layout.add_widget(availability_days_label)
        self.update_availability_days_input = self.create_input("e.g., Mon,Wed,Fri")
        availability_layout.add_widget(self.update_availability_days_input)

        # Availability Hours
        availability_hours_label = QLabel("Availability Hours:")
        availability_layout.add_widget(availability_hours_label)
        self.update_availability_hours_input = self.create_input("e.g., 8:00-16:00")
        availability_layout.add_widget(self.update_availability_hours_input)

        # Update availability button
        update_availability_button = self.create_button("Update Availability", "primary")
        update_availability_button.clicked.connect(self._on_update_availability)
        availability_layout.add_widget(update_availability_button)

        availability_form.setLayout(availability_layout._layout)
        availability_section.layout.addWidget(availability_form)
        layout.add_widget(availability_section)

        tab.setLayout(layout._layout)
        return tab

    def _create_performance_tab(self) -> QWidget:
        """Create the performance and qualifications tab."""
        tab = QWidget()
        layout = self.create_flex_layout("column", False)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.set_spacing(15)

        # Add Performance Record Section
        performance_section = self.create_card("Add Performance Record", "")
        performance_form = QWidget()
        performance_layout = self.create_flex_layout("column", False)
        performance_layout.set_spacing(10)

        # Teacher ID
        performance_teacher_id_label = QLabel("Teacher ID:")
        performance_layout.add_widget(performance_teacher_id_label)
        self.add_performance_teacher_id_input = self.create_input("Enter teacher ID")
        performance_layout.add_widget(self.add_performance_teacher_id_input)

        # Performance Date
        performance_date_label = QLabel("Performance Date (YYYY-MM-DD):")
        performance_layout.add_widget(performance_date_label)
        self.add_performance_date_input = self.create_input("Enter date")
        performance_layout.add_widget(self.add_performance_date_input)

        # Performance Score
        performance_score_label = QLabel("Performance Score (1-100):")
        performance_layout.add_widget(performance_score_label)
        self.add_performance_score_input = self.create_input("Enter score")
        performance_layout.add_widget(self.add_performance_score_input)

        # Performance Notes
        performance_notes_label = QLabel("Performance Notes:")
        performance_layout.add_widget(performance_notes_label)
        self.add_performance_notes_input = self.create_input("Enter notes")
        performance_layout.add_widget(self.add_performance_notes_input)

        # Add performance button
        add_performance_button = self.create_button("Add Performance Record", "primary")
        add_performance_button.clicked.connect(self._on_add_performance_record)
        performance_layout.add_widget(add_performance_button)

        performance_form.setLayout(performance_layout._layout)
        performance_section.layout.addWidget(performance_form)
        layout.add_widget(performance_section)

        # Validate Qualifications Section
        qualifications_section = self.create_card("Validate Teacher Qualifications", "")
        qualifications_form = QWidget()
        qualifications_layout = self.create_flex_layout("column", False)
        qualifications_layout.set_spacing(10)

        # Teacher ID
        qualifications_teacher_id_label = QLabel("Teacher ID:")
        qualifications_layout.add_widget(qualifications_teacher_id_label)
        self.validate_qualifications_teacher_id_input = self.create_input("Enter teacher ID")
        qualifications_layout.add_widget(self.validate_qualifications_teacher_id_input)

        # Qualifications (comma separated)
        qualifications_label = QLabel("Qualifications (comma separated):")
        qualifications_layout.add_widget(qualifications_label)
        self.validate_qualifications_input = self.create_input("e.g., B.Ed, M.Ed, PhD")
        qualifications_layout.add_widget(self.validate_qualifications_input)

        # Validate qualifications button
        validate_qualifications_button = self.create_button("Validate Qualifications", "secondary")
        validate_qualifications_button.clicked.connect(self._on_validate_qualifications)
        qualifications_layout.add_widget(validate_qualifications_button)

        qualifications_form.setLayout(qualifications_layout._layout)
        qualifications_section.layout.addWidget(qualifications_form)
        layout.add_widget(qualifications_section)

        # View Performance Records Section
        view_performance_section = self.create_card("View Performance Records", "")
        view_performance_form = QWidget()
        view_performance_layout = self.create_flex_layout("column", False)
        view_performance_layout.set_spacing(10)

        # Teacher ID
        view_performance_teacher_id_label = QLabel("Teacher ID:")
        view_performance_layout.add_widget(view_performance_teacher_id_label)
        self.view_performance_teacher_id_input = self.create_input("Enter teacher ID")
        view_performance_layout.add_widget(self.view_performance_teacher_id_input)

        # View performance button
        view_performance_button = self.create_button("View Performance Records", "primary")
        view_performance_button.clicked.connect(self._on_view_performance_records)
        view_performance_layout.add_widget(view_performance_button)

        # Performance records display
        self.performance_records_display = QTextEdit()
        self.performance_records_display.setReadOnly(True)
        self.performance_records_display.setMaximumHeight(200)
        view_performance_layout.add_widget(self.performance_records_display)

        view_performance_form.setLayout(view_performance_layout._layout)
        view_performance_section.layout.addWidget(view_performance_form)
        layout.add_widget(view_performance_section)

        tab.setLayout(layout._layout)
        return tab

    def _create_notifications_tab(self) -> QWidget:
        """Create the notifications and communication tab."""
        tab = QWidget()
        layout = self.create_flex_layout("column", False)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.set_spacing(15)

        # Send Notification Section
        notification_section = self.create_card("Send Notification to Teacher", "")
        notification_form = QWidget()
        notification_layout = self.create_flex_layout("column", False)
        notification_layout.set_spacing(10)

        # Teacher ID
        notification_teacher_id_label = QLabel("Teacher ID:")
        notification_layout.add_widget(notification_teacher_id_label)
        self.send_notification_teacher_id_input = self.create_input("Enter teacher ID")
        notification_layout.add_widget(self.send_notification_teacher_id_input)

        # Notification Message
        notification_message_label = QLabel("Notification Message:")
        notification_layout.add_widget(notification_message_label)
        self.send_notification_message_input = QTextEdit()
        self.send_notification_message_input.setMaximumHeight(100)
        notification_layout.add_widget(self.send_notification_message_input)

        # Send notification button
        send_notification_button = self.create_button("Send Notification", "primary")
        send_notification_button.clicked.connect(self._on_send_notification)
        notification_layout.add_widget(send_notification_button)

        notification_form.setLayout(notification_layout._layout)
        notification_section.layout.addWidget(notification_form)
        layout.add_widget(notification_section)

        # View Teacher Statistics Section
        statistics_section = self.create_card("View Teacher Statistics", "")
        statistics_form = QWidget()
        statistics_layout = self.create_flex_layout("column", False)
        statistics_layout.set_spacing(10)

        # Teacher ID
        statistics_teacher_id_label = QLabel("Teacher ID:")
        statistics_layout.add_widget(statistics_teacher_id_label)
        self.view_statistics_teacher_id_input = self.create_input("Enter teacher ID")
        statistics_layout.add_widget(self.view_statistics_teacher_id_input)

        # View statistics button
        view_statistics_button = self.create_button("View Statistics", "secondary")
        view_statistics_button.clicked.connect(self._on_view_teacher_statistics)
        statistics_layout.add_widget(view_statistics_button)

        # Statistics display
        self.statistics_display = QTextEdit()
        self.statistics_display.setReadOnly(True)
        self.statistics_display.setMaximumHeight(200)
        statistics_layout.add_widget(self.statistics_display)

        statistics_form.setLayout(statistics_layout._layout)
        statistics_section.layout.addWidget(statistics_form)
        layout.add_widget(statistics_section)

        # View Notifications Section
        view_notifications_section = self.create_card("View Teacher Notifications", "")
        view_notifications_form = QWidget()
        view_notifications_layout = self.create_flex_layout("column", False)
        view_notifications_layout.set_spacing(10)

        # Teacher ID
        view_notifications_teacher_id_label = QLabel("Teacher ID:")
        view_notifications_layout.add_widget(view_notifications_teacher_id_label)
        self.view_notifications_teacher_id_input = self.create_input("Enter teacher ID")
        view_notifications_layout.add_widget(self.view_notifications_teacher_id_input)

        # View notifications button
        view_notifications_button = self.create_button("View Notifications", "primary")
        view_notifications_button.clicked.connect(self._on_view_notifications)
        view_notifications_layout.add_widget(view_notifications_button)

        # Notifications display
        self.notifications_display = QTextEdit()
        self.notifications_display.setReadOnly(True)
        self.notifications_display.setMaximumHeight(200)
        view_notifications_layout.add_widget(self.notifications_display)

        view_notifications_form.setLayout(view_notifications_layout._layout)
        view_notifications_section.layout.addWidget(view_notifications_form)
        layout.add_widget(view_notifications_section)

        tab.setLayout(layout._layout)
        return tab

    def _create_import_export_tab(self) -> QWidget:
        """Create the import/export tab."""
        tab = QWidget()
        layout = self.create_flex_layout("column", False)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.set_spacing(15)

        # Import Teachers Section
        import_section = self.create_card("Import Teachers from Excel", "")
        import_form = QWidget()
        import_layout = self.create_flex_layout("column", False)
        import_layout.set_spacing(10)

        # File selection
        self.import_file_label = QLabel("No file selected")
        import_layout.add_widget(self.import_file_label)

        # Browse button
        browse_button = self.create_button("Browse Excel File", "primary")
        browse_button.clicked.connect(self._on_browse_import_file)
        import_layout.add_widget(browse_button)

        # Import button
        import_button = self.create_button("Import Teachers", "secondary")
        import_button.clicked.connect(self._on_import_teachers)
        import_layout.add_widget(import_button)

        import_form.setLayout(import_layout._layout)
        import_section.layout.addWidget(import_form)
        layout.add_widget(import_section)

        # Export Teachers Section
        export_section = self.create_card("Export Teachers to Excel", "")
        export_form = QWidget()
        export_layout = self.create_flex_layout("column", False)
        export_layout.set_spacing(10)

        # Export button
        export_button = self.create_button("Export All Teachers", "primary")
        export_button.clicked.connect(self._on_export_teachers)
        export_layout.add_widget(export_button)

        export_form.setLayout(export_layout._layout)
        export_section.layout.addWidget(export_form)
        layout.add_widget(export_section)

        tab.setLayout(layout._layout)
        return tab

    def _create_reports_tab(self) -> QWidget:
        """Create the reports and analytics tab."""
        tab = QWidget()
        layout = self.create_flex_layout("column", False)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.set_spacing(15)

        # Teacher Summary Section
        summary_section = self.create_card("Teacher Summary Report", "")
        summary_form = QWidget()
        summary_layout = self.create_flex_layout("column", False)
        summary_layout.set_spacing(10)

        # Teacher ID
        summary_teacher_id_label = QLabel("Teacher ID:")
        summary_layout.add_widget(summary_teacher_id_label)
        self.summary_teacher_id_input = self.create_input("Enter teacher ID")
        summary_layout.add_widget(self.summary_teacher_id_input)

        # Generate summary button
        generate_summary_button = self.create_button("Generate Summary", "primary")
        generate_summary_button.clicked.connect(self._on_generate_teacher_summary)
        summary_layout.add_widget(generate_summary_button)

        # Summary results display
        self.summary_results_display = QTextEdit()
        self.summary_results_display.setReadOnly(True)
        self.summary_results_display.setMaximumHeight(200)
        summary_layout.add_widget(self.summary_results_display)

        summary_form.setLayout(summary_layout._layout)
        summary_section.layout.addWidget(summary_form)
        layout.add_widget(summary_section)

        # Department Analysis Section
        department_section = self.create_card("Department Analysis Report", "")
        department_form = QWidget()
        department_layout = self.create_flex_layout("column", False)
        department_layout.set_spacing(10)

        # Department
        department_label = QLabel("Department:")
        department_layout.add_widget(department_label)
        self.department_analysis_department_input = self.create_input("Enter department name")
        department_layout.add_widget(self.department_analysis_department_input)

        # Generate department analysis button
        generate_department_button = self.create_button("Generate Department Analysis", "secondary")
        generate_department_button.clicked.connect(self._on_generate_department_analysis)
        department_layout.add_widget(generate_department_button)

        # Department analysis results display
        self.department_analysis_results_display = QTextEdit()
        self.department_analysis_results_display.setReadOnly(True)
        self.department_analysis_results_display.setMaximumHeight(200)
        department_layout.add_widget(self.department_analysis_results_display)

        department_form.setLayout(department_layout._layout)
        department_section.layout.addWidget(department_form)
        layout.add_widget(department_section)

        # Performance Trends Section
        performance_section = self.create_card("Performance Trends Report", "")
        performance_form = QWidget()
        performance_layout = self.create_flex_layout("column", False)
        performance_layout.set_spacing(10)

        # Teacher ID
        performance_teacher_id_label = QLabel("Teacher ID:")
        performance_layout.add_widget(performance_teacher_id_label)
        self.performance_trends_teacher_id_input = self.create_input("Enter teacher ID")
        performance_layout.add_widget(self.performance_trends_teacher_id_input)

        # Generate performance trends button
        generate_performance_button = self.create_button("Generate Performance Trends", "primary")
        generate_performance_button.clicked.connect(self._on_generate_performance_trends)
        performance_layout.add_widget(generate_performance_button)

        # Performance trends results display
        self.performance_trends_results_display = QTextEdit()
        self.performance_trends_results_display.setReadOnly(True)
        self.performance_trends_results_display.setMaximumHeight(200)
        performance_layout.add_widget(self.performance_trends_results_display)

        performance_form.setLayout(performance_layout._layout)
        performance_section.layout.addWidget(performance_form)
        layout.add_widget(performance_section)

        tab.setLayout(layout._layout)
        return tab

    # Event handlers for Teacher Management
    def _handle_operation_completed(self, success: bool, message: str):
        """
        Handle completion of teacher operations with appropriate feedback and state updates.
        
        This method serves as the central callback for all teacher workflow operations,
        ensuring consistent post-operation behavior including table refreshes,
        user notifications, and undo tracking.
        
        Args:
            success: Boolean indicating if the operation was successful
            message: Descriptive message about the operation result
        """
        if success:
            # Refresh the teachers table to show latest data
            self._refresh_teachers_table()
            
            # Show appropriate success message based on operation type
            if "created" in message.lower():
                show_success_message("Success", message, self)
                # Track creation for potential undo (5-second window)
                # Teacher ID can be extracted from message for undo tracking
            elif "updated" in message.lower():
                show_success_message("Success", message, self)
                # Track update for potential undo
            elif "deleted" in message.lower():
                show_success_message("Success", message, self)
                # Track deletion for potential undo
        else:
            # Show error message for failed operations
            show_error_message("Error", message, self)

    def _refresh_teachers_table(self):
        """Refresh the teachers table."""
        try:
            teachers = self.teacher_service.get_all_teachers()
            self._populate_teachers_table(teachers)
        except Exception as e:
            show_error_message("Error", f"Failed to refresh teachers: {str(e)}", self)

    def _populate_teachers_table(self, teachers):
        """Populate the teachers table with data and enhanced features."""
        self.teachers_table.setRowCount(0)

        for teacher in teachers:
            row_position = self.teachers_table.rowCount()
            self.teachers_table.insertRow(row_position)

            self.teachers_table.setItem(row_position, 0, QTableWidgetItem(str(teacher.teacher_id)))
            self.teachers_table.setItem(row_position, 1, QTableWidgetItem(teacher.teacher_name))
            self.teachers_table.setItem(row_position, 2, QTableWidgetItem(getattr(teacher, 'department', '')))

            # Add action buttons container
            action_widget = QWidget()
            action_layout = QHBoxLayout(action_widget)
            action_layout.setContentsMargins(0, 0, 0, 0)
            action_layout.setSpacing(5)

            # View button
            view_button = self.create_button("View", "secondary")
            view_button.clicked.connect(lambda _, tid=teacher.teacher_id: self._view_teacher_details(tid))
            action_layout.addWidget(view_button)

            # Edit button
            edit_button = self.create_button("Edit", "primary")
            edit_button.clicked.connect(lambda _, tid=teacher.teacher_id: self._start_edit_workflow(tid))
            action_layout.addWidget(edit_button)

            # Delete button
            delete_button = self.create_button("Delete", "danger")
            delete_button.clicked.connect(lambda _, tid=teacher.teacher_id: self._start_delete_workflow(tid))
            action_layout.addWidget(delete_button)

            self.teachers_table.setCellWidget(row_position, 3, action_widget)
            
            # Add undo placeholder (will be populated if undo is available)
            undo_button = self.create_button("Undo", "secondary")
            undo_button.setVisible(False)  # Initially hidden
            self.teachers_table.setCellWidget(row_position, 4, undo_button)

    def _start_edit_workflow(self, teacher_id: str):
        """Start the edit workflow for a specific teacher."""
        try:
            teacher = self.teacher_service.get_teacher_by_id(teacher_id)
            if teacher:
                # Create update workflow and pre-populate with teacher data
                update_workflow = TeacherUpdateWorkflow(self)
                update_workflow.operation_completed.connect(self._handle_operation_completed)
                
                # Pre-populate the teacher ID field
                if hasattr(update_workflow, 'teacher_id_input'):
                    update_workflow.teacher_id_input.setText(teacher.teacher_id)
                    update_workflow.teacher_id_input.setReadOnly(True)
                
                # Show the workflow
                self.workflow_manager.start_workflow("update")
                
            else:
                show_error_message("Error", "Teacher not found", self)
        except Exception as e:
            show_error_message("Error", f"Failed to start edit workflow: {str(e)}", self)

    def _start_delete_workflow(self, teacher_id: str):
        """Start the delete workflow for a specific teacher."""
        try:
            teacher = self.teacher_service.get_teacher_by_id(teacher_id)
            if teacher:
                # Create delete workflow and pre-populate with teacher data
                delete_workflow = TeacherDeletionWorkflow(self)
                delete_workflow.operation_completed.connect(self._handle_operation_completed)
                
                # Pre-populate the teacher ID field
                if hasattr(delete_workflow, 'teacher_id_input'):
                    delete_workflow.teacher_id_input.setText(teacher.teacher_id)
                    delete_workflow.teacher_id_input.setReadOnly(True)
                
                # Show the workflow
                self.workflow_manager.start_workflow("delete")
                
            else:
                show_error_message("Error", "Teacher not found", self)
        except Exception as e:
            show_error_message("Error", f"Failed to start delete workflow: {str(e)}", self)

    def _view_teacher_details(self, teacher_id: str):
        """View detailed information about a teacher."""
        try:
            teacher = self.teacher_service.get_teacher_by_id(teacher_id)
            if teacher:
                details = f"Teacher Details:\n\nID: {teacher.teacher_id}\nName: {teacher.teacher_name}\nDepartment: {getattr(teacher, 'department', 'N/A')}"
                show_success_message("Teacher Details", details, self)
            else:
                show_error_message("Error", "Teacher not found", self)
        except Exception as e:
            show_error_message("Error", f"Failed to view teacher details: {str(e)}", self)

    def _on_search_teachers(self, query: str):
        """Handle teacher search."""
        try:
            # For now, just refresh the table (search functionality would need to be implemented in service)
            self._refresh_teachers_table()
        except Exception as e:
            show_error_message("Error", f"Search failed: {str(e)}", self)

    # Event handlers for Subject & Class Assignment
    def _on_assign_subject(self):
        """Handle assign subject button click."""
        try:
            teacher_id = self.assign_subject_teacher_id_input.text().strip()
            subject_id = self.assign_subject_id_input.text().strip()

            if not teacher_id or not subject_id:
                show_error_message("Validation Error", "Teacher ID and Subject ID are required", self)
                return

            success = self.teacher_service.assign_subject_to_teacher(teacher_id, subject_id)
            if success:
                show_success_message("Success", f"Subject {subject_id} assigned to teacher {teacher_id}", self)
                # Clear form
                self.assign_subject_teacher_id_input.clear()
                self.assign_subject_id_input.clear()
            else:
                show_error_message("Error", "Failed to assign subject", self)

        except Exception as e:
            show_error_message("Error", f"An error occurred: {str(e)}", self)

    def _on_assign_class(self):
        """Handle assign class button click."""
        try:
            teacher_id = self.assign_class_teacher_id_input.text().strip()
            class_id = self.assign_class_id_input.text().strip()

            if not teacher_id or not class_id:
                show_error_message("Validation Error", "Teacher ID and Class ID are required", self)
                return

            success = self.teacher_service.assign_class_to_teacher(teacher_id, class_id)
            if success:
                show_success_message("Success", f"Class {class_id} assigned to teacher {teacher_id}", self)
                # Clear form
                self.assign_class_teacher_id_input.clear()
                self.assign_class_id_input.clear()
            else:
                show_error_message("Error", "Failed to assign class", self)

        except Exception as e:
            show_error_message("Error", f"An error occurred: {str(e)}", self)

    def _on_update_availability(self):
        """Handle update availability button click."""
        try:
            teacher_id = self.update_availability_teacher_id_input.text().strip()
            days = self.update_availability_days_input.text().strip()
            hours = self.update_availability_hours_input.text().strip()

            if not teacher_id or not days or not hours:
                show_error_message("Validation Error", "Teacher ID, Days, and Hours are required", self)
                return

            availability_data = {
                'days': days,
                'hours': hours
            }

            success = self.teacher_service.update_teacher_availability(teacher_id, availability_data)
            if success:
                show_success_message("Success", f"Availability updated for teacher {teacher_id}", self)
                # Clear form
                self.update_availability_teacher_id_input.clear()
                self.update_availability_days_input.clear()
                self.update_availability_hours_input.clear()
            else:
                show_error_message("Error", "Failed to update availability", self)

        except Exception as e:
            show_error_message("Error", f"An error occurred: {str(e)}", self)

    # Event handlers for Performance & Qualifications
    def _on_add_performance_record(self):
        """Handle add performance record button click."""
        try:
            teacher_id = self.add_performance_teacher_id_input.text().strip()
            date = self.add_performance_date_input.text().strip()
            score = self.add_performance_score_input.text().strip()
            notes = self.add_performance_notes_input.text().strip()

            if not teacher_id or not date or not score:
                show_error_message("Validation Error", "Teacher ID, Date, and Score are required", self)
                return

            performance_data = {
                'date': date,
                'score': int(score),
                'notes': notes
            }

            success = self.teacher_service.add_teacher_performance_record(teacher_id, performance_data)
            if success:
                show_success_message("Success", f"Performance record added for teacher {teacher_id}", self)
                # Clear form
                self.add_performance_teacher_id_input.clear()
                self.add_performance_date_input.clear()
                self.add_performance_score_input.clear()
                self.add_performance_notes_input.clear()
            else:
                show_error_message("Error", "Failed to add performance record", self)

        except ValueError:
            show_error_message("Error", "Invalid score value", self)
        except Exception as e:
            show_error_message("Error", f"An error occurred: {str(e)}", self)

    def _on_validate_qualifications(self):
        """Handle validate qualifications button click."""
        try:
            teacher_id = self.validate_qualifications_teacher_id_input.text().strip()
            qualifications_text = self.validate_qualifications_input.text().strip()

            if not teacher_id or not qualifications_text:
                show_error_message("Validation Error", "Teacher ID and Qualifications are required", self)
                return

            qualifications = [q.strip() for q in qualifications_text.split(',')]

            success = self.teacher_service.validate_teacher_qualifications(teacher_id, qualifications)
            if success:
                show_success_message("Success", f"Qualifications validated for teacher {teacher_id}", self)
                # Clear form
                self.validate_qualifications_teacher_id_input.clear()
                self.validate_qualifications_input.clear()
            else:
                show_error_message("Error", "Failed to validate qualifications", self)

        except Exception as e:
            show_error_message("Error", f"An error occurred: {str(e)}", self)

    def _on_view_performance_records(self):
        """Handle view performance records button click."""
        try:
            teacher_id = self.view_performance_teacher_id_input.text().strip()

            if not teacher_id:
                show_error_message("Validation Error", "Teacher ID is required", self)
                return

            teacher = self.teacher_service.get_teacher_by_id(teacher_id)
            if not teacher:
                show_error_message("Error", "Teacher not found", self)
                return

            # Get performance records
            records = getattr(teacher, 'performance_records', [])
            if records:
                records_text = f"Performance Records for Teacher {teacher_id}:\n\n"
                for i, record in enumerate(records, 1):
                    records_text += f"Record {i}:\n"
                    records_text += f"  Date: {record.get('date', 'N/A')}\n"
                    records_text += f"  Score: {record.get('score', 'N/A')}\n"
                    records_text += f"  Notes: {record.get('notes', 'N/A')}\n\n"
                self.performance_records_display.setText(records_text)
            else:
                self.performance_records_display.setText(f"No performance records found for teacher {teacher_id}")

        except Exception as e:
            show_error_message("Error", f"An error occurred: {str(e)}", self)

    # Event handlers for Notifications & Communication
    def _on_send_notification(self):
        """Handle send notification button click."""
        try:
            teacher_id = self.send_notification_teacher_id_input.text().strip()
            message = self.send_notification_message_input.toPlainText().strip()

            if not teacher_id or not message:
                show_error_message("Validation Error", "Teacher ID and Message are required", self)
                return

            success = self.teacher_service.send_teacher_notification(teacher_id, message)
            if success:
                show_success_message("Success", f"Notification sent to teacher {teacher_id}", self)
                # Clear form
                self.send_notification_teacher_id_input.clear()
                self.send_notification_message_input.clear()
            else:
                show_error_message("Error", "Failed to send notification", self)

        except Exception as e:
            show_error_message("Error", f"An error occurred: {str(e)}", self)

    def _on_view_teacher_statistics(self):
        """Handle view teacher statistics button click."""
        try:
            teacher_id = self.view_statistics_teacher_id_input.text().strip()

            if not teacher_id:
                show_error_message("Validation Error", "Teacher ID is required", self)
                return

            stats = self.teacher_service.get_teacher_statistics(teacher_id)
            if stats:
                stats_text = f"Teacher Statistics for {teacher_id}:\n\n"
                stats_text += f"Teacher Name: {stats.get('teacher_name', 'N/A')}\n"
                stats_text += f"Subjects Taught: {stats.get('subjects_taught', 0)}\n"
                stats_text += f"Classes Assigned: {stats.get('classes_assigned', 0)}\n"
                stats_text += f"Performance Records: {stats.get('performance_records', 0)}\n"
                stats_text += f"Qualifications: {stats.get('qualifications', 0)}\n"
                self.statistics_display.setText(stats_text)
            else:
                show_error_message("Error", "Teacher not found", self)

        except Exception as e:
            show_error_message("Error", f"An error occurred: {str(e)}", self)

    def _on_view_notifications(self):
        """Handle view notifications button click."""
        try:
            teacher_id = self.view_notifications_teacher_id_input.text().strip()

            if not teacher_id:
                show_error_message("Validation Error", "Teacher ID is required", self)
                return

            teacher = self.teacher_service.get_teacher_by_id(teacher_id)
            if not teacher:
                show_error_message("Error", "Teacher not found", self)
                return

            # Get notifications
            notifications = getattr(teacher, 'notifications', [])
            if notifications:
                notifications_text = f"Notifications for Teacher {teacher_id}:\n\n"
                for i, notification in enumerate(notifications, 1):
                    notifications_text += f"Notification {i}:\n"
                    notifications_text += f"  Message: {notification.get('message', 'N/A')}\n"
                    notifications_text += f"  Timestamp: {notification.get('timestamp', 'N/A')}\n"
                    notifications_text += f"  Status: {'Read' if notification.get('read', False) else 'Unread'}\n\n"
                self.notifications_display.setText(notifications_text)
            else:
                self.notifications_display.setText(f"No notifications found for teacher {teacher_id}")

        except Exception as e:
            show_error_message("Error", f"An error occurred: {str(e)}", self)

    # Event handlers for Import/Export
    def _on_browse_import_file(self):
        """Handle browse import file button click."""
        file_dialog = QFileDialog()
        file_path, _ = file_dialog.getOpenFileName(self, "Select Excel File", "", "Excel Files (*.xlsx *.xls)")

        if file_path:
            self.import_file_label.setText(file_path)
            self.import_file_path = file_path

    def _on_import_teachers(self):
        """Handle import teachers button click."""
        try:
            if not hasattr(self, 'import_file_path'):
                show_error_message("Error", "Please select a file first", self)
                return

            teachers = self.teacher_service.import_teachers_from_excel(self.import_file_path)
            show_success_message("Success", f"Imported {len(teachers)} teachers successfully", self)
            self._refresh_teachers_table()

        except Exception as e:
            show_error_message("Error", f"Import failed: {str(e)}", self)

    def _on_export_teachers(self):
        """Handle export teachers button click."""
        try:
            file_dialog = QFileDialog()
            file_path, _ = file_dialog.getSaveFileName(self, "Save Excel File", "teachers_export.xlsx", "Excel Files (*.xlsx)")

            if file_path:
                success = self.teacher_service.export_teachers_to_excel(file_path)
                if success:
                    show_success_message("Success", "Teachers exported successfully", self)
                else:
                    show_error_message("Error", "Export failed", self)

        except Exception as e:
            show_error_message("Error", f"Export failed: {str(e)}", self)

    # Event handlers for Reports & Analytics
    def _on_generate_teacher_summary(self):
        """Handle generate teacher summary button click."""
        try:
            teacher_id = self.summary_teacher_id_input.text().strip()

            if not teacher_id:
                show_error_message("Validation Error", "Teacher ID is required", self)
                return

            # Get teacher summary data
            teacher = self.teacher_service.get_teacher_by_id(teacher_id)
            if not teacher:
                show_error_message("Error", "Teacher not found", self)
                return

            # Get statistics
            stats = self.teacher_service.get_teacher_statistics(teacher_id)

            # Generate summary report
            report_text = f"Teacher Summary Report for {teacher.teacher_name} (ID: {teacher.teacher_id})\n\n"
            report_text += f"Department: {getattr(teacher, 'department', 'N/A')}\n\n"
            report_text += "Teaching Statistics:\n"
            report_text += f"  Subjects Taught: {stats.get('subjects_taught', 0)}\n"
            report_text += f"  Classes Assigned: {stats.get('classes_assigned', 0)}\n\n"
            report_text += "Performance Statistics:\n"
            report_text += f"  Performance Records: {stats.get('performance_records', 0)}\n"
            report_text += f"  Qualifications: {stats.get('qualifications', 0)}\n"

            self.summary_results_display.setText(report_text)

        except Exception as e:
            show_error_message("Error", f"Failed to generate report: {str(e)}", self)

    def _on_generate_department_analysis(self):
        """Handle generate department analysis button click."""
        try:
            department = self.department_analysis_department_input.text().strip()

            if not department:
                show_error_message("Validation Error", "Department name is required", self)
                return

            # Get all teachers in department
            all_teachers = self.teacher_service.get_all_teachers()
            department_teachers = [t for t in all_teachers if getattr(t, 'department', '') == department]

            # Generate department analysis report
            report_text = f"Department Analysis Report for {department}\n\n"
            report_text += f"Total Teachers: {len(department_teachers)}\n"

            # Calculate statistics
            total_subjects = 0
            total_classes = 0
            for teacher in department_teachers:
                stats = self.teacher_service.get_teacher_statistics(teacher.teacher_id)
                total_subjects += stats.get('subjects_taught', 0)
                total_classes += stats.get('classes_assigned', 0)

            report_text += f"Total Subjects Taught: {total_subjects}\n"
            report_text += f"Total Classes Assigned: {total_classes}\n"
            report_text += f"Average Subjects per Teacher: {total_subjects / len(department_teachers) if department_teachers else 0:.2f}\n"
            report_text += f"Average Classes per Teacher: {total_classes / len(department_teachers) if department_teachers else 0:.2f}\n"

            self.department_analysis_results_display.setText(report_text)

        except Exception as e:
            show_error_message("Error", f"Failed to generate report: {str(e)}", self)

    def _on_generate_performance_trends(self):
        """Handle generate performance trends button click."""
        try:
            teacher_id = self.performance_trends_teacher_id_input.text().strip()

            if not teacher_id:
                show_error_message("Validation Error", "Teacher ID is required", self)
                return

            teacher = self.teacher_service.get_teacher_by_id(teacher_id)
            if not teacher:
                show_error_message("Error", "Teacher not found", self)
                return

            # Get performance records
            records = getattr(teacher, 'performance_records', [])

            if records:
                # Calculate trends
                total_score = sum(record.get('score', 0) for record in records)
                avg_score = total_score / len(records)
                
                # Find highest and lowest scores
                highest_score = max(record.get('score', 0) for record in records)
                lowest_score = min(record.get('score', 0) for record in records)

                report_text = f"Performance Trends Report for Teacher {teacher_id}\n\n"
                report_text += f"Total Performance Records: {len(records)}\n"
                report_text += f"Average Performance Score: {avg_score:.2f}\n"
                report_text += f"Highest Score: {highest_score}\n"
                report_text += f"Lowest Score: {lowest_score}\n"
                report_text += f"Performance Trend: {'Improving' if records[-1].get('score', 0) > records[0].get('score', 0) else 'Stable' if abs(records[-1].get('score', 0) - records[0].get('score', 0)) < 5 else 'Declining'}\n"
                
                self.performance_trends_results_display.setText(report_text)
            else:
                self.performance_trends_results_display.setText(f"No performance records found for teacher {teacher_id}")

        except Exception as e:
            show_error_message("Error", f"Failed to generate report: {str(e)}", self)