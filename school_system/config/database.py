import os
import sys
import json
import logging
import sqlite3
import tkinter as tk
from tkinter import messagebox, simpledialog
from sqlalchemy import create_engine

from .path_manager import (
    get_path_manager, 
    PathType,
    ExecutionContext,
    PathValidationError,
    PathPermissionError
)

logger = logging.getLogger('DatabaseConfig')
logger.setLevel(logging.INFO)

# DATABASE_CONFIG definition (moved before engine creation)
DATABASE_CONFIG = {
    'engine': 'sqlite',
    'name': 'school_db',
    'backup_interval': 3600,  # 1 hour in seconds
    'connection_pool_size': 10,
    'connection_timeout': 30,
    'max_overflow': 20,
    'pool_recycle': 3600,  # Recycle connections after 1 hour
    'echo': False,  # Set to True for debugging SQL queries
    
    # SQLite specific settings
    'sqlite': {
        'check_same_thread': False,
        'isolation_level': None,
        'timeout': 10.0
    },
    
    # Backup settings
    'backup': {
        'enabled': True,
        'max_backups': 5,
        'backup_on_startup': True
    }
}

# SQLite doesn't use a connection pool, so we'll manage a single DB file
DATABASE_FILE = "school_db"

def resource_path(relative_path: str) -> str:
    """
    Get absolute path to resource, works for dev and PyInstaller.
    
    This function is maintained for backward compatibility.
    New code should use PathManager.resolve_path() instead.
    
    Args:
        relative_path: Path relative to project root.
        
    Returns:
        Absolute path to the resource.
    """
    path_manager = get_path_manager()
    return path_manager.resolve_path(relative_path)


# SQLite doesn't use a connection pool, so we'll manage a single DB file
DATABASE_FILE = "school_db"


def load_db_config(config_file: str = 'config.json') -> dict:
    """
    Loads database config from file or uses defaults if not available.
    
    Uses PathManager to determine the correct config location based on
    execution context (development vs packaged).
    
    Args:
        config_file: Name of the config file.
        
    Returns:
        Database configuration dictionary.
    """
    path_manager = get_path_manager()
    
    # Use the config path from path manager
    config_dir = path_manager.get_config_path()
    config_path = os.path.join(config_dir, config_file)
    
    # If not in config dir, try project root for backward compatibility
    if not os.path.exists(config_path):
        config_path = os.path.join(path_manager.get_executable_directory(), config_file)
    
    logger.info(f"Attempting to load config from: {config_path}")
    
    # Default configuration for SQLite (only needs database file path)
    # Use the database path from path manager
    db_dir = path_manager.get_database_path()
    default_db_name = "school_db"
    default_config = {
        "database": os.path.join(db_dir, default_db_name)
    }
    
    try:
        if os.path.exists(config_path):
            with open(config_path, 'r') as f:
                config_data = json.load(f)
                db_config = config_data.get('database_config', {})
                if not db_config or 'database' not in db_config:
                    logger.warning("Invalid or missing 'database_config' section, using defaults")
                    return default_config
                logger.debug("Database config loaded successfully")
                return db_config
        else:
            logger.info(f"Config file not found at {config_path}, using defaults and creating config")
            # Ensure config directory exists
            os.makedirs(config_dir, exist_ok=True)
            with open(config_path, 'w') as f:
                json.dump({"database_config": default_config}, f, indent=4)
            return default_config
    except Exception as e:
        logger.error(f"Failed to load or create config: {e}, falling back to defaults")
        return default_config


def prompt_for_db_config(config_file):
    """Prompts for database config (SQLite file path)."""
    root = tk.Tk()
    root.withdraw()
    messagebox.showinfo("Setup", "Please specify the SQLite database file location.")
    database = simpledialog.askstring("Database File", "Enter SQLite database file path (e.g., library_db.sqlite):", initialvalue="library_db.sqlite")
    root.destroy()
    
    if not database:
        messagebox.showerror("Error", "Database file path is required.")
        return None
    
    db_config = {"database": database}
    try:
        # Test if the file can be created/opened
        conn = sqlite3.connect(database)
        conn.close()
        with open(config_file, 'w') as f:
            json.dump({"database_config": db_config}, f, indent=4)
        logger.info(f"Config saved to {config_file}")
        return db_config
    except sqlite3.Error as e:
        messagebox.showerror("Connection Error", f"Invalid SQLite file path: {e}")
        return None

# Now that load_db_config is defined, we can call it
db_config = load_db_config()
engine = create_engine(f"sqlite:///{db_config['database']}")
