#!/usr/bin/env python3
"""
Migration script to add the department column to the teachers table.
This migration adds the department field to the teachers table.
"""

import sqlite3
from school_system.config.logging import logger
from school_system.config.database import load_db_config


def migrate_teachers_table():
    """Add the department column to the teachers table."""
    logger.info("Starting teachers table migration...")
    
    try:
        config = load_db_config()
        if not config:
            logger.error("Cannot migrate: No valid database configuration")
            return False
        
        conn = sqlite3.connect(config['database'])
        cursor = conn.cursor()
        
        # Check if the department column already exists
        cursor.execute("PRAGMA table_info(teachers)")
        columns = [column[1] for column in cursor.fetchall()]
        
        if 'department' in columns:
            logger.info("Teachers table already has the department column")
            return True
        
        # Add the department column
        cursor.execute("ALTER TABLE teachers ADD COLUMN department TEXT")
        logger.info("Added department column to teachers table")
        
        conn.commit()
        logger.info("Teachers table migration completed successfully")
        return True
        
    except sqlite3.Error as e:
        logger.error(f"Migration failed: {e}")
        if conn:
            conn.rollback()
        return False
    finally:
        if conn:
            conn.close()


if __name__ == "__main__":
    success = migrate_teachers_table()
    if success:
        print("✓ Teachers table migration completed successfully")
    else:
        print("✗ Teachers table migration failed")