"""
Enhanced Furniture Management Window

Comprehensive window for borrowing and returning furniture per stream per subject.
"""

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QLineEdit,
    QComboBox, QTableWidget, QTableWidgetItem, QHeaderView, QMessageBox,
    QDialog, QGroupBox, QCheckBox, QAbstractItemView, QTabWidget
)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont
from typing import Optional, List, Dict
from datetime import datetime

from school_system.gui.windows.base_function_window import BaseFunctionWindow
from school_system.gui.dialogs.message_dialog import show_error_message, show_success_message
from school_system.config.logging import logger
from school_system.services.furniture_service import FurnitureService
from school_system.services.class_management_service import ClassManagementService
from school_system.services.student_service import StudentService


class EnhancedFurnitureManagementWindow(QDialog):
    """Enhanced window for managing furniture borrowing and returning per stream per subject."""

    furniture_operation_completed = pyqtSignal()

    def __init__(
        self,
        parent=None,
        current_user: str = "",
        current_role: str = "",
        class_level: Optional[int] = None,
        stream: Optional[str] = None
    ):
        """Initialize the enhanced furniture management window."""
        super().__init__(parent)
        
        self.setWindowTitle("Furniture Management per Stream")
        self.setMinimumWidth(1200)
        self.setMinimumHeight(700)
        
        self.furniture_service = FurnitureService()
        self.class_management_service = ClassManagementService()
        self.student_service = StudentService()
        
        self.class_level = class_level
        self.stream = stream
        self.current_user = current_user
        
        self.students = []
        
        self.setup_ui()
        self.load_students()

    def setup_ui(self):
        """Setup the UI components."""
        from school_system.gui.base.widgets.theme import ThemeManager
        theme_manager = ThemeManager()
        theme = theme_manager._themes[theme_manager.get_theme()]
        
        layout = QVBoxLayout(self)
        layout.setSpacing(20)
        layout.setContentsMargins(24, 24, 24, 24)
        
        # Title
        title_label = QLabel("🪑 Furniture Management per Stream")
        title_font = QFont("Segoe UI", 18, QFont.Weight.Medium)
        title_label.setFont(title_font)
        title_label.setStyleSheet(f"color: {theme['text']}; margin-bottom: 8px;")
        layout.addWidget(title_label)
        
        # Filters/Info Group
        info_group = QGroupBox("Management Criteria")
        info_group.setStyleSheet(f"""
            QGroupBox {{
                font-weight: 600;
                border: 2px solid {theme['border']};
                border-radius: 8px;
                margin-top: 12px;
                padding-top: 12px;
            }}
            QGroupBox::title {{
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px;
            }}
        """)
        info_layout = QVBoxLayout(info_group)
        
        criteria_text = []
        if self.class_level is not None:
            display_name = self.class_management_service.format_class_display_name(self.class_level, self.stream)
            criteria_text.append(f"Class-Stream: {display_name}")
        
        if not criteria_text:
            criteria_text.append("All Students")
        
        criteria_label = QLabel("\n".join(criteria_text))
        criteria_label.setStyleSheet(f"color: {theme['text_secondary']}; padding: 8px;")
        info_layout.addWidget(criteria_label)
        
        layout.addWidget(info_group)
        
        # Tabs for Borrow and Return
        tabs = QTabWidget()
        
        # Borrow Tab
        borrow_tab = self._create_borrow_tab(theme)
        tabs.addTab(borrow_tab, "Borrow Furniture")
        
        # Return Tab
        return_tab = self._create_return_tab(theme)
        tabs.addTab(return_tab, "Return Furniture")
        
        layout.addWidget(tabs)
        
        # Close Button
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        
        close_btn = QPushButton("Close")
        close_btn.setFixedHeight(44)
        close_btn.setFixedWidth(120)
        close_btn.clicked.connect(self.close)
        close_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {theme['surface']};
                color: {theme['text']};
                border: 1px solid {theme['border']};
                border-radius: 6px;
                padding: 8px;
            }}
            QPushButton:hover {{
                background-color: {theme['border']};
            }}
        """)
        button_layout.addWidget(close_btn)
        
        layout.addLayout(button_layout)

    def _create_borrow_tab(self, theme: dict) -> QWidget:
        """Create the borrow furniture tab."""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setSpacing(15)
        
        # Furniture Type Selection
        type_layout = QHBoxLayout()
        type_layout.addWidget(QLabel("Furniture Type:"))
        self.furniture_type_combo = QComboBox()
        self.furniture_type_combo.addItems(["Chair", "Locker"])
        self.furniture_type_combo.currentTextChanged.connect(self._refresh_borrow_table)
        type_layout.addWidget(self.furniture_type_combo)
        type_layout.addStretch()
        layout.addLayout(type_layout)
        
        # Borrow Table
        self.borrow_table = QTableWidget()
        self.borrow_table.setColumnCount(7)
        self.borrow_table.setHorizontalHeaderLabels([
            "Student Name", "Admission Number", "Item Name/ID", "Quantity", "Condition", "Save", "Status"
        ])
        
        header = self.borrow_table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(3, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(4, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(5, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(6, QHeaderView.ResizeMode.ResizeToContents)
        
        self.borrow_table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.borrow_table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.borrow_table.verticalHeader().setVisible(False)
        
        self.borrow_table.setStyleSheet(f"""
            QTableWidget {{
                background-color: {theme['background']};
                border: 1px solid {theme['border']};
                border-radius: 6px;
                gridline-color: {theme['border']};
            }}
            QHeaderView::section {{
                background-color: {theme['surface']};
                color: {theme['text']};
                padding: 8px;
                border: 1px solid {theme['border']};
                font-weight: 600;
            }}
        """)
        
        layout.addWidget(self.borrow_table)
        
        # Action Buttons
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        
        borrow_all_btn = QPushButton("Borrow All")
        borrow_all_btn.setFixedHeight(44)
        borrow_all_btn.setFixedWidth(150)
        borrow_all_btn.clicked.connect(self._borrow_all_furniture)
        borrow_all_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {theme['primary']};
                color: white;
                border: none;
                border-radius: 6px;
                padding: 8px;
                font-weight: 600;
            }}
            QPushButton:hover {{
                background-color: {theme.get('primary_hover', theme['primary'])};
            }}
        """)
        button_layout.addWidget(borrow_all_btn)
        
        layout.addLayout(button_layout)
        
        return tab

    def _create_return_tab(self, theme: dict) -> QWidget:
        """Create the return furniture tab."""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setSpacing(15)
        
        # Furniture Type Selection
        type_layout = QHBoxLayout()
        type_layout.addWidget(QLabel("Furniture Type:"))
        self.return_furniture_type_combo = QComboBox()
        self.return_furniture_type_combo.addItems(["Chair", "Locker"])
        self.return_furniture_type_combo.currentTextChanged.connect(self._refresh_return_table)
        type_layout.addWidget(self.return_furniture_type_combo)
        type_layout.addStretch()
        layout.addLayout(type_layout)
        
        # Select All
        self.select_all_checkbox = QCheckBox("Select All")
        self.select_all_checkbox.stateChanged.connect(self._toggle_select_all_furniture)
        layout.addWidget(self.select_all_checkbox)
        
        # Return Table
        self.return_table = QTableWidget()
        self.return_table.setColumnCount(8)
        self.return_table.setHorizontalHeaderLabels([
            "Select", "Student Name", "Admission Number", "Item Name/ID", "Quantity", 
            "Condition", "Return", "Status"
        ])
        
        header = self.return_table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(3, QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(4, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(5, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(6, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(7, QHeaderView.ResizeMode.ResizeToContents)
        
        self.return_table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.return_table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.return_table.verticalHeader().setVisible(False)
        
        self.return_table.setStyleSheet(f"""
            QTableWidget {{
                background-color: {theme['background']};
                border: 1px solid {theme['border']};
                border-radius: 6px;
                gridline-color: {theme['border']};
            }}
            QHeaderView::section {{
                background-color: {theme['surface']};
                color: {theme['text']};
                padding: 8px;
                border: 1px solid {theme['border']};
                font-weight: 600;
            }}
        """)
        
        layout.addWidget(self.return_table)
        
        # Action Buttons
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        
        return_all_btn = QPushButton("Return All Selected")
        return_all_btn.setFixedHeight(44)
        return_all_btn.setFixedWidth(180)
        return_all_btn.clicked.connect(self._return_all_selected_furniture)
        return_all_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {theme['primary']};
                color: white;
                border: none;
                border-radius: 6px;
                padding: 8px;
                font-weight: 600;
            }}
            QPushButton:hover {{
                background-color: {theme.get('primary_hover', theme['primary'])};
            }}
        """)
        button_layout.addWidget(return_all_btn)
        
        layout.addLayout(button_layout)
        
        return tab

    def load_students(self):
        """Load students based on class level and stream."""
        try:
            if self.class_level is not None and self.stream is not None:
                self.students = self.class_management_service.get_students_by_class_and_stream(
                    self.class_level, self.stream
                )
            elif self.class_level is not None:
                self.students = self.class_management_service.get_students_by_class_level(self.class_level)
            elif self.stream is not None:
                self.students = self.class_management_service.get_students_by_stream(self.stream)
            else:
                self.students = self.student_service.get_all_students()
            
            self._refresh_borrow_table()
            self._refresh_return_table()
        except Exception as e:
            logger.error(f"Error loading students: {e}")
            show_error_message("Error", f"Failed to load students: {str(e)}", self)

    def _refresh_borrow_table(self):
        """Refresh the borrow table."""
        self.borrow_table.setRowCount(0)
        
        furniture_type = self.furniture_type_combo.currentText().lower()
        
        for student in self.students:
            row = self.borrow_table.rowCount()
            self.borrow_table.insertRow(row)
            
            # Student Name
            name_item = QTableWidgetItem(student.name)
            name_item.setData(Qt.ItemDataRole.UserRole, student.student_id)
            self.borrow_table.setItem(row, 0, name_item)
            
            # Admission Number
            admission_item = QTableWidgetItem(student.admission_number or str(student.student_id))
            self.borrow_table.setItem(row, 1, admission_item)
            
            # Item Name/ID Input
            item_input = QLineEdit()
            item_input.setPlaceholderText(f"Enter {furniture_type} ID")
            item_input.setFixedHeight(32)
            self.borrow_table.setCellWidget(row, 2, item_input)
            
            # Quantity Input
            quantity_input = QLineEdit()
            quantity_input.setPlaceholderText("1")
            quantity_input.setText("1")
            quantity_input.setFixedHeight(32)
            quantity_input.setFixedWidth(80)
            self.borrow_table.setCellWidget(row, 3, quantity_input)
            
            # Condition Input
            condition_input = QComboBox()
            condition_input.addItems(["Good", "Fair", "Poor", "Needs Repair"])
            condition_input.setCurrentText("Good")
            condition_input.setFixedHeight(32)
            self.borrow_table.setCellWidget(row, 4, condition_input)
            
            # Save Button
            save_btn = QPushButton("Save")
            save_btn.setFixedHeight(32)
            save_btn.setFixedWidth(80)
            save_btn.clicked.connect(lambda checked, r=row: self._save_individual_furniture_borrow(r))
            self.borrow_table.setCellWidget(row, 5, save_btn)
            
            # Status
            status_item = QTableWidgetItem("Pending")
            status_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self.borrow_table.setItem(row, 6, status_item)

    def _refresh_return_table(self):
        """Refresh the return table with assigned furniture."""
        self.return_table.setRowCount(0)
        
        furniture_type = self.return_furniture_type_combo.currentText().lower()
        
        try:
            for student in self.students:
                # Check for assigned furniture
                try:
                    if furniture_type == "chair":
                        assignment = self.furniture_service.chair_assignment_repository.get_by_id(student.student_id)
                        furniture_id = assignment.chair_id if assignment else None
                    else:  # locker
                        assignment = self.furniture_service.locker_assignment_repository.get_by_id(student.student_id)
                        furniture_id = assignment.locker_id if assignment else None
                    
                    if not furniture_id:
                        continue
                    
                    # Get furniture details
                    if furniture_type == "chair":
                        furniture = self.furniture_service.chair_repository.get_by_id(furniture_id)
                    else:
                        furniture = self.furniture_service.locker_repository.get_by_id(furniture_id)
                except Exception:
                    continue
                
                if not furniture:
                    continue
                
                row = self.return_table.rowCount()
                self.return_table.insertRow(row)
                
                # Select Checkbox
                checkbox = QCheckBox()
                checkbox.setCheckState(Qt.CheckState.Unchecked)
                self.return_table.setCellWidget(row, 0, checkbox)
                
                # Student Name
                name_item = QTableWidgetItem(student.name)
                name_item.setData(Qt.ItemDataRole.UserRole, (student.student_id, furniture_id))
                self.return_table.setItem(row, 1, name_item)
                
                # Admission Number
                admission_item = QTableWidgetItem(student.admission_number or str(student.student_id))
                self.return_table.setItem(row, 2, admission_item)
                
                # Item Name/ID
                item_id = getattr(furniture, f"{furniture_type}_id", furniture_id)
                item_item = QTableWidgetItem(str(item_id))
                self.return_table.setItem(row, 3, item_item)
                
                # Quantity
                quantity_item = QTableWidgetItem("1")
                self.return_table.setItem(row, 4, quantity_item)
                
                # Condition
                condition = getattr(furniture, 'cond', 'Good')
                condition_item = QTableWidgetItem(str(condition))
                self.return_table.setItem(row, 5, condition_item)
                
                # Return Button
                return_btn = QPushButton("Return")
                return_btn.setFixedHeight(32)
                return_btn.setFixedWidth(80)
                return_btn.clicked.connect(lambda checked, r=row: self._return_individual_furniture(r))
                self.return_table.setCellWidget(row, 6, return_btn)
                
                # Status
                status_item = QTableWidgetItem("Assigned")
                status_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                self.return_table.setItem(row, 7, status_item)
        except Exception as e:
            logger.error(f"Error refreshing return table: {e}")

    def _save_individual_furniture_borrow(self, row: int):
        """Save individual furniture borrow."""
        try:
            student_item = self.borrow_table.item(row, 0)
            if not student_item:
                return
            
            student_id = student_item.data(Qt.ItemDataRole.UserRole)
            item_input = self.borrow_table.cellWidget(row, 2)
            quantity_input = self.borrow_table.cellWidget(row, 3)
            condition_input = self.borrow_table.cellWidget(row, 4)
            
            item_id_str = item_input.text().strip() if item_input else ""
            
            if not item_id_str:
                show_error_message("Validation Error", "Please enter an item ID.", self)
                return
            
            try:
                item_id = int(item_id_str)
            except ValueError:
                show_error_message("Validation Error", "Item ID must be a valid number.", self)
                return
            
            furniture_type = self.furniture_type_combo.currentText().lower()
            condition = condition_input.currentText() if condition_input else "Good"
            
            # Assign furniture (this is a simplified version - actual implementation may vary)
            success = False
            try:
                if furniture_type == "chair":
                    # Assign chair logic would go here
                    from school_system.models.furniture import ChairAssignment
                    from datetime import date
                    assignment = ChairAssignment(student_id, item_id, date.today())
                    assignment.save()
                    
                    # Mark chair as assigned
                    chair = self.furniture_service.chair_repository.get_by_id(item_id)
                    if chair:
                        chair.assigned = 1
                        self.furniture_service.chair_repository.update(chair)
                    
                    success = True
                else:  # locker
                    from school_system.models.furniture import LockerAssignment
                    from datetime import date
                    assignment = LockerAssignment(student_id, item_id, date.today())
                    assignment.save()
                    
                    # Mark locker as assigned
                    locker = self.furniture_service.locker_repository.get_by_id(item_id)
                    if locker:
                        locker.assigned = 1
                        self.furniture_service.locker_repository.update(locker)
                    
                    success = True
            except Exception as e:
                logger.error(f"Error assigning furniture: {e}")
            
            status_item = self.borrow_table.item(row, 6)
            if success:
                status_item.setText("Assigned ✓")
                status_item.setForeground(Qt.GlobalColor.green)
                show_success_message("Success", f"{furniture_type.capitalize()} {item_id} assigned successfully.", self)
            else:
                status_item.setText("Failed ✗")
                status_item.setForeground(Qt.GlobalColor.red)
                show_error_message("Error", f"Failed to assign {furniture_type}.", self)
            
        except Exception as e:
            logger.error(f"Error in individual furniture borrow: {e}")
            show_error_message("Error", f"Failed to process assignment: {str(e)}", self)

    def _return_individual_furniture(self, row: int):
        """Return individual furniture item."""
        try:
            student_item = self.return_table.item(row, 1)
            if not student_item:
                return
            
            student_id, furniture_id = student_item.data(Qt.ItemDataRole.UserRole)
            furniture_type = self.return_furniture_type_combo.currentText().lower()
            
            # Unassign furniture
            success = False
            try:
                if furniture_type == "chair":
                    assignment = self.furniture_service.chair_assignment_repository.get_by_id(student_id)
                    if assignment:
                        self.furniture_service.chair_assignment_repository.delete(assignment)
                        
                        # Mark chair as available
                        chair = self.furniture_service.chair_repository.get_by_id(furniture_id)
                        if chair:
                            chair.assigned = 0
                            self.furniture_service.chair_repository.update(chair)
                        
                        success = True
                else:  # locker
                    assignment = self.furniture_service.locker_assignment_repository.get_by_id(student_id)
                    if assignment:
                        self.furniture_service.locker_assignment_repository.delete(assignment)
                        
                        # Mark locker as available
                        locker = self.furniture_service.locker_repository.get_by_id(furniture_id)
                        if locker:
                            locker.assigned = 0
                            self.furniture_service.locker_repository.update(locker)
                        
                        success = True
            except Exception as e:
                logger.error(f"Error returning furniture: {e}")
            
            status_item = self.return_table.item(row, 7)
            if success:
                status_item.setText("Returned ✓")
                status_item.setForeground(Qt.GlobalColor.green)
                
                # Disable return button
                return_btn = self.return_table.cellWidget(row, 6)
                if return_btn:
                    return_btn.setEnabled(False)
                
                # Disable checkbox
                checkbox = self.return_table.cellWidget(row, 0)
                if checkbox:
                    checkbox.setEnabled(False)
                
                show_success_message("Success", f"{furniture_type.capitalize()} returned successfully.", self)
            else:
                status_item.setText("Failed ✗")
                status_item.setForeground(Qt.GlobalColor.red)
                show_error_message("Error", f"Failed to return {furniture_type}.", self)
            
        except Exception as e:
            logger.error(f"Error in individual furniture return: {e}")
            show_error_message("Error", f"Failed to process return: {str(e)}", self)

    def _borrow_all_furniture(self):
        """Borrow furniture for all students with entered item IDs."""
        # Similar to book borrow all - iterate through table and process
        try:
            successful = 0
            failed = 0
            
            for row in range(self.borrow_table.rowCount()):
                status_item = self.borrow_table.item(row, 6)
                if status_item and status_item.text() == "Assigned ✓":
                    continue  # Already assigned
                
                self._save_individual_furniture_borrow(row)
                status_item = self.borrow_table.item(row, 6)
                if status_item and "✓" in status_item.text():
                    successful += 1
                else:
                    failed += 1
            
            show_success_message(
                "Bulk Assignment Complete",
                f"Successfully assigned {successful} item(s). Failed: {failed}.",
                self
            )
            
        except Exception as e:
            logger.error(f"Error in bulk furniture borrow: {e}")
            show_error_message("Error", f"Failed to process bulk assignment: {str(e)}", self)

    def _return_all_selected_furniture(self):
        """Return all selected furniture items."""
        try:
            selected_rows = []
            for row in range(self.return_table.rowCount()):
                checkbox = self.return_table.cellWidget(row, 0)
                if checkbox and checkbox.isChecked():
                    selected_rows.append(row)
            
            if not selected_rows:
                show_error_message("Validation Error", "Please select at least one item to return.", self)
                return
            
            reply = QMessageBox.question(
                self,
                "Confirm Return All",
                f"Return {len(selected_rows)} selected item(s)?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                QMessageBox.StandardButton.No
            )
            
            if reply != QMessageBox.StandardButton.Yes:
                return
            
            successful = 0
            failed = 0
            
            for row in selected_rows:
                status_item = self.return_table.item(row, 7)
                if status_item and status_item.text() == "Returned ✓":
                    continue
                
                self._return_individual_furniture(row)
                status_item = self.return_table.item(row, 7)
                if status_item and "✓" in status_item.text():
                    successful += 1
                else:
                    failed += 1
            
            show_success_message(
                "Bulk Return Complete",
                f"Successfully returned {successful} item(s). Failed: {failed}.",
                self
            )
            
        except Exception as e:
            logger.error(f"Error in bulk furniture return: {e}")
            show_error_message("Error", f"Failed to process returns: {str(e)}", self)

    def _toggle_select_all_furniture(self, state: int):
        """Toggle all checkboxes in return table."""
        checked = state == Qt.CheckState.Checked.value
        for row in range(self.return_table.rowCount()):
            checkbox = self.return_table.cellWidget(row, 0)
            if checkbox:
                checkbox.setCheckState(Qt.CheckState.Checked if checked else Qt.CheckState.Unchecked)
