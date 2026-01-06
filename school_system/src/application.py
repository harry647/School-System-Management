"""
Main application class for the School System Management.

This module contains the SchoolSystemApplication class that manages the main GUI
and coordinates between different components of the application.
"""

from PyQt6.QtWidgets import QMainWindow, QWidget, QVBoxLayout, QLabel, QMessageBox
from PyQt6.QtCore import Qt
from typing import Optional

from school_system.config.logging import logger
from school_system.config.settings import Settings
from school_system.database import get_db_session
from school_system.database.repositories import (
    StudentRepository, TeacherRepository, BookRepository, UserRepository,
    ChairRepository, LockerRepository, FurnitureCategoryRepository
)
from school_system.models import (
    Student, Teacher, Book, User, Chair, Locker, FurnitureCategory
)
from school_system.core.exceptions import DatabaseException
from school_system.gui.windows import LoginWindow, MainWindow
from school_system.gui.dialogs.message_dialog import show_error_message, show_info_message


class SchoolSystemApplication:
    """Main application class that manages the school system GUI."""
    
    def __init__(self):
        """Initialize the application."""
        self.settings = Settings()
        self.current_user: Optional[str] = None
        self.main_window: Optional[MainWindow] = None
        self.login_window: Optional[LoginWindow] = None
        
        # Create the main application window
        self._create_main_window()
        
        # Show login window
        self._show_login()
    
    def _create_main_window(self):
        """Create the main application window."""
        from PyQt6.QtWidgets import QApplication
        self.app = QApplication.instance() or QApplication([])
        
        self.main_widget = QMainWindow()
        self.main_widget.setWindowTitle(self.settings.app_name)
        self.main_widget.setGeometry(
            self.settings.default_window_size[0],
            self.settings.default_window_size[1],
            self.settings.default_window_size[0],
            self.settings.default_window_size[1]
        )
        self.main_widget.setMinimumSize(800, 600)
        
        # Handle window closing
        self.main_widget.closeEvent = self._on_closing
        
        logger.info("Main application window created")
    
    def _show_login(self):
        """Display the login window."""
        try:
            self.login_window = LoginWindow(self.main_widget, self._on_login_success)
            self.login_window.show()
            logger.info("Login window displayed")
        except Exception as e:
            logger.error(f"Failed to create login window: {e}")
            show_error_message("Error", f"Failed to display login window: {e}", self.main_widget)
    
    def _on_login_success(self, username: str, role: str):
        """
        Handle successful login.
        
        Args:
            username: The username of the logged-in user
            role: The role of the logged-in user
        """
        self.current_user = username
        logger.info(f"User {username} logged in with role {role}")
        
        # Close login window
        if self.login_window:
            self.login_window.close()
            self.login_window = None
        
        # Create and display the main window
        try:
            self.main_window = MainWindow(self.main_widget, username, role, self._on_logout)
            logger.info("Main application window created")
        except Exception as e:
            logger.error(f"Failed to create main window: {e}")
            show_error_message("Error", f"Failed to create main window: {e}", self.main_widget)
    
    def _on_logout(self):
        """Handle user logout."""
        logger.info(f"User {self.current_user} logged out")
        self.current_user = None
        
        # Close main window
        if self.main_window:
            self.main_window.close()
            self.main_window = None
        
        # Show login again
        self._show_login()
    
    def _show_about(self):
        """Display the about dialog."""
        about_text = f"""
{self.settings.app_name}
Version: {self.settings.app_version}

A comprehensive school management system for managing:
• Students and Teachers
• Books and Library
• Furniture and Equipment
• User Accounts and Permissions

Developed for efficient school administration.
        """
        show_info_message("About", about_text.strip(), self.main_widget)
    
    def _on_closing(self, event):
        """Handle window closing."""
        from PyQt6.QtWidgets import QMessageBox
        reply = QMessageBox.question(
            self.main_widget,
            "Exit Application",
            "Are you sure you want to exit?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            logger.info("Application closing")
            
            # Clean up database connection
            try:
                db_session = get_db_session()
                if db_session:
                    db_session.close()
                    logger.info("Database connection closed")
            except Exception as e:
                logger.error(f"Error closing database connection: {e}")
            
            self.app.quit()
        else:
            event.ignore()
    
    def get_current_user(self) -> Optional[str]:
        """
        Get the currently logged-in user.
        
        Returns:
            The username of the current user, or None if not logged in
        """
        return self.current_user
    
    def is_logged_in(self) -> bool:
        """
        Check if a user is currently logged in.
        
        Returns:
            True if a user is logged in, False otherwise
        """
        return self.current_user is not None
    
    def show_message(self, title: str, message: str, message_type: str = "info"):
        """
        Show a message dialog.
        
        Args:
            title: The dialog title
            message: The message content
            message_type: The type of message (info, warning, error)
        """
        if message_type == "error":
            show_error_message(title, message, self.main_widget)
        elif message_type == "warning":
            from school_system.gui.dialogs.message_dialog import show_warning_message
            show_warning_message(title, message, self.main_widget)
        else:
            show_info_message(title, message, self.main_widget)
    
    def run(self):
        """Run the application."""
        from PyQt6.QtWidgets import QApplication
        self.main_widget.show()
        return self.app.exec()


if __name__ == "__main__":
    app = SchoolSystemApplication()
    app.run()
