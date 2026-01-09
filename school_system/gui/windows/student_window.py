"""
Student management window for the School System Management application.

This module provides the student management interface for admin users (admin and librarian roles).
Implements standardized, user-centric workflows for all student-related services with consistency,
validation, and system integrity following the STUDENT MANAGEMENT FLOW template.
"""

from PyQt6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QLabel, QLineEdit, QPushButton,
                            QHBoxLayout, QComboBox, QTabWidget, QTableWidget, QTableWidgetItem,
                            QTextEdit, QSizePolicy, QFileDialog, QMessageBox, QDialog, QMenu,
                            QListWidget, QListWidgetItem, QStyle, QFormLayout, QHeaderView, QTableView)
from PyQt6.QtCore import Qt, pyqtSignal, QTimer
from PyQt6.QtGui import QAction
from typing import Callable, Optional
from datetime import datetime

from school_system.gui.base.base_window import BaseWindow
from school_system.gui.dialogs.message_dialog import show_error_message, show_success_message
from school_system.gui.dialogs.confirm_dialog import ConfirmationDialog
from school_system.config.logging import logger
from school_system.services.student_service import StudentService
from school_system.core.exceptions import DatabaseException, ValidationError
from school_system.gui.windows.student_validation import StudentValidator, ValidationResult, FieldValidator
from school_system.gui.windows.student_workflow_components import (
    StudentWorkflowManager, StudentCreationWorkflow,
    StudentUpdateWorkflow, StudentDeletionWorkflow
)
from school_system.database.repositories.student_repo import ReamEntryRepository


