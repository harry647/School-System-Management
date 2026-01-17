#!/usr/bin/env python3
"""
Migration script to add QR code columns to books and students tables.
This migration adds:
- qr_code TEXT UNIQUE column to both tables
- qr_generated_at TIMESTAMP column to both tables
"""

import sqlite3
from school_system.config.logging import logger
from school_system.config.database import load_db_config


def migrate_qr_codes():
    """Add QR code columns to books and students tables."""
    logger.info("Starting QR code columns migration...")

    conn = None
    try:
        config = load_db_config()
        if not config:
            logger.error("Cannot migrate: No valid database configuration")
            return False

        conn = sqlite3.connect(config['database'])
        cursor = conn.cursor()

        # Migrate books table
        logger.info("Migrating books table...")
        cursor.execute("PRAGMA table_info(books)")
        books_columns = [column[1] for column in cursor.fetchall()]

        # Add QR code columns to books if they don't exist
        if 'qr_code' not in books_columns:
            cursor.execute("ALTER TABLE books ADD COLUMN qr_code TEXT UNIQUE")
            logger.info("Added qr_code column to books table")
        else:
            logger.info("Books table already has qr_code column")

        if 'qr_generated_at' not in books_columns:
            cursor.execute("ALTER TABLE books ADD COLUMN qr_generated_at TIMESTAMP")
            logger.info("Added qr_generated_at column to books table")
        else:
            logger.info("Books table already has qr_generated_at column")

        # Migrate students table
        logger.info("Migrating students table...")
        cursor.execute("PRAGMA table_info(students)")
        students_columns = [column[1] for column in cursor.fetchall()]

        # Add QR code columns to students if they don't exist
        if 'qr_code' not in students_columns:
            cursor.execute("ALTER TABLE students ADD COLUMN qr_code TEXT UNIQUE")
            logger.info("Added qr_code column to students table")
        else:
            logger.info("Students table already has qr_code column")

        if 'qr_generated_at' not in students_columns:
            cursor.execute("ALTER TABLE students ADD COLUMN qr_generated_at TIMESTAMP")
            logger.info("Added qr_generated_at column to students table")
        else:
            logger.info("Students table already has qr_generated_at column")

        conn.commit()
        logger.info("QR code migration completed successfully")
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
    success = migrate_qr_codes()
    if success:
        print("✓ QR code migration completed successfully")
    else:
        print("✗ QR code migration failed")