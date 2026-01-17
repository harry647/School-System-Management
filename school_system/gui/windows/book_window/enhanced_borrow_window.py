"""
Enhanced Borrow per Stream per Subject Window

Comprehensive window for borrowing books per stream and subject with table-based interface.
"""

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QLineEdit,
    QComboBox, QTableWidget, QTableWidgetItem, QHeaderView, QMessageBox,
    QDialog, QGroupBox, QCheckBox, QAbstractItemView
)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont
from typing import Optional, List, Dict
from datetime import datetime

from school_system.gui.windows.base_function_window import BaseFunctionWindow
from school_system.gui.dialogs.message_dialog import show_error_message, show_success_message
from school_system.config.logging import logger
from school_system.services.book_service import BookService
from school_system.services.class_management_service import ClassManagementService
from school_system.services.student_service import StudentService


class EnhancedBorrowWindow(QDialog):
    """Enhanced window for borrowing books per stream per subject with table interface."""

    borrow_completed = pyqtSignal()

    def __init__(
        self,
        parent=None,
        current_user: str = "",
        current_role: str = "",
        class_level: Optional[int] = None,
        stream: Optional[str] = None,
        subject: Optional[str] = None
    ):
        """Initialize the enhanced borrow window."""
        super().__init__(parent)
        
        self.setWindowTitle("Borrow per Stream per Subject")
        self.setMinimumWidth(1000)
        self.setMinimumHeight(700)
        
        self.book_service = BookService()
        self.class_management_service = ClassManagementService()
        self.student_service = StudentService()
        
        self.class_level = class_level
        self.stream = stream
        self.subject = subject
        self.current_user = current_user
        
        self.students = []
        self.borrow_preview_data = {}  # Store preview data: {student_id: {book_id, subject}}
        
        self.setup_ui()
        self.load_students()

    def setup_ui(self):
        """Setup the UI components."""
        from school_system.gui.theme_manager import ThemeManager
        theme_manager = ThemeManager()
        theme = theme_manager._themes[theme_manager.get_theme()]
        
        layout = QVBoxLayout(self)
        layout.setSpacing(20)
        layout.setContentsMargins(24, 24, 24, 24)
        
        # Title
        title_label = QLabel("📚 Borrow per Stream per Subject")
        title_font = QFont("Segoe UI", 18, QFont.Weight.Medium)
        title_label.setFont(title_font)
        title_label.setStyleSheet(f"color: {theme['text']}; margin-bottom: 8px;")
        layout.addWidget(title_label)
        
        # Filters/Info Group
        info_group = QGroupBox("Borrow Criteria")
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
        
        criteria_text = []
        if self.class_level is not None:
            display_name = self.class_management_service.format_class_display_name(self.class_level, self.stream)
            criteria_text.append(f"Class-Stream: {display_name}")
        if self.subject:
            criteria_text.append(f"Subject: {self.subject}")
        
        if not criteria_text:
            criteria_text.append("All Students")
        
        criteria_label = QLabel("\n".join(criteria_text))
        criteria_label.setStyleSheet(f"color: {theme['text_secondary']}; padding: 8px;")
        info_layout.addWidget(criteria_label)
        
        layout.addWidget(info_group)
        
        # Students Table
        table_group = QGroupBox("Students - Book Borrowing")
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
        self.students_table = QTableWidget()
        self.students_table.setColumnCount(6)
        self.students_table.setHorizontalHeaderLabels([
            "Student Name", "Admission Number", "Book Number", "Subject", "Save", "Status"
        ])
        
        # Set header properties
        header = self.students_table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(3, QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(4, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(5, QHeaderView.ResizeMode.ResizeToContents)
        
        self.students_table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.students_table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.students_table.verticalHeader().setVisible(False)
        
        self.students_table.setStyleSheet(f"""
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
        
        table_layout.addWidget(self.students_table)
        layout.addWidget(table_group)
        
        # Action Buttons
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        
        preview_btn = QPushButton("Preview All")
        preview_btn.setFixedHeight(44)
        preview_btn.setFixedWidth(150)
        preview_btn.clicked.connect(self._preview_all)
        preview_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {theme['surface']};
                color: {theme['text']};
                border: 1px solid {theme['border']};
                border-radius: 6px;
                padding: 8px;
                font-weight: 600;
            }}
            QPushButton:hover {{
                background-color: {theme['border']};
            }}
        """)
        button_layout.addWidget(preview_btn)
        
        borrow_all_btn = QPushButton("Borrow All")
        borrow_all_btn.setFixedHeight(44)
        borrow_all_btn.setFixedWidth(150)
        borrow_all_btn.clicked.connect(self._borrow_all)
        borrow_all_btn.setStyleSheet(f"""
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
        button_layout.addWidget(borrow_all_btn)
        
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

    def load_students(self):
        """Load students based on class level and stream."""
        try:
            if self.class_level is not None and self.stream is not None:
                self.students = self.class_management_service.get_students_by_class_and_stream(
                    self.class_level, self.stream
                )
            elif self.class_level is not None:
                self.students = self.class_management_service.get_students_by_class_level(self.class_level)
            elif self.stream is not None:
                self.students = self.class_management_service.get_students_by_stream(self.stream)
            else:
                self.students = self.student_service.get_all_students()
            
            self.populate_table()
        except Exception as e:
            logger.error(f"Error loading students: {e}")
            show_error_message("Error", f"Failed to load students: {str(e)}", self)

    def populate_table(self):
        """Populate the table with students."""
        self.students_table.setRowCount(0)
        
        for student in self.students:
            row = self.students_table.rowCount()
            self.students_table.insertRow(row)
            
            # Student Name
            name_item = QTableWidgetItem(student.name)
            name_item.setData(Qt.ItemDataRole.UserRole, student.student_id)
            self.students_table.setItem(row, 0, name_item)
            
            # Admission Number
            admission_item = QTableWidgetItem(student.admission_number or str(student.student_id))
            self.students_table.setItem(row, 1, admission_item)
            
            # Book Number Input
            book_input = QLineEdit()
            book_input.setPlaceholderText("Enter book number")
            book_input.setFixedHeight(32)
            self.students_table.setCellWidget(row, 2, book_input)
            
            # Subject Input
            subject_input = QLineEdit()
            subject_input.setPlaceholderText("Enter subject")
            if self.subject:
                subject_input.setText(self.subject)
            subject_input.setFixedHeight(32)
            self.students_table.setCellWidget(row, 3, subject_input)
            
            # Save Button
            save_btn = QPushButton("Save")
            save_btn.setFixedHeight(32)
            save_btn.setFixedWidth(80)
            save_btn.clicked.connect(lambda checked, r=row: self._save_individual_borrow(r))
            self.students_table.setCellWidget(row, 4, save_btn)
            
            # Status
            status_item = QTableWidgetItem("Pending")
            status_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self.students_table.setItem(row, 5, status_item)

    def _save_individual_borrow(self, row: int):
        """Save individual borrow for a specific student."""
        try:
            student_item = self.students_table.item(row, 0)
            if not student_item:
                return
            
            student_id = student_item.data(Qt.ItemDataRole.UserRole)
            book_input = self.students_table.cellWidget(row, 2)
            subject_input = self.students_table.cellWidget(row, 3)
            
            book_id_str = book_input.text().strip() if book_input else ""
            subject = subject_input.text().strip() if subject_input else self.subject or ""
            
            if not book_id_str:
                show_error_message("Validation Error", "Please enter a book number.", self)
                return
            
            try:
                book_id = int(book_id_str)
            except ValueError:
                show_error_message("Validation Error", "Book number must be a valid number.", self)
                return
            
            # Borrow the book
            success = self.book_service.borrow_book(book_id, str(student_id), 'student')
            
            status_item = self.students_table.item(row, 5)
            if success:
                status_item.setText("Borrowed ✓")
                status_item.setForeground(Qt.GlobalColor.green)
                show_success_message("Success", f"Book {book_id} borrowed successfully for {student_item.text()}.", self)
            else:
                status_item.setText("Failed ✗")
                status_item.setForeground(Qt.GlobalColor.red)
                show_error_message("Error", f"Failed to borrow book {book_id} for {student_item.text()}.", self)
            
        except Exception as e:
            logger.error(f"Error in individual borrow: {e}")
            show_error_message("Error", f"Failed to process borrow: {str(e)}", self)

    def _preview_all(self):
        """Preview all borrowing operations before executing."""
        try:
            preview_data = []
            
            for row in range(self.students_table.rowCount()):
                student_item = self.students_table.item(row, 0)
                if not student_item:
                    continue
                
                student_id = student_item.data(Qt.ItemDataRole.UserRole)
                student_name = student_item.text()
                admission_item = self.students_table.item(row, 1)
                admission_number = admission_item.text() if admission_item else ""
                
                book_input = self.students_table.cellWidget(row, 2)
                subject_input = self.students_table.cellWidget(row, 3)
                
                book_id_str = book_input.text().strip() if book_input else ""
                subject = subject_input.text().strip() if subject_input else ""
                
                if book_id_str:
                    try:
                        book_id = int(book_id_str)
                        preview_data.append({
                            'student_id': student_id,
                            'student_name': student_name,
                            'admission_number': admission_number,
                            'book_id': book_id,
                            'subject': subject
                        })
                    except ValueError:
                        continue
            
            if not preview_data:
                show_error_message("Validation Error", "No valid borrow operations to preview. Please enter book numbers.", self)
                return
            
            # Show preview dialog
            preview_text = f"Preview - {len(preview_data)} Borrow Operations:\n\n"
            for item in preview_data:
                preview_text += f"• {item['student_name']} ({item['admission_number']}): Book {item['book_id']}"
                if item['subject']:
                    preview_text += f" - {item['subject']}"
                preview_text += "\n"
            
            reply = QMessageBox.question(
                self,
                "Preview Borrow Operations",
                preview_text + "\n\nProceed with these borrow operations?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                QMessageBox.StandardButton.No
            )
            
            if reply == QMessageBox.StandardButton.Yes:
                self._execute_previewed_borrows(preview_data)
                
        except Exception as e:
            logger.error(f"Error in preview: {e}")
            show_error_message("Error", f"Failed to preview operations: {str(e)}", self)

    def _execute_previewed_borrows(self, preview_data: List[Dict]):
        """Execute the previewed borrow operations."""
        try:
            successful = 0
            failed = 0
            
            for item in preview_data:
                try:
                    success = self.book_service.borrow_book(
                        item['book_id'],
                        str(item['student_id']),
                        'student'
                    )
                    
                    if success:
                        successful += 1
                    else:
                        failed += 1
                except Exception as e:
                    failed += 1
                    logger.error(f"Error borrowing for {item['student_name']}: {e}")
            
            # Update status in table
            for row in range(self.students_table.rowCount()):
                student_item = self.students_table.item(row, 0)
                if not student_item:
                    continue
                
                student_id = student_item.data(Qt.ItemDataRole.UserRole)
                book_input = self.students_table.cellWidget(row, 2)
                
                if not book_input or not book_input.text().strip():
                    continue
                
                # Find matching preview item
                for item in preview_data:
                    if item['student_id'] == student_id and str(item['book_id']) == book_input.text().strip():
                        status_item = self.students_table.item(row, 5)
                        if item.get('success', False):
                            status_item.setText("Borrowed ✓")
                            status_item.setForeground(Qt.GlobalColor.green)
                        else:
                            status_item.setText("Failed ✗")
                            status_item.setForeground(Qt.GlobalColor.red)
                        break
            
            show_success_message(
                "Bulk Borrow Complete",
                f"Successfully borrowed for {successful} students. Failed: {failed}.",
                self
            )
            
            self.borrow_completed.emit()
            
        except Exception as e:
            logger.error(f"Error executing previewed borrows: {e}")
            show_error_message("Error", f"Failed to execute borrow operations: {str(e)}", self)

    def _borrow_all(self):
        """Borrow books for all students with entered book numbers."""
        self._preview_all()  # Reuse preview functionality which shows confirmation
