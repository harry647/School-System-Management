"""
Settings Service

Comprehensive service for managing application-wide and user-specific settings.
Handles both global application settings and individual user preferences.
"""

from typing import Dict, Any, Optional, List
import json
import os
from datetime import datetime

from school_system.config.logging import logger
from school_system.config.settings import Settings as GlobalSettings
from school_system.core.exceptions import DatabaseException, ValidationError
from school_system.core.utils import ValidationUtils
from school_system.models.user import UserSetting, GlobalSetting
from school_system.database.repositories.user_repo import UserSettingRepository, GlobalSettingRepository


class SettingsService:
    """Service for managing application settings and user preferences."""

    # Default settings for various categories
    DEFAULT_USER_SETTINGS = {
        "notifications": {
            "reminder_frequency": "daily",
            "sound_enabled": True,
            "email_notifications": False,
            "push_notifications": True,
            "reminder_time": "09:00",  # 9 AM
        },
        "appearance": {
            "theme": "light",
            "font_size": "medium",
            "language": "en",
            "compact_view": False,
        },
        "behavior": {
            "auto_save": True,
            "confirm_deletions": True,
            "show_tooltips": True,
            "keyboard_shortcuts": True,
        },
        "export": {
            "default_format": "excel",
            "include_qr_codes": True,
            "compress_exports": False,
            "auto_open_after_export": True,
        },
        "privacy": {
            "track_activity": True,
            "share_usage_data": False,
            "data_retention_days": 365,
        }
    }

    DEFAULT_GLOBAL_SETTINGS = {
        "application": {
            "app_name": "School System Management",
            "app_version": "1.0.0",
            "maintenance_mode": False,
            "debug_mode": False,
        },
        "database": {
            "backup_enabled": True,
            "backup_interval_hours": 24,
            "max_backup_files": 30,
            "auto_cleanup_backups": True,
        },
        "security": {
            "max_login_attempts": 3,
            "session_timeout_minutes": 60,
            "password_min_length": 8,
            "require_special_chars": True,
            "password_expiry_days": 90,
        },
        "system": {
            "log_level": "INFO",
            "max_file_size_mb": 100,
            "temp_file_cleanup_hours": 24,
            "system_notifications": True,
        },
        "features": {
            "qr_codes_enabled": True,
            "bulk_operations_enabled": True,
            "advanced_reporting": True,
            "api_access_enabled": False,
        }
    }

    def __init__(self):
        """Initialize the settings service."""
        self.user_setting_repository = UserSettingRepository()
        self.global_setting_repository = GlobalSettingRepository()
        self.global_settings = GlobalSettings()

    # ===== USER SETTINGS METHODS =====

    def get_user_settings(self, user_id: int, category: str = None) -> Dict[str, Any]:
        """
        Get user settings for a specific user.

        Args:
            user_id: The user ID
            category: Optional category filter (e.g., 'notifications', 'appearance')

        Returns:
            Dictionary containing user settings
        """
        try:
            logger.info(f"Retrieving user settings for user ID: {user_id}")

            # Try to get from database first
            user_setting = self.user_setting_repository.get_by_id(user_id)

            if user_setting:
                # Parse stored settings
                settings = json.loads(user_setting.settings_json) if user_setting.settings_json else {}
            else:
                # Use defaults if no settings exist
                settings = self.DEFAULT_USER_SETTINGS.copy()

            # Merge with defaults to ensure all keys exist
            merged_settings = self._merge_with_defaults(settings, self.DEFAULT_USER_SETTINGS)

            if category and category in merged_settings:
                return merged_settings[category]
            elif category:
                return {}
            else:
                return merged_settings

        except Exception as e:
            logger.error(f"Error retrieving user settings for user {user_id}: {e}")
            return self.DEFAULT_USER_SETTINGS.copy()

    def update_user_settings(self, user_id: int, settings: Dict[str, Any], category: str = None) -> bool:
        """
        Update user settings for a specific user.

        Args:
            user_id: The user ID
            settings: Settings dictionary to update
            category: Optional category to update (updates only that category)

        Returns:
            True if successful, False otherwise
        """
        try:
            logger.info(f"Updating user settings for user ID: {user_id}")

            # Get existing settings
            existing_settings = self.get_user_settings(user_id)

            if category:
                # Update only the specified category
                if category not in existing_settings:
                    existing_settings[category] = {}
                existing_settings[category].update(settings)
            else:
                # Update all settings
                existing_settings.update(settings)

            # Validate settings
            self._validate_user_settings(existing_settings)

            # Save to database
            settings_json = json.dumps(existing_settings)

            # Check if user settings already exist
            user_setting = self.user_setting_repository.get_by_id(user_id)
            if user_setting:
                # Update existing
                user_setting.settings_json = settings_json
                user_setting.updated_at = datetime.now()
                success = self.user_setting_repository.update(user_setting)
            else:
                # Create new
                user_setting = UserSetting(
                    user_id=user_id,
                    settings_json=settings_json,
                    created_at=datetime.now(),
                    updated_at=datetime.now()
                )
                success = self.user_setting_repository.create(user_setting)

            if success:
                logger.info(f"User settings updated successfully for user ID: {user_id}")
            return success

        except Exception as e:
            logger.error(f"Error updating user settings for user {user_id}: {e}")
            return False

    def reset_user_settings(self, user_id: int, category: str = None) -> bool:
        """
        Reset user settings to defaults.

        Args:
            user_id: The user ID
            category: Optional category to reset (resets only that category)

        Returns:
            True if successful, False otherwise
        """
        try:
            logger.info(f"Resetting user settings for user ID: {user_id}")

            if category:
                # Reset only the specified category
                default_settings = {category: self.DEFAULT_USER_SETTINGS.get(category, {})}
                return self.update_user_settings(user_id, default_settings, category)
            else:
                # Reset all settings
                return self.update_user_settings(user_id, self.DEFAULT_USER_SETTINGS.copy())

        except Exception as e:
            logger.error(f"Error resetting user settings for user {user_id}: {e}")
            return False

    # ===== GLOBAL SETTINGS METHODS =====

    def get_global_settings(self, category: str = None) -> Dict[str, Any]:
        """
        Get global application settings.

        Args:
            category: Optional category filter

        Returns:
            Dictionary containing global settings
        """
        try:
            logger.info("Retrieving global settings")

            # Try to get from database first
            global_setting = self.global_setting_repository.get_by_key("global_settings")

            if global_setting:
                # Parse stored settings
                settings = json.loads(global_setting.value_json) if global_setting.value_json else {}
            else:
                # Use defaults if no settings exist
                settings = self.DEFAULT_GLOBAL_SETTINGS.copy()

            # Merge with defaults to ensure all keys exist
            merged_settings = self._merge_with_defaults(settings, self.DEFAULT_GLOBAL_SETTINGS)

            if category and category in merged_settings:
                return merged_settings[category]
            elif category:
                return {}
            else:
                return merged_settings

        except Exception as e:
            logger.error(f"Error retrieving global settings: {e}")
            return self.DEFAULT_GLOBAL_SETTINGS.copy()

    def update_global_settings(self, settings: Dict[str, Any], category: str = None) -> bool:
        """
        Update global application settings.

        Args:
            settings: Settings dictionary to update
            category: Optional category to update

        Returns:
            True if successful, False otherwise
        """
        try:
            logger.info("Updating global settings")

            # Get existing settings
            existing_settings = self.get_global_settings()

            if category:
                # Update only the specified category
                if category not in existing_settings:
                    existing_settings[category] = {}
                existing_settings[category].update(settings)
            else:
                # Update all settings
                existing_settings.update(settings)

            # Validate settings
            self._validate_global_settings(existing_settings)

            # Save to database
            settings_json = json.dumps(existing_settings)

            # Check if global settings already exist
            global_setting = self.global_setting_repository.get_by_key("global_settings")
            if global_setting:
                # Update existing
                global_setting.value_json = settings_json
                global_setting.updated_at = datetime.now()
                success = self.global_setting_repository.update(global_setting)
            else:
                # Create new
                global_setting = GlobalSetting(
                    key="global_settings",
                    value_json=settings_json,
                    created_at=datetime.now(),
                    updated_at=datetime.now()
                )
                success = self.global_setting_repository.create(global_setting)

            if success:
                logger.info("Global settings updated successfully")
                # Update the in-memory global settings instance
                self._sync_global_settings_instance(existing_settings)

            return success

        except Exception as e:
            logger.error(f"Error updating global settings: {e}")
            return False

    def reset_global_settings(self, category: str = None) -> bool:
        """
        Reset global settings to defaults.

        Args:
            category: Optional category to reset

        Returns:
            True if successful, False otherwise
        """
        try:
            logger.info("Resetting global settings")

            if category:
                # Reset only the specified category
                default_settings = {category: self.DEFAULT_GLOBAL_SETTINGS.get(category, {})}
                return self.update_global_settings(default_settings, category)
            else:
                # Reset all settings
                return self.update_global_settings(self.DEFAULT_GLOBAL_SETTINGS.copy())

        except Exception as e:
            logger.error(f"Error resetting global settings: {e}")
            return False

    # ===== UTILITY METHODS =====

    def get_setting(self, user_id: int, key_path: str, default: Any = None) -> Any:
        """
        Get a specific setting value using dot notation.

        Args:
            user_id: The user ID (use 0 for global settings)
            key_path: Dot-separated path (e.g., 'notifications.sound_enabled')
            default: Default value if setting not found

        Returns:
            The setting value or default
        """
        try:
            if user_id == 0:
                # Global setting
                settings = self.get_global_settings()
            else:
                # User setting
                settings = self.get_user_settings(user_id)

            # Navigate the path
            value = settings
            for key in key_path.split('.'):
                if isinstance(value, dict) and key in value:
                    value = value[key]
                else:
                    return default

            return value

        except Exception as e:
            logger.error(f"Error getting setting {key_path} for user {user_id}: {e}")
            return default

    def set_setting(self, user_id: int, key_path: str, value: Any) -> bool:
        """
        Set a specific setting value using dot notation.

        Args:
            user_id: The user ID (use 0 for global settings)
            key_path: Dot-separated path (e.g., 'notifications.sound_enabled')
            value: The value to set

        Returns:
            True if successful, False otherwise
        """
        try:
            path_parts = key_path.split('.')
            if len(path_parts) < 2:
                raise ValidationError("Setting key path must have at least 2 parts (category.setting)")

            category = path_parts[0]
            setting_key = '.'.join(path_parts[1:])

            settings_update = {setting_key: value}

            if user_id == 0:
                # Global setting
                return self.update_global_settings(settings_update, category)
            else:
                # User setting
                return self.update_user_settings(user_id, settings_update, category)

        except Exception as e:
            logger.error(f"Error setting {key_path} for user {user_id}: {e}")
            return False

    def get_available_themes(self) -> List[str]:
        """Get list of available themes."""
        return ["light", "dark", "auto"]

    def get_available_languages(self) -> List[str]:
        """Get list of available languages."""
        return ["en", "es", "fr", "de", "zh"]

    def get_available_font_sizes(self) -> List[str]:
        """Get list of available font sizes."""
        return ["small", "medium", "large", "extra_large"]

    def get_available_export_formats(self) -> List[str]:
        """Get list of available export formats."""
        return ["excel", "csv", "pdf", "json"]

    def get_available_reminder_frequencies(self) -> List[str]:
        """Get list of available reminder frequencies."""
        return ["disabled", "daily", "weekly", "monthly"]

    # ===== PRIVATE METHODS =====

    def _merge_with_defaults(self, settings: Dict[str, Any], defaults: Dict[str, Any]) -> Dict[str, Any]:
        """Merge settings with defaults, ensuring all keys exist."""
        merged = defaults.copy()

        def deep_merge(target, source):
            for key, value in source.items():
                if key in target and isinstance(target[key], dict) and isinstance(value, dict):
                    deep_merge(target[key], value)
                else:
                    target[key] = value

        deep_merge(merged, settings)
        return merged

    def _validate_user_settings(self, settings: Dict[str, Any]) -> None:
        """Validate user settings structure."""
        required_categories = ["notifications", "appearance", "behavior", "export", "privacy"]

        for category in required_categories:
            if category not in settings:
                raise ValidationError(f"Missing required settings category: {category}")

            if not isinstance(settings[category], dict):
                raise ValidationError(f"Settings category '{category}' must be a dictionary")

    def _validate_global_settings(self, settings: Dict[str, Any]) -> None:
        """Validate global settings structure."""
        required_categories = ["application", "database", "security", "system", "features"]

        for category in required_categories:
            if category not in settings:
                raise ValidationError(f"Missing required global settings category: {category}")

            if not isinstance(settings[category], dict):
                raise ValidationError(f"Global settings category '{category}' must be a dictionary")

    def _sync_global_settings_instance(self, settings: Dict[str, Any]) -> None:
        """Sync the global settings instance with database values."""
        try:
            # Update the global settings instance with database values
            if "application" in settings:
                app_settings = settings["application"]
                self.global_settings.app_name = app_settings.get("app_name", self.global_settings.app_name)
                self.global_settings.app_version = app_settings.get("app_version", self.global_settings.app_version)
                self.global_settings.debug = app_settings.get("debug_mode", self.global_settings.debug)

            if "system" in settings:
                sys_settings = settings["system"]
                self.global_settings.log_level = sys_settings.get("log_level", self.global_settings.log_level)

            if "appearance" in settings:
                app_settings = settings["appearance"]
                self.global_settings.theme = app_settings.get("theme", self.global_settings.theme)

        except Exception as e:
            logger.error(f"Error syncing global settings instance: {e}")