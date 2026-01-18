"""
Global Settings Window

Window for managing application-wide settings and system configuration.
"""

from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
                             QLineEdit, QComboBox, QCheckBox, QGroupBox, QTabWidget,
                             QSpinBox, QTextEdit, QMessageBox)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont

from school_system.gui.windows.base_function_window import BaseFunctionWindow
from school_system.gui.dialogs.message_dialog import show_error_message, show_success_message
from school_system.config.logging import logger
from school_system.services.settings_service import SettingsService


class GlobalSettingsWindow(BaseFunctionWindow):
    """Window for managing application-wide settings."""

    def __init__(self, parent=None, current_user: str = "", current_role: str = ""):
        """Initialize the global settings window."""
        super().__init__("Global Settings Management", parent, current_user, current_role)

        # Check if user has admin privileges
        if current_role not in ["admin"]:
            show_error_message("Access Denied", "You do not have permission to access global settings.", self)
            self.close()
            return

        self.settings_service = SettingsService()

        # Setup content
        self.setup_content()

    def setup_content(self):
        """Setup the global settings management interface."""
        # Create main content layout
        main_layout = self.create_flex_layout("column", False)
        main_layout.set_margins(24, 24, 24, 24)
        main_layout.set_spacing(24)

        # Header section
        header_section = self._create_header_section()
        main_layout.add_widget(header_section)

        # Settings Tabs
        settings_tabs = self._create_settings_tabs()
        main_layout.add_widget(settings_tabs)

        # Action Buttons
        action_section = self._create_action_buttons_section()
        main_layout.add_widget(action_section)

        # Add to content
        self.add_layout_to_content(main_layout)

        # Load current settings
        self._load_current_settings()

    def _create_header_section(self) -> QWidget:
        """Create the header section."""
        theme_manager = self.get_theme_manager()
        theme = theme_manager._themes[self.get_theme()]

        header = QWidget()
        layout = QVBoxLayout(header)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(8)

        header.setStyleSheet(f"""
            QWidget {{
                background-color: {theme["surface"]};
                border: 1px solid {theme["border"]};
                border-radius: 12px;
                padding: 20px;
            }}
        """)

        # Title
        title = QLabel("Global Application Settings")
        title_font = QFont()
        title_font.setPointSize(20)
        title_font.setBold(True)
        title.setFont(title_font)
        title.setStyleSheet(f"color: {theme['text']}; margin-bottom: 8px;")
        layout.addWidget(title)

        # Description
        description = QLabel(
            "Configure system-wide settings that affect all users. "
            "Changes here will apply globally across the application."
        )
        description.setStyleSheet(f"color: {theme['text_secondary']};")
        description.setWordWrap(True)
        layout.addWidget(description)

        return header

    def _create_settings_tabs(self) -> QTabWidget:
        """Create the settings tabs widget."""
        tabs = QTabWidget()

        # Create individual tabs
        tabs.addTab(self._create_application_tab(), "🏢 Application")
        tabs.addTab(self._create_database_tab(), "💾 Database")
        tabs.addTab(self._create_security_tab(), "🔐 Security")
        tabs.addTab(self._create_system_tab(), "⚙️ System")
        tabs.addTab(self._create_features_tab(), "✨ Features")

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

    def _create_application_tab(self) -> QWidget:
        """Create the application settings tab."""
        theme_manager = self.get_theme_manager()
        theme = theme_manager._themes[self.get_theme()]

        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(16)

        # Application info
        info_label = QLabel("Application Information:")
        info_label.setStyleSheet(f"color: {theme['text']}; font-weight: 600; font-size: 14px;")
        layout.addWidget(info_label)

        # App name
        name_layout = QHBoxLayout()
        name_label = QLabel("Application Name:")
        name_label.setStyleSheet(f"color: {theme['text']}; font-weight: 500;")
        name_layout.addWidget(name_label)

        self.app_name_input = QLineEdit()
        self.app_name_input.setStyleSheet(self._get_input_style(theme))
        name_layout.addWidget(self.app_name_input)
        layout.addLayout(name_layout)

        # App version
        version_layout = QHBoxLayout()
        version_label = QLabel("Version:")
        version_label.setStyleSheet(f"color: {theme['text']}; font-weight: 500;")
        version_layout.addWidget(version_label)

        self.app_version_input = QLineEdit()
        self.app_version_input.setStyleSheet(self._get_input_style(theme))
        version_layout.addWidget(self.app_version_input)
        layout.addLayout(version_layout)

        # Maintenance mode
        self.maintenance_checkbox = QCheckBox("Enable maintenance mode")
        self.maintenance_checkbox.setStyleSheet(self._get_checkbox_style(theme))
        layout.addWidget(self.maintenance_checkbox)

        # Debug mode
        self.debug_checkbox = QCheckBox("Enable debug mode")
        self.debug_checkbox.setStyleSheet(self._get_checkbox_style(theme))
        layout.addWidget(self.debug_checkbox)

        layout.addStretch()
        return tab

    def _create_database_tab(self) -> QWidget:
        """Create the database settings tab."""
        theme_manager = self.get_theme_manager()
        theme = theme_manager._themes[self.get_theme()]

        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(16)

        # Backup settings
        backup_label = QLabel("Backup Configuration:")
        backup_label.setStyleSheet(f"color: {theme['text']}; font-weight: 600; font-size: 14px;")
        layout.addWidget(backup_label)

        self.backup_enabled_checkbox = QCheckBox("Enable automatic backups")
        self.backup_enabled_checkbox.setStyleSheet(self._get_checkbox_style(theme))
        layout.addWidget(self.backup_enabled_checkbox)

        # Backup interval
        interval_layout = QHBoxLayout()
        interval_label = QLabel("Backup Interval (hours):")
        interval_label.setStyleSheet(f"color: {theme['text']}; font-weight: 500;")
        interval_layout.addWidget(interval_label)

        self.backup_interval_spinbox = QSpinBox()
        self.backup_interval_spinbox.setRange(1, 168)  # 1 hour to 1 week
        self.backup_interval_spinbox.setValue(24)
        self.backup_interval_spinbox.setStyleSheet(self._get_input_style(theme))
        interval_layout.addWidget(self.backup_interval_spinbox)
        layout.addLayout(interval_layout)

        # Max backup files
        max_layout = QHBoxLayout()
        max_label = QLabel("Maximum Backup Files:")
        max_label.setStyleSheet(f"color: {theme['text']}; font-weight: 500;")
        max_layout.addWidget(max_label)

        self.max_backup_spinbox = QSpinBox()
        self.max_backup_spinbox.setRange(1, 100)
        self.max_backup_spinbox.setValue(30)
        self.max_backup_spinbox.setStyleSheet(self._get_input_style(theme))
        max_layout.addWidget(self.max_backup_spinbox)
        layout.addLayout(max_layout)

        # Auto cleanup
        self.auto_cleanup_checkbox = QCheckBox("Automatically cleanup old backups")
        self.auto_cleanup_checkbox.setStyleSheet(self._get_checkbox_style(theme))
        layout.addWidget(self.auto_cleanup_checkbox)

        layout.addStretch()
        return tab

    def _create_security_tab(self) -> QWidget:
        """Create the security settings tab."""
        theme_manager = self.get_theme_manager()
        theme = theme_manager._themes[self.get_theme()]

        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(16)

        # Login settings
        login_label = QLabel("Login Security:")
        login_label.setStyleSheet(f"color: {theme['text']}; font-weight: 600; font-size: 14px;")
        layout.addWidget(login_label)

        # Max attempts
        attempts_layout = QHBoxLayout()
        attempts_label = QLabel("Maximum Login Attempts:")
        attempts_label.setStyleSheet(f"color: {theme['text']}; font-weight: 500;")
        attempts_layout.addWidget(attempts_label)

        self.max_attempts_spinbox = QSpinBox()
        self.max_attempts_spinbox.setRange(1, 10)
        self.max_attempts_spinbox.setValue(3)
        self.max_attempts_spinbox.setStyleSheet(self._get_input_style(theme))
        attempts_layout.addWidget(self.max_attempts_spinbox)
        layout.addLayout(attempts_layout)

        # Session timeout
        timeout_layout = QHBoxLayout()
        timeout_label = QLabel("Session Timeout (minutes):")
        timeout_label.setStyleSheet(f"color: {theme['text']}; font-weight: 500;")
        timeout_layout.addWidget(timeout_label)

        self.session_timeout_spinbox = QSpinBox()
        self.session_timeout_spinbox.setRange(5, 480)  # 5 min to 8 hours
        self.session_timeout_spinbox.setValue(60)
        self.session_timeout_spinbox.setStyleSheet(self._get_input_style(theme))
        timeout_layout.addWidget(self.session_timeout_spinbox)
        layout.addLayout(timeout_layout)

        # Password settings
        password_label = QLabel("Password Requirements:")
        password_label.setStyleSheet(f"color: {theme['text']}; font-weight: 600; font-size: 14px;")
        layout.addWidget(password_label)

        # Min length
        length_layout = QHBoxLayout()
        length_label = QLabel("Minimum Password Length:")
        length_label.setStyleSheet(f"color: {theme['text']}; font-weight: 500;")
        length_layout.addWidget(length_label)

        self.min_password_spinbox = QSpinBox()
        self.min_password_spinbox.setRange(6, 32)
        self.min_password_spinbox.setValue(8)
        self.min_password_spinbox.setStyleSheet(self._get_input_style(theme))
        length_layout.addWidget(self.min_password_spinbox)
        layout.addLayout(length_layout)

        # Special characters
        self.special_chars_checkbox = QCheckBox("Require special characters")
        self.special_chars_checkbox.setStyleSheet(self._get_checkbox_style(theme))
        layout.addWidget(self.special_chars_checkbox)

        # Password expiry
        expiry_layout = QHBoxLayout()
        expiry_label = QLabel("Password Expiry (days):")
        expiry_label.setStyleSheet(f"color: {theme['text']}; font-weight: 500;")
        expiry_layout.addWidget(expiry_label)

        self.password_expiry_spinbox = QSpinBox()
        self.password_expiry_spinbox.setRange(30, 365)
        self.password_expiry_spinbox.setValue(90)
        self.password_expiry_spinbox.setStyleSheet(self._get_input_style(theme))
        expiry_layout.addWidget(self.password_expiry_spinbox)
        layout.addLayout(expiry_layout)

        layout.addStretch()
        return tab

    def _create_system_tab(self) -> QWidget:
        """Create the system settings tab."""
        theme_manager = self.get_theme_manager()
        theme = theme_manager._themes[self.get_theme()]

        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(16)

        # Logging settings
        log_label = QLabel("Logging Configuration:")
        log_label.setStyleSheet(f"color: {theme['text']}; font-weight: 600; font-size: 14px;")
        layout.addWidget(log_label)

        # Log level
        level_layout = QHBoxLayout()
        level_label = QLabel("Log Level:")
        level_label.setStyleSheet(f"color: {theme['text']}; font-weight: 500;")
        level_layout.addWidget(level_label)

        self.log_level_combo = QComboBox()
        self.log_level_combo.addItems(["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"])
        self.log_level_combo.setStyleSheet(self._get_combo_style(theme))
        level_layout.addWidget(self.log_level_combo)
        layout.addLayout(level_layout)

        # File settings
        file_label = QLabel("File Management:")
        file_label.setStyleSheet(f"color: {theme['text']}; font-weight: 600; font-size: 14px;")
        layout.addWidget(file_label)

        # Max file size
        size_layout = QHBoxLayout()
        size_label = QLabel("Maximum File Size (MB):")
        size_label.setStyleSheet(f"color: {theme['text']}; font-weight: 500;")
        size_layout.addWidget(size_label)

        self.max_file_size_spinbox = QSpinBox()
        self.max_file_size_spinbox.setRange(1, 1000)
        self.max_file_size_spinbox.setValue(100)
        self.max_file_size_spinbox.setStyleSheet(self._get_input_style(theme))
        size_layout.addWidget(self.max_file_size_spinbox)
        layout.addLayout(size_layout)

        # Temp file cleanup
        cleanup_layout = QHBoxLayout()
        cleanup_label = QLabel("Temp File Cleanup (hours):")
        cleanup_label.setStyleSheet(f"color: {theme['text']}; font-weight: 500;")
        cleanup_layout.addWidget(cleanup_label)

        self.temp_cleanup_spinbox = QSpinBox()
        self.temp_cleanup_spinbox.setRange(1, 168)
        self.temp_cleanup_spinbox.setValue(24)
        self.temp_cleanup_spinbox.setStyleSheet(self._get_input_style(theme))
        cleanup_layout.addWidget(self.temp_cleanup_spinbox)
        layout.addLayout(cleanup_layout)

        # System notifications
        self.system_notifications_checkbox = QCheckBox("Enable system notifications")
        self.system_notifications_checkbox.setStyleSheet(self._get_checkbox_style(theme))
        layout.addWidget(self.system_notifications_checkbox)

        layout.addStretch()
        return tab

    def _create_features_tab(self) -> QWidget:
        """Create the features settings tab."""
        theme_manager = self.get_theme_manager()
        theme = theme_manager._themes[self.get_theme()]

        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(16)

        # Feature toggles
        features_label = QLabel("Feature Availability:")
        features_label.setStyleSheet(f"color: {theme['text']}; font-weight: 600; font-size: 14px;")
        layout.addWidget(features_label)

        self.qr_enabled_checkbox = QCheckBox("Enable QR code functionality")
        self.qr_enabled_checkbox.setStyleSheet(self._get_checkbox_style(theme))
        layout.addWidget(self.qr_enabled_checkbox)

        self.bulk_ops_checkbox = QCheckBox("Enable bulk operations")
        self.bulk_ops_checkbox.setStyleSheet(self._get_checkbox_style(theme))
        layout.addWidget(self.bulk_ops_checkbox)

        self.advanced_reporting_checkbox = QCheckBox("Enable advanced reporting")
        self.advanced_reporting_checkbox.setStyleSheet(self._get_checkbox_style(theme))
        layout.addWidget(self.advanced_reporting_checkbox)

        self.api_access_checkbox = QCheckBox("Enable API access")
        self.api_access_checkbox.setStyleSheet(self._get_checkbox_style(theme))
        layout.addWidget(self.api_access_checkbox)

        layout.addStretch()
        return tab

    def _create_action_buttons_section(self) -> QWidget:
        """Create the action buttons section."""
        section = QWidget()
        layout = QHBoxLayout(section)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(16)

        # Buttons
        save_button = self.create_button("💾 Save Global Settings", "primary")
        save_button.clicked.connect(self._on_save_settings)
        layout.addWidget(save_button)

        reset_button = self.create_button("🔄 Reset to Defaults", "secondary")
        reset_button.clicked.connect(self._on_reset_settings)
        layout.addWidget(reset_button)

        layout.addStretch()

        return section

    def _get_combo_style(self, theme: dict) -> str:
        """Get consistent combo box styling."""
        return f"""
            QComboBox {{
                padding: 8px 12px;
                border: 1px solid {theme["border"]};
                border-radius: 6px;
                background-color: {theme["surface"]};
                color: {theme["text"]};
                min-height: 32px;
            }}

            QComboBox:hover {{
                border-color: {theme["text_secondary"]};
            }}

            QComboBox:focus {{
                border: 2px solid {theme["border_focus"]};
            }}
        """

    def _get_input_style(self, theme: dict) -> str:
        """Get consistent input field styling."""
        return f"""
            QLineEdit, QSpinBox {{
                padding: 8px 12px;
                border: 1px solid {theme["border"]};
                border-radius: 6px;
                background-color: {theme["surface"]};
                color: {theme["text"]};
                min-height: 32px;
            }}

            QLineEdit:hover, QSpinBox:hover {{
                border-color: {theme["text_secondary"]};
            }}

            QLineEdit:focus, QSpinBox:focus {{
                border: 2px solid {theme["border_focus"]};
            }}
        """

    def _get_checkbox_style(self, theme: dict) -> str:
        """Get consistent checkbox styling."""
        return f"""
            QCheckBox {{
                color: {theme["text"]};
                font-size: 13px;
                spacing: 6px;
            }}

            QCheckBox::indicator {{
                width: 18px;
                height: 18px;
                border: 2px solid {theme["border"]};
                border-radius: 3px;
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

    def _load_current_settings(self):
        """Load current global settings into the UI."""
        try:
            settings = self.settings_service.get_global_settings()

            # Application tab
            app_settings = settings.get("application", {})
            self.app_name_input.setText(app_settings.get("app_name", ""))
            self.app_version_input.setText(app_settings.get("app_version", ""))
            self.maintenance_checkbox.setChecked(app_settings.get("maintenance_mode", False))
            self.debug_checkbox.setChecked(app_settings.get("debug_mode", False))

            # Database tab
            db_settings = settings.get("database", {})
            self.backup_enabled_checkbox.setChecked(db_settings.get("backup_enabled", True))
            self.backup_interval_spinbox.setValue(db_settings.get("backup_interval_hours", 24))
            self.max_backup_spinbox.setValue(db_settings.get("max_backup_files", 30))
            self.auto_cleanup_checkbox.setChecked(db_settings.get("auto_cleanup_backups", True))

            # Security tab
            security_settings = settings.get("security", {})
            self.max_attempts_spinbox.setValue(security_settings.get("max_login_attempts", 3))
            self.session_timeout_spinbox.setValue(security_settings.get("session_timeout_minutes", 60))
            self.min_password_spinbox.setValue(security_settings.get("password_min_length", 8))
            self.special_chars_checkbox.setChecked(security_settings.get("require_special_chars", True))
            self.password_expiry_spinbox.setValue(security_settings.get("password_expiry_days", 90))

            # System tab
            system_settings = settings.get("system", {})
            self.log_level_combo.setCurrentText(system_settings.get("log_level", "INFO"))
            self.max_file_size_spinbox.setValue(system_settings.get("max_file_size_mb", 100))
            self.temp_cleanup_spinbox.setValue(system_settings.get("temp_file_cleanup_hours", 24))
            self.system_notifications_checkbox.setChecked(system_settings.get("system_notifications", True))

            # Features tab
            feature_settings = settings.get("features", {})
            self.qr_enabled_checkbox.setChecked(feature_settings.get("qr_codes_enabled", True))
            self.bulk_ops_checkbox.setChecked(feature_settings.get("bulk_operations_enabled", True))
            self.advanced_reporting_checkbox.setChecked(feature_settings.get("advanced_reporting", True))
            self.api_access_checkbox.setChecked(feature_settings.get("api_access_enabled", False))

        except Exception as e:
            logger.error(f"Error loading global settings: {str(e)}")
            show_error_message("Error", f"Failed to load settings: {str(e)}", self)

    def _collect_settings_from_ui(self) -> dict:
        """Collect all settings from the UI."""
        settings = {
            "application": {
                "app_name": self.app_name_input.text().strip(),
                "app_version": self.app_version_input.text().strip(),
                "maintenance_mode": self.maintenance_checkbox.isChecked(),
                "debug_mode": self.debug_checkbox.isChecked(),
            },
            "database": {
                "backup_enabled": self.backup_enabled_checkbox.isChecked(),
                "backup_interval_hours": self.backup_interval_spinbox.value(),
                "max_backup_files": self.max_backup_spinbox.value(),
                "auto_cleanup_backups": self.auto_cleanup_checkbox.isChecked(),
            },
            "security": {
                "max_login_attempts": self.max_attempts_spinbox.value(),
                "session_timeout_minutes": self.session_timeout_spinbox.value(),
                "password_min_length": self.min_password_spinbox.value(),
                "require_special_chars": self.special_chars_checkbox.isChecked(),
                "password_expiry_days": self.password_expiry_spinbox.value(),
            },
            "system": {
                "log_level": self.log_level_combo.currentText(),
                "max_file_size_mb": self.max_file_size_spinbox.value(),
                "temp_file_cleanup_hours": self.temp_cleanup_spinbox.value(),
                "system_notifications": self.system_notifications_checkbox.isChecked(),
            },
            "features": {
                "qr_codes_enabled": self.qr_enabled_checkbox.isChecked(),
                "bulk_operations_enabled": self.bulk_ops_checkbox.isChecked(),
                "advanced_reporting": self.advanced_reporting_checkbox.isChecked(),
                "api_access_enabled": self.api_access_checkbox.isChecked(),
            }
        }
        return settings

    def _on_save_settings(self):
        """Handle save settings button click."""
        try:
            # Confirm save action
            reply = QMessageBox.question(
                self, "Confirm Save",
                "Are you sure you want to save these global settings? This will affect all users.",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
            )

            if reply != QMessageBox.StandardButton.Yes:
                return

            # Collect settings from UI
            settings_data = self._collect_settings_from_ui()

            # Save settings
            success = self.settings_service.update_global_settings(settings_data)

            if success:
                show_success_message("Success", "Global settings saved successfully.", self)
            else:
                show_error_message("Error", "Failed to save global settings.", self)

        except Exception as e:
            logger.error(f"Error saving global settings: {str(e)}")
            show_error_message("Error", f"An error occurred: {str(e)}", self)

    def _on_reset_settings(self):
        """Handle reset settings button click."""
        try:
            # Confirm reset action
            reply = QMessageBox.question(
                self, "Confirm Reset",
                "Are you sure you want to reset all global settings to defaults? This cannot be undone.",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
            )

            if reply != QMessageBox.StandardButton.Yes:
                return

            # Reset to defaults
            success = self.settings_service.reset_global_settings()

            if success:
                # Reload default settings into UI
                self._load_current_settings()
                show_success_message("Success", "Global settings reset to defaults.", self)
            else:
                show_error_message("Error", "Failed to reset global settings.", self)

        except Exception as e:
            logger.error(f"Error resetting global settings: {str(e)}")
            show_error_message("Error", f"An error occurred: {str(e)}", self)