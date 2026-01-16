"""
Add Book Window

Dedicated window for adding new books.
"""

from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QLineEdit, QComboBox, QTextEdit
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont

from school_system.gui.windows.base_function_window import BaseFunctionWindow
from school_system.gui.dialogs.message_dialog import show_error_message, show_success_message
from school_system.config.logging import logger
from school_system.services.book_service import BookService
from school_system.gui.windows.book_window.utils import (
    BOOK_CONDITIONS, STANDARD_SUBJECTS, STANDARD_CLASSES, STANDARD_STREAMS
)


class AddBookWindow(BaseFunctionWindow):
    """Dedicated window for adding new books."""
    
    book_added = pyqtSignal()
    
    def __init__(self, parent=None, current_user: str = "", current_role: str = ""):
        """Initialize the add book window."""
        super().__init__("Add New Book", parent, current_user, current_role)
        
        self.book_service = BookService()
        
        # Setup content
        self.setup_content()
    
    def setup_content(self):
        """Setup the add book form."""
        # Create main content layout
        main_layout = self.create_flex_layout("column", False)
        main_layout.setContentsMargins(24, 24, 24, 24)
        main_layout.set_spacing(24)
        
        # Form card
        form_card = self._create_form_card()
        main_layout.add_widget(form_card)
        
        # Add to content
        self.add_layout_to_content(main_layout)
    
    def _create_form_card(self) -> QWidget:
        """Create the book form card."""
        theme_manager = self.get_theme_manager()
        theme = theme_manager._themes[self.get_theme()]
        
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
        form_layout.setContentsMargins(24, 24, 24, 24)
        form_layout.setSpacing(20)
        
        # Form title
        title_label = QLabel("Book Information")
        title_font = QFont("Segoe UI", 18, QFont.Weight.Medium)
        title_label.setFont(title_font)
        title_label.setStyleSheet(f"color: {theme["text"]}; margin-bottom: 8px;")
        form_layout.addWidget(title_label)
        
        # Book ID field
        id_layout = QVBoxLayout()
        id_label = QLabel("Book ID *")
        id_label.setStyleSheet(f"font-weight: 500; color: {theme["text"]}; margin-bottom: 4px;")
        id_layout.addWidget(id_label)
        
        self.book_id_input = self.create_input("Enter book ID")
        self.book_id_input.setFixedHeight(44)
        id_layout.addWidget(self.book_id_input)
        form_layout.addLayout(id_layout)
        
        # Title field
        title_layout = QVBoxLayout()
        title_label = QLabel("Title *")
        title_label.setStyleSheet(f"font-weight: 500; color: {theme["text"]}; margin-bottom: 4px;")
        title_layout.addWidget(title_label)
        
        self.title_input = self.create_input("Enter book title")
        self.title_input.setFixedHeight(44)
        title_layout.addWidget(self.title_input)
        form_layout.addLayout(title_layout)
        
        # Author field
        author_layout = QVBoxLayout()
        author_label = QLabel("Author")
        author_label.setStyleSheet(f"font-weight: 500; color: {theme["text"]}; margin-bottom: 4px;")
        author_layout.addWidget(author_label)
        
        self.author_input = self.create_input("Enter author name")
        self.author_input.setFixedHeight(44)
        author_layout.addWidget(self.author_input)
        form_layout.addLayout(author_layout)
        
        # ISBN field
        isbn_layout = QVBoxLayout()
        isbn_label = QLabel("ISBN")
        isbn_label.setStyleSheet(f"font-weight: 500; color: {theme["text"]}; margin-bottom: 4px;")
        isbn_layout.addWidget(isbn_label)
        
        self.isbn_input = self.create_input("Enter ISBN")
        self.isbn_input.setFixedHeight(44)
        isbn_layout.addWidget(self.isbn_input)
        form_layout.addLayout(isbn_layout)
        
        # Subject field
        subject_layout = QVBoxLayout()
        subject_label = QLabel("Subject")
        subject_label.setStyleSheet(f"font-weight: 500; color: {theme["text"]}; margin-bottom: 4px;")
        subject_layout.addWidget(subject_label)
        
        self.subject_input = QComboBox()
        self.subject_input.setFixedHeight(44)
        self.subject_input.addItem("")
        self.subject_input.addItems(STANDARD_SUBJECTS)
        self.subject_input.setEditable(True)
        subject_layout.addWidget(self.subject_input)
        form_layout.addLayout(subject_layout)
        
        # Class field
        class_layout = QVBoxLayout()
        class_label = QLabel("Class")
        class_label.setStyleSheet(f"font-weight: 500; color: {theme["text"]}; margin-bottom: 4px;")
        class_layout.addWidget(class_label)
        
        self.class_input = QComboBox()
        self.class_input.setFixedHeight(44)
        self.class_input.addItem("")
        self.class_input.addItems(STANDARD_CLASSES)
        self.class_input.setEditable(True)
        class_layout.addWidget(self.class_input)
        form_layout.addLayout(class_layout)
        
        # Condition field
        condition_layout = QVBoxLayout()
        condition_label = QLabel("Condition *")
        condition_label.setStyleSheet(f"font-weight: 500; color: {theme["text"]}; margin-bottom: 4px;")
        condition_layout.addWidget(condition_label)
        
        self.condition_input = QComboBox()
        self.condition_input.setFixedHeight(44)
        self.condition_input.addItems(BOOK_CONDITIONS)
        condition_layout.addWidget(self.condition_input)
        form_layout.addLayout(condition_layout)
        
        form_layout.addStretch()
        
        # Action buttons
        button_layout = QHBoxLayout()
        button_layout.setSpacing(12)
        
        cancel_btn = self.create_button("Cancel", "outline")
        cancel_btn.clicked.connect(self.close)
        button_layout.addWidget(cancel_btn)
        
        button_layout.addStretch()
        
        save_btn = self.create_button("Save Book", "primary")
        save_btn.clicked.connect(self._on_save_book)
        button_layout.addWidget(save_btn)
        
        form_layout.addLayout(button_layout)
        
        return form_card
    
    def _on_save_book(self):
        """Handle save book button click."""
        # Get form data
        book_id = self.book_id_input.text().strip()
        title = self.title_input.text().strip()
        author = self.author_input.text().strip()
        isbn = self.isbn_input.text().strip()
        subject = self.subject_input.currentText().strip()
        class_name = self.class_input.currentText().strip()
        condition = self.condition_input.currentText().strip()
        
        # Validate
        if not book_id or not title or not condition:
            show_error_message("Validation Error", "Please fill in all required fields (Book ID, Title, Condition).", self)
            return
        
        try:
            # Create book
            book_data = {
                "book_id": book_id,
                "title": title,
                "author": author if author else None,
                "isbn": isbn if isbn else None,
                "subject": subject if subject else None,
                "class_name": class_name if class_name else None,
                "condition": condition
            }
            
            self.book_service.add_book(book_data)
            show_success_message("Success", f"Book {book_id} added successfully.", self)
            
            # Emit signal and close
            self.book_added.emit()
            self.close()
            
        except Exception as e:
            logger.error(f"Error adding book: {e}")
            show_error_message("Error", f"Failed to add book: {str(e)}", self)
