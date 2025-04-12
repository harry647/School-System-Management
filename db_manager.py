import sqlite3
from sqlite3 import Error as SQLiteError
import logging
from datetime import date, datetime
import re
import openpyxl
from tkinter import messagebox
from db_utils import create_db_connection, close_db_connection

class DatabaseManager:
    def __init__(self, conn):
        """Initialize DatabaseManager with a provided connection."""
        self.logger = logging.getLogger('DatabaseManager')
        self.logger.info("Initializing DatabaseManager")
        self.connection = conn
        if not self.connection:
            self.logger.error("No valid connection provided")
            raise RuntimeError("Database connection is required")
    
        self.logger.info("DatabaseManager initialized with connection")

    def _create_connection(self):
        """Reuse or create a persistent database connection."""
        if self.connection is None:
            self.logger.warning("Connection is None, attempting to recreate")
            self.connection = create_db_connection()  # From db_utils.py
            if not self.connection:
                self.logger.error("Failed to recreate connection")
                return None
            self.logger.info("New database connection created successfully")
        try:
            # Test the connection to ensure it’s alive
            self.connection.execute("SELECT 1")
            return self.connection
        except SQLiteError as e:
            self.logger.error(f"Connection is invalid: {e}, attempting to recreate")
            self.connection = create_db_connection()
            if not self.connection:
                self.logger.error("Failed to recreate connection after error")
                return None
            return self.connection

    def _close_connection(self, conn):
        """Close a specific connection only if it’s not the persistent one."""
        if conn and conn != self.connection:
            conn.close()
            self.logger.debug("Temporary connection closed")
        


    def load_users(self):
        """Load all users from the database."""
        users = {}
        conn = self._create_connection()
        if not conn:
            return users

        cursor = conn.cursor()
        try:
            cursor.execute("SELECT username, password, role FROM users")
            for username, password, role in cursor.fetchall():
                users[username] = {"password": password, "role": role}
        except SQLiteError as e:
            messagebox.showerror("Database Error", f"Error loading users: {e}")
        finally:
            cursor.close()
        return users

    def load_password(self):
        """Load the admin password from the database."""
        conn = self._create_connection()
        if not conn:
            return None

        cursor = conn.cursor()
        try:
            cursor.execute("SELECT password FROM users WHERE username = 'admin'")
            result = cursor.fetchone()
            return result[0] if result else None
        except SQLiteError as e:
            messagebox.showerror("Database Error", f"Error loading password: {e}")
            return None
        finally:
            cursor.close()


    def save_password(self, password):  
        """Save a password for the admin user."""
        conn = self._create_connection()
        if not conn:
            return

        cursor = conn.cursor()
        try:
            cursor.execute("INSERT OR REPLACE INTO users (username, password, role) VALUES ('admin', ?, 'administrator')", (password,))
            conn.commit()
        except SQLiteError as e:
            messagebox.showerror("Database Error", f"Error saving password: {e}")
        finally:
            cursor.close()

    def load_teachers(self):
        """Load all teachers from the database."""
        teachers = {}
        conn = self._create_connection()
        if not conn:
            return teachers

        cursor = conn.cursor()
        try:
            cursor.execute("SELECT teacher_id, teacher_name FROM teachers")
            for teacher_id, teacher_name in cursor.fetchall():
                teachers[teacher_id] = {"teacher_name": teacher_name}
        except SQLiteError as e:
            messagebox.showerror("Database Error", f"Error loading teachers: {e}")
        finally:
            cursor.close()
        return teachers

    def save_user(self, username, password, role):
        """Save a new user to the database."""
        conn = self._create_connection()
        if not conn:
            return False

        cursor = conn.cursor()
        try:
            cursor.execute("SELECT username FROM users WHERE username = ?", (username,))
            if cursor.fetchone():
                messagebox.showerror("Error", "Username already exists.")
                return False
            cursor.execute("INSERT INTO users (username, password, role) VALUES (?, ?, ?)", (username, password, role))
            conn.commit()
            return True
        except SQLiteError as e:
            messagebox.showerror("Database Error", f"Error saving user: {e}")
            return False
        finally:
            cursor.close()


    def save_student(self, student_id, name, stream):
        """Save or update a student in the database with mandatory stream."""
        conn = self._create_connection()  
        if not conn:
            return False

        cursor = conn.cursor()
        try:
            # Validate inputs (all are required)
            if not all([student_id, name, stream]):
                self.logger.error("All fields (student_id, name, stream) must be provided.")
                return False

            cursor.execute("""
                INSERT OR REPLACE INTO students (student_id, name, stream)
                VALUES (?, ?, ?)
            """, (student_id, name, stream))
            conn.commit()
            return True
        except SQLiteError as e:
            self.logger.error(f"Error saving student: {e}")  
            messagebox.showerror("Database Error", f"Error saving student: {e}")
            return False
        finally:
            cursor.close()
             

    def save_teacher(self, teacher_id, teacher_name):
        """Save or update a teacher in the database."""
        conn = self._create_connection()
        if not conn:
            return False

        cursor = conn.cursor()
        try:
            cursor.execute("INSERT OR REPLACE INTO teachers (teacher_id, teacher_name) VALUES (?, ?)", (teacher_id, teacher_name))
            conn.commit()
            return True
        except SQLiteError as e:
            messagebox.showerror("Database Error", f"Error saving teacher: {e}")
            return False
        finally:
            cursor.close()

    def save_book(self, book_id, tags=None):
        """Save or update a book in the database with optional tags."""
        conn = self._create_connection()
        if not conn:
            return False

        cursor = conn.cursor()
        try:
            cursor.execute("""
                INSERT OR REPLACE INTO books (book_id, available, book_condition)
                VALUES (?, 1, 'New')
            """, (book_id,))
            if tags:
                for tag in tags:
                    cursor.execute("INSERT OR IGNORE INTO book_tags (book_id, tag) VALUES (?, ?)", (book_id, tag))
            conn.commit()
            return True
        except SQLiteError as e:
            conn.rollback()
            messagebox.showerror("Database Error", f"Error saving book: {e}")
            return False
        finally:
            cursor.close()

    def save_revision_book(self, book_id, tags=None, condition=None):
        """Save or update a revision book in the database."""
        conn = self._create_connection()
        if not conn:
            return False

        cursor = conn.cursor()
        try:
            cursor.execute("INSERT OR REPLACE INTO books (book_id, available, revision, book_condition) VALUES (?, 1, 1, ?)",
                           (book_id, condition or 'New'))
            if tags:
                for tag in tags:
                    cursor.execute("INSERT OR IGNORE INTO book_tags (book_id, tag) VALUES (?, ?)", (book_id, tag.strip()))
            conn.commit()
            return True
        except SQLiteError as e:
            conn.rollback()
            messagebox.showerror("Database Error", f"Error saving revision book: {e}")
            return False
        finally:
            cursor.close()

    def load_books(self):
        """Load all book IDs from the database."""
        conn = self._create_connection()
        if not conn:
            return []

        cursor = conn.cursor()
        try:
            cursor.execute("SELECT book_id FROM books")
            return [row[0] for row in cursor.fetchall()]
        except SQLiteError as e:
            messagebox.showerror("Database Error", f"Error loading books: {e}")
            return []
        finally:
            cursor.close()

    def get_books_by_tags(self, tag_filter=None):
        """Fetch books filtered by a tag."""
        conn = self._create_connection()
        if not conn:
            return []

        cursor = conn.cursor()
        try:
            query = "SELECT DISTINCT book_id FROM books b"
            params = []
            if tag_filter:
                query += " JOIN book_tags bt ON b.book_id = bt.book_id WHERE bt.tag = ?"
                params.append(tag_filter)
            cursor.execute(query, params)
            return [row[0] for row in cursor.fetchall()]
        except SQLiteError as e:
            messagebox.showerror("Database Error", f"Error fetching books by tags: {e}")
            return []
        finally:
            cursor.close()

    def borrow_book_teacher(self, teacher_id, book_id, borrowed_on, condition="New"):
        """Record a book borrowed by a teacher."""
        conn = self._create_connection()
        if not conn:
            return False

        cursor = conn.cursor()
        try:
            cursor.execute("SELECT teacher_id FROM teachers WHERE teacher_id = ?", (teacher_id,))
            if not cursor.fetchone():
                messagebox.showerror("Error", "Teacher ID not found.")
                return False

            cursor.execute("SELECT available FROM books WHERE book_id = ?", (book_id,))
            book_record = cursor.fetchone()
            if book_record and not book_record[0]:
                messagebox.showerror("Error", "Book is currently unavailable.")
                return False

            cursor.execute("INSERT OR REPLACE INTO books (book_id, available, book_condition) VALUES (?, 0, ?)",
                           (book_id, condition))
            cursor.execute("INSERT INTO borrowed_books_teacher (teacher_id, book_id, borrowed_on) VALUES (?, ?, ?)",
                           (teacher_id, book_id, borrowed_on))
            conn.commit()
            return True
        except SQLiteError as e:
            conn.rollback()
            messagebox.showerror("Database Error", f"Error borrowing book: {e}")
            return False
        finally:
            cursor.close()

    def borrow_book_student(self, student_id, book_ids, borrowed_on, reminder_days=None, condition="New"):
        """Record books borrowed by a student."""
        conn = self._create_connection()
        if not conn:
            return False, "Database connection failed."

        cursor = conn.cursor()
        results = {"success": [], "already_borrowed": [], "errors": []}

        try:
            cursor.execute("SELECT student_id FROM students WHERE student_id = ?", (student_id,))
            if not cursor.fetchone():
                return False, "Student ID not found."

            for book_id in book_ids:
                cursor.execute("SELECT available FROM books WHERE book_id = ?", (book_id,))
                book_record = cursor.fetchone()

                if not book_record:
                    cursor.execute("INSERT INTO books (book_id, available, book_condition) VALUES (?, 0, ?)",
                                   (book_id, condition))
                    cursor.execute("INSERT INTO borrowed_books_student (student_id, book_id, borrowed_on, reminder_days) VALUES (?, ?, ?, ?)",
                                   (student_id, book_id, borrowed_on, reminder_days))
                    results["success"].append(book_id)
                elif not book_record[0]:
                    cursor.execute("""
                        SELECT s.student_id, s.name, s.stream
                        FROM students s
                        JOIN borrowed_books_student bbs ON s.student_id = bbs.student_id
                        WHERE bbs.book_id = ?
                    """, (book_id,))
                    borrower = cursor.fetchone()
                    if borrower:
                        results["already_borrowed"].append(f"Book ID '{book_id}' is already borrowed by Student ID: {borrower[0]}, Name: {borrower[1]}, Stream: {borrower[2]}")
                    else:
                        results["errors"].append(f"Book ID '{book_id}' is unavailable, but no borrower found.")
                else:
                    cursor.execute("UPDATE books SET available = 0, book_condition = ? WHERE book_id = ?",
                                   (condition, book_id))
                    cursor.execute("INSERT INTO borrowed_books_student (student_id, book_id, borrowed_on, reminder_days) VALUES (?, ?, ?, ?)",
                                   (student_id, book_id, borrowed_on, reminder_days))
                    results["success"].append(book_id)

            conn.commit()
            error_message = "\n".join(results["errors"]) if results["errors"] else ""
            feedback = "\n".join(
                [f"Successfully borrowed books: {', '.join(results['success'])}"] +
                results["already_borrowed"] +
                ([f"Errors: {error_message}"] if error_message else [])
            )
            return True, feedback or "All books processed successfully."
        except SQLiteError as e:
            conn.rollback()
            return False, f"Error borrowing books: {e}"
        finally:
            cursor.close()

    def return_book_teacher(self, teacher_id, book_id, condition=None):
        """Record the return of a book by a teacher."""
        conn = self._create_connection()
        if not conn:
            return False

        cursor = conn.cursor()
        try:
            cursor.execute("SELECT teacher_id FROM teachers WHERE teacher_id = ?", (teacher_id,))
            if not cursor.fetchone():
                messagebox.showerror("Error", "Teacher ID not found.")
                return False

            cursor.execute("DELETE FROM borrowed_books_teacher WHERE teacher_id = ? AND book_id = ?", (teacher_id, book_id))
            if cursor.rowcount == 0:
                messagebox.showerror("Error", "No borrowing record found for this teacher and book.")
                return False

            params = [1] + ([condition] if condition else []) + [book_id]
            cursor.execute(f"UPDATE books SET available = ?{' , book_condition = ?' if condition else ''} WHERE book_id = ?", params)
            conn.commit()
            return True
        except SQLiteError as e:
            conn.rollback()
            messagebox.showerror("Database Error", f"Error returning book: {e}")
            return False
        finally:
            cursor.close()

    def return_book_student(self, student_id, book_id, condition=None):
        """Record the return of a book by a student."""
        conn = self._create_connection()
        if not conn:
            return False

        cursor = conn.cursor()
        try:
            cursor.execute("DELETE FROM borrowed_books_student WHERE student_id = ? AND book_id = ?", (student_id, book_id))
            if cursor.rowcount == 0:
                messagebox.showerror("Error", "No borrowing record found for this student and book.")
                return False

            params = [1] + ([condition] if condition else []) + [book_id]
            cursor.execute(f"UPDATE books SET available = ?{' , book_condition = ?' if condition else ''} WHERE book_id = ?", params)
            conn.commit()
            return True
        except SQLiteError as e:
            conn.rollback()
            messagebox.showerror("Database Error", f"Error returning book: {e}")
            return False
        finally:
            cursor.close()

    def add_ream(self, student_id, reams_brought):
        """Add a ream entry for a student and update total reams."""
        conn = self._create_connection()
        if not conn:
            self.logger.warning("No database connection for adding reams")
            return False

        cursor = conn.cursor()
        try:
            cursor.execute("SELECT student_id FROM students WHERE student_id = ?", (student_id,))
            if not cursor.fetchone():
                messagebox.showerror("Error", "Student not found!")
                return False

            cursor.execute("INSERT INTO ream_entries (student_id, reams_count, date_added) VALUES (?, ?, DATE('now'))",
                           (student_id, reams_brought))
            cursor.execute("UPDATE total_reams SET total_available = total_available + ? WHERE id = 1", (reams_brought,))
            conn.commit()
            self.logger.info(f"Added {reams_brought} reams for {student_id}")
            return True
        except SQLiteError as e:
            conn.rollback()
            messagebox.showerror("Database Error", f"Error adding reams: {e}")
            return False
        finally:
            cursor.close()

    def deduct_reams(self, used_reams):
        conn = self._create_connection()
        if not conn:
            self.logger.warning("No database connection for ream deduction")
            return False

        cursor = conn.cursor()
        try:
            # Get total from ream_entries (consistent with get_total_reams)
            cursor.execute("SELECT SUM(reams_count) FROM ream_entries")
            total_reams = cursor.fetchone()[0] or 0
            if used_reams > total_reams:
                messagebox.showerror("Error", f"Not enough reams: {total_reams} available, {used_reams} requested.")
                return False

            # Record the deduction in ream_entries (negative entry)
            cursor.execute("INSERT INTO ream_entries (student_id, reams_count, date_added) VALUES (?, ?, ?)",
                           (None, -used_reams, datetime.now().strftime("%Y-%m-%d")))
            # Update total_available to stay in sync
            cursor.execute("UPDATE total_reams SET total_available = MAX(0, total_available - ?) WHERE id = 1", (used_reams,))
            conn.commit()
            self.logger.info(f"Deducted {used_reams} reams")
            return True
        except SQLiteError as e:
            conn.rollback()
            messagebox.showerror("Database Error", f"Error deducting reams: {e}")
            return False
        finally:
            cursor.close()
            

    def get_all_reams(self, student_id_filter=None, date_start=None, date_end=None, min_reams=None, view_mode="detailed"):
        """Fetch ream entries with filters and view mode."""
        conn = self._create_connection()
        if not conn:
            return []

        cursor = conn.cursor()
        try:
            base_query = """
                FROM ream_entries r
                JOIN students s ON r.student_id = s.student_id
                WHERE 1=1
            """
            params = []

            if student_id_filter:
                base_query += " AND r.student_id LIKE ?"
                params.append(f"%{student_id_filter}%")
            if date_start:
                base_query += " AND r.date_added >= ?"
                params.append(date_start)
            if date_end:
                base_query += " AND r.date_added <= ?"
                params.append(date_end)

            if view_mode == "aggregated":
                query = f"""
                    SELECT r.student_id, s.name, SUM(r.reams_count) as total_reams, MAX(r.date_added) as last_added
                    {base_query}
                    GROUP BY r.student_id, s.name
                """
                if min_reams is not None:
                    query += " HAVING total_reams >= ?"
                    params.append(min_reams)
                query += " ORDER BY total_reams DESC, r.student_id ASC"
            else:
                query = f"""
                    SELECT r.student_id, s.name, r.reams_count, r.date_added
                    {base_query}
                """
                if min_reams is not None:
                    query += " AND r.reams_count >= ?"
                    params.append(min_reams)
                query += " ORDER BY r.reams_count DESC, r.student_id ASC"

            cursor.execute(query, params)
            return [(row[0], row[1], row[2], row[3]) for row in cursor.fetchall()]
        except SQLiteError as e:
            messagebox.showerror("Database Error", f"Error fetching reams: {e}")
            return []
        finally:
            cursor.close()

    def get_total_reams(self):
        """Fetch total reams, form-wise reams, streams, and per-student data."""
        conn = self._create_connection()
        if not conn:
            return 0, [], {}, {}, 0

        cursor = conn.cursor()
        try:
            cursor.execute("SELECT SUM(reams_count) FROM ream_entries")
            total_reams = cursor.fetchone()[0] or 0

            cursor.execute("SELECT DISTINCT stream FROM students WHERE stream IS NOT NULL")
            streams = [row[0] for row in cursor.fetchall()]
            form_streams = {f"Form {i}": [] for i in range(1, 5)}
            for stream in streams:
                match = re.match(r"(\d+)", stream)
                if match:
                    form_num = int(match.group(1))
                    if 1 <= form_num <= 4:
                        form_streams[f"Form {form_num}"].append(stream)

            form_reams = {f"Form {i}": 0 for i in range(1, 5)}
            cursor.execute("SELECT s.stream, SUM(r.reams_count) FROM ream_entries r JOIN students s ON r.student_id = s.student_id GROUP BY s.stream")
            for stream, reams in cursor.fetchall():
                match = re.match(r"(\d+)", stream or "")
                if match:
                    form_num = int(match.group(1))
                    if 1 <= form_num <= 4:
                        form_reams[f"Form {form_num}"] += reams or 0

            cursor.execute("SELECT s.student_id, s.name, s.stream, SUM(r.reams_count) FROM ream_entries r JOIN students s ON r.student_id = s.student_id GROUP BY s.student_id, s.name, s.stream ORDER BY s.student_id")
            student_reams = cursor.fetchall()

            form_stream_students = {f"Form {i}": {} for i in range(1, 5)}
            for student_id, name, stream, reams in student_reams:
                match = re.match(r"(\d+)", stream or "")
                if match:
                    form_num = int(match.group(1))
                    if 1 <= form_num <= 4:
                        form_key = f"Form {form_num}"
                        if stream not in form_stream_students[form_key]:
                            form_stream_students[form_key][stream] = []
                        form_stream_students[form_key][stream].append({"student_id": student_id, "name": name, "reams": reams or 0})

            exported_reams = 0  # Placeholder
            return total_reams, student_reams, form_reams, form_stream_students, exported_reams
        except SQLiteError as e:
            messagebox.showerror("Database Error", f"Error fetching total reams: {e}")
            return 0, [], {}, {}, 0
        finally:
            cursor.close()

    def get_student_info(self, student_id, conn=None):
        """Retrieve comprehensive student information."""
        close_conn = False
        if not conn:
            conn = self._create_connection()
            if not conn:
                return None, None, [], 0, None, None
            close_conn = True

        cursor = conn.cursor()
        try:
            cursor.execute("SELECT name, stream FROM students WHERE student_id = ?", (student_id,))
            result = cursor.fetchone()
            if not result:
                return None, None, [], 0, None, None
            name, stream = result

            cursor.execute("SELECT book_id FROM borrowed_books_student WHERE student_id = ?", (student_id,))
            borrowed_books = [row[0] for row in cursor.fetchall()]

            cursor.execute("SELECT SUM(reams_count) FROM ream_entries WHERE student_id = ?", (student_id,))
            reams_count = cursor.fetchone()[0] or 0

            cursor.execute("SELECT locker_id FROM locker_assignments WHERE student_id = ?", (student_id,))
            locker_id = cursor.fetchone()[0] if cursor.rowcount > 0 else None

            cursor.execute("SELECT chair_id FROM chair_assignments WHERE student_id = ?", (student_id,))
            chair_id = cursor.fetchone()[0] if cursor.rowcount > 0 else None

            return name, stream, borrowed_books, reams_count, locker_id, chair_id
        except SQLiteError as e:
            messagebox.showerror("Database Error", f"Error fetching student info: {e}")
            return None, None, [], 0, None, None
        finally:
            if close_conn:
                cursor.close()

    def get_teacher_info(self, teacher_id):
        """Fetch teacher details including borrowed books."""
        conn = self._create_connection()
        if not conn:
            self.logger.error(f"Failed to create connection for teacher_id: {teacher_id}")
            return None, []

        cursor = conn.cursor()
        try:
            # Fetch teacher name
            cursor.execute("SELECT teacher_name FROM teachers WHERE teacher_id = ?", (teacher_id,))
            result = cursor.fetchone()
            if not result:
                self.logger.warning(f"No teacher found with teacher_id: {teacher_id}")
                return None, []
            name = result[0]

            # Fetch borrowed books
            cursor.execute("""
                SELECT b.book_id, b.book_condition
                FROM borrowed_books_teacher bbt
                JOIN books b ON bbt.book_id = b.book_id
                WHERE bbt.teacher_id = ?
            """, (teacher_id,))
            borrowed_books = [(row[0], row[1]) for row in cursor.fetchall()]
            
            self.logger.info(f"Fetched info for teacher {teacher_id}: name={name}, books={borrowed_books}")
            return name, borrowed_books
        except SQLiteError as e:
            self.logger.error(f"Error fetching teacher info for {teacher_id}: {e}")
            return None, []
        finally:
            cursor.close()
            

    def get_unreturned_books(self):
        """Fetch all unreturned books with borrower details."""
        conn = self._create_connection()
        if not conn:
            return {"students": [], "teachers": []}

        cursor = conn.cursor()
        try:
            cursor.execute("""
                SELECT bbs.student_id, s.name AS student_name, s.stream, bbs.book_id, bbs.borrowed_on, b.book_condition
                FROM borrowed_books_student bbs
                JOIN students s ON bbs.student_id = s.student_id
                JOIN books b ON bbs.book_id = b.book_id
                WHERE b.available = 0
                ORDER BY s.stream, bbs.student_id
            """)
            students = [{"student_id": row[0], "student_name": row[1], "stream": row[2], "book_id": row[3], "borrowed_on": row[4], "book_condition": row[5]}
                        for row in cursor.fetchall()]

            cursor.execute("""
                SELECT bbt.teacher_id, t.teacher_name, bbt.book_id, bbt.borrowed_on, b.book_condition
                FROM borrowed_books_teacher bbt
                JOIN teachers t ON bbt.teacher_id = t.teacher_id
                JOIN books b ON bbt.book_id = b.book_id
                WHERE b.available = 0
                ORDER BY t.teacher_id
            """)
            teachers = [{"teacher_id": row[0], "teacher_name": row[1], "book_id": row[2], "borrowed_on": row[3], "book_condition": row[4]}
                        for row in cursor.fetchall()]

            return {"students": students, "teachers": teachers}
        except SQLiteError as e:
            messagebox.showerror("Database Error", f"Error fetching unreturned books: {e}")
            return {"students": [], "teachers": []}
        finally:
            cursor.close()

    def load_books_from_excel(self, book_ids, conditions=None):
        """Load books from a list with optional conditions."""
        conn = self._create_connection()
        if not conn:
            return 0

        cursor = conn.cursor()
        try:
            book_count = 0
            for i, book_id in enumerate(book_ids):
                condition = conditions[i] if conditions and i < len(conditions) else "New"
                if condition not in ["New", "Good", "Damaged"]:
                    condition = "New"
                cursor.execute("INSERT OR REPLACE INTO books (book_id, available, book_condition) VALUES (?, 1, ?)",
                               (book_id, condition))
                book_count += 1
            conn.commit()
            self.logger.info(f"Loaded {book_count} books from Excel")
            return book_count
        except SQLiteError as e:
            conn.rollback()
            messagebox.showerror("Database Error", f"Error loading books from Excel: {e}")
            return 0
        finally:
            cursor.close()

    def bulk_borrow(self, borrowings):
        """Perform bulk borrowing for students or teachers, returning detailed results."""
        results = {"success": [], "already_borrowed": [], "errors": []}
        for user_id, book_id, entity_type, condition in borrowings:
            try:
                if entity_type == "Student":
                    success, _ = self.borrow_book_student(user_id, [book_id], date.today(), None, condition)
                elif entity_type == "Teacher":
                    success = self.borrow_book_teacher(user_id, book_id, date.today(), condition)
                else:
                    results["errors"].append((book_id, f"Invalid entity type for user {user_id}"))
                    continue
                
                if success:
                    results["success"].append(book_id)
                else:
                    # Check if the book is already borrowed
                    conn = self._create_connection()
                    if conn:
                        cursor = conn.cursor()
                        cursor.execute("SELECT COUNT(*) FROM borrowings WHERE book_id = ? AND return_date IS NULL", (book_id,))
                        if cursor.fetchone()[0] > 0:
                            results["already_borrowed"].append(book_id)
                        else:
                            results["errors"].append((book_id, "Borrowing failed (unknown reason)"))
                        cursor.close()
                    else:
                        results["errors"].append((book_id, "Database connection failed"))
            except SQLiteError as e:
                results["errors"].append((book_id, str(e)))

        successes = len(results["success"])
        total_failures = len(results["already_borrowed"]) + len(results["errors"])
        self.logger.info(f"Bulk borrowed {successes} books, {total_failures} failures")
        # Remove inline messagebox to let GUI handle feedback
        return results

    def bulk_return(self, returns):
        """Perform bulk returning for students or teachers."""
        successes, failures = 0, []
        for user_id, book_id, entity_type, condition in returns:
            try:
                if entity_type == "Student":
                    success = self.return_book_student(user_id, book_id, condition)
                elif entity_type == "Teacher":
                    success = self.return_book_teacher(user_id, book_id, condition)
                else:
                    failures.append((user_id, book_id, "Invalid entity type"))
                    continue
                if success:
                    successes += 1
                else:
                    failures.append((user_id, book_id, "Returning failed"))
            except SQLiteError as e:
                failures.append((user_id, book_id, str(e)))
        self.logger.info(f"Bulk returned {successes} books, {len(failures)} failures")
        if failures:
            messagebox.showerror("Bulk Return Error", f"Failed to return {len(failures)} books.")
        return successes, failures

    def get_student_borrowed_revision_books(self, student_id):
        """Fetch revision books borrowed by a student."""
        conn = self._create_connection()
        if not conn:
            return []

        cursor = conn.cursor()
        try:
            cursor.execute("""
                SELECT bbs.book_id, bbs.borrowed_on, bbs.reminder_days
                FROM borrowed_books_student bbs
                JOIN books b ON bbs.book_id = b.book_id
                WHERE bbs.student_id = ? AND b.revision = 1 AND b.available = 0
            """, (student_id,))
            return [(row[0], row[1], row[2]) for row in cursor.fetchall()]
        except SQLiteError as e:
            messagebox.showerror("Database Error", f"Error fetching revision books: {e}")
            return []
        finally:
            cursor.close()

    def get_student_name(self, student_id):
        """Retrieve a student's name."""
        conn = self._create_connection()
        if not conn:
            return None

        cursor = conn.cursor()
        try:
            cursor.execute("SELECT name FROM students WHERE student_id = ?", (student_id,))
            result = cursor.fetchone()
            return result[0] if result else None
        except SQLiteError as e:
            messagebox.showerror("Database Error", f"Error fetching student name: {e}")
            return None
        finally:
            cursor.close()

    def get_revision_books(self):
        """Fetch all revision book IDs."""
        return self.load_revision_books()  # Alias for consistency

    def load_revision_books(self):
        """Load all revision book IDs."""
        conn = self._create_connection()
        if not conn:
            return []

        cursor = conn.cursor()
        try:
            cursor.execute("SELECT book_id FROM books WHERE revision = 1")
            return [row[0] for row in cursor.fetchall()]
        except SQLiteError as e:
            messagebox.showerror("Database Error", f"Error loading revision books: {e}")
            return []
        finally:
            cursor.close()

    def get_revision_books_by_tags(self, tag_filter=None):
        """Fetch revision books filtered by a tag."""
        conn = self._create_connection()
        if not conn:
            return []

        cursor = conn.cursor()
        try:
            query = "SELECT DISTINCT b.book_id FROM books b"
            params = []
            if tag_filter:
                query += " JOIN book_tags bt ON b.book_id = bt.book_id WHERE b.revision = 1 AND bt.tag = ?"
                params.append(tag_filter)
            else:
                query += " WHERE b.revision = 1"
            cursor.execute(query, params)
            return [row[0] for row in cursor.fetchall()]
        except SQLiteError as e:
            messagebox.showerror("Database Error", f"Error fetching revision books by tags: {e}")
            return []
        finally:
            cursor.close()

    def get_students_with_revision_books(self, student_id_filter=None, name_filter=None):
        """Fetch students with borrowed revision books."""
        conn = self._create_connection()
        if not conn:
            return []

        cursor = conn.cursor()
        try:
            query = """
                SELECT s.student_id, s.name, s.stream, bbs.book_id, bbs.borrowed_on, bbs.reminder_days
                FROM borrowed_books_student bbs
                JOIN students s ON bbs.student_id = s.student_id
                JOIN books b ON bbs.book_id = b.book_id
                WHERE b.revision = 1 AND b.available = 0
            """
            params = []
            if student_id_filter:
                query += " AND s.student_id = ?"
                params.append(student_id_filter)
            if name_filter:
                query += " AND s.name LIKE ?"
                params.append(f"%{name_filter}%")
            cursor.execute(query, params)
            return [(row[0], row[1], row[2], row[3], row[4], row[5]) for row in cursor.fetchall()]
        except SQLiteError as e:
            messagebox.showerror("Database Error", f"Error fetching students with revision books: {e}")
            return []
        finally:
            cursor.close()

    def check_overdue_revision_books(self):
        """Check for overdue revision books."""
        conn = self._create_connection()
        if not conn:
            return []

        cursor = conn.cursor()
        try:
            cursor.execute("""
                SELECT s.student_id, s.name, bbs.book_id, bbs.borrowed_on, bbs.reminder_days
                FROM borrowed_books_student bbs
                JOIN students s ON bbs.student_id = s.student_id
                JOIN books b ON bbs.book_id = b.book_id
                WHERE b.revision = 1 AND b.available = 0
                AND DATE(bbs.borrowed_on, '+' || bbs.reminder_days || ' days') < DATE('now')
            """)
            return [(row[0], row[1], row[2], row[3], row[4]) for row in cursor.fetchall()]
        except SQLiteError as e:
            messagebox.showerror("Database Error", f"Error checking overdue books: {e}")
            return []
        finally:
            cursor.close()

    def get_books_by_condition(self, condition_filter=None):
        """Fetch books grouped by condition."""
        books_by_condition = {"New": [], "Good": [], "Damaged": []}
        conn = self._create_connection()
        if not conn:
            return books_by_condition

        cursor = conn.cursor()
        try:
            query = "SELECT book_id, book_condition FROM books WHERE book_condition IN ('New', 'Good', 'Damaged')"
            params = []
            if condition_filter:
                query += " AND book_condition = ?"
                params.append(condition_filter)
            cursor.execute(query, params)
            for book_id, condition in cursor.fetchall():
                books_by_condition[condition].append(book_id)
            return books_by_condition
        except SQLiteError as e:
            messagebox.showerror("Database Error", f"Error fetching books by condition: {e}")
            return books_by_condition
        finally:
            cursor.close()

    def save_reminder_settings(self, user_id, reminder_frequency, sound_enabled):
        """Save or update reminder settings for a user."""
        conn = self._create_connection()
        if not conn:
            return False

        cursor = conn.cursor()
        try:
            cursor.execute("""
                INSERT OR REPLACE INTO settings (user_id, reminder_frequency, sound_enabled)
                VALUES (?, ?, ?)
            """, (user_id, reminder_frequency, 1 if sound_enabled else 0))
            conn.commit()
            self.logger.info(f"Saved reminder settings for {user_id}")
            return True
        except SQLiteError as e:
            conn.rollback()
            messagebox.showerror("Database Error", f"Error saving reminder settings: {e}")
            return False
        finally:
            cursor.close()

    def get_reminder_settings(self, user_id):
        """Fetch reminder settings for a user."""
        conn = self._create_connection()
        if not conn:
            return None, None

        cursor = conn.cursor()
        try:
            cursor.execute("SELECT reminder_frequency, sound_enabled FROM settings WHERE user_id = ?", (user_id,))
            result = cursor.fetchone()
            return (result[0], bool(result[1])) if result else ("daily", True)
        except SQLiteError as e:
            messagebox.showerror("Database Error", f"Error fetching reminder settings: {e}")
            return None, None
        finally:
            cursor.close()

    def export_data(self):
        """Export all library data to a dictionary."""
        conn = self._create_connection()
        if not conn:
            return None

        cursor = conn.cursor()
        try:
            tables = {
                "books": "SELECT book_id, available, book_condition FROM books",
                "users": "SELECT username, password, role FROM users",
                "borrowed_books_student": "SELECT student_id, book_id, borrowed_on, reminder_days FROM borrowed_books_student",
                "borrowed_books_teacher": "SELECT teacher_id, book_id, borrowed_on FROM borrowed_books_teacher",
                "teachers": "SELECT teacher_id, teacher_name FROM teachers",
                "students": "SELECT student_id, name, stream FROM students",
                "ream_entries": "SELECT student_id, reams_count, date_added FROM ream_entries",
                "book_tags": "SELECT book_id, tag FROM book_tags",
                "settings": "SELECT user_id, reminder_frequency, sound_enabled FROM settings",
                "total_reams": "SELECT total_available FROM total_reams LIMIT 1",
                "chairs": "SELECT chair_id, location, form, color, cond, assigned FROM chairs",
                "lockers": "SELECT locker_id, location, form, color, cond, assigned FROM lockers",
                "locker_assignments": "SELECT student_id, locker_id, assigned_date FROM locker_assignments",
                "chair_assignments": "SELECT student_id, chair_id, assigned_date FROM chair_assignments",
                "furniture_categories": "SELECT category_id, category_name, total_count, needs_repair FROM furniture_categories"
            }
            data = {}
            for table, query in tables.items():
                cursor.execute(query)
                rows = [{"book_id": row[0], "available": bool(row[1]), "book_condition": row[2]} if table == "books" else
                        dict(zip([col[0] for col in cursor.description], row)) for row in cursor.fetchall()]
                data[table] = rows
            return data
        except SQLiteError as e:
            self.logger.error(f"Error exporting data: {e}")
            return None
        finally:
            cursor.close()

    def import_data(self, data):
        """Import library data, replacing existing data."""
        conn = self._create_connection()
        if not conn:
            return False

        cursor = conn.cursor()
        try:
            cursor.execute("PRAGMA foreign_keys = OFF")
            for table in data:
                if data[table]:
                    cursor.execute(f"DELETE FROM {table}")
            self._import_data_rows(cursor, data)
            cursor.execute("PRAGMA foreign_keys = ON")
            conn.commit()
            self.logger.info("Data imported successfully")
            return True
        except SQLiteError as e:
            conn.rollback()
            self.logger.error(f"Error importing data: {e}")
            return False
        finally:
            cursor.close()

    def incremental_import_data(self, data):
        """Import library data incrementally, merging with existing data."""
        conn = self._create_connection()
        if not conn:
            return False

        cursor = conn.cursor()
        try:
            cursor.execute("PRAGMA foreign_keys = OFF")
            self._import_data_rows(cursor, data)
            cursor.execute("PRAGMA foreign_keys = ON")
            conn.commit()
            self.logger.info("Data incrementally imported successfully")
            return True
        except SQLiteError as e:
            conn.rollback()
            self.logger.error(f"Error incrementally importing data: {e}")
            return False
        finally:
            cursor.close()

    def _import_data_rows(self, cursor, data):
        """Helper method to import rows into tables."""
        for table, rows in data.items():
            if not rows:
                continue
            if table == "books":
                for row in rows:
                    cursor.execute("INSERT OR REPLACE INTO books (book_id, available, book_condition) VALUES (?, ?, ?)",
                                   (row["book_id"], row.get("available", True), row.get("book_condition", "Good")))
            elif table == "users":
                for row in rows:
                    cursor.execute("INSERT OR REPLACE INTO users (username, password, role) VALUES (?, ?, ?)",
                                   (row["username"], row["password"], row["role"]))
            elif table == "borrowed_books_student":
                for row in rows:
                    cursor.execute("INSERT OR IGNORE INTO borrowed_books_student (student_id, book_id, borrowed_on, reminder_days) VALUES (?, ?, ?, ?)",
                                   (row["student_id"], row["book_id"], row["borrowed_on"], row.get("reminder_days", 0)))
            elif table == "borrowed_books_teacher":
                for row in rows:
                    cursor.execute("INSERT OR IGNORE INTO borrowed_books_teacher (teacher_id, book_id, borrowed_on) VALUES (?, ?, ?)",
                                   (row["teacher_id"], row["book_id"], row["borrowed_on"]))
            elif table == "teachers":
                for row in rows:
                    cursor.execute("INSERT OR REPLACE INTO teachers (teacher_id, teacher_name) VALUES (?, ?)",
                                   (row["teacher_id"], row["teacher_name"]))
            elif table == "students":
                for row in rows:
                    cursor.execute("INSERT OR REPLACE INTO students (student_id, name, stream) VALUES (?, ?, ?)",
                                   (row["student_id"], row["name"], row.get("stream")))
            elif table == "ream_entries":
                for row in rows:
                    cursor.execute("INSERT OR IGNORE INTO ream_entries (student_id, reams_count, date_added) VALUES (?, ?, ?)",
                                   (row["student_id"], row["reams_count"], row["date_added"]))
            elif table == "book_tags":
                for row in rows:
                    cursor.execute("INSERT OR IGNORE INTO book_tags (book_id, tag) VALUES (?, ?)",
                                   (row["book_id"], row["tag"]))
            elif table == "settings":
                for row in rows:
                    cursor.execute("INSERT OR REPLACE INTO settings (user_id, reminder_frequency, sound_enabled) VALUES (?, ?, ?)",
                                   (row["user_id"], row["reminder_frequency"], row["sound_enabled"]))
            elif table == "total_reams":
                total = rows[0]["total_available"] if rows else 0
                cursor.execute("INSERT OR REPLACE INTO total_reams (id, total_available) VALUES (1, ?)", (total,))
            elif table == "chairs":
                for row in rows:
                    cursor.execute("INSERT OR REPLACE INTO chairs (chair_id, location, form, color, cond, assigned) VALUES (?, ?, ?, ?, ?, ?)",
                                   (row["chair_id"], row["location"], row["form"], row["color"], row.get("cond", "Good"), row.get("assigned", 0)))
            elif table == "lockers":
                for row in rows:
                    cursor.execute("INSERT OR REPLACE INTO lockers (locker_id, location, form, color, cond, assigned) VALUES (?, ?, ?, ?, ?, ?)",
                                   (row["locker_id"], row["location"], row["form"], row["color"], row.get("cond", "Good"), row.get("assigned", 0)))
            elif table == "locker_assignments":
                for row in rows:
                    cursor.execute("INSERT OR IGNORE INTO locker_assignments (student_id, locker_id, assigned_date) VALUES (?, ?, ?)",
                                   (row["student_id"], row["locker_id"], row.get("assigned_date", "now")))
            elif table == "chair_assignments":
                for row in rows:
                    cursor.execute("INSERT OR IGNORE INTO chair_assignments (student_id, chair_id, assigned_date) VALUES (?, ?, ?)",
                                   (row["student_id"], row["chair_id"], row.get("assigned_date", "now")))
            elif table == "furniture_categories":
                for row in rows:
                    cursor.execute("INSERT OR REPLACE INTO furniture_categories (category_id, category_name, total_count, needs_repair) VALUES (?, ?, ?, ?)",
                                   (row["category_id"], row["category_name"], row.get("total_count", 0), row.get("needs_repair", 0)))

    def add_short_form_mapping(self, short_form, full_name, mapping_type):
        """Add or update a short form mapping."""
        conn = self._create_connection()
        if not conn:
            return False, "Database connection failed."

        cursor = conn.cursor()
        try:
            cursor.execute("""
                INSERT OR REPLACE INTO short_form_mappings (short_form, full_name, type)
                VALUES (?, ?, ?)
            """, (short_form.lower(), full_name, mapping_type))
            conn.commit()
            return True, "Short form mapping added successfully."
        except SQLiteError as e:
            return False, f"Error adding short form mapping: {e}"
        finally:
            cursor.close()

    def get_short_form_mappings(self):
        """Fetch all short form mappings."""
        conn = self._create_connection()
        if not conn:
            return False, "Database connection failed."

        cursor = conn.cursor()
        try:
            cursor.execute("SELECT short_form, full_name, type FROM short_form_mappings")
            class_mappings = {}
            subject_mappings = {}
            for short_form, full_name, mapping_type in cursor.fetchall():
                if mapping_type == "class":
                    class_mappings[short_form] = full_name
                elif mapping_type == "subject":
                    subject_mappings[short_form] = full_name
            return True, {"class": class_mappings, "subject": subject_mappings}
        except SQLiteError as e:
            return False, f"Error fetching short form mappings: {e}"
        finally:
            cursor.close()


    def close(self):
        """Close the database connection when the application exits."""
        self._close_connection()

    
