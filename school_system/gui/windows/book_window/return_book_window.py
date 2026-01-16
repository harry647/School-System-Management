"""
Return Book Window

Dedicated window for returning books.
"""

from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QLineEdit, QComboBox
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont

from school_system.gui.windows.base_function_window import BaseFunctionWindow
from school_system.gui.dialogs.message_dialog import show_error_message, show_success_message
from school_system.config.logging import logger
from school_system.services.book_service import BookService
from school_system.gui.windows.book_window.utils import USER_TYPES, RETURN_CONDITIONS


class ReturnBookWindow(BaseFunctionWindow):
    """Dedicated window for returning books."""
    
    book_returned = pyqtSignal()
    
    def __init__(self, parent=None, current_user: str = "", current_role: str = ""):
        """Initialize the return book window."""
        super().__init__("Return Book", parent, current_user, current_role)
        
        self.book_service = BookService()
        
        # Setup content
        self.setup_content()
    
    def setup_content(self):
        """Setup the return book form."""
        # Create main content layout
        main_layout = self.create_flex_layout("column", False)
        main_layout.setContentsMargins(24, 24, 24, 24)
        main_layout.set_spacing(24)
        
        # Return form card
        return_card = self._create_return_form_card()
        main_layout.add_widget(return_card)
        
        # Add to content
        self.add_layout_to_content(main_layout)
    
    def _create_return_form_card(self) -> QWidget:
        """Create the return book form card."""
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
        title_label = QLabel("Return Book")
        title_font = QFont("Segoe UI", 18, QFont.Weight.Medium)
        title_label.setFont(title_font)
        title_label.setStyleSheet(f"color: {theme["text"]}; margin-bottom: 8px;")
        form_layout.addWidget(title_label)
        
        # User Type
        user_type_layout = QVBoxLayout()
        user_type_label = QLabel("User Type *")
        user_type_label.setStyleSheet(f"font-weight: 500; color: {theme["text"]}; margin-bottom: 4px;")
        user_type_layout.addWidget(user_type_label)
        
        self.user_type_combo = QComboBox()
        self.user_type_combo.setFixedHeight(44)
        self.user_type_combo.addItems(USER_TYPES)
        user_type_layout.addWidget(self.user_type_combo)
        form_layout.addLayout(user_type_layout)
        
        # User ID
        user_id_layout = QVBoxLayout()
        user_id_label = QLabel("User ID *")
        user_id_label.setStyleSheet(f"font-weight: 500; color: {theme["text"]}; margin-bottom: 4px;")
        user_id_layout.addWidget(user_id_label)
        
        self.user_id_input = self.create_input("Enter user ID")
        self.user_id_input.setFixedHeight(44)
        user_id_layout.addWidget(self.user_id_input)
        form_layout.addLayout(user_id_layout)
        
        # Book ID
        book_id_layout = QVBoxLayout()
        book_id_label = QLabel("Book ID *")
        book_id_label.setStyleSheet(f"font-weight: 500; color: {theme["text"]}; margin-bottom: 4px;")
        book_id_layout.addWidget(book_id_label)
        
        self.book_id_input = self.create_input("Enter book ID")
        self.book_id_input.setFixedHeight(44)
        book_id_layout.addWidget(self.book_id_input)
        form_layout.addLayout(book_id_layout)
        
        # Condition
        condition_layout = QVBoxLayout()
        condition_label = QLabel("Return Condition *")
        condition_label.setStyleSheet(f"font-weight: 500; color: {theme["text"]}; margin-bottom: 4px;")
        condition_layout.addWidget(condition_label)
        
        self.condition_combo = QComboBox()
        self.condition_combo.setFixedHeight(44)
        self.condition_combo.addItems(RETURN_CONDITIONS)
        condition_layout.addWidget(self.condition_combo)
        form_layout.addLayout(condition_layout)
        
        # Fine Amount
        fine_layout = QVBoxLayout()
        fine_label = QLabel("Fine Amount")
        fine_label.setStyleSheet(f"font-weight: 500; color: {theme["text"]}; margin-bottom: 4px;")
        fine_layout.addWidget(fine_label)
        
        self.fine_input = self.create_input("Enter fine amount (0 if none)")
        self.fine_input.setFixedHeight(44)
        fine_layout.addWidget(self.fine_input)
        form_layout.addLayout(fine_layout)
        
        form_layout.addStretch()
        
        # Action buttons
        button_layout = QHBoxLayout()
        button_layout.setSpacing(12)
        
        cancel_btn = self.create_button("Cancel", "outline")
        cancel_btn.clicked.connect(self.close)
        button_layout.addWidget(cancel_btn)
        
        button_layout.addStretch()
        
        return_btn = self.create_button("Return Book", "primary")
        return_btn.clicked.connect(self._on_return_book)
        button_layout.addWidget(return_btn)
        
        form_layout.addLayout(button_layout)
        
        return form_card
    
    def _on_return_book(self):
        """Handle return book button click."""
        # Get form data
        user_type = self.user_type_combo.currentText().strip()
        user_id = self.user_id_input.text().strip()
        book_id = self.book_id_input.text().strip()
        condition = self.condition_combo.currentText().strip()
        fine_text = self.fine_input.text().strip()
        
        # Validate
        if not user_type or not user_id or not book_id or not condition:
            show_error_message("Validation Error", "Please fill in all required fields.", self)
            return
        
        # Parse fine amount
        fine_amount = 0.0
        if fine_text:
            try:
                fine_amount = float(fine_text)
                if fine_amount < 0:
                    raise ValueError("Fine amount cannot be negative")
            except ValueError:
                show_error_message("Validation Error", "Please enter a valid fine amount.", self)
                return
        
        try:
            # Return book
            self.book_service.return_book(book_id, user_id, user_type, condition, fine_amount)
            show_success_message("Success", f"Book {book_id} returned successfully.", self)
            
            # Clear inputs
            self.user_id_input.clear()
            self.book_id_input.clear()
            self.fine_input.clear()
            
            # Emit signal
            self.book_returned.emit()
            
        except Exception as e:
            logger.error(f"Error returning book: {e}")
            show_error_message("Error", f"Failed to return book: {str(e)}", self)
