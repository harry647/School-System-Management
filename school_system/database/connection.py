import sqlite3
from sqlite3 import Error as SQLiteError
from typing import Optional
from ..config.database import DATABASE_CONFIG, load_db_config, resource_path, prompt_for_db_config
from ..config.logging import logger
from ..core.exceptions import DatabaseException, ConfigurationError
from ..core.utils import HashUtils
from ..core.validators import UserValidator
import os
import sys
import json
from datetime import datetime, date
import tkinter as tk
from tkinter import messagebox, simpledialog


class DatabaseConnection:
    """Database connection manager using SQLite."""
    
    def __init__(self):
        self._connection = None
        self._config = DATABASE_CONFIG
          
    def get_connection(self) -> Optional[sqlite3.Connection]:
        """Get a database connection, creating one if necessary."""
        if self._connection is None:
            self._connection = self._create_connection()
        return self._connection
      
    def _create_connection(self) -> Optional[sqlite3.Connection]:
        """Create a new database connection."""
        try:
            conn = sqlite3.connect(
                self._config['name'],
                check_same_thread=self._config['sqlite']['check_same_thread'],
                isolation_level=self._config['sqlite']['isolation_level'],
                timeout=self._config['sqlite']['timeout']
            )
            
            # Enable foreign key support
            conn.execute("PRAGMA foreign_keys = ON")
            
            logger.info(f"Database connection established to {self._config['name']}")
            return conn
            
        except SQLiteError as e:
            logger.error(f"Failed to create database connection: {e}")
            raise DatabaseException(f"Failed to create database connection: {e}")
      
    def close_connection(self):
        """Close the database connection."""
        if self._connection is not None:
            try:
                self._connection.close()
                logger.info("Database connection closed")
            except SQLiteError as e:
                logger.error(f"Error closing database connection: {e}")
                raise DatabaseException(f"Error closing database connection: {e}")
            finally:
                self._connection = None
    
    def __enter__(self):
        """Context manager entry."""
        return self.get_connection()
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.close_connection()


def create_db_connection():
    """Creates a direct SQLite connection."""
    logger.debug("Requesting SQLite database connection")
    config = load_db_config()
    if not config:
        logger.warning("No valid config to create connection")
        raise ConfigurationError("No valid configuration found")
    
    try:
        conn = sqlite3.connect(config['database'])
        logger.debug("SQLite connection created")
        return conn
    except SQLiteError as e:
        logger.error(f"Failed to create SQLite connection: {e}")
        messagebox.showerror("Database Error", f"Failed to connect to SQLite: {e}")
        raise DatabaseException(f"Failed to create SQLite connection: {e}")


def close_db_connection(conn):
    """Closes the SQLite connection."""
    if conn:
        try:
            conn.close()
            logger.debug("SQLite connection closed")
        except SQLiteError as e:
            logger.error(f"Failed to close SQLite connection: {e}")
            raise DatabaseException(f"Failed to close SQLite connection: {e}")


