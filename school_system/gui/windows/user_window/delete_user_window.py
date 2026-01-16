"""
Delete User Window

Dedicated window for deleting user accounts with confirmation.
"""

from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QCheckBox
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont

from school_system.gui.windows.base_function_window import BaseFunctionWindow
from school_system.gui.dialogs.message_dialog import show_error_message, show_success_message
from school_system.config.logging import logger
from school_system.services.auth_service import AuthService
from school_system.gui.windows.user_window.user_validation import UserValidator


class DeleteUserWindow(BaseFunctionWindow):
    """Dedicated window for deleting user accounts with confirmation."""

    user_deleted = pyqtSignal()

    def __init__(self, parent=None, current_user: str = "", current_role: str = "", username_to_delete: str = ""):
        """Initialize the delete user window."""
        super().__init__("Delete User Account", parent, current_user, current_role)

        self.auth_service = AuthService()
        self.validator = UserValidator()
        self.username_to_delete = username_to_delete

        # Setup content
        self.setup_content()

        # Load user data if username provided
        if self.username_to_delete:
            self._load_user_data()

    def setup_content(self):
        """Setup the delete user confirmation form."""
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
        """Create the user deletion confirmation card."""
        theme_manager = self.get_theme_manager()
        theme = theme_manager._themes[self.get_theme()]

        # Create card container
        card = QWidget()
        card_layout = QVBoxLayout(card)
        card_layout.setContentsMargins(24, 24, 24, 24)
        card_layout.setSpacing(16)

        # Apply card styling with danger color
        card.setStyleSheet(f"""
            QWidget {{
                background-color: {theme["surface"]};
                border: 2px solid #ef4444;
                border-radius: 12px;
            }}
        """)

        # Warning icon/title
        warning_container = QWidget()
        warning_layout = QHBoxLayout(warning_container)
        warning_layout.setContentsMargins(0, 0, 0, 0)
        warning_layout.setSpacing(12)

        # Warning icon (using text emoji)
        warning_icon = QLabel("⚠️")
        warning_icon.setStyleSheet("font-size: 24px;")
        warning_layout.addWidget(warning_icon)

        # Title
        title = QLabel("Delete User Account")
        title_font = QFont()
        title_font.setPointSize(18)
        title_font.setBold(True)
        title.setFont(title_font)
        title.setStyleSheet("color: #dc2626; margin-bottom: 8px;")
        warning_layout.addWidget(title)
        warning_layout.addStretch()

        card_layout.addWidget(warning_container)

        # Description
        description = QLabel("This action will permanently remove the user account from the system. This cannot be undone.")
        description.setStyleSheet("color: #dc2626; margin-bottom: 16px; font-weight: 500;")
        description.setWordWrap(True)
        card_layout.addWidget(description)

        # User info container
        info_container = QWidget()
        info_layout = QVBoxLayout(info_container)
        info_layout.setContentsMargins(0, 0, 0, 0)
        info_layout.setSpacing(8)

        # Username field (read-only)
        username_label = QLabel("Username to Delete:")
        username_label.setStyleSheet(f"color: {theme['text']}; font-weight: 500;")
        info_layout.addWidget(username_label)

        self.username_display = QLabel("")
        self.username_display.setStyleSheet(f"""
            QLabel {{
                padding: 10px 14px;
                border: 1px solid {theme["border"]};
                border-radius: 8px;
                background-color: {theme["surface_hover"]};
                color: #dc2626;
                min-height: 36px;
                font-weight: 500;
            }}
        """)
        info_layout.addWidget(self.username_display)

        # Role display
        role_label = QLabel("Current Role:")
        role_label.setStyleSheet(f"color: {theme['text']}; font-weight: 500;")
        info_layout.addWidget(role_label)

        self.role_display = QLabel("")
        self.role_display.setStyleSheet(f"""
            QLabel {{
                padding: 10px 14px;
                border: 1px solid {theme["border"]};
                border-radius: 8px;
                background-color: {theme["surface_hover"]};
                color: {theme["text_secondary"]};
                min-height: 36px;
            }}
        """)
        info_layout.addWidget(self.role_display)

        card_layout.addWidget(info_container)

        # Confirmation checkbox
        self.confirmation_checkbox = QCheckBox("I understand that this action cannot be undone")
        self.confirmation_checkbox.setStyleSheet(f"""
            QCheckBox {{
                color: {theme["text"]};
                font-size: 14px;
                font-weight: 500;
                spacing: 8px;
            }}

            QCheckBox::indicator {{
                width: 20px;
                height: 20px;
                border: 2px solid #ef4444;
                border-radius: 4px;
                background-color: {theme["surface"]};
            }}

            QCheckBox::indicator:hover {{
                border-color: #dc2626;
            }}

            QCheckBox::indicator:checked {{
                background-color: #dc2626;
                border-color: #dc2626;
            }}
        """)
        card_layout.addWidget(self.confirmation_checkbox)

        # Additional warning
        warning_text = QLabel("⚠️ Please ensure no critical data depends on this user account before proceeding.")
        warning_text.setStyleSheet("color: #ea580c; font-size: 13px; margin-top: 8px;")
        warning_text.setWordWrap(True)
        card_layout.addWidget(warning_text)

        # Action buttons
        button_container = QWidget()
        button_layout = QHBoxLayout(button_container)
        button_layout.setContentsMargins(0, 24, 0, 0)
        button_layout.setSpacing(12)

        # Cancel button
        cancel_button = self.create_button("Cancel", "secondary")
        cancel_button.clicked.connect(self.close)
        button_layout.addWidget(cancel_button)

        # Delete button (styled as danger)
        self.delete_button_widget = QPushButton("Delete User")
        self.delete_button_widget.setStyleSheet("""
            QPushButton {
                padding: 10px 20px;
                border-radius: 8px;
                border: 2px solid #dc2626;
                background-color: #dc2626;
                color: white;
                min-height: 36px;
                font-size: 14px;
                font-weight: 600;
            }

            QPushButton:hover {
                background-color: #b91c1c;
                border-color: #b91c1c;
            }

            QPushButton:pressed {
                background-color: #991b1b;
            }

            QPushButton:disabled {
                background-color: #9ca3af;
                border-color: #9ca3af;
                color: #6b7280;
            }
        """)
        self.delete_button_widget.clicked.connect(self._on_delete_user)
        self.delete_button_widget.setEnabled(False)  # Initially disabled until confirmation
        button_layout.addWidget(self.delete_button_widget)

        card_layout.addWidget(button_container)

        # Connect checkbox to enable/disable delete button
        self.confirmation_checkbox.stateChanged.connect(self._on_confirmation_changed)

        return card

    def _load_user_data(self):
        """Load user data for deletion confirmation."""
        try:
            user = self.auth_service.get_user_by_username(self.username_to_delete)
            if user:
                self.username_display.setText(user.username)
                self.role_display.setText(user.role)
            else:
                show_error_message("Error", f"User '{self.username_to_delete}' not found.", self)
                self.close()
        except Exception as e:
            logger.error(f"Error loading user data: {str(e)}")
            show_error_message("Error", f"Failed to load user data: {str(e)}", self)
            self.close()

    def _on_confirmation_changed(self, state):
        """Enable/disable delete button based on confirmation checkbox."""
        self.delete_button_widget.setEnabled(state == Qt.CheckState.Checked)

    def _on_delete_user(self):
        """Handle the delete user button click."""
        try:
            if not self.username_to_delete:
                show_error_message("Error", "No user selected for deletion.", self)
                return

            # Double-check confirmation
            if not self.confirmation_checkbox.isChecked():
                show_error_message("Confirmation Required", "Please check the confirmation box to proceed.", self)
                return

            # Validate deletion
            validation_result = self.validator.validate_user_deletion(self.username_to_delete, self.current_user)
            if not validation_result.is_valid:
                show_error_message("Validation Error", validation_result.error_message, self)
                return

            # Delete the user
            success = self.auth_service.delete_user(self.username_to_delete)
            if success:
                show_success_message("Success", f"User '{self.username_to_delete}' has been permanently deleted.", self)

                # Emit signal and close window
                self.user_deleted.emit()
                self.close()
            else:
                show_error_message("Error", "Failed to delete user. Please try again.", self)

        except Exception as e:
            logger.error(f"Error deleting user: {str(e)}")
            show_error_message("Error", f"An unexpected error occurred: {str(e)}", self)
