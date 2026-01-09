# Initialization file for the windows module

from school_system.gui.windows.login_window import LoginWindow
from school_system.gui.windows.main_window import MainWindow
from school_system.gui.windows.user_window.user_window import UserWindow
from school_system.gui.windows.book_window.book_window import BookWindow
from school_system.gui.windows.student_window.student_window import StudentWindow
from school_system.gui.windows.teacher_window.teacher_window import TeacherWindow
from school_system.gui.windows.furniture_window.furniture_window import FurnitureWindow
from school_system.gui.windows.report_window.report_window import ReportWindow


__all__ = ['LoginWindow', 'MainWindow', 'UserWindow', 'BookWindow', 'StudentWindow', 'TeacherWindow', 'FurnitureWindow', 'ReportWindow']