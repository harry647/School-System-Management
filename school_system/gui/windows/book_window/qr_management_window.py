"""
QR Management Window

Comprehensive window for QR code-based book and student management including:
- Book QR code generation and management
- Student QR code generation and management
- QR-based borrowing and returning
- Batch QR code operations
"""

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QLineEdit,
    QComboBox, QTableWidget, QTableWidgetItem, QHeaderView, QMessageBox,
    QDialog, QGroupBox, QCheckBox, QAbstractItemView, QTabWidget, QTextEdit,
    QProgressBar, QFrame
)
from PyQt6.QtCore import Qt, pyqtSignal, QTimer
from PyQt6.QtGui import QFont, QPixmap, QPainter
from typing import Optional, List, Dict, Tuple
import qrcode
import io
from datetime import datetime

from school_system.gui.windows.base_function_window import BaseFunctionWindow
from school_system.gui.dialogs.message_dialog import show_error_message, show_success_message
from school_system.config.logging import logger
from school_system.services.book_service import BookService
from school_system.services.student_service import StudentService


class QRManagementWindow(QDialog):
    """Comprehensive QR management window for books and students."""

    operation_completed = pyqtSignal()

    def __init__(
        self,
        parent=None,
        current_user: str = "",
        current_role: str = "",
        initial_tab: str = "books"
    ):
        """Initialize the QR management window."""
        super().__init__(parent)

        self.setWindowTitle("QR Code Management System")
        self.setMinimumWidth(1400)
        self.setMinimumHeight(800)

        self.book_service = BookService()
        self.student_service = StudentService()

        self.current_user = current_user
        self.current_role = current_role

        self.setup_ui()
        self.load_initial_data()

        # Set initial tab
        tab_index = {"books": 0, "students": 1, "borrow": 2, "return": 3}.get(initial_tab, 0)
        self.tabs.setCurrentIndex(tab_index)

    def setup_ui(self):
        """Setup the UI components."""
        from school_system.gui.theme_manager import ThemeManager
        theme_manager = ThemeManager()
        theme = theme_manager._themes[theme_manager.get_theme()]

        layout = QVBoxLayout(self)
        layout.setSpacing(20)
        layout.setContentsMargins(24, 24, 24, 24)

        # Title
        title_label = QLabel("📱 QR Code Management System")
        title_font = QFont("Segoe UI", 18, QFont.Weight.Medium)
        title_label.setFont(title_font)
        title_label.setStyleSheet(f"color: {theme['text']}; margin-bottom: 8px;")
        layout.addWidget(title_label)

        # Subtitle
        subtitle_label = QLabel("Manage QR codes for books and students, enable QR-based borrowing and returning")
        subtitle_label.setStyleSheet(f"color: {theme['text_secondary']}; font-size: 12px;")
        layout.addWidget(subtitle_label)

        # Tabs
        self.tabs = QTabWidget()
        self.tabs.currentChanged.connect(self._on_tab_changed)

        # Book QR Management Tab
        books_tab = self._create_books_qr_tab(theme)
        self.tabs.addTab(books_tab, "📚 Book QR Codes")

        # Student QR Management Tab
        students_tab = self._create_students_qr_tab(theme)
        self.tabs.addTab(students_tab, "👨‍🎓 Student QR Codes")

        # QR Borrow Tab
        borrow_tab = self._create_qr_borrow_tab(theme)
        self.tabs.addTab(borrow_tab, "📖 QR Borrow")

        # QR Return Tab
        return_tab = self._create_qr_return_tab(theme)
        self.tabs.addTab(return_tab, "↩️ QR Return")

        layout.addWidget(self.tabs)

        # Close Button
        button_layout = QHBoxLayout()
        button_layout.addStretch()

        close_btn = QPushButton("Close")
        close_btn.setFixedHeight(44)
        close_btn.setFixedWidth(120)
        close_btn.clicked.connect(self.close)
        close_btn.setStyleSheet(f"""
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
        button_layout.addWidget(close_btn)

        layout.addLayout(button_layout)

    def _create_books_qr_tab(self, theme: dict) -> QWidget:
        """Create the books QR management tab."""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setSpacing(15)

        # Controls
        controls_layout = QHBoxLayout()

        # Search
        search_layout = QVBoxLayout()
        search_label = QLabel("Search Books:")
        search_label.setStyleSheet(f"font-weight: 500; color: {theme['text']};")
        search_layout.addWidget(search_label)

        self.books_search_input = QLineEdit()
        self.books_search_input.setPlaceholderText("Search by title, author, or book number...")
        self.books_search_input.setFixedHeight(32)
        self.books_search_input.textChanged.connect(self._filter_books_table)
        search_layout.addWidget(self.books_search_input)
        controls_layout.addLayout(search_layout)

        # Filter by QR status
        qr_filter_layout = QVBoxLayout()
        qr_filter_label = QLabel("QR Status:")
        qr_filter_label.setStyleSheet(f"font-weight: 500; color: {theme['text']};")
        qr_filter_layout.addWidget(qr_filter_label)

        self.books_qr_filter = QComboBox()
        self.books_qr_filter.addItems(["All Books", "With QR Code", "Without QR Code"])
        self.books_qr_filter.currentTextChanged.connect(self._filter_books_table)
        self.books_qr_filter.setFixedHeight(32)
        qr_filter_layout.addWidget(self.books_qr_filter)
        controls_layout.addLayout(qr_filter_layout)

        controls_layout.addStretch()

        # Batch operations
        batch_layout = QVBoxLayout()
        batch_label = QLabel("Batch Operations:")
        batch_label.setStyleSheet(f"font-weight: 500; color: {theme['text']};")
        batch_layout.addWidget(batch_label)

        batch_buttons_layout = QHBoxLayout()
        generate_all_btn = QPushButton("Generate QR for All")
        generate_all_btn.setFixedHeight(32)
        generate_all_btn.clicked.connect(self._generate_qr_for_all_books)
        batch_buttons_layout.addWidget(generate_all_btn)

        export_qr_btn = QPushButton("Export QR Codes")
        export_qr_btn.setFixedHeight(32)
        export_qr_btn.clicked.connect(self._export_book_qr_codes)
        batch_buttons_layout.addWidget(export_qr_btn)

        batch_layout.addLayout(batch_buttons_layout)
        controls_layout.addLayout(batch_layout)

        layout.addLayout(controls_layout)

        # Books table
        self.books_table = QTableWidget()
        self.books_table.setColumnCount(9)
        self.books_table.setHorizontalHeaderLabels([
            "Book Number", "Title", "Author", "Subject", "Class", "Available", "QR Code", "Generated", "Actions"
        ])

        header = self.books_table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(3, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(4, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(5, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(6, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(7, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(8, QHeaderView.ResizeMode.ResizeToContents)

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
            QHeaderView::section {{
                background-color: {theme['surface']};
                color: {theme['text']};
                padding: 8px;
                border: 1px solid {theme['border']};
                font-weight: 600;
            }}
        """)

        layout.addWidget(self.books_table)

        # Progress bar (hidden by default)
        self.books_progress_bar = QProgressBar()
        self.books_progress_bar.setVisible(False)
        layout.addWidget(self.books_progress_bar)

        return tab

    def _create_students_qr_tab(self, theme: dict) -> QWidget:
        """Create the students QR management tab."""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setSpacing(15)

        # Controls
        controls_layout = QHBoxLayout()

        # Search
        search_layout = QVBoxLayout()
        search_label = QLabel("Search Students:")
        search_label.setStyleSheet(f"font-weight: 500; color: {theme['text']};")
        search_layout.addWidget(search_label)

        self.students_search_input = QLineEdit()
        self.students_search_input.setPlaceholderText("Search by name or admission number...")
        self.students_search_input.setFixedHeight(32)
        self.students_search_input.textChanged.connect(self._filter_students_table)
        search_layout.addWidget(self.students_search_input)
        controls_layout.addLayout(search_layout)

        # Filter by QR status
        qr_filter_layout = QVBoxLayout()
        qr_filter_label = QLabel("QR Status:")
        qr_filter_label.setStyleSheet(f"font-weight: 500; color: {theme['text']};")
        qr_filter_layout.addWidget(qr_filter_label)

        self.students_qr_filter = QComboBox()
        self.students_qr_filter.addItems(["All Students", "With QR Code", "Without QR Code"])
        self.students_qr_filter.currentTextChanged.connect(self._filter_students_table)
        self.students_qr_filter.setFixedHeight(32)
        qr_filter_layout.addWidget(self.students_qr_filter)
        controls_layout.addLayout(qr_filter_layout)

        controls_layout.addStretch()

        # Batch operations
        batch_layout = QVBoxLayout()
        batch_label = QLabel("Batch Operations:")
        batch_label.setStyleSheet(f"font-weight: 500; color: {theme['text']};")
        batch_layout.addWidget(batch_label)

        batch_buttons_layout = QHBoxLayout()
        generate_all_btn = QPushButton("Generate QR for All")
        generate_all_btn.setFixedHeight(32)
        generate_all_btn.clicked.connect(self._generate_qr_for_all_students)
        batch_buttons_layout.addWidget(generate_all_btn)

        export_qr_btn = QPushButton("Export QR Codes")
        export_qr_btn.setFixedHeight(32)
        export_qr_btn.clicked.connect(self._export_student_qr_codes)
        batch_buttons_layout.addWidget(export_qr_btn)

        batch_layout.addLayout(batch_buttons_layout)
        controls_layout.addLayout(batch_layout)

        layout.addLayout(controls_layout)

        # Students table
        self.students_table = QTableWidget()
        self.students_table.setColumnCount(7)
        self.students_table.setHorizontalHeaderLabels([
            "Admission Number", "Name", "Stream", "QR Code", "Generated", "Actions", "Card Preview"
        ])

        header = self.students_table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(3, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(4, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(5, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(6, QHeaderView.ResizeMode.Fixed)
        header.resizeSection(6, 120)

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
            QHeaderView::section {{
                background-color: {theme['surface']};
                color: {theme['text']};
                padding: 8px;
                border: 1px solid {theme['border']};
                font-weight: 600;
            }}
        """)

        layout.addWidget(self.students_table)

        # Progress bar (hidden by default)
        self.students_progress_bar = QProgressBar()
        self.students_progress_bar.setVisible(False)
        layout.addWidget(self.students_progress_bar)

        return tab

    def _create_qr_borrow_tab(self, theme: dict) -> QWidget:
        """Create the QR borrow tab."""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setSpacing(20)

        # Instructions
        instructions = QLabel("Scan QR codes to borrow books:")
        instructions.setStyleSheet(f"font-weight: 500; color: {theme['text']}; font-size: 14px;")
        layout.addWidget(instructions)

        # QR Input Section
        input_group = QGroupBox("QR Code Input")
        input_group.setStyleSheet(f"""
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
        input_layout = QVBoxLayout(input_group)

        # Book QR input
        book_qr_layout = QHBoxLayout()
        book_qr_label = QLabel("Book QR Code:")
        book_qr_label.setStyleSheet(f"font-weight: 500; color: {theme['text']};")
        book_qr_layout.addWidget(book_qr_label)

        self.book_qr_input = QLineEdit()
        self.book_qr_input.setPlaceholderText("Scan or enter book QR code...")
        self.book_qr_input.setFixedHeight(40)
        self.book_qr_input.setStyleSheet(f"""
            QLineEdit {{
                padding: 8px;
                border: 2px solid {theme['border']};
                border-radius: 6px;
                background-color: {theme['background']};
                color: {theme['text']};
                font-size: 16px;
                font-weight: bold;
            }}
        """)
        book_qr_layout.addWidget(self.book_qr_input)
        input_layout.addLayout(book_qr_layout)

        # Student QR input
        student_qr_layout = QHBoxLayout()
        student_qr_label = QLabel("Student QR Code:")
        student_qr_label.setStyleSheet(f"font-weight: 500; color: {theme['text']};")
        student_qr_layout.addWidget(student_qr_label)

        self.student_qr_input = QLineEdit()
        self.student_qr_input.setPlaceholderText("Scan or enter student QR code...")
        self.student_qr_input.setFixedHeight(40)
        self.student_qr_input.setStyleSheet(f"""
            QLineEdit {{
                padding: 8px;
                border: 2px solid {theme['border']};
                border-radius: 6px;
                background-color: {theme['background']};
                color: {theme['text']};
                font-size: 16px;
                font-weight: bold;
            }}
        """)
        student_qr_layout.addWidget(self.student_qr_input)
        input_layout.addLayout(student_qr_layout)

        layout.addWidget(input_group)

        # Borrow button
        borrow_btn = QPushButton("📖 Borrow Book")
        borrow_btn.setFixedHeight(50)
        borrow_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {theme['primary']};
                color: white;
                border: none;
                border-radius: 8px;
                padding: 12px;
                font-size: 16px;
                font-weight: bold;
            }}
            QPushButton:hover {{
                background-color: {theme.get('primary_hover', theme['primary'])};
            }}
        """)
        borrow_btn.clicked.connect(self._borrow_by_qr)
        layout.addWidget(borrow_btn)

        # Status display
        self.borrow_status_text = QTextEdit()
        self.borrow_status_text.setReadOnly(True)
        self.borrow_status_text.setMaximumHeight(200)
        self.borrow_status_text.setStyleSheet(f"""
            QTextEdit {{
                background-color: {theme['background']};
                border: 1px solid {theme['border']};
                border-radius: 6px;
                padding: 8px;
                color: {theme['text']};
            }}
        """)
        layout.addWidget(self.borrow_status_text)

        layout.addStretch()
        return tab

    def _create_qr_return_tab(self, theme: dict) -> QWidget:
        """Create the QR return tab."""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setSpacing(20)

        # Instructions
        instructions = QLabel("Scan QR codes to return books:")
        instructions.setStyleSheet(f"font-weight: 500; color: {theme['text']}; font-size: 14px;")
        layout.addWidget(instructions)

        # QR Input Section
        input_group = QGroupBox("QR Code Input")
        input_group.setStyleSheet(f"""
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
        input_layout = QVBoxLayout(input_group)

        # Book QR input
        book_qr_layout = QHBoxLayout()
        book_qr_label = QLabel("Book QR Code:")
        book_qr_label.setStyleSheet(f"font-weight: 500; color: {theme['text']};")
        book_qr_layout.addWidget(book_qr_label)

        self.return_book_qr_input = QLineEdit()
        self.return_book_qr_input.setPlaceholderText("Scan or enter book QR code...")
        self.return_book_qr_input.setFixedHeight(40)
        self.return_book_qr_input.setStyleSheet(f"""
            QLineEdit {{
                padding: 8px;
                border: 2px solid {theme['border']};
                border-radius: 6px;
                background-color: {theme['background']};
                color: {theme['text']};
                font-size: 16px;
                font-weight: bold;
            }}
        """)
        book_qr_layout.addWidget(self.return_book_qr_input)
        input_layout.addLayout(book_qr_layout)

        # Student QR input
        student_qr_layout = QHBoxLayout()
        student_qr_label = QLabel("Student QR Code:")
        student_qr_label.setStyleSheet(f"font-weight: 500; color: {theme['text']};")
        student_qr_layout.addWidget(student_qr_label)

        self.return_student_qr_input = QLineEdit()
        self.return_student_qr_input.setPlaceholderText("Scan or enter student QR code...")
        self.return_student_qr_input.setFixedHeight(40)
        self.return_student_qr_input.setStyleSheet(f"""
            QLineEdit {{
                padding: 8px;
                border: 2px solid {theme['border']};
                border-radius: 6px;
                background-color: {theme['background']};
                color: {theme['text']};
                font-size: 16px;
                font-weight: bold;
            }}
        """)
        student_qr_layout.addWidget(self.return_student_qr_input)
        input_layout.addLayout(student_qr_layout)

        # Return condition
        condition_layout = QHBoxLayout()
        condition_label = QLabel("Return Condition:")
        condition_label.setStyleSheet(f"font-weight: 500; color: {theme['text']};")
        condition_layout.addWidget(condition_label)

        self.return_condition_combo = QComboBox()
        self.return_condition_combo.addItems(["Good", "Fair", "Poor", "Lost", "Damaged"])
        self.return_condition_combo.setCurrentText("Good")
        self.return_condition_combo.setFixedHeight(40)
        condition_layout.addWidget(self.return_condition_combo)
        condition_layout.addStretch()
        input_layout.addLayout(condition_layout)

        layout.addWidget(input_group)

        # Return button
        return_btn = QPushButton("↩️ Return Book")
        return_btn.setFixedHeight(50)
        return_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {theme['primary']};
                color: white;
                border: none;
                border-radius: 8px;
                padding: 12px;
                font-size: 16px;
                font-weight: bold;
            }}
            QPushButton:hover {{
                background-color: {theme.get('primary_hover', theme['primary'])};
            }}
        """)
        return_btn.clicked.connect(self._return_by_qr)
        layout.addWidget(return_btn)

        # Status display
        self.return_status_text = QTextEdit()
        self.return_status_text.setReadOnly(True)
        self.return_status_text.setMaximumHeight(200)
        self.return_status_text.setStyleSheet(f"""
            QTextEdit {{
                background-color: {theme['background']};
                border: 1px solid {theme['border']};
                border-radius: 6px;
                padding: 8px;
                color: {theme['text']};
            }}
        """)
        layout.addWidget(self.return_status_text)

        layout.addStretch()
        return tab

    def load_initial_data(self):
        """Load initial data for all tabs."""
        self._load_books_data()
        self._load_students_data()

    def _load_books_data(self):
        """Load books data for the books tab."""
        try:
            books = self.book_service.get_all_books()
            self._populate_books_table(books)
        except Exception as e:
            logger.error(f"Error loading books data: {e}")
            show_error_message("Error", f"Failed to load books data: {str(e)}", self)

    def _load_students_data(self):
        """Load students data for the students tab."""
        try:
            students = self.student_service.get_all_students()
            self._populate_students_table(students)
        except Exception as e:
            logger.error(f"Error loading students data: {e}")
            show_error_message("Error", f"Failed to load students data: {str(e)}", self)

    def _populate_books_table(self, books: List):
        """Populate the books table."""
        self.books_table.setRowCount(0)

        for book in books:
            row = self.books_table.rowCount()
            self.books_table.insertRow(row)

            # Book Number
            book_number_item = QTableWidgetItem(book.book_number)
            book_number_item.setData(Qt.ItemDataRole.UserRole, book.id)
            self.books_table.setItem(row, 0, book_number_item)

            # Title
            title_item = QTableWidgetItem(book.title)
            self.books_table.setItem(row, 1, title_item)

            # Author
            author_item = QTableWidgetItem(book.author)
            self.books_table.setItem(row, 2, author_item)

            # Subject
            subject_item = QTableWidgetItem(getattr(book, 'subject', ''))
            self.books_table.setItem(row, 3, subject_item)

            # Class
            class_item = QTableWidgetItem(getattr(book, 'class_name', ''))
            self.books_table.setItem(row, 4, class_item)

            # Available
            available_item = QTableWidgetItem("Yes" if book.available else "No")
            available_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self.books_table.setItem(row, 5, available_item)

            # QR Code
            qr_code = getattr(book, 'qr_code', None)
            qr_item = QTableWidgetItem(qr_code or "Not Generated")
            if qr_code:
                qr_item.setForeground(Qt.GlobalColor.darkGreen)
            else:
                qr_item.setForeground(Qt.GlobalColor.red)
            self.books_table.setItem(row, 6, qr_item)

            # Generated Date
            generated_at = getattr(book, 'qr_generated_at', None)
            generated_item = QTableWidgetItem(generated_at or "N/A")
            self.books_table.setItem(row, 7, generated_item)

            # Actions
            actions_widget = self._create_book_actions_widget(book)
            self.books_table.setCellWidget(row, 8, actions_widget)

    def _create_book_actions_widget(self, book) -> QWidget:
        """Create action buttons for a book row."""
        widget = QWidget()
        layout = QHBoxLayout(widget)
        layout.setContentsMargins(2, 2, 2, 2)
        layout.setSpacing(4)

        # Generate QR button
        if not getattr(book, 'qr_code', None):
            generate_btn = QPushButton("Generate QR")
            generate_btn.setFixedSize(100, 28)
            generate_btn.clicked.connect(lambda: self._generate_qr_for_book(book))
            layout.addWidget(generate_btn)
        else:
            view_qr_btn = QPushButton("View QR")
            view_qr_btn.setFixedSize(80, 28)
            view_qr_btn.clicked.connect(lambda: self._view_book_qr_code(book))
            layout.addWidget(view_qr_btn)

        layout.addStretch()
        return widget

    def _populate_students_table(self, students: List):
        """Populate the students table."""
        self.students_table.setRowCount(0)

        for student in students:
            row = self.students_table.rowCount()
            self.students_table.insertRow(row)

            # Admission Number
            admission_item = QTableWidgetItem(student.admission_number or str(student.student_id))
            admission_item.setData(Qt.ItemDataRole.UserRole, student.student_id)
            self.students_table.setItem(row, 0, admission_item)

            # Name
            name_item = QTableWidgetItem(student.name)
            self.students_table.setItem(row, 1, name_item)

            # Stream
            stream_item = QTableWidgetItem(student.stream)
            self.students_table.setItem(row, 2, stream_item)

            # QR Code
            qr_code = getattr(student, 'qr_code', None)
            qr_item = QTableWidgetItem(qr_code or "Not Generated")
            if qr_code:
                qr_item.setForeground(Qt.GlobalColor.darkGreen)
            else:
                qr_item.setForeground(Qt.GlobalColor.red)
            self.students_table.setItem(row, 3, qr_item)

            # Generated Date
            generated_at = getattr(student, 'qr_generated_at', None)
            generated_item = QTableWidgetItem(generated_at or "N/A")
            self.students_table.setItem(row, 4, generated_item)

            # Actions
            actions_widget = self._create_student_actions_widget(student)
            self.students_table.setCellWidget(row, 5, actions_widget)

            # Card Preview
            card_widget = self._create_student_card_preview_widget(student)
            self.students_table.setCellWidget(row, 6, card_widget)

    def _create_student_actions_widget(self, student) -> QWidget:
        """Create action buttons for a student row."""
        widget = QWidget()
        layout = QHBoxLayout(widget)
        layout.setContentsMargins(2, 2, 2, 2)
        layout.setSpacing(4)

        # Generate QR button
        if not getattr(student, 'qr_code', None):
            generate_btn = QPushButton("Generate QR")
            generate_btn.setFixedSize(100, 28)
            generate_btn.clicked.connect(lambda: self._generate_qr_for_student(student))
            layout.addWidget(generate_btn)
        else:
            view_qr_btn = QPushButton("View QR")
            view_qr_btn.setFixedSize(80, 28)
            view_qr_btn.clicked.connect(lambda: self._view_student_qr_code(student))
            layout.addWidget(view_qr_btn)

        layout.addStretch()
        return widget

    def _create_student_card_preview_widget(self, student) -> QWidget:
        """Create a preview widget for student borrowing card."""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(2, 2, 2, 2)
        layout.setSpacing(2)

        preview_btn = QPushButton("Preview Card")
        preview_btn.setFixedSize(110, 32)
        preview_btn.clicked.connect(lambda: self._show_student_card_preview(student))
        layout.addWidget(preview_btn)

        return widget

    def _generate_qr_for_book(self, book):
        """Generate QR code for a specific book."""
        try:
            qr_code = self.book_service.generate_qr_code_for_book(book.id)
            if qr_code:
                show_success_message("Success", f"QR code generated for book '{book.title}': {qr_code}", self)
                self._load_books_data()  # Refresh table
            else:
                show_error_message("Error", f"Failed to generate QR code for book '{book.title}'", self)
        except Exception as e:
            logger.error(f"Error generating QR for book {book.id}: {e}")
            show_error_message("Error", f"Failed to generate QR code: {str(e)}", self)

    def _view_book_qr_code(self, book):
        """View QR code for a book."""
        self._show_qr_code_dialog("Book QR Code", book.title, getattr(book, 'qr_code', None))

    def _generate_qr_for_student(self, student):
        """Generate QR code for a specific student."""
        try:
            admission_number = student.admission_number or str(student.student_id)
            qr_code = self.student_service.generate_qr_code_for_student(admission_number)
            if qr_code:
                show_success_message("Success", f"QR code generated for student '{student.name}': {qr_code}", self)
                self._load_students_data()  # Refresh table
            else:
                show_error_message("Error", f"Failed to generate QR code for student '{student.name}'", self)
        except Exception as e:
            logger.error(f"Error generating QR for student {student.student_id}: {e}")
            show_error_message("Error", f"Failed to generate QR code: {str(e)}", self)

    def _view_student_qr_code(self, student):
        """View QR code for a student."""
        self._show_qr_code_dialog("Student QR Code", student.name, getattr(student, 'qr_code', None))

    def _show_qr_code_dialog(self, title: str, item_name: str, qr_code: str):
        """Show a dialog with QR code."""
        if not qr_code:
            show_error_message("Error", "No QR code available", self)
            return

        dialog = QDialog(self)
        dialog.setWindowTitle(title)
        dialog.setMinimumWidth(400)
        dialog.setMinimumHeight(450)

        layout = QVBoxLayout(dialog)

        # Title
        title_label = QLabel(f"{title}: {item_name}")
        title_label.setStyleSheet("font-weight: bold; font-size: 14px;")
        layout.addWidget(title_label)

        # QR Code display
        qr_label = QLabel()
        qr_pixmap = self._generate_qr_pixmap(qr_code, 200)
        if qr_pixmap:
            qr_label.setPixmap(qr_pixmap)
        else:
            qr_label.setText("Failed to generate QR code image")
        qr_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(qr_label)

        # QR Code text
        code_label = QLabel(f"Code: {qr_code}")
        code_label.setStyleSheet("font-family: monospace; font-size: 12px; color: #666;")
        code_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(code_label)

        # Close button
        close_btn = QPushButton("Close")
        close_btn.clicked.connect(dialog.close)
        layout.addWidget(close_btn)

        dialog.exec()

    def _generate_qr_pixmap(self, data: str, size: int = 200) -> Optional[QPixmap]:
        """Generate QR code pixmap."""
        try:
            qr = qrcode.QRCode(version=1, box_size=10, border=5)
            qr.add_data(data)
            qr.make(fit=True)

            img = qr.make_image(fill_color="black", back_color="white")

            # Convert PIL image to QPixmap
            buffer = io.BytesIO()
            img.save(buffer, format='PNG')
            buffer.seek(0)

            pixmap = QPixmap()
            pixmap.loadFromData(buffer.getvalue(), 'PNG')
            pixmap = pixmap.scaled(size, size, Qt.AspectRatioMode.KeepAspectRatio)
            return pixmap

        except Exception as e:
            logger.error(f"Error generating QR pixmap: {e}")
            return None

    def _show_student_card_preview(self, student):
        """Show student borrowing card preview."""
        dialog = QDialog(self)
        dialog.setWindowTitle("Student Borrowing Card Preview")
        dialog.setMinimumWidth(600)
        dialog.setMinimumHeight(400)

        layout = QVBoxLayout(dialog)

        # Card preview
        card_widget = self._create_borrowing_card(student)
        layout.addWidget(card_widget)

        # Close button
        close_btn = QPushButton("Close")
        close_btn.clicked.connect(dialog.close)
        layout.addWidget(close_btn)

        dialog.exec()

    def _create_borrowing_card(self, student) -> QWidget:
        """Create a borrowing card widget."""
        card = QFrame()
        card.setFixedSize(550, 350)
        card.setStyleSheet("""
            QFrame {
                background-color: white;
                border: 2px solid #333;
                border-radius: 10px;
            }
        """)

        layout = QVBoxLayout(card)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(10)

        # Header
        header = QLabel("STUDENT BORROWING CARD")
        header.setStyleSheet("font-size: 16px; font-weight: bold; color: #333;")
        header.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(header)

        # Student info
        info_layout = QVBoxLayout()
        info_layout.setSpacing(5)

        name_label = QLabel(f"Name: {student.name}")
        name_label.setStyleSheet("font-size: 12px; font-weight: bold;")
        info_layout.addWidget(name_label)

        admission_label = QLabel(f"Admission No: {student.admission_number or student.student_id}")
        admission_label.setStyleSheet("font-size: 12px;")
        info_layout.addWidget(admission_label)

        stream_label = QLabel(f"Stream: {student.stream}")
        stream_label.setStyleSheet("font-size: 12px;")
        info_layout.addWidget(stream_label)

        layout.addLayout(info_layout)

        # QR Code
        qr_code = getattr(student, 'qr_code', None)
        if qr_code:
            qr_label = QLabel()
            qr_pixmap = self._generate_qr_pixmap(qr_code, 120)
            if qr_pixmap:
                qr_label.setPixmap(qr_pixmap)
            qr_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            layout.addWidget(qr_label)

            qr_text_label = QLabel(f"QR Code: {qr_code}")
            qr_text_label.setStyleSheet("font-family: monospace; font-size: 10px; color: #666;")
            qr_text_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            layout.addWidget(qr_text_label)
        else:
            no_qr_label = QLabel("No QR Code Generated")
            no_qr_label.setStyleSheet("color: red; font-size: 12px;")
            no_qr_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            layout.addWidget(no_qr_label)

        # Footer
        footer = QLabel("Scan this card to borrow/return books")
        footer.setStyleSheet("font-size: 10px; color: #666;")
        footer.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(footer)

        layout.addStretch()
        return card

    def _borrow_by_qr(self):
        """Borrow a book using QR codes."""
        book_qr = self.book_qr_input.text().strip()
        student_qr = self.student_qr_input.text().strip()

        if not book_qr or not student_qr:
            self._update_borrow_status("Error: Please enter both book and student QR codes")
            return

        try:
            success = self.book_service.borrow_book_by_qr(book_qr, student_qr)
            if success:
                # Get book and student details for display
                book = self.book_service.get_book_by_qr_code(book_qr)
                student = self.student_service.get_student_by_qr_code(student_qr)

                book_name = book.title if book else "Unknown Book"
                student_name = student.name if student else "Unknown Student"

                self._update_borrow_status(f"✅ SUCCESS: '{book_name}' borrowed by {student_name}")

                # Clear inputs
                self.book_qr_input.clear()
                self.student_qr_input.clear()

                # Refresh data
                self.operation_completed.emit()
            else:
                self._update_borrow_status("❌ FAILED: Could not process borrowing request")

        except Exception as e:
            logger.error(f"Error in QR borrow: {e}")
            self._update_borrow_status(f"❌ ERROR: {str(e)}")

    def _return_by_qr(self):
        """Return a book using QR codes."""
        book_qr = self.return_book_qr_input.text().strip()
        student_qr = self.return_student_qr_input.text().strip()
        condition = self.return_condition_combo.currentText()

        if not book_qr or not student_qr:
            self._update_return_status("Error: Please enter both book and student QR codes")
            return

        try:
            success = self.book_service.return_book_by_qr(book_qr, student_qr, condition)
            if success:
                # Get book and student details for display
                book = self.book_service.get_book_by_qr_code(book_qr)
                student = self.student_service.get_student_by_qr_code(student_qr)

                book_name = book.title if book else "Unknown Book"
                student_name = student.name if student else "Unknown Student"

                self._update_return_status(f"✅ SUCCESS: '{book_name}' returned by {student_name}\nCondition: {condition}")

                # Clear inputs
                self.return_book_qr_input.clear()
                self.return_student_qr_input.clear()
                self.return_condition_combo.setCurrentText("Good")

                # Refresh data
                self.operation_completed.emit()
            else:
                self._update_return_status("❌ FAILED: Could not process return request")

        except Exception as e:
            logger.error(f"Error in QR return: {e}")
            self._update_return_status(f"❌ ERROR: {str(e)}")

    def _update_borrow_status(self, message: str):
        """Update borrow status display."""
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.borrow_status_text.append(f"[{timestamp}] {message}\n")
        # Auto scroll to bottom
        cursor = self.borrow_status_text.textCursor()
        cursor.movePosition(cursor.MoveOperation.End)
        self.borrow_status_text.setTextCursor(cursor)

    def _update_return_status(self, message: str):
        """Update return status display."""
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.return_status_text.append(f"[{timestamp}] {message}\n")
        # Auto scroll to bottom
        cursor = self.return_status_text.textCursor()
        cursor.movePosition(cursor.MoveOperation.End)
        self.return_status_text.setTextCursor(cursor)

    def _filter_books_table(self):
        """Filter books table based on search and QR status."""
        search_text = self.books_search_input.text().lower()
        qr_filter = self.books_qr_filter.currentText()

        for row in range(self.books_table.rowCount()):
            show_row = True

            # Search filter
            if search_text:
                title = self.books_table.item(row, 1).text().lower()
                author = self.books_table.item(row, 2).text().lower()
                book_number = self.books_table.item(row, 0).text().lower()

                if search_text not in title and search_text not in author and search_text not in book_number:
                    show_row = False

            # QR filter
            if show_row and qr_filter != "All Books":
                qr_code = self.books_table.item(row, 6).text()
                has_qr = qr_code != "Not Generated"

                if qr_filter == "With QR Code" and not has_qr:
                    show_row = False
                elif qr_filter == "Without QR Code" and has_qr:
                    show_row = False

            self.books_table.setRowHidden(row, not show_row)

    def _filter_students_table(self):
        """Filter students table based on search and QR status."""
        search_text = self.students_search_input.text().lower()
        qr_filter = self.students_qr_filter.currentText()

        for row in range(self.students_table.rowCount()):
            show_row = True

            # Search filter
            if search_text:
                name = self.students_table.item(row, 1).text().lower()
                admission = self.students_table.item(row, 0).text().lower()

                if search_text not in name and search_text not in admission:
                    show_row = False

            # QR filter
            if show_row and qr_filter != "All Students":
                qr_code = self.students_table.item(row, 3).text()
                has_qr = qr_code != "Not Generated"

                if qr_filter == "With QR Code" and not has_qr:
                    show_row = False
                elif qr_filter == "Without QR Code" and has_qr:
                    show_row = False

            self.students_table.setRowHidden(row, not show_row)

    def _generate_qr_for_all_books(self):
        """Generate QR codes for all books without QR codes."""
        reply = QMessageBox.question(
            self,
            "Generate QR Codes",
            "Generate QR codes for all books that don't have them?\nThis may take a while for large collections.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )

        if reply != QMessageBox.StandardButton.Yes:
            return

        # Show progress bar
        self.books_progress_bar.setVisible(True)
        self.books_progress_bar.setRange(0, 0)  # Indeterminate progress

        # Process in background
        QTimer.singleShot(100, lambda: self._do_generate_qr_for_all_books())

    def _do_generate_qr_for_all_books(self):
        """Background task to generate QR codes for all books."""
        try:
            books = self.book_service.get_all_books()
            generated = 0

            for book in books:
                if not getattr(book, 'qr_code', None):
                    qr_code = self.book_service.generate_qr_code_for_book(book.id)
                    if qr_code:
                        generated += 1

            show_success_message("Success", f"Generated QR codes for {generated} books", self)
            self._load_books_data()  # Refresh table

        except Exception as e:
            logger.error(f"Error generating QR codes for all books: {e}")
            show_error_message("Error", f"Failed to generate QR codes: {str(e)}", self)

        finally:
            self.books_progress_bar.setVisible(False)

    def _generate_qr_for_all_students(self):
        """Generate QR codes for all students without QR codes."""
        reply = QMessageBox.question(
            self,
            "Generate QR Codes",
            "Generate QR codes for all students that don't have them?\nThis may take a while for large student populations.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )

        if reply != QMessageBox.StandardButton.Yes:
            return

        # Show progress bar
        self.students_progress_bar.setVisible(True)
        self.students_progress_bar.setRange(0, 0)  # Indeterminate progress

        # Process in background
        QTimer.singleShot(100, lambda: self._do_generate_qr_for_all_students())

    def _do_generate_qr_for_all_students(self):
        """Background task to generate QR codes for all students."""
        try:
            students = self.student_service.get_all_students()
            generated = 0

            for student in students:
                if not getattr(student, 'qr_code', None):
                    admission_number = student.admission_number or str(student.student_id)
                    qr_code = self.student_service.generate_qr_code_for_student(admission_number)
                    if qr_code:
                        generated += 1

            show_success_message("Success", f"Generated QR codes for {generated} students", self)
            self._load_students_data()  # Refresh table

        except Exception as e:
            logger.error(f"Error generating QR codes for all students: {e}")
            show_error_message("Error", f"Failed to generate QR codes: {str(e)}", self)

        finally:
            self.students_progress_bar.setVisible(False)

    def _export_book_qr_codes(self):
        """Export book QR codes."""
        QMessageBox.information(self, "Export", "QR code export functionality will be implemented here.")

    def _export_student_qr_codes(self):
        """Export student QR codes."""
        QMessageBox.information(self, "Export", "QR code export functionality will be implemented here.")

    def _on_tab_changed(self, index: int):
        """Handle tab changes."""
        # Refresh data when switching to tabs
        if index == 0:  # Books tab
            self._load_books_data()
        elif index == 1:  # Students tab
            self._load_students_data()