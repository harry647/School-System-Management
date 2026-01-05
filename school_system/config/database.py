import os
import sys
import json
import logging
import sqlite3
import tkinter as tk
from tkinter import messagebox, simpledialog
from sqlalchemy import create_engine

logger = logging.getLogger('DatabaseConfig')
logger.setLevel(logging.INFO)

# DATABASE_CONFIG definition (moved before engine creation)
DATABASE_CONFIG = {
    'engine': 'sqlite',
    'name': 'school.db',
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
DATABASE_FILE = "school.db"

def resource_path(relative_path):
    """Get absolute path to resource, works for dev and PyInstaller."""
    if hasattr(sys, '_MEIPASS'):
        return os.path.join(sys._MEIPASS, relative_path)
    return os.path.join(os.path.abspath("."), relative_path)


# SQLite doesn't use a connection pool, so we'll manage a single DB file
DATABASE_FILE = "school.db"


def load_db_config(config_file='config.json'):
    """Loads database config from file or uses defaults if not available."""
    config_path = resource_path(config_file)
    logger.info(f"Attempting to load config from: {config_path}")
    
    # Default configuration for SQLite (only needs database file path)
    default_config = {
        "database": DATABASE_FILE
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