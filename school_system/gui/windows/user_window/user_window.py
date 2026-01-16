"""
User management window for the School System Management application.

This module provides the main user management navigation interface for admin users (admin and librarian roles).
Provides access to individual user management functions through dedicated windows.
"""

from PyQt6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QLabel, QPushButton, QHBoxLayout, QGridLayout)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont

from school_system.gui.base.base_window import BaseWindow
from school_system.gui.dialogs.message_dialog import show_error_message
from school_system.config.logging import logger
from school_system.services.auth_service import AuthService
from school_system.core.exceptions import AuthenticationError
from school_system.gui.windows.user_window.add_user_window import AddUserWindow
from school_system.gui.windows.user_window.edit_user_window import EditUserWindow
from school_system.gui.windows.user_window.delete_user_window import DeleteUserWindow
from school_system.gui.windows.user_window.view_users_window import ViewUsersWindow
from school_system.gui.windows.user_window.user_settings_window import UserSettingsWindow
from school_system.gui.windows.user_window.short_form_mappings_window import ShortFormMappingsWindow
from school_system.gui.windows.user_window.user_sessions_window import UserSessionsWindow
from school_system.gui.windows.user_window.user_activity_window import UserActivityWindow


class UserWindow(BaseWindow):
    """Main user management navigation window for admin users."""

    def __init__(self, parent: QMainWindow, current_user: str, current_role: str):
        """
        Initialize the user management navigation window.

        Args:
            parent: The parent window
            current_user: The current logged-in username
            current_role: The current user's role
        """
        super().__init__("School System - User Management", parent)

        self.parent = parent
        self.current_user = current_user
        self.current_role = current_role
        self.auth_service = AuthService()

        # Check if user has admin privileges
        if self.current_role not in ["admin", "librarian"]:
            show_error_message("Access Denied", "You do not have permission to access user management.", self)
            self.close()
            return

        # Set minimum size
        self.setMinimumSize(1000, 700)

        # Apply modern web-style styling
        self._apply_modern_styling()

        # Initialize UI
        self._setup_widgets()

    def _apply_modern_styling(self):
        """Apply modern web-style styling to the user window using theme system."""
        theme_manager = self.get_theme_manager()
        theme = theme_manager._themes[self.get_theme()]

        self.setStyleSheet(f"""
            /* Base styling */
            QWidget {{
                font-family: 'Segoe UI', -apple-system, BlinkMacSystemFont, 'Roboto', sans-serif;
                font-size: 14px;
                background-color: {theme["background"]};
                color: {theme["text"]};
            }}

            /* Window styling */
            UserWindow {{
                background-color: {theme["background"]};
            }}

            /* Tab widget styling - modern web-style */
            QTabWidget::pane {{
                border: 1px solid {theme["border"]};
                background-color: {theme["surface"]};
                border-radius: 12px;
                padding: 20px;
            }}

            QTabBar::tab {{
                padding: 12px 24px;
                background-color: transparent;
                color: {theme["text_secondary"]};
                border: none;
                border-bottom: 2px solid transparent;
                font-size: 14px;
                font-weight: 500;
                margin-right: 4px;
            }}

            QTabBar::tab:hover {{
                color: {theme["text"]};
                background-color: {theme["surface_hover"]};
            }}

            QTabBar::tab:selected {{
                background-color: {theme["surface"]};
                color: {theme["primary"]};
                border-bottom: 2px solid {theme["primary"]};
            }}

            /* Button styling - using theme */
            QPushButton {{
                padding: 10px 20px;
                border-radius: 8px;
                border: 1px solid {theme["border"]};
                background-color: {theme["surface"]};
                color: {theme["text"]};
                min-height: 36px;
                font-size: 14px;
                font-weight: 500;
            }}

            QPushButton:hover {{
                background-color: {theme["surface_hover"]};
                border-color: {theme["text_secondary"]};
            }}

            /* Input field styling */
            QLineEdit, QComboBox, QTextEdit, QPlainTextEdit {{
                padding: 10px 14px;
                border: 1px solid {theme["border"]};
                border-radius: 8px;
                background-color: {theme["surface"]};
                color: {theme["text"]};
                min-height: 36px;
            }}

            QLineEdit:hover, QComboBox:hover, QTextEdit:hover, QPlainTextEdit:hover {{
                border-color: {theme["text_secondary"]};
            }}

            QLineEdit:focus, QComboBox:focus, QTextEdit:focus, QPlainTextEdit:focus {{
                border: 2px solid {theme["border_focus"]};
                background-color: {theme["surface"]};
            }}

            /* Table styling - modern web-style */
            QTableView, QTableWidget {{
                border: 1px solid {theme["border"]};
                border-radius: 12px;
                background-color: {theme["surface"]};
                gridline-color: {theme["border"]};
            }}

            QHeaderView::section {{
                background-color: {theme["surface"]};
                padding: 12px 16px;
                border: none;
                border-bottom: 2px solid {theme["border"]};
                font-weight: 600;
                font-size: 13px;
                color: {theme["text"]};
                text-transform: uppercase;
                letter-spacing: 0.5px;
            }}

            QTableView::item:selected, QTableWidget::item:selected {{
                background-color: {theme["primary"]};
                color: white;
            }}

            QTableView::item:hover, QTableWidget::item:hover {{
                background-color: {theme["surface_hover"]};
            }}

            /* Card styling - modern web-style */
            QGroupBox {{
                border: 1px solid {theme["border"]};
                border-radius: 12px;
                background-color: {theme["surface"]};
                margin-top: 12px;
                padding: 20px;
            }}

            QGroupBox::title {{
                subcontrol-origin: margin;
                left: 16px;
                padding: 0 8px;
                color: {theme["text"]};
                font-weight: 600;
                font-size: 15px;
            }}

            QFrame[card="true"] {{
                background-color: {theme["surface"]};
                border: 1px solid {theme["border"]};
                border-radius: 12px;
                padding: 24px;
            }}

            /* Checkbox styling */
            QCheckBox {{
                color: {theme["text"]};
                font-size: 14px;
                spacing: 8px;
            }}

            QCheckBox::indicator {{
                width: 20px;
                height: 20px;
                border: 2px solid {theme["border"]};
                border-radius: 4px;
                background-color: {theme["surface"]};
            }}

            QCheckBox::indicator:hover {{
                border-color: {theme["primary"]};
            }}

            QCheckBox::indicator:checked {{
                background-color: {theme["primary"]};
                border-color: {theme["primary"]};
            }}
        """)

    def _setup_widgets(self):
        """Setup the user management navigation widgets."""
        # Create main content layout
        main_layout = self.create_flex_layout("column", False)
        main_layout.setContentsMargins(24, 24, 24, 24)
        main_layout.set_spacing(24)

        # Header section
        header = self._create_header_section()
        main_layout.add_widget(header)

        # Function cards grid
        cards_grid = self._create_function_cards()
        main_layout.add_widget(cards_grid)

        # Add to content
        self.add_layout_to_content(main_layout)

    def _create_header_section(self) -> QWidget:
        """Create the header section with title and description."""
        theme_manager = self.get_theme_manager()
        theme = theme_manager._themes[self.get_theme()]

        header = QWidget()
        header_layout = QVBoxLayout(header)
        header_layout.setContentsMargins(0, 0, 0, 0)
        header_layout.setSpacing(8)

        # Title
        title = QLabel("User Management Center")
        title_font = QFont()
        title_font.setPointSize(24)
        title_font.setBold(True)
        title.setFont(title_font)
        title.setStyleSheet(f"color: {theme['text']}; margin-bottom: 8px;")
        header_layout.addWidget(title)

        # Subtitle
        subtitle = QLabel(f"Welcome, {self.current_user} ({self.current_role})")
        subtitle_font = QFont()
        subtitle_font.setPointSize(14)
        subtitle.setFont(subtitle_font)
        subtitle.setStyleSheet(f"color: {theme['text_secondary']}; margin-bottom: 16px;")
        header_layout.addWidget(subtitle)

        # Description
        description = QLabel(
            "Manage user accounts, settings, sessions, and activity logs. "
            "Click on any function below to open the dedicated management window."
        )
        description.setStyleSheet(f"color: {theme['text_secondary']};")
        description.setWordWrap(True)
        header_layout.addWidget(description)

        return header

    def _create_function_cards(self) -> QWidget:
        """Create a grid of function cards for navigation."""
        theme_manager = self.get_theme_manager()
        theme = theme_manager._themes[self.get_theme()]

        container = QWidget()
        grid_layout = QGridLayout(container)
        grid_layout.setContentsMargins(0, 0, 0, 0)
        grid_layout.setSpacing(16)

        # Row 1: User Management functions
        grid_layout.addWidget(self._create_function_card(
            "👥 Manage Users", "View, add, edit, and delete user accounts",
            self._open_view_users_window, theme
        ), 0, 0)

        grid_layout.addWidget(self._create_function_card(
            "➕ Add User", "Create new user accounts with roles",
            self._open_add_user_window, theme
        ), 0, 1)

        grid_layout.addWidget(self._create_function_card(
            "✏️ Edit User", "Update user roles and permissions",
            self._open_edit_user_window, theme
        ), 0, 2)

        grid_layout.addWidget(self._create_function_card(
            "🗑️ Delete User", "Remove user accounts permanently",
            self._open_delete_user_window, theme
        ), 0, 3)

        # Row 2: Settings and mappings
        grid_layout.addWidget(self._create_function_card(
            "⚙️ User Settings", "Manage user preferences and notifications",
            self._open_user_settings_window, theme
        ), 1, 0)

        grid_layout.addWidget(self._create_function_card(
            "🔤 Short Forms", "Manage short form mappings",
            self._open_short_form_mappings_window, theme
        ), 1, 1)

        grid_layout.addWidget(self._create_function_card(
            "🔐 Sessions", "Manage user login sessions",
            self._open_user_sessions_window, theme
        ), 1, 2)

        grid_layout.addWidget(self._create_function_card(
            "📊 Activity Logs", "Track user actions and activities",
            self._open_user_activity_window, theme
        ), 1, 3)

        return container

    def _create_function_card(self, title: str, description: str, callback, theme) -> QWidget:
        """Create a function navigation card."""
        card = QWidget()
        card_layout = QVBoxLayout(card)
        card_layout.setContentsMargins(20, 20, 20, 20)
        card_layout.setSpacing(12)

        # Apply card styling
        card.setStyleSheet(f"""
            QWidget {{
                background-color: {theme["surface"]};
                border: 1px solid {theme["border"]};
                border-radius: 12px;
                min-height: 120px;
            }}

            QWidget:hover {{
                background-color: {theme["surface_hover"]};
                border-color: {theme["primary"]};
            }}
        """)

        # Make card clickable
        card.mousePressEvent = lambda event: callback()

        # Title
        title_label = QLabel(title)
        title_font = QFont()
        title_font.setPointSize(16)
        title_font.setBold(True)
        title_label.setFont(title_font)
        title_label.setStyleSheet(f"color: {theme['text']};")
        card_layout.addWidget(title_label)

        # Description
        desc_label = QLabel(description)
        desc_label.setStyleSheet(f"color: {theme['text_secondary']};")
        desc_label.setWordWrap(True)
        card_layout.addWidget(desc_label)

        card_layout.addStretch()

        return card

    # Window opening methods
    def _open_view_users_window(self):
        """Open the view users window."""
        try:
            window = ViewUsersWindow(self, self.current_user, self.current_role)
            window.show()
        except Exception as e:
            logger.error(f"Error opening view users window: {str(e)}")
            show_error_message("Error", f"Failed to open users view: {str(e)}", self)

    def _open_add_user_window(self):
        """Open the add user window."""
        try:
            window = AddUserWindow(self, self.current_user, self.current_role)
            window.user_added.connect(self._on_user_data_changed)
            window.show()
        except Exception as e:
            logger.error(f"Error opening add user window: {str(e)}")
            show_error_message("Error", f"Failed to open add user window: {str(e)}", self)

    def _open_edit_user_window(self):
        """Open the edit user window."""
        try:
            # For editing, we need to select a user first
            # This would typically open a user selection dialog or use the view window
            window = ViewUsersWindow(self, self.current_user, self.current_role)
            window.show()
        except Exception as e:
            logger.error(f"Error opening edit user window: {str(e)}")
            show_error_message("Error", f"Failed to open edit user window: {str(e)}", self)

    def _open_delete_user_window(self):
        """Open the delete user window."""
        try:
            # For deletion, we need to select a user first
            # This would typically open a user selection dialog or use the view window
            window = ViewUsersWindow(self, self.current_user, self.current_role)
            window.show()
        except Exception as e:
            logger.error(f"Error opening delete user window: {str(e)}")
            show_error_message("Error", f"Failed to open delete user window: {str(e)}", self)

    def _open_user_settings_window(self):
        """Open the user settings window."""
        try:
            window = UserSettingsWindow(self, self.current_user, self.current_role)
            window.show()
        except Exception as e:
            logger.error(f"Error opening user settings window: {str(e)}")
            show_error_message("Error", f"Failed to open user settings: {str(e)}", self)

    def _open_short_form_mappings_window(self):
        """Open the short form mappings window."""
        try:
            window = ShortFormMappingsWindow(self, self.current_user, self.current_role)
            window.show()
        except Exception as e:
            logger.error(f"Error opening short form mappings window: {str(e)}")
            show_error_message("Error", f"Failed to open mappings window: {str(e)}", self)

    def _open_user_sessions_window(self):
        """Open the user sessions window."""
        try:
            window = UserSessionsWindow(self, self.current_user, self.current_role)
            window.show()
        except Exception as e:
            logger.error(f"Error opening user sessions window: {str(e)}")
            show_error_message("Error", f"Failed to open sessions window: {str(e)}", self)

    def _open_user_activity_window(self):
        """Open the user activity window."""
        try:
            window = UserActivityWindow(self, self.current_user, self.current_role)
            window.show()
        except Exception as e:
            logger.error(f"Error opening user activity window: {str(e)}")
            show_error_message("Error", f"Failed to open activity window: {str(e)}", self)

    def _on_user_data_changed(self):
        """Handle when user data has been changed (user added/edited/deleted)."""
        # This could trigger a refresh of any open user lists
        # For now, it's a placeholder for future enhancements
        pass
