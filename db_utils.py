# db_utils.py

import sqlite3 as sqlite
import json
from tkinter import messagebox, simpledialog
import logging
import subprocess
import os
from datetime import datetime, date 
import tkinter as tk
from sqlite3 import Error as SQLiteError
import sys
import hashlib

logger = logging.getLogger('DBUtils')
logger.setLevel(logging.INFO)

def resource_path(relative_path):
    if hasattr(sys, '_MEIPASS'):
        return os.path.join(sys._MEIPASS, relative_path)
    return os.path.join(os.path.abspath("."), relative_path)

# SQLite doesn't use a connection pool, so we'll manage a single DB file
DATABASE_FILE = "School_Management_db"  

def load_db_config(config_file='config.json'):
    """Loads database config from file or uses defaults if not available."""
    config_path = resource_path(config_file)
    logger.info(f"Attempting to load config from: {config_path}")
    
    # Default configuration for SQLite (only needs database file path)
    default_config = {
        "database": DATABASE_FILE
    }

    try:
        if os.path.exists(config_path):
            with open(config_path, 'r') as f:
                config_data = json.load(f)
                db_config = config_data.get('database_config', {})
                if not db_config or 'database' not in db_config:
                    logger.warning("Invalid or missing 'database_config' section, using defaults")
                    return default_config
                logger.debug("Database config loaded successfully")
                return db_config
        else:
            logger.info(f"Config file not found at {config_path}, using defaults and creating config")
            with open(config_path, 'w') as f:
                json.dump({"database_config": default_config}, f, indent=4)
            return default_config
    except Exception as e:
        logger.error(f"Failed to load or create config: {e}, falling back to defaults")
        return default_config

def prompt_for_db_config(config_file):
    """Prompts for database config (SQLite file path)."""
    root = tk.Tk()
    root.withdraw()
    messagebox.showinfo("Setup", "Please specify the SQLite database file location.")
    database = simpledialog.askstring("Database File", "Enter SQLite database file path (e.g., library_db.sqlite):", initialvalue="library_db.sqlite")
    root.destroy()

    if not database:
        messagebox.showerror("Error", "Database file path is required.")
        return None

    db_config = {"database": database}
    try:
        # Test if the file can be created/opened
        conn = sqlite3.connect(database)
        conn.close()
        with open(config_file, 'w') as f:
            json.dump({"database_config": db_config}, f, indent=4)
        logger.info(f"Config saved to {config_file}")
        return db_config
    except sqlite3.Error as e:
        messagebox.showerror("Connection Error", f"Invalid SQLite file path: {e}")
        return None

def initialize_database():
    """Initializes the SQLite database by creating necessary tables with all updates included."""
    logger.info("Initializing database tables")
    config = load_db_config()
    if not config:
        logger.error("Cannot initialize database: No valid configuration")
        return False

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
                id INTEGER PRIMARY KEY AUTOINCREMENT,   -- SYSTEM ID
                book_number TEXT NOT NULL UNIQUE,        -- HUMAN book number (accession)
                available INTEGER DEFAULT 1,
                revision INTEGER DEFAULT 0,  -- Added from update schema
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
        default_password = hashlib.sha256("harry123".encode()).hexdigest()
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
        return False
    except Exception as e:
        logger.error(f"Unexpected error during initialization: {e}")
        messagebox.showerror("Error", f"Unexpected error: {e}")
        return False
    finally:
        if cursor:
            cursor.close()
        

def create_db_connection():
    """Creates a direct SQLite connection."""
    logger.debug("Requesting SQLite database connection")
    config = load_db_config()
    if not config:
        logger.warning("No valid config to create connection")
        return None

    try:
        conn = sqlite.connect(config['database'])
        logger.debug("SQLite connection created")
        return conn
    except SQLiteError as e:
        logger.error(f"Failed to create SQLite connection: {e}")
        messagebox.showerror("Database Error", f"Failed to connect to SQLite: {e}")
        return None

def close_db_connection(conn):
    """Closes the SQLite connection."""
    if conn:
        try:
            conn.close()
            logger.debug("SQLite connection closed")
        except SQLiteError as e:
            logger.error(f"Failed to close SQLite connection: {e}")

