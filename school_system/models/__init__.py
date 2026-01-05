# Initialize the models package
# This file can be used to import all models for easier access
from .base import BaseModel
from .student import Student, ReamEntry, TotalReams
from .teacher import Teacher
from .book import Book, BookTag, BorrowedBookStudent, BorrowedBookTeacher, QRBook, QRBorrowLog, DistributionSession, DistributionStudent, DistributionImportLog
from .furniture import Chair, Locker, FurnitureCategory, LockerAssignment, ChairAssignment
from .user import User, UserSetting, ShortFormMapping
from .base import get_db_session
