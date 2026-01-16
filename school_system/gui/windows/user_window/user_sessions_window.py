"""
User Sessions Window

Dedicated window for managing user sessions (create and expire).
"""

from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QLineEdit, QGroupBox
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont

from school_system.gui.windows.base_function_window import BaseFunctionWindow
from school_system.gui.dialogs.message_dialog import show_error_message, show_success_message
from school_system.config.logging import logger
from school_system.services.auth_service import AuthService


class UserSessionsWindow(BaseFunctionWindow):
    """Dedicated window for managing user sessions."""

    def __init__(self, parent=None, current_user: str = "", current_role: str = ""):
        """Initialize the user sessions window."""
        super().__init__("User Sessions Management", parent, current_user, current_role)

        self.auth_service = AuthService()

        # Setup content
        self.setup_content()

    def setup_content(self):
        """Setup the user sessions management interface."""
        # Create main content layout
        main_layout = self.create_flex_layout("column", False)
        main_layout.setContentsMargins(24, 24, 24, 24)
        main_layout.set_spacing(24)

        # Create Session Section
        create_section = self._create_session_section()
        main_layout.add_widget(create_section)

        # Expire Session Section
        expire_section = self._expire_session_section()
        main_layout.add_widget(expire_section)

        # Add to content
        self.add_layout_to_content(main_layout)

    def _create_session_section(self) -> QWidget:
        """Create the create user session section."""
        theme_manager = self.get_theme_manager()
        theme = theme_manager._themes[self.get_theme()]

        # Create section container
        section = QWidget()
        section_layout = QVBoxLayout(section)
        section_layout.setContentsMargins(0, 0, 0, 0)
        section_layout.setSpacing(16)

        # Section styling
        section.setStyleSheet(f"""
            QWidget {{
                background-color: {theme["surface"]};
                border: 1px solid {theme["border"]};
                border-radius: 12px;
                padding: 20px;
            }}
        """)

        # Title
        title = QLabel("Create User Session")
        title_font = QFont()
        title_font.setPointSize(16)
        title_font.setBold(True)
        title.setFont(title_font)
        title.setStyleSheet(f"color: {theme['text']}; margin-bottom: 8px;")
        section_layout.addWidget(title)

        # Description
        description = QLabel("Create a new login session for a user with IP address tracking.")
        description.setStyleSheet(f"color: {theme['text_secondary']}; margin-bottom: 16px;")
        section_layout.addWidget(description)

        # Form container
        form_container = QWidget()
        form_layout = QVBoxLayout(form_container)
        form_layout.setContentsMargins(0, 0, 0, 0)
        form_layout.setSpacing(12)

        # Username input
        username_label = QLabel("Username:")
        username_label.setStyleSheet(f"color: {theme['text']}; font-weight: 500;")
        form_layout.addWidget(username_label)

        self.session_username_input = self.create_input("Enter username")
        self.session_username_input.setPlaceholderText("Username for the session")
        form_layout.addWidget(self.session_username_input)

        # IP Address input
        ip_label = QLabel("IP Address:")
        ip_label.setStyleSheet(f"color: {theme['text']}; font-weight: 500;")
        form_layout.addWidget(ip_label)

        self.ip_input = self.create_input("Enter IP address")
        self.ip_input.setPlaceholderText("e.g., 192.168.1.100")
        form_layout.addWidget(self.ip_input)

        # Create button
        create_button = self.create_button("Create Session", "primary")
        create_button.clicked.connect(self._on_create_session)
        form_layout.addWidget(create_button)

        section_layout.addWidget(form_container)
        return section

    def _expire_session_section(self) -> QWidget:
        """Create the expire user session section."""
        theme_manager = self.get_theme_manager()
        theme = theme_manager._themes[self.get_theme()]

        # Create section container
        section = QWidget()
        section_layout = QVBoxLayout(section)
        section_layout.setContentsMargins(0, 0, 0, 0)
        section_layout.setSpacing(16)

        # Section styling
        section.setStyleSheet(f"""
            QWidget {{
                background-color: {theme["surface"]};
                border: 1px solid {theme["border"]};
                border-radius: 12px;
                padding: 20px;
            }}
        """)

        # Title
        title = QLabel("Expire User Session")
        title_font = QFont()
        title_font.setPointSize(16)
        title_font.setBold(True)
        title.setFont(title_font)
        title.setStyleSheet(f"color: {theme['text']}; margin-bottom: 8px;")
        section_layout.addWidget(title)

        # Description
        description = QLabel("Forcefully expire an active user session by session ID.")
        description.setStyleSheet(f"color: {theme['text_secondary']}; margin-bottom: 16px;")
        section_layout.addWidget(description)

        # Form container
        form_container = QWidget()
        form_layout = QVBoxLayout(form_container)
        form_layout.setContentsMargins(0, 0, 0, 0)
        form_layout.setSpacing(12)

        # Session ID input
        session_id_label = QLabel("Session ID:")
        session_id_label.setStyleSheet(f"color: {theme['text']}; font-weight: 500;")
        form_layout.addWidget(session_id_label)

        self.session_id_input = self.create_input("Enter session ID")
        self.session_id_input.setPlaceholderText("Numeric session ID to expire")
        form_layout.addWidget(self.session_id_input)

        # Expire button
        expire_button = QPushButton("Expire Session")
        expire_button.setStyleSheet(f"""
            QPushButton {{
                padding: 10px 20px;
                border-radius: 8px;
                border: 2px solid #ea580c;
                background-color: #ea580c;
                color: white;
                min-height: 36px;
                font-size: 14px;
                font-weight: 600;
            }}

            QPushButton:hover {{
                background-color: #c2410c;
                border-color: #c2410c;
            }}

            QPushButton:pressed {{
                background-color: #9a3412;
            }}
        """)
        expire_button.clicked.connect(self._on_expire_session)
        form_layout.addWidget(expire_button)

        section_layout.addWidget(form_container)
        return section

    def _on_create_session(self):
        """Handle create session button click."""
        try:
            username = self.session_username_input.text().strip()
            ip = self.ip_input.text().strip()

            # Validation
            if not username:
                show_error_message("Error", "Username is required.", self)
                return
            if not ip:
                show_error_message("Error", "IP address is required.", self)
                return

            # Basic IP validation
            if not self._is_valid_ip(ip):
                show_error_message("Error", "Please enter a valid IP address.", self)
                return

            # Create session
            success = self.auth_service.create_user_session(username, ip)
            if success:
                show_success_message("Success", f"Session created for user '{username}' from IP {ip}.", self)
                # Clear form
                self.session_username_input.clear()
                self.ip_input.clear()
            else:
                show_error_message("Error", "Failed to create session. User may not exist or session already active.", self)

        except Exception as e:
            logger.error(f"Error creating user session: {str(e)}")
            show_error_message("Error", f"An error occurred: {str(e)}", self)

    def _on_expire_session(self):
        """Handle expire session button click."""
        try:
            session_id_text = self.session_id_input.text().strip()
            if not session_id_text:
                show_error_message("Error", "Session ID is required.", self)
                return

            session_id = int(session_id_text)
            success = self.auth_service.expire_user_session(session_id)

            if success:
                show_success_message("Success", f"Session {session_id} has been expired.", self)
                # Clear form
                self.session_id_input.clear()
            else:
                show_error_message("Error", f"Session {session_id} not found or already expired.", self)

        except ValueError:
            show_error_message("Error", "Invalid session ID. Please enter a numeric value.", self)
        except Exception as e:
            logger.error(f"Error expiring user session: {str(e)}")
            show_error_message("Error", f"An error occurred: {str(e)}", self)

    def _is_valid_ip(self, ip: str) -> bool:
        """Basic IP address validation."""
        try:
            parts = ip.split('.')
            if len(parts) != 4:
                return False
            for part in parts:
                num = int(part)
                if num < 0 or num > 255:
                    return False
            return True
        except ValueError:
            return False
