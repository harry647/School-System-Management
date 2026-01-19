"""
View Books Window

Dedicated window for viewing and managing books list.
"""

from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QTableWidget, QTableWidgetItem, QComboBox, QFileDialog
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont

from school_system.gui.windows.base_function_window import BaseFunctionWindow
from school_system.gui.dialogs.message_dialog import show_error_message, show_success_message
from school_system.config.logging import logger
from school_system.services.book_service import BookService
from school_system.services.import_export_service import ImportExportService
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
        self.import_export_service = ImportExportService()
        self.books_table = None
        self.current_books_data = []  # Store current filtered books data
        
        # Setup content
        self.setup_content()
        
        # Load initial data
        self._refresh_books_table()
    
    def _load_subjects(self):
        """Load subjects dynamically from the database."""
        try:
            available_subjects = self.book_service.get_all_subjects()
            if available_subjects:
                self.subject_filter.addItems(available_subjects)
            else:
                # Fallback to standard subjects if database is empty
                self.subject_filter.addItems(STANDARD_SUBJECTS)
                logger.warning("No subjects found in database, using standard subjects")
        except Exception as e:
            logger.error(f"Error loading subjects from database: {e}")
            # Fallback to standard subjects on error
            self.subject_filter.addItems(STANDARD_SUBJECTS)
    
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
        # Load subjects dynamically from database
        self._load_subjects()
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

        # Sort controls
        sort_label = QLabel("Sort by Book Number:")
        sort_label.setStyleSheet(f"color: {theme['text']}; font-weight: 500; margin-left: 16px;")
        action_layout.addWidget(sort_label)

        self.sort_combo = QComboBox()
        self.sort_combo.addItems(["None", "Ascending", "Descending"])
        self.sort_combo.setMinimumWidth(120)
        self.sort_combo.currentTextChanged.connect(self._on_sort_changed)
        action_layout.addWidget(self.sort_combo)

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
        
        # Export section
        export_label = QLabel("Export:")
        export_label.setStyleSheet(f"color: {theme['text']}; font-weight: 500; margin-left: 16px;")
        action_layout.addWidget(export_label)

        excel_btn = self.create_button("📊 Excel", "secondary")
        excel_btn.clicked.connect(self._on_export_excel)
        excel_btn.setToolTip("Export books list to Excel")
        action_layout.addWidget(excel_btn)

        pdf_btn = self.create_button("📄 PDF", "secondary")
        pdf_btn.clicked.connect(self._on_export_pdf)
        pdf_btn.setToolTip("Export books list to PDF")
        action_layout.addWidget(pdf_btn)

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
        self.books_table = self.create_table(0, 9)
        self.books_table.setColumnCount(9)
        self.books_table.setHorizontalHeaderLabels([
            "Book Number", "Title", "Author", "ISBN", "Subject", "Class", "Type", "Condition", "Status"
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
                # Check both subject and category fields for compatibility
                books = [b for b in books if (getattr(b, 'subject', None) == subject or getattr(b, 'category', None) == subject)]
            if class_name:
                books = [b for b in books if b.class_name == class_name]

            # Store current filtered data
            self.current_books_data = books

            # Apply sorting
            sort_order = self.sort_combo.currentText()
            if sort_order == "Ascending":
                books = sorted(books, key=lambda x: x.book_number or "")
            elif sort_order == "Descending":
                books = sorted(books, key=lambda x: x.book_number or "", reverse=True)
            
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
                # Display subject if available, otherwise fall back to category
                subject_display = getattr(book, 'subject', None) or getattr(book, 'category', None) or ""
                self.books_table.setItem(row, 4, QTableWidgetItem(subject_display))
                self.books_table.setItem(row, 5, QTableWidgetItem(book.class_name or ""))
                self.books_table.setItem(row, 6, QTableWidgetItem(book.book_type.title()))
                self.books_table.setItem(row, 7, QTableWidgetItem(book.book_condition or "Good"))
                self.books_table.setItem(row, 8, QTableWidgetItem(status))
            
            logger.info(f"Refreshed books table with {len(books)} books")
        except Exception as e:
            logger.error(f"Error refreshing books table: {e}")
            show_error_message("Error", f"Failed to refresh books: {str(e)}", self)
    
    def _on_search(self, text: str):
        """Handle search text change."""
        # Filter table based on search text
        for row in range(self.books_table.rowCount()):
            match = False
            for col in range(9):  # Check all columns
                item = self.books_table.item(row, col)
                if item and text.lower() in item.text().lower():
                    match = True
                    break
            self.books_table.setRowHidden(row, not match)
    
    def _on_filter_changed(self, text: str):
        """Handle filter change."""
        self._refresh_books_table()

    def _on_sort_changed(self, sort_order: str):
        """Handle sort order change."""
        self._refresh_books_table()
    
    def _on_add_book(self):
        """Open add book window."""
        from school_system.gui.windows.book_window.add_book_window import AddBookWindow
        add_window = AddBookWindow(self, self.current_user, self.current_role)
        add_window.book_added.connect(self._on_book_added)
        add_window.show()
    
    def _on_book_added(self):
        """Handle book added event - refresh table and subjects."""
        self._refresh_subjects()
        self._refresh_books_table()
    
    def _on_edit_book(self):
        """Open edit book window."""
        selected_rows = self.books_table.selectionModel().selectedRows()
        if not selected_rows:
            show_error_message("No Selection", "Please select a book to edit.", self)
            return
        
        book_number = self.books_table.item(selected_rows[0].row(), 0).text()
        from school_system.gui.windows.book_window.edit_book_window import EditBookWindow
        edit_window = EditBookWindow(book_number, self, self.current_user, self.current_role)
        edit_window.book_updated.connect(self._on_book_updated)
        edit_window.show()
    
    def _on_book_updated(self):
        """Handle book updated event - refresh table and subjects."""
        self._refresh_subjects()
        self._refresh_books_table()
    
    def _refresh_subjects(self):
        """Refresh the subjects combobox with latest data from database."""
        current_selection = self.subject_filter.currentText()
        self.subject_filter.clear()
        self.subject_filter.addItem("All Subjects")
        self._load_subjects()
        # Restore previous selection if it still exists
        index = self.subject_filter.findText(current_selection)
        if index >= 0:
            self.subject_filter.setCurrentIndex(index)
    
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

    def _on_export_excel(self):
        """Handle Excel export button click."""
        try:
            if not self.current_books_data:
                show_error_message("No Data", "No books data to export. Please refresh the table first.", self)
                return

            # Convert books data to export format
            export_data = self._prepare_books_export_data()

            # Get file path from user
            file_path, _ = QFileDialog.getSaveFileName(
                self,
                "Export Books List - Excel",
                f"books_list_{self.subject_filter.currentText().replace(' ', '_')}_{self.class_filter.currentText().replace(' ', '_')}.xlsx",
                "Excel Files (*.xlsx);;All Files (*)"
            )

            if not file_path:
                return

            # Export to Excel
            success = self.import_export_service.export_to_excel(export_data, file_path)

            if success:
                show_success_message("Export Successful", f"Books list exported to Excel:\n{file_path}", self)
            else:
                show_error_message("Export Failed", "Failed to export books list to Excel.", self)

        except Exception as e:
            logger.error(f"Error exporting to Excel: {str(e)}")
            show_error_message("Export Error", f"An error occurred: {str(e)}", self)

    def _on_export_pdf(self):
        """Handle PDF export button click."""
        try:
            if not self.current_books_data:
                show_error_message("No Data", "No books data to export. Please refresh the table first.", self)
                return

            # Convert books data to export format
            export_data = self._prepare_books_export_data()

            # Get file path from user
            file_path, _ = QFileDialog.getSaveFileName(
                self,
                "Export Books List - PDF",
                f"books_list_{self.subject_filter.currentText().replace(' ', '_')}_{self.class_filter.currentText().replace(' ', '_')}.pdf",
                "PDF Files (*.pdf);;All Files (*)"
            )

            if not file_path:
                return

            # Export to PDF
            success = self.import_export_service.export_to_pdf(export_data, file_path)

            if success:
                show_success_message("Export Successful", f"Books list exported to PDF:\n{file_path}", self)
            else:
                show_error_message("Export Failed", "Failed to export books list to PDF.", self)

        except Exception as e:
            logger.error(f"Error exporting to PDF: {str(e)}")
            show_error_message("Export Error", f"An error occurred: {str(e)}", self)

    def _prepare_books_export_data(self) -> list:
        """Prepare books data for export."""
        export_data = []

        try:
            for book in self.current_books_data:
                # Get status
                status = "Available"
                try:
                    borrowed = self.book_service.get_borrowed_books()
                    if any(b.book_number == book.book_number for b in borrowed):
                        status = "Borrowed"
                except:
                    pass

                book_info = {
                    "Book_Number": book.book_number,
                    "Title": book.title,
                    "Author": book.author or "",
                    "ISBN": book.isbn or "",
                    "Subject": book.subject or book.category or "",
                    "Class_Level": book.class_name or "",
                    "Book_Type": book.book_type.title() if hasattr(book, 'book_type') and book.book_type else "course",
                    "Book_Condition": book.book_condition or "Good",
                    "Status": status,
                    "Publisher": getattr(book, 'publisher', ''),
                    "Publication_Year": getattr(book, 'publication_date', ''),
                    "Date_Added": getattr(book, 'created_at', ''),
                }
                export_data.append(book_info)

        except Exception as e:
            logger.error(f"Error preparing books export data: {str(e)}")

        return export_data
