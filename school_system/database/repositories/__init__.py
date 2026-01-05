"""
Repository classes for database operations.
"""

from .base import (
    BaseRepository,
    StudentRepository,
    TeacherRepository,
    BookRepository,
    UserRepository,
    # Student-related repositories
    ReamEntryRepository,
    TotalReamsRepository,
    # Book-related repositories
    BookTagRepository,
    BorrowedBookStudentRepository,
    BorrowedBookTeacherRepository,
    QRBookRepository,
    QRBorrowLogRepository,
    DistributionSessionRepository,
    DistributionStudentRepository,
    DistributionImportLogRepository,
    # User-related repositories
    UserSettingRepository,
    ShortFormMappingRepository,
    # Furniture-related repositories
    ChairRepository,
    LockerRepository,
    FurnitureCategoryRepository,
    LockerAssignmentRepository,
    ChairAssignmentRepository
)

__all__ = [
    'BaseRepository',
    'StudentRepository',
    'TeacherRepository',
    'BookRepository',
    'UserRepository',
    # Student-related repositories
    'ReamEntryRepository',
    'TotalReamsRepository',
    # Book-related repositories
    'BookTagRepository',
    'BorrowedBookStudentRepository',
    'BorrowedBookTeacherRepository',
    'QRBookRepository',
    'QRBorrowLogRepository',
    'DistributionSessionRepository',
    'DistributionStudentRepository',
    'DistributionImportLogRepository',
    # User-related repositories
    'UserSettingRepository',
    'ShortFormMappingRepository',
    # Furniture-related repositories
    'ChairRepository',
    'LockerRepository',
    'FurnitureCategoryRepository',
    'LockerAssignmentRepository',
    'ChairAssignmentRepository'
]
