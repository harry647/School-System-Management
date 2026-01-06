"""
Book management window for the School System Management application.

This module provides the book management interface for admin users (admin and librarian roles).
"""

from PyQt6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QLabel, QLineEdit, QPushButton, 
                            QHBoxLayout, QComboBox, QTabWidget, QTableWidget, QTableWidgetItem, 
                            QTextEdit, QSizePolicy, QFileDialog, QMessageBox)
from PyQt6.QtCore import Qt
from typing import Callable, Optional

from school_system.gui.base.base_window import BaseWindow
from school_system.gui.dialogs.message_dialog import show_error_message, show_success_message
from school_system.config.logging import logger
from school_system.services.book_service import BookService
from school_system.core.exceptions import DatabaseException, ValidationError


class BookWindow(BaseWindow):
    """Book management window for admin users."""

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

        # Initialize UI
        self._setup_widgets()

    def _setup_widgets(self):
        """Setup the book management widgets."""
        # Create tab widget for different sections
        tab_widget = QTabWidget()
        self.add_widget_to_content(tab_widget)

        # Book Management Tab
        book_tab = self._create_book_management_tab()
        tab_widget.addTab(book_tab, "Book Management")

        # Book Borrowing Tab
        borrowing_tab = self._create_borrowing_tab()
        tab_widget.addTab(borrowing_tab, "Book Borrowing")

        # Distribution Sessions Tab
        distribution_tab = self._create_distribution_tab()
        tab_widget.addTab(distribution_tab, "Distribution Sessions")

        # Import/Export Tab
        import_export_tab = self._create_import_export_tab()
        tab_widget.addTab(import_export_tab, "Import/Export")

        # Reports Tab
        reports_tab = self._create_reports_tab()
        tab_widget.addTab(reports_tab, "Reports")

    def _create_book_management_tab(self) -> QWidget:
        """Create the book management tab."""
        tab = QWidget()
        layout = self.create_flex_layout("column", False)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.set_spacing(15)

        # Create Book Section
        create_section = self.create_card("Create New Book", "")
        create_form = QWidget()
        create_layout = self.create_flex_layout("column", False)
        create_layout.set_spacing(10)

        # Book Number
        book_number_label = QLabel("Book Number:")
        create_layout.add_widget(book_number_label)
        self.create_book_number_input = self.create_input("Enter book number")
        create_layout.add_widget(self.create_book_number_input)

        # Title
        title_label = QLabel("Title:")
        create_layout.add_widget(title_label)
        self.create_title_input = self.create_input("Enter book title")
        create_layout.add_widget(self.create_title_input)

        # Author
        author_label = QLabel("Author:")
        create_layout.add_widget(author_label)
        self.create_author_input = self.create_input("Enter author name")
        create_layout.add_widget(self.create_author_input)

        # Category
        category_label = QLabel("Category:")
        create_layout.add_widget(category_label)
        self.create_category_input = self.create_input("Enter category")
        create_layout.add_widget(self.create_category_input)

        # ISBN
        isbn_label = QLabel("ISBN:")
        create_layout.add_widget(isbn_label)
        self.create_isbn_input = self.create_input("Enter ISBN")
        create_layout.add_widget(self.create_isbn_input)

        # Publication Date
        pub_date_label = QLabel("Publication Date:")
        create_layout.add_widget(pub_date_label)
        self.create_pub_date_input = self.create_input("YYYY-MM-DD")
        create_layout.add_widget(self.create_pub_date_input)

        # Create button
        create_button = self.create_button("Create Book", "primary")
        create_button.clicked.connect(self._on_create_book)
        create_layout.add_widget(create_button)

        create_form.setLayout(create_layout._layout)
        create_section.layout.addWidget(create_form)
        layout.add_widget(create_section)

        # Update Book Section
        update_section = self.create_card("Update Book", "")
        update_form = QWidget()
        update_layout = self.create_flex_layout("column", False)
        update_layout.set_spacing(10)

        # Book ID
        book_id_label = QLabel("Book ID:")
        update_layout.add_widget(book_id_label)
        self.update_book_id_input = self.create_input("Enter book ID")
        update_layout.add_widget(self.update_book_id_input)

        # Title
        update_title_label = QLabel("New Title:")
        update_layout.add_widget(update_title_label)
        self.update_title_input = self.create_input("Enter new title")
        update_layout.add_widget(self.update_title_input)

        # Author
        update_author_label = QLabel("New Author:")
        update_layout.add_widget(update_author_label)
        self.update_author_input = self.create_input("Enter new author")
        update_layout.add_widget(self.update_author_input)

        # Update button
        update_button = self.create_button("Update Book", "secondary")
        update_button.clicked.connect(self._on_update_book)
        update_layout.add_widget(update_button)

        update_form.setLayout(update_layout._layout)
        update_section.layout.addWidget(update_form)
        layout.add_widget(update_section)

        # View Books Section
        view_section = self.create_card("View Books", "")
        view_form = QWidget()
        view_layout = self.create_flex_layout("column", False)
        view_layout.set_spacing(10)

        # Search box
        self.search_box = self.create_search_box("Search books...")
        self.search_box.search_text_changed.connect(self._on_search_books)
        view_layout.add_widget(self.search_box)

        # Refresh button
        refresh_button = self.create_button("Refresh Books", "secondary")
        refresh_button.clicked.connect(self._refresh_books_table)
        view_layout.add_widget(refresh_button)

        # Books table
        self.books_table = self.create_table(0, 7)
        self.books_table.setHorizontalHeaderLabels(["ID", "Book Number", "Title", "Author", "Category", "Available", "Condition"])
        view_layout.add_widget(self.books_table)

        view_form.setLayout(view_layout._layout)
        view_section.layout.addWidget(view_form)
        layout.add_widget(view_section)

        tab.setLayout(layout._layout)
        return tab

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
        self.borrowed_books_table.setHorizontalHeaderLabels(["User ID", "User Type", "Book ID", "Borrowed On", "Returned On", "Condition"])
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
        self.distribution_sessions_table.setHorizontalHeaderLabels(["ID", "Class", "Stream", "Subject", "Term", "Status"])
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
            
            self.books_table.setRowCount(0)
            
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