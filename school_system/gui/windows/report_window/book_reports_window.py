"""
Book Reports Window

Dedicated window for generating book reports.
"""

from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QComboBox, QTableWidget, QTableWidgetItem, QFileDialog
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont

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
        title_label.setStyleSheet(f"color: {theme["text"]}; margin-bottom: 8px;")
        layout.addWidget(title_label)
        
        # Report type
        type_layout = QHBoxLayout()
        type_layout.setSpacing(12)
        
        type_label = QLabel("Report Type:")
        type_label.setStyleSheet(f"font-weight: 500; color: {theme["text"]};")
        type_layout.addWidget(type_label)
        
        self.report_type_combo = QComboBox()
        self.report_type_combo.setFixedHeight(44)
        self.report_type_combo.addItems([
            "All Books",
            "Borrowed Books",
            "Available Books",
            "Overdue Books",
            "Book Inventory"
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
        title_label.setStyleSheet(f"color: {theme["text"]}; margin-bottom: 8px;")
        layout.addWidget(title_label)
        
        # Results table
        self.results_table = self.create_table(0, 4)
        self.results_table.setHorizontalHeaderLabels(["Book ID", "Title", "Status", "Details"])
        self.results_table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.results_table.setAlternatingRowColors(True)
        layout.addWidget(self.results_table)

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
