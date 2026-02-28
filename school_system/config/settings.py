import os
import logging
from typing import Optional

from .path_manager import (
    PathManager, 
    PathType, 
    get_path_manager,
    initialize_path_manager,
    ExecutionContext,
    PathValidationError,
    PathPermissionError,
    NetworkPathUnavailableError
)

logger = logging.getLogger(__name__)


class Settings:
    """
    Application-wide settings and configuration.
    
    All paths are now managed through the PathManager to ensure:
    - Centralized path configuration
    - Cross-platform compatibility
    - Proper handling of development vs packaged executable contexts
    - Permission validation and fallback strategies
    """
    
    # Application metadata (class-level defaults)
    APP_NAME = "School System Management"
    APP_VERSION = "1.0.0"
    
    def __init__(self, app_name: Optional[str] = None):
        """
        Initialize settings with path management.
        
        Args:
            app_name: Optional application name. Defaults to class APP_NAME.
        """
        # Initialize path manager
        if app_name:
            self.APP_NAME = app_name
            self.path_manager = initialize_path_manager(app_name)
        else:
            self.path_manager = get_path_manager()
        
        # Database configuration
        self.database_url = "sqlite:///school_db"
        self.debug = False
        self.log_level = "INFO"
        
        # QR Code settings
        self.qr_code_size = (200, 200)
        self.qr_code_version = 1
        self.qr_code_error_correction = 1
        
        # Security settings
        self.max_login_attempts = 3
        self.session_timeout = 3600  # 1 hour in seconds
        self.password_min_length = 8
        
        # Application settings
        self.app_name = self.APP_NAME
        self.app_version = self.APP_VERSION
        self.default_language = "en"
        
        # GUI settings
        self.default_window_size = (1024, 768)
        self.default_font = ("Arial", 10)
        self.theme = "light"  # 'light' or 'dark'
        
        # Initialize paths from PathManager (these are now dynamic)
        self._initialize_paths()
    
    def _initialize_paths(self) -> None:
        """
        Initialize all path settings from the PathManager.
        
        This ensures all paths are validated and appropriate for the
        current execution context (development or packaged).
        """
        try:
            # Get validated paths from PathManager
            # These paths handle fallback strategies automatically
            self.data_path = self.path_manager.get_data_path()
            self.data_backup_path = self.path_manager.get_backup_path()
            self.data_export_path = self.path_manager.get_export_path()
            self.log_path = self.path_manager.get_log_path()
            self.log_file_path = os.path.join(self.log_path, "app.log")
            self.config_path = self.path_manager.get_config_path()
            self.cache_path = self.path_manager.get_cache_path()
            self.temp_path = self.path_manager.get_temp_path()
            
            # Database path - try executable dir first, then fallback
            self.database_path = self.path_manager.get_database_path()
            self.database_file = os.path.join(self.database_path, "school_db")
            
            # Resource paths - resolve relative to executable
            self.logo_path = self.path_manager.resolve_path(
                "school_system/gui/resources/icons/logo.png"
            )
            
            # Execution context info
            self.execution_context = self.path_manager.execution_context
            self.is_frozen = self.path_manager.is_frozen
            self.is_windows = self.path_manager.is_windows
            
            logger.info(f"Paths initialized for {self.execution_context.value} context")
            logger.info(f"Database path: {self.database_file}")
            logger.info(f"Log path: {self.log_path}")
            
        except PathValidationError as e:
            logger.error(f"Path validation error: {e}")
            raise
        except Exception as e:
            logger.error(f"Error initializing paths: {e}")
            raise
    
    def get_path(self, path_type: PathType) -> str:
        """
        Get a path for a specific type using the PathManager.
        
        Args:
            path_type: The type of path to retrieve.
            
        Returns:
            The validated path.
        """
        return self.path_manager.get_path_for_type(path_type)
    
    def validate_path(self, path: str, operation: str = "write") -> tuple:
        """
        Validate a path for a specific operation.
        
        Args:
            path: The path to validate.
            operation: The operation to validate for ("read", "write").
            
        Returns:
            Tuple of (is_valid, error_message).
        """
        return self.path_manager.validate_path_for_operation(path, operation)
    
    def get_safe_write_path(
        self, 
        preferred_path: str, 
        fallback_type: Optional[PathType] = None
    ) -> str:
        """
        Get a safe path for writing with automatic fallback.
        
        Args:
            preferred_path: The preferred path.
            fallback_type: PathType to use for fallback if preferred fails.
            
        Returns:
            A validated, writable path.
        """
        return self.path_manager.get_safe_write_path(preferred_path, fallback_type)
    
    def resolve_path(self, relative_path: str) -> str:
        """
        Resolve a relative path to absolute based on execution context.
        
        Args:
            relative_path: The relative path to resolve.
            
        Returns:
            Absolute path.
        """
        return self.path_manager.resolve_path(relative_path)
    
    def is_path_restricted(self, path: str) -> tuple:
        """
        Check if a path is in a restricted directory.
        
        Args:
            path: The path to check.
            
        Returns:
            Tuple of (is_restricted, reason).
        """
        return self.path_manager.is_path_restricted(path)
    
    def check_write_permission(self, path: str) -> bool:
        """
        Check if we have write permission for a path.
        
        Args:
            path: The path to check.
            
        Returns:
            True if we have write permission.
        """
        return self.path_manager.check_write_permission(path)


# Global settings instance - initialize with application name
def _get_settings():
    """
    Get or create the global settings instance.
    
    This function ensures settings is properly initialized with
    the correct application name.
    """
    global _settings
    if _settings is None:
        # Try to get app name from version module if available
        app_name = "School System Management"
        try:
            from ..version import APP_NAME
            app_name = APP_NAME
        except ImportError:
            pass
        
        _settings = Settings(app_name)
    return _settings


_settings: Optional[Settings] = None


def get_settings() -> Settings:
    """Get the global settings instance."""
    return _get_settings()


# For backward compatibility, also expose as 'settings'
settings = get_settings()
