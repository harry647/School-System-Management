"""
Cross-platform path management system for the School System Management application.

This module provides robust path handling with:
- Execution context detection (development vs packaged executable)
- Permission validation with Windows-specific handling
- Automatic fallback strategies for various scenarios
- Centralized path configuration
"""

import os
import sys
import stat
import errno
import platform
import logging
import tempfile
from pathlib import Path
from typing import Optional, Union, Tuple
from enum import Enum

logger = logging.getLogger(__name__)


class ExecutionContext(Enum):
    """Enumeration of possible execution contexts."""
    DEVELOPMENT = "development"
    PYINSTALLER_FROZEN = "pyinstaller_frozen"
    CX_FREEZE_FROZEN = "cx_freeze_frozen"
    PY2EXE_FROZEN = "py2exe_frozen"
    UNKNOWN = "unknown"


class PathType(Enum):
    """Types of paths used by the application."""
    DATA = "data"
    BACKUP = "backup"
    EXPORT = "export"
    LOG = "log"
    CONFIG = "config"
    CACHE = "cache"
    TEMP = "temp"
    DATABASE = "database"


class PathValidationError(Exception):
    """Exception raised when path validation fails."""
    def __init__(self, path: str, reason: str, suggestion: Optional[str] = None):
        self.path = path
        self.reason = reason
        self.suggestion = suggestion
        message = f"Path validation failed for '{path}': {reason}"
        if suggestion:
            message += f". Suggestion: {suggestion}"
        super().__init__(message)


class PathPermissionError(Exception):
    """Exception raised when path permission check fails."""
    def __init__(self, path: str, operation: str, reason: str):
        self.path = path
        self.operation = operation
        self.reason = reason
        super().__init__(f"Permission denied: Cannot {operation} at '{path}': {reason}")


class PathNotFoundError(Exception):
    """Exception raised when path does not exist and cannot be created."""
    def __init__(self, path: str, reason: str = "Path does not exist"):
        self.path = path
        self.reason = reason
        super().__init__(f"Path not found: '{path}': {reason}")


class NetworkPathUnavailableError(Exception):
    """Exception raised when network path is unavailable."""
    def __init__(self, path: str, reason: str = "Network path is not accessible"):
        self.path = path
        self.reason = reason
        super().__init__(f"Network path unavailable: '{path}': {reason}")


