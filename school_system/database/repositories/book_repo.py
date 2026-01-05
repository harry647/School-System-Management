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
    
    def get_borrowed_books_by_student(self, student_id: str) -> List[BorrowedBookStudent]:
        """Get all books currently borrowed by a student."""
        try:
            cursor = self.db.cursor()
            cursor.execute("""
                SELECT * FROM borrowed_books_student
                WHERE student_id = ? AND returned_on IS NULL
            """, (student_id,))
            results = cursor.fetchall()
            return [self.model(**dict(zip([column[0] for column in cursor.description], row))) for row in results]
        except Exception as e:
            raise DatabaseException(f"Error retrieving borrowed books for student: {e}")
    
    def get_returned_books_by_student(self, student_id: str) -> List[BorrowedBookStudent]:
        """Get all books returned by a student."""
        try:
            cursor = self.db.cursor()
            cursor.execute("""
                SELECT * FROM borrowed_books_student
                WHERE student_id = ? AND returned_on IS NOT NULL
            """, (student_id,))
            results = cursor.fetchall()
            return [self.model(**dict(zip([column[0] for column in cursor.description], row))) for row in results]
        except Exception as e:
            raise DatabaseException(f"Error retrieving returned books for student: {e}")
    
    def get_overdue_books(self, days_overdue: int = 14) -> List[BorrowedBookStudent]:
        """Get all overdue books (not returned after the due date)."""
        try:
            cursor = self.db.cursor()
            cursor.execute("""
                SELECT * FROM borrowed_books_student
                WHERE returned_on IS NULL
                AND borrowed_on < DATE('now', ?)
            """, (f'-{days_overdue} days',))
            results = cursor.fetchall()
            return [self.model(**dict(zip([column[0] for column in cursor.description], row))) for row in results]
        except Exception as e:
            raise DatabaseException(f"Error retrieving overdue books: {e}")
    
    def return_book(self, student_id: str, book_id: int, return_condition: str = "Good",
                   fine_amount: float = 0, returned_by: str = None) -> bool:
        """Mark a book as returned by a student."""
        try:
            from datetime import date
            cursor = self.db.cursor()
            
            # Update the borrow record
            cursor.execute("""
                UPDATE borrowed_books_student
                SET returned_on = ?, return_condition = ?, fine_amount = ?, returned_by = ?
                WHERE student_id = ? AND book_id = ? AND returned_on IS NULL
            """, (date.today(), return_condition, fine_amount, returned_by, student_id, book_id))
            
            if cursor.rowcount == 0:
                return False  # No book was updated (already returned or doesn't exist)
            
            # Mark the book as available
            cursor.execute("UPDATE books SET available = 1 WHERE id = ?", (book_id,))
            
            self.db.commit()
            return True
        except Exception as e:
            self.db.rollback()
            raise DatabaseException(f"Error returning book: {e}")


class BorrowedBookTeacherRepository(BaseRepository):
    """Repository for borrowed book teacher operations."""

    def __init__(self):
        super().__init__(BorrowedBookTeacher)
    
    def get_borrowed_books_by_teacher(self, teacher_id: str) -> List[BorrowedBookTeacher]:
        """Get all books currently borrowed by a teacher."""
        try:
            cursor = self.db.cursor()
            cursor.execute("""
                SELECT * FROM borrowed_books_teacher
                WHERE teacher_id = ? AND returned_on IS NULL
            """, (teacher_id,))
            results = cursor.fetchall()
            return [self.model(**dict(zip([column[0] for column in cursor.description], row))) for row in results]
        except Exception as e:
            raise DatabaseException(f"Error retrieving borrowed books for teacher: {e}")
    
    def get_returned_books_by_teacher(self, teacher_id: str) -> List[BorrowedBookTeacher]:
        """Get all books returned by a teacher."""
        try:
            cursor = self.db.cursor()
            cursor.execute("""
                SELECT * FROM borrowed_books_teacher
                WHERE teacher_id = ? AND returned_on IS NOT NULL
            """, (teacher_id,))
            results = cursor.fetchall()
            return [self.model(**dict(zip([column[0] for column in cursor.description], row))) for row in results]
        except Exception as e:
            raise DatabaseException(f"Error retrieving returned books for teacher: {e}")
    
    def return_book(self, teacher_id: str, book_id: int) -> bool:
        """Mark a book as returned by a teacher."""
        try:
            from datetime import date
            cursor = self.db.cursor()
            
            # Update the borrow record
            cursor.execute("""
                UPDATE borrowed_books_teacher
                SET returned_on = ?
                WHERE teacher_id = ? AND book_id = ? AND returned_on IS NULL
            """, (date.today(), teacher_id, book_id))
            
            if cursor.rowcount == 0:
                return False  # No book was updated (already returned or doesn't exist)
            
            # Mark the book as available
            cursor.execute("UPDATE books SET available = 1 WHERE id = ?", (book_id,))
            
            self.db.commit()
            return True
        except Exception as e:
            self.db.rollback()
            raise DatabaseException(f"Error returning book: {e}")


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