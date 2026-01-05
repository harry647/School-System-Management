"""
Login window for the School System Management application.

This module provides the login interface for user authentication.
"""

import tkinter as tk
from tkinter import ttk, messagebox
from typing import Callable, Optional

from school_system.config.logging import logger
from school_system.services.auth_service import AuthService
from school_system.core.exceptions import AuthenticationError


class LoginWindow:
    """Login window for user authentication."""
    
    def __init__(self, parent: tk.Tk, on_success: Callable[[str, str], None]):
        """
        Initialize the login window.
        
        Args:
            parent: The parent window
            on_success: Callback function called on successful login with (username, role)
        """
        self.parent = parent
        self.on_success = on_success
        self.window: Optional[tk.Toplevel] = None
        self.username_var = tk.StringVar()
        self.password_var = tk.StringVar()
        self.auth_service = AuthService()
        
        self._create_window()
        self._setup_widgets()
    
    def _create_window(self):
        """Create the login window."""
        self.window = tk.Toplevel(self.parent)
        self.window.title("School System - Login")
        self.window.geometry("400x300")
        self.window.resizable(False, False)
        
        # Center the window
        self.window.transient(self.parent)
        self.window.grab_set()
        
        # Calculate center position
        self.window.update_idletasks()
        x = (self.window.winfo_screenwidth() // 2) - (400 // 2)
        y = (self.window.winfo_screenheight() // 2) - (300 // 2)
        self.window.geometry(f"400x300+{x}+{y}")
        
        # Handle window closing
        self.window.protocol("WM_DELETE_WINDOW", self._on_closing)
    
    def _setup_widgets(self):
        """Setup the login form widgets."""
        # Main frame
        main_frame = ttk.Frame(self.window, padding="20")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Configure grid weights
        self.window.columnconfigure(0, weight=1)
        self.window.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        
        # Title
        title_label = ttk.Label(main_frame, text="School System Management", 
                               font=("Arial", 16, "bold"))
        title_label.grid(row=0, column=0, columnspan=2, pady=(0, 20))
        
        # Username
        ttk.Label(main_frame, text="Username:").grid(row=1, column=0, sticky=tk.W, pady=5)
        username_entry = ttk.Entry(main_frame, textvariable=self.username_var, width=30)
        username_entry.grid(row=1, column=1, sticky=(tk.W, tk.E), pady=5, padx=(10, 0))
        username_entry.focus()
        
        # Password
        ttk.Label(main_frame, text="Password:").grid(row=2, column=0, sticky=tk.W, pady=5)
        password_entry = ttk.Entry(main_frame, textvariable=self.password_var, 
                                  show="*", width=30)
        password_entry.grid(row=2, column=1, sticky=(tk.W, tk.E), pady=5, padx=(10, 0))
        
        # Login button
        login_button = ttk.Button(main_frame, text="Login", command=self._on_login)
        login_button.grid(row=3, column=0, columnspan=2, pady=20)
        
        # Bind Enter key to login
        username_entry.bind("<Return>", lambda e: password_entry.focus())
        password_entry.bind("<Return>", lambda e: self._on_login())
        
        # Default credentials info
        info_text = "Default login:\nUsername: admin\nPassword: harry123"
        info_label = ttk.Label(main_frame, text=info_text, 
                              font=("Arial", 9), foreground="gray")
        info_label.grid(row=4, column=0, columnspan=2, pady=(10, 0))
    
    def _on_login(self):
        """Handle login button click."""
        username = self.username_var.get().strip()
        password = self.password_var.get()
        
        if not username or not password:
            messagebox.showerror("Error", "Please enter both username and password")
            return
        
        try:
            # Authenticate user using AuthService
            user = self.auth_service.authenticate_user(username, password)
            logger.info(f"User {username} logged in successfully")
            self.window.destroy()
            # Get user role using AuthService
            role = self.auth_service.get_user_role(username)
            self.on_success(username, role)
        except AuthenticationError:
            messagebox.showerror("Error", "Invalid username or password")
            logger.warning(f"Failed login attempt for user: {username}")
        except Exception as e:
            messagebox.showerror("Error", f"An error occurred: {str(e)}")
            logger.error(f"Login error for user {username}: {str(e)}")
    
    
    def _on_closing(self):
        """Handle window closing."""
        self.window.destroy()
        # Also close parent application if this is the main window
        self.parent.quit()
    
    def show(self):
        """Show the login window."""
        if self.window:
            self.window.deiconify()
            self.window.lift()
    
    def destroy(self):
        """Destroy the login window."""
        if self.window:
            self.window.destroy()