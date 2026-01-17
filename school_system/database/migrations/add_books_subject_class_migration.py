#!/usr/bin/env python3
"""
Migration script to add subject and class columns to the books table.
This migration adds:
- subject TEXT column for book subject categorization
- class TEXT column for book class association (as class_name in model)
"""

import sqlite3
from school_system.config.logging import logger
from school_system.config.database import load_db_config


def migrate_books_table():
    """Add subject and class columns to the books table."""
    logger.info("Starting books table migration to add subject and class columns...")

    conn = None
    try:
        config = load_db_config()
        if not config:
            logger.error("Cannot migrate: No valid database configuration")
            return False

        conn = sqlite3.connect(config['database'])
        cursor = conn.cursor()

        # Check existing columns
        cursor.execute("PRAGMA table_info(books)")
        columns = [column[1] for column in cursor.fetchall()]

        # Add subject column if it doesn't exist
        if 'subject' not in columns:
            cursor.execute("ALTER TABLE books ADD COLUMN subject TEXT")
            logger.info("Added subject column to books table")
        else:
            logger.info("Books table already has subject column")

        # Add class column if it doesn't exist (model uses class_name but DB uses 'class')
        if 'class' not in columns:
            cursor.execute("ALTER TABLE books ADD COLUMN class TEXT")
            logger.info("Added class column to books table")
        else:
            logger.info("Books table already has class column")

        # Add QR code columns for books
        if 'qr_code' not in columns:
            cursor.execute("ALTER TABLE books ADD COLUMN qr_code TEXT")
            logger.info("Added qr_code column to books table")
        else:
            logger.info("Books table already has qr_code column")

        if 'qr_generated_at' not in columns:
            cursor.execute("ALTER TABLE books ADD COLUMN qr_generated_at TIMESTAMP")
            logger.info("Added qr_generated_at column to books table")
        else:
            logger.info("Books table already has qr_generated_at column")

        conn.commit()
        logger.info("Books table migration completed successfully")
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
    success = migrate_books_table()
    if success:
        print("Books table migration completed successfully")
    else:
        print("Books table migration failed")
