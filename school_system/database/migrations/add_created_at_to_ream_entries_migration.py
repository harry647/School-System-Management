"""
Migration script to add created_at column to the ream_entries table.
This migration adds a created_at TIMESTAMP column with default CURRENT_TIMESTAMP.
"""

from school_system.config.logging import logger
from school_system.database.connection import create_db_connection, close_db_connection


def migrate_ream_entries_table():
    """Add created_at column to the ream_entries table."""
    logger.info("Starting ream_entries table migration...")
    
    db = None
    try:
        db = create_db_connection()
        if not db:
            logger.error("Failed to create database connection for migration")
            return False
        
        cursor = db.cursor()
        
        # Check if created_at column already exists
        cursor.execute("PRAGMA table_info(ream_entries)")
        columns = [column[1] for column in cursor.fetchall()]  # Get column names
        
        if 'created_at' in columns:
            logger.info("Ream entries table already has created_at column")
            return True
        
        # Add the created_at column
        cursor.execute("ALTER TABLE ream_entries ADD COLUMN created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP")
        logger.info("Added created_at column to ream_entries table")
        
        # Update existing records to have a created_at value
        cursor.execute("UPDATE ream_entries SET created_at = date_added WHERE created_at IS NULL")
        updated_count = cursor.rowcount
        logger.info(f"Updated {updated_count} existing ream entries with created_at values")
        
        db.commit()
        logger.info("Ream entries table migration completed successfully")
        return True
        
    except Exception as e:
        logger.error(f"Error during ream_entries migration: {e}")
        if db:
            db.rollback()
        return False
    finally:
        if db:
            close_db_connection(db)


if __name__ == "__main__":
    migrate_ream_entries_table()
