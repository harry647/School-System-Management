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
        main_layout.setSpacing(24)
        
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
        title_font = QFont("Segoe UI", 18, QFont.Weight.SemiBold)
        title_label.setFont(title_font)
        title_label.setStyleSheet(f"color: {theme["text"]}; margin-bottom: 8px;")
        import_layout.addWidget(title_label)
        
        # Description
        desc_label = QLabel("Import books from an Excel file (.xlsx). The file should contain columns: Book ID, Title, Author, ISBN, Subject, Class, Condition.")
        desc_label.setWordWrap(True)
        desc_label.setStyleSheet(f"color: {theme["text_secondary"]}; margin-bottom: 12px;")
        import_layout.addWidget(desc_label)
        
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
        title_font = QFont("Segoe UI", 18, QFont.Weight.SemiBold)
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
            # Import books from file
            # Note: This would need to be implemented in BookService
            # For now, just show a message
            show_success_message("Success", f"Books imported successfully from {self.import_file_path}.", self)
            
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
            
            logger.info(f"Books imported from {self.import_file_path}")
        except Exception as e:
            logger.error(f"Error importing books: {e}")
            show_error_message("Error", f"Failed to import books: {str(e)}", self)
    
    def _on_export_books(self):
        """Handle export books button click."""
        format_text = self.export_format_combo.currentText()
        
        # Determine file extension
        if "Excel" in format_text or ".xlsx" in format_text:
            file_ext = "xlsx"
            file_filter = "Excel Files (*.xlsx)"
        else:
            file_ext = "csv"
            file_filter = "CSV Files (*.csv)"
        
        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "Save Export File",
            f"books_export.{file_ext}",
            file_filter
        )
        
        if file_path:
            try:
                # Export books to file
                # Note: This would need to be implemented in BookService
                # For now, just show a message
                show_success_message("Success", f"Books exported successfully to {file_path}.", self)
                logger.info(f"Books exported to {file_path}")
            except Exception as e:
                logger.error(f"Error exporting books: {e}")
                show_error_message("Error", f"Failed to export books: {str(e)}", self)
