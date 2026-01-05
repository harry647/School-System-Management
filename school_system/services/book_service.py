"""
Book service for managing book-related operations.
"""

from typing import List, Optional
from school_system.config.logging import logger
from school_system.config.settings import Settings
from school_system.core.exceptions import DatabaseException
from school_system.core.utils import ValidationUtils
from school_system.services.import_export_service import ImportExportService

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

    def get_all_books(self) -> List[Book]:
        """
        Retrieve all books.

        Returns:
            A list of all Book objects.
        """
        return self.book_repository.get_all()

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
        
        book = Book(**book_data)
        created_book = self.book_repository.create(book)
        logger.info(f"Book created successfully with ID: {created_book.id}")
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