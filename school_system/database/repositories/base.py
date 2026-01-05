from typing import List, Optional, Type, TypeVar, Generic
from ...core.exceptions import DatabaseException
from ...core.validators import StudentValidator, TeacherValidator, BookValidator, UserValidator

T = TypeVar('T')


class BaseRepository(Generic[T]):
    """Base repository class implementing CRUD operations."""
    
    def __init__(self, model: Type[T]):
        self.model = model
        self._db = None  # Lazy initialization
    
    @property
    def db(self):
        """Lazy import database connection to avoid circular imports."""
        if self._db is None:
            from ..connection import get_db_session
            self._db = get_db_session()
        return self._db
    
    def get_by_id(self, id: int) -> Optional[T]:
        """Get entity by ID."""
        try:
            cursor = self.db.cursor()
            cursor.execute(f"SELECT * FROM {self.model.__tablename__} WHERE id = ?", (id,))
            result = cursor.fetchone()
            if result:
                return self.model(**dict(zip([column[0] for column in cursor.description], result)))
            return None
        except Exception as e:
            raise DatabaseException(f"Error retrieving entity by ID: {e}")

    def get_all(self) -> List[T]:
        """Get all entities."""
        try:
            cursor = self.db.cursor()
            cursor.execute(f"SELECT * FROM {self.model.__tablename__}")
            results = cursor.fetchall()
            return [self.model(**dict(zip([column[0] for column in cursor.description], row))) for row in results]
        except Exception as e:
            raise DatabaseException(f"Error retrieving all entities: {e}")

    def create(self, **kwargs) -> T:
        """Create a new entity."""
        try:
            cursor = self.db.cursor()
            columns = ', '.join(kwargs.keys())
            placeholders = ', '.join(['?'] * len(kwargs))
            cursor.execute(f"INSERT INTO {self.model.__tablename__} ({columns}) VALUES ({placeholders})", tuple(kwargs.values()))
            self.db.commit()
            return self.model(**kwargs)
        except Exception as e:
            raise DatabaseException(f"Error creating entity: {e}")

    def update(self, id: int, **kwargs) -> Optional[T]:
        """Update an existing entity."""
        try:
            cursor = self.db.cursor()
            set_clause = ', '.join([f"{key} = ?" for key in kwargs.keys()])
            cursor.execute(f"UPDATE {self.model.__tablename__} SET {set_clause} WHERE id = ?", (*kwargs.values(), id))
            self.db.commit()
            return self.get_by_id(id)
        except Exception as e:
            raise DatabaseException(f"Error updating entity: {e}")

    def delete(self, id: int) -> bool:
        """Delete an entity."""
        try:
            cursor = self.db.cursor()
            cursor.execute(f"DELETE FROM {self.model.__tablename__} WHERE id = ?", (id,))
            self.db.commit()
            return cursor.rowcount > 0
        except Exception as e:
            raise DatabaseException(f"Error deleting entity: {e}")

    def find_by_field(self, field_name: str, value) -> List[T]:
        """Find entities by a specific field."""
        try:
            cursor = self.db.cursor()
            cursor.execute(f"SELECT * FROM {self.model.__tablename__} WHERE {field_name} = ?", (value,))
            results = cursor.fetchall()
            return [self.model(**dict(zip([column[0] for column in cursor.description], row))) for row in results]
        except Exception as e:
            raise DatabaseException(f"Error finding entities by field: {e}")

    def count(self) -> int:
        """Count all entities."""
        try:
            cursor = self.db.cursor()
            cursor.execute(f"SELECT COUNT(*) FROM {self.model.__tablename__}")
            return cursor.fetchone()[0]
        except Exception as e:
            raise DatabaseException(f"Error counting entities: {e}")


# Specific repository classes for different entities
class StudentRepository(BaseRepository):
    """Repository for student operations."""
    
    def __init__(self):
        from ...models.student import Student
        super().__init__(Student)
    
    def validate_student_data(self, student_id: str, name: str, stream: str) -> bool:
        """Validate student data before operations."""
        try:
            StudentValidator.validate_student_id(student_id)
            StudentValidator.validate_name(name)
            # Add stream validation if available
            return True
        except Exception as e:
            raise DatabaseException(f"Student validation failed: {e}")


class TeacherRepository(BaseRepository):
    """Repository for teacher operations."""
    
    def __init__(self):
        from ...models.teacher import Teacher
        super().__init__(Teacher)
    
    def validate_teacher_data(self, teacher_id: str, teacher_name: str) -> bool:
        """Validate teacher data before operations."""
        try:
            TeacherValidator.validate_teacher_id(teacher_id)
            TeacherValidator.validate_name(teacher_name)
            return True
        except Exception as e:
            raise DatabaseException(f"Teacher validation failed: {e}")