def initialize_database():
    """Initializes the SQLite database by creating necessary tables with all updates included."""
    logger.info("Initializing database tables")
    config = load_db_config()
    if not config:
        logger.error("Cannot initialize database: No valid configuration")
        raise ConfigurationError("Cannot initialize database: No valid configuration")
    
    mydb = create_db_connection()
    if not mydb:
        logger.warning("No database connection for initialization")
        config = prompt_for_db_config('config.json')
        if not config:
            return False
        mydb = create_db_connection()
        if not mydb:
            messagebox.showerror("Connection Error", "Failed to connect to SQLite database.")
            return False
    
    cursor = None
    try:
        cursor = mydb.cursor()
        
        # Create all tables with updated schema from the start
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                username TEXT PRIMARY KEY,
                password TEXT NOT NULL,
                role TEXT DEFAULT 'student' CHECK (role IN ('admin', 'librarian', 'student')),
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS students (
                student_id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                stream TEXT NOT NULL
            )
        """)
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS books (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                book_number TEXT NOT NULL UNIQUE,
                title TEXT NOT NULL,
                author TEXT NOT NULL,
                category TEXT,
                isbn TEXT,
                publication_date TEXT,
                available INTEGER DEFAULT 1,
                revision INTEGER DEFAULT 0,
                book_condition TEXT DEFAULT 'New'
            )
        """)
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS short_form_mappings (
                short_form TEXT PRIMARY KEY,
                full_name TEXT NOT NULL,
                type TEXT NOT NULL CHECK (type IN ('class', 'subject'))
            )
        """)
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS book_tags (  -- Added from update schema
                book_id INTEGER,
                tag TEXT,
                PRIMARY KEY (book_id, tag),
                FOREIGN KEY (book_id) REFERENCES books(id) ON DELETE CASCADE
            )
        """)
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS borrowed_books_student (
                student_id TEXT,
                book_id INTEGER,
                borrowed_on DATE,
                reminder_days INTEGER DEFAULT NULL,
                PRIMARY KEY (student_id, book_id, borrowed_on),
                FOREIGN KEY (student_id) REFERENCES students(student_id) ON DELETE CASCADE,
                FOREIGN KEY (book_id) REFERENCES books(id) ON DELETE CASCADE
            )
        """)
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS teachers (
                teacher_id TEXT PRIMARY KEY,
                teacher_name TEXT
            )
        """)
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS settings (
                user_id TEXT PRIMARY KEY,
                reminder_frequency TEXT DEFAULT 'daily' CHECK (reminder_frequency IN ('daily', 'weekly', 'disabled')),
                sound_enabled INTEGER DEFAULT 1,
                FOREIGN KEY (user_id) REFERENCES users(username) ON DELETE CASCADE
            )
        """)
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS borrowed_books_teacher (
                teacher_id TEXT,
                book_id INTEGER,
                borrowed_on DATE,
                PRIMARY KEY (teacher_id, book_id, borrowed_on),
                FOREIGN KEY (teacher_id) REFERENCES teachers(teacher_id) ON DELETE CASCADE,
                FOREIGN KEY (book_id) REFERENCES books(id) ON DELETE CASCADE
            )
        """)
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS chairs (
                chair_id TEXT PRIMARY KEY,
                location TEXT NULL,
                form TEXT NULL,
                color TEXT NOT NULL,
                cond TEXT DEFAULT 'Good',
                assigned INTEGER DEFAULT 0
            )
        """)
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS lockers (
                locker_id TEXT NOT NULL PRIMARY KEY,
                location TEXT NULL,
                form TEXT NULL,
                color TEXT NOT NULL,
                cond TEXT DEFAULT 'Good',
                assigned INTEGER DEFAULT 0
            )
        """)
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS locker_assignments (
                student_id TEXT,
                locker_id TEXT,
                assigned_date DATE DEFAULT (DATE('now')),
                PRIMARY KEY (student_id, locker_id),
                FOREIGN KEY (student_id) REFERENCES students(student_id) ON DELETE CASCADE,
                FOREIGN KEY (locker_id) REFERENCES lockers(locker_id) ON DELETE CASCADE
            )
        """)
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS chair_assignments (
                student_id TEXT,
                chair_id TEXT,
                assigned_date DATE DEFAULT (DATE('now')),
                PRIMARY KEY (student_id, chair_id),
                FOREIGN KEY (student_id) REFERENCES students(student_id) ON DELETE CASCADE,
                FOREIGN KEY (chair_id) REFERENCES chairs(chair_id) ON DELETE CASCADE
            )
        """)
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS furniture_categories (
                category_id INTEGER PRIMARY KEY AUTOINCREMENT,
                category_name TEXT NOT NULL UNIQUE,
                total_count INTEGER NOT NULL DEFAULT 0,
                needs_repair INTEGER NOT NULL DEFAULT 0,
                CHECK (total_count >= needs_repair)
            )
        """)
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS ream_entries (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                student_id TEXT,
                reams_count INTEGER NOT NULL,
                date_added DATE DEFAULT (DATE('now')),
                FOREIGN KEY (student_id) REFERENCES students(student_id) ON DELETE CASCADE
            )
        """)
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS total_reams (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                total_available INTEGER NOT NULL DEFAULT 0
            )
        """)

        cursor.execute("""
                CREATE TABLE IF NOT EXISTS qr_books (
                    book_number TEXT PRIMARY KEY,
                    details TEXT,
                    added_date TEXT
                )
            """)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS qr_borrow_log (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                book_number TEXT,
                student_id TEXT,
                borrow_date TEXT,
                return_date TEXT,
                FOREIGN KEY (book_number) REFERENCES qr_books(book_number) ON DELETE CASCADE,
                FOREIGN KEY (student_id) REFERENCES students(student_id) ON DELETE SET NULL
            )
        """)

        # Distribution tables
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS distribution_sessions (
                session_id INTEGER PRIMARY KEY AUTOINCREMENT,
                class TEXT NOT NULL,
                stream TEXT NOT NULL,
                subject TEXT NOT NULL,
                term TEXT NOT NULL,
                created_by TEXT NOT NULL,
                distributed_by TEXT,
                status TEXT DEFAULT 'DRAFT'
                    CHECK (status IN ('DRAFT', 'IN_PROGRESS', 'FINALIZED')),
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                finalized_at TIMESTAMP
            )
        """)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS distribution_students (
                session_id INTEGER,
                student_id TEXT,
                book_id INTEGER DEFAULT NULL,
                book_number TEXT DEFAULT NULL,
                notes TEXT,
                PRIMARY KEY (session_id, student_id),
                FOREIGN KEY (session_id)
                    REFERENCES distribution_sessions(session_id)
                    ON DELETE CASCADE,
                FOREIGN KEY (student_id)
                    REFERENCES students(student_id)
                    ON DELETE CASCADE,
                FOREIGN KEY (book_id)
                    REFERENCES books(id)
                    ON DELETE SET NULL
            )
        """)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS distribution_import_logs (
                log_id INTEGER PRIMARY KEY AUTOINCREMENT,
                session_id INTEGER,
                file_name TEXT,
                imported_by TEXT,
                imported_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                status TEXT,
                message TEXT,
                FOREIGN KEY (session_id)
                    REFERENCES distribution_sessions(session_id)
                    ON DELETE CASCADE
            )
        """)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS user_sessions (
                session_id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT NOT NULL,
                ip_address TEXT NOT NULL,
                is_active INTEGER DEFAULT 1,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (username) REFERENCES users(username) ON DELETE CASCADE
            )
        """)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS audit_logs (
                log_id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id TEXT NOT NULL,
                action TEXT NOT NULL,
                details TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(username) ON DELETE CASCADE
            )
        """)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS user_activities (
                activity_id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT NOT NULL,
                activity_type TEXT NOT NULL,
                details TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (username) REFERENCES users(username) ON DELETE CASCADE
            )
        """)
        
        # Insert initial total_reams value
        cursor.execute("SELECT SUM(reams_count) FROM ream_entries")
        initial_total = cursor.fetchone()[0] or 0
        cursor.execute("INSERT OR IGNORE INTO total_reams (id, total_available) VALUES (1, ?)", (initial_total,))
        
        # Set reminder_days to 7 for revision books during initialization
        cursor.execute("""
            UPDATE borrowed_books_student
            SET reminder_days =7
            WHERE reminder_days IS NULL AND book_id IN (SELECT book_id FROM books WHERE revision = 1)
        """)
        affected_rows = cursor.rowcount
        if affected_rows > 0:
            logger.info(f"Initialized {affected_rows} reminder_days to 7 for revision books")
        
        # Insert default admin user with password
        default_username = "admin"
        default_password = HashUtils.hash_password("harry123")
        cursor.execute("""
            INSERT OR IGNORE INTO users (username, password, role)
            VALUES (?, ?, 'admin')
        """, (default_username, default_password))
        if cursor.rowcount > 0:
            logger.info("Default admin user created with password")
        
        mydb.commit()
        logger.info("Database initialized successfully with all updates")
        return mydb
    except SQLiteError as e:
        logger.error(f"SQLite error during initialization: {e}")
        messagebox.showerror("Database Error", f"SQLite error during initialization: {e}")
        raise DatabaseException(f"SQLite error during initialization: {e}")
    except Exception as e:
        logger.error(f"Unexpected error during initialization: {e}")
        messagebox.showerror("Error", f"Unexpected error: {e}")
        raise DatabaseException(f"Unexpected error during initialization: {e}")
    finally:
        if cursor:
            cursor.close()


# Global database connection instance
db_connection = DatabaseConnection()


def get_db_session():
    """Get a database session (connection)."""
    return db_connection.get_connection()