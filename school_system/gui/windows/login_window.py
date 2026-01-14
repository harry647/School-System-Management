"""
Login window for the School System Management application.

This module provides the login interface for user authentication.
"""

from PyQt6.QtWidgets import QMainWindow, QWidget, QVBoxLayout, QLabel, QLineEdit, QPushButton, QHBoxLayout, QSizePolicy, QFrame
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QPixmap, QIcon, QFont
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

        # Set fixed size for login window (modern web-style dimensions)
        self.setFixedSize(680, 640)

        # Use light theme for modern web-style appearance
        self.set_theme("light")
        
        # Apply modern web-style login page styling
        self._apply_modern_login_styling()

        # Initialize UI
        self._setup_widgets()
    
    
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
                show_success_message("Password Reset", "Password reset request sent successfully. Check your email.", self)
                logger.info(f"Password reset requested for user: {username}")
            else:
                show_error_message("Error", "Failed to request password reset. User may not exist.", self)
                logger.warning(f"Failed password reset request for user: {username}")
        except Exception as e:
            show_error_message("Error", f"An error occurred: {str(e)}", self)
            logger.error(f"Password reset error for user {username}: {str(e)}")
    
    def _toggle_password_visibility(self):
        """Toggle password visibility."""
        if self.password_input.echoMode() == QLineEdit.EchoMode.Password:
            self.password_input.setEchoMode(QLineEdit.EchoMode.Normal)
            self.toggle_password_button.setText("🙈")
        else:
            self.password_input.setEchoMode(QLineEdit.EchoMode.Password)
            self.toggle_password_button.setText("👁")

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
    
    
    def _apply_modern_login_styling(self):
        """Apply modern web-style login page styling."""
        theme_manager = self.get_theme_manager()
        theme = theme_manager._themes[self.get_theme()]
        self.setStyleSheet(f"""
            QMainWindow {{
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 {theme["background"]}, stop:1 {theme["surface"]});
            }}
            QFrame[loginCard="true"] {{
                background-color: {theme["surface"]};
                border: 1px solid {theme["border"]};
                border-radius: 16px;
                padding: 40px;
                min-width: 400px;
                max-width: 400px;
            }}
            QLabel[fieldLabel="true"] {{
                font-size: 13px;
                font-weight: 600;
                color: {theme["text"]};
                margin-bottom: 4px;
            }}
            QLabel[infoText="true"] {{
                font-size: 12px;
                color: {theme["text_muted"]};
                padding: 8px;
            }}
            QPushButton[buttonType="link"] {{
                background-color: transparent;
                color: {theme["primary"]};
                border: none;
                font-size: 13px;
                font-weight: 500;
                padding: 4px 8px;
                text-align: left;
            }}
            QPushButton[buttonType="link"]:hover {{
                color: {theme["primary_hover"]};
                text-decoration: underline;
            }}
        """)
    
    def _setup_widgets(self):
        """Setup the modern web-style login form widgets."""
        # Create main container layout
        main_layout = self.create_flex_layout("column", False)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.set_spacing(0)
        main_layout.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        
        # Create centered card container
        card_container = QFrame()
        card_container.setObjectName("loginCard")
        card_container.setProperty("card", "true")
        card_layout = QVBoxLayout(card_container)
        card_layout.setContentsMargins(40, 40, 40, 40)
        card_layout.setSpacing(24)
        
        # Logo section
        logo_container = QFrame()
        logo_container.setFixedHeight(80)
        logo_layout = QVBoxLayout(logo_container)
        logo_layout.setContentsMargins(0, 0, 0, 0)
        logo_layout.setSpacing(8)
        
        logo_label = QLabel()
        logo_pixmap = QPixmap("school_system/gui/resources/icons/logo.png")
        if not logo_pixmap.isNull():
            logo_label.setPixmap(logo_pixmap.scaled(64, 64, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation))
        logo_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        logo_layout.addWidget(logo_label)
        
        # Title with modern typography
        title_label = QLabel("School System Management")
        title_font = QFont("Segoe UI", 28, QFont.Weight.Bold)
        title_label.setFont(title_font)
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        card_layout.addWidget(logo_container)
        card_layout.addWidget(title_label)
        
        # Subtitle
        subtitle_label = QLabel("Sign in to your account")
        subtitle_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        card_layout.addWidget(subtitle_label)
        card_layout.addSpacing(8)
        
        # Username field with modern styling
        username_label = QLabel("Username")
        username_label.setProperty("fieldLabel", "true")
        card_layout.addWidget(username_label)
        
        self.username_input = self.create_input("Enter your username")
        self.username_input.setFixedHeight(44)
        card_layout.addWidget(self.username_input)
        
        # Password field
        password_label = QLabel("Password")
        password_label.setProperty("fieldLabel", "true")
        card_layout.addWidget(password_label)
        
        # Password input with visibility toggle
        password_container = QHBoxLayout()
        password_container.setSpacing(8)
        
        self.password_input = self.create_input("Enter your password")
        self.password_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.password_input.setFixedHeight(44)
        password_container.addWidget(self.password_input)
        
        # Modern visibility toggle button
        self.toggle_password_button = QPushButton("👁")
        self.toggle_password_button.setFixedSize(44, 44)
        self.toggle_password_button.setProperty("buttonType", "outline")
        self.toggle_password_button.clicked.connect(self._toggle_password_visibility)
        password_container.addWidget(self.toggle_password_button)
        
        card_layout.addLayout(password_container)
        
        # Login button - modern and prominent
        login_button = self.create_button("Sign In", "primary")
        login_button.setFixedHeight(48)
        login_font = QFont("Segoe UI", 15, QFont.Weight.DemiBold)
        login_button.setFont(login_font)
        login_button.clicked.connect(self._on_login)
        card_layout.addWidget(login_button)
        card_layout.addSpacing(8)
        
        # Action links - modern link styling
        action_layout = QHBoxLayout()
        action_layout.setSpacing(16)
        
        forgot_password_button = QPushButton("Forgot Password?")
        forgot_password_button.setProperty("buttonType", "link")
        forgot_password_button.setCursor(Qt.CursorShape.PointingHandCursor)
        forgot_password_button.clicked.connect(self._on_forgot_password)
        action_layout.addWidget(forgot_password_button)
        
        action_layout.addStretch()
        
        create_account_button = QPushButton("Create Account")
        create_account_button.setProperty("buttonType", "link")
        create_account_button.setCursor(Qt.CursorShape.PointingHandCursor)
        create_account_button.clicked.connect(self._on_create_account)
        action_layout.addWidget(create_account_button)
        
        card_layout.addLayout(action_layout)
        card_layout.addSpacing(16)
        
        # Info text - subtle styling
        info_text = "Default: admin / harry123"
        info_label = QLabel(info_text)
        info_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        info_label.setProperty("infoText", "true")
        card_layout.addWidget(info_label)
        
        # Add card to main layout with centering
        main_layout.add_stretch()
        main_layout.add_widget(card_container)
        main_layout.add_stretch()
        
        # Add main layout to content area
        self.add_layout_to_content(main_layout)
        
        # Set focus to username field
        self.username_input.setFocus()
        
        # Connect Enter key for login
        self.username_input.returnPressed.connect(lambda: self.password_input.setFocus())
        self.password_input.returnPressed.connect(self._on_login)

    def closeEvent(self, event):
        """Handle window closing."""
        super().closeEvent(event)
        # Also close parent application if this is the main window
        if self.parent:
            self.parent.close()
    
    def show(self):
        """Show the login window."""
        super().show()
        self.activateWindow()
        self.raise_()
