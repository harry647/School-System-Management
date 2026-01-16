"""
View Teachers Window

Dedicated window for viewing and managing teachers list.
"""

from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QTableWidget, QTableWidgetItem, QComboBox
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont

from school_system.gui.windows.base_function_window import BaseFunctionWindow
from school_system.gui.dialogs.message_dialog import show_error_message, show_success_message
from school_system.config.logging import logger
from school_system.services.teacher_service import TeacherService


class ViewTeachersWindow(BaseFunctionWindow):
    """Dedicated window for viewing and managing teachers."""
    
    def __init__(self, parent=None, current_user: str = "", current_role: str = ""):
        """Initialize the view teachers window."""
        super().__init__("View Teachers", parent, current_user, current_role)
        
        self.teacher_service = TeacherService()
        self.teachers_table = None
        
        # Setup content
        self.setup_content()
        
        # Load initial data
        self._refresh_teachers_table()
    
    def setup_content(self):
        """Setup the main content area."""
        # Create main content layout
        main_layout = self.create_flex_layout("column", False)
        main_layout.set_margins(24, 24, 24, 24)
        main_layout.set_spacing(16)
        
        # Action bar with search and filters
        action_bar = self._create_action_bar()
        main_layout.add_widget(action_bar)
        
        # Teachers table
        teachers_card = self._create_teachers_table()
        main_layout.add_widget(teachers_card, stretch=1)
        
        # Add to content
        self.add_layout_to_content(main_layout)
    
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
        action_layout.setContentsMargins(16, 16, 16, 16)
        action_layout.setSpacing(12)
        
        # Search box
        self.search_box = self.create_search_box("Search teachers by name, ID, or department...")
        self.search_box.setMinimumWidth(300)
        self.search_box.search_text_changed.connect(self._on_search)
        action_layout.addWidget(self.search_box)
        
        action_layout.addStretch()
        
        # Action buttons
        add_btn = self.create_button("➕ Add Teacher", "primary")
        add_btn.clicked.connect(self._on_add_teacher)
        action_layout.addWidget(add_btn)
        
        edit_btn = self.create_button("✏️ Edit", "secondary")
        edit_btn.clicked.connect(self._on_edit_teacher)
        action_layout.addWidget(edit_btn)
        
        delete_btn = self.create_button("🗑️ Delete", "danger")
        delete_btn.clicked.connect(self._on_delete_teacher)
        action_layout.addWidget(delete_btn)
        
        refresh_btn = self.create_button("🔄 Refresh", "outline")
        refresh_btn.clicked.connect(self._refresh_teachers_table)
        action_layout.addWidget(refresh_btn)
        
        return action_card
    
    def _create_teachers_table(self) -> QWidget:
        """Create the teachers table card."""
        theme_manager = self.get_theme_manager()
        theme = theme_manager._themes[self.get_theme()]
        
        table_card = QWidget()
        table_card.setProperty("card", "true")
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
        title_label = QLabel("Teachers List")
        title_font = QFont("Segoe UI", 16, QFont.Weight.Medium)
        title_label.setFont(title_font)
        title_label.setStyleSheet(f"color: {theme["text"]}; margin-bottom: 8px;")
        table_layout.addWidget(title_label)
        
        # Teachers table
        self.teachers_table = self.create_table(0, 5)
        self.teachers_table.setColumnCount(5)  # Ensure columns are set
        self.teachers_table.setHorizontalHeaderLabels(["Teacher ID", "Name", "Department", "Email", "Phone"])
        self.teachers_table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.teachers_table.setAlternatingRowColors(True)
        table_layout.addWidget(self.teachers_table)
        
        return table_card
    
    def _refresh_teachers_table(self):
        """Refresh the teachers table with current data."""
        try:
            teachers = self.teacher_service.get_all_teachers()
            
            # Clear table
            self.teachers_table.setRowCount(0)
            
            # Populate table
            for teacher in teachers:
                row = self.teachers_table.rowCount()
                self.teachers_table.insertRow(row)
                
                self.teachers_table.setItem(row, 0, QTableWidgetItem(teacher.teacher_id))
                self.teachers_table.setItem(row, 1, QTableWidgetItem(teacher.name))
                self.teachers_table.setItem(row, 2, QTableWidgetItem(teacher.department or ""))
                self.teachers_table.setItem(row, 3, QTableWidgetItem(teacher.email or ""))
                self.teachers_table.setItem(row, 4, QTableWidgetItem(teacher.phone or ""))
            
            logger.info(f"Refreshed teachers table with {len(teachers)} teachers")
        except Exception as e:
            logger.error(f"Error refreshing teachers table: {e}")
            show_error_message("Error", f"Failed to refresh teachers: {str(e)}", self)
    
    def _on_search(self, text: str):
        """Handle search text change."""
        # Filter table based on search text
        for row in range(self.teachers_table.rowCount()):
            match = False
            for col in range(5):  # Check all columns
                item = self.teachers_table.item(row, col)
                if item and text.lower() in item.text().lower():
                    match = True
                    break
            self.teachers_table.setRowHidden(row, not match)
    
    def _on_add_teacher(self):
        """Open add teacher window."""
        from school_system.gui.windows.teacher_window.add_teacher_window import AddTeacherWindow
        add_window = AddTeacherWindow(self, self.current_user, self.current_role)
        add_window.teacher_added.connect(self._refresh_teachers_table)
        add_window.show()
    
    def _on_edit_teacher(self):
        """Open edit teacher window."""
        selected_rows = self.teachers_table.selectionModel().selectedRows()
        if not selected_rows:
            show_error_message("No Selection", "Please select a teacher to edit.", self)
            return
        
        teacher_id = self.teachers_table.item(selected_rows[0].row(), 0).text()
        from school_system.gui.windows.teacher_window.edit_teacher_window import EditTeacherWindow
        edit_window = EditTeacherWindow(teacher_id, self, self.current_user, self.current_role)
        edit_window.teacher_updated.connect(self._refresh_teachers_table)
        edit_window.show()
    
    def _on_delete_teacher(self):
        """Handle delete teacher."""
        selected_rows = self.teachers_table.selectionModel().selectedRows()
        if not selected_rows:
            show_error_message("No Selection", "Please select a teacher to delete.", self)
            return
        
        teacher_id = self.teachers_table.item(selected_rows[0].row(), 0).text()
        from school_system.gui.dialogs.confirm_dialog import ConfirmationDialog
        dialog = ConfirmationDialog(
            title="Delete Teacher",
            message=f"Are you sure you want to delete teacher {teacher_id}?\n\nThis action cannot be undone.",
            parent=self,
            confirm_text="Delete",
            cancel_text="Cancel"
        )
        
        if dialog.exec() == ConfirmationDialog.DialogCode.Accepted:
            try:
                self.teacher_service.delete_teacher(teacher_id)
                show_success_message("Success", f"Teacher {teacher_id} deleted successfully.", self)
                self._refresh_teachers_table()
            except Exception as e:
                show_error_message("Error", f"Failed to delete teacher: {str(e)}", self)
