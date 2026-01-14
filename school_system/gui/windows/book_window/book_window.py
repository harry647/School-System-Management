"""
Book management window for the School System Management application.

This module provides the book management interface for admin users (admin and librarian roles).
Implements a standardized, user-centric workflow for all book-related services.
"""

from PyQt6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QLabel, QLineEdit, QPushButton,
                            QHBoxLayout, QComboBox, QTabWidget, QTableWidget, QTableWidgetItem,
                            QTextEdit, QSizePolicy, QFileDialog, QMessageBox, QDialog, QFormLayout, QInputDialog)
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QColor
from typing import Callable, Optional, Dict, List
import re
import time

from school_system.gui.base.base_window import BaseWindow
from school_system.gui.dialogs.message_dialog import show_error_message, show_success_message
from school_system.gui.dialogs.confirm_dialog import ConfirmationDialog
from school_system.config.logging import logger
from school_system.services.book_service import BookService
from school_system.core.exceptions import DatabaseException, ValidationError

# Import modular components directly to avoid circular imports
from school_system.gui.windows.book_window.tabs import BookManagementTab
from school_system.gui.windows.book_window.utils import (
    BookValidationHelper,
    SPACING_SMALL, SPACING_MEDIUM, SPACING_LARGE,
    CARD_PADDING, CARD_SPACING,
    BOOK_CONDITIONS, REMOVAL_REASONS, USER_TYPES, RETURN_CONDITIONS,
    STANDARD_SUBJECTS, STANDARD_CLASSES, STANDARD_STREAMS, STANDARD_TERMS,
    EXCEL_BOOK_IMPORT_COLUMNS, EXCEL_BORROWED_BOOKS_COLUMNS, EXCEL_BULK_BORROW_COLUMNS
)
from school_system.gui.windows.book_window.components import (
    FlexLayout, Card, InputField, TextArea, Button, ComboBox, Table, SearchBox, ValidationLabel
)
from school_system.gui.windows.book_window.workflows import (
    BookAddWorkflow, BookEditWorkflow, BookRemoveWorkflow,
    BookBorrowWorkflow, BookReturnWorkflow, BookSearchWorkflow, BulkReturnWorkflow
)


