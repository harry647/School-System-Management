"""
Main application window for the School System Management.

This module provides the main GUI interface for the school system with
dropdown menus and dynamic content loading.
"""

from PyQt6.QtWidgets import (QLabel, QMessageBox, QMenuBar, QSizePolicy, QFrame,
                            QVBoxLayout, QToolButton, QHBoxLayout, QPushButton,
                            QLineEdit, QGridLayout, QSplitter, QScrollArea,
                            QStackedWidget, QWidget, QMenu)
from PyQt6.QtCore import Qt, QTime, QTimer, pyqtSignal
from PyQt6.QtGui import QIcon, QFont, QAction
from typing import Callable, Dict, Any

from school_system.config.logging import logger
from school_system.gui.base.base_window import BaseApplicationWindow
from school_system.gui.windows.user_window.user_window import UserWindow
from school_system.gui.windows.user_window.view_users_window import ViewUsersWindow
from school_system.gui.windows.user_window.add_user_window import AddUserWindow
from school_system.gui.windows.user_window.edit_user_window import EditUserWindow
from school_system.gui.windows.user_window.delete_user_window import DeleteUserWindow
from school_system.gui.windows.user_window.user_settings_window import UserSettingsWindow
from school_system.gui.windows.user_window.short_form_mappings_window import ShortFormMappingsWindow
from school_system.gui.windows.user_window.user_sessions_window import UserSessionsWindow
from school_system.gui.windows.user_window.user_activity_window import UserActivityWindow
from school_system.gui.windows.user_window.user_validation import UserValidator
from school_system.gui.windows.book_window import (
    BookWindow,
    BookAddWorkflow,
    BookEditWorkflow,
    BookBorrowWorkflow,
    BookReturnWorkflow
)
from school_system.gui.windows.book_window.book_import_export_window import BookImportExportWindow
from school_system.gui.windows.book_window.distribution_window import DistributionWindow
from school_system.gui.windows.furniture_window.manage_furniture_window import ManageFurnitureWindow
from school_system.gui.windows.furniture_window.furniture_assignments_window import FurnitureAssignmentsWindow
from school_system.gui.windows.furniture_window.furniture_maintenance_window import FurnitureMaintenanceWindow
from school_system.gui.windows.report_window.book_reports_window import BookReportsWindow
from school_system.gui.windows.report_window.student_reports_window import StudentReportsWindow
from school_system.gui.windows.report_window.custom_reports_window import CustomReportsWindow
from school_system.gui.windows.student_window.add_student_window import AddStudentWindow
from school_system.gui.windows.student_window.edit_student_window import EditStudentWindow
from school_system.gui.windows.student_window.view_students_window import ViewStudentsWindow
from school_system.gui.windows.student_window.ream_management_window import ReamManagementWindow
from school_system.gui.windows.teacher_window.add_teacher_window import AddTeacherWindow
from school_system.gui.windows.teacher_window.edit_teacher_window import EditTeacherWindow
from school_system.gui.windows.teacher_window.view_teachers_window import ViewTeachersWindow
from school_system.gui.windows.teacher_window.teacher_import_export_window import TeacherImportExportWindow


