"""
Enhanced Return per Stream per Subject Window

Comprehensive window for returning books per stream and subject with table-based interface.
"""

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QComboBox,
    QTableWidget, QTableWidgetItem, QHeaderView, QMessageBox, QDialog,
    QGroupBox, QCheckBox, QAbstractItemView, QLineEdit, QTextEdit
)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont
from typing import Optional, List, Dict, Tuple
from datetime import datetime

from school_system.gui.windows.base_function_window import BaseFunctionWindow
from school_system.gui.dialogs.message_dialog import show_error_message, show_success_message
from school_system.config.logging import logger
from school_system.services.book_service import BookService
from school_system.services.class_management_service import ClassManagementService
from school_system.services.student_service import StudentService
from school_system.database.repositories.book_repo import BorrowedBookStudentRepository
from school_system.models.book import BorrowedBookStudent, Book


class EnhancedReturnWindow(QDialog):
    """Enhanced window for returning books per stream per subject with table interface."""

    return_completed = pyqtSignal()

    def __init__(
        self,
        parent=None,
        current_user: str = "",
        current_role: str = "",
        class_name: Optional[str] = None,
        stream_name: Optional[str] = None,
        subject: Optional[str] = None
    ):
        """Initialize the enhanced return window."""
        super().__init__(parent)
        
        self.setWindowTitle("Return per Stream per Subject")
        self.setMinimumWidth(1200)
        self.setMinimumHeight(700)
        
        self.book_service = BookService()
        self.class_management_service = ClassManagementService()
        self.student_service = StudentService()
        self.borrowed_book_repo = BorrowedBookStudentRepository()
        
        self.class_name = class_name
        self.stream_name = stream_name
        self.subject = subject
        self.current_user = current_user

        # Extract class level from class name for display purposes
        self.class_level = None
        if self.class_name:
            # Extract numeric level from class name (e.g., "Form 4" -> 4)
            if 'Form' in self.class_name:
                parts = self.class_name.split()
                for part in parts:
                    if part.isdigit():
                        self.class_level = int(part)
                        break
            elif 'Grade' in self.class_name:
                parts = self.class_name.split()
                for part in parts:
                    if part.isdigit():
                        self.class_level = int(part)
                        break
            elif self.class_name.isdigit():
                self.class_level = int(self.class_name)

        self.stream = self.stream_name  # For compatibility with format_class_display_name

        self.borrowed_books_data = []  # List of dicts with student and book info

        # Initialize filter criteria
        self.selected_stream = "All Streams"
        self.selected_subject = "All Subjects"

        self.setup_ui()
        self.load_borrowed_books()

    def setup_ui(self):
        """Setup the UI components."""
        from school_system.gui.base.widgets.theme import ThemeManager
        theme_manager = ThemeManager()
        theme = theme_manager._themes[theme_manager.get_theme()]
        
        layout = QVBoxLayout(self)
        layout.setSpacing(20)
        layout.setContentsMargins(24, 24, 24, 24)
        
        # Title
        title_label = QLabel("📖 Return per Stream per Subject")
        title_font = QFont("Segoe UI", 18, QFont.Weight.Medium)
        title_label.setFont(title_font)
        title_label.setStyleSheet(f"color: {theme['text']}; margin-bottom: 8px;")
        layout.addWidget(title_label)
        
        # Filters/Info Group
        info_group = QGroupBox("Return Criteria")
        info_group.setStyleSheet(f"""
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
        info_layout = QVBoxLayout(info_group)

        # Class display (read-only)
        if self.class_name:
            class_layout = QHBoxLayout()
            class_label = QLabel("Class:")
            class_label.setStyleSheet(f"font-weight: 500; color: {theme['text']};")
            class_layout.addWidget(class_label)

            self.class_display = QLabel(self.class_name)
            self.class_display.setStyleSheet(f"color: {theme['text_secondary']}; padding: 4px; background-color: {theme['surface']}; border-radius: 4px;")
            class_layout.addWidget(self.class_display)

            class_layout.addStretch()
            info_layout.addLayout(class_layout)

        # Stream selection
        stream_layout = QHBoxLayout()
        stream_label = QLabel("Stream:")
        stream_label.setStyleSheet(f"font-weight: 500; color: {theme['text']};")
        stream_layout.addWidget(stream_label)

        self.stream_combo = QComboBox()
        self.stream_combo.addItem("All Streams")
        # Load available streams dynamically
        try:
            available_streams = self.class_management_service.get_all_stream_names()
            self.stream_combo.addItems(available_streams)
        except Exception as e:
            logger.warning(f"Could not load streams dynamically: {e}")
            # Fallback to default streams
            self.stream_combo.addItems(["Red", "Blue", "Green", "Yellow", "Orange"])
        self.stream_combo.setFixedHeight(40)
        self.stream_combo.currentTextChanged.connect(self._on_criteria_changed)
        stream_layout.addWidget(self.stream_combo)

        stream_layout.addStretch()
        info_layout.addLayout(stream_layout)

        # Subject selection
        subject_layout = QHBoxLayout()
        subject_label = QLabel("Subject:")
        subject_label.setStyleSheet(f"font-weight: 500; color: {theme['text']};")
        subject_layout.addWidget(subject_label)

        self.subject_combo = QComboBox()
        self.subject_combo.addItem("All Subjects")
        # Load available subjects dynamically from database
        try:
            available_subjects = self.book_service.get_all_subjects()
            if available_subjects:
                self.subject_combo.addItems(available_subjects)
            else:
                # Fallback if no subjects found
                self.subject_combo.addItems(["Mathematics", "Science", "English", "History", "Geography"])
        except Exception as e:
            logger.warning(f"Could not load subjects dynamically: {e}")
            # Fallback to default subjects
            self.subject_combo.addItems(["Mathematics", "Science", "English", "History", "Geography"])
        self.subject_combo.setFixedHeight(40)
        self.subject_combo.currentTextChanged.connect(self._on_criteria_changed)
        subject_layout.addWidget(self.subject_combo)

        subject_layout.addStretch()
        info_layout.addLayout(subject_layout)
        
        layout.addWidget(info_group)
        
        # Control Buttons (Select All / Return All)
        control_layout = QHBoxLayout()
        
        self.select_all_checkbox = QCheckBox("Select All")
        self.select_all_checkbox.stateChanged.connect(self._toggle_select_all)
        control_layout.addWidget(self.select_all_checkbox)
        
        control_layout.addStretch()
        
        layout.addLayout(control_layout)
        
        # Books Table
        table_group = QGroupBox("Borrowed Books - Return Management")
        table_group.setStyleSheet(f"""
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
        table_layout = QVBoxLayout(table_group)
        
        # Table
        self.books_table = QTableWidget()
        self.books_table.setColumnCount(8)
        self.books_table.setHorizontalHeaderLabels([
            "Select", "Student Name", "Admission Number", "Book Number", "Subject", 
            "Borrowed Date", "Return", "Status"
        ])
        
        # Set header properties
        header = self.books_table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(3, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(4, QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(5, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(6, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(7, QHeaderView.ResizeMode.ResizeToContents)
        
        self.books_table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.books_table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.books_table.verticalHeader().setVisible(False)
        
        self.books_table.setStyleSheet(f"""
            QTableWidget {{
                background-color: {theme['background']};
                border: 1px solid {theme['border']};
                border-radius: 6px;
                gridline-color: {theme['border']};
            }}
            QTableWidget::item {{
                padding: 8px;
            }}
            QHeaderView::section {{
                background-color: {theme['surface']};
                color: {theme['text']};
                padding: 8px;
                border: 1px solid {theme['border']};
                font-weight: 600;
            }}
        """)
        
        table_layout.addWidget(self.books_table)
        layout.addWidget(table_group)
        
        # Action Buttons
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        
        return_all_btn = QPushButton("Return All Selected")
        return_all_btn.setFixedHeight(44)
        return_all_btn.setFixedWidth(180)
        return_all_btn.clicked.connect(self._return_all_selected)
        return_all_btn.setStyleSheet(f"""
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
        button_layout.addWidget(return_all_btn)
        
        cancel_btn = QPushButton("Close")
        cancel_btn.setFixedHeight(44)
        cancel_btn.setFixedWidth(120)
        cancel_btn.clicked.connect(self.close)
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
        
        layout.addLayout(button_layout)

    def load_borrowed_books(self):
        """Load borrowed books based on class and current filter criteria."""
        try:
            # Get students based on class and selected filters
            base_students = []
            if self.class_name is not None:
                base_students = self.class_management_service.get_students_by_class(self.class_name)
            else:
                base_students = self.student_service.get_all_students()

            # Apply stream filter
            if self.selected_stream != "All Streams":
                base_students = [s for s in base_students if s.stream_name == self.selected_stream]

            students = base_students
            
            # Get all borrowed books for these students
            self.borrowed_books_data = []
            
            for student in students:
                borrowed_books = self.borrowed_book_repo.get_borrowed_books_by_student(str(student.student_id))
                
                for borrowed_book in borrowed_books:
                    # Get book details
                    book = self.book_service.book_repository.get_by_id(borrowed_book.book_id)
                    if not book:
                        continue
                    
                    # Filter by subject if selected
                    book_subject = getattr(book, 'subject', None) or getattr(book, 'category', None) or 'N/A'
                    if self.selected_subject != "All Subjects" and book_subject and book_subject != self.selected_subject:
                        continue
                    
                    # Get book number - try different attributes
                    book_number = getattr(book, 'book_number', None) or getattr(book, 'id', None) or str(borrowed_book.book_id)
                    
                    self.borrowed_books_data.append({
                        'student_id': student.student_id,
                        'student_name': student.name,
                        'admission_number': getattr(student, 'admission_number', None) or str(student.student_id),
                        'book_id': borrowed_book.book_id,
                        'book_number': str(book_number),
                        'subject': book_subject or 'N/A',
                        'borrowed_on': borrowed_book.borrowed_on,
                        'borrowed_book': borrowed_book
                    })
            
            self.populate_table()
        except Exception as e:
            logger.error(f"Error loading borrowed books: {e}")
            show_error_message("Error", f"Failed to load borrowed books: {str(e)}", self)

    def populate_table(self):
        """Populate the table with borrowed books."""
        self.books_table.setRowCount(0)
        
        for idx, data in enumerate(self.borrowed_books_data):
            row = self.books_table.rowCount()
            self.books_table.insertRow(row)
            
            # Select Checkbox
            checkbox = QCheckBox()
            checkbox.setCheckState(Qt.CheckState.Unchecked)
            self.books_table.setCellWidget(row, 0, checkbox)
            
            # Student Name
            name_item = QTableWidgetItem(data['student_name'])
            name_item.setData(Qt.ItemDataRole.UserRole, idx)  # Store index for lookup
            self.books_table.setItem(row, 1, name_item)
            
            # Admission Number
            admission_item = QTableWidgetItem(data['admission_number'])
            self.books_table.setItem(row, 2, admission_item)
            
            # Book Number
            book_item = QTableWidgetItem(str(data['book_number']))
            self.books_table.setItem(row, 3, book_item)
            
            # Subject
            subject_item = QTableWidgetItem(data['subject'])
            self.books_table.setItem(row, 4, subject_item)
            
            # Borrowed Date
            borrowed_date = data['borrowed_on']
            if isinstance(borrowed_date, datetime):
                date_str = borrowed_date.strftime("%Y-%m-%d")
            else:
                date_str = str(borrowed_date)
            date_item = QTableWidgetItem(date_str)
            self.books_table.setItem(row, 5, date_item)
            
            # Return Button
            return_btn = QPushButton("Return")
            return_btn.setFixedHeight(32)
            return_btn.setFixedWidth(80)
            return_btn.clicked.connect(lambda checked, r=row: self._return_individual(r))
            self.books_table.setCellWidget(row, 6, return_btn)
            
            # Status
            status_item = QTableWidgetItem("Borrowed")
            status_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self.books_table.setItem(row, 7, status_item)

    def _toggle_select_all(self, state: int):
        """Toggle all checkboxes based on Select All checkbox."""
        checked = state == Qt.CheckState.Checked.value
        for row in range(self.books_table.rowCount()):
            checkbox = self.books_table.cellWidget(row, 0)
            if checkbox:
                checkbox.setCheckState(Qt.CheckState.Checked if checked else Qt.CheckState.Unchecked)

    def _return_individual(self, row: int):
        """Return individual book."""
        try:
            if row >= len(self.borrowed_books_data):
                return
            
            data = self.borrowed_books_data[row]
            student_id = str(data['student_id'])
            book_id = data['book_id']
            
            # Return the book
            success = self.book_service.return_book_student(
                student_id,
                book_id,
                return_condition="Good",
                fine_amount=0,
                returned_by=self.current_user
            )
            
            status_item = self.books_table.item(row, 7)
            if success:
                status_item.setText("Returned ✓")
                status_item.setForeground(Qt.GlobalColor.green)
                
                # Disable return button
                return_btn = self.books_table.cellWidget(row, 6)
                if return_btn:
                    return_btn.setEnabled(False)
                
                # Uncheck checkbox
                checkbox = self.books_table.cellWidget(row, 0)
                if checkbox:
                    checkbox.setEnabled(False)
                
                show_success_message(
                    "Success",
                    f"Book {data['book_number']} returned successfully for {data['student_name']}.",
                    self
                )
            else:
                status_item.setText("Failed ✗")
                status_item.setForeground(Qt.GlobalColor.red)
                show_error_message(
                    "Error",
                    f"Failed to return book {data['book_number']} for {data['student_name']}.",
                    self
                )
            
        except Exception as e:
            logger.error(f"Error in individual return: {e}")
            show_error_message("Error", f"Failed to process return: {str(e)}", self)

    def _return_all_selected(self):
        """Return all selected books."""
        try:
            selected_rows = []
            for row in range(self.books_table.rowCount()):
                checkbox = self.books_table.cellWidget(row, 0)
                if checkbox and checkbox.isChecked():
                    selected_rows.append(row)
            
            if not selected_rows:
                show_error_message("Validation Error", "Please select at least one book to return.", self)
                return
            
            # Confirm action
            reply = QMessageBox.question(
                self,
                "Confirm Return All",
                f"Return {len(selected_rows)} selected book(s)?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                QMessageBox.StandardButton.No
            )
            
            if reply != QMessageBox.StandardButton.Yes:
                return
            
            # Process returns
            successful = 0
            failed = 0
            
            for row in selected_rows:
                if row >= len(self.borrowed_books_data):
                    continue
                
                try:
                    data = self.borrowed_books_data[row]
                    
                    # Check if already returned
                    status_item = self.books_table.item(row, 7)
                    if status_item and status_item.text() == "Returned ✓":
                        continue
                    
                    student_id = str(data['student_id'])
                    book_id = data['book_id']
                    
                    success = self.book_service.return_book_student(
                        student_id,
                        book_id,
                        return_condition="Good",
                        fine_amount=0,
                        returned_by=self.current_user
                    )
                    
                    if success:
                        successful += 1
                        status_item.setText("Returned ✓")
                        status_item.setForeground(Qt.GlobalColor.green)
                        
                        # Disable return button
                        return_btn = self.books_table.cellWidget(row, 6)
                        if return_btn:
                            return_btn.setEnabled(False)
                        
                        # Disable checkbox
                        checkbox = self.books_table.cellWidget(row, 0)
                        if checkbox:
                            checkbox.setEnabled(False)
                    else:
                        failed += 1
                        status_item.setText("Failed ✗")
                        status_item.setForeground(Qt.GlobalColor.red)
                        
                except Exception as e:
                    failed += 1
                    logger.error(f"Error returning book at row {row}: {e}")
            
            show_success_message(
                "Bulk Return Complete",
                f"Successfully returned {successful} book(s). Failed: {failed}.",
                self
            )
            
            self.return_completed.emit()
            
        except Exception as e:
            logger.error(f"Error in bulk return: {e}")
            show_error_message("Error", f"Failed to process returns: {str(e)}", self)

    def _on_criteria_changed(self):
        """Handle changes in filter criteria."""
        self.selected_stream = self.stream_combo.currentText()
        self.selected_subject = self.subject_combo.currentText()
        self.load_borrowed_books()
