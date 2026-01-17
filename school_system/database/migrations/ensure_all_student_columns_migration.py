#!/usr/bin/env python3
"""
Migration script to ensure students table has all required columns.
This migration ensures:
- admission_number TEXT column exists
- created_at TIMESTAMP column exists
This is a combined migration that checks and adds both if missing.
"""

import sqlite3
from school_system.config.logging import logger
from school_system.config.database import load_db_config


def migrate_students_table():
    """Ensure students table has admission_number and created_at columns."""
    logger.info("Starting students table migration to ensure all required columns...")

    conn = None
    try:
        config = load_db_config()
        if not config:
            logger.error("Cannot migrate: No valid database configuration")
            return False

        conn = sqlite3.connect(config['database'])
        cursor = conn.cursor()

        # Check existing columns
        cursor.execute("PRAGMA table_info(students)")
        columns = [column[1] for column in cursor.fetchall()]

        # Add admission_number column if it doesn't exist
        if 'admission_number' not in columns:
            cursor.execute("ALTER TABLE students ADD COLUMN admission_number TEXT")
            logger.info("Added admission_number column to students table")
            
            # Backfill: Set admission_number = student_id for existing records
            cursor.execute("UPDATE students SET admission_number = student_id WHERE admission_number IS NULL")
            logger.info("Backfilled admission_number with student_id values")
        else:
            logger.info("Students table already has admission_number column")

        # Add created_at column if it doesn't exist
        if 'created_at' not in columns:
            cursor.execute("ALTER TABLE students ADD COLUMN created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP")
            logger.info("Added created_at column to students table")
        else:
            logger.info("Students table already has created_at column")

        # Add QR code columns for students
        if 'qr_code' not in columns:
            cursor.execute("ALTER TABLE students ADD COLUMN qr_code TEXT UNIQUE")
            logger.info("Added qr_code column to students table")
        else:
            logger.info("Students table already has qr_code column")

        if 'qr_generated_at' not in columns:
            cursor.execute("ALTER TABLE students ADD COLUMN qr_generated_at TIMESTAMP")
            logger.info("Added qr_generated_at column to students table")
        else:
            logger.info("Students table already has qr_generated_at column")

        conn.commit()
        logger.info("Students table migration completed successfully")
        return True

    except sqlite3.Error as e:
        logger.error(f"Migration failed: {e}")
        if conn:
            conn.rollback()
        return False
    except Exception as e:
        logger.error(f"Unexpected error during migration: {e}")
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
