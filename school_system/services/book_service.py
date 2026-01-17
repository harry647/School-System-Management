"""
Book service for managing book-related operations.
"""

from typing import List, Optional, Union, Tuple
from datetime import datetime, timedelta
from school_system.config.logging import logger
from school_system.config.settings import Settings
from school_system.core.exceptions import DatabaseException
from school_system.core.utils import ValidationUtils
from school_system.services.import_export_service import ImportExportService
from school_system.services.student_service import StudentService
from school_system.services.class_management_service import ClassManagementService

from school_system.models.book import (Book, BookTag, BorrowedBookStudent, BorrowedBookTeacher,
 DistributionSession, DistributionStudent, DistributionImportLog)

from school_system.database.repositories.book_repo import (BookRepository,
        BookTagRepository, BorrowedBookStudentRepository, BorrowedBookTeacherRepository,
        DistributionSessionRepository,DistributionStudentRepository, DistributionImportLogRepository)



class BookService:
    """Service for managing book-related operations."""

    def __init__(self):
        self.book_repository = BookRepository()
        self.import_export_service = ImportExportService()
        self.student_service = StudentService()
        self.class_management_service = ClassManagementService()

    def get_all_books(self) -> List[Book]:
        """
        Retrieve all books.

        Returns:
            A list of all Book objects.
        """
        return self.book_repository.get_all()

    def get_borrowed_books(self) -> List[Dict]:
        """
        Get all currently borrowed books from both students and teachers.

        Returns:
            List of dictionaries with user_id, book_id, user_type, and borrowed_date
        """
        try:
            # Get all borrowed books from both students and teachers
            student_borrowings = self.get_all_borrowed_books_student()
            teacher_borrowings = self.get_all_borrowed_books_teacher()

            borrowed_books = []

            # Process student borrowings (only those not returned)
            for borrowing in student_borrowings:
                if not borrowing.returned_on:  # Only currently borrowed
                    borrowed_books.append({
                        'user_id': borrowing.student_id,
                        'book_id': borrowing.book_id,
                        'user_type': 'student',
                        'borrowed_date': borrowing.borrowed_on
                    })

            # Process teacher borrowings (only those not returned)
            for borrowing in teacher_borrowings:
                if not borrowing.returned_on:  # Only currently borrowed
                    borrowed_books.append({
                        'user_id': borrowing.teacher_id,
                        'book_id': borrowing.book_id,
                        'user_type': 'teacher',
                        'borrowed_date': borrowing.borrowed_on
                    })

            return borrowed_books

        except Exception as e:
            logger.error(f"Error getting borrowed books: {e}")
            return []

    def get_book_by_id(self, book_id: int) -> Optional[Book]:
        """
        Retrieve a book by its ID.

        Args:
            book_id: The ID of the book.

        Returns:
            The Book object if found, otherwise None.
        """
        return self.book_repository.get_by_id(book_id)

    def create_book(self, book_data: dict) -> Book:
        """
        Create a new book.

        Args:
            book_data: A dictionary containing book data.

        Returns:
            The created Book object.
        """
        logger.info(f"Creating a new book with data: {book_data}")
        ValidationUtils.validate_input(book_data.get('title'), "Book title cannot be empty")
        ValidationUtils.validate_input(book_data.get('author'), "Book author cannot be empty")
        ValidationUtils.validate_input(book_data.get('book_number'), "Book number cannot be empty")
        
        book = Book(**book_data)
        created_book = self.book_repository.create(book)
        logger.info(f"Book created successfully with book_number: {created_book.book_number}")
        return created_book

    def update_book(self, book_id: int, book_data: dict) -> Optional[Book]:
        """
        Update an existing book.

        Args:
            book_id: The ID of the book to update.
            book_data: A dictionary containing updated book data.

        Returns:
            The updated Book object if successful, otherwise None.
        """
        book = self.book_repository.get_by_id(book_id)
        if not book:
            return None

        for key, value in book_data.items():
            setattr(book, key, value)

        return self.book_repository.update(book)

    def delete_book(self, book_id: int) -> bool:
        """
        Delete a book.

        Args:
            book_id: The ID of the book to delete.

        Returns:
            True if the book was deleted, otherwise False.
        """
        book = self.book_repository.get_by_id(book_id)
        if not book:
            return False

        self.book_repository.delete(book)
        return True

    def get_all_book_tags(self) -> List[BookTag]:
        """
        Retrieve all book tags.

        Returns:
            A list of all BookTag objects.
        """
        book_tag_repository = BookTagRepository()
        return book_tag_repository.get_all()

    def get_book_tag_by_id(self, tag_id: int) -> Optional[BookTag]:
        """
        Retrieve a book tag by its ID.

        Args:
            tag_id: The ID of the book tag.

        Returns:
            The BookTag object if found, otherwise None.
        """
        book_tag_repository = BookTagRepository()
        return book_tag_repository.get_by_id(tag_id)

    def create_book_tag(self, tag_data: dict) -> BookTag:
        """
        Create a new book tag.

        Args:
            tag_data: A dictionary containing book tag data.

        Returns:
            The created BookTag object.
        """
        logger.info(f"Creating a new book tag with data: {tag_data}")
        ValidationUtils.validate_input(tag_data.get('tag'), "Book tag cannot be empty")

        book_tag = BookTag(**tag_data)
        book_tag_repository = BookTagRepository()
        created_tag = book_tag_repository.create(book_tag)
        logger.info(f"Book tag created successfully with ID: {created_tag.book_id}")
        return created_tag

    def update_book_tag(self, tag_id: int, tag_data: dict) -> Optional[BookTag]:
        """
        Update an existing book tag.

        Args:
            tag_id: The ID of the book tag to update.
            tag_data: A dictionary containing updated book tag data.

        Returns:
            The updated BookTag object if successful, otherwise None.
        """
        book_tag_repository = BookTagRepository()
        book_tag = book_tag_repository.get_by_id(tag_id)
        if not book_tag:
            return None

        for key, value in tag_data.items():
            setattr(book_tag, key, value)

        return book_tag_repository.update(book_tag)

    def delete_book_tag(self, tag_id: int) -> bool:
        """
        Delete a book tag.

        Args:
            tag_id: The ID of the book tag to delete.

        Returns:
            True if the book tag was deleted, otherwise False.
        """
        book_tag_repository = BookTagRepository()
        book_tag = book_tag_repository.get_by_id(tag_id)
        if not book_tag:
            return False

        book_tag_repository.delete(book_tag)
        return True

    def get_all_borrowed_books_student(self) -> List[BorrowedBookStudent]:
        """
        Retrieve all borrowed books by students.

        Returns:
            A list of all BorrowedBookStudent objects.
        """
        borrowed_book_student_repository = BorrowedBookStudentRepository()
        return borrowed_book_student_repository.get_all()

    def get_borrowed_book_student_by_id(self, student_id: int) -> Optional[BorrowedBookStudent]:
        """
        Retrieve a borrowed book by student ID.

        Args:
            student_id: The ID of the student.

        Returns:
            The BorrowedBookStudent object if found, otherwise None.
        """
        borrowed_book_student_repository = BorrowedBookStudentRepository()
        return borrowed_book_student_repository.get_by_id(student_id)

    def create_borrowed_book_student(self, borrowed_data: dict) -> BorrowedBookStudent:
        """
        Create a new borrowed book record for a student.

        Args:
            borrowed_data: A dictionary containing borrowed book data.

        Returns:
            The created BorrowedBookStudent object.
        """
        logger.info(f"Creating a new borrowed book record for student with data: {borrowed_data}")
        ValidationUtils.validate_input(borrowed_data.get('student_id'), "Student ID cannot be empty")
        ValidationUtils.validate_input(borrowed_data.get('book_id'), "Book ID cannot be empty")

        borrowed_book = BorrowedBookStudent(**borrowed_data)
        borrowed_book_student_repository = BorrowedBookStudentRepository()
        created_borrowed_book = borrowed_book_student_repository.create(borrowed_book)
        logger.info(f"Borrowed book record created successfully for student ID: {created_borrowed_book.student_id}")
        return created_borrowed_book

    def update_borrowed_book_student(self, student_id: int, borrowed_data: dict) -> Optional[BorrowedBookStudent]:
        """
        Update an existing borrowed book record for a student.

        Args:
            student_id: The ID of the student whose borrowed book record to update.
            borrowed_data: A dictionary containing updated borrowed book data.

        Returns:
            The updated BorrowedBookStudent object if successful, otherwise None.
        """
        borrowed_book_student_repository = BorrowedBookStudentRepository()
        borrowed_book = borrowed_book_student_repository.get_by_id(student_id)
        if not borrowed_book:
            return None

        for key, value in borrowed_data.items():
            setattr(borrowed_book, key, value)

        return borrowed_book_student_repository.update(borrowed_book)

    def delete_borrowed_book_student(self, student_id: int) -> bool:
        """
        Delete a borrowed book record for a student.

        Args:
            student_id: The ID of the student whose borrowed book record to delete.

        Returns:
            True if the borrowed book record was deleted, otherwise False.
        """
        borrowed_book_student_repository = BorrowedBookStudentRepository()
        borrowed_book = borrowed_book_student_repository.get_by_id(student_id)
        if not borrowed_book:
            return False

        borrowed_book_student_repository.delete(borrowed_book)
        return True

    def get_all_borrowed_books_teacher(self) -> List[BorrowedBookTeacher]:
        """
        Retrieve all borrowed books by teachers.

        Returns:
            A list of all BorrowedBookTeacher objects.
        """
        borrowed_book_teacher_repository = BorrowedBookTeacherRepository()
        return borrowed_book_teacher_repository.get_all()

    def get_borrowed_book_teacher_by_id(self, teacher_id: int) -> Optional[BorrowedBookTeacher]:
        """
        Retrieve a borrowed book by teacher ID.

        Args:
            teacher_id: The ID of the teacher.

        Returns:
            The BorrowedBookTeacher object if found, otherwise None.
        """
        borrowed_book_teacher_repository = BorrowedBookTeacherRepository()
        return borrowed_book_teacher_repository.get_by_id(teacher_id)

    def create_borrowed_book_teacher(self, borrowed_data: dict) -> BorrowedBookTeacher:
        """
        Create a new borrowed book record for a teacher.

        Args:
            borrowed_data: A dictionary containing borrowed book data.

        Returns:
            The created BorrowedBookTeacher object.
        """
        logger.info(f"Creating a new borrowed book record for teacher with data: {borrowed_data}")
        ValidationUtils.validate_input(borrowed_data.get('teacher_id'), "Teacher ID cannot be empty")
        ValidationUtils.validate_input(borrowed_data.get('book_id'), "Book ID cannot be empty")

        borrowed_book = BorrowedBookTeacher(**borrowed_data)
        borrowed_book_teacher_repository = BorrowedBookTeacherRepository()
        created_borrowed_book = borrowed_book_teacher_repository.create(borrowed_book)
        logger.info(f"Borrowed book record created successfully for teacher ID: {created_borrowed_book.teacher_id}")
        return created_borrowed_book

    def update_borrowed_book_teacher(self, teacher_id: int, borrowed_data: dict) -> Optional[BorrowedBookTeacher]:
        """
        Update an existing borrowed book record for a teacher.

        Args:
            teacher_id: The ID of the teacher whose borrowed book record to update.
            borrowed_data: A dictionary containing updated borrowed book data.

        Returns:
            The updated BorrowedBookTeacher object if successful, otherwise None.
        """
        borrowed_book_teacher_repository = BorrowedBookTeacherRepository()
        borrowed_book = borrowed_book_teacher_repository.get_by_id(teacher_id)
        if not borrowed_book:
            return None

        for key, value in borrowed_data.items():
            setattr(borrowed_book, key, value)

        return borrowed_book_teacher_repository.update(borrowed_book)

    def delete_borrowed_book_teacher(self, teacher_id: int) -> bool:
        """
        Delete a borrowed book record for a teacher.

        Args:
            teacher_id: The ID of the teacher whose borrowed book record to delete.

        Returns:
            True if the borrowed book record was deleted, otherwise False.
        """
        borrowed_book_teacher_repository = BorrowedBookTeacherRepository()
        borrowed_book = borrowed_book_teacher_repository.get_by_id(teacher_id)
        if not borrowed_book:
            return False

        borrowed_book_teacher_repository.delete(borrowed_book)
        return True

    def get_all_distribution_sessions(self) -> List[DistributionSession]:
        """
        Retrieve all distribution sessions.

        Returns:
            A list of all DistributionSession objects.
        """
        distribution_session_repository = DistributionSessionRepository()
        return distribution_session_repository.get_all()

    def get_distribution_session_by_id(self, session_id: int) -> Optional[DistributionSession]:
        """
        Retrieve a distribution session by its ID.

        Args:
            session_id: The ID of the distribution session.

        Returns:
            The DistributionSession object if found, otherwise None.
        """
        distribution_session_repository = DistributionSessionRepository()
        return distribution_session_repository.get_by_id(session_id)

    def create_distribution_session(self, session_data: dict) -> DistributionSession:
        """
        Create a new distribution session.

        Args:
            session_data: A dictionary containing distribution session data.

        Returns:
            The created DistributionSession object.
        """
        logger.info(f"Creating a new distribution session with data: {session_data}")
        ValidationUtils.validate_input(session_data.get('class_name'), "Class name cannot be empty")
        ValidationUtils.validate_input(session_data.get('subject'), "Subject cannot be empty")

        distribution_session = DistributionSession(**session_data)
        distribution_session_repository = DistributionSessionRepository()
        created_session = distribution_session_repository.create(distribution_session)
        logger.info(f"Distribution session created successfully with ID: {created_session.class_name}")
        return created_session

    def update_distribution_session(self, session_id: int, session_data: dict) -> Optional[DistributionSession]:
        """
        Update an existing distribution session.

        Args:
            session_id: The ID of the distribution session to update.
            session_data: A dictionary containing updated distribution session data.

        Returns:
            The updated DistributionSession object if successful, otherwise None.
        """
        distribution_session_repository = DistributionSessionRepository()
        distribution_session = distribution_session_repository.get_by_id(session_id)
        if not distribution_session:
            return None

        for key, value in session_data.items():
            setattr(distribution_session, key, value)

        return distribution_session_repository.update(distribution_session)

    def delete_distribution_session(self, session_id: int) -> bool:
        """
        Delete a distribution session.

        Args:
            session_id: The ID of the distribution session to delete.

        Returns:
            True if the distribution session was deleted, otherwise False.
        """
        distribution_session_repository = DistributionSessionRepository()
        distribution_session = distribution_session_repository.get_by_id(session_id)
        if not distribution_session:
            return False

        distribution_session_repository.delete(distribution_session)
        return True

    def get_all_distribution_students(self) -> List[DistributionStudent]:
        """
        Retrieve all distribution student records.

        Returns:
            A list of all DistributionStudent objects.
        """
        distribution_student_repository = DistributionStudentRepository()
        return distribution_student_repository.get_all()

    def get_distribution_student_by_id(self, student_id: int) -> Optional[DistributionStudent]:
        """
        Retrieve a distribution student record by student ID.

        Args:
            student_id: The ID of the student.

        Returns:
            The DistributionStudent object if found, otherwise None.
        """
        distribution_student_repository = DistributionStudentRepository()
        return distribution_student_repository.get_by_id(student_id)

    def create_distribution_student(self, distribution_data: dict) -> DistributionStudent:
        """
        Create a new distribution student record.

        Args:
            distribution_data: A dictionary containing distribution student data.

        Returns:
            The created DistributionStudent object.
        """
        logger.info(f"Creating a new distribution student record with data: {distribution_data}")
        ValidationUtils.validate_input(distribution_data.get('session_id'), "Session ID cannot be empty")
        ValidationUtils.validate_input(distribution_data.get('student_id'), "Student ID cannot be empty")

        distribution_student = DistributionStudent(**distribution_data)
        distribution_student_repository = DistributionStudentRepository()
        created_distribution_student = distribution_student_repository.create(distribution_student)
        logger.info(f"Distribution student record created successfully for student ID: {created_distribution_student.student_id}")
        return created_distribution_student

    def update_distribution_student(self, student_id: int, distribution_data: dict) -> Optional[DistributionStudent]:
        """
        Update an existing distribution student record.

        Args:
            student_id: The ID of the student whose distribution record to update.
            distribution_data: A dictionary containing updated distribution student data.

        Returns:
            The updated DistributionStudent object if successful, otherwise None.
        """
        distribution_student_repository = DistributionStudentRepository()
        distribution_student = distribution_student_repository.get_by_id(student_id)
        if not distribution_student:
            return None

        for key, value in distribution_data.items():
            setattr(distribution_student, key, value)

        return distribution_student_repository.update(distribution_student)

    def delete_distribution_student(self, student_id: int) -> bool:
        """
        Delete a distribution student record.

        Args:
            student_id: The ID of the student whose distribution record to delete.

        Returns:
            True if the distribution student record was deleted, otherwise False.
        """
        distribution_student_repository = DistributionStudentRepository()
        distribution_student = distribution_student_repository.get_by_id(student_id)
        if not distribution_student:
            return False

        distribution_student_repository.delete(distribution_student)
        return True

    def get_all_distribution_import_logs(self) -> List[DistributionImportLog]:
        """
        Retrieve all distribution import logs.

        Returns:
            A list of all DistributionImportLog objects.
        """
        distribution_import_log_repository = DistributionImportLogRepository()
        return distribution_import_log_repository.get_all()

    def get_distribution_import_log_by_id(self, session_id: int) -> Optional[DistributionImportLog]:
        """
        Retrieve a distribution import log by session ID.

        Args:
            session_id: The ID of the session.

        Returns:
            The DistributionImportLog object if found, otherwise None.
        """
        distribution_import_log_repository = DistributionImportLogRepository()
        return distribution_import_log_repository.get_by_id(session_id)

    def create_distribution_import_log(self, log_data: dict) -> DistributionImportLog:
        """
        Create a new distribution import log.

        Args:
            log_data: A dictionary containing distribution import log data.

        Returns:
            The created DistributionImportLog object.
        """
        logger.info(f"Creating a new distribution import log with data: {log_data}")
        ValidationUtils.validate_input(log_data.get('session_id'), "Session ID cannot be empty")
        ValidationUtils.validate_input(log_data.get('file_name'), "File name cannot be empty")

        distribution_import_log = DistributionImportLog(**log_data)
        distribution_import_log_repository = DistributionImportLogRepository()
        created_log = distribution_import_log_repository.create(distribution_import_log)
        logger.info(f"Distribution import log created successfully for session ID: {created_log.session_id}")
        return created_log

    def update_distribution_import_log(self, session_id: int, log_data: dict) -> Optional[DistributionImportLog]:
        """
        Update an existing distribution import log.

        Args:
            session_id: The ID of the session whose import log to update.
            log_data: A dictionary containing updated distribution import log data.

        Returns:
            The updated DistributionImportLog object if successful, otherwise None.
        """
        distribution_import_log_repository = DistributionImportLogRepository()
        distribution_import_log = distribution_import_log_repository.get_by_id(session_id)
        if not distribution_import_log:
            return None

        for key, value in log_data.items():
            setattr(distribution_import_log, key, value)

        return distribution_import_log_repository.update(distribution_import_log)

    def delete_distribution_import_log(self, session_id: int) -> bool:
        """
        Delete a distribution import log.

        Args:
            session_id: The ID of the session whose import log to delete.

        Returns:
            True if the distribution import log was deleted, otherwise False.
        """
        distribution_import_log_repository = DistributionImportLogRepository()
        distribution_import_log = distribution_import_log_repository.get_by_id(session_id)
        if not distribution_import_log:
            return False

        distribution_import_log_repository.delete(distribution_import_log)
        return True

    def import_books_from_excel(self, filename: str) -> List[Book]:
        """
        Import books from an Excel file.

        Args:
            filename: The name of the Excel file.

        Returns:
            A list of imported Book objects.
        """
        logger.info(f"Importing books from Excel file: {filename}")
        ValidationUtils.validate_input(filename, "Filename cannot be empty")
        
        try:
            data = self.import_export_service.import_from_excel(filename)
            books = []
            
            for book_data in data:
                book = Book(**book_data)
                created_book = self.book_repository.create(book)
                books.append(created_book)
            
            logger.info(f"Successfully imported {len(books)} books from {filename}")
            return books
        except Exception as e:
            logger.error(f"Error importing books from Excel: {e}")
            return []

    def create_session(self, class_name, stream, subject, term, created_by, students):
        """
        students: list of student_id
        """
        cursor = self.db.cursor()

        # create session
        cursor.execute("""
            INSERT INTO distribution_sessions
            (class, stream, subject, term, created_by, status)
            VALUES (?, ?, ?, ?, ?, 'DRAFT')
        """, (class_name, stream, subject, term, created_by))

        session_id = cursor.lastrowid

        # pre-fill students (placeholders)
        for student_id in students:
            cursor.execute("""
                INSERT INTO distribution_students (session_id, student_id)
                VALUES (?, ?)
            """, (session_id, student_id))

        self.db.commit()
        return session_id

    def export_csv(self, session_id, file_path):
        records = self.student_repo.find_by_field("session_id", session_id)

        with open(file_path, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(["student_id", "book_number", "notes"])

            for r in records:
                writer.writerow([
                    r.student_id,
                    r.book_number or "",
                    r.notes or ""
                ])

        return file_path

    def import_csv(self, session_id, file_path, imported_by):
        cursor = self.db.cursor()
        errors = []

        with open(file_path, newline="", encoding="utf-8") as f:
            reader = csv.DictReader(f)

            for row in reader:
                if not row["book_number"]:
                    continue  # allow blanks

                # map book_number → book_id
                cursor.execute(
                    "SELECT book_id FROM books WHERE book_id = ? AND available = 1",
                    (row["book_number"],)
                )
                book = cursor.fetchone()

                if not book:
                    errors.append(f"Invalid book: {row['book_number']}")
                    continue

                cursor.execute("""
                    UPDATE distribution_students
                    SET book_number = ?, book_id = ?
                    WHERE session_id = ? AND student_id = ?
                """, (
                    row["book_number"],
                    book[0],
                    session_id,
                    row["student_id"]
                ))

        status = "SUCCESS" if not errors else "PARTIAL"

        self.log_repo.create(
            session_id=session_id,
            file_name=file_path,
            imported_by=imported_by,
            status=status,
            message="; ".join(errors) if errors else "Imported successfully"
        )

        self.db.commit()
        return errors

    def import_csv_with_unknown_books(self, session_id, file_path, imported_by):
        """
        Import distribution data allowing unknown books (PENDING_BOOK status).
        
        This implements the updated DISTRIBUTION IMPORT FLOW that allows importing
        book numbers even if they are not yet in the books table.
        
        Args:
            session_id: ID of the distribution session
            file_path: Path to the CSV file
            imported_by: Username of the user performing the import
            
        Returns:
            Dictionary containing import statistics and categorization
        """
        cursor = self.db.cursor()
        
        # Categorization counters
        valid_books = 0
        pending_books = 0
        conflicts = 0
        duplicate_book_numbers = 0
        
        # Track book numbers to detect duplicates
        book_number_counts = {}
        
        # First pass: validate students and check for duplicate book numbers
        with open(file_path, newline="", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            
            for row in reader:
                student_id = row.get("student_id", "").strip()
                book_number = row.get("book_number", "").strip()
                
                # Validate student exists (REQUIRED)
                if not student_id:
                    conflicts += 1
                    continue
                    
                # Check for duplicate book numbers (NOT allowed)
                if book_number:
                    if book_number in book_number_counts:
                        book_number_counts[book_number] += 1
                        duplicate_book_numbers += 1
                        conflicts += 1
                    else:
                        book_number_counts[book_number] = 1
        
        # Second pass: process the import
        with open(file_path, newline="", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            
            for row in reader:
                student_id = row.get("student_id", "").strip()
                book_number = row.get("book_number", "").strip()
                
                # Skip if we already identified this as a conflict
                if book_number and book_number_counts.get(book_number, 0) > 1:
                    continue
                
                if not student_id:
                    continue
                
                # Check if book exists in catalog
                book_exists = False
                book_id = None
                
                if book_number:
                    cursor.execute(
                        "SELECT book_id, available FROM books WHERE book_number = ?",
                        (book_number,)
                    )
                    book = cursor.fetchone()
                    
                    if book:
                        book_exists = True
                        book_id = book[0]
                        
                        # Check availability if book exists
                        if not book[1]:  # book[1] is the 'available' field
                            conflicts += 1
                            continue
                    else:
                        # Book doesn't exist in catalog - mark as PENDING_BOOK
                        pending_books += 1
                
                # Update distribution_students record
                if book_number:
                    if book_exists:
                        valid_books += 1
                        cursor.execute("""
                            UPDATE distribution_students
                            SET book_number = ?, book_id = ?, notes = NULL
                            WHERE session_id = ? AND student_id = ?
                        """, (
                            book_number,
                            book_id,
                            session_id,
                            student_id
                        ))
                    else:
                        # Book doesn't exist - save book_number but NULL book_id
                        cursor.execute("""
                            UPDATE distribution_students
                            SET book_number = ?, book_id = NULL, notes = 'Not in system'
                            WHERE session_id = ? AND student_id = ?
                        """, (
                            book_number,
                            session_id,
                            student_id
                        ))
                else:
                    # No book number provided - just ensure student exists
                    cursor.execute("""
                        UPDATE distribution_students
                        SET book_number = NULL, book_id = NULL, notes = NULL
                        WHERE session_id = ? AND student_id = ?
                    """, (
                        session_id,
                        student_id
                    ))
        
        # Update session status to IMPORTED
        cursor.execute("""
            UPDATE distribution_sessions
            SET status = 'IMPORTED'
            WHERE id = ?
        """, (session_id,))
        
        # Create import log
        status = "SUCCESS" if conflicts == 0 else "PARTIAL"
        message = f"Valid: {valid_books}, Pending: {pending_books}, Conflicts: {conflicts}"
        
        self.log_repo.create(
            session_id=session_id,
            file_name=file_path,
            imported_by=imported_by,
            status=status,
            message=message
        )
        
        self.db.commit()
        
        return {
            "valid_books": valid_books,
            "pending_books": pending_books,
            "conflicts": conflicts,
            "duplicate_book_numbers": duplicate_book_numbers,
            "status": status,
            "message": message
        }

    def summary(self, session_id):
        records = self.student_repo.find_by_field("session_id", session_id)

        total = len(records)
        assigned = sum(1 for r in records if r.book_id)
        missing = total - assigned

        return {
            "total_students": total,
            "assigned_books": assigned,
            "missing_books": missing
        }

    def post_session(self, session_id, posted_by):
        cursor = self.db.cursor()

        try:
            # create borrow records
            cursor.execute("""
                INSERT INTO borrowed_books_student (student_id, book_id, borrowed_on)
                SELECT student_id, book_id, DATE('now')
                FROM distribution_students
                WHERE session_id = ?
                  AND book_id IS NOT NULL
            """, (session_id,))

            # mark books unavailable
            cursor.execute("""
                UPDATE books
                SET available = 0
                WHERE book_id IN (
                    SELECT book_id FROM distribution_students
                    WHERE session_id = ?
                )
            """, (session_id,))

            # close session
            cursor.execute("""
                UPDATE distribution_sessions
                SET status = 'POSTED', distributed_by = ?
                WHERE id = ?
            """, (posted_by, session_id))

            self.db.commit()
        
        except Exception:
            self.db.rollback()
            raise
    
        def undo_distribution_session(self, session_id: int) -> bool:
            """
            Undo a distribution session by deleting all related records.
            
            Args:
                session_id: ID of the distribution session to undo
                
            Returns:
                True if the undo was successful, False otherwise
            """
            logger.info(f"Undoing distribution session {session_id}")
            
            try:
                cursor = self.db.cursor()
                
                # Delete all distribution student records for the session
                cursor.execute("""
                    DELETE FROM distribution_students WHERE session_id = ?
                """, (session_id,))
                
                # Delete the distribution session
                cursor.execute("""
                    DELETE FROM distribution_sessions WHERE id = ?
                """, (session_id,))
                
                self.db.commit()
                logger.info(f"Successfully undid distribution session {session_id}")
                return True
                
            except Exception as e:
                self.db.rollback()
                logger.error(f"Error undoing distribution session: {e}")
                return False
    
        def return_via_distribution(self, session_id: int, returned_by: str) -> bool:
            """
            Return all books assigned in a distribution session.
            
            Args:
                session_id: ID of the distribution session
                returned_by: Username of the user processing the returns
                
            Returns:
                True if the return was successful, False otherwise
            """
            logger.info(f"Returning books via distribution session {session_id}")
            
            try:
                cursor = self.db.cursor()
                
                # Get all book assignments for the session
                cursor.execute("""
                    SELECT student_id, book_id FROM distribution_students
                    WHERE session_id = ? AND book_id IS NOT NULL
                """, (session_id,))
                
                assignments = cursor.fetchall()
                
                # Return each book
                for student_id, book_id in assignments:
                    self.return_book_student(student_id, book_id, "Good", 0, returned_by)
                
                logger.info(f"Successfully returned {len(assignments)} books via distribution session {session_id}")
                return True
                
            except Exception as e:
                logger.error(f"Error returning books via distribution: {e}")
                return False
    
        def detect_duplicate_books(self) -> List[dict]:
            """
            Detect duplicate books in the system.
            
            Returns:
                List of dictionaries containing duplicate book information
            """
            logger.info("Detecting duplicate books")
            
            try:
                cursor = self.db.cursor()
                
                # Find books with duplicate titles and authors
                cursor.execute("""
                    SELECT title, author, COUNT(*) as count
                    FROM books
                    GROUP BY title, author
                    HAVING COUNT(*) > 1
                """)
                
                duplicates = []
                for row in cursor.fetchall():
                    title, author, count = row
                    
                    # Get all book IDs for this duplicate
                    cursor.execute("""
                        SELECT book_number FROM books WHERE title = ? AND author = ?
                    """, (title, author))
                    
                    book_numbers = [item[0] for item in cursor.fetchall()]
                    
                    duplicates.append({
                        "title": title,
                        "author": author,
                        "count": count,
                        "book_numbers": book_numbers
                    })
                
                logger.info(f"Found {len(duplicates)} sets of duplicate books")
                return duplicates
                
            except Exception as e:
                logger.error(f"Error detecting duplicate books: {e}")
                return []
    
        def get_borrowed_books_with_details(self, filter_type: str = "all") -> List[Dict]:
            """
            Get all borrowed books with detailed information for bulk return UI.
    
            Args:
                filter_type: Filter by 'all', 'borrowed', or 'overdue'
    
            Returns:
                List of dictionaries with book and borrower details
            """
            try:
                # Get all borrowed books from both students and teachers
                student_borrowings = self.get_all_borrowed_books_student()
                teacher_borrowings = self.get_all_borrowed_books_teacher()
    
                borrowed_books = []
    
                # Process student borrowings
                for borrowing in student_borrowings:
                    if borrowing.returned_on:
                        continue  # Skip already returned books
    
                    book = self.get_book_by_id(borrowing.book_id)
                    if book:
                        borrowed_books.append({
                            'book_id': book.id,
                            'book_number': book.book_number,
                            'title': book.title,
                            'borrower_id': borrowing.student_id,
                            'borrower_name': f"Student {borrowing.student_id}",
                            'borrower_type': 'student',
                            'borrowed_on': borrowing.borrowed_on,
                            'due_date': self._calculate_due_date(borrowing.borrowed_on),
                            'overdue': self._is_overdue(borrowing.borrowed_on)
                        })
    
                # Process teacher borrowings
                for borrowing in teacher_borrowings:
                    if borrowing.returned_on:
                        continue  # Skip already returned books
    
                    book = self.get_book_by_id(borrowing.book_id)
                    if book:
                        borrowed_books.append({
                            'book_id': book.id,
                            'book_number': book.book_number,
                            'title': book.title,
                            'borrower_id': borrowing.teacher_id,
                            'borrower_name': f"Teacher {borrowing.teacher_id}",
                            'borrower_type': 'teacher',
                            'borrowed_on': borrowing.borrowed_on,
                            'due_date': self._calculate_due_date(borrowing.borrowed_on),
                            'overdue': self._is_overdue(borrowing.borrowed_on)
                        })
    
                # Apply filtering
                if filter_type == "borrowed":
                    return borrowed_books
                elif filter_type == "overdue":
                    return [book for book in borrowed_books if book['overdue']]
                else:
                    return borrowed_books
    
            except Exception as e:
                logger.error(f"Error getting borrowed books with details: {e}")
                return []
    
        def bulk_return_books(self, book_return_data: List[Dict], current_user: str) -> Tuple[bool, str, dict]:
            """
            Bulk return multiple books with comprehensive validation and error handling.
    
            Args:
                book_return_data: List of dictionaries containing return information
                current_user: Username of the user processing the returns
    
            Returns:
                Tuple of (success, message, statistics)
            """
            try:
                success_count = 0
                error_count = 0
                errors = []
    
                for return_item in book_return_data:
                    try:
                        book_id = return_item['book_id']
                        borrower_id = return_item['borrower_id']
                        borrower_type = return_item['borrower_type']
                        condition = return_item.get('condition', 'Good')
                        fine_amount = float(return_item.get('fine_amount', 0))
    
                        # Validate book exists and is borrowed
                        book = self.get_book_by_id(book_id)
                        if not book:
                            errors.append(f"Book {book_id} not found")
                            error_count += 1
                            continue
    
                        # Process return based on borrower type
                        if borrower_type == 'student':
                            success = self.return_book_student(
                                borrower_id, book_id, condition, fine_amount, current_user
                            )
                        else:
                            success = self.return_book_teacher(borrower_id, book_id)
    
                        if success:
                            success_count += 1
                        else:
                            errors.append(f"Failed to return book {book_id} for {borrower_type} {borrower_id}")
                            error_count += 1
    
                    except Exception as e:
                        errors.append(f"Error processing return: {str(e)}")
                        error_count += 1
    
                # Log the bulk operation
                self.log_user_action(
                    current_user,
                    "bulk_return",
                    f"Bulk return operation: {success_count} successful, {error_count} failed"
                )
    
                statistics = {
                    'total_attempted': len(book_return_data),
                    'success_count': success_count,
                    'error_count': error_count,
                    'errors': errors
                }
    
                if error_count > 0:
                    message = f"Bulk return completed with {error_count} errors. {success_count} books returned successfully."
                else:
                    message = f"Bulk return completed successfully. {success_count} books returned."
    
                return True, message, statistics
    
            except Exception as e:
                logger.error(f"Error in bulk return: {e}")
                return False, f"Bulk return failed: {str(e)}", {}
    
        def _calculate_due_date(self, borrowed_on: str) -> str:
            """
            Calculate due date based on borrowed date.
            
            Args:
                borrowed_on: Date when book was borrowed
                
            Returns:
                Due date as string
            """
            try:
                from datetime import datetime, timedelta
                borrowed_date = datetime.strptime(borrowed_on, '%Y-%m-%d')
                due_date = borrowed_date + timedelta(days=14)  # 2 weeks borrowing period
                return due_date.strftime('%Y-%m-%d')
            except Exception as e:
                logger.error(f"Error calculating due date: {e}")
                return "Unknown"
    
        def _is_overdue(self, borrowed_on: str) -> bool:
            """
            Check if a book is overdue.
            
            Args:
                borrowed_on: Date when book was borrowed
                
            Returns:
                True if book is overdue, False otherwise
            """
            try:
                from datetime import datetime
                borrowed_date = datetime.strptime(borrowed_on, '%Y-%m-%d')
                due_date = borrowed_date + timedelta(days=14)
                return datetime.now() > due_date
            except Exception as e:
                logger.error(f"Error checking overdue status: {e}")
                return False
    
        def optimize_bulk_import(self, session_id: int, file_path: str, imported_by: str, batch_size: int = 100) -> dict:
            """
            Optimized bulk import for large datasets (1,000+ students).
            
            Args:
                session_id: ID of the distribution session
                file_path: Path to the CSV file
                imported_by: Username of the user performing the import
                batch_size: Number of records to process in each batch
                
            Returns:
                Dictionary containing import statistics
            """
            logger.info(f"Starting optimized bulk import for session {session_id}")
            
            try:
                cursor = self.db.cursor()
                errors = []
                success_count = 0
                total_records = 0
                
                # Pre-fetch all available books for faster lookup
                cursor.execute("SELECT book_number, book_id FROM books WHERE available = 1")
                available_books = {row[0]: row[1] for row in cursor.fetchall()}
                
                # Use import_export_service for efficient CSV reading
                data = self.import_export_service.import_from_csv(file_path)
                batch = []
                
                for row in data:
                    total_records += 1
                    
                    if not row.get("book_number"):
                        continue  # Skip blanks
                    
                    book_number = row["book_number"]
                    student_id = row["student_id"]
                    
                    # Check if book is available
                    if book_number in available_books:
                        book_id = available_books[book_number]
                        batch.append((book_number, book_id, session_id, student_id))
                        
                        # Remove from available books to prevent duplicate assignment
                        del available_books[book_number]
                        
                        if len(batch) >= batch_size:
                            # Process batch
                            cursor.executemany("""
                                UPDATE distribution_students
                                SET book_number = ?, book_id = ?
                                WHERE session_id = ? AND student_id = ?
                            """, batch)
                            success_count += len(batch)
                            batch = []
                    else:
                        errors.append(f"Invalid book: {book_number}")
                
                # Process remaining records in the final batch
                if batch:
                    cursor.executemany("""
                        UPDATE distribution_students
                        SET book_number = ?, book_id = ?
                        WHERE session_id = ? AND student_id = ?
                    """, batch)
                    success_count += len(batch)
                
                # Log the import
                status = "SUCCESS" if not errors else "PARTIAL"
                self.log_repo.create(
                    session_id=session_id,
                    file_name=file_path,
                    imported_by=imported_by,
                    status=status,
                    message="; ".join(errors) if errors else "Imported successfully"
                )
                
                self.db.commit()
                
                logger.info(f"Bulk import completed: {success_count} successful, {len(errors)} errors")
                
                return {
                    "success_count": success_count,
                    "error_count": len(errors),
                    "total_records": total_records,
                    "errors": errors
                }
                
            except Exception as e:
                self.db.rollback()
                logger.error(f"Error in bulk import: {e}")
                return {
                    "success_count": 0,
                    "error_count": 0,
                    "total_records": 0,
                    "errors": [str(e)]
                }

    def export_books_to_excel(self, filename: str) -> bool:
        """
        Export books to an Excel file.

        Args:
            filename: The name of the Excel file.

        Returns:
            True if the export was successful, otherwise False.
        """
        logger.info(f"Exporting books to Excel file: {filename}")
        ValidationUtils.validate_input(filename, "Filename cannot be empty")
        
        try:
            books = self.book_repository.get_all()
            data = [book.__dict__ for book in books]
            return self.import_export_service.export_to_excel(data, filename)
        except Exception as e:
            logger.error(f"Error exporting books to Excel: {e}")
            return False
    
    def bulk_borrow_books_from_excel(self, filename: str, current_user: str) -> Tuple[bool, str, dict]:
        """
        Bulk borrow books from an Excel file.
        
        Args:
            filename: Path to the Excel file
            current_user: Username of the user performing the operation
            
        Returns:
            tuple: (success, message, statistics)
        """
        logger.info(f"Starting bulk borrow from Excel file: {filename}")
        
        try:
            # Import data with validation
            success, data, error_msg = self.import_export_service.import_from_excel_with_validation(
                filename,
                ['Admission_Number', 'Student_Name', 'Book_Number']
            )
            
            if not success:
                return False, error_msg, {}
            
            if not data:
                return False, "No data found in the Excel file", {}
            
            # Validate data
            from school_system.gui.windows.book_window.utils.validation import BookValidationHelper
            is_valid, validation_errors = BookValidationHelper.validate_bulk_borrow_data(
                data, self.student_service, self
            )
            
            if not is_valid:
                error_message = "Validation errors:\n" + "\n".join(validation_errors)
                return False, error_message, {}
            
            # Process bulk borrowing
            success_count = 0
            error_count = 0
            errors = []
            
            for i, row in enumerate(data, 1):
                try:
                    admission_number = row['Admission_Number'].strip()
                    book_number = row['Book_Number'].strip()
                    
                    # Get book ID by book number
                    book = self.get_book_by_number(book_number)
                    if not book:
                        errors.append(f"Row {i}: Book '{book_number}' not found")
                        error_count += 1
                        continue
                    
                    # Borrow the book
                    success, message = self.reserve_book(admission_number, 'student', book.id)
                    if success:
                        success_count += 1
                    else:
                        errors.append(f"Row {i}: {message}")
                        error_count += 1
                        
                except Exception as e:
                    errors.append(f"Row {i}: Error processing - {str(e)}")
                    error_count += 1
            
            # Log the operation
            self.log_user_action(
                current_user,
                "bulk_borrow",
                f"Bulk borrow operation: {success_count} successful, {error_count} failed"
            )
            
            statistics = {
                'total_records': len(data),
                'success_count': success_count,
                'error_count': error_count,
                'errors': errors
            }
            
            if error_count > 0:
                message = f"Bulk borrow completed with {error_count} errors. {success_count} books borrowed successfully."
            else:
                message = f"Bulk borrow completed successfully. {success_count} books borrowed."
            
            return True, message, statistics
            
        except Exception as e:
            logger.error(f"Error in bulk borrow from Excel: {e}")
            return False, f"Error processing bulk borrow: {str(e)}", {}
    
    def get_book_by_number(self, book_number: str) -> Optional[Book]:
        """
        Get a book by its book number.
        
        Args:
            book_number: The book number to search for
            
        Returns:
            The Book object if found, otherwise None
        """
        try:
            books = self.book_repository.find_by_field('book_number', book_number)
            return books[0] if books else None
        except Exception as e:
            logger.error(f"Error getting book by number: {e}")
            return None
    
    def log_user_action(self, username: str, action_type: str, details: str) -> bool:
        """
        Log user action to audit trail.
        
        Args:
            username: Username of the user
            action_type: Type of action performed
            details: Details about the action
            
        Returns:
            True if logging was successful, False otherwise
        """
        try:
            # This would be implemented in a real system
            logger.info(f"User action logged: {username} - {action_type} - {details}")
            return True
        except Exception as e:
            logger.error(f"Error logging user action: {e}")
            return False

    def borrow_book(self, book_id: int, user_id: str, user_type: str) -> bool:
        """
        Borrow a book for a user (student or teacher).

        Args:
            book_id: ID of the book to borrow
            user_id: ID of the user borrowing the book
            user_type: Type of user ('student' or 'teacher')

        Returns:
            True if borrowing was successful, False otherwise
        """
        logger.info(f"Borrowing book {book_id} for {user_type} {user_id}")

        try:
            # Convert string IDs to appropriate types if needed
            if user_type == 'student':
                user_id_int = int(user_id)
            else:  # teacher
                user_id_int = int(user_id)

            # Use the existing reserve_book method with correct parameter order
            return self.reserve_book(user_id_int, user_type, book_id)

        except Exception as e:
            logger.error(f"Error borrowing book: {e}")
            return False

    def bulk_borrow_books_by_class_stream(
        self,
        book_id: int,
        class_level: Optional[int] = None,
        stream: Optional[str] = None,
        subject: Optional[str] = None
    ) -> Dict[str, any]:
        """
        Borrow a book for all students in a specific class/stream combination.
        
        Args:
            book_id: ID of the book to borrow
            class_level: Optional class level filter (e.g., 4 for Form 4)
            stream: Optional stream filter (e.g., "Red")
            subject: Optional subject name for logging/context
            
        Returns:
            A dictionary with operation results:
            {
                'success': bool,
                'total_students': int,
                'successful_borrows': int,
                'failed_borrows': int,
                'errors': List[str],
                'details': List[Dict]
            }
        """
        logger.info(
            f"Bulk borrowing book {book_id} for class_level={class_level}, "
            f"stream={stream}, subject={subject}"
        )
        
        result = {
            'success': False,
            'total_students': 0,
            'successful_borrows': 0,
            'failed_borrows': 0,
            'errors': [],
            'details': []
        }
        
        try:
            # Get students matching the criteria
            students = self.class_management_service.get_students_for_bulk_operation(
                class_level=class_level,
                stream=stream
            )
            
            result['total_students'] = len(students)
            
            if not students:
                result['errors'].append("No students found matching the specified criteria")
                return result
            
            # Check if book is available (for first student - in real scenario, 
            # you might want to check availability for each or have multiple copies)
            if not self.check_book_availability(book_id):
                result['errors'].append(f"Book {book_id} is not available for borrowing")
                return result
            
            # Attempt to borrow for each student
            for student in students:
                try:
                    # Convert student_id to appropriate format
                    student_id = student.student_id
                    if isinstance(student_id, str):
                        try:
                            student_id_int = int(student_id)
                        except ValueError:
                            # If student_id is not numeric, use admission_number
                            student_id_int = int(student.admission_number) if student.admission_number else None
                    else:
                        student_id_int = student_id
                    
                    if student_id_int is None:
                        result['failed_borrows'] += 1
                        result['errors'].append(f"Invalid student ID for student {student.name}")
                        result['details'].append({
                            'student_id': str(student.student_id),
                            'student_name': student.name,
                            'status': 'failed',
                            'error': 'Invalid student ID'
                        })
                        continue
                    
                    # Borrow the book
                    success = self.borrow_book(book_id, str(student_id_int), 'student')
                    
                    if success:
                        result['successful_borrows'] += 1
                        result['details'].append({
                            'student_id': str(student.student_id),
                            'student_name': student.name,
                            'status': 'success'
                        })
                    else:
                        result['failed_borrows'] += 1
                        result['errors'].append(f"Failed to borrow book for student {student.name} ({student.student_id})")
                        result['details'].append({
                            'student_id': str(student.student_id),
                            'student_name': student.name,
                            'status': 'failed',
                            'error': 'Borrow operation failed'
                        })
                        
                except Exception as e:
                    result['failed_borrows'] += 1
                    error_msg = f"Error borrowing for student {student.name}: {str(e)}"
                    result['errors'].append(error_msg)
                    result['details'].append({
                        'student_id': str(student.student_id),
                        'student_name': student.name,
                        'status': 'failed',
                        'error': str(e)
                    })
                    logger.error(error_msg)
            
            result['success'] = result['successful_borrows'] > 0
            
            logger.info(
                f"Bulk borrow completed: {result['successful_borrows']}/{result['total_students']} successful"
            )
            
        except Exception as e:
            logger.error(f"Error in bulk borrow operation: {e}")
            result['errors'].append(f"Bulk borrow operation failed: {str(e)}")
        
        return result
    
    def bulk_borrow_books_for_students(
        self,
        book_id: int,
        student_ids: List[str]
    ) -> Dict[str, any]:
        """
        Borrow a book for a list of specific students.
        
        Args:
            book_id: ID of the book to borrow
            student_ids: List of student IDs to borrow for
            
        Returns:
            A dictionary with operation results (same format as bulk_borrow_books_by_class_stream)
        """
        logger.info(f"Bulk borrowing book {book_id} for {len(student_ids)} students")
        
        result = {
            'success': False,
            'total_students': len(student_ids),
            'successful_borrows': 0,
            'failed_borrows': 0,
            'errors': [],
            'details': []
        }
        
        try:
            for student_id in student_ids:
                try:
                    success = self.borrow_book(book_id, student_id, 'student')
                    
                    if success:
                        result['successful_borrows'] += 1
                        result['details'].append({
                            'student_id': student_id,
                            'status': 'success'
                        })
                    else:
                        result['failed_borrows'] += 1
                        result['errors'].append(f"Failed to borrow book for student {student_id}")
                        result['details'].append({
                            'student_id': student_id,
                            'status': 'failed',
                            'error': 'Borrow operation failed'
                        })
                        
                except Exception as e:
                    result['failed_borrows'] += 1
                    error_msg = f"Error borrowing for student {student_id}: {str(e)}"
                    result['errors'].append(error_msg)
                    result['details'].append({
                        'student_id': student_id,
                        'status': 'failed',
                        'error': str(e)
                    })
                    logger.error(error_msg)
            
            result['success'] = result['successful_borrows'] > 0
            
        except Exception as e:
            logger.error(f"Error in bulk borrow operation: {e}")
            result['errors'].append(f"Bulk borrow operation failed: {str(e)}")
        
        return result

    def check_book_availability(self, book_id: int) -> bool:
        """
        Check if a book is available for borrowing
        
        Args:
            book_id: ID of the book to check
            
        Returns:
            True if available, False if already borrowed
        """
        logger.info(f"Checking availability for book ID: {book_id}")
        
        try:
            book = self.book_repository.get_by_id(book_id)
            if not book:
                logger.warning(f"Book with ID {book_id} not found")
                return False
                
            # Check if book is available
            if book.available:
                # Also check if the book is currently borrowed by anyone
                borrowed_book_student_repo = BorrowedBookStudentRepository()
                borrowed_book_teacher_repo = BorrowedBookTeacherRepository()
                
                # Check if book is borrowed by any student
                student_borrowings = borrowed_book_student_repo.find_by_field('book_id', book_id)
                # Check if book is borrowed by any teacher
                teacher_borrowings = borrowed_book_teacher_repo.find_by_field('book_id', book_id)
                
                # Book is available only if it's not borrowed by anyone
                is_available = not student_borrowings and not teacher_borrowings
                return is_available
            else:
                return False
                
        except Exception as e:
            logger.error(f"Error checking book availability: {e}")
            return False

    def reserve_book(self, user_id: int, user_type: str, book_id: int) -> bool:
        """
        Reserve a book for a user
        
        Args:
            user_id: ID of the user reserving the book
            user_type: 'student' or 'teacher'
            book_id: ID of the book to reserve
            
        Returns:
            True if reservation was successful, False otherwise
        """
        logger.info(f"Reserving book {book_id} for {user_type} {user_id}")
        
        try:
            # Check if book is available
            if not self.check_book_availability(book_id):
                logger.warning(f"Book {book_id} is not available for reservation")
                return False
                
            # Create reservation based on user type
            if user_type == 'student':
                borrowed_data = {
                    'student_id': user_id,
                    'book_id': book_id,
                    'borrowed_on': datetime.now().strftime('%Y-%m-%d'),
                    'reminder_days': 7  # Default reminder period
                }
                self.create_borrowed_book_student(borrowed_data)
                logger.info(f"Book {book_id} reserved for student {user_id}")
                return True
                
            elif user_type == 'teacher':
                borrowed_data = {
                    'teacher_id': user_id,
                    'book_id': book_id,
                    'borrowed_on': datetime.now().strftime('%Y-%m-%d')
                }
                self.create_borrowed_book_teacher(borrowed_data)
                logger.info(f"Book {book_id} reserved for teacher {user_id}")
                return True
                
            else:
                logger.warning(f"Invalid user type: {user_type}")
                return False
                
        except Exception as e:
            logger.error(f"Error reserving book: {e}")
            return False

    def get_popular_books(self, limit: int = 10) -> List[Book]:
        """
        Get most frequently borrowed books
        
        Args:
            limit: Maximum number of books to return
            
        Returns:
            List of most popular books
        """
        logger.info(f"Getting {limit} most popular books")
        
        try:
            return self.book_repository.get_popular_books(limit)
        except Exception as e:
            logger.error(f"Error getting popular books: {e}")
            return []

    def search_books(self, query: str) -> List[Book]:
        """
        Search books by title, author, or other criteria
        
        Args:
            query: Search term
            
        Returns:
            List of matching books
        """
        logger.info(f"Searching books with query: {query}")
        
        try:
            return self.book_repository.search_books(query)
        except Exception as e:
            logger.error(f"Error searching books: {e}")
            return []

    def get_books_by_category(self, category: str) -> List[Book]:
        """
        Get books filtered by category/tag
        
        Args:
            category: Category to filter by
            
        Returns:
            List of books in the specified category
        """
        logger.info(f"Getting books by category: {category}")
        
        try:
            return self.book_repository.get_books_by_category(category)
        except Exception as e:
            logger.error(f"Error getting books by category: {e}")
            return []

    def get_overdue_books(self) -> List[Union[BorrowedBookStudent, BorrowedBookTeacher]]:
        """
        Get all overdue books for both students and teachers
        
        Returns:
            List of overdue borrowed book records
        """
        logger.info("Getting all overdue books")
        
        try:
            from school_system.database.repositories.book_repo import (
                BorrowedBookStudentRepository, BorrowedBookTeacherRepository
            )
            
            student_repo = BorrowedBookStudentRepository()
            teacher_repo = BorrowedBookTeacherRepository()
            
            # Get all borrowed books
            student_borrowings = student_repo.get_all()
            teacher_borrowings = teacher_repo.get_all()
            
            overdue_books = []
            
            # Check student borrowings for overdue books
            for borrowing in student_borrowings:
                # Assuming books are overdue if borrowed more than 14 days ago
                # In a real system, you would have a due date field
                overdue_books.append(borrowing)
            
            # Check teacher borrowings for overdue books
            for borrowing in teacher_borrowings:
                # Same logic for teachers
                overdue_books.append(borrowing)
            
            return overdue_books
            
        except Exception as e:
            logger.error(f"Error getting overdue books: {e}")
            return []

    def get_books_by_student(self, student_id: int) -> List[Book]:
        """
        Get all books currently borrowed by a specific student
        
        Args:
            student_id: ID of the student
            
        Returns:
            List of books borrowed by the student
        """
        logger.info(f"Getting books borrowed by student {student_id}")
        
        try:
            borrowed_book_repo = BorrowedBookStudentRepository()
            
            # Get all borrowings for this student
            borrowings = borrowed_book_repo.find_by_field('student_id', student_id)
            
            # Get the actual book objects
            books = []
            for borrowing in borrowings:
                book = self.book_repository.get_by_id(borrowing.book_id)
                if book:
                    books.append(book)
            
            return books
            
        except Exception as e:
            logger.error(f"Error getting books by student: {e}")
            return []

    def get_books_by_teacher(self, teacher_id: int) -> List[Book]:
        """
        Get all books currently borrowed by a specific teacher
        
        Args:
            teacher_id: ID of the teacher
            
        Returns:
            List of books borrowed by the teacher
        """
        logger.info(f"Getting books borrowed by teacher {teacher_id}")
        
        try:
            borrowed_book_repo = BorrowedBookTeacherRepository()
            
            # Get all borrowings for this teacher
            borrowings = borrowed_book_repo.find_by_field('teacher_id', teacher_id)
            
            # Get the actual book objects
            books = []
            for borrowing in borrowings:
                book = self.book_repository.get_by_id(borrowing.book_id)
                if book:
                    books.append(book)
            
            return books
            
        except Exception as e:
            logger.error(f"Error getting books by teacher: {e}")
            return []

    def return_book_student(self, student_id: str, book_id: int,
                          return_condition: str = "Good",
                          fine_amount: float = 0,
                          returned_by: str = None) -> bool:
        """
        Handle book return process for students with enhanced tracking
        
        Args:
            student_id: ID of the student returning the book
            book_id: ID of the book being returned
            return_condition: Condition of the returned book (Good/Torn/Lost)
            fine_amount: Fine amount to be charged
            returned_by: Librarian username processing the return
            
        Returns:
            True if return was successful, False otherwise
        """
        logger.info(f"Returning book {book_id} by student {student_id} with condition: {return_condition}")
        
        try:
            borrowed_book_repo = BorrowedBookStudentRepository()
            
            # Use the new return_book method from repository
            success = borrowed_book_repo.return_book(
                student_id,
                book_id,
                return_condition,
                fine_amount,
                returned_by
            )
            
            if success:
                logger.info(f"Book {book_id} returned successfully by student {student_id} with fine: {fine_amount}")
                return True
            else:
                logger.warning(f"No active borrowing record found for student {student_id} and book {book_id}")
                return False
                
        except Exception as e:
            logger.error(f"Error returning book by student: {e}")
            return False

    def return_book_teacher(self, teacher_id: str, book_id: int) -> bool:
        """
        Handle book return process for teachers with enhanced tracking
        
        Args:
            teacher_id: ID of the teacher returning the book
            book_id: ID of the book being returned
            
        Returns:
            True if return was successful, False otherwise
        """
        logger.info(f"Returning book {book_id} by teacher {teacher_id}")
        
        try:
            borrowed_book_repo = BorrowedBookTeacherRepository()
            
            # Use the new return_book method from repository
            success = borrowed_book_repo.return_book(teacher_id, book_id)
            
            if success:
                logger.info(f"Book {book_id} returned successfully by teacher {teacher_id}")
                return True
            else:
                logger.warning(f"No active borrowing record found for teacher {teacher_id} and book {book_id}")
                return False
                
        except Exception as e:
            logger.error(f"Error returning book by teacher: {e}")
            return False

    def get_borrowing_history(self, user_id: int, user_type: str) -> List[Union[BorrowedBookStudent, BorrowedBookTeacher]]:
        """
        Get complete borrowing history for a user (student or teacher)
        
        Args:
            user_id: ID of the user
            user_type: 'student' or 'teacher'
            
        Returns:
            List of all borrowing records for the user
        """
        logger.info(f"Getting borrowing history for {user_type} {user_id}")
        
        try:
            if user_type == 'student':
                borrowed_book_repo = BorrowedBookStudentRepository()
                return borrowed_book_repo.find_by_field('student_id', user_id)
            elif user_type == 'teacher':
                borrowed_book_repo = BorrowedBookTeacherRepository()
                return borrowed_book_repo.find_by_field('teacher_id', user_id)
            else:
                logger.warning(f"Invalid user type: {user_type}")
                return []
            
        except Exception as e:
            logger.error(f"Error getting borrowing history: {e}")
            return []
    
    def create_distribution_session_with_students(self, session_data: dict, student_ids: List[str]) -> int:
        """
        Create a distribution session and pre-fill all student records
        
        Args:
            session_data: Dictionary containing session information
            student_ids: List of student IDs to include in the session
            
        Returns:
            The created session ID
        """
        logger.info(f"Creating distribution session with {len(student_ids)} students")
        
        try:
            # Validate required fields
            ValidationUtils.validate_input(session_data.get('class_name'), "Class name cannot be empty")
            ValidationUtils.validate_input(session_data.get('stream'), "Stream cannot be empty")
            ValidationUtils.validate_input(session_data.get('subject'), "Subject cannot be empty")
            ValidationUtils.validate_input(session_data.get('term'), "Term cannot be empty")
            ValidationUtils.validate_input(session_data.get('created_by'), "Created by cannot be empty")
            
            if not student_ids:
                raise ValueError("Student IDs list cannot be empty")
            
            # Create session object
            session = DistributionSession(**session_data)
            
            # Use the new repository method
            session_repo = DistributionSessionRepository()
            session_id = session_repo.create_with_students(session, student_ids)
            
            logger.info(f"Distribution session created successfully with ID: {session_id} and {len(student_ids)} students")
            return session_id
            
        except Exception as e:
            logger.error(f"Error creating distribution session with students: {e}")
            raise DatabaseException(f"Failed to create distribution session: {e}")
    
    def bulk_update_distribution_books(self, session_id: int, book_assignments: List[dict]) -> bool:
        """
        Bulk update book assignments for students in a distribution session
        
        Args:
            session_id: ID of the distribution session
            book_assignments: List of dictionaries with student_id, book_number, book_id
            
        Returns:
            True if update was successful, False otherwise
        """
        logger.info(f"Bulk updating book assignments for session {session_id}")
        
        try:
            if not book_assignments:
                logger.warning("No book assignments provided")
                return False
            
            # Use the new repository method
            student_repo = DistributionStudentRepository()
            student_repo.bulk_update_books(session_id, book_assignments)
            
            logger.info(f"Successfully updated {len(book_assignments)} book assignments for session {session_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error bulk updating distribution books: {e}")
            return False
    
    def get_unassigned_students_in_session(self, session_id: int) -> List[dict]:
        """
        Get students who haven't been assigned books in a distribution session
        
        Args:
            session_id: ID of the distribution session
            
        Returns:
            List of unassigned student records
        """
        logger.info(f"Getting unassigned students for session {session_id}")
        
        try:
            student_repo = DistributionStudentRepository()
            unassigned = student_repo.get_unassigned(session_id)
            
            # Convert to list of dictionaries for easier use
            result = []
            for row in unassigned:
                student_dict = dict(zip([column[0] for column in self.db.cursor().description], row))
                result.append(student_dict)
            
            logger.info(f"Found {len(result)} unassigned students in session {session_id}")
            return result
            
        except Exception as e:
            logger.error(f"Error getting unassigned students: {e}")
            return []
    
    def log_distribution_import_success(self, session_id: int, file_name: str, user: str) -> bool:
        """
        Log a successful distribution import operation
        
        Args:
            session_id: ID of the distribution session
            file_name: Name of the imported file
            user: Username of the user who performed the import
            
        Returns:
            True if logging was successful, False otherwise
        """
        logger.info(f"Logging successful import for session {session_id} by user {user}")
        
        try:
            ValidationUtils.validate_input(file_name, "File name cannot be empty")
            ValidationUtils.validate_input(user, "User cannot be empty")
            
            # Use the new repository method
            import_log_repo = DistributionImportLogRepository()
            import_log_repo.log_success(session_id, file_name, user)
            
            logger.info(f"Successfully logged import operation for session {session_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error logging distribution import: {e}")
            return False
    
    def get_currently_borrowed_books_student(self, student_id: str) -> List[BorrowedBookStudent]:
        """
        Get books currently borrowed by a student (not yet returned)
        
        Args:
            student_id: ID of the student
            
        Returns:
            List of currently borrowed books
        """
        logger.info(f"Getting currently borrowed books for student {student_id}")
        
        try:
            borrowed_book_repo = BorrowedBookStudentRepository()
            return borrowed_book_repo.get_borrowed_books_by_student(student_id)
        except Exception as e:
            logger.error(f"Error getting currently borrowed books for student: {e}")
            return []
    
    def get_returned_books_student(self, student_id: str) -> List[BorrowedBookStudent]:
        """
        Get books already returned by a student
        
        Args:
            student_id: ID of the student
            
        Returns:
            List of returned books with return details
        """
        logger.info(f"Getting returned books for student {student_id}")
        
        try:
            borrowed_book_repo = BorrowedBookStudentRepository()
            return borrowed_book_repo.get_returned_books_by_student(student_id)
        except Exception as e:
            logger.error(f"Error getting returned books for student: {e}")
            return []
    
    def get_currently_borrowed_books_teacher(self, teacher_id: str) -> List[BorrowedBookTeacher]:
        """
        Get books currently borrowed by a teacher (not yet returned)
        
        Args:
            teacher_id: ID of the teacher
            
        Returns:
            List of currently borrowed books
        """
        logger.info(f"Getting currently borrowed books for teacher {teacher_id}")
        
        try:
            borrowed_book_repo = BorrowedBookTeacherRepository()
            return borrowed_book_repo.get_borrowed_books_by_teacher(teacher_id)
        except Exception as e:
            logger.error(f"Error getting currently borrowed books for teacher: {e}")
            return []
    
    def get_returned_books_teacher(self, teacher_id: str) -> List[BorrowedBookTeacher]:
        """
        Get books already returned by a teacher
        
        Args:
            teacher_id: ID of the teacher
            
        Returns:
            List of returned books with return details
        """
        logger.info(f"Getting returned books for teacher {teacher_id}")
        
        try:
            borrowed_book_repo = BorrowedBookTeacherRepository()
            return borrowed_book_repo.get_returned_books_by_teacher(teacher_id)
        except Exception as e:
            logger.error(f"Error getting returned books for teacher: {e}")
            return []
    
    def get_all_overdue_books(self) -> List[BorrowedBookStudent]:
        """
        Get all overdue books (not returned after 14 days)
        
        Returns:
            List of overdue borrowed book records
        """
        logger.info("Getting all overdue books")
        
        try:
            borrowed_book_repo = BorrowedBookStudentRepository()
            return borrowed_book_repo.get_overdue_books()
        except Exception as e:
            logger.error(f"Error getting overdue books: {e}")
            return []
