"""
Library Activity Window

Dedicated window for managing student library activities (borrowing/returning books).
"""

from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QTableWidget, QTableWidgetItem, QLineEdit, QComboBox, QSplitter, QTabWidget
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont
from datetime import datetime, timedelta
from typing import List, Optional

from school_system.gui.windows.base_function_window import BaseFunctionWindow
from school_system.gui.dialogs.message_dialog import show_error_message, show_success_message, show_info_message
from school_system.config.logging import logger
from school_system.services.student_service import StudentService
from school_system.services.book_service import BookService
from school_system.database.repositories.book_repo import BorrowedBookStudentRepository


class LibraryActivityWindow(BaseFunctionWindow):
    """Dedicated window for managing student library activities."""

    def __init__(self, parent=None, current_user: str = "", current_role: str = ""):
        """Initialize the library activity window."""
        super().__init__("Library Activity Management", parent, current_user, current_role)

        self.student_service = StudentService()
        self.book_service = BookService()
        self.borrow_repo = BorrowedBookStudentRepository()

        # Setup content
        self.setup_content()

        # Load initial data
        self._refresh_borrow_records()

    def setup_content(self):
        """Setup the main content area."""
        # Create main content layout
        main_layout = self.create_flex_layout("column", False)
        main_layout.set_margins(24, 24, 24, 24)
        main_layout.set_spacing(20)

        # Create tab widget for different activities
        tab_widget = QTabWidget()
        tab_widget.setStyleSheet("""
            QTabWidget::pane {
                border: 1px solid #ddd;
                border-radius: 8px;
                background-color: white;
            }
            QTabBar::tab {
                padding: 12px 24px;
                margin-right: 2px;
                border-radius: 8px 8px 0 0;
            }
            QTabBar::tab:selected {
                background-color: #007bff;
                color: white;
            }
        """)

        # Borrow tab
        borrow_tab = self._create_borrow_tab()
        tab_widget.addTab(borrow_tab, "📖 Borrow Book")

        # Return tab
        return_tab = self._create_return_tab()
        tab_widget.addTab(return_tab, "↩️ Return Book")

        # History tab
        history_tab = self._create_history_tab()
        tab_widget.addTab(history_tab, "📚 Activity History")

        main_layout.add_widget(tab_widget, stretch=1)

        # Add to content
        self.add_layout_to_content(main_layout)

    def _create_borrow_tab(self) -> QWidget:
        """Create the borrow book tab."""
        theme_manager = self.get_theme_manager()
        theme = theme_manager._themes[self.get_theme()]

        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(20)

        # Header
        header = QLabel("📖 Borrow Book")
        header_font = QFont("Segoe UI", 18, QFont.Weight.Medium)
        header.setFont(header_font)
        header.setStyleSheet(f"color: {theme["text"]};")
        layout.addWidget(header)

        # Borrow form
        form_card = QWidget()
        form_card.setProperty("card", "true")
        form_card.setStyleSheet(f"""
            QWidget[card="true"] {{
                background-color: {theme["surface"]};
                border: 1px solid {theme["border"]};
                border-radius: 12px;
                padding: 24px;
            }}
        """)

        form_layout = QVBoxLayout(form_card)
        form_layout.setSpacing(16)

        # Student ID input
        student_layout = QVBoxLayout()
        student_label = QLabel("Student ID:")
        student_label.setStyleSheet(f"font-weight: 500; color: {theme["text"]};")
        student_layout.addWidget(student_label)

        self.borrow_student_id_input = self.create_input("Enter student ID")
        self.borrow_student_id_input.setFixedHeight(44)
        student_layout.addWidget(self.borrow_student_id_input)
        form_layout.addLayout(student_layout)

        # Book selection
        book_layout = QVBoxLayout()
        book_label = QLabel("Select Book:")
        book_label.setStyleSheet(f"font-weight: 500; color: {theme["text"]};")
        book_layout.addWidget(book_label)

        self.borrow_book_combo = QComboBox()
        self.borrow_book_combo.setFixedHeight(44)
        self._populate_available_books()
        book_layout.addWidget(self.borrow_book_combo)
        form_layout.addLayout(book_layout)

        # Borrow duration
        duration_layout = QVBoxLayout()
        duration_label = QLabel("Borrow Duration (days):")
        duration_label.setStyleSheet(f"font-weight: 500; color: {theme["text"]};")
        duration_layout.addWidget(duration_label)

        self.borrow_duration_combo = QComboBox()
        self.borrow_duration_combo.addItems(["7", "14", "21", "30"])
        self.borrow_duration_combo.setCurrentText("14")  # Default 2 weeks
        self.borrow_duration_combo.setFixedHeight(44)
        duration_layout.addWidget(self.borrow_duration_combo)
        form_layout.addLayout(duration_layout)

        # Borrow button
        borrow_btn = self.create_button("📖 Borrow Book", "primary")
        borrow_btn.clicked.connect(self._borrow_book)
        form_layout.addWidget(borrow_btn)

        layout.addWidget(form_card)

        # Current borrows section
        current_borrows_card = QWidget()
        current_borrows_card.setProperty("card", "true")
        current_borrows_card.setStyleSheet(f"""
            QWidget[card="true"] {{
                background-color: {theme["surface"]};
                border: 1px solid {theme["border"]};
                border-radius: 12px;
                padding: 24px;
            }}
        """)

        borrows_layout = QVBoxLayout(current_borrows_card)

        borrows_header = QHBoxLayout()
        borrows_title = QLabel("Current Borrows")
        borrows_title.setStyleSheet(f"font-weight: 600; color: {theme["text"]};")
        borrows_header.addWidget(borrows_title)

        borrows_header.addStretch()

        refresh_borrows_btn = self.create_button("🔄 Refresh", "outline")
        refresh_borrows_btn.clicked.connect(self._refresh_borrow_records)
        borrows_header.addWidget(refresh_borrows_btn)

        borrows_layout.addLayout(borrows_header)

        # Current borrows table
        self.current_borrows_table = self.create_table(0, 5)
        self.current_borrows_table.setColumnCount(5)
        self.current_borrows_table.setHorizontalHeaderLabels(["Student ID", "Book Title", "Borrow Date", "Due Date", "Status"])
        self.current_borrows_table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.current_borrows_table.setAlternatingRowColors(True)
        borrows_layout.addWidget(self.current_borrows_table)

        layout.addWidget(current_borrows_card, stretch=1)

        return widget

    def _create_return_tab(self) -> QWidget:
        """Create the return book tab."""
        theme_manager = self.get_theme_manager()
        theme = theme_manager._themes[self.get_theme()]

        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(20)

        # Header
        header = QLabel("↩️ Return Book")
        header_font = QFont("Segoe UI", 18, QFont.Weight.Medium)
        header.setFont(header_font)
        header.setStyleSheet(f"color: {theme["text"]};")
        layout.addWidget(header)

        # Return form
        form_card = QWidget()
        form_card.setProperty("card", "true")
        form_card.setStyleSheet(f"""
            QWidget[card="true"] {{
                background-color: {theme["surface"]};
                border: 1px solid {theme["border"]};
                border-radius: 12px;
                padding: 24px;
            }}
        """)

        form_layout = QVBoxLayout(form_card)
        form_layout.setSpacing(16)

        # Outstanding borrows selection
        borrow_layout = QVBoxLayout()
        borrow_label = QLabel("Select Borrow Record:")
        borrow_label.setStyleSheet(f"font-weight: 500; color: {theme["text"]};")
        borrow_layout.addWidget(borrow_label)

        self.return_borrow_combo = QComboBox()
        self.return_borrow_combo.setFixedHeight(44)
        self._populate_outstanding_borrows()
        borrow_layout.addWidget(self.return_borrow_combo)
        form_layout.addLayout(borrow_layout)

        # Return button
        return_btn = self.create_button("↩️ Return Book", "success")
        return_btn.clicked.connect(self._return_book)
        form_layout.addWidget(return_btn)

        layout.addWidget(form_card)

        # Overdue books section
        overdue_card = QWidget()
        overdue_card.setProperty("card", "true")
        overdue_card.setStyleSheet(f"""
            QWidget[card="true"] {{
                background-color: {theme["surface"]};
                border: 1px solid {theme["border"]};
                border-radius: 12px;
                padding: 24px;
            }}
        """)

        overdue_layout = QVBoxLayout(overdue_card)

        overdue_header = QHBoxLayout()
        overdue_title = QLabel("⚠️ Overdue Books")
        overdue_title.setStyleSheet(f"font-weight: 600; color: {theme["text"]}; color: #dc3545;")
        overdue_header.addWidget(overdue_title)

        overdue_header.addStretch()

        overdue_layout.addLayout(overdue_header)

        # Overdue books table
        self.overdue_table = self.create_table(0, 6)
        self.overdue_table.setColumnCount(6)
        self.overdue_table.setHorizontalHeaderLabels(["Student ID", "Book Title", "Borrow Date", "Due Date", "Days Overdue", "Fine"])
        self.overdue_table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.overdue_table.setAlternatingRowColors(True)
        overdue_layout.addWidget(self.overdue_table)

        layout.addWidget(overdue_card, stretch=1)

        return widget

    def _create_history_tab(self) -> QWidget:
        """Create the activity history tab."""
        theme_manager = self.get_theme_manager()
        theme = theme_manager._themes[self.get_theme()]

        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(20)

        # Header
        header = QLabel("📚 Library Activity History")
        header_font = QFont("Segoe UI", 18, QFont.Weight.Medium)
        header.setFont(header_font)
        header.setStyleSheet(f"color: {theme["text"]};")
        layout.addWidget(header)

        # Filters
        filter_card = QWidget()
        filter_card.setProperty("card", "true")
        filter_card.setStyleSheet(f"""
            QWidget[card="true"] {{
                background-color: {theme["surface"]};
                border: 1px solid {theme["border"]};
                border-radius: 12px;
                padding: 16px;
            }}
        """)

        filter_layout = QHBoxLayout(filter_card)
        filter_layout.setSpacing(12)

        # Student filter
        student_filter_label = QLabel("Student ID:")
        student_filter_label.setStyleSheet(f"font-weight: 500; color: {theme["text"]};")
        filter_layout.addWidget(student_filter_label)

        self.history_student_filter = self.create_input("Filter by student ID")
        self.history_student_filter.setFixedWidth(200)
        self.history_student_filter.textChanged.connect(self._filter_history)
        filter_layout.addWidget(self.history_student_filter)

        # Activity type filter
        type_label = QLabel("Activity:")
        type_label.setStyleSheet(f"font-weight: 500; color: {theme["text"]};")
        filter_layout.addWidget(type_label)

        self.history_type_filter = QComboBox()
        self.history_type_filter.addItems(["All", "Borrow", "Return"])
        self.history_type_filter.currentTextChanged.connect(self._filter_history)
        filter_layout.addWidget(self.history_type_filter)

        filter_layout.addStretch()

        # Refresh button
        refresh_history_btn = self.create_button("🔄 Refresh", "outline")
        refresh_history_btn.clicked.connect(self._refresh_history)
        filter_layout.addWidget(refresh_history_btn)

        layout.addWidget(filter_card)

        # History table
        table_card = QWidget()
        table_card.setProperty("card", "true")
        table_card.setStyleSheet(f"""
            QWidget[card="true"] {{
                background-color: {theme["surface"]};
                border: 1px solid {theme["border"]};
                border-radius: 12px;
                padding: 24px;
            }}
        """)

        table_layout = QVBoxLayout(table_card)

        # History table
        self.history_table = self.create_table(0, 6)
        self.history_table.setColumnCount(6)
        self.history_table.setHorizontalHeaderLabels(["Student ID", "Book Title", "Activity", "Date", "Due Date", "Return Date"])
        self.history_table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.history_table.setAlternatingRowColors(True)
        table_layout.addWidget(self.history_table)

        layout.addWidget(table_card, stretch=1)

        return widget

    def _populate_available_books(self):
        """Populate the available books combo box."""
        try:
            self.borrow_book_combo.clear()
            books = self.book_service.get_all_books()

            for book in books:
                # Check if book is available
                if book.available:
                    display_text = f"{book.title} (ID: {book.book_number})"
                    self.borrow_book_combo.addItem(display_text, book.id)

            if self.borrow_book_combo.count() == 0:
                self.borrow_book_combo.addItem("No books available", None)

        except Exception as e:
            logger.error(f"Error populating available books: {e}")
            self.borrow_book_combo.addItem("Error loading books", None)

    def _populate_outstanding_borrows(self):
        """Populate the outstanding borrows combo box."""
        try:
            self.return_borrow_combo.clear()
            # Get all borrowed books that haven't been returned
            records = self.borrow_repo.get_all()

            for record in records:
                if record.returned_on is None:  # Not returned yet
                    try:
                        student = self.student_service.get_student_by_id(record.student_id)
                        book = self.book_service.get_book_by_id(record.book_id)

                        student_name = student.name if student else "Unknown"
                        book_title = book.title if book else "Unknown"

                        display_text = f"{record.student_id} ({student_name}) - {book_title}"
                        self.return_borrow_combo.addItem(display_text, (record.student_id, record.book_id))
                    except Exception as e:
                        logger.error(f"Error processing borrow record: {e}")

            if self.return_borrow_combo.count() == 0:
                self.return_borrow_combo.addItem("No outstanding borrows", None)

        except Exception as e:
            logger.error(f"Error populating outstanding borrows: {e}")
            self.return_borrow_combo.addItem("Error loading records", None)

    def _refresh_borrow_records(self):
        """Refresh all borrow-related tables."""
        self._populate_available_books()
        self._populate_outstanding_borrows()
        self._refresh_current_borrows()
        self._refresh_overdue_books()
        self._refresh_history()

    def _refresh_current_borrows(self):
        """Refresh the current borrows table."""
        try:
            records = self.borrow_repo.get_all()
            self.current_borrows_table.setRowCount(0)

            for record in records:
                if record.returned_on is None:  # Not returned yet
                    row = self.current_borrows_table.rowCount()
                    self.current_borrows_table.insertRow(row)

                    try:
                        student = self.student_service.get_student_by_id(record.student_id)
                        book = self.book_service.get_book_by_id(record.book_id)

                        student_display = f"{record.student_id}"
                        book_title = book.title if book else "Unknown"

                        # Calculate due date (borrowed_on + reminder_days, defaulting to 14 days)
                        borrowed_date = datetime.strptime(record.borrowed_on, '%Y-%m-%d').date()
                        reminder_days = record.reminder_days or 14
                        due_date = borrowed_date + timedelta(days=reminder_days)

                        self.current_borrows_table.setItem(row, 0, QTableWidgetItem(student_display))
                        self.current_borrows_table.setItem(row, 1, QTableWidgetItem(book_title))
                        self.current_borrows_table.setItem(row, 2, QTableWidgetItem(str(record.borrowed_on)))
                        self.current_borrows_table.setItem(row, 3, QTableWidgetItem(str(due_date)))

                        # Status
                        today = datetime.now().date()
                        if due_date < today:
                            status = "Overdue"
                            status_item = QTableWidgetItem(status)
                            status_item.setBackground(Qt.GlobalColor.red)
                            status_item.setForeground(Qt.GlobalColor.white)
                        else:
                            status = "Active"
                            status_item = QTableWidgetItem(status)
                            status_item.setBackground(Qt.GlobalColor.green)
                            status_item.setForeground(Qt.GlobalColor.white)

                        self.current_borrows_table.setItem(row, 4, status_item)

                    except Exception as e:
                        logger.error(f"Error processing borrow record {record.student_id}: {e}")

        except Exception as e:
            logger.error(f"Error refreshing current borrows: {e}")

    def _refresh_overdue_books(self):
        """Refresh the overdue books table."""
        try:
            records = self.borrow_repo.get_overdue_books()
            self.overdue_table.setRowCount(0)

            for record in records:
                row = self.overdue_table.rowCount()
                self.overdue_table.insertRow(row)

                try:
                    student = self.student_service.get_student_by_id(record.student_id)
                    book = self.book_service.get_book_by_id(record.book_id)

                    student_display = f"{record.student_id}"
                    book_title = book.title if book else "Unknown"

                    borrowed_date = datetime.strptime(record.borrowed_on, '%Y-%m-%d').date()
                    reminder_days = record.reminder_days or 14
                    due_date = borrowed_date + timedelta(days=reminder_days)
                    today = datetime.now().date()
                    days_overdue = (today - due_date).days
                    fine_amount = max(0, days_overdue * 1.0)  # $1 per day fine

                    self.overdue_table.setItem(row, 0, QTableWidgetItem(student_display))
                    self.overdue_table.setItem(row, 1, QTableWidgetItem(book_title))
                    self.overdue_table.setItem(row, 2, QTableWidgetItem(str(record.borrowed_on)))
                    self.overdue_table.setItem(row, 3, QTableWidgetItem(str(due_date)))
                    self.overdue_table.setItem(row, 4, QTableWidgetItem(str(max(0, days_overdue))))
                    self.overdue_table.setItem(row, 5, QTableWidgetItem(".2f"))

                except Exception as e:
                    logger.error(f"Error processing overdue record: {e}")

        except Exception as e:
            logger.error(f"Error refreshing overdue books: {e}")

    def _refresh_history(self):
        """Refresh the activity history table."""
        try:
            records = self.borrow_repo.get_all()
            self.history_table.setRowCount(0)

            for record in records:
                row = self.history_table.rowCount()
                self.history_table.insertRow(row)

                try:
                    student = self.student_service.get_student_by_id(record.student_id)
                    book = self.book_service.get_book_by_id(record.book_id)

                    student_display = f"{record.student_id}"
                    book_title = book.title if book else "Unknown"

                    activity = "Return" if record.returned_on else "Borrow"

                    # Calculate due date
                    borrowed_date = datetime.strptime(record.borrowed_on, '%Y-%m-%d').date()
                    reminder_days = record.reminder_days or 14
                    due_date = borrowed_date + timedelta(days=reminder_days)

                    self.history_table.setItem(row, 0, QTableWidgetItem(student_display))
                    self.history_table.setItem(row, 1, QTableWidgetItem(book_title))
                    self.history_table.setItem(row, 2, QTableWidgetItem(activity))
                    self.history_table.setItem(row, 3, QTableWidgetItem(str(record.borrowed_on)))
                    self.history_table.setItem(row, 4, QTableWidgetItem(str(due_date)))
                    self.history_table.setItem(row, 5, QTableWidgetItem(str(record.returned_on) if record.returned_on else "Not returned"))

                except Exception as e:
                    logger.error(f"Error processing history record: {e}")

        except Exception as e:
            logger.error(f"Error refreshing history: {e}")

    def _filter_history(self):
        """Filter the history table based on current filters."""
        student_filter = self.history_student_filter.text().strip().lower()
        type_filter = self.history_type_filter.currentText()

        for row in range(self.history_table.rowCount()):
            student_item = self.history_table.item(row, 0)
            type_item = self.history_table.item(row, 2)

            show_row = True

            if student_filter and student_item:
                if student_filter not in student_item.text().lower():
                    show_row = False

            if type_filter != "All" and type_item:
                if type_filter != type_item.text():
                    show_row = False

            self.history_table.setRowHidden(row, not show_row)

    def _borrow_book(self):
        """Handle book borrowing."""
        student_id = self.borrow_student_id_input.text().strip()
        book_id = self.borrow_book_combo.currentData()
        duration_text = self.borrow_duration_combo.currentText()

        if not student_id:
            show_error_message("Validation Error", "Please enter a student ID.", self)
            return

        if not book_id:
            show_error_message("Validation Error", "Please select a book.", self)
            return

        try:
            duration_days = int(duration_text)
            borrow_date = datetime.now().date()
            due_date = borrow_date + timedelta(days=duration_days)

            # Check if student exists
            student = self.student_service.get_student_by_id(student_id)
            if not student:
                show_error_message("Student Not Found", f"Student {student_id} not found.", self)
                return

            # Check if student already has this book
            if self.borrow_repo.has_student_borrowed_book(student_id, book_id):
                show_error_message("Already Borrowed", f"Student {student_id} already has this book.", self)
                return

            # Create borrow record
            from school_system.models.book import BorrowedBookStudent
            borrow_record = BorrowedBookStudent(
                student_id=student_id,
                book_id=book_id,
                borrowed_on=borrow_date,
                reminder_days=duration_days
            )
            borrow_record.save()

            # Mark book as unavailable
            book.available = False
            book.save()

            show_success_message("Success", f"Book borrowed successfully for student {student_id}. Due date: {due_date}", self)

            # Clear form
            self.borrow_student_id_input.clear()
            self.borrow_duration_combo.setCurrentText("14")

            # Refresh displays
            self._refresh_borrow_records()

        except ValueError:
            show_error_message("Validation Error", "Invalid duration.", self)
        except Exception as e:
            logger.error(f"Error borrowing book: {e}")
            show_error_message("Error", f"Failed to borrow book: {str(e)}", self)

    def _return_book(self):
        """Handle book returning."""
        record_data = self.return_borrow_combo.currentData()

        if not record_data:
            show_error_message("Validation Error", "Please select a borrow record.", self)
            return

        student_id, book_id = record_data

        try:
            # Return the book using the repository method
            success = self.borrow_repo.return_book(student_id, book_id, returned_by=self.current_user)

            if success:
                show_success_message("Success", "Book returned successfully.", self)

                # Clear selection
                self.return_borrow_combo.setCurrentIndex(0)

                # Refresh displays
                self._refresh_borrow_records()
            else:
                show_error_message("Error", "Book was not found or already returned.", self)

        except Exception as e:
            logger.error(f"Error returning book: {e}")
            show_error_message("Error", f"Failed to return book: {str(e)}", self)
