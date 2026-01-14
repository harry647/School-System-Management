#!/usr/bin/env python3
"""
Main entry point for the School System Management application.

This module initializes the application and starts the main event loop.
"""

import sys
import os

# Add the project root to Python path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

from PyQt6.QtWidgets import QMessageBox

from school_system.config.logging import logger
from school_system.config.database import load_db_config
from school_system.database import initialize_database, get_db_session
from school_system.src.application import SchoolSystemApplication


def main():
    """Main application entry point."""
    try:
        logger.info("Starting School System Management Application")
        
        # Load configuration
        config = load_db_config()
        if not config:
            logger.error("Failed to load database configuration")
            QMessageBox.critical(None, "Configuration Error", "Failed to load database configuration")
            return 1
        
        # Initialize database if needed
        logger.info("Initializing database")
        try:
            db_connection = initialize_database()
            if not db_connection:
                logger.error("Failed to initialize database")
                return 1
        except Exception as e:
            logger.error(f"Database initialization failed: {e}")
            QMessageBox.critical(None, "Database Error", f"Failed to initialize database: {e}")
            return 1
        
        # Create and run the main application window
        app = SchoolSystemApplication()
        
        logger.info("Application started successfully")
        return app.run()
        
    except Exception as e:
        logger.error(f"Application failed to start: {e}")
        QMessageBox.critical(None, "Application Error", f"Failed to start application: {e}")
        return 1
    
    finally:
        # Clean up database connection
        try:
            db_session = get_db_session()
            if db_session:
                db_session.close()
                logger.info("Database connection closed")
        except Exception as e:
            logger.error(f"Error closing database connection: {e}")


if __name__ == "__main__":
    sys.exit(main())