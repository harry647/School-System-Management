"""
QR service for managing QR code-related operations.
"""

from typing import Optional
from school_system.config.logging import logger
from school_system.config.settings import Settings
from school_system.core.exceptions import DatabaseException
from school_system.core.utils import validate_input
from school_system.models.qr import QRCode
from school_system.database.repositories.qr_repository import QRRepository


class QRService:
    """Service for managing QR code-related operations."""

    def __init__(self):
        self.qr_repository = QRRepository()

    def generate_qr_code(self, data: str) -> str:
        """
        Generate a QR code for the given data.

        Args:
            data: The data to encode in the QR code.

        Returns:
            The generated QR code as a string.
        """
        logger.info(f"Generating QR code for data: {data}")
        validate_input(data, "Data for QR code cannot be empty")
        
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

    def save_qr_code(self, qr_code: str, metadata: dict) -> QRCode:
        """
        Save a QR code to the database.

        Args:
            qr_code: The QR code to save.
            metadata: Additional metadata for the QR code.

        Returns:
            The saved QRCode object.
        """
        qr = QRCode(qr_code=qr_code, **metadata)
        return self.qr_repository.create(qr)

    def get_qr_code_by_id(self, qr_id: int) -> Optional[QRCode]:
        """
        Retrieve a QR code by its ID.

        Args:
            qr_id: The ID of the QR code.

        Returns:
            The QRCode object if found, otherwise None.
        """
        return self.qr_repository.get_by_id(qr_id)