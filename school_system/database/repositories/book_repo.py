"""
Repository for book operations.
"""

from .base import BaseRepository
from ...models.book import Book, BookTag, BorrowedBookStudent, BorrowedBookTeacher, QRBook, QRBorrowLog, DistributionSession, DistributionStudent, DistributionImportLog
from ...core.exceptions import DatabaseException


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

    def get_available_books(self) -> List[Book]:
        """Get only books that are available for borrowing"""
        try:
            cursor = self.db.cursor()
            cursor.execute("SELECT * FROM books WHERE available = 1")
            results = cursor.fetchall()
            return [self.model(**dict(zip([column[0] for column in cursor.description], row))) for row in results]
        except Exception as e:
            raise DatabaseException(f"Error retrieving available books: {e}")

    def get_books_by_category(self, category: str) -> List[Book]:
        """Get books filtered by category"""
        try:
            cursor = self.db.cursor()
            cursor.execute("SELECT * FROM books WHERE category = ?", (category,))
            results = cursor.fetchall()
            return [self.model(**dict(zip([column[0] for column in cursor.description], row))) for row in results]
        except Exception as e:
            raise DatabaseException(f"Error retrieving books by category: {e}")

    def search_books(self, query: str) -> List[Book]:
        """Search books by title, author, or ISBN"""
        try:
            cursor = self.db.cursor()
            search_query = f"%{query}%"
            cursor.execute("""
                SELECT * FROM books
                WHERE title LIKE ?
                OR author LIKE ?
                OR isbn LIKE ?
            """, (search_query, search_query, search_query))
            results = cursor.fetchall()
            return [self.model(**dict(zip([column[0] for column in cursor.description], row))) for row in results]
        except Exception as e:
            raise DatabaseException(f"Error searching books: {e}")

    def get_popular_books(self, limit: int = 10) -> List[Book]:
        """Get most frequently borrowed books"""
        try:
            cursor = self.db.cursor()
            # Count borrowings from both student and teacher tables
            cursor.execute("""
                SELECT b.*,
                (SELECT COUNT(*) FROM borrowed_books_student WHERE book_id = b.id) +
                (SELECT COUNT(*) FROM borrowed_books_teacher WHERE book_id = b.id) as borrow_count
                FROM books b
                WHERE borrow_count > 0
                ORDER BY borrow_count DESC
                LIMIT ?
            """, (limit,))
            results = cursor.fetchall()
            return [self.model(**dict(zip([column[0] for column in cursor.description], row))) for row in results]
        except Exception as e:
            raise DatabaseException(f"Error retrieving popular books: {e}")


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