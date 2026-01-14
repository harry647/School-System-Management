"""
Report management window for the School System Management application.

This module provides the report management interface for admin users (admin and librarian roles).
"""

from PyQt6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QLabel, QLineEdit, QPushButton, 
                            QHBoxLayout, QComboBox, QTabWidget, QTableWidget, QTableWidgetItem, 
                            QTextEdit, QSizePolicy, QFileDialog, QMessageBox)
from PyQt6.QtCore import Qt
from typing import Callable, Optional

from school_system.gui.base.base_window import BaseWindow
from school_system.gui.dialogs.message_dialog import show_error_message, show_success_message
from school_system.config.logging import logger
from school_system.services.report_service import ReportService
from school_system.core.exceptions import DatabaseException, ValidationError


class ReportWindow(BaseWindow):
    """Report management window for admin users."""

    def __init__(self, parent: QMainWindow, current_user: str, current_role: str):
        """
        Initialize the report window.

        Args:
            parent: The parent window
            current_user: The current logged-in username
            current_role: The current user's role
        """
        super().__init__("School System - Report Management", parent)

        self.parent = parent
        self.current_user = current_user
        self.current_role = current_role
        self.report_service = ReportService()

        # Check if user has admin privileges
        if self.current_role not in ["admin", "librarian"]:
            show_error_message("Access Denied", "You do not have permission to access report management.", self)
            self.close()
            return

        # Set minimum size
        self.setMinimumSize(1200, 800)

        # Apply modern web-style styling
        self._apply_modern_styling()

        # Initialize UI
        self._setup_widgets()

    def _setup_widgets(self):
        """Setup the report management widgets."""
        # Create tab widget for different sections
        tab_widget = QTabWidget()
        self.add_widget_to_content(tab_widget)

        # Book Reports Tab
        book_reports_tab = self._create_book_reports_tab()
        tab_widget.addTab(book_reports_tab, "Book Reports")

        # Student Reports Tab
        student_reports_tab = self._create_student_reports_tab()
        tab_widget.addTab(student_reports_tab, "Student Reports")

        # Import/Export Reports Tab
        import_export_tab = self._create_import_export_tab()
        tab_widget.addTab(import_export_tab, "Import/Export")

        # Custom Reports Tab
        custom_reports_tab = self._create_custom_reports_tab()
        tab_widget.addTab(custom_reports_tab, "Custom Reports")

    def _apply_modern_styling(self):
        """Apply modern web-style styling to the report window using theme system."""
        theme_manager = self.get_theme_manager()
        theme = theme_manager._themes[self.get_theme()]
        
        self.setStyleSheet(f"""
            /* Base styling */
            QWidget {{
                font-family: 'Segoe UI', -apple-system, BlinkMacSystemFont, 'Roboto', sans-serif;
                font-size: 14px;
                background-color: {theme["background"]};
                color: {theme["text"]};
            }}
            
            /* Window styling */
            ReportWindow {{
                background-color: {theme["background"]};
            }}
            
            /* Tab widget styling - modern web-style */
            QTabWidget::pane {{
                border: 1px solid {theme["border"]};
                background-color: {theme["surface"]};
                border-radius: 12px;
                padding: 20px;
            }}
            
            QTabBar::tab {{
                padding: 12px 24px;
                background-color: transparent;
                color: {theme["text_secondary"]};
                border: none;
                border-bottom: 2px solid transparent;
                font-size: 14px;
                font-weight: 500;
                margin-right: 4px;
            }}
            
            QTabBar::tab:hover {{
                color: {theme["text"]};
                background-color: {theme["surface_hover"]};
            }}
            
            QTabBar::tab:selected {{
                background-color: {theme["surface"]};
                color: {theme["primary"]};
                border-bottom: 2px solid {theme["primary"]};
            }}
            
            /* Button styling - using theme */
            QPushButton {{
                padding: 10px 20px;
                border-radius: 8px;
                border: 1px solid {theme["border"]};
                background-color: {theme["surface"]};
                color: {theme["text"]};
                min-height: 36px;
                font-size: 14px;
                font-weight: 500;
            }}
            
            QPushButton:hover {{
                background-color: {theme["surface_hover"]};
                border-color: {theme["text_secondary"]};
            }}
            
            /* Input field styling */
            QLineEdit, QComboBox, QTextEdit, QPlainTextEdit {{
                padding: 10px 14px;
                border: 1px solid {theme["border"]};
                border-radius: 8px;
                background-color: {theme["surface"]};
                color: {theme["text"]};
                min-height: 36px;
            }}
            
            QLineEdit:hover, QComboBox:hover, QTextEdit:hover, QPlainTextEdit:hover {{
                border-color: {theme["text_secondary"]};
            }}
            
            QLineEdit:focus, QComboBox:focus, QTextEdit:focus, QPlainTextEdit:focus {{
                border: 2px solid {theme["border_focus"]};
                background-color: {theme["surface"]};
            }}
            
            /* Table styling - modern web-style */
            QTableView, QTableWidget {{
                border: 1px solid {theme["border"]};
                border-radius: 12px;
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
                text-transform: uppercase;
                letter-spacing: 0.5px;
            }}
            
            QTableView::item:selected, QTableWidget::item:selected {{
                background-color: {theme["primary"]};
                color: white;
            }}
            
            QTableView::item:hover, QTableWidget::item:hover {{
                background-color: {theme["surface_hover"]};
            }}
            
            /* Card styling - modern web-style */
            QGroupBox {{
                border: 1px solid {theme["border"]};
                border-radius: 12px;
                background-color: {theme["surface"]};
                margin-top: 12px;
                padding: 20px;
            }}
            
            QGroupBox::title {{
                subcontrol-origin: margin;
                left: 16px;
                padding: 0 8px;
                color: {theme["text"]};
                font-weight: 600;
                font-size: 15px;
            }}
            
            QFrame[card="true"] {{
                background-color: {theme["surface"]};
                border: 1px solid {theme["border"]};
                border-radius: 12px;
                padding: 24px;
            }}
        """)

    def _create_book_reports_tab(self) -> QWidget:
        """Create the book reports tab."""
        tab = QWidget()
        layout = self.create_flex_layout("column", False)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.set_spacing(15)

        # Individual Book Report Section
        individual_section = self.create_card("Individual Book Report", "")
        individual_form = QWidget()
        individual_layout = self.create_flex_layout("column", False)
        individual_layout.set_spacing(10)

        # Book ID
        book_id_label = QLabel("Book ID:")
        individual_layout.add_widget(book_id_label)
        self.book_report_id_input = self.create_input("Enter book ID")
        individual_layout.add_widget(self.book_report_id_input)

        # Generate button
        generate_individual_button = self.create_button("Generate Book Report", "primary")
        generate_individual_button.clicked.connect(self._on_generate_book_report)
        individual_layout.add_widget(generate_individual_button)

        # Results display
        self.book_report_display = QTextEdit()
        self.book_report_display.setReadOnly(True)
        self.book_report_display.setMaximumHeight(200)
        individual_layout.add_widget(self.book_report_display)

        individual_form.setLayout(individual_layout._layout)
        individual_section.layout.addWidget(individual_form)
        layout.add_widget(individual_section)

        # All Books Report Section
        all_books_section = self.create_card("All Books Report", "")
        all_books_form = QWidget()
        all_books_layout = self.create_flex_layout("column", False)
        all_books_layout.set_spacing(10)

        # Generate all books button
        generate_all_button = self.create_button("Generate All Books Report", "primary")
        generate_all_button.clicked.connect(self._on_generate_all_books_report)
        all_books_layout.add_widget(generate_all_button)

        # Results display
        self.all_books_report_display = QTextEdit()
        self.all_books_report_display.setReadOnly(True)
        self.all_books_report_display.setMaximumHeight(200)
        all_books_layout.add_widget(self.all_books_report_display)

        all_books_form.setLayout(all_books_layout._layout)
        all_books_section.layout.addWidget(all_books_form)
        layout.add_widget(all_books_section)

        # Books Table
        books_table_section = self.create_card("Books Data", "")
        books_table_form = QWidget()
        books_table_layout = self.create_flex_layout("column", False)
        books_table_layout.set_spacing(10)

        # Refresh button
        refresh_books_button = self.create_button("Refresh Books Data", "secondary")
        refresh_books_button.clicked.connect(self._refresh_books_table)
        books_table_layout.add_widget(refresh_books_button)

        # Books table
        self.books_table = self.create_table(0, 8)
        self.books_table.setHorizontalHeaderLabels(["ID", "Book Number", "Title", "Author", "Category", "ISBN", "Available", "Condition"])
        books_table_layout.add_widget(self.books_table)

        books_table_form.setLayout(books_table_layout._layout)
        books_table_section.layout.addWidget(books_table_form)
        layout.add_widget(books_table_section)

        tab.setLayout(layout._layout)
        return tab

    def _create_student_reports_tab(self) -> QWidget:
        """Create the student reports tab."""
        tab = QWidget()
        layout = self.create_flex_layout("column", False)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.set_spacing(15)

        # Student Report Section
        student_section = self.create_card("Student Report", "")
        student_form = QWidget()
        student_layout = self.create_flex_layout("column", False)
        student_layout.set_spacing(10)

        # Student ID
        student_id_label = QLabel("Student ID:")
        student_layout.add_widget(student_id_label)
        self.student_report_id_input = self.create_input("Enter student ID")
        student_layout.add_widget(self.student_report_id_input)

        # Generate button
        generate_student_button = self.create_button("Generate Student Report", "primary")
        generate_student_button.clicked.connect(self._on_generate_student_report)
        student_layout.add_widget(generate_student_button)

        # Results display
        self.student_report_display = QTextEdit()
        self.student_report_display.setReadOnly(True)
        self.student_report_display.setMaximumHeight(200)
        student_layout.add_widget(self.student_report_display)

        student_form.setLayout(student_layout._layout)
        student_section.layout.addWidget(student_form)
        layout.add_widget(student_section)

        # All Students Report Section
        all_students_section = self.create_card("All Students Report", "")
        all_students_form = QWidget()
        all_students_layout = self.create_flex_layout("column", False)
        all_students_layout.set_spacing(10)

        # Generate all students button
        generate_all_students_button = self.create_button("Generate All Students Report", "primary")
        generate_all_students_button.clicked.connect(self._on_generate_all_students_report)
        all_students_layout.add_widget(generate_all_students_button)

        # Results display
        self.all_students_report_display = QTextEdit()
        self.all_students_report_display.setReadOnly(True)
        self.all_students_report_display.setMaximumHeight(200)
        all_students_layout.add_widget(self.all_students_report_display)

        all_students_form.setLayout(all_students_layout._layout)
        all_students_section.layout.addWidget(all_students_form)
        layout.add_widget(all_students_section)

        tab.setLayout(layout._layout)
        return tab

    def _create_import_export_tab(self) -> QWidget:
        """Create the import/export tab."""
        tab = QWidget()
        layout = self.create_flex_layout("column", False)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.set_spacing(15)

        # Export Reports Section
        export_section = self.create_card("Export Reports to Excel", "")
        export_form = QWidget()
        export_layout = self.create_flex_layout("column", False)
        export_layout.set_spacing(10)

        # Report Type
        report_type_label = QLabel("Report Type:")
        export_layout.add_widget(report_type_label)
        self.export_report_type_combo = QComboBox()
        self.export_report_type_combo.addItems(["Books", "Students", "Borrowed Books", "Overdue Books"])
        export_layout.add_widget(self.export_report_type_combo)

        # Export button
        export_button = self.create_button("Export Report to Excel", "primary")
        export_button.clicked.connect(self._on_export_report)
        export_layout.add_widget(export_button)

        export_form.setLayout(export_layout._layout)
        export_section.layout.addWidget(export_form)
        layout.add_widget(export_section)

        # Import Reports Section
        import_section = self.create_card("Import Reports from Excel", "")
        import_form = QWidget()
        import_layout = self.create_flex_layout("column", False)
        import_layout.set_spacing(10)

        # File selection
        self.import_file_label = QLabel("No file selected")
        import_layout.add_widget(self.import_file_label)

        # Browse button
        browse_button = self.create_button("Browse Excel File", "primary")
        browse_button.clicked.connect(self._on_browse_import_file)
        import_layout.add_widget(browse_button)

        # Import button
        import_button = self.create_button("Import Report", "secondary")
        import_button.clicked.connect(self._on_import_report)
        import_layout.add_widget(import_button)

        import_form.setLayout(import_layout._layout)
        import_section.layout.addWidget(import_form)
        layout.add_widget(import_section)

        tab.setLayout(layout._layout)
        return tab

    def _create_custom_reports_tab(self) -> QWidget:
        """Create the custom reports tab."""
        tab = QWidget()
        layout = self.create_flex_layout("column", False)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.set_spacing(15)

        # Custom Report Generator Section
        custom_section = self.create_card("Custom Report Generator", "")
        custom_form = QWidget()
        custom_layout = self.create_flex_layout("column", False)
        custom_layout.set_spacing(10)

        # Report Type
        custom_report_type_label = QLabel("Report Type:")
        custom_layout.add_widget(custom_report_type_label)
        self.custom_report_type_input = self.create_input("Enter report type (e.g., 'library_usage')")
        custom_layout.add_widget(self.custom_report_type_input)

        # Parameters (JSON format)
        parameters_label = QLabel("Parameters (JSON format):")
        custom_layout.add_widget(parameters_label)
        self.custom_parameters_input = QTextEdit()
        self.custom_parameters_input.setPlaceholderText('{"limit": 10, "category": "fiction"}')
        self.custom_parameters_input.setMaximumHeight(100)
        custom_layout.add_widget(self.custom_parameters_input)

        # Generate button
        generate_custom_button = self.create_button("Generate Custom Report", "primary")
        generate_custom_button.clicked.connect(self._on_generate_custom_report)
        custom_layout.add_widget(generate_custom_button)

        # Results display
        self.custom_report_display = QTextEdit()
        self.custom_report_display.setReadOnly(True)
        self.custom_report_display.setMaximumHeight(200)
        custom_layout.add_widget(self.custom_report_display)

        custom_form.setLayout(custom_layout._layout)
        custom_section.layout.addWidget(custom_form)
        layout.add_widget(custom_section)

        tab.setLayout(layout._layout)
        return tab

    # Event handlers
    def _on_generate_book_report(self):
        """Handle generate book report button click."""
        try:
            book_id = int(self.book_report_id_input.text().strip())
            report_data = self.report_service.get_book_report(book_id)
            
            if report_data and 'book' in report_data:
                book = report_data['book']
                report_text = f"Book Report - ID: {book.id}\n\n"
                report_text += f"Title: {book.title}\n"
                report_text += f"Author: {book.author}\n"
                report_text += f"Book Number: {book.book_number}\n"
                report_text += f"Category: {book.category or 'N/A'}\n"
                report_text += f"ISBN: {book.isbn or 'N/A'}\n"
                report_text += f"Publication Date: {book.publication_date or 'N/A'}\n"
                report_text += f"Available: {'Yes' if book.available else 'No'}\n"
                report_text += f"Condition: {book.book_condition or 'N/A'}\n"
                
                self.book_report_display.setText(report_text)
                show_success_message("Success", "Book report generated successfully", self)
            else:
                show_error_message("Error", "Book not found", self)
                
        except ValueError:
            show_error_message("Error", "Invalid book ID", self)
        except Exception as e:
            show_error_message("Error", f"Failed to generate book report: {str(e)}", self)

    def _on_generate_all_books_report(self):
        """Handle generate all books report button click."""
        try:
            report_data = self.report_service.get_all_books_report()
            
            if report_data:
                report_text = "All Books Report\n\n"
                report_text += f"Total Books: {len(report_data)}\n\n"
                
                for i, book_data in enumerate(report_data, 1):
                    book = book_data['book']
                    report_text += f"{i}. {book.title} by {book.author} (ID: {book.id})\n"
                
                self.all_books_report_display.setText(report_text)
                show_success_message("Success", "All books report generated successfully", self)
            else:
                show_error_message("Error", "No books found", self)
                
        except Exception as e:
            show_error_message("Error", f"Failed to generate all books report: {str(e)}", self)

    def _on_generate_student_report(self):
        """Handle generate student report button click."""
        try:
            student_id = self.student_report_id_input.text().strip()
            # This would be implemented with actual student service
            report_text = f"Student Report - ID: {student_id}\n\n"
            report_text += "This feature would show detailed student information and borrowing history.\n"
            report_text += "Implementation would use StudentService to fetch student data."
            
            self.student_report_display.setText(report_text)
            show_success_message("Success", "Student report generated successfully", self)
                
        except Exception as e:
            show_error_message("Error", f"Failed to generate student report: {str(e)}", self)

    def _on_generate_all_students_report(self):
        """Handle generate all students report button click."""
        try:
            # This would be implemented with actual student service
            report_text = "All Students Report\n\n"
            report_text += "This feature would show a summary of all students.\n"
            report_text += "Implementation would use StudentService to fetch all student data."
            
            self.all_students_report_display.setText(report_text)
            show_success_message("Success", "All students report generated successfully", self)
                
        except Exception as e:
            show_error_message("Error", f"Failed to generate all students report: {str(e)}", self)

    def _refresh_books_table(self):
        """Refresh the books table."""
        try:
            books = self.report_service.book_repository.get_all()
            self._populate_books_table(books)
            show_success_message("Success", "Books data refreshed successfully", self)
        except Exception as e:
            show_error_message("Error", f"Failed to refresh books data: {str(e)}", self)

    def _populate_books_table(self, books):
        """Populate the books table with data."""
        self.books_table.setRowCount(0)
        
        for book in books:
            row_position = self.books_table.rowCount()
            self.books_table.insertRow(row_position)
            
            self.books_table.setItem(row_position, 0, QTableWidgetItem(str(book.id)))
            self.books_table.setItem(row_position, 1, QTableWidgetItem(book.book_number))
            self.books_table.setItem(row_position, 2, QTableWidgetItem(book.title))
            self.books_table.setItem(row_position, 3, QTableWidgetItem(book.author))
            self.books_table.setItem(row_position, 4, QTableWidgetItem(book.category or ""))
            self.books_table.setItem(row_position, 5, QTableWidgetItem(book.isbn or ""))
            self.books_table.setItem(row_position, 6, QTableWidgetItem("Yes" if book.available else "No"))
            self.books_table.setItem(row_position, 7, QTableWidgetItem(book.book_condition or ""))

    def _on_export_report(self):
        """Handle export report button click."""
        try:
            report_type = self.export_report_type_combo.currentText()
            
            # Get report data based on type
            if report_type == "Books":
                report_data = self.report_service.get_all_books_report()
            elif report_type == "Students":
                # This would use student service
                report_data = []
                show_error_message("Info", "Student reports would be implemented with StudentService", self)
                return
            elif report_type == "Borrowed Books":
                # This would use book service
                report_data = []
                show_error_message("Info", "Borrowed books reports would be implemented with BookService", self)
                return
            elif report_type == "Overdue Books":
                # This would use book service
                report_data = []
                show_error_message("Info", "Overdue books reports would be implemented with BookService", self)
                return
            else:
                report_data = []
            
            if report_data:
                file_dialog = QFileDialog()
                file_path, _ = file_dialog.getSaveFileName(self, "Save Report", f"{report_type.lower()}_report.xlsx", "Excel Files (*.xlsx)")
                
                if file_path:
                    success = self.report_service.export_report_to_excel(report_data, file_path)
                    if success:
                        show_success_message("Success", f"{report_type} report exported successfully", self)
                    else:
                        show_error_message("Error", "Failed to export report", self)
            else:
                show_error_message("Error", "No data available for export", self)
                
        except Exception as e:
            show_error_message("Error", f"Failed to export report: {str(e)}", self)

    def _on_browse_import_file(self):
        """Handle browse import file button click."""
        file_dialog = QFileDialog()
        file_path, _ = file_dialog.getOpenFileName(self, "Select Excel File", "", "Excel Files (*.xlsx *.xls)")
        
        if file_path:
            self.import_file_label.setText(file_path)
            self.import_file_path = file_path

    def _on_import_report(self):
        """Handle import report button click."""
        try:
            if not hasattr(self, 'import_file_path'):
                show_error_message("Error", "Please select a file first", self)
                return
                
            report_data = self.report_service.import_report_from_excel(self.import_file_path)
            
            if report_data:
                show_success_message("Success", f"Imported {len(report_data)} report records successfully", self)
                # Refresh any relevant data
                self._refresh_books_table()
            else:
                show_error_message("Error", "No data imported or file was empty", self)
                
        except Exception as e:
            show_error_message("Error", f"Import failed: {str(e)}", self)

    def _on_generate_custom_report(self):
        """Handle generate custom report button click."""
        try:
            report_type = self.custom_report_type_input.text().strip()
            parameters_text = self.custom_parameters_input.toPlainText().strip()
            
            # Parse parameters
            parameters = {}
            if parameters_text:
                import json
                try:
                    parameters = json.loads(parameters_text)
                except json.JSONDecodeError:
                    show_error_message("Error", "Invalid JSON format for parameters", self)
                    return
            
            # Generate custom report
            report_data = self.report_service.generate_report(report_type, parameters)
            
            if report_data:
                report_text = f"Custom Report - {report_type}\n\n"
                report_text += f"Parameters: {parameters}\n\n"
                report_text += f"Report Data: {report_data}"
                
                self.custom_report_display.setText(report_text)
                show_success_message("Success", "Custom report generated successfully", self)
            else:
                show_error_message("Error", "Failed to generate custom report", self)
                
        except Exception as e:
            show_error_message("Error", f"Failed to generate custom report: {str(e)}", self)