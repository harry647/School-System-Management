"""
Class Management Window

Dedicated window for managing student classes and sections.
"""

from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QTableWidget, QTableWidgetItem, QLineEdit, QComboBox, QListWidget, QListWidgetItem, QSplitter
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont
from typing import List, Optional

from school_system.gui.windows.base_function_window import BaseFunctionWindow
from school_system.gui.dialogs.message_dialog import show_error_message, show_success_message
from school_system.config.logging import logger
from school_system.services.student_service import StudentService


class ClassManagementWindow(BaseFunctionWindow):
    """Dedicated window for managing student classes and sections."""

    def __init__(self, parent=None, current_user: str = "", current_role: str = ""):
        """Initialize the class management window."""
        super().__init__("Class Management", parent, current_user, current_role)

        self.student_service = StudentService()
        # For now, use a simple dictionary to store class information
        # In a real implementation, this would be backed by a database
        self.classes = {}  # class_id -> {"name": str, "stream": str, "students": set}

        # Setup content
        self.setup_content()

        # Load initial data
        self._refresh_classes()

    def setup_content(self):
        """Setup the main content area."""
        # Create main content layout
        main_layout = self.create_flex_layout("column", False)
        main_layout.setContentsMargins(24, 24, 24, 24)
        main_layout.setSpacing(20)

        # Create splitter for classes and students
        splitter = QSplitter(Qt.Orientation.Horizontal)

        # Left panel - Classes
        classes_panel = self._create_classes_panel()
        splitter.addWidget(classes_panel)

        # Right panel - Students in selected class
        students_panel = self._create_students_panel()
        splitter.addWidget(students_panel)

        # Set splitter proportions
        splitter.setSizes([400, 600])

        main_layout.add_widget(splitter, stretch=1)

        # Add to content
        self.add_layout_to_content(main_layout)

    def _create_classes_panel(self) -> QWidget:
        """Create the classes management panel."""
        theme_manager = self.get_theme_manager()
        theme = theme_manager._themes[self.get_theme()]

        panel = QWidget()
        layout = QVBoxLayout(panel)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(16)

        # Header
        header_label = QLabel("📚 Classes")
        header_font = QFont("Segoe UI", 16, QFont.Weight.SemiBold)
        header_label.setFont(header_font)
        header_label.setStyleSheet(f"color: {theme["text"]}; margin-bottom: 8px;")
        layout.addWidget(header_label)

        # Add class section
        add_class_card = QWidget()
        add_class_card.setProperty("card", "true")
        add_class_card.setStyleSheet(f"""
            QWidget[card="true"] {{
                background-color: {theme["surface"]};
                border: 1px solid {theme["border"]};
                border-radius: 12px;
                padding: 16px;
            }}
        """)

        add_layout = QVBoxLayout(add_class_card)
        add_layout.setSpacing(12)

        # Class name input
        name_layout = QVBoxLayout()
        name_label = QLabel("Class Name:")
        name_label.setStyleSheet(f"font-weight: 500; color: {theme["text"]};")
        name_layout.addWidget(name_label)

        self.class_name_input = self.create_input("Enter class name (e.g., Class 10-A)")
        self.class_name_input.setFixedHeight(44)
        name_layout.addWidget(self.class_name_input)
        add_layout.addLayout(name_layout)

        # Stream selection
        stream_layout = QVBoxLayout()
        stream_label = QLabel("Stream:")
        stream_label.setStyleSheet(f"font-weight: 500; color: {theme["text"]};")
        stream_layout.addWidget(stream_label)

        self.class_stream_combo = QComboBox()
        self.class_stream_combo.addItems(["Science", "Arts", "Commerce"])
        self.class_stream_combo.setEditable(True)
        self.class_stream_combo.setFixedHeight(44)
        stream_layout.addWidget(self.class_stream_combo)
        add_layout.addLayout(stream_layout)

        # Add class button
        add_btn = self.create_button("➕ Add Class", "primary")
        add_btn.clicked.connect(self._add_class)
        add_layout.addWidget(add_btn)

        layout.addWidget(add_class_card)

        # Classes list
        list_card = QWidget()
        list_card.setProperty("card", "true")
        list_card.setStyleSheet(f"""
            QWidget[card="true"] {{
                background-color: {theme["surface"]};
                border: 1px solid {theme["border"]};
                border-radius: 12px;
                padding: 16px;
            }}
        """)

        list_layout = QVBoxLayout(list_card)

        # List header with actions
        list_header = QHBoxLayout()
        list_title = QLabel("Existing Classes")
        list_title.setStyleSheet(f"font-weight: 600; color: {theme["text"]};")
        list_header.addWidget(list_title)

        list_header.addStretch()

        refresh_btn = self.create_button("🔄", "outline")
        refresh_btn.setFixedWidth(40)
        refresh_btn.clicked.connect(self._refresh_classes)
        list_header.addWidget(refresh_btn)

        list_layout.addLayout(list_header)

        # Classes list
        self.classes_list = QListWidget()
        self.classes_list.setSelectionMode(QListWidget.SelectionMode.SingleSelection)
        self.classes_list.itemSelectionChanged.connect(self._on_class_selected)
        self.classes_list.setStyleSheet(f"""
            QListWidget {{
                background-color: {theme["background"]};
                border: 1px solid {theme["border"]};
                border-radius: 8px;
                padding: 8px;
            }}
            QListWidget::item {{
                padding: 8px;
                border-bottom: 1px solid {theme["border"]};
            }}
            QListWidget::item:selected {{
                background-color: {theme["primary"]};
                color: white;
            }}
        """)
        list_layout.addWidget(self.classes_list)

        # Class actions
        actions_layout = QHBoxLayout()
        actions_layout.setSpacing(8)

        edit_btn = self.create_button("✏️ Edit", "secondary")
        edit_btn.clicked.connect(self._edit_class)
        actions_layout.addWidget(edit_btn)

        delete_btn = self.create_button("🗑️ Delete", "danger")
        delete_btn.clicked.connect(self._delete_class)
        actions_layout.addWidget(delete_btn)

        list_layout.addLayout(actions_layout)

        layout.addWidget(list_card, stretch=1)

        return panel

    def _create_students_panel(self) -> QWidget:
        """Create the students in class panel."""
        theme_manager = self.get_theme_manager()
        theme = theme_manager._themes[self.get_theme()]

        panel = QWidget()
        layout = QVBoxLayout(panel)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(16)

        # Header
        header_label = QLabel("👨‍🎓 Students in Class")
        header_font = QFont("Segoe UI", 16, QFont.Weight.SemiBold)
        header_label.setFont(header_font)
        header_label.setStyleSheet(f"color: {theme["text"]}; margin-bottom: 8px;")
        layout.addWidget(header_label)

        # Current class display
        self.current_class_label = QLabel("No class selected")
        self.current_class_label.setStyleSheet(f"""
            color: {theme["text_secondary"]};
            font-style: italic;
            padding: 8px;
            background-color: {theme["surface"]};
            border-radius: 8px;
        """)
        layout.addWidget(self.current_class_label)

        # Students table
        table_card = QWidget()
        table_card.setProperty("card", "true")
        table_card.setStyleSheet(f"""
            QWidget[card="true"] {{
                background-color: {theme["surface"]};
                border: 1px solid {theme["border"]};
                border-radius: 12px;
                padding: 16px;
            }}
        """)

        table_layout = QVBoxLayout(table_card)

        # Table header with actions
        table_header = QHBoxLayout()
        table_title = QLabel("Enrolled Students")
        table_title.setStyleSheet(f"font-weight: 600; color: {theme["text"]};")
        table_header.addWidget(table_title)

        table_header.addStretch()

        add_student_btn = self.create_button("➕ Add Student", "primary")
        add_student_btn.clicked.connect(self._add_student_to_class)
        table_header.addWidget(add_student_btn)

        remove_student_btn = self.create_button("➖ Remove", "danger")
        remove_student_btn.clicked.connect(self._remove_student_from_class)
        table_header.addWidget(remove_student_btn)

        table_layout.addLayout(table_header)

        # Students table
        self.class_students_table = self.create_table(0, 3)
        self.class_students_table.setHorizontalHeaderLabels(["Student ID", "Name", "Stream"])
        self.class_students_table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.class_students_table.setAlternatingRowColors(True)
        table_layout.addWidget(self.class_students_table)

        layout.addWidget(table_card, stretch=1)

        # Class statistics
        stats_card = QWidget()
        stats_card.setProperty("card", "true")
        stats_card.setStyleSheet(f"""
            QWidget[card="true"] {{
                background-color: {theme["surface"]};
                border: 1px solid {theme["border"]};
                border-radius: 12px;
                padding: 16px;
            }}
        """)

        stats_layout = QVBoxLayout(stats_card)

        stats_title = QLabel("📊 Class Statistics")
        stats_title.setStyleSheet(f"font-weight: 600; color: {theme["text"]};")
        stats_layout.addWidget(stats_title)

        self.stats_label = QLabel("Select a class to view statistics")
        self.stats_label.setStyleSheet(f"color: {theme["text_secondary"]};")
        self.stats_label.setWordWrap(True)
        stats_layout.addWidget(self.stats_label)

        layout.addWidget(stats_card)

        return panel

    def _refresh_classes(self):
        """Refresh the classes list."""
        try:
            self.classes_list.clear()

            # Get all classes from our simple storage
            for class_id, class_info in self.classes.items():
                item_text = f"{class_info['name']} ({class_info['stream']})"
                item = QListWidgetItem(item_text)
                item.setData(Qt.ItemDataRole.UserRole, class_id)
                self.classes_list.addItem(item)

            logger.info(f"Refreshed classes list with {len(self.classes)} classes")
        except Exception as e:
            logger.error(f"Error refreshing classes: {e}")
            show_error_message("Error", f"Failed to refresh classes: {str(e)}", self)

    def _on_class_selected(self):
        """Handle class selection change."""
        selected_items = self.classes_list.selectedItems()
        if not selected_items:
            self.current_class_label.setText("No class selected")
            self.class_students_table.setRowCount(0)
            self.stats_label.setText("Select a class to view statistics")
            return

        class_id = selected_items[0].data(Qt.ItemDataRole.UserRole)
        class_info = self.classes.get(class_id)

        if class_info:
            self.current_class_label.setText(f"Selected: {class_info['name']} ({class_info['stream']})")
            self._refresh_class_students(class_id)
            self._update_class_statistics(class_id)
        else:
            self.current_class_label.setText("Class not found")
            self.class_students_table.setRowCount(0)

    def _refresh_class_students(self, class_id: str):
        """Refresh students in the selected class."""
        try:
            class_info = self.classes.get(class_id, {})
            student_ids = class_info.get('students', set())

            self.class_students_table.setRowCount(0)

            for student_id in student_ids:
                try:
                    student = self.student_service.get_student_by_id(student_id)
                    if student:
                        row = self.class_students_table.rowCount()
                        self.class_students_table.insertRow(row)

                        self.class_students_table.setItem(row, 0, QTableWidgetItem(student.student_id))
                        self.class_students_table.setItem(row, 1, QTableWidgetItem(student.name))
                        self.class_students_table.setItem(row, 2, QTableWidgetItem(student.stream))
                except Exception as e:
                    logger.error(f"Error loading student {student_id}: {e}")

            logger.info(f"Refreshed class students with {len(student_ids)} students")
        except Exception as e:
            logger.error(f"Error refreshing class students: {e}")
            show_error_message("Error", f"Failed to refresh students: {str(e)}", self)

    def _update_class_statistics(self, class_id: str):
        """Update class statistics display."""
        try:
            class_info = self.classes.get(class_id, {})
            student_ids = class_info.get('students', set())
            total_students = len(student_ids)

            # Count by stream
            stream_counts = {}
            for student_id in student_ids:
                try:
                    student = self.student_service.get_student_by_id(student_id)
                    if student:
                        stream_counts[student.stream] = stream_counts.get(student.stream, 0) + 1
                except Exception as e:
                    logger.error(f"Error loading student {student_id} for stats: {e}")

            stats_text = f"Total Students: {total_students}\n\nStream Distribution:"
            for stream, count in stream_counts.items():
                stats_text += f"\n{stream}: {count}"

            self.stats_label.setText(stats_text)
        except Exception as e:
            logger.error(f"Error updating class statistics: {e}")
            self.stats_label.setText("Error loading statistics")

    def _add_class(self):
        """Add a new class."""
        class_name = self.class_name_input.text().strip()
        stream = self.class_stream_combo.currentText().strip()

        if not class_name or not stream:
            show_error_message("Validation Error", "Please fill in all fields.", self)
            return

        try:
            # Generate a simple class ID
            class_id = f"{class_name.replace(' ', '_')}_{stream}"

            # Check if class already exists
            if class_id in self.classes:
                show_error_message("Class Exists", f"Class '{class_name}' already exists.", self)
                return

            # Add to our simple storage
            self.classes[class_id] = {
                "name": class_name,
                "stream": stream,
                "students": set()
            }

            show_success_message("Success", f"Class '{class_name}' added successfully.", self)

            # Clear inputs
            self.class_name_input.clear()

            # Refresh classes list
            self._refresh_classes()

        except Exception as e:
            logger.error(f"Error adding class: {e}")
            show_error_message("Error", f"Failed to add class: {str(e)}", self)

    def _edit_class(self):
        """Edit the selected class."""
        selected_items = self.classes_list.selectedItems()
        if not selected_items:
            show_error_message("No Selection", "Please select a class to edit.", self)
            return

        class_id = selected_items[0].data(Qt.ItemDataRole.UserRole)
        class_info = self.classes.get(class_id)

        if not class_info:
            show_error_message("Error", "Class not found.", self)
            return

        # Set current values in inputs
        self.class_name_input.setText(class_info["name"])

        # Set stream
        index = self.class_stream_combo.findText(class_info["stream"])
        if index >= 0:
            self.class_stream_combo.setCurrentIndex(index)
        else:
            self.class_stream_combo.setEditText(class_info["stream"])

        # Change button text temporarily
        # Note: In a real implementation, you'd want to track edit mode
        show_info_message("Edit Mode", "Update the class information and save.", self)

    def _delete_class(self):
        """Delete the selected class."""
        selected_items = self.classes_list.selectedItems()
        if not selected_items:
            show_error_message("No Selection", "Please select a class to delete.", self)
            return

        class_id = selected_items[0].data(Qt.ItemDataRole.UserRole)
        class_info = self.classes.get(class_id)

        if not class_info:
            show_error_message("Error", "Class not found.", self)
            return

        from school_system.gui.dialogs.confirm_dialog import ConfirmationDialog
        dialog = ConfirmationDialog(
            self,
            "Delete Class",
            f"Are you sure you want to delete class '{class_info['name']}'?",
            "This will remove all student enrollments for this class."
        )

        if dialog.exec() == ConfirmationDialog.DialogCode.Accepted:
            try:
                # Remove from our simple storage
                del self.classes[class_id]
                show_success_message("Success", f"Class '{class_info['name']}' deleted successfully.", self)
                self._refresh_classes()

                # Clear students table if this class was selected
                if self.classes_list.selectedItems():
                    self.class_students_table.setRowCount(0)
                    self.current_class_label.setText("No class selected")
                    self.stats_label.setText("Select a class to view statistics")

            except Exception as e:
                logger.error(f"Error deleting class: {e}")
                show_error_message("Error", f"Failed to delete class: {str(e)}", self)

    def _add_student_to_class(self):
        """Add a student to the selected class."""
        selected_items = self.classes_list.selectedItems()
        if not selected_items:
            show_error_message("No Selection", "Please select a class first.", self)
            return

        class_id = selected_items[0].data(Qt.ItemDataRole.UserRole)

        # Show student selection dialog
        from school_system.gui.windows.student_window.view_students_window import ViewStudentsWindow
        students_window = ViewStudentsWindow(self, self.current_user, self.current_role)

        # Override the selection behavior to return selected student
        def on_student_selected():
            selected_rows = students_window.students_table.selectionModel().selectedRows()
            if selected_rows:
                student_id = students_window.students_table.item(selected_rows[0].row(), 0).text()
                try:
                    # Add to our simple storage
                    if class_id in self.classes:
                        self.classes[class_id]['students'].add(student_id)
                    show_success_message("Success", f"Student {student_id} added to class.", self)
                    self._refresh_class_students(class_id)
                    self._update_class_statistics(class_id)
                except Exception as e:
                    show_error_message("Error", f"Failed to add student: {str(e)}", self)
            students_window.close()

        # Add selection button to students window
        select_btn = students_window.create_button("Select Student", "primary")
        select_btn.clicked.connect(on_student_selected)

        # Add to the action bar
        students_window.main_layout.insertWidget(0, select_btn)
        students_window.show()

    def _remove_student_from_class(self):
        """Remove a student from the selected class."""
        selected_class_items = self.classes_list.selectedItems()
        if not selected_class_items:
            show_error_message("No Selection", "Please select a class first.", self)
            return

        selected_student_rows = self.class_students_table.selectionModel().selectedRows()
        if not selected_student_rows:
            show_error_message("No Selection", "Please select a student to remove.", self)
            return

        class_id = selected_class_items[0].data(Qt.ItemDataRole.UserRole)
        student_id = self.class_students_table.item(selected_student_rows[0].row(), 0).text()

        from school_system.gui.dialogs.confirm_dialog import ConfirmationDialog
        dialog = ConfirmationDialog(
            self,
            "Remove Student",
            f"Are you sure you want to remove student {student_id} from this class?",
            "The student will no longer be enrolled in this class."
        )

        if dialog.exec() == ConfirmationDialog.DialogCode.Accepted:
            try:
                # Remove from our simple storage
                if class_id in self.classes and student_id in self.classes[class_id]['students']:
                    self.classes[class_id]['students'].remove(student_id)
                show_success_message("Success", f"Student {student_id} removed from class.", self)
                self._refresh_class_students(class_id)
                self._update_class_statistics(class_id)
            except Exception as e:
                logger.error(f"Error removing student from class: {e}")
                show_error_message("Error", f"Failed to remove student: {str(e)}", self)