#!/usr/bin/env python3
"""
Migration script to add return tracking columns to borrowed_books_student and borrowed_books_teacher tables.
This migration adds: returned_on, return_condition, fine_amount, and returned_by columns.
"""

import sqlite3
from school_system.config.logging import logger
from school_system.config.database import load_db_config


def migrate_borrowed_books_tables():
    """Add return tracking columns to borrowed books tables."""
    logger.info("Starting borrowed books tables migration...")
    
    try:
        config = load_db_config()
        if not config:
            logger.error("Cannot migrate: No valid database configuration")
            return False
        
        conn = sqlite3.connect(config['database'])
        cursor = conn.cursor()
        
        # Migrate borrowed_books_student table
        logger.info("Migrating borrowed_books_student table...")
        cursor.execute("PRAGMA table_info(borrowed_books_student)")
        student_columns = [column[1] for column in cursor.fetchall()]
        
        # Columns to add for student table
        student_new_columns = [
            ('returned_on', 'DATE DEFAULT NULL'),
            ('return_condition', 'TEXT DEFAULT NULL'),
            ('fine_amount', 'REAL DEFAULT 0'),
            ('returned_by', 'TEXT DEFAULT NULL')
        ]
        
        for column_name, column_def in student_new_columns:
            if column_name not in student_columns:
                cursor.execute(f"ALTER TABLE borrowed_books_student ADD COLUMN {column_name} {column_def}")
                logger.info(f"Added {column_name} column to borrowed_books_student table")
            else:
                logger.info(f"Column {column_name} already exists in borrowed_books_student table")
        
        # Migrate borrowed_books_teacher table
        logger.info("Migrating borrowed_books_teacher table...")
        cursor.execute("PRAGMA table_info(borrowed_books_teacher)")
        teacher_columns = [column[1] for column in cursor.fetchall()]
        
        # Columns to add for teacher table (only returned_on for now)
        teacher_new_columns = [
            ('returned_on', 'DATE DEFAULT NULL')
        ]
        
        for column_name, column_def in teacher_new_columns:
            if column_name not in teacher_columns:
                cursor.execute(f"ALTER TABLE borrowed_books_teacher ADD COLUMN {column_name} {column_def}")
                logger.info(f"Added {column_name} column to borrowed_books_teacher table")
            else:
                logger.info(f"Column {column_name} already exists in borrowed_books_teacher table")
        
        conn.commit()
        logger.info("Borrowed books tables migration completed successfully")
        return True
        
    except sqlite3.Error as e:
        logger.error(f"Migration failed: {e}")
        if 'conn' in locals() and conn:
            conn.rollback()
        return False
    finally:
        if 'conn' in locals() and conn:
            conn.close()


if __name__ == "__main__":
    success = migrate_borrowed_books_tables()
    if success:
        print("Borrowed books tables migration completed successfully")
    else:
        print("Borrowed books tables migration failed")