"""
Edit User Window

Dedicated window for editing user roles and permissions.
"""

from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QComboBox
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont

from school_system.gui.windows.base_function_window import BaseFunctionWindow
from school_system.gui.dialogs.message_dialog import show_error_message, show_success_message
from school_system.config.logging import logger
from school_system.services.auth_service import AuthService
from school_system.gui.windows.user_window.user_validation import UserValidator


class EditUserWindow(BaseFunctionWindow):
    """Dedicated window for editing user roles and permissions."""

    user_updated = pyqtSignal()

    def __init__(self, parent=None, current_user: str = "", current_role: str = "", username_to_edit: str = ""):
        """Initialize the edit user window."""
        super().__init__("Edit User Role", parent, current_user, current_role)

        self.auth_service = AuthService()
        self.validator = UserValidator()
        self.username_to_edit = username_to_edit

        # Setup content
        self.setup_content()

        # Load user data if username provided
        if self.username_to_edit:
            self._load_user_data()

    def setup_content(self):
        """Setup the edit user form."""
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
        """Create the user edit form card."""
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
        title = QLabel("Update User Role")
        title_font = QFont()
        title_font.setPointSize(16)
        title_font.setBold(True)
        title.setFont(title_font)
        title.setStyleSheet(f"color: {theme['text']}; margin-bottom: 8px;")
        card_layout.addWidget(title)

        # Description
        description = QLabel("Change the role and permissions for an existing user account.")
        description.setStyleSheet(f"color: {theme['text_secondary']}; margin-bottom: 16px;")
        description.setWordWrap(True)
        card_layout.addWidget(description)

        # Form fields container
        form_container = QWidget()
        form_layout = QVBoxLayout(form_container)
        form_layout.setContentsMargins(0, 0, 0, 0)
        form_layout.setSpacing(16)

        # Username field (read-only)
        username_label = QLabel("Username:")
        username_label.setStyleSheet(f"color: {theme['text']}; font-weight: 500;")
        form_layout.addWidget(username_label)

        self.username_display = QLabel("")
        self.username_display.setStyleSheet(f"""
            QLabel {{
                padding: 10px 14px;
                border: 1px solid {theme["border"]};
                border-radius: 8px;
                background-color: {theme["surface_hover"]};
                color: {theme["text_secondary"]};
                min-height: 36px;
            }}
        """)
        form_layout.addWidget(self.username_display)

        # Current Role display
        current_role_label = QLabel("Current Role:")
        current_role_label.setStyleSheet(f"color: {theme['text']}; font-weight: 500;")
        form_layout.addWidget(current_role_label)

        self.current_role_display = QLabel("")
        self.current_role_display.setStyleSheet(f"""
            QLabel {{
                padding: 10px 14px;
                border: 1px solid {theme["border"]};
                border-radius: 8px;
                background-color: {theme["surface_hover"]};
                color: {theme["text_secondary"]};
                min-height: 36px;
            }}
        """)
        form_layout.addWidget(self.current_role_display)

        # New Role field
        new_role_label = QLabel("New Role:")
        new_role_label.setStyleSheet(f"color: {theme['text']}; font-weight: 500;")
        form_layout.addWidget(new_role_label)

        self.new_role_combo = QComboBox()
        self.new_role_combo.addItems(["student", "teacher", "librarian", "admin"])
        self.new_role_combo.setStyleSheet(f"""
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
        form_layout.addWidget(self.new_role_combo)

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

        # Update button
        self.update_button_widget = self.create_button("Update Role", "primary")
        self.update_button_widget.clicked.connect(self._on_update_user)
        button_layout.addWidget(self.update_button_widget)

        card_layout.addWidget(button_container)

        return card

    def _load_user_data(self):
        """Load user data for editing."""
        try:
            user = self.auth_service.get_user_by_username(self.username_to_edit)
            if user:
                self.username_display.setText(user.username)
                self.current_role_display.setText(user.role)
                # Set current role as default in combo box
                index = self.new_role_combo.findText(user.role)
                if index >= 0:
                    self.new_role_combo.setCurrentIndex(index)
            else:
                show_error_message("Error", f"User '{self.username_to_edit}' not found.", self)
                self.close()
        except Exception as e:
            logger.error(f"Error loading user data: {str(e)}")
            show_error_message("Error", f"Failed to load user data: {str(e)}", self)
            self.close()

    def _on_update_user(self):
        """Handle the update user button click."""
        try:
            if not self.username_to_edit:
                show_error_message("Error", "No user selected for editing.", self)
                return

            # Get new role
            new_role = self.new_role_combo.currentText()
            current_role = self.current_role_display.text()

            # Check if role actually changed
            if new_role == current_role:
                show_error_message("No Changes", "The selected role is the same as the current role.", self)
                return

            # Validate role change
            validation_result = self.validator.validate_role_update(self.username_to_edit, new_role)
            if not validation_result.is_valid:
                show_error_message("Validation Error", validation_result.error_message, self)
                return

            # Update the user role
            success = self.auth_service.update_user_role(self.username_to_edit, new_role)
            if success:
                show_success_message("Success", f"User '{self.username_to_edit}' role updated to '{new_role}'.", self)

                # Emit signal and close window
                self.user_updated.emit()
                self.close()
            else:
                show_error_message("Error", "Failed to update user role. Please try again.", self)

        except Exception as e:
            logger.error(f"Error updating user: {str(e)}")
            show_error_message("Error", f"An unexpected error occurred: {str(e)}", self)
