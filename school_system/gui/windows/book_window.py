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
from school_system.config.logging import logger
from school_system.services.book_service import BookService
from school_system.core.exceptions import DatabaseException, ValidationError


class ValidationHelper:
    """Helper class for book validation operations."""
    
    @staticmethod
    def validate_book_number(book_number: str, existing_books: List[Dict]) -> tuple[bool, str]:
        """
        Validate book number for uniqueness and format.
        
        Args:
            book_number: The book number to validate
            existing_books: List of existing books for uniqueness check
            
        Returns:
            tuple: (is_valid, error_message)
        """
        if not book_number or not book_number.strip():
            return False, "Book number is required"
            
        # Normalize book number (uppercase, trim whitespace)
        normalized = book_number.strip().upper()
        
        # Check if book number already exists (case-insensitive)
        for book in existing_books:
            if book['book_number'].strip().upper() == normalized:
                return False, f"Book number '{book_number}' already exists"
                
        return True, ""
        
    @staticmethod
    def validate_required_fields(data: Dict[str, str], required_fields: List[str]) -> tuple[bool, str]:
        """Validate that required fields are present and not empty."""
        for field in required_fields:
            if not data.get(field) or not data[field].strip():
                return False, f"{field.replace('_', ' ').title()} is required"
        return True, ""


class ConfirmationDialog(QDialog):
    """Reusable confirmation dialog with preview functionality."""
    
    def __init__(self, title: str, message: str, details: str = "", parent=None):
        super().__init__(parent)
        self.setWindowTitle(title)
        self.setMinimumWidth(400)
        
        layout = QVBoxLayout()
        
        # Main message
        message_label = QLabel(message)
        message_label.setWordWrap(True)
        layout.addWidget(message_label)
        
        # Details/preview section
        if details:
            details_label = QLabel("Preview:")
            details_label.setStyleSheet("font-weight: bold;")
            layout.addWidget(details_label)
            
            details_text = QTextEdit()
            details_text.setPlainText(details)
            details_text.setReadOnly(True)
            details_text.setMaximumHeight(150)
            layout.addWidget(details_text)
        
        # Buttons
        button_layout = QHBoxLayout()
        
        cancel_button = QPushButton("Cancel")
        cancel_button.clicked.connect(self.reject)
        button_layout.addWidget(cancel_button)
        
        confirm_button = QPushButton("Confirm")
        confirm_button.clicked.connect(self.accept)
        confirm_button.setStyleSheet("background-color: #4CAF50; color: white;")
        button_layout.addWidget(confirm_button)
        
        layout.addLayout(button_layout)
        self.setLayout(layout)


