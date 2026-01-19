"""
Custom Reports Window

Dedicated window for generating custom reports.
"""

from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QComboBox, QTableWidget, QTableWidgetItem, QFileDialog, QTextEdit
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont

from school_system.gui.windows.base_function_window import BaseFunctionWindow
from school_system.gui.dialogs.message_dialog import show_error_message, show_success_message
from school_system.config.logging import logger
from school_system.services.report_service import ReportService


class CustomReportsWindow(BaseFunctionWindow):
    """Dedicated window for generating custom reports."""
    
    def __init__(self, parent=None, current_user: str = "", current_role: str = ""):
        """Initialize the custom reports window."""
        super().__init__("Custom Reports", parent, current_user, current_role)
        
        self.report_service = ReportService()
        
        # Setup content
        self.setup_content()
    
    def setup_content(self):
        """Setup the main content area."""
        # Create main content layout
        main_layout = self.create_flex_layout("column", False)
        main_layout.setContentsMargins(24, 24, 24, 24)
        main_layout.set_spacing(16)
        
        # Report builder card
        builder_card = self._create_report_builder_card()
        main_layout.add_widget(builder_card)
        
        # Report results card
        results_card = self._create_report_results_card()
        main_layout.add_widget(results_card, stretch=1)
        
        # Add to content
        self.add_layout_to_content(main_layout)
    
    def _create_report_builder_card(self) -> QWidget:
        """Create the report builder card."""
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
        title_label = QLabel("Custom Report Builder")
        title_font = QFont("Segoe UI", 18, QFont.Weight.Medium)
        title_label.setFont(title_font)
        title_label.setStyleSheet(f"color: {theme["text"]}; margin-bottom: 8px;")
        layout.addWidget(title_label)
        
        # Data source
        source_layout = QHBoxLayout()
        source_layout.setSpacing(12)
        
        source_label = QLabel("Data Source:")
        source_label.setStyleSheet(f"font-weight: 500; color: {theme["text"]};")
        source_layout.addWidget(source_label)
        
        self.data_source_combo = QComboBox()
        self.data_source_combo.setFixedHeight(44)
        self.data_source_combo.addItems(["Books", "Students", "Teachers", "Furniture", "All"])
        source_layout.addWidget(self.data_source_combo)
        
        source_layout.addStretch()
        
        # Generate button
        generate_btn = self.create_button("Generate Report", "primary")
        generate_btn.setFixedHeight(44)
        generate_btn.clicked.connect(self._on_generate_report)
        source_layout.addWidget(generate_btn)
        
        # Export button
        export_btn = self.create_button("Export Report", "secondary")
        export_btn.setFixedHeight(44)
        export_btn.clicked.connect(self._on_export_report)
        source_layout.addWidget(export_btn)
        
        layout.addLayout(source_layout)
        
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
        self.results_table = self.create_table(0, 5)
        self.results_table.setColumnCount(5)
        self.results_table.setHorizontalHeaderLabels(["ID", "Name", "Type", "Status", "Details"])
        self.results_table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.results_table.setAlternatingRowColors(True)
        layout.addWidget(self.results_table)

        return card

    def _populate_custom_table(self, report_data: list, data_source: str):
        """Populate the results table with custom report data."""
        try:
            self.results_table.setRowCount(0)  # Clear existing data

            for row_idx, item_data in enumerate(report_data):
                self.results_table.insertRow(row_idx)

                # Handle different data types based on the data source
                if data_source == "Books" or "book" in item_data:
                    # item_data is like {"book": <Book object>}
                    book = item_data.get('book')
                    if book:
                        item_id = getattr(book, 'id', '')
                        name = getattr(book, 'title', '')
                        item_type = "Book"
                        # Determine status based on availability
                        status = "Available" if getattr(book, 'available', True) else "Borrowed"
                        details = getattr(book, 'author', '') or 'N/A'
                    else:
                        item_id = name = details = ''
                        item_type = "Book"
                        status = "Unknown"

                elif data_source == "Students" or "student" in item_data:
                    # item_data is like {"student": <Student object>}
                    student = item_data.get('student')
                    if student:
                        item_id = getattr(student, 'student_id', '')
                        name = getattr(student, 'name', '')
                        item_type = "Student"
                        status = "Active"
                        details = getattr(student, 'stream', '') or getattr(student, 'class_name', '') or 'N/A'
                    else:
                        item_id = name = details = ''
                        item_type = "Student"
                        status = "Unknown"

                else:
                    # Generic handling for other data types (Teachers, Furniture, etc.)
                    if item_data and isinstance(item_data, dict):
                        # For placeholder data like {"teacher": {"id": "N/A", "name": "Feature not implemented"}}
                        item_key = list(item_data.keys())[0] if item_data else None
                        item = item_data.get(item_key, {}) if item_key else {}

                        if isinstance(item, dict):
                            # Dictionary-based item
                            item_id = item.get('id', '')
                            name = item.get('name', '') or item.get('title', '')
                            item_type = item_key.title() if item_key else data_source
                            status = item.get('status', 'Unknown')
                            details = item.get('subject', '') or item.get('type', '') or 'N/A'
                        else:
                            # Object-based item (fallback)
                            item_id = getattr(item, 'id', '') if hasattr(item, 'id') else ''
                            name = getattr(item, 'name', '') if hasattr(item, 'name') else getattr(item, 'title', '') if hasattr(item, 'title') else ''
                            item_type = data_source
                            status = getattr(item, 'status', 'Unknown') if hasattr(item, 'status') else 'Unknown'
                            details = 'N/A'
                    else:
                        item_id = name = details = ''
                        item_type = data_source
                        status = "Unknown"

                # Set table items
                self.results_table.setItem(row_idx, 0, QTableWidgetItem(str(item_id)))
                self.results_table.setItem(row_idx, 1, QTableWidgetItem(name))
                self.results_table.setItem(row_idx, 2, QTableWidgetItem(item_type))
                self.results_table.setItem(row_idx, 3, QTableWidgetItem(status))
                self.results_table.setItem(row_idx, 4, QTableWidgetItem(details))

        except Exception as e:
            logger.error(f"Error populating custom table: {e}")
            show_error_message("Error", f"Failed to display report data: {str(e)}", self)
    
    def _on_generate_report(self):
        """Handle generate report."""
        data_source = self.data_source_combo.currentText()

        try:
            # Clear table first
            self.results_table.setRowCount(0)

            # Generate report based on data source
            if data_source == "Books":
                report_data = self.report_service.get_all_books_report()
                self._populate_custom_table(report_data, "Books")
            elif data_source == "Students":
                report_data = self.report_service.get_all_students_report()
                self._populate_custom_table(report_data, "Students")
            elif data_source == "Teachers":
                # This would need to be implemented in ReportService
                report_data = self.report_service.get_all_teachers_report()
                self._populate_custom_table(report_data, "Teachers")
            elif data_source == "Furniture":
                # This would need to be implemented in ReportService
                report_data = self.report_service.get_all_furniture_report()
                self._populate_custom_table(report_data, "Furniture")
            elif data_source == "All":
                # Combine all data sources
                books_data = self.report_service.get_all_books_report()
                students_data = self.report_service.get_all_students_report()
                combined_data = books_data + students_data
                self._populate_custom_table(combined_data, "All")

            show_success_message("Success", f"Custom report for '{data_source}' generated successfully.", self)

        except Exception as e:
            logger.error(f"Error generating custom report: {e}")
            show_error_message("Error", f"Failed to generate report: {str(e)}", self)
    
    def _on_export_report(self):
        """Handle export report."""
        if self.results_table.rowCount() == 0:
            show_error_message("Error", "No report data to export. Generate a report first.", self)
            return

        file_path, selected_filter = QFileDialog.getSaveFileName(
            self,
            "Save Report",
            "custom_report.xlsx",
            "Excel Files (*.xlsx);;CSV Files (*.csv)"
        )

        if file_path:
            try:
                # Collect table data
                headers = []
                for col in range(self.results_table.columnCount()):
                    header_item = self.results_table.horizontalHeaderItem(col)
                    headers.append(header_item.text() if header_item else f"Column {col+1}")

                data = [headers]  # Start with headers

                # Add all rows
                for row in range(self.results_table.rowCount()):
                    row_data = []
                    for col in range(self.results_table.columnCount()):
                        item = self.results_table.item(row, col)
                        row_data.append(item.text() if item else "")
                    data.append(row_data)

                # Determine file type and export
                if selected_filter == "Excel Files (*.xlsx)" or file_path.lower().endswith('.xlsx'):
                    success = self.report_service.export_report_to_excel(data, file_path)
                elif selected_filter == "CSV Files (*.csv)" or file_path.lower().endswith('.csv'):
                    success = self._export_to_csv(data, file_path)
                else:
                    # Default to Excel
                    success = self.report_service.export_report_to_excel(data, file_path)

                if success:
                    show_success_message("Success", f"Report exported to {file_path}.", self)
                else:
                    show_error_message("Error", "Failed to export report.", self)

            except Exception as e:
                logger.error(f"Error exporting report: {e}")
                show_error_message("Error", f"Failed to export report: {str(e)}", self)

    def _export_to_csv(self, data: list, filename: str) -> bool:
        """Export data to CSV file."""
        try:
            import csv
            with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
                writer = csv.writer(csvfile)
                for row in data:
                    writer.writerow(row)
            return True
        except Exception as e:
            logger.error(f"Error exporting to CSV: {e}")
            return False
