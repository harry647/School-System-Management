"""
Main application class for the School System Management.

This module contains the SchoolSystemApplication class that manages the main GUI
and coordinates between different components of the application.
"""

import tkinter as tk
from tkinter import ttk, messagebox
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


class SchoolSystemApplication:
    """Main application class that manages the school system GUI."""
    
    def __init__(self, root: tk.Tk):
        """
        Initialize the application.
        
        Args:
            root: The root Tkinter window
        """
        self.root = root
        self.settings = Settings()
        self.current_user: Optional[str] = None
        self.main_window: Optional[MainWindow] = None
        
        self._setup_window()
        self._setup_menu()
        self._show_login()
    
    def _setup_window(self):
        """Configure the main application window."""
        self.root.title(self.settings.app_name)
        self.root.geometry(f"{self.settings.default_window_size[0]}x{self.settings.default_window_size[1]}")
        self.root.minsize(800, 600)
        
        # Set window icon if available
        try:
            # You can add an icon file here if needed
            # self.root.iconbitmap("path/to/icon.ico")
            pass
        except Exception as e:
            logger.warning(f"Could not set window icon: {e}")
        
        # Configure window closing
        self.root.protocol("WM_DELETE_WINDOW", self._on_closing)
    
    def _setup_menu(self):
        """Create the application menu bar."""
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)
        
        # File menu
        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="File", menu=file_menu)
        file_menu.add_command(label="Exit", command=self._on_closing)
        
        # Help menu
        help_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Help", menu=help_menu)
        help_menu.add_command(label="About", command=self._show_about)
    
    def _show_login(self):
        """Display the login window."""
        try:
            login_window = LoginWindow(self.root, self._on_login_success)
            logger.info("Login window displayed")
        except Exception as e:
            logger.error(f"Failed to create login window: {e}")
            messagebox.showerror("Error", f"Failed to display login window: {e}")
    
    def _on_login_success(self, username: str, role: str):
        """
        Handle successful login.
        
        Args:
            username: The username of the logged-in user
            role: The role of the logged-in user
        """
        self.current_user = username
        logger.info(f"User {username} logged in with role {role}")
        
        # Create and display the main window
        try:
            self.main_window = MainWindow(self.root, username, role, self._on_logout)
            logger.info("Main application window created")
        except Exception as e:
            logger.error(f"Failed to create main window: {e}")
            messagebox.showerror("Error", f"Failed to create main window: {e}")
    
    def _on_logout(self):
        """Handle user logout."""
        logger.info(f"User {self.current_user} logged out")
        self.current_user = None
        
        # Close main window and show login again
        if self.main_window:
            self.main_window.destroy()
            self.main_window = None
        
        self._show_login()
    
    def _show_about(self):
        """Display the about dialog."""
        about_text = f"""
{self.settings.app_name}
Version: {self.settings.app_version}

A comprehensive school management system for managing:
- Students and Teachers
- Books and Library
- Furniture and Equipment
- User Accounts and Permissions

Developed for efficient school administration.
        """
        messagebox.showinfo("About", about_text.strip())
    
    def _on_closing(self):
        """Handle application closing."""
        result = messagebox.askyesno("Exit Application", "Are you sure you want to exit?")
        if result:
            logger.info("Application closing")
            
            # Clean up database connection
            try:
                db_session = get_db_session()
                if db_session:
                    db_session.close()
                    logger.info("Database connection closed")
            except Exception as e:
                logger.error(f"Error closing database connection: {e}")
            
            self.root.quit()
            self.root.destroy()
    
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
            messagebox.showerror(title, message)
        elif message_type == "warning":
            messagebox.showwarning(title, message)
        else:
            messagebox.showinfo(title, message)