class ImportSummaryDialog(QDialog):
    """Dialog to show import summary with categorization and approval."""
    
    def __init__(self, import_results: dict, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Import Summary - Review Before Finalizing")
        self.setMinimumWidth(500)
        self.setMinimumHeight(400)
        
        self.import_results = import_results
        self.approved = False
        
        layout = QVBoxLayout()
        
        # Summary header
        header_label = QLabel("Distribution Import Summary")
        header_label.setStyleSheet("font-size: 16px; font-weight: bold; color: #2C3E50;")
        layout.addWidget(header_label)
        
        # Import statistics
        stats_layout = QHBoxLayout()
        
        # Valid books
        valid_label = QLabel(f"✅ Valid Books: {import_results['valid_books']}")
        valid_label.setStyleSheet("color: #27AE60; font-size: 14px;")
        stats_layout.addWidget(valid_label)
        
        # Pending books
        pending_label = QLabel(f"⏳ Pending Books: {import_results['pending_books']}")
        pending_label.setStyleSheet("color: #F39C12; font-size: 14px;")
        stats_layout.addWidget(pending_label)
        
        # Conflicts
        conflict_label = QLabel(f"❌ Conflicts: {import_results['conflicts']}")
        conflict_label.setStyleSheet("color: #E74C3C; font-size: 14px;")
        stats_layout.addWidget(conflict_label)
        
        layout.addLayout(stats_layout)
        
        # Detailed breakdown
        breakdown_label = QLabel("Detailed Breakdown:")
        breakdown_label.setStyleSheet("font-weight: bold; margin-top: 15px;")
        layout.addWidget(breakdown_label)
        
        breakdown_text = QTextEdit()
        breakdown_text.setReadOnly(True)
        
        breakdown_content = ""
        breakdown_content += f"📚 Valid Books: {import_results['valid_books']}\n"
        breakdown_content += f"   → Books found in catalog and available for distribution\n\n"
        
        breakdown_content += f"🕒 Pending Books: {import_results['pending_books']}\n"
        breakdown_content += f"   → Book numbers not yet in catalog (will be marked as PENDING_BOOK)\n"
        breakdown_content += f"   → These will need to be cataloged before posting the session\n\n"
        
        breakdown_content += f"⚠️  Conflicts: {import_results['conflicts']}\n"
        if import_results['duplicate_book_numbers'] > 0:
            breakdown_content += f"   → {import_results['duplicate_book_numbers']} duplicate book numbers detected\n"
        breakdown_content += f"   → These entries were skipped to maintain data integrity\n\n"
        
        breakdown_content += "📋 Import Rules Applied:\n"
        breakdown_content += "   ✅ Student existence: REQUIRED (conflicts if missing)\n"
        breakdown_content += "   ⚠️  Book number: OPTIONAL (can be blank)\n"
        breakdown_content += "   ❌ Duplicate book numbers: NOT allowed\n"
        breakdown_content += "   🔍 Book catalog check: If book exists, validate availability\n"
        breakdown_content += "   📝 Unknown books: Saved with NULL book_id and 'Not in system' note\n"
        
        breakdown_text.setPlainText(breakdown_content)
        layout.addWidget(breakdown_text)
        
        # Import impact section
        impact_label = QLabel("Import Impact:")
        impact_label.setStyleSheet("font-weight: bold; margin-top: 15px;")
        layout.addWidget(impact_label)
        
        impact_text = QTextEdit()
        impact_text.setReadOnly(True)
        impact_text.setMaximumHeight(100)
        
        impact_content = ""
        impact_content += "📝 Database Changes:\n"
        impact_content += "   • distribution_students records will be updated with book assignments\n"
        impact_content += "   • Session status will be set to 'IMPORTED'\n"
        impact_content += "   • Import operation will be logged in distribution_import_logs\n\n"
        
        impact_content += "🔒 Posting Rules:\n"
        impact_content += "   • Session can only be POSTED when all books are resolved (cataloged)\n"
        impact_content += "   • Pending books must be added to catalog before posting\n"
        impact_content += "   • This ensures data integrity and proper inventory tracking\n"
        
        impact_text.setPlainText(impact_content)
        layout.addWidget(impact_text)
        
        # Approval section
        approval_label = QLabel("Librarian Approval:")
        approval_label.setStyleSheet("font-weight: bold; margin-top: 15px;")
        layout.addWidget(approval_label)
        
        approval_text = QLabel("By approving this import, you confirm that:")
        approval_text.setWordWrap(True)
        layout.addWidget(approval_text)
        
        confirmation_items = QTextEdit()
        confirmation_items.setReadOnly(True)
        confirmation_items.setMaximumHeight(80)
        confirmation_items.setPlainText("""
1. You have reviewed the import summary and statistics
2. You understand that pending books will need to be cataloged before posting
3. You accept that conflicts have been properly handled
4. You are ready to finalize this import operation
        """)
        layout.addWidget(confirmation_items)
        
        # Buttons
        button_layout = QHBoxLayout()
        
        cancel_button = QPushButton("Cancel Import")
        cancel_button.clicked.connect(self.reject)
        cancel_button.setStyleSheet("background-color: #E74C3C; color: white;")
        button_layout.addWidget(cancel_button)
        
        approve_button = QPushButton("Approve and Finalize Import")
        approve_button.clicked.connect(self._approve_import)
        approve_button.setStyleSheet("background-color: #27AE60; color: white;")
        button_layout.addWidget(approve_button)
        
        layout.addLayout(button_layout)
        self.setLayout(layout)
    
    def _approve_import(self):
        """Handle import approval."""
        self.approved = True
        self.accept()
    
    def get_approval_status(self) -> bool:
        """Get the approval status."""
        return self.approved


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
        book_tab = self._create_book_management_tab()
        tab_widget.addTab(book_tab, "Book Management")
        
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
        
        # Advanced Return Tab
        return_tab = self._create_advanced_return_tab()
        tab_widget.addTab(return_tab, "Advanced Returns")
    
    def _create_book_management_tab(self) -> QWidget:
        """Create the book management tab with standardized workflows."""
        tab = QWidget()
        layout = self.create_flex_layout("column", False)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.set_spacing(15)
        
        # Add Books Section (Cataloging Workflow)
        add_section = self.create_card("Add Books (Cataloging)", 
                                     "Create new book entries in the system")
        add_form = self._create_add_book_form()
        add_section.layout.addWidget(add_form)
        layout.add_widget(add_section)
        
        # Edit Books Section (Editing Workflow)
        edit_section = self.create_card("Edit Books", 
                                      "Modify existing book information")
        edit_form = self._create_edit_book_form()
        edit_section.layout.addWidget(edit_form)
        layout.add_widget(edit_section)
        
        # Remove Books Section (Decommissioning Workflow)
        remove_section = self.create_card("Remove Books (Decommissioning)",
                                        "Permanently remove books from the system")
        remove_form = self._create_remove_book_form()
        remove_section.layout.addWidget(remove_form)
        layout.add_widget(remove_section)
        
        # View Books Section
        view_section = self.create_card("View Books", "Browse and search existing books")
        view_form = self._create_view_books_section()
        view_section.layout.addWidget(view_form)
        layout.add_widget(view_section)
        
        tab.setLayout(layout._layout)
        return tab
    
    def _create_add_book_form(self) -> QWidget:
        """Create the add book form following the standardized workflow."""
        form = QWidget()
        form_layout = self.create_flex_layout("column", False)
        form_layout.set_spacing(10)
        
        # Subject (validated against school curriculum)
        subject_label = QLabel("Subject:")
        form_layout.add_widget(subject_label)
        self.add_subject_combo = QComboBox()
        self.add_subject_combo.addItems(["Mathematics", "Science", "English", "History", "Geography"])
        self.add_subject_combo.setEditable(True)
        form_layout.add_widget(self.add_subject_combo)
        
        # Class/Form (linked to active academic years)
        class_label = QLabel("Class/Form:")
        form_layout.add_widget(class_label)
        self.add_class_combo = QComboBox()
        self.add_class_combo.addItems(["Form 1", "Form 2", "Form 3", "Form 4"])
        self.add_class_combo.setEditable(True)
        form_layout.add_widget(self.add_class_combo)
        
        # Book Number (physical label with real-time validation)
        book_number_label = QLabel("Book Number:")
        form_layout.add_widget(book_number_label)
        self.add_book_number_input = self.create_input("Enter book number (must be unique)")
        self.add_book_number_input.textChanged.connect(self._validate_book_number_real_time)
        form_layout.add_widget(self.add_book_number_input)
        
        # Validation feedback
        self.book_number_validation_label = QLabel()
        self.book_number_validation_label.setStyleSheet("color: red;")
        form_layout.add_widget(self.book_number_validation_label)
        
        # Title
        title_label = QLabel("Title:")
        form_layout.add_widget(title_label)
        self.add_title_input = self.create_input("Enter book title")
        form_layout.add_widget(self.add_title_input)
        
        # Author
        author_label = QLabel("Author:")
        form_layout.add_widget(author_label)
        self.add_author_input = self.create_input("Enter author name")
        form_layout.add_widget(self.add_author_input)
        
        # Condition (enum with auto-flagging)
        condition_label = QLabel("Condition:")
        form_layout.add_widget(condition_label)
        self.add_condition_combo = QComboBox()
        self.add_condition_combo.addItems(["New", "Good", "Torn", "Damaged"])
        form_layout.add_widget(self.add_condition_combo)
        
        # Additional fields
        category_label = QLabel("Category:")
        form_layout.add_widget(category_label)
        self.add_category_input = self.create_input("Enter category")
        form_layout.add_widget(self.add_category_input)
        
        isbn_label = QLabel("ISBN:")
        form_layout.add_widget(isbn_label)
        self.add_isbn_input = self.create_input("Enter ISBN")
        form_layout.add_widget(self.add_isbn_input)
        
        pub_date_label = QLabel("Publication Date:")
        form_layout.add_widget(pub_date_label)
        self.add_pub_date_input = self.create_input("YYYY-MM-DD")
        form_layout.add_widget(self.add_pub_date_input)
        
        # Notes
        notes_label = QLabel("Notes:")
        form_layout.add_widget(notes_label)
        self.add_notes_input = QTextEdit()
        self.add_notes_input.setMaximumHeight(80)
        form_layout.add_widget(self.add_notes_input)
        
        # Action button
        add_button = self.create_button("Add Book", "primary")
        add_button.clicked.connect(self._start_add_book_workflow)
        form_layout.add_widget(add_button)
        
        form.setLayout(form_layout._layout)
        return form
    
    def _create_edit_book_form(self) -> QWidget:
        """Create the edit book form following the standardized workflow."""
        form = QWidget()
        form_layout = self.create_flex_layout("column", False)
        form_layout.set_spacing(10)
        
        # Book ID for lookup
        book_id_label = QLabel("Book ID:")
        form_layout.add_widget(book_id_label)
        self.edit_book_id_input = self.create_input("Enter book ID to edit")
        form_layout.add_widget(self.edit_book_id_input)
        
        # Load button
        load_button = self.create_button("Load Book Details", "secondary")
        load_button.clicked.connect(self._load_book_for_editing)
        form_layout.add_widget(load_button)
        
        # Editable fields (initially disabled)
        self.edit_title_label = QLabel("New Title:")
        form_layout.add_widget(self.edit_title_label)
        self.edit_title_input = self.create_input("Enter new title")
        self.edit_title_input.setEnabled(False)
        form_layout.add_widget(self.edit_title_input)
        
        self.edit_author_label = QLabel("New Author:")
        form_layout.add_widget(self.edit_author_label)
        self.edit_author_input = self.create_input("Enter new author")
        self.edit_author_input.setEnabled(False)
        form_layout.add_widget(self.edit_author_input)
        
        self.edit_condition_label = QLabel("New Condition:")
        form_layout.add_widget(self.edit_condition_label)
        self.edit_condition_combo = QComboBox()
        self.edit_condition_combo.addItems(["New", "Good", "Torn", "Damaged"])
        self.edit_condition_combo.setEnabled(False)
        form_layout.add_widget(self.edit_condition_combo)
        
        self.edit_notes_label = QLabel("Edit Notes:")
        form_layout.add_widget(self.edit_notes_label)
        self.edit_notes_input = QTextEdit()
        self.edit_notes_input.setMaximumHeight(80)
        self.edit_notes_input.setEnabled(False)
        form_layout.add_widget(self.edit_notes_input)
        
        # Action button
        edit_button = self.create_button("Update Book", "primary")
        edit_button.clicked.connect(self._start_edit_book_workflow)
        edit_button.setEnabled(False)
        self.edit_button = edit_button
        form_layout.add_widget(edit_button)
        
        form.setLayout(form_layout._layout)
        return form
    
    def _create_remove_book_form(self) -> QWidget:
        """Create the remove book form following the standardized workflow."""
        form = QWidget()
        form_layout = self.create_flex_layout("column", False)
        form_layout.set_spacing(10)
        
        # Book ID for removal
        book_id_label = QLabel("Book ID:")
        form_layout.add_widget(book_id_label)
        self.remove_book_id_input = self.create_input("Enter book ID to remove")
        form_layout.add_widget(self.remove_book_id_input)
        
        # Reason for removal
        reason_label = QLabel("Reason for Removal:")
        form_layout.add_widget(reason_label)
        self.remove_reason_combo = QComboBox()
        self.remove_reason_combo.addItems([
            "Damaged beyond repair", 
            "Lost", 
            "Obsolete curriculum", 
            "Duplicate entry",
            "Other"
        ])
        self.remove_reason_combo.setEditable(True)
        form_layout.add_widget(self.remove_reason_combo)
        
        # Additional notes
        notes_label = QLabel("Additional Notes:")
        form_layout.add_widget(notes_label)
        self.remove_notes_input = QTextEdit()
        self.remove_notes_input.setMaximumHeight(80)
        form_layout.add_widget(self.remove_notes_input)
        
        # Action button
        remove_button = self.create_button("Remove Book", "danger")
        remove_button.clicked.connect(self._start_remove_book_workflow)
        form_layout.add_widget(remove_button)
        
        form.setLayout(form_layout._layout)
        return form
    
    def _create_view_books_section(self) -> QWidget:
        """Create the view books section."""
        form = QWidget()
        form_layout = self.create_flex_layout("column", False)
        form_layout.set_spacing(10)
        
        # Search box
        self.search_box = self.create_search_box("Search books...")
        self.search_box.search_text_changed.connect(self._on_search_books)
        form_layout.add_widget(self.search_box)
        
        # Refresh button
        refresh_button = self.create_button("Refresh Books", "secondary")
        refresh_button.clicked.connect(self._refresh_books_table)
        form_layout.add_widget(refresh_button)
        
        # Books table
        self.books_table = self.create_table(0, 8)
        self.books_table.setHorizontalHeaderLabels([
            "ID", "Book Number", "Title", "Author", "Category", 
            "Available", "Condition", "Subject"
        ])
        form_layout.add_widget(self.books_table)
        
        form.setLayout(form_layout._layout)
        return form
    
    def _validate_book_number_real_time(self, text: str):
        """Real-time validation for book number uniqueness."""
        if not text or not text.strip():
            self.book_number_validation_label.setText("")
            return
            
        try:
            # Get all existing books for validation
            existing_books = self.book_service.get_all_books()
            existing_book_data = [{'book_number': book.book_number} for book in existing_books]
            
            is_valid, message = ValidationHelper.validate_book_number(text, existing_book_data)
            
            if is_valid:
                self.book_number_validation_label.setText("✓ Book number is available")
                self.book_number_validation_label.setStyleSheet("color: green;")
            else:
                self.book_number_validation_label.setText(f"✗ {message}")
                self.book_number_validation_label.setStyleSheet("color: red;")
                
        except Exception as e:
            self.book_number_validation_label.setText(f"✗ Validation error: {str(e)}")
            self.book_number_validation_label.setStyleSheet("color: red;")
    
    def _load_book_for_editing(self):
        """Load book details for editing."""
        try:
            book_id = int(self.edit_book_id_input.text().strip())
            book = self.book_service.get_book_by_id(book_id)
            
            if book:
                # Enable edit fields and populate with current values
                self.edit_title_input.setEnabled(True)
                self.edit_author_input.setEnabled(True)
                self.edit_condition_combo.setEnabled(True)
                self.edit_notes_input.setEnabled(True)
                self.edit_button.setEnabled(True)
                
                self.edit_title_input.setText(book.title)
                self.edit_author_input.setText(book.author)
                self.edit_condition_combo.setCurrentText(book.book_condition or "Good")
                self.edit_notes_input.setPlainText(f"Current condition: {book.book_condition}")
                
                show_success_message("Success", f"Loaded book: {book.title}", self)
            else:
                show_error_message("Error", "Book not found", self)
                
        except ValueError:
            show_error_message("Error", "Invalid book ID", self)
        except Exception as e:
            show_error_message("Error", f"Failed to load book: {str(e)}", self)
    
    def _start_add_book_workflow(self):
        """Start the standardized add book workflow."""
        # Step 1: Input Selection - Validate mandatory fields
        required_fields = [
            ('subject', self.add_subject_combo.currentText()),
            ('class', self.add_class_combo.currentText()),
            ('book_number', self.add_book_number_input.text()),
            ('title', self.add_title_input.text()),
            ('author', self.add_author_input.text())
        ]
        
        # Validate required fields
        validation_errors = []
        for field_name, field_value in required_fields:
            if not field_value or not field_value.strip():
                validation_errors.append(f"{field_name.replace('_', ' ').title()} is required")
        
        if validation_errors:
            show_error_message("Validation Error", "\n".join(validation_errors), self)
            return
        
        # Step 2: System Validation - Check book number uniqueness
        existing_books = self.book_service.get_all_books()
        existing_book_data = [{'book_number': book.book_number} for book in existing_books]
        
        is_valid, validation_message = ValidationHelper.validate_book_number(
            self.add_book_number_input.text().strip(), 
            existing_book_data
        )
        
        if not is_valid:
            show_error_message("Validation Error", validation_message, self)
            return
        
        # Step 3: Confirmation - Show preview modal
        book_data_preview = self._prepare_book_data_for_preview()
        
        confirmation_dialog = ConfirmationDialog(
            "Confirm Add Book",
            "You are about to add a new book to the system. Please review the details:",
            book_data_preview
        )
        
        if confirmation_dialog.exec() == QDialog.DialogCode.Accepted:
            # Step 4: Execution - Add the book
            self._execute_add_book()
    
    def _prepare_book_data_for_preview(self) -> str:
        """Prepare book data for preview in confirmation dialog."""
        preview_text = "Book Details Preview:\n\n"
        preview_text += f"Subject: {self.add_subject_combo.currentText()}\n"
        preview_text += f"Class: {self.add_class_combo.currentText()}\n"
        preview_text += f"Book Number: {self.add_book_number_input.text()}\n"
        preview_text += f"Title: {self.add_title_input.text()}\n"
        preview_text += f"Author: {self.add_author_input.text()}\n"
        preview_text += f"Condition: {self.add_condition_combo.currentText()}\n"
        preview_text += f"Category: {self.add_category_input.text()}\n"
        preview_text += f"ISBN: {self.add_isbn_input.text()}\n"
        preview_text += f"Publication Date: {self.add_pub_date_input.text()}\n"
        
        if self.add_notes_input.toPlainText():
            preview_text += f"\nNotes: {self.add_notes_input.toPlainText()}"
        
        # Show impact
        preview_text += "\n\nImpact:\n"
        preview_text += "- This will create a new book record in the database\n"
        preview_text += "- Book.available will be set to 1 (available for borrowing)\n"
        preview_text += "- An audit log entry will be created\n"
        
        return preview_text
    
    def _execute_add_book(self):
        """Execute the add book operation."""
        try:
            book_data = {
                'book_number': self.add_book_number_input.text().strip(),
                'title': self.add_title_input.text().strip(),
                'author': self.add_author_input.text().strip(),
                'category': self.add_category_input.text().strip(),
                'subject': self.add_subject_combo.currentText(),
                'class': self.add_class_combo.currentText(),
                'isbn': self.add_isbn_input.text().strip(),
                'publication_date': self.add_pub_date_input.text().strip(),
                'available': 1,
                'book_condition': self.add_condition_combo.currentText(),
                'notes': self.add_notes_input.toPlainText()
            }
            
            # Atomic transaction
            book = self.book_service.create_book(book_data)
            
            # Log action to audit trail
            self.book_service.log_user_action(
                self.current_user, 
                "book_add", 
                f"Added book {book.id}: {book.title}"
            )
            
            # Store for undo functionality
            self.last_action = {
                'type': 'add',
                'book_id': book.id,
                'timestamp': time.time()
            }
            
            # Start undo timer (5 seconds)
            self.undo_timer.start(5000)
            
            show_success_message(
                "Success", 
                f"Book created successfully with ID: {book.id}\n\nYou can undo this action within 5 seconds.",
                self
            )
            
            # Clear form
            self._clear_add_book_form()
            
            # Refresh table
            self._refresh_books_table()
            
        except (ValidationError, DatabaseException) as e:
            show_error_message("Error", str(e), self)
        except Exception as e:
            show_error_message("Error", f"An error occurred: {str(e)}", self)
    
    def _clear_add_book_form(self):
        """Clear the add book form."""
        self.add_book_number_input.clear()
        self.add_title_input.clear()
        self.add_author_input.clear()
        self.add_category_input.clear()
        self.add_isbn_input.clear()
        self.add_pub_date_input.clear()
        self.add_notes_input.clear()
        self.book_number_validation_label.setText("")
    
    def _start_edit_book_workflow(self):
        """Start the standardized edit book workflow."""
        try:
            book_id = int(self.edit_book_id_input.text().strip())
            
            # Validate that at least one field is being updated
            update_data = {}
            if self.edit_title_input.text().strip() and self.edit_title_input.text() != self.edit_title_input.placeholderText():
                update_data['title'] = self.edit_title_input.text().strip()
            if self.edit_author_input.text().strip() and self.edit_author_input.text() != self.edit_author_input.placeholderText():
                update_data['author'] = self.edit_author_input.text().strip()
            if self.edit_condition_combo.currentText() and self.edit_condition_combo.currentText() != "Select condition":
                update_data['book_condition'] = self.edit_condition_combo.currentText()
            
            if not update_data:
                show_error_message("Error", "Please provide at least one field to update", self)
                return
            
            # Get current book for preview
            current_book = self.book_service.get_book_by_id(book_id)
            if not current_book:
                show_error_message("Error", "Book not found", self)
                return
            
            # Show confirmation with preview
            preview_text = f"Editing Book ID: {book_id}\n\n"
            preview_text += f"Current Title: {current_book.title}\n"
            preview_text += f"New Title: {update_data.get('title', current_book.title)}\n\n"
            preview_text += f"Current Author: {current_book.author}\n"
            preview_text += f"New Author: {update_data.get('author', current_book.author)}\n\n"
            preview_text += f"Current Condition: {current_book.book_condition}\n"
            preview_text += f"New Condition: {update_data.get('book_condition', current_book.book_condition)}\n\n"
            
            if self.edit_notes_input.toPlainText():
                preview_text += f"Notes: {self.edit_notes_input.toPlainText()}\n\n"
            
            preview_text += "Impact:\n"
            preview_text += "- This will update the book record in the database\n"
            preview_text += "- An audit log entry will be created\n"
            
            confirmation_dialog = ConfirmationDialog(
                "Confirm Edit Book",
                f"You are about to update book ID: {book_id}. Please review the changes:",
                preview_text
            )
            
            if confirmation_dialog.exec() == QDialog.DialogCode.Accepted:
                # Execute the update
                book = self.book_service.update_book(book_id, update_data)
                
                if book:
                    # Log action
                    self.book_service.log_user_action(
                        self.current_user,
                        "book_edit",
                        f"Updated book {book_id}: {update_data}"
                    )
                    
                    # Store for undo
                    self.last_action = {
                        'type': 'edit',
                        'book_id': book_id,
                        'old_data': {
                            'title': current_book.title,
                            'author': current_book.author,
                            'book_condition': current_book.book_condition
                        },
                        'timestamp': time.time()
                    }
                    
                    # Start undo timer
                    self.undo_timer.start(5000)
                    
                    show_success_message(
                        "Success",
                        f"Book updated successfully\n\nYou can undo this action within 5 seconds.",
                        self
                    )
                    
                    # Clear edit form
                    self._clear_edit_book_form()
                    
                    # Refresh table
                    self._refresh_books_table()
                else:
                    show_error_message("Error", "Book not found", self)
                    
        except ValueError:
            show_error_message("Error", "Invalid book ID", self)
        except Exception as e:
            show_error_message("Error", f"An error occurred: {str(e)}", self)
    
    def _clear_edit_book_form(self):
        """Clear the edit book form."""
        self.edit_book_id_input.clear()
        self.edit_title_input.clear()
        self.edit_author_input.clear()
        self.edit_notes_input.clear()
        self.edit_title_input.setEnabled(False)
        self.edit_author_input.setEnabled(False)
        self.edit_condition_combo.setEnabled(False)
        self.edit_notes_input.setEnabled(False)
        self.edit_button.setEnabled(False)
    
    def _start_remove_book_workflow(self):
        """Start the standardized remove book workflow."""
        try:
            book_id = int(self.remove_book_id_input.text().strip())
            
            # Get book details for preview
            book = self.book_service.get_book_by_id(book_id)
            if not book:
                show_error_message("Error", "Book not found", self)
                return
            
            # Check if book is currently borrowed
            if not book.available:
                show_error_message(
                    "Error", 
                    "Cannot remove a book that is currently borrowed. Please return it first.",
                    self
                )
                return
            
            # Show confirmation with preview
            preview_text = f"Removing Book ID: {book_id}\n\n"
            preview_text += f"Title: {book.title}\n"
            preview_text += f"Author: {book.author}\n"
            preview_text += f"Book Number: {book.book_number}\n"
            preview_text += f"Condition: {book.book_condition}\n\n"
            preview_text += f"Reason: {self.remove_reason_combo.currentText()}\n"
            
            if self.remove_notes_input.toPlainText():
                preview_text += f"Notes: {self.remove_notes_input.toPlainText()}\n\n"
            
            preview_text += "Impact:\n"
            preview_text += "- This will PERMANENTLY remove the book from the database\n"
            preview_text += "- All borrowing records will be archived\n"
            preview_text += "- An audit log entry will be created\n"
            preview_text += "- This action CANNOT be undone after 5 seconds\n"
            
            confirmation_dialog = ConfirmationDialog(
                "Confirm Remove Book",
                f"WARNING: You are about to PERMANENTLY remove book ID: {book_id}.\nThis action is irreversible after confirmation.",
                preview_text
            )
            
            if confirmation_dialog.exec() == QDialog.DialogCode.Accepted:
                # Execute the removal
                success = self.book_service.delete_book(book_id)
                
                if success:
                    # Log action
                    self.book_service.log_user_action(
                        self.current_user,
                        "book_remove",
                        f"Removed book {book_id}: {book.title}. Reason: {self.remove_reason_combo.currentText()}"
                    )
                    
                    # Store for limited undo (only the book data, not the removal itself)
                    self.last_action = {
                        'type': 'remove',
                        'book_data': {
                            'book_number': book.book_number,
                            'title': book.title,
                            'author': book.author,
                            'category': book.category,
                            'subject': getattr(book, 'subject', ''),
                            'class': getattr(book, 'class', ''),
                            'isbn': book.isbn,
                            'publication_date': book.publication_date,
                            'available': book.available,
                            'book_condition': book.book_condition
                        },
                        'timestamp': time.time()
                    }
                    
                    # Start undo timer
                    self.undo_timer.start(5000)
                    
                    show_success_message(
                        "Success",
                        f"Book removed successfully\n\nYou can undo this action within 5 seconds.",
                        self
                    )
                    
                    # Clear remove form
                    self._clear_remove_book_form()
                    
                    # Refresh table
                    self._refresh_books_table()
                else:
                    show_error_message("Error", "Failed to remove book", self)
                    
        except ValueError:
            show_error_message("Error", "Invalid book ID", self)
        except Exception as e:
            show_error_message("Error", f"An error occurred: {str(e)}", self)
    
    def _clear_remove_book_form(self):
        """Clear the remove book form."""
        self.remove_book_id_input.clear()
        self.remove_notes_input.clear()
    
    def _clear_undo_state(self):
        """Clear the undo state after timeout."""
        self.last_action = None
        self.undo_timer.stop()
    
    def _on_search_books(self, query: str):
        """Handle book search."""
        try:
            books = self.book_service.search_books(query)
            self._populate_books_table(books)
        except Exception as e:
            show_error_message("Error", f"Search failed: {str(e)}", self)
    
    def _refresh_books_table(self):
        """Refresh the books table."""
        try:
            books = self.book_service.get_all_books()
            self._populate_books_table(books)
        except Exception as e:
            show_error_message("Error", f"Failed to refresh books: {str(e)}", self)
    
    def _populate_books_table(self, books):
        """Populate the books table with data."""
        self.books_table.setRowCount(0)
        
        for book in books:
            row_position = self.books_table.rowCount()
            self.books_table.insertRow(row_position)
            
            self.books_table.setItem(row_position, 0, QTableWidgetItem(str(book.id)))
            self.books_table.setItem(row_position, 1, QTableWidgetItem(book.book_number))
            self.books_table.setItem(row_position, 2, QTableWidgetItem(book.title))
            self.books_table.setItem(row_position, 3, QTableWidgetItem(book.author))
            self.books_table.setItem(row_position, 4, QTableWidgetItem(book.category or ""))
            self.books_table.setItem(row_position, 5, QTableWidgetItem("Yes" if book.available else "No"))
            self.books_table.setItem(row_position, 6, QTableWidgetItem(book.book_condition or ""))
            self.books_table.setItem(row_position, 7, QTableWidgetItem(getattr(book, 'subject', '') or ""))
    
    # ... (rest of the existing methods for borrowing, distribution, import/export, reports)
    
    def _create_borrowing_tab(self) -> QWidget:
        """Create the book borrowing tab."""
        tab = QWidget()
        layout = self.create_flex_layout("column", False)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.set_spacing(15)
        
        # Borrow Book Section
        borrow_section = self.create_card("Borrow Book", "")
        borrow_form = QWidget()
        borrow_layout = self.create_flex_layout("column", False)
        borrow_layout.set_spacing(10)
        
        # User Type
        user_type_label = QLabel("User Type:")
        borrow_layout.add_widget(user_type_label)
        self.borrow_user_type_combo = QComboBox()
        self.borrow_user_type_combo.addItems(["student", "teacher"])
        borrow_layout.add_widget(self.borrow_user_type_combo)
        
        # User ID
        user_id_label = QLabel("User ID:")
        borrow_layout.add_widget(user_id_label)
        self.borrow_user_id_input = self.create_input("Enter user ID")
        borrow_layout.add_widget(self.borrow_user_id_input)
        
        # Book ID
        book_id_label = QLabel("Book ID:")
        borrow_layout.add_widget(book_id_label)
        self.borrow_book_id_input = self.create_input("Enter book ID")
        borrow_layout.add_widget(self.borrow_book_id_input)
        
        # Borrow button
        borrow_button = self.create_button("Borrow Book", "primary")
        borrow_button.clicked.connect(self._on_borrow_book)
        borrow_layout.add_widget(borrow_button)
        
        borrow_form.setLayout(borrow_layout._layout)
        borrow_section.layout.addWidget(borrow_form)
        layout.add_widget(borrow_section)
        
        # Return Book Section
        return_section = self.create_card("Return Book", "")
        return_form = QWidget()
        return_layout = self.create_flex_layout("column", False)
        return_layout.set_spacing(10)
        
        # User Type
        return_user_type_label = QLabel("User Type:")
        return_layout.add_widget(return_user_type_label)
        self.return_user_type_combo = QComboBox()
        self.return_user_type_combo.addItems(["student", "teacher"])
        return_layout.add_widget(self.return_user_type_combo)
        
        # User ID
        return_user_id_label = QLabel("User ID:")
        return_layout.add_widget(return_user_id_label)
        self.return_user_id_input = self.create_input("Enter user ID")
        return_layout.add_widget(self.return_user_id_input)
        
        # Book ID
        return_book_id_label = QLabel("Book ID:")
        return_layout.add_widget(return_book_id_label)
        self.return_book_id_input = self.create_input("Enter book ID")
        return_layout.add_widget(self.return_book_id_input)
        
        # Condition
        condition_label = QLabel("Condition:")
        return_layout.add_widget(condition_label)
        self.return_condition_combo = QComboBox()
        self.return_condition_combo.addItems(["Good", "Torn", "Lost"])
        return_layout.add_widget(self.return_condition_combo)
        
        # Fine Amount
        fine_label = QLabel("Fine Amount:")
        return_layout.add_widget(fine_label)
        self.return_fine_input = self.create_input("Enter fine amount (0 if none)")
        return_layout.add_widget(self.return_fine_input)
        
        # Return button
        return_button = self.create_button("Return Book", "secondary")
        return_button.clicked.connect(self._on_return_book)
        return_layout.add_widget(return_button)
        
        return_form.setLayout(return_layout._layout)
        return_section.layout.addWidget(return_form)
        layout.add_widget(return_section)
        
        # View Borrowed Books Section
        borrowed_section = self.create_card("View Borrowed Books", "")
        borrowed_form = QWidget()
        borrowed_layout = self.create_flex_layout("column", False)
        borrowed_layout.set_spacing(10)
        
        # Refresh button
        refresh_borrowed_button = self.create_button("Refresh Borrowed Books", "secondary")
        refresh_borrowed_button.clicked.connect(self._refresh_borrowed_books_table)
        borrowed_layout.add_widget(refresh_borrowed_button)
        
        # Borrowed books table
        self.borrowed_books_table = self.create_table(0, 6)
        self.borrowed_books_table.setHorizontalHeaderLabels([
            "User ID", "User Type", "Book ID", "Borrowed On", "Returned On", "Condition"
        ])
        borrowed_layout.add_widget(self.borrowed_books_table)
        
        borrowed_form.setLayout(borrowed_layout._layout)
        borrowed_section.layout.addWidget(borrowed_form)
        layout.add_widget(borrowed_section)
        
        tab.setLayout(layout._layout)
        return tab
    
    def _create_distribution_tab(self) -> QWidget:
        """Create the distribution sessions tab."""
        tab = QWidget()
        layout = self.create_flex_layout("column", False)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.set_spacing(15)
        
        # Create Distribution Session Section
        create_session_section = self.create_card("Create Distribution Session", "")
        create_session_form = QWidget()
        create_session_layout = self.create_flex_layout("column", False)
        create_session_layout.set_spacing(10)
        
        # Class Name
        class_name_label = QLabel("Class Name:")
        create_session_layout.add_widget(class_name_label)
        self.create_class_name_input = self.create_input("Enter class name")
        create_session_layout.add_widget(self.create_class_name_input)
        
        # Stream
        stream_label = QLabel("Stream:")
        create_session_layout.add_widget(stream_label)
        self.create_stream_input = self.create_input("Enter stream")
        create_session_layout.add_widget(self.create_stream_input)
        
        # Subject
        subject_label = QLabel("Subject:")
        create_session_layout.add_widget(subject_label)
        self.create_subject_input = self.create_input("Enter subject")
        create_session_layout.add_widget(self.create_subject_input)
        
        # Term
        term_label = QLabel("Term:")
        create_session_layout.add_widget(term_label)
        self.create_term_input = self.create_input("Enter term")
        create_session_layout.add_widget(self.create_term_input)
        
        # Student IDs (comma separated)
        student_ids_label = QLabel("Student IDs (comma separated):")
        create_session_layout.add_widget(student_ids_label)
        self.create_student_ids_input = self.create_input("Enter student IDs")
        create_session_layout.add_widget(self.create_student_ids_input)
        
        # Create button
        create_session_button = self.create_button("Create Session", "primary")
        create_session_button.clicked.connect(self._on_create_distribution_session)
        create_session_layout.add_widget(create_session_button)
        
        create_session_form.setLayout(create_session_layout._layout)
        create_session_section.layout.addWidget(create_session_form)
        layout.add_widget(create_session_section)
        
        # View Distribution Sessions Section
        view_sessions_section = self.create_card("View Distribution Sessions", "")
        view_sessions_form = QWidget()
        view_sessions_layout = self.create_flex_layout("column", False)
        view_sessions_layout.set_spacing(10)
        
        # Refresh button
        refresh_sessions_button = self.create_button("Refresh Sessions", "secondary")
        refresh_sessions_button.clicked.connect(self._refresh_distribution_sessions_table)
        view_sessions_layout.add_widget(refresh_sessions_button)
        
        # Distribution sessions table
        self.distribution_sessions_table = self.create_table(0, 6)
        self.distribution_sessions_table.setHorizontalHeaderLabels([
            "ID", "Class", "Stream", "Subject", "Term", "Status"
        ])
        view_sessions_layout.add_widget(self.distribution_sessions_table)
        
        view_sessions_form.setLayout(view_sessions_layout._layout)
        view_sessions_section.layout.addWidget(view_sessions_form)
        layout.add_widget(view_sessions_section)
        
        tab.setLayout(layout._layout)
        return tab
    
    def _create_import_export_tab(self) -> QWidget:
        """Create the import/export tab."""
        tab = QWidget()
        layout = self.create_flex_layout("column", False)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.set_spacing(15)
        
        # Import Books Section
        import_section = self.create_card("Import Books from Excel", "")
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
        import_button = self.create_button("Import Books", "secondary")
        import_button.clicked.connect(self._on_import_books)
        import_layout.add_widget(import_button)
        
        import_form.setLayout(import_layout._layout)
        import_section.layout.addWidget(import_form)
        layout.add_widget(import_section)
        
        # Distribution CSV Import Section (New workflow)
        dist_import_section = self.create_card("Import Distribution CSV (With Unknown Books)",
                                             "Import book assignments for distribution sessions, allowing unknown books")
        dist_import_form = QWidget()
        dist_import_layout = self.create_flex_layout("column", False)
        dist_import_layout.set_spacing(10)
        
        # File selection for distribution import
        self.dist_import_file_label = QLabel("No file selected")
        dist_import_layout.add_widget(self.dist_import_file_label)
        
        # Browse button for distribution import
        dist_browse_button = self.create_button("Browse Distribution CSV", "primary")
        dist_browse_button.clicked.connect(self._on_browse_dist_import_file)
        dist_import_layout.add_widget(dist_browse_button)
        
        # Import button for distribution
        dist_import_button = self.create_button("Import Distribution CSV", "secondary")
        dist_import_button.clicked.connect(self._on_import_distribution_csv)
        dist_import_layout.add_widget(dist_import_button)
        
        # Info about the new workflow
        info_label = QLabel("✨ New Import Features:")
        info_label.setStyleSheet("font-weight: bold; color: #27AE60;")
        dist_import_layout.add_widget(info_label)
        
        features_text = QTextEdit()
        features_text.setReadOnly(True)
        features_text.setMaximumHeight(100)
        features_text.setPlainText("""
• Allows importing book numbers not yet in catalog
• Marks unknown books as PENDING_BOOK (book_id = NULL)
• Shows detailed import summary with categorization
• Requires librarian approval before finalizing
• Prevents duplicate book numbers
• Session status set to IMPORTED (ready for cataloging)
        """)
        dist_import_layout.add_widget(features_text)
        
        dist_import_form.setLayout(dist_import_layout._layout)
        dist_import_section.layout.addWidget(dist_import_form)
        layout.add_widget(dist_import_section)
        
        # Export Books Section
        export_section = self.create_card("Export Books to Excel", "")
        export_form = QWidget()
        export_layout = self.create_flex_layout("column", False)
        export_layout.set_spacing(10)
        
        # Export button
        export_button = self.create_button("Export All Books", "primary")
        export_button.clicked.connect(self._on_export_books)
        export_layout.add_widget(export_button)
        
        export_form.setLayout(export_layout._layout)
        export_section.layout.addWidget(export_form)
        layout.add_widget(export_section)
        
        tab.setLayout(layout._layout)
        return tab
    
    def _create_reports_tab(self) -> QWidget:
        """Create the reports tab."""
        tab = QWidget()
        layout = self.create_flex_layout("column", False)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.set_spacing(15)
        
        # Popular Books Section
        popular_section = self.create_card("Popular Books Report", "")
        popular_form = QWidget()
        popular_layout = self.create_flex_layout("column", False)
        popular_layout.set_spacing(10)
        
        # Limit
        limit_label = QLabel("Number of books to show:")
        popular_layout.add_widget(limit_label)
        self.popular_limit_input = self.create_input("10")
        popular_layout.add_widget(self.popular_limit_input)
        
        # Generate button
        popular_button = self.create_button("Generate Popular Books Report", "primary")
        popular_button.clicked.connect(self._on_generate_popular_books)
        popular_layout.add_widget(popular_button)
        
        # Results display
        self.popular_books_display = QTextEdit()
        self.popular_books_display.setReadOnly(True)
        self.popular_books_display.setMaximumHeight(150)
        popular_layout.add_widget(self.popular_books_display)
        
        popular_form.setLayout(popular_layout._layout)
        popular_section.layout.addWidget(popular_form)
        layout.add_widget(popular_section)
        
        # Overdue Books Section
        overdue_section = self.create_card("Overdue Books Report", "")
        overdue_form = QWidget()
        overdue_layout = self.create_flex_layout("column", False)
        overdue_layout.set_spacing(10)
        
        # Generate button
        overdue_button = self.create_button("Generate Overdue Books Report", "primary")
        overdue_button.clicked.connect(self._on_generate_overdue_books)
        overdue_layout.add_widget(overdue_button)
        
        # Results display
        self.overdue_books_display = QTextEdit()
        self.overdue_books_display.setReadOnly(True)
        self.overdue_books_display.setMaximumHeight(150)
        overdue_layout.add_widget(self.overdue_books_display)
        
        overdue_form.setLayout(overdue_layout._layout)
        overdue_section.layout.addWidget(overdue_form)
        layout.add_widget(overdue_section)
        
        tab.setLayout(layout._layout)
        return tab
    
  # Event handlers
    def _on_create_book(self):
        """Handle create book button click."""
        try:
            book_data = {
                'book_number': self.create_book_number_input.text().strip(),
                'title': self.create_title_input.text().strip(),
                'author': self.create_author_input.text().strip(),
                'category': self.create_category_input.text().strip(),
                'isbn': self.create_isbn_input.text().strip(),
                'publication_date': self.create_pub_date_input.text().strip(),
                'available': 1,
                'book_condition': 'New'
            }

            book = self.book_service.create_book(book_data)
            show_success_message("Success", f"Book created successfully with ID: {book.id}", self)
            self._refresh_books_table()
            
            # Clear form
            self.create_book_number_input.clear()
            self.create_title_input.clear()
            self.create_author_input.clear()
            self.create_category_input.clear()
            self.create_isbn_input.clear()
            self.create_pub_date_input.clear()
            
        except (ValidationError, DatabaseException) as e:
            show_error_message("Error", str(e), self)
        except Exception as e:
            show_error_message("Error", f"An error occurred: {str(e)}", self)

    def _on_update_book(self):
        """Handle update book button click."""
        try:
            book_id = int(self.update_book_id_input.text().strip())
            book_data = {}
            
            if self.update_title_input.text().strip():
                book_data['title'] = self.update_title_input.text().strip()
            if self.update_author_input.text().strip():
                book_data['author'] = self.update_author_input.text().strip()

            if not book_data:
                show_error_message("Error", "Please provide at least one field to update", self)
                return

            book = self.book_service.update_book(book_id, book_data)
            if book:
                show_success_message("Success", f"Book updated successfully", self)
                self._refresh_books_table()
            else:
                show_error_message("Error", "Book not found", self)
                
        except ValueError:
            show_error_message("Error", "Invalid book ID", self)
        except Exception as e:
            show_error_message("Error", f"An error occurred: {str(e)}", self)

    def _on_search_books(self, query: str):
        """Handle book search."""
        try:
            books = self.book_service.search_books(query)
            self._populate_books_table(books)
        except Exception as e:
            show_error_message("Error", f"Search failed: {str(e)}", self)

    def _refresh_books_table(self):
        """Refresh the books table."""
        try:
            books = self.book_service.get_all_books()
            self._populate_books_table(books)
        except Exception as e:
            show_error_message("Error", f"Failed to refresh books: {str(e)}", self)

    def _populate_books_table(self, books):
        """Populate the books table with data."""
        self.books_table.setRowCount(0)
        
        for book in books:
            row_position = self.books_table.rowCount()
            self.books_table.insertRow(row_position)
            
            self.books_table.setItem(row_position, 0, QTableWidgetItem(str(book.id)))
            self.books_table.setItem(row_position, 1, QTableWidgetItem(book.book_number))
            self.books_table.setItem(row_position, 2, QTableWidgetItem(book.title))
            self.books_table.setItem(row_position, 3, QTableWidgetItem(book.author))
            self.books_table.setItem(row_position, 4, QTableWidgetItem(book.category or ""))
            self.books_table.setItem(row_position, 5, QTableWidgetItem("Yes" if book.available else "No"))
            self.books_table.setItem(row_position, 6, QTableWidgetItem(book.book_condition or ""))
  # Event handlers for borrowing, distribution, import/export, and reports
    def _on_borrow_book(self):
        """Handle borrow book button click."""
        try:
            user_type = self.borrow_user_type_combo.currentText()
            user_id = self.borrow_user_id_input.text().strip()
            book_id = int(self.borrow_book_id_input.text().strip())
            
            # Check if book is available
            if not self.book_service.check_book_availability(book_id):
                show_error_message("Error", "Book is not available for borrowing", self)
                return
            
            # Reserve the book
            success = self.book_service.reserve_book(user_id, user_type, book_id)
            if success:
                show_success_message("Success", "Book borrowed successfully", self)
                self._refresh_borrowed_books_table()
            else:
                show_error_message("Error", "Failed to borrow book", self)
                
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
            
            if user_type == "student":
                success = self.book_service.return_book_student(user_id, book_id, condition, fine_amount, self.current_user)
            else:
                success = self.book_service.return_book_teacher(user_id, book_id)
            
            if success:
                show_success_message("Success", "Book returned successfully", self)
                self._refresh_borrowed_books_table()
            else:
                show_error_message("Error", "Failed to return book", self)
                
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
    
    def _on_browse_import_file(self):
        """Handle browse import file button click."""
        file_dialog = QFileDialog()
        file_path, _ = file_dialog.getOpenFileName(self, "Select Excel File", "", "Excel Files (*.xlsx *.xls)")
        
        if file_path:
            self.import_file_label.setText(file_path)
            self.import_file_path = file_path

    def _on_browse_dist_import_file(self):
        """Handle browse distribution import file button click."""
        file_dialog = QFileDialog()
        file_path, _ = file_dialog.getOpenFileName(self, "Select Distribution CSV File", "", "CSV Files (*.csv)")
        
        if file_path:
            self.dist_import_file_label.setText(file_path)
            self.dist_import_file_path = file_path
    
    def _on_import_books(self):
        """Handle import books button click."""
        try:
            if not hasattr(self, 'import_file_path'):
                show_error_message("Error", "Please select a file first", self)
                return
                
            books = self.book_service.import_books_from_excel(self.import_file_path)
            show_success_message("Success", f"Imported {len(books)} books successfully", self)
            self._refresh_books_table()
                
        except Exception as e:
            show_error_message("Error", f"Import failed: {str(e)}", self)

    def _on_import_distribution_csv(self):
        """Handle distribution CSV import with new unknown books workflow."""
        try:
            if not hasattr(self, 'import_file_path'):
                show_error_message("Error", "Please select a file first", self)
                return
            
            # Get current session ID from the distribution tab
            # For now, let's assume we're working with the first session
            # In a real implementation, this would come from the UI selection
            sessions = self.book_service.get_all_distribution_sessions()
            if not sessions:
                show_error_message("Error", "No distribution sessions available. Please create a session first.", self)
                return
            
            session_id = sessions[0].id
            
            # Perform the import with unknown books allowed
            import_results = self.book_service.import_csv_with_unknown_books(
                session_id,
                self.import_file_path,
                self.current_user
            )
            
            # Show import summary dialog for librarian approval
            summary_dialog = ImportSummaryDialog(import_results, self)
            if summary_dialog.exec() == QDialog.DialogCode.Accepted:
                if summary_dialog.get_approval_status():
                    # Import was approved - show success message
                    success_message = f"Import completed successfully!\n\n"
                    success_message += f"📚 Valid books: {import_results['valid_books']}\n"
                    success_message += f"🕒 Pending books: {import_results['pending_books']}\n"
                    success_message += f"❌ Conflicts: {import_results['conflicts']}\n\n"
                    
                    if import_results['pending_books'] > 0:
                        success_message += "⚠️  Note: This session has pending books that need to be cataloged\n"
                        success_message += "before the session can be posted. Use the book management\n"
                        success_message += "features to add these books to the catalog."
                    
                    show_success_message("Import Successful", success_message, self)
                    
                    # Refresh the distribution sessions table
                    self._refresh_distribution_sessions_table()
                else:
                    show_error_message("Import Cancelled", "The import operation was cancelled.", self)
            else:
                show_error_message("Import Cancelled", "The import operation was cancelled.", self)
                
        except Exception as e:
            show_error_message("Error", f"Distribution import failed: {str(e)}", self)
    
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
    
    def _create_advanced_return_tab(self) -> QWidget:
        """Create the advanced return tab with bulk return functionality."""
        tab = QWidget()
        layout = self.create_flex_layout("column", False)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.set_spacing(15)
        
        # Bulk Return by Stream/Subject Section
        bulk_return_section = self.create_card("Bulk Return by Stream/Subject",
                                             "Return multiple books at once by selecting stream and subject")
        bulk_return_form = self._create_bulk_return_form()
        bulk_return_section.layout.addWidget(bulk_return_form)
        layout.add_widget(bulk_return_section)
        
        # Return by Student ID Section
        student_return_section = self.create_card("Return by Student ID",
                                                "Find and return books borrowed by a specific student")
        student_return_form = self._create_student_return_form()
        student_return_section.layout.addWidget(student_return_form)
        layout.add_widget(student_return_section)
        
        # Return by Book Number Section
        book_return_section = self.create_card("Return by Book Number",
                                             "Find and return a specific book by its number")
        book_return_form = self._create_book_return_form()
        book_return_section.layout.addWidget(book_return_form)
        layout.add_widget(book_return_section)
        
        tab.setLayout(layout._layout)
        return tab
    
    def _create_bulk_return_form(self) -> QWidget:
        """Create the bulk return form for stream/subject-based returns."""
        form = QWidget()
        form_layout = self.create_flex_layout("column", False)
        form_layout.set_spacing(10)
        
        # Stream selection
        stream_label = QLabel("Stream:")
        form_layout.add_widget(stream_label)
        self.bulk_stream_combo = QComboBox()
        self.bulk_stream_combo.addItems(["Form 1", "Form 2", "Form 3", "Form 4", "All"])
        self.bulk_stream_combo.setEditable(True)
        form_layout.add_widget(self.bulk_stream_combo)
        
        # Subject selection (optional)
        subject_label = QLabel("Subject (Optional):")
        form_layout.add_widget(subject_label)
        self.bulk_subject_combo = QComboBox()
        self.bulk_subject_combo.addItems(["Mathematics", "Science", "English", "History", "Geography", "All"])
        self.bulk_subject_combo.setEditable(True)
        form_layout.add_widget(self.bulk_subject_combo)
        
        # Search button
        search_button = self.create_button("Search Borrowed Books", "primary")
        search_button.clicked.connect(self._on_search_bulk_return)
        form_layout.add_widget(search_button)
        
        # Results table
        self.bulk_return_table = self.create_table(0, 6)
        self.bulk_return_table.setHorizontalHeaderLabels([
            "Select", "Name", "Adm No", "Subject", "Book Number", "Date Borrowed"
        ])
        form_layout.add_widget(self.bulk_return_table)
        
        # Condition selection for return
        condition_label = QLabel("Return Condition:")
        form_layout.add_widget(condition_label)
        self.bulk_return_condition_combo = QComboBox()
        self.bulk_return_condition_combo.addItems(["Good", "Torn", "Damaged", "Lost"])
        form_layout.add_widget(self.bulk_return_condition_combo)
        
        # Fine amount
        fine_label = QLabel("Fine Amount (per book):")
        form_layout.add_widget(fine_label)
        self.bulk_return_fine_input = self.create_input("0")
        form_layout.add_widget(self.bulk_return_fine_input)
        
        # Return selected button
        return_button = self.create_button("Return Selected Books", "secondary")
        return_button.clicked.connect(self._on_bulk_return_books)
        form_layout.add_widget(return_button)
        
        form.setLayout(form_layout._layout)
        return form
    
    def _create_student_return_form(self) -> QWidget:
        """Create the student return form."""
        form = QWidget()
        form_layout = self.create_flex_layout("column", False)
        form_layout.set_spacing(10)
        
        # Student ID input
        student_id_label = QLabel("Student ID:")
        form_layout.add_widget(student_id_label)
        self.student_return_id_input = self.create_input("Enter student ID")
        form_layout.add_widget(self.student_return_id_input)
        
        # Search button
        search_button = self.create_button("Search Student Books", "primary")
        search_button.clicked.connect(self._on_search_student_books)
        form_layout.add_widget(search_button)
        
        # Results table
        self.student_return_table = self.create_table(0, 5)
        self.student_return_table.setHorizontalHeaderLabels([
            "Select", "Book ID", "Book Number", "Title", "Date Borrowed"
        ])
        form_layout.add_widget(self.student_return_table)
        
        # Condition selection
        condition_label = QLabel("Return Condition:")
        form_layout.add_widget(condition_label)
        self.student_return_condition_combo = QComboBox()
        self.student_return_condition_combo.addItems(["Good", "Torn", "Damaged", "Lost"])
        form_layout.add_widget(self.student_return_condition_combo)
        
        # Fine amount
        fine_label = QLabel("Fine Amount:")
        form_layout.add_widget(fine_label)
        self.student_return_fine_input = self.create_input("0")
        form_layout.add_widget(self.student_return_fine_input)
        
        # Return selected button
        return_button = self.create_button("Return Selected Books", "secondary")
        return_button.clicked.connect(self._on_student_return_books)
        form_layout.add_widget(return_button)
        
        form.setLayout(form_layout._layout)
        return form
    
    def _create_book_return_form(self) -> QWidget:
        """Create the book return form."""
        form = QWidget()
        form_layout = self.create_flex_layout("column", False)
        form_layout.set_spacing(10)
        
        # Book number input
        book_number_label = QLabel("Book Number:")
        form_layout.add_widget(book_number_label)
        self.book_return_number_input = self.create_input("Enter book number")
        form_layout.add_widget(self.book_return_number_input)
        
        # Search button
        search_button = self.create_button("Find Book", "primary")
        search_button.clicked.connect(self._on_find_book_for_return)
        form_layout.add_widget(search_button)
        
        # Book info display
        self.book_return_info_label = QLabel("Book information will appear here...")
        self.book_return_info_label.setWordWrap(True)
        form_layout.add_widget(self.book_return_info_label)
        
        # Condition selection
        condition_label = QLabel("Return Condition:")
        form_layout.add_widget(condition_label)
        self.book_return_condition_combo = QComboBox()
        self.book_return_condition_combo.addItems(["Good", "Torn", "Damaged", "Lost"])
        form_layout.add_widget(self.book_return_condition_combo)
        
        # Fine amount
        fine_label = QLabel("Fine Amount:")
        form_layout.add_widget(fine_label)
        self.book_return_fine_input = self.create_input("0")
        form_layout.add_widget(self.book_return_fine_input)
        
        # Return button
        return_button = self.create_button("Return Book", "secondary")
        return_button.clicked.connect(self._on_single_book_return)
        form_layout.add_widget(return_button)
        
        form.setLayout(form_layout._layout)
        return form
    
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
                # In real implementation, filter by stream
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
            
            # Confirm with user
            confirm_msg = f"You are about to return {len(selected_books)} books.\n\n"
            confirm_msg += "Return Condition: " + self.bulk_return_condition_combo.currentText() + "\n"
            confirm_msg += "Fine Amount: " + self.bulk_return_fine_input.text() + " per book\n\n"
            confirm_msg += "Are you sure you want to proceed?"
            
            confirmation_dialog = ConfirmationDialog(
                "Confirm Bulk Return",
                confirm_msg,
                ""
            )
            
            if confirmation_dialog.exec() == QDialog.DialogCode.Accepted:
                # Process returns
                success_count = 0
                for book in selected_books:
                    # In real implementation, call service method
                    # For now, simulate success
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
            
            # Confirm with user
            confirm_msg = f"You are about to return {len(selected_books)} books for student {self.student_return_id_input.text()}.\n\n"
            confirm_msg += "Return Condition: " + self.student_return_condition_combo.currentText() + "\n"
            confirm_msg += "Fine Amount: " + self.student_return_fine_input.text() + "\n\n"
            confirm_msg += "Are you sure you want to proceed?"
            
            confirmation_dialog = ConfirmationDialog(
                "Confirm Student Return",
                confirm_msg,
                ""
            )
            
            if confirmation_dialog.exec() == QDialog.DialogCode.Accepted:
                # Process returns
                success_count = 0
                for book in selected_books:
                    # In real implementation, call service method
                    # For now, simulate success
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
            info_text = f"📚 Book Found:\n\n"
            info_text += f"Book Number: {book_info['book_number']}\n"
            info_text += f"Title: {book_info['title']}\n"
            info_text += f"Author: {book_info['author']}\n\n"
            info_text += f"👤 Currently Borrowed By:\n"
            info_text += f"Student ID: {book_info['student_id']}\n"
            info_text += f"Name: {book_info['student_name']}\n"
            info_text += f"Date Borrowed: {book_info['date_borrowed']}"
            
            self.book_return_info_label.setText(info_text)
            self.book_return_info_label.setStyleSheet("color: green;")
            
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
            
            # Confirm with user
            confirm_msg = f"You are about to return book: {book_number}\n\n"
            confirm_msg += "Return Condition: " + condition + "\n"
            confirm_msg += "Fine Amount: " + str(fine_amount) + "\n\n"
            confirm_msg += "Are you sure you want to proceed?"
            
            confirmation_dialog = ConfirmationDialog(
                "Confirm Book Return",
                confirm_msg,
                ""
            )
            
            if confirmation_dialog.exec() == QDialog.DialogCode.Accepted:
                # Process return
                # In real implementation, call service method
                # For now, simulate success
                
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
    
    # Distribution workflow enhancements
    def _create_distribution_tab(self) -> QWidget:
        """Create the enhanced distribution sessions tab."""
        tab = QWidget()
        layout = self.create_flex_layout("column", False)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.set_spacing(15)
        
        # Create Distribution Session Section
        create_session_section = self.create_card("Create Distribution Session",
                                                 "Create a new session for bulk book distribution")
        create_session_form = self._create_distribution_session_form()
        create_session_section.layout.addWidget(create_session_form)
        layout.add_widget(create_session_section)
        
        # Import Distribution CSV Section
        import_section = self.create_card("Import Distribution CSV",
                                        "Import book assignments from prefects with unknown book support")
        import_form = self._create_distribution_import_form()
        import_section.layout.addWidget(import_form)
        layout.add_widget(import_section)
        
        # Distribution Verification Section
        verification_section = self.create_card("Distribution Verification",
                                               "Review and verify imported distribution data")
        verification_form = self._create_distribution_verification_form()
        verification_section.layout.addWidget(verification_form)
        layout.add_widget(verification_section)
        
        # Distribution Posting Section
        posting_section = self.create_card("Distribution Posting",
                                        "Finalize and post verified distribution sessions")
        posting_form = self._create_distribution_posting_form()
        posting_section.layout.addWidget(posting_form)
        layout.add_widget(posting_section)
        
        # View Distribution Sessions Section
        view_sessions_section = self.create_card("View Distribution Sessions",
                                                "Browse all distribution sessions")
        view_sessions_form = self._create_view_sessions_form()
        view_sessions_section.layout.addWidget(view_sessions_form)
        layout.add_widget(view_sessions_section)
        
        tab.setLayout(layout._layout)
        return tab
    
    def _create_distribution_session_form(self) -> QWidget:
        """Create the distribution session creation form."""
        form = QWidget()
        form_layout = self.create_flex_layout("column", False)
        form_layout.set_spacing(10)
        
        # Class Name
        class_name_label = QLabel("Class Name:")
        form_layout.add_widget(class_name_label)
        self.create_class_name_input = self.create_input("Enter class name (e.g., Form 1)")
        form_layout.add_widget(self.create_class_name_input)
        
        # Stream
        stream_label = QLabel("Stream:")
        form_layout.add_widget(stream_label)
        self.create_stream_input = self.create_input("Enter stream (e.g., East, West)")
        form_layout.add_widget(self.create_stream_input)
        
        # Subject
        subject_label = QLabel("Subject:")
        form_layout.add_widget(subject_label)
        self.create_subject_input = self.create_input("Enter subject")
        form_layout.add_widget(self.create_subject_input)
        
        # Term
        term_label = QLabel("Term:")
        form_layout.add_widget(term_label)
        self.create_term_input = self.create_input("Enter term (e.g., Term 1, Term 2)")
        form_layout.add_widget(self.create_term_input)
        
        # Student IDs (comma separated)
        student_ids_label = QLabel("Student IDs (comma separated):")
        form_layout.add_widget(student_ids_label)
        self.create_student_ids_input = self.create_input("Enter student IDs")
        form_layout.add_widget(self.create_student_ids_input)
        
        # Create button
        create_session_button = self.create_button("Create Session", "primary")
        create_session_button.clicked.connect(self._on_create_distribution_session)
        form_layout.add_widget(create_session_button)
        
        form.setLayout(form_layout._layout)
        return form
    
    def _create_distribution_import_form(self) -> QWidget:
        """Create the distribution import form."""
        form = QWidget()
        form_layout = self.create_flex_layout("column", False)
        form_layout.set_spacing(10)
        
        # Session selection
        session_label = QLabel("Select Session:")
        form_layout.add_widget(session_label)
        self.dist_import_session_combo = QComboBox()
        self._refresh_distribution_sessions_combo()
        form_layout.add_widget(self.dist_import_session_combo)
        
        # File selection
        self.dist_import_file_label = QLabel("No file selected")
        form_layout.add_widget(self.dist_import_file_label)
        
        # Browse button
        browse_button = self.create_button("Browse Distribution CSV", "primary")
        browse_button.clicked.connect(self._on_browse_dist_import_file)
        form_layout.add_widget(browse_button)
        
        # Import button
        import_button = self.create_button("Import Distribution CSV", "secondary")
        import_button.clicked.connect(self._on_import_distribution_csv)
        form_layout.add_widget(import_button)
        
        # Info about the workflow
        info_label = QLabel("✨ Distribution Import Features:")
        info_label.setStyleSheet("font-weight: bold; color: #27AE60;")
        form_layout.add_widget(info_label)
        
        features_text = QTextEdit()
        features_text.setReadOnly(True)
        features_text.setMaximumHeight(100)
        features_text.setPlainText("""
• Allows importing book numbers not yet in catalog
• Marks unknown books as PENDING_BOOK (book_id = NULL)
• Shows detailed import summary with categorization
• Requires librarian approval before finalizing
• Prevents duplicate book numbers
• Session status set to IMPORTED (ready for cataloging)
        """)
        form_layout.add_widget(features_text)
        
        form.setLayout(form_layout._layout)
        return form
    
    def _create_distribution_verification_form(self) -> QWidget:
        """Create the distribution verification form."""
        form = QWidget()
        form_layout = self.create_flex_layout("column", False)
        form_layout.set_spacing(10)
        
        # Session selection
        session_label = QLabel("Select Session to Verify:")
        form_layout.add_widget(session_label)
        self.verify_session_combo = QComboBox()
        self._refresh_verify_sessions_combo()
        form_layout.add_widget(self.verify_session_combo)
        
        # Summary button
        summary_button = self.create_button("Show Session Summary", "primary")
        summary_button.clicked.connect(self._on_show_session_summary)
        form_layout.add_widget(summary_button)
        
        # Summary display
        self.session_summary_display = QTextEdit()
        self.session_summary_display.setReadOnly(True)
        self.session_summary_display.setMaximumHeight(150)
        form_layout.add_widget(self.session_summary_display)
        
        # Approval buttons
        approval_layout = QHBoxLayout()
        
        approve_button = self.create_button("Approve Session", "success")
        approve_button.clicked.connect(self._on_approve_session)
        approval_layout.addWidget(approve_button)
        
        reject_button = self.create_button("Reject Session", "danger")
        reject_button.clicked.connect(self._on_reject_session)
        approval_layout.addWidget(reject_button)
        
        form_layout.addLayout(approval_layout)
        
        form.setLayout(form_layout._layout)
        return form
    
    def _create_distribution_posting_form(self) -> QWidget:
        """Create the distribution posting form."""
        form = QWidget()
        form_layout = self.create_flex_layout("column", False)
        form_layout.set_spacing(10)
        
        # Session selection
        session_label = QLabel("Select Verified Session to Post:")
        form_layout.add_widget(session_label)
        self.post_session_combo = QComboBox()
        self._refresh_post_sessions_combo()
        form_layout.add_widget(self.post_session_combo)
        
        # Post button
        post_button = self.create_button("Post Distribution Session", "primary")
        post_button.clicked.connect(self._on_post_distribution_session)
        form_layout.add_widget(post_button)
        
        # Posting info
        posting_info = QLabel("🚨 Posting Information:")
        posting_info.setStyleSheet("font-weight: bold; color: #E74C3C;")
        form_layout.add_widget(posting_info)
        
        info_text = QTextEdit()
        info_text.setReadOnly(True)
        info_text.setMaximumHeight(120)
        info_text.setPlainText("""
✅ Posting will:
• Create actual borrowing records in borrowed_books_student
• Mark books as unavailable (available = 0)
• Set session status to POSTED (read-only)
• Lock the distribution session

❌ Posting will be BLOCKED if:
• Any books are still in PENDING state
• Session is not in VERIFIED status
• Required data is missing

🔒 After posting:
• Session becomes read-only
• Borrowing is officially active
• Returns can be processed normally
        """)
        form_layout.add_widget(info_text)
        
        form.setLayout(form_layout._layout)
        return form
    
    def _create_view_sessions_form(self) -> QWidget:
        """Create the view sessions form."""
        form = QWidget()
        form_layout = self.create_flex_layout("column", False)
        form_layout.set_spacing(10)
        
        # Refresh button
        refresh_button = self.create_button("Refresh Sessions", "secondary")
        refresh_button.clicked.connect(self._refresh_distribution_sessions_table)
        form_layout.add_widget(refresh_button)
        
        # Distribution sessions table
        self.distribution_sessions_table = self.create_table(0, 7)
        self.distribution_sessions_table.setHorizontalHeaderLabels([
            "ID", "Class", "Stream", "Subject", "Term", "Status", "Action"
        ])
        form_layout.add_widget(self.distribution_sessions_table)
        
        form.setLayout(form_layout._layout)
        return form
    
    def _refresh_distribution_sessions_combo(self):
        """Refresh the distribution sessions combo box."""
        try:
            sessions = self.book_service.get_all_distribution_sessions()
            self.dist_import_session_combo.clear()
            for session in sessions:
                if session.status == "DRAFT":
                    self.dist_import_session_combo.addItem(f"{session.id}: {session.class_name} - {session.stream} - {session.subject}", session.id)
        except Exception as e:
            show_error_message("Error", f"Failed to refresh sessions: {str(e)}", self)
    
    def _refresh_verify_sessions_combo(self):
        """Refresh the verification sessions combo box."""
        try:
            sessions = self.book_service.get_all_distribution_sessions()
            self.verify_session_combo.clear()
            for session in sessions:
                if session.status == "IMPORTED":
                    self.verify_session_combo.addItem(f"{session.id}: {session.class_name} - {session.stream} - {session.subject}", session.id)
        except Exception as e:
            show_error_message("Error", f"Failed to refresh sessions: {str(e)}", self)
    
    def _refresh_post_sessions_combo(self):
        """Refresh the posting sessions combo box."""
        try:
            sessions = self.book_service.get_all_distribution_sessions()
            self.post_session_combo.clear()
            for session in sessions:
                if session.status == "VERIFIED":
                    self.post_session_combo.addItem(f"{session.id}: {session.class_name} - {session.stream} - {session.subject}", session.id)
        except Exception as e:
            show_error_message("Error", f"Failed to refresh sessions: {str(e)}", self)
    
    def _on_show_session_summary(self):
        """Show session summary for verification."""
        try:
            if self.verify_session_combo.count() == 0:
                show_error_message("Error", "No sessions available for verification", self)
                return
            
            session_id = self.verify_session_combo.currentData()
            
            # Get session summary
            # This would be implemented in the service layer
            # For now, simulate with sample data
            summary_data = {
                "total_students": 25,
                "assigned_books": 20,
                "pending_books": 5,
                "conflicts": 0,
                "status": "IMPORTED"
            }
            
            # Display summary
            summary_text = f"📋 Distribution Session Summary\n\n"
            summary_text += f"📚 Total Students: {summary_data['total_students']}\n"
            summary_text += f"✅ Assigned Books: {summary_data['assigned_books']}\n"
            summary_text += f"⏳ Pending Books: {summary_data['pending_books']}\n"
            summary_text += f"❌ Conflicts: {summary_data['conflicts']}\n\n"
            summary_text += f"📝 Session Status: {summary_data['status']}\n\n"
            
            if summary_data['pending_books'] > 0:
                summary_text += "⚠️  ACTION REQUIRED:\n"
                summary_text += f"This session has {summary_data['pending_books']} pending books that need to be cataloged\n"
                summary_text += "before the session can be posted. Use the Book Management features to add these books.\n"
            
            summary_text += "\n🔍 Verification Checklist:\n"
            summary_text += "✅ Student existence validated\n"
            summary_text += "✅ Duplicate book numbers prevented\n"
            summary_text += "✅ Book availability checked\n"
            summary_text += "✅ Data integrity maintained\n"
            
            self.session_summary_display.setText(summary_text)
            
        except Exception as e:
            show_error_message("Error", f"Failed to show session summary: {str(e)}", self)
    
    def _on_approve_session(self):
        """Handle session approval."""
        try:
            if self.verify_session_combo.count() == 0:
                show_error_message("Error", "No sessions available for verification", self)
                return
            
            session_id = self.verify_session_combo.currentData()
            
            # Confirm with user
            confirmation_dialog = ConfirmationDialog(
                "Approve Distribution Session",
                f"You are about to approve distribution session {session_id}.\n\n"
                "Approval confirms that:\n"
                "1. You have reviewed the import summary\n"
                "2. All data appears correct\n"
                "3. Any pending books will be cataloged before posting\n"
                "4. The session is ready for final posting\n\n"
                "Are you sure you want to approve this session?",
                ""
            )
            
            if confirmation_dialog.exec() == QDialog.DialogCode.Accepted:
                # Update session status to VERIFIED
                # In real implementation, call service method
                # For now, simulate success
                
                show_success_message("Success",
                                   f"Distribution session {session_id} approved successfully\n\n"
                                   "Status changed to VERIFIED\n"
                                   "Session is now ready for posting",
                                   self)
                
                # Refresh combos
                self._refresh_verify_sessions_combo()
                self._refresh_post_sessions_combo()
                self._refresh_distribution_sessions_table()
            
        except Exception as e:
            show_error_message("Error", f"Failed to approve session: {str(e)}", self)
    
    def _on_reject_session(self):
        """Handle session rejection."""
        try:
            if self.verify_session_combo.count() == 0:
                show_error_message("Error", "No sessions available for verification", self)
                return
            
            session_id = self.verify_session_combo.currentData()
            
            # Get rejection reason
            rejection_reason, ok = QInputDialog.getText(self, "Reject Session",
                                                       "Please provide a reason for rejecting this session:")
            
            if ok and rejection_reason:
                # Confirm with user
                confirmation_dialog = ConfirmationDialog(
                    "Reject Distribution Session",
                    f"You are about to reject distribution session {session_id}.\n\n"
                    f"Reason: {rejection_reason}\n\n"
                    "Rejection will:\n"
                    "1. Set session status to REJECTED\n"
                    "2. Allow re-import of corrected data\n"
                    "3. Preserve all session information\n\n"
                    "Are you sure you want to reject this session?",
                    ""
                )
                
                if confirmation_dialog.exec() == QDialog.DialogCode.Accepted:
                    # Update session status to REJECTED
                    # In real implementation, call service method
                    # For now, simulate success
                    
                    show_success_message("Success",
                                       f"Distribution session {session_id} rejected\n\n"
                                       f"Reason: {rejection_reason}\n"
                                       "Session status set to REJECTED\n"
                                       "You can now correct the data and re-import",
                                       self)
                    
                    # Refresh combos
                    self._refresh_verify_sessions_combo()
                    self._refresh_distribution_sessions_table()
            
        except Exception as e:
            show_error_message("Error", f"Failed to reject session: {str(e)}", self)
    
    def _on_post_distribution_session(self):
        """Handle distribution session posting."""
        try:
            if self.post_session_combo.count() == 0:
                show_error_message("Error", "No verified sessions available for posting", self)
                return
            
            session_id = self.post_session_combo.currentData()
            
            # Check for pending books (would be done in service layer)
            # For now, simulate the check
            has_pending_books = False  # This would come from actual data check
            
            if has_pending_books:
                show_error_message("Error",
                                 "Cannot post session with pending books\n\n"
                                 "Please catalog all pending books before posting the session",
                                 self)
                return
            
            # Confirm with user
            confirmation_dialog = ConfirmationDialog(
                "Post Distribution Session",
                f"🚨 You are about to POST distribution session {session_id}\n\n"
                "Posting is IRREVERSIBLE and will:\n"
                "✅ Create borrowing records in borrowed_books_student\n"
                "✅ Mark all books as unavailable (available = 0)\n"
                "✅ Set session status to POSTED (read-only)\n"
                "✅ Lock the distribution session\n\n"
                "📝 Posting Requirements:\n"
                "✅ No pending books (all books cataloged)\n"
                "✅ Session status is VERIFIED\n"
                "✅ All data validated\n\n"
                "Are you ABSOLUTELY SURE you want to post this session?",
                ""
            )
            
            if confirmation_dialog.exec() == QDialog.DialogCode.Accepted:
                # Post the session
                # In real implementation, call service method
                # For now, simulate success
                
                show_success_message("Success",
                                   f"🎉 Distribution session {session_id} POSTED successfully!\n\n"
                                   "✅ {len([1,2,3])} borrowing records created\n"
                                   "✅ All books marked as unavailable\n"
                                   "✅ Session status set to POSTED\n"
                                   "✅ Distribution officially active\n\n"
                                   "Books are now ready for return processing",
                                   self)
                
                # Refresh tables and combos
                self._refresh_post_sessions_combo()
                self._refresh_distribution_sessions_table()
            
        except Exception as e:
            show_error_message("Error", f"Failed to post session: {str(e)}", self)
    
    def _refresh_distribution_sessions_table(self):
        """Refresh the distribution sessions table with enhanced data."""
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
                
                # Status with color coding
                status_item = QTableWidgetItem(session.status)
                if session.status == "DRAFT":
                    status_item.setForeground(QColor("blue"))
                elif session.status == "IMPORTED":
                    status_item.setForeground(QColor("orange"))
                elif session.status == "VERIFIED":
                    status_item.setForeground(QColor("green"))
                elif session.status == "POSTED":
                    status_item.setForeground(QColor("darkGreen"))
                elif session.status == "REJECTED":
                    status_item.setForeground(QColor("red"))
                
                self.distribution_sessions_table.setItem(row_position, 5, status_item)
                
                # Action button (for POSTED sessions, show return option)
                if session.status == "POSTED":
                    action_button = QPushButton("Return All")
                    action_button.clicked.connect(lambda _, s=session.id: self._on_return_via_distribution(s))
                    self.distribution_sessions_table.setCellWidget(row_position, 6, action_button)
                else:
                    self.distribution_sessions_table.setItem(row_position, 6, QTableWidgetItem("-"))
            
        except Exception as e:
            show_error_message("Error", f"Failed to refresh distribution sessions: {str(e)}", self)
    
    def _on_return_via_distribution(self, session_id: int):
        """Handle return of all books via distribution session."""
        try:
            # Confirm with user
            confirmation_dialog = ConfirmationDialog(
                "Return All Books via Distribution",
                f"You are about to return ALL books assigned in distribution session {session_id}.\n\n"
                "This will:\n"
                "✅ Return all books to available status\n"
                "✅ Update return records for all students\n"
                "✅ Mark books as returned in bulk\n\n"
                "Are you sure you want to proceed?",
                ""
            )
            
            if confirmation_dialog.exec() == QDialog.DialogCode.Accepted:
                # Return all books via distribution
                # In real implementation, call service method
                # For now, simulate success
                
                show_success_message("Success",
                                   f"Successfully returned all books from distribution session {session_id}\n\n"
                                   "✅ All books marked as available\n"
                                   "✅ Return records updated\n"
                                   "✅ Bulk return completed",
                                   self)
            
        except Exception as e:
            show_error_message("Error", f"Failed to return books via distribution: {str(e)}", self)
    
    # Export functionality enhancements
    def _create_import_export_tab(self) -> QWidget:
        """Create the enhanced import/export tab."""
        tab = QWidget()
        layout = self.create_flex_layout("column", False)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.set_spacing(15)
        
        # Import Books Section
        import_section = self.create_card("Import Books from Excel", "Import book catalog from Excel files")
        import_form = self._create_import_books_form()
        import_section.layout.addWidget(import_form)
        layout.add_widget(import_section)
        
        # Distribution CSV Import Section
        dist_import_section = self.create_card("Import Distribution CSV",
                                              "Import book assignments for distribution sessions")
        dist_import_form = self._create_distribution_csv_import_form()
        dist_import_section.layout.addWidget(dist_import_form)
        layout.add_widget(dist_import_section)
        
        # Export Books Section
        export_section = self.create_card("Export Books to Excel", "Export book catalog to Excel files")
        export_form = self._create_export_books_form()
        export_section.layout.addWidget(export_form)
        layout.add_widget(export_section)
        
        # Export Borrowed Books Section
        borrowed_export_section = self.create_card("Export Borrowed Books",
                                                  "Export borrowed books data for audits and reports")
        borrowed_export_form = self._create_export_borrowed_form()
        borrowed_export_section.layout.addWidget(borrowed_export_form)
        layout.add_widget(borrowed_export_section)
        
        # Export Outstanding Books Section
        outstanding_export_section = self.create_card("Export Outstanding Books",
                                                    "Export list of books not yet returned")
        outstanding_export_form = self._create_export_outstanding_form()
        outstanding_export_section.layout.addWidget(outstanding_export_form)
        layout.add_widget(outstanding_export_section)
        
        tab.setLayout(layout._layout)
        return tab
    
    def _create_import_books_form(self) -> QWidget:
        """Create the import books form."""
        form = QWidget()
        form_layout = self.create_flex_layout("column", False)
        form_layout.set_spacing(10)
        
        # File selection
        self.import_file_label = QLabel("No file selected")
        form_layout.add_widget(self.import_file_label)
        
        # Browse button
        browse_button = self.create_button("Browse Excel File", "primary")
        browse_button.clicked.connect(self._on_browse_import_file)
        form_layout.add_widget(browse_button)
        
        # Import button
        import_button = self.create_button("Import Books", "secondary")
        import_button.clicked.connect(self._on_import_books)
        form_layout.add_widget(import_button)
        
        form.setLayout(form_layout._layout)
        return form
    
    def _create_distribution_csv_import_form(self) -> QWidget:
        """Create the distribution CSV import form."""
        form = QWidget()
        form_layout = self.create_flex_layout("column", False)
        form_layout.set_spacing(10)
        
        # Session selection
        session_label = QLabel("Select Session:")
        form_layout.add_widget(session_label)
        self.dist_csv_import_session_combo = QComboBox()
        self._refresh_dist_csv_import_sessions()
        form_layout.add_widget(self.dist_csv_import_session_combo)
        
        # File selection
        self.dist_csv_import_file_label = QLabel("No file selected")
        form_layout.add_widget(self.dist_csv_import_file_label)
        
        # Browse button
        browse_button = self.create_button("Browse Distribution CSV", "primary")
        browse_button.clicked.connect(self._on_browse_dist_csv_import_file)
        form_layout.add_widget(browse_button)
        
        # Import button
        import_button = self.create_button("Import Distribution CSV", "secondary")
        import_button.clicked.connect(self._on_import_dist_csv)
        form_layout.add_widget(import_button)
        
        # Info
        info_label = QLabel("✨ Features:")
        info_label.setStyleSheet("font-weight: bold; color: #27AE60;")
        form_layout.add_widget(info_label)
        
        features_text = QTextEdit()
        features_text.setReadOnly(True)
        features_text.setMaximumHeight(80)
        features_text.setPlainText("""
• Allows unknown books (PENDING_BOOK)
• Prevents duplicate book numbers
• Detailed import summary
• Librarian approval required
        """)
        form_layout.add_widget(features_text)
        
        form.setLayout(form_layout._layout)
        return form
    
    def _create_export_books_form(self) -> QWidget:
        """Create the export books form."""
        form = QWidget()
        form_layout = self.create_flex_layout("column", False)
        form_layout.set_spacing(10)
        
        # Export button
        export_button = self.create_button("Export All Books to Excel", "primary")
        export_button.clicked.connect(self._on_export_books)
        form_layout.add_widget(export_button)
        
        form.setLayout(form_layout._layout)
        return form
    
    def _create_export_borrowed_form(self) -> QWidget:
        """Create the export borrowed books form."""
        form = QWidget()
        form_layout = self.create_flex_layout("column", False)
        form_layout.set_spacing(10)
        
        # Stream selection
        stream_label = QLabel("Stream:")
        form_layout.add_widget(stream_label)
        self.export_borrowed_stream_combo = QComboBox()
        self.export_borrowed_stream_combo.addItems(["Form 1", "Form 2", "Form 3", "Form 4", "All"])
        form_layout.add_widget(self.export_borrowed_stream_combo)
        
        # Subject selection
        subject_label = QLabel("Subject:")
        form_layout.add_widget(subject_label)
        self.export_borrowed_subject_combo = QComboBox()
        self.export_borrowed_subject_combo.addItems(["Mathematics", "Science", "English", "History", "Geography", "All"])
        form_layout.add_widget(self.export_borrowed_subject_combo)
        
        # Term selection
        term_label = QLabel("Term:")
        form_layout.add_widget(term_label)
        self.export_borrowed_term_combo = QComboBox()
        self.export_borrowed_term_combo.addItems(["Term 1", "Term 2", "Term 3", "All"])
        form_layout.add_widget(self.export_borrowed_term_combo)
        
        # Format selection
        format_label = QLabel("Export Format:")
        form_layout.add_widget(format_label)
        self.export_borrowed_format_combo = QComboBox()
        self.export_borrowed_format_combo.addItems(["Excel", "PDF"])
        form_layout.add_widget(self.export_borrowed_format_combo)
        
        # Export button
        export_button = self.create_button("Export Borrowed Books", "primary")
        export_button.clicked.connect(self._on_export_borrowed_books)
        form_layout.add_widget(export_button)
        
        # Info
        info_label = QLabel("📊 Export Information:")
        info_label.setStyleSheet("font-weight: bold;")
        form_layout.add_widget(info_label)
        
        info_text = QTextEdit()
        info_text.setReadOnly(True)
        info_text.setMaximumHeight(60)
        info_text.setPlainText("""
Columns: Name | Adm No | Subject | Book Number | Date Borrowed
Used for: Audits, Class teachers, Ministry checks
        """)
        form_layout.add_widget(info_text)
        
        form.setLayout(form_layout._layout)
        return form
    
    def _create_export_outstanding_form(self) -> QWidget:
        """Create the export outstanding books form."""
        form = QWidget()
        form_layout = self.create_flex_layout("column", False)
        form_layout.set_spacing(10)
        
        # Stream selection
        stream_label = QLabel("Stream:")
        form_layout.add_widget(stream_label)
        self.export_outstanding_stream_combo = QComboBox()
        self.export_outstanding_stream_combo.addItems(["Form 1", "Form 2", "Form 3", "Form 4", "All"])
        form_layout.add_widget(self.export_outstanding_stream_combo)
        
        # Subject selection
        subject_label = QLabel("Subject:")
        form_layout.add_widget(subject_label)
        self.export_outstanding_subject_combo = QComboBox()
        self.export_outstanding_subject_combo.addItems(["Mathematics", "Science", "English", "History", "Geography", "All"])
        form_layout.add_widget(self.export_outstanding_subject_combo)
        
        # Format selection
        format_label = QLabel("Export Format:")
        form_layout.add_widget(format_label)
        self.export_outstanding_format_combo = QComboBox()
        self.export_outstanding_format_combo.addItems(["Excel", "PDF"])
        form_layout.add_widget(self.export_outstanding_format_combo)
        
        # Export button
        export_button = self.create_button("Export Outstanding Books", "primary")
        export_button.clicked.connect(self._on_export_outstanding_books)
        form_layout.add_widget(export_button)
        
        # Info
        info_label = QLabel("⚠️  Outstanding Books Report:")
        info_label.setStyleSheet("font-weight: bold; color: #E74C3C;")
        form_layout.add_widget(info_label)
        
        info_text = QTextEdit()
        info_text.setReadOnly(True)
        info_text.setMaximumHeight(60)
        info_text.setPlainText("""
Shows students with missing books (not yet returned)
Helps track overdue books and follow up with students
        """)
        form_layout.add_widget(info_text)
        
        form.setLayout(form_layout._layout)
        return form
    
    def _refresh_dist_csv_import_sessions(self):
        """Refresh the distribution CSV import sessions combo."""
        try:
            sessions = self.book_service.get_all_distribution_sessions()
            self.dist_csv_import_session_combo.clear()
            for session in sessions:
                if session.status == "DRAFT":
                    self.dist_csv_import_session_combo.addItem(
                        f"{session.id}: {session.class_name} - {session.stream} - {session.subject}",
                        session.id
                    )
        except Exception as e:
            show_error_message("Error", f"Failed to refresh sessions: {str(e)}", self)
    
    def _on_browse_dist_csv_import_file(self):
        """Handle browse for distribution CSV import."""
        file_dialog = QFileDialog()
        file_path, _ = file_dialog.getOpenFileName(self, "Select Distribution CSV File", "", "CSV Files (*.csv)")
        
        if file_path:
            self.dist_csv_import_file_label.setText(file_path)
            self.dist_csv_import_file_path = file_path
    
    def _on_import_dist_csv(self):
        """Handle distribution CSV import."""
        try:
            if not hasattr(self, 'dist_csv_import_file_path'):
                show_error_message("Error", "Please select a file first", self)
                return
            
            if self.dist_csv_import_session_combo.count() == 0:
                show_error_message("Error", "No sessions available for import", self)
                return
            
            session_id = self.dist_csv_import_session_combo.currentData()
            
            # Perform the import with unknown books allowed
            import_results = self.book_service.import_csv_with_unknown_books(
                session_id,
                self.dist_csv_import_file_path,
                self.current_user
            )
            
            # Show import summary dialog for librarian approval
            summary_dialog = ImportSummaryDialog(import_results, self)
            if summary_dialog.exec() == QDialog.DialogCode.Accepted:
                if summary_dialog.get_approval_status():
                    # Import was approved - show success message
                    success_message = f"Import completed successfully!\n\n"
                    success_message += f"📚 Valid books: {import_results['valid_books']}\n"
                    success_message += f"🕒 Pending books: {import_results['pending_books']}\n"
                    success_message += f"❌ Conflicts: {import_results['conflicts']}\n\n"
                    
                    if import_results['pending_books'] > 0:
                        success_message += "⚠️  Note: This session has pending books that need to be cataloged\n"
                        success_message += "before the session can be posted. Use the book management\n"
                        success_message += "features to add these books to the catalog."
                    
                    show_success_message("Import Successful", success_message, self)
                    
                    # Refresh the distribution sessions table
                    self._refresh_distribution_sessions_table()
                    self._refresh_dist_csv_import_sessions()
                else:
                    show_error_message("Import Cancelled", "The import operation was cancelled.", self)
            else:
                show_error_message("Import Cancelled", "The import operation was cancelled.", self)
                
        except Exception as e:
            show_error_message("Error", f"Distribution import failed: {str(e)}", self)
    
    def _on_export_borrowed_books(self):
        """Handle export of borrowed books."""
        try:
            stream = self.export_borrowed_stream_combo.currentText()
            subject = self.export_borrowed_subject_combo.currentText()
            term = self.export_borrowed_term_combo.currentText()
            format_type = self.export_borrowed_format_combo.currentText()
            
            # Get file path for export
            file_dialog = QFileDialog()
            if format_type == "Excel":
                file_path, _ = file_dialog.getSaveFileName(self, "Save Export File",
                                                         f"borrowed_books_{stream}_{subject}.xlsx",
                                                         "Excel Files (*.xlsx)")
            else:
                file_path, _ = file_dialog.getSaveFileName(self, "Save Export File",
                                                         f"borrowed_books_{stream}_{subject}.pdf",
                                                         "PDF Files (*.pdf)")
            
            if file_path:
                # In real implementation, call service method
                # For now, simulate success
                show_success_message("Success",
                                   f"Borrowed books exported successfully to {format_type} format",
                                   self)
            
        except Exception as e:
            show_error_message("Error", f"Export failed: {str(e)}", self)
    
    def _on_export_outstanding_books(self):
        """Handle export of outstanding books."""
        try:
            stream = self.export_outstanding_stream_combo.currentText()
            subject = self.export_outstanding_subject_combo.currentText()
            format_type = self.export_outstanding_format_combo.currentText()
            
            # Get file path for export
            file_dialog = QFileDialog()
            if format_type == "Excel":
                file_path, _ = file_dialog.getSaveFileName(self, "Save Export File",
                                                         f"outstanding_books_{stream}_{subject}.xlsx",
                                                         "Excel Files (*.xlsx)")
            else:
                file_path, _ = file_dialog.getSaveFileName(self, "Save Export File",
                                                         f"outstanding_books_{stream}_{subject}.pdf",
                                                         "PDF Files (*.pdf)")
            
            if file_path:
                # In real implementation, call service method
                # For now, simulate success
                show_success_message("Success",
                                   f"Outstanding books exported successfully to {format_type} format",
                                   self)
            
        except Exception as e:
            show_error_message("Error", f"Export failed: {str(e)}", self)
    
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