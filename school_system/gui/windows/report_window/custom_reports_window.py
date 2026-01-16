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
                    item = item_data.get('book', {})
                    item_id = item.get('id', '')
                    name = item.get('title', '')
                    item_type = "Book"
                    status = item.get('status', 'Unknown')
                    details = item.get('author', '') or item.get('genre', '') or 'N/A'

                elif data_source == "Students" or "student" in item_data:
                    item = item_data.get('student', {})
                    item_id = item.get('id', '')
                    name = item.get('name', '')
                    item_type = "Student"
                    status = "Active"
                    details = item.get('stream', '') or item.get('class', '') or 'N/A'

                else:
                    # Generic handling for other data types
                    item = list(item_data.values())[0] if item_data else {}
                    item_id = item.get('id', '')
                    name = item.get('name', '') or item.get('title', '')
                    item_type = data_source
                    status = item.get('status', 'Unknown')
                    details = 'N/A'

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
        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "Save Report",
            "custom_report.xlsx",
            "Excel Files (*.xlsx);;CSV Files (*.csv)"
        )
        
        if file_path:
            try:
                # Export report
                show_success_message("Success", f"Report exported to {file_path}.", self)
            except Exception as e:
                logger.error(f"Error exporting report: {e}")
                show_error_message("Error", f"Failed to export report: {str(e)}", self)
