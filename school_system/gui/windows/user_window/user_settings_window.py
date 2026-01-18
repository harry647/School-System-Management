"""
User Settings Window

Comprehensive window for managing user settings across multiple categories.
"""

from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
                             QLineEdit, QComboBox, QCheckBox, QTextEdit, QGroupBox,
                             QTabWidget, QScrollArea, QFrame, QTimeEdit, QSpinBox)
from PyQt6.QtCore import Qt, pyqtSignal, QTime
from PyQt6.QtGui import QFont

from school_system.gui.windows.base_function_window import BaseFunctionWindow
from school_system.gui.dialogs.message_dialog import show_error_message, show_success_message
from school_system.config.logging import logger
from school_system.services.auth_service import AuthService
from school_system.services.settings_service import SettingsService


class UserSettingsWindow(BaseFunctionWindow):
    """Comprehensive window for managing user settings across multiple categories."""

    def __init__(self, parent=None, current_user: str = "", current_role: str = ""):
        """Initialize the user settings window."""
        super().__init__("User Settings Management", parent, current_user, current_role)

        self.auth_service = AuthService()
        self.settings_service = SettingsService()
        self.current_user_id = None  # Will be set when loading settings

        # Setup content
        self.setup_content()

    def setup_content(self):
        """Setup the comprehensive user settings management interface."""
        # Create main content layout
        main_layout = self.create_flex_layout("column", False)
        main_layout.set_margins(24, 24, 24, 24)
        main_layout.set_spacing(24)

        # User Selection Section
        user_section = self._create_user_selection_section()
        main_layout.add_widget(user_section)

        # Settings Tabs
        settings_tabs = self._create_settings_tabs()
        main_layout.add_widget(settings_tabs)

        # Action Buttons
        action_section = self._create_action_buttons_section()
        main_layout.add_widget(action_section)

        # Add to content
        self.add_layout_to_content(main_layout)

    def _create_user_selection_section(self) -> QWidget:
        """Create the user selection section."""
        theme_manager = self.get_theme_manager()
        theme = theme_manager._themes[self.get_theme()]

        section = QWidget()
        section_layout = QHBoxLayout(section)
        section_layout.setContentsMargins(0, 0, 0, 0)
        section_layout.setSpacing(16)

        section.setStyleSheet(f"""
            QWidget {{
                background-color: {theme["surface"]};
                border: 1px solid {theme["border"]};
                border-radius: 12px;
                padding: 20px;
            }}
        """)

        # Title
        title = QLabel("User Selection")
        title_font = QFont()
        title_font.setPointSize(16)
        title_font.setBold(True)
        title.setFont(title_font)
        title.setStyleSheet(f"color: {theme['text']};")
        section_layout.addWidget(title)

        # User ID input
        userid_label = QLabel("User ID:")
        userid_label.setStyleSheet(f"color: {theme['text']}; font-weight: 500;")
        section_layout.addWidget(userid_label)

        self.user_id_input = self.create_input("Enter user ID")
        self.user_id_input.setPlaceholderText("Numeric user ID")
        section_layout.addWidget(self.user_id_input)

        # Load button
        load_button = self.create_button("Load Settings", "primary")
        load_button.clicked.connect(self._on_load_settings)
        section_layout.addWidget(load_button)

        # Current user info
        self.current_user_label = QLabel(f"Current User: {self.current_user}")
        self.current_user_label.setStyleSheet(f"color: {theme['text_secondary']};")
        section_layout.addStretch()
        section_layout.addWidget(self.current_user_label)

        return section

    def _create_settings_tabs(self) -> QTabWidget:
        """Create the settings tabs widget."""
        tabs = QTabWidget()

        # Create individual tabs
        tabs.addTab(self._create_notifications_tab(), "🔔 Notifications")
        tabs.addTab(self._create_appearance_tab(), "🎨 Appearance")
        tabs.addTab(self._create_behavior_tab(), "⚙️ Behavior")
        tabs.addTab(self._create_export_tab(), "📤 Export")
        tabs.addTab(self._create_privacy_tab(), "🔒 Privacy")

        # Tab styling
        theme_manager = self.get_theme_manager()
        theme = theme_manager._themes[self.get_theme()]

        tabs.setStyleSheet(f"""
            QTabWidget::pane {{
                border: 1px solid {theme["border"]};
                background-color: {theme["surface"]};
                border-radius: 8px;
                padding: 10px;
            }}

            QTabBar::tab {{
                padding: 10px 16px;
                background-color: transparent;
                color: {theme["text_secondary"]};
                border: none;
                border-bottom: 2px solid transparent;
                font-size: 13px;
                font-weight: 500;
                margin-right: 2px;
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
        """)

        return tabs

    def _create_notifications_tab(self) -> QWidget:
        """Create the notifications settings tab."""
        theme_manager = self.get_theme_manager()
        theme = theme_manager._themes[self.get_theme()]

        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(16)

        # Reminder Frequency
        freq_label = QLabel("Reminder Frequency:")
        freq_label.setStyleSheet(f"color: {theme['text']}; font-weight: 600; font-size: 14px;")
        layout.addWidget(freq_label)

        self.reminder_freq_combo = QComboBox()
        self.reminder_freq_combo.addItems(self.settings_service.get_available_reminder_frequencies())
        self.reminder_freq_combo.setStyleSheet(self._get_combo_style(theme))
        layout.addWidget(self.reminder_freq_combo)

        # Reminder Time
        time_label = QLabel("Reminder Time:")
        time_label.setStyleSheet(f"color: {theme['text']}; font-weight: 600; font-size: 14px;")
        layout.addWidget(time_label)

        self.reminder_time_edit = QTimeEdit()
        self.reminder_time_edit.setTime(QTime(9, 0))  # 9:00 AM default
        self.reminder_time_edit.setStyleSheet(self._get_input_style(theme))
        layout.addWidget(self.reminder_time_edit)

        # Notification checkboxes
        self.sound_checkbox = QCheckBox("Enable sound notifications")
        self.sound_checkbox.setStyleSheet(self._get_checkbox_style(theme))
        layout.addWidget(self.sound_checkbox)

        self.email_checkbox = QCheckBox("Enable email notifications")
        self.email_checkbox.setStyleSheet(self._get_checkbox_style(theme))
        layout.addWidget(self.email_checkbox)

        self.push_checkbox = QCheckBox("Enable push notifications")
        self.push_checkbox.setStyleSheet(self._get_checkbox_style(theme))
        layout.addWidget(self.push_checkbox)

        layout.addStretch()
        return tab

    def _create_appearance_tab(self) -> QWidget:
        """Create the appearance settings tab."""
        theme_manager = self.get_theme_manager()
        theme = theme_manager._themes[self.get_theme()]

        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(16)

        # Theme selection
        theme_label = QLabel("Theme:")
        theme_label.setStyleSheet(f"color: {theme['text']}; font-weight: 600; font-size: 14px;")
        layout.addWidget(theme_label)

        self.theme_combo = QComboBox()
        self.theme_combo.addItems(self.settings_service.get_available_themes())
        self.theme_combo.setStyleSheet(self._get_combo_style(theme))
        layout.addWidget(self.theme_combo)

        # Font Size
        font_label = QLabel("Font Size:")
        font_label.setStyleSheet(f"color: {theme['text']}; font-weight: 600; font-size: 14px;")
        layout.addWidget(font_label)

        self.font_size_combo = QComboBox()
        self.font_size_combo.addItems(self.settings_service.get_available_font_sizes())
        self.font_size_combo.setStyleSheet(self._get_combo_style(theme))
        layout.addWidget(self.font_size_combo)

        # Language
        lang_label = QLabel("Language:")
        lang_label.setStyleSheet(f"color: {theme['text']}; font-weight: 600; font-size: 14px;")
        layout.addWidget(lang_label)

        self.language_combo = QComboBox()
        self.language_combo.addItems(self.settings_service.get_available_languages())
        self.language_combo.setStyleSheet(self._get_combo_style(theme))
        layout.addWidget(self.language_combo)

        # Compact View
        self.compact_checkbox = QCheckBox("Enable compact view")
        self.compact_checkbox.setStyleSheet(self._get_checkbox_style(theme))
        layout.addWidget(self.compact_checkbox)

        layout.addStretch()
        return tab

    def _create_behavior_tab(self) -> QWidget:
        """Create the behavior settings tab."""
        theme_manager = self.get_theme_manager()
        theme = theme_manager._themes[self.get_theme()]

        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(16)

        # Behavior checkboxes
        self.auto_save_checkbox = QCheckBox("Enable auto-save")
        self.auto_save_checkbox.setStyleSheet(self._get_checkbox_style(theme))
        layout.addWidget(self.auto_save_checkbox)

        self.confirm_delete_checkbox = QCheckBox("Show confirmation dialogs for deletions")
        self.confirm_delete_checkbox.setStyleSheet(self._get_checkbox_style(theme))
        layout.addWidget(self.confirm_delete_checkbox)

        self.show_tooltips_checkbox = QCheckBox("Show tooltips")
        self.show_tooltips_checkbox.setStyleSheet(self._get_checkbox_style(theme))
        layout.addWidget(self.show_tooltips_checkbox)

        self.keyboard_shortcuts_checkbox = QCheckBox("Enable keyboard shortcuts")
        self.keyboard_shortcuts_checkbox.setStyleSheet(self._get_checkbox_style(theme))
        layout.addWidget(self.keyboard_shortcuts_checkbox)

        layout.addStretch()
        return tab

    def _create_export_tab(self) -> QWidget:
        """Create the export settings tab."""
        theme_manager = self.get_theme_manager()
        theme = theme_manager._themes[self.get_theme()]

        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(16)

        # Default format
        format_label = QLabel("Default Export Format:")
        format_label.setStyleSheet(f"color: {theme['text']}; font-weight: 600; font-size: 14px;")
        layout.addWidget(format_label)

        self.export_format_combo = QComboBox()
        self.export_format_combo.addItems(self.settings_service.get_available_export_formats())
        self.export_format_combo.setStyleSheet(self._get_combo_style(theme))
        layout.addWidget(self.export_format_combo)

        # Export options
        self.include_qr_checkbox = QCheckBox("Include QR codes in exports")
        self.include_qr_checkbox.setStyleSheet(self._get_checkbox_style(theme))
        layout.addWidget(self.include_qr_checkbox)

        self.compress_exports_checkbox = QCheckBox("Compress exported files")
        self.compress_exports_checkbox.setStyleSheet(self._get_checkbox_style(theme))
        layout.addWidget(self.compress_exports_checkbox)

        self.auto_open_checkbox = QCheckBox("Automatically open exported files")
        self.auto_open_checkbox.setStyleSheet(self._get_checkbox_style(theme))
        layout.addWidget(self.auto_open_checkbox)

        layout.addStretch()
        return tab

    def _create_privacy_tab(self) -> QWidget:
        """Create the privacy settings tab."""
        theme_manager = self.get_theme_manager()
        theme = theme_manager._themes[self.get_theme()]

        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(16)

        # Privacy settings
        self.track_activity_checkbox = QCheckBox("Track user activity for analytics")
        self.track_activity_checkbox.setStyleSheet(self._get_checkbox_style(theme))
        layout.addWidget(self.track_activity_checkbox)

        self.share_data_checkbox = QCheckBox("Share usage data for improvements")
        self.share_data_checkbox.setStyleSheet(self._get_checkbox_style(theme))
        layout.addWidget(self.share_data_checkbox)

        # Data retention
        retention_label = QLabel("Data Retention Period (days):")
        retention_label.setStyleSheet(f"color: {theme['text']}; font-weight: 600; font-size: 14px;")
        layout.addWidget(retention_label)

        self.retention_spinbox = QSpinBox()
        self.retention_spinbox.setRange(30, 3650)  # 1 month to 10 years
        self.retention_spinbox.setValue(365)  # 1 year default
        self.retention_spinbox.setStyleSheet(self._get_input_style(theme))
        layout.addWidget(self.retention_spinbox)

        layout.addStretch()
        return tab

    def _get_combo_style(self, theme: dict) -> str:
        """Get consistent combo box styling."""
        return f"""
            QComboBox {{
                padding: 10px 14px;
                border: 1px solid {theme["border"]};
                border-radius: 8px;
                background-color: {theme["surface"]};
                color: {theme["text"]};
                min-height: 36px;
                font-size: 14px;
            }}

            QComboBox:hover {{
                border-color: {theme["text_secondary"]};
            }}

            QComboBox:focus {{
                border: 2px solid {theme["border_focus"]};
            }}

            QComboBox::drop-down {{
                border: none;
                width: 20px;
            }}

            QComboBox::down-arrow {{
                image: none;
                border-left: 4px solid transparent;
                border-right: 4px solid transparent;
                border-top: 4px solid {theme["text"]};
                margin-right: 8px;
            }}
        """

    def _get_input_style(self, theme: dict) -> str:
        """Get consistent input field styling."""
        return f"""
            QTimeEdit, QSpinBox {{
                padding: 10px 14px;
                border: 1px solid {theme["border"]};
                border-radius: 8px;
                background-color: {theme["surface"]};
                color: {theme["text"]};
                min-height: 36px;
                font-size: 14px;
            }}

            QTimeEdit:hover, QSpinBox:hover {{
                border-color: {theme["text_secondary"]};
            }}

            QTimeEdit:focus, QSpinBox:focus {{
                border: 2px solid {theme["border_focus"]};
            }}
        """

    def _get_checkbox_style(self, theme: dict) -> str:
        """Get consistent checkbox styling."""
        return f"""
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
        """

    def _create_action_buttons_section(self) -> QWidget:
        """Create the action buttons section."""
        theme_manager = self.get_theme_manager()
        theme = theme_manager._themes[self.get_theme()]

        section = QWidget()
        layout = QHBoxLayout(section)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(16)

        # Buttons
        save_button = self.create_button("💾 Save Settings", "primary")
        save_button.clicked.connect(self._on_save_settings)
        layout.addWidget(save_button)

        reset_button = self.create_button("🔄 Reset to Defaults", "secondary")
        reset_button.clicked.connect(self._on_reset_settings)
        layout.addWidget(reset_button)

        layout.addStretch()

        return section

    def _on_load_settings(self):
        """Handle load settings button click."""
        try:
            userid_text = self.user_id_input.text().strip()
            if not userid_text:
                show_error_message("Error", "Please enter a user ID.", self)
                return

            user_id = int(userid_text)
            self.current_user_id = user_id

            # Load user settings
            settings = self.settings_service.get_user_settings(user_id)

            # Populate the UI with loaded settings
            self._populate_settings_ui(settings)

            # Update current user info
            self.current_user_label.setText(f"Current User ID: {user_id}")

            show_success_message("Success", f"Settings loaded for user ID {user_id}.", self)

        except ValueError:
            show_error_message("Error", "Invalid user ID. Please enter a numeric value.", self)
        except Exception as e:
            logger.error(f"Error loading user settings: {str(e)}")
            show_error_message("Error", f"An error occurred: {str(e)}", self)

    def _on_save_settings(self):
        """Handle save settings button click."""
        try:
            if not self.current_user_id:
                show_error_message("Error", "Please load user settings first.", self)
                return

            # Collect all settings from UI
            settings_data = self._collect_settings_from_ui()

            # Save settings
            success = self.settings_service.update_user_settings(self.current_user_id, settings_data)

            if success:
                show_success_message("Success", f"Settings saved successfully for user ID {self.current_user_id}.", self)
            else:
                show_error_message("Error", "Failed to save settings.", self)

        except Exception as e:
            logger.error(f"Error saving user settings: {str(e)}")
            show_error_message("Error", f"An error occurred: {str(e)}", self)

    def _on_reset_settings(self):
        """Handle reset settings button click."""
        try:
            if not self.current_user_id:
                show_error_message("Error", "Please load user settings first.", self)
                return

            # Reset to defaults
            success = self.settings_service.reset_user_settings(self.current_user_id)

            if success:
                # Reload default settings into UI
                default_settings = self.settings_service.get_user_settings(self.current_user_id)
                self._populate_settings_ui(default_settings)
                show_success_message("Success", f"Settings reset to defaults for user ID {self.current_user_id}.", self)
            else:
                show_error_message("Error", "Failed to reset settings.", self)

        except Exception as e:
            logger.error(f"Error resetting user settings: {str(e)}")
            show_error_message("Error", f"An error occurred: {str(e)}", self)

    def _populate_settings_ui(self, settings: dict):
        """Populate the UI with settings data."""
        try:
            # Notifications tab
            notifications = settings.get("notifications", {})
            self.reminder_freq_combo.setCurrentText(notifications.get("reminder_frequency", "daily"))

            reminder_time = notifications.get("reminder_time", "09:00")
            time_parts = reminder_time.split(":")
            if len(time_parts) == 2:
                self.reminder_time_edit.setTime(QTime(int(time_parts[0]), int(time_parts[1])))

            self.sound_checkbox.setChecked(notifications.get("sound_enabled", True))
            self.email_checkbox.setChecked(notifications.get("email_notifications", False))
            self.push_checkbox.setChecked(notifications.get("push_notifications", True))

            # Appearance tab
            appearance = settings.get("appearance", {})
            self.theme_combo.setCurrentText(appearance.get("theme", "light"))
            self.font_size_combo.setCurrentText(appearance.get("font_size", "medium"))
            self.language_combo.setCurrentText(appearance.get("language", "en"))
            self.compact_checkbox.setChecked(appearance.get("compact_view", False))

            # Behavior tab
            behavior = settings.get("behavior", {})
            self.auto_save_checkbox.setChecked(behavior.get("auto_save", True))
            self.confirm_delete_checkbox.setChecked(behavior.get("confirm_deletions", True))
            self.show_tooltips_checkbox.setChecked(behavior.get("show_tooltips", True))
            self.keyboard_shortcuts_checkbox.setChecked(behavior.get("keyboard_shortcuts", True))

            # Export tab
            export_settings = settings.get("export", {})
            self.export_format_combo.setCurrentText(export_settings.get("default_format", "excel"))
            self.include_qr_checkbox.setChecked(export_settings.get("include_qr_codes", True))
            self.compress_exports_checkbox.setChecked(export_settings.get("compress_exports", False))
            self.auto_open_checkbox.setChecked(export_settings.get("auto_open_after_export", True))

            # Privacy tab
            privacy = settings.get("privacy", {})
            self.track_activity_checkbox.setChecked(privacy.get("track_activity", True))
            self.share_data_checkbox.setChecked(privacy.get("share_usage_data", False))
            self.retention_spinbox.setValue(privacy.get("data_retention_days", 365))

        except Exception as e:
            logger.error(f"Error populating settings UI: {str(e)}")

    def _collect_settings_from_ui(self) -> dict:
        """Collect all settings from the UI."""
        settings = {
            "notifications": {
                "reminder_frequency": self.reminder_freq_combo.currentText(),
                "reminder_time": self.reminder_time_edit.time().toString("HH:mm"),
                "sound_enabled": self.sound_checkbox.isChecked(),
                "email_notifications": self.email_checkbox.isChecked(),
                "push_notifications": self.push_checkbox.isChecked(),
            },
            "appearance": {
                "theme": self.theme_combo.currentText(),
                "font_size": self.font_size_combo.currentText(),
                "language": self.language_combo.currentText(),
                "compact_view": self.compact_checkbox.isChecked(),
            },
            "behavior": {
                "auto_save": self.auto_save_checkbox.isChecked(),
                "confirm_deletions": self.confirm_delete_checkbox.isChecked(),
                "show_tooltips": self.show_tooltips_checkbox.isChecked(),
                "keyboard_shortcuts": self.keyboard_shortcuts_checkbox.isChecked(),
            },
            "export": {
                "default_format": self.export_format_combo.currentText(),
                "include_qr_codes": self.include_qr_checkbox.isChecked(),
                "compress_exports": self.compress_exports_checkbox.isChecked(),
                "auto_open_after_export": self.auto_open_checkbox.isChecked(),
            },
            "privacy": {
                "track_activity": self.track_activity_checkbox.isChecked(),
                "share_usage_data": self.share_data_checkbox.isChecked(),
                "data_retention_days": self.retention_spinbox.value(),
            }
        }
        return settings
