"""
View Students Window

Dedicated window for viewing and managing students list.
"""

from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QTableWidget, QTableWidgetItem, QComboBox, QListWidget, QSizePolicy
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont
from typing import Optional

from school_system.gui.windows.base_function_window import BaseFunctionWindow
from school_system.gui.dialogs.message_dialog import show_error_message, show_success_message
from school_system.config.logging import logger
from school_system.services.student_service import StudentService
from school_system.gui.windows.student_window.student_workflow_components import (
    StudentCreationWorkflow, StudentUpdateWorkflow, StudentDeletionWorkflow
)


class ViewStudentsWindow(BaseFunctionWindow):
    """Dedicated window for viewing and managing students."""
    
    def __init__(self, parent=None, current_user: str = "", current_role: str = ""):
        """Initialize the view students window."""
        super().__init__("View Students", parent, current_user, current_role)

        self.student_service = StudentService()
        self.students_table = None
        self.action_bar_layout = None  # Reference to action bar layout

        # Setup content
        self.setup_content()
    
    def setup_content(self):
        """Setup the main content area."""
        # Create main content layout
        main_layout = self.create_flex_layout("column", False)
        main_layout.set_margins(24, 24, 24, 24)
        main_layout.set_spacing(16)
        
        # Action bar with search and filters
        action_bar = self._create_action_bar()
        main_layout.add_widget(action_bar)
        
        # Students table
        students_card = self._create_students_table()
        main_layout.add_widget(students_card, stretch=1)
        
        # Add to content
        self.add_layout_to_content(main_layout)

        # Load initial data after table is created
        self._refresh_students_table()

    def add_button_to_action_bar(self, button: QPushButton, position: int = -1):
        """
        Add a button to the action bar.

        Args:
            button: Button to add
            position: Position to insert (default: append to end)
        """
        if self.action_bar_layout is not None:
            if position == -1:
                self.action_bar_layout.addWidget(button)
            else:
                self.action_bar_layout.insertWidget(position, button)

    def _create_action_bar(self) -> QWidget:
        """Create the action bar with search, filters, and action buttons."""
        theme_manager = self.get_theme_manager()
        theme = theme_manager._themes[self.get_theme()]

        action_card = QWidget()
        action_card.setProperty("card", "true")
        action_card.setFixedHeight(80)
        action_card.setStyleSheet(f"""
            QWidget[card="true"] {{
                background-color: {theme["surface"]};
                border: 1px solid {theme["border"]};
                border-radius: 12px;
                padding: 16px;
            }}
        """)

        action_layout = QHBoxLayout(action_card)
        self.action_bar_layout = action_layout  # Store reference to the layout
        action_layout.setContentsMargins(16, 16, 16, 16)
        action_layout.setSpacing(12)
        
        # Search box
        self.search_box = self.create_search_box("Search students by name, ID, or stream...")
        self.search_box.setMinimumWidth(250)
        self.search_box.search_text_changed.connect(self._on_search)
        action_layout.addWidget(self.search_box)
        
        # Class filter
        self.class_filter = QComboBox()
        self.class_filter.addItem("All Classes")
        self.class_filter.setMinimumWidth(150)
        self.class_filter.currentTextChanged.connect(self._on_class_filter_changed)
        action_layout.addWidget(self.class_filter)

        # Stream filter
        self.stream_filter = QComboBox()
        self.stream_filter.addItem("All Streams")
        self.stream_filter.setMinimumWidth(150)
        self.stream_filter.currentTextChanged.connect(self._on_filter_changed)
        action_layout.addWidget(self.stream_filter)

        # Populate filters
        self._populate_class_filter()
        self._populate_stream_filter()
        
        action_layout.addStretch()
        
        # Action buttons
        add_btn = self.create_button("➕ Add Student", "primary")
        add_btn.clicked.connect(self._on_add_student)
        action_layout.addWidget(add_btn)
        
        edit_btn = self.create_button("✏️ Edit", "secondary")
        edit_btn.clicked.connect(self._on_edit_student)
        action_layout.addWidget(edit_btn)
        
        delete_btn = self.create_button("🗑️ Delete", "danger")
        delete_btn.clicked.connect(self._on_delete_student)
        action_layout.addWidget(delete_btn)
        
        refresh_btn = self.create_button("🔄 Refresh", "outline")
        refresh_btn.clicked.connect(self._refresh_students_table)
        action_layout.addWidget(refresh_btn)
        
        return action_card
    
    def _create_students_table(self) -> QWidget:
        """Create the students table card."""
        theme_manager = self.get_theme_manager()
        theme = theme_manager._themes[self.get_theme()]
        
        table_card = QWidget()
        table_card.setProperty("card", "true")
        table_card.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        table_card.setMinimumHeight(250)
        table_card.setStyleSheet(f"""
            QWidget[card="true"] {{
                background-color: {theme["surface"]};
                border: 1px solid {theme["border"]};
                border-radius: 12px;
                padding: 24px;
            }}
        """)
        
        table_layout = QVBoxLayout(table_card)
        table_layout.setContentsMargins(0, 0, 0, 0)
        table_layout.setSpacing(12)
        
        # Table title
        title_label = QLabel("Students List")
        title_font = QFont("Segoe UI", 16, QFont.Weight.Medium)
        title_label.setFont(title_font)
        title_label.setStyleSheet(f"color: {theme["text"]}; margin-bottom: 8px;")
        table_layout.addWidget(title_label)
        
        # Students table
        self.students_table = self.create_table(0, 6)
        self.students_table.setColumnCount(6)  # Ensure columns are set
        self.students_table.setHorizontalHeaderLabels(["Student ID", "Name", "Class", "Stream", "Legacy Stream", "Actions"])
        self.students_table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.students_table.setAlternatingRowColors(True)
        self.students_table.setMinimumHeight(150)
        self.students_table.setMinimumWidth(400)
        table_layout.addWidget(self.students_table)
        
        return table_card
    
    def _populate_class_filter(self):
        """Populate the class filter with available classes."""
        try:
            classes = self.student_service.get_all_classes()
            current_class = self.class_filter.currentText()

            self.class_filter.clear()
            self.class_filter.addItem("All Classes")
            for class_name in classes:
                self.class_filter.addItem(class_name)

            # Restore selection if possible
            index = self.class_filter.findText(current_class)
            if index >= 0:
                self.class_filter.setCurrentIndex(index)
        except Exception as e:
            logger.error(f"Error populating class filter: {e}")

    def _populate_stream_filter(self):
        """Populate the stream filter with available streams."""
        try:
            selected_class = self.class_filter.currentText()
            if selected_class and selected_class != "All Classes":
                streams = self.student_service.get_streams_for_class(selected_class)
            else:
                streams = self.student_service.get_all_stream_names()

            current_stream = self.stream_filter.currentText()

            self.stream_filter.clear()
            self.stream_filter.addItem("All Streams")
            for stream in streams:
                self.stream_filter.addItem(stream)

            # Restore selection if possible
            index = self.stream_filter.findText(current_stream)
            if index >= 0:
                self.stream_filter.setCurrentIndex(index)
        except Exception as e:
            logger.error(f"Error populating stream filter: {e}")

    def _on_class_filter_changed(self):
        """Handle class filter change - repopulate stream filter."""
        self._populate_stream_filter()
        self._refresh_students_table()
    
    def _refresh_students_table(self):
        """Refresh the students table with current data."""
        try:
            # Get filters
            class_filter = self.class_filter.currentText()
            stream_filter = self.stream_filter.currentText()

            class_name = None if class_filter == "All Classes" else class_filter
            stream_name = None if stream_filter == "All Streams" else stream_filter

            # Get students based on filters
            if class_name and stream_name:
                students = self.student_service.get_students_by_class_and_stream(class_name, stream_name)
            elif class_name:
                students = self.student_service.get_students_by_class(class_name)
            elif stream_name:
                students = self.student_service.get_students_by_stream_name(stream_name)
            else:
                students = self.student_service.get_all_students()
            
            # Clear table
            self.students_table.setRowCount(0)
            
            # Populate table
            for student in students:
                row = self.students_table.rowCount()
                self.students_table.insertRow(row)
                
                self.students_table.setItem(row, 0, QTableWidgetItem(student.student_id))
                self.students_table.setItem(row, 1, QTableWidgetItem(student.name))
                self.students_table.setItem(row, 2, QTableWidgetItem(student.class_name or ""))
                self.students_table.setItem(row, 3, QTableWidgetItem(student.stream_name or ""))
                self.students_table.setItem(row, 4, QTableWidgetItem(student.stream))

                # Actions column (can add buttons here if needed)
                self.students_table.setItem(row, 5, QTableWidgetItem(""))

            # Resize columns to fit content
            self.students_table.resizeColumnsToContents()
            self.students_table.resizeRowsToContents()

            # Ensure minimum height for visibility
            if self.students_table.rowCount() > 0:
                self.students_table.setMinimumHeight(200)

            # Force layout update
            self.students_table.update()
            self.students_table.repaint()
            table_card = self.students_table.parent()
            if table_card:
                table_card.update()
                table_card.repaint()

            logger.info(f"Refreshed students table with {len(students)} students")
            logger.debug(f"Table row count: {self.students_table.rowCount()}, column count: {self.students_table.columnCount()}")
            logger.debug(f"Table is visible: {self.students_table.isVisible()}")
            logger.debug(f"Table size: {self.students_table.size()}")
        except Exception as e:
            logger.error(f"Error refreshing students table: {e}")
            show_error_message("Error", f"Failed to refresh students: {str(e)}", self)
    
    def _on_search(self, text: str):
        """Handle search text change."""
        # Filter table based on search text
        for row in range(self.students_table.rowCount()):
            match = False
            for col in range(3):  # Check first 3 columns
                item = self.students_table.item(row, col)
                if item and text.lower() in item.text().lower():
                    match = True
                    break
            self.students_table.setRowHidden(row, not match)
    
    def _on_filter_changed(self, text: str):
        """Handle filter change."""
        self._refresh_students_table()
    
    def _on_add_student(self):
        """Open add student window."""
        from school_system.gui.windows.student_window.add_student_window import AddStudentWindow
        add_window = AddStudentWindow(self, self.current_user, self.current_role)
        add_window.student_added.connect(self._refresh_students_table)
        add_window.show()
    
    def _on_edit_student(self):
        """Open edit student window."""
        selected_rows = self.students_table.selectionModel().selectedRows()
        if not selected_rows:
            show_error_message("No Selection", "Please select a student to edit.", self)
            return
        
        student_id = self.students_table.item(selected_rows[0].row(), 0).text()
        from school_system.gui.windows.student_window.edit_student_window import EditStudentWindow
        edit_window = EditStudentWindow(student_id, self, self.current_user, self.current_role)
        edit_window.student_updated.connect(self._refresh_students_table)
        edit_window.show()
    
    def _on_delete_student(self):
        """Handle delete student."""
        selected_rows = self.students_table.selectionModel().selectedRows()
        if not selected_rows:
            show_error_message("No Selection", "Please select a student to delete.", self)
            return
        
        student_id = self.students_table.item(selected_rows[0].row(), 0).text()
        from school_system.gui.dialogs.confirm_dialog import ConfirmationDialog
        dialog = ConfirmationDialog(
            title="Delete Student",
            message=f"Are you sure you want to delete student {student_id}?\n\nThis action cannot be undone.",
            parent=self,
            confirm_text="Delete",
            cancel_text="Cancel"
        )
        
        if dialog.exec() == ConfirmationDialog.DialogCode.Accepted:
            try:
                self.student_service.delete_student(student_id)
                show_success_message("Success", f"Student {student_id} deleted successfully.", self)
                self._refresh_students_table()
            except Exception as e:
                show_error_message("Error", f"Failed to delete student: {str(e)}", self)
