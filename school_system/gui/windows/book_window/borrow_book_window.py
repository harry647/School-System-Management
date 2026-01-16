"""
Borrow Book Window

Dedicated window for borrowing books.
"""

from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QLineEdit, QComboBox, QTableWidget, QTableWidgetItem
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont

from school_system.gui.windows.base_function_window import BaseFunctionWindow
from school_system.gui.dialogs.message_dialog import show_error_message, show_success_message
from school_system.config.logging import logger
from school_system.services.book_service import BookService
from school_system.gui.windows.book_window.utils import USER_TYPES


class BorrowBookWindow(BaseFunctionWindow):
    """Dedicated window for borrowing books."""
    
    book_borrowed = pyqtSignal()
    
    def __init__(self, parent=None, current_user: str = "", current_role: str = ""):
        """Initialize the borrow book window."""
        super().__init__("Borrow Book", parent, current_user, current_role)
        
        self.book_service = BookService()
        
        # Setup content
        self.setup_content()
        
        # Load borrowed books
        self._refresh_borrowed_books_table()
    
    def setup_content(self):
        """Setup the borrow book form."""
        # Create main content layout
        main_layout = self.create_flex_layout("column", False)
        main_layout.setContentsMargins(24, 24, 24, 24)
        main_layout.set_spacing(16)
        
        # Borrow form card
        borrow_card = self._create_borrow_form_card()
        main_layout.add_widget(borrow_card)
        
        # Borrowed books table
        table_card = self._create_borrowed_books_table_card()
        main_layout.add_widget(table_card, stretch=1)
        
        # Add to content
        self.add_layout_to_content(main_layout)
    
    def _create_borrow_form_card(self) -> QWidget:
        """Create the borrow book form card."""
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
        form_layout.setSpacing(16)
        
        # Form title
        title_label = QLabel("Borrow Book")
        title_font = QFont("Segoe UI", 18, QFont.Weight.Medium)
        title_label.setFont(title_font)
        title_label.setStyleSheet(f"color: {theme["text"]}; margin-bottom: 8px;")
        form_layout.addWidget(title_label)
        
        # Form fields in horizontal layout
        fields_layout = QHBoxLayout()
        fields_layout.setSpacing(12)
        
        # User Type
        user_type_layout = QVBoxLayout()
        user_type_label = QLabel("User Type *")
        user_type_label.setStyleSheet(f"font-weight: 500; color: {theme["text"]}; margin-bottom: 4px;")
        user_type_layout.addWidget(user_type_label)
        
        self.user_type_combo = QComboBox()
        self.user_type_combo.setFixedHeight(44)
        self.user_type_combo.addItems(USER_TYPES)
        user_type_layout.addWidget(self.user_type_combo)
        fields_layout.addLayout(user_type_layout)
        
        # User ID
        user_id_layout = QVBoxLayout()
        user_id_label = QLabel("User ID *")
        user_id_label.setStyleSheet(f"font-weight: 500; color: {theme["text"]}; margin-bottom: 4px;")
        user_id_layout.addWidget(user_id_label)
        
        self.user_id_input = self.create_input("Enter user ID")
        self.user_id_input.setFixedHeight(44)
        self.user_id_input.setMinimumWidth(200)
        user_id_layout.addWidget(self.user_id_input)
        fields_layout.addLayout(user_id_layout)
        
        # Book ID
        book_id_layout = QVBoxLayout()
        book_id_label = QLabel("Book ID *")
        book_id_label.setStyleSheet(f"font-weight: 500; color: {theme["text"]}; margin-bottom: 4px;")
        book_id_layout.addWidget(book_id_label)
        
        self.book_id_input = self.create_input("Enter book ID")
        self.book_id_input.setFixedHeight(44)
        self.book_id_input.setMinimumWidth(200)
        book_id_layout.addWidget(self.book_id_input)
        fields_layout.addLayout(book_id_layout)
        
        fields_layout.addStretch()
        
        # Borrow button
        borrow_btn = self.create_button("Borrow Book", "primary")
        borrow_btn.setFixedHeight(44)
        borrow_btn.clicked.connect(self._on_borrow_book)
        fields_layout.addWidget(borrow_btn)
        
        form_layout.addLayout(fields_layout)
        
        return form_card
    
    def _create_borrowed_books_table_card(self) -> QWidget:
        """Create the borrowed books table card."""
        theme_manager = self.get_theme_manager()
        theme = theme_manager._themes[self.get_theme()]
        
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
        table_layout.setContentsMargins(0, 0, 0, 0)
        table_layout.setSpacing(12)
        
        # Table title and refresh button
        title_layout = QHBoxLayout()
        title_label = QLabel("Borrowed Books")
        title_font = QFont("Segoe UI", 16, QFont.Weight.Medium)
        title_label.setFont(title_font)
        title_label.setStyleSheet(f"color: {theme["text"]}; margin-bottom: 8px;")
        title_layout.addWidget(title_label)
        
        title_layout.addStretch()
        
        refresh_btn = self.create_button("🔄 Refresh", "outline")
        refresh_btn.clicked.connect(self._refresh_borrowed_books_table)
        title_layout.addWidget(refresh_btn)
        
        table_layout.addLayout(title_layout)
        
        # Borrowed books table
        self.borrowed_books_table = self.create_table(0, 5)
        self.borrowed_books_table.setHorizontalHeaderLabels([
            "User ID", "User Type", "Book ID", "Borrowed Date", "Status"
        ])
        self.borrowed_books_table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.borrowed_books_table.setAlternatingRowColors(True)
        table_layout.addWidget(self.borrowed_books_table)
        
        return table_card
    
    def _on_borrow_book(self):
        """Handle borrow book button click."""
        # Get form data
        user_type = self.user_type_combo.currentText().strip()
        user_id = self.user_id_input.text().strip()
        book_id = self.book_id_input.text().strip()
        
        # Validate
        if not user_type or not user_id or not book_id:
            show_error_message("Validation Error", "Please fill in all required fields.", self)
            return
        
        try:
            # Borrow book
            self.book_service.borrow_book(book_id, user_id, user_type)
            show_success_message("Success", f"Book {book_id} borrowed successfully by {user_id}.", self)
            
            # Clear inputs
            self.user_id_input.clear()
            self.book_id_input.clear()
            
            # Refresh table
            self._refresh_borrowed_books_table()
            
            # Emit signal
            self.book_borrowed.emit()
            
        except Exception as e:
            logger.error(f"Error borrowing book: {e}")
            show_error_message("Error", f"Failed to borrow book: {str(e)}", self)
    
    def _refresh_borrowed_books_table(self):
        """Refresh the borrowed books table."""
        try:
            borrowed_books = self.book_service.get_borrowed_books()
            
            # Clear table
            self.borrowed_books_table.setRowCount(0)
            
            # Populate table
            for borrow in borrowed_books:
                row = self.borrowed_books_table.rowCount()
                self.borrowed_books_table.insertRow(row)
                
                self.borrowed_books_table.setItem(row, 0, QTableWidgetItem(borrow.user_id))
                self.borrowed_books_table.setItem(row, 1, QTableWidgetItem(borrow.user_type))
                self.borrowed_books_table.setItem(row, 2, QTableWidgetItem(borrow.book_id))
                self.borrowed_books_table.setItem(row, 3, QTableWidgetItem(str(borrow.borrowed_date)))
                self.borrowed_books_table.setItem(row, 4, QTableWidgetItem("Borrowed"))
            
            logger.info(f"Refreshed borrowed books table with {len(borrowed_books)} entries")
        except Exception as e:
            logger.error(f"Error refreshing borrowed books table: {e}")
            show_error_message("Error", f"Failed to refresh borrowed books: {str(e)}", self)
