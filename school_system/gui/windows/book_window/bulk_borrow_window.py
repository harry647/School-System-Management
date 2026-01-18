"""
Bulk Book Borrow Window

Window for borrowing books for multiple students based on class/stream criteria.
"""

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QLineEdit,
    QComboBox, QTextEdit, QGroupBox, QMessageBox, QDialog, QTableWidget, QTableWidgetItem
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont
from typing import Optional, List

from school_system.gui.windows.base_function_window import BaseFunctionWindow
from school_system.gui.dialogs.message_dialog import show_error_message, show_success_message
from school_system.config.logging import logger
from school_system.services.book_service import BookService
from school_system.services.class_management_service import ClassManagementService


class BulkBorrowWindow(QDialog):
    """Dialog for bulk book borrowing operations."""

    def __init__(
        self,
        parent=None,
        current_user: str = "",
        current_role: str = "",
        class_level: Optional[int] = None,
        stream: Optional[str] = None,
        student_ids: Optional[List[str]] = None
    ):
        """Initialize the bulk borrow window."""
        super().__init__(parent)
        
        self.setWindowTitle("Bulk Book Borrow")
        self.setMinimumWidth(600)
        self.setMinimumHeight(500)
        
        self.book_service = BookService()
        self.class_management_service = ClassManagementService()
        
        self.class_level = class_level
        self.stream = stream
        self.student_ids = student_ids

        # Determine if we're in "all students" mode
        self.all_students_mode = not self.student_ids or len(self.student_ids) == 0

        self.setup_ui()
        
    def setup_ui(self):
        """Setup the UI components."""
        from school_system.gui.base.widgets.theme import ThemeManager
        theme_manager = ThemeManager()
        theme = theme_manager._themes[theme_manager.get_theme()]
        
        layout = QVBoxLayout(self)
        layout.setSpacing(20)
        layout.setContentsMargins(24, 24, 24, 24)
        
        # Title
        title_label = QLabel("📚 Bulk Book Borrow")
        title_font = QFont("Segoe UI", 18, QFont.Weight.Medium)
        title_label.setFont(title_font)
        title_label.setStyleSheet(f"color: {theme['text']}; margin-bottom: 8px;")
        layout.addWidget(title_label)
        
        # Criteria display
        criteria_group = QGroupBox("Borrow Criteria")
        criteria_group.setStyleSheet(f"""
            QGroupBox {{
                font-weight: 600;
                border: 2px solid {theme['border']};
                border-radius: 8px;
                margin-top: 12px;
                padding-top: 12px;
            }}
            QGroupBox::title {{
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px;
            }}
        """)
        criteria_layout = QVBoxLayout(criteria_group)
        
        criteria_text = []
        if self.class_level is not None:
            display_name = self.class_management_service.format_class_display_name(self.class_level, self.stream)
            criteria_text.append(f"Class-Stream: {display_name}")
        elif self.stream is not None:
            criteria_text.append(f"Stream: {self.stream}")
        
        if self.student_ids:
            criteria_text.append(f"Selected Students: {len(self.student_ids)}")
        
        if not criteria_text:
            criteria_text.append("All Students")
        
        criteria_label = QLabel("\n".join(criteria_text))
        criteria_label.setStyleSheet(f"color: {theme['text_secondary']}; padding: 8px;")
        criteria_layout.addWidget(criteria_label)
        
        layout.addWidget(criteria_group)

        if self.all_students_mode:
            # All students mode - show table with individual book assignments
            self._setup_all_students_ui(layout, theme)
        else:
            # Selected students mode - show simple form
            self._setup_selected_students_ui(layout, theme)
        
        # Action buttons
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        
        cancel_btn = QPushButton("Cancel")
        cancel_btn.setFixedHeight(44)
        cancel_btn.setFixedWidth(120)
        cancel_btn.clicked.connect(self.reject)
        cancel_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {theme['surface']};
                color: {theme['text']};
                border: 1px solid {theme['border']};
                border-radius: 6px;
                padding: 8px;
            }}
            QPushButton:hover {{
                background-color: {theme['border']};
            }}
        """)
        button_layout.addWidget(cancel_btn)
        
        borrow_btn = QPushButton("Borrow for All")
        borrow_btn.setFixedHeight(44)
        borrow_btn.setFixedWidth(150)
        borrow_btn.clicked.connect(self._execute_bulk_borrow)
        borrow_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {theme['primary']};
                color: white;
                border: none;
                border-radius: 6px;
                padding: 8px;
                font-weight: 600;
            }}
            QPushButton:hover {{
                background-color: {theme.get('primary_hover', theme['primary'])};
            }}
        """)
        button_layout.addWidget(borrow_btn)
        
        layout.addLayout(button_layout)
        
        # Results area (initially hidden)
        self.results_group = QGroupBox("Operation Results")
        self.results_group.setStyleSheet(f"""
            QGroupBox {{
                font-weight: 600;
                border: 2px solid {theme['border']};
                border-radius: 8px;
                margin-top: 12px;
                padding-top: 12px;
            }}
            QGroupBox::title {{
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px;
            }}
        """)
        self.results_group.setVisible(False)
        
        results_layout = QVBoxLayout(self.results_group)
        
        self.results_text = QTextEdit()
        self.results_text.setReadOnly(True)
        self.results_text.setMaximumHeight(200)
        self.results_text.setStyleSheet(f"""
            QTextEdit {{
                background-color: {theme['background']};
                border: 1px solid {theme['border']};
                border-radius: 6px;
                padding: 8px;
                color: {theme['text']};
            }}
        """)
        results_layout.addWidget(self.results_text)
        
        layout.addWidget(self.results_group)

    def _setup_all_students_ui(self, layout, theme):
        """Setup UI for all students mode with table."""
        from PyQt6.QtWidgets import QTableWidget, QTableWidgetItem, QHeaderView

        # Book type and subject selection at top
        selection_layout = QHBoxLayout()
        selection_layout.setSpacing(12)

        # Book type
        type_layout = QVBoxLayout()
        type_label = QLabel("Book Type:")
        type_label.setStyleSheet(f"font-weight: 500; color: {theme['text']}; margin-bottom: 4px;")
        type_layout.addWidget(type_label)

        self.book_type_combo = QComboBox()
        self.book_type_combo.addItems(["course", "revision"])
        self.book_type_combo.setFixedHeight(40)
        type_layout.addWidget(self.book_type_combo)
        selection_layout.addLayout(type_layout)

        # Subject
        subject_layout = QVBoxLayout()
        subject_label = QLabel("Subject:")
        subject_label.setStyleSheet(f"font-weight: 500; color: {theme['text']}; margin-bottom: 4px;")
        subject_layout.addWidget(subject_label)

        self.subject_combo = QComboBox()
        try:
            from school_system.gui.windows.book_window.utils.constants import STANDARD_SUBJECTS
            self.subject_combo.addItems(STANDARD_SUBJECTS)
        except:
            self.subject_combo.addItems(["Mathematics", "Science", "English", "History", "Geography"])
        self.subject_combo.setFixedHeight(40)
        subject_layout.addWidget(self.subject_combo)
        selection_layout.addLayout(subject_layout)

        selection_layout.addStretch()
        layout.addLayout(selection_layout)

        # Students table
        table_group = QGroupBox("Assign Books to Students")
        table_group.setStyleSheet(f"""
            QGroupBox {{
                font-weight: 600;
                border: 2px solid {theme['border']};
                border-radius: 8px;
                margin-top: 12px;
                padding-top: 12px;
            }}
        """)

        table_layout = QVBoxLayout(table_group)

        # Create table
        self.students_table = QTableWidget()
        self.students_table.setColumnCount(4)
        self.students_table.setHorizontalHeaderLabels([
            "Student Name", "Admission Number", "Book Number", "Status"
        ])

        # Set header properties
        header = self.students_table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(3, QHeaderView.ResizeMode.ResizeToContents)

        table_layout.addWidget(self.students_table)

        layout.addWidget(table_group)

        # Load students into table
        self._load_students_into_table()

        # Borrow All button
        borrow_all_btn = QPushButton("📚 Borrow All Books")
        borrow_all_btn.setFixedHeight(44)
        borrow_all_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {theme['primary']};
                color: white;
                border: none;
                border-radius: 8px;
                padding: 12px 24px;
                font-weight: 500;
                font-size: 14px;
            }}
            QPushButton:hover {{
                background-color: {theme.get('primary_dark', theme['primary'])};
            }}
        """)
        borrow_all_btn.clicked.connect(self._on_borrow_all_books)
        layout.addWidget(borrow_all_btn)

    def _setup_selected_students_ui(self, layout, theme):
        """Setup UI for selected students mode (original interface)."""
        # Book ID input
        book_layout = QVBoxLayout()
        book_label = QLabel("Book ID *")
        book_label.setStyleSheet(f"font-weight: 500; color: {theme['text']}; margin-bottom: 4px;")
        book_layout.addWidget(book_label)

        self.book_id_input = QLineEdit()
        self.book_id_input.setPlaceholderText("Enter book ID")
        self.book_id_input.setFixedHeight(44)
        self.book_id_input.setStyleSheet(f"""
            QLineEdit {{
                padding: 8px;
                border: 1px solid {theme['border']};
                border-radius: 6px;
                background-color: {theme['background']};
                color: {theme['text']};
            }}
        """)
        book_layout.addWidget(self.book_id_input)
        layout.addLayout(book_layout)

        # Subject (optional, for context)
        subject_layout = QVBoxLayout()
        subject_label = QLabel("Subject (Optional)")
        subject_label.setStyleSheet(f"font-weight: 500; color: {theme['text']}; margin-bottom: 4px;")
        subject_layout.addWidget(subject_label)

        self.subject_input = QLineEdit()
        self.subject_input.setPlaceholderText("e.g., Mathematics, English")
        self.subject_input.setFixedHeight(44)
        self.subject_input.setStyleSheet(f"""
            QLineEdit {{
                padding: 8px;
                border: 1px solid {theme['border']};
                border-radius: 6px;
                background-color: {theme['background']};
                color: {theme['text']};
            }}
        """)
        subject_layout.addWidget(self.subject_input)
        layout.addLayout(subject_layout)

        # Action buttons
        button_layout = QHBoxLayout()
        button_layout.addStretch()

        borrow_btn = QPushButton("📚 Borrow Book")
        borrow_btn.setFixedHeight(44)
        borrow_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {theme['primary']};
                color: white;
                border: none;
                border-radius: 8px;
                padding: 12px 24px;
                font-weight: 500;
                font-size: 14px;
            }}
            QPushButton:hover {{
                background-color: {theme.get('primary_dark', theme['primary'])};
            }}
        """)
        borrow_btn.clicked.connect(self._execute_bulk_borrow)
        button_layout.addWidget(borrow_btn)

        layout.addLayout(button_layout)

    def _load_students_into_table(self):
        """Load all students into the table for individual book assignments."""
        try:
            # Get students based on class/stream criteria
            if self.class_level is not None and self.stream is not None:
                students = self.class_management_service.get_students_by_class_and_stream(self.class_level, self.stream)
            elif self.class_level is not None:
                students = self.class_management_service.get_students_by_class_level(self.class_level)
            elif self.stream is not None:
                students = self.class_management_service.get_students_by_stream(self.stream)
            else:
                students = self.class_management_service.get_all_students()

            self.students_table.setRowCount(0)

            for student in students:
                row = self.students_table.rowCount()
                self.students_table.insertRow(row)

                # Student Name
                name_item = QTableWidgetItem(student.name)
                name_item.setData(Qt.ItemDataRole.UserRole, student.student_id)
                self.students_table.setItem(row, 0, name_item)

                # Admission Number
                admission_item = QTableWidgetItem(student.admission_number or str(student.student_id))
                self.students_table.setItem(row, 1, admission_item)

                # Book Number input field
                from PyQt6.QtWidgets import QLineEdit
                book_input = QLineEdit()
                book_input.setPlaceholderText("Enter book number")
                self.students_table.setCellWidget(row, 2, book_input)

                # Status (initially empty)
                status_item = QTableWidgetItem("")
                self.students_table.setItem(row, 3, status_item)

        except Exception as e:
            logger.error(f"Error loading students into table: {e}")
            show_error_message("Error", f"Failed to load students: {str(e)}", self)

    def _on_borrow_all_books(self):
        """Handle borrowing books for all students in the table."""
        try:
            book_type = self.book_type_combo.currentText()
            subject = self.subject_combo.currentText()

            successful_borrows = 0
            failed_borrows = 0

            # Process each row in the table
            for row in range(self.students_table.rowCount()):
                # Get student ID
                name_item = self.students_table.item(row, 0)
                if not name_item:
                    continue
                student_id = name_item.data(Qt.ItemDataRole.UserRole)

                # Get book number from input field
                book_input = self.students_table.cellWidget(row, 2)
                if not book_input:
                    continue
                book_number = book_input.text().strip()

                if not book_number:
                    # Update status to indicate missing book number
                    status_item = self.students_table.item(row, 3)
                    if status_item:
                        status_item.setText("⚠️ No book number")
                    continue

                try:
                    # Attempt to borrow the book
                    success = self.book_service.borrow_book(book_number, str(student_id), 'student')
                    status_item = self.students_table.item(row, 3)

                    if success:
                        if status_item:
                            status_item.setText("✅ Borrowed")
                        successful_borrows += 1
                    else:
                        if status_item:
                            status_item.setText("❌ Failed")
                        failed_borrows += 1

                except Exception as e:
                    logger.error(f"Error borrowing book {book_number} for student {student_id}: {e}")
                    status_item = self.students_table.item(row, 3)
                    if status_item:
                        status_item.setText("❌ Error")
                    failed_borrows += 1

            # Show results
            if successful_borrows > 0:
                success_msg = f"Successfully borrowed {successful_borrows} books."
                if failed_borrows > 0:
                    success_msg += f" {failed_borrows} borrows failed."
                show_success_message("Bulk Borrow Complete", success_msg, self)
            else:
                show_error_message("No Books Borrowed", "No books were successfully borrowed. Check the status column for details.", self)

        except Exception as e:
            logger.error(f"Error in bulk borrow: {e}")
            show_error_message("Error", f"Failed to process bulk borrow: {str(e)}", self)

    def _execute_bulk_borrow(self):
        """Execute the bulk borrow operation."""
        book_id_str = self.book_id_input.text().strip()
        subject = self.subject_input.text().strip() or None
        
        if not book_id_str:
            show_error_message("Validation Error", "Please enter a book ID.", self)
            return
        
        try:
            book_id = int(book_id_str)
        except ValueError:
            show_error_message("Validation Error", "Book ID must be a valid number.", self)
            return
        
        # Show confirmation
        if self.class_level is not None and self.stream is not None:
            display_name = self.class_management_service.format_class_display_name(self.class_level, self.stream)
            message = f"Borrow book {book_id} for all students in {display_name}?"
        elif self.student_ids:
            message = f"Borrow book {book_id} for {len(self.student_ids)} selected students?"
        else:
            message = f"Borrow book {book_id} for all students?"
        
        reply = QMessageBox.question(
            self,
            "Confirm Bulk Borrow",
            message,
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )
        
        if reply != QMessageBox.StandardButton.Yes:
            return
        
        try:
            # Execute bulk borrow
            if self.student_ids:
                result = self.book_service.bulk_borrow_books_for_students(book_id, self.student_ids)
            else:
                result = self.book_service.bulk_borrow_books_by_class_stream(
                    book_id,
                    class_level=self.class_level,
                    stream=self.stream,
                    subject=subject
                )
            
            # Display results
            self._display_results(result)
            
            if result['success']:
                show_success_message(
                    "Success",
                    f"Successfully borrowed book for {result['successful_borrows']} out of {result['total_students']} students.",
                    self
                )
            else:
                show_error_message(
                    "Partial Success",
                    f"Only {result['successful_borrows']} out of {result['total_students']} borrows succeeded. Check results for details.",
                    self
                )
                
        except Exception as e:
            logger.error(f"Error in bulk borrow: {e}")
            show_error_message("Error", f"Failed to execute bulk borrow: {str(e)}", self)
    
    def _display_results(self, result: dict):
        """Display the operation results."""
        self.results_group.setVisible(True)
        
        results_text = f"""
Operation Summary:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ students: {result['total_students']}
        Successful: {result['successful_borrows']}
        Failed: {result['failed_borrows']}
        """
        
        if result['errors']:
            results_text += "\n\nErrors:\n"
            for error in result['errors'][:10]:  # Show first 10 errors
                results_text += f"  • {error}\n"
            if len(result['errors']) > 10:
                results_text += f"  ... and {len(result['errors']) - 10} more errors\n"
        
        self.results_text.setPlainText(results_text)
