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
from school_system.gui.windows.user_window.user_window import UserWindow


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
        """Setup modern web-style sidebar navigation."""
        theme_manager = self.get_theme_manager()
        theme = theme_manager._themes[self.get_theme()]
        
        # Create sidebar frame with modern styling
        sidebar = QFrame(self)
        sidebar.setFixedWidth(260)
        sidebar.setProperty("sidebar", "true")
        sidebar.setStyleSheet(f"""
            QFrame[sidebar="true"] {{
                background-color: {theme["surface"]};
                border-right: 1px solid {theme["border"]};
            }}
            QToolButton {{
                color: {theme["text"]};
                text-align: left;
                padding: 14px 20px;
                border: none;
                font-size: 14px;
                font-weight: 500;
                border-radius: 8px;
                margin: 2px 8px;
            }}
            QToolButton:hover {{
                background-color: {theme["surface_hover"]};
                color: {theme["primary"]};
            }}
            QToolButton:pressed {{
                background-color: {theme["border"]};
            }}
        """)
         
        # Create vertical layout for sidebar
        sidebar_layout = QVBoxLayout(sidebar)
        sidebar_layout.setContentsMargins(12, 20, 12, 20)
        sidebar_layout.setSpacing(4)
         
        # Dashboard
        dashboard_btn = QToolButton()
        dashboard_btn.setText("  🏠  Dashboard")
        dashboard_btn.setToolButtonStyle(Qt.ToolButtonStyle.ToolButtonTextBesideIcon)
        dashboard_btn.clicked.connect(self._show_dashboard)
        sidebar_layout.addWidget(dashboard_btn)
        
        sidebar_layout.addSpacing(12)
        
        # Students section
        students_label = QLabel("STUDENTS")
        students_label.setStyleSheet(f"""
            color: {theme["text_secondary"]};
            font-size: 11px;
            font-weight: 600;
            text-transform: uppercase;
            letter-spacing: 1px;
            padding: 8px 20px;
            margin-top: 4px;
        """)
        sidebar_layout.addWidget(students_label)
        
        students_actions = [
            ("👁️ View Students", self._show_students),
            ("➕ Add Student", self._add_student),
            ("✏️ Edit Student", self._show_edit_student),
            ("📝 Ream Management", self._show_ream_management_window),
            ("📚 Library Activity", self._show_library_activity),
            ("📤 Import/Export", self._show_student_import_export),
        ]
        
        for text, callback in students_actions:
            btn = QToolButton()
            btn.setText(f"  {text}")
            btn.setToolButtonStyle(Qt.ToolButtonStyle.ToolButtonTextBesideIcon)
            btn.clicked.connect(callback)
            sidebar_layout.addWidget(btn)
        
        sidebar_layout.addSpacing(12)
        
        # Books section
        books_label = QLabel("BOOKS")
        books_label.setStyleSheet(f"""
            color: {theme["text_secondary"]};
            font-size: 11px;
            font-weight: 600;
            text-transform: uppercase;
            letter-spacing: 1px;
            padding: 8px 20px;
            margin-top: 4px;
        """)
        sidebar_layout.addWidget(books_label)
        
        books_actions = [
            ("👁️ View Books", self._show_books),
            ("➕ Add Book", self._add_book),
            ("📖 Borrow Book", self._show_borrow_book),
            ("↩️ Return Book", self._show_return_book),
            ("📦 Distribution", self._show_distribution),
            ("📤 Import/Export", self._show_book_import_export),
        ]
        
        for text, callback in books_actions:
            btn = QToolButton()
            btn.setText(f"  {text}")
            btn.setToolButtonStyle(Qt.ToolButtonStyle.ToolButtonTextBesideIcon)
            btn.clicked.connect(callback)
            sidebar_layout.addWidget(btn)
        
        sidebar_layout.addSpacing(12)
        
        # Teachers section
        teachers_label = QLabel("TEACHERS")
        teachers_label.setStyleSheet(f"""
            color: {theme["text_secondary"]};
            font-size: 11px;
            font-weight: 600;
            text-transform: uppercase;
            letter-spacing: 1px;
            padding: 8px 20px;
            margin-top: 4px;
        """)
        sidebar_layout.addWidget(teachers_label)
        
        teachers_actions = [
            ("👁️ View Teachers", self._show_teachers),
            ("➕ Add Teacher", self._add_teacher),
            ("✏️ Edit Teacher", self._show_edit_teacher),
            ("📤 Import/Export", self._show_teacher_import_export),
        ]
        
        for text, callback in teachers_actions:
            btn = QToolButton()
            btn.setText(f"  {text}")
            btn.setToolButtonStyle(Qt.ToolButtonStyle.ToolButtonTextBesideIcon)
            btn.clicked.connect(callback)
            sidebar_layout.addWidget(btn)
        
        sidebar_layout.addSpacing(12)
        
        # Furniture section
        furniture_label = QLabel("FURNITURE")
        furniture_label.setStyleSheet(f"""
            color: {theme["text_secondary"]};
            font-size: 11px;
            font-weight: 600;
            text-transform: uppercase;
            letter-spacing: 1px;
            padding: 8px 20px;
            margin-top: 4px;
        """)
        sidebar_layout.addWidget(furniture_label)
        
        furniture_actions = [
            ("🪑 Manage Furniture", self._show_furniture_management),
            ("📋 Assignments", self._show_furniture_assignments),
            ("🔧 Maintenance", self._show_furniture_maintenance),
        ]
        
        for text, callback in furniture_actions:
            btn = QToolButton()
            btn.setText(f"  {text}")
            btn.setToolButtonStyle(Qt.ToolButtonStyle.ToolButtonTextBesideIcon)
            btn.clicked.connect(callback)
            sidebar_layout.addWidget(btn)
        
        sidebar_layout.addSpacing(12)
        
        # Users section
        users_label = QLabel("USERS")
        users_label.setStyleSheet(f"""
            color: {theme["text_secondary"]};
            font-size: 11px;
            font-weight: 600;
            text-transform: uppercase;
            letter-spacing: 1px;
            padding: 8px 20px;
            margin-top: 4px;
        """)
        sidebar_layout.addWidget(users_label)
        
        users_btn = QToolButton()
        users_btn.setText("  👤 Manage Users")
        users_btn.setToolButtonStyle(Qt.ToolButtonStyle.ToolButtonTextBesideIcon)
        users_btn.clicked.connect(self._show_user_management)
        sidebar_layout.addWidget(users_btn)

        view_users_btn = QToolButton()
        view_users_btn.setText("  👁️ View Users")
        view_users_btn.setToolButtonStyle(Qt.ToolButtonStyle.ToolButtonTextBesideIcon)
        view_users_btn.clicked.connect(self._show_view_users)
        sidebar_layout.addWidget(view_users_btn)
        
        sidebar_layout.addSpacing(12)
        
        # Reports section
        reports_label = QLabel("REPORTS")
        reports_label.setStyleSheet(f"""
            color: {theme["text_secondary"]};
            font-size: 11px;
            font-weight: 600;
            text-transform: uppercase;
            letter-spacing: 1px;
            padding: 8px 20px;
            margin-top: 4px;
        """)
        sidebar_layout.addWidget(reports_label)
        
        reports_actions = [
            ("📊 Book Reports", self._show_book_reports),
            ("📊 Student Reports", self._show_student_reports),
            ("📊 Custom Reports", self._show_custom_reports),
        ]
        
        for text, callback in reports_actions:
            btn = QToolButton()
            btn.setText(f"  {text}")
            btn.setToolButtonStyle(Qt.ToolButtonStyle.ToolButtonTextBesideIcon)
            btn.clicked.connect(callback)
            sidebar_layout.addWidget(btn)
        
        sidebar_layout.addSpacing(12)
        
        # Settings
        settings_btn = QToolButton()
        settings_btn.setText("  ⚙️  Settings")
        settings_btn.setToolButtonStyle(Qt.ToolButtonStyle.ToolButtonTextBesideIcon)
        settings_btn.clicked.connect(self._show_settings)
        sidebar_layout.addWidget(settings_btn)
         
        # Add stretch to push buttons to top
        sidebar_layout.addStretch()
         
        # Add sidebar to main layout
        self._main_layout.insertWidget(0, sidebar)
        
    def _setup_top_bar(self):
        """Setup modern web-style top bar."""
        theme_manager = self.get_theme_manager()
        theme = theme_manager._themes[self.get_theme()]
        role_color = self._get_role_color()
        
        top_bar = QFrame(self)
        top_bar.setFixedHeight(72)
        top_bar.setProperty("topBar", "true")
        top_bar.setStyleSheet(f"""
            QFrame[topBar="true"] {{
                background-color: {theme["surface"]};
                border-bottom: 1px solid {theme["border"]};
            }}
            QLabel {{
                color: {theme["text"]};
                font-size: 16px;
                font-weight: 600;
            }}
            QToolButton {{
                background-color: transparent;
                color: {theme["text"]};
                border: 1px solid {theme["border"]};
                border-radius: 8px;
                padding: 8px 16px;
                font-size: 14px;
                font-weight: 500;
            }}
            QToolButton:hover {{
                background-color: {theme["surface_hover"]};
                border-color: {role_color};
                color: {role_color};
            }}
        """)
         
        # Create horizontal layout for top bar
        top_layout = QHBoxLayout(top_bar)
        top_layout.setContentsMargins(24, 0, 24, 0)
        top_layout.setSpacing(16)
        
        # School branding with modern typography
        logo_label = QLabel("🏫 School System")
        logo_font = QFont("Segoe UI", 18, QFont.Weight.Bold)
        logo_label.setFont(logo_font)
        top_layout.addWidget(logo_label)
        
        # Spacer
        top_layout.addStretch()
        
        # User info badge
        user_info = QLabel(f"👤 {self.username}")
        user_info.setStyleSheet(f"""
            font-size: 14px;
            font-weight: 500;
            color: {theme["text"]};
            padding: 6px 12px;
            background-color: {theme["surface_hover"]};
            border-radius: 8px;
        """)
        top_layout.addWidget(user_info)
        
        # Role badge
        role_badge = QLabel(self.role.upper())
        role_badge.setStyleSheet(f"""
            font-size: 11px;
            font-weight: 600;
            color: white;
            background-color: {role_color};
            padding: 4px 10px;
            border-radius: 6px;
            letter-spacing: 0.5px;
        """)
        top_layout.addWidget(role_badge)
        
        # Logout button
        logout_btn = QToolButton()
        logout_btn.setText("Logout")
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
        self._update_welcome_header()
        logger.info(f"Theme changed to {theme_name}, updated main window styling and welcome header")
    
    def _apply_professional_styling(self):
        """Apply modern web-style professional styling to the main window."""
        theme_manager = self.get_theme_manager()
        theme = theme_manager._themes[self.get_theme()]
        role_color = self._get_role_color()
        
        # Apply modern web-style theme
        self.setStyleSheet(f"""
            MainWindow {{
                background-color: {theme["background"]};
                font-family: 'Segoe UI', -apple-system, BlinkMacSystemFont, 'Roboto', sans-serif;
            }}
            QFrame[statCard="true"] {{
                background-color: {theme["surface"]};
                border-radius: 12px;
                border-left: 4px solid {role_color};
                border: 1px solid {theme["border"]};
                padding: 20px;
            }}
            QFrame[statCard="true"]:hover {{
                border-color: {role_color};
                background-color: {theme["surface_hover"]};
                transform: translateY(-2px);
            }}
            QLabel[title="true"] {{
                font-size: 16px;
                font-weight: 600;
                color: {theme["text"]};
                padding: 12px 16px;
                border-bottom: 1px solid {theme["border"]};
            }}
            QLabel[content="true"] {{
                font-size: 14px;
                color: {theme["text_secondary"]};
                padding: 16px;
            }}
            QToolButton[actionButton="true"] {{
                background-color: {theme["surface"]};
                border: 1px solid {role_color};
                color: {role_color};
                padding: 10px 20px;
                border-radius: 8px;
                font-size: 14px;
                font-weight: 500;
            }}
            QToolButton[actionButton="true"]:hover {{
                background-color: {role_color};
                color: white;
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

    def clear_content(self):
        """Clear all widgets from the content area to avoid duplication."""
        # Clear all widgets from the content layout
        while self._content_layout.count():
            item = self._content_layout.takeAt(0)
            widget = item.widget()
            if widget is not None:
                widget.deleteLater()
            else:
                # If it's a layout, clear it as well
                layout = item.layout()
                if layout is not None:
                    self._clear_layout(layout)
        
        logger.info("Content area cleared to prevent duplication")
    
    def _clear_layout(self, layout):
        """Recursively clear all widgets from a layout."""
        while layout.count():
            item = layout.takeAt(0)
            widget = item.widget()
            if widget is not None:
                widget.deleteLater()
            else:
                # If it's a nested layout, clear it as well
                nested_layout = item.layout()
                if nested_layout is not None:
                    self._clear_layout(nested_layout)
    
    def _setup_content(self):
        """Setup the main content area with statistics display."""
        # Clear existing content to avoid duplication
        self.clear_content()
        
        # Create main vertical layout with clean spacing
        main_layout = self.create_layout("vbox")
        main_layout.set_spacing(24)
        main_layout.set_margins(24, 24, 24, 24)
        
        # Add the main layout to content area
        self.add_layout_to_content(main_layout)
          
        # Dynamic welcome header
        self._setup_welcome_header(main_layout)
         
        # Quick actions section
        self._setup_quick_actions(main_layout)
         
        # Statistics section - show totals only, no management sections
        stats_layout = self.create_flex_layout(direction="row", wrap=True)
        stats_layout.set_spacing(20)
         
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
            stats_layout.add_widget(stat_card)
         
        # Add stats layout widget to main layout widget
        main_layout.add_layout(stats_layout)
        
        # Basic information card
        info_card = self.create_card(
            title="System Information",
            content="<p>Use the sidebar and top bar to navigate through the system.</p>"
        )
        info_card.setMinimumHeight(60)
        info_card.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        main_layout.add_widget(info_card)
    
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
                padding: 24px;
            }
        """)
         
        welcome_layout = QVBoxLayout(welcome_card)
        welcome_layout.setContentsMargins(16, 16, 16, 16)
        welcome_layout.setSpacing(16)
         
        # Personalized greeting with time-based and role-based message
        self._setup_personalized_greeting(welcome_layout)
        
        # Role-specific overview
        self._setup_role_overview(welcome_layout)
        
        # Contextual help tips
        self._setup_help_tips(welcome_layout)
        
        # System insights
        self._setup_system_insights(welcome_layout)
        
        main_layout.add_widget(welcome_card)
        
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
    
    def _setup_quick_actions(self, main_layout):
        """Setup the quick actions section with icon-prefixed buttons."""
        theme_manager = self.get_theme_manager()
        theme = theme_manager._themes[self.get_theme()]
        role_color = self._get_role_color()
        
        quick_actions_card = QFrame()
        quick_actions_card.setProperty("card", "true")
        quick_actions_card.setStyleSheet(f"""
            QFrame[card="true"] {{
                background-color: {theme["surface"]};
                border-radius: 12px;
                border: 1px solid {theme["border"]};
                padding: 24px;
            }}
        """)
        
        # Title for quick actions
        card_layout = QVBoxLayout(quick_actions_card)
        card_layout.setContentsMargins(24, 24, 24, 24)
        card_layout.setSpacing(16)
        
        title_label = QLabel("Quick Actions")
        title_font = QFont("Segoe UI", 16, QFont.Weight.SemiBold)
        title_label.setFont(title_font)
        title_label.setStyleSheet(f"color: {theme["text"]}; margin-bottom: 8px;")
        card_layout.addWidget(title_label)
         
        quick_actions_layout = QHBoxLayout()
        quick_actions_layout.setContentsMargins(0, 0, 0, 0)
        quick_actions_layout.setSpacing(12)
         
        # Quick action buttons with modern styling
        actions = [
            ("➕ Add Student", self._add_student),
            ("➕ Add Book", self._add_book),
            ("👁️ View Students", self._show_students),
            ("👁️ View Books", self._show_books),
        ]
         
        for text, callback in actions:
            btn = QToolButton()
            btn.setText(text)
            btn.setProperty("actionButton", "true")
            btn.setStyleSheet(f"""
                QToolButton[actionButton="true"] {{
                    background-color: {theme["surface"]};
                    border: 1px solid {role_color};
                    color: {role_color};
                    padding: 12px 20px;
                    border-radius: 8px;
                    font-size: 14px;
                    font-weight: 500;
                }}
                QToolButton[actionButton="true"]:hover {{
                    background-color: {role_color};
                    color: white;
                }}
            """)
            btn.clicked.connect(callback)
            quick_actions_layout.addWidget(btn)
        
        quick_actions_layout.addStretch()
        card_layout.addLayout(quick_actions_layout)
         
        main_layout.add_widget(quick_actions_card)
    
    def _create_modern_stat_card(self, title, count, icon):
        """Create modern web-style statistics card."""
        theme_manager = self.get_theme_manager()
        theme = theme_manager._themes[self.get_theme()]
        role_color = self._get_role_color()
        
        card = QFrame()
        card.setProperty("statCard", "true")
        card.setStyleSheet(f"""
            QFrame[statCard="true"] {{
                background-color: {theme["surface"]};
                border-radius: 12px;
                border-left: 4px solid {role_color};
                border: 1px solid {theme["border"]};
                padding: 20px;
            }}
            QFrame[statCard="true"]:hover {{
                border-color: {role_color};
                background-color: {theme["surface_hover"]};
            }}
        """)
        card.setMinimumWidth(180)
        card.setMaximumWidth(240)
        card.setMinimumHeight(140)
         
        layout = QVBoxLayout(card)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(12)
         
        # Icon and title
        title_label = QLabel(f"{icon} {title}")
        title_label.setStyleSheet(f"""
            font-size: 13px;
            color: {theme["text_secondary"]};
            font-weight: 500;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        """)
        layout.addWidget(title_label)
         
        # Large number with modern typography
        count_label = QLabel(count)
        count_font = QFont("Segoe UI", 32, QFont.Weight.Bold)
        count_label.setFont(count_font)
        count_label.setStyleSheet(f"color: {theme["text"]};")
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
        """Show view students window."""
        try:
            from school_system.gui.windows.student_window.view_students_window import ViewStudentsWindow
            window = ViewStudentsWindow(self, self.username, self.role)
            window.show()
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to open students window: {str(e)}")
    
    def _add_student(self):
        """Show add student window."""
        try:
            from school_system.gui.windows.student_window.add_student_window import AddStudentWindow
            window = AddStudentWindow(self, self.username, self.role)
            window.student_added.connect(lambda: logger.info("Student added, refresh if needed"))
            window.show()
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to open add student window: {str(e)}")
    
    def _manage_students(self):
        """Show view students window (same as _show_students)."""
        self._show_students()
    
    def _show_student_management(self):
        """Show the student management window (legacy - redirects to view students)."""
        self._show_students()
    
    def _show_edit_student(self):
        """Show edit student window."""
        try:
            from school_system.gui.windows.student_window.edit_student_window import EditStudentWindow
            window = EditStudentWindow(self, self.username, self.role)
            window.show()
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to open edit student window: {str(e)}")
    
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

    def _show_edit_teacher(self):
        """Show edit teacher window."""
        try:
            from school_system.gui.windows.teacher_window.edit_teacher_window import EditTeacherWindow
            window = EditTeacherWindow(self, self.username, self.role)
            window.show()
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to open edit teacher window: {str(e)}")

    def _show_teacher_import_export(self):
        """Show teacher import/export window."""
        try:
            from school_system.gui.windows.teacher_window.teacher_import_export_window import TeacherImportExportWindow
            window = TeacherImportExportWindow(self, self.username, self.role)
            window.show()
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to open teacher import/export window: {str(e)}")

    def _show_user_management(self):
        """Show user management window."""
        try:
            user_window = UserWindow(self, self.username, self.role)
            user_window.show()
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to open user management: {str(e)}")

    def _show_view_users(self):
        """Show view users window."""
        try:
            from school_system.gui.windows.user_window.view_users_window import ViewUsersWindow
            view_users_window = ViewUsersWindow(self, self.username, self.role)
            view_users_window.show()
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to open view users window: {str(e)}")
    
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

    def _show_borrow_book(self):
        """Show borrow book window."""
        try:
            from school_system.gui.windows.book_window.borrow_book_window import BorrowBookWindow
            borrow_window = BorrowBookWindow(self, self.username, self.role)
            borrow_window.show()
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to open borrow book window: {str(e)}")

    def _show_return_book(self):
        """Show return book window."""
        try:
            from school_system.gui.windows.book_window.return_book_window import ReturnBookWindow
            return_window = ReturnBookWindow(self, self.username, self.role)
            return_window.show()
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to open return book window: {str(e)}")

    def _show_distribution(self):
        """Show distribution window."""
        try:
            from school_system.gui.windows.book_window.distribution_window import DistributionWindow
            distribution_window = DistributionWindow(self, self.username, self.role)
            distribution_window.show()
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to open distribution window: {str(e)}")

    def _show_book_import_export(self):
        """Show book import/export window."""
        try:
            from school_system.gui.windows.book_window.book_import_export_window import BookImportExportWindow
            import_export_window = BookImportExportWindow(self, self.username, self.role)
            import_export_window.show()
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to open book import/export window: {str(e)}")
    
    def _show_furniture_management(self):
        """Show furniture management window."""
        try:
            from school_system.gui.windows.furniture_window.manage_furniture_window import ManageFurnitureWindow
            window = ManageFurnitureWindow(self, self.username, self.role)
            window.show()
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to open furniture management: {str(e)}")
    
    def _show_furniture_assignments(self):
        """Show furniture assignments window."""
        try:
            from school_system.gui.windows.furniture_window.furniture_assignments_window import FurnitureAssignmentsWindow
            window = FurnitureAssignmentsWindow(self, self.username, self.role)
            window.show()
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to open furniture assignments: {str(e)}")
    
    def _show_furniture_maintenance(self):
        """Show furniture maintenance window."""
        try:
            from school_system.gui.windows.furniture_window.furniture_maintenance_window import FurnitureMaintenanceWindow
            window = FurnitureMaintenanceWindow(self, self.username, self.role)
            window.show()
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to open furniture maintenance: {str(e)}")
    
    def _show_book_reports(self):
        """Show book reports window."""
        try:
            from school_system.gui.windows.report_window.book_reports_window import BookReportsWindow
            window = BookReportsWindow(self, self.username, self.role)
            window.show()
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to open book reports: {str(e)}")
    
    def _show_student_reports(self):
        """Show student reports window."""
        try:
            from school_system.gui.windows.report_window.student_reports_window import StudentReportsWindow
            window = StudentReportsWindow(self, self.username, self.role)
            window.show()
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to open student reports: {str(e)}")
    
    def _show_custom_reports(self):
        """Show custom reports window."""
        try:
            from school_system.gui.windows.report_window.custom_reports_window import CustomReportsWindow
            window = CustomReportsWindow(self, self.username, self.role)
            window.show()
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to open custom reports: {str(e)}")
    
    def _show_report_management(self):
        """Show the report management window (legacy - redirects to book reports)."""
        self._show_book_reports()
    
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
    
    def _show_ream_management_window(self):
        """Show the ream management window."""
        try:
            from school_system.gui.windows.student_window.ream_management_window import ReamManagementWindow
            window = ReamManagementWindow(self, self.username, self.role)
            window.show()
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to open ream management: {str(e)}")
    
    def closeEvent(self, event):
        """Handle window closing."""
        super().closeEvent(event)
