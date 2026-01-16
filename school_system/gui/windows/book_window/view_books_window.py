"""
View Books Window

Dedicated window for viewing and managing books list.
"""

from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QTableWidget, QTableWidgetItem, QComboBox
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont

from school_system.gui.windows.base_function_window import BaseFunctionWindow
from school_system.gui.dialogs.message_dialog import show_error_message, show_success_message
from school_system.config.logging import logger
from school_system.services.book_service import BookService
from school_system.gui.windows.book_window.utils import (
    BOOK_CONDITIONS, STANDARD_SUBJECTS, STANDARD_CLASSES, STANDARD_STREAMS
)


class ViewBooksWindow(BaseFunctionWindow):
    """Dedicated window for viewing and managing books."""
    
    book_updated = pyqtSignal()
    
    def __init__(self, parent=None, current_user: str = "", current_role: str = ""):
        """Initialize the view books window."""
        super().__init__("View Books", parent, current_user, current_role)
        
        self.book_service = BookService()
        self.books_table = None
        
        # Setup content
        self.setup_content()
        
        # Load initial data
        self._refresh_books_table()
    
    def setup_content(self):
        """Setup the main content area."""
        # Create main content layout
        main_layout = self.create_flex_layout("column", False)
        main_layout.set_margins(24, 24, 24, 24)
        main_layout.set_spacing(16)
        
        # Action bar with search and filters
        action_bar = self._create_action_bar()
        main_layout.add_widget(action_bar)
        
        # Books table
        books_card = self._create_books_table()
        main_layout.add_widget(books_card, stretch=1)
        
        # Add to content
        self.add_layout_to_content(main_layout)
    
    def _create_action_bar(self) -> QWidget:
        """Create the action bar with search, filters, and action buttons."""
        theme_manager = self.get_theme_manager()
        theme = theme_manager._themes[self.get_theme()]
        
        action_card = QWidget()
        action_card.setProperty("card", "true")
        action_card.setFixedHeight(80)
        action_card.setStyleSheet(f"""
            QWidget[card="true"] {{
                background-color: {theme["surface"]};
                border: 1px solid {theme["border"]};
                border-radius: 12px;
                padding: 16px;
            }}
        """)
        
        action_layout = QHBoxLayout(action_card)
        action_layout.setContentsMargins(16, 16, 16, 16)
        action_layout.setSpacing(12)
        
        # Search box
        self.search_box = self.create_search_box("Search books by title, author, ISBN, or ID...")
        self.search_box.setMinimumWidth(300)
        self.search_box.search_text_changed.connect(self._on_search)
        action_layout.addWidget(self.search_box)
        
        # Subject filter
        self.subject_filter = QComboBox()
        self.subject_filter.addItem("All Subjects")
        self.subject_filter.addItems(STANDARD_SUBJECTS)
        self.subject_filter.setMinimumWidth(150)
        self.subject_filter.currentTextChanged.connect(self._on_filter_changed)
        action_layout.addWidget(self.subject_filter)
        
        # Class filter
        self.class_filter = QComboBox()
        self.class_filter.addItem("All Classes")
        self.class_filter.addItems(STANDARD_CLASSES)
        self.class_filter.setMinimumWidth(120)
        self.class_filter.currentTextChanged.connect(self._on_filter_changed)
        action_layout.addWidget(self.class_filter)
        
        action_layout.addStretch()
        
        # Action buttons
        add_btn = self.create_button("➕ Add Book", "primary")
        add_btn.clicked.connect(self._on_add_book)
        action_layout.addWidget(add_btn)
        
        edit_btn = self.create_button("✏️ Edit", "secondary")
        edit_btn.clicked.connect(self._on_edit_book)
        action_layout.addWidget(edit_btn)
        
        delete_btn = self.create_button("🗑️ Delete", "danger")
        delete_btn.clicked.connect(self._on_delete_book)
        action_layout.addWidget(delete_btn)
        
        refresh_btn = self.create_button("🔄 Refresh", "outline")
        refresh_btn.clicked.connect(self._refresh_books_table)
        action_layout.addWidget(refresh_btn)
        
        return action_card
    
    def _create_books_table(self) -> QWidget:
        """Create the books table card."""
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
        
        # Table title
        title_label = QLabel("Books List")
        title_font = QFont("Segoe UI", 16, QFont.Weight.Medium)
        title_label.setFont(title_font)
        title_label.setStyleSheet(f"color: {theme["text"]}; margin-bottom: 8px;")
        table_layout.addWidget(title_label)
        
        # Books table
        self.books_table = self.create_table(0, 8)
        self.books_table.setColumnCount(8)
        self.books_table.setHorizontalHeaderLabels([
            "Book ID", "Title", "Author", "ISBN", "Category", "Class", "Condition", "Status"
        ])
        self.books_table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.books_table.setAlternatingRowColors(True)
        table_layout.addWidget(self.books_table)
        
        return table_card
    
    def _refresh_books_table(self):
        """Refresh the books table with current data."""
        try:
            # Get filters
            subject_filter = self.subject_filter.currentText()
            class_filter = self.class_filter.currentText()
            
            subject = None if subject_filter == "All Subjects" else subject_filter
            class_name = None if class_filter == "All Classes" else class_filter
            
            # Get books
            books = self.book_service.get_all_books()
            
            # Apply filters
            if subject:
                books = [b for b in books if b.subject == subject]
            if class_name:
                books = [b for b in books if b.class_name == class_name]
            
            # Clear table
            self.books_table.setRowCount(0)
            
            # Populate table
            for book in books:
                row = self.books_table.rowCount()
                self.books_table.insertRow(row)
                
                # Get status
                status = "Available"
                try:
                    borrowed = self.book_service.get_borrowed_books()
                    if any(b.book_number == book.book_number for b in borrowed):
                        status = "Borrowed"
                except:
                    pass
                
                self.books_table.setItem(row, 0, QTableWidgetItem(book.book_number))
                self.books_table.setItem(row, 1, QTableWidgetItem(book.title))
                self.books_table.setItem(row, 2, QTableWidgetItem(book.author or ""))
                self.books_table.setItem(row, 3, QTableWidgetItem(book.isbn or ""))
                self.books_table.setItem(row, 4, QTableWidgetItem(book.category or ""))
                self.books_table.setItem(row, 5, QTableWidgetItem(""))
                self.books_table.setItem(row, 6, QTableWidgetItem(book.book_condition or "Good"))
                self.books_table.setItem(row, 7, QTableWidgetItem(status))
            
            logger.info(f"Refreshed books table with {len(books)} books")
        except Exception as e:
            logger.error(f"Error refreshing books table: {e}")
            show_error_message("Error", f"Failed to refresh books: {str(e)}", self)
    
    def _on_search(self, text: str):
        """Handle search text change."""
        # Filter table based on search text
        for row in range(self.books_table.rowCount()):
            match = False
            for col in range(7):  # Check first 7 columns
                item = self.books_table.item(row, col)
                if item and text.lower() in item.text().lower():
                    match = True
                    break
            self.books_table.setRowHidden(row, not match)
    
    def _on_filter_changed(self, text: str):
        """Handle filter change."""
        self._refresh_books_table()
    
    def _on_add_book(self):
        """Open add book window."""
        from school_system.gui.windows.book_window.add_book_window import AddBookWindow
        add_window = AddBookWindow(self, self.current_user, self.current_role)
        add_window.book_added.connect(self._refresh_books_table)
        add_window.show()
    
    def _on_edit_book(self):
        """Open edit book window."""
        selected_rows = self.books_table.selectionModel().selectedRows()
        if not selected_rows:
            show_error_message("No Selection", "Please select a book to edit.", self)
            return
        
        book_number = self.books_table.item(selected_rows[0].row(), 0).text()
        from school_system.gui.windows.book_window.edit_book_window import EditBookWindow
        edit_window = EditBookWindow(book_number, self, self.current_user, self.current_role)
        edit_window.book_updated.connect(self._refresh_books_table)
        edit_window.show()
    
    def _on_delete_book(self):
        """Handle delete book."""
        selected_rows = self.books_table.selectionModel().selectedRows()
        if not selected_rows:
            show_error_message("No Selection", "Please select a book to delete.", self)
            return
        
        book_number = self.books_table.item(selected_rows[0].row(), 0).text()
        from school_system.gui.dialogs.confirm_dialog import ConfirmationDialog
        dialog = ConfirmationDialog(
            title="Delete Book",
            message=f"Are you sure you want to delete book {book_number}?\n\nThis action cannot be undone.",
            parent=self,
            confirm_text="Delete",
            cancel_text="Cancel"
        )

        if dialog.exec() == ConfirmationDialog.DialogCode.Accepted:
            try:
                self.book_service.remove_book(book_number)
                show_success_message("Success", f"Book {book_number} deleted successfully.", self)
                self._refresh_books_table()
            except Exception as e:
                show_error_message("Error", f"Failed to delete book: {str(e)}", self)
