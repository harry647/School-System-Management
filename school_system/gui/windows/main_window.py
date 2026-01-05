"""
Main application window for the School System Management.

This module provides the main GUI interface for the school system.
"""

import tkinter as tk
from tkinter import ttk, messagebox
from typing import Optional, Callable

from school_system.config.logging import logger


class MainWindow:
    """Main application window for the school system."""
    
    def __init__(self, parent: tk.Tk, username: str, role: str, on_logout: Callable):
        """
        Initialize the main window.
        
        Args:
            parent: The parent window
            username: The logged-in username
            role: The user role
            on_logout: Callback function for logout
        """
        self.parent = parent
        self.username = username
        self.role = role
        self.on_logout = on_logout
        self.window: Optional[tk.Toplevel] = None
        
        self._create_window()
        self._setup_widgets()
        
        logger.info(f"Main window created for user {username} with role {role}")
    
    def _create_window(self):
        """Create the main window."""
        self.window = tk.Toplevel(self.parent)
        self.window.title(f"School System Management - {self.username} ({self.role})")
        self.window.geometry("1000x700")
        
        # Handle window closing
        self.window.protocol("WM_DELETE_WINDOW", self._on_closing)
    
    def _setup_widgets(self):
        """Setup the main window widgets."""
        # Create menu bar
        self._create_menu_bar()
        
        # Create main content area
        self._create_content_area()
        
        # Create status bar
        self._create_status_bar()
    
    def _create_menu_bar(self):
        """Create the application menu bar."""
        menubar = tk.Menu(self.window)
        self.window.config(menu=menubar)
        
        # File menu
        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="File", menu=file_menu)
        file_menu.add_command(label="Logout", command=self._on_logout)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self._on_closing)
        
        # Students menu (for admin and librarian)
        if self.role in ['admin', 'librarian']:
            students_menu = tk.Menu(menubar, tearoff=0)
            menubar.add_cascade(label="Students", menu=students_menu)
            students_menu.add_command(label="View Students", command=self._show_students)
            students_menu.add_command(label="Add Student", command=self._add_student)
            if self.role == 'admin':
                students_menu.add_command(label="Manage Students", command=self._manage_students)
        
        # Teachers menu (admin only)
        if self.role == 'admin':
            teachers_menu = tk.Menu(menubar, tearoff=0)
            menubar.add_cascade(label="Teachers", menu=teachers_menu)
            teachers_menu.add_command(label="View Teachers", command=self._show_teachers)
            teachers_menu.add_command(label="Add Teacher", command=self._add_teacher)
            teachers_menu.add_command(label="Manage Teachers", command=self._manage_teachers)
        
        # Books menu
        books_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Books", menu=books_menu)
        books_menu.add_command(label="View Books", command=self._show_books)
        books_menu.add_command(label="Add Book", command=self._add_book)
        books_menu.add_command(label="Borrowed Books", command=self._show_borrowed_books)
        if self.role in ['admin', 'librarian']:
            books_menu.add_command(label="Manage Books", command=self._manage_books)
        
        # Furniture menu
        if self.role in ['admin', 'librarian']:
            furniture_menu = tk.Menu(menubar, tearoff=0)
            menubar.add_cascade(label="Furniture", menu=furniture_menu)
            furniture_menu.add_command(label="View Chairs", command=self._show_chairs)
            furniture_menu.add_command(label="View Lockers", command=self._show_lockers)
            furniture_menu.add_command(label="Manage Furniture", command=self._manage_furniture)
        
        # Reports menu
        if self.role in ['admin', 'librarian']:
            reports_menu = tk.Menu(menubar, tearoff=0)
            menubar.add_cascade(label="Reports", menu=reports_menu)
            reports_menu.add_command(label="Student Report", command=self._student_report)
            reports_menu.add_command(label="Book Report", command=self._book_report)
            reports_menu.add_command(label="Inventory Report", command=self._inventory_report)
        
        # Help menu
        help_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Help", menu=help_menu)
        help_menu.add_command(label="About", command=self._show_about)
    
    def _create_content_area(self):
        """Create the main content area with tabs."""
        # Create notebook for tabs
        self.notebook = ttk.Notebook(self.window)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
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
        dashboard_frame = ttk.Frame(self.notebook)
        self.notebook.add(dashboard_frame, text="Dashboard")
        
        # Welcome message
        welcome_label = ttk.Label(dashboard_frame, 
                                 text=f"Welcome to School System Management\nLogged in as: {self.username} ({self.role})",
                                 font=("Arial", 14, "bold"))
        welcome_label.pack(pady=20)
        
        # Quick stats
        stats_frame = ttk.LabelFrame(dashboard_frame, text="Quick Statistics", padding="10")
        stats_frame.pack(fill=tk.X, padx=20, pady=10)
        
        # This would be populated with actual stats from database
        ttk.Label(stats_frame, text="• Students: 0").pack(anchor=tk.W)
        ttk.Label(stats_frame, text="• Teachers: 0").pack(anchor=tk.W)
        ttk.Label(stats_frame, text="• Books: 0").pack(anchor=tk.W)
        ttk.Label(stats_frame, text="• Available Chairs: 0").pack(anchor=tk.W)
        ttk.Label(stats_frame, text="• Available Lockers: 0").pack(anchor=tk.W)
        
        # Recent activity
        activity_frame = ttk.LabelFrame(dashboard_frame, text="Recent Activity", padding="10")
        activity_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
        # Placeholder for activity list
        activity_text = tk.Text(activity_frame, height=10, wrap=tk.WORD)
        activity_text.pack(fill=tk.BOTH, expand=True)
        activity_text.insert(tk.END, "No recent activity.\n\nThis area will show recent system activity such as:\n• New student registrations\n• Book borrowings\n• Equipment assignments\n• System updates")
        activity_text.config(state=tk.DISABLED)
    
    def _create_students_tab(self):
        """Create the students management tab."""
        students_frame = ttk.Frame(self.notebook)
        self.notebook.add(students_frame, text="Students")
        
        # Students content placeholder
        ttk.Label(students_frame, text="Students Management", font=("Arial", 12, "bold")).pack(pady=10)
        ttk.Label(students_frame, text="This tab will contain student management functionality.").pack()
    
    def _create_books_tab(self):
        """Create the books management tab."""
        books_frame = ttk.Frame(self.notebook)
        self.notebook.add(books_frame, text="Books")
        
        # Books content placeholder
        ttk.Label(books_frame, text="Books Management", font=("Arial", 12, "bold")).pack(pady=10)
        ttk.Label(books_frame, text="This tab will contain book management functionality.").pack()
    
    def _create_furniture_tab(self):
        """Create the furniture management tab."""
        furniture_frame = ttk.Frame(self.notebook)
        self.notebook.add(furniture_frame, text="Furniture")
        
        # Furniture content placeholder
        ttk.Label(furniture_frame, text="Furniture Management", font=("Arial", 12, "bold")).pack(pady=10)
        ttk.Label(furniture_frame, text="This tab will contain furniture management functionality.").pack()
    
    def _create_settings_tab(self):
        """Create the settings tab (admin only)."""
        settings_frame = ttk.Frame(self.notebook)
        self.notebook.add(settings_frame, text="Settings")
        
        # Settings content placeholder
        ttk.Label(settings_frame, text="System Settings", font=("Arial", 12, "bold")).pack(pady=10)
        ttk.Label(settings_frame, text="This tab will contain system settings and configuration.").pack()
    
    def _create_status_bar(self):
        """Create the status bar."""
        self.status_bar = ttk.Frame(self.window)
        self.status_bar.pack(side=tk.BOTTOM, fill=tk.X)
        
        self.status_label = ttk.Label(self.status_bar, text="Ready")
        self.status_label.pack(side=tk.LEFT, padx=5, pady=2)
        
        # User info on the right
        user_label = ttk.Label(self.status_bar, text=f"User: {self.username} | Role: {self.role}")
        user_label.pack(side=tk.RIGHT, padx=5, pady=2)
    
    def _show_students(self):
        """Show students functionality."""
        messagebox.showinfo("Students", "Students functionality coming soon!")
    
    def _add_student(self):
        """Add student functionality."""
        messagebox.showinfo("Add Student", "Add student functionality coming soon!")
    
    def _manage_students(self):
        """Manage students functionality."""
        messagebox.showinfo("Manage Students", "Manage students functionality coming soon!")
    
    def _show_teachers(self):
        """Show teachers functionality."""
        messagebox.showinfo("Teachers", "Teachers functionality coming soon!")
    
    def _add_teacher(self):
        """Add teacher functionality."""
        messagebox.showinfo("Add Teacher", "Add teacher functionality coming soon!")
    
    def _manage_teachers(self):
        """Manage teachers functionality."""
        messagebox.showinfo("Manage Teachers", "Manage teachers functionality coming soon!")
    
    def _show_books(self):
        """Show books functionality."""
        messagebox.showinfo("Books", "Books functionality coming soon!")
    
    def _add_book(self):
        """Add book functionality."""
        messagebox.showinfo("Add Book", "Add book functionality coming soon!")
    
    def _show_borrowed_books(self):
        """Show borrowed books functionality."""
        messagebox.showinfo("Borrowed Books", "Borrowed books functionality coming soon!")
    
    def _manage_books(self):
        """Manage books functionality."""
        messagebox.showinfo("Manage Books", "Manage books functionality coming soon!")
    
    def _show_chairs(self):
        """Show chairs functionality."""
        messagebox.showinfo("Chairs", "Chairs functionality coming soon!")
    
    def _show_lockers(self):
        """Show lockers functionality."""
        messagebox.showinfo("Lockers", "Lockers functionality coming soon!")
    
    def _manage_furniture(self):
        """Manage furniture functionality."""
        messagebox.showinfo("Manage Furniture", "Manage furniture functionality coming soon!")
    
    def _student_report(self):
        """Generate student report."""
        messagebox.showinfo("Student Report", "Student report functionality coming soon!")
    
    def _book_report(self):
        """Generate book report."""
        messagebox.showinfo("Book Report", "Book report functionality coming soon!")
    
    def _inventory_report(self):
        """Generate inventory report."""
        messagebox.showinfo("Inventory Report", "Inventory report functionality coming soon!")
    
    def _show_about(self):
        """Show about dialog."""
        about_text = """School System Management
Version: 1.0.0

A comprehensive school management system for managing:
• Students and Teachers
• Books and Library
• Furniture and Equipment
• User Accounts and Permissions

Developed for efficient school administration."""
        messagebox.showinfo("About", about_text)
    
    def _on_logout(self):
        """Handle logout."""
        result = messagebox.askyesno("Logout", "Are you sure you want to logout?")
        if result:
            logger.info(f"User {self.username} logged out")
            self.window.destroy()
            self.on_logout()
    
    def _on_closing(self):
        """Handle window closing."""
        result = messagebox.askyesno("Exit Application", "Are you sure you want to exit?")
        if result:
            logger.info("Application closing from main window")
            self.window.destroy()
            self.parent.quit()
    
    def update_status(self, message: str):
        """Update the status bar message."""
        self.status_label.config(text=message)
    
    def destroy(self):
        """Destroy the main window."""
        if self.window:
            self.window.destroy()