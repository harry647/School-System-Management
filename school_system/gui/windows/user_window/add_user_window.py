"""
Add User Window

Dedicated window for adding new users.
"""

from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QLineEdit, QComboBox
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont

from school_system.gui.windows.base_function_window import BaseFunctionWindow
from school_system.gui.dialogs.message_dialog import show_error_message, show_success_message
from school_system.config.logging import logger
from school_system.services.auth_service import AuthService
from school_system.gui.windows.user_window.user_validation import UserValidator


class AddUserWindow(BaseFunctionWindow):
    """Dedicated window for adding new users."""

    user_added = pyqtSignal()

    def __init__(self, parent=None, current_user: str = "", current_role: str = ""):
        """Initialize the add user window."""
        super().__init__("Add New User", parent, current_user, current_role)

        self.auth_service = AuthService()
        self.validator = UserValidator()

        # Setup content
        self.setup_content()

    def setup_content(self):
        """Setup the add user form."""
        # Create main content layout
        main_layout = self.create_flex_layout("column", False)
        main_layout.set_margins(24, 24, 24, 24)
        main_layout.set_spacing(24)

        # Form card
        form_card = self._create_form_card()
        main_layout.add_widget(form_card)

        # Add to content
        self.add_layout_to_content(main_layout)

    def _create_form_card(self) -> QWidget:
        """Create the user form card."""
        theme_manager = self.get_theme_manager()
        theme = theme_manager._themes[self.get_theme()]

        # Create card container
        card = QWidget()
        card_layout = QVBoxLayout(card)
        card_layout.setContentsMargins(24, 24, 24, 24)
        card_layout.setSpacing(16)

        # Apply card styling
        card.setStyleSheet(f"""
            QWidget {{
                background-color: {theme["surface"]};
                border: 1px solid {theme["border"]};
                border-radius: 12px;
            }}
        """)

        # Title
        title = QLabel("Create New User Account")
        title_font = QFont()
        title_font.setPointSize(16)
        title_font.setBold(True)
        title.setFont(title_font)
        title.setStyleSheet(f"color: {theme['text']}; margin-bottom: 8px;")
        card_layout.addWidget(title)

        # Description
        description = QLabel("Fill in the details below to create a new user account in the system.")
        description.setStyleSheet(f"color: {theme['text_secondary']}; margin-bottom: 16px;")
        description.setWordWrap(True)
        card_layout.addWidget(description)

        # Form fields container
        form_container = QWidget()
        form_layout = QVBoxLayout(form_container)
        form_layout.setContentsMargins(0, 0, 0, 0)
        form_layout.setSpacing(16)

        # Username field
        username_label = QLabel("Username:")
        username_label.setStyleSheet(f"color: {theme['text']}; font-weight: 500;")
        form_layout.addWidget(username_label)

        self.username_input = self.create_input("Enter username")
        self.username_input.setPlaceholderText("Choose a unique username")
        form_layout.addWidget(self.username_input)

        # Password field
        password_label = QLabel("Password:")
        password_label.setStyleSheet(f"color: {theme['text']}; font-weight: 500;")
        form_layout.addWidget(password_label)

        self.password_input = self.create_input("Enter a secure password")
        self.password_input.setEchoMode(QLineEdit.EchoMode.Password)
        form_layout.addWidget(self.password_input)

        # Confirm Password field
        confirm_password_label = QLabel("Confirm Password:")
        confirm_password_label.setStyleSheet(f"color: {theme['text']}; font-weight: 500;")
        form_layout.addWidget(confirm_password_label)

        self.confirm_password_input = self.create_input("Re-enter the password")
        self.confirm_password_input.setEchoMode(QLineEdit.EchoMode.Password)
        form_layout.addWidget(self.confirm_password_input)

        # Role field
        role_label = QLabel("Role:")
        role_label.setStyleSheet(f"color: {theme['text']}; font-weight: 500;")
        form_layout.addWidget(role_label)

        self.role_combo = QComboBox()
        self.role_combo.addItems(["student", "teacher", "librarian", "admin"])
        self.role_combo.setCurrentText("student")  # Default to student
        self.role_combo.setStyleSheet(f"""
            QComboBox {{
                padding: 10px 14px;
                border: 1px solid {theme["border"]};
                border-radius: 8px;
                background-color: {theme["surface"]};
                color: {theme["text"]};
                min-height: 36px;
            }}

            QComboBox:hover {{
                border-color: {theme["text_secondary"]};
            }}

            QComboBox:focus {{
                border: 2px solid {theme["border_focus"]};
            }}

            QComboBox::drop-down {{
                border: none;
                width: 30px;
            }}

            QComboBox::down-arrow {{
                image: none;
                border-left: 5px solid transparent;
                border-right: 5px solid transparent;
                border-top: 5px solid {theme["text"]};
                margin-right: 10px;
            }}
        """)
        form_layout.addWidget(self.role_combo)

        card_layout.addWidget(form_container)

        # Action buttons
        button_container = QWidget()
        button_layout = QHBoxLayout(button_container)
        button_layout.setContentsMargins(0, 24, 0, 0)
        button_layout.setSpacing(12)

        # Cancel button
        cancel_button = self.create_button("Cancel", "secondary")
        cancel_button.clicked.connect(self.close)
        button_layout.addWidget(cancel_button)

        # Create button
        self.create_button_widget = self.create_button("Create User", "primary")
        self.create_button_widget.clicked.connect(self._on_create_user)
        button_layout.addWidget(self.create_button_widget)

        card_layout.addWidget(button_container)

        return card

    def _on_create_user(self):
        """Handle the create user button click."""
        try:
            # Get form data
            username = self.username_input.text().strip()
            password = self.password_input.text()
            confirm_password = self.confirm_password_input.text()
            role = self.role_combo.currentText()

            # Validate form data
            validation_result = self.validator.validate_user_creation(username, password, confirm_password, role)
            if not validation_result.is_valid:
                show_error_message("Validation Error", validation_result.error_message, self)
                return

            # Create the user
            success = self.auth_service.create_user(username, password, role)
            if success:
                show_success_message("Success", f"User '{username}' created successfully with role '{role}'.", self)

                # Emit signal and close window
                self.user_added.emit()
                self.close()
            else:
                show_error_message("Error", "Failed to create user. Please try again.", self)

        except Exception as e:
            logger.error(f"Error creating user: {str(e)}")
            show_error_message("Error", f"An unexpected error occurred: {str(e)}", self)
