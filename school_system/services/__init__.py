# Initialize the services package
# This file can be used to import all services for easier access

from .auth_service import AuthService
from .student_service import StudentService
from .teacher_service import TeacherService
from .book_service import BookService
from .furniture_service import FurnitureService
from .qr_service import QRService
from .report_service import ReportService
from .import_export_service import ImportExportService
from .notification_service import NotificationService

__all__ = [
    'AuthService',
    'StudentService',
    'TeacherService',
    'BookService',
    'FurnitureService',
    'QRService',
    'ReportService',
    'ImportExportService',
    'NotificationService'
]
