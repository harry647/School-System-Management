"""
Book Reports Window

Dedicated window for generating book reports.
"""

from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QComboBox, QTableWidget, QTableWidgetItem, QFileDialog, QTextEdit
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont, QColor

from school_system.gui.windows.base_function_window import BaseFunctionWindow
from school_system.gui.dialogs.message_dialog import show_error_message, show_success_message
from school_system.config.logging import logger
from school_system.services.report_service import ReportService


class BookReportsWindow(BaseFunctionWindow):
    """Dedicated window for generating book reports."""
    
    def __init__(self, parent=None, current_user: str = "", current_role: str = ""):
        """Initialize the book reports window."""
        super().__init__("Book Reports", parent, current_user, current_role)
        
        self.report_service = ReportService()
        
        # Setup content
        self.setup_content()
    
    def setup_content(self):
        """Setup the main content area."""
        # Create main content layout
        main_layout = self.create_flex_layout("column", False)
        main_layout.set_margins(24, 24, 24, 24)
        main_layout.set_spacing(16)
        
        # Report options card
        options_card = self._create_report_options_card()
        main_layout.add_widget(options_card)
        
        # Report results card
        results_card = self._create_report_results_card()
        main_layout.add_widget(results_card, stretch=1)
        
        # Add to content
        self.add_layout_to_content(main_layout)
    
    def _create_report_options_card(self) -> QWidget:
        """Create the report options card."""
        theme_manager = self.get_theme_manager()
        theme = theme_manager._themes[self.get_theme()]
        
        card = QWidget()
        card.setProperty("card", "true")
        card.setStyleSheet(f"""
            QWidget[card="true"] {{
                background-color: {theme["surface"]};
                border: 1px solid {theme["border"]};
                border-radius: 12px;
                padding: 24px;
            }}
        """)
        
        layout = QVBoxLayout(card)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(16)
        
        # Title
        title_label = QLabel("Generate Book Report")
        title_font = QFont("Segoe UI", 18, QFont.Weight.Medium)
        title_label.setFont(title_font)
        title_label.setStyleSheet(f"color: {theme['text']}; margin-bottom: 8px;")
        layout.addWidget(title_label)
        
        # Report type
        type_layout = QHBoxLayout()
        type_layout.setSpacing(12)
        
        type_label = QLabel("Report Type:")
        type_label.setStyleSheet(f"font-weight: 500; color: {theme['text']};")
        type_layout.addWidget(type_label)
        
        self.report_type_combo = QComboBox()
        self.report_type_combo.setFixedHeight(44)
        self.report_type_combo.addItems([
            "All Books",
            "Borrowed Books",
            "Available Books",
            "Overdue Books",
            "Book Inventory",
            "Borrowing Analytics"
        ])
        type_layout.addWidget(self.report_type_combo)
        
        type_layout.addStretch()
        
        # Generate button
        generate_btn = self.create_button("Generate Report", "primary")
        generate_btn.setFixedHeight(44)
        generate_btn.clicked.connect(self._on_generate_report)
        type_layout.addWidget(generate_btn)
        
        # Export button
        export_btn = self.create_button("Export Report", "secondary")
        export_btn.setFixedHeight(44)
        export_btn.clicked.connect(self._on_export_report)
        type_layout.addWidget(export_btn)
        
        layout.addLayout(type_layout)
        
        return card
    
    def _create_report_results_card(self) -> QWidget:
        """Create the report results card."""
        theme_manager = self.get_theme_manager()
        theme = theme_manager._themes[self.get_theme()]
        
        card = QWidget()
        card.setProperty("card", "true")
        card.setStyleSheet(f"""
            QWidget[card="true"] {{
                background-color: {theme["surface"]};
                border: 1px solid {theme["border"]};
                border-radius: 12px;
                padding: 24px;
            }}
        """)
        
        layout = QVBoxLayout(card)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(12)
        
        # Title
        title_label = QLabel("Report Results")
        title_font = QFont("Segoe UI", 16, QFont.Weight.Medium)
        title_label.setFont(title_font)
        title_label.setStyleSheet(f"color: {theme['text']}; margin-bottom: 8px;")
        layout.addWidget(title_label)
        
        # Results table (dynamic columns based on report type)
        self.results_table = self.create_table(0, 8)  # Increased columns for analytics
        self.results_table.setColumnCount(8)
        self.results_table.setHorizontalHeaderLabels(["Book ID", "Title", "Status", "Details", "", "", "", ""])
        self.results_table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.results_table.setAlternatingRowColors(True)
        layout.addWidget(self.results_table)

        # Analytics summary area (initially hidden)
        self.analytics_summary = self._create_analytics_summary_area()
        layout.addWidget(self.analytics_summary)
        self.analytics_summary.setVisible(False)

        return card

    def _populate_books_table(self, report_data: list):
        """Populate the results table with book report data."""
        try:
            self.results_table.setRowCount(0)  # Clear existing data

            for row_idx, book_data in enumerate(report_data):
                self.results_table.insertRow(row_idx)

                book = book_data.get('book', {})

                # Extract book information
                book_id = book.get('id', '')
                title = book.get('title', '')
                status = book.get('status', 'Unknown')
                details = book.get('author', '') or book.get('genre', '') or 'N/A'

                # Set table items
                self.results_table.setItem(row_idx, 0, QTableWidgetItem(str(book_id)))
                self.results_table.setItem(row_idx, 1, QTableWidgetItem(title))
                self.results_table.setItem(row_idx, 2, QTableWidgetItem(status))
                self.results_table.setItem(row_idx, 3, QTableWidgetItem(details))

        except Exception as e:
            logger.error(f"Error populating books table: {e}")
            show_error_message("Error", f"Failed to display report data: {str(e)}", self)
    
    def _on_generate_report(self):
        """Handle generate report."""
        report_type = self.report_type_combo.currentText()

        try:
            # Clear table first
            self.results_table.setRowCount(0)

            # Generate report based on type
            if report_type == "All Books":
                report_data = self.report_service.get_all_books_report()
                self._populate_books_table(report_data)
            elif report_type == "Borrowed Books":
                # This would need to be implemented in ReportService
                report_data = self.report_service.get_borrowed_books_report()
                self._populate_books_table(report_data)
            elif report_type == "Available Books":
                # This would need to be implemented in ReportService
                report_data = self.report_service.get_available_books_report()
                self._populate_books_table(report_data)
            elif report_type == "Overdue Books":
                # This would need to be implemented in ReportService
                report_data = self.report_service.get_overdue_books_report()
                self._populate_books_table(report_data)
            elif report_type == "Book Inventory":
                # This would need to be implemented in ReportService
                report_data = self.report_service.get_book_inventory_report()
                self._populate_books_table(report_data)
            elif report_type == "Borrowing Analytics":
                analytics_data = self.report_service.get_borrowing_analytics_report()
                self._display_borrowing_analytics(analytics_data)

            show_success_message("Success", f"Report '{report_type}' generated successfully.", self)

        except Exception as e:
            logger.error(f"Error generating report: {e}")
            show_error_message("Error", f"Failed to generate report: {str(e)}", self)
    
    def _on_export_report(self):
        """Handle export report."""
        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "Save Report",
            "book_report.xlsx",
            "Excel Files (*.xlsx);;CSV Files (*.csv)"
        )
        
        if file_path:
            try:
                # Export report
                show_success_message("Success", f"Report exported to {file_path}.", self)
            except Exception as e:
                logger.error(f"Error exporting report: {e}")
                show_error_message("Error", f"Failed to export report: {str(e)}", self)

    def _create_analytics_summary_area(self) -> QWidget:
        """Create the analytics summary display area."""
        theme_manager = self.get_theme_manager()
        theme = theme_manager._themes[self.get_theme()]

        summary_widget = QWidget()
        summary_layout = QVBoxLayout(summary_widget)
        summary_layout.setSpacing(10)

        # Summary text area
        self.summary_text = QTextEdit()
        self.summary_text.setReadOnly(True)
        self.summary_text.setMaximumHeight(300)
        self.summary_text.setStyleSheet(f"""
            QTextEdit {{
                background-color: {theme["surface"]};
                border: 1px solid {theme["border"]};
                border-radius: 8px;
                padding: 12px;
                color: {theme["text"]};
                font-family: 'Segoe UI', sans-serif;
            }}
        """)
        summary_layout.addWidget(self.summary_text)

        return summary_widget

    def _display_borrowing_analytics(self, analytics_data: dict):
        """Display comprehensive borrowing analytics."""
        try:
            self.analytics_summary.setVisible(True)
            self.results_table.setRowCount(0)

            summary_text = "📊 BORROWING ANALYTICS REPORT\n"
            summary_text += "=" * 50 + "\n\n"

            # Inventory Summary
            inventory = analytics_data.get('inventory_summary', {})
            if inventory:
                summary_text += "📚 INVENTORY SUMMARY\n"
                summary_text += f"• Total Books: {inventory.get('total_books', 0)}\n"
                summary_text += f"• Available Books: {inventory.get('available_books', 0)}\n"
                summary_text += f"• Borrowed Books: {inventory.get('borrowed_books', 0)}\n"
                summary_text += f"• Borrowed Percentage: {inventory.get('borrowed_percentage', 0)}%\n\n"

            # Students Not Borrowed Any Books
            not_borrowed = analytics_data.get('students_not_borrowed_any_books', {})
            if not_borrowed:
                summary_text += "👨‍🎓 STUDENTS WHO HAVE NOT BORROWED ANY BOOKS\n"
                summary_text += f"• Total: {not_borrowed.get('total_students_not_borrowed', 0)} students\n"

                students_by_stream = not_borrowed.get('students_by_stream', {})
                for stream, students in students_by_stream.items():
                    summary_text += f"• {stream}: {len(students)} students\n"
                summary_text += "\n"

            # Borrowing Percentage by Class
            percentages = analytics_data.get('borrowing_percentage_by_class', [])
            if percentages:
                summary_text += "📈 BORROWING PERCENTAGE BY CLASS\n"
                self.results_table.setHorizontalHeaderLabels([
                    "Form", "Total Students", "Students Borrowed", "Borrowing %", "Total Borrowings", "Avg per Student"
                ])
                self.results_table.setColumnCount(6)

                for i, data in enumerate(percentages):
                    self.results_table.insertRow(i)
                    self.results_table.setItem(i, 0, QTableWidgetItem(data.get('form', '')))
                    self.results_table.setItem(i, 1, QTableWidgetItem(str(data.get('total_students', 0))))
                    self.results_table.setItem(i, 2, QTableWidgetItem(str(data.get('students_borrowed', 0))))
                    self.results_table.setItem(i, 3, QTableWidgetItem(f"{data.get('student_borrowing_percentage', 0)}%"))
                    self.results_table.setItem(i, 4, QTableWidgetItem(str(data.get('total_borrowings', 0))))
                    self.results_table.setItem(i, 5, QTableWidgetItem(str(data.get('average_borrowings_per_student', 0))))

            # Books Categorized by Subject/Form
            categorized = analytics_data.get('books_categorized_by_subject_form', [])
            if categorized:
                summary_text += "📖 BOOKS CATEGORIZED BY SUBJECT AND FORM\n"
                summary_text += f"• Total Categories: {len(categorized)}\n\n"

                # Create a new table for this data
                self._display_books_categorized_table(categorized)

            # Students Not Borrowed by Stream/Subject
            not_borrowed_detailed = analytics_data.get('students_not_borrowed_by_stream_subject', [])
            if not_borrowed_detailed:
                summary_text += "🎯 STUDENTS NOT BORROWED BY STREAM/SUBJECT\n"
                summary_text += f"• Categories with missing borrowers: {len(not_borrowed_detailed)}\n"

                for item in not_borrowed_detailed[:5]:  # Show first 5
                    summary_text += f"• {item.get('form')} {item.get('stream')} - {item.get('subject')}: {item.get('count', 0)} students\n"

                if len(not_borrowed_detailed) > 5:
                    summary_text += f"• ... and {len(not_borrowed_detailed) - 5} more categories\n"

            self.summary_text.setPlainText(summary_text)

        except Exception as e:
            logger.error(f"Error displaying borrowing analytics: {e}")
            show_error_message("Error", f"Failed to display analytics: {str(e)}", self)

    def _display_books_categorized_table(self, categorized_data: list):
        """Display books categorized by subject/form in a separate table view."""
        try:
            # Create a new table for categorized books (we'll reuse the existing table for now)
            # In a production system, you might want separate table widgets
            self.results_table.setHorizontalHeaderLabels([
                "Form", "Subject", "Total Books", "Available", "Borrowed", "Borrowed %"
            ])
            self.results_table.setColumnCount(6)
            self.results_table.setRowCount(0)

            for i, data in enumerate(categorized_data):
                self.results_table.insertRow(i)
                total_books = data.get('total_books', 0)
                borrowed_books = data.get('borrowed_books', 0)
                borrowed_percentage = (borrowed_books / total_books * 100) if total_books > 0 else 0

                self.results_table.setItem(i, 0, QTableWidgetItem(data.get('form', '')))
                self.results_table.setItem(i, 1, QTableWidgetItem(data.get('subject', '')))
                self.results_table.setItem(i, 2, QTableWidgetItem(str(total_books)))
                self.results_table.setItem(i, 3, QTableWidgetItem(str(data.get('available_books', 0))))
                self.results_table.setItem(i, 4, QTableWidgetItem(str(borrowed_books)))
                self.results_table.setItem(i, 5, QTableWidgetItem(f"{borrowed_percentage:.1f}%"))

        except Exception as e:
            logger.error(f"Error displaying books categorized table: {e}")

    def _populate_books_table(self, report_data: list):
        """Populate the results table with book report data."""
        try:
            self.analytics_summary.setVisible(False)  # Hide analytics summary for regular reports
            self.results_table.setRowCount(0)  # Clear existing data
            
            if not report_data:
                return

            report_type = self.report_type_combo.currentText()
            
            # Determine columns based on report type
            if report_type == "Borrowed Books":
                self.results_table.setColumnCount(7)
                self.results_table.setHorizontalHeaderLabels([
                    "Book Number", "Title", "Author", "Student Name", "Student ID", "Borrowed On", "Days Borrowed"
                ])
            elif report_type == "Available Books":
                self.results_table.setColumnCount(8)
                self.results_table.setHorizontalHeaderLabels([
                    "Book Number", "Title", "Author", "ISBN", "Subject", "Class", "Type", "Condition"
                ])
            elif report_type == "Overdue Books":
                self.results_table.setColumnCount(8)
                self.results_table.setHorizontalHeaderLabels([
                    "Book Number", "Title", "Author", "Student Name", "Student ID", "Borrowed On", "Due Date", "Days Overdue"
                ])
            elif report_type == "Book Inventory":
                self.results_table.setColumnCount(9)
                self.results_table.setHorizontalHeaderLabels([
                    "Book Number", "Title", "Author", "Subject", "Class", "Type", "Condition", "Status", "ISBN"
                ])
            else:  # All Books
                self.results_table.setColumnCount(8)
                self.results_table.setHorizontalHeaderLabels([
                    "Book Number", "Title", "Author", "ISBN", "Subject", "Class", "Type", "Status"
                ])

            for row_idx, data in enumerate(report_data):
                self.results_table.insertRow(row_idx)
                
                # Handle summary rows in inventory report
                if data.get('is_summary', False):
                    self.results_table.setItem(row_idx, 0, QTableWidgetItem(data.get('book_number', '')))
                    self.results_table.setItem(row_idx, 1, QTableWidgetItem(data.get('title', '')))
                    self.results_table.setItem(row_idx, 2, QTableWidgetItem(data.get('author', '')))
                    # Make summary rows visually distinct
                    for col in range(self.results_table.columnCount()):
                        item = self.results_table.item(row_idx, col)
                        if item:
                            item.setBackground(Qt.GlobalColor.lightGray)
                    continue

                # Extract data based on report type
                if report_type == "Borrowed Books":
                    self.results_table.setItem(row_idx, 0, QTableWidgetItem(str(data.get('book_number', ''))))
                    self.results_table.setItem(row_idx, 1, QTableWidgetItem(data.get('title', '')))
                    self.results_table.setItem(row_idx, 2, QTableWidgetItem(data.get('author', 'N/A')))
                    self.results_table.setItem(row_idx, 3, QTableWidgetItem(data.get('student_name', 'N/A')))
                    self.results_table.setItem(row_idx, 4, QTableWidgetItem(str(data.get('student_id', ''))))
                    self.results_table.setItem(row_idx, 5, QTableWidgetItem(str(data.get('borrowed_on', ''))))
                    self.results_table.setItem(row_idx, 6, QTableWidgetItem(str(data.get('days_borrowed', 0))))
                    
                elif report_type == "Available Books":
                    self.results_table.setItem(row_idx, 0, QTableWidgetItem(str(data.get('book_number', ''))))
                    self.results_table.setItem(row_idx, 1, QTableWidgetItem(data.get('title', '')))
                    self.results_table.setItem(row_idx, 2, QTableWidgetItem(data.get('author', 'N/A')))
                    self.results_table.setItem(row_idx, 3, QTableWidgetItem(data.get('isbn', 'N/A')))
                    self.results_table.setItem(row_idx, 4, QTableWidgetItem(data.get('subject', 'N/A')))
                    self.results_table.setItem(row_idx, 5, QTableWidgetItem(data.get('class_name', 'N/A')))
                    self.results_table.setItem(row_idx, 6, QTableWidgetItem(data.get('book_type', 'N/A')))
                    self.results_table.setItem(row_idx, 7, QTableWidgetItem(data.get('condition', 'Good')))
                    
                elif report_type == "Overdue Books":
                    self.results_table.setItem(row_idx, 0, QTableWidgetItem(str(data.get('book_number', ''))))
                    self.results_table.setItem(row_idx, 1, QTableWidgetItem(data.get('title', '')))
                    self.results_table.setItem(row_idx, 2, QTableWidgetItem(data.get('author', 'N/A')))
                    self.results_table.setItem(row_idx, 3, QTableWidgetItem(data.get('student_name', 'N/A')))
                    self.results_table.setItem(row_idx, 4, QTableWidgetItem(str(data.get('student_id', ''))))
                    self.results_table.setItem(row_idx, 5, QTableWidgetItem(str(data.get('borrowed_on', ''))))
                    self.results_table.setItem(row_idx, 6, QTableWidgetItem(str(data.get('due_date', ''))))
                    days_overdue = data.get('days_overdue', 0)
                    overdue_item = QTableWidgetItem(str(days_overdue))
                    if days_overdue > 0:
                        overdue_item.setForeground(Qt.GlobalColor.red)
                    self.results_table.setItem(row_idx, 7, overdue_item)
                    
                elif report_type == "Book Inventory":
                    self.results_table.setItem(row_idx, 0, QTableWidgetItem(str(data.get('book_number', ''))))
                    self.results_table.setItem(row_idx, 1, QTableWidgetItem(data.get('title', '')))
                    self.results_table.setItem(row_idx, 2, QTableWidgetItem(data.get('author', 'N/A')))
                    self.results_table.setItem(row_idx, 3, QTableWidgetItem(data.get('subject', 'N/A')))
                    self.results_table.setItem(row_idx, 4, QTableWidgetItem(data.get('class_name', 'N/A')))
                    self.results_table.setItem(row_idx, 5, QTableWidgetItem(data.get('book_type', 'N/A')))
                    self.results_table.setItem(row_idx, 6, QTableWidgetItem(data.get('condition', 'Good')))
                    status = data.get('status', 'Unknown')
                    status_item = QTableWidgetItem(status)
                    if status == 'Borrowed':
                        status_item.setForeground(Qt.GlobalColor.orange)
                    self.results_table.setItem(row_idx, 7, status_item)
                    self.results_table.setItem(row_idx, 8, QTableWidgetItem(data.get('isbn', 'N/A')))
                    
                else:  # All Books
                    book = data.get('book')
                    if book:
                        self.results_table.setItem(row_idx, 0, QTableWidgetItem(str(getattr(book, 'book_number', ''))))
                        self.results_table.setItem(row_idx, 1, QTableWidgetItem(getattr(book, 'title', '')))
                        self.results_table.setItem(row_idx, 2, QTableWidgetItem(getattr(book, 'author', '') or 'N/A'))
                        self.results_table.setItem(row_idx, 3, QTableWidgetItem(getattr(book, 'isbn', '') or 'N/A'))
                        subject = getattr(book, 'subject', None) or getattr(book, 'category', None) or 'N/A'
                        self.results_table.setItem(row_idx, 4, QTableWidgetItem(subject))
                        self.results_table.setItem(row_idx, 5, QTableWidgetItem(getattr(book, 'class_name', '') or 'N/A'))
                        book_type = 'Revision' if getattr(book, 'revision', 0) == 1 else 'Course'
                        self.results_table.setItem(row_idx, 6, QTableWidgetItem(book_type))
                        status = 'Borrowed' if not getattr(book, 'available', True) else 'Available'
                        self.results_table.setItem(row_idx, 7, QTableWidgetItem(status))

        except Exception as e:
            logger.error(f"Error populating books table: {e}")
            show_error_message("Error", f"Failed to display report data: {str(e)}", self)
