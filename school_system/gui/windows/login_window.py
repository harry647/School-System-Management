"""
Login window for the School System Management application.

This module provides the login interface for user authentication.
"""

from PyQt6.QtWidgets import QMainWindow, QWidget, QVBoxLayout, QLabel, QLineEdit, QPushButton, QHBoxLayout
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QPixmap, QIcon
from typing import Callable, Optional

from school_system.gui.base.base_window import BaseWindow
from school_system.gui.dialogs.message_dialog import show_error_message, show_success_message
from school_system.config.logging import logger
from school_system.services.auth_service import AuthService
from school_system.core.exceptions import AuthenticationError, ValidationError


class LoginWindow(BaseWindow):
    """Login window for user authentication."""
    
    def __init__(self, parent: QMainWindow, on_success: Callable[[str, str], None]):
        """
        Initialize the login window.
        
        Args:
            parent: The parent window
            on_success: Callback function called on successful login with (username, role)
        """
        super().__init__("School System - Login", parent)
        
        self.parent = parent
        self.on_success = on_success
        self.auth_service = AuthService()
        
        # Set fixed size for login window
        self.setFixedSize(400, 300)
        
        # Initialize UI
        self._setup_widgets()
    
    def _setup_widgets(self):
        """Setup the login form widgets using BaseWindow methods."""
        # Create main layout
        main_layout = self.create_flex_layout("column", False)
        main_layout.setContentsMargins(30, 30, 30, 30)
        main_layout.setSpacing(20)
        
        # Add school logo
        logo_label = QLabel()
        logo_pixmap = QPixmap("school_system/gui/resources/icons/logo.png")
        if not logo_pixmap.isNull():
            logo_label.setPixmap(logo_pixmap.scaled(100, 100, Qt.AspectRatioMode.KeepAspectRatio))
            logo_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            main_layout.addWidget(logo_label)
        
        # Title
        title_label = QLabel("School System Management")
        title_label.setStyleSheet("font-size: 20px; font-weight: bold; color: #2C3E50;")
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        main_layout.addWidget(title_label)
        
        # Subtitle
        subtitle_label = QLabel("Please login to continue")
        subtitle_label.setStyleSheet("font-size: 14px; color: #7F8C8D;")
        subtitle_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        main_layout.addWidget(subtitle_label)
        
        # Add spacing
        main_layout.addSpacing(20)
        
        # Username field
        username_label = QLabel("Username")
        username_label.setStyleSheet("font-size: 14px; font-weight: bold; color: #2C3E50;")
        main_layout.addWidget(username_label)
        
        self.username_input = self.create_input("Enter your username")
        self.username_input.setFixedHeight(40)
        self.username_input.setStyleSheet("""
            QLineEdit {
                border: 1px solid #BDC3C7;
                border-radius: 5px;
                padding: 0 10px;
                font-size: 14px;
            }
            QLineEdit:focus {
                border: 2px solid #3498DB;
            }
        """)
        main_layout.addWidget(self.username_input)
        
        # Add spacing
        main_layout.addSpacing(10)
        
        # Password field
        password_label = QLabel("Password")
        password_label.setStyleSheet("font-size: 14px; font-weight: bold; color: #2C3E50;")
        main_layout.addWidget(password_label)
        
        self.password_input = self.create_input("Enter your password")
        self.password_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.password_input.setFixedHeight(40)
        self.password_input.setStyleSheet("""
            QLineEdit {
                border: 1px solid #BDC3C7;
                border-radius: 5px;
                padding: 0 10px;
                font-size: 14px;
            }
            QLineEdit:focus {
                border: 2px solid #3498DB;
            }
        """)
        main_layout.addWidget(self.password_input)
        
        # Add spacing
        main_layout.addSpacing(20)
        
        # Login button
        login_button = self.create_button("Login", "primary")
        login_button.setFixedHeight(45)
        login_button.setStyleSheet("""
            QPushButton {
                background-color: #3498DB;
                color: white;
                border: none;
                border-radius: 5px;
                font-size: 16px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #2980B9;
            }
            QPushButton:pressed {
                background-color: #1F618D;
            }
        """)
        login_button.clicked.connect(self._on_login)
        main_layout.addWidget(login_button)
        
        # Add spacing
        main_layout.addSpacing(15)
        
        # Action buttons layout
        action_layout = QHBoxLayout()
        action_layout.setSpacing(10)
        
        forgot_password_button = QPushButton("Forgot Password?")
        forgot_password_button.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                color: #3498DB;
                border: none;
                font-size: 12px;
                text-decoration: underline;
            }
            QPushButton:hover {
                color: #2980B9;
            }
        """)
        forgot_password_button.clicked.connect(self._on_forgot_password)
        action_layout.addWidget(forgot_password_button)
        
        action_layout.addStretch()
        
        create_account_button = QPushButton("Create Account")
        create_account_button.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                color: #3498DB;
                border: none;
                font-size: 12px;
                text-decoration: underline;
            }
            QPushButton:hover {
                color: #2980B9;
            }
        """)
        create_account_button.clicked.connect(self._on_create_account)
        action_layout.addWidget(create_account_button)
        
        main_layout.addLayout(action_layout)
        
        # Add spacing
        main_layout.addSpacing(15)
        
        # Default credentials info
        info_text = "Default login: Username: admin | Password: harry123"
        info_label = QLabel(info_text)
        info_label.setStyleSheet("font-size: 11px; color: #95A5A6;")
        info_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        main_layout.addWidget(info_label)
        
        # Add main layout to content area
        self.add_layout_to_content(main_layout)
        
        # Set focus to username field
        self.username_input.setFocus()
        
        # Connect Enter key for login
        self.username_input.returnPressed.connect(lambda: self.password_input.setFocus())
        self.password_input.returnPressed.connect(self._on_login)
    
    def _on_login(self):
        """Handle login button click."""
        username = self.username_input.text().strip()
        password = self.password_input.text()
        
        try:
            # Authenticate user using AuthService
            user = self.auth_service.authenticate_user(username, password)
            logger.info(f"User {username} logged in successfully")
            self.close()
            # Get user role from the authenticated user object
            role = user.role
            self.on_success(username, role)
        except AuthenticationError as e:
            show_error_message("Login Failed", str(e), self)
            logger.warning(f"Failed login attempt for user: {username}")
        except Exception as e:
            show_error_message("Login Error", f"An error occurred: {str(e)}", self)
            logger.error(f"Login error for user {username}: {str(e)}")
    
    def _on_forgot_password(self):
        """Handle forgot password button click."""
        username = self.username_input.text().strip()
        
        try:
            # Request password reset using AuthService
            success = self.auth_service.request_password_reset(username)
            if success:
                show_error_message("Password Reset", "Password reset request sent successfully. Check your email.", self)
                logger.info(f"Password reset requested for user: {username}")
            else:
                show_error_message("Error", "Failed to request password reset. User may not exist.", self)
                logger.warning(f"Failed password reset request for user: {username}")
        except Exception as e:
            show_error_message("Error", f"An error occurred: {str(e)}", self)
            logger.error(f"Password reset error for user {username}: {str(e)}")
    
    def _on_create_account(self):
        """Handle create account button click."""
        username = self.username_input.text().strip()
        password = self.password_input.text()
        
        try:
            # Validate input
            if not username or not password:
                show_error_message("Validation Error", "Please enter both username and password", self)
                return
            
            # Create user using AuthService
            user = self.auth_service.create_user(username, password, role="student")
            show_success_message("Account Created", f"User account created successfully for: {username}", self)
            logger.info(f"New user account created: {username}")
            
            # Clear the form
            self.username_input.clear()
            self.password_input.clear()
            
        except ValidationError as e:
            show_error_message("Validation Error", str(e), self)
            logger.warning(f"Account creation validation failed: {str(e)}")
        except AuthenticationError as e:
            show_error_message("Account Creation Failed", str(e), self)
            logger.warning(f"Account creation failed: {str(e)}")
        except Exception as e:
            show_error_message("Error", f"An error occurred: {str(e)}", self)
            logger.error(f"Account creation error: {str(e)}")
    
    
    def closeEvent(self, event):
        """Handle window closing."""
        super().closeEvent(event)
        # Also close parent application if this is the main window
        self.parent.close()
    
    def show(self):
        """Show the login window."""
        super().show()
        self.activateWindow()
        self.raise_()
