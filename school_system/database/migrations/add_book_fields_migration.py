#!/usr/bin/env python3
"""
Migration script to add new fields to the books table.
This migration adds: title, author, category, isbn, and publication_date fields.
"""

import sqlite3
from school_system.config.logging import logger
from school_system.config.database import load_db_config


def migrate_books_table():
    """Add new fields to the books table."""
    logger.info("Starting books table migration...")
    
    try:
        config = load_db_config()
        if not config:
            logger.error("Cannot migrate: No valid database configuration")
            return False

        conn = sqlite3.connect(config['database'])
        cursor = conn.cursor()

        # Check if columns already exist
        cursor.execute("PRAGMA table_info(books)")
        columns = [column[1] for column in cursor.fetchall()]
        
        new_columns = ['title', 'author', 'category', 'isbn', 'publication_date']
        columns_to_add = [col for col in new_columns if col not in columns]
        
        if not columns_to_add:
            logger.info("Books table already has all required columns")
            return True

        # Add each missing column
        for column in columns_to_add:
            if column in ['title', 'author']:
                # Required fields - add with default values, then update existing records
                cursor.execute(f"ALTER TABLE books ADD COLUMN {column} TEXT")
                
                # Set default values for existing records
                default_value = "Unknown" if column == "title" else "Anonymous"
                cursor.execute(f"UPDATE books SET {column} = ? WHERE {column} IS NULL", (default_value,))
                
                # Now make the column NOT NULL
                logger.info(f"Added {column} column with default values for existing records")
            else:
                # Optional fields
                cursor.execute(f"ALTER TABLE books ADD COLUMN {column} TEXT")
                logger.info(f"Added {column} column")

        # Update the table to make title and author NOT NULL for new records
        # This is handled by the CREATE TABLE statement in connection.py
        
        conn.commit()
        logger.info("Books table migration completed successfully")
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
    success = migrate_books_table()
    if success:
        print("✓ Books table migration completed successfully")
    else:
        print("✗ Books table migration failed")