class PathManager:
    """
    Centralized path management system for cross-platform file operations.
    
    This class handles:
    - Execution context detection
    - Permission validation
    - Fallback strategies for various scenarios
    - Windows-specific path handling
    """
    
    # Application name (can be overridden)
    APP_NAME = "SchoolSystemManagement"
    
    # Known restricted Windows directories
    WINDOWS_RESTRICTED_DIRS = [
        os.path.join(os.environ.get('ProgramFiles', 'C:/Program Files'), ''),
        os.path.join(os.environ.get('ProgramFiles(x86)', 'C:/Program Files (x86)'), ''),
        os.path.join(os.environ.get('CommonProgramFiles', 'C:/Program Files/Common Files'), ''),
        os.path.join(os.environ.get('CommonProgramFiles(x86)', 'C:/Program Files (x86)/Common Files'), ''),
        'C:/Windows/',
        'C:/ProgramData/',
    ]
    
    def __init__(self, app_name: Optional[str] = None):
        """
        Initialize the PathManager.
        
        Args:
            app_name: Optional application name override. Defaults to class APP_NAME.
        """
        if app_name:
            self.APP_NAME = app_name
            
        self._context = None
        self._executable_dir = None
        self._user_data_dir = None
        self._temp_dir = None
        self._validated_paths = {}
        
        # Detect execution context on initialization
        self._detect_execution_context()
        
        logger.info(f"PathManager initialized in {self._context.value} context")
    
    @property
    def execution_context(self) -> ExecutionContext:
        """Get the current execution context."""
        return self._context
    
    @property
    def is_frozen(self) -> bool:
        """Check if running as a packaged executable."""
        return self._context != ExecutionContext.DEVELOPMENT
    
    @property
    def is_windows(self) -> bool:
        """Check if running on Windows."""
        return platform.system() == "Windows"
    
    def _detect_execution_context(self) -> None:
        """Detect the current execution context."""
        # Check for various frozen executable indicators
        if getattr(sys, 'frozen', False):
            # PyInstaller
            if hasattr(sys, '_MEIPASS'):
                self._context = ExecutionContext.PYINSTALLER_FROZEN
                self._executable_dir = os.path.dirname(sys.executable)
                logger.info("Detected PyInstaller frozen executable")
                return
            
            # cx_Freeze
            if hasattr(sys, 'cx_Freeze'):
                self._context = ExecutionContext.CX_FREEZE_FROZEN
                self._executable_dir = os.path.dirname(sys.executable)
                logger.info("Detected cx_Freeze frozen executable")
                return
            
            # py2exe
            if hasattr(sys, 'console'):
                self._context = ExecutionContext.PY2EXE_FROZEN
                self._executable_dir = os.path.dirname(sys.executable)
                logger.info("Detected py2exe frozen executable")
                return
            
            # Generic frozen (unknown type)
            self._context = ExecutionContext.UNKNOWN
            self._executable_dir = os.path.dirname(sys.executable)
            logger.info("Detected unknown frozen executable type")
            return
        
        # Development context
        self._context = ExecutionContext.DEVELOPMENT
        # Get the project root (parent of school_system directory)
        self._executable_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        logger.info("Detected development context")
    
    def get_executable_directory(self) -> str:
        """
        Get the directory where the executable (or main script) is located.
        
        Returns:
            Absolute path to the executable directory.
        """
        return self._executable_dir
    
    def _get_user_data_directory(self) -> str:
        """
        Get the user data directory appropriate for the platform.
        
        Returns:
            Absolute path to the user data directory.
        """
        if self.is_windows:
            base = os.environ.get('LOCALAPPDATA', os.path.expanduser('~/AppData/Local'))
        elif platform.system() == 'Darwin':  # macOS
            base = os.path.join(os.path.expanduser('~/Library/Application Support'))
        else:  # Linux and others
            base = os.environ.get('XDG_DATA_HOME', os.path.expanduser('~/.local/share'))
        
        return os.path.join(base, self.APP_NAME)
    
    def _get_temp_directory(self) -> str:
        """
        Get the temporary directory for the application.
        
        Returns:
            Absolute path to the temp directory.
        """
        if self.is_windows:
            base = tempfile.gettempdir()
        else:
            base = tempfile.gettempdir()
        
        return os.path.join(base, self.APP_NAME)
    
    def is_path_restricted(self, path: str) -> Tuple[bool, Optional[str]]:
        """
        Check if a path is in a restricted Windows directory.
        
        Args:
            path: The path to check.
            
        Returns:
            Tuple of (is_restricted, reason)
        """
        if not self.is_windows:
            return False, None
        
        path = os.path.abspath(path)
        
        # Check against known restricted directories
        for restricted in self.WINDOWS_RESTRICTED_DIRS:
            if path.startswith(restricted):
                return True, f"Path is within restricted Windows directory: {restricted}"
        
        # Check for desktop path
        desktop = os.path.expanduser('~/Desktop')
        if path.startswith(desktop):
            return True, "Desktop locations may have limited permissions on Windows"
        
        return False, None
    
    def is_network_path(self, path: str) -> bool:
        """
        Check if a path is a network path.
        
        Args:
            path: The path to check.
            
        Returns:
            True if the path is a network path.
        """
        # UNC path
        if path.startswith('\\\\'):
            return True
        
        # Windows network drive letter
        if self.is_windows and len(path) >= 2 and path[0].isalpha() and path[1] == ':':
            # Check if it's a mapped network drive
            import win32api  # May not be available, handle gracefully
            try:
                import subprocess
                result = subprocess.run(
                    ['net', 'use'],
                    capture_output=True,
                    text=True,
                    timeout=5
                )
                drive_letter = path[0].upper()
                if drive_letter + ':' in result.stdout:
                    return True
            except Exception:
                pass
        
        return False
    
    def check_write_permission(self, path: str, create_if_missing: bool = True) -> bool:
        """
        Check if we have write permission to a path.
        
        Args:
            path: The path to check.
            create_if_missing: Whether to create the directory if it doesn't exist.
            
        Returns:
            True if we have write permission.
        """
        path = os.path.abspath(path)
        
        # Check if path exists
        if not os.path.exists(path):
            if create_if_missing:
                try:
                    os.makedirs(path, exist_ok=True)
                except OSError as e:
                    logger.warning(f"Cannot create directory {path}: {e}")
                    return False
            else:
                # Check parent directory permissions
                parent = os.path.dirname(path)
                if not os.path.exists(parent):
                    return False
                path = parent
        
        # Check if it's a file or directory
        if os.path.isfile(path):
            # Check file write permission
            return os.access(path, os.W_OK)
        
        # Check directory write permission
        if not os.access(path, os.W_OK):
            return False
        
        # Try to create a test file
        test_file = os.path.join(path, '.write_test_temp')
        try:
            with open(test_file, 'w') as f:
                f.write('test')
            os.remove(test_file)
            return True
        except (OSError, PermissionError) as e:
            logger.warning(f"Write test failed for {path}: {e}")
            return False
    
    def validate_path_for_operation(
        self, 
        path: str, 
        operation: str = "write",
        create_if_missing: bool = True
    ) -> Tuple[bool, Optional[str]]:
        """
        Validate a path for a specific operation.
        
        Args:
            path: The path to validate.
            operation: The intended operation ("read", "write", "execute").
            create_if_missing: Whether to create the directory if missing.
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        path = os.path.abspath(path)
        
        # Check for restricted Windows directories
        is_restricted, restriction_reason = self.is_path_restricted(path)
        if is_restricted:
            return False, f"Path is in restricted directory: {restriction_reason}"
        
        # Check for network path availability
        if self.is_network_path(path):
            if not self._check_network_path_accessible(path):
                return False, "Network path is not accessible"
        
        # Check path exists or can be created
        if not os.path.exists(path):
            if create_if_missing:
                try:
                    os.makedirs(path, exist_ok=True)
                except OSError as e:
                    return False, f"Cannot create path: {e}"
            else:
                return False, "Path does not exist"
        
        # Check permissions based on operation
        if operation == "write":
            if not self.check_write_permission(path, create_if_missing=False):
                return False, "No write permission for this path"
        elif operation == "read":
            if not os.access(path, os.R_OK):
                return False, "No read permission for this path"
        
        return True, None
    
    def _check_network_path_accessible(self, path: str) -> bool:
        """
        Check if a network path is accessible.
        
        Args:
            path: The network path to check.
            
        Returns:
            True if accessible.
        """
        try:
            # Try to list the parent directory
            parent = os.path.dirname(path)
            if os.path.exists(parent):
                return True
            
            # Try to access the path directly
            if os.path.exists(path):
                return True
            
            # Try a simple operation
            test_file = os.path.join(path, '.network_test')
            with open(test_file, 'w') as f:
                f.write('test')
            os.remove(test_file)
            return True
        except (OSError, IOError, PermissionError) as e:
            logger.warning(f"Network path {path} not accessible: {e}")
            return False
    
    def get_path_for_type(
        self, 
        path_type: PathType, 
        create: bool = True,
        use_executable_dir: Optional[bool] = None
    ) -> str:
        """
        Get the appropriate path for a specific type of data.
        
        This method implements the fallback strategy:
        1. For packaged apps: Try executable directory first, then AppData/Local
        2. For development: Use relative paths from project root
        
        Args:
            path_type: The type of path needed.
            create: Whether to create the directory if it doesn't exist.
            use_executable_dir: Override the default behavior for packaged apps.
            
        Returns:
            Validated path string.
            
        Raises:
            PathValidationError: If no valid path could be found.
        """
        # Check cache first
        cache_key = f"{path_type.value}_{create}_{use_executable_dir}"
        if cache_key in self._validated_paths:
            return self._validated_paths[cache_key]
        
        # Determine the base directory
        if use_executable_dir is None:
            use_executable_dir = self.is_frozen
        
        if use_executable_dir and self.is_frozen:
            # Try executable directory first for packaged apps
            base_dir = self.get_executable_directory()
        else:
            # For development, use project root
            base_dir = self.get_executable_directory()
        
        # Build the path based on type
        subdirs = {
            PathType.DATA: "data",
            PathType.BACKUP: "data/backup",
            PathType.EXPORT: "data/exports",
            PathType.LOG: "logs",
            PathType.CONFIG: "config",
            PathType.CACHE: "cache",
            PathType.TEMP: "temp",
            PathType.DATABASE: "",  # Database goes in base directory
        }
        
        subdir = subdirs.get(path_type, "")
        if subdir:
            path = os.path.join(base_dir, subdir)
        else:
            path = base_dir
        
        # For packaged apps, try executable dir first, then fallback
        if self.is_frozen and use_executable_dir:
            # First attempt: executable directory
            if self._can_use_path(path):
                if create:
                    self._ensure_path_exists(path)
                self._validated_paths[cache_key] = path
                logger.info(f"Using executable directory for {path_type.value}: {path}")
                return path
            
            # Fallback: AppData/Local
            fallback_path = os.path.join(self._get_user_data_directory(), subdir)
            if self._can_use_path(fallback_path):
                if create:
                    self._ensure_path_exists(fallback_path)
                self._validated_paths[cache_key] = fallback_path
                logger.info(f"Falling back to user data directory for {path_type.value}: {fallback_path}")
                return fallback_path
            
            # Last resort: temp directory
            temp_path = os.path.join(self._get_temp_directory(), subdir)
            if self._can_use_path(temp_path):
                if create:
                    self._ensure_path_exists(temp_path)
                self._validated_paths[cache_key] = temp_path
                logger.warning(f"Using temp directory as last resort for {path_type.value}: {temp_path}")
                return temp_path
            
            raise PathValidationError(
                path, 
                "No writable location found",
                "Check application permissions and disk space"
            )
        
        # Development mode: just ensure it exists
        if create:
            self._ensure_path_exists(path)
        
        self._validated_paths[cache_key] = path
        return path
    
    def _can_use_path(self, path: str) -> bool:
        """
        Check if a path can be used (exists and writable, or can be created).
        
        Args:
            path: The path to check.
            
        Returns:
            True if the path can be used.
        """
        # Check if path is restricted
        is_restricted, _ = self.is_path_restricted(path)
        if is_restricted:
            return False
        
        # Check if it's a network path that's not accessible
        if self.is_network_path(path):
            if not self._check_network_path_accessible(path):
                return False
        
        # Try to check write permission
        return self.check_write_permission(path, create_if_missing=True)
    
    def _ensure_path_exists(self, path: str) -> None:
        """
        Ensure a path exists, creating it if necessary.
        
        Args:
            path: The path to ensure exists.
            
        Raises:
            PathValidationError: If the path cannot be created.
        """
        try:
            os.makedirs(path, exist_ok=True)
        except OSError as e:
            if e.errno == errno.EACCES:
                raise PathPermissionError(path, "create directory", str(e))
            elif e.errno == errno.ENOENT:
                raise PathNotFoundError(path, "Parent directory does not exist")
            else:
                raise PathValidationError(path, str(e))
    
    def get_database_path(self) -> str:
        """
        Get the path for the database file.
        
        Returns:
            Path to the database.
        """
        return self.get_path_for_type(PathType.DATABASE, create=True)
    
    def get_backup_path(self) -> str:
        """
        Get the path for backup files.
        
        Returns:
            Path to the backup directory.
        """
        return self.get_path_for_type(PathType.BACKUP, create=True)
    
    def get_export_path(self) -> str:
        """
        Get the path for export files.
        
        Returns:
            Path to the export directory.
        """
        return self.get_path_for_type(PathType.EXPORT, create=True)
    
    def get_log_path(self) -> str:
        """
        Get the path for log files.
        
        Returns:
            Path to the log directory.
        """
        return self.get_path_for_type(PathType.LOG, create=True)
    
    def get_config_path(self) -> str:
        """
        Get the path for configuration files.
        
        Returns:
            Path to the config directory.
        """
        return self.get_path_for_type(PathType.CONFIG, create=True)
    
    def get_cache_path(self) -> str:
        """
        Get the path for cache files.
        
        Returns:
            Path to the cache directory.
        """
        return self.get_path_for_type(PathType.CACHE, create=True)
    
    def get_temp_path(self) -> str:
        """
        Get the path for temporary files.
        
        Returns:
            Path to the temp directory.
        """
        return self.get_path_for_type(PathType.TEMP, create=True)
    
    def get_data_path(self) -> str:
        """
        Get the path for general data files.
        
        Returns:
            Path to the data directory.
        """
        return self.get_path_for_type(PathType.DATA, create=True)
    
    def resolve_path(self, relative_path: str) -> str:
        """
        Resolve a relative path to an absolute path based on the current context.
        
        Args:
            relative_path: The relative path to resolve.
            
        Returns:
            Absolute path.
        """
        if os.path.isabs(relative_path):
            return relative_path
        
        # If in development, resolve from project root
        if not self.is_frozen:
            return os.path.join(self.get_executable_directory(), relative_path)
        
        # For frozen apps, try executable dir first
        exec_path = os.path.join(self.get_executable_directory(), relative_path)
        if os.path.exists(exec_path):
            return exec_path
        
        # Try user data directory
        user_path = os.path.join(self._get_user_data_directory(), relative_path)
        if os.path.exists(user_path):
            return user_path
        
        # Return executable path as default
        return exec_path
    
    def safe_file_operation(
        self,
        file_path: str,
        operation: str,
        *args,
        **kwargs
    ):
        """
        Perform a file operation with comprehensive error handling.
        
        Args:
            file_path: Path to the file.
            operation: The operation to perform ('read', 'write', 'append').
            *args, **kwargs: Arguments to pass to the file operation.
            
        Returns:
            Result of the file operation.
            
        Raises:
            PathPermissionError: If permission is denied.
            PathNotFoundError: If path doesn't exist.
            NetworkPathUnavailableError: If network path is unavailable.
            PathValidationError: For other path-related errors.
        """
        file_path = os.path.abspath(file_path)
        
        # Validate directory permissions
        dir_path = os.path.dirname(file_path)
        is_valid, error_msg = self.validate_path_for_operation(dir_path, "write")
        if not is_valid:
            if "restricted" in error_msg.lower() or "permission" in error_msg.lower():
                raise PathPermissionError(file_path, operation, error_msg)
            elif "network" in error_msg.lower():
                raise NetworkPathUnavailableError(file_path, error_msg)
            else:
                raise PathValidationError(file_path, error_msg)
        
        try:
            if operation == 'read':
                with open(file_path, 'r', *args, **kwargs) as f:
                    return f.read()
            elif operation == 'write':
                with open(file_path, 'w', *args, **kwargs) as f:
                    return f.write(*args, **kwargs)
            elif operation == 'append':
                with open(file_path, 'a', *args, **kwargs) as f:
                    return f.write(*args, **kwargs)
            else:
                raise ValueError(f"Unknown operation: {operation}")
        except PermissionError as e:
            raise PathPermissionError(file_path, operation, str(e))
        except FileNotFoundError as e:
            raise PathNotFoundError(file_path, str(e))
        except OSError as e:
            if e.errno == errno.EACCES:
                raise PathPermissionError(file_path, operation, str(e))
            elif e.errno == errno.ENOENT:
                raise PathNotFoundError(file_path, str(e))
            elif e.errno == errno.EHOSTUNREACH or e.errno == errno.ETIMEDOUT:
                raise NetworkPathUnavailableError(file_path, str(e))
            else:
                raise PathValidationError(file_path, str(e))
    
    def get_safe_write_path(
        self,
        preferred_path: str,
        fallback_type: Optional[PathType] = None
    ) -> str:
        """
        Get a safe path for writing, with automatic fallback.
        
        Args:
            preferred_path: The preferred path.
            fallback_type: Type to use for fallback if preferred fails.
            
        Returns:
            A validated, writable path.
        """
        # Try the preferred path first
        is_valid, error_msg = self.validate_path_for_operation(preferred_path, "write")
        if is_valid:
            return preferred_path
        
        logger.warning(f"Preferred path {preferred_path} not usable: {error_msg}")
        
        # Try fallback type
        if fallback_type:
            fallback_path = self.get_path_for_type(fallback_type, create=True)
            is_valid, error_msg = self.validate_path_for_operation(fallback_path, "write")
            if is_valid:
                logger.info(f"Using fallback path: {fallback_path}")
                return fallback_path
        
        # Last resort: temp directory
        temp_path = self.get_temp_path()
        logger.warning(f"Using temp directory as last resort: {temp_path}")
        return temp_path


# Global path manager instance
_path_manager: Optional[PathManager] = None


def get_path_manager(app_name: Optional[str] = None) -> PathManager:
    """
    Get the global PathManager instance (singleton).
    
    Args:
        app_name: Optional app name to initialize with.
        
    Returns:
        The global PathManager instance.
    """
    global _path_manager
    if _path_manager is None:
        _path_manager = PathManager(app_name)
    return _path_manager


def initialize_path_manager(app_name: str) -> PathManager:
    """
    Initialize the global PathManager with a specific app name.
    
    Args:
        app_name: Name of the application.
        
    Returns:
        The initialized PathManager instance.
    """
    global _path_manager
    _path_manager = PathManager(app_name)
    return _path_manager
