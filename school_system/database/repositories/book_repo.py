"""
Repository for book operations.
"""

from .base import BaseRepository
from ...models.book import Book, BookTag, BorrowedBookStudent, BorrowedBookTeacher, QRBook, QRBorrowLog, DistributionSession, DistributionStudent, DistributionImportLog


class BookRepository(BaseRepository):
    """Repository for book operations."""

    def __init__(self):
        super().__init__(Book)

    def validate_book_data(self, book_number: str, available: bool = True) -> bool:
        """Validate book data before operations."""
        try:
            from ...core.validators import BookValidator
            BookValidator.validate_book_number(book_number)
            return True
        except Exception as e:
            raise Exception(f"Book validation failed: {e}")


class BookTagRepository(BaseRepository):
    """Repository for book tag operations."""

    def __init__(self):
        super().__init__(BookTag)


class BorrowedBookStudentRepository(BaseRepository):
    """Repository for borrowed book student operations."""

    def __init__(self):
        super().__init__(BorrowedBookStudent)


class BorrowedBookTeacherRepository(BaseRepository):
    """Repository for borrowed book teacher operations."""

    def __init__(self):
        super().__init__(BorrowedBookTeacher)


class QRBookRepository(BaseRepository):
    """Repository for QR book operations."""

    def __init__(self):
        super().__init__(QRBook)


class QRBorrowLogRepository(BaseRepository):
    """Repository for QR borrow log operations."""

    def __init__(self):
        super().__init__(QRBorrowLog)


class DistributionSessionRepository(BaseRepository):
    """Repository for distribution session operations."""

    def __init__(self):
        super().__init__(DistributionSession)


class DistributionStudentRepository(BaseRepository):
    """Repository for distribution student operations."""

    def __init__(self):
        super().__init__(DistributionStudent)


class DistributionImportLogRepository(BaseRepository):
    """Repository for distribution import log operations."""

    def __init__(self):
        super().__init__(DistributionImportLog)