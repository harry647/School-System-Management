"""
User Settings Window

Dedicated window for managing user settings (reminder frequency, sound notifications).
"""

from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QLineEdit, QComboBox, QCheckBox, QTextEdit, QGroupBox
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont

from school_system.gui.windows.base_function_window import BaseFunctionWindow
from school_system.gui.dialogs.message_dialog import show_error_message, show_success_message
from school_system.config.logging import logger
from school_system.services.auth_service import AuthService


class UserSettingsWindow(BaseFunctionWindow):
    """Dedicated window for managing user settings."""

    def __init__(self, parent=None, current_user: str = "", current_role: str = ""):
        """Initialize the user settings window."""
        super().__init__("User Settings Management", parent, current_user, current_role)

        self.auth_service = AuthService()

        # Setup content
        self.setup_content()

    def setup_content(self):
        """Setup the user settings management interface."""
        # Create main content layout
        main_layout = self.create_flex_layout("column", False)
        main_layout.set_margins(24, 24, 24, 24)
        main_layout.set_spacing(24)

        # Get Settings Section
        get_section = self._create_get_settings_section()
        main_layout.add_widget(get_section)

        # Update Settings Section
        update_section = self._create_update_settings_section()
        main_layout.add_widget(update_section)

        # Add to content
        self.add_layout_to_content(main_layout)

    def _create_get_settings_section(self) -> QWidget:
        """Create the get user settings section."""
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
        title = QLabel("Get User Settings")
        title_font = QFont()
        title_font.setPointSize(16)
        title_font.setBold(True)
        title.setFont(title_font)
        title.setStyleSheet(f"color: {theme['text']}; margin-bottom: 8px;")
        section_layout.addWidget(title)

        # Description
        description = QLabel("Retrieve current settings for a specific user by their ID.")
        description.setStyleSheet(f"color: {theme['text_secondary']}; margin-bottom: 16px;")
        section_layout.addWidget(description)

        # Form container
        form_container = QWidget()
        form_layout = QVBoxLayout(form_container)
        form_layout.setContentsMargins(0, 0, 0, 0)
        form_layout.setSpacing(12)

        # User ID input
        userid_label = QLabel("User ID:")
        userid_label.setStyleSheet(f"color: {theme['text']}; font-weight: 500;")
        form_layout.addWidget(userid_label)

        self.get_userid_input = self.create_input("Enter user ID")
        self.get_userid_input.setPlaceholderText("Numeric user ID")
        form_layout.addWidget(self.get_userid_input)

        # Get button
        get_button = self.create_button("Get Settings", "primary")
        get_button.clicked.connect(self._on_get_settings)
        form_layout.addWidget(get_button)

        # Settings display
        display_label = QLabel("Current Settings:")
        display_label.setStyleSheet(f"color: {theme['text']}; font-weight: 500;")
        form_layout.addWidget(display_label)

        self.settings_display = QTextEdit()
        self.settings_display.setReadOnly(True)
        self.settings_display.setMaximumHeight(100)
        self.settings_display.setStyleSheet(f"""
            QTextEdit {{
                border: 1px solid {theme["border"]};
                border-radius: 8px;
                background-color: {theme["surface_hover"]};
                color: {theme["text"]};
                padding: 8px;
            }}
        """)
        self.settings_display.setPlainText("No settings loaded yet.")
        form_layout.addWidget(self.settings_display)

        section_layout.addWidget(form_container)
        return section

    def _create_update_settings_section(self) -> QWidget:
        """Create the update user settings section."""
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
        title = QLabel("Update User Settings")
        title_font = QFont()
        title_font.setPointSize(16)
        title_font.setBold(True)
        title.setFont(title_font)
        title.setStyleSheet(f"color: {theme['text']}; margin-bottom: 8px;")
        section_layout.addWidget(title)

        # Description
        description = QLabel("Modify reminder frequency and notification preferences for a user.")
        description.setStyleSheet(f"color: {theme['text_secondary']}; margin-bottom: 16px;")
        section_layout.addWidget(description)

        # Form container
        form_container = QWidget()
        form_layout = QVBoxLayout(form_container)
        form_layout.setContentsMargins(0, 0, 0, 0)
        form_layout.setSpacing(12)

        # User ID input
        update_userid_label = QLabel("User ID:")
        update_userid_label.setStyleSheet(f"color: {theme['text']}; font-weight: 500;")
        form_layout.addWidget(update_userid_label)

        self.update_userid_input = self.create_input("Enter user ID")
        self.update_userid_input.setPlaceholderText("Numeric user ID")
        form_layout.addWidget(self.update_userid_input)

        # Reminder Frequency
        freq_label = QLabel("Reminder Frequency:")
        freq_label.setStyleSheet(f"color: {theme['text']}; font-weight: 500;")
        form_layout.addWidget(freq_label)

        self.freq_combo = QComboBox()
        self.freq_combo.addItems(["daily", "weekly", "monthly"])
        self.freq_combo.setCurrentText("daily")  # Default
        self.freq_combo.setStyleSheet(f"""
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
        """)
        form_layout.addWidget(self.freq_combo)

        # Sound Enabled
        sound_label = QLabel("Sound Notifications:")
        sound_label.setStyleSheet(f"color: {theme['text']}; font-weight: 500;")
        form_layout.addWidget(sound_label)

        self.sound_checkbox = QCheckBox("Enable sound notifications")
        self.sound_checkbox.setChecked(True)  # Default enabled
        self.sound_checkbox.setStyleSheet(f"""
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
        form_layout.addWidget(self.sound_checkbox)

        # Update button
        update_button = self.create_button("Update Settings", "secondary")
        update_button.clicked.connect(self._on_update_settings)
        form_layout.addWidget(update_button)

        section_layout.addWidget(form_container)
        return section

    def _on_get_settings(self):
        """Handle get settings button click."""
        try:
            userid_text = self.get_userid_input.text().strip()
            if not userid_text:
                show_error_message("Error", "Please enter a user ID.", self)
                return

            user_id = int(userid_text)
            settings = self.auth_service.get_user_setting(user_id)

            if settings:
                display_text = f"""Reminder Frequency: {settings.reminder_frequency}
Sound Enabled: {settings.sound_enabled}
Last Updated: {settings.updated_at if hasattr(settings, 'updated_at') else 'N/A'}"""
                self.settings_display.setPlainText(display_text)
                show_success_message("Success", "Settings retrieved successfully.", self)
            else:
                self.settings_display.setPlainText("No settings found for this user.")
                show_error_message("Not Found", "No settings found for this user ID.", self)

        except ValueError:
            show_error_message("Error", "Invalid user ID. Please enter a numeric value.", self)
        except Exception as e:
            logger.error(f"Error getting user settings: {str(e)}")
            show_error_message("Error", f"An error occurred: {str(e)}", self)

    def _on_update_settings(self):
        """Handle update settings button click."""
        try:
            userid_text = self.update_userid_input.text().strip()
            if not userid_text:
                show_error_message("Error", "Please enter a user ID.", self)
                return

            user_id = int(userid_text)
            freq = self.freq_combo.currentText()
            sound = self.sound_checkbox.isChecked()

            # Try to update, if not exist, create
            existing = self.auth_service.get_user_setting(user_id)
            if existing:
                success = self.auth_service.update_user_setting(user_id, freq, sound)
                message = "Settings updated successfully."
            else:
                success = self.auth_service.create_user_setting(user_id, freq, sound)
                message = "Settings created successfully."

            if success:
                show_success_message("Success", message, self)
                # Clear form
                self.update_userid_input.clear()
                self.freq_combo.setCurrentText("daily")
                self.sound_checkbox.setChecked(True)
            else:
                show_error_message("Error", "Failed to save settings.", self)

        except ValueError:
            show_error_message("Error", "Invalid user ID. Please enter a numeric value.", self)
        except Exception as e:
            logger.error(f"Error updating user settings: {str(e)}")
            show_error_message("Error", f"An error occurred: {str(e)}", self)
