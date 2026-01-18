#!/usr/bin/env python3
"""
Master migration script to run all pending migrations.
This ensures the database schema is up-to-date with all model requirements.
"""

import sys
from school_system.config.logging import logger

def run_all_migrations():
    """Run all database migrations to ensure schema is current."""
    logger.info("Starting comprehensive database migration...")
    
    migrations = [
        ('add_books_subject_class_migration', 'migrate_books_table'),
        ('ensure_all_student_columns_migration', 'migrate_students_table'),
        ('add_qr_codes_migration', 'migrate_qr_codes'),
        ('add_class_stream_to_students_migration', 'migrate_students_table'),
        ('add_global_settings_migration', 'migrate_global_settings'),
    ]
    
    results = []
    
    for module_name, function_name in migrations:
        try:
            module = __import__(f'school_system.database.migrations.{module_name}', 
                              fromlist=[function_name])
            migrate_func = getattr(module, function_name)
            result = migrate_func()
            results.append((module_name, result))
            if result:
                logger.info(f"✓ {module_name} completed successfully")
            else:
                logger.warning(f"✗ {module_name} completed with warnings")
        except Exception as e:
            logger.error(f"✗ {module_name} failed: {e}")
            results.append((module_name, False))
    
    # Summary
    successful = sum(1 for _, result in results if result)
    total = len(results)
    
    logger.info(f"Migration summary: {successful}/{total} migrations completed successfully")
    
    if successful == total:
        logger.info("All migrations completed successfully!")
        return True
    else:
        logger.warning("Some migrations had issues. Check logs for details.")
        return False


if __name__ == "__main__":
    success = run_all_migrations()
    sys.exit(0 if success else 1)
