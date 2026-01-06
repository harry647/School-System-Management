"""
Main application window for the School System Management.

This module provides the main GUI interface for the school system.
"""

from PyQt6.QtWidgets import QLabel, QMessageBox, QMenuBar, QSizePolicy
from PyQt6.QtCore import Qt
from typing import Callable

from school_system.config.logging import logger
from school_system.gui.base.base_window import BaseApplicationWindow
from school_system.gui.windows.user_window import UserWindow
from school_system.gui.windows.book_window import BookWindow
from school_system.gui.windows.student_window import StudentWindow


class MainWindow(BaseApplicationWindow):
    """Main application window for the school system."""
    
    def __init__(self, parent, username: str, role: str, on_logout: Callable):
        """
        Initialize the main window.

        Args:
            parent: The parent window
            username: The logged-in username
            role: The user role
            on_logout: Callback function for logout
        """
        super().__init__(title=f"School System Management - {username} ({role})", parent=parent)

        self.username = username
        self.role = role
        self.on_logout = on_logout

        # Connect theme change signal to update UI
        self.theme_changed.connect(self._on_theme_changed)

        self._setup_role_based_menus()
        self._setup_content()
        self._apply_professional_styling()

        logger.info(f"Main window created for user {username} with role {role}")

    def _apply_professional_styling(self):
        """Apply professional styling to the main window."""
        # Set consistent font and styling based on current theme
        current_theme = self.get_theme()
        
        # Apply theme-specific styling to enhance professional appearance
        if current_theme == "light":
            self.setStyleSheet("""
                MainWindow {
                    background-color: #f5f7fa;
                    font-family: 'Segoe UI', Arial, sans-serif;
                }
                QCard {
                    border-radius: 8px;
                    border: 1px solid #e1e4e8;
                    background-color: white;
                }
                QLabel {
                    font-family: 'Segoe UI', Arial, sans-serif;
                }
                QCard QLabel[title="true"] {
                    font-size: 16px;
                    font-weight: 600;
                    color: #24292e;
                    padding: 8px 12px;
                    border-bottom: 1px solid #e1e4e8;
                }
                QCard QLabel[content="true"] {
                    font-size: 14px;
                    color: #586069;
                    padding: 12px;
                }
            """)
        else:  # dark theme
            self.setStyleSheet("""
                MainWindow {
                    background-color: #24292e;
                    font-family: 'Segoe UI', Arial, sans-serif;
                }
                QCard {
                    border-radius: 8px;
                    border: 1px solid #373e47;
                    background-color: #2d333b;
                }
                QLabel {
                    font-family: 'Segoe UI', Arial, sans-serif;
                    color: #e6edf3;
                }
                QCard QLabel[title="true"] {
                    font-size: 16px;
                    font-weight: 600;
                    color: #f0f6fc;
                    padding: 8px 12px;
                    border-bottom: 1px solid #373e47;
                }
                QCard QLabel[content="true"] {
                    font-size: 14px;
                    color: #c9d1d9;
                    padding: 12px;
                }
            """)

    def _on_theme_changed(self, theme_name: str):
        """Handle theme changes to maintain consistent styling."""
        self._apply_professional_styling()
        logger.info(f"Theme changed to {theme_name}, updated main window styling")
    
    def _setup_role_based_menus(self):
        """Setup role-based menus."""
        # File menu already exists from base, add logout
        file_menu = self._menu_bar.actions()[0].menu()  # File is the first menu
        file_menu.addAction("Logout", self._on_logout)
        file_menu.addSeparator()  # Exit is already there

        # Students menu (for admin and librarian)
        if self.role in ['admin', 'librarian']:
            students_menu = self._menu_bar.addMenu("Students")
            students_menu.addAction("View Students", self._show_students)
            students_menu.addAction("Add Student", self._add_student)
            if self.role == 'admin':
                students_menu.addAction("Manage Students", self._manage_students)

        # Teachers menu (admin only)
        if self.role == 'admin':
            teachers_menu = self._menu_bar.addMenu("Teachers")
            teachers_menu.addAction("View Teachers", self._show_teachers)
            teachers_menu.addAction("Add Teacher", self._add_teacher)
            teachers_menu.addAction("Manage Teachers", self._manage_teachers)

        # Users menu (admin only)
        if self.role == 'admin':
            users_menu = self._menu_bar.addMenu("Users")
            users_menu.addAction("User Management", self._show_user_management)

        # Books menu
        books_menu = self._menu_bar.addMenu("Books")
        books_menu.addAction("View Books", self._show_books)
        books_menu.addAction("Add Book", self._add_book)
        books_menu.addAction("Borrowed Books", self._show_borrowed_books)
        if self.role in ['admin', 'librarian']:
            books_menu.addAction("Manage Books", self._manage_books)

        # Furniture menu
        if self.role in ['admin', 'librarian']:
            furniture_menu = self._menu_bar.addMenu("Furniture")
            furniture_menu.addAction("View Chairs", self._show_chairs)
            furniture_menu.addAction("View Lockers", self._show_lockers)
            furniture_menu.addAction("Manage Furniture", self._manage_furniture)

        # Reports menu
        if self.role in ['admin', 'librarian']:
            reports_menu = self._menu_bar.addMenu("Reports")
            reports_menu.addAction("Student Report", self._student_report)
            reports_menu.addAction("Book Report", self._book_report)
            reports_menu.addAction("Inventory Report", self._inventory_report)

    def _setup_content(self):
        """Setup the main content area with statistics display."""
        # Create main vertical layout with clean spacing
        main_layout = self.create_layout("vbox")
        main_layout.set_spacing(20)
        main_layout.set_margins(0, 0, 0, 0)
        self.add_layout_to_content(main_layout)

        # Simple welcome message
        welcome_card = self.create_card(
            title="Welcome",
            content=f"<p>Hello, {self.username}!</p><p>Role: {self.role}</p>"
        )
        welcome_card.setMinimumHeight(80)
        welcome_card.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        main_layout._layout.addWidget(welcome_card)

        # Statistics section - show totals only, no management sections
        stats_layout = self.create_flex_layout(direction="row", wrap=True)
        stats_layout.set_spacing(16)
        
        # Show relevant statistics based on user role
        stats_cards = []
        if self.role in ['admin', 'librarian']:
            stats_cards.extend([
                ("Total Students", "0"),
                ("Total Teachers", "0"),
                ("Total Books", "0"),
                ("Available Chairs", "0"),
                ("Available Lockers", "0")
            ])
        else:
            stats_cards.append(("Total Books", "0"))
        
        for title, count in stats_cards:
            stat_card = self.create_card(title=title, content=f"<div style='font-size: 24px; font-weight: bold;'>{count}</div>")
            stat_card.setMinimumWidth(150)
            stat_card.setMaximumWidth(200)
            stat_card.setMinimumHeight(120)
            stats_layout._layout.addWidget(stat_card)
        
        main_layout._layout.addWidget(stats_layout)

        # Basic information card
        info_card = self.create_card(
            title="System Information",
            content="<p>Use the menu bar and status bar buttons to navigate through the system.</p>"
        )
        info_card.setMinimumHeight(60)
        info_card.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        main_layout._layout.addWidget(info_card)
    
    
    def _show_students(self):
        """Show student management window."""
        self._show_student_management()
    
    def _add_student(self):
        """Show student management window."""
        self._show_student_management()
    
    def _manage_students(self):
        """Show student management window."""
        self._show_student_management()
    
    def _show_student_management(self):
        """Show the student management window."""
        try:
            student_window = StudentWindow(self, self.username, self.role)
            student_window.show()
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to open student management: {str(e)}")
    
    def _show_teachers(self):
        """Show teachers functionality."""
        QMessageBox.information(self, "Teachers", "Teachers functionality coming soon!")
    
    def _add_teacher(self):
        """Add teacher functionality."""
        QMessageBox.information(self, "Add Teacher", "Add teacher functionality coming soon!")
    
    def _manage_teachers(self):
        """Manage teachers functionality."""
        QMessageBox.information(self, "Manage Teachers", "Manage teachers functionality coming soon!")

    def _show_user_management(self):
        """Show user management window."""
        try:
            user_window = UserWindow(self, self.username, self.role)
            user_window.show()
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to open user management: {str(e)}")
    
    def _show_books(self):
        """Show books management window."""
        self._show_book_management()
    
    def _add_book(self):
        """Show books management window."""
        self._show_book_management()
    
    def _show_borrowed_books(self):
        """Show books management window."""
        self._show_book_management()
    
    def _manage_books(self):
        """Show books management window."""
        self._show_book_management()
    
    def _show_book_management(self):
        """Show the book management window."""
        try:
            book_window = BookWindow(self, self.username, self.role)
            book_window.show()
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to open book management: {str(e)}")
    
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
        full_message = f"{message} | User: {self.username} | Role: {self.role}"
        super().update_status(full_message)
    
    def closeEvent(self, event):
        """Handle window closing."""
        super().closeEvent(event)
