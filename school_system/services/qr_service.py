"""
QR service for managing QR code-related operations.
"""

from typing import Optional
from school_system.config.logging import logger
from school_system.config.settings import Settings
from school_system.core.exceptions import DatabaseException
from school_system.core.utils import ValidationUtils
from school_system.models.book import QRBook, QRBorrowLog
from school_system.database.repositories.book_repo import QRBookRepository, QRBorrowLogRepository


class QRService:
    """Service for managing QR code-related operations."""
 
    def __init__(self):
        self.qr_book_repository = QRBookRepository()

    def generate_qr_code(self, data: str) -> str:
        """
        Generate a QR code for the given data.

        Args:
            data: The data to encode in the QR code.

        Returns:
            The generated QR code as a string.
        """
        logger.info(f"Generating QR code for data: {data}")
        ValidationUtils.validate_input(data, "Data for QR code cannot be empty")
        
        # Logic to generate QR code
        qr_code = self._generate_qr(data)
        logger.info(f"QR code generated successfully: {qr_code}")
        return qr_code

    def _generate_qr(self, data: str) -> str:
        """
        Internal method to generate QR code.

        Args:
            data: The data to encode.

        Returns:
            The generated QR code.
        """
        # Placeholder for QR generation logic
        return f"QR_CODE_{data}"

    def save_qr_book(self, qr_book: str, metadata: dict) -> QRBook:
        """
        Save a QR book to the database.

        Args:
            qr_book: The QR book to save.
            metadata: Additional metadata for the QR book.

        Returns:
            The saved QRBook object.
        """
        qr = QRBook(qr_book=qr_book, **metadata)
        return self.qr_book_repository.create(qr)
 
    def get_qr_book_by_id(self, qr_id: int) -> Optional[QRBook]:
        """
        Retrieve a QR book by its ID.

        Args:
            qr_id: The ID of the QR book.

        Returns:
            The QRBook object if found, otherwise None.
        """
        return self.qr_book_repository.get_by_id(qr_id)

    def get_all_qr_books(self) -> List[QRBook]:
        """
        Retrieve all QR books.

        Returns:
            A list of all QRBook objects.
        """
        return self.qr_book_repository.get_all()

    def create_qr_book(self, qr_book_data: dict) -> QRBook:
        """
        Create a new QR book.

        Args:
            qr_book_data: A dictionary containing QR book data.

        Returns:
            The created QRBook object.
        """
        logger.info(f"Creating a new QR book with data: {qr_book_data}")
        ValidationUtils.validate_input(qr_book_data.get('book_number'), "Book number cannot be empty")

        qr_book = QRBook(**qr_book_data)
        created_qr_book = self.qr_book_repository.create(qr_book)
        logger.info(f"QR book created successfully with ID: {created_qr_book.book_number}")
        return created_qr_book

    def update_qr_book(self, book_number: int, qr_book_data: dict) -> Optional[QRBook]:
        """
        Update an existing QR book.

        Args:
            book_number: The book number of the QR book to update.
            qr_book_data: A dictionary containing updated QR book data.

        Returns:
            The updated QRBook object if successful, otherwise None.
        """
        qr_book = self.qr_book_repository.get_by_id(book_number)
        if not qr_book:
            return None

        for key, value in qr_book_data.items():
            setattr(qr_book, key, value)

        return self.qr_book_repository.update(qr_book)

    def delete_qr_book(self, book_number: int) -> bool:
        """
        Delete a QR book.

        Args:
            book_number: The book number of the QR book to delete.

        Returns:
            True if the QR book was deleted, otherwise False.
        """
        qr_book = self.qr_book_repository.get_by_id(book_number)
        if not qr_book:
            return False

        self.qr_book_repository.delete(qr_book)
        return True

    def get_all_qr_borrow_logs(self) -> List[QRBorrowLog]:
        """
        Retrieve all QR borrow logs.

        Returns:
            A list of all QRBorrowLog objects.
        """
        qr_borrow_log_repository = QRBorrowLogRepository()
        return qr_borrow_log_repository.get_all()

    def get_qr_borrow_log_by_id(self, book_number: int) -> Optional[QRBorrowLog]:
        """
        Retrieve a QR borrow log by book number.

        Args:
            book_number: The book number of the QR borrow log.

        Returns:
            The QRBorrowLog object if found, otherwise None.
        """
        qr_borrow_log_repository = QRBorrowLogRepository()
        return qr_borrow_log_repository.get_by_id(book_number)

    def create_qr_borrow_log(self, borrow_log_data: dict) -> QRBorrowLog:
        """
        Create a new QR borrow log.

        Args:
            borrow_log_data: A dictionary containing QR borrow log data.

        Returns:
            The created QRBorrowLog object.
        """
        logger.info(f"Creating a new QR borrow log with data: {borrow_log_data}")
        ValidationUtils.validate_input(borrow_log_data.get('book_number'), "Book number cannot be empty")
        ValidationUtils.validate_input(borrow_log_data.get('student_id'), "Student ID cannot be empty")

        qr_borrow_log = QRBorrowLog(**borrow_log_data)
        qr_borrow_log_repository = QRBorrowLogRepository()
        created_log = qr_borrow_log_repository.create(qr_borrow_log)
        logger.info(f"QR borrow log created successfully for book number: {created_log.book_number}")
        return created_log

    def update_qr_borrow_log(self, book_number: int, borrow_log_data: dict) -> Optional[QRBorrowLog]:
        """
        Update an existing QR borrow log.

        Args:
            book_number: The book number of the QR borrow log to update.
            borrow_log_data: A dictionary containing updated QR borrow log data.

        Returns:
            The updated QRBorrowLog object if successful, otherwise None.
        """
        qr_borrow_log_repository = QRBorrowLogRepository()
        qr_borrow_log = qr_borrow_log_repository.get_by_id(book_number)
        if not qr_borrow_log:
            return None

        for key, value in borrow_log_data.items():
            setattr(qr_borrow_log, key, value)

        return qr_borrow_log_repository.update(qr_borrow_log)

    def delete_qr_borrow_log(self, book_number: int) -> bool:
        """
        Delete a QR borrow log.

        Args:
            book_number: The book number of the QR borrow log to delete.

        Returns:
            True if the QR borrow log was deleted, otherwise False.
        """
        qr_borrow_log_repository = QRBorrowLogRepository()
        qr_borrow_log = qr_borrow_log_repository.get_by_id(book_number)
        if not qr_borrow_log:
            return False

        qr_borrow_log_repository.delete(qr_borrow_log)
        return True