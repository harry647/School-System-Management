"""
Main application window for the School System Management.

This module provides the main GUI interface for the school system.
"""

from PyQt6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QLabel, QPushButton, 
                             QHBoxLayout, QTabWidget, QFrame, QMessageBox, QMenuBar)
from PyQt6.QtCore import Qt
from typing import Optional, Callable

from school_system.config.logging import logger


class MainWindow(QMainWindow):
    """Main application window for the school system."""
    
    def __init__(self, parent: QMainWindow, username: str, role: str, on_logout: Callable):
        """
        Initialize the main window.
        
        Args:
            parent: The parent window
            username: The logged-in username
            role: The user role
            on_logout: Callback function for logout
        """
        super().__init__(parent)
        
        self.username = username
        self.role = role
        self.on_logout = on_logout
        
        self._create_window()
        self._setup_widgets()
        
        logger.info(f"Main window created for user {username} with role {role}")
    
    def _create_window(self):
        """Create the main window."""
        self.setWindowTitle(f"School System Management - {self.username} ({self.role})")
        self.setGeometry(100, 100, 1000, 700)
        self.setMinimumSize(800, 600)
    
    def _setup_widgets(self):
        """Setup the main window widgets."""
        # Create central widget with layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # Create menu bar
        self._create_menu_bar()
        
        # Create main content area with tabs
        self._create_content_area(main_layout)
        
        # Create status bar
        self._create_status_bar(main_layout)
    
    def _create_menu_bar(self):
        """Create the application menu bar."""
        menubar = self.menuBar()
        
        # File menu
        file_menu = menubar.addMenu("File")
        file_menu.addAction("Logout", self._on_logout)
        file_menu.addSeparator()
        file_menu.addAction("Exit", self._on_closing)
        
        # Students menu (for admin and librarian)
        if self.role in ['admin', 'librarian']:
            students_menu = menubar.addMenu("Students")
            students_menu.addAction("View Students", self._show_students)
            students_menu.addAction("Add Student", self._add_student)
            if self.role == 'admin':
                students_menu.addAction("Manage Students", self._manage_students)
        
        # Teachers menu (admin only)
        if self.role == 'admin':
            teachers_menu = menubar.addMenu("Teachers")
            teachers_menu.addAction("View Teachers", self._show_teachers)
            teachers_menu.addAction("Add Teacher", self._add_teacher)
            teachers_menu.addAction("Manage Teachers", self._manage_teachers)
        
        # Books menu
        books_menu = menubar.addMenu("Books")
        books_menu.addAction("View Books", self._show_books)
        books_menu.addAction("Add Book", self._add_book)
        books_menu.addAction("Borrowed Books", self._show_borrowed_books)
        if self.role in ['admin', 'librarian']:
            books_menu.addAction("Manage Books", self._manage_books)
        
        # Furniture menu
        if self.role in ['admin', 'librarian']:
            furniture_menu = menubar.addMenu("Furniture")
            furniture_menu.addAction("View Chairs", self._show_chairs)
            furniture_menu.addAction("View Lockers", self._show_lockers)
            furniture_menu.addAction("Manage Furniture", self._manage_furniture)
        
        # Reports menu
        if self.role in ['admin', 'librarian']:
            reports_menu = menubar.addMenu("Reports")
            reports_menu.addAction("Student Report", self._student_report)
            reports_menu.addAction("Book Report", self._book_report)
            reports_menu.addAction("Inventory Report", self._inventory_report)
        
        # Help menu
        help_menu = menubar.addMenu("Help")
        help_menu.addAction("About", self._show_about)
    
    def _create_content_area(self, parent_layout: QVBoxLayout):
        """Create the main content area with tabs."""
        # Create tab widget
        self.tab_widget = QTabWidget()
        self.tab_widget.setDocumentMode(True)
        parent_layout.addWidget(self.tab_widget, 1)  # Add with stretch factor 1
        
        # Dashboard tab
        self._create_dashboard_tab()
        
        # Students tab (if user has access)
        if self.role in ['admin', 'librarian']:
            self._create_students_tab()
        
        # Books tab
        self._create_books_tab()
        
        # Furniture tab (if user has access)
        if self.role in ['admin', 'librarian']:
            self._create_furniture_tab()
        
        # Settings tab
        if self.role == 'admin':
            self._create_settings_tab()
    
    def _create_dashboard_tab(self):
        """Create the dashboard tab."""
        dashboard_frame = QFrame()
        dashboard_layout = QVBoxLayout(dashboard_frame)
        
        # Welcome message
        welcome_label = QLabel(f"Welcome to School System Management\nLogged in as: {self.username} ({self.role})")
        welcome_label.setStyleSheet("font-size: 16px; font-weight: bold;")
        welcome_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        dashboard_layout.addWidget(welcome_label)
        
        # Quick stats frame
        stats_frame = QFrame()
        stats_frame.setFrameShape(QFrame.Shape.StyledPanel)
        stats_layout = QVBoxLayout(stats_frame)
        stats_layout.addWidget(QLabel("Quick Statistics"))
        
        # This would be populated with actual stats from database
        stats_layout.addWidget(QLabel("• Students: 0"))
        stats_layout.addWidget(QLabel("• Teachers: 0"))
        stats_layout.addWidget(QLabel("• Books: 0"))
        stats_layout.addWidget(QLabel("• Available Chairs: 0"))
        stats_layout.addWidget(QLabel("• Available Lockers: 0"))
        
        dashboard_layout.addWidget(stats_frame)
        
        # Recent activity frame
        activity_frame = QFrame()
        activity_frame.setFrameShape(QFrame.Shape.StyledPanel)
        activity_layout = QVBoxLayout(activity_frame)
        activity_layout.addWidget(QLabel("Recent Activity"))
        
        activity_text = QLabel("No recent activity.\n\nThis area will show recent system activity such as:\n• New student registrations\n• Book borrowings\n• Equipment assignments\n• System updates")
        activity_layout.addWidget(activity_text)
        
        dashboard_layout.addWidget(activity_frame)
        
        self.tab_widget.addTab(dashboard_frame, "Dashboard")
    
    def _create_students_tab(self):
        """Create the students management tab."""
        students_frame = QFrame()
        students_layout = QVBoxLayout(students_frame)
        
        title_label = QLabel("Students Management")
        title_label.setStyleSheet("font-size: 14px; font-weight: bold;")
        students_layout.addWidget(title_label)
        
        content_label = QLabel("This tab will contain student management functionality.")
        students_layout.addWidget(content_label)
        
        students_layout.addStretch()
        
        self.tab_widget.addTab(students_frame, "Students")
    
    def _create_books_tab(self):
        """Create the books management tab."""
        books_frame = QFrame()
        books_layout = QVBoxLayout(books_frame)
        
        title_label = QLabel("Books Management")
        title_label.setStyleSheet("font-size: 14px; font-weight: bold;")
        books_layout.addWidget(title_label)
        
        content_label = QLabel("This tab will contain book management functionality.")
        books_layout.addWidget(content_label)
        
        books_layout.addStretch()
        
        self.tab_widget.addTab(books_frame, "Books")
    
    def _create_furniture_tab(self):
        """Create the furniture management tab."""
        furniture_frame = QFrame()
        furniture_layout = QVBoxLayout(furniture_frame)
        
        title_label = QLabel("Furniture Management")
        title_label.setStyleSheet("font-size: 14px; font-weight: bold;")
        furniture_layout.addWidget(title_label)
        
        content_label = QLabel("This tab will contain furniture management functionality.")
        furniture_layout.addWidget(content_label)
        
        furniture_layout.addStretch()
        
        self.tab_widget.addTab(furniture_frame, "Furniture")
    
    def _create_settings_tab(self):
        """Create the settings tab (admin only)."""
        settings_frame = QFrame()
        settings_layout = QVBoxLayout(settings_frame)
        
        title_label = QLabel("System Settings")
        title_label.setStyleSheet("font-size: 14px; font-weight: bold;")
        settings_layout.addWidget(title_label)
        
        content_label = QLabel("This tab will contain system settings and configuration.")
        settings_layout.addWidget(content_label)
        
        settings_layout.addStretch()
        
        self.tab_widget.addTab(settings_frame, "Settings")
    
    def _create_status_bar(self, parent_layout: QVBoxLayout):
        """Create the status bar."""
        status_bar = QFrame()
        status_bar.setMaximumHeight(30)
        status_bar.setStyleSheet("background-color: #f0f0f0; border-top: 1px solid #ccc;")
        status_layout = QHBoxLayout(status_bar)
        status_layout.setContentsMargins(5, 2, 5, 2)
        
        # Status label on the left
        self.status_label = QLabel("Ready")
        status_layout.addWidget(self.status_label)
        
        # User info on the right
        user_label = QLabel(f"User: {self.username} | Role: {self.role}")
        status_layout.addWidget(user_label)
        
        parent_layout.addWidget(status_bar)  # Add to bottom
    
    def _show_students(self):
        """Show students functionality."""
        QMessageBox.information(self, "Students", "Students functionality coming soon!")
    
    def _add_student(self):
        """Add student functionality."""
        QMessageBox.information(self, "Add Student", "Add student functionality coming soon!")
    
    def _manage_students(self):
        """Manage students functionality."""
        QMessageBox.information(self, "Manage Students", "Manage students functionality coming soon!")
    
    def _show_teachers(self):
        """Show teachers functionality."""
        QMessageBox.information(self, "Teachers", "Teachers functionality coming soon!")
    
    def _add_teacher(self):
        """Add teacher functionality."""
        QMessageBox.information(self, "Add Teacher", "Add teacher functionality coming soon!")
    
    def _manage_teachers(self):
        """Manage teachers functionality."""
        QMessageBox.information(self, "Manage Teachers", "Manage teachers functionality coming soon!")
    
    def _show_books(self):
        """Show books functionality."""
        QMessageBox.information(self, "Books", "Books functionality coming soon!")
    
    def _add_book(self):
        """Add book functionality."""
        QMessageBox.information(self, "Add Book", "Add book functionality coming soon!")
    
    def _show_borrowed_books(self):
        """Show borrowed books functionality."""
        QMessageBox.information(self, "Borrowed Books", "Borrowed books functionality coming soon!")
    
    def _manage_books(self):
        """Manage books functionality."""
        QMessageBox.information(self, "Manage Books", "Manage books functionality coming soon!")
    
    def _show_chairs(self):
        """Show chairs functionality."""
        QMessageBox.information(self, "Chairs", "Chairs functionality coming soon!")
    
    def _show_lockers(self):
        """Show lockers functionality."""
        QMessageBox.information(self, "Lockers", "Lockers functionality coming soon!")
    
    def _manage_furniture(self):
        """Manage furniture functionality."""
        QMessageBox.information(self, "Manage Furniture", "Manage furniture functionality coming soon!")
    
    def _student_report(self):
        """Generate student report."""
        QMessageBox.information(self, "Student Report", "Student report functionality coming soon!")
    
    def _book_report(self):
        """Generate book report."""
        QMessageBox.information(self, "Book Report", "Book report functionality coming soon!")
    
    def _inventory_report(self):
        """Generate inventory report."""
        QMessageBox.information(self, "Inventory Report", "Inventory report functionality coming soon!")
    
    def _show_about(self):
        """Show about dialog."""
        about_text = f"""School System Management
Version: 1.0.0

A comprehensive school management system for managing:
• Students and Teachers
• Books and Library
• Furniture and Equipment
• User Accounts and Permissions

Developed for efficient school administration."""
        QMessageBox.about(self, "About", about_text)
    
    def _on_logout(self):
        """Handle logout."""
        reply = QMessageBox.question(
            self, 
            "Logout", 
            "Are you sure you want to logout?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            logger.info(f"User {self.username} logged out")
            self.close()
            self.on_logout()
    
    def _on_closing(self):
        """Handle window closing."""
        reply = QMessageBox.question(
            self, 
            "Exit Application", 
            "Are you sure you want to exit?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            logger.info("Application closing from main window")
            self.close()
            # This will trigger the parent's close event
    
    def update_status(self, message: str):
        """Update the status bar message."""
        self.status_label.setText(message)
    
    def closeEvent(self, event):
        """Handle window closing."""
        super().closeEvent(event)