class BookRepository(BaseRepository):
    """Repository for book operations."""
    
    def __init__(self):
        from ...models.book import Book
        super().__init__(Book)
    
    def validate_book_data(self, book_number: str, available: bool = True) -> bool:
        """Validate book data before operations."""
        try:
            BookValidator.validate_book_number(book_number)
            return True
        except Exception as e:
            raise DatabaseException(f"Book validation failed: {e}")


class UserRepository(BaseRepository):
    """Repository for user operations."""
    
    def __init__(self):
        from ...models.user import User
        super().__init__(User)
    
    def validate_user_data(self, username: str, password: str) -> bool:
        """Validate user data before operations."""
        try:
            UserValidator.validate_username(username)
            UserValidator.validate_password(password)
            return True
        except Exception as e:
            raise DatabaseException(f"User validation failed: {e}")


# Student-related repositories
class ReamEntryRepository(BaseRepository):
    """Repository for ream entry operations."""
    
    def __init__(self):
        from ...models.student import ReamEntry
        super().__init__(ReamEntry)


class TotalReamsRepository(BaseRepository):
    """Repository for total reams operations."""
    
    def __init__(self):
        from ...models.student import TotalReams
        super().__init__(TotalReams)


# Book-related repositories
class BookTagRepository(BaseRepository):
    """Repository for book tag operations."""
    
    def __init__(self):
        from ...models.book import BookTag
        super().__init__(BookTag)


class BorrowedBookStudentRepository(BaseRepository):
    """Repository for borrowed book student operations."""
    
    def __init__(self):
        from ...models.book import BorrowedBookStudent
        super().__init__(BorrowedBookStudent)


class BorrowedBookTeacherRepository(BaseRepository):
    """Repository for borrowed book teacher operations."""
    
    def __init__(self):
        from ...models.book import BorrowedBookTeacher
        super().__init__(BorrowedBookTeacher)


class QRBookRepository(BaseRepository):
    """Repository for QR book operations."""
    
    def __init__(self):
        from ...models.book import QRBook
        super().__init__(QRBook)


class QRBorrowLogRepository(BaseRepository):
    """Repository for QR borrow log operations."""
    
    def __init__(self):
        from ...models.book import QRBorrowLog
        super().__init__(QRBorrowLog)


class DistributionSessionRepository(BaseRepository):
    """Repository for distribution session operations."""
    
    def __init__(self):
        from ...models.book import DistributionSession
        super().__init__(DistributionSession)


class DistributionStudentRepository(BaseRepository):
    """Repository for distribution student operations."""
    
    def __init__(self):
        from ...models.book import DistributionStudent
        super().__init__(DistributionStudent)


class DistributionImportLogRepository(BaseRepository):
    """Repository for distribution import log operations."""
    
    def __init__(self):
        from ...models.book import DistributionImportLog
        super().__init__(DistributionImportLog)


# User-related repositories
class UserSettingRepository(BaseRepository):
    """Repository for user setting operations."""
    
    def __init__(self):
        from ...models.user import UserSetting
        super().__init__(UserSetting)


class ShortFormMappingRepository(BaseRepository):
    """Repository for short form mapping operations."""
    
    def __init__(self):
        from ...models.user import ShortFormMapping
        super().__init__(ShortFormMapping)


# Furniture-related repositories
class ChairRepository(BaseRepository):
    """Repository for chair operations."""
    
    def __init__(self):
        from ...models.furniture import Chair
        super().__init__(Chair)


class LockerRepository(BaseRepository):
    """Repository for locker operations."""
    
    def __init__(self):
        from ...models.furniture import Locker
        super().__init__(Locker)


class FurnitureCategoryRepository(BaseRepository):
    """Repository for furniture category operations."""
    
    def __init__(self):
        from ...models.furniture import FurnitureCategory
        super().__init__(FurnitureCategory)


class LockerAssignmentRepository(BaseRepository):
    """Repository for locker assignment operations."""
    
    def __init__(self):
        from ...models.furniture import LockerAssignment
        super().__init__(LockerAssignment)


class ChairAssignmentRepository(BaseRepository):
    """Repository for chair assignment operations."""
    
    def __init__(self):
        from ...models.furniture import ChairAssignment
        super().__init__(ChairAssignment)