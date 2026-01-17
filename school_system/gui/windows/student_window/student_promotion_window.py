"""
Student Promotion Window

Dedicated window for managing student promotions - both individual and bulk operations.
"""

from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QTableWidget, QTableWidgetItem, QComboBox, QGroupBox, QProgressBar, QTextEdit, QMessageBox
from PyQt6.QtCore import Qt, pyqtSignal, QThread, QTimer
from PyQt6.QtGui import QFont

from school_system.gui.windows.base_function_window import BaseFunctionWindow
from school_system.gui.dialogs.message_dialog import show_error_message, show_success_message, show_info_message
from school_system.config.logging import logger
from school_system.services.student_service import StudentService
from school_system.gui.windows.book_window.utils.constants import STANDARD_CLASSES


class PromotionWorker(QThread):
    """Worker thread for bulk promotion operations."""
    progress = pyqtSignal(int)
    finished = pyqtSignal(dict)  # Promotion results
    error = pyqtSignal(str)

    def __init__(self, operation: str, params: dict, student_service: StudentService):
        super().__init__()
        self.operation = operation
        self.params = params
        self.student_service = student_service

    def run(self):
        """Run the promotion operation."""
        try:
            if self.operation == "yearly":
                result = self.student_service.promote_all_students_yearly()
            elif self.operation == "class_bulk":
                current_class = self.params['current_class']
                target_class = self.params.get('target_class')
                promoted, total = self.student_service.promote_students_by_class(current_class, target_class)
                result = {
                    'summary': {current_class: {'promoted': promoted, 'total': total, 'target_class': target_class}},
                    'total_promoted': promoted,
                    'total_processed': total,
                    'success_rate': (promoted / total * 100) if total > 0 else 0
                }
            elif self.operation == "individual":
                success = self.student_service.promote_student(
                    self.params['admission_number'],
                    self.params.get('target_class')
                )
                result = {
                    'success': success,
                    'total_promoted': 1 if success else 0,
                    'total_processed': 1
                }

            self.finished.emit(result)

        except Exception as e:
            self.error.emit(f"Promotion failed: {str(e)}")


