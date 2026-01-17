#!/usr/bin/env python3
"""
Migration script to add separate class and stream columns to the students table.
This migration adds:
- class TEXT column for student class (Form 3, Form 4, Grade 10, etc.)
- stream TEXT column for student stream within the class (Red, Blue, Orange, etc.)
- Updates existing data by parsing the current stream field
"""

import sqlite3
from school_system.config.logging import logger
from school_system.config.database import load_db_config
from school_system.core.class_parser import ClassParser


def migrate_students_table():
    """Add class and stream columns to the students table and populate them."""
    logger.info("Starting students table migration to add class and stream columns...")

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

        # Add class column if it doesn't exist
        if 'class' not in columns:
            logger.info("Adding 'class' column to students table...")
            cursor.execute("ALTER TABLE students ADD COLUMN class TEXT")
            logger.info("'class' column added successfully")
        else:
            logger.info("'class' column already exists")

        # Add stream column if it doesn't exist (rename existing stream to stream_name or something)
        if 'stream_name' not in columns:
            logger.info("Adding 'stream_name' column to students table...")
            cursor.execute("ALTER TABLE students ADD COLUMN stream_name TEXT")
            logger.info("'stream_name' column added successfully")
        else:
            logger.info("'stream_name' column already exists")

        # Initialize class parser
        parser = ClassParser()

        # Update existing data by parsing the current stream field
        logger.info("Populating class and stream_name columns from existing stream data...")
        cursor.execute("SELECT student_id, stream FROM students WHERE stream IS NOT NULL AND stream != ''")
        students_to_update = cursor.fetchall()

        updated_count = 0
        for student_id, current_stream in students_to_update:
            try:
                # Parse the current stream to get class and stream components
                class_level, stream = parser.parse_class_identifier(current_stream)

                # Convert class level to proper class name
                class_name = get_class_name_from_level(class_level)

                # Update the student record
                cursor.execute("""
                    UPDATE students
                    SET class = ?, stream_name = ?
                    WHERE student_id = ?
                """, (class_name, stream, student_id))

                updated_count += 1
                logger.debug(f"Updated student {student_id}: class='{class_name}', stream='{stream}'")

            except Exception as e:
                logger.warning(f"Failed to parse stream '{current_stream}' for student {student_id}: {e}")
                # For unparseable streams, set defaults
                cursor.execute("""
                    UPDATE students
                    SET class = 'Form 4', stream_name = ?
                    WHERE student_id = ?
                """, (current_stream, student_id))
                updated_count += 1

        logger.info(f"Successfully updated {updated_count} student records")
        conn.commit()
        logger.info("Students table migration completed successfully")
        return True

    except Exception as e:
        logger.error(f"Error during students table migration: {e}")
        if conn:
            conn.rollback()
        return False

    finally:
        if conn:
            conn.close()


def get_class_name_from_level(class_level):
    """Convert numeric class level to proper class name."""
    class_mapping = {
        3: "Form 3",
        4: "Form 4",
        10: "Grade 10",
        11: "Grade 11",
        12: "Grade 12"
    }
    return class_mapping.get(class_level, f"Form {class_level}")


def run_migration():
    """Run the migration."""
    logger.info("Running add_class_stream_to_students migration...")
    success = migrate_students_table()
    if success:
        logger.info("Migration completed successfully")
    else:
        logger.error("Migration failed")
    return success


if __name__ == "__main__":
    run_migration()