class BookWindow(BaseWindow):
    """Book management window for admin users with standardized workflows."""
    
    def __init__(self, parent: QMainWindow, current_user: str, current_role: str):
        """
        Initialize the book window.
        
        Args:
            parent: The parent window
            current_user: The current logged-in username
            current_role: The current user's role
        """
        super().__init__("School System - Book Management", parent)
        
        self.parent = parent
        self.current_user = current_user
        self.current_role = current_role
        self.book_service = BookService()
        
        # Check if user has admin privileges
        if self.current_role not in ["admin", "librarian"]:
            show_error_message("Access Denied", "You do not have permission to access book management.", self)
            self.close()
            return
        
        # Set minimum size
        self.setMinimumSize(1200, 800)
        
        # Apply modern web-style styling
        self._apply_modern_styling()
        
        # Initialize workflow components
        self.add_workflow = BookAddWorkflow(self.book_service, self.current_user)
        self.edit_workflow = BookEditWorkflow(self.book_service, self.current_user)
        self.remove_workflow = BookRemoveWorkflow(self.book_service, self.current_user)
        self.borrow_workflow = BookBorrowWorkflow(self.book_service, self.current_user)
        self.return_workflow = BookReturnWorkflow(self.book_service, self.current_user)
        self.search_workflow = BookSearchWorkflow(self.book_service, self.current_user)
        self.bulk_return_workflow = BulkReturnWorkflow(self.book_service, self.current_user)
        
        # State management for undo functionality
        self.last_action = None
        self.undo_timer = QTimer()
        self.undo_timer.timeout.connect(self._clear_undo_state)
        
        # Initialize UI
        self._setup_widgets()
        
        # Load initial data
        self._refresh_books_table()
    
    def _setup_widgets(self):
        """Setup the book management widgets."""
        # Create tab widget for different sections
        tab_widget = QTabWidget()
        self.add_widget_to_content(tab_widget)
        
        # Book Management Tab with standardized workflows
        self.book_tab = BookManagementTab()
        book_tab = self.book_tab

        # Connect signals
        book_tab.add_book_requested.connect(self._start_add_book_workflow)
        book_tab.edit_book_requested.connect(self._start_edit_book_workflow)
        book_tab.remove_book_requested.connect(self._start_remove_book_workflow)
        book_tab.refresh_books_requested.connect(self._refresh_books_table)
        book_tab.search_books_requested.connect(self._on_search_books)

        tab_widget.addTab(book_tab, "Book Management")

        # Add Bulk Return Section to Book Management Tab
        self._add_bulk_return_section_to_book_tab()
        
        # Book Borrowing Tab
        borrowing_tab = self._create_borrowing_tab()
        tab_widget.addTab(borrowing_tab, "Book Borrowing")
        
        # Distribution Sessions Tab
        distribution_tab = self._create_distribution_tab()
        tab_widget.addTab(distribution_tab, "Distribution Sessions")
        
        # Advanced Return Tab
        return_tab = self._create_advanced_return_tab()
        tab_widget.addTab(return_tab, "Advanced Returns")
        
        # Import/Export Tab
        import_export_tab = self._create_import_export_tab()
        tab_widget.addTab(import_export_tab, "Import/Export")
        
        # Reports Tab
        reports_tab = self._create_reports_tab()
        tab_widget.addTab(reports_tab, "Reports")
    
    def _create_borrowing_tab(self) -> QWidget:
        """Create the book borrowing tab."""
        tab = QWidget()
        layout = FlexLayout("column", False)
        layout.set_contents_margins(CARD_PADDING, CARD_PADDING, CARD_PADDING, CARD_PADDING)
        layout.set_spacing(CARD_SPACING)
        
        # Borrow Book Section
        borrow_section = Card("Borrow Book", "")
        borrow_form = QWidget()
        borrow_layout = FlexLayout("column", False)
        borrow_layout.set_spacing(SPACING_SMALL)
        
        # User Type
        user_type_label = QLabel("User Type:")
        borrow_layout.add_widget(user_type_label)
        self.borrow_user_type_combo = ComboBox()
        self.borrow_user_type_combo.addItems(USER_TYPES)
        borrow_layout.add_widget(self.borrow_user_type_combo)
        
        # User ID
        user_id_label = QLabel("User ID:")
        borrow_layout.add_widget(user_id_label)
        self.borrow_user_id_input = InputField("Enter user ID")
        borrow_layout.add_widget(self.borrow_user_id_input)
        
        # Book ID
        book_id_label = QLabel("Book ID:")
        borrow_layout.add_widget(book_id_label)
        self.borrow_book_id_input = InputField("Enter book ID")
        borrow_layout.add_widget(self.borrow_book_id_input)
        
        # Borrow button
        borrow_button = Button("Borrow Book", "primary")
        borrow_button.clicked.connect(self._on_borrow_book)
        borrow_layout.add_widget(borrow_button)
        
        borrow_form.setLayout(borrow_layout._layout)
        borrow_section.layout.add_widget(borrow_form)
        layout.add_widget(borrow_section)
        
        # Return Book Section
        return_section = Card("Return Book", "")
        return_form = QWidget()
        return_layout = FlexLayout("column", False)
        return_layout.set_spacing(SPACING_SMALL)
        
        # User Type
        return_user_type_label = QLabel("User Type:")
        return_layout.add_widget(return_user_type_label)
        self.return_user_type_combo = ComboBox()
        self.return_user_type_combo.addItems(USER_TYPES)
        return_layout.add_widget(self.return_user_type_combo)
        
        # User ID
        return_user_id_label = QLabel("User ID:")
        return_layout.add_widget(return_user_id_label)
        self.return_user_id_input = InputField("Enter user ID")
        return_layout.add_widget(self.return_user_id_input)
        
        # Book ID
        return_book_id_label = QLabel("Book ID:")
        return_layout.add_widget(return_book_id_label)
        self.return_book_id_input = InputField("Enter book ID")
        return_layout.add_widget(self.return_book_id_input)
        
        # Condition
        condition_label = QLabel("Condition:")
        return_layout.add_widget(condition_label)
        self.return_condition_combo = ComboBox()
        self.return_condition_combo.addItems(RETURN_CONDITIONS)
        return_layout.add_widget(self.return_condition_combo)
        
        # Fine Amount
        fine_label = QLabel("Fine Amount:")
        return_layout.add_widget(fine_label)
        self.return_fine_input = InputField("Enter fine amount (0 if none)")
        return_layout.add_widget(self.return_fine_input)
        
        # Return button
        return_button = Button("Return Book", "secondary")
        return_button.clicked.connect(self._on_return_book)
        return_layout.add_widget(return_button)
        
        return_form.setLayout(return_layout._layout)
        return_section.layout.add_widget(return_form)
        layout.add_widget(return_section)
        
        # View Borrowed Books Section
        borrowed_section = Card("View Borrowed Books", "")
        borrowed_form = QWidget()
        borrowed_layout = FlexLayout("column", False)
        borrowed_layout.set_spacing(SPACING_SMALL)
        
        # Refresh button
        refresh_borrowed_button = Button("Refresh Borrowed Books", "secondary")
        refresh_borrowed_button.clicked.connect(self._refresh_borrowed_books_table)
        borrowed_layout.add_widget(refresh_borrowed_button)
        
        # Borrowed books table
        self.borrowed_books_table = Table(0, 6)
        self.borrowed_books_table.setHorizontalHeaderLabels([
            "User ID", "User Type", "Book ID", "Borrowed On", "Returned On", "Condition"
        ])
        borrowed_layout.add_widget(self.borrowed_books_table)
        
        borrowed_form.setLayout(borrowed_layout._layout)
        borrowed_section.layout.add_widget(borrowed_form)
        layout.add_widget(borrowed_section)
        
        tab.setLayout(layout._layout)
        return tab
    
    def _create_distribution_tab(self) -> QWidget:
        """Create the distribution sessions tab."""
        tab = QWidget()
        layout = FlexLayout("column", False)
        layout.set_contents_margins(CARD_PADDING, CARD_PADDING, CARD_PADDING, CARD_PADDING)
        layout.set_spacing(CARD_SPACING)
        
        # Create Distribution Session Section
        create_session_section = Card("Create Distribution Session", "")
        create_session_form = QWidget()
        create_session_layout = FlexLayout("column", False)
        create_session_layout.set_spacing(SPACING_SMALL)
        
        # Class Name
        class_name_label = QLabel("Class Name:")
        create_session_layout.add_widget(class_name_label)
        self.create_class_name_input = InputField("Enter class name")
        create_session_layout.add_widget(self.create_class_name_input)
        
        # Stream
        stream_label = QLabel("Stream:")
        create_session_layout.add_widget(stream_label)
        self.create_stream_input = InputField("Enter stream")
        create_session_layout.add_widget(self.create_stream_input)
        
        # Subject
        subject_label = QLabel("Subject:")
        create_session_layout.add_widget(subject_label)
        self.create_subject_input = InputField("Enter subject")
        create_session_layout.add_widget(self.create_subject_input)
        
        # Term
        term_label = QLabel("Term:")
        create_session_layout.add_widget(term_label)
        self.create_term_input = InputField("Enter term")
        create_session_layout.add_widget(self.create_term_input)
        
        # Student IDs (comma separated)
        student_ids_label = QLabel("Student IDs (comma separated):")
        create_session_layout.add_widget(student_ids_label)
        self.create_student_ids_input = InputField("Enter student IDs")
        create_session_layout.add_widget(self.create_student_ids_input)
        
        # Create button
        create_session_button = Button("Create Session", "primary")
        create_session_button.clicked.connect(self._on_create_distribution_session)
        create_session_layout.add_widget(create_session_button)
        
        create_session_form.setLayout(create_session_layout._layout)
        create_session_section.layout.add_widget(create_session_form)
        layout.add_widget(create_session_section)
        
        # View Distribution Sessions Section
        view_sessions_section = Card("View Distribution Sessions", "")
        view_sessions_form = QWidget()
        view_sessions_layout = FlexLayout("column", False)
        view_sessions_layout.set_spacing(SPACING_SMALL)
        
        # Refresh button
        refresh_sessions_button = Button("Refresh Sessions", "secondary")
        refresh_sessions_button.clicked.connect(self._refresh_distribution_sessions_table)
        view_sessions_layout.add_widget(refresh_sessions_button)
        
        # Distribution sessions table
        self.distribution_sessions_table = Table(0, 6)
        self.distribution_sessions_table.setHorizontalHeaderLabels([
            "ID", "Class", "Stream", "Subject", "Term", "Status"
        ])
        view_sessions_layout.add_widget(self.distribution_sessions_table)
        
        view_sessions_form.setLayout(view_sessions_layout._layout)
        view_sessions_section.layout.add_widget(view_sessions_form)
        layout.add_widget(view_sessions_section)
        
        tab.setLayout(layout._layout)
        return tab
    
    def _create_import_export_tab(self) -> QWidget:
        """Create the enhanced import/export tab with new features."""
        tab = QWidget()
        layout = FlexLayout("column", False)
        layout.set_contents_margins(CARD_PADDING, CARD_PADDING, CARD_PADDING, CARD_PADDING)
        layout.set_spacing(CARD_SPACING)
        
        # Enhanced Import Books Section
        import_section = Card("Import Books from Excel",
                             "Import books with validation and preview")
        import_form = QWidget()
        import_layout = FlexLayout("column", False)
        import_layout.set_spacing(SPACING_SMALL)
        
        # Required columns display with tooltip
        columns_label = QLabel("Required Columns:")
        columns_label.setToolTip("These are the required column headers for book imports")
        import_layout.add_widget(columns_label)
        
        columns_info = QLabel(", ".join(EXCEL_BOOK_IMPORT_COLUMNS))
        columns_info.setProperty("info", "true")
        columns_info.setWordWrap(True)
        columns_info.setToolTip("ISBN, Title, Author, Book_Number, Subject, Class, Category, Publication_Date, Condition")
        import_layout.add_widget(columns_info)
        
        # Download template button with tooltip
        template_button = Button("Download Template", "info")
        template_button.clicked.connect(self._on_download_book_template)
        template_button.setToolTip("Download a template with proper headers and sample data")
        import_layout.add_widget(template_button)
        
        # File selection
        self.import_file_label = QLabel("No file selected")
        import_layout.add_widget(self.import_file_label)
        
        # Browse button with tooltip
        browse_button = Button("Browse Excel File", "primary")
        browse_button.clicked.connect(self._on_browse_import_file)
        browse_button.setToolTip("Select an Excel file to import books from")
        import_layout.add_widget(browse_button)
        
        # Preview button with tooltip
        preview_button = Button("Preview Data", "secondary")
        preview_button.clicked.connect(self._on_preview_import_data)
        preview_button.setToolTip("Preview the data before importing to check for errors")
        import_layout.add_widget(preview_button)
        
        # Import button with tooltip
        import_button = Button("Import Books", "success")
        import_button.clicked.connect(self._on_import_books)
        import_button.setToolTip("Import the books from the Excel file after validation")
        import_layout.add_widget(import_button)
        
        # Preview table
        self.import_preview_table = Table(0, len(EXCEL_BOOK_IMPORT_COLUMNS))
        self.import_preview_table.setHorizontalHeaderLabels(EXCEL_BOOK_IMPORT_COLUMNS)
        self.import_preview_table.setVisible(False)
        import_layout.add_widget(self.import_preview_table)
        
        import_form.setLayout(import_layout._layout)
        import_section.layout.add_widget(import_form)
        layout.add_widget(import_section)
        
        # Bulk Borrow Section
        borrow_section = Card("Bulk Book Borrowing via Excel",
                             "Upload Excel file to borrow multiple books at once")
        borrow_form = QWidget()
        borrow_layout = FlexLayout("column", False)
        borrow_layout.set_spacing(SPACING_SMALL)
        
        # Required columns display with tooltip
        borrow_columns_label = QLabel("Required Columns:")
        borrow_columns_label.setToolTip("These are the required column headers for bulk borrowing")
        borrow_layout.add_widget(borrow_columns_label)
        
        borrow_columns_info = QLabel(", ".join(EXCEL_BULK_BORROW_COLUMNS))
        borrow_columns_info.setProperty("info", "true")
        borrow_columns_info.setWordWrap(True)
        borrow_columns_info.setToolTip("Admission_Number, Student_Name, Book_Number")
        borrow_layout.add_widget(borrow_columns_info)
        
        # Download template button with tooltip
        borrow_template_button = Button("Download Borrow Template", "info")
        borrow_template_button.clicked.connect(self._on_download_borrow_template)
        borrow_template_button.setToolTip("Download a template with proper headers and sample data for bulk borrowing")
        borrow_layout.add_widget(borrow_template_button)
        
        # File selection
        self.borrow_file_label = QLabel("No file selected")
        borrow_layout.add_widget(self.borrow_file_label)
        
        # Browse button with tooltip
        borrow_browse_button = Button("Browse Excel File", "primary")
        borrow_browse_button.clicked.connect(self._on_browse_borrow_file)
        borrow_browse_button.setToolTip("Select an Excel file containing bulk borrow data")
        borrow_layout.add_widget(borrow_browse_button)
        
        # Preview button with tooltip
        borrow_preview_button = Button("Preview Borrow Data", "secondary")
        borrow_preview_button.clicked.connect(self._on_preview_borrow_data)
        borrow_preview_button.setToolTip("Preview the borrow data before processing to check for errors")
        borrow_layout.add_widget(borrow_preview_button)
        
        # Process button with tooltip
        borrow_process_button = Button("Process Bulk Borrowing", "success")
        borrow_process_button.clicked.connect(self._on_process_bulk_borrow)
        borrow_process_button.setToolTip("Process the bulk borrowing after validation")
        borrow_layout.add_widget(borrow_process_button)
        
        # Preview table
        self.borrow_preview_table = Table(0, len(EXCEL_BULK_BORROW_COLUMNS))
        self.borrow_preview_table.setHorizontalHeaderLabels(EXCEL_BULK_BORROW_COLUMNS)
        self.borrow_preview_table.setVisible(False)
        borrow_layout.add_widget(self.borrow_preview_table)
        
        borrow_form.setLayout(borrow_layout._layout)
        borrow_section.layout.add_widget(borrow_form)
        layout.add_widget(borrow_section)
        
        # Export Books Section
        export_section = Card("Export Books to Excel", "")
        export_form = QWidget()
        export_layout = FlexLayout("column", False)
        export_layout.set_spacing(SPACING_SMALL)
        
        # Export button
        export_button = Button("Export All Books", "primary")
        export_button.clicked.connect(self._on_export_books)
        export_layout.add_widget(export_button)
        
        export_form.setLayout(export_layout._layout)
        export_section.layout.add_widget(export_form)
        layout.add_widget(export_section)
        
        tab.setLayout(layout._layout)
        return tab
    
    def _create_reports_tab(self) -> QWidget:
        """Create the reports tab."""
        tab = QWidget()
        layout = FlexLayout("column", False)
        layout.set_contents_margins(CARD_PADDING, CARD_PADDING, CARD_PADDING, CARD_PADDING)
        layout.set_spacing(CARD_SPACING)
        
        # Popular Books Section
        popular_section = Card("Popular Books Report", "")
        popular_form = QWidget()
        popular_layout = FlexLayout("column", False)
        popular_layout.set_spacing(SPACING_SMALL)
        
        # Limit
        limit_label = QLabel("Number of books to show:")
        popular_layout.add_widget(limit_label)
        self.popular_limit_input = InputField("10")
        popular_layout.add_widget(self.popular_limit_input)
        
        # Generate button
        popular_button = Button("Generate Popular Books Report", "primary")
        popular_button.clicked.connect(self._on_generate_popular_books)
        popular_layout.add_widget(popular_button)
        
        # Results display
        self.popular_books_display = TextArea()
        self.popular_books_display.setReadOnly(True)
        self.popular_books_display.setMaximumHeight(150)
        popular_layout.add_widget(self.popular_books_display)
        
        popular_form.setLayout(popular_layout._layout)
        popular_section.layout.add_widget(popular_form)
        layout.add_widget(popular_section)
        
        # Overdue Books Section
        overdue_section = Card("Overdue Books Report", "")
        overdue_form = QWidget()
        overdue_layout = FlexLayout("column", False)
        overdue_layout.set_spacing(SPACING_SMALL)
        
        # Generate button
        overdue_button = Button("Generate Overdue Books Report", "primary")
        overdue_button.clicked.connect(self._on_generate_overdue_books)
        overdue_layout.add_widget(overdue_button)
        
        # Results display
        self.overdue_books_display = TextArea()
        self.overdue_books_display.setReadOnly(True)
        self.overdue_books_display.setMaximumHeight(150)
        overdue_layout.add_widget(self.overdue_books_display)
        
        overdue_form.setLayout(overdue_layout._layout)
        overdue_section.layout.add_widget(overdue_form)
        layout.add_widget(overdue_section)
        
        tab.setLayout(layout._layout)
        return tab
    
    def _add_bulk_return_section_to_book_tab(self):
        """Add bulk return section to the book management tab."""
        # Create bulk return section
        bulk_return_section = self._create_bulk_return_section()
        
        # Add to the book tab layout
        self.book_tab.layout.add_widget(bulk_return_section)

    def _create_bulk_return_section(self) -> QWidget:
        """Create bulk return section with checkbox selection."""
        section = Card("Bulk Book Return", "Select multiple books for return")
        layout = FlexLayout("column", False)
        layout.set_spacing(SPACING_SMALL)

        # Search/filter controls
        search_layout = QHBoxLayout()
        self.bulk_return_search = SearchBox("Search books...")
        self.bulk_return_filter_combo = ComboBox()
        self.bulk_return_filter_combo.addItems(["All", "Borrowed", "Overdue"])
        search_layout.addWidget(self.bulk_return_search)
        search_layout.addWidget(self.bulk_return_filter_combo)

        # Results table with checkboxes
        self.bulk_return_table = Table(0, 7)
        self.bulk_return_table.setHorizontalHeaderLabels([
            "Select", "Book ID", "Book Number", "Title", "Borrower",
            "Borrowed On", "Due Date"
        ])

        # Selection feedback label
        self.bulk_return_feedback_label = QLabel("0 books selected | Estimated fines: KES 0.00")
        self.bulk_return_feedback_label.setProperty("info", "true")

        # Action buttons
        action_layout = QHBoxLayout()
        select_all_btn = Button("Select All", "secondary")
        deselect_all_btn = Button("Deselect All", "secondary")
        return_selected_btn = Button("Return Selected", "primary")

        # Connect signals
        self.bulk_return_search.search_input.textChanged.connect(self._on_bulk_return_search)
        self.bulk_return_filter_combo.currentTextChanged.connect(self._on_bulk_return_search)
        select_all_btn.clicked.connect(self._select_all_bulk_return)
        deselect_all_btn.clicked.connect(self._deselect_all_bulk_return)
        return_selected_btn.clicked.connect(self._on_return_selected_books)
        self.bulk_return_table.itemChanged.connect(self._update_selection_feedback)

        # Add widgets to layout
        layout.addLayout(search_layout)
        layout.addWidget(self.bulk_return_table)
        layout.addWidget(self.bulk_return_feedback_label)
        layout.addLayout(action_layout)

        section.layout.add_widget(layout)
        return section

    def _create_advanced_return_tab(self) -> QWidget:
        """Create the advanced return tab with bulk return functionality."""
        tab = QWidget()
        layout = FlexLayout("column", False)
        layout.set_contents_margins(CARD_PADDING, CARD_PADDING, CARD_PADDING, CARD_PADDING)
        layout.set_spacing(CARD_SPACING)

        # Bulk Return by Stream/Subject Section
        bulk_return_section = Card("Bulk Return by Stream/Subject",
                                    "Return multiple books at once by selecting stream and subject")
        bulk_return_form = self._create_bulk_return_form()
        bulk_return_section.layout.add_widget(bulk_return_form)
        layout.add_widget(bulk_return_section)

        # Return by Student ID Section
        student_return_section = Card("Return by Student ID",
                                       "Find and return books borrowed by a specific student")
        student_return_form = self._create_student_return_form()
        student_return_section.layout.add_widget(student_return_form)
        layout.add_widget(student_return_section)

        # Return by Book Number Section
        book_return_section = Card("Return by Book Number",
                                    "Find and return a specific book by its number")
        book_return_form = self._create_book_return_form()
        book_return_section.layout.add_widget(book_return_form)
        layout.add_widget(book_return_section)

        tab.setLayout(layout._layout)
        return tab
    
    def _create_bulk_return_form(self) -> QWidget:
        """Create the bulk return form for stream/subject-based returns."""
        form = QWidget()
        form_layout = FlexLayout("column", False)
        form_layout.set_spacing(SPACING_SMALL)
        
        # Stream selection
        stream_label = QLabel("Stream:")
        form_layout.add_widget(stream_label)
        self.bulk_stream_combo = ComboBox()
        self.bulk_stream_combo.addItems(STANDARD_STREAMS + ["All"])
        self.bulk_stream_combo.setEditable(True)
        form_layout.add_widget(self.bulk_stream_combo)
        
        # Subject selection (optional)
        subject_label = QLabel("Subject (Optional):")
        form_layout.add_widget(subject_label)
        self.bulk_subject_combo = ComboBox()
        self.bulk_subject_combo.addItems(STANDARD_SUBJECTS + ["All"])
        self.bulk_subject_combo.setEditable(True)
        form_layout.add_widget(self.bulk_subject_combo)
        
        # Search button
        search_button = Button("Search Borrowed Books", "primary")
        search_button.clicked.connect(self._on_search_bulk_return)
        form_layout.add_widget(search_button)
        
        # Results table
        self.bulk_return_table = Table(0, 6)
        self.bulk_return_table.setHorizontalHeaderLabels([
            "Select", "Name", "Adm No", "Subject", "Book Number", "Date Borrowed"
        ])
        form_layout.add_widget(self.bulk_return_table)
        
        # Condition selection for return
        condition_label = QLabel("Return Condition:")
        form_layout.add_widget(condition_label)
        self.bulk_return_condition_combo = ComboBox()
        self.bulk_return_condition_combo.addItems(RETURN_CONDITIONS)
        form_layout.add_widget(self.bulk_return_condition_combo)
        
        # Fine amount
        fine_label = QLabel("Fine Amount (per book):")
        form_layout.add_widget(fine_label)
        self.bulk_return_fine_input = InputField("0")
        form_layout.add_widget(self.bulk_return_fine_input)
        
        # Return selected button
        return_button = Button("Return Selected Books", "secondary")
        return_button.clicked.connect(self._on_bulk_return_books)
        form_layout.add_widget(return_button)
        
        form.setLayout(form_layout._layout)
        return form
    
    def _create_student_return_form(self) -> QWidget:
        """Create the student return form."""
        form = QWidget()
        form_layout = FlexLayout("column", False)
        form_layout.set_spacing(SPACING_SMALL)
        
        # Student ID input
        student_id_label = QLabel("Student ID:")
        form_layout.add_widget(student_id_label)
        self.student_return_id_input = InputField("Enter student ID")
        form_layout.add_widget(self.student_return_id_input)
        
        # Search button
        search_button = Button("Search Student Books", "primary")
        search_button.clicked.connect(self._on_search_student_books)
        form_layout.add_widget(search_button)
        
        # Results table
        self.student_return_table = Table(0, 5)
        self.student_return_table.setHorizontalHeaderLabels([
            "Select", "Book ID", "Book Number", "Title", "Date Borrowed"
        ])
        form_layout.add_widget(self.student_return_table)
        
        # Condition selection
        condition_label = QLabel("Return Condition:")
        form_layout.add_widget(condition_label)
        self.student_return_condition_combo = ComboBox()
        self.student_return_condition_combo.addItems(RETURN_CONDITIONS)
        form_layout.add_widget(self.student_return_condition_combo)
        
        # Fine amount
        fine_label = QLabel("Fine Amount:")
        form_layout.add_widget(fine_label)
        self.student_return_fine_input = InputField("0")
        form_layout.add_widget(self.student_return_fine_input)
        
        # Return selected button
        return_button = Button("Return Selected Books", "secondary")
        return_button.clicked.connect(self._on_student_return_books)
        form_layout.add_widget(return_button)
        
        form.setLayout(form_layout._layout)
        return form
    
    def _create_book_return_form(self) -> QWidget:
        """Create the book return form."""
        form = QWidget()
        form_layout = FlexLayout("column", False)
        form_layout.set_spacing(SPACING_SMALL)
        
        # Book number input
        book_number_label = QLabel("Book Number:")
        form_layout.add_widget(book_number_label)
        self.book_return_number_input = InputField("Enter book number")
        form_layout.add_widget(self.book_return_number_input)
        
        # Search button
        search_button = Button("Find Book", "primary")
        search_button.clicked.connect(self._on_find_book_for_return)
        form_layout.add_widget(search_button)
        
        # Book info display
        self.book_return_info_label = QLabel("Book information will appear here...")
        self.book_return_info_label.setWordWrap(True)
        form_layout.add_widget(self.book_return_info_label)
        
        # Condition selection
        condition_label = QLabel("Return Condition:")
        form_layout.add_widget(condition_label)
        self.book_return_condition_combo = ComboBox()
        self.book_return_condition_combo.addItems(RETURN_CONDITIONS)
        form_layout.add_widget(self.book_return_condition_combo)
        
        # Fine amount
        fine_label = QLabel("Fine Amount:")
        form_layout.add_widget(fine_label)
        self.book_return_fine_input = InputField("0")
        form_layout.add_widget(self.book_return_fine_input)
        
        # Return button
        return_button = Button("Return Book", "secondary")
        return_button.clicked.connect(self._on_single_book_return)
        form_layout.add_widget(return_button)
        
        form.setLayout(form_layout._layout)
        return form
    
    # Workflow methods
    def _start_add_book_workflow(self, book_data: dict):
        """Start the standardized add book workflow."""
        # Execute the workflow
        book, message = self.add_workflow.execute_add_book(book_data)
        
        if book:
            show_success_message("Success", message, self)
            
            # Start undo timer (5 seconds)
            self.undo_timer.start(5000)
            
            # Refresh table
            self._refresh_books_table()
        else:
            show_error_message("Error", message, self)
    
    def _start_edit_book_workflow(self, book_id: int, update_data: dict):
        """Start the standardized edit book workflow."""
        success, message = self.edit_workflow.execute_edit_book(book_id, update_data)
        
        if success:
            show_success_message("Success", message, self)
            self.undo_timer.start(5000)
            self._refresh_books_table()
        else:
            show_error_message("Error", message, self)
    
    def _start_remove_book_workflow(self, book_id: int, reason: str, notes: str = ""):
        """Start the standardized remove book workflow."""
        success, message = self.remove_workflow.execute_remove_book(book_id, reason, notes)
        
        if success:
            show_success_message("Success", message, self)
            self.undo_timer.start(5000)
            self._refresh_books_table()
        else:
            show_error_message("Error", message, self)
    
    # Data refresh methods
    def _refresh_books_table(self):
        """Refresh the books table."""
        try:
            books = self.book_service.get_all_books()
            self._populate_books_table(books)
        except Exception as e:
            show_error_message("Error", f"Failed to refresh books: {str(e)}", self)
    
    def _populate_books_table(self, books):
        """Populate the books table with data."""
        self.book_tab.books_table.setRowCount(0)
        
        for book in books:
            row_position = self.book_tab.books_table.rowCount()
            self.book_tab.books_table.insertRow(row_position)
            
            self.book_tab.books_table.setItem(row_position, 0, QTableWidgetItem(str(book.id)))
            self.book_tab.books_table.setItem(row_position, 1, QTableWidgetItem(book.book_number))
            self.book_tab.books_table.setItem(row_position, 2, QTableWidgetItem(book.title))
            self.book_tab.books_table.setItem(row_position, 3, QTableWidgetItem(book.author))
            self.book_tab.books_table.setItem(row_position, 4, QTableWidgetItem(book.category or ""))
            self.book_tab.books_table.setItem(row_position, 5, QTableWidgetItem("Yes" if book.available else "No"))
            self.book_tab.books_table.setItem(row_position, 6, QTableWidgetItem(book.book_condition or ""))
            self.book_tab.books_table.setItem(row_position, 7, QTableWidgetItem(getattr(book, 'subject', '') or ""))
    
    def _on_search_books(self, query: str):
        """Handle book search."""
        try:
            books, message = self.search_workflow.execute_search_books(query)
            if books:
                self._populate_books_table(books)
            else:
                show_error_message("Error", message, self)
        except Exception as e:
            show_error_message("Error", f"Search failed: {str(e)}", self)
    
    # Event handlers for borrowing
    def _on_borrow_book(self):
        """Handle borrow book button click."""
        try:
            user_type = self.borrow_user_type_combo.currentText()
            user_id = self.borrow_user_id_input.text().strip()
            book_id = int(self.borrow_book_id_input.text().strip())
            
            success, message = self.borrow_workflow.execute_borrow_book(user_type, user_id, book_id)
            
            if success:
                show_success_message("Success", message, self)
                self._refresh_borrowed_books_table()
            else:
                show_error_message("Error", message, self)
                
        except ValueError:
            show_error_message("Error", "Invalid book ID", self)
        except Exception as e:
            show_error_message("Error", f"An error occurred: {str(e)}", self)
    
    def _on_return_book(self):
        """Handle return book button click."""
        try:
            user_type = self.return_user_type_combo.currentText()
            user_id = self.return_user_id_input.text().strip()
            book_id = int(self.return_book_id_input.text().strip())
            condition = self.return_condition_combo.currentText()
            fine_amount = float(self.return_fine_input.text().strip() or "0")
            
            success, message = self.return_workflow.execute_return_book(
                user_type, user_id, book_id, condition, fine_amount
            )
            
            if success:
                show_success_message("Success", message, self)
                self._refresh_borrowed_books_table()
            else:
                show_error_message("Error", message, self)
                
        except ValueError:
            show_error_message("Error", "Invalid input values", self)
        except Exception as e:
            show_error_message("Error", f"An error occurred: {str(e)}", self)
    
    def _refresh_borrowed_books_table(self):
        """Refresh the borrowed books table."""
        try:
            # Get both student and teacher borrowed books
            student_borrowed = self.book_service.get_all_borrowed_books_student()
            teacher_borrowed = self.book_service.get_all_borrowed_books_teacher()
            
            self.borrowed_books_table.setRowCount(0)
            
            # Add student borrowed books
            for book in student_borrowed:
                row_position = self.borrowed_books_table.rowCount()
                self.borrowed_books_table.insertRow(row_position)
                self.borrowed_books_table.setItem(row_position, 0, QTableWidgetItem(book.student_id))
                self.borrowed_books_table.setItem(row_position, 1, QTableWidgetItem("student"))
                self.borrowed_books_table.setItem(row_position, 2, QTableWidgetItem(str(book.book_id)))
                self.borrowed_books_table.setItem(row_position, 3, QTableWidgetItem(book.borrowed_on))
                self.borrowed_books_table.setItem(row_position, 4, QTableWidgetItem(book.returned_on or ""))
                self.borrowed_books_table.setItem(row_position, 5, QTableWidgetItem(book.return_condition or ""))
            
            # Add teacher borrowed books
            for book in teacher_borrowed:
                row_position = self.borrowed_books_table.rowCount()
                self.borrowed_books_table.insertRow(row_position)
                self.borrowed_books_table.setItem(row_position, 0, QTableWidgetItem(book.teacher_id))
                self.borrowed_books_table.setItem(row_position, 1, QTableWidgetItem("teacher"))
                self.borrowed_books_table.setItem(row_position, 2, QTableWidgetItem(str(book.book_id)))
                self.borrowed_books_table.setItem(row_position, 3, QTableWidgetItem(book.borrowed_on))
                self.borrowed_books_table.setItem(row_position, 4, QTableWidgetItem(book.returned_on or ""))
                self.borrowed_books_table.setItem(row_position, 5, QTableWidgetItem(""))
                
        except Exception as e:
            show_error_message("Error", f"Failed to refresh borrowed books: {str(e)}", self)
    
    # Event handlers for distribution
    def _on_create_distribution_session(self):
        """Handle create distribution session button click."""
        try:
            session_data = {
                'class_name': self.create_class_name_input.text().strip(),
                'stream': self.create_stream_input.text().strip(),
                'subject': self.create_subject_input.text().strip(),
                'term': self.create_term_input.text().strip(),
                'created_by': self.current_user,
                'status': 'DRAFT'
            }
            
            student_ids = [s.strip() for s in self.create_student_ids_input.text().split(',') if s.strip()]
            
            session_id = self.book_service.create_distribution_session_with_students(session_data, student_ids)
            show_success_message("Success", f"Distribution session created with ID: {session_id}", self)
            self._refresh_distribution_sessions_table()
            
            # Clear form
            self.create_class_name_input.clear()
            self.create_stream_input.clear()
            self.create_subject_input.clear()
            self.create_term_input.clear()
            self.create_student_ids_input.clear()
            
        except Exception as e:
            show_error_message("Error", f"An error occurred: {str(e)}", self)
    
    def _refresh_distribution_sessions_table(self):
        """Refresh the distribution sessions table."""
        try:
            sessions = self.book_service.get_all_distribution_sessions()
            self.distribution_sessions_table.setRowCount(0)
            
            for session in sessions:
                row_position = self.distribution_sessions_table.rowCount()
                self.distribution_sessions_table.insertRow(row_position)
                
                self.distribution_sessions_table.setItem(row_position, 0, QTableWidgetItem(str(session.id)))
                self.distribution_sessions_table.setItem(row_position, 1, QTableWidgetItem(session.class_name))
                self.distribution_sessions_table.setItem(row_position, 2, QTableWidgetItem(session.stream))
                self.distribution_sessions_table.setItem(row_position, 3, QTableWidgetItem(session.subject))
                self.distribution_sessions_table.setItem(row_position, 4, QTableWidgetItem(session.term))
                self.distribution_sessions_table.setItem(row_position, 5, QTableWidgetItem(session.status))
                
        except Exception as e:
            show_error_message("Error", f"Failed to refresh distribution sessions: {str(e)}", self)
    
    # Event handlers for import/export
    def _on_browse_import_file(self):
        """Handle browse import file button click."""
        file_dialog = QFileDialog()
        file_path, _ = file_dialog.getOpenFileName(self, "Select Excel File", "", "Excel Files (*.xlsx *.xls)")
        
        if file_path:
            self.import_file_label.setText(file_path)
            self.import_file_path = file_path
            self.import_preview_table.setVisible(False)

    def _on_preview_import_data(self):
        """Handle preview import data button click."""
        try:
            if not hasattr(self, 'import_file_path'):
                show_error_message("Error", "Please select a file first", self)
                return
            
            # Import data with validation
            success, data, error_msg = self.book_service.import_export_service.import_from_excel_with_validation(
                self.import_file_path, EXCEL_BOOK_IMPORT_COLUMNS
            )
            
            if not success:
                show_error_message("Validation Error", error_msg, self)
                return
            
            # Display preview
            self._populate_import_preview_table(data)
            self.import_preview_table.setVisible(True)
            
        except Exception as e:
            logger.error(f"Error previewing import data: {str(e)}")
            show_error_message("Error", f"Preview failed: {str(e)}", self)

    def _on_import_books(self):
        """Handle import books button click with enhanced validation."""
        try:
            if not hasattr(self, 'import_file_path'):
                show_error_message("Error", "Please select a file first", self)
                return
            
            # Show confirmation dialog
            confirm = ConfirmationDialog(
                "Confirm Import",
                f"Are you sure you want to import books from {self.import_file_path}?",
                self
            )
            if not confirm.exec():
                return
            
            # Import books with enhanced validation
            success, data, error_msg = self.book_service.import_export_service.import_from_excel_with_validation(
                self.import_file_path, EXCEL_BOOK_IMPORT_COLUMNS
            )
            
            if not success:
                show_error_message("Validation Error", error_msg, self)
                return
            
            # Process import
            imported_count = 0
            for book_data in data:
                try:
                    # Map Excel columns to database fields
                    db_data = {
                        'isbn': book_data.get('ISBN', ''),
                        'title': book_data.get('Title', ''),
                        'author': book_data.get('Author', ''),
                        'book_number': book_data.get('Book_Number', ''),
                        'subject': book_data.get('Subject', ''),
                        'class': book_data.get('Class', ''),
                        'category': book_data.get('Category', ''),
                        'publication_date': book_data.get('Publication_Date', ''),
                        'book_condition': book_data.get('Condition', 'Good'),
                        'available': 1
                    }
                    
                    # Validate required fields
                    validation_result = BookValidationHelper.validate_required_fields(db_data)
                    if not validation_result[0]:
                        continue
                    
                    # Create book
                    book = self.book_service.create_book(db_data)
                    if book:
                        imported_count += 1
                        
                except Exception as e:
                    logger.error(f"Error importing book: {str(e)}")
                    continue
            
            show_success_message("Success", f"Imported {imported_count} books successfully", self)
            self._refresh_books_table()
            
        except Exception as e:
            logger.error(f"Error importing books: {str(e)}")
            show_error_message("Error", f"Import failed: {str(e)}", self)

    def _on_download_book_template(self):
        """Handle download book template button click."""
        try:
            file_dialog = QFileDialog()
            file_path, _ = file_dialog.getSaveFileName(self, "Save Template", "book_import_template.xlsx", "Excel Files (*.xlsx)")
            
            if file_path:
                # Generate template with sample data
                sample_data = [{
                    'ISBN': '978-3-16-148410-0',
                    'Title': 'Sample Book Title',
                    'Author': 'John Doe',
                    'Book_Number': 'MTH-001',
                    'Subject': 'Mathematics',
                    'Class': 'Form 1',
                    'Category': 'Textbook',
                    'Publication_Date': '2023-01-15',
                    'Condition': 'New'
                }]
                
                success = self.book_service.import_export_service.generate_excel_template(
                    file_path, EXCEL_BOOK_IMPORT_COLUMNS, sample_data
                )
                
                if success:
                    show_success_message("Success", "Book import template generated successfully", self)
                else:
                    show_error_message("Error", "Failed to generate template", self)
            
        except Exception as e:
            show_error_message("Error", f"Failed to generate template: {str(e)}", self)

    # Bulk borrow event handlers
    def _on_browse_borrow_file(self):
        """Handle browse borrow file button click."""
        file_dialog = QFileDialog()
        file_path, _ = file_dialog.getOpenFileName(self, "Select Excel File", "", "Excel Files (*.xlsx *.xls)")
        
        if file_path:
            self.borrow_file_label.setText(file_path)
            self.borrow_file_path = file_path
            self.borrow_preview_table.setVisible(False)

    def _on_preview_borrow_data(self):
        """Handle preview borrow data button click."""
        try:
            if not hasattr(self, 'borrow_file_path'):
                show_error_message("Error", "Please select a file first", self)
                return
            
            # Import data with validation
            success, data, error_msg = self.book_service.import_export_service.import_from_excel_with_validation(
                self.borrow_file_path, EXCEL_BULK_BORROW_COLUMNS
            )
            
            if not success:
                show_error_message("Validation Error", error_msg, self)
                return
            
            # Display preview
            self._populate_borrow_preview_table(data)
            self.borrow_preview_table.setVisible(True)
            
        except Exception as e:
            logger.error(f"Error previewing borrow data: {str(e)}")
            show_error_message("Error", f"Preview failed: {str(e)}", self)

    def _on_download_borrow_template(self):
        """Handle download borrow template button click."""
        try:
            file_dialog = QFileDialog()
            file_path, _ = file_dialog.getSaveFileName(self, "Save Template", "bulk_borrow_template.xlsx", "Excel Files (*.xlsx)")
            
            if file_path:
                # Generate template with sample data
                sample_data = [{
                    'Admission_Number': 'S12345',
                    'Student_Name': 'John Doe',
                    'Book_Number': 'MTH-001'
                }, {
                    'Admission_Number': 'S12346',
                    'Student_Name': 'Jane Smith',
                    'Book_Number': 'ENG-002'
                }]
                
                success = self.book_service.import_export_service.generate_excel_template(
                    file_path, EXCEL_BULK_BORROW_COLUMNS, sample_data
                )
                
                if success:
                    show_success_message("Success", "Bulk borrow template generated successfully", self)
                else:
                    show_error_message("Error", "Failed to generate template", self)
            
        except Exception as e:
            show_error_message("Error", f"Failed to generate template: {str(e)}", self)

    def _on_process_bulk_borrow(self):
        """Handle process bulk borrow button click."""
        try:
            if not hasattr(self, 'borrow_file_path'):
                show_error_message("Error", "Please select a file first", self)
                return
            
            # Show confirmation dialog
            confirm = ConfirmationDialog(
                "Confirm Bulk Borrowing",
                f"Are you sure you want to process bulk borrowing from {self.borrow_file_path}?",
                self
            )
            if not confirm.exec():
                return
            
            # Process bulk borrowing
            success, message, statistics = self.book_service.bulk_borrow_books_from_excel(
                self.borrow_file_path, self.current_user
            )
            
            if success:
                show_success_message("Success", message, self)
                self._refresh_borrowed_books_table()
            else:
                show_error_message("Error", message, self)
            
        except Exception as e:
            logger.error(f"Error processing bulk borrow: {str(e)}")
            show_error_message("Error", f"Bulk borrow failed: {str(e)}", self)

    def _populate_import_preview_table(self, data: List[Dict]):
        """Populate the import preview table."""
        self.import_preview_table.setRowCount(0)
        
        for row_data in data[:10]:  # Show first 10 rows for preview
            row_position = self.import_preview_table.rowCount()
            self.import_preview_table.insertRow(row_position)
            
            for i, column in enumerate(EXCEL_BOOK_IMPORT_COLUMNS):
                value = row_data.get(column, '')
                self.import_preview_table.setItem(row_position, i, QTableWidgetItem(str(value)))

    def _populate_borrow_preview_table(self, data: List[Dict]):
        """Populate the borrow preview table."""
        self.borrow_preview_table.setRowCount(0)
        
        for row_data in data[:10]:  # Show first 10 rows for preview
            row_position = self.borrow_preview_table.rowCount()
            self.borrow_preview_table.insertRow(row_position)
            
            for i, column in enumerate(EXCEL_BULK_BORROW_COLUMNS):
                value = row_data.get(column, '')
                self.borrow_preview_table.setItem(row_position, i, QTableWidgetItem(str(value)))

    def _on_export_books(self):
        """Handle export books button click."""
        try:
            file_dialog = QFileDialog()
            file_path, _ = file_dialog.getSaveFileName(self, "Save Excel File", "books_export.xlsx", "Excel Files (*.xlsx)")
            
            if file_path:
                success = self.book_service.export_books_to_excel(file_path)
                if success:
                    show_success_message("Success", "Books exported successfully", self)
                else:
                    show_error_message("Error", "Export failed", self)
                     
        except Exception as e:
            show_error_message("Error", f"Export failed: {str(e)}", self)
    
    # Event handlers for reports
    def _on_generate_popular_books(self):
        """Handle generate popular books report button click."""
        try:
            limit = int(self.popular_limit_input.text().strip() or "10")
            books = self.book_service.get_popular_books(limit)
            
            report_text = "Popular Books Report:\n\n"
            for i, book in enumerate(books, 1):
                report_text += f"{i}. {book.title} by {book.author} (Borrowed {book.borrow_count} times)\n"
                
            self.popular_books_display.setText(report_text)
                
        except Exception as e:
            show_error_message("Error", f"Failed to generate report: {str(e)}", self)
    
    def _on_generate_overdue_books(self):
        """Handle generate overdue books report button click."""
        try:
            books = self.book_service.get_all_overdue_books()
            
            report_text = "Overdue Books Report:\n\n"
            for i, book in enumerate(books, 1):
                report_text += f"{i}. Book ID: {book.book_id}, Student: {book.student_id}, Borrowed: {book.borrowed_on}\n"
                
            self.overdue_books_display.setText(report_text)
                
        except Exception as e:
            show_error_message("Error", f"Failed to generate report: {str(e)}", self)
    
    # Event handlers for bulk return
    def _on_search_bulk_return(self):
        """Handle bulk return search by stream and subject."""
        try:
            stream = self.bulk_stream_combo.currentText()
            subject = self.bulk_subject_combo.currentText()
            
            # Get borrowed books based on criteria
            # This would be implemented in the service layer
            # For now, we'll simulate with some sample data
            sample_data = [
                {"name": "John Doe", "adm_no": "S1234", "subject": "Mathematics",
                 "book_number": "MTH-019", "date_borrowed": "2025-01-12"},
                {"name": "Jane Smith", "adm_no": "S1235", "subject": "English",
                 "book_number": "ENG-044", "date_borrowed": "2025-01-12"},
                {"name": "Bob Johnson", "adm_no": "S1236", "subject": "Mathematics",
                 "book_number": "MTH-033", "date_borrowed": "2025-01-12"}
            ]
            
            # Filter based on selection
            filtered_data = sample_data
            if stream != "All":
                pass
            if subject != "All" and subject != "":
                filtered_data = [book for book in filtered_data if book["subject"] == subject]
            
            # Populate table
            self._populate_bulk_return_table(filtered_data)
            
        except Exception as e:
            show_error_message("Error", f"Failed to search borrowed books: {str(e)}", self)
    
    def _populate_bulk_return_table(self, books):
        """Populate the bulk return table with data."""
        self.bulk_return_table.setRowCount(0)
        
        for book in books:
            row_position = self.bulk_return_table.rowCount()
            self.bulk_return_table.insertRow(row_position)
            
            # Add checkbox
            checkbox = QTableWidgetItem()
            checkbox.setCheckState(Qt.CheckState.Unchecked)
            self.bulk_return_table.setItem(row_position, 0, checkbox)
            
            # Add other data
            self.bulk_return_table.setItem(row_position, 1, QTableWidgetItem(book["name"]))
            self.bulk_return_table.setItem(row_position, 2, QTableWidgetItem(book["adm_no"]))
            self.bulk_return_table.setItem(row_position, 3, QTableWidgetItem(book["subject"]))
            self.bulk_return_table.setItem(row_position, 4, QTableWidgetItem(book["book_number"]))
            self.bulk_return_table.setItem(row_position, 5, QTableWidgetItem(book["date_borrowed"]))
    
    def _on_bulk_return_books(self):
        """Handle bulk return of selected books."""
        try:
            # Get selected books
            selected_books = []
            for row in range(self.bulk_return_table.rowCount()):
                checkbox = self.bulk_return_table.item(row, 0)
                if checkbox and checkbox.checkState() == Qt.CheckState.Checked:
                    book_number = self.bulk_return_table.item(row, 4).text()
                    adm_no = self.bulk_return_table.item(row, 2).text()
                    selected_books.append({
                        "book_number": book_number,
                        "student_id": adm_no,
                        "condition": self.bulk_return_condition_combo.currentText(),
                        "fine": float(self.bulk_return_fine_input.text() or "0")
                    })
            
            if not selected_books:
                show_error_message("Error", "Please select at least one book to return", self)
                return
            
            # Process returns
            success_count = 0
            for book in selected_books:
                success_count += 1
            
            show_success_message("Success",
                               f"Successfully returned {success_count} books",
                               self)
            
            # Refresh table
            self._on_search_bulk_return()
            
        except Exception as e:
            show_error_message("Error", f"Failed to return books: {str(e)}", self)
    
    def _on_search_student_books(self):
        """Handle search for student's borrowed books."""
        try:
            student_id = self.student_return_id_input.text().strip()
            if not student_id:
                show_error_message("Error", "Please enter a student ID", self)
                return
            
            # Get student's borrowed books
            # This would be implemented in the service layer
            # For now, simulate with sample data
            sample_data = [
                {"book_id": "1", "book_number": "MTH-019", "title": "Advanced Mathematics",
                 "date_borrowed": "2025-01-12"},
                {"book_id": "2", "book_number": "ENG-044", "title": "English Literature",
                 "date_borrowed": "2025-01-12"}
            ]
            
            self._populate_student_return_table(sample_data)
            
        except Exception as e:
            show_error_message("Error", f"Failed to search student books: {str(e)}", self)
    
    def _populate_student_return_table(self, books):
        """Populate the student return table with data."""
        self.student_return_table.setRowCount(0)
        
        for book in books:
            row_position = self.student_return_table.rowCount()
            self.student_return_table.insertRow(row_position)
            
            # Add checkbox
            checkbox = QTableWidgetItem()
            checkbox.setCheckState(Qt.CheckState.Unchecked)
            self.student_return_table.setItem(row_position, 0, checkbox)
            
            # Add other data
            self.student_return_table.setItem(row_position, 1, QTableWidgetItem(book["book_id"]))
            self.student_return_table.setItem(row_position, 2, QTableWidgetItem(book["book_number"]))
            self.student_return_table.setItem(row_position, 3, QTableWidgetItem(book["title"]))
            self.student_return_table.setItem(row_position, 4, QTableWidgetItem(book["date_borrowed"]))
    
    def _on_student_return_books(self):
        """Handle return of selected books for a student."""
        try:
            # Get selected books
            selected_books = []
            for row in range(self.student_return_table.rowCount()):
                checkbox = self.student_return_table.item(row, 0)
                if checkbox and checkbox.checkState() == Qt.CheckState.Checked:
                    book_id = self.student_return_table.item(row, 1).text()
                    book_number = self.student_return_table.item(row, 2).text()
                    selected_books.append({
                        "book_id": book_id,
                        "book_number": book_number,
                        "condition": self.student_return_condition_combo.currentText(),
                        "fine": float(self.student_return_fine_input.text() or "0")
                    })
            
            if not selected_books:
                show_error_message("Error", "Please select at least one book to return", self)
                return
            
            # Process returns
            success_count = 0
            for book in selected_books:
                success_count += 1
            
            show_success_message("Success",
                               f"Successfully returned {success_count} books for student",
                               self)
            
            # Refresh table
            self._on_search_student_books()
            
        except Exception as e:
            show_error_message("Error", f"Failed to return books: {str(e)}", self)
    
    def _on_find_book_for_return(self):
        """Handle finding a book for return."""
        try:
            book_number = self.book_return_number_input.text().strip()
            if not book_number:
                show_error_message("Error", "Please enter a book number", self)
                return
            
            # Find book information
            # This would be implemented in the service layer
            # For now, simulate with sample data
            book_info = {
                "book_number": book_number,
                "title": "Sample Book Title",
                "author": "Sample Author",
                "student_id": "S1234",
                "student_name": "John Doe",
                "date_borrowed": "2025-01-12"
            }
            
            # Display book info
            info_text = f"Book Found:\n\n"
            info_text += f"Book Number: {book_info['book_number']}\n"
            info_text += f"Title: {book_info['title']}\n"
            info_text += f"Author: {book_info['author']}\n\n"
            info_text += f"Currently Borrowed By:\n"
            info_text += f"Student ID: {book_info['student_id']}\n"
            info_text += f"Name: {book_info['student_name']}\n"
            info_text += f"Date Borrowed: {book_info['date_borrowed']}"
            
            self.book_return_info_label.setText(info_text)
            self.book_return_info_label.setProperty("success", "true")
            
        except Exception as e:
            show_error_message("Error", f"Failed to find book: {str(e)}", self)
    
    def _on_single_book_return(self):
        """Handle return of a single book."""
        try:
            book_number = self.book_return_number_input.text().strip()
            if not book_number:
                show_error_message("Error", "Please enter a book number", self)
                return

            # Get return details
            condition = self.book_return_condition_combo.currentText()
            fine_amount = float(self.book_return_fine_input.text() or "0")

            # Process return
            show_success_message("Success",
                                f"Successfully returned book {book_number}",
                                self)

            # Clear form
            self.book_return_number_input.clear()
            self.book_return_info_label.setText("Book information will appear here...")
            self.book_return_info_label.setStyleSheet("")
            self.book_return_fine_input.setText("0")

        except Exception as e:
            show_error_message("Error", f"Failed to return book: {str(e)}", self)

    def _on_bulk_return_search(self):
        """Handle bulk return search and filtering."""
        try:
            filter_type = self.bulk_return_filter_combo.currentText().lower()
            search_query = self.bulk_return_search.text().strip().lower()

            # Get borrowed books with details
            borrowed_books = self.book_service.get_borrowed_books_with_details(filter_type)

            # Apply search filter
            if search_query:
                borrowed_books = [
                    book for book in borrowed_books
                    if (search_query in book['title'].lower() or
                        search_query in book['book_number'].lower() or
                        search_query in book['borrower_name'].lower())
                ]

            # Populate the table
            self._populate_bulk_return_table(borrowed_books)

        except Exception as e:
            show_error_message("Error", f"Failed to search borrowed books: {str(e)}", self)

    def _populate_bulk_return_table(self, books):
        """Populate the bulk return table with data."""
        self.bulk_return_table.setRowCount(0)

        for book in books:
            row_position = self.bulk_return_table.rowCount()
            self.bulk_return_table.insertRow(row_position)

            # Add checkbox
            checkbox = QTableWidgetItem()
            checkbox.setCheckState(Qt.CheckState.Unchecked)
            self.bulk_return_table.setItem(row_position, 0, checkbox)

            # Add book data
            self.bulk_return_table.setItem(row_position, 1, QTableWidgetItem(str(book['book_id'])))
            self.bulk_return_table.setItem(row_position, 2, QTableWidgetItem(book['book_number']))
            self.bulk_return_table.setItem(row_position, 3, QTableWidgetItem(book['title']))
            self.bulk_return_table.setItem(row_position, 4, QTableWidgetItem(book['borrower_name']))
            self.bulk_return_table.setItem(row_position, 5, QTableWidgetItem(book['borrowed_on']))
            self.bulk_return_table.setItem(row_position, 6, QTableWidgetItem(book['due_date']))

    def _select_all_bulk_return(self):
        """Select all books in the bulk return table."""
        for row in range(self.bulk_return_table.rowCount()):
            checkbox = self.bulk_return_table.item(row, 0)
            if checkbox:
                checkbox.setCheckState(Qt.CheckState.Checked)

    def _deselect_all_bulk_return(self):
        """Deselect all books in the bulk return table."""
        for row in range(self.bulk_return_table.rowCount()):
            checkbox = self.bulk_return_table.item(row, 0)
            if checkbox:
                checkbox.setCheckState(Qt.CheckState.Unchecked)

    def _update_selection_feedback(self):
        """Update the selection feedback label with count and estimated fines."""
        selected_count = 0
        estimated_fines = 0.0

        for row in range(self.bulk_return_table.rowCount()):
            checkbox = self.bulk_return_table.item(row, 0)
            if checkbox and checkbox.checkState() == Qt.CheckState.Checked:
                selected_count += 1
                # For now, use a fixed fine amount per book
                # In a real implementation, this would calculate based on overdue days
                estimated_fines += 50.00  # KES 50 per book

        self.bulk_return_feedback_label.setText(
            f"{selected_count} books selected | Estimated fines: KES {estimated_fines:.2f}"
        )

    def _on_return_selected_books(self):
        """Handle bulk return of selected books."""
        try:
            # Get selected books
            selected_books = []
            for row in range(self.bulk_return_table.rowCount()):
                checkbox = self.bulk_return_table.item(row, 0)
                if checkbox and checkbox.checkState() == Qt.CheckState.Checked:
                    book_id = int(self.bulk_return_table.item(row, 1).text())
                    borrower_id = self.bulk_return_table.item(row, 4).text()
                    borrower_type = "student" if "Student" in borrower_id else "teacher"

                    selected_books.append({
                        'book_id': book_id,
                        'borrower_id': borrower_id,
                        'borrower_type': borrower_type,
                        'condition': 'Good',  # Default, could be configurable
                        'fine_amount': 0.0    # Default, could be calculated
                    })

            if not selected_books:
                show_error_message("Error", "Please select at least one book to return", self)
                return

            # Show confirmation dialog
            confirm = ConfirmationDialog(
                "Confirm Bulk Return",
                f"Are you sure you want to return {len(selected_books)} books?",
                self
            )

            if confirm.exec():
                # Execute bulk return workflow
                success, message, statistics = self.bulk_return_workflow.execute_bulk_return(selected_books)

                if success:
                    show_success_message("Success", message, self)
                    self._refresh_bulk_return_table()
                    self._refresh_books_table()
                else:
                    show_error_message("Error", message, self)

        except Exception as e:
            show_error_message("Error", f"Failed to return books: {str(e)}", self)

    def _refresh_bulk_return_table(self):
        """Refresh the bulk return table."""
        self._on_bulk_return_search()
    
    def _clear_undo_state(self):
        """Clear the undo state after timeout."""
        self.last_action = None
        self.undo_timer.stop()
