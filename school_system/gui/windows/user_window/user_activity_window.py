"""
User Activity Window

Dedicated window for managing user activity logging and tracking.
"""

from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QLineEdit, QTextEdit, QGroupBox
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont

from school_system.gui.windows.base_function_window import BaseFunctionWindow
from school_system.gui.dialogs.message_dialog import show_error_message, show_success_message
from school_system.config.logging import logger
from school_system.services.auth_service import AuthService


class UserActivityWindow(BaseFunctionWindow):
    """Dedicated window for managing user activity logging and tracking."""

    def __init__(self, parent=None, current_user: str = "", current_role: str = ""):
        """Initialize the user activity window."""
        super().__init__("User Activity Management", parent, current_user, current_role)

        self.auth_service = AuthService()

        # Setup content
        self.setup_content()

    def setup_content(self):
        """Setup the user activity management interface."""
        # Create main content layout
        main_layout = self.create_flex_layout("column", False)
        main_layout.set_margins(24, 24, 24, 24)
        main_layout.set_spacing(24)

        # Log Action Section
        log_section = self._create_log_action_section()
        main_layout.add_widget(log_section)

        # Track Activity Section
        track_section = self._create_track_activity_section()
        main_layout.add_widget(track_section)

        # Password Reset Section
        reset_section = self._create_password_reset_section()
        main_layout.add_widget(reset_section)

        # Add to content
        self.add_layout_to_content(main_layout)

    def _create_log_action_section(self) -> QWidget:
        """Create the log user action section."""
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
        title = QLabel("Log User Action")
        title_font = QFont()
        title_font.setPointSize(16)
        title_font.setBold(True)
        title.setFont(title_font)
        title.setStyleSheet(f"color: {theme['text']}; margin-bottom: 8px;")
        section_layout.addWidget(title)

        # Description
        description = QLabel("Record a specific action performed by a user in the system.")
        description.setStyleSheet(f"color: {theme['text_secondary']}; margin-bottom: 16px;")
        section_layout.addWidget(description)

        # Form container
        form_container = QWidget()
        form_layout = QVBoxLayout(form_container)
        form_layout.setContentsMargins(0, 0, 0, 0)
        form_layout.setSpacing(12)

        # Username input
        log_username_label = QLabel("Username:")
        log_username_label.setStyleSheet(f"color: {theme['text']}; font-weight: 500;")
        form_layout.addWidget(log_username_label)

        self.log_username_input = self.create_input("Enter username")
        self.log_username_input.setPlaceholderText("Username of the user performing the action")
        form_layout.addWidget(self.log_username_input)

        # Action input
        action_label = QLabel("Action:")
        action_label.setStyleSheet(f"color: {theme['text']}; font-weight: 500;")
        form_layout.addWidget(action_label)

        self.action_input = self.create_input("Enter action")
        self.action_input.setPlaceholderText("e.g., 'login', 'view_report', 'update_profile'")
        form_layout.addWidget(self.action_input)

        # Details input
        details_label = QLabel("Details:")
        details_label.setStyleSheet(f"color: {theme['text']}; font-weight: 500;")
        form_layout.addWidget(details_label)

        self.details_input = QTextEdit()
        self.details_input.setMaximumHeight(80)
        self.details_input.setPlaceholderText("Additional details about the action...")
        self.details_input.setStyleSheet(f"""
            QTextEdit {{
                border: 1px solid {theme["border"]};
                border-radius: 8px;
                background-color: {theme["surface"]};
                color: {theme["text"]};
                padding: 8px;
            }}

            QTextEdit:focus {{
                border: 2px solid {theme["border_focus"]};
            }}
        """)
        form_layout.addWidget(self.details_input)

        # Log button
        log_button = self.create_button("Log Action", "primary")
        log_button.clicked.connect(self._on_log_action)
        form_layout.addWidget(log_button)

        section_layout.addWidget(form_container)
        return section

    def _create_track_activity_section(self) -> QWidget:
        """Create the track user activity section."""
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
        title = QLabel("Track User Activity")
        title_font = QFont()
        title_font.setPointSize(16)
        title_font.setBold(True)
        title.setFont(title_font)
        title.setStyleSheet(f"color: {theme['text']}; margin-bottom: 8px;")
        section_layout.addWidget(title)

        # Description
        description = QLabel("Track ongoing user activities and behaviors in the system.")
        description.setStyleSheet(f"color: {theme['text_secondary']}; margin-bottom: 16px;")
        section_layout.addWidget(description)

        # Form container
        form_container = QWidget()
        form_layout = QVBoxLayout(form_container)
        form_layout.setContentsMargins(0, 0, 0, 0)
        form_layout.setSpacing(12)

        # Username input
        track_username_label = QLabel("Username:")
        track_username_label.setStyleSheet(f"color: {theme['text']}; font-weight: 500;")
        form_layout.addWidget(track_username_label)

        self.track_username_input = self.create_input("Enter username")
        self.track_username_input.setPlaceholderText("Username of the user to track")
        form_layout.addWidget(self.track_username_input)

        # Activity Type input
        activity_type_label = QLabel("Activity Type:")
        activity_type_label.setStyleSheet(f"color: {theme['text']}; font-weight: 500;")
        form_layout.addWidget(activity_type_label)

        self.activity_type_input = self.create_input("Enter activity type")
        self.activity_type_input.setPlaceholderText("e.g., 'browsing', 'editing', 'searching'")
        form_layout.addWidget(self.activity_type_input)

        # Details input
        track_details_label = QLabel("Details:")
        track_details_label.setStyleSheet(f"color: {theme['text']}; font-weight: 500;")
        form_layout.addWidget(track_details_label)

        self.track_details_input = QTextEdit()
        self.track_details_input.setMaximumHeight(80)
        self.track_details_input.setPlaceholderText("Activity details and context...")
        self.track_details_input.setStyleSheet(f"""
            QTextEdit {{
                border: 1px solid {theme["border"]};
                border-radius: 8px;
                background-color: {theme["surface"]};
                color: {theme["text"]};
                padding: 8px;
            }}

            QTextEdit:focus {{
                border: 2px solid {theme["border_focus"]};
            }}
        """)
        form_layout.addWidget(self.track_details_input)

        # Track button
        track_button = self.create_button("Track Activity", "secondary")
        track_button.clicked.connect(self._on_track_activity)
        form_layout.addWidget(track_button)

        section_layout.addWidget(form_container)
        return section

    def _create_password_reset_section(self) -> QWidget:
        """Create the password reset request section."""
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
        title = QLabel("Request Password Reset")
        title_font = QFont()
        title_font.setPointSize(16)
        title_font.setBold(True)
        title.setFont(title_font)
        title.setStyleSheet(f"color: {theme['text']}; margin-bottom: 8px;")
        section_layout.addWidget(title)

        # Description
        description = QLabel("Initiate a password reset request for a user account.")
        description.setStyleSheet(f"color: {theme['text_secondary']}; margin-bottom: 16px;")
        section_layout.addWidget(description)

        # Form container
        form_container = QWidget()
        form_layout = QVBoxLayout(form_container)
        form_layout.setContentsMargins(0, 0, 0, 0)
        form_layout.setSpacing(12)

        # Username input
        reset_username_label = QLabel("Username:")
        reset_username_label.setStyleSheet(f"color: {theme['text']}; font-weight: 500;")
        form_layout.addWidget(reset_username_label)

        self.reset_username_input = self.create_input("Enter username")
        self.reset_username_input.setPlaceholderText("Username requesting password reset")
        form_layout.addWidget(self.reset_username_input)

        # Reset button
        reset_button = self.create_button("Request Reset", "secondary")
        reset_button.clicked.connect(self._on_password_reset)
        form_layout.addWidget(reset_button)

        section_layout.addWidget(form_container)
        return section

    def _on_log_action(self):
        """Handle log action button click."""
        try:
            username = self.log_username_input.text().strip()
            action = self.action_input.text().strip()
            details = self.details_input.toPlainText().strip()

            # Validation
            if not username:
                show_error_message("Error", "Username is required.", self)
                return
            if not action:
                show_error_message("Error", "Action is required.", self)
                return

            # Log action
            success = self.auth_service.log_user_action(username, action, details)
            if success:
                show_success_message("Success", f"Action '{action}' logged for user '{username}'.", self)
                # Clear form
                self.log_username_input.clear()
                self.action_input.clear()
                self.details_input.clear()
            else:
                show_error_message("Error", "Failed to log action. User may not exist.", self)

        except Exception as e:
            logger.error(f"Error logging user action: {str(e)}")
            show_error_message("Error", f"An error occurred: {str(e)}", self)

    def _on_track_activity(self):
        """Handle track activity button click."""
        try:
            username = self.track_username_input.text().strip()
            activity_type = self.activity_type_input.text().strip()
            details = self.track_details_input.toPlainText().strip()

            # Validation
            if not username:
                show_error_message("Error", "Username is required.", self)
                return
            if not activity_type:
                show_error_message("Error", "Activity type is required.", self)
                return

            # Track activity
            success = self.auth_service.track_user_activity(username, activity_type, details)
            if success:
                show_success_message("Success", f"Activity '{activity_type}' tracked for user '{username}'.", self)
                # Clear form
                self.track_username_input.clear()
                self.activity_type_input.clear()
                self.track_details_input.clear()
            else:
                show_error_message("Error", "Failed to track activity. User may not exist.", self)

        except Exception as e:
            logger.error(f"Error tracking user activity: {str(e)}")
            show_error_message("Error", f"An error occurred: {str(e)}", self)

    def _on_password_reset(self):
        """Handle password reset button click."""
        try:
            username = self.reset_username_input.text().strip()

            # Validation
            if not username:
                show_error_message("Error", "Username is required.", self)
                return

            # Request password reset
            success = self.auth_service.request_password_reset(username)
            if success:
                show_success_message("Success", f"Password reset requested for user '{username}'.", self)
                # Clear form
                self.reset_username_input.clear()
            else:
                show_error_message("Error", "Failed to request password reset. User may not exist.", self)

        except Exception as e:
            logger.error(f"Error requesting password reset: {str(e)}")
            show_error_message("Error", f"An error occurred: {str(e)}", self)
