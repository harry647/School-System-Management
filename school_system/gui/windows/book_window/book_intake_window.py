"""
Book Intake Window

Window for registering new books that arrive at the library.
Generates book numbers following the pattern: PUBLISHER_SHORT/SUBJECT_SHORT/CLASS_LEVEL/BOOK_SEQUENCE/YEAR
"""

from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
                             QLineEdit, QComboBox, QSpinBox, QGroupBox, QTextEdit,
                             QTableWidget, QTableWidgetItem, QHeaderView, QMessageBox, QFileDialog, QGridLayout)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont

from school_system.gui.windows.base_function_window import BaseFunctionWindow
from school_system.gui.dialogs.message_dialog import show_error_message, show_success_message
from school_system.config.logging import logger
from school_system.services.book_service import BookService
from school_system.services.settings_service import SettingsService
from school_system.services.import_export_service import ImportExportService
from school_system.gui.windows.book_window.utils.constants import BOOK_TYPES, STANDARD_CLASSES


class BookIntakeWindow(BaseFunctionWindow):
    """Window for registering new books arriving at the library."""

    def __init__(self, parent=None, current_user: str = "", current_role: str = ""):
        """Initialize the book intake window."""
        super().__init__("Book Intake Registration", parent, current_user, current_role)

        self.book_service = BookService()
        self.settings_service = SettingsService()
        self.import_export_service = ImportExportService()

        # Setup content
        self.setup_content()

    def setup_content(self):
        """Setup the book intake registration interface."""
        # Create main content layout
        main_layout = self.create_flex_layout("column", False)
        main_layout.set_margins(24, 24, 24, 24)
        main_layout.set_spacing(24)

        # Header section
        header_section = self._create_header_section()
        main_layout.add_widget(header_section)

        # Book details section
        details_section = self._create_book_details_section()
        main_layout.add_widget(details_section)

        # Book numbering section
        numbering_section = self._create_book_numbering_section()
        main_layout.add_widget(numbering_section)

        # Generated books preview
        preview_section = self._create_preview_section()
        main_layout.add_widget(preview_section)

        # Action buttons
        action_section = self._create_action_buttons_section()
        main_layout.add_widget(action_section)

        # Add to content
        self.add_layout_to_content(main_layout)

    def _create_header_section(self) -> QWidget:
        """Create the header section."""
        theme_manager = self.get_theme_manager()
        theme = theme_manager._themes[self.get_theme()]

        header = QWidget()
        layout = QVBoxLayout(header)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(8)

        header.setStyleSheet(f"""
            QWidget {{
                background-color: {theme["surface"]};
                border: 1px solid {theme["border"]};
                border-radius: 12px;
                padding: 20px;
            }}
        """)

        # Title
        title = QLabel("📚 New Book Intake Registration")
        title_font = QFont()
        title_font.setPointSize(20)
        title_font.setBold(True)
        title.setFont(title_font)
        title.setStyleSheet(f"color: {theme['text']}; margin-bottom: 8px;")
        layout.addWidget(title)

        # Description
        description = QLabel(
            "Register new books arriving at the library. Book numbers will be automatically generated "
            "following the pattern: PUBLISHER_SHORT/SUBJECT_SHORT/CLASS_LEVEL/SEQUENCE/YEAR"
        )
        description.setStyleSheet(f"color: {theme['text_secondary']};")
        description.setWordWrap(True)
        layout.addWidget(description)

        return header

    def _create_book_details_section(self) -> QWidget:
        """Create the book details input section."""
        theme_manager = self.get_theme_manager()
        theme = theme_manager._themes[self.get_theme()]

        section = QWidget()
        layout = QVBoxLayout(section)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(16)

        section.setStyleSheet(f"""
            QWidget {{
                background-color: {theme["surface"]};
                border: 1px solid {theme["border"]};
                border-radius: 12px;
                padding: 20px;
            }}
        """)

        # Section title
        title = QLabel("📖 Book Details")
        title_font = QFont()
        title_font.setPointSize(16)
        title_font.setBold(True)
        title.setFont(title_font)
        title.setStyleSheet(f"color: {theme['text']}; margin-bottom: 8px;")
        layout.addWidget(title)

        # Create form grid
        form_widget = QWidget()
        form_layout = QGridLayout(form_widget)
        form_layout.setContentsMargins(0, 0, 0, 0)
        form_layout.setSpacing(12)

        # Row 1: Publisher and Subject
        publisher_label = QLabel("Publisher:")
        publisher_label.setStyleSheet(f"color: {theme['text']}; font-weight: 500;")
        form_layout.addWidget(publisher_label, 0, 0)

        self.publisher_input = QLineEdit()
        self.publisher_input.setPlaceholderText("e.g., KLB, Oxford, Pearson")
        self.publisher_input.setStyleSheet(self._get_input_style(theme))
        form_layout.addWidget(self.publisher_input, 0, 1)

        subject_label = QLabel("Subject:")
        subject_label.setStyleSheet(f"color: {theme['text']}; font-weight: 500;")
        form_layout.addWidget(subject_label, 0, 2)

        self.subject_input = QLineEdit()
        self.subject_input.setPlaceholderText("e.g., English, Mathematics, Physics")
        self.subject_input.setStyleSheet(self._get_input_style(theme))
        form_layout.addWidget(self.subject_input, 0, 3)

        # Row 2: Class Level and Book Type
        class_label = QLabel("Class Level:")
        class_label.setStyleSheet(f"color: {theme['text']}; font-weight: 500;")
        form_layout.addWidget(class_label, 1, 0)

        self.class_combo = QComboBox()
        self.class_combo.addItems(STANDARD_CLASSES)
        self.class_combo.setStyleSheet(self._get_combo_style(theme))
        form_layout.addWidget(self.class_combo, 1, 1)

        book_type_label = QLabel("Book Type:")
        book_type_label.setStyleSheet(f"color: {theme['text']}; font-weight: 500;")
        form_layout.addWidget(book_type_label, 1, 2)

        self.book_type_combo = QComboBox()
        self.book_type_combo.addItems(BOOK_TYPES)
        self.book_type_combo.setStyleSheet(self._get_combo_style(theme))
        form_layout.addWidget(self.book_type_combo, 1, 3)

        # Row 3: Number of Books and Year
        count_label = QLabel("Number of Books:")
        count_label.setStyleSheet(f"color: {theme['text']}; font-weight: 500;")
        form_layout.addWidget(count_label, 2, 0)

        self.book_count_spinbox = QSpinBox()
        self.book_count_spinbox.setRange(1, 1000)
        self.book_count_spinbox.setValue(1)
        self.book_count_spinbox.setStyleSheet(self._get_input_style(theme))
        form_layout.addWidget(self.book_count_spinbox, 2, 1)

        year_label = QLabel("Year Acquired:")
        year_label.setStyleSheet(f"color: {theme['text']}; font-weight: 500;")
        form_layout.addWidget(year_label, 2, 2)

        self.year_spinbox = QSpinBox()
        self.year_spinbox.setRange(2000, 2100)
        self.year_spinbox.setValue(2026)  # Current year
        self.year_spinbox.setStyleSheet(self._get_input_style(theme))
        form_layout.addWidget(self.year_spinbox, 2, 3)

        # Row 4: Short Forms
        short_forms_label = QLabel("Short Forms:")
        short_forms_label.setStyleSheet(f"color: {theme['text']}; font-weight: 500;")
        short_forms_label.setToolTip("Short forms for publisher and subject (comma-separated)")
        form_layout.addWidget(short_forms_label, 3, 0)

        self.short_forms_input = QLineEdit()
        self.short_forms_input.setPlaceholderText("e.g., KLB/ENG, OXF/MATH")
        self.short_forms_input.setToolTip("Format: PUBLISHER_SHORT/SUBJECT_SHORT")
        self.short_forms_input.setStyleSheet(self._get_input_style(theme))
        form_layout.addWidget(self.short_forms_input, 3, 1, 1, 3)

        layout.addWidget(form_widget)

        # Preview button
        preview_button = self.create_button("🔍 Preview Book Numbers", "secondary")
        preview_button.clicked.connect(self._on_preview_books)
        layout.addWidget(preview_button)

        return section

    def _create_book_numbering_section(self) -> QWidget:
        """Create the book numbering explanation section."""
        theme_manager = self.get_theme_manager()
        theme = theme_manager._themes[self.get_theme()]

        section = QWidget()
        layout = QVBoxLayout(section)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(16)

        section.setStyleSheet(f"""
            QWidget {{
                background-color: {theme["surface"]};
                border: 1px solid {theme["border"]};
                border-radius: 12px;
                padding: 20px;
            }}
        """)

        # Section title
        title = QLabel("🔢 Book Numbering System")
        title_font = QFont()
        title_font.setPointSize(16)
        title_font.setBold(True)
        title.setFont(title_font)
        title.setStyleSheet(f"color: {theme['text']}; margin-bottom: 8px;")
        layout.addWidget(title)

        # Explanation
        explanation = QLabel(
            "Book numbers are generated automatically using this pattern:\n"
            "<b>PUBLISHER_SHORT/SUBJECT_SHORT/CLASS_LEVEL/SEQUENCE_NUMBER/YEAR</b>\n\n"
            "Examples:\n"
            "• KLB/ENG/4/1/26 - KLB English book for Form 4, first book, year 2026\n"
            "• OXF/MATH/3/5/25 - Oxford Mathematics book for Form 3, fifth book, year 2025\n"
            "• PH/KISW/2/12/26 - Phoenix Kiswahili book for Form 2, twelfth book, year 2026"
        )
        explanation.setStyleSheet(f"color: {theme['text_secondary']};")
        explanation.setWordWrap(True)
        layout.addWidget(explanation)

        return section

    def _create_preview_section(self) -> QWidget:
        """Create the generated books preview section."""
        theme_manager = self.get_theme_manager()
        theme = theme_manager._themes[self.get_theme()]

        section = QWidget()
        layout = QVBoxLayout(section)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(16)

        section.setStyleSheet(f"""
            QWidget {{
                background-color: {theme["surface"]};
                border: 1px solid {theme["border"]};
                border-radius: 12px;
                padding: 20px;
            }}
        """)

        # Section title
        title = QLabel("📋 Generated Books Preview & Export")
        title_font = QFont()
        title_font.setPointSize(16)
        title_font.setBold(True)
        title.setFont(title_font)
        title.setStyleSheet(f"color: {theme['text']}; margin-bottom: 8px;")
        layout.addWidget(title)

        # Description
        description = QLabel(
            "Preview the generated book numbers below. Use the export buttons to download "
            "the book numbers as Excel or PDF files for printing and writing on the books."
        )
        description.setStyleSheet(f"color: {theme['text_secondary']};")
        description.setWordWrap(True)
        layout.addWidget(description)

        # Create table
        self.books_table = QTableWidget()
        self.books_table.setColumnCount(5)
        self.books_table.setHorizontalHeaderLabels([
            "Book Number", "Title", "Author", "Subject", "Book Type"
        ])

        # Table styling
        self.books_table.setStyleSheet(f"""
            QTableWidget {{
                border: 1px solid {theme["border"]};
                border-radius: 8px;
                background-color: {theme["surface"]};
                gridline-color: {theme["border"]};
            }}

            QHeaderView::section {{
                background-color: {theme["surface"]};
                padding: 12px 16px;
                border: none;
                border-bottom: 2px solid {theme["border"]};
                font-weight: 600;
                font-size: 13px;
                color: {theme["text"]};
            }}

            QTableWidget::item {{
                padding: 8px 12px;
                border-bottom: 1px solid {theme["border"]};
                color: {theme["text"]};
            }}

            QTableWidget::item:selected {{
                background-color: {theme["primary"]};
                color: white;
            }}
        """)

        # Set column widths
        header = self.books_table.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)  # Book Number

        layout.addWidget(self.books_table)

        return section

    def _create_action_buttons_section(self) -> QWidget:
        """Create the action buttons section."""
        section = QWidget()
        layout = QHBoxLayout(section)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(16)

        # Primary actions
        save_button = self.create_button("💾 Register Books", "primary")
        save_button.clicked.connect(self._on_register_books)
        layout.addWidget(save_button)

        # Export actions
        export_section = QWidget()
        export_layout = QHBoxLayout(export_section)
        export_layout.setContentsMargins(0, 0, 0, 0)
        export_layout.setSpacing(8)

        export_label = QLabel("📥 Export:")
        export_layout.addWidget(export_label)

        excel_button = self.create_button("📊 Excel", "secondary")
        excel_button.clicked.connect(self._on_export_excel)
        excel_button.setToolTip("Download book numbers as Excel file")
        export_layout.addWidget(excel_button)

        pdf_button = self.create_button("📄 PDF", "secondary")
        pdf_button.clicked.connect(self._on_export_pdf)
        pdf_button.setToolTip("Download book numbers as PDF file")
        export_layout.addWidget(pdf_button)

        layout.addWidget(export_section)

        # Clear form button
        clear_button = self.create_button("🗑️ Clear Form", "secondary")
        clear_button.clicked.connect(self._on_clear_form)
        layout.addWidget(clear_button)

        layout.addStretch()

        return section

    def _get_combo_style(self, theme: dict) -> str:
        """Get consistent combo box styling."""
        return f"""
            QComboBox {{
                padding: 8px 12px;
                border: 1px solid {theme["border"]};
                border-radius: 6px;
                background-color: {theme["surface"]};
                color: {theme["text"]};
                min-height: 32px;
                font-size: 14px;
            }}

            QComboBox:hover {{
                border-color: {theme["text_secondary"]};
            }}

            QComboBox:focus {{
                border: 2px solid {theme["border_focus"]};
            }}
        """

    def _get_input_style(self, theme: dict) -> str:
        """Get consistent input field styling."""
        return f"""
            QLineEdit, QSpinBox {{
                padding: 8px 12px;
                border: 1px solid {theme["border"]};
                border-radius: 6px;
                background-color: {theme["surface"]};
                color: {theme["text"]};
                min-height: 32px;
                font-size: 14px;
            }}

            QLineEdit:hover, QSpinBox:hover {{
                border-color: {theme["text_secondary"]};
            }}

            QLineEdit:focus, QSpinBox:focus {{
                border: 2px solid {theme["border_focus"]};
            }}
        """

    def _on_preview_books(self):
        """Handle preview button click."""
        try:
            # Validate inputs
            if not self._validate_inputs():
                return

            # Get form data
            publisher = self.publisher_input.text().strip()
            subject = self.subject_input.text().strip()
            class_level = self.class_combo.currentText()
            book_type = self.book_type_combo.currentText()
            book_count = self.book_count_spinbox.value()
            year = self.year_spinbox.value()
            short_forms = self.short_forms_input.text().strip()

            # Parse short forms
            if "/" in short_forms:
                publisher_short, subject_short = short_forms.split("/", 1)
                publisher_short = publisher_short.strip()
                subject_short = subject_short.strip()
            else:
                show_error_message("Error", "Short forms must be in format: PUBLISHER_SHORT/SUBJECT_SHORT", self)
                return

            # Extract class level number
            class_num = self._extract_class_level(class_level)

            # Generate book numbers
            generated_books = []
            for i in range(1, book_count + 1):
                book_number = f"{publisher_short}/{subject_short}/{class_num}/{i}/{str(year)[-2:]}"

                # Create a sample book entry for preview
                book_data = {
                    "book_number": book_number,
                    "title": f"{subject} Book {i}",
                    "author": publisher,
                    "subject": subject,
                    "book_type": book_type
                }
                generated_books.append(book_data)

            # Update table
            self._update_books_table(generated_books)

            show_success_message("Success", f"Generated {book_count} book numbers for preview.", self)

        except Exception as e:
            logger.error(f"Error generating book preview: {str(e)}")
            show_error_message("Error", f"An error occurred: {str(e)}", self)

    def _on_register_books(self):
        """Handle register books button click."""
        try:
            # Validate inputs
            if not self._validate_inputs():
                return

            # Confirm action
            book_count = self.book_count_spinbox.value()
            reply = QMessageBox.question(
                self, "Confirm Registration",
                f"Are you sure you want to register {book_count} new books?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
            )

            if reply != QMessageBox.StandardButton.Yes:
                return

            # Get form data
            publisher = self.publisher_input.text().strip()
            subject = self.subject_input.text().strip()
            class_level = self.class_combo.currentText()
            book_type = self.book_type_combo.currentText()
            book_count = self.book_count_spinbox.value()
            year = self.year_spinbox.value()
            short_forms = self.short_forms_input.text().strip()

            # Parse short forms
            if "/" in short_forms:
                publisher_short, subject_short = short_forms.split("/", 1)
                publisher_short = publisher_short.strip()
                subject_short = subject_short.strip()
            else:
                show_error_message("Error", "Short forms must be in format: PUBLISHER_SHORT/SUBJECT_SHORT", self)
                return

            # Extract class level number
            class_num = self._extract_class_level(class_level)

            # Register books
            registered_count = 0
            errors = []

            for i in range(1, book_count + 1):
                try:
                    book_number = f"{publisher_short}/{subject_short}/{class_num}/{i}/{str(year)[-2:]}"

                    book_data = {
                        "book_number": book_number,
                        "title": f"{subject} Book",
                        "author": publisher,
                        "category": subject,  # Subject as category
                        "subject": subject,
                        "class": class_level,  # Use 'class' instead of 'class_name'
                        "book_type": book_type,
                        "available": True,
                        "book_condition": "new"
                    }

                    # Create book
                    book = self.book_service.create_book(book_data)
                    if book:
                        registered_count += 1
                    else:
                        errors.append(f"Failed to register book {book_number}")

                except Exception as e:
                    errors.append(f"Error registering book {i}: {str(e)}")

            # Show results
            if registered_count > 0:
                message = f"Successfully registered {registered_count} books."
                if errors:
                    message += f"\n\nErrors ({len(errors)}):\n" + "\n".join(errors[:5])  # Show first 5 errors
                show_success_message("Registration Complete", message, self)

                # Clear form on success
                self._on_clear_form()
            else:
                error_message = "Failed to register any books.\n\nErrors:\n" + "\n".join(errors)
                show_error_message("Registration Failed", error_message, self)

        except Exception as e:
            logger.error(f"Error registering books: {str(e)}")
            show_error_message("Error", f"An error occurred: {str(e)}", self)

    def _on_clear_form(self):
        """Handle clear form button click."""
        self.publisher_input.clear()
        self.subject_input.clear()
        self.class_combo.setCurrentIndex(0)
        self.book_type_combo.setCurrentIndex(0)
        self.book_count_spinbox.setValue(1)
        self.year_spinbox.setValue(2026)
        self.short_forms_input.clear()
        self.books_table.setRowCount(0)

    def _validate_inputs(self) -> bool:
        """Validate form inputs."""
        if not self.publisher_input.text().strip():
            show_error_message("Validation Error", "Publisher is required.", self)
            return False

        if not self.subject_input.text().strip():
            show_error_message("Validation Error", "Subject is required.", self)
            return False

        if not self.short_forms_input.text().strip():
            show_error_message("Validation Error", "Short forms are required.", self)
            return False

        short_forms = self.short_forms_input.text().strip()
        if "/" not in short_forms:
            show_error_message("Validation Error", "Short forms must be in format: PUBLISHER_SHORT/SUBJECT_SHORT", self)
            return False

        return True

    def _extract_class_level(self, class_name: str) -> int:
        """Extract numeric class level from class name."""
        import re
        match = re.search(r'\d+', class_name)
        return int(match.group()) if match else 1

    def _update_books_table(self, books_data: list):
        """Update the books preview table."""
        self.books_table.setRowCount(len(books_data))

        for row, book in enumerate(books_data):
            self.books_table.setItem(row, 0, QTableWidgetItem(book["book_number"]))
            self.books_table.setItem(row, 1, QTableWidgetItem(book["title"]))
            self.books_table.setItem(row, 2, QTableWidgetItem(book["author"]))
            self.books_table.setItem(row, 3, QTableWidgetItem(book.get("subject", "")))
            self.books_table.setItem(row, 4, QTableWidgetItem(book.get("book_type", "")))

    def _on_export_excel(self):
        """Handle Excel export button click."""
        try:
            # Get book data from table
            book_data = self._get_book_data_from_table()

            if not book_data:
                show_error_message("No Data", "No book data to export. Please preview books first.", self)
                return

            # Get file path from user
            file_path, _ = QFileDialog.getSaveFileName(
                self,
                "Save Book Numbers - Excel",
                f"book_numbers_{self.publisher_input.text().strip()}_{self.subject_input.text().strip()}.xlsx",
                "Excel Files (*.xlsx);;All Files (*)"
            )

            if not file_path:
                return

            # Export to Excel
            success = self.import_export_service.export_to_excel(book_data, file_path)

            if success:
                show_success_message("Export Successful", f"Book numbers exported to Excel:\n{file_path}", self)
            else:
                show_error_message("Export Failed", "Failed to export book numbers to Excel.", self)

        except Exception as e:
            logger.error(f"Error exporting to Excel: {str(e)}")
            show_error_message("Export Error", f"An error occurred: {str(e)}", self)

    def _on_export_pdf(self):
        """Handle PDF export button click."""
        try:
            # Get book data from table
            book_data = self._get_book_data_from_table()

            if not book_data:
                show_error_message("No Data", "No book data to export. Please preview books first.", self)
                return

            # Get file path from user
            file_path, _ = QFileDialog.getSaveFileName(
                self,
                "Save Book Numbers - PDF",
                f"book_numbers_{self.publisher_input.text().strip()}_{self.subject_input.text().strip()}.pdf",
                "PDF Files (*.pdf);;All Files (*)"
            )

            if not file_path:
                return

            # Export to PDF
            success = self.import_export_service.export_to_pdf(book_data, file_path)

            if success:
                show_success_message("Export Successful", f"Book numbers exported to PDF:\n{file_path}", self)
            else:
                show_error_message("Export Failed", "Failed to export book numbers to PDF.", self)

        except Exception as e:
            logger.error(f"Error exporting to PDF: {str(e)}")
            show_error_message("Export Error", f"An error occurred: {str(e)}", self)

    def _get_book_data_from_table(self) -> list:
        """Extract book data from the preview table."""
        book_data = []

        try:
            row_count = self.books_table.rowCount()
            if row_count == 0:
                return []

            for row in range(row_count):
                book_info = {
                    "Book_Number": self.books_table.item(row, 0).text() if self.books_table.item(row, 0) else "",
                    "Title": self.books_table.item(row, 1).text() if self.books_table.item(row, 1) else "",
                    "Author": self.books_table.item(row, 2).text() if self.books_table.item(row, 2) else "",
                    "Subject": self.books_table.item(row, 3).text() if self.books_table.item(row, 3) else "",
                    "Book_Type": self.books_table.item(row, 4).text() if self.books_table.item(row, 4) else "",
                    "Publisher": self.publisher_input.text().strip(),
                    "Class_Level": self.class_combo.currentText(),
                    "Year_Acquired": str(self.year_spinbox.value()),
                }
                book_data.append(book_info)

        except Exception as e:
            logger.error(f"Error extracting book data from table: {str(e)}")

        return book_data