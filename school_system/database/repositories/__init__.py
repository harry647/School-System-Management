"""
Repository classes for database operations.
"""

from .base import BaseRepository
from .user_repo import UserRepository, UserSettingRepository, ShortFormMappingRepository
from .student_repo import StudentRepository, ReamEntryRepository, TotalReamsRepository
from .teacher_repo import TeacherRepository
from .book_repo import (
    BookRepository, BookTagRepository, BorrowedBookStudentRepository,
    BorrowedBookTeacherRepository, QRBookRepository, QRBorrowLogRepository,
    DistributionSessionRepository, DistributionStudentRepository, DistributionImportLogRepository
)
from .furniture_repo import (
    ChairRepository, LockerRepository, FurnitureCategoryRepository,
    LockerAssignmentRepository, ChairAssignmentRepository
)
from .session_repo import UserSessionRepository
from .audit_log_repo import AuditLogRepository
from .user_activity_repo import UserActivityRepository

__all__ = [
    'BaseRepository',
    'UserRepository', 'UserSettingRepository', 'ShortFormMappingRepository',
    'StudentRepository', 'ReamEntryRepository', 'TotalReamsRepository',
    'TeacherRepository',
    'BookRepository', 'BookTagRepository', 'BorrowedBookStudentRepository',
    'BorrowedBookTeacherRepository', 'QRBookRepository', 'QRBorrowLogRepository',
    'DistributionSessionRepository', 'DistributionStudentRepository', 'DistributionImportLogRepository',
    'ChairRepository', 'LockerRepository', 'FurnitureCategoryRepository',
    'LockerAssignmentRepository', 'ChairAssignmentRepository',
    'UserSessionRepository', 'AuditLogRepository', 'UserActivityRepository'
]
