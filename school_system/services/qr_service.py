"""
QR service for managing QR code-related operations.
"""

from typing import Optional
from school_system.config.logging import logger
from school_system.config.settings import Settings
from school_system.core.exceptions import DatabaseException
from school_system.core.utils import ValidationUtils
from school_system.models.book import QRBook
from school_system.database.repositories.book_repo import QRBookRepository


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