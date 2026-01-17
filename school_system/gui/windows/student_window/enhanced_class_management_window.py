"""
Enhanced Class Management Window

This window provides comprehensive class and stream management with dynamic parsing
from the database, filtering, and bulk operations.
"""

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QTableWidget,
    QTableWidgetItem, QComboBox, QListWidget, QListWidgetItem, QSplitter,
    QGroupBox, QMessageBox, QHeaderView
)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont
from typing import List, Optional, Tuple

from school_system.gui.windows.base_function_window import BaseFunctionWindow
from school_system.gui.dialogs.message_dialog import show_error_message, show_success_message, show_info_message
from school_system.config.logging import logger
from school_system.services.student_service import StudentService
from school_system.services.class_management_service import ClassManagementService
from school_system.models.student import Student


class EnhancedClassManagementWindow(BaseFunctionWindow):
    """Enhanced window for managing classes and streams with dynamic parsing."""

    def __init__(self, parent=None, current_user: str = "", current_role: str = ""):
        """Initialize the enhanced class management window."""
        super().__init__("Class & Stream Management", parent, current_user, current_role)

        self.student_service = StudentService()
        self.class_management_service = ClassManagementService()

        # Setup content
        self.setup_content()

        # Load initial data
        self._refresh_all_data()

    def setup_content(self):
        """Setup the main content area."""
        # Create main content layout
        main_layout = self.create_flex_layout("column", False)
        main_layout.set_margins(24, 24, 24, 24)
        main_layout.set_spacing(20)

        # Create splitter for filters and content
        splitter = QSplitter(Qt.Orientation.Horizontal)

        # Left panel - Filters and class list
        filters_panel = self._create_filters_panel()
        splitter.addWidget(filters_panel)

        # Right panel - Students table and actions
        students_panel = self._create_students_panel()
        splitter.addWidget(students_panel)

        # Set splitter proportions
        splitter.setSizes([350, 650])

        main_layout.add_widget(splitter, stretch=1)

        # Statistics panel at bottom
        stats_panel = self._create_statistics_panel()
        main_layout.add_widget(stats_panel)

        # Add to content
        self.add_layout_to_content(main_layout)

    def _create_filters_panel(self) -> QWidget:
        """Create the filters and class list panel."""
        theme_manager = self.get_theme_manager()
        theme = theme_manager._themes[self.get_theme()]

        panel = QWidget()
        layout = QVBoxLayout(panel)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(16)

        # Header
        header_label = QLabel("📚 Class & Stream Filters")
        header_font = QFont("Segoe UI", 16, QFont.Weight.Medium)
        header_label.setFont(header_font)
        header_label.setStyleSheet(f"color: {theme['text']}; margin-bottom: 8px;")
        layout.addWidget(header_label)

        # Filter card
        filter_card = QWidget()
        filter_card.setProperty("card", "true")
        filter_card.setStyleSheet(f"""
            QWidget[card="true"] {{
                background-color: {theme['surface']};
                border: 1px solid {theme['border']};
                border-radius: 12px;
                padding: 16px;
            }}
        """)

        filter_layout = QVBoxLayout(filter_card)
        filter_layout.setSpacing(12)

        # Class level filter
        class_level_layout = QVBoxLayout()
        class_level_label = QLabel("Class Level:")
        class_level_label.setStyleSheet(f"font-weight: 500; color: {theme['text']};")
        class_level_layout.addWidget(class_level_label)

        self.class_level_combo = QComboBox()
        self.class_level_combo.setFixedHeight(44)
        self.class_level_combo.addItem("All Classes")
        self.class_level_combo.currentTextChanged.connect(self._on_filter_changed)
        class_level_layout.addWidget(self.class_level_combo)
        filter_layout.addLayout(class_level_layout)

        # Stream filter
        stream_layout = QVBoxLayout()
        stream_label = QLabel("Stream:")
        stream_label.setStyleSheet(f"font-weight: 500; color: {theme['text']};")
        stream_layout.addWidget(stream_label)

        self.stream_combo = QComboBox()
        self.stream_combo.setFixedHeight(44)
        self.stream_combo.addItem("All Streams")
        self.stream_combo.currentTextChanged.connect(self._on_filter_changed)
        stream_layout.addWidget(self.stream_combo)
        filter_layout.addLayout(stream_layout)

        # Refresh button
        refresh_btn = self.create_button("🔄 Refresh Data", "primary")
        refresh_btn.clicked.connect(self._refresh_all_data)
        filter_layout.addWidget(refresh_btn)

        layout.addWidget(filter_card)

        # Class-Stream combinations list
        combinations_card = QWidget()
        combinations_card.setProperty("card", "true")
        combinations_card.setStyleSheet(f"""
            QWidget[card="true"] {{
                background-color: {theme['surface']};
                border: 1px solid {theme['border']};
                border-radius: 12px;
                padding: 16px;
            }}
        """)

        combinations_layout = QVBoxLayout(combinations_card)
        
        combinations_title = QLabel("Class-Stream Combinations")
        combinations_title.setStyleSheet(f"font-weight: 600; color: {theme['text']};")
        combinations_layout.addWidget(combinations_title)

        self.combinations_list = QListWidget()
        self.combinations_list.setSelectionMode(QListWidget.SelectionMode.SingleSelection)
        self.combinations_list.itemSelectionChanged.connect(self._on_combination_selected)
        self.combinations_list.setStyleSheet(f"""
            QListWidget {{
                background-color: {theme['background']};
                border: 1px solid {theme['border']};
                border-radius: 8px;
                padding: 8px;
            }}
            QListWidget::item {{
                padding: 8px;
                border-bottom: 1px solid {theme['border']};
            }}
            QListWidget::item:selected {{
                background-color: {theme['primary']};
                color: white;
            }}
        """)
        combinations_layout.addWidget(self.combinations_list)

        layout.addWidget(combinations_card, stretch=1)

        return panel

    def _create_students_panel(self) -> QWidget:
        """Create the students display panel."""
        theme_manager = self.get_theme_manager()
        theme = theme_manager._themes[self.get_theme()]

        panel = QWidget()
        layout = QVBoxLayout(panel)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(16)

        # Header with actions
        header_layout = QHBoxLayout()
        header_label = QLabel("👨‍🎓 Students")
        header_font = QFont("Segoe UI", 16, QFont.Weight.Medium)
        header_label.setFont(header_font)
        header_label.setStyleSheet(f"color: {theme['text']};")
        header_layout.addWidget(header_label)

        header_layout.addStretch()

        # Bulk actions button
        self.bulk_actions_btn = self.create_button("📚 Bulk Book Borrow", "primary")
        self.bulk_actions_btn.clicked.connect(self._open_bulk_borrow_dialog)
        header_layout.addWidget(self.bulk_actions_btn)

        layout.addLayout(header_layout)

        # Current filter display
        self.current_filter_label = QLabel("Showing: All Students")
        self.current_filter_label.setStyleSheet(f"""
            color: {theme['text_secondary']};
            font-style: italic;
            padding: 8px;
            background-color: {theme['surface']};
            border-radius: 8px;
        """)
        layout.addWidget(self.current_filter_label)

        # Students table
        table_card = QWidget()
        table_card.setProperty("card", "true")
        table_card.setStyleSheet(f"""
            QWidget[card="true"] {{
                background-color: {theme['surface']};
                border: 1px solid {theme['border']};
                border-radius: 12px;
                padding: 16px;
            }}
        """)

        table_layout = QVBoxLayout(table_card)

        self.students_table = self.create_table(0, 4)
        self.students_table.setColumnCount(4)
        self.students_table.setHorizontalHeaderLabels([
            "Student ID", "Name", "Class Level", "Stream"
        ])
        self.students_table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.students_table.setSelectionMode(QTableWidget.SelectionMode.ExtendedSelection)
        self.students_table.setAlternatingRowColors(True)
        
        # Set column widths
        header = self.students_table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(3, QHeaderView.ResizeMode.ResizeToContents)
        
        table_layout.addWidget(self.students_table)

        layout.addWidget(table_card, stretch=1)

        return panel

    def _create_statistics_panel(self) -> QWidget:
        """Create the statistics panel."""
        theme_manager = self.get_theme_manager()
        theme = theme_manager._themes[self.get_theme()]

        panel = QWidget()
        panel.setProperty("card", "true")
        panel.setStyleSheet(f"""
            QWidget[card="true"] {{
                background-color: {theme['surface']};
                border: 1px solid {theme['border']};
                border-radius: 12px;
                padding: 16px;
            }}
        """)

        layout = QHBoxLayout(panel)
        layout.setSpacing(24)

        self.stats_label = QLabel("Loading statistics...")
        self.stats_label.setStyleSheet(f"color: {theme['text']};")
        self.stats_label.setWordWrap(True)
        layout.addWidget(self.stats_label)

        return panel

    def _refresh_all_data(self):
        """Refresh all data including filters and student lists."""
        try:
            # Refresh classes
            classes = self.student_service.get_all_classes()
            current_class = self.class_level_combo.currentText()

            self.class_level_combo.clear()
            self.class_level_combo.addItem("All Classes")
            for class_name in classes:
                self.class_level_combo.addItem(class_name, class_name)

            # Restore selection if possible
            index = self.class_level_combo.findText(current_class)
            if index >= 0:
                self.class_level_combo.setCurrentIndex(index)
            else:
                self.class_level_combo.setCurrentIndex(0)

            # Refresh streams
            self._refresh_streams()

            # Refresh combinations
            self._refresh_combinations()

            # Refresh students
            self._refresh_students()

            # Refresh statistics
            self._refresh_statistics()

            logger.info("Refreshed all class management data")
        except Exception as e:
            logger.error(f"Error refreshing data: {e}")
            show_error_message("Error", f"Failed to refresh data: {str(e)}", self)

    def _refresh_streams(self):
        """Refresh the stream filter based on selected class."""
        try:
            current_stream = self.stream_combo.currentText()
            selected_class = self.class_level_combo.currentData()

            if selected_class:
                streams = self.student_service.get_streams_for_class(selected_class)
            else:
                streams = self.student_service.get_all_stream_names()

            self.stream_combo.clear()
            self.stream_combo.addItem("All Streams")
            for stream in streams:
                self.stream_combo.addItem(stream)

            # Restore selection if possible
            index = self.stream_combo.findText(current_stream)
            if index >= 0:
                self.stream_combo.setCurrentIndex(index)
            else:
                self.stream_combo.setCurrentIndex(0)
        except Exception as e:
            logger.error(f"Error refreshing streams: {e}")

    def _refresh_combinations(self):
        """Refresh the class-stream combinations list."""
        try:
            self.combinations_list.clear()

            # Get categorized students from class management service
            categorized = self.class_management_service.categorize_all_students()

            for class_name, streams_dict in categorized.items():
                for stream_name, students_list in streams_dict.items():
                    count = len(students_list)
                    item_text = f"{class_name} - {stream_name} ({count} students)"
                    item = QListWidgetItem(item_text)
                    item.setData(Qt.ItemDataRole.UserRole, (class_name, stream_name))
                    self.combinations_list.addItem(item)
        except Exception as e:
            logger.error(f"Error refreshing combinations: {e}")

    def _refresh_students(self):
        """Refresh the students table based on current filters."""
        try:
            self.students_table.setRowCount(0)
            
            # Get filter values
            selected_class = self.class_level_combo.currentText()
            selected_stream = self.stream_combo.currentText()

            class_name = selected_class if selected_class != "All Classes" else None
            stream_name = selected_stream if selected_stream != "All Streams" else None

            # Get students
            if class_name is not None and stream_name is not None:
                students = self.student_service.get_students_by_class_and_stream(class_name, stream_name)
                filter_text = f"{class_name} - {stream_name}"
            elif class_name is not None:
                students = self.student_service.get_students_by_class(class_name)
                filter_text = f"Class: {class_name}"
            elif stream_name is not None:
                students = self.student_service.get_students_by_stream_name(stream_name)
                filter_text = f"Stream: {stream_name}"
            else:
                students = self.student_service.get_all_students()
                filter_text = "All Students"
            
            # Update filter label
            self.current_filter_label.setText(f"Showing: {filter_text} ({len(students)} students)")
            
            # Populate table
            for student in students:
                row = self.students_table.rowCount()
                self.students_table.insertRow(row)
                
                # Parse student's stream to get class level and stream
                try:
                    class_level, stream_name = self.class_management_service.parse_student_stream(student.stream)
                    class_display = str(class_level)
                    stream_display = stream_name or "N/A"
                except Exception:
                    class_display = "N/A"
                    stream_display = student.stream or "N/A"
                
                self.students_table.setItem(row, 0, QTableWidgetItem(str(student.student_id)))
                self.students_table.setItem(row, 1, QTableWidgetItem(student.name))
                self.students_table.setItem(row, 2, QTableWidgetItem(class_display))
                self.students_table.setItem(row, 3, QTableWidgetItem(stream_display))
            
            logger.info(f"Refreshed students table with {len(students)} students")
        except Exception as e:
            logger.error(f"Error refreshing students: {e}")
            show_error_message("Error", f"Failed to refresh students: {str(e)}", self)

    def _refresh_statistics(self):
        """Refresh the statistics display."""
        try:
            # Get basic statistics using the new class/stream system
            all_students = self.student_service.get_all_students()
            classes = self.student_service.get_all_classes()
            streams = self.student_service.get_all_stream_names()

            # Calculate combinations from categorized data
            categorized = self.class_management_service.categorize_all_students()
            combinations = sum(len(streams_dict) for streams_dict in categorized.values())

            stats_text = (
                f"📊 Statistics: "
                f"Total Students: {len(all_students)} | "
                f"Classes: {len(classes)} | "
                f"Streams: {len(streams)} | "
                f"Combinations: {combinations}"
            )

            self.stats_label.setText(stats_text)
        except Exception as e:
            logger.error(f"Error refreshing statistics: {e}")
            self.stats_label.setText("Error loading statistics")

    def _on_filter_changed(self):
        """Handle filter changes."""
        # Update streams when class level changes
        if self.sender() == self.class_level_combo:
            self._refresh_streams()
        
        # Refresh students
        self._refresh_students()

    def _on_combination_selected(self):
        """Handle combination selection."""
        selected_items = self.combinations_list.selectedItems()
        if not selected_items:
            return

        class_name, stream_name = selected_items[0].data(Qt.ItemDataRole.UserRole)

        # Set filters to match selection
        index = self.class_level_combo.findText(class_name)
        if index >= 0:
            self.class_level_combo.setCurrentIndex(index)

        index = self.stream_combo.findText(stream_name)
        if index >= 0:
            self.stream_combo.setCurrentIndex(index)

        # Refresh students
        self._refresh_students()

    def _open_bulk_borrow_dialog(self):
        """Open the bulk book borrowing dialog."""
        from school_system.gui.windows.book_window.bulk_borrow_window import BulkBorrowWindow
        
        # Get current filter criteria
        selected_class_item = self.class_level_combo.currentData()
        selected_stream = self.stream_combo.currentText()
        
        class_level = selected_class_item if selected_class_item else None
        stream = selected_stream if selected_stream != "All Streams" else None
        
        # Get selected students from table
        selected_rows = self.students_table.selectionModel().selectedRows()
        student_ids = []
        if selected_rows:
            for row in selected_rows:
                student_id = self.students_table.item(row.row(), 0).text()
                student_ids.append(student_id)
        
        # Open bulk borrow window
        bulk_window = BulkBorrowWindow(
            self,
            self.current_user,
            self.current_role,
            class_level=class_level,
            stream=stream,
            student_ids=student_ids if student_ids else None
        )
        bulk_window.exec()
