"""
Student management window for the School System Management application.

This module provides the student management interface for admin users (admin and librarian roles).
"""

from PyQt6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QLabel, QLineEdit, QPushButton, 
                            QHBoxLayout, QComboBox, QTabWidget, QTableWidget, QTableWidgetItem, 
                            QTextEdit, QSizePolicy, QFileDialog, QMessageBox)
from PyQt6.QtCore import Qt
from typing import Callable, Optional

from school_system.gui.base.base_window import BaseWindow
from school_system.gui.dialogs.message_dialog import show_error_message, show_success_message
from school_system.config.logging import logger
from school_system.services.student_service import StudentService
from school_system.core.exceptions import DatabaseException, ValidationError


class StudentWindow(BaseWindow):
    """Student management window for admin users."""

    def __init__(self, parent: QMainWindow, current_user: str, current_role: str):
        """
        Initialize the student window.

        Args:
            parent: The parent window
            current_user: The current logged-in username
            current_role: The current user's role
        """
        super().__init__("School System - Student Management", parent)

        self.parent = parent
        self.current_user = current_user
        self.current_role = current_role
        self.student_service = StudentService()

        # Check if user has admin privileges
        if self.current_role not in ["admin", "librarian"]:
            show_error_message("Access Denied", "You do not have permission to access student management.", self)
            self.close()
            return

        # Set minimum size
        self.setMinimumSize(1200, 800)

        # Initialize UI
        self._setup_widgets()

    def _setup_widgets(self):
        """Setup the student management widgets."""
        # Create tab widget for different sections
        tab_widget = QTabWidget()
        self.add_widget_to_content(tab_widget)

        # Student Management Tab
        student_tab = self._create_student_management_tab()
        tab_widget.addTab(student_tab, "Student Management")

        # Ream Management Tab
        ream_tab = self._create_ream_management_tab()
        tab_widget.addTab(ream_tab, "Ream Management")

        # Library Activity Tab
        library_tab = self._create_library_activity_tab()
        tab_widget.addTab(library_tab, "Library Activity")

        # Import/Export Tab
        import_export_tab = self._create_import_export_tab()
        tab_widget.addTab(import_export_tab, "Import/Export")

        # Reports Tab
        reports_tab = self._create_reports_tab()
        tab_widget.addTab(reports_tab, "Reports")

    def _create_student_management_tab(self) -> QWidget:
        """Create the student management tab."""
        tab = QWidget()
        layout = self.create_flex_layout("column", False)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.set_spacing(15)

        # Create Student Section
        create_section = self.create_card("Create New Student", "")
        create_form = QWidget()
        create_layout = self.create_flex_layout("column", False)
        create_layout.set_spacing(10)

        # Student ID
        student_id_label = QLabel("Student ID:")
        create_layout.add_widget(student_id_label)
        self.create_student_id_input = self.create_input("Enter student ID")
        create_layout.add_widget(self.create_student_id_input)

        # Name
        name_label = QLabel("Name:")
        create_layout.add_widget(name_label)
        self.create_name_input = self.create_input("Enter student name")
        create_layout.add_widget(self.create_name_input)

        # Stream
        stream_label = QLabel("Stream:")
        create_layout.add_widget(stream_label)
        self.create_stream_input = self.create_input("Enter stream (e.g., Science, Arts)")
        create_layout.add_widget(self.create_stream_input)

        # Create button
        create_button = self.create_button("Create Student", "primary")
        create_button.clicked.connect(self._on_create_student)
        create_layout.add_widget(create_button)

        create_form.setLayout(create_layout._layout)
        create_section.layout.addWidget(create_form)
        layout.add_widget(create_section)

        # Update Student Section
        update_section = self.create_card("Update Student", "")
        update_form = QWidget()
        update_layout = self.create_flex_layout("column", False)
        update_layout.set_spacing(10)

        # Student ID
        update_student_id_label = QLabel("Student ID:")
        update_layout.add_widget(update_student_id_label)
        self.update_student_id_input = self.create_input("Enter student ID")
        update_layout.add_widget(self.update_student_id_input)

        # New Name
        update_name_label = QLabel("New Name:")
        update_layout.add_widget(update_name_label)
        self.update_name_input = self.create_input("Enter new name")
        update_layout.add_widget(self.update_name_input)

        # New Stream
        update_stream_label = QLabel("New Stream:")
        update_layout.add_widget(update_stream_label)
        self.update_stream_input = self.create_input("Enter new stream")
        update_layout.add_widget(self.update_stream_input)

        # Update button
        update_button = self.create_button("Update Student", "secondary")
        update_button.clicked.connect(self._on_update_student)
        update_layout.add_widget(update_button)

        update_form.setLayout(update_layout._layout)
        update_section.layout.addWidget(update_form)
        layout.add_widget(update_section)

        # Delete Student Section
        delete_section = self.create_card("Delete Student", "")
        delete_form = QWidget()
        delete_layout = self.create_flex_layout("column", False)
        delete_layout.set_spacing(10)

        # Student ID
        delete_student_id_label = QLabel("Student ID:")
        delete_layout.add_widget(delete_student_id_label)
        self.delete_student_id_input = self.create_input("Enter student ID to delete")
        delete_layout.add_widget(self.delete_student_id_input)

        # Delete button
        delete_button = self.create_button("Delete Student", "danger")
        delete_button.clicked.connect(self._on_delete_student)
        delete_layout.add_widget(delete_button)

        delete_form.setLayout(delete_layout._layout)
        delete_section.layout.addWidget(delete_form)
        layout.add_widget(delete_section)

        # View Students Section
        view_section = self.create_card("View Students", "")
        view_form = QWidget()
        view_layout = self.create_flex_layout("column", False)
        view_layout.set_spacing(10)

        # Search box
        self.search_box = self.create_search_box("Search students...")
        self.search_box.search_text_changed.connect(self._on_search_students)
        view_layout.add_widget(self.search_box)

        # Refresh button
        refresh_button = self.create_button("Refresh Students", "secondary")
        refresh_button.clicked.connect(self._refresh_students_table)
        view_layout.add_widget(refresh_button)

        # Students table
        self.students_table = self.create_table(0, 4)
        self.students_table.setHorizontalHeaderLabels(["Student ID", "Name", "Stream", "Actions"])
        view_layout.add_widget(self.students_table)

        view_form.setLayout(view_layout._layout)
        view_section.layout.addWidget(view_form)
        layout.add_widget(view_section)

        tab.setLayout(layout._layout)
        return tab

    def _create_ream_management_tab(self) -> QWidget:
        """Create the ream management tab."""
        tab = QWidget()
        layout = self.create_flex_layout("column", False)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.set_spacing(15)

        # Add Reams Section
        add_ream_section = self.create_card("Add Reams to Student", "")
        add_ream_form = QWidget()
        add_ream_layout = self.create_flex_layout("column", False)
        add_ream_layout.set_spacing(10)

        # Student ID
        add_ream_student_id_label = QLabel("Student ID:")
        add_ream_layout.add_widget(add_ream_student_id_label)
        self.add_ream_student_id_input = self.create_input("Enter student ID")
        add_ream_layout.add_widget(self.add_ream_student_id_input)

        # Reams Count
        reams_count_label = QLabel("Reams Count:")
        add_ream_layout.add_widget(reams_count_label)
        self.add_ream_count_input = self.create_input("Enter number of reams")
        add_ream_layout.add_widget(self.add_ream_count_input)

        # Source
        source_label = QLabel("Source:")
        add_ream_layout.add_widget(source_label)
        self.add_ream_source_combo = QComboBox()
        self.add_ream_source_combo.addItems(["Distribution", "Purchase", "Transfer", "Other"])
        add_ream_layout.add_widget(self.add_ream_source_combo)

        # Add reams button
        add_ream_button = self.create_button("Add Reams", "primary")
        add_ream_button.clicked.connect(self._on_add_reams)
        add_ream_layout.add_widget(add_ream_button)

        add_ream_form.setLayout(add_ream_layout._layout)
        add_ream_section.layout.addWidget(add_ream_form)
        layout.add_widget(add_ream_section)

        # Deduct Reams Section
        deduct_ream_section = self.create_card("Deduct Reams from Student", "")
        deduct_ream_form = QWidget()
        deduct_ream_layout = self.create_flex_layout("column", False)
        deduct_ream_layout.set_spacing(10)

        # Student ID
        deduct_ream_student_id_label = QLabel("Student ID:")
        deduct_ream_layout.add_widget(deduct_ream_student_id_label)
        self.deduct_ream_student_id_input = self.create_input("Enter student ID")
        deduct_ream_layout.add_widget(self.deduct_ream_student_id_input)

        # Reams Count
        deduct_reams_count_label = QLabel("Reams Count:")
        deduct_ream_layout.add_widget(deduct_reams_count_label)
        self.deduct_ream_count_input = self.create_input("Enter number of reams to deduct")
        deduct_ream_layout.add_widget(self.deduct_ream_count_input)

        # Purpose
        purpose_label = QLabel("Purpose:")
        deduct_ream_layout.add_widget(purpose_label)
        self.deduct_ream_purpose_combo = QComboBox()
        self.deduct_ream_purpose_combo.addItems(["Usage", "Transfer", "Loss", "Other"])
        deduct_ream_layout.add_widget(self.deduct_ream_purpose_combo)

        # Deduct reams button
        deduct_ream_button = self.create_button("Deduct Reams", "secondary")
        deduct_ream_button.clicked.connect(self._on_deduct_reams)
        deduct_ream_layout.add_widget(deduct_ream_button)

        deduct_ream_form.setLayout(deduct_ream_layout._layout)
        deduct_ream_section.layout.addWidget(deduct_ream_form)
        layout.add_widget(deduct_ream_section)

        # Transfer Reams Section
        transfer_ream_section = self.create_card("Transfer Reams Between Students", "")
        transfer_ream_form = QWidget()
        transfer_ream_layout = self.create_flex_layout("column", False)
        transfer_ream_layout.set_spacing(10)

        # From Student ID
        from_student_id_label = QLabel("From Student ID:")
        transfer_ream_layout.add_widget(from_student_id_label)
        self.transfer_from_student_id_input = self.create_input("Enter source student ID")
        transfer_ream_layout.add_widget(self.transfer_from_student_id_input)

        # To Student ID
        to_student_id_label = QLabel("To Student ID:")
        transfer_ream_layout.add_widget(to_student_id_label)
        self.transfer_to_student_id_input = self.create_input("Enter destination student ID")
        transfer_ream_layout.add_widget(self.transfer_to_student_id_input)

        # Reams Count
        transfer_reams_count_label = QLabel("Reams Count:")
        transfer_ream_layout.add_widget(transfer_reams_count_label)
        self.transfer_ream_count_input = self.create_input("Enter number of reams to transfer")
        transfer_ream_layout.add_widget(self.transfer_ream_count_input)

        # Reason
        reason_label = QLabel("Reason:")
        transfer_ream_layout.add_widget(reason_label)
        self.transfer_reason_input = self.create_input("Enter reason for transfer")
        transfer_ream_layout.add_widget(self.transfer_reason_input)

        # Transfer reams button
        transfer_ream_button = self.create_button("Transfer Reams", "primary")
        transfer_ream_button.clicked.connect(self._on_transfer_reams)
        transfer_ream_layout.add_widget(transfer_ream_button)

        transfer_ream_form.setLayout(transfer_ream_layout._layout)
        transfer_ream_section.layout.addWidget(transfer_ream_form)
        layout.add_widget(transfer_ream_section)

        # View Ream Transactions Section
        ream_transactions_section = self.create_card("View Ream Transactions", "")
        ream_transactions_form = QWidget()
        ream_transactions_layout = self.create_flex_layout("column", False)
        ream_transactions_layout.set_spacing(10)

        # Student ID for transactions
        transactions_student_id_label = QLabel("Student ID:")
        ream_transactions_layout.add_widget(transactions_student_id_label)
        self.transactions_student_id_input = self.create_input("Enter student ID")
        ream_transactions_layout.add_widget(self.transactions_student_id_input)

        # View transactions button
        view_transactions_button = self.create_button("View Transactions", "secondary")
        view_transactions_button.clicked.connect(self._on_view_ream_transactions)
        ream_transactions_layout.add_widget(view_transactions_button)

        # Ream transactions table
        self.ream_transactions_table = self.create_table(0, 5)
        self.ream_transactions_table.setHorizontalHeaderLabels(["Student ID", "Reams Count", "Date Added", "Type", "Balance"])
        ream_transactions_layout.add_widget(self.ream_transactions_table)

        ream_transactions_form.setLayout(ream_transactions_layout._layout)
        ream_transactions_section.layout.addWidget(ream_transactions_form)
        layout.add_widget(ream_transactions_section)

        tab.setLayout(layout._layout)
        return tab

    def _create_library_activity_tab(self) -> QWidget:
        """Create the library activity tab."""
        tab = QWidget()
        layout = self.create_flex_layout("column", False)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.set_spacing(15)

        # View Borrowed Books Section
        borrowed_section = self.create_card("View Borrowed Books", "")
        borrowed_form = QWidget()
        borrowed_layout = self.create_flex_layout("column", False)
        borrowed_layout.set_spacing(10)

        # Student ID
        borrowed_student_id_label = QLabel("Student ID:")
        borrowed_layout.add_widget(borrowed_student_id_label)
        self.borrowed_student_id_input = self.create_input("Enter student ID")
        borrowed_layout.add_widget(self.borrowed_student_id_input)

        # View borrowed books button
        view_borrowed_button = self.create_button("View Borrowed Books", "primary")
        view_borrowed_button.clicked.connect(self._on_view_borrowed_books)
        borrowed_layout.add_widget(view_borrowed_button)

        # Borrowed books table
        self.borrowed_books_table = self.create_table(0, 5)
        self.borrowed_books_table.setHorizontalHeaderLabels(["Book ID", "Title", "Borrowed On", "Due Date", "Status"])
        borrowed_layout.add_widget(self.borrowed_books_table)

        borrowed_form.setLayout(borrowed_layout._layout)
        borrowed_section.layout.addWidget(borrowed_form)
        layout.add_widget(borrowed_section)

        # View Borrowing History Section
        history_section = self.create_card("View Borrowing History", "")
        history_form = QWidget()
        history_layout = self.create_flex_layout("column", False)
        history_layout.set_spacing(10)

        # Student ID
        history_student_id_label = QLabel("Student ID:")
        history_layout.add_widget(history_student_id_label)
        self.history_student_id_input = self.create_input("Enter student ID")
        history_layout.add_widget(self.history_student_id_input)

        # View history button
        view_history_button = self.create_button("View History", "secondary")
        view_history_button.clicked.connect(self._on_view_borrowing_history)
        history_layout.add_widget(view_history_button)

        # Borrowing history table
        self.borrowing_history_table = self.create_table(0, 6)
        self.borrowing_history_table.setHorizontalHeaderLabels(["Book ID", "Title", "Borrowed On", "Returned On", "Condition", "Fine"])
        history_layout.add_widget(self.borrowing_history_table)

        history_form.setLayout(history_layout._layout)
        history_section.layout.addWidget(history_form)
        layout.add_widget(history_section)

        # View Overdue Books Section
        overdue_section = self.create_card("View Overdue Books", "")
        overdue_form = QWidget()
        overdue_layout = self.create_flex_layout("column", False)
        overdue_layout.set_spacing(10)

        # Student ID
        overdue_student_id_label = QLabel("Student ID:")
        overdue_layout.add_widget(overdue_student_id_label)
        self.overdue_student_id_input = self.create_input("Enter student ID")
        overdue_layout.add_widget(self.overdue_student_id_input)

        # View overdue books button
        view_overdue_button = self.create_button("View Overdue Books", "danger")
        view_overdue_button.clicked.connect(self._on_view_overdue_books)
        overdue_layout.add_widget(view_overdue_button)

        # Overdue books table
        self.overdue_books_table = self.create_table(0, 5)
        self.overdue_books_table.setHorizontalHeaderLabels(["Book ID", "Title", "Borrowed On", "Due Date", "Days Overdue"])
        overdue_layout.add_widget(self.overdue_books_table)

        overdue_form.setLayout(overdue_layout._layout)
        overdue_section.layout.addWidget(overdue_form)
        layout.add_widget(overdue_section)

        tab.setLayout(layout._layout)
        return tab

    def _create_import_export_tab(self) -> QWidget:
        """Create the import/export tab."""
        tab = QWidget()
        layout = self.create_flex_layout("column", False)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.set_spacing(15)

        # Import Students Section
        import_section = self.create_card("Import Students from Excel", "")
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
        import_button = self.create_button("Import Students", "secondary")
        import_button.clicked.connect(self._on_import_students)
        import_layout.add_widget(import_button)

        import_form.setLayout(import_layout._layout)
        import_section.layout.addWidget(import_form)
        layout.add_widget(import_section)

        # Export Students Section
        export_section = self.create_card("Export Students to Excel", "")
        export_form = QWidget()
        export_layout = self.create_flex_layout("column", False)
        export_layout.set_spacing(10)

        # Export button
        export_button = self.create_button("Export All Students", "primary")
        export_button.clicked.connect(self._on_export_students)
        export_layout.add_widget(export_button)

        export_form.setLayout(export_layout._layout)
        export_section.layout.addWidget(export_form)
        layout.add_widget(export_section)

        tab.setLayout(layout._layout)
        return tab

    def _create_reports_tab(self) -> QWidget:
        """Create the reports tab."""
        tab = QWidget()
        layout = self.create_flex_layout("column", False)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.set_spacing(15)

        # Student Summary Section
        summary_section = self.create_card("Student Summary Report", "")
        summary_form = QWidget()
        summary_layout = self.create_flex_layout("column", False)
        summary_layout.set_spacing(10)

        # Student ID
        summary_student_id_label = QLabel("Student ID:")
        summary_layout.add_widget(summary_student_id_label)
        self.summary_student_id_input = self.create_input("Enter student ID")
        summary_layout.add_widget(self.summary_student_id_input)

        # Generate summary button
        generate_summary_button = self.create_button("Generate Summary", "primary")
        generate_summary_button.clicked.connect(self._on_generate_student_summary)
        summary_layout.add_widget(generate_summary_button)

        # Summary results display
        self.summary_results_display = QTextEdit()
        self.summary_results_display.setReadOnly(True)
        self.summary_results_display.setMaximumHeight(200)
        summary_layout.add_widget(self.summary_results_display)

        summary_form.setLayout(summary_layout._layout)
        summary_section.layout.addWidget(summary_form)
        layout.add_widget(summary_section)

        # Stream Analysis Section
        stream_section = self.create_card("Stream Analysis Report", "")
        stream_form = QWidget()
        stream_layout = self.create_flex_layout("column", False)
        stream_layout.set_spacing(10)

        # Stream
        stream_label = QLabel("Stream:")
        stream_layout.add_widget(stream_label)
        self.stream_analysis_stream_input = self.create_input("Enter stream name")
        stream_layout.add_widget(self.stream_analysis_stream_input)

        # Generate stream analysis button
        generate_stream_button = self.create_button("Generate Stream Analysis", "secondary")
        generate_stream_button.clicked.connect(self._on_generate_stream_analysis)
        stream_layout.add_widget(generate_stream_button)

        # Stream analysis results display
        self.stream_analysis_results_display = QTextEdit()
        self.stream_analysis_results_display.setReadOnly(True)
        self.stream_analysis_results_display.setMaximumHeight(200)
        stream_layout.add_widget(self.stream_analysis_results_display)

        stream_form.setLayout(stream_layout._layout)
        stream_section.layout.addWidget(stream_form)
        layout.add_widget(stream_section)

        # Ream Usage Section
        ream_section = self.create_card("Ream Usage Report", "")
        ream_form = QWidget()
        ream_layout = self.create_flex_layout("column", False)
        ream_layout.set_spacing(10)

        # Student ID
        ream_student_id_label = QLabel("Student ID:")
        ream_layout.add_widget(ream_student_id_label)
        self.ream_usage_student_id_input = self.create_input("Enter student ID")
        ream_layout.add_widget(self.ream_usage_student_id_input)

        # Generate ream usage button
        generate_ream_button = self.create_button("Generate Ream Usage Report", "primary")
        generate_ream_button.clicked.connect(self._on_generate_ream_usage_report)
        ream_layout.add_widget(generate_ream_button)

        # Ream usage results display
        self.ream_usage_results_display = QTextEdit()
        self.ream_usage_results_display.setReadOnly(True)
        self.ream_usage_results_display.setMaximumHeight(200)
        ream_layout.add_widget(self.ream_usage_results_display)

        ream_form.setLayout(ream_layout._layout)
        ream_section.layout.addWidget(ream_form)
        layout.add_widget(ream_section)

        tab.setLayout(layout._layout)
        return tab

    # Event handlers for Student Management
    def _on_create_student(self):
        """Handle create student button click."""
        try:
            student_data = {
                'student_id': self.create_student_id_input.text().strip(),
                'name': self.create_name_input.text().strip(),
                'stream': self.create_stream_input.text().strip()
            }

            # Validate required fields
            if not student_data['student_id'] or not student_data['name']:
                show_error_message("Validation Error", "Student ID and Name are required", self)
                return

            student = self.student_service.create_student(student_data)
            show_success_message("Success", f"Student created successfully with ID: {student.student_id}", self)
            self._refresh_students_table()

            # Clear form
            self.create_student_id_input.clear()
            self.create_name_input.clear()
            self.create_stream_input.clear()

        except (ValidationError, DatabaseException) as e:
            show_error_message("Error", str(e), self)
        except Exception as e:
            show_error_message("Error", f"An error occurred: {str(e)}", self)

    def _on_update_student(self):
        """Handle update student button click."""
        try:
            student_id = self.update_student_id_input.text().strip()
            student_data = {}

            if self.update_name_input.text().strip():
                student_data['name'] = self.update_name_input.text().strip()
            if self.update_stream_input.text().strip():
                student_data['stream'] = self.update_stream_input.text().strip()

            if not student_data:
                show_error_message("Error", "Please provide at least one field to update", self)
                return

            student = self.student_service.update_student(student_id, student_data)
            if student:
                show_success_message("Success", f"Student updated successfully", self)
                self._refresh_students_table()
            else:
                show_error_message("Error", "Student not found", self)

        except Exception as e:
            show_error_message("Error", f"An error occurred: {str(e)}", self)

    def _on_delete_student(self):
        """Handle delete student button click."""
        try:
            student_id = self.delete_student_id_input.text().strip()

            if not student_id:
                show_error_message("Validation Error", "Student ID is required", self)
                return

            # Confirm deletion
            confirm = QMessageBox.question(
                self, "Confirm Deletion", 
                f"Are you sure you want to delete student with ID: {student_id}?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
            )

            if confirm == QMessageBox.StandardButton.Yes:
                success = self.student_service.delete_student(student_id)
                if success:
                    show_success_message("Success", "Student deleted successfully", self)
                    self._refresh_students_table()
                else:
                    show_error_message("Error", "Student not found", self)

        except Exception as e:
            show_error_message("Error", f"An error occurred: {str(e)}", self)

    def _on_search_students(self, query: str):
        """Handle student search."""
        try:
            # For now, just refresh the table (search functionality would need to be implemented in service)
            self._refresh_students_table()
        except Exception as e:
            show_error_message("Error", f"Search failed: {str(e)}", self)

    def _refresh_students_table(self):
        """Refresh the students table."""
        try:
            students = self.student_service.get_all_students()
            self._populate_students_table(students)
        except Exception as e:
            show_error_message("Error", f"Failed to refresh students: {str(e)}", self)

    def _populate_students_table(self, students):
        """Populate the students table with data."""
        self.students_table.setRowCount(0)

        for student in students:
            row_position = self.students_table.rowCount()
            self.students_table.insertRow(row_position)

            self.students_table.setItem(row_position, 0, QTableWidgetItem(str(student.student_id)))
            self.students_table.setItem(row_position, 1, QTableWidgetItem(student.name))
            self.students_table.setItem(row_position, 2, QTableWidgetItem(student.stream or ""))

            # Add view button
            view_button = QPushButton("View")
            view_button.clicked.connect(lambda _, sid=student.student_id: self._view_student_details(sid))
            self.students_table.setCellWidget(row_position, 3, view_button)

    def _view_student_details(self, student_id: str):
        """View detailed information about a student."""
        try:
            student = self.student_service.get_student_by_id(student_id)
            if student:
                details = f"Student Details:\n\nID: {student.student_id}\nName: {student.name}\nStream: {student.stream}"
                show_success_message("Student Details", details, self)
            else:
                show_error_message("Error", "Student not found", self)
        except Exception as e:
            show_error_message("Error", f"Failed to view student details: {str(e)}", self)

    # Event handlers for Ream Management
    def _on_add_reams(self):
        """Handle add reams button click."""
        try:
            student_id = self.add_ream_student_id_input.text().strip()
            reams_count = int(self.add_ream_count_input.text().strip())
            source = self.add_ream_source_combo.currentText()

            if not student_id or reams_count <= 0:
                show_error_message("Validation Error", "Student ID and positive reams count are required", self)
                return

            entry = self.student_service.add_reams_to_student(student_id, reams_count, source)
            show_success_message("Success", f"Added {reams_count} reams to student {student_id}", self)

            # Clear form
            self.add_ream_student_id_input.clear()
            self.add_ream_count_input.clear()

        except ValueError:
            show_error_message("Error", "Invalid reams count", self)
        except Exception as e:
            show_error_message("Error", f"An error occurred: {str(e)}", self)

    def _on_deduct_reams(self):
        """Handle deduct reams button click."""
        try:
            student_id = self.deduct_ream_student_id_input.text().strip()
            reams_count = int(self.deduct_ream_count_input.text().strip())
            purpose = self.deduct_ream_purpose_combo.currentText()

            if not student_id or reams_count <= 0:
                show_error_message("Validation Error", "Student ID and positive reams count are required", self)
                return

            entry = self.student_service.deduct_reams_from_student(student_id, reams_count, purpose)
            show_success_message("Success", f"Deducted {reams_count} reams from student {student_id}", self)

            # Clear form
            self.deduct_ream_student_id_input.clear()
            self.deduct_ream_count_input.clear()

        except ValueError:
            show_error_message("Error", "Invalid reams count", self)
        except Exception as e:
            show_error_message("Error", f"An error occurred: {str(e)}", self)

    def _on_transfer_reams(self):
        """Handle transfer reams button click."""
        try:
            from_student_id = self.transfer_from_student_id_input.text().strip()
            to_student_id = self.transfer_to_student_id_input.text().strip()
            reams_count = int(self.transfer_ream_count_input.text().strip())
            reason = self.transfer_reason_input.text().strip()

            if not from_student_id or not to_student_id or reams_count <= 0:
                show_error_message("Validation Error", "Both student IDs and positive reams count are required", self)
                return

            success = self.student_service.transfer_reams_between_students(
                from_student_id, to_student_id, reams_count, reason
            )

            if success:
                show_success_message("Success", f"Transferred {reams_count} reams from {from_student_id} to {to_student_id}", self)
                # Clear form
                self.transfer_from_student_id_input.clear()
                self.transfer_to_student_id_input.clear()
                self.transfer_ream_count_input.clear()
                self.transfer_reason_input.clear()
            else:
                show_error_message("Error", "Failed to transfer reams", self)

        except ValueError:
            show_error_message("Error", "Invalid reams count", self)
        except Exception as e:
            show_error_message("Error", f"An error occurred: {str(e)}", self)

    def _on_view_ream_transactions(self):
        """Handle view ream transactions button click."""
        try:
            student_id = self.transactions_student_id_input.text().strip()

            if not student_id:
                show_error_message("Validation Error", "Student ID is required", self)
                return

            transactions = self.student_service.get_student_ream_transaction_history(student_id)
            self._populate_ream_transactions_table(transactions)

        except Exception as e:
            show_error_message("Error", f"An error occurred: {str(e)}", self)

    def _populate_ream_transactions_table(self, transactions):
        """Populate the ream transactions table with data."""
        self.ream_transactions_table.setRowCount(0)

        # Get current balance for the student
        current_balance = 0
        if transactions:
            current_balance = self.student_service.get_student_ream_balance(transactions[0].student_id)

        for transaction in transactions:
            row_position = self.ream_transactions_table.rowCount()
            self.ream_transactions_table.insertRow(row_position)

            self.ream_transactions_table.setItem(row_position, 0, QTableWidgetItem(str(transaction.student_id)))
            self.ream_transactions_table.setItem(row_position, 1, QTableWidgetItem(str(transaction.reams_count)))
            self.ream_transactions_table.setItem(row_position, 2, QTableWidgetItem(transaction.date_added or ""))
            self.ream_transactions_table.setItem(row_position, 3, QTableWidgetItem("Add" if transaction.reams_count > 0 else "Deduct"))
            self.ream_transactions_table.setItem(row_position, 4, QTableWidgetItem(str(current_balance)))

    # Event handlers for Library Activity
    def _on_view_borrowed_books(self):
        """Handle view borrowed books button click."""
        try:
            student_id = self.borrowed_student_id_input.text().strip()

            if not student_id:
                show_error_message("Validation Error", "Student ID is required", self)
                return

            books = self.student_service.get_student_current_borrowed_books(student_id)
            self._populate_borrowed_books_table(books)

        except Exception as e:
            show_error_message("Error", f"An error occurred: {str(e)}", self)

    def _populate_borrowed_books_table(self, books):
        """Populate the borrowed books table with data."""
        self.borrowed_books_table.setRowCount(0)

        for book in books:
            row_position = self.borrowed_books_table.rowCount()
            self.borrowed_books_table.insertRow(row_position)

            self.borrowed_books_table.setItem(row_position, 0, QTableWidgetItem(str(book.book_id)))
            self.borrowed_books_table.setItem(row_position, 1, QTableWidgetItem(book.title or ""))
            self.borrowed_books_table.setItem(row_position, 2, QTableWidgetItem(book.borrowed_on or ""))
            self.borrowed_books_table.setItem(row_position, 3, QTableWidgetItem(book.due_date or ""))
            self.borrowed_books_table.setItem(row_position, 4, QTableWidgetItem("Borrowed"))

    def _on_view_borrowing_history(self):
        """Handle view borrowing history button click."""
        try:
            student_id = self.history_student_id_input.text().strip()

            if not student_id:
                show_error_message("Validation Error", "Student ID is required", self)
                return

            history = self.student_service.get_student_borrowing_history(student_id)
            self._populate_borrowing_history_table(history)

        except Exception as e:
            show_error_message("Error", f"An error occurred: {str(e)}", self)

    def _populate_borrowing_history_table(self, history):
        """Populate the borrowing history table with data."""
        self.borrowing_history_table.setRowCount(0)

        for record in history:
            row_position = self.borrowing_history_table.rowCount()
            self.borrowing_history_table.insertRow(row_position)

            self.borrowing_history_table.setItem(row_position, 0, QTableWidgetItem(str(record.book_id)))
            self.borrowing_history_table.setItem(row_position, 1, QTableWidgetItem(record.title or ""))
            self.borrowing_history_table.setItem(row_position, 2, QTableWidgetItem(record.borrowed_on or ""))
            self.borrowing_history_table.setItem(row_position, 3, QTableWidgetItem(record.returned_on or ""))
            self.borrowing_history_table.setItem(row_position, 4, QTableWidgetItem(record.return_condition or ""))
            self.borrowing_history_table.setItem(row_position, 5, QTableWidgetItem(str(record.fine_amount or 0)))

    def _on_view_overdue_books(self):
        """Handle view overdue books button click."""
        try:
            student_id = self.overdue_student_id_input.text().strip()

            if not student_id:
                show_error_message("Validation Error", "Student ID is required", self)
                return

            books = self.student_service.get_student_overdue_books(student_id)
            self._populate_overdue_books_table(books)

        except Exception as e:
            show_error_message("Error", f"An error occurred: {str(e)}", self)

    def _populate_overdue_books_table(self, books):
        """Populate the overdue books table with data."""
        self.overdue_books_table.setRowCount(0)

        for book in books:
            row_position = self.overdue_books_table.rowCount()
            self.overdue_books_table.insertRow(row_position)

            self.overdue_books_table.setItem(row_position, 0, QTableWidgetItem(str(book.book_id)))
            self.overdue_books_table.setItem(row_position, 1, QTableWidgetItem(book.title or ""))
            self.overdue_books_table.setItem(row_position, 2, QTableWidgetItem(book.borrowed_on or ""))
            self.overdue_books_table.setItem(row_position, 3, QTableWidgetItem(book.due_date or ""))
            self.overdue_books_table.setItem(row_position, 4, QTableWidgetItem(str(book.days_overdue or 0)))

    # Event handlers for Import/Export
    def _on_browse_import_file(self):
        """Handle browse import file button click."""
        file_dialog = QFileDialog()
        file_path, _ = file_dialog.getOpenFileName(self, "Select Excel File", "", "Excel Files (*.xlsx *.xls)")

        if file_path:
            self.import_file_label.setText(file_path)
            self.import_file_path = file_path

    def _on_import_students(self):
        """Handle import students button click."""
        try:
            if not hasattr(self, 'import_file_path'):
                show_error_message("Error", "Please select a file first", self)
                return

            students = self.student_service.import_students_from_excel(self.import_file_path)
            show_success_message("Success", f"Imported {len(students)} students successfully", self)
            self._refresh_students_table()

        except Exception as e:
            show_error_message("Error", f"Import failed: {str(e)}", self)

    def _on_export_students(self):
        """Handle export students button click."""
        try:
            file_dialog = QFileDialog()
            file_path, _ = file_dialog.getSaveFileName(self, "Save Excel File", "students_export.xlsx", "Excel Files (*.xlsx)")

            if file_path:
                success = self.student_service.export_students_to_excel(file_path)
                if success:
                    show_success_message("Success", "Students exported successfully", self)
                else:
                    show_error_message("Error", "Export failed", self)

        except Exception as e:
            show_error_message("Error", f"Export failed: {str(e)}", self)

    # Event handlers for Reports
    def _on_generate_student_summary(self):
        """Handle generate student summary button click."""
        try:
            student_id = self.summary_student_id_input.text().strip()

            if not student_id:
                show_error_message("Validation Error", "Student ID is required", self)
                return

            # Get student summary data
            student = self.student_service.get_student_by_id(student_id)
            if not student:
                show_error_message("Error", "Student not found", self)
                return

            # Get library activity summary
            library_summary = self.student_service.get_student_library_activity_summary(student_id)

            # Get ream balance
            ream_balance = self.student_service.get_student_ream_balance(student_id)

            # Generate summary report
            report_text = f"Student Summary Report for {student.name} (ID: {student.student_id})\n\n"
            report_text += f"Stream: {student.stream}\n"
            report_text += f"Ream Balance: {ream_balance}\n\n"
            report_text += "Library Activity:\n"
            report_text += f"  Total Books Borrowed: {library_summary.get('total_books_borrowed', 0)}\n"
            report_text += f"  Current Books Borrowed: {library_summary.get('current_books_borrowed', 0)}\n"
            report_text += f"  Overdue Books: {library_summary.get('overdue_books', 0)}\n"
            report_text += f"  Books Read: {library_summary.get('books_read', 0)}\n"

            self.summary_results_display.setText(report_text)

        except Exception as e:
            show_error_message("Error", f"Failed to generate report: {str(e)}", self)

    def _on_generate_stream_analysis(self):
        """Handle generate stream analysis button click."""
        try:
            stream = self.stream_analysis_stream_input.text().strip()

            if not stream:
                show_error_message("Validation Error", "Stream name is required", self)
                return

            # Get stream analysis data
            stream_data = self.student_service.get_stream_ream_usage(stream)

            # Generate stream analysis report
            report_text = f"Stream Analysis Report for {stream}\n\n"
            report_text += f"Total Students: {stream_data.get('total_students', 0)}\n"
            report_text += f"Total Ream Usage: {stream_data.get('total_ream_usage', 0)}\n"
            report_text += f"Average per Student: {stream_data.get('average_per_student', 0):.2f}\n"

            self.stream_analysis_results_display.setText(report_text)

        except Exception as e:
            show_error_message("Error", f"Failed to generate report: {str(e)}", self)

    def _on_generate_ream_usage_report(self):
        """Handle generate ream usage report button click."""
        try:
            student_id = self.ream_usage_student_id_input.text().strip()

            if not student_id:
                show_error_message("Validation Error", "Student ID is required", self)
                return

            # Get ream usage summary
            ream_summary = self.student_service.get_student_ream_summary(student_id)

            # Generate ream usage report
            report_text = f"Ream Usage Report for Student ID: {student_id}\n\n"
            report_text += f"Current Balance: {ream_summary.get('current_balance', 0)}\n"
            report_text += f"Total Reams Added: {ream_summary.get('total_reams_added', 0)}\n"
            report_text += f"Total Reams Used: {ream_summary.get('total_reams_used', 0)}\n"
            report_text += f"Total Transactions: {ream_summary.get('total_transactions', 0)}\n"
            report_text += f"Average Daily Usage: {ream_summary.get('average_daily_usage', 0):.2f}\n"

            self.ream_usage_results_display.setText(report_text)

        except Exception as e:
            show_error_message("Error", f"Failed to generate report: {str(e)}", self)