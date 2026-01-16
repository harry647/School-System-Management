#!/usr/bin/env python3
"""
Migration script to add admission_number column to the students table.
This migration adds an admission_number TEXT column to store the student's admission number.
"""

import sqlite3
from school_system.config.logging import logger
from school_system.config.database import load_db_config


def migrate_students_table():
    """Add admission_number column to the students table."""
    logger.info("Starting students table migration to add admission_number...")

    try:
        config = load_db_config()
        if not config:
            logger.error("Cannot migrate: No valid database configuration")
            return False

        conn = sqlite3.connect(config['database'])
        cursor = conn.cursor()

        # Check if admission_number column already exists
        cursor.execute("PRAGMA table_info(students)")
        columns = [column[1] for column in cursor.fetchall()]

        if 'admission_number' in columns:
            logger.info("Students table already has admission_number column")
            return True

        # Add the admission_number column
        cursor.execute("ALTER TABLE students ADD COLUMN admission_number TEXT")
        logger.info("Added admission_number column to students table")

        conn.commit()
        logger.info("Students table migration completed successfully")
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
    success = migrate_students_table()
    if success:
        print("Students table migration completed successfully")
    else:
        print("Students table migration failed")