class StudentWindow(BaseWindow):
    """Student management window for admin users with standardized workflows."""

    def __init__(self, parent: QMainWindow, current_user: str, current_role: str):
        """
        Initialize the student window with standardized workflow management.

        Args:
            parent: The parent window
            current_user: The current logged-in username
            current_role: The current user's role
        """
        super().__init__("School System - Student Management", parent)

        self.parent = parent
        self.current_user = current_user
        self.current_role = current_role
        self.student_service = StudentService()
        self.validator = StudentValidator()
         
        # Initialize workflow manager
        self.workflow_manager = StudentWorkflowManager(self)

        # Check if user has admin privileges
        if self.current_role not in ["admin", "librarian"]:
            show_error_message("Access Denied", "You do not have permission to access student management.", self)
            self.close()
            return

        # Set minimum size
        self.setMinimumSize(1200, 800)

        # Apply modern styling
        self._apply_modern_styling()

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
        
        # Refresh students table to populate initial data
        self._refresh_students_table()
        
        # Schedule population of recent transactions table after UI is fully initialized
        QTimer.singleShot(100, self._populate_recent_transactions_on_startup)

    def _apply_modern_styling(self):
        """Apply modern styling to the student window."""
        # Modern color scheme
        self.setStyleSheet("""
            /* Base styling */
            QWidget {
                font-family: 'Segoe UI', Arial, sans-serif;
                font-size: 14px;
                line-height: 1.4;
                background-color: #f5f5f5;
            }
            
            /* Window styling */
            StudentWindow {
                background-color: #f5f5f5;
            }
            
            /* Tab widget styling */
            QTabWidget::pane {
                border: 1px solid #e0e0e0;
                background-color: white;
                border-radius: 4px;
            }
            
            QTabBar::tab {
                padding: 8px 16px;
                background-color: #e0e0e0;
                color: #212121;
                border: none;
                border-top-left-radius: 4px;
                border-top-right-radius: 4px;
            }
            
            QTabBar::tab:selected {
                background-color: white;
                color: #4CAF50;
                border-bottom: 2px solid #4CAF50;
            }
            
            /* Button styling */
            QPushButton {
                padding: 8px 16px;
                border-radius: 4px;
                border: 1px solid #e0e0e0;
                background-color: white;
                min-height: 36px;
            }
            
            QPushButton[button_type="primary"] {
                background-color: #4CAF50;
                color: white;
                border: none;
            }
            
            QPushButton[button_type="primary"]:hover {
                background-color: #45a049;
            }
            
            QPushButton[button_type="primary"]:pressed {
                background-color: #3d8b40;
            }
            
            QPushButton[button_type="secondary"] {
                background-color: #2196F3;
                color: white;
                border: none;
            }
            
            QPushButton[button_type="secondary"]:hover {
                background-color: #1e88e5;
            }
            
            QPushButton[button_type="secondary"]:pressed {
                background-color: #1976d2;
            }
            
            QPushButton[button_type="danger"] {
                background-color: #F44336;
                color: white;
                border: none;
            }
            
            QPushButton[button_type="danger"]:hover {
                background-color: #e53935;
            }
            
            QPushButton[button_type="danger"]:pressed {
                background-color: #d32f2f;
            }
            
            /* Input field styling */
            QLineEdit, QComboBox {
                padding: 8px 12px;
                border: 1px solid #e0e0e0;
                border-radius: 4px;
                background-color: white;
                min-height: 36px;
            }
            
            QLineEdit:focus, QComboBox:focus {
                border: 1px solid #4CAF50;
            }
            
            /* Table styling */
            QTableView {
                border: 1px solid #e0e0e0;
                border-radius: 4px;
                background-color: white;
            }
            
            QHeaderView::section {
                background-color: #f5f5f5;
                padding: 8px;
                border: none;
                font-weight: 600;
                color: #212121;
            }
            
            QTableView::item:selected {
                background-color: #e3f2fd;
            }
            
            /* Card styling */
            QGroupBox {
                border: 1px solid #e0e0e0;
                border-radius: 4px;
                background-color: white;
                margin-top: 8px;
            }
            
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 3px;
                color: #4CAF50;
                font-weight: 600;
            }
            
            /* Label styling */
            QLabel {
                color: #212121;
            }
            
            QLabel.title {
                font-size: 18px;
                font-weight: 600;
                color: #212121;
            }
            
            QLabel.subtitle {
                font-size: 14px;
                font-weight: 500;
                color: #757575;
            }
        """)

    def _setup_widgets(self):
        """Setup the student management widgets."""
        # Create tab widget for different sections
        tab_widget = QTabWidget()
        self.add_widget_to_content(tab_widget)

        # Student Management Tab
        student_tab = self._create_student_management_tab()
        tab_widget.addTab(student_tab, "Student Management")

        # Ream Management Tab
        ream_tab = self._create_ream_management_tab()
        tab_widget.addTab(ream_tab, "Ream Management")

        # Library Activity Tab
        library_tab = self._create_library_activity_tab()
        tab_widget.addTab(library_tab, "Library Activity")

        # Import/Export Tab
        import_export_tab = self._create_import_export_tab()
        tab_widget.addTab(import_export_tab, "Import/Export")

        # Reports Tab
        reports_tab = self._create_reports_tab()
        tab_widget.addTab(reports_tab, "Reports")
        tab_widget.setCurrentIndex(0)

    def _setup_undo_system(self):
        """Setup the undo system for student operations."""
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
                    # Undo create by deleting - get student_id from the operation data
                    student_id = last_operation['data']['student_id']
                    self.student_service.delete_student(student_id)
                    show_success_message("Undo Successful",
                                        f"Student creation undone: {student_id}", self)
                elif last_operation['type'] == 'delete':
                    # Undo delete by recreating
                    student_data = last_operation['data']['student_data']
                    self.student_service.create_student(student_data)
                    show_success_message("Undo Successful",
                                        f"Student deletion undone: {last_operation['data']['student_id']}", self)
                 
                # Refresh table
                self._refresh_students_table()
                 
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
    
    def _clear_undo_stack(self):
        """Clear the undo stack after timeout."""
        self.undo_stack.clear()
        if self.undo_action:
            self.undo_action.setEnabled(False)
        if self.undo_timer:
            self.undo_timer.stop()

    def _create_student_management_tab(self) -> QWidget:
        """Create the student management tab with modern UI/UX design."""
        tab = QWidget()
        main_layout = self.create_flex_layout("column", False)
        main_layout.setContentsMargins(16, 16, 16, 16)  # Reduced from 20px
        main_layout.set_spacing(12)  # Consistent 12px spacing
        
        # Top action bar - horizontal layout for better space use
        action_bar = self.create_flex_layout("row", False)
        action_bar.set_spacing(8)
        
        # Search - integrated with filters
        search_container = self.create_flex_layout("row", False)
        search_container.set_spacing(8)
        
        # Smart search box with suggestions
        self.search_box = self.create_search_box("Search students by name, ID, or stream...")
        self.search_box.setMinimumWidth(180)
        self.search_box.setMaximumWidth(250)
        
        # Add search suggestions dropdown
        self.search_suggestions = QListWidget()
        self.search_suggestions.setWindowFlags(Qt.WindowType.Popup)
        self.search_suggestions.hide()
        
        # Connect signals for smart search
        self.search_box.search_text_changed.connect(self._show_search_suggestions)
        self.search_suggestions.itemClicked.connect(self._on_suggestion_selected)
        
        search_container.add_widget(self.search_box)
        
        # Filter dropdowns
        self.stream_filter = QComboBox()
        self.stream_filter.addItem("All Streams")
        self.stream_filter.setMinimumWidth(150)
        search_container.add_widget(self.stream_filter)
        
        # Populate stream filter with actual streams from database
        self._populate_stream_filter()
        
        action_bar.add_layout(search_container)
        
        # Quick action buttons - horizontal group
        button_group = self.create_flex_layout("row", False)
        button_group.set_spacing(8)
        
        create_btn = self.create_button("Add Student", "primary")
        create_btn.setIcon(self.style().standardIcon(QStyle.StandardPixmap.SP_FileIcon))
        create_btn.clicked.connect(self._show_create_student_dialog)
        button_group.add_widget(create_btn)
        
        import_btn = self.create_button("Import", "secondary")
        import_btn.setIcon(self.style().standardIcon(QStyle.StandardPixmap.SP_DialogOpenButton))
        import_btn.clicked.connect(self._on_browse_import_file)
        button_group.add_widget(import_btn)
        
        export_btn = self.create_button("Export", "secondary")
        export_btn.setIcon(self.style().standardIcon(QStyle.StandardPixmap.SP_DialogSaveButton))
        export_btn.clicked.connect(self._on_export_students)
        button_group.add_widget(export_btn)
        
        action_bar.add_layout(button_group)
        main_layout.add_layout(action_bar)
        
        # Enhanced students table with inline actions
        self.students_table = self.create_table(0, 4)  # Reduced from 5 columns
        self.students_table.setHorizontalHeaderLabels([
            "Admission Number",
            "Name",
            "Stream",
            "Actions"  # Single unified actions column
        ])
        self.students_table.horizontalHeader().setStretchLastSection(True)
        self.students_table.verticalHeader().setVisible(False)
        self.students_table.setAlternatingRowColors(True)
        self.students_table.setSelectionBehavior(QTableView.SelectionBehavior.SelectRows)
        
        main_layout.add_widget(self.students_table)
        
        # Pagination controls
        pagination_layout = self.create_flex_layout("row", False)
        pagination_layout.set_spacing(8)
        pagination_layout.add_stretch()
        
        self.prev_page_btn = self.create_button("Previous", "secondary")
        self.prev_page_btn.setEnabled(False)
        self.prev_page_btn.clicked.connect(self._on_previous_page)
        pagination_layout.add_widget(self.prev_page_btn)
        
        self.page_label = QLabel("Page 1 of 1")
        pagination_layout.add_widget(self.page_label)
        
        self.next_page_btn = self.create_button("Next", "secondary")
        self.next_page_btn.setEnabled(False)
        self.next_page_btn.clicked.connect(self._on_next_page)
        pagination_layout.add_widget(self.next_page_btn)
        
        # Items per page selector
        items_per_page_layout = self.create_flex_layout("row", False)
        items_per_page_layout.set_spacing(4)
        items_per_page_layout.add_widget(QLabel("Items per page:"))
        
        self.items_per_page_combo = QComboBox()
        self.items_per_page_combo.addItems(["10", "25", "50", "100"])
        self.items_per_page_combo.setCurrentText("25")
        self.items_per_page_combo.currentTextChanged.connect(self._on_items_per_page_changed)
        items_per_page_layout.add_widget(self.items_per_page_combo)
        
        pagination_layout.add_layout(items_per_page_layout)
        
        main_layout.add_layout(pagination_layout)
        
        # Initialize pagination state
        self.current_page = 1
        self.items_per_page = 25
        self.total_pages = 1
        
        # Create a main layout for the tab and add our layout widget to it
        tab_layout = QVBoxLayout(tab)
        tab_layout.setContentsMargins(0, 0, 0, 0)
        tab_layout.setSpacing(0)
        tab_layout.addWidget(main_layout)
        return tab

    def _show_search_suggestions(self, text):
        """Show search suggestions based on user input."""
        if len(text) < 2:
            self.search_suggestions.hide()
            return
        
        try:
            # Get all students and filter based on search text
            all_students = self.student_service.get_all_students()
            suggestions = []
            
            for student in all_students:
                # Check if stream is not None before calling lower()
                stream_match = False
                if student.stream is not None:
                    stream_match = text.lower() in student.stream.lower()
                
                if (text.lower() in student.student_id.lower() or
                    text.lower() in student.name.lower() or
                    stream_match):
                    # Handle None stream in display
                    stream_display = student.stream if student.stream is not None else "No Stream"
                    suggestions.append(f"{student.student_id} - {student.name} ({stream_display})")
            
            # Populate suggestions list
            self.search_suggestions.clear()
            if suggestions:
                for suggestion in suggestions[:5]:  # Limit to 5 suggestions
                    item = QListWidgetItem(suggestion)
                    self.search_suggestions.addItem(item)
                
                # Position and show suggestions
                pos = self.search_box.mapToGlobal(self.search_box.rect().bottomLeft())
                self.search_suggestions.setGeometry(pos.x(), pos.y(), self.search_box.width(), min(150, len(suggestions) * 30))
                self.search_suggestions.show()
            else:
                self.search_suggestions.hide()
                
        except Exception as e:
            print(f"Error showing search suggestions: {e}")
            self.search_suggestions.hide()

    def _populate_stream_filter(self):
        """Populate the stream filter dropdown with unique streams from the database."""
        try:
            # Get all students to extract unique streams
            all_students = self.student_service.get_all_students()
            
            # Extract unique streams (excluding None values)
            unique_streams = set()
            for student in all_students:
                if student.stream and student.stream.strip():
                    unique_streams.add(student.stream.strip())
            
            # Add unique streams to the filter dropdown
            for stream in sorted(unique_streams):
                self.stream_filter.addItem(stream)
                
            # Connect the stream filter to refresh table when changed
            self.stream_filter.currentTextChanged.connect(self._on_stream_filter_changed)
                
        except Exception as e:
            print(f"Error populating stream filter: {e}")

    def _on_stream_filter_changed(self, stream: str):
        """Handle stream filter change to filter students by selected stream."""
        try:
            # Reset to first page when filtering
            self.current_page = 1
            
            # Refresh the students table with the new filter
            self._refresh_students_table()
                
        except Exception as e:
            show_error_message("Error", f"Failed to apply stream filter: {str(e)}", self)

    def _on_suggestion_selected(self, item):
        """Handle search suggestion selection."""
        # Extract student ID from suggestion and search for it
        suggestion_text = item.text()
        student_id = suggestion_text.split(' - ')[0]
        
        self.search_box.set_search_text(student_id)
        self.search_suggestions.hide()
        
        # Perform search
        self._on_search_students(student_id)

    def _create_ream_management_tab(self) -> QWidget:
        """Create the ream management tab with modern UI/UX design."""
        tab = QWidget()
        main_layout = self.create_flex_layout("column", False)
        main_layout.setContentsMargins(16, 16, 16, 16)
        main_layout.set_spacing(12)
        
        # Ream management tabs
        ream_tabs = QTabWidget()
        
        # Add Reams tab
        add_tab = QWidget()
        add_layout = self.create_flex_layout("column", False)
        add_layout.set_spacing(12)
        
        # Use form layout for better alignment
        form_layout = QFormLayout()
        form_layout.setVerticalSpacing(8)
        form_layout.setHorizontalSpacing(16)
        
        self.add_ream_student_id_input = self.create_input("Enter admission number")
        form_layout.addRow("Admission Number:", self.add_ream_student_id_input)
        
        self.add_ream_count_input = self.create_input("Enter number of reams")
        form_layout.addRow("Reams Count:", self.add_ream_count_input)
        
        self.add_ream_source_combo = QComboBox()
        self.add_ream_source_combo.addItems(["Distribution", "Purchase", "Transfer", "Other"])
        form_layout.addRow("Source:", self.add_ream_source_combo)
        
        add_layout.add_layout(form_layout)
        
        add_ream_button = self.create_button("Add Reams", "primary")
        add_ream_button.clicked.connect(self._on_add_reams)
        add_layout.add_widget(add_ream_button)
        
        # Create a layout for the add tab and add our layout widget to it
        add_tab_layout = QVBoxLayout(add_tab)
        add_tab_layout.setContentsMargins(0, 0, 0, 0)
        add_tab_layout.setSpacing(0)
        add_tab_layout.addWidget(add_layout)
        ream_tabs.addTab(add_tab, "Add Reams")
        
        # Deduct Reams tab
        deduct_tab = QWidget()
        deduct_layout = self.create_flex_layout("column", False)
        deduct_layout.set_spacing(12)
        
        deduct_form_layout = QFormLayout()
        deduct_form_layout.setVerticalSpacing(8)
        deduct_form_layout.setHorizontalSpacing(16)
        
        self.deduct_ream_student_id_input = self.create_input("Enter admission number")
        deduct_form_layout.addRow("Admission Number:", self.deduct_ream_student_id_input)
        
        self.deduct_ream_count_input = self.create_input("Enter number of reams to deduct")
        deduct_form_layout.addRow("Reams Count:", self.deduct_ream_count_input)
        
        self.deduct_ream_purpose_combo = QComboBox()
        self.deduct_ream_purpose_combo.addItems(["Usage", "Transfer", "Loss", "Other"])
        deduct_form_layout.addRow("Purpose:", self.deduct_ream_purpose_combo)
        
        deduct_layout.add_layout(deduct_form_layout)
        
        deduct_ream_button = self.create_button("Deduct Reams", "secondary")
        deduct_ream_button.clicked.connect(self._on_deduct_reams)
        deduct_layout.add_widget(deduct_ream_button)
        
        # Create a layout for the deduct tab and add our layout widget to it
        deduct_tab_layout = QVBoxLayout(deduct_tab)
        deduct_tab_layout.setContentsMargins(0, 0, 0, 0)
        deduct_tab_layout.setSpacing(0)
        deduct_tab_layout.addWidget(deduct_layout)
        ream_tabs.addTab(deduct_tab, "Deduct Reams")
        
        # Transfer Reams tab
        transfer_tab = QWidget()
        transfer_layout = self.create_flex_layout("column", False)
        transfer_layout.set_spacing(12)
        
        transfer_form_layout = QFormLayout()
        transfer_form_layout.setVerticalSpacing(8)
        transfer_form_layout.setHorizontalSpacing(16)
        
        self.transfer_from_student_id_input = self.create_input("Enter source admission number")
        transfer_form_layout.addRow("From Admission Number:", self.transfer_from_student_id_input)
        
        self.transfer_to_student_id_input = self.create_input("Enter destination admission number")
        transfer_form_layout.addRow("To Admission Number:", self.transfer_to_student_id_input)
        
        self.transfer_ream_count_input = self.create_input("Enter number of reams to transfer")
        transfer_form_layout.addRow("Reams Count:", self.transfer_ream_count_input)
        
        self.transfer_reason_input = self.create_input("Enter reason for transfer")
        transfer_form_layout.addRow("Reason:", self.transfer_reason_input)
        
        transfer_layout.add_layout(transfer_form_layout)
        
        transfer_ream_button = self.create_button("Transfer Reams", "primary")
        transfer_ream_button.clicked.connect(self._on_transfer_reams)
        transfer_layout.add_widget(transfer_ream_button)
        
        # Create a layout for the transfer tab and add our layout widget to it
        transfer_tab_layout = QVBoxLayout(transfer_tab)
        transfer_tab_layout.setContentsMargins(0, 0, 0, 0)
        transfer_tab_layout.setSpacing(0)
        transfer_tab_layout.addWidget(transfer_layout)
        ream_tabs.addTab(transfer_tab, "Transfer Reams")
        
        main_layout.add_widget(ream_tabs)
        
        # Recent transactions table
        transactions_section = self.create_card("Recent Transactions", "")
        transactions_layout = self.create_flex_layout("column", False)
        transactions_layout.set_spacing(8)
        
        # Create table with proper column count
        self.ream_transactions_table = self.create_table(0, 0)
        self.ream_transactions_table.setColumnCount(5)  # Set column count explicitly
        self.ream_transactions_table.setHorizontalHeaderLabels([
            "Student ID", "Reams", "Date", "Type", "Balance"
        ])
        
        transactions_layout.add_widget(self.ream_transactions_table)
        
        # Add the transactions layout widget to the section instead of its internal layout
        transactions_section.layout.addWidget(transactions_layout)
        main_layout.add_widget(transactions_section)
        
        # Create a main layout for the tab and add our layout widget to it
        tab_layout = QVBoxLayout(tab)
        tab_layout.setContentsMargins(0, 0, 0, 0)
        tab_layout.setSpacing(0)
        tab_layout.addWidget(main_layout)
        return tab

    def _create_library_activity_tab(self) -> QWidget:
        """Create the library activity tab."""
        tab = QWidget()
        layout = self.create_flex_layout("column", False)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.set_spacing(15)

        # View Borrowed Books Section
        borrowed_section = self.create_card("View Borrowed Books", "")
        borrowed_form = QWidget()
        borrowed_layout = self.create_flex_layout("column", False)
        borrowed_layout.set_spacing(10)

        # Admission Number
        borrowed_student_id_label = QLabel("Admission Number:")
        borrowed_layout.add_widget(borrowed_student_id_label)
        self.borrowed_student_id_input = self.create_input("Enter admission number")
        borrowed_layout.add_widget(self.borrowed_student_id_input)

        # View borrowed books button
        view_borrowed_button = self.create_button("View Borrowed Books", "primary")
        view_borrowed_button.clicked.connect(self._on_view_borrowed_books)
        borrowed_layout.add_widget(view_borrowed_button)

        # Borrowed books table
        self.borrowed_books_table = self.create_table(0, 5)
        self.borrowed_books_table.setHorizontalHeaderLabels(["Book ID", "Title", "Borrowed On", "Due Date", "Status"])
        borrowed_layout.add_widget(self.borrowed_books_table)

        # Create a layout for the borrowed form and add our layout widget to it
        borrowed_form_layout = QVBoxLayout(borrowed_form)
        borrowed_form_layout.setContentsMargins(0, 0, 0, 0)
        borrowed_form_layout.setSpacing(0)
        borrowed_form_layout.addWidget(borrowed_layout)
        borrowed_section.layout.addWidget(borrowed_form)
        layout.add_widget(borrowed_section)

        # View Borrowing History Section
        history_section = self.create_card("View Borrowing History", "")
        history_form = QWidget()
        history_layout = self.create_flex_layout("column", False)
        history_layout.set_spacing(10)

        # Admission Number
        history_student_id_label = QLabel("Admission Number:")
        history_layout.add_widget(history_student_id_label)
        self.history_student_id_input = self.create_input("Enter admission number")
        history_layout.add_widget(self.history_student_id_input)

        # View history button
        view_history_button = self.create_button("View History", "secondary")
        view_history_button.clicked.connect(self._on_view_borrowing_history)
        history_layout.add_widget(view_history_button)

        # Borrowing history table
        self.borrowing_history_table = self.create_table(0, 6)
        self.borrowing_history_table.setHorizontalHeaderLabels(["Book ID", "Title", "Borrowed On", "Returned On", "Condition", "Fine"])
        history_layout.add_widget(self.borrowing_history_table)

        # Create a layout for the history form and add our layout widget to it
        history_form_layout = QVBoxLayout(history_form)
        history_form_layout.setContentsMargins(0, 0, 0, 0)
        history_form_layout.setSpacing(0)
        history_form_layout.addWidget(history_layout)
        history_section.layout.addWidget(history_form)
        layout.add_widget(history_section)

        # View Overdue Books Section
        overdue_section = self.create_card("View Overdue Books", "")
        overdue_form = QWidget()
        overdue_layout = self.create_flex_layout("column", False)
        overdue_layout.set_spacing(10)

        # Admission Number
        overdue_student_id_label = QLabel("Admission Number:")
        overdue_layout.add_widget(overdue_student_id_label)
        self.overdue_student_id_input = self.create_input("Enter admission number")
        overdue_layout.add_widget(self.overdue_student_id_input)

        # View overdue books button
        view_overdue_button = self.create_button("View Overdue Books", "danger")
        view_overdue_button.clicked.connect(self._on_view_overdue_books)
        overdue_layout.add_widget(view_overdue_button)

        # Overdue books table
        self.overdue_books_table = self.create_table(0, 5)
        self.overdue_books_table.setHorizontalHeaderLabels(["Book ID", "Title", "Borrowed On", "Due Date", "Days Overdue"])
        overdue_layout.add_widget(self.overdue_books_table)

        # Create a layout for the overdue form and add our layout widget to it
        overdue_form_layout = QVBoxLayout(overdue_form)
        overdue_form_layout.setContentsMargins(0, 0, 0, 0)
        overdue_form_layout.setSpacing(0)
        overdue_form_layout.addWidget(overdue_layout)
        overdue_section.layout.addWidget(overdue_form)
        layout.add_widget(overdue_section)

        # Create a main layout for the tab and add our layout widget to it
        tab_layout = QVBoxLayout(tab)
        tab_layout.setContentsMargins(0, 0, 0, 0)
        tab_layout.setSpacing(0)
        tab_layout.addWidget(layout)
        return tab

    def _create_import_export_tab(self) -> QWidget:
        """Create the import/export tab with enhanced user guidance."""
        tab = QWidget()
        main_layout = self.create_flex_layout("column", False)
        main_layout.setContentsMargins(16, 16, 16, 16)
        main_layout.set_spacing(12)

        # Import Students Section with detailed instructions
        import_section = self.create_card("Import Students from Excel",
                                         "Please ensure your Excel file follows the required format:")
        import_form = QWidget()
        import_layout = self.create_flex_layout("column", False)
        import_layout.set_spacing(10)

        # Detailed instructions
        instructions_label = QLabel("""
        <b>Required Excel Format:</b><br>
        • Column A: Student ID (Admission Number)<br>
        • Column B: Name (Full Student Name)<br>
        • Column C: Stream (Student Stream)<br>
        <br>
        <b>Example:</b><br>
        | A1: Student ID | B1: Name | C1: Stream |<br>
        | A2: S001 | B2: John Doe | C2: Science |<br>
        | A3: S002 | B3: Jane Smith | C2: Arts |
        """)
        instructions_label.setWordWrap(True)
        import_layout.add_widget(instructions_label)

        # File selection
        self.import_file_label = QLabel("No file selected")
        import_layout.add_widget(self.import_file_label)

        # Browse button
        browse_button = self.create_button("Browse Excel File", "primary")
        browse_button.setIcon(self.style().standardIcon(QStyle.StandardPixmap.SP_DialogOpenButton))
        browse_button.clicked.connect(self._on_browse_import_file)
        import_layout.add_widget(browse_button)

        # Import button
        import_button = self.create_button("Import Students", "secondary")
        import_button.setIcon(self.style().standardIcon(QStyle.StandardPixmap.SP_ArrowRight))
        import_button.clicked.connect(self._on_import_students)
        import_layout.add_widget(import_button)

        # Import status
        self.import_status_label = QLabel("")
        self.import_status_label.setStyleSheet("color: #666;")
        import_layout.add_widget(self.import_status_label)

        # Create a layout for the import form and add our layout widget to it
        import_form_layout = QVBoxLayout(import_form)
        import_form_layout.setContentsMargins(0, 0, 0, 0)
        import_form_layout.setSpacing(0)
        import_form_layout.addWidget(import_layout)
        import_section.layout.addWidget(import_form)
        main_layout.add_widget(import_section)

        # Export Students Section
        export_section = self.create_card("Export Students to Excel",
                                         "Export all student data to Excel format")
        export_form = QWidget()
        export_layout = self.create_flex_layout("column", False)
        export_layout.set_spacing(10)

        # Export button
        export_button = self.create_button("Export All Students", "primary")
        export_button.setIcon(self.style().standardIcon(QStyle.StandardPixmap.SP_DialogSaveButton))
        export_button.clicked.connect(self._on_export_students)
        export_layout.add_widget(export_button)

        # Export status
        self.export_status_label = QLabel("")
        self.export_status_label.setStyleSheet("color: #666;")
        export_layout.add_widget(self.export_status_label)

        # Create a layout for the export form and add our layout widget to it
        export_form_layout = QVBoxLayout(export_form)
        export_form_layout.setContentsMargins(0, 0, 0, 0)
        export_form_layout.setSpacing(0)
        export_form_layout.addWidget(export_layout)
        export_section.layout.addWidget(export_form)
        main_layout.add_widget(export_section)

        # Create a main layout for the tab and add our layout widget to it
        tab_layout = QVBoxLayout(tab)
        tab_layout.setContentsMargins(0, 0, 0, 0)
        tab_layout.setSpacing(0)
        tab_layout.addWidget(main_layout)
        return tab

    def _create_reports_tab(self) -> QWidget:
        """Create the reports tab."""
        tab = QWidget()
        layout = self.create_flex_layout("column", False)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.set_spacing(15)

        # Student Summary Section
        summary_section = self.create_card("Student Summary Report", "")
        summary_form = QWidget()
        summary_layout = self.create_flex_layout("column", False)
        summary_layout.set_spacing(10)

        # Admission Number
        summary_student_id_label = QLabel("Admission Number:")
        summary_layout.add_widget(summary_student_id_label)
        self.summary_student_id_input = self.create_input("Enter admission number")
        summary_layout.add_widget(self.summary_student_id_input)

        # Generate summary button
        generate_summary_button = self.create_button("Generate Summary", "primary")
        generate_summary_button.clicked.connect(self._on_generate_student_summary)
        summary_layout.add_widget(generate_summary_button)

        # Summary results display
        self.summary_results_display = QTextEdit()
        self.summary_results_display.setReadOnly(True)
        self.summary_results_display.setMaximumHeight(200)
        summary_layout.add_widget(self.summary_results_display)

        # Add the summary layout widget to the form instead of setting its internal layout
        summary_form_layout = QVBoxLayout(summary_form)
        summary_form_layout.setContentsMargins(0, 0, 0, 0)
        summary_form_layout.addWidget(summary_layout)
        summary_section.layout.addWidget(summary_form)
        layout.add_widget(summary_section)

        # Stream Analysis Section
        stream_section = self.create_card("Stream Analysis Report", "")
        stream_form = QWidget()
        stream_layout = self.create_flex_layout("column", False)
        stream_layout.set_spacing(10)

        # Stream
        stream_label = QLabel("Stream:")
        stream_layout.add_widget(stream_label)
        self.stream_analysis_stream_input = self.create_input("Enter stream name")
        stream_layout.add_widget(self.stream_analysis_stream_input)

        # Generate stream analysis button
        generate_stream_button = self.create_button("Generate Stream Analysis", "secondary")
        generate_stream_button.clicked.connect(self._on_generate_stream_analysis)
        stream_layout.add_widget(generate_stream_button)

        # Stream analysis results display
        self.stream_analysis_results_display = QTextEdit()
        self.stream_analysis_results_display.setReadOnly(True)
        self.stream_analysis_results_display.setMaximumHeight(200)
        stream_layout.add_widget(self.stream_analysis_results_display)

        # Add the stream layout widget to the form instead of setting its internal layout
        stream_form_layout = QVBoxLayout(stream_form)
        stream_form_layout.setContentsMargins(0, 0, 0, 0)
        stream_form_layout.addWidget(stream_layout)
        stream_section.layout.addWidget(stream_form)
        layout.add_widget(stream_section)

        # Ream Usage Section
        ream_section = self.create_card("Ream Usage Report", "")
        ream_form = QWidget()
        ream_layout = self.create_flex_layout("column", False)
        ream_layout.set_spacing(10)

        # Admission Number
        ream_student_id_label = QLabel("Admission Number:")
        ream_layout.add_widget(ream_student_id_label)
        self.ream_usage_student_id_input = self.create_input("Enter admission number")
        ream_layout.add_widget(self.ream_usage_student_id_input)

        # Generate ream usage button
        generate_ream_button = self.create_button("Generate Ream Usage Report", "primary")
        generate_ream_button.clicked.connect(self._on_generate_ream_usage_report)
        ream_layout.add_widget(generate_ream_button)

        # Ream usage results display
        self.ream_usage_results_display = QTextEdit()
        self.ream_usage_results_display.setReadOnly(True)
        self.ream_usage_results_display.setMaximumHeight(200)
        ream_layout.add_widget(self.ream_usage_results_display)

        # Add the ream layout widget to the form instead of setting its internal layout
        ream_form_layout = QVBoxLayout(ream_form)
        ream_form_layout.setContentsMargins(0, 0, 0, 0)
        ream_form_layout.addWidget(ream_layout)
        ream_section.layout.addWidget(ream_form)
        layout.add_widget(ream_section)

        # Create a main layout for the tab and add our layout widget to it
        tab_layout = QVBoxLayout(tab)
        tab_layout.setContentsMargins(0, 0, 0, 0)
        tab_layout.setSpacing(0)
        tab_layout.addWidget(layout)
        return tab

    # Event handlers for Student Management
    def _on_create_student(self):
        """Handle create student button click."""
        try:
            student_data = {
                'student_id': self.create_student_id_input.text().strip(),
                'name': self.create_name_input.text().strip(),
                'stream': self.create_stream_input.text().strip()
            }

            # Validate required fields
            if not student_data['student_id'] or not student_data['name']:
                show_error_message("Validation Error", "Student ID and Name are required", self)
                return

            student = self.student_service.create_student(student_data)
            show_success_message("Success", f"Student created successfully with ID: {student.student_id}", self)
            self._refresh_students_table()

            # Clear form
            self.create_student_id_input.clear()
            self.create_name_input.clear()
            self.create_stream_input.clear()

        except (ValidationError, DatabaseException) as e:
            show_error_message("Error", str(e), self)
        except Exception as e:
            show_error_message("Error", f"An error occurred: {str(e)}", self)

    def _on_update_student(self):
        """Handle update student button click."""
        try:
            student_id = self.update_student_id_input.text().strip()
            student_data = {}

            if self.update_name_input.text().strip():
                student_data['name'] = self.update_name_input.text().strip()
            if self.update_stream_input.text().strip():
                student_data['stream'] = self.update_stream_input.text().strip()

            if not student_data:
                show_error_message("Error", "Please provide at least one field to update", self)
                return

            student = self.student_service.update_student(student_id, student_data)
            if student:
                show_success_message("Success", f"Student updated successfully", self)
                self._refresh_students_table()
            else:
                show_error_message("Error", "Student not found", self)

        except Exception as e:
            show_error_message("Error", f"An error occurred: {str(e)}", self)

    def _on_delete_student(self):
        """Handle delete student button click."""
        try:
            student_id = self.delete_student_id_input.text().strip()

            if not student_id:
                show_error_message("Validation Error", "Admission number is required", self)
                return

            # Confirm deletion
            confirm = QMessageBox.question(
                self, "Confirm Deletion", 
                f"Are you sure you want to delete student with ID: {student_id}?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
            )

            if confirm == QMessageBox.StandardButton.Yes:
                success = self.student_service.delete_student(student_id)
                if success:
                    show_success_message("Success", "Student deleted successfully", self)
                    self._refresh_students_table()
                else:
                    show_error_message("Error", "Student not found", self)

        except Exception as e:
            show_error_message("Error", f"An error occurred: {str(e)}", self)

    def _on_search_students(self, query: str):
        """Handle student search with pagination."""
        try:
            # Reset to first page when searching
            self.current_page = 1
            
            # For now, just refresh the table (search functionality would need to be implemented in service)
            self._refresh_students_table()
        except Exception as e:
            show_error_message("Error", f"Search failed: {str(e)}", self)

    def _on_previous_page(self):
        """Handle previous page navigation."""
        if self.current_page > 1:
            self.current_page -= 1
            self._refresh_students_table()

    def _on_next_page(self):
        """Handle next page navigation."""
        if self.current_page < self.total_pages:
            self.current_page += 1
            self._refresh_students_table()

    def _on_items_per_page_changed(self, items_per_page_str: str):
        """Handle items per page change."""
        self.items_per_page = int(items_per_page_str)
        self.current_page = 1  # Reset to first page
        self._refresh_students_table()

    def _refresh_students_table(self):
        """Refresh the students table with pagination and stream filtering."""
        try:
            all_students = self.student_service.get_all_students()
            
            # Apply stream filter if a specific stream is selected (not "All Streams")
            selected_stream = self.stream_filter.currentText()
            if selected_stream and selected_stream != "All Streams":
                filtered_students = [s for s in all_students if s.stream == selected_stream]
            else:
                filtered_students = all_students
            
            # Apply pagination
            start_index = (self.current_page - 1) * self.items_per_page
            end_index = start_index + self.items_per_page
            paginated_students = filtered_students[start_index:end_index]
            
            # Calculate total pages based on filtered results
            self.total_pages = max(1, (len(filtered_students) + self.items_per_page - 1) // self.items_per_page)
            
            # Update pagination controls
            self.prev_page_btn.setEnabled(self.current_page > 1)
            self.next_page_btn.setEnabled(self.current_page < self.total_pages)
            self.page_label.setText(f"Page {self.current_page} of {self.total_pages}")
            
            self._populate_students_table(paginated_students)
        except Exception as e:
            show_error_message("Error", f"Failed to refresh students: {str(e)}", self)

    def _handle_operation_completed(self, success: bool, message: str):
        """
        Handle completion of student operations with appropriate feedback and state updates.
        
        This method serves as the central callback for all student workflow operations,
        ensuring consistent post-operation behavior including table refreshes,
        user notifications, and undo tracking.
        
        Args:
            success: Boolean indicating if the operation was successful
            message: Descriptive message about the operation result
        """
        if success:
            # Refresh the students table to show latest data
            self._refresh_students_table()
            
            # Show appropriate success message based on operation type
            if "created" in message.lower():
                show_success_message("Success", message, self)
                # Track creation for potential undo (5-second window)
                # Student ID can be extracted from message for undo tracking
            elif "updated" in message.lower():
                show_success_message("Success", message, self)
                # Track update for potential undo
            elif "deleted" in message.lower():
                show_success_message("Success", message, self)
                # Track deletion for potential undo
        else:
            # Show error message for failed operations
            show_error_message("Error", message, self)

    def _show_create_student_dialog(self):
        """Show create student dialog with form validation."""
        from school_system.gui.dialogs.input_dialog import InputDialog
        
        # Create dialog with form fields
        dialog = InputDialog("Create New Student", "Enter student details:", self)
        
        # Add form fields
        student_id_input = dialog.add_input_field("Admission Number:", "Enter student ID")
        name_input = dialog.add_input_field("Name:", "Enter student name")
        stream_input = dialog.add_input_field("Stream:", "Enter student stream")
        
        # Show dialog and handle result
        if dialog.exec() == QDialog.DialogCode.Accepted:
            student_data = {
                'student_id': student_id_input.text().strip(),
                'name': name_input.text().strip(),
                'stream': stream_input.text().strip()
            }
            
            # Validate required fields
            if not student_data['student_id'] or not student_data['name']:
                show_error_message("Validation Error", "Student ID and Name are required", self)
                return
            
            try:
                student = self.student_service.create_student(student_data)
                show_success_message("Success", f"Student created successfully with ID: {student.student_id}", self)
                self._refresh_students_table()
                
                # Track operation for undo
                self._track_operation('create', {
                    'student_id': student.student_id,
                    'student_data': student_data
                })
                
            except (ValidationError, DatabaseException) as e:
                show_error_message("Error", str(e), self)
            except Exception as e:
                show_error_message("Error", f"An error occurred: {str(e)}", self)

    def _populate_students_table(self, students):
        """Populate the students table with data and enhanced features."""
        # Ensure table has correct column count
        if self.students_table.columnCount() != 4:
            self.students_table.setColumnCount(4)
            self.students_table.setHorizontalHeaderLabels([
                "Admission Number",
                "Name",
                "Stream",
                "Actions"
            ])
        
        self.students_table.setRowCount(0)
 
        for student in students:
            row_position = self.students_table.rowCount()
            self.students_table.insertRow(row_position)

            self.students_table.setItem(row_position, 0, QTableWidgetItem(str(student.admission_number)))
            self.students_table.setItem(row_position, 1, QTableWidgetItem(student.name))
            self.students_table.setItem(row_position, 2, QTableWidgetItem(student.stream or ""))
 
            # Add action buttons container
            action_widget = QWidget()
            action_layout = QHBoxLayout(action_widget)
            action_layout.setContentsMargins(0, 0, 0, 0)
            action_layout.setSpacing(5)

            # View button with icon
            view_button = self.create_button("View", "secondary")
            view_button.setIcon(self.style().standardIcon(QStyle.StandardPixmap.SP_DialogOpenButton))
            view_button.clicked.connect(lambda _, sid=student.admission_number: self._view_student_details(sid))
            action_layout.addWidget(view_button)

            # Edit button with icon
            edit_button = self.create_button("Edit", "primary")
            edit_button.setIcon(self.style().standardIcon(QStyle.StandardPixmap.SP_FileDialogDetailedView))
            edit_button.clicked.connect(lambda _, sid=student.admission_number: self._start_edit_workflow(sid))
            action_layout.addWidget(edit_button)

            # Delete button with icon
            delete_button = self.create_button("Delete", "danger")
            delete_button.setIcon(self.style().standardIcon(QStyle.StandardPixmap.SP_TrashIcon))
            delete_button.clicked.connect(lambda _, sid=student.admission_number: self._start_delete_workflow(sid))
            action_layout.addWidget(delete_button)

            self.students_table.setCellWidget(row_position, 3, action_widget)

    def _start_edit_workflow(self, student_id: str):
        """Start the edit workflow for a specific student."""
        try:
            student = self.student_service.get_student_by_id(student_id)
            if student:
                # Create update workflow and pre-populate with student data
                update_workflow = StudentUpdateWorkflow(self)
                update_workflow.operation_completed.connect(self._handle_operation_completed)
                  
                # Pre-populate the student ID field
                if hasattr(update_workflow, 'student_id_input'):
                    update_workflow.student_id_input.setText(student.student_id)
                    update_workflow.student_id_input.setReadOnly(True)
                  
                # Show the workflow by calling start_workflow on the workflow manager
                print(f"DEBUG: Calling workflow_manager.start_workflow('update')")
                self.workflow_manager.start_workflow("update")
                print(f"DEBUG: Called workflow_manager.start_workflow('update')")
                  
            else:
                show_error_message("Error", "Student not found", self)
        except Exception as e:
            show_error_message("Error", f"Failed to start edit workflow: {str(e)}", self)

    def _start_delete_workflow(self, student_id: str):
        """Start the delete workflow for a specific student."""
        try:
            student = self.student_service.get_student_by_id(student_id)
            if student:
                # Create delete workflow and pre-populate with student data
                delete_workflow = StudentDeletionWorkflow(self)
                delete_workflow.operation_completed.connect(self._handle_operation_completed)
                 
                # Pre-populate the student ID field
                if hasattr(delete_workflow, 'student_id_input'):
                    delete_workflow.student_id_input.setText(student.student_id)
                    delete_workflow.student_id_input.setReadOnly(True)
                 
                # Show the workflow by calling start_workflow on the workflow manager
                self.workflow_manager.start_workflow("delete")
                 
            else:
                show_error_message("Error", "Student not found", self)
        except Exception as e:
            show_error_message("Error", f"Failed to start delete workflow: {str(e)}", self)

    def _view_student_details(self, student_id: str):
        """View detailed information about a student."""
        try:
            student = self.student_service.get_student_by_id(student_id)
            if student:
                stream_display = student.stream if student.stream is not None else "No Stream"
                # Display student_id which should now be properly populated (same as admission_number)
                details = f"Student Details:\n\nID: {student.student_id}\nName: {student.name}\nStream: {stream_display}"
                show_success_message("Student Details", details, self)
            else:
                show_error_message("Error", "Student not found", self)
        except Exception as e:
            show_error_message("Error", f"Failed to view student details: {str(e)}", self)

    # Event handlers for Ream Management
    def _on_add_reams(self):
        """Handle add reams button click."""
        try:
            student_id = self.add_ream_student_id_input.text().strip()
            reams_count = int(self.add_ream_count_input.text().strip())
            source = self.add_ream_source_combo.currentText()

            if not student_id or reams_count <= 0:
                show_error_message("Validation Error", "Admission number and positive reams count are required", self)
                return

            entry = self.student_service.add_reams_to_student(student_id, reams_count, source)
            show_success_message("Success", f"Added {reams_count} reams to student {student_id}", self)

            # Clear form
            self.add_ream_student_id_input.clear()
            self.add_ream_count_input.clear()

            # Refresh ream transactions table for this student
            self._refresh_ream_transactions_table(student_id)

        except ValueError:
            show_error_message("Error", "Invalid reams count", self)
        except Exception as e:
            show_error_message("Error", f"An error occurred: {str(e)}", self)

    def _on_deduct_reams(self):
        """Handle deduct reams button click."""
        try:
            student_id = self.deduct_ream_student_id_input.text().strip()
            reams_count = int(self.deduct_ream_count_input.text().strip())
            purpose = self.deduct_ream_purpose_combo.currentText()

            if not student_id or reams_count <= 0:
                show_error_message("Validation Error", "Admission number and positive reams count are required", self)
                return

            entry = self.student_service.deduct_reams_from_student(student_id, reams_count, purpose)
            show_success_message("Success", f"Deducted {reams_count} reams from student {student_id}", self)

            # Clear form
            self.deduct_ream_student_id_input.clear()
            self.deduct_ream_count_input.clear()

            # Refresh ream transactions table for this student
            self._refresh_ream_transactions_table(student_id)

        except ValueError:
            show_error_message("Error", "Invalid reams count", self)
        except Exception as e:
            show_error_message("Error", f"An error occurred: {str(e)}", self)

    def _on_transfer_reams(self):
        """Handle transfer reams button click."""
        try:
            from_student_id = self.transfer_from_student_id_input.text().strip()
            to_student_id = self.transfer_to_student_id_input.text().strip()
            reams_count = int(self.transfer_ream_count_input.text().strip())
            reason = self.transfer_reason_input.text().strip()

            if not from_student_id or not to_student_id or reams_count <= 0:
                show_error_message("Validation Error", "Both admission numbers and positive reams count are required", self)
                return

            success = self.student_service.transfer_reams_between_students(
                from_student_id, to_student_id, reams_count, reason
            )

            if success:
                show_success_message("Success", f"Transferred {reams_count} reams from {from_student_id} to {to_student_id}", self)
                # Clear form
                self.transfer_from_student_id_input.clear()
                self.transfer_to_student_id_input.clear()
                self.transfer_ream_count_input.clear()
                self.transfer_reason_input.clear()
                
                # Refresh ream transactions table for both students
                self._refresh_ream_transactions_table(from_student_id)
                self._refresh_ream_transactions_table(to_student_id)
            else:
                show_error_message("Error", "Failed to transfer reams", self)

        except ValueError:
            show_error_message("Error", "Invalid reams count", self)
        except Exception as e:
            show_error_message("Error", f"An error occurred: {str(e)}", self)

    def _on_view_ream_transactions(self):
        """Handle view ream transactions button click."""
        try:
            student_id = self.transactions_student_id_input.text().strip()

            if not student_id:
                show_error_message("Validation Error", "Student ID is required", self)
                return

            transactions = self.student_service.get_student_ream_transaction_history(student_id)
            self._populate_ream_transactions_table(transactions)

        except Exception as e:
            show_error_message("Error", f"An error occurred: {str(e)}", self)

    def _populate_ream_transactions_table(self, transactions):
        """Populate the ream transactions table with data."""
        # Clear the table
        self.ream_transactions_table.setRowCount(0)
        
        # Check if transactions list is empty
        if not transactions:
            return
            
        # Set the correct number of rows at once for better performance
        self.ream_transactions_table.setRowCount(len(transactions))

        for row_position, transaction in enumerate(transactions):
            # Get current balance for this specific student
            current_balance = self.student_service.get_student_ream_balance(transaction.student_id)

            # Create and set items for each column
            student_id_item = QTableWidgetItem(str(transaction.student_id))
            reams_count_item = QTableWidgetItem(str(transaction.reams_count))
            date_item = QTableWidgetItem(transaction.date_added or "")
            type_item = QTableWidgetItem("Add" if transaction.reams_count > 0 else "Deduct")
            balance_item = QTableWidgetItem(str(current_balance))
            
            # Set items in the table
            self.ream_transactions_table.setItem(row_position, 0, student_id_item)
            self.ream_transactions_table.setItem(row_position, 1, reams_count_item)
            self.ream_transactions_table.setItem(row_position, 2, date_item)
            self.ream_transactions_table.setItem(row_position, 3, type_item)
            self.ream_transactions_table.setItem(row_position, 4, balance_item)
        
        # Ensure the table is visible and properly laid out
        self.ream_transactions_table.setVisible(True)
        self.ream_transactions_table.resizeColumnsToContents()
        self.ream_transactions_table.resizeRowsToContents()

    def _refresh_ream_transactions_table(self, student_id: str):
        """Refresh the ream transactions table for a specific student."""
        try:
            if student_id:  # Only refresh if we have a valid student ID
                transactions = self.student_service.get_student_ream_transaction_history(student_id)
                self._populate_ream_transactions_table(transactions)
        except Exception as e:
            print(f"Error refreshing ream transactions table: {e}")
            # Don't show error to user as this is an automatic refresh

    def _populate_recent_transactions_on_startup(self):
        """Populate the recent transactions table with recent transactions from all students on startup."""
        try:
            # Check if the table is initialized
            if not hasattr(self, 'ream_transactions_table'):
                return
            
            # Get all ream entries from the database (most recent first)
            ream_entry_repository = ReamEntryRepository()
            all_transactions = ream_entry_repository.get_all()
            
            # Sort by date_added (newest first) and limit to 20 most recent
            sorted_transactions = sorted(
                all_transactions,
                key=lambda x: x.date_added if x.date_added else '',
                reverse=True
            )[:20]  # Show 20 most recent transactions
            
            # Populate the table with these transactions
            self._populate_ream_transactions_table(sorted_transactions)
            
            # Ensure the table is visible and properly laid out
            self.ream_transactions_table.setVisible(True)
            self.ream_transactions_table.resizeColumnsToContents()
            self.ream_transactions_table.resizeRowsToContents()
            
        except Exception as e:
            # Don't show error to user as this is automatic
            pass

    # Event handlers for Library Activity
    def _on_view_borrowed_books(self):
        """Handle view borrowed books button click."""
        try:
            student_id = self.borrowed_student_id_input.text().strip()

            if not student_id:
                show_error_message("Validation Error", "Student ID is required", self)
                return

            books = self.student_service.get_student_current_borrowed_books(student_id)
            self._populate_borrowed_books_table(books)

        except Exception as e:
            show_error_message("Error", f"An error occurred: {str(e)}", self)

    def _populate_borrowed_books_table(self, books):
        """Populate the borrowed books table with data."""
        self.borrowed_books_table.setRowCount(0)

        for book in books:
            row_position = self.borrowed_books_table.rowCount()
            self.borrowed_books_table.insertRow(row_position)

            self.borrowed_books_table.setItem(row_position, 0, QTableWidgetItem(str(book.book_id)))
            self.borrowed_books_table.setItem(row_position, 1, QTableWidgetItem(book.title or ""))
            self.borrowed_books_table.setItem(row_position, 2, QTableWidgetItem(book.borrowed_on or ""))
            self.borrowed_books_table.setItem(row_position, 3, QTableWidgetItem(book.due_date or ""))
            self.borrowed_books_table.setItem(row_position, 4, QTableWidgetItem("Borrowed"))

    def _on_view_borrowing_history(self):
        """Handle view borrowing history button click."""
        try:
            student_id = self.history_student_id_input.text().strip()

            if not student_id:
                show_error_message("Validation Error", "Student ID is required", self)
                return

            history = self.student_service.get_student_borrowing_history(student_id)
            self._populate_borrowing_history_table(history)

        except Exception as e:
            show_error_message("Error", f"An error occurred: {str(e)}", self)

    def _populate_borrowing_history_table(self, history):
        """Populate the borrowing history table with data."""
        self.borrowing_history_table.setRowCount(0)

        for record in history:
            row_position = self.borrowing_history_table.rowCount()
            self.borrowing_history_table.insertRow(row_position)

            self.borrowing_history_table.setItem(row_position, 0, QTableWidgetItem(str(record.book_id)))
            self.borrowing_history_table.setItem(row_position, 1, QTableWidgetItem(record.title or ""))
            self.borrowing_history_table.setItem(row_position, 2, QTableWidgetItem(record.borrowed_on or ""))
            self.borrowing_history_table.setItem(row_position, 3, QTableWidgetItem(record.returned_on or ""))
            self.borrowing_history_table.setItem(row_position, 4, QTableWidgetItem(record.return_condition or ""))
            self.borrowing_history_table.setItem(row_position, 5, QTableWidgetItem(str(record.fine_amount or 0)))

    def _on_view_overdue_books(self):
        """Handle view overdue books button click."""
        try:
            student_id = self.overdue_student_id_input.text().strip()

            if not student_id:
                show_error_message("Validation Error", "Student ID is required", self)
                return

            books = self.student_service.get_student_overdue_books(student_id)
            self._populate_overdue_books_table(books)

        except Exception as e:
            show_error_message("Error", f"An error occurred: {str(e)}", self)

    def _populate_overdue_books_table(self, books):
        """Populate the overdue books table with data."""
        self.overdue_books_table.setRowCount(0)

        for book in books:
            row_position = self.overdue_books_table.rowCount()
            self.overdue_books_table.insertRow(row_position)

            self.overdue_books_table.setItem(row_position, 0, QTableWidgetItem(str(book.book_id)))
            self.overdue_books_table.setItem(row_position, 1, QTableWidgetItem(book.title or ""))
            self.overdue_books_table.setItem(row_position, 2, QTableWidgetItem(book.borrowed_on or ""))
            self.overdue_books_table.setItem(row_position, 3, QTableWidgetItem(book.due_date or ""))
            self.overdue_books_table.setItem(row_position, 4, QTableWidgetItem(str(book.days_overdue or 0)))

    # Event handlers for Import/Export
    def _on_browse_import_file(self):
        """Handle browse import file button click."""
        file_dialog = QFileDialog()
        file_path, _ = file_dialog.getOpenFileName(self, "Select Excel File", "", "Excel Files (*.xlsx *.xls)")

        if file_path:
            self.import_file_label.setText(file_path)
            self.import_file_path = file_path

    def _on_import_students(self):
        """Handle import students button click with enhanced feedback."""
        try:
            if not hasattr(self, 'import_file_path'):
                show_error_message("Error", "Please select a file first", self)
                return

            self.import_status_label.setText("Importing students...")
            self.import_status_label.setStyleSheet("color: #2196F3;")
            self.repaint()

            students = self.student_service.import_students_from_excel(self.import_file_path)
            
            if students:
                self.import_status_label.setText(f"✓ Successfully imported {len(students)} students")
                self.import_status_label.setStyleSheet("color: #4CAF50;")
                show_success_message("Success", f"Imported {len(students)} students successfully", self)
                self._refresh_students_table()
            else:
                self.import_status_label.setText("✗ No students were imported")
                self.import_status_label.setStyleSheet("color: #F44336;")
                show_error_message("Error", "No valid student data found in the file", self)

        except Exception as e:
            self.import_status_label.setText(f"✗ Import failed: {str(e)}")
            self.import_status_label.setStyleSheet("color: #F44336;")
            show_error_message("Error", f"Import failed: {str(e)}", self)

    def _on_export_students(self):
        """Handle export students button click with enhanced feedback."""
        try:
            file_dialog = QFileDialog()
            file_path, _ = file_dialog.getSaveFileName(self, "Save Excel File", "students_export.xlsx", "Excel Files (*.xlsx)")

            if file_path:
                self.export_status_label.setText("Exporting students...")
                self.export_status_label.setStyleSheet("color: #2196F3;")
                self.repaint()

                success = self.student_service.export_students_to_excel(file_path)
                
                if success:
                    self.export_status_label.setText(f"✓ Students exported successfully to {file_path}")
                    self.export_status_label.setStyleSheet("color: #4CAF50;")
                    show_success_message("Success", "Students exported successfully", self)
                else:
                    self.export_status_label.setText("✗ Export failed")
                    self.export_status_label.setStyleSheet("color: #F44336;")
                    show_error_message("Error", "Export failed", self)

        except Exception as e:
            self.export_status_label.setText(f"✗ Export failed: {str(e)}")
            self.export_status_label.setStyleSheet("color: #F44336;")
            show_error_message("Error", f"Export failed: {str(e)}", self)

    # Event handlers for Reports
    def _on_generate_student_summary(self):
        """Handle generate student summary button click."""
        try:
            student_id = self.summary_student_id_input.text().strip()

            if not student_id:
                show_error_message("Validation Error", "Student ID is required", self)
                return

            # Get student summary data
            student = self.student_service.get_student_by_id(student_id)
            if not student:
                show_error_message("Error", "Student not found", self)
                return

            # Get library activity summary - convert student_id to int as expected by the service
            library_summary = self.student_service.get_student_library_activity_summary(int(student_id))

            # Get ream balance
            ream_balance = self.student_service.get_student_ream_balance(student_id)

            # Generate summary report
            report_text = f"Student Summary Report for {student.name} (ID: {student.student_id})\n\n"
            stream_display = student.stream if student.stream is not None else "No Stream"
            report_text += f"Stream: {stream_display}\n"
            report_text += f"Ream Balance: {ream_balance}\n\n"
            report_text += "Library Activity:\n"
            report_text += f"  Total Books Borrowed: {library_summary.get('total_books_borrowed', 0)}\n"
            report_text += f"  Current Books Borrowed: {library_summary.get('current_books_borrowed', 0)}\n"
            report_text += f"  Overdue Books: {library_summary.get('overdue_books', 0)}\n"
            report_text += f"  Books Read: {library_summary.get('books_read', 0)}\n"

            self.summary_results_display.setText(report_text)

        except Exception as e:
            show_error_message("Error", f"Failed to generate report: {str(e)}", self)

    def _on_generate_stream_analysis(self):
        """Handle generate stream analysis button click."""
        try:
            stream = self.stream_analysis_stream_input.text().strip()

            if not stream:
                show_error_message("Validation Error", "Stream name is required", self)
                return

            # Get stream analysis data
            stream_data = self.student_service.get_stream_ream_usage(stream)

            # Generate stream analysis report
            report_text = f"Stream Analysis Report for {stream}\n\n"
            report_text += f"Total Students: {stream_data.get('total_students', 0)}\n"
            report_text += f"Total Ream Usage: {stream_data.get('total_ream_usage', 0)}\n"
            report_text += f"Average per Student: {stream_data.get('average_per_student', 0):.2f}\n"

            self.stream_analysis_results_display.setText(report_text)

        except Exception as e:
            show_error_message("Error", f"Failed to generate report: {str(e)}", self)

    def _on_generate_ream_usage_report(self):
        """Handle generate ream usage report button click."""
        try:
            student_id = self.ream_usage_student_id_input.text().strip()

            if not student_id:
                show_error_message("Validation Error", "Student ID is required", self)
                return

            # Get ream usage summary
            ream_summary = self.student_service.get_student_ream_summary(student_id)

            # Generate ream usage report
            report_text = f"Ream Usage Report for Student ID: {student_id}\n\n"
            report_text += f"Current Balance: {ream_summary.get('current_balance', 0)}\n"
            report_text += f"Total Reams Added: {ream_summary.get('total_reams_added', 0)}\n"
            report_text += f"Total Reams Used: {ream_summary.get('total_reams_used', 0)}\n"
            report_text += f"Total Transactions: {ream_summary.get('total_transactions', 0)}\n"
            report_text += f"Average Daily Usage: {ream_summary.get('average_daily_usage', 0):.2f}\n"

            self.ream_usage_results_display.setText(report_text)

        except Exception as e:
            show_error_message("Error", f"Failed to generate report: {str(e)}", self)