class StudentPromotionWindow(BaseFunctionWindow):
    """Dedicated window for managing student promotions."""

    def __init__(self, parent=None, current_user: str = "", current_role: str = ""):
        """Initialize the student promotion window."""
        super().__init__("Student Promotion", parent, current_user, current_role)

        self.student_service = StudentService()
        self.promotion_worker = None

        # Setup content
        self.setup_content()

        # Load initial data
        self._refresh_students_table()

    def setup_content(self):
        """Setup the main content area."""
        # Create tab widget for different promotion types
        from PyQt6.QtWidgets import QTabWidget
        self.tabs = QTabWidget()

        # Individual Promotion Tab
        individual_tab = self._create_individual_promotion_tab()
        self.tabs.addTab(individual_tab, "👤 Individual Promotion")

        # Bulk Promotion Tab
        bulk_tab = self._create_bulk_promotion_tab()
        self.tabs.addTab(bulk_tab, "📚 Bulk Promotion")

        # Yearly Promotion Tab
        yearly_tab = self._create_yearly_promotion_tab()
        self.tabs.addTab(yearly_tab, "📅 Yearly Promotion")

        # Add tabs to main layout
        main_layout = QVBoxLayout()
        main_layout.addWidget(self.tabs)
        main_layout.setContentsMargins(0, 0, 0, 0)

        # Add to content
        self.add_layout_to_content(main_layout)

    def _create_individual_promotion_tab(self) -> QWidget:
        """Create the individual promotion tab."""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setSpacing(16)

        # Student selection section
        selection_group = QGroupBox("Select Student")
        selection_layout = QVBoxLayout(selection_group)

        # Class filter
        class_layout = QHBoxLayout()
        class_label = QLabel("Filter by Class:")
        class_label.setStyleSheet("font-weight: 500;")
        class_layout.addWidget(class_label)

        self.individual_class_combo = QComboBox()
        self.individual_class_combo.addItem("All Classes")
        self.individual_class_combo.addItems(STANDARD_CLASSES)
        self.individual_class_combo.currentTextChanged.connect(self._filter_individual_students)
        class_layout.addWidget(self.individual_class_combo)

        class_layout.addStretch()
        selection_layout.addLayout(class_layout)

        # Students table
        self.individual_students_table = self.create_table(0, 5)
        self.individual_students_table.setColumnCount(5)
        self.individual_students_table.setHorizontalHeaderLabels([
            "Student ID", "Admission No", "Name", "Current Class", "Stream"
        ])
        self.individual_students_table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.individual_students_table.setAlternatingRowColors(True)
        selection_layout.addWidget(self.individual_students_table)

        layout.addWidget(selection_group)

        # Promotion section
        promotion_group = QGroupBox("Promotion Details")
        promotion_layout = QVBoxLayout(promotion_group)

        # Current student info
        info_layout = QHBoxLayout()
        self.student_info_label = QLabel("No student selected")
        self.student_info_label.setStyleSheet("font-weight: 500; padding: 8px; background-color: #f0f0f0; border-radius: 4px;")
        info_layout.addWidget(self.student_info_label)
        info_layout.addStretch()
        promotion_layout.addLayout(info_layout)

        # Target class selection
        target_layout = QHBoxLayout()
        target_label = QLabel("Promote to Class:")
        target_label.setStyleSheet("font-weight: 500;")
        target_layout.addWidget(target_label)

        self.target_class_combo = QComboBox()
        self.target_class_combo.addItems(STANDARD_CLASSES)
        target_layout.addWidget(self.target_class_combo)

        target_layout.addStretch()
        promotion_layout.addLayout(target_layout)

        # Promote button
        promote_btn = self.create_button("🚀 Promote Student", "primary")
        promote_btn.clicked.connect(self._promote_individual_student)
        promotion_layout.addWidget(promote_btn)

        layout.addWidget(promotion_group)
        return tab

    def _create_bulk_promotion_tab(self) -> QWidget:
        """Create the bulk promotion tab."""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setSpacing(16)

        # Bulk promotion section
        bulk_group = QGroupBox("Bulk Class Promotion")
        bulk_layout = QVBoxLayout(bulk_group)

        # Current class selection
        current_layout = QHBoxLayout()
        current_label = QLabel("Promote from Class:")
        current_label.setStyleSheet("font-weight: 500;")
        current_layout.addWidget(current_label)

        self.bulk_current_class_combo = QComboBox()
        # Only show classes that can be promoted
        promotable_classes = ["Form 1", "Form 2", "Form 3", "Grade 10", "Grade 11"]
        self.bulk_current_class_combo.addItems(promotable_classes)
        current_layout.addWidget(self.bulk_current_class_combo)

        current_layout.addStretch()
        bulk_layout.addLayout(current_layout)

        # Target class display (auto-calculated)
        target_display_layout = QHBoxLayout()
        target_display_label = QLabel("Will promote to:")
        target_display_label.setStyleSheet("font-weight: 500;")
        target_display_layout.addWidget(target_display_label)

        self.bulk_target_display = QLabel("Select a class above")
        self.bulk_target_display.setStyleSheet("font-weight: 500; color: #1976d2; padding: 4px; background-color: #e3f2fd; border-radius: 4px;")
        target_display_layout.addWidget(self.bulk_target_display)

        target_display_layout.addStretch()
        bulk_layout.addLayout(target_display_layout)

        # Connect to update target display
        self.bulk_current_class_combo.currentTextChanged.connect(self._update_bulk_target_display)

        # Student count display
        count_layout = QHBoxLayout()
        count_label = QLabel("Students to promote:")
        count_label.setStyleSheet("font-weight: 500;")
        count_layout.addWidget(count_label)

        self.bulk_student_count_label = QLabel("0 students")
        self.bulk_student_count_label.setStyleSheet("font-weight: 500; color: #2e7d32; padding: 4px; background-color: #e8f5e8; border-radius: 4px;")
        count_layout.addWidget(self.bulk_student_count_label)

        count_layout.addStretch()
        bulk_layout.addLayout(count_layout)

        # Bulk promote button
        bulk_promote_btn = self.create_button("🚀 Promote All Students in Class", "success")
        bulk_promote_btn.setFixedHeight(44)
        bulk_promote_btn.clicked.connect(self._promote_bulk_class)
        bulk_layout.addWidget(bulk_promote_btn)

        layout.addWidget(bulk_group)

        # Progress section
        self.bulk_progress_group = QGroupBox("Promotion Progress")
        self.bulk_progress_group.setVisible(False)
        progress_layout = QVBoxLayout(self.bulk_progress_group)

        self.bulk_progress_bar = QProgressBar()
        self.bulk_progress_bar.setRange(0, 100)
        progress_layout.addWidget(self.bulk_progress_bar)

        self.bulk_status_label = QLabel("Preparing promotion...")
        progress_layout.addWidget(self.bulk_status_label)

        layout.addWidget(self.bulk_progress_group)
        return tab

    def _create_yearly_promotion_tab(self) -> QWidget:
        """Create the yearly promotion tab."""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setSpacing(16)

        # Yearly promotion section
        yearly_group = QGroupBox("Yearly Promotion for All Eligible Students")
        yearly_layout = QVBoxLayout(yearly_group)

        # Description
        desc_label = QLabel("This will promote all students in eligible classes to their next grade level:")
        desc_label.setWordWrap(True)
        desc_label.setStyleSheet("margin-bottom: 8px;")
        yearly_layout.addWidget(desc_label)

        # Promotion path display
        path_label = QLabel("• Form 1 → Form 2\n• Form 2 → Form 3\n• Form 3 → Form 4\n• Grade 10 → Grade 11\n• Grade 11 → Grade 12")
        path_label.setStyleSheet("font-family: monospace; background-color: #f5f5f5; padding: 12px; border-radius: 4px;")
        yearly_layout.addWidget(path_label)

        # Statistics preview
        stats_layout = QVBoxLayout()
        stats_label = QLabel("Students ready for promotion:")
        stats_label.setStyleSheet("font-weight: 500; margin-top: 12px;")
        stats_layout.addWidget(stats_label)

        self.yearly_stats_label = QLabel("Click 'Preview Promotion' to see statistics")
        self.yearly_stats_label.setStyleSheet("color: #666; font-style: italic;")
        stats_layout.addWidget(self.yearly_stats_label)

        yearly_layout.addLayout(stats_layout)

        # Action buttons
        buttons_layout = QHBoxLayout()

        preview_btn = self.create_button("👁️ Preview Promotion", "outline")
        preview_btn.clicked.connect(self._preview_yearly_promotion)
        buttons_layout.addWidget(preview_btn)

        buttons_layout.addStretch()

        yearly_promote_btn = self.create_button("🎓 Execute Yearly Promotion", "primary")
        yearly_promote_btn.setFixedHeight(44)
        yearly_promote_btn.clicked.connect(self._execute_yearly_promotion)
        buttons_layout.addWidget(yearly_promote_btn)

        yearly_layout.addLayout(buttons_layout)

        layout.addWidget(yearly_group)

        # Progress section
        self.yearly_progress_group = QGroupBox("Yearly Promotion Progress")
        self.yearly_progress_group.setVisible(False)
        progress_layout = QVBoxLayout(self.yearly_progress_group)

        self.yearly_progress_bar = QProgressBar()
        self.yearly_progress_bar.setRange(0, 100)
        progress_layout.addWidget(self.yearly_progress_bar)

        self.yearly_status_label = QLabel("Starting yearly promotion...")
        progress_layout.addWidget(self.yearly_status_label)

        # Results display
        self.yearly_results_text = QTextEdit()
        self.yearly_results_text.setReadOnly(True)
        self.yearly_results_text.setMaximumHeight(200)
        progress_layout.addWidget(self.yearly_results_text)

        layout.addWidget(self.yearly_progress_group)
        return tab

    def _refresh_students_table(self):
        """Refresh the individual students table."""
        try:
            # Get all students
            students = self.student_service.get_all_students()

            self.individual_students_table.setRowCount(0)

            for student in students:
                row = self.individual_students_table.rowCount()
                self.individual_students_table.insertRow(row)

                self.individual_students_table.setItem(row, 0, QTableWidgetItem(student.student_id))
                self.individual_students_table.setItem(row, 1, QTableWidgetItem(student.admission_number))
                self.individual_students_table.setItem(row, 2, QTableWidgetItem(student.name))
                self.individual_students_table.setItem(row, 3, QTableWidgetItem(student.class_name or ""))
                self.individual_students_table.setItem(row, 4, QTableWidgetItem(student.stream_name or ""))

            # Resize columns
            self.individual_students_table.resizeColumnsToContents()

        except Exception as e:
            logger.error(f"Error refreshing students table: {e}")
            show_error_message("Error", f"Failed to refresh students table: {str(e)}", self)

    def _filter_individual_students(self, class_filter: str):
        """Filter students by class in individual promotion tab."""
        try:
            if class_filter == "All Classes":
                students = self.student_service.get_all_students()
            else:
                students = self.student_service.get_students_by_class(class_filter)

            self.individual_students_table.setRowCount(0)

            for student in students:
                row = self.individual_students_table.rowCount()
                self.individual_students_table.insertRow(row)

                self.individual_students_table.setItem(row, 0, QTableWidgetItem(student.student_id))
                self.individual_students_table.setItem(row, 1, QTableWidgetItem(student.admission_number))
                self.individual_students_table.setItem(row, 2, QTableWidgetItem(student.name))
                self.individual_students_table.setItem(row, 3, QTableWidgetItem(student.class_name or ""))
                self.individual_students_table.setItem(row, 4, QTableWidgetItem(student.stream_name or ""))

            self.individual_students_table.resizeColumnsToContents()

        except Exception as e:
            logger.error(f"Error filtering students: {e}")

    def _promote_individual_student(self):
        """Promote the selected individual student."""
        # Get selected student
        selected_rows = self.individual_students_table.selectionModel().selectedRows()
        if not selected_rows:
            show_error_message("No Selection", "Please select a student to promote.", self)
            return

        row = selected_rows[0].row()
        admission_number = self.individual_students_table.item(row, 1).text()
        student_name = self.individual_students_table.item(row, 2).text()
        current_class = self.individual_students_table.item(row, 3).text()
        target_class = self.target_class_combo.currentText()

        # Confirm promotion
        from PyQt6.QtWidgets import QMessageBox
        reply = QMessageBox.question(
            self,
            "Confirm Promotion",
            f"Are you sure you want to promote {student_name} ({admission_number}) from {current_class} to {target_class}?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )

        if reply == QMessageBox.StandardButton.Yes:
            self._start_promotion_worker("individual", {
                'admission_number': admission_number,
                'target_class': target_class
            })

    def _update_bulk_target_display(self, current_class: str):
        """Update the bulk promotion target class display."""
        if current_class:
            target_class = self.student_service.get_next_class(current_class)
            if target_class:
                self.bulk_target_display.setText(target_class)
                # Update student count
                try:
                    students = self.student_service.get_students_by_class(current_class)
                    self.bulk_student_count_label.setText(f"{len(students)} students")
                except Exception as e:
                    self.bulk_student_count_label.setText("Error loading count")
            else:
                self.bulk_target_display.setText("No promotion available")
                self.bulk_student_count_label.setText("0 students")
        else:
            self.bulk_target_display.setText("Select a class above")
            self.bulk_student_count_label.setText("0 students")

    def _promote_bulk_class(self):
        """Promote all students in the selected class."""
        current_class = self.bulk_current_class_combo.currentText()
        if not current_class:
            show_error_message("No Class Selected", "Please select a class to promote from.", self)
            return

        target_class = self.student_service.get_next_class(current_class)
        if not target_class:
            show_error_message("No Promotion Available", f"No promotion available for {current_class}.", self)
            return

        # Confirm bulk promotion
        from PyQt6.QtWidgets import QMessageBox
        reply = QMessageBox.question(
            self,
            "Confirm Bulk Promotion",
            f"Are you sure you want to promote ALL students from {current_class} to {target_class}?\n\nThis action cannot be undone.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )

        if reply == QMessageBox.StandardButton.Yes:
            self._start_promotion_worker("class_bulk", {
                'current_class': current_class,
                'target_class': target_class
            })

    def _preview_yearly_promotion(self):
        """Preview the yearly promotion statistics."""
        try:
            # Calculate preview statistics
            promotable_classes = ["Form 1", "Form 2", "Form 3", "Grade 10", "Grade 11"]
            preview_text = "Yearly Promotion Preview:\n\n"

            total_students = 0
            for current_class in promotable_classes:
                students = self.student_service.get_students_by_class(current_class)
                if students:
                    target_class = self.student_service.get_next_class(current_class)
                    preview_text += f"• {current_class} → {target_class}: {len(students)} students\n"
                    total_students += len(students)

            preview_text += f"\nTotal students to promote: {total_students}"

            self.yearly_stats_label.setText(preview_text.replace('\n', ' | '))

        except Exception as e:
            logger.error(f"Error previewing yearly promotion: {e}")
            self.yearly_stats_label.setText(f"Error: {str(e)}")

    def _execute_yearly_promotion(self):
        """Execute the yearly promotion for all eligible students."""
        # Confirm yearly promotion
        from PyQt6.QtWidgets import QMessageBox
        reply = QMessageBox.question(
            self,
            "Confirm Yearly Promotion",
            "Are you sure you want to execute the yearly promotion for ALL eligible students?\n\nThis will promote students from:\n• Form 1 → Form 2\n• Form 2 → Form 3\n• Form 3 → Form 4\n• Grade 10 → Grade 11\n• Grade 11 → Grade 12\n\nThis action cannot be undone.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )

        if reply == QMessageBox.StandardButton.Yes:
            self._start_promotion_worker("yearly", {})

    def _start_promotion_worker(self, operation: str, params: dict):
        """Start the promotion worker thread."""
        if self.promotion_worker and self.promotion_worker.isRunning():
            return

        self.promotion_worker = PromotionWorker(operation, params, self.student_service)

        # Connect signals
        if operation in ["class_bulk", "yearly"]:
            self.promotion_worker.progress.connect(self._update_progress)
            self.promotion_worker.finished.connect(self._on_bulk_promotion_finished)
        else:
            self.promotion_worker.finished.connect(self._on_individual_promotion_finished)

        self.promotion_worker.error.connect(self._on_promotion_error)

        # Show progress for bulk operations
        if operation in ["class_bulk", "yearly"]:
            if operation == "class_bulk":
                self.bulk_progress_group.setVisible(True)
                self.bulk_progress_bar.setValue(0)
                self.bulk_status_label.setText("Starting bulk promotion...")
            else:  # yearly
                self.yearly_progress_group.setVisible(True)
                self.yearly_progress_bar.setValue(0)
                self.yearly_status_label.setText("Starting yearly promotion...")

        self.promotion_worker.start()

    def _update_progress(self, value: int):
        """Update progress bars."""
        if self.tabs.currentIndex() == 1:  # Bulk promotion tab
            self.bulk_progress_bar.setValue(value)
            self.bulk_status_label.setText(f"Processing... {value}%")
        else:  # Yearly promotion tab
            self.yearly_progress_bar.setValue(value)
            self.yearly_status_label.setText(f"Processing... {value}%")

    def _on_individual_promotion_finished(self, result: dict):
        """Handle individual promotion completion."""
        if result.get('success', False):
            show_success_message("Promotion Successful",
                               f"Student promoted successfully!", self)
            self._refresh_students_table()
        else:
            show_error_message("Promotion Failed",
                             "Failed to promote the student. Please try again.", self)

    def _on_bulk_promotion_finished(self, result: dict):
        """Handle bulk promotion completion."""
        # Hide progress
        if self.tabs.currentIndex() == 1:  # Bulk promotion tab
            self.bulk_progress_group.setVisible(False)
        else:  # Yearly promotion tab
            self.yearly_progress_group.setVisible(False)

        # Show results
        total_promoted = result.get('total_promoted', 0)
        total_processed = result.get('total_processed', 0)
        success_rate = result.get('success_rate', 0)

        if total_processed > 0:
            message = f"Promotion completed!\n\nPromoted: {total_promoted} out of {total_processed} students\nSuccess Rate: {success_rate:.1f}%"

            if self.tabs.currentIndex() == 2:  # Yearly promotion tab
                # Show detailed results
                results_text = "Yearly Promotion Results:\n\n"
                for class_name, stats in result.get('summary', {}).items():
                    results_text += f"{class_name} → {stats['target_class']}: {stats['promoted']}/{stats['total']} students\n"
                results_text += f"\nTotal: {total_promoted}/{total_processed} students promoted"

                self.yearly_results_text.setPlainText(results_text)

            show_success_message("Bulk Promotion Completed", message, self)
            self._refresh_students_table()
        else:
            show_info_message("No Students to Promote", "No eligible students found for promotion.", self)

    def _on_promotion_error(self, error_msg: str):
        """Handle promotion errors."""
        # Hide progress
        self.bulk_progress_group.setVisible(False)
        self.yearly_progress_group.setVisible(False)

        show_error_message("Promotion Error", error_msg, self)