class MainWindow(BaseApplicationWindow):
    """Main application window for the school system with dropdown menus and dynamic content."""

    # Signal for content changes
    content_changed = pyqtSignal(str)

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

        # Content management
        self.current_view = "dashboard"
        self.content_views = {}

        # Connect theme change signal to update UI
        self.theme_changed.connect(self._on_theme_changed)
        self.content_changed.connect(self._on_content_changed)

        self._setup_role_based_menus()
        self._setup_main_layout()
        self._setup_sidebar()
        self._setup_content_area()
        self._setup_initial_content()
        self._apply_professional_styling()

        logger.info(f"Main window created for user {username} with role {role}")

    def _setup_main_layout(self):
        """Setup the main splitter layout for sidebar and content area."""
        self.main_splitter = QSplitter(Qt.Orientation.Horizontal)
        self.main_splitter.setHandleWidth(2)
        self.main_splitter.setStretchFactor(0, 0)  # Sidebar doesn't stretch
        self.main_splitter.setStretchFactor(1, 1)  # Content area stretches
        self.setCentralWidget(self.main_splitter)

    def _setup_sidebar(self):
        """Setup modern professional sidebar navigation with dropdown menus."""
        theme_manager = self.get_theme_manager()
        theme = theme_manager._themes[self.get_theme()]
        role_color = self._get_role_color()

        # Create sidebar frame with enhanced professional styling
        sidebar = QFrame()
        sidebar.setFixedWidth(300)
        sidebar.setProperty("sidebar", "true")
        sidebar.setStyleSheet(f"""
            QFrame[sidebar="true"] {{
                background-color: {theme["surface"]};
                border-right: 1px solid {theme["border"]};
                border-radius: 8px;
            }}
            QToolButton {{
                color: {theme["text"]};
                text-align: left;
                padding: 12px 20px;
                border: none;
                font-size: 13px;
                font-weight: 500;
                border-radius: 10px;
                margin: 2px 10px;
                min-height: 44px;
            }}
            QToolButton:hover {{
                background-color: {theme["surface_hover"]};
                color: {role_color};
            }}
            QToolButton:pressed {{
                background-color: {theme["border"]};
            }}
            QToolButton::menu-indicator {{
                image: none;
                width: 0px;
            }}
            QLabel[sectionHeader="true"] {{
                color: {theme["text_secondary"]};
                font-size: 10px;
                font-weight: 700;
                text-transform: uppercase;
                letter-spacing: 1.2px;
                padding: 12px 20px 8px 20px;
                margin-top: 8px;
                border-bottom: 1px solid {theme["border"]};
            }}
            QLabel[sectionIcon="true"] {{
                font-size: 14px;
                margin-right: 8px;
            }}
        """)

        # Create vertical layout for sidebar
        sidebar_layout = QVBoxLayout(sidebar)
        sidebar_layout.setContentsMargins(0, 20, 0, 20)
        sidebar_layout.setSpacing(8)

        # Logo/Brand section
        logo_section = QFrame()
        logo_section.setStyleSheet(f"""
            QFrame {{
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 {role_color}, stop:1 {theme["surface"]});
                border-radius: 0 0 16px 16px;
                margin: 0 10px 20px 10px;
                padding: 20px;
            }}
        """)
        logo_layout = QVBoxLayout(logo_section)
        logo_layout.setContentsMargins(10, 10, 10, 10)

        logo_label = QLabel("🏫")
        logo_label.setStyleSheet("font-size: 32px; text-align: center;")
        logo_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        brand_label = QLabel("School\nManager")
        brand_label.setStyleSheet(f"""
            color: white;
            font-size: 14px;
            font-weight: bold;
            text-align: center;
            line-height: 1.2;
        """)
        brand_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        logo_layout.addWidget(logo_label)
        logo_layout.addWidget(brand_label)
        sidebar_layout.addWidget(logo_section)

        # Dashboard button (prominent)
        dashboard_btn = QToolButton()
        dashboard_btn.setText("🏠 Dashboard")
        dashboard_btn.setToolButtonStyle(Qt.ToolButtonStyle.ToolButtonTextBesideIcon)
        dashboard_btn.setStyleSheet(f"""
            QToolButton {{
                background-color: {role_color};
                color: white;
                font-weight: 600;
                border-radius: 12px;
                margin: 8px 12px;
                padding: 16px 20px;
                font-size: 14px;
            }}
            QToolButton:hover {{
                background-color: {theme["primary"]};
            }}
        """)
        dashboard_btn.clicked.connect(lambda: self._load_content("dashboard"))
        sidebar_layout.addWidget(dashboard_btn)
        sidebar_layout.addSpacing(12)

        # Furniture Management buttons
        furniture_btn = QToolButton()
        furniture_btn.setText("🪑 Furniture Management")
        furniture_btn.setToolButtonStyle(Qt.ToolButtonStyle.ToolButtonTextBesideIcon)
        furniture_btn.setStyleSheet(f"""
            QToolButton {{
                background-color: {theme["surface"]};
                color: {theme["text"]};
                font-weight: 500;
                border-radius: 10px;
                margin: 2px 10px;
                padding: 12px 20px;
                font-size: 13px;
                border: 1px solid {theme["border"]};
            }}
            QToolButton:hover {{
                background-color: {theme["surface_hover"]};
                color: {role_color};
            }}
        """)
        furniture_btn.clicked.connect(lambda: self._load_content("manage_furniture"))
        sidebar_layout.addWidget(furniture_btn)

        # User Management buttons
        user_btn = QToolButton()
        user_btn.setText("👥 User Management")
        user_btn.setToolButtonStyle(Qt.ToolButtonStyle.ToolButtonTextBesideIcon)
        user_btn.setStyleSheet(f"""
            QToolButton {{
                background-color: {theme["surface"]};
                color: {theme["text"]};
                font-weight: 500;
                border-radius: 10px;
                margin: 2px 10px;
                padding: 12px 20px;
                font-size: 13px;
                border: 1px solid {theme["border"]};
            }}
            QToolButton:hover {{
                background-color: {theme["surface_hover"]};
                color: {role_color};
            }}
        """)
        user_btn.clicked.connect(lambda: self._load_content("manage_users"))
        sidebar_layout.addWidget(user_btn)

        sidebar_layout.addSpacing(16)

        # Core Management Sections with Dropdown Menus
        sections = [
            {
                "icon": "👨‍🎓",
                "title": "Student Management",
                "menu_items": [
                    ("👁️ View Students", "view_students"),
                    ("➕ Add Student", "add_student"),
                    ("✏️ Edit Student", "edit_student"),
                    ("📝 Class Management", "class_management"),
                    ("📚 Library Activity", "library_activity"),
                    ("📤 Import/Export", "student_import_export"),
                    ("📄 Ream Management", "ream_management"),
                ]
            },
            {
                "icon": "📚",
                "title": "Library Management",
                "menu_items": [
                    ("👁️ View Books", "view_books"),
                    ("➕ Add Book", "add_book"),
                    ("📖 Borrow Book", "borrow_book"),
                    ("↩️ Return Book", "return_book"),
                    ("📦 Distribution", "distribution"),
                    ("📤 Import/Export", "book_import_export"),
                ]
            },
            {
                "icon": "👩‍🏫",
                "title": "Staff Management",
                "menu_items": [
                    ("👁️ View Teachers", "view_teachers"),
                    ("➕ Add Teacher", "add_teacher"),
                    ("✏️ Edit Teacher", "edit_teacher"),
                    ("📤 Import/Export", "teacher_import_export"),
                ]
            },
            {
                "icon": "🪑",
                "title": "Facility Management",
                "menu_items": [
                    ("🪑 Manage Furniture", "manage_furniture"),
                    ("📋 Assignments", "furniture_assignments"),
                    ("🔧 Maintenance", "furniture_maintenance"),
                ]
            },
            {
                "icon": "👥",
                "title": "User Management",
                "menu_items": [
                    ("👤 Manage Users", "manage_users"),
                    ("👁️ View Users", "view_users"),
                    ("➕ Add User", "add_user"),
                    ("✏️ Edit User", "edit_user"),
                    ("🗑️ Delete User", "delete_user"),
                    ("⚙️ User Settings", "user_settings"),
                    ("🔤 Short Form Mappings", "short_form_mappings"),
                    ("🔐 User Sessions", "user_sessions"),
                    ("📊 User Activity", "user_activity"),
                ]
            },
            {
                "icon": "📊",
                "title": "Reports & Analytics",
                "menu_items": [
                    ("📊 Book Reports", "book_reports"),
                    ("📊 Student Reports", "student_reports"),
                    ("📊 Custom Reports", "custom_reports"),
                ]
            }
        ]

        # Add sections with dropdown menus
        for section in sections:
            # Section header with icon
            section_frame = QFrame()
            section_layout = QVBoxLayout(section_frame)
            section_layout.setContentsMargins(0, 0, 0, 0)
            section_layout.setSpacing(6)

            header_layout = QHBoxLayout()
            header_layout.setContentsMargins(20, 10, 20, 10)

            icon_label = QLabel(section["icon"])
            icon_label.setProperty("sectionIcon", "true")

            title_label = QLabel(section["title"].upper())
            title_label.setProperty("sectionHeader", "true")

            header_layout.addWidget(icon_label)
            header_layout.addWidget(title_label)
            header_layout.addStretch()

            section_layout.addLayout(header_layout)

            # Dropdown button for this section
            dropdown_btn = QToolButton()
            dropdown_btn.setText(f"  {section['title']} ▼")
            dropdown_btn.setToolButtonStyle(Qt.ToolButtonStyle.ToolButtonTextBesideIcon)
            dropdown_btn.setPopupMode(QToolButton.ToolButtonPopupMode.InstantPopup)
            dropdown_btn.setStyleSheet(f"""
                QToolButton {{
                    margin: 0 10px;
                }}
            """)

            # Create dropdown menu
            menu = QMenu(dropdown_btn)
            dropdown_btn.setMenu(menu)

            for text, action_id in section["menu_items"]:
                action = QAction(text, self)
                action.triggered.connect(lambda checked, aid=action_id: self._load_content(aid))
                menu.addAction(action)

            section_layout.addWidget(dropdown_btn)
            sidebar_layout.addWidget(section_frame)
            sidebar_layout.addSpacing(8)

        # Settings and Help section at bottom
        bottom_section = QFrame()
        bottom_layout = QVBoxLayout(bottom_section)
        bottom_layout.setContentsMargins(10, 10, 10, 10)
        bottom_layout.setSpacing(8)

        # Settings button
        settings_btn = QToolButton()
        settings_btn.setText("⚙️ Settings")
        settings_btn.setToolButtonStyle(Qt.ToolButtonStyle.ToolButtonTextBesideIcon)
        settings_btn.clicked.connect(lambda: self._load_content("settings"))
        bottom_layout.addWidget(settings_btn)

        # Help button
        help_btn = QToolButton()
        help_btn.setText("❓ Help & Support")
        help_btn.setToolButtonStyle(Qt.ToolButtonStyle.ToolButtonTextBesideIcon)
        help_btn.clicked.connect(lambda: self._load_content("help"))
        bottom_layout.addWidget(help_btn)

        sidebar_layout.addWidget(bottom_section)
        sidebar_layout.addSpacing(16)

        # Add stretch to push everything to top
        sidebar_layout.addStretch()

        # Create a scroll area for the sidebar
        sidebar_scroll = QScrollArea()
        sidebar_scroll.setWidgetResizable(True)
        sidebar_scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        sidebar_scroll.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        sidebar_scroll.setStyleSheet(f"""
            QScrollArea {{
                background-color: transparent;
                border: none;
            }}
            QScrollBar:vertical {{
                background-color: {theme["surface"]};
                width: 8px;
                border-radius: 4px;
            }}
            QScrollBar::handle:vertical {{
                background-color: {theme["border"]};
                border-radius: 4px;
            }}
            QScrollBar::handle:vertical:hover {{
                background-color: {theme["text_secondary"]};
            }}
        """)

        # Set the sidebar frame as the widget for the scroll area
        sidebar_scroll.setWidget(sidebar)

        # Add scrollable sidebar to splitter
        self.main_splitter.addWidget(sidebar_scroll)

    def _setup_content_area(self):
        """Setup the dynamic content area that loads different views."""
        theme_manager = self.get_theme_manager()
        theme = theme_manager._themes[self.get_theme()]

        # Create main content frame
        content_frame = QFrame()
        content_frame.setProperty("contentArea", "true")
        content_frame.setStyleSheet(f"""
            QFrame[contentArea="true"] {{
                background-color: {theme["background"]};
                border: none;
            }}
        """)

        # Create vertical layout for content
        content_layout = QVBoxLayout(content_frame)
        content_layout.setContentsMargins(0, 0, 0, 0)
        content_layout.setSpacing(0)

        # Add top bar to content area
        self._setup_top_bar()
        content_layout.addWidget(self.top_bar)

        # Create scroll area for content
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        scroll_area.setStyleSheet(f"""
            QScrollArea {{
                border: none;
                background-color: {theme["background"]};
                border-radius: 8px;
            }}
            QScrollBar:vertical {{
                background-color: {theme["surface"]};
                width: 12px;
                border-radius: 6px;
            }}
            QScrollBar::handle:vertical {{
                background-color: {theme["border"]};
                border-radius: 6px;
            }}
            QScrollBar::handle:vertical:hover {{
                background-color: {theme["text_secondary"]};
            }}
        """)

        # Create stacked widget for different content views
        self.content_stack = QStackedWidget()
        self.content_stack.setStyleSheet(f"""
            QStackedWidget {{
                background-color: {theme["background"]};
            }}
        """)

        scroll_area.setWidget(self.content_stack)
        scroll_area.setWidgetResizable(True)

        content_layout.addWidget(scroll_area)

        # Add content area to splitter
        self.main_splitter.addWidget(content_frame)

        # Set splitter proportions (sidebar : content = 1 : 3)
        self.main_splitter.setSizes([300, 900])

    def _setup_top_bar(self):
        """Setup modern professional top bar with search and advanced features."""
        theme_manager = self.get_theme_manager()
        theme = theme_manager._themes[self.get_theme()]
        role_color = self._get_role_color()

        self.top_bar = QFrame()
        self.top_bar.setFixedHeight(80)
        self.top_bar.setProperty("topBar", "true")
        self.top_bar.setStyleSheet(f"""
            QFrame[topBar="true"] {{
                background-color: {theme["surface"]};
                border-bottom: 1px solid {theme["border"]};
                border-radius: 8px;
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
            QLineEdit {{
                background-color: {theme["background"]};
                border: 1px solid {theme["border"]};
                border-radius: 20px;
                padding: 8px 16px;
                padding-left: 40px;
                font-size: 14px;
                color: {theme["text"]};
            }}
            QLineEdit:focus {{
                border-color: {role_color};
                background-color: {theme["surface"]};
            }}
            QLineEdit::placeholder {{
                color: {theme["text_secondary"]};
            }}
        """)

        # Create horizontal layout for top bar
        top_layout = QHBoxLayout(self.top_bar)
        top_layout.setContentsMargins(32, 16, 32, 16)
        top_layout.setSpacing(20)

        # Enhanced branding
        branding_frame = QFrame()
        branding_layout = QHBoxLayout(branding_frame)
        branding_layout.setContentsMargins(0, 0, 0, 0)
        branding_layout.setSpacing(12)

        logo_label = QLabel("🏫")
        logo_label.setStyleSheet("font-size: 28px;")

        brand_text = QFrame()
        brand_layout = QVBoxLayout(brand_text)
        brand_layout.setContentsMargins(0, 0, 0, 0)
        brand_layout.setSpacing(0)

        title_label = QLabel("School Management System")
        title_font = QFont("Segoe UI", 16, QFont.Weight.Bold)
        title_label.setFont(title_font)
        title_label.setStyleSheet(f"color: {theme['text']};")

        subtitle_label = QLabel("Professional Dashboard")
        subtitle_label.setStyleSheet(f"""
            color: {theme["text_secondary"]};
            font-size: 12px;
            font-weight: 400;
        """)

        brand_layout.addWidget(title_label)
        brand_layout.addWidget(subtitle_label)

        branding_layout.addWidget(logo_label)
        branding_layout.addWidget(brand_text)

        top_layout.addWidget(branding_frame)

        # Search bar
        search_frame = QFrame()
        search_layout = QHBoxLayout(search_frame)
        search_layout.setContentsMargins(0, 0, 0, 0)
        search_layout.setSpacing(0)

        search_icon = QLabel("🔍")
        search_icon.setStyleSheet("font-size: 16px; margin-left: 12px;")

        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Search students, books, users...")
        self.search_input.setMinimumWidth(300)
        self.search_input.textChanged.connect(self._on_search_text_changed)

        search_layout.addWidget(search_icon)
        search_layout.addWidget(self.search_input)

        top_layout.addWidget(search_frame)

        # Spacer
        top_layout.addStretch()

        # Quick action buttons
        quick_actions_layout = QHBoxLayout()
        quick_actions_layout.setSpacing(8)

        # Theme toggle
        theme_btn = QToolButton()
        theme_btn.setText("🌙")
        theme_btn.setToolTip("Toggle Theme")
        theme_btn.clicked.connect(self._toggle_theme)
        theme_btn.setStyleSheet(f"""
            QToolButton {{
                background-color: transparent;
                border: none;
                border-radius: 8px;
                padding: 8px;
                font-size: 16px;
            }}
            QToolButton:hover {{
                background-color: {theme["surface_hover"]};
            }}
        """)
        quick_actions_layout.addWidget(theme_btn)

        # Notifications
        notif_btn = QToolButton()
        notif_btn.setText("🔔")
        notif_btn.setToolTip("Notifications")
        notif_btn.clicked.connect(self._show_notifications)
        notif_btn.setStyleSheet(f"""
            QToolButton {{
                background-color: transparent;
                border: none;
                border-radius: 8px;
                padding: 8px;
                font-size: 16px;
            }}
            QToolButton:hover {{
                background-color: {theme["surface_hover"]};
            }}
        """)
        quick_actions_layout.addWidget(notif_btn)

        top_layout.addLayout(quick_actions_layout)

        # User info section
        user_frame = QFrame()
        user_layout = QHBoxLayout(user_frame)
        user_layout.setContentsMargins(0, 0, 0, 0)
        user_layout.setSpacing(12)

        # User avatar and info
        user_info_frame = QFrame()
        user_info_layout = QHBoxLayout(user_info_frame)
        user_info_layout.setContentsMargins(0, 0, 0, 0)
        user_info_layout.setSpacing(8)

        avatar_label = QLabel("👤")
        avatar_label.setStyleSheet(f"""
            font-size: 24px;
            background-color: {role_color};
            color: white;
            border-radius: 12px;
            padding: 4px;
        """)

        user_details = QFrame()
        details_layout = QVBoxLayout(user_details)
        details_layout.setContentsMargins(0, 0, 0, 0)
        details_layout.setSpacing(0)

        username_label = QLabel(self.username)
        username_label.setStyleSheet(f"""
            font-size: 14px;
            font-weight: 600;
            color: {theme["text"]};
        """)

        role_label = QLabel(self.role.capitalize())
        role_label.setStyleSheet(f"""
            font-size: 11px;
            color: {theme["text_secondary"]};
            font-weight: 500;
        """)

        details_layout.addWidget(username_label)
        details_layout.addWidget(role_label)

        user_info_layout.addWidget(avatar_label)
        user_info_layout.addWidget(user_details)

        # Role badge
        role_badge = QLabel(self.role.upper())
        role_badge.setStyleSheet(f"""
            font-size: 10px;
            font-weight: 700;
            color: white;
            background-color: {role_color};
            padding: 4px 8px;
            border-radius: 6px;
            letter-spacing: 0.5px;
        """)

        # Logout button
        logout_btn = QToolButton()
        logout_btn.setText("🚪")
        logout_btn.setToolTip("Logout")
        logout_btn.clicked.connect(self._on_logout)
        logout_btn.setStyleSheet(f"""
            QToolButton {{
                background-color: transparent;
                border: 1px solid {theme["border"]};
                border-radius: 8px;
                padding: 6px 12px;
                font-size: 14px;
            }}
            QToolButton:hover {{
                background-color: #ffebee;
                border-color: #f44336;
                color: #f44336;
            }}
        """)

        user_layout.addWidget(user_info_frame)
        user_layout.addWidget(role_badge)
        user_layout.addWidget(logout_btn)

        top_layout.addWidget(user_frame)

    def _setup_initial_content(self):
        """Setup initial dashboard content."""
        self._load_content("dashboard")

    def _load_content(self, content_id: str):
        """Load and display the specified content view."""
        try:
            if content_id in self.content_views:
                # Switch to existing view
                self.content_stack.setCurrentWidget(self.content_views[content_id])
            else:
                # Create new view
                view = self._create_content_view(content_id)
                if view:
                    self.content_views[content_id] = view
                    self.content_stack.addWidget(view)
                    self.content_stack.setCurrentWidget(view)

            self.current_view = content_id
            self.content_changed.emit(content_id)
            logger.info(f"Loaded content view: {content_id}")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to load content: {str(e)}")
            logger.error(f"Error loading content view {content_id}: {str(e)}")

    def _create_content_view(self, content_id: str) -> QWidget:
        """Create a content view widget for the given content ID."""
        theme_manager = self.get_theme_manager()
        theme = theme_manager._themes[self.get_theme()]
        role_color = self._get_role_color()

        # Content view mapping
        content_creators = {
            "dashboard": self._create_dashboard_view,
            "view_students": lambda: self._create_view_students_view(),
            "add_student": lambda: self._create_add_student_view(),
            "edit_student": lambda: self._create_edit_student_view(),
            "view_books": lambda: self._create_view_books_view(),
            "add_book": lambda: self._create_add_book_view(),
            "borrow_book": lambda: self._create_borrow_book_view(),
            "return_book": lambda: self._create_return_book_view(),
            "distribution": lambda: self._create_distribution_view(),
            "book_import_export": lambda: self._create_book_import_export_view(),
            "view_teachers": lambda: self._create_view_teachers_view(),
            "add_teacher": lambda: self._create_add_teacher_view(),
            "edit_teacher": lambda: self._create_edit_teacher_view(),
            "teacher_import_export": lambda: self._create_teacher_import_export_view(),
            "manage_users": lambda: self._create_manage_users_view(),
            "view_users": lambda: self._create_view_users_view(),
            "add_user": lambda: self._create_add_user_view(),
            "edit_user": lambda: self._create_edit_user_view(),
            "delete_user": lambda: self._create_delete_user_view(),
            "user_settings": lambda: self._create_user_settings_view(),
            "short_form_mappings": lambda: self._create_short_form_mappings_view(),
            "user_sessions": lambda: self._create_user_sessions_view(),
            "user_activity": lambda: self._create_user_activity_view(),
            "settings": lambda: self._create_settings_view(),
            "help": lambda: self._create_help_view(),
            "manage_furniture": lambda: self._create_manage_furniture_view(),
            "furniture_assignments": lambda: self._create_furniture_assignments_view(),
            "furniture_maintenance": lambda: self._create_furniture_maintenance_view(),
            "book_reports": lambda: self._create_book_reports_view(),
            "student_reports": lambda: self._create_student_reports_view(),
            "custom_reports": lambda: self._create_custom_reports_view(),
            "ream_management": lambda: self._create_ream_management_view(),
            "class_management": lambda: self._create_class_management_view(),
            "library_activity": lambda: self._create_library_activity_view(),
            "student_import_export": lambda: self._create_student_import_export_view(),
        }
        
        # Add error handling for missing or corrupted files
        try:
            # Verify that all furniture windows can be imported
            from school_system.gui.windows.furniture_window.manage_furniture_window import ManageFurnitureWindow
            from school_system.gui.windows.furniture_window.furniture_assignments_window import FurnitureAssignmentsWindow
            from school_system.gui.windows.furniture_window.furniture_maintenance_window import FurnitureMaintenanceWindow
            logger.info("All furniture windows imported successfully")
        except ImportError as e:
            logger.error(f"Failed to import furniture windows: {str(e)}")
            QMessageBox.critical(self, "Error", f"Failed to load furniture module: {str(e)}")
        except Exception as e:
            logger.error(f"Unexpected error loading furniture module: {str(e)}")
            QMessageBox.critical(self, "Error", f"Unexpected error loading furniture module: {str(e)}")

        # Add error handling for user windows
        try:
            # Verify that all user windows can be imported
            from school_system.gui.windows.user_window.user_window import UserWindow
            from school_system.gui.windows.user_window.view_users_window import ViewUsersWindow
            from school_system.gui.windows.user_window.add_user_window import AddUserWindow
            from school_system.gui.windows.user_window.edit_user_window import EditUserWindow
            from school_system.gui.windows.user_window.delete_user_window import DeleteUserWindow
            from school_system.gui.windows.user_window.user_settings_window import UserSettingsWindow
            from school_system.gui.windows.user_window.short_form_mappings_window import ShortFormMappingsWindow
            from school_system.gui.windows.user_window.user_sessions_window import UserSessionsWindow
            from school_system.gui.windows.user_window.user_activity_window import UserActivityWindow
            logger.info("All user windows imported successfully")
        except ImportError as e:
            logger.error(f"Failed to import user windows: {str(e)}")
            QMessageBox.critical(self, "Error", f"Failed to load user module: {str(e)}")
        except Exception as e:
            logger.error(f"Unexpected error loading user module: {str(e)}")
            QMessageBox.critical(self, "Error", f"Unexpected error loading user module: {str(e)}")

        # Add error handling for student windows
        try:
            # Verify that all student windows can be imported
            from school_system.gui.windows.student_window.add_student_window import AddStudentWindow
            from school_system.gui.windows.student_window.edit_student_window import EditStudentWindow
            from school_system.gui.windows.student_window.view_students_window import ViewStudentsWindow
            from school_system.gui.windows.student_window.ream_management_window import ReamManagementWindow
            from school_system.gui.windows.student_window.student_import_export_window import StudentImportExportWindow
            from school_system.gui.windows.student_window.class_management_window import ClassManagementWindow
            from school_system.gui.windows.student_window.library_activity_window import LibraryActivityWindow
            logger.info("All student windows imported successfully")
        except ImportError as e:
            logger.error(f"Failed to import student windows: {str(e)}")
            QMessageBox.critical(self, "Error", f"Failed to load student module: {str(e)}")
        except Exception as e:
            logger.error(f"Unexpected error loading student module: {str(e)}")
            QMessageBox.critical(self, "Error", f"Unexpected error loading student module: {str(e)}")

        # Add error handling for report windows
        try:
            # Verify that all report windows can be imported
            from school_system.gui.windows.report_window.book_reports_window import BookReportsWindow
            from school_system.gui.windows.report_window.student_reports_window import StudentReportsWindow
            from school_system.gui.windows.report_window.custom_reports_window import CustomReportsWindow
            logger.info("All report windows imported successfully")
        except ImportError as e:
            logger.error(f"Failed to import report windows: {str(e)}")
            QMessageBox.critical(self, "Error", f"Failed to load report module: {str(e)}")
        except Exception as e:
            logger.error(f"Unexpected error loading report module: {str(e)}")
            QMessageBox.critical(self, "Error", f"Unexpected error loading report module: {str(e)}")

        # Add error handling for teacher windows
        try:
            # Verify that all teacher windows can be imported
            from school_system.gui.windows.teacher_window.add_teacher_window import AddTeacherWindow
            from school_system.gui.windows.teacher_window.edit_teacher_window import EditTeacherWindow
            from school_system.gui.windows.teacher_window.view_teachers_window import ViewTeachersWindow
            from school_system.gui.windows.teacher_window.teacher_import_export_window import TeacherImportExportWindow
            logger.info("All teacher windows imported successfully")
        except ImportError as e:
            logger.error(f"Failed to import teacher windows: {str(e)}")
            QMessageBox.critical(self, "Error", f"Failed to load teacher module: {str(e)}")
        except Exception as e:
            logger.error(f"Unexpected error loading teacher module: {str(e)}")
            QMessageBox.critical(self, "Error", f"Unexpected error loading teacher module: {str(e)}")

        try:
            creator = content_creators.get(content_id)
            if creator:
                return creator()
            else:
                # Default empty view
                return self._create_default_view(content_id, theme, role_color)
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to create content view: {str(e)}")
            logger.error(f"Error creating content view {content_id}: {str(e)}")
            return self._create_default_view(content_id, theme, role_color)

    def _create_dashboard_view(self) -> QWidget:
        """Create the main dashboard view."""
        theme_manager = self.get_theme_manager()
        theme = theme_manager._themes[self.get_theme()]
        role_color = self._get_role_color()

        scroll_widget = QWidget()
        layout = QVBoxLayout(scroll_widget)
        layout.setContentsMargins(32, 32, 32, 32)
        layout.setSpacing(32)

        # Enhanced welcome header
        welcome_card = QFrame()
        welcome_card.setObjectName("welcomeHeader")
        welcome_card.setStyleSheet(f"""
            QFrame#welcomeHeader {{
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 {role_color}, stop:1 {theme["primary"]});
                border-radius: 16px;
                padding: 24px;
                color: white;
                border: 1px solid {role_color};
            }}
        """)

        welcome_layout = QVBoxLayout(welcome_card)
        welcome_layout.setContentsMargins(16, 16, 16, 16)
        welcome_layout.setSpacing(16)

        # Personalized greeting
        current_time = QTime.currentTime()
        hour = current_time.hour()
        if hour < 12:
            time_greeting = "Good morning"
        elif hour < 18:
            time_greeting = "Good afternoon"
        else:
            time_greeting = "Good evening"

        role_capitalized = self.role.capitalize()
        if self.role == 'admin':
            role_message = "Administrator"
        elif self.role == 'teacher':
            role_message = "Educator"
        else:
            role_message = role_capitalized

        greeting_label = QLabel(f"{time_greeting}, {role_message} {self.username}! 👋")
        greeting_label.setStyleSheet("font-size: 24px; font-weight: bold;")
        welcome_layout.addWidget(greeting_label)

        welcome_label = QLabel("Welcome back! Here's what's new today:")
        welcome_label.setStyleSheet("font-size: 16px; color: rgba(255, 255, 255, 0.9);")
        welcome_layout.addWidget(welcome_label)

        layout.addWidget(welcome_card)

        # Top dashboard row - Quick Actions and Key Metrics
        self._setup_dashboard_top_row(layout)

        # Middle dashboard row - Statistics and Activity
        self._setup_dashboard_middle_row(layout)

        # Bottom dashboard row - Additional widgets and notifications
        self._setup_dashboard_bottom_row(layout)

        return scroll_widget

    def _setup_dashboard_top_row(self, layout):
        """Setup the top row with quick actions and key performance indicators."""
        theme_manager = self.get_theme_manager()
        theme = theme_manager._themes[self.get_theme()]
        role_color = self._get_role_color()

        # Create horizontal layout for top row
        top_row_layout = QHBoxLayout()
        top_row_layout.setSpacing(24)

        # Quick Actions Panel (Left side)
        quick_actions_panel = self._create_quick_actions_panel()
        top_row_layout.addWidget(quick_actions_panel, 2)  # 2/3 width

        # Key Metrics Panel (Right side)
        key_metrics_panel = self._create_key_metrics_panel()
        top_row_layout.addWidget(key_metrics_panel, 1)  # 1/3 width

        layout.addLayout(top_row_layout)

    def _setup_dashboard_middle_row(self, layout):
        """Setup the middle row with detailed statistics and recent activity."""
        # Create horizontal layout for middle row
        middle_row_layout = QHBoxLayout()
        middle_row_layout.setSpacing(24)

        # Statistics Grid (Left side)
        stats_panel = self._create_statistics_grid()
        middle_row_layout.addWidget(stats_panel, 2)  # 2/3 width

        # Activity Panel (Right side)
        activity_panel = self._create_activity_panel()
        middle_row_layout.addWidget(activity_panel, 1)  # 1/3 width

        layout.addLayout(middle_row_layout)

    def _setup_dashboard_bottom_row(self, layout):
        """Setup the bottom row with notifications and system alerts."""
        # Create horizontal layout for bottom row
        bottom_row_layout = QHBoxLayout()
        bottom_row_layout.setSpacing(24)

        # Notifications Panel
        notifications_panel = self._create_notifications_panel()
        bottom_row_layout.addWidget(notifications_panel, 1)

        # System Alerts Panel
        alerts_panel = self._create_system_alerts_panel()
        bottom_row_layout.addWidget(alerts_panel, 1)

        # Calendar/Events Panel
        calendar_panel = self._create_calendar_panel()
        bottom_row_layout.addWidget(calendar_panel, 1)

        layout.addLayout(bottom_row_layout)

    def _create_view_students_view(self) -> QWidget:
        """Create the view students content view."""
        theme_manager = self.get_theme_manager()
        theme = theme_manager._themes[self.get_theme()]

        scroll_widget = QWidget()
        layout = QVBoxLayout(scroll_widget)
        layout.setContentsMargins(32, 32, 32, 32)
        layout.setSpacing(20)

        # Header
        header = QLabel("👨‍🎓 Student Management")
        header.setStyleSheet(f"""
            font-size: 28px;
            font-weight: bold;
            color: {theme["text"]};
            margin-bottom: 16px;
        """)
        layout.addWidget(header)

        # Content area for student list/table
        content_card = QFrame()
        content_card.setProperty("contentCard", "true")
        content_card.setStyleSheet(f"""
            QFrame[contentCard="true"] {{
                background-color: {theme["surface"]};
                border-radius: 12px;
                border: 1px solid {theme["border"]};
                padding: 24px;
            }}
        """)

        card_layout = QVBoxLayout(content_card)

        # Placeholder for student table/list
        placeholder_label = QLabel("Student list and management tools will be displayed here.\n\nUse the buttons below to manage students.")
        placeholder_label.setStyleSheet(f"""
            font-size: 16px;
            color: {theme["text_secondary"]};
            text-align: center;
        """)
        placeholder_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        card_layout.addWidget(placeholder_label)

        # Action buttons
        actions_layout = QHBoxLayout()
        actions_layout.setSpacing(12)

        add_btn = QPushButton("➕ Add Student")
        add_btn.clicked.connect(lambda: self._load_content("add_student"))
        add_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {theme["primary"]};
                color: white;
                border: none;
                border-radius: 8px;
                padding: 12px 24px;
                font-size: 14px;
                font-weight: 500;
            }}
            QPushButton:hover {{
                background-color: {theme["primary"]};
                opacity: 0.9;
            }}
        """)

        edit_btn = QPushButton("✏️ Edit Student")
        edit_btn.clicked.connect(lambda: self._load_content("edit_student"))
        edit_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {theme["surface"]};
                color: {theme["text"]};
                border: 1px solid {theme["border"]};
                border-radius: 8px;
                padding: 12px 24px;
                font-size: 14px;
                font-weight: 500;
            }}
            QPushButton:hover {{
                background-color: {theme["surface_hover"]};
            }}
        """)

        actions_layout.addWidget(add_btn)
        actions_layout.addWidget(edit_btn)
        actions_layout.addStretch()

        card_layout.addLayout(actions_layout)

        layout.addWidget(content_card)
        layout.addStretch()

        return scroll_widget

    def _create_add_student_view(self) -> QWidget:
        """Create the add student content view."""
        theme_manager = self.get_theme_manager()
        theme = theme_manager._themes[self.get_theme()]

        scroll_widget = QWidget()
        layout = QVBoxLayout(scroll_widget)
        layout.setContentsMargins(32, 32, 32, 32)
        layout.setSpacing(20)

        # Header
        header = QLabel("➕ Add New Student")
        header.setStyleSheet(f"""
            font-size: 28px;
            font-weight: bold;
            color: {theme["text"]};
            margin-bottom: 16px;
        """)
        layout.addWidget(header)

        # Form placeholder
        content_card = QFrame()
        content_card.setProperty("contentCard", "true")
        content_card.setStyleSheet(f"""
            QFrame[contentCard="true"] {{
                background-color: {theme["surface"]};
                border-radius: 12px;
                border: 1px solid {theme["border"]};
                padding: 32px;
            }}
        """)

        card_layout = QVBoxLayout(content_card)

        form_placeholder = QLabel("Student registration form will be displayed here.\n\nFields: Name, Grade, Contact Info, etc.")
        form_placeholder.setStyleSheet(f"""
            font-size: 16px;
            color: {theme["text_secondary"]};
            text-align: center;
        """)
        form_placeholder.setAlignment(Qt.AlignmentFlag.AlignCenter)
        card_layout.addWidget(form_placeholder)

        layout.addWidget(content_card)
        layout.addStretch()

        return scroll_widget

    def _create_edit_student_view(self) -> QWidget:
        """Create the edit student content view."""
        theme_manager = self.get_theme_manager()
        theme = theme_manager._themes[self.get_theme()]

        scroll_widget = QWidget()
        layout = QVBoxLayout(scroll_widget)
        layout.setContentsMargins(32, 32, 32, 32)
        layout.setSpacing(20)

        # Header
        header = QLabel("✏️ Edit Student")
        header.setStyleSheet(f"""
            font-size: 28px;
            font-weight: bold;
            color: {theme["text"]};
            margin-bottom: 16px;
        """)
        layout.addWidget(header)

        # Content placeholder
        content_card = QFrame()
        content_card.setProperty("contentCard", "true")
        content_card.setStyleSheet(f"""
            QFrame[contentCard="true"] {{
                background-color: {theme["surface"]};
                border-radius: 12px;
                border: 1px solid {theme["border"]};
                padding: 32px;
            }}
        """)

        card_layout = QVBoxLayout(content_card)

        placeholder = QLabel("Student selection and editing form will be displayed here.\n\nSelect a student to edit their information.")
        placeholder.setStyleSheet(f"""
            font-size: 16px;
            color: {theme["text_secondary"]};
            text-align: center;
        """)
        placeholder.setAlignment(Qt.AlignmentFlag.AlignCenter)
        card_layout.addWidget(placeholder)

        layout.addWidget(content_card)
        layout.addStretch()

        return scroll_widget

    def _create_ream_management_view(self) -> QWidget:
        """Create the ream management content view."""
        theme_manager = self.get_theme_manager()
        theme = theme_manager._themes[self.get_theme()]
        role_color = self._get_role_color()

        scroll_widget = QWidget()
        layout = QVBoxLayout(scroll_widget)
        layout.setContentsMargins(32, 32, 32, 32)
        layout.setSpacing(20)

        # Header
        header = QLabel("📄 Ream Management")
        header.setStyleSheet(f"""
            font-size: 28px;
            font-weight: bold;
            color: {theme["text"]};
            margin-bottom: 16px;
        """)
        layout.addWidget(header)

        # Content area
        content_card = QFrame()
        content_card.setProperty("contentCard", "true")
        content_card.setStyleSheet(f"""
            QFrame[contentCard="true"] {{
                background-color: {theme["surface"]};
                border-radius: 12px;
                border: 1px solid {theme["border"]};
                padding: 24px;
            }}
        """)

        card_layout = QVBoxLayout(content_card)

        # Description
        desc_label = QLabel("Manage student ream allocations and track usage.")
        desc_label.setStyleSheet(f"""
            font-size: 16px;
            color: {theme["text_secondary"]};
            margin-bottom: 16px;
        """)
        card_layout.addWidget(desc_label)

        # Action buttons
        actions_layout = QHBoxLayout()
        actions_layout.setSpacing(12)

        open_ream_btn = QPushButton("📄 Open Ream Management")
        open_ream_btn.clicked.connect(self._show_ream_management_window)
        open_ream_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {role_color};
                color: white;
                border: none;
                padding: 12px 24px;
                border-radius: 8px;
                font-size: 14px;
                font-weight: 500;
            }}
            QPushButton:hover {{
                background-color: {theme["primary"]};
            }}
        """)
        actions_layout.addWidget(open_ream_btn)

        actions_layout.addStretch()
        card_layout.addLayout(actions_layout)

        layout.addWidget(content_card)
        layout.addStretch()

        return scroll_widget

    def _create_class_management_view(self) -> QWidget:
        """Create the class management content view."""
        theme_manager = self.get_theme_manager()
        theme = theme_manager._themes[self.get_theme()]
        role_color = self._get_role_color()

        scroll_widget = QWidget()
        layout = QVBoxLayout(scroll_widget)
        layout.setContentsMargins(32, 32, 32, 32)
        layout.setSpacing(20)

        # Header
        header = QLabel("📝 Class Management")
        header.setStyleSheet(f"""
            font-size: 28px;
            font-weight: bold;
            color: {theme["text"]};
            margin-bottom: 16px;
        """)
        layout.addWidget(header)

        # Content area
        content_card = QFrame()
        content_card.setProperty("contentCard", "true")
        content_card.setStyleSheet(f"""
            QFrame[contentCard="true"] {{
                background-color: {theme["surface"]};
                border-radius: 12px;
                border: 1px solid {theme["border"]};
                padding: 24px;
            }}
        """)

        card_layout = QVBoxLayout(content_card)

        # Description
        desc_label = QLabel("Create and manage student classes, assign students to classes, and track class statistics.")
        desc_label.setStyleSheet(f"""
            font-size: 16px;
            color: {theme["text_secondary"]};
            margin-bottom: 16px;
        """)
        desc_label.setWordWrap(True)
        card_layout.addWidget(desc_label)

        # Action buttons
        actions_layout = QHBoxLayout()
        actions_layout.setSpacing(12)

        open_class_btn = QPushButton("📝 Open Class Management")
        open_class_btn.clicked.connect(lambda: self._show_class_management_window())
        open_class_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {role_color};
                color: white;
                border: none;
                padding: 12px 24px;
                border-radius: 8px;
                font-size: 14px;
                font-weight: 500;
            }}
            QPushButton:hover {{
                background-color: {theme["primary"]};
            }}
        """)
        actions_layout.addWidget(open_class_btn)

        actions_layout.addStretch()
        card_layout.addLayout(actions_layout)

        layout.addWidget(content_card)
        layout.addStretch()

        return scroll_widget

    def _create_library_activity_view(self) -> QWidget:
        """Create the library activity content view."""
        theme_manager = self.get_theme_manager()
        theme = theme_manager._themes[self.get_theme()]
        role_color = self._get_role_color()

        scroll_widget = QWidget()
        layout = QVBoxLayout(scroll_widget)
        layout.setContentsMargins(32, 32, 32, 32)
        layout.setSpacing(20)

        # Header
        header = QLabel("📚 Library Activity")
        header.setStyleSheet(f"""
            font-size: 28px;
            font-weight: bold;
            color: {theme["text"]};
            margin-bottom: 16px;
        """)
        layout.addWidget(header)

        # Content area
        content_card = QFrame()
        content_card.setProperty("contentCard", "true")
        content_card.setStyleSheet(f"""
            QFrame[contentCard="true"] {{
                background-color: {theme["surface"]};
                border-radius: 12px;
                border: 1px solid {theme["border"]};
                padding: 24px;
            }}
        """)

        card_layout = QVBoxLayout(content_card)

        # Description
        desc_label = QLabel("Manage student library activities including book borrowing, returns, and track overdue books.")
        desc_label.setStyleSheet(f"""
            font-size: 16px;
            color: {theme["text_secondary"]};
            margin-bottom: 16px;
        """)
        desc_label.setWordWrap(True)
        card_layout.addWidget(desc_label)

        # Action buttons
        actions_layout = QHBoxLayout()
        actions_layout.setSpacing(12)

        borrow_btn = QPushButton("📖 Borrow Book")
        borrow_btn.clicked.connect(lambda: self._load_content("borrow_book"))
        borrow_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {role_color};
                color: white;
                border: none;
                padding: 12px 24px;
                border-radius: 8px;
                font-size: 14px;
                font-weight: 500;
            }}
            QPushButton:hover {{
                background-color: {theme["primary"]};
            }}
        """)
        actions_layout.addWidget(borrow_btn)

        return_btn = QPushButton("↩️ Return Book")
        return_btn.clicked.connect(lambda: self._load_content("return_book"))
        return_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {theme["success"]};
                color: white;
                border: none;
                padding: 12px 24px;
                border-radius: 8px;
                font-size: 14px;
                font-weight: 500;
            }}
            QPushButton:hover {{
                background-color: #28a745;
            }}
        """)
        actions_layout.addWidget(return_btn)

        full_activity_btn = QPushButton("📚 Full Activity Management")
        full_activity_btn.clicked.connect(lambda: self._show_library_activity_window())
        full_activity_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {theme["secondary"]};
                color: white;
                border: none;
                padding: 12px 24px;
                border-radius: 8px;
                font-size: 14px;
                font-weight: 500;
            }}
            QPushButton:hover {{
                background-color: {theme["primary"]};
            }}
        """)
        actions_layout.addWidget(full_activity_btn)

        actions_layout.addStretch()
        card_layout.addLayout(actions_layout)

        layout.addWidget(content_card)
        layout.addStretch()

        return scroll_widget

    def _create_student_import_export_view(self) -> QWidget:
        """Create the student import/export content view."""
        theme_manager = self.get_theme_manager()
        theme = theme_manager._themes[self.get_theme()]
        role_color = self._get_role_color()

        scroll_widget = QWidget()
        layout = QVBoxLayout(scroll_widget)
        layout.setContentsMargins(32, 32, 32, 32)
        layout.setSpacing(20)

        # Header
        header = QLabel("📤 Student Import/Export")
        header.setStyleSheet(f"""
            font-size: 28px;
            font-weight: bold;
            color: {theme["text"]};
            margin-bottom: 16px;
        """)
        layout.addWidget(header)

        # Content area
        content_card = QFrame()
        content_card.setProperty("contentCard", "true")
        content_card.setStyleSheet(f"""
            QFrame[contentCard="true"] {{
                background-color: {theme["surface"]};
                border-radius: 12px;
                border: 1px solid {theme["border"]};
                padding: 24px;
            }}
        """)

        card_layout = QVBoxLayout(content_card)

        # Description
        desc_label = QLabel("Import student data from CSV, Excel, or JSON files, or export student data for backup or analysis.")
        desc_label.setStyleSheet(f"""
            font-size: 16px;
            color: {theme["text_secondary"]};
            margin-bottom: 16px;
        """)
        desc_label.setWordWrap(True)
        card_layout.addWidget(desc_label)

        # Action buttons
        actions_layout = QHBoxLayout()
        actions_layout.setSpacing(12)

        import_btn = QPushButton("📥 Import Students")
        import_btn.clicked.connect(self._show_student_import_export)
        import_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {role_color};
                color: white;
                border: none;
                padding: 12px 24px;
                border-radius: 8px;
                font-size: 14px;
                font-weight: 500;
            }}
            QPushButton:hover {{
                background-color: {theme["primary"]};
            }}
        """)
        actions_layout.addWidget(import_btn)

        export_btn = QPushButton("📤 Export Students")
        export_btn.clicked.connect(self._show_student_import_export)
        export_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {theme["success"]};
                color: white;
                border: none;
                padding: 12px 24px;
                border-radius: 8px;
                font-size: 14px;
                font-weight: 500;
            }}
            QPushButton:hover {{
                background-color: #28a745;
            }}
        """)
        actions_layout.addWidget(export_btn)

        actions_layout.addStretch()
        card_layout.addLayout(actions_layout)

        layout.addWidget(content_card)
        layout.addStretch()

        return scroll_widget

    def _create_view_books_view(self) -> QWidget:
        """Create the view books content view."""
        theme_manager = self.get_theme_manager()
        theme = theme_manager._themes[self.get_theme()]

        scroll_widget = QWidget()
        layout = QVBoxLayout(scroll_widget)
        layout.setContentsMargins(32, 32, 32, 32)
        layout.setSpacing(20)

        # Header
        header = QLabel("📚 Library Management")
        header.setStyleSheet(f"""
            font-size: 28px;
            font-weight: bold;
            color: {theme["text"]};
            margin-bottom: 16px;
        """)
        layout.addWidget(header)

        # Content area for book list/table
        content_card = QFrame()
        content_card.setProperty("contentCard", "true")
        content_card.setStyleSheet(f"""
            QFrame[contentCard="true"] {{
                background-color: {theme["surface"]};
                border-radius: 12px;
                border: 1px solid {theme["border"]};
                padding: 24px;
            }}
        """)

        card_layout = QVBoxLayout(content_card)

        # Placeholder for book table/list
        placeholder_label = QLabel("Book catalog and management tools will be displayed here.\n\nUse the buttons below to manage books.")
        placeholder_label.setStyleSheet(f"""
            font-size: 16px;
            color: {theme["text_secondary"]};
            text-align: center;
        """)
        placeholder_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        card_layout.addWidget(placeholder_label)

        # Action buttons
        actions_layout = QHBoxLayout()
        actions_layout.setSpacing(12)

        add_btn = QPushButton("➕ Add Book")
        add_btn.clicked.connect(lambda: self._load_content("add_book"))
        add_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {theme["primary"]};
                color: white;
                border: none;
                border-radius: 8px;
                padding: 12px 24px;
                font-size: 14px;
                font-weight: 500;
            }}
            QPushButton:hover {{
                background-color: {theme["primary"]};
                opacity: 0.9;
            }}
        """)

        borrow_btn = QPushButton("📖 Borrow Book")
        borrow_btn.clicked.connect(lambda: self._load_content("borrow_book"))
        borrow_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {theme["surface"]};
                color: {theme["text"]};
                border: 1px solid {theme["border"]};
                border-radius: 8px;
                padding: 12px 24px;
                font-size: 14px;
                font-weight: 500;
            }}
            QPushButton:hover {{
                background-color: {theme["surface_hover"]};
            }}
        """)

        return_btn = QPushButton("↩️ Return Book")
        return_btn.clicked.connect(lambda: self._load_content("return_book"))
        return_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {theme["surface"]};
                color: {theme["text"]};
                border: 1px solid {theme["border"]};
                border-radius: 8px;
                padding: 12px 24px;
                font-size: 14px;
                font-weight: 500;
            }}
            QPushButton:hover {{
                background-color: {theme["surface_hover"]};
            }}
        """)

        distribution_btn = QPushButton("📦 Distribution")
        distribution_btn.clicked.connect(lambda: self._load_content("distribution"))
        distribution_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {theme["surface"]};
                color: {theme["text"]};
                border: 1px solid {theme["border"]};
                border-radius: 8px;
                padding: 12px 24px;
                font-size: 14px;
                font-weight: 500;
            }}
            QPushButton:hover {{
                background-color: {theme["surface_hover"]};
            }}
        """)

        import_export_btn = QPushButton("📤 Import/Export")
        import_export_btn.clicked.connect(lambda: self._load_content("book_import_export"))
        import_export_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {theme["surface"]};
                color: {theme["text"]};
                border: 1px solid {theme["border"]};
                border-radius: 8px;
                padding: 12px 24px;
                font-size: 14px;
                font-weight: 500;
            }}
            QPushButton:hover {{
                background-color: {theme["surface_hover"]};
            }}
        """)

        actions_layout.addWidget(add_btn)
        actions_layout.addWidget(borrow_btn)
        actions_layout.addWidget(return_btn)
        actions_layout.addWidget(distribution_btn)
        actions_layout.addWidget(import_export_btn)
        actions_layout.addStretch()

        card_layout.addLayout(actions_layout)

        layout.addWidget(content_card)
        layout.addStretch()

        return scroll_widget

    def _create_add_book_view(self) -> QWidget:
        """Create the add book content view."""
        theme_manager = self.get_theme_manager()
        theme = theme_manager._themes[self.get_theme()]

        scroll_widget = QWidget()
        layout = QVBoxLayout(scroll_widget)
        layout.setContentsMargins(32, 32, 32, 32)
        layout.setSpacing(20)

        # Header
        header = QLabel("➕ Add New Book")
        header.setStyleSheet(f"""
            font-size: 28px;
            font-weight: bold;
            color: {theme["text"]};
            margin-bottom: 16px;
        """)
        layout.addWidget(header)

        # Form placeholder
        content_card = QFrame()
        content_card.setProperty("contentCard", "true")
        content_card.setStyleSheet(f"""
            QFrame[contentCard="true"] {{
                background-color: {theme["surface"]};
                border-radius: 12px;
                border: 1px solid {theme["border"]};
                padding: 32px;
            }}
        """)

        card_layout = QVBoxLayout(content_card)

        form_placeholder = QLabel("Book registration form will be displayed here.\n\nFields: Title, Author, ISBN, Category, etc.")
        form_placeholder.setStyleSheet(f"""
            font-size: 16px;
            color: {theme["text_secondary"]};
            text-align: center;
        """)
        form_placeholder.setAlignment(Qt.AlignmentFlag.AlignCenter)
        card_layout.addWidget(form_placeholder)

        layout.addWidget(content_card)
        layout.addStretch()

        return scroll_widget

    def _create_distribution_view(self) -> QWidget:
        """Create the distribution content view."""
        theme_manager = self.get_theme_manager()
        theme = theme_manager._themes[self.get_theme()]

        scroll_widget = QWidget()
        layout = QVBoxLayout(scroll_widget)
        layout.setContentsMargins(32, 32, 32, 32)
        layout.setSpacing(20)

        # Header
        header = QLabel("📦 Book Distribution")
        header.setStyleSheet(f"""
            font-size: 28px;
            font-weight: bold;
            color: {theme["text"]};
            margin-bottom: 16px;
        """)
        layout.addWidget(header)

        # Content placeholder
        content_card = QFrame()
        content_card.setProperty("contentCard", "true")
        content_card.setStyleSheet(f"""
            QFrame[contentCard="true"] {{
                background-color: {theme["surface"]};
                border-radius: 12px;
                border: 1px solid {theme["border"]};
                padding: 32px;
            }}
        """)

        card_layout = QVBoxLayout(content_card)

        placeholder = QLabel("Book distribution interface will be displayed here.\n\nManage book distribution sessions and allocations.")
        placeholder.setStyleSheet(f"""
            font-size: 16px;
            color: {theme["text_secondary"]};
            text-align: center;
        """)
        placeholder.setAlignment(Qt.AlignmentFlag.AlignCenter)
        card_layout.addWidget(placeholder)

        layout.addWidget(content_card)
        layout.addStretch()

        return scroll_widget

    def _create_book_import_export_view(self) -> QWidget:
        """Create the book import/export content view."""
        theme_manager = self.get_theme_manager()
        theme = theme_manager._themes[self.get_theme()]

        scroll_widget = QWidget()
        layout = QVBoxLayout(scroll_widget)
        layout.setContentsMargins(32, 32, 32, 32)
        layout.setSpacing(20)

        # Header
        header = QLabel("📤 Book Import/Export")
        header.setStyleSheet(f"""
            font-size: 28px;
            font-weight: bold;
            color: {theme["text"]};
            margin-bottom: 16px;
        """)
        layout.addWidget(header)

        # Content placeholder
        content_card = QFrame()
        content_card.setProperty("contentCard", "true")
        content_card.setStyleSheet(f"""
            QFrame[contentCard="true"] {{
                background-color: {theme["surface"]};
                border-radius: 12px;
                border: 1px solid {theme["border"]};
                padding: 32px;
            }}
        """)

        card_layout = QVBoxLayout(content_card)

        placeholder = QLabel("Book import/export interface will be displayed here.\n\nImport books from files or export book data.")
        placeholder.setStyleSheet(f"""
            font-size: 16px;
            color: {theme["text_secondary"]};
            text-align: center;
        """)
        placeholder.setAlignment(Qt.AlignmentFlag.AlignCenter)
        card_layout.addWidget(placeholder)

        layout.addWidget(content_card)
        layout.addStretch()

        return scroll_widget

    def _create_borrow_book_view(self) -> QWidget:
        """Create the borrow book content view."""
        theme_manager = self.get_theme_manager()
        theme = theme_manager._themes[self.get_theme()]

        scroll_widget = QWidget()
        layout = QVBoxLayout(scroll_widget)
        layout.setContentsMargins(32, 32, 32, 32)
        layout.setSpacing(20)

        # Header
        header = QLabel("📖 Borrow Book")
        header.setStyleSheet(f"""
            font-size: 28px;
            font-weight: bold;
            color: {theme["text"]};
            margin-bottom: 16px;
        """)
        layout.addWidget(header)

        # Content placeholder
        content_card = QFrame()
        content_card.setProperty("contentCard", "true")
        content_card.setStyleSheet(f"""
            QFrame[contentCard="true"] {{
                background-color: {theme["surface"]};
                border-radius: 12px;
                border: 1px solid {theme["border"]};
                padding: 32px;
            }}
        """)

        card_layout = QVBoxLayout(content_card)

        placeholder = QLabel("Book borrowing interface will be displayed here.\n\nSelect a book and student to create a borrowing record.")
        placeholder.setStyleSheet(f"""
            font-size: 16px;
            color: {theme["text_secondary"]};
            text-align: center;
        """)
        placeholder.setAlignment(Qt.AlignmentFlag.AlignCenter)
        card_layout.addWidget(placeholder)

        layout.addWidget(content_card)
        layout.addStretch()

        return scroll_widget

    def _create_return_book_view(self) -> QWidget:
        """Create the return book content view."""
        theme_manager = self.get_theme_manager()
        theme = theme_manager._themes[self.get_theme()]

        scroll_widget = QWidget()
        layout = QVBoxLayout(scroll_widget)
        layout.setContentsMargins(32, 32, 32, 32)
        layout.setSpacing(20)

        # Header
        header = QLabel("↩️ Return Book")
        header.setStyleSheet(f"""
            font-size: 28px;
            font-weight: bold;
            color: {theme["text"]};
            margin-bottom: 16px;
        """)
        layout.addWidget(header)

        # Content placeholder
        content_card = QFrame()
        content_card.setProperty("contentCard", "true")
        content_card.setStyleSheet(f"""
            QFrame[contentCard="true"] {{
                background-color: {theme["surface"]};
                border-radius: 12px;
                border: 1px solid {theme["border"]};
                padding: 32px;
            }}
        """)

        card_layout = QVBoxLayout(content_card)

        placeholder = QLabel("Book return interface will be displayed here.\n\nSelect a borrowed book to mark it as returned.")
        placeholder.setStyleSheet(f"""
            font-size: 16px;
            color: {theme["text_secondary"]};
            text-align: center;
        """)
        placeholder.setAlignment(Qt.AlignmentFlag.AlignCenter)
        card_layout.addWidget(placeholder)

        layout.addWidget(content_card)
        layout.addStretch()

        return scroll_widget

    def _create_view_teachers_view(self) -> QWidget:
        """Create the view teachers content view."""
        theme_manager = self.get_theme_manager()
        theme = theme_manager._themes[self.get_theme()]

        scroll_widget = QWidget()
        layout = QVBoxLayout(scroll_widget)
        layout.setContentsMargins(32, 32, 32, 32)
        layout.setSpacing(20)

        # Header
        header = QLabel("👩‍🏫 Staff Management")
        header.setStyleSheet(f"""
            font-size: 28px;
            font-weight: bold;
            color: {theme["text"]};
            margin-bottom: 16px;
        """)
        layout.addWidget(header)

        # Content area for teacher list/table
        content_card = QFrame()
        content_card.setProperty("contentCard", "true")
        content_card.setStyleSheet(f"""
            QFrame[contentCard="true"] {{
                background-color: {theme["surface"]};
                border-radius: 12px;
                border: 1px solid {theme["border"]};
                padding: 24px;
            }}
        """)

        card_layout = QVBoxLayout(content_card)

        # Placeholder for teacher table/list
        placeholder_label = QLabel("Teacher list and management tools will be displayed here.\n\nUse the buttons below to manage staff.")
        placeholder_label.setStyleSheet(f"""
            font-size: 16px;
            color: {theme["text_secondary"]};
            text-align: center;
        """)
        placeholder_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        card_layout.addWidget(placeholder_label)

        # Action buttons
        actions_layout = QHBoxLayout()
        actions_layout.setSpacing(12)

        add_btn = QPushButton("➕ Add Teacher")
        add_btn.clicked.connect(lambda: self._load_content("add_teacher"))
        add_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {theme["primary"]};
                color: white;
                border: none;
                border-radius: 8px;
                padding: 12px 24px;
                font-size: 14px;
                font-weight: 500;
            }}
            QPushButton:hover {{
                background-color: {theme["primary"]};
                opacity: 0.9;
            }}
        """)

        edit_btn = QPushButton("✏️ Edit Teacher")
        edit_btn.clicked.connect(lambda: self._load_content("edit_teacher"))
        edit_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {theme["surface"]};
                color: {theme["text"]};
                border: 1px solid {theme["border"]};
                border-radius: 8px;
                padding: 12px 24px;
                font-size: 14px;
                font-weight: 500;
            }}
            QPushButton:hover {{
                background-color: {theme["surface_hover"]};
            }}
        """)

        actions_layout.addWidget(add_btn)
        actions_layout.addWidget(edit_btn)
        actions_layout.addStretch()

        card_layout.addLayout(actions_layout)

        layout.addWidget(content_card)
        layout.addStretch()

        return scroll_widget

    def _create_add_teacher_view(self) -> QWidget:
        """Create the add teacher content view."""
        try:
            window = AddTeacherWindow(self, self.username, self.role)
            window.show()
            return QWidget()
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to open add teacher window: {str(e)}")
            logger.error(f"Error opening add teacher window: {str(e)}")
            return self._create_default_view("add_teacher", theme, role_color)

    def _create_edit_teacher_view(self) -> QWidget:
        """Create the edit teacher content view."""
        try:
            # Open the view teachers window first to allow teacher selection
            view_window = ViewTeachersWindow(self, self.username, self.role)
            view_window.setWindowTitle("Select Teacher to Edit")
            view_window.show()

            # Note: The actual edit functionality is handled within ViewTeachersWindow
            # when the user clicks the Edit button on a selected teacher
            return QWidget()
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to open teacher selection window: {str(e)}")
            logger.error(f"Error opening teacher selection window: {str(e)}")
            return self._create_default_view("edit_teacher", self.get_theme_manager()._themes[self.get_theme()], self._get_role_color())

    def _create_teacher_import_export_view(self) -> QWidget:
        """Create the teacher import/export content view."""
        try:
            window = TeacherImportExportWindow(self, self.username, self.role)
            window.show()
            return QWidget()
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to open teacher import/export window: {str(e)}")
            logger.error(f"Error opening teacher import/export window: {str(e)}")
            return self._create_default_view("teacher_import_export", theme, role_color)

    def _create_manage_users_view(self) -> QWidget:
        """Create the manage users content view."""
        try:
            window = UserWindow(self, self.username, self.role)
            window.show()
            return QWidget()
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to open user management window: {str(e)}")
            logger.error(f"Error opening user management window: {str(e)}")
            return self._create_default_view("manage_users", theme, role_color)

    def _create_view_users_view(self) -> QWidget:
        """Create the view users content view."""
        try:
            window = ViewUsersWindow(self, self.username, self.role)
            window.show()
            return QWidget()
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to open view users window: {str(e)}")
            logger.error(f"Error opening view users window: {str(e)}")
            return self._create_default_view("view_users", theme, role_color)

    def _create_add_user_view(self) -> QWidget:
        """Create the add user content view."""
        try:
            window = AddUserWindow(self, self.username, self.role)
            window.show()
            return QWidget()
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to open add user window: {str(e)}")
            logger.error(f"Error opening add user window: {str(e)}")
            return self._create_default_view("add_user", theme, role_color)

    def _create_edit_user_view(self) -> QWidget:
        """Create the edit user content view."""
        try:
            window = EditUserWindow(self, self.username, self.role)
            window.show()
            return QWidget()
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to open edit user window: {str(e)}")
            logger.error(f"Error opening edit user window: {str(e)}")
            return self._create_default_view("edit_user", theme, role_color)

    def _create_delete_user_view(self) -> QWidget:
        """Create the delete user content view."""
        try:
            window = DeleteUserWindow(self, self.username, self.role)
            window.show()
            return QWidget()
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to open delete user window: {str(e)}")
            logger.error(f"Error opening delete user window: {str(e)}")
            return self._create_default_view("delete_user", theme, role_color)

    def _create_user_settings_view(self) -> QWidget:
        """Create the user settings content view."""
        try:
            window = UserSettingsWindow(self, self.username, self.role)
            window.show()
            return QWidget()
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to open user settings window: {str(e)}")
            logger.error(f"Error opening user settings window: {str(e)}")
            return self._create_default_view("user_settings", theme, role_color)

    def _create_short_form_mappings_view(self) -> QWidget:
        """Create the short form mappings content view."""
        try:
            window = ShortFormMappingsWindow(self, self.username, self.role)
            window.show()
            return QWidget()
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to open short form mappings window: {str(e)}")
            logger.error(f"Error opening short form mappings window: {str(e)}")
            return self._create_default_view("short_form_mappings", theme, role_color)

    def _create_user_sessions_view(self) -> QWidget:
        """Create the user sessions content view."""
        try:
            window = UserSessionsWindow(self, self.username, self.role)
            window.show()
            return QWidget()
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to open user sessions window: {str(e)}")
            logger.error(f"Error opening user sessions window: {str(e)}")
            return self._create_default_view("user_sessions", theme, role_color)

    def _create_user_activity_view(self) -> QWidget:
        """Create the user activity content view."""
        try:
            window = UserActivityWindow(self, self.username, self.role)
            window.show()
            return QWidget()
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to open user activity window: {str(e)}")
            logger.error(f"Error opening user activity window: {str(e)}")
            return self._create_default_view("user_activity", theme, role_color)

    def _create_settings_view(self) -> QWidget:
        """Create the settings content view."""
        theme_manager = self.get_theme_manager()
        theme = theme_manager._themes[self.get_theme()]

        scroll_widget = QWidget()
        layout = QVBoxLayout(scroll_widget)
        layout.setContentsMargins(32, 32, 32, 32)
        layout.setSpacing(20)

        # Header
        header = QLabel("⚙️ Settings")
        header.setStyleSheet(f"""
            font-size: 28px;
            font-weight: bold;
            color: {theme["text"]};
            margin-bottom: 16px;
        """)
        layout.addWidget(header)

        # Settings content
        content_card = QFrame()
        content_card.setProperty("contentCard", "true")
        content_card.setStyleSheet(f"""
            QFrame[contentCard="true"] {{
                background-color: {theme["surface"]};
                border-radius: 12px;
                border: 1px solid {theme["border"]};
                padding: 32px;
            }}
        """)

        card_layout = QVBoxLayout(content_card)

        settings_placeholder = QLabel("System settings and preferences will be displayed here.\n\nConfigure themes, notifications, and system options.")
        settings_placeholder.setStyleSheet(f"""
            font-size: 16px;
            color: {theme["text_secondary"]};
            text-align: center;
        """)
        settings_placeholder.setAlignment(Qt.AlignmentFlag.AlignCenter)
        card_layout.addWidget(settings_placeholder)

        layout.addWidget(content_card)
        layout.addStretch()

        return scroll_widget

    def _create_help_view(self) -> QWidget:
        """Create the help content view."""
        theme_manager = self.get_theme_manager()
        theme = theme_manager._themes[self.get_theme()]

        scroll_widget = QWidget()
        layout = QVBoxLayout(scroll_widget)
        layout.setContentsMargins(32, 32, 32, 32)
        layout.setSpacing(20)

        # Header
        header = QLabel("❓ Help & Support")
        header.setStyleSheet(f"""
            font-size: 28px;
            font-weight: bold;
            color: {theme["text"]};
            margin-bottom: 16px;
        """)
        layout.addWidget(header)

        # Help content
        content_card = QFrame()
        content_card.setProperty("contentCard", "true")
        content_card.setStyleSheet(f"""
            QFrame[contentCard="true"] {{
                background-color: {theme["surface"]};
                border-radius: 12px;
                border: 1px solid {theme["border"]};
                padding: 32px;
            }}
        """)

        card_layout = QVBoxLayout(content_card)

        help_content = QLabel("""
Help & Documentation

• Dashboard Navigation: Use the sidebar to navigate between different sections
• Quick Actions: Access common tasks from the dashboard
• Search: Use the search bar in the top bar to find students, books, or users
• Reports: Generate various reports from the Reports section
• Settings: Configure system preferences and user settings

For additional support, contact your system administrator.
        """)
        help_content.setStyleSheet(f"""
            font-size: 16px;
            color: {theme["text"]};
            line-height: 1.6;
        """)
        card_layout.addWidget(help_content)

        layout.addWidget(content_card)
        layout.addStretch()

        return scroll_widget

    def _create_default_view(self, content_id: str, theme: Dict[str, str], role_color: str) -> QWidget:
        """Create a default content view for unspecified content IDs."""
        scroll_widget = QWidget()
        layout = QVBoxLayout(scroll_widget)
        layout.setContentsMargins(32, 32, 32, 32)
        layout.setSpacing(20)
        
        # Header
        header = QLabel(f"📄 {content_id.replace('_', ' ').title()}")
        header.setStyleSheet(f"""
            font-size: 28px;
            font-weight: bold;
            color: {theme["text"]};
            margin-bottom: 16px;
        """)
        layout.addWidget(header)
        
        # Content placeholder
        content_card = QFrame()
        content_card.setProperty("contentCard", "true")
        content_card.setStyleSheet(f"""
            QFrame[contentCard="true"] {{
                background-color: {theme["surface"]};
                border-radius: 12px;
                border: 1px solid {theme["border"]};
                padding: 32px;
            }}
        """)
        
        card_layout = QVBoxLayout(content_card)
        
        placeholder_label = QLabel(f"This is the {content_id.replace('_', ' ')} view.\n\nFeature coming soon! 🚧")
        placeholder_label.setStyleSheet(f"""
            font-size: 18px;
            color: {theme["text_secondary"]};
            text-align: center;
        """)
        placeholder_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        card_layout.addWidget(placeholder_label)
        
        layout.addWidget(content_card)
        layout.addStretch()
        
        return scroll_widget

    def _create_book_reports_view(self) -> QWidget:
        """Create the book reports content view."""
        theme_manager = self.get_theme_manager()
        theme = theme_manager._themes[self.get_theme()]
        
        scroll_widget = QWidget()
        layout = QVBoxLayout(scroll_widget)
        layout.setContentsMargins(32, 32, 32, 32)
        layout.setSpacing(20)
        
        # Header
        header = QLabel("📊 Book Reports")
        header.setStyleSheet(f"""
            font-size: 28px;
            font-weight: bold;
            color: {theme["text"]};
            margin-bottom: 16px;
        """)
        layout.addWidget(header)
        
        # Content placeholder
        content_card = QFrame()
        content_card.setProperty("contentCard", "true")
        content_card.setStyleSheet(f"""
            QFrame[contentCard="true"] {{
                background-color: {theme["surface"]};
                border-radius: 12px;
                border: 1px solid {theme["border"]};
                padding: 32px;
            }}
        """)
        
        card_layout = QVBoxLayout(content_card)
        
        placeholder_label = QLabel("Book reports interface will be displayed here.\n\nGenerate and view various book-related reports.")
        placeholder_label.setStyleSheet(f"""
            font-size: 16px;
            color: {theme["text_secondary"]};
            text-align: center;
        """)
        placeholder_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        card_layout.addWidget(placeholder_label)
        
        # Action buttons
        actions_layout = QHBoxLayout()
        actions_layout.setSpacing(12)
        
        generate_btn = QPushButton("📊 Generate Report")
        generate_btn.clicked.connect(self._show_book_reports)
        generate_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {theme["primary"]};
                color: white;
                border: none;
                border-radius: 8px;
                padding: 12px 24px;
                font-size: 14px;
                font-weight: 500;
            }}
            QPushButton:hover {{
                background-color: {theme["primary"]};
                opacity: 0.9;
            }}
        """)
        
        actions_layout.addWidget(generate_btn)
        actions_layout.addStretch()
        
        card_layout.addLayout(actions_layout)
        
        layout.addWidget(content_card)
        layout.addStretch()
        
        return scroll_widget

    def _create_student_reports_view(self) -> QWidget:
        """Create the student reports content view."""
        theme_manager = self.get_theme_manager()
        theme = theme_manager._themes[self.get_theme()]
        
        scroll_widget = QWidget()
        layout = QVBoxLayout(scroll_widget)
        layout.setContentsMargins(32, 32, 32, 32)
        layout.setSpacing(20)
        
        # Header
        header = QLabel("📊 Student Reports")
        header.setStyleSheet(f"""
            font-size: 28px;
            font-weight: bold;
            color: {theme["text"]};
            margin-bottom: 16px;
        """)
        layout.addWidget(header)
        
        # Content placeholder
        content_card = QFrame()
        content_card.setProperty("contentCard", "true")
        content_card.setStyleSheet(f"""
            QFrame[contentCard="true"] {{
                background-color: {theme["surface"]};
                border-radius: 12px;
                border: 1px solid {theme["border"]};
                padding: 32px;
            }}
        """)
        
        card_layout = QVBoxLayout(content_card)
        
        placeholder_label = QLabel("Student reports interface will be displayed here.\n\nGenerate and view various student-related reports.")
        placeholder_label.setStyleSheet(f"""
            font-size: 16px;
            color: {theme["text_secondary"]};
            text-align: center;
        """)
        placeholder_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        card_layout.addWidget(placeholder_label)
        
        # Action buttons
        actions_layout = QHBoxLayout()
        actions_layout.setSpacing(12)
        
        generate_btn = QPushButton("📊 Generate Report")
        generate_btn.clicked.connect(self._show_student_reports)
        generate_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {theme["primary"]};
                color: white;
                border: none;
                border-radius: 8px;
                padding: 12px 24px;
                font-size: 14px;
                font-weight: 500;
            }}
            QPushButton:hover {{
                background-color: {theme["primary"]};
                opacity: 0.9;
            }}
        """)
        
        actions_layout.addWidget(generate_btn)
        actions_layout.addStretch()
        
        card_layout.addLayout(actions_layout)
        
        layout.addWidget(content_card)
        layout.addStretch()
        
        return scroll_widget

    def _create_custom_reports_view(self) -> QWidget:
        """Create the custom reports content view."""
        theme_manager = self.get_theme_manager()
        theme = theme_manager._themes[self.get_theme()]
        
        scroll_widget = QWidget()
        layout = QVBoxLayout(scroll_widget)
        layout.setContentsMargins(32, 32, 32, 32)
        layout.setSpacing(20)
        
        # Header
        header = QLabel("📊 Custom Reports")
        header.setStyleSheet(f"""
            font-size: 28px;
            font-weight: bold;
            color: {theme["text"]};
            margin-bottom: 16px;
        """)
        layout.addWidget(header)
        
        # Content placeholder
        content_card = QFrame()
        content_card.setProperty("contentCard", "true")
        content_card.setStyleSheet(f"""
            QFrame[contentCard="true"] {{
                background-color: {theme["surface"]};
                border-radius: 12px;
                border: 1px solid {theme["border"]};
                padding: 32px;
            }}
        """)
        
        card_layout = QVBoxLayout(content_card)
        
        placeholder_label = QLabel("Custom reports interface will be displayed here.\n\nCreate and generate custom reports across all data.")
        placeholder_label.setStyleSheet(f"""
            font-size: 16px;
            color: {theme["text_secondary"]};
            text-align: center;
        """)
        placeholder_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        card_layout.addWidget(placeholder_label)
        
        # Action buttons
        actions_layout = QHBoxLayout()
        actions_layout.setSpacing(12)
        
        generate_btn = QPushButton("📊 Generate Report")
        generate_btn.clicked.connect(self._show_custom_reports)
        generate_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {theme["primary"]};
                color: white;
                border: none;
                border-radius: 8px;
                padding: 12px 24px;
                font-size: 14px;
                font-weight: 500;
            }}
            QPushButton:hover {{
                background-color: {theme["primary"]};
                opacity: 0.9;
            }}
        """)
        
        actions_layout.addWidget(generate_btn)
        actions_layout.addStretch()
        
        card_layout.addLayout(actions_layout)
        
        layout.addWidget(content_card)
        layout.addStretch()
        
        return scroll_widget

    def _create_manage_furniture_view(self) -> QWidget:
        """Create the manage furniture content view."""
        try:
            from school_system.gui.windows.furniture_window.manage_furniture_window import ManageFurnitureWindow
            window = ManageFurnitureWindow(self, self.username, self.role)
            window.show()
            return QWidget()
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to open furniture management: {str(e)}")
            logger.error(f"Error opening furniture management window: {str(e)}")
            return self._create_default_view("manage_furniture", self.get_theme_manager()._themes[self.get_theme()], self._get_role_color())

    def _create_furniture_assignments_view(self) -> QWidget:
        """Create the furniture assignments content view."""
        try:
            from school_system.gui.windows.furniture_window.furniture_assignments_window import FurnitureAssignmentsWindow
            window = FurnitureAssignmentsWindow(self, self.username, self.role)
            window.show()
            return QWidget()
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to open furniture assignments: {str(e)}")
            logger.error(f"Error opening furniture assignments window: {str(e)}")
            return self._create_default_view("furniture_assignments", self.get_theme_manager()._themes[self.get_theme()], self._get_role_color())

    def _create_furniture_maintenance_view(self) -> QWidget:
        """Create the furniture maintenance content view."""
        try:
            from school_system.gui.windows.furniture_window.furniture_maintenance_window import FurnitureMaintenanceWindow
            window = FurnitureMaintenanceWindow(self, self.username, self.role)
            window.show()
            return QWidget()
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to open furniture maintenance: {str(e)}")
            logger.error(f"Error opening furniture maintenance window: {str(e)}")
            return self._create_default_view("furniture_maintenance", self.get_theme_manager()._themes[self.get_theme()], self._get_role_color())

    def _on_content_changed(self, content_id: str):
        """Handle content view changes."""
        self.update_status(f"Viewing: {content_id.replace('_', ' ').title()}")


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
        """Apply outstanding professional styling to the main window."""
        theme_manager = self.get_theme_manager()
        theme = theme_manager._themes[self.get_theme()]
        role_color = self._get_role_color()

        # Apply comprehensive modern professional theme
        self.setStyleSheet(f"""
            MainWindow {{
                background-color: {theme["background"]};
                font-family: 'Segoe UI', -apple-system, BlinkMacSystemFont, 'Roboto', sans-serif;
                color: {theme["text"]};
            }}

            /* Dashboard Panels */
            QFrame[dashboardPanel="true"] {{
                background-color: {theme["surface"]};
                border-radius: 16px;
                border: 1px solid {theme["border"]};
            }}
            QFrame[dashboardPanel="true"]:hover {{
                background-color: {theme["surface_hover"]};
            }}

            /* Statistics Cards */
            QFrame[statCard="true"] {{
                background-color: {theme["surface"]};
                border-radius: 12px;
                border-left: 4px solid {role_color};
                border: 1px solid {theme["border"]};
                padding: 20px;
                transition: all 0.3s ease;
            }}
            QFrame[statCard="true"]:hover {{
                border-color: {role_color};
                background-color: {theme["surface_hover"]};
            }}

            /* Enhanced Statistics Cards */
            QFrame[enhancedStatCard="true"] {{
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 {theme["surface"]}, stop:1 rgba(255, 255, 255, 0.8));
                border-radius: 14px;
                border: 1px solid {theme["border"]};
            }}
            QFrame[enhancedStatCard="true"]:hover {{
                border-color: {role_color};
            }}

            /* Welcome Header */
            QFrame#welcomeHeader {{
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 {role_color}, stop:1 {theme["primary"]});
                border-radius: 16px;
                padding: 24px;
                color: white;
            }}

            /* Buttons */
            QPushButton {{
                background-color: {theme["surface"]};
                border: 1px solid {theme["border"]};
                border-radius: 8px;
                padding: 10px 16px;
                font-size: 14px;
                font-weight: 500;
            }}
            QPushButton:hover {{
                background-color: {role_color};
                color: white;
                border-color: {role_color};
            }}

            /* Tool Buttons */
            QToolButton {{
                border-radius: 8px;
                padding: 8px 12px;
            }}
            QToolButton:hover {{
            }}

            /* Labels */
            QLabel {{
                color: {theme["text"]};
            }}
            QLabel[title="true"] {{
                font-size: 18px;
                font-weight: 600;
                color: {theme["text"]};
                padding: 16px;
                border-bottom: 1px solid {theme["border"]};
            }}
            QLabel[content="true"] {{
                font-size: 14px;
                color: {theme["text_secondary"]};
                padding: 16px;
                line-height: 1.5;
            }}

            /* Cards */
            QFrame[card="true"] {{
                background-color: {theme["surface"]};
                border-radius: 12px;
                border: 1px solid {theme["border"]};
            }}
            QFrame[card="true"]:hover {{
            }}

            /* Scroll Areas */
            QScrollArea {{
                border: none;
                background-color: transparent;
            }}
            QScrollArea QWidget {{
                background-color: transparent;
            }}

            /* Focus States */
            *:focus {{
                outline: 2px solid {role_color};
                outline-offset: 2px;
            }}

            /* Animations */
            * {{
                transition: all 0.2s ease;
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
        """Deprecated: Content is now handled by the dynamic content area system."""
        pass

    def _setup_old_content(self):
        """Setup the main content area with a professional dashboard layout."""
        # Clear existing content to avoid duplication
        self.clear_content()

        # Create main vertical layout with modern spacing
        main_layout = self.create_layout("vbox")
        main_layout.set_spacing(32)
        main_layout.set_margins(32, 32, 32, 32)

        # Add the main layout to content area
        self.add_layout_to_content(main_layout)

        # Enhanced welcome header
        self._setup_welcome_header(main_layout)

        # Top dashboard row - Quick Actions and Key Metrics
        self._setup_top_dashboard_row(main_layout)

        # Middle dashboard row - Statistics and Activity
        self._setup_middle_dashboard_row(main_layout)

        # Bottom dashboard row - Additional widgets and notifications
        self._setup_bottom_dashboard_row(main_layout)

    def _setup_top_dashboard_row(self, main_layout):
        """Setup the top row with quick actions and key performance indicators."""
        theme_manager = self.get_theme_manager()
        theme = theme_manager._themes[self.get_theme()]
        role_color = self._get_role_color()

        # Create horizontal layout for top row
        top_row_layout = QHBoxLayout()
        top_row_layout.setSpacing(24)

        # Quick Actions Panel (Left side)
        quick_actions_panel = self._create_quick_actions_panel()
        top_row_layout.addWidget(quick_actions_panel, 2)  # 2/3 width

        # Key Metrics Panel (Right side)
        key_metrics_panel = self._create_key_metrics_panel()
        top_row_layout.addWidget(key_metrics_panel, 1)  # 1/3 width

        main_layout.addLayout(top_row_layout)

    def _setup_middle_dashboard_row(self, main_layout):
        """Setup the middle row with detailed statistics and recent activity."""
        # Create horizontal layout for middle row
        middle_row_layout = QHBoxLayout()
        middle_row_layout.setSpacing(24)

        # Statistics Grid (Left side)
        stats_panel = self._create_statistics_grid()
        middle_row_layout.addWidget(stats_panel, 2)  # 2/3 width

        # Activity Panel (Right side)
        activity_panel = self._create_activity_panel()
        middle_row_layout.addWidget(activity_panel, 1)  # 1/3 width

        main_layout.addLayout(middle_row_layout)

    def _setup_bottom_dashboard_row(self, main_layout):
        """Setup the bottom row with notifications and system alerts."""
        # Create horizontal layout for bottom row
        bottom_row_layout = QHBoxLayout()
        bottom_row_layout.setSpacing(24)

        # Notifications Panel
        notifications_panel = self._create_notifications_panel()
        bottom_row_layout.addWidget(notifications_panel, 1)

        # System Alerts Panel
        alerts_panel = self._create_system_alerts_panel()
        bottom_row_layout.addWidget(alerts_panel, 1)

        # Calendar/Events Panel
        calendar_panel = self._create_calendar_panel()
        bottom_row_layout.addWidget(calendar_panel, 1)

        main_layout.addLayout(bottom_row_layout)

    def _create_quick_actions_panel(self):
        """Create a comprehensive quick actions panel."""
        theme_manager = self.get_theme_manager()
        theme = theme_manager._themes[self.get_theme()]
        role_color = self._get_role_color()

        panel = QFrame()
        panel.setProperty("dashboardPanel", "true")
        panel.setStyleSheet(f"""
            QFrame[dashboardPanel="true"] {{
                background-color: {theme["surface"]};
                border-radius: 16px;
                border: 1px solid {theme["border"]};
                padding: 24px;
            }}
        """)

        layout = QVBoxLayout(panel)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(20)

        # Panel Title
        title = QLabel("⚡ Quick Actions")
        title.setStyleSheet(f"""
            font-size: 18px;
            font-weight: bold;
            color: {theme["text"]};
            margin-bottom: 8px;
        """)
        layout.addWidget(title)

        # Action Categories
        categories = [
            {
                "title": "Student Management",
                "actions": [
                    ("➕ Add Student", self._add_student),
                    ("👁️ View Students", self._show_students),
                    ("✏️ Edit Student", self._show_edit_student),
                    ("📤 Import Students", self._show_student_import_export),
                ]
            },
            {
                "title": "Book Management",
                "actions": [
                    ("➕ Add Book", self._show_add_book_window),
                    ("👁️ View Books", self._show_view_books_window),
                    ("📖 Borrow Book", self._show_borrow_book_window),
                    ("↩️ Return Book", self._show_return_book_window),
                ]
            },
            {
                "title": "Reports & Analytics",
                "actions": [
                    ("📊 Book Reports", self._show_book_reports),
                    ("📊 Student Reports", self._show_student_reports),
                    ("📊 Custom Reports", self._show_custom_reports),
                ]
            }
        ]

        for category in categories:
            # Category title
            cat_title = QLabel(category["title"])
            cat_title.setStyleSheet(f"""
                font-size: 14px;
                font-weight: 600;
                color: {theme["text_secondary"]};
                text-transform: uppercase;
                letter-spacing: 0.5px;
                margin-top: 12px;
                margin-bottom: 8px;
            """)
            layout.addWidget(cat_title)

            # Action buttons grid
            actions_layout = QHBoxLayout()
            actions_layout.setSpacing(8)

            for action_text, action_callback in category["actions"]:
                btn = QPushButton(action_text)
                btn.setStyleSheet(f"""
                    QPushButton {{
                        background-color: transparent;
                        border: 1px solid {role_color};
                        color: {role_color};
                        padding: 8px 12px;
                        border-radius: 8px;
                        font-size: 12px;
                        font-weight: 500;
                        min-width: 80px;
                    }}
                    QPushButton:hover {{
                        background-color: {role_color};
                        color: white;
                    }}
                """)
                btn.clicked.connect(action_callback)
                actions_layout.addWidget(btn)

            layout.addLayout(actions_layout)

        layout.addStretch()
        return panel

    def _create_key_metrics_panel(self):
        """Create a key metrics panel with important KPIs."""
        theme_manager = self.get_theme_manager()
        theme = theme_manager._themes[self.get_theme()]
        role_color = self._get_role_color()

        panel = QFrame()
        panel.setProperty("dashboardPanel", "true")
        panel.setStyleSheet(f"""
            QFrame[dashboardPanel="true"] {{
                background-color: {theme["surface"]};
                border-radius: 16px;
                border: 1px solid {theme["border"]};
                padding: 24px;
            }}
        """)

        layout = QVBoxLayout(panel)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(16)

        # Panel Title
        title = QLabel("🎯 Key Metrics")
        title.setStyleSheet(f"""
            font-size: 18px;
            font-weight: bold;
            color: {theme["text"]};
            margin-bottom: 8px;
        """)
        layout.addWidget(title)

        # Key metrics based on role
        if self.role in ['admin', 'librarian']:
            metrics = [
                ("System Health", "98%", "#27ae60", "🟢"),
                ("Active Users", "247", role_color, "👥"),
                ("Books Borrowed Today", "23", "#f39c12", "📚"),
                ("Pending Approvals", "5", "#e74c3c", "⚠️"),
            ]
        else:
            metrics = [
                ("Books Available", "1,245", "#27ae60", "📚"),
                ("Your Borrowed Books", "3", role_color, "📖"),
                ("Due Soon", "2", "#f39c12", "⏰"),
            ]

        for metric_name, value, color, icon in metrics:
            metric_card = QFrame()
            metric_card.setStyleSheet(f"""
                QFrame {{
                    background-color: {theme["surface_hover"]};
                    border-radius: 8px;
                    border-left: 3px solid {color};
                    padding: 12px;
                }}
            """)

            metric_layout = QHBoxLayout(metric_card)
            metric_layout.setContentsMargins(12, 12, 12, 12)

            # Icon and name
            icon_label = QLabel(f"{icon} {metric_name}")
            icon_label.setStyleSheet(f"color: {theme['text']}; font-size: 14px; font-weight: 500;")

            # Value
            value_label = QLabel(value)
            value_label.setStyleSheet(f"color: {color}; font-size: 16px; font-weight: bold;")

            metric_layout.addWidget(icon_label)
            metric_layout.addStretch()
            metric_layout.addWidget(value_label)

            layout.addWidget(metric_card)

        layout.addStretch()
        return panel

    def _create_statistics_grid(self):
        """Create a comprehensive statistics grid."""
        theme_manager = self.get_theme_manager()
        theme = theme_manager._themes[self.get_theme()]
        role_color = self._get_role_color()

        panel = QFrame()
        panel.setProperty("dashboardPanel", "true")
        panel.setStyleSheet(f"""
            QFrame[dashboardPanel="true"] {{
                background-color: {theme["surface"]};
                border-radius: 16px;
                border: 1px solid {theme["border"]};
                padding: 24px;
            }}
        """)

        layout = QVBoxLayout(panel)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(20)

        # Panel Title
        title = QLabel("📊 System Statistics")
        title.setStyleSheet(f"""
            font-size: 18px;
            font-weight: bold;
            color: {theme["text"]};
            margin-bottom: 8px;
        """)
        layout.addWidget(title)

        # Statistics grid
        if self.role in ['admin', 'librarian']:
            stats_data = [
                ("Total Students", "1,247", "👨‍🎓", "#3498db", "+12%"),
                ("Total Teachers", "89", "👩‍🏫", "#2ecc71", "+3%"),
                ("Total Books", "3,456", "📚", "#9b59b6", "+8%"),
                ("Available Chairs", "245", "🪑", "#f39c12", "-2%"),
                ("Available Lockers", "67", "🔐", "#e74c3c", "+5%"),
                ("Books Borrowed", "892", "📖", "#1abc9c", "+15%"),
            ]
        else:
            stats_data = [
                ("Total Books", "3,456", "📚", "#9b59b6", "+8%"),
                ("Available Books", "2,564", "📖", "#27ae60", "+12%"),
                ("Your Borrowed", "3", "📚", "#3498db", "0%"),
                ("Due Soon", "2", "⏰", "#f39c12", "0%"),
            ]

        # Create grid layout for stats
        grid_layout = QGridLayout()
        grid_layout.setSpacing(16)

        row, col = 0, 0
        max_cols = 2

        for title, count, icon, color, change in stats_data:
            stat_card = self._create_enhanced_stat_card(title, count, icon, color, change)
            grid_layout.addWidget(stat_card, row, col)

            col += 1
            if col >= max_cols:
                col = 0
                row += 1

        layout.addLayout(grid_layout)
        layout.addStretch()
        return panel

    def _create_enhanced_stat_card(self, title, count, icon, color, change):
        """Create an enhanced statistics card with trend indicator."""
        theme_manager = self.get_theme_manager()
        theme = theme_manager._themes[self.get_theme()]

        card = QFrame()
        card.setProperty("enhancedStatCard", "true")
        card.setStyleSheet(f"""
            QFrame[enhancedStatCard="true"] {{
                background-color: {theme["surface"]};
                border-radius: 12px;
                border: 1px solid {theme["border"]};
                padding: 20px;
                min-height: 120px;
            }}
            QFrame[enhancedStatCard="true"]:hover {{
                border-color: {color};
                background-color: {theme["surface_hover"]};
            }}
        """)

        layout = QVBoxLayout(card)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(8)

        # Icon and title
        header_layout = QHBoxLayout()
        icon_label = QLabel(icon)
        icon_label.setStyleSheet(f"font-size: 24px;")
        title_label = QLabel(title)
        title_label.setStyleSheet(f"""
            font-size: 14px;
            color: {theme["text_secondary"]};
            font-weight: 500;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        """)

        header_layout.addWidget(icon_label)
        header_layout.addWidget(title_label)
        header_layout.addStretch()
        layout.addLayout(header_layout)

        # Count
        count_label = QLabel(count)
        count_font = QFont("Segoe UI", 28, QFont.Weight.Bold)
        count_label.setFont(count_font)
        count_label.setStyleSheet(f"color: {theme['text']};")
        layout.addWidget(count_label)

        # Change indicator
        change_label = QLabel(f"{change} from last month")
        change_label.setStyleSheet(f"""
            font-size: 12px;
            color: {color};
            font-weight: 500;
        """)
        layout.addWidget(change_label)

        return card

    def _create_activity_panel(self):
        """Create a recent activity panel."""
        theme_manager = self.get_theme_manager()
        theme = theme_manager._themes[self.get_theme()]
        role_color = self._get_role_color()

        panel = QFrame()
        panel.setProperty("dashboardPanel", "true")
        panel.setStyleSheet(f"""
            QFrame[dashboardPanel="true"] {{
                background-color: {theme["surface"]};
                border-radius: 16px;
                border: 1px solid {theme["border"]};
                padding: 24px;
            }}
        """)

        layout = QVBoxLayout(panel)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(16)

        # Panel Title
        title = QLabel("📋 Recent Activity")
        title.setStyleSheet(f"""
            font-size: 18px;
            font-weight: bold;
            color: {theme["text"]};
            margin-bottom: 8px;
        """)
        layout.addWidget(title)

        # Recent activities
        activities = [
            ("Book borrowed: 'Python Programming' by John Doe", "2 min ago", "📖"),
            ("New student registered: Jane Smith", "15 min ago", "👨‍🎓"),
            ("Book returned: 'Data Science 101'", "1 hour ago", "↩️"),
            ("Teacher added: Prof. Michael Johnson", "2 hours ago", "👩‍🏫"),
            ("System backup completed", "3 hours ago", "💾"),
        ]

        for activity, time, icon in activities:
            activity_item = QFrame()
            activity_item.setStyleSheet(f"""
                QFrame {{
                    background-color: {theme["surface_hover"]};
                    border-radius: 8px;
                    padding: 12px;
                }}
            """)

            item_layout = QHBoxLayout(activity_item)
            item_layout.setContentsMargins(12, 12, 12, 12)

            # Icon
            icon_label = QLabel(icon)
            icon_label.setStyleSheet("font-size: 16px;")

            # Activity text
            text_label = QLabel(activity)
            text_label.setStyleSheet(f"""
                color: {theme['text']};
                font-size: 13px;
                font-weight: 500;
            """)
            text_label.setWordWrap(True)

            # Time
            time_label = QLabel(time)
            time_label.setStyleSheet(f"""
                color: {theme['text_secondary']};
                font-size: 11px;
            """)

            item_layout.addWidget(icon_label)
            item_layout.addWidget(text_label, 1)
            item_layout.addWidget(time_label)

            layout.addWidget(activity_item)

        # View all activities button
        view_all_btn = QPushButton("View All Activities")
        view_all_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: transparent;
                border: 1px solid {role_color};
                color: {role_color};
                padding: 8px 16px;
                border-radius: 6px;
                font-size: 12px;
                font-weight: 500;
            }}
            QPushButton:hover {{
                background-color: {role_color};
                color: white;
            }}
        """)
        layout.addWidget(view_all_btn)

        return panel

    def _create_notifications_panel(self):
        """Create a notifications panel."""
        theme_manager = self.get_theme_manager()
        theme = theme_manager._themes[self.get_theme()]
        role_color = self._get_role_color()

        panel = QFrame()
        panel.setProperty("dashboardPanel", "true")
        panel.setStyleSheet(f"""
            QFrame[dashboardPanel="true"] {{
                background-color: {theme["surface"]};
                border-radius: 16px;
                border: 1px solid {theme["border"]};
                padding: 24px;
            }}
        """)

        layout = QVBoxLayout(panel)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(16)

        # Panel Title
        title = QLabel("🔔 Notifications")
        title.setStyleSheet(f"""
            font-size: 18px;
            font-weight: bold;
            color: {theme["text"]};
            margin-bottom: 8px;
        """)
        layout.addWidget(title)

        # Notifications
        notifications = [
            ("Book due soon: 'Advanced Mathematics'", "warning", "2 days left"),
            ("New system update available", "info", "Version 1.2.0"),
            ("Student attendance report ready", "success", "Generated"),
            ("Maintenance scheduled", "warning", "Tomorrow 2:00 PM"),
        ]

        for notification, type_, detail in notifications:
            notif_item = QFrame()
            color_map = {
                "warning": "#f39c12",
                "info": role_color,
                "success": "#27ae60"
            }
            notif_color = color_map.get(type_, role_color)

            notif_item.setStyleSheet(f"""
                QFrame {{
                    background-color: {theme["surface_hover"]};
                    border-radius: 8px;
                    border-left: 3px solid {notif_color};
                    padding: 12px;
                }}
            """)

            item_layout = QVBoxLayout(notif_item)
            item_layout.setContentsMargins(12, 12, 12, 12)

            # Notification text
            text_label = QLabel(notification)
            text_label.setStyleSheet(f"""
                color: {theme['text']};
                font-size: 13px;
                font-weight: 500;
            """)
            text_label.setWordWrap(True)

            # Detail
            detail_label = QLabel(detail)
            detail_label.setStyleSheet(f"""
                color: {notif_color};
                font-size: 11px;
                font-weight: 500;
            """)

            item_layout.addWidget(text_label)
            item_layout.addWidget(detail_label)

            layout.addWidget(notif_item)

        layout.addStretch()
        return panel

    def _create_system_alerts_panel(self):
        """Create a system alerts panel."""
        theme_manager = self.get_theme_manager()
        theme = theme_manager._themes[self.get_theme()]
        role_color = self._get_role_color()

        panel = QFrame()
        panel.setProperty("dashboardPanel", "true")
        panel.setStyleSheet(f"""
            QFrame[dashboardPanel="true"] {{
                background-color: {theme["surface"]};
                border-radius: 16px;
                border: 1px solid {theme["border"]};
                padding: 24px;
            }}
        """)

        layout = QVBoxLayout(panel)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(16)

        # Panel Title
        title = QLabel("⚠️ System Alerts")
        title.setStyleSheet(f"""
            font-size: 18px;
            font-weight: bold;
            color: {theme["text"]};
            margin-bottom: 8px;
        """)
        layout.addWidget(title)

        # System alerts
        alerts = [
            ("Low inventory: Mathematics textbooks", "critical", "Only 5 left"),
            ("Server maintenance tonight", "warning", "11:00 PM - 1:00 AM"),
            ("Database backup successful", "success", "Completed 2 hours ago"),
            ("New user registrations pending", "info", "3 approvals needed"),
        ]

        for alert, type_, detail in alerts:
            alert_item = QFrame()
            color_map = {
                "critical": "#e74c3c",
                "warning": "#f39c12",
                "success": "#27ae60",
                "info": role_color
            }
            alert_color = color_map.get(type_, role_color)

            alert_item.setStyleSheet(f"""
                QFrame {{
                    background-color: {theme["surface_hover"]};
                    border-radius: 8px;
                    border-left: 3px solid {alert_color};
                    padding: 12px;
                }}
            """)

            item_layout = QVBoxLayout(alert_item)
            item_layout.setContentsMargins(12, 12, 12, 12)

            # Alert text
            text_label = QLabel(alert)
            text_label.setStyleSheet(f"""
                color: {theme['text']};
                font-size: 13px;
                font-weight: 500;
            """)
            text_label.setWordWrap(True)

            # Detail
            detail_label = QLabel(detail)
            detail_label.setStyleSheet(f"""
                color: {alert_color};
                font-size: 11px;
                font-weight: 500;
            """)

            item_layout.addWidget(text_label)
            item_layout.addWidget(detail_label)

            layout.addWidget(alert_item)

        layout.addStretch()
        return panel

    def _create_calendar_panel(self):
        """Create a calendar/events panel."""
        theme_manager = self.get_theme_manager()
        theme = theme_manager._themes[self.get_theme()]
        role_color = self._get_role_color()

        panel = QFrame()
        panel.setProperty("dashboardPanel", "true")
        panel.setStyleSheet(f"""
            QFrame[dashboardPanel="true"] {{
                background-color: {theme["surface"]};
                border-radius: 16px;
                border: 1px solid {theme["border"]};
                padding: 24px;
            }}
        """)

        layout = QVBoxLayout(panel)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(16)

        # Panel Title
        title = QLabel("📅 Upcoming Events")
        title.setStyleSheet(f"""
            font-size: 18px;
            font-weight: bold;
            color: {theme["text"]};
            margin-bottom: 8px;
        """)
        layout.addWidget(title)

        # Current date
        current_date = QLabel("Today - January 14, 2026")
        current_date.setStyleSheet(f"""
            color: {theme["text_secondary"]};
            font-size: 12px;
            font-weight: 500;
            margin-bottom: 8px;
        """)
        layout.addWidget(current_date)

        # Upcoming events
        events = [
            ("Parent-Teacher Meeting", "Today, 2:00 PM", "#3498db"),
            ("Book Return Deadline", "Tomorrow", "#e74c3c"),
            ("Staff Training Session", "Jan 16, 10:00 AM", "#27ae60"),
            ("Library Maintenance", "Jan 18, All Day", "#f39c12"),
        ]

        for event, time, color in events:
            event_item = QFrame()
            event_item.setStyleSheet(f"""
                QFrame {{
                    background-color: {theme["surface_hover"]};
                    border-radius: 8px;
                    border-left: 3px solid {color};
                    padding: 12px;
                }}
            """)

            item_layout = QVBoxLayout(event_item)
            item_layout.setContentsMargins(12, 12, 12, 12)

            # Event title
            title_label = QLabel(event)
            title_label.setStyleSheet(f"""
                color: {theme['text']};
                font-size: 13px;
                font-weight: 600;
            """)

            # Time
            time_label = QLabel(time)
            time_label.setStyleSheet(f"""
                color: {color};
                font-size: 11px;
                font-weight: 500;
            """)

            item_layout.addWidget(title_label)
            item_layout.addWidget(time_label)

            layout.addWidget(event_item)

        # Add event button
        add_event_btn = QPushButton("📅 Add Event")
        add_event_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: transparent;
                border: 1px solid {role_color};
                color: {role_color};
                padding: 8px 16px;
                border-radius: 6px;
                font-size: 12px;
                font-weight: 500;
            }}
            QPushButton:hover {{
                background-color: {role_color};
                color: white;
            }}
        """)
        layout.addWidget(add_event_btn)

        return panel

    def _on_search_text_changed(self, text):
        """Handle search input changes."""
        if len(text.strip()) >= 3:
            # Perform search across different entities
            self._perform_global_search(text.strip())
        elif len(text.strip()) == 0:
            # Clear search results
            self._clear_search_results()

    def _perform_global_search(self, query):
        """Perform global search across students, books, and users."""
        # This would integrate with your data models
        # For now, show a placeholder message
        self.update_status(f"Searching for: {query}")
        logger.info(f"Global search initiated for: {query}")

    def _clear_search_results(self):
        """Clear search results and return to normal view."""
        self.update_status("Search cleared")
        logger.info("Search results cleared")

    def _toggle_theme(self):
        """Toggle between light and dark themes."""
        theme_manager = self.get_theme_manager()
        current_theme = self.get_theme()
        new_theme = "dark" if current_theme == "light" else "light"
        theme_manager.set_theme(new_theme)
        logger.info(f"Theme toggled to: {new_theme}")

    def _show_notifications(self):
        """Show notifications panel."""
        # Create a notification popup or dialog
        QMessageBox.information(self, "Notifications",
                               "🔔 You have 3 unread notifications:\n\n"
                               "• Book return reminder\n"
                               "• New student registration\n"
                               "• System maintenance scheduled")
        logger.info("Notifications panel opened")

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
        title_font = QFont("Segoe UI", 16, QFont.Weight.DemiBold)
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
            window = ViewStudentsWindow(self, self.username, self.role)
            window.show()
            logger.info(f"View students window opened by user {self.username}")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to open students window: {str(e)}")
            logger.error(f"Error opening view students window: {str(e)}")
    
    def _add_student(self):
        """Show add student window."""
        try:
            window = AddStudentWindow(self, self.username, self.role)
            window.student_added.connect(lambda: logger.info("Student added, refresh if needed"))
            window.show()
            logger.info(f"Add student window opened by user {self.username}")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to open add student window: {str(e)}")
            logger.error(f"Error opening add student window: {str(e)}")
    
    def _manage_students(self):
        """Show view students window (same as _show_students)."""
        self._show_students()
    
    def _show_student_management(self):
        """Show the student management window (legacy - redirects to view students)."""
        self._show_students()
    
    def _show_edit_student(self):
        """Show edit student window."""
        try:
            window = EditStudentWindow(self, self.username, self.role)
            window.show()
            logger.info(f"Edit student window opened by user {self.username}")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to open edit student window: {str(e)}")
            logger.error(f"Error opening edit student window: {str(e)}")
    
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
            from school_system.gui.windows.teacher_window.view_teachers_window import ViewTeachersWindow
            teacher_window = ViewTeachersWindow(self, self.username, self.role)
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
            window = TeacherImportExportWindow(self, self.username, self.role)
            window.show()
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to open teacher import/export window: {str(e)}")

    def _show_student_import_export(self):
        """Show student import/export window."""
        try:
            from school_system.gui.windows.student_window.student_import_export_window import StudentImportExportWindow
            window = StudentImportExportWindow(self, self.username, self.role)
            window.show()
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to open student import/export window: {str(e)}")

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
            logger.error(f"Error opening book management window: {str(e)}")

    def _show_distribution(self):
        """Show distribution window."""
        try:
            from school_system.gui.windows.book_window.distribution_window import DistributionWindow
            distribution_window = DistributionWindow(self, self.username, self.role)
            distribution_window.show()
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to open distribution window: {str(e)}")
            logger.error(f"Error opening distribution window: {str(e)}")

    def _show_book_import_export(self):
        """Show book import/export window."""
        try:
            from school_system.gui.windows.book_window.book_import_export_window import BookImportExportWindow
            import_export_window = BookImportExportWindow(self, self.username, self.role)
            import_export_window.show()
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to open book import/export window: {str(e)}")
            logger.error(f"Error opening book import/export window: {str(e)}")

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

    def _show_add_book_window(self):
        """Show add book window."""
        try:
            # Validate that the required module exists
            import os
            module_path = os.path.join(os.path.dirname(__file__), 'book_window', 'add_book_window.py')
            if not os.path.exists(module_path):
                raise FileNotFoundError(f"Book window module not found: {module_path}")

            from school_system.gui.windows.book_window.add_book_window import AddBookWindow
            add_window = AddBookWindow(self, self.username, self.role)
            add_window.book_added.connect(self._on_book_data_changed)
            add_window.show()
        except FileNotFoundError as e:
            QMessageBox.critical(self, "Error", f"Book management module is missing or corrupted. Please reinstall the application.\n\nDetails: {str(e)}")
            logger.error(f"Missing book window file: {str(e)}")
        except ImportError as e:
            QMessageBox.critical(self, "Error", f"Failed to import book management components. The module may be corrupted.\n\nDetails: {str(e)}")
            logger.error(f"Import error for add book window: {str(e)}")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to open add book window: {str(e)}")
            logger.error(f"Error opening add book window: {str(e)}")

    def _show_view_books_window(self):
        """Show view books window."""
        try:
            import os
            module_path = os.path.join(os.path.dirname(__file__), 'book_window', 'view_books_window.py')
            if not os.path.exists(module_path):
                raise FileNotFoundError(f"Book window module not found: {module_path}")

            from school_system.gui.windows.book_window.view_books_window import ViewBooksWindow
            view_window = ViewBooksWindow(self, self.username, self.role)
            view_window.book_updated.connect(self._on_book_data_changed)
            view_window.show()
        except FileNotFoundError as e:
            QMessageBox.critical(self, "Error", f"Book management module is missing or corrupted. Please reinstall the application.\n\nDetails: {str(e)}")
            logger.error(f"Missing book window file: {str(e)}")
        except ImportError as e:
            QMessageBox.critical(self, "Error", f"Failed to import book management components. The module may be corrupted.\n\nDetails: {str(e)}")
            logger.error(f"Import error for view books window: {str(e)}")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to open view books window: {str(e)}")
            logger.error(f"Error opening view books window: {str(e)}")

    def _show_borrow_book_window(self):
        """Show borrow book window."""
        try:
            import os
            module_path = os.path.join(os.path.dirname(__file__), 'book_window', 'borrow_book_window.py')
            if not os.path.exists(module_path):
                raise FileNotFoundError(f"Book window module not found: {module_path}")

            from school_system.gui.windows.book_window.borrow_book_window import BorrowBookWindow
            borrow_window = BorrowBookWindow(self, self.username, self.role)
            borrow_window.book_borrowed.connect(self._on_book_data_changed)
            borrow_window.show()
        except FileNotFoundError as e:
            QMessageBox.critical(self, "Error", f"Book management module is missing or corrupted. Please reinstall the application.\n\nDetails: {str(e)}")
            logger.error(f"Missing book window file: {str(e)}")
        except ImportError as e:
            QMessageBox.critical(self, "Error", f"Failed to import book management components. The module may be corrupted.\n\nDetails: {str(e)}")
            logger.error(f"Import error for borrow book window: {str(e)}")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to open borrow book window: {str(e)}")
            logger.error(f"Error opening borrow book window: {str(e)}")

    def _show_return_book_window(self):
        """Show return book window."""
        try:
            import os
            module_path = os.path.join(os.path.dirname(__file__), 'book_window', 'return_book_window.py')
            if not os.path.exists(module_path):
                raise FileNotFoundError(f"Book window module not found: {module_path}")

            from school_system.gui.windows.book_window.return_book_window import ReturnBookWindow
            return_window = ReturnBookWindow(self, self.username, self.role)
            return_window.book_returned.connect(self._on_book_data_changed)
            return_window.show()
        except FileNotFoundError as e:
            QMessageBox.critical(self, "Error", f"Book management module is missing or corrupted. Please reinstall the application.\n\nDetails: {str(e)}")
            logger.error(f"Missing book window file: {str(e)}")
        except ImportError as e:
            QMessageBox.critical(self, "Error", f"Failed to import book management components. The module may be corrupted.\n\nDetails: {str(e)}")
            logger.error(f"Import error for return book window: {str(e)}")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to open return book window: {str(e)}")
            logger.error(f"Error opening return book window: {str(e)}")

    def _on_book_data_changed(self):
        """Handle book data changes from child windows."""
        try:
            # Refresh dashboard if it's currently visible
            if self.current_view == "dashboard":
                self._load_content("dashboard")
            # Refresh book-related views if they're currently loaded
            elif self.current_view in ["view_books", "add_book", "borrow_book", "return_book", "book_import_export"]:
                self._load_content(self.current_view)

            logger.info("Book data changed, refreshed relevant views")
        except Exception as e:
            logger.error(f"Error handling book data change: {str(e)}")

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
            logger.info(f"Furniture management window opened by user {self.username}")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to open furniture management: {str(e)}")
            logger.error(f"Error opening furniture management window: {str(e)}")
    
    def _show_furniture_assignments(self):
        """Show furniture assignments window."""
        try:
            from school_system.gui.windows.furniture_window.furniture_assignments_window import FurnitureAssignmentsWindow
            window = FurnitureAssignmentsWindow(self, self.username, self.role)
            window.show()
            logger.info(f"Furniture assignments window opened by user {self.username}")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to open furniture assignments: {str(e)}")
            logger.error(f"Error opening furniture assignments window: {str(e)}")
    
    def _show_furniture_maintenance(self):
        """Show furniture maintenance window."""
        try:
            from school_system.gui.windows.furniture_window.furniture_maintenance_window import FurnitureMaintenanceWindow
            window = FurnitureMaintenanceWindow(self, self.username, self.role)
            window.show()
            logger.info(f"Furniture maintenance window opened by user {self.username}")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to open furniture maintenance: {str(e)}")
            logger.error(f"Error opening furniture maintenance window: {str(e)}")
    
    def _show_book_reports(self):
        """Show book reports window."""
        try:
            window = BookReportsWindow(self, self.username, self.role)
            window.show()
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to open book reports: {str(e)}")
    
    def _show_student_reports(self):
        """Show student reports window."""
        try:
            window = StudentReportsWindow(self, self.username, self.role)
            window.show()
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to open student reports: {str(e)}")
    
    def _show_custom_reports(self):
        """Show custom reports window."""
        try:
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
    
    def _show_library_activity(self):
        """Show library activity window."""
        try:
            from school_system.gui.windows.book_window.borrow_book_window import BorrowBookWindow
            window = BorrowBookWindow(self, self.username, self.role)
            window.show()
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to open library activity: {str(e)}")

    def _show_ream_management_window(self):
        """Show the ream management window."""
        try:
            window = ReamManagementWindow(self, self.username, self.role)
            window.show()
            logger.info(f"Ream management window opened by user {self.username}")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to open ream management: {str(e)}")
            logger.error(f"Error opening ream management window: {str(e)}")

    def _show_class_management_window(self):
        """Show the class management window."""
        try:
            from school_system.gui.windows.student_window.class_management_window import ClassManagementWindow
            window = ClassManagementWindow(self, self.username, self.role)
            window.show()
            logger.info(f"Class management window opened by user {self.username}")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to open class management: {str(e)}")
            logger.error(f"Error opening class management window: {str(e)}")

    def _show_library_activity_window(self):
        """Show the library activity window."""
        try:
            from school_system.gui.windows.student_window.library_activity_window import LibraryActivityWindow
            window = LibraryActivityWindow(self, self.username, self.role)
            window.show()
            logger.info(f"Library activity window opened by user {self.username}")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to open library activity: {str(e)}")
            logger.error(f"Error opening library activity window: {str(e)}")

    def closeEvent(self, event):
        """Handle window closing."""
        super().closeEvent(event)
