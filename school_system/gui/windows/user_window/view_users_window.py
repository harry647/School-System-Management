"""
View Users Window

Dedicated window for viewing and managing users.
"""

from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QTableWidget, QTableWidgetItem, QComboBox, QSizePolicy
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont

from school_system.gui.windows.base_function_window import BaseFunctionWindow
from school_system.gui.dialogs.message_dialog import show_error_message, show_success_message
from school_system.config.logging import logger
from school_system.services.auth_service import AuthService


class ViewUsersWindow(BaseFunctionWindow):
    """Dedicated window for viewing and managing users."""
    
    def __init__(self, parent=None, current_user: str = "", current_role: str = ""):
        """Initialize the view users window."""
        super().__init__("Manage Users", parent, current_user, current_role)
        
        self.auth_service = AuthService()
        self.users_table = None
        
        # Setup content
        self.setup_content()
        
        # Load initial data
        self._refresh_users_table()
    
    def setup_content(self):
        """Setup the main content area."""
        # Create main content layout
        main_layout = self.create_flex_layout("column", False)
        main_layout.set_margins(24, 24, 24, 24)
        main_layout.set_spacing(16)
        
        # Action bar
        action_bar = self._create_action_bar()
        main_layout.add_widget(action_bar)
        
        # Users table
        users_card = self._create_users_table()
        main_layout.add_widget(users_card, stretch=1)

        logger.debug(f"Users card created: {users_card}")
        logger.debug(f"Users card size policy: {users_card.sizePolicy()}")
        
        # Add to content
        logger.debug(f"Adding main layout to content: {main_layout}")
        self.add_layout_to_content(main_layout)
        logger.debug("Main layout added to content")
    
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
        self.search_box = self.create_search_box("Search users by username or role...")
        self.search_box.setMinimumWidth(300)
        self.search_box.search_text_changed.connect(self._on_search)
        action_layout.addWidget(self.search_box)
        
        # Role filter
        self.role_filter = QComboBox()
        self.role_filter.addItem("All Roles")
        self.role_filter.addItems(["admin", "librarian", "teacher", "student"])
        self.role_filter.setMinimumWidth(150)
        self.role_filter.currentTextChanged.connect(self._on_filter_changed)
        action_layout.addWidget(self.role_filter)
        
        action_layout.addStretch()
        
        # Action buttons
        add_btn = self.create_button("➕ Add User", "primary")
        add_btn.clicked.connect(self._on_add_user)
        action_layout.addWidget(add_btn)
        
        refresh_btn = self.create_button("🔄 Refresh", "outline")
        refresh_btn.clicked.connect(self._refresh_users_table)
        action_layout.addWidget(refresh_btn)
        
        return action_card
    
    def _create_users_table(self) -> QWidget:
        """Create the users table card."""
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
        title_label = QLabel("Users List")
        title_font = QFont("Segoe UI", 16, QFont.Weight.Medium)
        title_label.setFont(title_font)
        title_label.setStyleSheet(f"color: {theme["text"]}; margin-bottom: 8px;")
        table_layout.addWidget(title_label)
        
        # Users table
        self.users_table = self.create_table(0, 3)
        self.users_table.setColumnCount(3)  # Ensure columns are set
        self.users_table.setHorizontalHeaderLabels(["Username", "Role", "Status"])
        self.users_table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.users_table.setAlternatingRowColors(True)
        self.users_table.setMinimumHeight(150)
        self.users_table.setMinimumWidth(400)
        table_layout.addWidget(self.users_table)

        logger.debug(f"Users table created: {self.users_table}")
        logger.debug(f"Table parent: {self.users_table.parent()}")
        logger.debug(f"Table is visible: {self.users_table.isVisible()}")
        
        return table_card
    
    def _refresh_users_table(self):
        """Refresh the users table."""
        try:
            # Get users
            users = self.auth_service.get_all_users()
            
            # Apply filter
            role_filter = self.role_filter.currentText()
            if role_filter != "All Roles":
                users = [u for u in users if u['role'] == role_filter]
            
            # Clear table
            self.users_table.setRowCount(0)
            
            # Populate table
            for user in users:
                row = self.users_table.rowCount()
                self.users_table.insertRow(row)

                self.users_table.setItem(row, 0, QTableWidgetItem(user['username']))
                self.users_table.setItem(row, 1, QTableWidgetItem(user['role']))
                self.users_table.setItem(row, 2, QTableWidgetItem("Active"))

            # Resize columns to fit content
            self.users_table.resizeColumnsToContents()
            self.users_table.resizeRowsToContents()

            # Ensure minimum height for visibility
            if self.users_table.rowCount() > 0:
                self.users_table.setMinimumHeight(200)

            # Force layout update
            self.users_table.update()
            self.users_table.repaint()
            table_card = self.users_table.parent()
            if table_card:
                table_card.update()
                table_card.repaint()

            logger.info(f"Refreshed users table with {len(users)} users")
            logger.debug(f"Table row count: {self.users_table.rowCount()}, column count: {self.users_table.columnCount()}")
            logger.debug(f"Table is visible: {self.users_table.isVisible()}")
            logger.debug(f"Table size: {self.users_table.size()}")

            # Additional debug info
            for row in range(self.users_table.rowCount()):
                username_item = self.users_table.item(row, 0)
                role_item = self.users_table.item(row, 1)
                status_item = self.users_table.item(row, 2)
                logger.debug(f"Row {row}: username='{username_item.text() if username_item else 'None'}', role='{role_item.text() if role_item else 'None'}', status='{status_item.text() if status_item else 'None'}'")
        except Exception as e:
            logger.error(f"Error refreshing users table: {e}")
            show_error_message("Error", f"Failed to refresh users: {str(e)}", self)
    
    def _on_search(self, text: str):
        """Handle search text change."""
        for row in range(self.users_table.rowCount()):
            match = False
            for col in range(3):
                item = self.users_table.item(row, col)
                if item and text.lower() in item.text().lower():
                    match = True
                    break
            self.users_table.setRowHidden(row, not match)
    
    def _on_filter_changed(self, text: str):
        """Handle filter change."""
        self._refresh_users_table()
    
    def _on_add_user(self):
        """Handle add user."""
        show_error_message("Info", "Add user functionality will be implemented here.", self)
