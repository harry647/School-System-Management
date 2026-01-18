#!/usr/bin/env python3
"""
Migration script to add global settings table and expand user settings.
This migration adds:
- global_settings table for application-wide settings
- Expands user settings table with settings_json column
"""

import sqlite3
from school_system.config.logging import logger
from school_system.config.database import load_db_config


def migrate_global_settings():
    """Add global settings table and expand user settings."""
    logger.info("Starting global settings migration...")

    conn = None
    try:
        config = load_db_config()
        if not config:
            logger.error("Cannot migrate: No valid database configuration")
            return False

        conn = sqlite3.connect(config['database'])
        cursor = conn.cursor()

        # Create global_settings table
        logger.info("Creating global_settings table...")
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS global_settings (
                key TEXT PRIMARY KEY,
                value_json TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        logger.info("Global settings table created successfully")

        # Expand settings table for users
        logger.info("Migrating settings table...")
        cursor.execute("PRAGMA table_info(settings)")
        settings_columns = [column[1] for column in cursor.fetchall()]

        # Add new columns to settings table if they don't exist
        if 'settings_json' not in settings_columns:
            cursor.execute("ALTER TABLE settings ADD COLUMN settings_json TEXT")
            logger.info("Added settings_json column to settings table")
        else:
            logger.info("Settings table already has settings_json column")

        if 'created_at' not in settings_columns:
            cursor.execute("ALTER TABLE settings ADD COLUMN created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP")
            logger.info("Added created_at column to settings table")
        else:
            logger.info("Settings table already has created_at column")

        if 'updated_at' not in settings_columns:
            cursor.execute("ALTER TABLE settings ADD COLUMN updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP")
            logger.info("Added updated_at column to settings table")
        else:
            logger.info("Settings table already has updated_at column")

        # Insert default global settings if table is empty
        cursor.execute("SELECT COUNT(*) FROM global_settings WHERE key = 'global_settings'")
        if cursor.fetchone()[0] == 0:
            default_global_settings = {
                "application": {
                    "app_name": "School System Management",
                    "app_version": "1.0.0",
                    "maintenance_mode": False,
                    "debug_mode": False
                },
                "database": {
                    "backup_enabled": True,
                    "backup_interval_hours": 24,
                    "max_backup_files": 30,
                    "auto_cleanup_backups": True
                },
                "security": {
                    "max_login_attempts": 3,
                    "session_timeout_minutes": 60,
                    "password_min_length": 8,
                    "require_special_chars": True,
                    "password_expiry_days": 90
                },
                "system": {
                    "log_level": "INFO",
                    "max_file_size_mb": 100,
                    "temp_file_cleanup_hours": 24,
                    "system_notifications": True
                },
                "features": {
                    "qr_codes_enabled": True,
                    "bulk_operations_enabled": True,
                    "advanced_reporting": True,
                    "api_access_enabled": False
                }
            }

            import json
            cursor.execute(
                "INSERT INTO global_settings (key, value_json, created_at, updated_at) VALUES (?, ?, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)",
                ("global_settings", json.dumps(default_global_settings))
            )
            logger.info("Inserted default global settings")

        conn.commit()
        logger.info("Global settings migration completed successfully")
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
    success = migrate_global_settings()
    if success:
        print("✓ Global settings migration completed successfully")
    else:
        print("✗ Global settings migration failed")