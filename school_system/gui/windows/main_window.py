"""
Main application window for the School System Management.

This module provides the main GUI interface for the school system.
"""

from PyQt6.QtWidgets import QLabel, QMessageBox, QMenuBar, QSizePolicy, QFrame, QVBoxLayout, QToolButton, QHBoxLayout, QPushButton
from PyQt6.QtCore import Qt, QTime, QTimer
from PyQt6.QtGui import QIcon, QFont
from typing import Callable

from school_system.config.logging import logger
from school_system.gui.base.base_window import BaseApplicationWindow
from school_system.gui.windows.user_window import UserWindow
from school_system.gui.windows.book_window import BookWindow
from school_system.gui.windows.student_window import StudentWindow
from school_system.gui.windows.teacher_window import TeacherWindow
from school_system.gui.windows.furniture_window import FurnitureWindow
from school_system.gui.windows.report_window import ReportWindow


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
        self._setup_sidebar()
        self._setup_top_bar()
        self._setup_content()
        self._apply_professional_styling()

        logger.info(f"Main window created for user {username} with role {role}")

    def _setup_sidebar(self):
        """Setup the left-aligned sidebar navigation."""
        # Create sidebar frame
        sidebar = QFrame(self)
        sidebar.setFixedWidth(200)
        sidebar.setStyleSheet("""
            QFrame {
                background-color: #2c3e50;
                border-right: 1px solid #34495e;
            }
            QToolButton {
                color: white;
                text-align: left;
                padding: 10px;
                border: none;
                font-size: 14px;
            }
            QToolButton:hover {
                background-color: #34495e;
            }
            QToolButton:pressed {
                background-color: #1a252f;
            }
        """)
        
        # Create vertical layout for sidebar
        sidebar_layout = QVBoxLayout(sidebar)
        sidebar_layout.setContentsMargins(0, 0, 0, 0)
        sidebar_layout.setSpacing(0)
        
        # Add navigation buttons
        modules = [
            ("Dashboard", "🏠", self._show_dashboard),
            ("Students", "👨‍🎓", self._show_students),
            ("Library", "📚", self._show_books),
            ("Teachers", "👩‍🏫", self._show_teachers),
            ("Furniture", "🪑", self._show_furniture_management),
            ("Reports", "📊", self._show_report_management),
            ("Settings", "⚙️", self._show_settings),
        ]
        
        for text, icon, callback in modules:
            btn = QToolButton()
            btn.setText(f"  {icon}  {text}")
            btn.setToolButtonStyle(Qt.ToolButtonStyle.ToolButtonTextBesideIcon)
            btn.clicked.connect(callback)
            sidebar_layout.addWidget(btn)
        
        # Add stretch to push buttons to top
        sidebar_layout.addStretch()
        
        # Add sidebar to main layout
        self._main_layout.insertWidget(0, sidebar)
        
    def _setup_top_bar(self):
        """Setup the top bar for branding, user info, and logout."""
        top_bar = QFrame(self)
        top_bar.setFixedHeight(60)
        top_bar.setStyleSheet("""
            QFrame {
                background-color: #3498db;
                color: white;
                border-bottom: 1px solid #2980b9;
            }
            QLabel {
                color: white;
                font-size: 16px;
                font-weight: bold;
            }
        """)
        
        # Create horizontal layout for top bar
        top_layout = QHBoxLayout(top_bar)
        top_layout.setContentsMargins(15, 0, 15, 0)
        
        # School branding
        logo_label = QLabel("🏫 School System Management")
        logo_label.setStyleSheet("font-size: 18px; font-weight: bold;")
        top_layout.addWidget(logo_label)
        
        # Spacer
        top_layout.addStretch()
        
        # User info and logout
        user_info = QLabel(f"👤 {self.username} | {self.role}")
        user_info.setStyleSheet("font-size: 14px;")
        top_layout.addWidget(user_info)
        
        # Logout button
        logout_btn = QToolButton()
        logout_btn.setText("Logout 🚪")
        logout_btn.setStyleSheet("color: white; font-size: 14px;")
        logout_btn.clicked.connect(self._on_logout)
        top_layout.addWidget(logout_btn)
        
        # Add top bar to main layout
        self._main_layout.insertWidget(0, top_bar)

    def _get_role_color(self):
        """Get the accent color based on user role."""
        if self.role == 'admin':
            return '#3498db'  # Blue
        elif self.role == 'librarian':
            return '#2ecc71'  # Green
        elif self.role == 'teacher':
            return '#9b59b6'  # Purple
        else:
            return '#3498db'  # Default blue
    
    def _on_theme_changed(self, theme_name: str):
        """Handle theme changes to maintain consistent styling."""
        self._apply_professional_styling()
        logger.info(f"Theme changed to {theme_name}, updated main window styling")
    
    def _apply_professional_styling(self):
        """Apply professional styling to the main window."""
        # Get role-based color
        role_color = self._get_role_color()
        
        # Set consistent font and styling based on current theme
        current_theme = self.get_theme()
         
        # Apply theme-specific styling to enhance professional appearance
        if current_theme == "light":
            self.setStyleSheet(f"""
                MainWindow {{
                    background-color: #f5f7fa;
                    font-family: 'Segoe UI', Arial, sans-serif;
                }}
                QFrame[statCard="true"] {{
                    background-color: white;
                    border-radius: 12px;
                    border-left: 4px solid {role_color};
                    border: 1px solid #e1e4e8;
                    padding: 16px;
                }}
                QFrame[statCard="true"]:hover {{
                    border-color: {role_color};
                    background-color: rgba(52, 152, 219, 0.05);
                }}
                QLabel {{
                    font-family: 'Segoe UI', Arial, sans-serif;
                }}
                QLabel[title="true"] {{
                    font-size: 16px;
                    font-weight: 600;
                    color: #24292e;
                    padding: 8px 12px;
                    border-bottom: 1px solid #e1e4e8;
                }}
                QLabel[content="true"] {{
                    font-size: 14px;
                    color: #586069;
                    padding: 12px;
                }}
                QToolButton[actionButton="true"] {{
                    background-color: white;
                    border: 1px solid {role_color};
                    color: {role_color};
                    padding: 8px 15px;
                    border-radius: 6px;
                    font-size: 14px;
                }}
                QToolButton[actionButton="true"]:hover {{
                    background-color: rgba(52, 152, 219, 0.1);
                }}
            """)
        else:  # dark theme
            self.setStyleSheet(f"""
                MainWindow {{
                    background-color: #24292e;
                    font-family: 'Segoe UI', Arial, sans-serif;
                }}
                QFrame[statCard="true"] {{
                    background-color: #2d333b;
                    border-radius: 12px;
                    border-left: 4px solid {role_color};
                    border: 1px solid #373e47;
                    padding: 16px;
                }}
                QFrame[statCard="true"]:hover {{
                    border-color: {role_color};
                    background-color: rgba(52, 152, 219, 0.05);
                }}
                QLabel {{
                    font-family: 'Segoe UI', Arial, sans-serif;
                    color: #e6edf3;
                }}
                QLabel[title="true"] {{
                    font-size: 16px;
                    font-weight: 600;
                    color: #f0f6fc;
                    padding: 8px 12px;
                    border-bottom: 1px solid #373e47;
                }}
                QLabel[content="true"] {{
                    font-size: 14px;
                    color: #c9d1d9;
                    padding: 12px;
                }}
                QToolButton[actionButton="true"] {{
                    background-color: #2d333b;
                    border: 1px solid {role_color};
                    color: {role_color};
                    padding: 8px 15px;
                    border-radius: 6px;
                    font-size: 14px;
                }}
                QToolButton[actionButton="true"]:hover {{
                    background-color: rgba(52, 152, 219, 0.1);
                }}
            """)
    
    def _setup_role_based_menus(self):
        """Setup minimal menu bar with only essential items."""
        # File menu already exists from base, add logout
        file_menu = self._menu_bar.actions()[0].menu()  # File is the first menu
        file_menu.addAction("Logout", self._on_logout)
        file_menu.addSeparator()  # Exit is already there

        # Help menu (keep for about and documentation)
        help_menu = self._menu_bar.addMenu("Help")
        help_menu.addAction("About", self._show_about)

        # Account menu (minimal user-related actions)
        account_menu = self._menu_bar.addMenu("Account")
        account_menu.addAction("Profile", self._show_profile)
        account_menu.addAction("Settings", self._show_settings)

    def _setup_content(self):
        """Setup the main content area with statistics display."""
        # Create main vertical layout with clean spacing
        main_layout = self.create_layout("vbox")
        main_layout.set_spacing(20)
        main_layout.set_margins(20, 20, 20, 20)
        self.add_layout_to_content(main_layout)
        
        # Dynamic welcome header
        self._setup_welcome_header(main_layout)
        
        # Quick actions section
        self._setup_quick_actions(main_layout)
        
        # Statistics section - show totals only, no management sections
        stats_layout = self.create_flex_layout(direction="row", wrap=True)
        stats_layout.set_spacing(16)
        
        # Show relevant statistics based on user role
        stats_cards = []
        if self.role in ['admin', 'librarian']:
            stats_cards.extend([
                ("Total Students", "0", "👨‍🎓"),
                ("Total Teachers", "0", "👩‍🏫"),
                ("Total Books", "0", "📚"),
                ("Available Chairs", "0", "🪑"),
                ("Available Lockers", "0", "🔐")
            ])
        else:
            stats_cards.append(("Total Books", "0", "📚"))
        
        for title, count, icon in stats_cards:
            stat_card = self._create_modern_stat_card(title, count, icon)
            stats_layout._layout.addWidget(stat_card)
        
        main_layout._layout.addWidget(stats_layout)
        
        # Basic information card
        info_card = self.create_card(
            title="System Information",
            content="<p>Use the sidebar and top bar to navigate through the system.</p>"
        )
        info_card.setMinimumHeight(60)
        info_card.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        main_layout._layout.addWidget(info_card)
    
    def _setup_welcome_header(self, main_layout):
        """Setup the enhanced welcome header with personalized greeting, role-specific overview, and system insights."""
        # Create welcome card with enhanced features
        welcome_card = QFrame()
        welcome_card.setObjectName("welcomeHeader")
        welcome_card.setStyleSheet("""
            QFrame#welcomeHeader {
                background-color: white;
                border-radius: 12px;
                border-left: 4px solid #3498db;
                padding: 20px;
            }
        """)
        
        welcome_layout = QVBoxLayout(welcome_card)
        welcome_layout.setContentsMargins(15, 15, 15, 15)
        welcome_layout.setSpacing(12)
        
        # Personalized greeting with time-based and role-based message
        self._setup_personalized_greeting(welcome_layout)
        
        # Role-specific overview
        self._setup_role_overview(welcome_layout)
        
        # Contextual help tips
        self._setup_help_tips(welcome_layout)
        
        # System insights
        self._setup_system_insights(welcome_layout)
        
        main_layout._layout.addWidget(welcome_card)
        
        # Log user interaction
        logger.info(f"User {self.username} viewed welcome header at {QTime.currentTime().toString()}")
    
    def _setup_personalized_greeting(self, layout):
        """Setup personalized greeting message based on time and role."""
        current_time = QTime.currentTime()
        hour = current_time.hour()
        
        # Time-based greeting
        if hour < 12:
            time_greeting = "Good morning"
        elif hour < 18:
            time_greeting = "Good afternoon"
        else:
            time_greeting = "Good evening"
        
        # Role-based greeting
        role_capitalized = self.role.capitalize()
        if self.role == 'admin':
            role_message = "Administrator"
        elif self.role == 'teacher':
            role_message = "Educator"
        else:
            role_message = role_capitalized
        
        # Create greeting label
        greeting_label = QLabel(f"{time_greeting}, {role_message} {self.username}! 👋")
        greeting_label.setStyleSheet("""
            font-size: 24px;
            font-weight: bold;
            color: #2c3e50;
        """)
        layout.addWidget(greeting_label)
        
        # Welcome back message
        welcome_label = QLabel("Welcome back! Here's what's new today:")
        welcome_label.setStyleSheet("""
            font-size: 16px;
            color: #7f8c8d;
            margin-bottom: 8px;
        """)
        layout.addWidget(welcome_label)
    
    def _setup_role_overview(self, layout):
        """Setup role-specific overview of key system advantages."""
        overview_frame = QFrame()
        overview_frame.setStyleSheet("""
            QFrame {
                background-color: #f8f9fa;
                border-radius: 8px;
                padding: 12px;
                border-left: 3px solid #3498db;
            }
        """)
        
        overview_layout = QVBoxLayout(overview_frame)
        overview_layout.setContentsMargins(10, 10, 10, 10)
        
        # Role-specific content
        if self.role == 'admin':
            overview_text = """
            <p><strong>Admin Dashboard Overview:</strong></p>
            <p>• Manage users, monitor activity, and customize settings—all from one centralized dashboard.</p>
            <p>• Access comprehensive reports and analytics to make data-driven decisions.</p>
            <p>• Control system-wide configurations and permissions with ease.</p>
            """
        elif self.role == 'librarian':
            overview_text = """
            <p><strong>Librarian Dashboard Overview:</strong></p>
            <p>• Efficiently manage the library catalog, track book borrowings, and monitor inventory.</p>
            <p>• Generate detailed reports on book circulation and student reading habits.</p>
            <p>• Streamline library operations with intuitive tools and quick access to resources.</p>
            """
        elif self.role == 'teacher':
            overview_text = """
            <p><strong>Teacher Dashboard Overview:</strong></p>
            <p>• Track student progress, assign tasks, and communicate effortlessly.</p>
            <p>• Access teaching resources, lesson plans, and educational materials in one place.</p>
            <p>• Collaborate with colleagues and share best practices for improved learning outcomes.</p>
            """
        else:
            overview_text = """
            <p><strong>Welcome to your Dashboard!</strong></p>
            <p>• Access all system features and tools tailored to your role.</p>
            <p>• Stay organized and productive with our intuitive interface.</p>
            """
        
        overview_label = QLabel(overview_text)
        overview_label.setStyleSheet("""
            font-size: 14px;
            color: #2c3e50;
            line-height: 1.6;
        """)
        overview_layout.addWidget(overview_label)
        
        layout.addWidget(overview_frame)
    
    def _setup_help_tips(self, layout):
        """Setup contextual help tips with collapsible/dismissible tooltips."""
        help_frame = QFrame()
        help_frame.setStyleSheet("""
            QFrame {
                background-color: #e8f4fc;
                border-radius: 8px;
                padding: 12px;
                border-left: 3px solid #3498db;
            }
        """)
        
        help_layout = QHBoxLayout(help_frame)
        help_layout.setContentsMargins(10, 10, 10, 10)
        
        # Help tip label
        help_label = QLabel("Need help? Click here to learn how to navigate the dashboard efficiently.")
        help_label.setStyleSheet("""
            font-size: 14px;
            color: #2980b9;
        """)
        help_layout.addWidget(help_label)
        
        # Help button
        help_btn = QPushButton("Show Tips")
        help_btn.setStyleSheet("""
            QPushButton {
                background-color: #3498db;
                color: white;
                border: none;
                border-radius: 4px;
                padding: 6px 12px;
                font-size: 12px;
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
        """)
        help_btn.clicked.connect(self._show_help_tips)
        help_layout.addWidget(help_btn)
        
        layout.addWidget(help_frame)
    
    def _setup_system_insights(self, layout):
        """Setup System Insights section with updates and notifications."""
        insights_frame = QFrame()
        insights_frame.setStyleSheet("""
            QFrame {
                background-color: #f8f9fa;
                border-radius: 8px;
                padding: 12px;
                border-left: 3px solid #2ecc71;
            }
        """)
        
        insights_layout = QVBoxLayout(insights_frame)
        insights_layout.setContentsMargins(10, 10, 10, 10)
        
        # System insights label
        insights_label = QLabel("📊 System Insights")
        insights_label.setStyleSheet("""
            font-size: 16px;
            font-weight: bold;
            color: #2c3e50;
            margin-bottom: 8px;
        """)
        insights_layout.addWidget(insights_label)
        
        # Dynamic insights content
        insights_content = QLabel("2 new announcements • 5 pending approvals • System performance: Optimal")
        insights_content.setStyleSheet("""
            font-size: 14px;
            color: #27ae60;
        """)
        insights_layout.addWidget(insights_content)
        
        layout.addWidget(insights_frame)
    
    def _show_help_tips(self):
        """Show contextual help tips in a message box."""
        help_message = """
        <h3>Dashboard Navigation Tips</h3>
        <ul>
        <li><strong>Sidebar:</strong> Use the left sidebar to quickly navigate between modules.</li>
        <li><strong>Top Bar:</strong> Access your profile, settings, and logout from the top bar.</li>
        <li><strong>Quick Actions:</strong> Use the quick action buttons for common tasks.</li>
        <li><strong>Statistics Cards:</strong> Click on stat cards for detailed information.</li>
        <li><strong>Search:</strong> Use the search functionality to find specific items quickly.</li>
        </ul>
        <p>Need more help? Contact support or check our documentation.</p>
        """
        QMessageBox.information(self, "Help Tips", help_message)
        logger.info(f"User {self.username} viewed help tips")
    
    def _update_welcome_header(self):
        """Update welcome header content based on user role, time, and system status."""
        # This method can be called to refresh the welcome header content
        # For now, we'll just log the update
        logger.info(f"Welcome header updated for user {self.username}")
        
        # In a real implementation, this would:
        # 1. Refresh the greeting based on current time
        # 2. Update system insights with real data
        # 3. Refresh role-specific content
        # 4. Apply any theme changes
    
    def _on_theme_changed(self, theme_name: str):
        """Handle theme changes to maintain consistent styling."""
        self._apply_professional_styling()
        self._update_welcome_header()
        logger.info(f"Theme changed to {theme_name}, updated main window styling and welcome header")
    
    def _setup_quick_actions(self, main_layout):
        """Setup the quick actions section with icon-prefixed buttons."""
        quick_actions_card = QFrame()
        quick_actions_card.setStyleSheet("""
            QFrame {
                background-color: white;
                border-radius: 12px;
                border: 1px solid #e1e4e8;
                padding: 15px;
            }
        """)
        
        quick_actions_layout = QHBoxLayout(quick_actions_card)
        quick_actions_layout.setContentsMargins(10, 10, 10, 10)
        quick_actions_layout.setSpacing(10)
        
        # Quick action buttons
        actions = [
            ("➕ Add Student", self._add_student),
            ("➕ Add Book", self._add_book),
            ("📤 Import Distribution", self._show_import),
            ("📄 Generate Report", self._show_report_management),
        ]
        
        for text, callback in actions:
            btn = QToolButton()
            btn.setText(text)
            btn.setStyleSheet("""
                QToolButton {
                    background-color: white;
                    border: 1px solid #3498db;
                    color: #3498db;
                    padding: 8px 15px;
                    border-radius: 6px;
                    font-size: 14px;
                }
                QToolButton:hover {
                    background-color: rgba(52, 152, 219, 0.1);
                }
            """)
            btn.clicked.connect(callback)
            quick_actions_layout.addWidget(btn)
        
        main_layout._layout.addWidget(quick_actions_card)
    
    def _create_modern_stat_card(self, title, count, icon):
        """Create a modern statistics card with icon, large number, and label."""
        card = QFrame()
        card.setStyleSheet("""
            QFrame {
                background-color: white;
                border-radius: 12px;
                border-left: 4px solid #3498db;
                border: 1px solid #e1e4e8;
                padding: 16px;
            }
            QFrame:hover {
                border-color: #2980b9;
                background-color: rgba(52, 152, 219, 0.05);
            }
        """)
        card.setMinimumWidth(150)
        card.setMaximumWidth(200)
        card.setMinimumHeight(120)
        
        layout = QVBoxLayout(card)
        layout.setContentsMargins(10, 10, 10, 10)
        
        # Icon and title
        title_label = QLabel(f"{icon} {title}")
        title_label.setStyleSheet("font-size: 14px; color: #7f8c8d;")
        layout.addWidget(title_label)
        
        # Large number
        count_label = QLabel(count)
        count_label.setStyleSheet("font-size: 32px; font-weight: bold; color: #2c3e50;")
        count_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(count_label)
        
        return card
    
    
    def _show_dashboard(self):
        """Show the dashboard (refresh view)."""
        # Refresh the dashboard view
        self._setup_content()
        logger.info(f"Dashboard refreshed for user {self.username}")
    
    def _show_import(self):
        """Show import functionality."""
        # Placeholder for import functionality
        QMessageBox.information(self, "Import", "Import functionality will be implemented here.")
        logger.info(f"User {self.username} accessed import functionality")
    
    def _show_profile(self):
        """Show user profile."""
        QMessageBox.information(self, "Profile", f"User Profile\n\nUsername: {self.username}\nRole: {self.role}")
        logger.info(f"User {self.username} accessed profile")
    
    def _show_settings(self):
        """Show settings window."""
        QMessageBox.information(self, "Settings", "Settings functionality will be implemented here.")
        logger.info(f"User {self.username} accessed settings")
    
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
        """Show teacher management window."""
        self._show_teacher_management()
    
    def _add_teacher(self):
        """Show teacher management window."""
        self._show_teacher_management()
    
    def _manage_teachers(self):
        """Show teacher management window."""
        self._show_teacher_management()
    
    def _show_teacher_management(self):
        """Show the teacher management window."""
        try:
            teacher_window = TeacherWindow(self, self.username, self.role)
            teacher_window.show()
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to open teacher management: {str(e)}")

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
        self._show_furniture_management()

    def _show_lockers(self):
        """Show lockers functionality."""
        self._show_furniture_management()

    def _manage_furniture(self):
        """Manage furniture functionality."""
        self._show_furniture_management()

    def _show_furniture_management(self):
        """Show the furniture management window."""
        try:
            furniture_window = FurnitureWindow(self, self.username, self.role)
            furniture_window.show()
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to open furniture management: {str(e)}")
    
    def _student_report(self):
        """Generate student report."""
        self._show_report_management()
    
    def _book_report(self):
        """Generate book report."""
        self._show_report_management()
    
    def _inventory_report(self):
        """Generate inventory report."""
        self._show_report_management()
    
    def _show_report_management(self):
        """Show the report management window."""
        try:
            report_window = ReportWindow(self, self.username, self.role)
            report_window.show()
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to open report management: {str(e)}")
    
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
