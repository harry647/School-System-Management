#!/usr/bin/env python3
"""
Migration to add missing columns to settings table for complex settings support.
"""

import sys
from pathlib import Path

# Add the project root to the Python path
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

from school_system.database.connection import get_db_session
from school_system.config.logging import logger


def migrate_settings_table():
    """
    Add missing columns to settings table to support complex JSON-based settings.
    """
    logger.info("Starting settings table migration for complex settings support")

    try:
        db = get_db_session()
        cursor = db.cursor()

        # Check current table structure
        cursor.execute("PRAGMA table_info(settings)")
        columns = cursor.fetchall()
        column_names = [col[1] for col in columns]

        logger.info(f"Current settings table columns: {column_names}")

        # Add settings_json column if it doesn't exist
        if 'settings_json' not in column_names:
            logger.info("Adding settings_json column to settings table")
            cursor.execute("ALTER TABLE settings ADD COLUMN settings_json TEXT")
        else:
            logger.info("settings_json column already exists")

        # Add created_at column if it doesn't exist
        if 'created_at' not in column_names:
            logger.info("Adding created_at column to settings table")
            cursor.execute("ALTER TABLE settings ADD COLUMN created_at TIMESTAMP")
        else:
            logger.info("created_at column already exists")

        # Add updated_at column if it doesn't exist
        if 'updated_at' not in column_names:
            logger.info("Adding updated_at column to settings table")
            cursor.execute("ALTER TABLE settings ADD COLUMN updated_at TIMESTAMP")
        else:
            logger.info("updated_at column already exists")

        # Set default values for existing rows
        logger.info("Setting default values for existing rows")
        cursor.execute("""
            UPDATE settings
            SET settings_json = '{}',
                created_at = CURRENT_TIMESTAMP,
                updated_at = CURRENT_TIMESTAMP
            WHERE settings_json IS NULL
        """)

        db.commit()
        logger.info("Settings table migration completed successfully")

        # Verify the migration
        cursor.execute("PRAGMA table_info(settings)")
        updated_columns = cursor.fetchall()
        updated_column_names = [col[1] for col in updated_columns]
        logger.info(f"Updated settings table columns: {updated_column_names}")

        return True

    except Exception as e:
        logger.error(f"Error during settings table migration: {e}")
        db.rollback()
        return False


if __name__ == "__main__":
    success = migrate_settings_table()
    sys.exit(0 if success else 1)