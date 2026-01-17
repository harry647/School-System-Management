"""
Book Import/Export Window

Dedicated window for importing and exporting book data.
"""

from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QFileDialog, QComboBox, QTextEdit
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont

from school_system.gui.windows.base_function_window import BaseFunctionWindow
from school_system.gui.dialogs.message_dialog import show_error_message, show_success_message
from school_system.config.logging import logger
from school_system.services.book_service import BookService
from school_system.gui.windows.book_window.utils import EXPORT_FORMATS
from school_system.gui.windows.book_window.utils.constants import (
    EXCEL_BOOK_IMPORT_COLUMNS,
    EXCEL_BOOK_EXPORT_COLUMNS,
    REQUIRED_FIELDS
)
from school_system.gui.windows.book_window.utils.class_utils import (
    normalize_class_name,
    validate_class_name
)


class BookImportExportWindow(BaseFunctionWindow):
    """Dedicated window for importing and exporting book data."""
    
    def __init__(self, parent=None, current_user: str = "", current_role: str = ""):
        """Initialize the book import/export window."""
        super().__init__("Book Import/Export", parent, current_user, current_role)
        
        self.book_service = BookService()
        
        # Setup content
        self.setup_content()
    
    def setup_content(self):
        """Setup the main content area."""
        # Create main content layout
        main_layout = self.create_flex_layout("column", False)
        main_layout.setContentsMargins(24, 24, 24, 24)
        main_layout.set_spacing(24)
        
        # Import section
        import_card = self._create_import_card()
        main_layout.add_widget(import_card)
        
        # Export section
        export_card = self._create_export_card()
        main_layout.add_widget(export_card)
        
        # Add to content
        self.add_layout_to_content(main_layout)
    
    def _create_import_card(self) -> QWidget:
        """Create the import card."""
        theme_manager = self.get_theme_manager()
        theme = theme_manager._themes[self.get_theme()]
        
        import_card = QWidget()
        import_card.setProperty("card", "true")
        import_card.setStyleSheet(f"""
            QWidget[card="true"] {{
                background-color: {theme["surface"]};
                border: 1px solid {theme["border"]};
                border-radius: 12px;
                padding: 24px;
            }}
        """)
        
        import_layout = QVBoxLayout(import_card)
        import_layout.setContentsMargins(24, 24, 24, 24)
        import_layout.setSpacing(16)
        
        # Title
        title_label = QLabel("Import Books")
        title_font = QFont("Segoe UI", 18, QFont.Weight.Medium)
        title_label.setFont(title_font)
        title_label.setStyleSheet(f"color: {theme["text"]}; margin-bottom: 8px;")
        import_layout.addWidget(title_label)
        
        # Required columns information
        columns_info = QVBoxLayout()
        columns_info.setSpacing(8)

        # Main description
        desc_label = QLabel("Import books from an Excel file (.xlsx).")
        desc_label.setWordWrap(True)
        desc_label.setStyleSheet(f"color: {theme["text_secondary"]}; margin-bottom: 8px;")
        columns_info.addWidget(desc_label)

        # Column information
        columns_label = QLabel("Excel File Columns:")
        columns_label.setStyleSheet(f"font-weight: 500; color: {theme["text"]}; font-size: 12px;")
        columns_info.addWidget(columns_label)

        # Show all columns with required/optional status
        for i, col in enumerate(EXCEL_BOOK_IMPORT_COLUMNS):
            is_required = col in REQUIRED_FIELDS
            status = "Required" if is_required else "Optional"
            color = theme["error"] if is_required else theme["text_secondary"]

            col_label = QLabel(f"• {col.replace('_', ' ')} ({status})")
            col_label.setStyleSheet(f"color: {color}; font-size: 11px; margin-left: 12px;")
            columns_info.addWidget(col_label)

        # Template generation button
        template_btn = self.create_button("📄 Generate Import Template", "outline")
        template_btn.setFixedWidth(200)
        template_btn.clicked.connect(self._generate_import_template)
        columns_info.addWidget(template_btn)

        import_layout.addLayout(columns_info)
        
        # File selection
        file_layout = QHBoxLayout()
        file_layout.setSpacing(12)
        
        self.import_file_label = QLabel("No file selected")
        self.import_file_label.setStyleSheet(f"color: {theme["text_secondary"]}; padding: 8px; border: 1px dashed {theme["border"]}; border-radius: 8px;")
        file_layout.addWidget(self.import_file_label, stretch=1)
        
        browse_btn = self.create_button("Browse...", "outline")
        browse_btn.clicked.connect(self._on_browse_import_file)
        file_layout.addWidget(browse_btn)
        
        import_layout.addLayout(file_layout)
        
        # Import button
        import_btn = self.create_button("Import Books", "primary")
        import_btn.clicked.connect(self._on_import_books)
        import_layout.addWidget(import_btn)
        
        return import_card
    
    def _create_export_card(self) -> QWidget:
        """Create the export card."""
        theme_manager = self.get_theme_manager()
        theme = theme_manager._themes[self.get_theme()]
        
        export_card = QWidget()
        export_card.setProperty("card", "true")
        export_card.setStyleSheet(f"""
            QWidget[card="true"] {{
                background-color: {theme["surface"]};
                border: 1px solid {theme["border"]};
                border-radius: 12px;
                padding: 24px;
            }}
        """)
        
        export_layout = QVBoxLayout(export_card)
        export_layout.setContentsMargins(24, 24, 24, 24)
        export_layout.setSpacing(16)
        
        # Title
        title_label = QLabel("Export Books")
        title_font = QFont("Segoe UI", 18, QFont.Weight.Medium)
        title_label.setFont(title_font)
        title_label.setStyleSheet(f"color: {theme["text"]}; margin-bottom: 8px;")
        export_layout.addWidget(title_label)
        
        # Description
        desc_label = QLabel("Export books to an Excel file (.xlsx) or CSV file (.csv).")
        desc_label.setWordWrap(True)
        desc_label.setStyleSheet(f"color: {theme["text_secondary"]}; margin-bottom: 12px;")
        export_layout.addWidget(desc_label)
        
        # Format selection
        format_layout = QVBoxLayout()
        format_label = QLabel("Export Format")
        format_label.setStyleSheet(f"font-weight: 500; color: {theme["text"]}; margin-bottom: 4px;")
        format_layout.addWidget(format_label)
        
        self.export_format_combo = QComboBox()
        self.export_format_combo.setFixedHeight(44)
        self.export_format_combo.addItems(EXPORT_FORMATS if EXPORT_FORMATS else ["Excel (.xlsx)", "CSV (.csv)"])
        format_layout.addWidget(self.export_format_combo)
        export_layout.addLayout(format_layout)
        
        # Export button
        export_btn = self.create_button("Export Books", "primary")
        export_btn.clicked.connect(self._on_export_books)
        export_layout.addWidget(export_btn)
        
        return export_card
    
    def _on_browse_import_file(self):
        """Handle browse import file button click."""
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Select Import File",
            "",
            "Excel Files (*.xlsx *.xls);;All Files (*)"
        )
        
        if file_path:
            self.import_file_path = file_path
            self.import_file_label.setText(file_path.split("/")[-1])
            self.import_file_label.setStyleSheet(f"""
                color: {self.get_theme_manager()._themes[self.get_theme()]["text"]};
                padding: 8px;
                border: 1px solid {self.get_theme_manager()._themes[self.get_theme()]["border"]};
                border-radius: 8px;
            """)
    
    def _on_import_books(self):
        """Handle import books button click."""
        if not hasattr(self, 'import_file_path') or not self.import_file_path:
            show_error_message("No File Selected", "Please select a file to import.", self)
            return

        try:
            # Define required columns for book import
            required_columns = ['book_number', 'title', 'author']

            # Import books from file using service method
            success, data, error_msg = self.book_service.import_books_from_excel_with_validation(
                self.import_file_path, required_columns
            )

            if not success:
                show_error_message("Import Error", error_msg, self)
                return

            # Process the imported data
            imported_books = []
            for book_data in data:
                try:
                    # Map Excel columns to model parameters
                    book_params = {
                        'book_number': str(book_data.get('book_number', '')).strip(),
                        'title': str(book_data.get('title', '')).strip(),
                        'author': str(book_data.get('author', '')).strip(),
                        'category': book_data.get('category'),
                        'isbn': book_data.get('isbn'),
                        'publication_date': book_data.get('publication_date'),
                        'subject': book_data.get('subject'),
                        'class_name': book_data.get('class'),
                        'book_condition': book_data.get('condition', 'New')
                    }

                    # Create book using service
                    created_book = self.book_service.create_book(book_params)
                    imported_books.append(created_book)

                except Exception as e:
                    logger.warning(f"Failed to create book from row: {book_data}, error: {e}")
                    continue

            if imported_books:
                show_success_message("Success",
                    f"Successfully imported {len(imported_books)} books from {self.import_file_path.split('/')[-1]}.",
                    self)
                logger.info(f"Imported {len(imported_books)} books from {self.import_file_path}")
            else:
                show_error_message("Import Warning",
                    "No books were imported. Please check your Excel file format and data.", self)

            # Clear file selection
            self.import_file_label.setText("No file selected")
            self.import_file_label.setStyleSheet(f"""
                color: {self.get_theme_manager()._themes[self.get_theme()]["text_secondary"]};
                padding: 8px;
                border: 1px dashed {self.get_theme_manager()._themes[self.get_theme()]["border"]};
                border-radius: 8px;
            """)
            if hasattr(self, 'import_file_path'):
                delattr(self, 'import_file_path')

        except Exception as e:
            logger.error(f"Error importing books: {e}")
            show_error_message("Error", f"Failed to import books: {str(e)}", self)
    
    def _on_export_books(self):
        """Handle export books button click."""
        format_text = self.export_format_combo.currentText()

        # Determine file extension and export method
        if "Excel" in format_text or ".xlsx" in format_text:
            file_ext = "xlsx"
            file_filter = "Excel Files (*.xlsx)"
            export_method = "excel"
        else:
            file_ext = "csv"
            file_filter = "CSV Files (*.csv)"
            export_method = "csv"

        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "Save Export File",
            f"books_export.{file_ext}",
            file_filter
        )

        if file_path:
            try:
                success = False
                if export_method == "excel":
                    success = self.book_service.export_books_to_excel(file_path)
                else:
                    # For CSV export, we'll need to implement this in the service
                    success = self.book_service.export_books_to_csv(file_path)

                if success:
                    show_success_message("Success", f"Books exported successfully to {file_path}.", self)
                    logger.info(f"Books exported to {file_path}")
                else:
                    show_error_message("Export Error", "Failed to export books. Please check the logs.", self)

            except Exception as e:
                logger.error(f"Error exporting books: {e}")
                show_error_message("Error", f"Failed to export books: {str(e)}", self)

    def _generate_import_template(self):
        """Generate an Excel template for book import."""
        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "Save Import Template",
            "book_import_template.xlsx",
            "Excel Files (*.xlsx)"
        )

        if file_path:
            try:
                # Define columns for the template
                columns = [
                    'book_number', 'title', 'author', 'category', 'isbn',
                    'publication_date', 'subject', 'class', 'condition'
                ]

                # Sample data
                sample_data = [
                    {
                        'book_number': 'MATH101',
                        'title': 'Advanced Mathematics',
                        'author': 'John Smith',
                        'category': 'Mathematics',
                        'isbn': '1234567890123',
                        'publication_date': '2024-01-15',
                        'subject': 'Mathematics',
                        'class': 'Form 4',
                        'condition': 'New'
                    },
                    {
                        'book_number': 'ENG201',
                        'title': 'English Literature',
                        'author': 'Jane Doe',
                        'category': 'English',
                        'isbn': '9876543210987',
                        'publication_date': '2023-09-01',
                        'subject': 'English',
                        'class': 'Form 3',
                        'condition': 'Good'
                    }
                ]

                # Generate template
                success = self.book_service.generate_book_import_template(file_path, columns, sample_data)

                if success:
                    show_success_message("Template Generated",
                        f"Import template saved to: {file_path}\n\nThe template includes sample data and all required columns.",
                        self)
                    logger.info(f"Book import template generated: {file_path}")
                else:
                    show_error_message("Template Error", "Failed to generate import template.", self)

            except Exception as e:
                logger.error(f"Error generating import template: {e}")
                show_error_message("Error", f"Failed to generate template: {str(e)}", self)
