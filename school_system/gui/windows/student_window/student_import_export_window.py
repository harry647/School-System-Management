"""
Student Import/Export Window

Dedicated window for importing and exporting student data.
"""

from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QTableWidget, QTableWidgetItem, QFileDialog, QProgressBar, QTextEdit, QComboBox
from PyQt6.QtCore import Qt, pyqtSignal, QThread, QTimer
from PyQt6.QtGui import QFont
import pandas as pd
import csv
import json
from typing import List, Dict, Any
from pathlib import Path

from school_system.gui.windows.base_function_window import BaseFunctionWindow
from school_system.gui.dialogs.message_dialog import show_error_message, show_success_message, show_info_message
from school_system.config.logging import logger
from school_system.services.student_service import StudentService
from school_system.gui.windows.student_window.student_validation import StudentValidator


class ImportWorker(QThread):
    """Worker thread for importing student data."""
    progress = pyqtSignal(int)
    finished = pyqtSignal(list)  # List of import results
    error = pyqtSignal(str)

    def __init__(self, file_path: str, file_format: str, student_service: StudentService, validator: StudentValidator):
        super().__init__()
        self.file_path = file_path
        self.file_format = file_format
        self.student_service = student_service
        self.validator = validator

    def run(self):
        """Run the import process."""
        try:
            # Read data from file
            data = self._read_file_data()
            if not data:
                self.error.emit("No data found in file or invalid format")
                return

            results = []
            total = len(data)

            for i, student_data in enumerate(data):
                try:
                    # Validate student data
                    validation_result = self.validator.validate_student_data(student_data)
                    if not validation_result['valid']:
                        results.append({
                            'success': False,
                            'student_id': student_data.get('student_id', 'Unknown'),
                            'error': validation_result['errors'][0] if validation_result['errors'] else 'Validation failed'
                        })
                        continue

                    # Check if student already exists
                    existing = self.student_service.get_student_by_id(student_data['student_id'])
                    if existing:
                        # Update existing student
                        self.student_service.update_student(student_data['student_id'], student_data)
                        results.append({
                            'success': True,
                            'student_id': student_data['student_id'],
                            'action': 'updated'
                        })
                    else:
                        # Create new student
                        self.student_service.create_student(student_data)
                        results.append({
                            'success': True,
                            'student_id': student_data['student_id'],
                            'action': 'created'
                        })

                except Exception as e:
                    results.append({
                        'success': False,
                        'student_id': student_data.get('student_id', 'Unknown'),
                        'error': str(e)
                    })

                # Update progress
                self.progress.emit(int((i + 1) / total * 100))

            self.finished.emit(results)

        except Exception as e:
            self.error.emit(f"Import failed: {str(e)}")

    def _read_file_data(self) -> List[Dict[str, Any]]:
        """Read data from the file based on format."""
        try:
            if self.file_format == 'csv':
                return self._read_csv()
            elif self.file_format == 'excel':
                return self._read_excel()
            elif self.file_format == 'json':
                return self._read_json()
            else:
                raise ValueError(f"Unsupported file format: {self.file_format}")
        except Exception as e:
            logger.error(f"Error reading file {self.file_path}: {e}")
            raise

    def _read_csv(self) -> List[Dict[str, Any]]:
        """Read data from CSV file."""
        data = []
        with open(self.file_path, 'r', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            for row in reader:
                # Clean and normalize data
                student_data = {
                    'student_id': row.get('student_id', '').strip(),
                    'name': row.get('name', '').strip(),
                    'stream': row.get('stream', '').strip()
                }
                data.append(student_data)
        return data

    def _read_excel(self) -> List[Dict[str, Any]]:
        """Read data from Excel file."""
        df = pd.read_excel(self.file_path)
        data = []
        for _, row in df.iterrows():
            student_data = {
                'student_id': str(row.get('student_id', '')).strip(),
                'name': str(row.get('name', '')).strip(),
                'stream': str(row.get('stream', '')).strip()
            }
            data.append(student_data)
        return data

    def _read_json(self) -> List[Dict[str, Any]]:
        """Read data from JSON file."""
        with open(self.file_path, 'r', encoding='utf-8') as file:
            data = json.load(file)
            # Handle both list and dict formats
            if isinstance(data, list):
                return data
            elif isinstance(data, dict) and 'students' in data:
                return data['students']
            else:
                raise ValueError("Invalid JSON format. Expected list or object with 'students' key")


class StudentImportExportWindow(BaseFunctionWindow):
    """Dedicated window for importing and exporting student data."""

    def __init__(self, parent=None, current_user: str = "", current_role: str = ""):
        """Initialize the import/export window."""
        super().__init__("Student Import/Export", parent, current_user, current_role)

        self.student_service = StudentService()
        self.validator = StudentValidator()
        self.import_worker = None

        # Setup content
        self.setup_content()

    def setup_content(self):
        """Setup the main content area."""
        # Create main content layout
        main_layout = self.create_flex_layout("column", False)
        main_layout.setContentsMargins(24, 24, 24, 24)
        main_layout.setSpacing(20)

        # Import section
        import_card = self._create_import_card()
        main_layout.add_widget(import_card)

        # Export section
        export_card = self._create_export_card()
        main_layout.add_widget(export_card)

        # Results section
        results_card = self._create_results_card()
        main_layout.add_widget(results_card, stretch=1)

        # Add to content
        self.add_layout_to_content(main_layout)

    def _create_import_card(self) -> QWidget:
        """Create the import section card."""
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
        title_label = QLabel("📥 Import Students")
        title_font = QFont("Segoe UI", 18, QFont.Weight.SemiBold)
        title_label.setFont(title_font)
        title_label.setStyleSheet(f"color: {theme["text"]};")
        layout.addWidget(title_label)

        # Import controls
        controls_layout = QHBoxLayout()
        controls_layout.setSpacing(12)

        # File format selector
        format_label = QLabel("Format:")
        format_label.setStyleSheet(f"font-weight: 500; color: {theme["text"]};")
        controls_layout.addWidget(format_label)

        self.format_combo = QComboBox()
        self.format_combo.addItems(["CSV", "Excel", "JSON"])
        self.format_combo.setFixedWidth(100)
        controls_layout.addWidget(self.format_combo)

        controls_layout.addStretch()

        # Browse button
        browse_btn = self.create_button("📁 Browse File", "secondary")
        browse_btn.clicked.connect(self._browse_import_file)
        controls_layout.addWidget(browse_btn)

        # Import button
        self.import_btn = self.create_button("⬆️ Import Data", "primary")
        self.import_btn.clicked.connect(self._start_import)
        self.import_btn.setEnabled(False)
        controls_layout.addWidget(self.import_btn)

        layout.addLayout(controls_layout)

        # File path display
        self.file_path_label = QLabel("No file selected")
        self.file_path_label.setStyleSheet(f"color: {theme["text_secondary"]}; font-style: italic;")
        layout.addWidget(self.file_path_label)

        # Progress bar
        self.import_progress = QProgressBar()
        self.import_progress.setVisible(False)
        self.import_progress.setStyleSheet(f"""
            QProgressBar {{
                border: 1px solid {theme["border"]};
                border-radius: 4px;
                text-align: center;
                background-color: {theme["surface"]};
            }}
            QProgressBar::chunk {{
                background-color: {theme["primary"]};
            }}
        """)
        layout.addWidget(self.import_progress)

        return card

    def _create_export_card(self) -> QWidget:
        """Create the export section card."""
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
        title_label = QLabel("📤 Export Students")
        title_font = QFont("Segoe UI", 18, QFont.Weight.SemiBold)
        title_label.setFont(title_font)
        title_label.setStyleSheet(f"color: {theme["text"]};")
        layout.addWidget(title_label)

        # Export controls
        controls_layout = QHBoxLayout()
        controls_layout.setSpacing(12)

        # Stream filter
        stream_label = QLabel("Filter by Stream:")
        stream_label.setStyleSheet(f"font-weight: 500; color: {theme["text"]};")
        controls_layout.addWidget(stream_label)

        self.export_stream_combo = QComboBox()
        self.export_stream_combo.addItem("All Streams")
        self._populate_export_stream_filter()
        controls_layout.addWidget(self.export_stream_combo)

        # Format selector
        format_label = QLabel("Format:")
        format_label.setStyleSheet(f"font-weight: 500; color: {theme["text"]};")
        controls_layout.addWidget(format_label)

        self.export_format_combo = QComboBox()
        self.export_format_combo.addItems(["CSV", "Excel", "JSON"])
        controls_layout.addWidget(self.export_format_combo)

        controls_layout.addStretch()

        # Export button
        export_btn = self.create_button("⬇️ Export Data", "success")
        export_btn.clicked.connect(self._start_export)
        controls_layout.addWidget(export_btn)

        layout.addLayout(controls_layout)

        return card

    def _create_results_card(self) -> QWidget:
        """Create the results section card."""
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
        title_label = QLabel("📊 Import Results")
        title_font = QFont("Segoe UI", 16, QFont.Weight.SemiBold)
        title_label.setFont(title_font)
        title_label.setStyleSheet(f"color: {theme["text"]};")
        layout.addWidget(title_label)

        # Results text area
        self.results_text = QTextEdit()
        self.results_text.setReadOnly(True)
        self.results_text.setStyleSheet(f"""
            QTextEdit {{
                background-color: {theme["background"]};
                border: 1px solid {theme["border"]};
                border-radius: 8px;
                padding: 12px;
                font-family: 'Consolas', monospace;
                font-size: 12px;
            }}
        """)
        layout.addWidget(self.results_text)

        return card

    def _populate_export_stream_filter(self):
        """Populate the export stream filter."""
        try:
            streams = self.student_service.get_all_streams()
            for stream in streams:
                if stream:
                    self.export_stream_combo.addItem(stream)
        except Exception as e:
            logger.error(f"Error populating export stream filter: {e}")

    def _browse_import_file(self):
        """Browse for import file."""
        format_map = {
            "CSV": "CSV Files (*.csv)",
            "Excel": "Excel Files (*.xlsx *.xls)",
            "JSON": "JSON Files (*.json)"
        }

        current_format = self.format_combo.currentText()
        file_filter = format_map.get(current_format, "All Files (*)")

        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Select Import File",
            "",
            file_filter
        )

        if file_path:
            self.selected_file_path = file_path
            self.file_path_label.setText(f"Selected: {Path(file_path).name}")
            self.import_btn.setEnabled(True)

    def _start_import(self):
        """Start the import process."""
        if not hasattr(self, 'selected_file_path'):
            show_error_message("No File Selected", "Please select a file to import.", self)
            return

        # Disable import button and show progress
        self.import_btn.setEnabled(False)
        self.import_progress.setVisible(True)
        self.import_progress.setValue(0)
        self.results_text.clear()

        # Start import worker
        format_map = {"CSV": "csv", "Excel": "excel", "JSON": "json"}
        file_format = format_map.get(self.format_combo.currentText(), "csv")

        self.import_worker = ImportWorker(
            self.selected_file_path,
            file_format,
            self.student_service,
            self.validator
        )

        self.import_worker.progress.connect(self._update_import_progress)
        self.import_worker.finished.connect(self._on_import_finished)
        self.import_worker.error.connect(self._on_import_error)
        self.import_worker.start()

    def _update_import_progress(self, value: int):
        """Update import progress."""
        self.import_progress.setValue(value)

    def _on_import_finished(self, results: list):
        """Handle import completion."""
        self.import_progress.setVisible(False)
        self.import_btn.setEnabled(True)

        # Count results
        successful = sum(1 for r in results if r['success'])
        failed = len(results) - successful

        # Display results
        result_text = f"Import completed: {successful} successful, {failed} failed\n\n"
        result_text += "Details:\n"

        for result in results:
            if result['success']:
                result_text += f"✓ {result['student_id']}: {result['action']}\n"
            else:
                result_text += f"✗ {result['student_id']}: {result['error']}\n"

        self.results_text.setPlainText(result_text)

        if successful > 0:
            show_success_message("Import Successful", f"Successfully imported {successful} students.", self)
        if failed > 0:
            show_info_message("Import Completed with Errors", f"{failed} students failed to import. Check results for details.", self)

    def _on_import_error(self, error_msg: str):
        """Handle import error."""
        self.import_progress.setVisible(False)
        self.import_btn.setEnabled(True)
        show_error_message("Import Error", error_msg, self)
        self.results_text.setPlainText(f"Import failed: {error_msg}")

    def _start_export(self):
        """Start the export process."""
        try:
            # Get filter
            stream_filter = self.export_stream_combo.currentText()
            stream = None if stream_filter == "All Streams" else stream_filter

            # Get students
            students = self.student_service.get_all_students(stream=stream)

            if not students:
                show_info_message("No Data", "No students found to export.", self)
                return

            # Choose export format
            format_map = {
                "CSV": self._export_csv,
                "Excel": self._export_excel,
                "JSON": self._export_json
            }

            export_func = format_map.get(self.export_format_combo.currentText())
            if export_func:
                export_func(students)
                show_success_message("Export Successful", f"Exported {len(students)} students successfully.", self)
            else:
                show_error_message("Export Error", "Invalid export format selected.", self)

        except Exception as e:
            logger.error(f"Error during export: {e}")
            show_error_message("Export Error", f"Failed to export students: {str(e)}", self)

    def _export_csv(self, students):
        """Export students to CSV."""
        file_path, _ = QFileDialog.getSaveFileName(
            self, "Save CSV File", "students.csv", "CSV Files (*.csv)"
        )

        if file_path:
            with open(file_path, 'w', newline='', encoding='utf-8') as file:
                writer = csv.writer(file)
                writer.writerow(['student_id', 'name', 'stream'])

                for student in students:
                    writer.writerow([student.student_id, student.name, student.stream])

    def _export_excel(self, students):
        """Export students to Excel."""
        file_path, _ = QFileDialog.getSaveFileName(
            self, "Save Excel File", "students.xlsx", "Excel Files (*.xlsx)"
        )

        if file_path:
            data = {
                'student_id': [s.student_id for s in students],
                'name': [s.name for s in students],
                'stream': [s.stream for s in students]
            }
            df = pd.DataFrame(data)
            df.to_excel(file_path, index=False)

    def _export_json(self, students):
        """Export students to JSON."""
        file_path, _ = QFileDialog.getSaveFileName(
            self, "Save JSON File", "students.json", "JSON Files (*.json)"
        )

        if file_path:
            data = {
                'students': [
                    {'student_id': s.student_id, 'name': s.name, 'stream': s.stream}
                    for s in students
                ]
            }

            with open(file_path, 'w', encoding='utf-8') as file:
                json.dump(data, file, indent=2, ensure_ascii=False)