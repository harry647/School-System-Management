import sqlite3
from sqlite3 import Error as SQLiteError
import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext, simpledialog, filedialog
import threading
import datetime
import json
import os
import logging
import time
import serial
import queue
import schedule  
import serial.tools.list_ports
import csv
import pandas as pd
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, LongTable
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import inch
import speech_recognition as sr  
try:
    import qrcode
except ImportError:
    qrcode = None

# Constants
MAX_book_number_LENGTH = 50
MIN_book_number_LENGTH = 3
VALID_FORM_RANGE = (1, 12)
MAX_STUDENT_ID_LENGTH = 20
MIN_STUDENT_ID_LENGTH = 3
MAX_BORROW_LIMIT = 15
MAX_RETRIES = 3
SCAN_COOLDOWN = 5
SCANNER_TIMEOUT = 5
OVERDUE_DAYS = 14
PAGE_SIZE = 20

class QRCodeBookManager:
    def __init__(self, db_manager, root=None):
        self.root = root
        self.db_manager = db_manager
        self.logger = logging.getLogger('QRCodeBookManager')
        self.last_scan_time = 0
        self.last_scan_data = None
        self.last_operation_result = None
        try:
            self.logger.info("Initializing QRCodeBookManager")
            self._create_database_tables()
            self.logger.info("QRCodeBookManager initialized successfully")
        except SQLiteError as db_err:
            self.logger.error(f"Failed to initialize QR tables: {db_err}")
            messagebox.showerror("Database Error", "Failed to initialize QR tables.")
            raise

    def _create_database_tables(self):
        """Create QR-specific tables in SQLite database."""
        conn = self.db_manager._create_connection()
        if not conn:
            raise SQLiteError("No database connection available.")
        try:
            cursor = conn.cursor()
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
            conn.commit()
        except SQLiteError as db_err:
            self.logger.error(f"Failed to create QR tables: {db_err}")
            raise
        finally:
            self.db_manager._close_connection(conn)

    def _validate_qr_format(self, scanned_data):
        """Validate QR code format."""
        if not scanned_data:
            raise ValueError("No data provided in QR code.")
        if scanned_data.startswith("BOOK-ID:"):
            book_number = scanned_data[len("BOOK-ID:"):].strip()
            if not (MIN_book_number_LENGTH <= len(book_number) <= MAX_book_number_LENGTH and book_number.replace('-', '').isalnum()):
                raise ValueError(f"Simple format ID must be {MIN_book_number_LENGTH}-{MAX_book_number_LENGTH} alphanumeric characters (hyphens allowed)")
            book_info = {"Format": "Simple", "ID": book_number}
            return book_number, book_info
        data_parts = scanned_data.split('/')
        if len(data_parts) != 5:
            raise ValueError("Expected format: 'Class/Subject/Form/Numberofbooks/Year' or 'BOOK-ID:unique_id'")
        book_class, subject, form, number_of_books, year = data_parts
        book_info = {
            "Class": book_class,
            "Subject": subject,
            "Form": form,
            "Numberofbooks": number_of_books,
            "Year": year
        }
        if not (book_info["Class"].isalnum() and len(book_info["Class"]) <= 20):
            raise ValueError("Class must be alphanumeric and <= 20 characters")
        if len(book_info["Subject"]) > 50:
            raise ValueError("Subject must be <= 50 characters")
        form_val = int(form)
        if not (VALID_FORM_RANGE[0] <= form_val <= VALID_FORM_RANGE[1]):
            raise ValueError(f"Form must be {VALID_FORM_RANGE[0]}-{VALID_FORM_RANGE[1]}")
        num_books = int(number_of_books)
        if num_books <= 0:
            raise ValueError("Numberofbooks must be positive")
        year_val = int(year)
        current_year = datetime.datetime.now().year
        current_century = (current_year // 100) * 100
        if 0 <= year_val <= 99:  # Two-digit year
            year_val += current_century
            book_info["Year"] = str(year_val)
        max_year = current_year + 10
        if not (1900 <= year_val <= max_year):
            raise ValueError(f"Year must be 1900-{max_year}")
        book_number = f"{book_class}/{subject}/{form}/{number_of_books}/{year}"
        book_info["Format"] = "Original"
        return book_number, book_info

    def add_new_book(self):
        """Add a new book via QR code, syncing with main books table."""
        scanned_data = self.read_qr_code()
        if not scanned_data:
            return "No QR code detected or scanning cancelled."
        try:
            book_number, book_info = self._validate_qr_format(scanned_data)
            conn = self.db_manager._create_connection()
            if not conn:
                return "Error: Database connection failed."
            try:
                cursor = conn.cursor()
                cursor.execute("SELECT book_number FROM qr_books WHERE book_number = ?", (book_number,))
                if cursor.fetchone():
                    return f"Error: Book with ID '{book_number}' already exists in QR books."
                cursor.execute("INSERT INTO qr_books (book_number, details, added_date) VALUES (?, ?, ?)",
                               (book_number, json.dumps(book_info), datetime.datetime.now().isoformat()))
                cursor.execute("INSERT OR IGNORE INTO books (book_number, available) VALUES (?, 1)",
                               (book_number,))
                conn.commit()
                self.last_operation_result = book_number
                details_str = ", ".join(f"{k}: {v}" for k, v in book_info.items() if k != "Format")
                return f"Book '{details_str}' added successfully with ID: {book_number} (Format: {book_info['Format']})"
            finally:
                self.db_manager._close_connection(conn)
        except ValueError as ve:
            return f"QR Code Format Error: {ve}"
        except SQLiteError as db_err:
            return f"Database Error: {db_err}"

    def bulk_add_books(self):
        """Add multiple books in bulk via QR code scanning."""
        books_to_add = []
        while True:
            scanned_data = self.read_qr_code()
            if not scanned_data or scanned_data.lower() == "q":
                break
            try:
                book_number, book_info = self._validate_qr_format(scanned_data)
                books_to_add.append((book_number, book_info))
            except ValueError as ve:
                return f"Invalid QR code: {ve}"
        if not books_to_add:
            return "Bulk add cancelled: No books scanned."
        conn = self.db_manager._create_connection()
        if not conn:
            return "Error: Database connection failed."
        try:
            cursor = conn.cursor()
            for book_number, book_info in books_to_add:
                cursor.execute("SELECT book_number FROM qr_books WHERE book_number = ?", (book_number,))
                if cursor.fetchone():
                    continue
                cursor.execute("INSERT INTO qr_books (book_number, details, added_date) VALUES (?, ?, ?)",
                               (book_number, json.dumps(book_info), datetime.datetime.now().isoformat()))
                cursor.execute("INSERT OR IGNORE INTO books (book_number, available) VALUES (?, 1)",
                               (book_number,))
            conn.commit()
            self.last_operation_result = books_to_add
            return f"Successfully added {len(books_to_add)} books."
        except SQLiteError as e:
            conn.rollback()
            return f"Error during bulk add: {e}"
        finally:
            self.db_manager._close_connection(conn)

    def undo_add_book(self):
        """Undo the last add book operation."""
        if not self.last_operation_result or isinstance(self.last_operation_result, list):
            return "Nothing to undo."
        book_number = self.last_operation_result
        conn = self.db_manager._create_connection()
        if not conn:
            return "Error: Database connection failed."
        try:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM qr_books WHERE book_number = ?", (book_number,))
            cursor.execute("DELETE FROM books WHERE book_number = ?", (book_number,))
            conn.commit()
            return f"Undo: Removed book with ID '{book_number}'."
        except SQLiteError as e:
            conn.rollback()
            return f"Undo failed: {e}"
        finally:
            self.db_manager._close_connection(conn)

    def undo_bulk_add(self):
        """Undo the last bulk add operation."""
        if not self.last_operation_result or not isinstance(self.last_operation_result, list):
            return "Nothing to undo."
        books_to_remove = self.last_operation_result
        conn = self.db_manager._create_connection()
        if not conn:
            return "Error: Database connection failed."
        try:
            cursor = conn.cursor()
            for book_number, _ in books_to_remove:
                cursor.execute("DELETE FROM qr_books WHERE book_number = ?", (book_number,))
                cursor.execute("DELETE FROM books WHERE book_number = ?", (book_number,))
            conn.commit()
            return f"Undo: Removed {len(books_to_remove)} books."
        except SQLiteError as e:
            conn.rollback()
            return f"Undo failed: {e}"
        finally:
            self.db_manager._close_connection(conn)

    def borrow_book(self, student_id):
        """Borrow a book via QR code, syncing with main borrow table."""
        scanned_data = self.read_qr_code()
        if not scanned_data:
            return "No QR code detected or scanning cancelled."
        if not student_id or not (MIN_STUDENT_ID_LENGTH <= len(student_id.strip()) <= MAX_STUDENT_ID_LENGTH and student_id.strip().isalnum()):
            return f"Error: Student ID must be {MIN_STUDENT_ID_LENGTH}-{MAX_STUDENT_ID_LENGTH} alphanumeric characters."
        try:
            book_number, book_info = self._validate_qr_format(scanned_data)
            conn = self.db_manager._create_connection()
            if not conn:
                return "Error: Database connection failed."
            try:
                cursor = conn.cursor()
                cursor.execute("SELECT COUNT(*) FROM qr_borrow_log WHERE student_id = ? AND return_date IS NULL", (student_id,))
                if cursor.fetchone()[0] >= MAX_BORROW_LIMIT:
                    return f"Error: Student ID '{self._mask_student_id(student_id)}' has reached the borrow limit of {MAX_BORROW_LIMIT} books."
                cursor.execute("SELECT book_number FROM qr_books WHERE book_number = ?", (book_number,))
                if not cursor.fetchone():
                    return f"Error: Book with ID '{book_number}' not found in QR books."
                cursor.execute("SELECT available FROM books WHERE book_number = ?", (book_number,))
                book_record = cursor.fetchone()
                if not book_record or not book_record[0]:
                    return f"Error: Book with ID '{book_number}' is unavailable."
                cursor.execute("UPDATE books SET available = 0 WHERE book_number = ?", (book_number,))
                now = datetime.datetime.now().isoformat()
                cursor.execute("INSERT INTO qr_borrow_log (book_number, student_id, borrow_date) VALUES (?, ?, ?)",
                               (book_number, student_id, now))
                cursor.execute("INSERT INTO borrowed_books_student (student_id, book_number, borrowed_on) VALUES (?, ?, ?)",
                               (student_id, book_number, datetime.date.today().isoformat()))
                conn.commit()
                self.last_operation_result = (book_number, student_id)
                details_str = ", ".join(f"{k}: {v}" for k, v in book_info.items() if k != "Format")
                return f"Book '{details_str}' borrowed successfully with ID: {book_number} for Student ID: {self._mask_student_id(student_id)}"
            finally:
                self.db_manager._close_connection(conn)
        except ValueError as ve:
            return f"QR Code Format Error: {ve}"
        except SQLiteError as db_err:
            return f"Database Error: {db_err}"

    def undo_borrow_book(self):
        """Undo the last borrow book operation."""
        if not self.last_operation_result or isinstance(self.last_operation_result, list):
            return "Nothing to undo."
        book_number, student_id = self.last_operation_result
        conn = self.db_manager._create_connection()
        if not conn:
            return "Error: Database connection failed."
        try:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM qr_borrow_log WHERE book_number = ? AND student_id = ? AND return_date IS NULL",
                           (book_number, student_id))
            cursor.execute("UPDATE books SET available = 1 WHERE book_number = ?", (book_number,))
            cursor.execute("DELETE FROM borrowed_books_student WHERE book_number = ? AND student_id = ?",
                           (book_number, student_id))
            conn.commit()
            return f"Undo: Cancelled borrow of book '{book_number}' for Student ID: {self._mask_student_id(student_id)}."
        except SQLiteError as e:
            conn.rollback()
            return f"Undo failed: {e}"
        finally:
            self.db_manager._close_connection(conn)

    def return_book(self):
        """Return a book via QR code, syncing with main borrow table."""
        scanned_data = self.read_qr_code()
        if not scanned_data:
            return "No QR code detected or scanning cancelled."
        try:
            book_number, book_info = self._validate_qr_format(scanned_data)
            conn = self.db_manager._create_connection()
            if not conn:
                return "Error: Database connection failed."
            try:
                cursor = conn.cursor()
                cursor.execute("SELECT book_number, student_id FROM qr_borrow_log WHERE book_number = ? AND return_date IS NULL", (book_number,))
                borrow_record = cursor.fetchone()
                if not borrow_record:
                    return f"Error: Book with ID '{book_number}' is not currently borrowed."
                student_id = borrow_record[1]
                now = datetime.datetime.now().isoformat()
                cursor.execute("UPDATE qr_borrow_log SET return_date = ? WHERE book_number = ? AND return_date IS NULL",
                               (now, book_number))
                cursor.execute("UPDATE books SET available = 1 WHERE book_number = ?", (book_number,))
                cursor.execute("DELETE FROM borrowed_books_student WHERE book_number = ? AND student_id = ?",
                               (book_number, student_id))
                conn.commit()
                self.last_operation_result = (book_number, student_id)
                details_str = ", ".join(f"{k}: {v}" for k, v in book_info.items() if k != "Format")
                return f"Book '{details_str}' returned successfully with ID: {book_number} by Student ID: {self._mask_student_id(student_id)}"
            finally:
                self.db_manager._close_connection(conn)
        except ValueError as ve:
            return f"QR Code Format Error: {ve}"
        except SQLiteError as db_err:
            return f"Database Error: {db_err}"

    def undo_return_book(self):
        """Undo the last return book operation."""
        if not self.last_operation_result or isinstance(self.last_operation_result, list):
            return "Nothing to undo."
        book_number, student_id = self.last_operation_result
        conn = self.db_manager._create_connection()
        if not conn:
            return "Error: Database connection failed."
        try:
            cursor = conn.cursor()
            cursor.execute("UPDATE qr_borrow_log SET return_date = NULL WHERE book_number = ? AND student_id = ?",
                           (book_number, student_id))
            cursor.execute("UPDATE books SET available = 0 WHERE book_number = ?", (book_number,))
            cursor.execute("INSERT INTO borrowed_books_student (student_id, book_number, borrowed_on) VALUES (?, ?, ?)",
                           (student_id, book_number, datetime.date.today().isoformat()))
            conn.commit()
            return f"Undo: Re-borrowed book '{book_number}' for Student ID: {self._mask_student_id(student_id)}."
        except SQLiteError as e:
            conn.rollback()
            return f"Undo failed: {e}"
        finally:
            self.db_manager._close_connection(conn)

    def view_book_data(self):
        """View all QR books with stream of the most recent borrower."""
        for attempt in range(MAX_RETRIES):
            try:
                conn = self.db_manager._create_connection()
                if not conn:
                    return []
                try:
                    cursor = conn.cursor()
                    cursor.execute("""
                        SELECT qb.book_number, qb.details, qb.added_date, s.stream
                        FROM qr_books qb
                        LEFT JOIN (
                            SELECT book_number, student_id
                            FROM qr_borrow_log
                            WHERE return_date IS NULL
                            ORDER BY borrow_date DESC
                        ) qbl ON qb.book_number = qbl.book_number
                        LEFT JOIN students s ON qbl.student_id = s.student_id
                    """)
                    return [
                        {
                            'book_number': row[0],
                            'details': json.loads(row[1]),
                            'added_date': row[2],
                            'stream': row[3] if row[3] else "N/A"
                        } for row in cursor.fetchall()
                    ]
                finally:
                    self.db_manager._close_connection(conn)
            except SQLiteError as db_err:
                self.logger.error(f"Attempt {attempt + 1}/{MAX_RETRIES} - Database Error: {db_err}")
                if attempt == MAX_RETRIES - 1:
                    return []
                time.sleep(1)
        return []

    def view_borrow_log(self):
        """View the QR borrow log with stream."""
        for attempt in range(MAX_RETRIES):
            try:
                conn = self.db_manager._create_connection()
                if not conn:
                    return []
                try:
                    cursor = conn.cursor()
                    cursor.execute("""
                        SELECT qbl.book_number, qbl.student_id, qbl.borrow_date, qbl.return_date, s.stream
                        FROM qr_borrow_log qbl
                        LEFT JOIN students s ON qbl.student_id = s.student_id
                    """)
                    return [
                        {
                            'book_number': row[0],
                            'student_id': row[1],
                            'borrow_date': row[2],
                            'return_date': row[3] if row[3] else "Not Returned",
                            'stream': row[4] if row[4] else "N/A"
                        } for row in cursor.fetchall()
                    ]
                finally:
                    self.db_manager._close_connection(conn)
            except SQLiteError as db_err:
                self.logger.error(f"Attempt {attempt + 1}/{MAX_RETRIES} - Database Error: {db_err}")
                if attempt == MAX_RETRIES - 1:
                    return []
                time.sleep(1)
        return []

    def search_student(self, student_id):
        """Search for a student and return their borrowing details."""
        for attempt in range(MAX_RETRIES):
            try:
                conn = self.db_manager._create_connection()
                if not conn:
                    return "Error: Could not connect to database."
                try:
                    cursor = conn.cursor()
                    cursor.execute("SELECT name, stream FROM students WHERE student_id = ?", (student_id,))
                    student_record = cursor.fetchone()
                    if not student_record:
                        return f"Error: Student ID '{self._mask_student_id(student_id)}' not found."
                    student_name, stream = student_record
                    cursor.execute("""
                        SELECT qb.book_number, qb.details, qbl.borrow_date, qbl.return_date
                        FROM qr_borrow_log qbl
                        JOIN qr_books qb ON qbl.book_number = qb.book_number
                        WHERE qbl.student_id = ?
                    """, (student_id,))
                    borrowed_books = [
                        {
                            'book_number': row[0],
                            'details': json.loads(row[1]),
                            'borrow_date': row[2],
                            'return_date': row[3] if row[3] else "Not Returned"
                        } for row in cursor.fetchall()
                    ]
                    return {
                        'student_id': student_id,
                        'student_name': student_name,
                        'stream': stream if stream else "N/A",
                        'borrowed_books': borrowed_books
                    }
                finally:
                    self.db_manager._close_connection(conn)
            except SQLiteError as db_err:
                self.logger.error(f"Attempt {attempt + 1}/{MAX_RETRIES} - Database Error: {db_err}")
                if attempt == MAX_RETRIES - 1:
                    return "Error: Database operation failed."
                time.sleep(1)
        return "Error: Database operation failed."

    def search_unreturned_books(self):
        """Fetch unreturned books with student details and stream."""
        for attempt in range(MAX_RETRIES):
            try:
                conn = self.db_manager._create_connection()
                if not conn:
                    return []
                try:
                    cursor = conn.cursor()
                    cursor.execute("""
                        SELECT qbl.book_number, qbl.student_id, s.name, qbl.borrow_date, s.stream
                        FROM qr_borrow_log qbl
                        JOIN students s ON qbl.student_id = s.student_id
                        WHERE qbl.return_date IS NULL
                        ORDER BY s.name ASC
                    """)
                    return [
                        {
                            'book_number': row[0],
                            'student_id': row[1],
                            'student_name': row[2],
                            'borrow_date': row[3],
                            'stream': row[4] if row[4] else "N/A"
                        } for row in cursor.fetchall()
                    ]
                finally:
                    self.db_manager._close_connection(conn)
            except SQLiteError as db_err:
                self.logger.error(f"Attempt {attempt + 1}/{MAX_RETRIES} - Database Error: {db_err}")
                if attempt == MAX_RETRIES - 1:
                    return []
                time.sleep(1)
        return []

    def _mask_student_id(self, student_id):
        """Mask student ID for privacy."""
        if len(student_id) > 3:
            return f"{student_id[:3]}{'*' * (len(student_id) - 3)}"
        return student_id

    def auto_detect_scanner(self):
        """Auto-detect scanner type (serial or HID)."""
        ports = list(serial.tools.list_ports.comports())
        if ports:
            try:
                serial_port = serial.Serial(ports[0].device, baudrate=9600, timeout=0.1)
                if serial_port.in_waiting > 0:
                    serial_port.close()
                    return "serial", ports[0].device
                serial_port.close()
            except serial.SerialException:
                pass
        return "hid", None

    def read_qr_code(self):
        """Read QR code from HID or serial scanner."""
        MIN_SCAN_INTERVAL = 2
        current_time = datetime.datetime.now().timestamp()
        if current_time - self.last_scan_time < MIN_SCAN_INTERVAL and self.last_scan_data:
            self.logger.debug(f"Duplicate scan prevented: {self.last_scan_data}")
            return self.last_scan_data

        if not self.root:
            self.logger.error("No GUI root available for scanning")
            return None

        self.logger.info("Starting QR code scan")
        scan_window = tk.Toplevel(self.root)
        scan_window.title("Scan QR Code")
        scan_window.geometry("400x200")
        ttk.Label(scan_window, text="Scan a QR code with your scanner").pack(pady=5)
        ttk.Label(scan_window, text=f"Waiting for input ({SCANNER_TIMEOUT}s timeout)...").pack(pady=5)
        ttk.Label(scan_window, text="Press 'q' to cancel").pack(pady=5)
        entry = ttk.Entry(scan_window)
        entry.pack(pady=5)
        entry.focus_set()

        qr_data = [None]
        scan_complete = [False]
        start_time = time.time()

        scanner_type, serial_device = self.auto_detect_scanner()
        self.logger.info(f"Detected scanner type: {scanner_type}")

        def on_key(event):
            if event.keysym == "Return" and entry.get().strip():
                qr_data[0] = entry.get().strip()
                scan_complete[0] = True
                scan_window.destroy()
            elif event.keysym == "q":
                scan_complete[0] = True
                scan_window.destroy()

        entry.bind("<KeyRelease>", on_key)

        serial_port = None
        if scanner_type == "serial":
            try:
                serial_port = serial.Serial(serial_device, baudrate=9600, timeout=0.1)
                self.logger.info(f"Listening on serial port {serial_device}")
            except serial.SerialException as e:
                self.logger.debug(f"Serial port error: {e}")
                scanner_type = "hid"

        def check_input():
            if scan_complete[0]:
                return
            if scanner_type == "serial" and serial_port and serial_port.in_waiting > 0:
                data = serial_port.readline().decode('utf-8', errors='ignore').strip()
                if data:
                    qr_data[0] = data
                    scan_complete[0] = True
                    scan_window.destroy()
                    return
            if time.time() - start_time > SCANNER_TIMEOUT:
                self.logger.info("Scan timeout reached")
                scan_complete[0] = True
                scan_window.destroy()
                return
            scan_window.after(100, check_input)

        scan_window.after(100, check_input)
        scan_window.wait_window()

        if serial_port and serial_port.is_open:
            serial_port.close()

        if not qr_data[0]:
            self.logger.info("Scan cancelled or timed out")
            return None

        if scanner_type == "hid":
            self.logger.info("Using HID scanner mode")
            hid_window = tk.Toplevel(self.root)
            hid_window.title("HID Scanner Input")
            hid_window.geometry("300x150")
            ttk.Label(hid_window, text="Scan QR code with HID scanner").pack(pady=5)
            hid_entry = ttk.Entry(hid_window)
            hid_entry.pack(pady=5)
            hid_entry.focus_set()

            def on_hid_key(event):
                if event.keysym == "Return" and hid_entry.get().strip():
                    qr_data[0] = hid_entry.get().strip()
                    hid_window.destroy()

            hid_entry.bind("<Return>", on_hid_key)
            ttk.Button(hid_window, text="Cancel", command=hid_window.destroy).pack(pady=5)
            hid_window.wait_window()

        if qr_data[0]:
            self.last_scan_time = current_time
            self.last_scan_data = qr_data[0]
            self.logger.info(f"QR code scanned: {qr_data[0]}")
            return qr_data[0]
        self.logger.info("Scan cancelled")
        return None

    def generate_qr_code(self, book_details):
        """Generate a QR code for a book."""
        if not qrcode:
            return "Error: qrcode library not installed."
        try:
            if "Format" in book_details and book_details["Format"] == "Simple":
                qr_data = f"BOOK-ID:{book_details['ID']}"
            else:
                qr_data = f"{book_details['Class']}/{book_details['Subject']}/{book_details['Form']}/{book_details['Numberofbooks']}/{book_details['Year']}"
            qr = qrcode.QRCode(version=1, box_size=10, border=5)
            qr.add_data(qr_data)
            qr.make(fit=True)
            img = qr.make_image(fill_color="black", back_color="white")
            filename = f"qr_{qr_data.replace('/', '_')}_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
            img.save(filename)
            return f"QR code generated and saved as '{filename}'"
        except Exception as e:
            return f"Error generating QR code: {e}"

    def analyze_borrowing_patterns(self):
        """Analyze borrowing patterns to find the most popular book."""
        try:
            borrow_log = self.view_borrow_log()
            book_counts = {}
            for log in borrow_log:
                book_counts[log['book_number']] = book_counts.get(log['book_number'], 0) + 1
            if not book_counts:
                return "No borrowing data available."
            most_popular = max(book_counts.items(), key=lambda x: x[1])
            return f"Most popular book: {most_popular[0]} (borrowed {most_popular[1]} times)"
        except Exception as e:
            return f"Error analyzing borrowing patterns: {e}"

    def get_overdue_books(self):
        """Fetch overdue books (borrowed > OVERDUE_DAYS)."""
        try:
            overdue_books = []
            for log in self.view_borrow_log():
                if log['return_date'] == "Not Returned":
                    borrow_date = datetime.datetime.fromisoformat(log['borrow_date'])
                    if (datetime.datetime.now() - borrow_date).days > OVERDUE_DAYS:
                        overdue_books.append(log)
            return overdue_books
        except Exception as e:
            self.logger.error(f"Error fetching overdue books: {e}")
            return []

    def backup_database(self):
        """Simulate database backup to a local SQL file."""
        try:
            backup_file = f"library_backup_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.sql"
            with open(backup_file, "w") as f:
                f.write("-- SQLite database backup\n")
                for book in self.view_book_data():
                    f.write(f"INSERT OR REPLACE INTO qr_books (book_number, details, added_date) VALUES ('{book['book_number']}', '{json.dumps(book['details'])}', '{book['added_date']}');\n")
            return f"Database backed up to {backup_file}"
        except Exception as e:
            return f"Error during backup: {e}"

    def get_total_books(self):
        """Return total number of books."""
        conn = self.db_manager._create_connection()
        if not conn:
            return 0
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM qr_books")
            total = cursor.fetchone()[0]
            return total
        except SQLiteError as e:
            self.logger.error(f"Error fetching total books: {e}")
            return 0
        finally:
            self.db_manager._close_connection(conn)

    def get_borrowed_books_count(self):
        """Return number of currently borrowed books."""
        conn = self.db_manager._create_connection()
        if not conn:
            return 0
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM qr_borrow_log WHERE return_date IS NULL")
            total = cursor.fetchone()[0]
            return total
        except SQLiteError as e:
            self.logger.error(f"Error fetching borrowed books count: {e}")
            return 0
        finally:
            self.db_manager._close_connection(conn)

    def get_overdue_books_count(self):
        """Return number of overdue books."""
        conn = self.db_manager._create_connection()
        if not conn:
            return 0
        try:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT COUNT(*) 
                FROM qr_borrow_log 
                WHERE return_date IS NULL 
                AND JULIANDAY('now') - JULIANDAY(borrow_date) > ?
            """, (OVERDUE_DAYS,))
            total = cursor.fetchone()[0]
            return total
        except SQLiteError as e:
            self.logger.error(f"Error fetching overdue books count: {e}")
            return 0
        finally:
            self.db_manager._close_connection(conn)


class QRCodeScannerGUI(ttk.Frame):
    def __init__(self, parent, db_manager, *args, **kwargs):
        self.logger = logging.getLogger('QRCodeScannerGUI')
        try:
            self.logger.info("Initializing QRCodeScannerGUI")
            ttk.Frame.__init__(self, parent, *args, **kwargs)
            self.root = parent
            self.db_manager = db_manager

            self.book_manager = QRCodeBookManager(self.db_manager)
            self.current_user = None
            self.undo_stack = []
            self.redo_stack = []

            self.queue = queue.Queue()
            self._after_id = None
            self._check_queue()

            style = ttk.Style()
            style.configure("TButton", padding=6, relief="raised")
            style.configure("TLabel", padding=6)
            style.configure("Header.TLabel", font=('Helvetica', 12, 'bold'))
            style.configure("Action.TButton", font=("Helvetica", 10, "bold"), padding=5, background="#4CAF50", foreground="white")

            self.grid(row=0, column=0, sticky="nsew")
            self.root.grid_columnconfigure(0, weight=1)
            self.root.grid_rowconfigure(0, weight=1)

            self.setup_main_gui()

        except Exception as e:
            self.logger.error(f"Failed to initialize QRCodeScannerGUI: {e}")
            raise

    def setup_main_gui(self):
        self.logger.info("Setting up main GUI with grid")
        main_frame = ttk.Frame(self, padding="10")
        main_frame.grid(row=0, column=0, sticky="nsew")
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)

        header_label = ttk.Label(main_frame, text="QR Code Book Management System", style="Header.TLabel")
        header_label.grid(row=0, column=0, columnspan=3, sticky="ew", pady=(0, 10))

        self.create_dashboard(main_frame)
        self.dashboard_frame.grid(row=1, column=0, columnspan=3, sticky="ew", pady=5)

        buttons_frame = ttk.LabelFrame(main_frame, text="Actions", padding="5")
        buttons_frame.grid(row=2, column=0, columnspan=3, sticky="ew", pady=5)

        # Buttons (unchanged layout, just ensuring functionality)
        self.add_book_button = ttk.Button(buttons_frame, text="Add New Book", command=self.add_new_book_action)
        self.add_book_button.grid(row=0, column=0, padx=5, pady=5, sticky="ew")
        self.bulk_add_button = ttk.Button(buttons_frame, text="Bulk Add Books", command=self.bulk_add_books_action)
        self.bulk_add_button.grid(row=0, column=1, padx=5, pady=5, sticky="ew")
        self.borrow_book_button = ttk.Button(buttons_frame, text="Borrow Book", command=self.borrow_book_action)
        self.borrow_book_button.grid(row=0, column=2, padx=5, pady=5, sticky="ew")

        self.return_book_button = ttk.Button(buttons_frame, text="Return Book", command=self.return_book_action)
        self.return_book_button.grid(row=1, column=0, padx=5, pady=5, sticky="ew")
        self.view_books_button = ttk.Button(buttons_frame, text="View Books", command=self.view_books_action)
        self.view_books_button.grid(row=1, column=1, padx=5, pady=5, sticky="ew")
        self.view_borrow_log_button = ttk.Button(buttons_frame, text="View Borrowed Books", command=self.view_borrow_log_action)
        self.view_borrow_log_button.grid(row=1, column=2, padx=5, pady=5, sticky="ew")

        self.search_student_button = ttk.Button(buttons_frame, text="Search Student", command=self.search_student_action)
        self.search_student_button.grid(row=2, column=0, padx=5, pady=5, sticky="ew")
        self.search_unreturned_button = ttk.Button(buttons_frame, text="Search Unreturned Books", command=self.search_unreturned_books_action)
        self.search_unreturned_button.grid(row=2, column=1, padx=5, pady=5, sticky="ew")
        self.generate_qr_button = ttk.Button(buttons_frame, text="Generate QR Code", command=self.generate_qr_action)
        self.generate_qr_button.grid(row=2, column=2, padx=5, pady=5, sticky="ew")

        self.undo_button = ttk.Button(buttons_frame, text="Undo", command=self.undo_action)
        self.undo_button.grid(row=3, column=0, padx=5, pady=5, sticky="ew")
        self.redo_button = ttk.Button(buttons_frame, text="Redo", command=self.redo_action)
        self.redo_button.grid(row=3, column=1, padx=5, pady=5, sticky="ew")
        self.voice_button = ttk.Button(buttons_frame, text="Enable Voice", command=self.enable_voice_commands)
        self.voice_button.grid(row=3, column=2, padx=5, pady=5, sticky="ew")

        self.analytics_button = ttk.Button(buttons_frame, text="Analytics", command=self.show_analytics)
        self.analytics_button.grid(row=4, column=0, padx=5, pady=5, sticky="ew")
        self.overdue_button = ttk.Button(buttons_frame, text="Check Overdue", command=self.check_overdue_books)
        self.overdue_button.grid(row=4, column=1, padx=5, pady=5, sticky="ew")
        self.backup_button = ttk.Button(buttons_frame, text="Backup Database", command=self.backup_database_action)
        self.backup_button.grid(row=4, column=2, padx=5, pady=5, sticky="ew")

        quit_button = ttk.Button(buttons_frame, text="Quit", command=self.root.destroy)
        quit_button.grid(row=5, column=0, columnspan=3, padx=5, pady=5, sticky="ew")

        for i in range(3):
            buttons_frame.grid_columnconfigure(i, weight=1)

        self.bind("<Control-a>", lambda event: self.add_new_book_action())
        self.bind("<Control-b>", lambda event: self.borrow_book_action())
        self.bind("<Control-r>", lambda event: self.return_book_action())
        self.bind("<Control-v>", lambda event: self.view_books_action())
        self.bind("<Control-z>", lambda event: self.undo_action())
        self.bind("<Control-y>", lambda event: self.redo_action())

        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        self.schedule_unreturned_report()
        self.logger.info("Main GUI setup completed with grid")

    def create_dashboard(self, parent):
        try:
            user_text = "Guest" if self.current_user is None else self.current_user.get('username', 'Unknown')
            self.dashboard_frame = ttk.LabelFrame(parent, text=f"Dashboard (User: {user_text})", padding="5")
            metrics_frame = ttk.Frame(self.dashboard_frame)
            metrics_frame.grid(row=0, column=0, sticky="ew")
            self.dashboard_frame.grid_columnconfigure(0, weight=1)

            self.total_books_label = ttk.Label(metrics_frame, text="Total Books: ...")
            self.total_books_label.grid(row=0, column=0, padx=10, pady=5, sticky="w")

            self.borrowed_today_label = ttk.Label(metrics_frame, text="Borrowed Today: ...")
            self.borrowed_today_label.grid(row=0, column=1, padx=10, pady=5, sticky="w")

            self.borrowed_books_label = ttk.Label(metrics_frame, text="Borrowed books: ...")
            self.borrowed_books_label.grid(row=0, column=2, padx=10, pady=5, sticky="w")

            self.overdue_label = ttk.Label(metrics_frame, text="Overdue Books: ...")
            self.overdue_label.grid(row=0, column=3, padx=10, pady=5, sticky="w")

            self.overdue_books_label = ttk.Label(metrics_frame, text="Overdue Books: ...")
            self.overdue_books_label.grid(row=0, column=4, padx=10, pady=5, sticky="w")


            metrics_frame.grid_columnconfigure(0, weight=1)
            metrics_frame.grid_columnconfigure(1, weight=1)
            metrics_frame.grid_columnconfigure(2, weight=1)

            recent_frame = ttk.LabelFrame(self.dashboard_frame, text="Recent Actions", padding="5")
            recent_frame.grid(row=1, column=0, columnspan=3, sticky="nsew", pady=5)
            self.dashboard_frame.grid_rowconfigure(1, weight=1)

            self.recent_tree = ttk.Treeview(recent_frame, columns=("Time", "Action"), show="headings")
            self.recent_tree.heading("Time", text="Time")
            self.recent_tree.heading("Action", text="Action")
            self.recent_tree.column("Time", width=150, anchor="center")
            self.recent_tree.column("Action", width=300, anchor="center")
            self.recent_tree.grid(row=0, column=0, sticky="nsew")
            recent_frame.grid_columnconfigure(0, weight=1)
            recent_frame.grid_rowconfigure(0, weight=1)

            self.update_dashboard()
            self.logger.info("Dashboard created successfully with grid")
        except Exception as e:
            self.logger.error(f"Failed to create dashboard: {e}")
            raise

    def update_dashboard(self):
        try:
            books = self.book_manager.view_book_data() if hasattr(self.book_manager, 'view_book_data') else []
            borrow_log = self.book_manager.view_borrow_log() if hasattr(self.book_manager, 'view_borrow_log') else []
            today = datetime.date.today()
            borrowed_today = sum(1 for log in borrow_log if log.get('borrow_date', '').startswith(str(today)))
            overdue_books = len(self.book_manager.get_overdue_books()) if hasattr(self.book_manager, 'get_overdue_books') else 0
            
            # Calculate total borrowed books (books that haven't been returned)
            borrowed_books = sum(1 for log in borrow_log if not log.get('return_date'))  # Assuming empty or missing return_date means not returned
            
            self.total_books_label.config(text=f"Total Books: {len(books)}")
            self.borrowed_today_label.config(text=f"Borrowed Today: {borrowed_today}")
            #self.borrowed_books_label.config(text=f"Borrowed Books: {borrowed_books}")
            self.overdue_label.config(text=f"Overdue Books: {overdue_books}")
            #self.overdue_books_label.config(text=f"Overdue Books: {overdue_books}")
            self.root.after(5000, self.update_dashboard)
        except Exception as e:
            self.logger.error(f"Error updating dashboard: {e}")



    def show_analytics(self):
        """Displays analytics about book borrowing (placeholder)."""
        try:
            analytics_window = tk.Toplevel(self)
            analytics_window.title("Library Analytics")
            analytics_window.geometry("600x400")
            analytics_window.configure(bg="#f0f0f0")

            ttk.Label(analytics_window, text="Library Analytics", font=("Helvetica", 16)).pack(pady=10)

            stats_frame = ttk.LabelFrame(analytics_window, text="Statistics", padding="5")
            stats_frame.pack(fill="x", padx=10, pady=5)

            ttk.Label(stats_frame, text="Total Books: N/A").pack(anchor="w")
            ttk.Label(stats_frame, text="Books Borrowed: N/A").pack(anchor="w")
            ttk.Label(stats_frame, text="Overdue Books: N/A").pack(anchor="w")

            ttk.Button(analytics_window, text="Close", command=analytics_window.destroy, style="Action.TButton").pack(pady=10)

            self._update_feedback("Opened Analytics window.")
        except tk.TclError as tcl_err:
            self._update_feedback(f"GUI Error: Failed to display analytics - {tcl_err}")
            messagebox.showerror("GUI Error", f"Failed to display analytics: {tcl_err}")

    def _update_dashboard(self, message):
        """Updates the recent actions in the dashboard."""
        try:
            if self.recent_tree.winfo_exists():
                timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                self.recent_tree.insert("", 0, values=(timestamp, message))
                if len(self.recent_tree.get_children()) > 5:  # Keep only the last 5 actions
                    self.recent_tree.delete(self.recent_tree.get_children()[-1])
        except tk.TclError as tcl_err:
            self.logger.error(f"Failed to update dashboard: {tcl_err}")

    def on_closing(self):
        """Clean up when closing the window."""
        if self._after_id is not None:
            self.after_cancel(self._after_id)
            self._after_id = None
        self.quit()
        self.destroy()

    def _check_queue(self):
        try:
            if self.winfo_exists():
                while True:
                    msg = self.queue.get_nowait()
                    if msg["action"] == "stop_progress":
                        pass  # Progress bar removed; dashboard updates handle feedback
                    elif msg["action"] == "update_feedback":
                        self._update_dashboard(msg["message"])
                    elif msg["action"] == "show_messagebox":
                        if "Error" in msg["message"]:
                            messagebox.showerror(msg["title"], msg["message"])
                        else:
                            messagebox.showinfo(msg["title"], msg["message"])
                    elif msg["action"] == "update_treeview":
                        tree, data, page, total_pages = msg["tree"], msg["data"], msg["page"], msg["total_pages"]
                        self._update_treeview(tree, data, page, total_pages)
        except queue.Empty:
            pass
        except tk.TclError:
            self.logger.debug("Queue check stopped due to window destruction")
            return
        if self.winfo_exists():
            self._after_id = self.after(100, self._check_queue)

    def _update_treeview(self, tree, data, page, total_pages):
        """Batch update the Treeview with pagination."""
        try:
            tree.delete(*tree.get_children())
            start_idx = (page - 1) * PAGE_SIZE
            end_idx = min(start_idx + PAGE_SIZE, len(data))
            for i in range(start_idx, end_idx):
                row = data[i]
                values = [row.get(col, "") for col in tree["columns"]]
                tree.insert("", tk.END, values=values)
            tree.update_idletasks()
        except tk.TclError as tcl_err:
            self.logger.error(f"Failed to update Treeview: {tcl_err}")

    def _fetch_data_async(self, fetch_func, success_callback, error_message):
        """Fetch data asynchronously."""
        self._update_dashboard(f"Fetching data... Please wait.")
        thread = threading.Thread(target=self._execute_fetch, args=(fetch_func, success_callback, error_message))
        thread.daemon = True
        thread.start()

    def _execute_fetch(self, fetch_func, success_callback, error_message):
        """Execute the fetch operation in a worker thread."""
        try:
            data = fetch_func()
            self.queue.put({"action": "stop_progress"})
            if not data:
                self.queue.put({"action": "update_feedback", "message": error_message})
                self.queue.put({"action": "show_messagebox", "title": "Info", "message": error_message})
            else:
                success_callback(data)
        except Exception as e:
            self.queue.put({"action": "stop_progress"})
            self.queue.put({"action": "update_feedback", "message": f"Error: {e}"})
            self.queue.put({"action": "show_messagebox", "title": "Error", "message": f"Failed to fetch data: {e}"})

    def _add_export_buttons(self, parent, data, columns, filename_prefix, title, total_label):
        """Helper method to add export buttons for Excel and PDF."""
        download_frame = ttk.Frame(parent)
        download_frame.pack(pady=5)

        format_var = tk.StringVar(value="Excel")
        format_menu = ttk.OptionMenu(download_frame, format_var, "Excel", "Excel", "PDF")
        format_menu.pack(side="left", padx=5)

        def download_data():
            file_format = format_var.get()
            file_path = filedialog.asksaveasfilename(
                title=f"Save as {file_format}",
                defaultextension=f".{file_format.lower()}",
                filetypes=[(f"{file_format} files", f"*.{file_format.lower()}"), ("All files", "*.*")],
                initialfile=f"{filename_prefix}_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.{file_format.lower()}"
            )
            if not file_path:
                return

            try:
                if file_format == "Excel":
                    df = pd.DataFrame(data)
                    df.to_excel(file_path, index=False)
                    self._update_dashboard(f"Data exported to {file_path}")
                    messagebox.showinfo("Export Success", f"Data saved to '{file_path}'", parent=parent)

                elif file_format == "PDF":
                    doc = SimpleDocTemplate(file_path, pagesize=letter, topMargin=1*inch, bottomMargin=0.5*inch)
                    elements = []
                    styles = getSampleStyleSheet()

                    def add_page_header_footer(canvas, doc):
                        canvas.saveState()
                        canvas.setFont("Helvetica-Bold", 12)
                        canvas.drawString(inch, letter[1] - 0.5*inch, title)
                        canvas.setFont("Helvetica", 10)
                        canvas.drawString(inch, letter[1] - 0.75*inch, total_label)
                        canvas.setFont("Helvetica", 8)
                        page_num = canvas.getPageNumber()
                        canvas.drawString(letter[0] - 1.5*inch, 0.3*inch, f"Page {page_num}")
                        canvas.restoreState()

                    table_data = [list(columns)]
                    for item in data:
                        row = []
                        for col in columns:
                            row.append(str(item.get(col, "")))
                        table_data.append(row)

                    table = LongTable(table_data)
                    table.setStyle(TableStyle([
                        ("BACKGROUND", (0, 0), (-1, 0), colors.grey),
                        ("TEXTCOLOR", (0, 0), (-1, 0), colors.whitesmoke),
                        ("ALIGN", (0, 0), (-1, -1), "CENTER"),
                        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                        ("FONTSIZE", (0, 0), (-1, 0), 10),
                        ("BOTTOMPADDING", (0, 0), (-1, 0), 12),
                        ("BACKGROUND", (0, 1), (-1, -1), colors.beige),
                        ("GRID", (0, 0), (-1, -1), 1, colors.black),
                        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                    ]))
                    elements.append(table)

                    doc.build(elements, onFirstPage=add_page_header_footer, onLaterPages=add_page_header_footer)
                    self._update_dashboard(f"Data exported to {file_path}")
                    messagebox.showinfo("Export Success", f"Data saved to '{file_path}'", parent=parent)

            except Exception as e:
                self._update_dashboard(f"Export Error: Failed to export data - {e}")
                messagebox.showerror("Export Error", f"Failed to export data: {e}", parent=parent)

        ttk.Button(download_frame, text="Download", command=download_data, style="Action.TButton").pack(side="left", padx=5)

    def _add_pagination_controls(self, parent, tree, data, total_label_widget):
        """Add pagination controls to the Treeview."""
        pagination_frame = ttk.Frame(parent)
        pagination_frame.pack(pady=5)

        self.current_page = tk.IntVar(value=1)
        total_pages = (len(data) + PAGE_SIZE - 1) // PAGE_SIZE
        total_label_widget.config(text=f"Page {self.current_page.get()} of {total_pages} | Total Records: {len(data)}")

        def update_page():
            page = self.current_page.get()
            total_label_widget.config(text=f"Page {page} of {total_pages} | Total Records: {len(data)}")
            self.queue.put({"action": "update_treeview", "tree": tree, "data": data, "page": page, "total_pages": total_pages})

        def prev_page():
            if self.current_page.get() > 1:
                self.current_page.set(self.current_page.get() - 1)
                update_page()

        def next_page():
            if self.current_page.get() < total_pages:
                self.current_page.set(self.current_page.get() + 1)
                update_page()

        ttk.Button(pagination_frame, text="Previous", command=prev_page).pack(side="left", padx=5)
        ttk.Label(pagination_frame, textvariable=self.current_page).pack(side="left", padx=5)
        ttk.Button(pagination_frame, text="Next", command=next_page).pack(side="left", padx=5)

    def _add_sort_and_filter(self, parent, tree, data, columns):
        """Add sorting and filtering to the Treeview."""
        filter_frame = ttk.Frame(parent)
        filter_frame.pack(pady=5)

        ttk.Label(filter_frame, text="Filter by:").pack(side="left", padx=5)
        filter_var = tk.StringVar()
        filter_column = ttk.Combobox(filter_frame, textvariable=filter_var, values=columns, state="readonly")
        filter_column.pack(side="left", padx=5)
        filter_column.set(columns[0])

        filter_entry = ttk.Entry(filter_frame)
        filter_entry.pack(side="left", padx=5)

        def sort_column(col, reverse):
            sorted_data = sorted(data, key=lambda x: x.get(col, ""), reverse=reverse)
            self.queue.put({"action": "update_treeview", "tree": tree, "data": sorted_data, "page": 1, "total_pages": (len(sorted_data) + PAGE_SIZE - 1) // PAGE_SIZE})
            tree.heading(col, command=lambda: sort_column(col, not reverse))

        for col in columns:
            tree.heading(col, text=col, command=lambda c=col: sort_column(c, False))

        def apply_filter():
            filter_text = filter_entry.get().lower()
            filter_col = filter_var.get()
            if not filter_text:
                filtered_data = data
            else:
                filtered_data = [item for item in data if filter_text in str(item.get(filter_col, "")).lower()]
            self.queue.put({"action": "update_treeview", "tree": tree, "data": filtered_data, "page": 1, "total_pages": (len(filtered_data) + PAGE_SIZE - 1) // PAGE_SIZE})

        ttk.Button(filter_frame, text="Apply Filter", command=apply_filter).pack(side="left", padx=5)

        return filter_var, filter_entry

    def _scan_and_process(self, operation, feedback_message, success_title="Scan Result", undo_action=None):
        self._update_dashboard(feedback_message)
        thread = threading.Thread(target=self._execute_scan, args=(operation, success_title, undo_action))
        thread.daemon = True
        thread.start()

    def _execute_scan(self, operation, success_title, undo_action):
        """Execute the scan operation in a worker thread."""
        try:
            result_message = operation()
            self.queue.put({"action": "stop_progress"})
            self.queue.put({"action": "update_feedback", "message": result_message})
            self.queue.put({"action": "show_messagebox", "title": success_title, "message": result_message})
            if undo_action and "Error" not in result_message:
                self.undo_stack.append(undo_action)
                self.redo_stack.clear()
        except Exception as e:
            error_message = f"Unexpected error during scan: {e}"
            self.queue.put({"action": "stop_progress"})
            self.queue.put({"action": "update_feedback", "message": error_message})
            self.queue.put({"action": "show_messagebox", "title": success_title, "message": error_message})

    def undo_action(self):
        if not self.undo_stack:
            self._update_dashboard("Nothing to undo.")
            return
        undo_func = self.undo_stack.pop()
        redo_func = undo_func()
        if redo_func:
            self.redo_stack.append(redo_func)
        self._update_dashboard("Undo operation completed.")

    def redo_action(self):
        if not self.redo_stack:
            self._update_dashboard("Nothing to redo.")
            return
        redo_func = self.redo_stack.pop()
        undo_func = redo_func()
        if undo_func:
            self.undo_stack.append(undo_func)
        self._update_dashboard("Redo operation completed.")

    def enable_voice_commands(self):
        """Enables voice commands for hands-free operation."""
        try:
            recognizer = sr.Recognizer()
            mic = sr.Microphone()

            def listen_for_commands():
                while True:
                    with mic as source:
                        recognizer.adjust_for_ambient_noise(source)
                        try:
                            audio = recognizer.listen(source, timeout=5)
                            command = recognizer.recognize_google(audio).lower()
                            self._update_dashboard(f"Voice command: {command}")
                            if "add book" in command:
                                self.add_new_book_action()
                            elif "borrow book" in command:
                                self.borrow_book_action()
                            elif "return book" in command:
                                self.return_book_action()
                            elif "exit voice" in command:
                                self._update_dashboard("Voice commands disabled.")
                                break
                        except sr.UnknownValueError:
                            self._update_dashboard("Voice command not understood.")
                        except sr.RequestError:
                            self._update_dashboard("Voice recognition service unavailable.")
                        except sr.WaitTimeoutError:
                            pass  # No speech detected

            threading.Thread(target=listen_for_commands, daemon=True).start()
            self._update_dashboard("Voice commands enabled. Say 'Add Book', 'Borrow Book', 'Return Book', or 'Exit Voice'.")
        except Exception as e:
            self._update_dashboard(f"Error enabling voice commands: {e}")

    def add_new_book_action(self):
        """Handles adding a new book via QR."""
        try:
            self._scan_and_process(
                self.book_manager.add_new_book,
                "Adding new book... Please scan QR code.",
                undo_action=self.book_manager.undo_add_book
            )
        except tk.TclError as tcl_err:
            self._update_dashboard(f"GUI Error: Failed to process add book action - {tcl_err}")

    def bulk_add_books_action(self):
        """Handles bulk adding of books via QR."""
        try:
            self._scan_and_process(
                self.book_manager.bulk_add_books,
                "Starting bulk add books... Scan QR codes (press 'q' to finish).",
                undo_action=self.book_manager.undo_bulk_add
            )
        except tk.TclError as tcl_err:
            self._update_dashboard(f"GUI Error: Failed to process bulk add books action - {tcl_err}")

    def borrow_book_action(self):
        """Handles borrowing a book via QR."""
        try:
            student_id = simpledialog.askstring("Borrow Book", "Enter Student ID:")
            if not student_id:
                self._update_dashboard("Borrow book operation cancelled: Student ID not provided.")
                return
            masked_student_id = self.book_manager._mask_student_id(student_id)
            self.logger.info(f"Attempting to borrow book for student ID: {masked_student_id}")
            if messagebox.askyesno("Confirm Borrow", f"Borrow book for Student ID: {masked_student_id}?"):
                self._scan_and_process(
                    lambda: self.book_manager.borrow_book(student_id),
                    f"Borrowing book for Student ID: {masked_student_id}... Please scan QR code.",
                    undo_action=self.book_manager.undo_borrow_book
                )
            else:
                self._update_dashboard("Borrow operation cancelled by user.")
        except tk.TclError as tcl_err:
            self._update_dashboard(f"GUI Error: Failed to process borrow book action - {tcl_err}")

    def return_book_action(self):
        """Handles returning a book via QR."""
        try:
            if messagebox.askyesno("Confirm Return", "Return a book?"):
                self._scan_and_process(
                    self.book_manager.return_book,
                    "Returning book... Please scan QR code.",
                    undo_action=self.book_manager.undo_return_book
                )
            else:
                self._update_dashboard("Return operation cancelled by user.")
        except tk.TclError as tcl_err:
            self._update_dashboard(f"GUI Error: Failed to process return book action - {tcl_err}")

    def view_books_action(self):
        """Displays all QR books with stream, pagination, sorting, and filtering."""
        try:
            view_window = tk.Toplevel(self)
            view_window.title("Library Book Inventory")
            view_window.geometry("800x500")
            view_window.configure(bg="#f0f0f0")

            total_frame = ttk.LabelFrame(view_window, text="Inventory Summary", padding="5")
            total_frame.pack(fill="x", padx=10, pady=5)
            total_label = ttk.Label(total_frame, text="Total Books in Inventory: ...")
            total_label.pack(anchor="w")

            books_frame = ttk.LabelFrame(view_window, text="Books", padding="5")
            books_frame.pack(fill="both", expand=True, padx=10, pady=5)

            tree = ttk.Treeview(
                books_frame,
                columns=("Book ID", "Details", "Added Date", "Stream"),
                show="headings",
                height=10
            )
            tree.heading("Book ID", text="Book ID")
            tree.heading("Details", text="Details")
            tree.heading("Added Date", text="Added Date")
            tree.heading("Stream", text="Stream")
            tree.column("Book ID", width=150, anchor="center")
            tree.column("Details", width=300, anchor="center")
            tree.column("Added Date", width=150, anchor="center")
            tree.column("Stream", width=100, anchor="center")

            scrollbar = ttk.Scrollbar(books_frame, orient="vertical", command=tree.yview)
            tree.configure(yscroll=scrollbar.set)
            tree.pack(side="left", fill="both", expand=True)
            scrollbar.pack(side="right", fill="y")

            def refresh_data():
                self._fetch_data_async(
                    self.book_manager.view_book_data,
                    lambda data: process_data(data),
                    "No book data available or error loading data."
                )

            def process_data(book_data):
                total_label.config(text=f"Total Books in Inventory: {len(book_data)}")
                export_data.clear()
                for book in book_data:
                    details_str = ", ".join(f"{k}: {v}" for k, v in book['details'].items() if k != "Format")
                    export_data.append({
                        "Book ID": book['book_number'],
                        "Details": details_str,
                        "Added Date": book['added_date'],
                        "Stream": book['stream']
                    })
                self.queue.put({"action": "update_treeview", "tree": tree, "data": export_data, "page": 1, "total_pages": (len(export_data) + PAGE_SIZE - 1) // PAGE_SIZE})
                self._update_dashboard(f"Loaded {len(book_data)} book(s) in inventory")

            export_data = []
            filter_var, filter_entry = self._add_sort_and_filter(books_frame, tree, export_data, ["Book ID", "Details", "Added Date", "Stream"])
            self._add_pagination_controls(books_frame, tree, export_data, total_label)

            def print_books():
                try:
                    filename = f"library_books_inventory_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
                    with open(filename, "w") as file:
                        file.write(f"Library Book Inventory - {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                        file.write(f"Total Books in Inventory: {len(export_data)}\n\n")
                        file.write("Books:\n")
                        for book in export_data:
                            file.write(f"  Book ID: {book['Book ID']}\n")
                            file.write(f"    Details: {book['Details']}\n")
                            file.write(f"    Added Date: {book['Added Date']}\n")
                            file.write(f"    Stream: {book['Stream']}\n")
                            file.write("\n")
                    self._update_dashboard(f"Book inventory printed to {filename}")
                    messagebox.showinfo("Print Success", f"Book inventory saved to '{filename}'", parent=view_window)
                except FileNotFoundError as fnf_err:
                    self._update_dashboard(f"File Error: Failed to access file system - {fnf_err}")

            ttk.Button(books_frame, text="Print", command=print_books).pack(pady=5)
            ttk.Button(books_frame, text="Refresh", command=refresh_data, style="Action.TButton").pack(pady=5)
            self._add_export_buttons(
                books_frame,
                export_data,
                ["Book ID", "Details", "Added Date", "Stream"],
                "library_books_inventory",
                "Library Book Inventory",
                f"Total Books in Inventory: {len(export_data)}"
            )
            ttk.Button(books_frame, text="Close", command=view_window.destroy, style="Action.TButton").pack(pady=5)

            refresh_data()

        except tk.TclError as tcl_err:
            self._update_dashboard(f"GUI Error: Failed to display books - {tcl_err}")

    def view_borrow_log_action(self):
        """Displays the QR borrow log with stream, pagination, sorting, and filtering."""
        try:
            view_window = tk.Toplevel(self)
            view_window.title("Borrow Log")
            view_window.geometry("800x500")
            view_window.configure(bg="#f0f0f0")

            log_frame = ttk.LabelFrame(view_window, text="Borrow Log", padding="5")
            log_frame.pack(fill="both", expand=True, padx=10, pady=5)

            tree = ttk.Treeview(
                log_frame,
                columns=("Book ID", "Student ID", "Borrow Date", "Return Date", "Stream"),
                show="headings",
                height=10
            )
            tree.heading("Book ID", text="Book ID")
            tree.heading("Student ID", text="Student ID")
            tree.heading("Borrow Date", text="Borrow Date")
            tree.heading("Return Date", text="Return Date")
            tree.heading("Stream", text="Stream")
            tree.column("Book ID", width=150, anchor="center")
            tree.column("Student ID", width=150, anchor="center")
            tree.column("Borrow Date", width=150, anchor="center")
            tree.column("Return Date", width=150, anchor="center")
            tree.column("Stream", width=100, anchor="center")

            scrollbar = ttk.Scrollbar(log_frame, orient="vertical", command=tree.yview)
            tree.configure(yscroll=scrollbar.set)
            tree.pack(side="left", fill="both", expand=True)
            scrollbar.pack(side="right", fill="y")

            def refresh_data():
                self._fetch_data_async(
                    self.book_manager.view_borrow_log,
                    lambda data: process_data(data),
                    "No borrow log data available or error loading log."
                )

            def process_data(borrow_log):
                export_data.clear()
                for log_entry in borrow_log:
                    export_data.append({
                        "Book ID": log_entry['book_number'],
                        "Student ID": self.book_manager._mask_student_id(log_entry['student_id']),
                        "Borrow Date": log_entry['borrow_date'],
                        "Return Date": log_entry['return_date'],
                        "Stream": log_entry['stream']
                    })
                self.queue.put({"action": "update_treeview", "tree": tree, "data": export_data, "page": 1, "total_pages": (len(export_data) + PAGE_SIZE - 1) // PAGE_SIZE})
                self._update_dashboard(f"Loaded {len(borrow_log)} borrow log entries")

            export_data = []
            filter_var, filter_entry = self._add_sort_and_filter(log_frame, tree, export_data, ["Book ID", "Student ID", "Borrow Date", "Return Date", "Stream"])
            self._add_pagination_controls(log_frame, tree, export_data, ttk.Label(log_frame))

            def export_to_csv():
                try:
                    filename = f"borrow_log_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
                    with open(filename, "w", newline='') as file:
                        writer = csv.writer(file)
                        writer.writerow(["Book ID", "Student ID", "Borrow Date", "Return Date", "Stream"])
                        for log_entry in export_data:
                            writer.writerow([log_entry['Book ID'], log_entry['Student ID'], log_entry['Borrow Date'], log_entry['Return Date'], log_entry['Stream']])
                    self._update_dashboard(f"Borrow log exported to {filename}")
                    messagebox.showinfo("Export Success", f"Borrow log saved to '{filename}'", parent=view_window)
                except IOError as io_err:
                    self._update_dashboard(f"File Error: Failed to export - {io_err}")

            ttk.Button(log_frame, text="Export to CSV", command=export_to_csv).pack(pady=5)
            ttk.Button(log_frame, text="Refresh", command=refresh_data, style="Action.TButton").pack(pady=5)
            self._add_export_buttons(
                log_frame,
                export_data,
                ["Book ID", "Student ID", "Borrow Date", "Return Date", "Stream"],
                "borrow_log",
                "Borrow Log",
                f"Total Borrow Log Entries: {len(export_data)}"
            )
            ttk.Button(log_frame, text="Close", command=view_window.destroy, style="Action.TButton").pack(pady=5)

            refresh_data()

        except tk.TclError as tcl_err:
            self._update_dashboard(f"GUI Error: Failed to display borrow log - {tcl_err}")

    def search_student_action(self):
        """Handles the search student action with stream, enhanced with advanced features."""
        try:
            student_id = simpledialog.askstring("Search Student", "Enter Student ID:")
            if not student_id:
                self._update_feedback("Search cancelled: No Student ID provided.")
                return
            self._update_feedback(f"Searching for Student ID: {student_id}...")

            def process_data(result):
                if isinstance(result, str):
                    self._update_feedback(result)
                    messagebox.showerror("Search Result", result, parent=self.root)
                    return

                result_window = tk.Toplevel(self)
                result_window.title(f"Student Borrowing Details - {student_id}")
                result_window.geometry("800x500")
                result_window.configure(bg="#f0f0f0")

                # Student Information Frame
                info_frame = ttk.LabelFrame(result_window, text="Student Information", padding="5")
                info_frame.pack(fill="x", padx=10, pady=5)
                ttk.Label(info_frame, text=f"Student ID: {result['student_id']}").pack(anchor="w")
                ttk.Label(info_frame, text=f"Name: {result['student_name']}").pack(anchor="w")
                ttk.Label(info_frame, text=f"Stream: {result['stream']}").pack(anchor="w")

                # Borrowed Books Frame
                books_frame = ttk.LabelFrame(result_window, text="Borrowed Books", padding="5")
                books_frame.pack(fill="both", expand=True, padx=10, pady=5)

                export_data = []
                if not result['borrowed_books']:
                    ttk.Label(books_frame, text="No books currently borrowed.").pack(pady=10)
                else:
                    tree = ttk.Treeview(
                        books_frame,
                        columns=("Book ID", "Details", "Borrow Date", "Return Date"),
                        show="headings",
                        height=10
                    )
                    tree.heading("Book ID", text="Book ID")
                    tree.heading("Details", text="Details")
                    tree.heading("Borrow Date", text="Borrow Date")
                    tree.heading("Return Date", text="Return Date")
                    tree.column("Book ID", width=150, anchor="center")
                    tree.column("Details", width=300, anchor="center")
                    tree.column("Borrow Date", width=150, anchor="center")
                    tree.column("Return Date", width=150, anchor="center")

                    # Populate Treeview and prepare export data
                    for book in result['borrowed_books']:
                        details_str = ", ".join(f"{k}: {v}" for k, v in book['details'].items() if k != "Format")
                        tree.insert("", tk.END, values=(book['book_number'], details_str, book['borrow_date'], book['return_date']))
                        export_data.append({
                            "Book ID": book['book_number'],
                            "Details": details_str,
                            "Borrow Date": book['borrow_date'],
                            "Return Date": book['return_date']
                        })

                    scrollbar = ttk.Scrollbar(books_frame, orient="vertical", command=tree.yview)
                    tree.configure(yscroll=scrollbar.set)
                    tree.pack(side="left", fill="both", expand=True)
                    scrollbar.pack(side="right", fill="y")

                    # Add sorting and filtering
                    filter_var, filter_entry = self._add_sort_and_filter(
                        books_frame, tree, export_data, ["Book ID", "Details", "Borrow Date", "Return Date"]
                    )

                    # Add pagination controls
                    total_label = ttk.Label(books_frame, text="Total Borrowed Books: ...")
                    total_label.pack(anchor="w")
                    self._add_pagination_controls(books_frame, tree, export_data, total_label)

                # Print borrowed books to a text file
                def print_borrowed_books():
                    try:
                        filename = f"student_borrowed_books_{student_id}_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
                        with open(filename, "w") as file:
                            file.write(f"Student Borrowing Details - {student_id}\n")
                            file.write(f"Student ID: {result['student_id']}\n")
                            file.write(f"Name: {result['student_name']}\n")
                            file.write(f"Stream: {result['stream']}\n")
                            file.write("Borrowed Books:\n")
                            if not result['borrowed_books']:
                                file.write("  No books currently borrowed.\n")
                            else:
                                for book in result['borrowed_books']:
                                    details_str = ", ".join(f"{k}: {v}" for k, v in book['details'].items() if k != "Format")
                                    file.write(f"  Book ID: {book['book_number']}\n")
                                    file.write(f"    Details: {details_str}\n")
                                    file.write(f"    Borrow Date: {book['borrow_date']}\n")
                                    file.write(f"    Return Date: {book['return_date']}\n")
                                    file.write("\n")
                        self._update_feedback(f"Borrowed books for Student ID {student_id} printed to {filename}")
                        messagebox.showinfo("Print Success", f"Borrowed books saved to '{filename}'", parent=result_window)
                    except FileNotFoundError as fnf_err:
                        self._update_feedback(f"File Error: Failed to access file system - {fnf_err}")
                        messagebox.showerror("Print Error", f"Failed to print: {fnf_err}", parent=result_window)

                # Add buttons
                ttk.Button(books_frame, text="Print", command=print_borrowed_books).pack(pady=5)
                self._add_export_buttons(
                    books_frame,
                    export_data,
                    ["Book ID", "Details", "Borrow Date", "Return Date"],
                    f"student_borrowed_books_{student_id}",
                    f"Student Borrowing Details - {student_id}",
                    f"Total Borrowed Books: {len(result['borrowed_books'])}"
                )
                ttk.Button(books_frame, text="Close", command=result_window.destroy, style="Action.TButton").pack(pady=5)

                # Update feedback and dashboard
                self._update_feedback(f"Found {len(result['borrowed_books'])} book(s) for Student ID: {student_id}")
                self.update_dashboard()

            # Fetch data asynchronously
            self._fetch_data_async(
                lambda: self.book_manager.search_student(student_id),
                process_data,
                f"No data found for Student ID: {student_id}"
            )

        except tk.TclError as tcl_err:
            self._update_feedback(f"GUI Error: Failed to display student search - {tcl_err}")
            messagebox.showerror("GUI Error", f"Failed to display student search: {tcl_err}")
        except Exception as e:
            self._update_feedback(f"Unexpected Error: {e}")
            messagebox.showerror("Error", f"An unexpected error occurred: {e}")


    def search_unreturned_books_action(self):
        """Displays unreturned books with stream, pagination, sorting, filtering, and advanced features."""
        try:
            view_window = tk.Toplevel(self)
            view_window.title("Unreturned Books")
            view_window.geometry("900x600")  # Increased size for additional controls
            view_window.configure(bg="#f0f0f0")

            total_frame = ttk.LabelFrame(view_window, text="Summary", padding="5")
            total_frame.pack(fill="x", padx=10, pady=5)
            total_label = ttk.Label(total_frame, text="Total Unreturned Books: ...")
            total_label.pack(anchor="w")

            books_frame = ttk.LabelFrame(view_window, text="Unreturned Books (Sorted by Student Name)", padding="5")
            books_frame.pack(fill="both", expand=True, padx=10, pady=5)

            tree = ttk.Treeview(
                books_frame,
                columns=("Book ID", "Student ID", "Student Name", "Borrow Date", "Stream", "Days Overdue"),
                show="headings",
                height=15  # Increased height for better visibility
            )
            tree.heading("Book ID", text="Book ID")
            tree.heading("Student ID", text="Student ID")
            tree.heading("Student Name", text="Student Name")
            tree.heading("Borrow Date", text="Borrow Date")
            tree.heading("Stream", text="Stream")
            tree.heading("Days Overdue", text="Days Overdue")
            tree.column("Book ID", width=150, anchor="center")
            tree.column("Student ID", width=150, anchor="center")
            tree.column("Student Name", width=200, anchor="center")
            tree.column("Borrow Date", width=150, anchor="center")
            tree.column("Stream", width=100, anchor="center")
            tree.column("Days Overdue", width=100, anchor="center")

            scrollbar = ttk.Scrollbar(books_frame, orient="vertical", command=tree.yview)
            tree.configure(yscroll=scrollbar.set)
            tree.pack(side="left", fill="both", expand=True)
            scrollbar.pack(side="right", fill="y")

            def refresh_data():
                self._fetch_data_async(
                    self.book_manager.search_unreturned_books,
                    lambda data: process_data(data),
                    "No unreturned books found or error loading data."
                )

            def process_data(unreturned_data):
                total_label.config(text=f"Total Unreturned Books: {len(unreturned_data)}")
                export_data.clear()
                tree.delete(*tree.get_children())  # Clear existing entries
                for book in unreturned_data:
                    # Calculate days overdue
                    borrow_date = datetime.datetime.strptime(book['borrow_date'], "%Y-%m-%d %H:%M:%S")
                    days_overdue = (datetime.datetime.now() - borrow_date).days
                    export_data.append({
                        "Book ID": book['book_number'],
                        "Student ID": book['student_id'],
                        "Student Name": book['student_name'],
                        "Borrow Date": book['borrow_date'],
                        "Stream": book['stream'],
                        "Days Overdue": str(days_overdue) if days_overdue > 0 else "0"
                    })
                    tree.insert("", tk.END, values=(
                        book['book_number'],
                        book['student_id'],
                        book['student_name'],
                        book['borrow_date'],
                        book['stream'],
                        str(days_overdue) if days_overdue > 0 else "0"
                    ))
                self.queue.put({"action": "update_treeview", "tree": tree, "data": export_data, "page": 1, "total_pages": (len(export_data) + PAGE_SIZE - 1) // PAGE_SIZE})
                self._update_feedback(f"Loaded {len(unreturned_data)} unreturned book(s)")

            export_data = []
            filter_var, filter_entry = self._add_sort_and_filter(
                books_frame, tree, export_data, ["Book ID", "Student ID", "Student Name", "Borrow Date", "Stream", "Days Overdue"]
            )
            self._add_pagination_controls(books_frame, tree, export_data, total_label)

            # Add a frame for action buttons
            action_frame = ttk.Frame(books_frame)
            action_frame.pack(fill="x", pady=5)

            def print_unreturned_books():
                try:
                    filename = f"unreturned_books_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
                    with open(filename, "w") as file:
                        file.write(f"Unreturned Books - {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                        file.write(f"Total Unreturned Books: {len(export_data)}\n\n")
                        file.write("Unreturned Books (Sorted by Student Name):\n")
                        for book in export_data:
                            file.write(f"  Book ID: {book['Book ID']}\n")
                            file.write(f"    Student ID: {book['Student ID']}\n")
                            file.write(f"    Student Name: {book['Student Name']}\n")
                            file.write(f"    Borrow Date: {book['Borrow Date']}\n")
                            file.write(f"    Stream: {book['Stream']}\n")
                            file.write(f"    Days Overdue: {book['Days Overdue']}\n")
                            file.write("\n")
                    self._update_feedback(f"Unreturned books printed to {filename}")
                    messagebox.showinfo("Print Success", f"Unreturned books saved to '{filename}'", parent=view_window)
                except FileNotFoundError as fnf_err:
                    self._update_feedback(f"File Error: Failed to access file system - {fnf_err}")
                    messagebox.showerror("Print Error", f"Failed to print: {fnf_err}", parent=view_window)

            def notify_overdue():
                """Sends email notifications for overdue books."""
                try:
                    overdue_books = [
                        book for book in export_data
                        if int(book['Days Overdue']) > 14  # Assuming 14 days is the overdue threshold
                    ]
                    if not overdue_books:
                        self._update_feedback("No overdue books to notify.")
                        messagebox.showinfo("Notification", "No overdue books to notify.", parent=view_window)
                        return

                    for book in overdue_books:
                        msg = MIMEText(
                            f"Dear {book['Student Name']},\n\n"
                            f"The book with ID {book['Book ID']} is overdue by {book['Days Overdue']} days. "
                            f"Please return it at your earliest convenience.\n\n"
                            f"Thanks,\nLibrary Team"
                        )
                        msg['Subject'] = "Overdue Book Reminder"
                        msg['From'] = "library@example.com"
                        msg['To'] = f"student_{book['Student ID']}@example.com"

                        with smtplib.SMTP("smtp.example.com", 587) as server:
                            server.starttls()
                            server.login("library@example.com", "password")  # Replace with actual credentials
                            server.send_message(msg)
                        self._update_feedback(f"Sent overdue notification for book {book['Book ID']} to student {book['Student ID']}.")
                    messagebox.showinfo("Notification Success", f"Sent notifications for {len(overdue_books)} overdue books.", parent=view_window)
                except Exception as e:
                    self._update_feedback(f"Error sending notifications: {e}")
                    messagebox.showerror("Notification Error", f"Failed to send notifications: {e}", parent=view_window)

            def return_selected_book():
                """Returns a selected book directly from the unreturned books list with undo support."""
                selected_item = tree.selection()
                if not selected_item:
                    self._update_feedback("No book selected to return.")
                    messagebox.showwarning("Selection Error", "Please select a book to return.", parent=view_window)
                    return

                book_number = tree.item(selected_item, "values")[0]
                student_id = tree.item(selected_item, "values")[1]

                def undo_return():
                    def undo():
                        with self.book_manager.create_db_connection() as mydb:
                            with mydb.cursor() as cursor:
                                cursor.execute(
                                    "UPDATE qr_borrow_log SET return_date = NULL WHERE book_number = %s AND student_id = %s",
                                    (book_number, student_id)
                                )
                                cursor.execute("UPDATE books SET available = FALSE WHERE book_number = %s", (book_number,))
                                cursor.execute(
                                    "INSERT INTO borrowed_books_student (student_id, book_number, borrowed_on) VALUES (%s, %s, %s)",
                                    (student_id, book_number, datetime.date.today())
                                )
                                mydb.commit()
                        return lambda: self.book_manager.return_book()  # Redo action
                    return undo

                if messagebox.askyesno("Confirm Return", f"Return book {book_number} for student {student_id}?", parent=view_window):
                    result, _, _ = self.book_manager.return_book()  # Simulate scanning by directly calling return_book
                    if "Error" not in result:
                        self.undo_stack.append(undo_return())
                        self.redo_stack.clear()
                        self._update_feedback(f"Book {book_number} returned successfully by Student ID: {student_id}")
                        refresh_data()  # Refresh the list after returning
                    else:
                        self._update_feedback(result)
                        messagebox.showerror("Return Error", result, parent=view_window)

             # Add buttons to the action frame
            ttk.Button(action_frame, text="Print", command=print_unreturned_books).pack(side="left", padx=5, pady=5)
            ttk.Button(action_frame, text="Notify Overdue", command=notify_overdue, style="Action.TButton").pack(side="left", padx=5, pady=5)
            ttk.Button(action_frame, text="Return Selected", command=return_selected_book, style="Action.TButton").pack(side="left", padx=5, pady=5)
            ttk.Button(action_frame, text="Refresh", command=refresh_data, style="Action.TButton").pack(side="left", padx=5, pady=5)
            self._add_export_buttons(
                action_frame,
                export_data,
                ["Book ID", "Student ID", "Student Name", "Borrow Date", "Stream", "Days Overdue"],
                "unreturned_books",
                "Unreturned Books",
                f"Total Unreturned Books: {len(export_data)}"
            )
            ttk.Button(action_frame, text="Close", command=view_window.destroy, style="Action.TButton").pack(side="left", padx=5, pady=5)

            refresh_data()
            self.update_dashboard()  # Update dashboard with this action

        except tk.TclError as tcl_err:
            self._update_feedback(f"GUI Error: Failed to display unreturned books - {tcl_err}")
            messagebox.showerror("GUI Error", f"Failed to display unreturned books: {tcl_err}")
        except Exception as e:
            self._update_feedback(f"Unexpected Error: {e}")
            messagebox.showerror("Error", f"An unexpected error occurred: {e}")



    def generate_qr_action(self):
        """Handles generating a QR code for a book with advanced features."""
        try:
            # Create a dialog window for QR code generation
            qr_window = tk.Toplevel(self)
            qr_window.title("Generate QR Code")
            qr_window.geometry("500x600")
            qr_window.configure(bg="#f0f0f0")

            # Format selection
            ttk.Label(qr_window, text="Select QR Format:").pack(pady=5)
            format_var = tk.StringVar(value="Simple")
            format_menu = ttk.OptionMenu(qr_window, format_var, "Simple", "Simple", "Original")
            format_menu.pack(pady=5)

            # Input fields frame
            input_frame = ttk.LabelFrame(qr_window, text="Book Details", padding="5")
            input_frame.pack(fill="x", padx=10, pady=5)

            # Simple format inputs
            simple_frame = ttk.Frame(input_frame)
            ttk.Label(simple_frame, text="Book ID:").pack(anchor="w")
            book_number_entry = ttk.Entry(simple_frame)
            book_number_entry.pack(fill="x", pady=5)

            # Original format inputs
            original_frame = ttk.Frame(input_frame)
            ttk.Label(original_frame, text="Class (e.g., A1):").pack(anchor="w")
            class_entry = ttk.Entry(original_frame)
            class_entry.pack(fill="x", pady=2)
            ttk.Label(original_frame, text="Subject:").pack(anchor="w")
            subject_entry = ttk.Entry(original_frame)
            subject_entry.pack(fill="x", pady=2)
            ttk.Label(original_frame, text="Form (1-12):").pack(anchor="w")
            form_entry = ttk.Entry(original_frame)
            form_entry.pack(fill="x", pady=2)
            ttk.Label(original_frame, text="Number of Books:").pack(anchor="w")
            num_books_entry = ttk.Entry(original_frame)
            num_books_entry.pack(fill="x", pady=2)
            ttk.Label(original_frame, text=f"Year (1900-{datetime.datetime.now().year}):").pack(anchor="w")
            year_entry = ttk.Entry(original_frame)
            year_entry.pack(fill="x", pady=2)

            # Toggle visibility of input fields based on format
            def toggle_inputs(*args):
                if format_var.get() == "Simple":
                    simple_frame.pack(fill="x", pady=5)
                    original_frame.pack_forget()
                else:
                    simple_frame.pack_forget()
                    original_frame.pack(fill="x", pady=5)

            format_var.trace("w", toggle_inputs)
            toggle_inputs()  # Initial toggle

            # Preview frame
            preview_frame = ttk.LabelFrame(qr_window, text="QR Code Preview", padding="5")
            preview_frame.pack(fill="both", expand=True, padx=10, pady=5)
            preview_label = ttk.Label(preview_frame, text="No QR code generated yet.")
            preview_label.pack(expand=True)

            # Action buttons
            action_frame = ttk.Frame(qr_window)
            action_frame.pack(fill="x", pady=5)

            generated_file = [None]  # To store the path of the generated QR code file

            def generate_and_preview():
                """Generates the QR code and displays a preview."""
                try:
                    if format_var.get() == "Simple":
                        book_number = book_number_entry.get().strip()
                        if not book_number or not (MIN_book_number_LENGTH <= len(book_number) <= MAX_book_number_LENGTH and book_number.replace('-', '').isalnum()):
                            self._update_feedback(f"Invalid Book ID: Must be {MIN_book_number_LENGTH}-{MAX_book_number_LENGTH} alphanumeric characters.")
                            messagebox.showerror("Input Error", f"Book ID must be {MIN_book_number_LENGTH}-{MAX_book_number_LENGTH} alphanumeric characters.", parent=qr_window)
                            return
                        book_details = {"Format": "Simple", "ID": book_number}
                    else:
                        class_name = class_entry.get().strip()
                        subject = subject_entry.get().strip()
                        form = form_entry.get().strip()
                        num_books = num_books_entry.get().strip()
                        year = year_entry.get().strip()

                        # Validate inputs
                        if not all([class_name, subject, form, num_books, year]):
                            self._update_feedback("QR generation cancelled: Missing required fields.")
                            messagebox.showerror("Input Error", "All fields are required.", parent=qr_window)
                            return
                        if not class_name.isalnum() or len(class_name) > 20:
                            self._update_feedback("Invalid Class: Must be alphanumeric and <= 20 characters.")
                            messagebox.showerror("Input Error", "Class must be alphanumeric and <= 20 characters.", parent=qr_window)
                            return
                        if len(subject) > 50:
                            self._update_feedback("Invalid Subject: Must be <= 50 characters.")
                            messagebox.showerror("Input Error", "Subject must be <= 50 characters.", parent=qr_window)
                            return
                        try:
                            form_val = int(form)
                            if not (1 <= form_val <= 12):
                                self._update_feedback("Invalid Form: Must be between 1 and 12.")
                                messagebox.showerror("Input Error", "Form must be between 1 and 12.", parent=qr_window)
                                return
                        except ValueError:
                            self._update_feedback("Invalid Form: Must be a number.")
                            messagebox.showerror("Input Error", "Form must be a number.", parent=qr_window)
                            return
                        try:
                            num_books_val = int(num_books)
                            if num_books_val <= 0:
                                self._update_feedback("Invalid Number of Books: Must be positive.")
                                messagebox.showerror("Input Error", "Number of Books must be positive.", parent=qr_window)
                                return
                        except ValueError:
                            self._update_feedback("Invalid Number of Books: Must be a number.")
                            messagebox.showerror("Input Error", "Number of Books must be a number.", parent=qr_window)
                            return
                        try:
                            year_val = int(year)
                            current_year = datetime.datetime.now().year
                            if not (1900 <= year_val <= current_year):
                                self._update_feedback(f"Invalid Year: Must be between 1900 and {current_year}.")
                                messagebox.showerror("Input Error", f"Year must be between 1900 and {current_year}.", parent=qr_window)
                                return
                        except ValueError:
                            self._update_feedback("Invalid Year: Must be a number.")
                            messagebox.showerror("Input Error", "Year must be a number.", parent=qr_window)
                            return

                        book_details = {
                            "Class": class_name,
                            "Subject": subject,
                            "Form": str(form_val),
                            "Numberofbooks": str(num_books_val),
                            "Year": str(year_val)
                        }

                    # Generate the QR code
                    result = self.book_manager.generate_qr_code(book_details)
                    if "Error" in result:
                        self._update_feedback(result)
                        messagebox.showerror("QR Error", result, parent=qr_window)
                        return

                    generated_file[0] = result.split("'")[1]  # Extract the filename from the result message
                    self._update_feedback(result)

                    # Display the QR code preview
                    qr_image = Image.open(generated_file[0])
                    qr_image = qr_image.resize((200, 200), Image.Resampling.LANCZOS)  # Resize for preview
                    qr_photo = tk.PhotoImage(image=qr_image)
                    preview_label.configure(image=qr_photo)
                    preview_label.image = qr_photo  # Keep a reference to avoid garbage collection

                    # Add to undo stack
                    def undo_generate():
                        def undo():
                            if os.path.exists(generated_file[0]):
                                os.remove(generated_file[0])
                                self._update_feedback(f"QR code file {generated_file[0]} deleted (undo).")
                            return lambda: self.book_manager.generate_qr_code(book_details)  # Redo action
                        return undo

                    self.undo_stack.append(undo_generate())
                    self.redo_stack.clear()

                except Exception as e:
                    self._update_feedback(f"Error generating QR code: {e}")
                    messagebox.showerror("Generation Error", f"Failed to generate QR code: {e}", parent=qr_window)

            def save_as():
                """Saves the generated QR code to a custom location."""
                if not generated_file[0]:
                    self._update_feedback("No QR code generated to save.")
                    messagebox.showwarning("Save Error", "Please generate a QR code first.", parent=qr_window)
                    return

                file_path = filedialog.asksaveasfilename(
                    title="Save QR Code As",
                    defaultextension=".png",
                    filetypes=[("PNG files", "*.png"), ("All files", "*.*")],
                    initialfile=os.path.basename(generated_file[0])
                )
                if file_path:
                    try:
                        import shutil
                        shutil.copy(generated_file[0], file_path)
                        self._update_feedback(f"QR code saved to {file_path}")
                        messagebox.showinfo("Save Success", f"QR code saved to '{file_path}'", parent=qr_window)
                    except Exception as e:
                        self._update_feedback(f"Error saving QR code: {e}")
                        messagebox.showerror("Save Error", f"Failed to save QR code: {e}", parent=qr_window)

            def upload_to_cloud():
                """Simulates uploading the QR code to a cloud service (AWS S3)."""
                if not generated_file[0]:
                    self._update_feedback("No QR code generated to upload.")
                    messagebox.showwarning("Upload Error", "Please generate a QR code first.", parent=qr_window)
                    return

                try:
                    # Placeholder for AWS S3 upload (requires boto3 and AWS credentials)
                    # import boto3
                    # s3 = boto3.client('s3', aws_access_key_id='YOUR_KEY', aws_secret_access_key='YOUR_SECRET')
                    # s3.upload_file(generated_file[0], 'your-bucket-name', os.path.basename(generated_file[0]))
                    self._update_feedback(f"Simulated upload of {generated_file[0]} to AWS S3.")
                    messagebox.showinfo("Upload Success", f"QR code uploaded to cloud (simulated).", parent=qr_window)
                except Exception as e:
                    self._update_feedback(f"Error uploading QR code to cloud: {e}")
                    messagebox.showerror("Upload Error", f"Failed to upload QR code: {e}", parent=qr_window)

            # Add action buttons
            ttk.Button(action_frame, text="Generate & Preview", command=generate_and_preview, style="Action.TButton").pack(side="left", padx=5, pady=5)
            ttk.Button(action_frame, text="Save As", command=save_as).pack(side="left", padx=5, pady=5)
            ttk.Button(action_frame, text="Upload to Cloud", command=upload_to_cloud).pack(side="left", padx=5, pady=5)
            ttk.Button(action_frame, text="Close", command=qr_window.destroy, style="Action.TButton").pack(side="left", padx=5, pady=5)

            self.update_dashboard()  # Update dashboard with this action

        except tk.TclError as tcl_err:
            self._update_feedback(f"GUI Error: Failed to generate QR code - {tcl_err}")
            messagebox.showerror("GUI Error", f"Failed to generate QR code: {tcl_err}")
        except Exception as e:
            self._update_feedback(f"Unexpected Error: {e}")
            messagebox.showerror("Error", f"An unexpected error occurred: {e}")


    def check_overdue_books(self):
        """Checks and displays overdue books."""
        try:
            view_window = tk.Toplevel(self)
            view_window.title("Overdue Books")
            view_window.geometry("800x500")
            view_window.configure(bg="#f0f0f0")

            total_frame = ttk.LabelFrame(view_window, text="Summary", padding="5")
            total_frame.pack(fill="x", padx=10, pady=5)
            total_label = ttk.Label(total_frame, text="Total Overdue Books: ...")
            total_label.pack(anchor="w")

            books_frame = ttk.LabelFrame(view_window, text="Overdue Books (Sorted by Days Overdue)", padding="5")
            books_frame.pack(fill="both", expand=True, padx=10, pady=5)

            tree = ttk.Treeview(
                books_frame,
                columns=("Book ID", "Student ID", "Student Name", "Borrow Date", "Stream", "Days Overdue"),
                show="headings",
                height=10
            )
            tree.heading("Book ID", text="Book ID")
            tree.heading("Student ID", text="Student ID")
            tree.heading("Student Name", text="Student Name")
            tree.heading("Borrow Date", text="Borrow Date")
            tree.heading("Stream", text="Stream")
            tree.heading("Days Overdue", text="Days Overdue")
            tree.column("Book ID", width=150, anchor="center")
            tree.column("Student ID", width=150, anchor="center")
            tree.column("Student Name", width=200, anchor="center")
            tree.column("Borrow Date", width=150, anchor="center")
            tree.column("Stream", width=100, anchor="center")
            tree.column("Days Overdue", width=100, anchor="center")

            scrollbar = ttk.Scrollbar(books_frame, orient="vertical", command=tree.yview)
            tree.configure(yscroll=scrollbar.set)
            tree.pack(side="left", fill="both", expand=True)
            scrollbar.pack(side="right", fill="y")

            def refresh_data():
                self._fetch_data_async(
                    self.book_manager.search_unreturned_books,  # Reuse the same method to get unreturned books
                    lambda data: process_data(data),
                    "No overdue books found or error loading data."
                )

            def process_data(unreturned_data):
                # Filter for overdue books (e.g., more than 14 days)
                overdue_books = []
                for book in unreturned_data:
                    borrow_date = datetime.datetime.strptime(book['borrow_date'], "%Y-%m-%d %H:%M:%S")
                    days_overdue = (datetime.datetime.now() - borrow_date).days
                    if days_overdue > 14:  # Assuming 14 days is the overdue threshold
                        book['days_overdue'] = days_overdue
                        overdue_books.append(book)

                total_label.config(text=f"Total Overdue Books: {len(overdue_books)}")
                export_data.clear()
                tree.delete(*tree.get_children())  # Clear existing entries
                for book in overdue_books:
                    export_data.append({
                        "Book ID": book['book_number'],
                        "Student ID": book['student_id'],
                        "Student Name": book['student_name'],
                        "Borrow Date": book['borrow_date'],
                        "Stream": book['stream'],
                        "Days Overdue": str(book['days_overdue'])
                    })
                    tree.insert("", tk.END, values=(
                        book['book_number'],
                        book['student_id'],
                        book['student_name'],
                        book['borrow_date'],
                        book['stream'],
                        str(book['days_overdue'])
                    ))
                self.queue.put({"action": "update_treeview", "tree": tree, "data": export_data, "page": 1, "total_pages": (len(export_data) + PAGE_SIZE - 1) // PAGE_SIZE})
                self._update_feedback(f"Loaded {len(overdue_books)} overdue book(s)")

            export_data = []
            filter_var, filter_entry = self._add_sort_and_filter(
                books_frame, tree, export_data, ["Book ID", "Student ID", "Student Name", "Borrow Date", "Stream", "Days Overdue"]
            )
            self._add_pagination_controls(books_frame, tree, export_data, total_label)

            def print_overdue_books():
                try:
                    filename = f"overdue_books_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
                    with open(filename, "w") as file:
                        file.write(f"Overdue Books - {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                        file.write(f"Total Overdue Books: {len(export_data)}\n\n")
                        file.write("Overdue Books (Sorted by Days Overdue):\n")
                        for book in export_data:
                            file.write(f"  Book ID: {book['Book ID']}\n")
                            file.write(f"    Student ID: {book['Student ID']}\n")
                            file.write(f"    Student Name: {book['Student Name']}\n")
                            file.write(f"    Borrow Date: {book['Borrow Date']}\n")
                            file.write(f"    Stream: {book['Stream']}\n")
                            file.write(f"    Days Overdue: {book['Days Overdue']}\n")
                            file.write("\n")
                    self._update_feedback(f"Overdue books printed to {filename}")
                    messagebox.showinfo("Print Success", f"Overdue books saved to '{filename}'", parent=view_window)
                except FileNotFoundError as fnf_err:
                    self._update_feedback(f"File Error: Failed to access file system - {fnf_err}")
                    messagebox.showerror("Print Error", f"Failed to print: {fnf_err}", parent=view_window)

            action_frame = ttk.Frame(books_frame)
            action_frame.pack(fill="x", pady=5)

            ttk.Button(action_frame, text="Print", command=print_overdue_books).pack(side="left", padx=5, pady=5)
            ttk.Button(action_frame, text="Refresh", command=refresh_data, style="Action.TButton").pack(side="left", padx=5, pady=5)
            self._add_export_buttons(
                action_frame,
                export_data,
                ["Book ID", "Student ID", "Student Name", "Borrow Date", "Stream", "Days Overdue"],
                "overdue_books",
                "Overdue Books",
                f"Total Overdue Books: {len(export_data)}"
            )
            ttk.Button(action_frame, text="Close", command=view_window.destroy, style="Action.TButton").pack(side="left", padx=5, pady=5)

            refresh_data()
            self.update_dashboard()  # Update dashboard with this action

        except tk.TclError as tcl_err:
            self._update_feedback(f"GUI Error: Failed to display overdue books - {tcl_err}")
            messagebox.showerror("GUI Error", f"Failed to display overdue books: {tcl_err}")
        except Exception as e:
            self._update_feedback(f"Unexpected Error: {e}")
            messagebox.showerror("Error", f"An unexpected error occurred: {e}")



    def backup_database_action(self):
        """Back up the SQLite database to a SQL file and optionally simulate cloud upload."""
        self.logger.debug("Attempting to initiate database backup")
        try:
            # Prompt user to select a save location
            backup_file = filedialog.asksaveasfilename(
                title="Save Database Backup",
                defaultextension=".sql",
                filetypes=[("SQL files", "*.sql"), ("All files", "*.*")],
                initialfile=f"library_backup_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.sql"
            )
            if not backup_file:
                self.logger.info("Backup cancelled: No file selected")
                self._update_feedback("Backup cancelled: No file selected.")
                return

            # Establish database connection
            conn = self.db_manager._create_connection()
            if not conn:
                self.logger.error("Backup failed: No database connection available")
                self._update_feedback("Backup failed: No database connection available.")
                messagebox.showerror("Backup Error", "No database connection available.", parent=self)
                return

            self.logger.debug("Database connection established for backup")

            try:
                cursor = conn.cursor()

                # SQLite doesn’t support "SELECT DATABASE()", so use the file name or a fixed DB name
                db_name = os.path.basename(self.db_manager.db_path) if hasattr(self.db_manager, 'db_path') else "library_db"
                self.logger.debug(f"Backing up database: {db_name}")

                # Open the backup file
                with open(backup_file, "w", encoding="utf-8") as f:
                    # Write header
                    f.write(f"-- SQLite Database Backup for {db_name}\n")
                    f.write(f"-- Generated on {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
                    f.write("PRAGMA foreign_keys=OFF;\n\n")

                    # Get list of all tables
                    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%'")
                    tables = [row[0] for row in cursor.fetchall()]

                    for table_name in tables:
                        self.logger.debug(f"Backing up table: {table_name}")
                        self._update_feedback(f"Backing up table: {table_name}")

                        # Get the CREATE TABLE statement
                        cursor.execute(f"SELECT sql FROM sqlite_master WHERE type='table' AND name=?", (table_name,))
                        create_table_stmt = cursor.fetchone()[0]
                        f.write(f"-- Table structure for {table_name}\n")
                        f.write(f"{create_table_stmt};\n\n")

                        # Get the data from the table
                        cursor.execute(f"SELECT * FROM {table_name}")
                        rows = cursor.fetchall()
                        if rows:
                            f.write(f"-- Data for {table_name}\n")
                            # Get column names
                            cursor.execute(f"PRAGMA table_info({table_name})")
                            columns = [col[1] for col in cursor.fetchall()]
                            # Generate INSERT statements
                            for row in rows:
                                values = []
                                for val in row:
                                    if val is None:
                                        values.append("NULL")
                                    elif isinstance(val, (int, float)):
                                        values.append(str(val))
                                    elif isinstance(val, bytes):
                                        values.append(f"X'{val.hex()}'")
                                    else:
                                        # SQLite escaping: double single quotes
                                        escaped_val = str(val).replace("'", "''")
                                        values.append(f"'{escaped_val}'")
                                values_str = ", ".join(values)
                                f.write(f"INSERT INTO \"{table_name}\" (\"{', '.join(columns)}\") VALUES ({values_str});\n")
                            f.write("\n")

                    f.write("PRAGMA foreign_keys=ON;\n")

                self.logger.info(f"Database backed up successfully to {backup_file}")
                self._update_feedback(f"Database backed up successfully to {backup_file}")

                # Add to undo stack
                def undo_backup():
                    def undo():
                        if os.path.exists(backup_file):
                            os.remove(backup_file)
                            self.logger.info(f"Backup file {backup_file} deleted (undo)")
                            self._update_feedback(f"Backup file {backup_file} deleted (undo).")
                        return lambda: self.backup_database_action()  # Redo action
                    return undo

                self.undo_stack.append(undo_backup())
                self.redo_stack.clear()

                # Optional cloud upload (simulated)
                if messagebox.askyesno("Cloud Upload", "Would you like to upload the backup to the cloud?", parent=self):
                    try:
                        # Placeholder for AWS S3 upload (requires boto3)
                        self.logger.info(f"Simulated upload of {backup_file} to AWS S3")
                        self._update_feedback(f"Simulated upload of {backup_file} to AWS S3.")
                        messagebox.showinfo("Upload Success", "Backup uploaded to cloud (simulated).", parent=self)
                    except Exception as e:
                        self.logger.error(f"Error uploading backup to cloud: {e}")
                        self._update_feedback(f"Error uploading backup to cloud: {e}")
                        messagebox.showerror("Upload Error", f"Failed to upload backup: {e}", parent=self)

                messagebox.showinfo("Backup Success", f"Database backed up to '{backup_file}'", parent=self)
                self.update_dashboard()

            except SQLiteError as db_err:
                self.logger.error(f"Database error during backup: {db_err}")
                self._update_feedback(f"Database error: {db_err}")
                messagebox.showerror("Backup Error", f"Database error: {db_err}", parent=self)
            finally:
                self.db_manager._close_connection(conn)

        except tk.TclError as tcl_err:
            self.logger.error(f"GUI Error: Failed to perform backup - {tcl_err}")
            self._update_feedback(f"GUI Error: Failed to perform backup - {tcl_err}")
            messagebox.showerror("GUI Error", f"Failed to perform backup: {tcl_err}", parent=self)
        except Exception as e:
            self.logger.error(f"Unexpected Error during backup: {e}")
            self._update_feedback(f"Unexpected Error: {e}")
            messagebox.showerror("Error", f"An unexpected error occurred: {e}", parent=self)


    def schedule_unreturned_report(self):
        """Schedules a periodic task to generate unreturned books reports."""
        self.logger.debug("Setting up scheduled task for unreturned books report")
        try:
            def generate_report():
                """Generates a report of unreturned books and saves it to a file."""
                try:
                    self.logger.debug("Generating unreturned books report")
                    unreturned_data = self.book_manager.search_unreturned_books()
                    if not unreturned_data:
                        self.logger.info("No unreturned books found for report")
                        self._update_feedback("Scheduled Report: No unreturned books found.")
                        return

                    # Generate a report file
                    report_file = f"unreturned_books_report_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
                    with open(report_file, "w", encoding="utf-8") as f:
                        f.write(f"Unreturned Books Report - {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                        f.write(f"Total Unreturned Books: {len(unreturned_data)}\n\n")
                        for book in unreturned_data:
                            f.write(f"Book ID: {book['book_number']}\n")
                            f.write(f"  Student ID: {book['student_id']}\n")
                            f.write(f"  Student Name: {book['student_name']}\n")
                            f.write(f"  Borrow Date: {book['borrow_date']}\n")
                            f.write(f"  Stream: {book['stream']}\n")
                            f.write("\n")

                    self.logger.info(f"Unreturned books report generated: {report_file}")
                    self._update_feedback(f"Scheduled Report: Unreturned books report saved to {report_file}")

                    # Optionally send email notification (if configured)
                    if hasattr(self, 'smtp_config') and self.smtp_config:
                        try:
                            import smtplib
                            from email.mime.text import MIMEText
                            from email.mime.multipart import MIMEMultipart

                            msg = MIMEMultipart()
                            msg['From'] = self.smtp_config['email']
                            msg['To'] = self.smtp_config['recipient']
                            msg['Subject'] = "Unreturned Books Report"
                            body = f"Unreturned books report generated on {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}.\n"
                            body += f"Total unreturned books: {len(unreturned_data)}\n"
                            body += f"Report saved to: {report_file}\n\n"
                            body += "See attached report for details."
                            msg.attach(MIMEText(body, 'plain'))

                            # Attach the report file
                            with open(report_file, "rb") as attachment:
                                part = MIMEText(attachment.read(), 'plain', 'utf-8')
                                part.add_header('Content-Disposition', f'attachment; filename={report_file}')
                                msg.attach(part)

                            with smtplib.SMTP(self.smtp_config['server'], self.smtp_config['port']) as server:
                                server.starttls()
                                server.login(self.smtp_config['email'], self.smtp_config['password'])
                                server.sendmail(self.smtp_config['email'], self.smtp_config['recipient'], msg.as_string())

                            self.logger.info("Unreturned books report emailed successfully")
                            self._update_feedback("Scheduled Report: Unreturned books report emailed successfully")
                        except Exception as e:
                            self.logger.error(f"Failed to send unreturned books report email: {e}")
                            self._update_feedback(f"Scheduled Report: Failed to send email - {e}")

                except Exception as e:
                    self.logger.error(f"Error generating unreturned books report: {e}")
                    self._update_feedback(f"Scheduled Report: Error generating report - {e}")

            # Schedule the report to run daily at a specific time (e.g., 8:00 AM)
            schedule.every().day.at("08:00").do(generate_report)
            self.logger.info("Scheduled unreturned books report to run daily at 08:00")

            # Start the scheduler in a separate thread to avoid blocking the GUI
            def run_scheduler():
                while True:
                    schedule.run_pending()
                    time.sleep(60)  # Check every minute

            scheduler_thread = threading.Thread(target=run_scheduler, daemon=True)
            scheduler_thread.start()
            self.logger.debug("Scheduler thread started for unreturned books report")

        except Exception as e:
            self.logger.error(f"Error scheduling unreturned books report: {e}")
            self._update_feedback(f"Scheduled Report: Error setting up schedule - {e}")
            messagebox.showerror("Scheduler Error", f"Failed to schedule unreturned books report: {e}")


    def update_dashboard(self):
        """Updates the dashboard with library statistics."""
        self.logger.debug("Updating dashboard")
        try:
            # Fetch statistics from book_manager (replace with actual queries)
            total_books = self.book_manager.get_total_books()  # Placeholder method
            borrowed_books = self.book_manager.get_borrowed_books_count()  # Placeholder method
            overdue_books = self.book_manager.get_overdue_books_count()  # Placeholder method

            # If the dashboard frame doesn't exist, create it
            if not hasattr(self, 'dashboard_frame'):
                self.dashboard_frame = ttk.LabelFrame(self, text="Dashboard", padding="5")
                self.dashboard_frame.pack(fill="x", padx=10, pady=5)

                # Create labels for statistics
                self.total_books_label = ttk.Label(self.dashboard_frame, text="Total Books: 0")
                self.total_books_label.pack(anchor="w")
                self.borrowed_books_label = ttk.Label(self.dashboard_frame, text="Borrowed Books: 0")
                self.borrowed_books_label.pack(anchor="w")
                self.overdue_books_label = ttk.Label(self.dashboard_frame, text="Overdue Books: 0")
                self.overdue_books_label.pack(anchor="w")

            # Update the labels with new data
            self.total_books_label.config(text=f"Total Books: {total_books}")
            self.borrowed_books_label.config(text=f"Borrowed Books: {borrowed_books}")
            self.overdue_books_label.config(text=f"Overdue Books: {overdue_books}")

            self.logger.debug("Dashboard updated successfully")
            self._update_feedback("Dashboard updated with latest statistics.")

        except AttributeError as attr_err:
            self.logger.error(f"Dashboard Error: Missing attribute - {attr_err}")
            self._update_feedback(f"Dashboard Error: Missing attribute - {attr_err}")
            messagebox.showerror("Dashboard Error", f"Failed to update dashboard: {attr_err}")
        except Exception as e:
            self.logger.error(f"Unexpected Error updating dashboard: {e}")
            self._update_feedback(f"Unexpected Error updating dashboard: {e}")
            messagebox.showerror("Dashboard Error", f"An unexpected error occurred: {e}")


    def _update_feedback(self, message):
        """Updates the feedback label with the given message."""
        self.logger.debug(f"Feedback: {message}")
        try:
            if hasattr(self, 'feedback_label') and self.feedback_label:
                self.feedback_label.config(text=message)
            else:
                self.logger.warning("Feedback label not initialized")
        except tk.TclError as tcl_err:
            self.logger.error(f"GUI Error in feedback update: {tcl_err}")