def backup_database(backup_file=None, encrypt=True):
    """Exports only the data from the SQLite database to a SQL file, optionally encrypted."""
    logger.info("Starting SQLite data-only backup")

    config = load_db_config()  
    if not config:
        logger.error("Cannot perform backup: No valid database configuration")
        messagebox.showerror("Backup Error", "No valid database configuration found.")
        return False

    if not backup_file:
        try:
            backup_file = f"library_data_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.sql"
            logger.debug(f"Generated backup file name: {backup_file}")
        except AttributeError as e:
            logger.error(f"Error generating backup filename: {e}")
            messagebox.showerror("Backup Error", f"datetime.now() failed: {e}")
            return False

    conn = create_db_connection()  
    if not conn:
        logger.error("No database connection for backup")
        messagebox.showerror("Backup Error", "No database connection available.")
        return False

    cursor = conn.cursor()
    try:
        # Get list of tables
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = [row[0] for row in cursor.fetchall() if row[0] != 'sqlite_sequence']
        if not tables:
            logger.warning("No tables found in database")
            messagebox.showinfo("Backup Info", "No tables found to backup.")
            return False

        with open(backup_file, 'w') as f:
            f.write("PRAGMA foreign_keys=OFF;\n")
            for table in tables:
                logger.debug(f"Backing up data from table: {table}")
                cursor.execute(f"SELECT * FROM {table}")
                rows = cursor.fetchall()
                if rows:
                    cursor.execute(f"PRAGMA table_info({table})")
                    columns = [col[1] for col in cursor.fetchall()]
                    for row in rows:
                        values = ','.join([escape_sql_value(v) for v in row])
                        f.write(f"INSERT OR IGNORE INTO {table} ({','.join(columns)}) VALUES ({values});\n")
                    f.write("\n")
            f.write("PRAGMA foreign_keys=ON;\n")

        if encrypt:
            root = tk.Tk()
            root.withdraw()  # Fixed typo
            password = simpledialog.askstring("Backup Encryption", "Enter password for encryption:", show="*")
            root.destroy()
            if not password:
                logger.warning("No password provided, skipping encryption")
                messagebox.showinfo("Backup Success", f"Database data backed up without encryption to '{backup_file}'")
                return True
            from cryptography.fernet import Fernet
            from cryptography.hazmat.primitives import hashes
            from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
            import base64
            fernet = generate_encryption_key(password)  
            encrypted_file = encrypt_file(backup_file, fernet)  
            messagebox.showinfo("Backup Success", f"Database data backed up and encrypted to '{encrypted_file}'")
            return True
        else:
            messagebox.showinfo("Backup Success", f"Database data backed up to '{backup_file}'")
            return True
    except sqlite.SQLiteError as e:  
        logger.error(f"SQLite error during backup: {e}")
        messagebox.showerror("Backup Error", f"SQLite error during backup: {e}")
        return False
    except Exception as e:
        logger.error(f"Unexpected error during backup: {e}")
        messagebox.showerror("Backup Error", f"Unexpected error during backup: {e}")
        return False
    finally:
        cursor.close()
        close_db_connection(conn) 

def restore_database(backup_file=None, password=None):
    """Restore data from an encrypted backup file, preserving existing data."""
    logger.info("Starting SQLite data restore")
    config = load_db_config()
    if not config:
        logger.error("Cannot restore: No valid database configuration")
        return False

    if not backup_file or not password:
        logger.error("Backup file or password missing")
        return False

    try:
        from cryptography.fernet import Fernet, InvalidToken
        from cryptography.hazmat.primitives import hashes
        from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
        import base64
        fernet = generate_encryption_key(password)
        decrypted_file = decrypt_file(backup_file, fernet)

        conn = create_db_connection()
        if not conn:
            logger.error("No database connection for restore")
            os.remove(decrypted_file)
            return False

        cursor = conn.cursor()
        try:
            with open(decrypted_file, 'r') as f:
                sql_content = f.read()

            statements = sql_content.split(';\n')
            for statement in statements:
                statement = statement.strip()
                if not statement or "PRAGMA foreign_keys" in statement:
                    if statement:
                        cursor.execute(statement)
                    continue

                try:
                    cursor.execute(statement)
                except sqlite3.IntegrityError:
                    logger.warning(f"Skipping duplicate entry in statement: {statement[:50]}...")
                    continue
                except sqlite3.OperationalError as e:
                    logger.error(f"Invalid SQL statement: {e} - {statement}")
                    conn.rollback()
                    return False

            conn.commit()
            logger.info(f"Database data restored successfully from {backup_file}")
            return True

        except Exception as e:
            logger.error(f"Error during SQL execution: {e}")
            conn.rollback()
            return False
        finally:
            cursor.close()
            close_db_connection(conn)

        os.remove(decrypted_file)
        logger.info(f"Cleaned up decrypted file: {decrypted_file}")

    except ValueError as ve:
        logger.error(f"Restore failed: {ve}")
        return False
    except Exception as e:
        logger.error(f"Unexpected error during restore: {e}")
        return False

def generate_encryption_key(password):
    """Generate a Fernet key from a user-provided password."""
    from cryptography.hazmat.primitives import hashes
    from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
    import base64
    salt = b'salt_library_backup'  # Unique salt; store securely in production
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=salt,
        iterations=100000,
    )
    key = base64.urlsafe_b64encode(kdf.derive(password.encode()))
    from cryptography.fernet import Fernet
    return Fernet(key)

def encrypt_file(file_path, fernet):
    """Encrypt a file using Fernet."""
    with open(file_path, 'rb') as f:
        data = f.read()
    encrypted_data = fernet.encrypt(data)
    encrypted_file_path = file_path + '.enc'
    with open(encrypted_file_path, 'wb') as f:
        f.write(encrypted_data)
    os.remove(file_path)
    logger.info(f"Encrypted backup saved as {encrypted_file_path}")
    return encrypted_file_path

def decrypt_file(encrypted_file_path, fernet):
    """Decrypt a file using Fernet."""
    from cryptography.fernet import InvalidToken
    try:
        with open(encrypted_file_path, 'rb') as f:
            encrypted_data = f.read()
        decrypted_data = fernet.decrypt(encrypted_data)
        decrypted_file_path = encrypted_file_path.replace('.enc', '')
        with open(decrypted_file_path, 'wb') as f:
            f.write(decrypted_data)
        logger.info(f"Decrypted backup to {decrypted_file_path}")
        return decrypted_file_path
    except InvalidToken:
        logger.error("Invalid decryption password")
        raise ValueError("Incorrect password provided for decryption")
    except Exception as e:
        logger.error(f"Failed to decrypt file: {e}")
        raise

def escape_sql_value(value):
    """Escape SQL values for safe insertion."""
    if value is None:
        return "NULL"
    elif isinstance(value, (int, float)):
        return str(value)
    elif isinstance(value, bool):
        return "1" if value else "0"
    elif isinstance(value, (date, datetime)):
        return f"'{value.strftime('%Y-%m-%d')}'" if isinstance(value, datetime) else f"'{value.strftime('%Y-%m-%d %H:%M:%S')}'"
    else:
        escaped_value = str(value).replace("'", "''")  
        return f"'{escaped_value}'"



