"""
Manage Furniture Window

Dedicated window for managing furniture items.
"""

from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QTableWidget, QTableWidgetItem, QComboBox, QLineEdit
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont

from school_system.gui.windows.base_function_window import BaseFunctionWindow
from school_system.gui.dialogs.message_dialog import show_error_message, show_success_message
from school_system.config.logging import logger
from school_system.services.furniture_service import FurnitureService


class ManageFurnitureWindow(BaseFunctionWindow):
    """Dedicated window for managing furniture items."""
    
    def __init__(self, parent=None, current_user: str = "", current_role: str = ""):
        """Initialize the manage furniture window."""
        super().__init__("Manage Furniture", parent, current_user, current_role)
        
        self.furniture_service = FurnitureService()
        
        # Setup content
        self.setup_content()
        
        # Load initial data
        self._refresh_furniture_table()
    
    def setup_content(self):
        """Setup the main content area."""
        # Create main content layout
        main_layout = self.create_flex_layout("column", False)
        main_layout.set_margins(24, 24, 24, 24)
        main_layout.set_spacing(16)
        
        # Action bar
        action_bar = self._create_action_bar()
        main_layout.add_widget(action_bar)
        
        # Furniture table
        furniture_card = self._create_furniture_table()
        main_layout.add_widget(furniture_card, stretch=1)
        
        # Add to content
        self.add_layout_to_content(main_layout)
    
    def _create_action_bar(self) -> QWidget:
        """Create the action bar."""
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
        self.search_box = self.create_search_box("Search furniture...")
        self.search_box.setMinimumWidth(300)
        self.search_box.search_text_changed.connect(self._on_search)
        action_layout.addWidget(self.search_box)
        
        # Type filter
        self.type_filter = QComboBox()
        self.type_filter.addItem("All Types")
        self.type_filter.addItems(["Chair", "Locker", "Desk", "Table"])
        self.type_filter.setMinimumWidth(150)
        self.type_filter.currentTextChanged.connect(self._on_filter_changed)
        action_layout.addWidget(self.type_filter)
        
        action_layout.addStretch()
        
        # Action buttons
        add_btn = self.create_button("➕ Add Furniture", "primary")
        add_btn.clicked.connect(self._on_add_furniture)
        action_layout.addWidget(add_btn)
        
        refresh_btn = self.create_button("🔄 Refresh", "outline")
        refresh_btn.clicked.connect(self._refresh_furniture_table)
        action_layout.addWidget(refresh_btn)
        
        return action_card
    
    def _create_furniture_table(self) -> QWidget:
        """Create the furniture table card."""
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
        title_label = QLabel("Furniture List")
        title_font = QFont("Segoe UI", 16, QFont.Weight.Medium)
        title_label.setFont(title_font)
        title_label.setStyleSheet(f"color: {theme['text']}; margin-bottom: 8px;")
        table_layout.addWidget(title_label)
        
        # Furniture table
        self.furniture_table = self.create_table(0, 5)
        self.furniture_table.setColumnCount(5)
        self.furniture_table.setHorizontalHeaderLabels(["Furniture ID", "Type", "Location", "Status", "Assigned To"])
        self.furniture_table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.furniture_table.setAlternatingRowColors(True)
        table_layout.addWidget(self.furniture_table)
        
        return table_card
    
    def _refresh_furniture_table(self):
        """Refresh the furniture table."""
        try:
            # Get furniture items
            furniture_items = self.furniture_service.get_all_furniture()

            # Apply filter
            type_filter = self.type_filter.currentText()
            if type_filter != "All Types":
                furniture_items = [f for f in furniture_items if f['type'] == type_filter]

            # Clear table
            self.furniture_table.setRowCount(0)

            # Populate table
            for item in furniture_items:
                row = self.furniture_table.rowCount()
                self.furniture_table.insertRow(row)

                self.furniture_table.setItem(row, 0, QTableWidgetItem(item['furniture_id']))
                self.furniture_table.setItem(row, 1, QTableWidgetItem(item['type']))
                self.furniture_table.setItem(row, 2, QTableWidgetItem(item['location'] or ""))
                self.furniture_table.setItem(row, 3, QTableWidgetItem(item['status'] or "Available"))
                self.furniture_table.setItem(row, 4, QTableWidgetItem(item['assigned_to'] or ""))

            logger.info(f"Refreshed furniture table with {len(furniture_items)} items")
        except Exception as e:
            logger.error(f"Error refreshing furniture table: {e}")
            show_error_message("Error", f"Failed to refresh furniture: {str(e)}", self)
    
    def _on_search(self, text: str):
        """Handle search text change."""
        for row in range(self.furniture_table.rowCount()):
            match = False
            for col in range(5):
                item = self.furniture_table.item(row, col)
                if item and text.lower() in item.text().lower():
                    match = True
                    break
            self.furniture_table.setRowHidden(row, not match)
    
    def _on_filter_changed(self, text: str):
        """Handle filter change."""
        self._refresh_furniture_table()
    
    def _on_add_furniture(self):
        """Handle add furniture."""
        try:
            # Create add furniture dialog
            self._show_add_furniture_dialog()
        except Exception as e:
            logger.error(f"Error showing add furniture dialog: {e}")
            show_error_message("Error", f"Failed to open add furniture dialog: {str(e)}", self)

    def _show_add_furniture_dialog(self):
        """Show the add furniture dialog."""
        from PyQt6.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QComboBox, QPushButton

        dialog = QDialog(self)
        dialog.setWindowTitle("Add New Furniture")
        dialog.setModal(True)

        theme_manager = self.get_theme_manager()
        theme = theme_manager._themes[self.get_theme()]

        layout = QVBoxLayout(dialog)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(16)

        # Title
        title = QLabel("Add New Furniture Item")
        title_font = QFont("Segoe UI", 16, QFont.Weight.Medium)
        title.setFont(title_font)
        title.setStyleSheet(f"color: {theme['text']}; margin-bottom: 8px;")
        layout.addWidget(title)

        # Form fields
        form_layout = QVBoxLayout()
        form_layout.setSpacing(12)

        # Furniture type
        type_layout = QHBoxLayout()
        type_label = QLabel("Type:")
        type_label.setMinimumWidth(80)
        type_label.setStyleSheet(f"color: {theme['text']}; font-weight: 500;")
        type_layout.addWidget(type_label)

        self.add_type_combo = QComboBox()
        self.add_type_combo.addItems(["Chair", "Locker"])
        self.add_type_combo.setMinimumWidth(200)
        type_layout.addWidget(self.add_type_combo)
        type_layout.addStretch()
        form_layout.addLayout(type_layout)

        # Location
        location_layout = QHBoxLayout()
        location_label = QLabel("Location:")
        location_label.setMinimumWidth(80)
        location_label.setStyleSheet(f"color: {theme['text']}; font-weight: 500;")
        location_layout.addWidget(location_label)

        self.add_location_input = QLineEdit()
        self.add_location_input.setPlaceholderText("e.g., Room 101")
        self.add_location_input.setMinimumWidth(200)
        location_layout.addWidget(self.add_location_input)
        location_layout.addStretch()
        form_layout.addLayout(location_layout)

        # Form (for chairs/lockers)
        form_layout_h = QHBoxLayout()
        form_label = QLabel("Form:")
        form_label.setMinimumWidth(80)
        form_label.setStyleSheet(f"color: {theme['text']}; font-weight: 500;")
        form_layout_h.addWidget(form_label)

        self.add_form_input = QLineEdit()
        self.add_form_input.setPlaceholderText("e.g., Standard, Executive")
        self.add_form_input.setMinimumWidth(200)
        form_layout_h.addWidget(self.add_form_input)
        form_layout_h.addStretch()
        form_layout.addLayout(form_layout_h)

        # Color
        color_layout = QHBoxLayout()
        color_label = QLabel("Color:")
        color_label.setMinimumWidth(80)
        color_label.setStyleSheet(f"color: {theme['text']}; font-weight: 500;")
        color_layout.addWidget(color_label)

        self.add_color_input = QLineEdit()
        self.add_color_input.setPlaceholderText("e.g., Blue, Brown")
        self.add_color_input.setMinimumWidth(200)
        color_layout.addWidget(self.add_color_input)
        color_layout.addStretch()
        form_layout.addLayout(color_layout)

        layout.addLayout(form_layout)

        # Buttons
        button_layout = QHBoxLayout()
        button_layout.addStretch()

        cancel_btn = QPushButton("Cancel")
        cancel_btn.clicked.connect(dialog.reject)
        cancel_btn.setStyleSheet(f"""
            QPushButton {{
                padding: 8px 16px;
                border-radius: 6px;
                border: 1px solid {theme['border']};
                background-color: transparent;
                color: {theme['text']};
            }}
            QPushButton:hover {{
                background-color: {theme['surface_hover']};
            }}
        """)
        button_layout.addWidget(cancel_btn)

        add_btn = QPushButton("Add Furniture")
        add_btn.clicked.connect(lambda: self._perform_add_furniture(dialog))
        add_btn.setStyleSheet(f"""
            QPushButton {{
                padding: 8px 16px;
                border-radius: 6px;
                border: none;
                background-color: #10b981;
                color: white;
                font-weight: 500;
            }}
            QPushButton:hover {{
                background-color: #059669;
            }}
        """)
        button_layout.addWidget(add_btn)

        layout.addLayout(button_layout)

        dialog.exec()

    def _perform_add_furniture(self, dialog):
        """Perform the add furniture operation."""
        try:
            furniture_type = self.add_type_combo.currentText()
            location = self.add_location_input.text().strip()
            form = self.add_form_input.text().strip()
            color = self.add_color_input.text().strip()

            # Validation
            if not color:
                show_error_message("Validation Error", "Color is required.", dialog)
                return

            # Create furniture based on type
            if furniture_type == "Chair":
                # Get next chair ID
                chairs = self.furniture_service.get_all_chairs()
                next_id = max([c.chair_id for c in chairs], default=0) + 1

                furniture_data = {
                    'chair_id': next_id,
                    'location': location,
                    'form': form,
                    'color': color,
                    'cond': 'Good',
                    'assigned': 0
                }
                result = self.furniture_service.create_chair(furniture_data)

            elif furniture_type == "Locker":
                # Get next locker ID
                lockers = self.furniture_service.get_all_lockers()
                next_id = max([l.locker_id for l in lockers], default=0) + 1

                furniture_data = {
                    'locker_id': next_id,
                    'location': location,
                    'form': form,
                    'color': color,
                    'cond': 'Good',
                    'assigned': 0
                }
                result = self.furniture_service.create_locker(furniture_data)

            if result:
                show_success_message("Success", f"{furniture_type} added successfully!", dialog)
                dialog.accept()
                self._refresh_furniture_table()
            else:
                show_error_message("Error", f"Failed to add {furniture_type.lower()}.", dialog)

        except Exception as e:
            logger.error(f"Error adding furniture: {e}")
            show_error_message("Error", f"Failed to add furniture: {str(e)}", dialog)
