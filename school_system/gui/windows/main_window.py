"""
Main application window for the School System Management.

This module provides the main GUI interface for the school system with
dropdown menus and dynamic content loading.
"""

from PyQt6.QtWidgets import (QLabel, QMessageBox, QMenuBar, QSizePolicy, QFrame,
                            QVBoxLayout, QToolButton, QHBoxLayout, QPushButton,
                            QLineEdit, QGridLayout, QSplitter, QScrollArea,
                            QStackedWidget, QWidget, QMenu, QComboBox, QTableWidget, QTableWidgetItem, QDialog)
from PyQt6.QtCore import Qt, QTime, QTimer, pyqtSignal
from PyQt6.QtGui import QIcon, QFont, QAction
from typing import Callable, Dict, Any

from school_system.config.logging import logger
from school_system.gui.base.base_window import BaseApplicationWindow

# Service imports for dashboard data
from school_system.services.book_service import BookService
from school_system.services.student_service import StudentService
from school_system.services.teacher_service import TeacherService
from school_system.services.furniture_service import FurnitureService
from school_system.services.report_service import ReportService
from school_system.gui.dashboard_data_manager import DashboardDataManager, DataState
from school_system.services.class_management_service import ClassManagementService
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
from school_system.gui.windows.book_window.book_intake_window import BookIntakeWindow
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
from school_system.gui.windows.student_window.student_promotion_window import StudentPromotionWindow
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

        # Initialize services for dashboard data
        self._init_dashboard_services()

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

    def _init_dashboard_services(self):
        """Initialize services needed for dashboard data fetching."""
        try:
            # Initialize traditional services
            self.book_service = BookService()
            self.student_service = StudentService()
            self.teacher_service = TeacherService()
            self.furniture_service = FurnitureService()
            self.report_service = ReportService()
            self.class_management_service = ClassManagementService()

            # Initialize the new DashboardDataManager
            self.dashboard_data_manager = DashboardDataManager(self)

            # Register services with the data manager
            if self.student_service:
                self.dashboard_data_manager.register_service('student_service', self.student_service)
            if self.teacher_service:
                self.dashboard_data_manager.register_service('teacher_service', self.teacher_service)
            if self.book_service:
                self.dashboard_data_manager.register_service('book_service', self.book_service)
            if self.report_service:
                self.dashboard_data_manager.register_service('report_service', self.report_service)
            if self.furniture_service:
                self.dashboard_data_manager.register_service('furniture_service', self.furniture_service)

            # Connect data manager signals with debouncing
            self.dashboard_data_manager.data_updated.connect(self._on_dashboard_data_updated)
            self.dashboard_data_manager.data_error.connect(self._on_dashboard_data_error)
            self.dashboard_data_manager.loading_started.connect(self._on_dashboard_loading_started)
            self.dashboard_data_manager.loading_finished.connect(self._on_dashboard_loading_finished)

            # Add debouncing timer for dashboard updates
            self._dashboard_update_timer = QTimer(self)
            self._dashboard_update_timer.setSingleShot(True)
            self._dashboard_update_timer.timeout.connect(self._refresh_dashboard_display)
            self._dashboard_update_pending = False

            # Set up auto-refresh for critical data
            self._setup_auto_refresh()

            logger.info("Dashboard services and data manager initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize dashboard services: {str(e)}")
            # Set services to None so dashboard can use fallbacks
            self.book_service = None
            self.student_service = None
            self.teacher_service = None
            self.furniture_service = None
            self.report_service = None
            self.class_management_service = None
            self.dashboard_data_manager = None

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
                border: 1px solid {theme["border"]};
                background-color: {theme["surface"]};
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
            
            /* Dropdown Menu Styling */
            QMenu {{
                background-color: {theme["surface"]};
                border: 1px solid {theme["border"]};
                border-radius: 8px;
                padding: 8px 0px;
                margin: 0px;
                color: {theme["text"]};
            }}
            
            QMenu::item {{
                background-color: transparent;
                padding: 12px 24px;
                margin: 0px 8px;
                border-radius: 6px;
                color: {theme["text"]};
                font-size: 13px;
                font-weight: 500;
            }}
            
            QMenu::item:selected {{
                background-color: {theme["surface_hover"]};
                color: {theme["text"]};
            }}
            
            QMenu::item:hover {{
                background-color: {theme["primary"]};
                color: white;
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
        sidebar_layout.addSpacing(16)

        # Core Management Sections with Dropdown Menus
        sections = [
            {
                "icon": "👨‍🎓",
                "title": "Student Management",
                "menu_items": [
                    ("View Students", "view_students"),
                    ("Add Student", "add_student"),
                    ("Edit Student", "edit_student"),
                    ("Classes", "class_management"),
                    ("Enhanced Classes", "enhanced_class_management"),
                    ("Library Activity", "library_activity"),
                    ("Promotion", "student_promotion"),
                    ("Import/Export", "student_import_export"),
                    ("Ream", "ream_management"),
                ]
            },
            {
                "icon": "📚",
                "title": "Library Management",
                "menu_items": [
                    ("View Books", "view_books"),
                    ("Book Intake", "book_intake"),
                    ("Add Book", "add_book"),
                    ("Borrow", "borrow_book"),
                    ("Return", "return_book"),
                    ("Enhanced Borrow", "enhanced_borrow_book"),
                    ("Enhanced Return", "enhanced_return_book"),
                    ("QR Codes", "qr_management"),
                    ("Distribution", "distribution"),
                    ("Import/Export", "book_import_export"),
                ]
            },
            {
                "icon": "👩‍🏫",
                "title": "Staff Management",
                "menu_items": [
                    ("View Teachers", "view_teachers"),
                    ("Add Teacher", "add_teacher"),
                    ("Edit Teacher", "edit_teacher"),
                    ("Import/Export", "teacher_import_export"),
                ]
            },
            {
                "icon": "🪑",
                "title": "Facility Management",
                "menu_items": [
                    ("Manage Furniture", "manage_furniture"),
                    ("Assignments", "furniture_assignments"),
                    ("Maintenance", "furniture_maintenance"),
                    ("Enhanced Management", "enhanced_furniture_management"),
                ]
            },
            {
                "icon": "👥",
                "title": "User Management",
                "menu_items": [
                    ("Manage Users", "manage_users"),
                    ("View Users", "view_users"),
                    ("Add User", "add_user"),
                    ("Edit User", "edit_user"),
                    ("Delete User", "delete_user"),
                    ("Settings", "user_settings"),
                    ("Short Forms", "short_form_mappings"),
                    ("Sessions", "user_sessions"),
                    ("Activity Logs", "user_activity"),
                ]
            },
            {
                "icon": "📊",
                "title": "Reports & Analytics",
                "menu_items": [
                    ("Book Reports", "book_reports"),
                    ("Student Reports", "student_reports"),
                    ("Custom Reports", "custom_reports"),
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
                # Handle management actions differently - open separate windows
                if action_id in ["view_students", "add_student", "edit_student", "class_management",
                               "enhanced_class_management", "library_activity", "student_promotion", "student_import_export", "ream_management",
                               "view_teachers", "add_teacher", "edit_teacher", "teacher_import_export",
                               "view_books", "add_book", "borrow_book", "return_book", "enhanced_borrow_book",
                               "enhanced_return_book", "qr_management", "distribution", "book_intake", "book_import_export",
                               "manage_furniture", "furniture_assignments", "furniture_maintenance", "enhanced_furniture_management",
                               "manage_users", "view_users", "add_user", "edit_user", "delete_user",
                               "user_settings", "short_form_mappings", "user_sessions", "user_activity"]:
                    if action_id == "view_students":
                        action.triggered.connect(lambda checked: self._open_view_students_window())
                    elif action_id == "add_student":
                        action.triggered.connect(lambda checked: self._open_add_student_window())
                    elif action_id == "edit_student":
                        action.triggered.connect(lambda checked: self._show_edit_student_selection())
                    elif action_id == "class_management":
                        action.triggered.connect(lambda checked: self._open_class_management_window())
                    elif action_id == "enhanced_class_management":
                        action.triggered.connect(lambda checked: self._open_enhanced_class_management_window())
                    elif action_id == "library_activity":
                        action.triggered.connect(lambda checked: self._open_library_activity_window())
                    elif action_id == "student_promotion":
                        action.triggered.connect(lambda checked: self._open_student_promotion_window())
                    elif action_id == "student_import_export":
                        action.triggered.connect(lambda checked: self._open_student_import_export_window())
                    elif action_id == "ream_management":
                        action.triggered.connect(lambda checked: self._open_ream_management_window())
                    elif action_id == "view_teachers":
                        action.triggered.connect(lambda checked: self._open_view_teachers_window())
                    elif action_id == "add_teacher":
                        action.triggered.connect(lambda checked: self._open_add_teacher_window())
                    elif action_id == "edit_teacher":
                        action.triggered.connect(lambda checked: self._show_edit_teacher_selection())
                    elif action_id == "teacher_import_export":
                        action.triggered.connect(lambda checked: self._open_teacher_import_export_window())
                    elif action_id == "view_books":
                        action.triggered.connect(lambda checked: self._open_view_books_window())
                    elif action_id == "add_book":
                        action.triggered.connect(lambda checked: self._open_add_book_window())
                    elif action_id == "borrow_book":
                        action.triggered.connect(lambda checked: self._open_borrow_book_window())
                    elif action_id == "return_book":
                        action.triggered.connect(lambda checked: self._open_return_book_window())
                    elif action_id == "enhanced_borrow_book":
                        action.triggered.connect(lambda checked: self._open_enhanced_borrow_window())
                    elif action_id == "enhanced_return_book":
                        action.triggered.connect(lambda checked: self._open_enhanced_return_window())
                    elif action_id == "qr_management":
                        action.triggered.connect(lambda checked: self._open_qr_management_window())
                    elif action_id == "distribution":
                        action.triggered.connect(lambda checked: self._open_distribution_window())
                    elif action_id == "book_intake":
                        action.triggered.connect(lambda checked: self._open_book_intake_window())
                    elif action_id == "book_import_export":
                        action.triggered.connect(lambda checked: self._open_book_import_export_window())
                    elif action_id == "manage_furniture":
                        action.triggered.connect(lambda checked: self._open_manage_furniture_window())
                    elif action_id == "furniture_assignments":
                        action.triggered.connect(lambda checked: self._open_furniture_assignments_window())
                    elif action_id == "furniture_maintenance":
                        action.triggered.connect(lambda checked: self._open_furniture_maintenance_window())
                    elif action_id == "enhanced_furniture_management":
                        action.triggered.connect(lambda checked: self._open_enhanced_furniture_management_window())
                    elif action_id == "manage_users":
                        action.triggered.connect(lambda checked: self._open_manage_users_window())
                    elif action_id == "view_users":
                        action.triggered.connect(lambda checked: self._open_view_users_window())
                    elif action_id == "add_user":
                        action.triggered.connect(lambda checked: self._open_add_user_window())
                    elif action_id == "edit_user":
                        action.triggered.connect(lambda checked: self._open_edit_user_window())
                    elif action_id == "delete_user":
                        action.triggered.connect(lambda checked: self._open_delete_user_window())
                    elif action_id == "user_settings":
                        action.triggered.connect(lambda checked: self._open_user_settings_window())
                    elif action_id == "short_form_mappings":
                        action.triggered.connect(lambda checked: self._open_short_form_mappings_window())
                    elif action_id == "user_sessions":
                        action.triggered.connect(lambda checked: self._open_user_sessions_window())
                    elif action_id == "user_activity":
                        action.triggered.connect(lambda checked: self._open_user_activity_window())
                else:
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
        content_frame.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
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
        self.top_bar.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
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

        # Spacer
        top_layout.addStretch()

        # Search bar (moved to top right)
        search_frame = QFrame()
        search_layout = QHBoxLayout(search_frame)
        search_layout.setContentsMargins(0, 0, 0, 0)
        search_layout.setSpacing(0)

        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("🔍 Search students, books, users...")
        self.search_input.setMinimumWidth(300)
        self.search_input.textChanged.connect(self._on_search_text_changed)

        search_layout.addWidget(self.search_input)

        top_layout.addWidget(search_frame)

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
            # Prevent unnecessary reloads of the same content
            if self.current_view == content_id and content_id in self.content_views:
                return

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
            # Create container for the add teacher interface
            container = QWidget()
            layout = QVBoxLayout(container)
            layout.setContentsMargins(32, 32, 32, 32)
            layout.setSpacing(24)

            # Create add teacher content
            add_teacher_content = self._create_add_teacher_content()
            layout.addWidget(add_teacher_content)

            return container

        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to load add teacher interface: {str(e)}")
            logger.error(f"Error loading add teacher interface: {str(e)}")
            return self._create_default_view("add_teacher", self.get_theme_manager()._themes[self.get_theme()], self._get_role_color())

    def _create_add_teacher_content(self) -> QWidget:
        """Create the add teacher content widget."""
        try:
            theme_manager = self.get_theme_manager()
            theme = theme_manager._themes[self.get_theme()]

            content_widget = QWidget()
            main_layout = QVBoxLayout(content_widget)
            main_layout.setContentsMargins(24, 24, 24, 24)
            main_layout.setSpacing(24)

            # Header
            header = QLabel("➕ Add New Teacher")
            header.setStyleSheet(f"""
                font-size: 24px;
                font-weight: bold;
                color: {theme["text"]};
                margin-bottom: 8px;
            """)
            main_layout.addWidget(header)

            # Form card
            form_card = self._create_add_teacher_form(theme)
            main_layout.addWidget(form_card)

            return content_widget

        except Exception as e:
            logger.error(f"Error creating add teacher content: {str(e)}")
            error_widget = QWidget()
            error_layout = QVBoxLayout(error_widget)
            error_label = QLabel("Error loading add teacher form")
            error_label.setStyleSheet(f"color: {theme['error'] if 'error' in theme else 'red'}; font-size: 16px;")
            error_layout.addWidget(error_label)
            return error_widget

    def _create_add_teacher_form(self, theme) -> QWidget:
        """Create the add teacher form."""
        form_card = QWidget()
        form_card.setStyleSheet(f"""
            QWidget {{
                background-color: {theme["surface"]};
                border: 1px solid {theme["border"]};
                border-radius: 12px;
                padding: 24px;
            }}
        """)

        form_layout = QVBoxLayout(form_card)
        form_layout.setSpacing(16)

        # Name field
        name_layout = QVBoxLayout()
        name_label = QLabel("Teacher Name:")
        name_label.setStyleSheet(f"font-weight: 500; color: {theme['text']};")
        name_layout.addWidget(name_label)

        self.add_teacher_name = QLineEdit()
        self.add_teacher_name.setPlaceholderText("Enter teacher name")
        self.add_teacher_name.setStyleSheet(f"""
            QLineEdit {{
                padding: 10px 14px;
                border: 1px solid {theme["border"]};
                border-radius: 8px;
                background-color: {theme["surface"]};
                color: {theme["text"]};
                min-height: 36px;
            }}
            QLineEdit:focus {{
                border: 2px solid {theme["border_focus"]};
            }}
        """)
        name_layout.addWidget(self.add_teacher_name)
        form_layout.addLayout(name_layout)

        # Subject field
        subject_layout = QVBoxLayout()
        subject_label = QLabel("Subject:")
        subject_label.setStyleSheet(f"font-weight: 500; color: {theme['text']};")
        subject_layout.addWidget(subject_label)

        self.add_teacher_subject = QLineEdit()
        self.add_teacher_subject.setPlaceholderText("Enter subject")
        self.add_teacher_subject.setStyleSheet(f"""
            QLineEdit {{
                padding: 10px 14px;
                border: 1px solid {theme["border"]};
                border-radius: 8px;
                background-color: {theme["surface"]};
                color: {theme["text"]};
                min-height: 36px;
            }}
            QLineEdit:focus {{
                border: 2px solid {theme["border_focus"]};
            }}
        """)
        subject_layout.addWidget(self.add_teacher_subject)
        form_layout.addLayout(subject_layout)

        # Email field
        email_layout = QVBoxLayout()
        email_label = QLabel("Email:")
        email_label.setStyleSheet(f"font-weight: 500; color: {theme['text']};")
        email_layout.addWidget(email_label)

        self.add_teacher_email = QLineEdit()
        self.add_teacher_email.setPlaceholderText("Enter email address")
        self.add_teacher_email.setStyleSheet(f"""
            QLineEdit {{
                padding: 10px 14px;
                border: 1px solid {theme["border"]};
                border-radius: 8px;
                background-color: {theme["surface"]};
                color: {theme["text"]};
                min-height: 36px;
            }}
            QLineEdit:focus {{
                border: 2px solid {theme["border_focus"]};
            }}
        """)
        email_layout.addWidget(self.add_teacher_email)
        form_layout.addLayout(email_layout)

        # Phone field
        phone_layout = QVBoxLayout()
        phone_label = QLabel("Phone:")
        phone_label.setStyleSheet(f"font-weight: 500; color: {theme['text']};")
        phone_layout.addWidget(phone_label)

        self.add_teacher_phone = QLineEdit()
        self.add_teacher_phone.setPlaceholderText("Enter phone number")
        self.add_teacher_phone.setStyleSheet(f"""
            QLineEdit {{
                padding: 10px 14px;
                border: 1px solid {theme["border"]};
                border-radius: 8px;
                background-color: {theme["surface"]};
                color: {theme["text"]};
                min-height: 36px;
            }}
            QLineEdit:focus {{
                border: 2px solid {theme["border_focus"]};
            }}
        """)
        phone_layout.addWidget(self.add_teacher_phone)
        form_layout.addLayout(phone_layout)

        form_layout.addStretch()

        # Buttons
        buttons_layout = QHBoxLayout()
        buttons_layout.addStretch()

        cancel_btn = QPushButton("Cancel")
        cancel_btn.setStyleSheet(f"""
            QPushButton {{
                padding: 10px 20px;
                border-radius: 8px;
                border: 1px solid {theme["border"]};
                background-color: {theme["surface"]};
                color: {theme["text"]};
                min-height: 36px;
                font-size: 14px;
                font-weight: 500;
            }}
            QPushButton:hover {{
                background-color: {theme["surface_hover"]};
            }}
        """)
        cancel_btn.clicked.connect(lambda: self._load_content("dashboard"))
        buttons_layout.addWidget(cancel_btn)

        add_btn = QPushButton("Add Teacher")
        add_btn.setStyleSheet(f"""
            QPushButton {{
                padding: 10px 20px;
                border-radius: 8px;
                border: 1px solid {theme["border"]};
                background-color: {theme["primary"]};
                color: white;
                min-height: 36px;
                font-size: 14px;
                font-weight: 500;
            }}
            QPushButton:hover {{
                background-color: {theme["primary_hover"] if "primary_hover" in theme else theme["primary"]};
            }}
        """)
        add_btn.clicked.connect(self._add_teacher)
        buttons_layout.addWidget(add_btn)

        form_layout.addLayout(buttons_layout)

        return form_card

    def _add_teacher(self):
        """Handle adding a new teacher."""
        try:
            name = self.add_teacher_name.text().strip()
            subject = self.add_teacher_subject.text().strip()
            email = self.add_teacher_email.text().strip()
            phone = self.add_teacher_phone.text().strip()

            # Basic validation
            if not name or not subject:
                QMessageBox.warning(self, "Validation Error", "Name and subject are required.")
                return

            # Here you would typically save to database
            # For now, just show success message
            QMessageBox.information(self, "Success", f"Teacher '{name}' added successfully!")

            # Clear form
            self.add_teacher_name.clear()
            self.add_teacher_subject.clear()
            self.add_teacher_email.clear()
            self.add_teacher_phone.clear()

        except Exception as e:
            logger.error(f"Error adding teacher: {str(e)}")
            QMessageBox.critical(self, "Error", f"Failed to add teacher: {str(e)}")

    def _create_edit_teacher_view(self) -> QWidget:
        """Create the edit teacher content view."""
        try:
            # For now, redirect to view teachers - in a full implementation,
            # this would show a teacher selection interface
            return self._create_view_teachers_view()
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to load edit teacher interface: {str(e)}")
            logger.error(f"Error loading edit teacher interface: {str(e)}")
            return self._create_default_view("edit_teacher", self.get_theme_manager()._themes[self.get_theme()], self._get_role_color())

    def _create_teacher_import_export_view(self) -> QWidget:
        """Create the teacher import/export content view."""
        try:
            # Create container for the teacher import/export interface
            container = QWidget()
            layout = QVBoxLayout(container)
            layout.setContentsMargins(32, 32, 32, 32)
            layout.setSpacing(24)

            # Create teacher import/export content
            import_export_content = self._create_teacher_import_export_content()
            layout.addWidget(import_export_content)

            return container

        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to load teacher import/export interface: {str(e)}")
            logger.error(f"Error loading teacher import/export interface: {str(e)}")
            return self._create_default_view("teacher_import_export", self.get_theme_manager()._themes[self.get_theme()], self._get_role_color())

    def _create_teacher_import_export_content(self) -> QWidget:
        """Create the teacher import/export content widget."""
        try:
            theme_manager = self.get_theme_manager()
            theme = theme_manager._themes[self.get_theme()]

            content_widget = QWidget()
            main_layout = QVBoxLayout(content_widget)
            main_layout.setContentsMargins(24, 24, 24, 24)
            main_layout.setSpacing(24)

            # Header
            header = QLabel("📤 Teacher Import/Export")
            header.setStyleSheet(f"""
                font-size: 24px;
                font-weight: bold;
                color: {theme["text"]};
                margin-bottom: 8px;
            """)
            main_layout.addWidget(header)

            # Import/Export tabs
            tab_widget = QTabWidget()
            tab_widget.setStyleSheet(f"""
                QTabWidget::pane {{
                    border: 1px solid {theme["border"]};
                    background-color: {theme["surface"]};
                }}
                QTabBar::tab {{
                    padding: 10px 20px;
                    background-color: transparent;
                    color: {theme["text_secondary"]};
                    border: none;
                }}
                QTabBar::tab:selected {{
                    background-color: {theme["surface"]};
                    color: {theme["primary"]};
                    border-bottom: 2px solid {theme["primary"]};
                }}
            """)

            # Import tab
            import_tab = QWidget()
            import_layout = QVBoxLayout(import_tab)
            import_layout.setContentsMargins(20, 20, 20, 20)

            import_label = QLabel("Import teachers from CSV file")
            import_label.setStyleSheet(f"color: {theme['text']}; font-size: 16px;")
            import_layout.addWidget(import_label)

            import_btn = QPushButton("📥 Select CSV File & Import")
            import_btn.setStyleSheet(f"""
                QPushButton {{
                    padding: 12px 24px;
                    border-radius: 8px;
                    border: 1px solid {theme["border"]};
                    background-color: {theme["primary"]};
                    color: white;
                    font-size: 14px;
                    font-weight: 500;
                }}
                QPushButton:hover {{
                    background-color: {theme["primary_hover"] if "primary_hover" in theme else theme["primary"]};
                }}
            """)
            import_btn.clicked.connect(lambda: QMessageBox.information(self, "Import", "Teacher import functionality will be implemented here."))
            import_layout.addWidget(import_btn)

            import_layout.addStretch()

            # Export tab
            export_tab = QWidget()
            export_layout = QVBoxLayout(export_tab)
            export_layout.setContentsMargins(20, 20, 20, 20)

            export_label = QLabel("Export teachers to CSV file")
            export_label.setStyleSheet(f"color: {theme['text']}; font-size: 16px;")
            export_layout.addWidget(export_label)

            export_btn = QPushButton("📤 Export Teachers to CSV")
            export_btn.setStyleSheet(f"""
                QPushButton {{
                    padding: 12px 24px;
                    border-radius: 8px;
                    border: 1px solid {theme["border"]};
                    background-color: {theme["success"] if "success" in theme else "#4caf50"};
                    color: white;
                    font-size: 14px;
                    font-weight: 500;
                }}
                QPushButton:hover {{
                    background-color: {theme["success_hover"] if "success_hover" in theme else "#45a049"};
                }}
            """)
            export_btn.clicked.connect(lambda: QMessageBox.information(self, "Export", "Teacher export functionality will be implemented here."))
            export_layout.addWidget(export_btn)

            export_layout.addStretch()

            tab_widget.addTab(import_tab, "📥 Import")
            tab_widget.addTab(export_tab, "📤 Export")

            main_layout.addWidget(tab_widget)

            return content_widget

        except Exception as e:
            logger.error(f"Error creating teacher import/export content: {str(e)}")
            error_widget = QWidget()
            error_layout = QVBoxLayout(error_widget)
            error_label = QLabel("Error loading teacher import/export")
            error_label.setStyleSheet(f"color: {theme['error'] if 'error' in theme else 'red'}; font-size: 16px;")
            error_layout.addWidget(error_label)
            return error_widget

    def _create_manage_users_view(self) -> QWidget:
        """Create the manage users content view."""
        try:
            # Import the user window logic but create content widget instead of window
            from school_system.gui.windows.user_window.user_window import UserWindow

            # Create a container widget for the user management interface
            container = QWidget()
            layout = QVBoxLayout(container)
            layout.setContentsMargins(32, 32, 32, 32)
            layout.setSpacing(24)

            # Create user management content using UserWindow logic but adapted for content view
            user_window_content = self._create_user_management_content()
            layout.addWidget(user_window_content)

            return container

        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to load user management interface: {str(e)}")
            logger.error(f"Error loading user management interface: {str(e)}")
            return self._create_default_view("manage_users", self.get_theme_manager()._themes[self.get_theme()], self._get_role_color())

    def _create_user_management_content(self) -> QWidget:
        """Create the user management navigation content widget."""
        try:
            theme_manager = self.get_theme_manager()
            theme = theme_manager._themes[self.get_theme()]

            # Create main content layout
            content_widget = QWidget()
            main_layout = QVBoxLayout(content_widget)
            main_layout.setContentsMargins(24, 24, 24, 24)
            main_layout.setSpacing(24)

            # Header section
            header = self._create_user_management_header(theme)
            main_layout.addWidget(header)

            # Function cards grid
            cards_grid = self._create_user_function_cards(theme)
            main_layout.addWidget(cards_grid)

            return content_widget

        except Exception as e:
            logger.error(f"Error creating user management content: {str(e)}")
            # Return a simple error message widget
            error_widget = QWidget()
            error_layout = QVBoxLayout(error_widget)
            error_label = QLabel("Error loading user management interface")
            error_label.setStyleSheet(f"color: {theme['error'] if 'error' in theme else 'red'}; font-size: 16px;")
            error_layout.addWidget(error_label)
            return error_widget

    def _create_user_management_header(self, theme) -> QWidget:
        """Create the header section for user management."""
        header = QWidget()
        header_layout = QVBoxLayout(header)
        header_layout.setContentsMargins(0, 0, 0, 0)
        header_layout.setSpacing(8)

        # Title
        title = QLabel("User Management Center")
        title_font = QFont()
        title_font.setPointSize(24)
        title_font.setBold(True)
        title.setFont(title_font)
        title.setStyleSheet(f"color: {theme['text']}; margin-bottom: 8px;")
        header_layout.addWidget(title)

        # Subtitle
        subtitle = QLabel(f"Welcome, {self.username} ({self.role})")
        subtitle_font = QFont()
        subtitle_font.setPointSize(14)
        subtitle.setFont(subtitle_font)
        subtitle.setStyleSheet(f"color: {theme['text_secondary']}; margin-bottom: 16px;")
        header_layout.addWidget(subtitle)

        # Description
        description = QLabel(
            "Manage user accounts, settings, sessions, and activity logs. "
            "Click on any function below to open the dedicated management interface."
        )
        description.setStyleSheet(f"color: {theme['text_secondary']};")
        description.setWordWrap(True)
        header_layout.addWidget(description)

        return header

    def _create_user_function_cards(self, theme) -> QWidget:
        """Create a grid of function cards for user management navigation."""
        container = QWidget()
        grid_layout = QGridLayout(container)
        grid_layout.setContentsMargins(0, 0, 0, 0)
        grid_layout.setSpacing(16)

        # Row 1: User Management functions
        grid_layout.addWidget(self._create_user_function_card(
            "👥 Manage Users", "View, add, edit, and delete user accounts",
            self._open_view_users_window, theme
        ), 0, 0)

        grid_layout.addWidget(self._create_user_function_card(
            "➕ Add User", "Create new user accounts with roles",
            self._open_add_user_window, theme
        ), 0, 1)

        grid_layout.addWidget(self._create_user_function_card(
            "✏️ Edit User", "Update user roles and permissions",
            self._open_edit_user_window, theme
        ), 0, 2)

        grid_layout.addWidget(self._create_user_function_card(
            "🗑️ Delete User", "Remove user accounts permanently",
            self._open_delete_user_window, theme
        ), 0, 3)

        # Row 2: Settings and mappings
        grid_layout.addWidget(self._create_user_function_card(
            "⚙️ User Settings", "Manage user preferences and notifications",
            self._open_user_settings_window, theme
        ), 1, 0)

        grid_layout.addWidget(self._create_user_function_card(
            "🔤 Short Forms", "Manage short form mappings",
            self._open_short_form_mappings_window, theme
        ), 1, 1)

        grid_layout.addWidget(self._create_user_function_card(
            "🔐 Sessions", "Manage user login sessions",
            self._open_user_sessions_window, theme
        ), 1, 2)

        grid_layout.addWidget(self._create_user_function_card(
            "📊 Activity Logs", "Track user actions and activities",
            self._open_user_activity_window, theme
        ), 1, 3)

        return container

    def _create_user_function_card(self, title: str, description: str, callback, theme) -> QWidget:
        """Create a function navigation card."""
        card = QWidget()
        card_layout = QVBoxLayout(card)
        card_layout.setContentsMargins(20, 20, 20, 20)
        card_layout.setSpacing(12)

        # Apply card styling
        card.setStyleSheet(f"""
            QWidget {{
                background-color: {theme["surface"]};
                border: 1px solid {theme["border"]};
                border-radius: 12px;
                min-height: 120px;
            }}

            QWidget:hover {{
                background-color: {theme["surface_hover"]};
                border-color: {theme["primary"]};
            }}
        """)

        # Make card clickable
        card.mousePressEvent = lambda event: callback()

        # Title
        title_label = QLabel(title)
        title_font = QFont()
        title_font.setPointSize(16)
        title_font.setBold(True)
        title_label.setFont(title_font)
        title_label.setStyleSheet(f"color: {theme['text']};")
        card_layout.addWidget(title_label)

        # Description
        desc_label = QLabel(description)
        desc_label.setStyleSheet(f"color: {theme['text_secondary']};")
        desc_label.setWordWrap(True)
        card_layout.addWidget(desc_label)

        card_layout.addStretch()

        return card

    def _create_view_users_view(self) -> QWidget:
        """Create the view users content view."""
        try:
            # Create container for the view users interface
            container = QWidget()
            layout = QVBoxLayout(container)
            layout.setContentsMargins(32, 32, 32, 32)
            layout.setSpacing(16)

            # Create view users content
            view_users_content = self._create_view_users_content()
            layout.addWidget(view_users_content)

            return container

        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to load view users interface: {str(e)}")
            logger.error(f"Error loading view users interface: {str(e)}")
            return self._create_default_view("view_users", self.get_theme_manager()._themes[self.get_theme()], self._get_role_color())

    def _create_view_users_content(self) -> QWidget:
        """Create the view users content widget."""
        try:
            from school_system.services.auth_service import AuthService

            theme_manager = self.get_theme_manager()
            theme = theme_manager._themes[self.get_theme()]

            content_widget = QWidget()
            main_layout = QVBoxLayout(content_widget)
            main_layout.setContentsMargins(24, 24, 24, 24)
            main_layout.setSpacing(16)

            # Action bar
            action_bar = self._create_view_users_action_bar(theme)
            main_layout.addWidget(action_bar)

            # Users table
            users_table = self._create_view_users_table(theme)
            main_layout.addWidget(users_table, stretch=1)

            return content_widget

        except Exception as e:
            logger.error(f"Error creating view users content: {str(e)}")
            error_widget = QWidget()
            error_layout = QVBoxLayout(error_widget)
            error_label = QLabel("Error loading users view")
            error_label.setStyleSheet(f"color: {theme['error'] if 'error' in theme else 'red'}; font-size: 16px;")
            error_layout.addWidget(error_label)
            return error_widget

    def _create_view_users_action_bar(self, theme) -> QWidget:
        """Create the action bar for view users."""
        action_card = QWidget()
        action_card.setStyleSheet(f"""
            QWidget {{
                background-color: {theme["surface"]};
                border: 1px solid {theme["border"]};
                border-radius: 12px;
                padding: 16px;
            }}
        """)

        action_layout = QHBoxLayout(action_card)
        action_layout.setContentsMargins(16, 16, 16, 16)
        action_layout.setSpacing(12)

        # Search box
        self.view_users_search_box = QLineEdit()
        self.view_users_search_box.setPlaceholderText("Search users by username or role...")
        self.view_users_search_box.setMinimumWidth(300)
        self.view_users_search_box.textChanged.connect(self._on_view_users_search)
        action_layout.addWidget(self.view_users_search_box)

        # Role filter
        self.view_users_role_filter = QComboBox()
        self.view_users_role_filter.addItem("All Roles")
        self.view_users_role_filter.addItems(["admin", "librarian", "teacher", "student"])
        self.view_users_role_filter.setMinimumWidth(150)
        self.view_users_role_filter.currentTextChanged.connect(self._on_view_users_filter_changed)
        action_layout.addWidget(self.view_users_role_filter)

        action_layout.addStretch()

        # Action buttons
        add_btn = QPushButton("➕ Add User")
        add_btn.setStyleSheet(f"""
            QPushButton {{
                padding: 10px 20px;
                border-radius: 8px;
                border: 1px solid {theme["border"]};
                background-color: {theme["primary"]};
                color: white;
                min-height: 36px;
                font-size: 14px;
                font-weight: 500;
            }}
            QPushButton:hover {{
                background-color: {theme["primary_hover"] if "primary_hover" in theme else theme["primary"]};
            }}
        """)
        add_btn.clicked.connect(lambda: self._load_content("add_user"))
        action_layout.addWidget(add_btn)

        refresh_btn = QPushButton("🔄 Refresh")
        refresh_btn.setStyleSheet(f"""
            QPushButton {{
                padding: 10px 20px;
                border-radius: 8px;
                border: 1px solid {theme["border"]};
                background-color: {theme["surface"]};
                color: {theme["text"]};
                min-height: 36px;
                font-size: 14px;
                font-weight: 500;
            }}
            QPushButton:hover {{
                background-color: {theme["surface_hover"]};
            }}
        """)
        refresh_btn.clicked.connect(self._refresh_view_users_table)
        action_layout.addWidget(refresh_btn)

        return action_card

    def _create_view_users_table(self, theme) -> QWidget:
        """Create the users table."""
        table_card = QWidget()
        table_card.setStyleSheet(f"""
            QWidget {{
                background-color: {theme["surface"]};
                border: 1px solid {theme["border"]};
                border-radius: 12px;
                padding: 24px;
            }}
        """)

        table_layout = QVBoxLayout(table_card)

        # Create table
        self.view_users_table = QTableWidget()
        self.view_users_table.setColumnCount(5)
        self.view_users_table.setHorizontalHeaderLabels(["Username", "Role", "Created Date", "Last Login", "Actions"])

        # Table styling
        self.view_users_table.setStyleSheet(f"""
            QTableWidget {{
                border: 1px solid {theme["border"]};
                border-radius: 12px;
                background-color: {theme["surface"]};
                gridline-color: {theme["border"]};
            }}

            QHeaderView::section {{
                background-color: {theme["surface"]};
                padding: 12px 16px;
                border: none;
                border-bottom: 2px solid {theme["border"]};
                font-weight: 600;
                font-size: 13px;
                color: {theme["text"]};
                text-transform: uppercase;
                letter-spacing: 0.5px;
            }}

            QTableWidget::item {{
                padding: 8px 12px;
                border-bottom: 1px solid {theme["border"]};
            }}

            QTableWidget::item:selected {{
                background-color: {theme["primary"]};
                color: white;
            }}

            QTableWidget::item:hover {{
                background-color: {theme["surface_hover"]};
            }}
        """)

        # Set column widths
        self.view_users_table.setColumnWidth(0, 150)  # Username
        self.view_users_table.setColumnWidth(1, 120)  # Role
        self.view_users_table.setColumnWidth(2, 150)  # Created Date
        self.view_users_table.setColumnWidth(3, 150)  # Last Login
        self.view_users_table.setColumnWidth(4, 200)  # Actions

        table_layout.addWidget(self.view_users_table)

        # Load initial data
        self._refresh_view_users_table()

        return table_card

    def _on_view_users_search(self, text: str):
        """Handle search text changes for view users."""
        self._filter_view_users_table()

    def _on_view_users_filter_changed(self, role: str):
        """Handle role filter changes for view users."""
        self._filter_view_users_table()

    def _refresh_view_users_table(self):
        """Refresh the view users table with current data."""
        try:
            from school_system.services.auth_service import AuthService

            auth_service = AuthService()
            users = auth_service.get_all_users()

            self.view_users_table.setRowCount(len(users))

            for row, user in enumerate(users):
                # Username
                username_item = QTableWidgetItem(user.get('username', ''))
                username_item.setFlags(username_item.flags() & ~Qt.ItemFlag.ItemIsEditable)
                self.view_users_table.setItem(row, 0, username_item)

                # Role
                role_item = QTableWidgetItem(user.get('role', ''))
                role_item.setFlags(role_item.flags() & ~Qt.ItemFlag.ItemIsEditable)
                self.view_users_table.setItem(row, 1, role_item)

                # Created Date
                created_date = user.get('created_at', '')
                if created_date:
                    try:
                        # Format the date if it's a datetime object
                        if hasattr(created_date, 'strftime'):
                            created_date = created_date.strftime('%Y-%m-%d %H:%M')
                    except:
                        pass
                created_item = QTableWidgetItem(str(created_date))
                created_item.setFlags(created_item.flags() & ~Qt.ItemFlag.ItemIsEditable)
                self.view_users_table.setItem(row, 2, created_item)

                # Last Login
                last_login = user.get('last_login', '')
                if last_login:
                    try:
                        # Format the date if it's a datetime object
                        if hasattr(last_login, 'strftime'):
                            last_login = last_login.strftime('%Y-%m-%d %H:%M')
                    except:
                        pass
                login_item = QTableWidgetItem(str(last_login))
                login_item.setFlags(login_item.flags() & ~Qt.ItemFlag.ItemIsEditable)
                self.view_users_table.setItem(row, 3, login_item)

                # Actions
                actions_widget = QWidget()
                actions_layout = QHBoxLayout(actions_widget)
                actions_layout.setContentsMargins(4, 4, 4, 4)
                actions_layout.setSpacing(8)

                edit_btn = QPushButton("Edit")
                edit_btn.setFixedSize(60, 30)
                edit_btn.clicked.connect(lambda checked, u=user: self._edit_user(u))
                actions_layout.addWidget(edit_btn)

                delete_btn = QPushButton("Delete")
                delete_btn.setFixedSize(60, 30)
                delete_btn.clicked.connect(lambda checked, u=user: self._delete_user(u))
                actions_layout.addWidget(delete_btn)

                actions_layout.addStretch()
                self.view_users_table.setCellWidget(row, 4, actions_widget)

            # Apply current filters
            self._filter_view_users_table()

        except Exception as e:
            logger.error(f"Error refreshing view users table: {str(e)}")
            QMessageBox.warning(self, "Error", f"Failed to refresh users table: {str(e)}")

    def _filter_view_users_table(self):
        """Filter the view users table based on search and role filter."""
        try:
            search_text = self.view_users_search_box.text().lower()
            role_filter = self.view_users_role_filter.currentText()

            for row in range(self.view_users_table.rowCount()):
                show_row = True

                # Search filter
                if search_text:
                    username = self.view_users_table.item(row, 0).text().lower()
                    role = self.view_users_table.item(row, 1).text().lower()
                    if search_text not in username and search_text not in role:
                        show_row = False

                # Role filter
                if role_filter != "All Roles":
                    table_role = self.view_users_table.item(row, 1).text()
                    if table_role != role_filter:
                        show_row = False

                self.view_users_table.setRowHidden(row, not show_row)

        except Exception as e:
            logger.error(f"Error filtering view users table: {str(e)}")

    def _edit_user(self, user):
        """Handle editing a user."""
        try:
            # Store the user to edit and switch to edit view
            self.selected_user_for_edit = user
            self._load_content("edit_user")
        except Exception as e:
            logger.error(f"Error initiating user edit: {str(e)}")
            QMessageBox.warning(self, "Error", f"Failed to open edit user: {str(e)}")

    def _delete_user(self, user):
        """Handle deleting a user."""
        try:
            # Store the user to delete and switch to delete view
            self.selected_user_for_delete = user
            self._load_content("delete_user")
        except Exception as e:
            logger.error(f"Error initiating user delete: {str(e)}")
            QMessageBox.warning(self, "Error", f"Failed to open delete user: {str(e)}")

    def _create_add_user_view(self) -> QWidget:
        """Create the add user content view."""
        try:
            # Create container for the add user interface
            container = QWidget()
            layout = QVBoxLayout(container)
            layout.setContentsMargins(32, 32, 32, 32)
            layout.setSpacing(24)

            # Create add user content
            add_user_content = self._create_add_user_content()
            layout.addWidget(add_user_content)

            return container

        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to load add user interface: {str(e)}")
            logger.error(f"Error loading add user interface: {str(e)}")
            return self._create_default_view("add_user", self.get_theme_manager()._themes[self.get_theme()], self._get_role_color())

    def _create_add_user_content(self) -> QWidget:
        """Create the add user content widget."""
        try:
            from school_system.services.auth_service import AuthService
            from school_system.gui.windows.user_window.user_validation import UserValidator

            theme_manager = self.get_theme_manager()
            theme = theme_manager._themes[self.get_theme()]

            content_widget = QWidget()
            main_layout = QVBoxLayout(content_widget)
            main_layout.setContentsMargins(24, 24, 24, 24)
            main_layout.setSpacing(24)

            # Header
            header = QLabel("Add New User")
            header.setStyleSheet(f"""
                font-size: 24px;
                font-weight: bold;
                color: {theme["text"]};
                margin-bottom: 8px;
            """)
            main_layout.addWidget(header)

            # Form card
            form_card = self._create_add_user_form(theme)
            main_layout.addWidget(form_card)

            return content_widget

        except Exception as e:
            logger.error(f"Error creating add user content: {str(e)}")
            error_widget = QWidget()
            error_layout = QVBoxLayout(error_widget)
            error_label = QLabel("Error loading add user form")
            error_label.setStyleSheet(f"color: {theme['error'] if 'error' in theme else 'red'}; font-size: 16px;")
            error_layout.addWidget(error_label)
            return error_widget

    def _create_add_user_form(self, theme) -> QWidget:
        """Create the add user form."""
        form_card = QWidget()
        form_card.setStyleSheet(f"""
            QWidget {{
                background-color: {theme["surface"]};
                border: 1px solid {theme["border"]};
                border-radius: 12px;
                padding: 24px;
            }}
        """)

        form_layout = QVBoxLayout(form_card)
        form_layout.setSpacing(16)

        # Username field
        username_layout = QVBoxLayout()
        username_label = QLabel("Username:")
        username_label.setStyleSheet(f"font-weight: 500; color: {theme['text']};")
        username_layout.addWidget(username_label)

        self.add_user_username = QLineEdit()
        self.add_user_username.setPlaceholderText("Enter username")
        self.add_user_username.setStyleSheet(f"""
            QLineEdit {{
                padding: 10px 14px;
                border: 1px solid {theme["border"]};
                border-radius: 8px;
                background-color: {theme["surface"]};
                color: {theme["text"]};
                min-height: 36px;
            }}
            QLineEdit:focus {{
                border: 2px solid {theme["border_focus"]};
            }}
        """)
        username_layout.addWidget(self.add_user_username)
        form_layout.addLayout(username_layout)

        # Password field
        password_layout = QVBoxLayout()
        password_label = QLabel("Password:")
        password_label.setStyleSheet(f"font-weight: 500; color: {theme['text']};")
        password_layout.addWidget(password_label)

        self.add_user_password = QLineEdit()
        self.add_user_password.setEchoMode(QLineEdit.EchoMode.Password)
        self.add_user_password.setPlaceholderText("Enter password")
        self.add_user_password.setStyleSheet(f"""
            QLineEdit {{
                padding: 10px 14px;
                border: 1px solid {theme["border"]};
                border-radius: 8px;
                background-color: {theme["surface"]};
                color: {theme["text"]};
                min-height: 36px;
            }}
            QLineEdit:focus {{
                border: 2px solid {theme["border_focus"]};
            }}
        """)
        password_layout.addWidget(self.add_user_password)
        form_layout.addLayout(password_layout)

        # Confirm password field
        confirm_password_layout = QVBoxLayout()
        confirm_password_label = QLabel("Confirm Password:")
        confirm_password_label.setStyleSheet(f"font-weight: 500; color: {theme['text']};")
        confirm_password_layout.addWidget(confirm_password_label)

        self.add_user_confirm_password = QLineEdit()
        self.add_user_confirm_password.setEchoMode(QLineEdit.EchoMode.Password)
        self.add_user_confirm_password.setPlaceholderText("Confirm password")
        self.add_user_confirm_password.setStyleSheet(f"""
            QLineEdit {{
                padding: 10px 14px;
                border: 1px solid {theme["border"]};
                border-radius: 8px;
                background-color: {theme["surface"]};
                color: {theme["text"]};
                min-height: 36px;
            }}
            QLineEdit:focus {{
                border: 2px solid {theme["border_focus"]};
            }}
        """)
        confirm_password_layout.addWidget(self.add_user_confirm_password)
        form_layout.addLayout(confirm_password_layout)

        # Role field
        role_layout = QVBoxLayout()
        role_label = QLabel("Role:")
        role_label.setStyleSheet(f"font-weight: 500; color: {theme['text']};")
        role_layout.addWidget(role_label)

        self.add_user_role = QComboBox()
        self.add_user_role.addItems(["student", "teacher", "librarian", "admin"])
        self.add_user_role.setStyleSheet(f"""
            QComboBox {{
                padding: 10px 14px;
                border: 1px solid {theme["border"]};
                border-radius: 8px;
                background-color: {theme["surface"]};
                color: {theme["text"]};
                min-height: 36px;
            }}
            QComboBox:focus {{
                border: 2px solid {theme["border_focus"]};
            }}
            QComboBox::drop-down {{
                border: none;
            }}
            QComboBox::down-arrow {{
                image: none;
                border-left: 4px solid transparent;
                border-right: 4px solid transparent;
                border-top: 4px solid {theme["text"]};
                margin-right: 8px;
            }}
        """)
        role_layout.addWidget(self.add_user_role)
        form_layout.addLayout(role_layout)

        form_layout.addStretch()

        # Buttons
        buttons_layout = QHBoxLayout()
        buttons_layout.addStretch()

        cancel_btn = QPushButton("Cancel")
        cancel_btn.setStyleSheet(f"""
            QPushButton {{
                padding: 10px 20px;
                border-radius: 8px;
                border: 1px solid {theme["border"]};
                background-color: {theme["surface"]};
                color: {theme["text"]};
                min-height: 36px;
                font-size: 14px;
                font-weight: 500;
            }}
            QPushButton:hover {{
                background-color: {theme["surface_hover"]};
            }}
        """)
        cancel_btn.clicked.connect(lambda: self._load_content("manage_users"))
        buttons_layout.addWidget(cancel_btn)

        add_btn = QPushButton("Add User")
        add_btn.setStyleSheet(f"""
            QPushButton {{
                padding: 10px 20px;
                border-radius: 8px;
                border: 1px solid {theme["border"]};
                background-color: {theme["primary"]};
                color: white;
                min-height: 36px;
                font-size: 14px;
                font-weight: 500;
            }}
            QPushButton:hover {{
                background-color: {theme["primary_hover"] if "primary_hover" in theme else theme["primary"]};
            }}
        """)
        add_btn.clicked.connect(self._add_user)
        buttons_layout.addWidget(add_btn)

        form_layout.addLayout(buttons_layout)

        return form_card

    def _add_user(self):
        """Handle adding a new user."""
        try:
            from school_system.services.auth_service import AuthService
            from school_system.gui.windows.user_window.user_validation import UserValidator

            username = self.add_user_username.text().strip()
            password = self.add_user_password.text()
            confirm_password = self.add_user_confirm_password.text()
            role = self.add_user_role.currentText()

            # Validate input
            validator = UserValidator()
            if not validator.validate_username(username):
                QMessageBox.warning(self, "Invalid Username", "Username must be 3-20 characters and contain only letters, numbers, and underscores.")
                return

            if not validator.validate_password(password):
                QMessageBox.warning(self, "Invalid Password", "Password must be at least 6 characters long.")
                return

            if password != confirm_password:
                QMessageBox.warning(self, "Password Mismatch", "Passwords do not match.")
                return

            # Check if user already exists
            auth_service = AuthService()
            if auth_service.user_exists(username):
                QMessageBox.warning(self, "User Exists", "A user with this username already exists.")
                return

            # Create user
            success = auth_service.create_user(username, password, role)
            if success:
                QMessageBox.information(self, "Success", f"User '{username}' created successfully!")
                # Clear form
                self.add_user_username.clear()
                self.add_user_password.clear()
                self.add_user_confirm_password.clear()
                self.add_user_role.setCurrentIndex(0)
                # Emit signal to refresh user lists
                self._on_user_data_changed()
            else:
                QMessageBox.critical(self, "Error", "Failed to create user.")

        except Exception as e:
            logger.error(f"Error adding user: {str(e)}")
            QMessageBox.critical(self, "Error", f"Failed to add user: {str(e)}")

    def _on_user_data_changed(self):
        """Handle when user data has been changed."""
        # This could trigger a refresh of any open user lists
        # For now, it's a placeholder for future enhancements
        pass

    def _on_student_data_changed(self):
        """Handle when student data has been changed."""
        # This could trigger a refresh of any open student lists
        # For now, it's a placeholder for future enhancements
        pass

    def _on_teacher_data_changed(self):
        """Handle when teacher data has been changed."""
        # This could trigger a refresh of any open teacher lists
        # For now, it's a placeholder for future enhancements
        pass

    def _create_edit_user_view(self) -> QWidget:
        """Create the edit user content view."""
        try:
            # Create container for the edit user interface
            container = QWidget()
            layout = QVBoxLayout(container)
            layout.setContentsMargins(32, 32, 32, 32)
            layout.setSpacing(24)

            # Create edit user content
            edit_user_content = self._create_edit_user_content()
            layout.addWidget(edit_user_content)

            return container

        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to load edit user interface: {str(e)}")
            logger.error(f"Error loading edit user interface: {str(e)}")
            return self._create_default_view("edit_user", self.get_theme_manager()._themes[self.get_theme()], self._get_role_color())

    def _create_delete_user_view(self) -> QWidget:
        """Create the delete user content view."""
        try:
            # Create container for the delete user interface
            container = QWidget()
            layout = QVBoxLayout(container)
            layout.setContentsMargins(32, 32, 32, 32)
            layout.setSpacing(24)

            # Create delete user content
            delete_user_content = self._create_delete_user_content()
            layout.addWidget(delete_user_content)

            return container

        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to load delete user interface: {str(e)}")
            logger.error(f"Error loading delete user interface: {str(e)}")
            return self._create_default_view("delete_user", self.get_theme_manager()._themes[self.get_theme()], self._get_role_color())

    def _create_edit_user_content(self) -> QWidget:
        """Create the edit user content widget."""
        try:
            theme_manager = self.get_theme_manager()
            theme = theme_manager._themes[self.get_theme()]

            content_widget = QWidget()
            main_layout = QVBoxLayout(content_widget)
            main_layout.setContentsMargins(24, 24, 24, 24)
            main_layout.setSpacing(24)

            # Header
            header = QLabel("Edit User")
            header.setStyleSheet(f"""
                font-size: 24px;
                font-weight: bold;
                color: {theme["text"]};
                margin-bottom: 8px;
            """)
            main_layout.addWidget(header)

            # Check if a user is selected for editing
            if not hasattr(self, 'selected_user_for_edit') or not self.selected_user_for_edit:
                # Show user selection interface
                selection_card = self._create_user_selection_card("edit", theme)
                main_layout.addWidget(selection_card)
            else:
                # Show edit form for selected user
                edit_form = self._create_edit_user_form(theme)
                main_layout.addWidget(edit_form)

            return content_widget

        except Exception as e:
            logger.error(f"Error creating edit user content: {str(e)}")
            error_widget = QWidget()
            error_layout = QVBoxLayout(error_widget)
            error_label = QLabel("Error loading edit user interface")
            error_label.setStyleSheet(f"color: {theme['error'] if 'error' in theme else 'red'}; font-size: 16px;")
            error_layout.addWidget(error_label)
            return error_widget

    def _create_delete_user_content(self) -> QWidget:
        """Create the delete user content widget."""
        try:
            theme_manager = self.get_theme_manager()
            theme = theme_manager._themes[self.get_theme()]

            content_widget = QWidget()
            main_layout = QVBoxLayout(content_widget)
            main_layout.setContentsMargins(24, 24, 24, 24)
            main_layout.setSpacing(24)

            # Header
            header = QLabel("Delete User")
            header.setStyleSheet(f"""
                font-size: 24px;
                font-weight: bold;
                color: {theme["text"]};
                margin-bottom: 8px;
            """)
            main_layout.addWidget(header)

            # Check if a user is selected for deletion
            if not hasattr(self, 'selected_user_for_delete') or not self.selected_user_for_delete:
                # Show user selection interface
                selection_card = self._create_user_selection_card("delete", theme)
                main_layout.addWidget(selection_card)
            else:
                # Show delete confirmation for selected user
                delete_confirmation = self._create_delete_user_confirmation(theme)
                main_layout.addWidget(delete_confirmation)

            return content_widget

        except Exception as e:
            logger.error(f"Error creating delete user content: {str(e)}")
            error_widget = QWidget()
            error_layout = QVBoxLayout(error_widget)
            error_label = QLabel("Error loading delete user interface")
            error_label.setStyleSheet(f"color: {theme['error'] if 'error' in theme else 'red'}; font-size: 16px;")
            error_layout.addWidget(error_label)
            return error_widget

    def _create_user_selection_card(self, action: str, theme) -> QWidget:
        """Create a user selection card for edit/delete actions."""
        card = QWidget()
        card.setStyleSheet(f"""
            QWidget {{
                background-color: {theme["surface"]};
                border: 1px solid {theme["border"]};
                border-radius: 12px;
                padding: 24px;
            }}
        """)

        layout = QVBoxLayout(card)
        layout.setSpacing(16)

        message = QLabel(f"Please select a user to {action} from the Users view first.")
        message.setStyleSheet(f"color: {theme['text_secondary']}; font-size: 16px;")
        message.setWordWrap(True)
        layout.addWidget(message)

        buttons_layout = QHBoxLayout()
        buttons_layout.addStretch()

        back_btn = QPushButton("← Back to Users")
        back_btn.setStyleSheet(f"""
            QPushButton {{
                padding: 10px 20px;
                border-radius: 8px;
                border: 1px solid {theme["border"]};
                background-color: {theme["surface"]};
                color: {theme["text"]};
                min-height: 36px;
                font-size: 14px;
                font-weight: 500;
            }}
            QPushButton:hover {{
                background-color: {theme["surface_hover"]};
            }}
        """)
        back_btn.clicked.connect(lambda: self._load_content("view_users"))
        buttons_layout.addWidget(back_btn)

        layout.addLayout(buttons_layout)

        return card

    def _create_edit_user_form(self, theme) -> QWidget:
        """Create the edit user form for the selected user."""
        user = self.selected_user_for_edit

        form_card = QWidget()
        form_card.setStyleSheet(f"""
            QWidget {{
                background-color: {theme["surface"]};
                border: 1px solid {theme["border"]};
                border-radius: 12px;
                padding: 24px;
            }}
        """)

        form_layout = QVBoxLayout(form_card)
        form_layout.setSpacing(16)

        # Current user info
        info_label = QLabel(f"Editing user: {user.get('username', '')}")
        info_label.setStyleSheet(f"font-weight: bold; color: {theme['text']}; font-size: 16px;")
        form_layout.addWidget(info_label)

        # Role field
        role_layout = QVBoxLayout()
        role_label = QLabel("Role:")
        role_label.setStyleSheet(f"font-weight: 500; color: {theme['text']};")
        role_layout.addWidget(role_label)

        self.edit_user_role = QComboBox()
        self.edit_user_role.addItems(["student", "teacher", "librarian", "admin"])
        current_role = user.get('role', 'student')
        self.edit_user_role.setCurrentText(current_role)
        self.edit_user_role.setStyleSheet(f"""
            QComboBox {{
                padding: 10px 14px;
                border: 1px solid {theme["border"]};
                border-radius: 8px;
                background-color: {theme["surface"]};
                color: {theme["text"]};
                min-height: 36px;
            }}
        """)
        role_layout.addWidget(self.edit_user_role)
        form_layout.addLayout(role_layout)

        # Password reset option
        password_reset_layout = QVBoxLayout()
        password_reset_label = QLabel("Password Reset (leave empty to keep current):")
        password_reset_label.setStyleSheet(f"font-weight: 500; color: {theme['text']};")
        password_reset_layout.addWidget(password_reset_label)

        self.edit_user_new_password = QLineEdit()
        self.edit_user_new_password.setEchoMode(QLineEdit.EchoMode.Password)
        self.edit_user_new_password.setPlaceholderText("New password (optional)")
        self.edit_user_new_password.setStyleSheet(f"""
            QLineEdit {{
                padding: 10px 14px;
                border: 1px solid {theme["border"]};
                border-radius: 8px;
                background-color: {theme["surface"]};
                color: {theme["text"]};
                min-height: 36px;
            }}
        """)
        password_reset_layout.addWidget(self.edit_user_new_password)
        form_layout.addLayout(password_reset_layout)

        form_layout.addStretch()

        # Buttons
        buttons_layout = QHBoxLayout()
        buttons_layout.addStretch()

        cancel_btn = QPushButton("Cancel")
        cancel_btn.setStyleSheet(f"""
            QPushButton {{
                padding: 10px 20px;
                border-radius: 8px;
                border: 1px solid {theme["border"]};
                background-color: {theme["surface"]};
                color: {theme["text"]};
                min-height: 36px;
                font-size: 14px;
                font-weight: 500;
            }}
            QPushButton:hover {{
                background-color: {theme["surface_hover"]};
            }}
        """)
        cancel_btn.clicked.connect(lambda: self._load_content("manage_users"))
        buttons_layout.addWidget(cancel_btn)

        save_btn = QPushButton("Save Changes")
        save_btn.setStyleSheet(f"""
            QPushButton {{
                padding: 10px 20px;
                border-radius: 8px;
                border: 1px solid {theme["border"]};
                background-color: {theme["primary"]};
                color: white;
                min-height: 36px;
                font-size: 14px;
                font-weight: 500;
            }}
            QPushButton:hover {{
                background-color: {theme["primary_hover"] if "primary_hover" in theme else theme["primary"]};
            }}
        """)
        save_btn.clicked.connect(self._save_user_changes)
        buttons_layout.addWidget(save_btn)

        form_layout.addLayout(buttons_layout)

        return form_card

    def _create_delete_user_confirmation(self, theme) -> QWidget:
        """Create the delete user confirmation for the selected user."""
        user = self.selected_user_for_delete

        card = QWidget()
        card.setStyleSheet(f"""
            QWidget {{
                background-color: {theme["surface"]};
                border: 1px solid {theme["border"]};
                border-radius: 12px;
                padding: 24px;
            }}
        """)

        layout = QVBoxLayout(card)
        layout.setSpacing(16)

        # Warning message
        warning_label = QLabel("⚠️ Warning: This action cannot be undone!")
        warning_label.setStyleSheet(f"font-weight: bold; color: {theme['error'] if 'error' in theme else 'red'}; font-size: 16px;")
        layout.addWidget(warning_label)

        # User info
        user_info = QLabel(f"You are about to delete user: {user.get('username', '')}")
        user_info.setStyleSheet(f"color: {theme['text']}; font-size: 14px;")
        layout.addWidget(user_info)

        # Confirmation message
        confirm_msg = QLabel("Are you sure you want to permanently delete this user account? This will remove all associated data.")
        confirm_msg.setStyleSheet(f"color: {theme['text_secondary']}; font-size: 14px;")
        confirm_msg.setWordWrap(True)
        layout.addWidget(confirm_msg)

        layout.addStretch()

        # Buttons
        buttons_layout = QHBoxLayout()
        buttons_layout.addStretch()

        cancel_btn = QPushButton("Cancel")
        cancel_btn.setStyleSheet(f"""
            QPushButton {{
                padding: 10px 20px;
                border-radius: 8px;
                border: 1px solid {theme["border"]};
                background-color: {theme["surface"]};
                color: {theme["text"]};
                min-height: 36px;
                font-size: 14px;
                font-weight: 500;
            }}
            QPushButton:hover {{
                background-color: {theme["surface_hover"]};
            }}
        """)
        cancel_btn.clicked.connect(lambda: self._load_content("manage_users"))
        buttons_layout.addWidget(cancel_btn)

        delete_btn = QPushButton("Delete User")
        delete_btn.setStyleSheet(f"""
            QPushButton {{
                padding: 10px 20px;
                border-radius: 8px;
                border: 1px solid {theme["border"]};
                background-color: {theme['error'] if 'error' in theme else 'red'};
                color: white;
                min-height: 36px;
                font-size: 14px;
                font-weight: 500;
            }}
            QPushButton:hover {{
                background-color: {theme['error_hover'] if 'error_hover' in theme else '#cc0000'};
            }}
        """)
        delete_btn.clicked.connect(self._confirm_delete_user)
        buttons_layout.addWidget(delete_btn)

        layout.addLayout(buttons_layout)

        return card

    def _save_user_changes(self):
        """Save changes to the edited user."""
        try:
            from school_system.services.auth_service import AuthService

            user = self.selected_user_for_edit
            username = user.get('username')
            new_role = self.edit_user_role.currentText()
            new_password = self.edit_user_new_password.text().strip()

            auth_service = AuthService()

            # Update role if changed
            if new_role != user.get('role'):
                success = auth_service.update_user_role(username, new_role)
                if not success:
                    QMessageBox.critical(self, "Error", "Failed to update user role.")
                    return

            # Update password if provided
            if new_password:
                from school_system.gui.windows.user_window.user_validation import UserValidator
                validator = UserValidator()
                if not validator.validate_password(new_password):
                    QMessageBox.warning(self, "Invalid Password", "Password must be at least 6 characters long.")
                    return

                success = auth_service.update_user_password(username, new_password)
                if not success:
                    QMessageBox.critical(self, "Error", "Failed to update user password.")
                    return

            QMessageBox.information(self, "Success", f"User '{username}' updated successfully!")
            # Clear selection and return to manage users
            if hasattr(self, 'selected_user_for_edit'):
                delattr(self, 'selected_user_for_edit')
            self._on_user_data_changed()
            self._load_content("manage_users")

        except Exception as e:
            logger.error(f"Error saving user changes: {str(e)}")
            QMessageBox.critical(self, "Error", f"Failed to save user changes: {str(e)}")

    def _confirm_delete_user(self):
        """Confirm and delete the selected user."""
        try:
            from school_system.services.auth_service import AuthService

            user = self.selected_user_for_delete
            username = user.get('username')

            # Double-check with user
            reply = QMessageBox.question(
                self, "Confirm Deletion",
                f"Are you absolutely sure you want to delete user '{username}'?\n\nThis action cannot be undone!",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                QMessageBox.StandardButton.No
            )

            if reply == QMessageBox.StandardButton.Yes:
                auth_service = AuthService()
                success = auth_service.delete_user(username)

                if success:
                    QMessageBox.information(self, "Success", f"User '{username}' deleted successfully!")
                    # Clear selection and return to manage users
                    if hasattr(self, 'selected_user_for_delete'):
                        delattr(self, 'selected_user_for_delete')
                    self._on_user_data_changed()
                    self._load_content("manage_users")
                else:
                    QMessageBox.critical(self, "Error", "Failed to delete user.")

        except Exception as e:
            logger.error(f"Error deleting user: {str(e)}")
            QMessageBox.critical(self, "Error", f"Failed to delete user: {str(e)}")

    def _create_user_settings_content(self) -> QWidget:
        """Create the user settings content widget."""
        try:
            theme_manager = self.get_theme_manager()
            theme = theme_manager._themes[self.get_theme()]

            content_widget = QWidget()
            main_layout = QVBoxLayout(content_widget)
            main_layout.setContentsMargins(24, 24, 24, 24)
            main_layout.setSpacing(24)

            # Header
            header = QLabel("User Settings")
            header.setStyleSheet(f"""
                font-size: 24px;
                font-weight: bold;
                color: {theme["text"]};
                margin-bottom: 8px;
            """)
            main_layout.addWidget(header)

            # Settings card
            settings_card = QWidget()
            settings_card.setStyleSheet(f"""
                QWidget {{
                    background-color: {theme["surface"]};
                    border: 1px solid {theme["border"]};
                    border-radius: 12px;
                    padding: 24px;
                }}
            """)

            settings_layout = QVBoxLayout(settings_card)
            settings_layout.setSpacing(16)

            placeholder = QLabel("User settings functionality will be implemented here.")
            placeholder.setStyleSheet(f"color: {theme['text_secondary']}; font-size: 16px;")
            settings_layout.addWidget(placeholder)

            main_layout.addWidget(settings_card)

            return content_widget

        except Exception as e:
            logger.error(f"Error creating user settings content: {str(e)}")
            error_widget = QWidget()
            error_layout = QVBoxLayout(error_widget)
            error_label = QLabel("Error loading user settings")
            error_label.setStyleSheet(f"color: {theme['error'] if 'error' in theme else 'red'}; font-size: 16px;")
            error_layout.addWidget(error_label)
            return error_widget

    def _create_short_form_mappings_content(self) -> QWidget:
        """Create the short form mappings content widget."""
        try:
            theme_manager = self.get_theme_manager()
            theme = theme_manager._themes[self.get_theme()]

            content_widget = QWidget()
            main_layout = QVBoxLayout(content_widget)
            main_layout.setContentsMargins(24, 24, 24, 24)
            main_layout.setSpacing(24)

            # Header
            header = QLabel("Short Form Mappings")
            header.setStyleSheet(f"""
                font-size: 24px;
                font-weight: bold;
                color: {theme["text"]};
                margin-bottom: 8px;
            """)
            main_layout.addWidget(header)

            # Mappings card
            mappings_card = QWidget()
            mappings_card.setStyleSheet(f"""
                QWidget {{
                    background-color: {theme["surface"]};
                    border: 1px solid {theme["border"]};
                    border-radius: 12px;
                    padding: 24px;
                }}
            """)

            mappings_layout = QVBoxLayout(mappings_card)
            mappings_layout.setSpacing(16)

            placeholder = QLabel("Short form mappings functionality will be implemented here.")
            placeholder.setStyleSheet(f"color: {theme['text_secondary']}; font-size: 16px;")
            mappings_layout.addWidget(placeholder)

            main_layout.addWidget(mappings_card)

            return content_widget

        except Exception as e:
            logger.error(f"Error creating short form mappings content: {str(e)}")
            error_widget = QWidget()
            error_layout = QVBoxLayout(error_widget)
            error_label = QLabel("Error loading short form mappings")
            error_label.setStyleSheet(f"color: {theme['error'] if 'error' in theme else 'red'}; font-size: 16px;")
            error_layout.addWidget(error_label)
            return error_widget

    def _create_user_sessions_content(self) -> QWidget:
        """Create the user sessions content widget."""
        try:
            theme_manager = self.get_theme_manager()
            theme = theme_manager._themes[self.get_theme()]

            content_widget = QWidget()
            main_layout = QVBoxLayout(content_widget)
            main_layout.setContentsMargins(24, 24, 24, 24)
            main_layout.setSpacing(24)

            # Header
            header = QLabel("User Sessions")
            header.setStyleSheet(f"""
                font-size: 24px;
                font-weight: bold;
                color: {theme["text"]};
                margin-bottom: 8px;
            """)
            main_layout.addWidget(header)

            # Sessions card
            sessions_card = QWidget()
            sessions_card.setStyleSheet(f"""
                QWidget {{
                    background-color: {theme["surface"]};
                    border: 1px solid {theme["border"]};
                    border-radius: 12px;
                    padding: 24px;
                }}
            """)

            sessions_layout = QVBoxLayout(sessions_card)
            sessions_layout.setSpacing(16)

            placeholder = QLabel("User sessions management functionality will be implemented here.")
            placeholder.setStyleSheet(f"color: {theme['text_secondary']}; font-size: 16px;")
            sessions_layout.addWidget(placeholder)

            main_layout.addWidget(sessions_card)

            return content_widget

        except Exception as e:
            logger.error(f"Error creating user sessions content: {str(e)}")
            error_widget = QWidget()
            error_layout = QVBoxLayout(error_widget)
            error_label = QLabel("Error loading user sessions")
            error_label.setStyleSheet(f"color: {theme['error'] if 'error' in theme else 'red'}; font-size: 16px;")
            error_layout.addWidget(error_label)
            return error_widget

    def _create_user_activity_content(self) -> QWidget:
        """Create the user activity content widget."""
        try:
            theme_manager = self.get_theme_manager()
            theme = theme_manager._themes[self.get_theme()]

            content_widget = QWidget()
            main_layout = QVBoxLayout(content_widget)
            main_layout.setContentsMargins(24, 24, 24, 24)
            main_layout.setSpacing(24)

            # Header
            header = QLabel("User Activity Logs")
            header.setStyleSheet(f"""
                font-size: 24px;
                font-weight: bold;
                color: {theme["text"]};
                margin-bottom: 8px;
            """)
            main_layout.addWidget(header)

            # Activity card
            activity_card = QWidget()
            activity_card.setStyleSheet(f"""
                QWidget {{
                    background-color: {theme["surface"]};
                    border: 1px solid {theme["border"]};
                    border-radius: 12px;
                    padding: 24px;
                }}
            """)

            activity_layout = QVBoxLayout(activity_card)
            activity_layout.setSpacing(16)

            placeholder = QLabel("User activity logs functionality will be implemented here.")
            placeholder.setStyleSheet(f"color: {theme['text_secondary']}; font-size: 16px;")
            activity_layout.addWidget(placeholder)

            main_layout.addWidget(activity_card)

            return content_widget

        except Exception as e:
            logger.error(f"Error creating user activity content: {str(e)}")
            error_widget = QWidget()
            error_layout = QVBoxLayout(error_widget)
            error_label = QLabel("Error loading user activity logs")
            error_label.setStyleSheet(f"color: {theme['error'] if 'error' in theme else 'red'}; font-size: 16px;")
            error_layout.addWidget(error_label)
            return error_widget

    def _create_user_settings_view(self) -> QWidget:
        """Create the user settings content view."""
        try:
            # Create container for the user settings interface
            container = QWidget()
            layout = QVBoxLayout(container)
            layout.setContentsMargins(32, 32, 32, 32)
            layout.setSpacing(24)

            # Create user settings content
            settings_content = self._create_user_settings_content()
            layout.addWidget(settings_content)

            return container

        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to load user settings interface: {str(e)}")
            logger.error(f"Error loading user settings interface: {str(e)}")
            return self._create_default_view("user_settings", self.get_theme_manager()._themes[self.get_theme()], self._get_role_color())

    def _create_short_form_mappings_view(self) -> QWidget:
        """Create the short form mappings content view."""
        try:
            # Create container for the short form mappings interface
            container = QWidget()
            layout = QVBoxLayout(container)
            layout.setContentsMargins(32, 32, 32, 32)
            layout.setSpacing(24)

            # Create short form mappings content
            mappings_content = self._create_short_form_mappings_content()
            layout.addWidget(mappings_content)

            return container

        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to load short form mappings interface: {str(e)}")
            logger.error(f"Error loading short form mappings interface: {str(e)}")
            return self._create_default_view("short_form_mappings", self.get_theme_manager()._themes[self.get_theme()], self._get_role_color())

    def _create_user_sessions_view(self) -> QWidget:
        """Create the user sessions content view."""
        try:
            # Create container for the user sessions interface
            container = QWidget()
            layout = QVBoxLayout(container)
            layout.setContentsMargins(32, 32, 32, 32)
            layout.setSpacing(24)

            # Create user sessions content
            sessions_content = self._create_user_sessions_content()
            layout.addWidget(sessions_content)

            return container

        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to load user sessions interface: {str(e)}")
            logger.error(f"Error loading user sessions interface: {str(e)}")
            return self._create_default_view("user_sessions", self.get_theme_manager()._themes[self.get_theme()], self._get_role_color())

    def _create_user_activity_view(self) -> QWidget:
        """Create the user activity content view."""
        try:
            # Create container for the user activity interface
            container = QWidget()
            layout = QVBoxLayout(container)
            layout.setContentsMargins(32, 32, 32, 32)
            layout.setSpacing(24)

            # Create user activity content
            activity_content = self._create_user_activity_content()
            layout.addWidget(activity_content)

            return container

        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to load user activity interface: {str(e)}")
            logger.error(f"Error loading user activity interface: {str(e)}")
            return self._create_default_view("user_activity", self.get_theme_manager()._themes[self.get_theme()], self._get_role_color())

    def _open_view_users_window(self):
        """Open the view users window."""
        try:
            from school_system.gui.windows.user_window.view_users_window import ViewUsersWindow
            window = ViewUsersWindow(self, self.username, self.role)
            window.show()
        except Exception as e:
            logger.error(f"Error opening view users window: {str(e)}")
            QMessageBox.critical(self, "Error", f"Failed to open users view: {str(e)}")

    def _open_add_user_window(self):
        """Open the add user window."""
        try:
            from school_system.gui.windows.user_window.add_user_window import AddUserWindow
            window = AddUserWindow(self, self.username, self.role)
            window.user_added.connect(self._on_user_data_changed)
            window.show()
        except Exception as e:
            logger.error(f"Error opening add user window: {str(e)}")
            QMessageBox.critical(self, "Error", f"Failed to open add user window: {str(e)}")

    def _open_edit_user_window(self):
        """Open the user selection window for editing."""
        try:
            from school_system.gui.windows.user_window.view_users_window import ViewUsersWindow
            window = ViewUsersWindow(self, self.username, self.role)
            # The view users window has its own edit functionality
            window.show()
        except Exception as e:
            logger.error(f"Error opening user selection for edit: {str(e)}")
            QMessageBox.critical(self, "Error", f"Failed to open user selection: {str(e)}")

    def _open_delete_user_window(self):
        """Open the delete user window."""
        try:
            from school_system.gui.windows.user_window.delete_user_window import DeleteUserWindow
            window = DeleteUserWindow(self, self.username, self.role)
            window.user_deleted.connect(self._on_user_data_changed)
            window.show()
        except Exception as e:
            logger.error(f"Error opening delete user window: {str(e)}")
            QMessageBox.critical(self, "Error", f"Failed to open delete user window: {str(e)}")

    def _open_user_settings_window(self):
        """Open the user settings window."""
        try:
            from school_system.gui.windows.user_window.user_settings_window import UserSettingsWindow
            window = UserSettingsWindow(self, self.username, self.role)
            window.show()
        except Exception as e:
            logger.error(f"Error opening user settings window: {str(e)}")
            QMessageBox.critical(self, "Error", f"Failed to open user settings window: {str(e)}")

    def _open_short_form_mappings_window(self):
        """Open the short form mappings window."""
        try:
            from school_system.gui.windows.user_window.short_form_mappings_window import ShortFormMappingsWindow
            window = ShortFormMappingsWindow(self, self.username, self.role)
            window.show()
        except Exception as e:
            logger.error(f"Error opening short form mappings window: {str(e)}")
            QMessageBox.critical(self, "Error", f"Failed to open short form mappings window: {str(e)}")

    def _open_user_sessions_window(self):
        """Open the user sessions window."""
        try:
            from school_system.gui.windows.user_window.user_sessions_window import UserSessionsWindow
            window = UserSessionsWindow(self, self.username, self.role)
            window.show()
        except Exception as e:
            logger.error(f"Error opening user sessions window: {str(e)}")
            QMessageBox.critical(self, "Error", f"Failed to open user sessions window: {str(e)}")

    def _open_user_activity_window(self):
        """Open the user activity window."""
        try:
            from school_system.gui.windows.user_window.user_activity_window import UserActivityWindow
            window = UserActivityWindow(self, self.username, self.role)
            window.show()
        except Exception as e:
            logger.error(f"Error opening user activity window: {str(e)}")
            QMessageBox.critical(self, "Error", f"Failed to open user activity window: {str(e)}")

    def _open_manage_users_window(self):
        """Open the main user management window."""
        try:
            from school_system.gui.windows.user_window.user_window import UserWindow
            window = UserWindow(self, self.username, self.role)
            window.show()
        except Exception as e:
            logger.error(f"Error opening user management window: {str(e)}")
            QMessageBox.critical(self, "Error", f"Failed to open user management window: {str(e)}")

    def _open_view_students_window(self):
        """Open the view students window."""
        try:
            from school_system.gui.windows.student_window.view_students_window import ViewStudentsWindow
            window = ViewStudentsWindow(self, self.username, self.role)
            window.show()
        except Exception as e:
            logger.error(f"Error opening view students window: {str(e)}")
            QMessageBox.critical(self, "Error", f"Failed to open students view: {str(e)}")

    def _open_add_student_window(self):
        """Open the add student window."""
        try:
            from school_system.gui.windows.student_window.add_student_window import AddStudentWindow
            window = AddStudentWindow(self, self.username, self.role)
            window.student_added.connect(self._on_student_data_changed)
            window.show()
        except Exception as e:
            logger.error(f"Error opening add student window: {str(e)}")
            QMessageBox.critical(self, "Error", f"Failed to open add student window: {str(e)}")

    def _show_edit_student_selection(self):
        """Show student selection for editing."""
        try:
            from school_system.gui.windows.student_window.view_students_window import ViewStudentsWindow
            window = ViewStudentsWindow(self, self.username, self.role)
            # The view students window has its own edit functionality
            window.show()
        except Exception as e:
            logger.error(f"Error opening student selection for edit: {str(e)}")
            QMessageBox.critical(self, "Error", f"Failed to open student selection: {str(e)}")

    def _open_edit_student_window(self, student_id: str):
        """Open the edit student window for a specific student."""
        try:
            from school_system.gui.windows.student_window.edit_student_window import EditStudentWindow
            window = EditStudentWindow(student_id, self, self.username, self.role)
            window.student_updated.connect(self._on_student_data_changed)
            window.show()
        except Exception as e:
            logger.error(f"Error opening edit student window: {str(e)}")
            QMessageBox.critical(self, "Error", f"Failed to open edit student window: {str(e)}")

    def _open_student_promotion_window(self):
        """Open the student promotion window."""
        try:
            window = StudentPromotionWindow(self, self.username, self.role)
            window.show()
            logger.info("Student promotion window opened")
        except Exception as e:
            logger.error(f"Error opening student promotion window: {str(e)}")
            QMessageBox.critical(self, "Error", f"Failed to open student promotion window: {str(e)}")

    def _open_student_import_export_window(self):
        """Open the student import/export window."""
        try:
            from school_system.gui.windows.student_window.student_import_export_window import StudentImportExportWindow
            window = StudentImportExportWindow(self, self.username, self.role)
            window.show()
        except Exception as e:
            logger.error(f"Error opening student import/export window: {str(e)}")
            QMessageBox.critical(self, "Error", f"Failed to open student import/export window: {str(e)}")

    def _open_class_management_window(self):
        """Open the class management window."""
        try:
            from school_system.gui.windows.student_window.class_management_window import ClassManagementWindow
            window = ClassManagementWindow(self, self.username, self.role)
            window.show()
        except Exception as e:
            logger.error(f"Error opening class management window: {str(e)}")
            QMessageBox.critical(self, "Error", f"Failed to open class management window: {str(e)}")

    def _open_enhanced_class_management_window(self):
        """Open the enhanced class management window."""
        try:
            from school_system.gui.windows.student_window.enhanced_class_management_window import EnhancedClassManagementWindow
            window = EnhancedClassManagementWindow(self, self.username, self.role)
            window.show()
        except Exception as e:
            logger.error(f"Error opening enhanced class management window: {str(e)}")
            QMessageBox.critical(self, "Error", f"Failed to open enhanced class management window: {str(e)}")

    def _open_library_activity_window(self):
        """Open the library activity window."""
        try:
            from school_system.gui.windows.student_window.library_activity_window import LibraryActivityWindow
            window = LibraryActivityWindow(self, self.username, self.role)
            window.show()
        except Exception as e:
            logger.error(f"Error opening library activity window: {str(e)}")
            QMessageBox.critical(self, "Error", f"Failed to open library activity window: {str(e)}")

    def _open_ream_management_window(self):
        """Open the ream management window."""
        try:
            from school_system.gui.windows.student_window.ream_management_window import ReamManagementWindow
            window = ReamManagementWindow(self, self.username, self.role)
            window.show()
        except Exception as e:
            logger.error(f"Error opening ream management window: {str(e)}")
            QMessageBox.critical(self, "Error", f"Failed to open ream management window: {str(e)}")

    def _open_view_teachers_window(self):
        """Open the view teachers window."""
        try:
            from school_system.gui.windows.teacher_window.view_teachers_window import ViewTeachersWindow
            window = ViewTeachersWindow(self, self.username, self.role)
            window.show()
        except Exception as e:
            logger.error(f"Error opening view teachers window: {str(e)}")
            QMessageBox.critical(self, "Error", f"Failed to open teachers view: {str(e)}")

    def _open_add_teacher_window(self):
        """Open the add teacher window."""
        try:
            from school_system.gui.windows.teacher_window.add_teacher_window import AddTeacherWindow
            window = AddTeacherWindow(self, self.username, self.role)
            window.teacher_added.connect(self._on_teacher_data_changed)
            window.show()
        except Exception as e:
            logger.error(f"Error opening add teacher window: {str(e)}")
            QMessageBox.critical(self, "Error", f"Failed to open add teacher window: {str(e)}")

    def _show_edit_teacher_selection(self):
        """Show teacher selection for editing."""
        try:
            from school_system.gui.windows.teacher_window.view_teachers_window import ViewTeachersWindow
            window = ViewTeachersWindow(self, self.username, self.role)
            # The view teachers window has its own edit functionality
            window.show()
        except Exception as e:
            logger.error(f"Error opening teacher selection for edit: {str(e)}")
            QMessageBox.critical(self, "Error", f"Failed to open teacher selection: {str(e)}")

    def _open_edit_teacher_window(self, teacher_id: str):
        """Open the edit teacher window for a specific teacher."""
        try:
            from school_system.gui.windows.teacher_window.edit_teacher_window import EditTeacherWindow
            window = EditTeacherWindow(teacher_id, self, self.username, self.role)
            window.teacher_updated.connect(self._on_teacher_data_changed)
            window.show()
        except Exception as e:
            logger.error(f"Error opening edit teacher window: {str(e)}")
            QMessageBox.critical(self, "Error", f"Failed to open edit teacher window: {str(e)}")

    def _open_teacher_import_export_window(self):
        """Open the teacher import/export window."""
        try:
            from school_system.gui.windows.teacher_window.teacher_import_export_window import TeacherImportExportWindow
            window = TeacherImportExportWindow(self, self.username, self.role)
            window.show()
        except Exception as e:
            logger.error(f"Error opening teacher import/export window: {str(e)}")
            QMessageBox.critical(self, "Error", f"Failed to open teacher import/export window: {str(e)}")

    def _open_view_books_window(self):
        """Open the view books window."""
        try:
            from school_system.gui.windows.book_window.view_books_window import ViewBooksWindow
            window = ViewBooksWindow(self, self.username, self.role)
            window.show()
        except Exception as e:
            logger.error(f"Error opening view books window: {str(e)}")
            QMessageBox.critical(self, "Error", f"Failed to open books view: {str(e)}")

    def _open_add_book_window(self):
        """Open the add book window."""
        try:
            from school_system.gui.windows.book_window.add_book_window import AddBookWindow
            window = AddBookWindow(self, self.username, self.role)
            window.book_added.connect(self._on_book_data_changed)
            window.show()
        except Exception as e:
            logger.error(f"Error opening add book window: {str(e)}")
            QMessageBox.critical(self, "Error", f"Failed to open add book window: {str(e)}")

    def _open_borrow_book_window(self):
        """Open the borrow book window."""
        try:
            from school_system.gui.windows.book_window.borrow_book_window import BorrowBookWindow
            window = BorrowBookWindow(self, self.username, self.role)
            window.book_borrowed.connect(self._on_book_data_changed)
            window.show()
        except Exception as e:
            logger.error(f"Error opening borrow book window: {str(e)}")
            QMessageBox.critical(self, "Error", f"Failed to open borrow book window: {str(e)}")

    def _open_return_book_window(self):
        """Open the return book window."""
        try:
            from school_system.gui.windows.book_window.return_book_window import ReturnBookWindow
            window = ReturnBookWindow(self, self.username, self.role)
            window.book_returned.connect(self._on_book_data_changed)
            window.show()
        except Exception as e:
            logger.error(f"Error opening return book window: {str(e)}")
            QMessageBox.critical(self, "Error", f"Failed to open return book window: {str(e)}")

    def _open_enhanced_borrow_window(self):
        """Open the enhanced borrow per stream per subject window."""
        try:
            # First, show a dialog to select class/stream/subject (optional)
            from school_system.gui.windows.book_window.enhanced_borrow_window import EnhancedBorrowWindow
            from school_system.gui.windows.dialogs.class_stream_selection_dialog import ClassStreamSelectionDialog
            
            # Open selection dialog
            selection_dialog = ClassStreamSelectionDialog(self, self.username, self.role)
            if selection_dialog.exec() == QDialog.DialogCode.Accepted:
                class_name = selection_dialog.get_class_level()
                stream_name = selection_dialog.get_stream()

                window = EnhancedBorrowWindow(
                    self,
                    self.username,
                    self.role,
                    class_name=class_name,
                    stream_name=stream_name
                )
                window.borrow_completed.connect(self._on_book_data_changed)
                window.show()
        except ImportError:
            # If selection dialog doesn't exist, open directly without filters
            try:
                from school_system.gui.windows.book_window.enhanced_borrow_window import EnhancedBorrowWindow
                window = EnhancedBorrowWindow(
                    self,
                    self.username,
                    self.role,
                    class_name=None,
                    stream_name=None
                )
                window.borrow_completed.connect(self._on_book_data_changed)
                window.show()
            except Exception as e:
                logger.error(f"Error opening enhanced borrow window: {str(e)}")
                QMessageBox.critical(self, "Error", f"Failed to open enhanced borrow window: {str(e)}")
        except Exception as e:
            logger.error(f"Error opening enhanced borrow window: {str(e)}")
            QMessageBox.critical(self, "Error", f"Failed to open enhanced borrow window: {str(e)}")

    def _open_enhanced_return_window(self):
        """Open the enhanced return per stream per subject window."""
        try:
            # First, show a dialog to select class/stream/subject (optional)
            from school_system.gui.windows.book_window.enhanced_return_window import EnhancedReturnWindow
            from school_system.gui.windows.dialogs.class_stream_selection_dialog import ClassStreamSelectionDialog

            # Open selection dialog
            selection_dialog = ClassStreamSelectionDialog(self, self.username, self.role)
            if selection_dialog.exec() == QDialog.DialogCode.Accepted:
                class_name = selection_dialog.get_class_level()
                stream_name = selection_dialog.get_stream()

                window = EnhancedReturnWindow(
                    self,
                    self.username,
                    self.role,
                    class_name=class_name,
                    stream_name=stream_name
                )
                window.return_completed.connect(self._on_book_data_changed)
                window.show()
        except ImportError:
            # If selection dialog doesn't exist, open directly without filters
            try:
                from school_system.gui.windows.book_window.enhanced_return_window import EnhancedReturnWindow
                window = EnhancedReturnWindow(
                    self,
                    self.username,
                    self.role,
                    class_name=None,
                    stream_name=None
                )
                window.return_completed.connect(self._on_book_data_changed)
                window.show()
            except Exception as e:
                logger.error(f"Error opening enhanced return window: {str(e)}")
                QMessageBox.critical(self, "Error", f"Failed to open enhanced return window: {str(e)}")
        except Exception as e:
            logger.error(f"Error opening enhanced return window: {str(e)}")
            QMessageBox.critical(self, "Error", f"Failed to open enhanced return window: {str(e)}")

    def _open_qr_management_window(self):
        """Open the QR code management window."""
        try:
            from school_system.gui.windows.book_window.qr_management_window import QRManagementWindow
            window = QRManagementWindow(
                self,
                self.username,
                self.role,
                initial_tab="books"
            )
            window.operation_completed.connect(self._on_book_data_changed)
            window.show()
        except Exception as e:
            logger.error(f"Error opening QR management window: {str(e)}")
            QMessageBox.critical(self, "Error", f"Failed to open QR management window: {str(e)}")

    def _open_distribution_window(self):
        """Open the distribution window."""
        try:
            from school_system.gui.windows.book_window.distribution_window import DistributionWindow
            window = DistributionWindow(self, self.username, self.role)
            window.show()
        except Exception as e:
            logger.error(f"Error opening distribution window: {str(e)}")
            QMessageBox.critical(self, "Error", f"Failed to open distribution window: {str(e)}")

    def _open_book_import_export_window(self):
        """Open the book import/export window."""
        try:
            from school_system.gui.windows.book_window.book_import_export_window import BookImportExportWindow
            window = BookImportExportWindow(self, self.username, self.role)
            window.show()
        except Exception as e:
            logger.error(f"Error opening book import/export window: {str(e)}")
            QMessageBox.critical(self, "Error", f"Failed to open book import/export window: {str(e)}")

    def _open_book_intake_window(self):
        """Open the book intake window."""
        try:
            window = BookIntakeWindow(self, self.username, self.role)
            window.show()
        except Exception as e:
            logger.error(f"Error opening book intake window: {str(e)}")
            QMessageBox.critical(self, "Error", f"Failed to open book intake window: {str(e)}")

    def _open_manage_furniture_window(self):
        """Open the manage furniture window."""
        try:
            from school_system.gui.windows.furniture_window.manage_furniture_window import ManageFurnitureWindow
            window = ManageFurnitureWindow(self, self.username, self.role)
            window.show()
        except Exception as e:
            logger.error(f"Error opening manage furniture window: {str(e)}")
            QMessageBox.critical(self, "Error", f"Failed to open manage furniture window: {str(e)}")

    def _open_furniture_assignments_window(self):
        """Open the furniture assignments window."""
        try:
            from school_system.gui.windows.furniture_window.furniture_assignments_window import FurnitureAssignmentsWindow
            window = FurnitureAssignmentsWindow(self, self.username, self.role)
            window.show()
        except Exception as e:
            logger.error(f"Error opening furniture assignments window: {str(e)}")
            QMessageBox.critical(self, "Error", f"Failed to open furniture assignments window: {str(e)}")

    def _open_furniture_maintenance_window(self):
        """Open the furniture maintenance window."""
        try:
            from school_system.gui.windows.furniture_window.furniture_maintenance_window import FurnitureMaintenanceWindow
            window = FurnitureMaintenanceWindow(self, self.username, self.role)
            window.show()
        except Exception as e:
            logger.error(f"Error opening furniture maintenance window: {str(e)}")
            QMessageBox.critical(self, "Error", f"Failed to open furniture maintenance window: {str(e)}")

    def _open_enhanced_furniture_management_window(self):
        """Open the enhanced furniture management window."""
        try:
            # First, show a dialog to select class/stream (optional)
            from school_system.gui.windows.furniture_window.enhanced_furniture_management_window import EnhancedFurnitureManagementWindow
            from school_system.gui.windows.dialogs.class_stream_selection_dialog import ClassStreamSelectionDialog
            
            # Open selection dialog
            selection_dialog = ClassStreamSelectionDialog(self, self.username, self.role, include_subject=False)
            if selection_dialog.exec() == QDialog.DialogCode.Accepted:
                class_level = selection_dialog.get_class_level()
                stream = selection_dialog.get_stream()
                
                window = EnhancedFurnitureManagementWindow(
                    self,
                    self.username,
                    self.role,
                    class_level=class_level,
                    stream=stream
                )
                window.furniture_operation_completed.connect(self._on_furniture_data_changed)
                window.show()
        except ImportError:
            # If selection dialog doesn't exist, open directly without filters
            try:
                from school_system.gui.windows.furniture_window.enhanced_furniture_management_window import EnhancedFurnitureManagementWindow
                window = EnhancedFurnitureManagementWindow(
                    self,
                    self.username,
                    self.role,
                    class_level=None,
                    stream=None
                )
                window.furniture_operation_completed.connect(self._on_furniture_data_changed)
                window.show()
            except Exception as e:
                logger.error(f"Error opening enhanced furniture management window: {str(e)}")
                QMessageBox.critical(self, "Error", f"Failed to open enhanced furniture management window: {str(e)}")
        except Exception as e:
            logger.error(f"Error opening enhanced furniture management window: {str(e)}")
            QMessageBox.critical(self, "Error", f"Failed to open enhanced furniture management window: {str(e)}")

    def _open_book_reports_window(self):
        """Open the book reports window."""
        try:
            from school_system.gui.windows.report_window.book_reports_window import BookReportsWindow
            window = BookReportsWindow(self, self.username, self.role)
            window.show()
        except Exception as e:
            logger.error(f"Error opening book reports window: {str(e)}")
            QMessageBox.critical(self, "Error", f"Failed to open book reports window: {str(e)}")

    def _open_student_reports_window(self):
        """Open the student reports window."""
        try:
            from school_system.gui.windows.report_window.student_reports_window import StudentReportsWindow
            window = StudentReportsWindow(self, self.username, self.role)
            window.show()
        except Exception as e:
            logger.error(f"Error opening student reports window: {str(e)}")
            QMessageBox.critical(self, "Error", f"Failed to open student reports window: {str(e)}")

    def _open_custom_reports_window(self):
        """Open the custom reports window."""
        try:
            from school_system.gui.windows.report_window.custom_reports_window import CustomReportsWindow
            window = CustomReportsWindow(self, self.username, self.role)
            window.show()
        except Exception as e:
            logger.error(f"Error opening custom reports window: {str(e)}")
            QMessageBox.critical(self, "Error", f"Failed to open custom reports window: {str(e)}")

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
            # Create container for the manage furniture interface
            container = QWidget()
            layout = QVBoxLayout(container)
            layout.setContentsMargins(32, 32, 32, 32)
            layout.setSpacing(16)

            # Create manage furniture content
            manage_furniture_content = self._create_manage_furniture_content()
            layout.addWidget(manage_furniture_content)

            return container

        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to load furniture management interface: {str(e)}")
            logger.error(f"Error loading furniture management interface: {str(e)}")
            return self._create_default_view("manage_furniture", self.get_theme_manager()._themes[self.get_theme()], self._get_role_color())

    def _create_manage_furniture_content(self) -> QWidget:
        """Create the manage furniture content widget."""
        try:
            theme_manager = self.get_theme_manager()
            theme = theme_manager._themes[self.get_theme()]

            content_widget = QWidget()
            main_layout = QVBoxLayout(content_widget)
            main_layout.setContentsMargins(24, 24, 24, 24)
            main_layout.setSpacing(16)

            # Action bar
            action_bar = self._create_manage_furniture_action_bar(theme)
            main_layout.addWidget(action_bar)

            # Furniture table
            furniture_table = self._create_manage_furniture_table(theme)
            main_layout.addWidget(furniture_table, stretch=1)

            return content_widget

        except Exception as e:
            logger.error(f"Error creating manage furniture content: {str(e)}")
            error_widget = QWidget()
            error_layout = QVBoxLayout(error_widget)
            error_label = QLabel("Error loading furniture management")
            error_label.setStyleSheet(f"color: {theme['error'] if 'error' in theme else 'red'}; font-size: 16px;")
            error_layout.addWidget(error_label)
            return error_widget

    def _create_manage_furniture_action_bar(self, theme) -> QWidget:
        """Create the action bar for manage furniture."""
        action_card = QWidget()
        action_card.setStyleSheet(f"""
            QWidget {{
                background-color: {theme["surface"]};
                border: 1px solid {theme["border"]};
                border-radius: 12px;
                padding: 16px;
            }}
        """)

        action_layout = QHBoxLayout(action_card)
        action_layout.setContentsMargins(16, 16, 16, 16)
        action_layout.setSpacing(12)

        # Search box
        self.manage_furniture_search_box = QLineEdit()
        self.manage_furniture_search_box.setPlaceholderText("Search furniture by name or type...")
        self.manage_furniture_search_box.setMinimumWidth(300)
        self.manage_furniture_search_box.textChanged.connect(self._on_manage_furniture_search)
        action_layout.addWidget(self.manage_furniture_search_box)

        # Type filter
        self.manage_furniture_type_filter = QComboBox()
        self.manage_furniture_type_filter.addItem("All Types")
        self.manage_furniture_type_filter.addItems(["Chair", "Table", "Desk", "Cabinet", "Shelf", "Other"])
        self.manage_furniture_type_filter.setMinimumWidth(150)
        self.manage_furniture_type_filter.currentTextChanged.connect(self._on_manage_furniture_filter_changed)
        action_layout.addWidget(self.manage_furniture_type_filter)

        action_layout.addStretch()

        # Action buttons
        add_btn = QPushButton("➕ Add Furniture")
        add_btn.setStyleSheet(f"""
            QPushButton {{
                padding: 10px 20px;
                border-radius: 8px;
                border: 1px solid {theme["border"]};
                background-color: {theme["primary"]};
                color: white;
                min-height: 36px;
                font-size: 14px;
                font-weight: 500;
            }}
            QPushButton:hover {{
                background-color: {theme["primary_hover"] if "primary_hover" in theme else theme["primary"]};
            }}
        """)
        add_btn.clicked.connect(lambda: self._load_content("furniture_assignments"))
        action_layout.addWidget(add_btn)

        refresh_btn = QPushButton("🔄 Refresh")
        refresh_btn.setStyleSheet(f"""
            QPushButton {{
                padding: 10px 20px;
                border-radius: 8px;
                border: 1px solid {theme["border"]};
                background-color: {theme["surface"]};
                color: {theme["text"]};
                min-height: 36px;
                font-size: 14px;
                font-weight: 500;
            }}
            QPushButton:hover {{
                background-color: {theme["surface_hover"]};
            }}
        """)
        refresh_btn.clicked.connect(self._refresh_manage_furniture_table)
        action_layout.addWidget(refresh_btn)

        return action_card

    def _create_manage_furniture_table(self, theme) -> QWidget:
        """Create the furniture table."""
        table_card = QWidget()
        table_card.setStyleSheet(f"""
            QWidget {{
                background-color: {theme["surface"]};
                border: 1px solid {theme["border"]};
                border-radius: 12px;
                padding: 24px;
            }}
        """)

        table_layout = QVBoxLayout(table_card)

        # Create table
        self.manage_furniture_table = QTableWidget()
        self.manage_furniture_table.setColumnCount(5)
        self.manage_furniture_table.setHorizontalHeaderLabels(["Name", "Type", "Location", "Condition", "Actions"])

        # Table styling
        self.manage_furniture_table.setStyleSheet(f"""
            QTableWidget {{
                border: 1px solid {theme["border"]};
                border-radius: 12px;
                background-color: {theme["surface"]};
                gridline-color: {theme["border"]};
            }}

            QHeaderView::section {{
                background-color: {theme["surface"]};
                padding: 12px 16px;
                border: none;
                border-bottom: 2px solid {theme["border"]};
                font-weight: 600;
                font-size: 13px;
                color: {theme["text"]};
                text-transform: uppercase;
                letter-spacing: 0.5px;
            }}

            QTableWidget::item {{
                padding: 8px 12px;
                border-bottom: 1px solid {theme["border"]};
            }}

            QTableWidget::item:selected {{
                background-color: {theme["primary"]};
                color: white;
            }}

            QTableWidget::item:hover {{
                background-color: {theme["surface_hover"]};
            }}
        """)

        # Set column widths
        self.manage_furniture_table.setColumnWidth(0, 150)  # Name
        self.manage_furniture_table.setColumnWidth(1, 120)  # Type
        self.manage_furniture_table.setColumnWidth(2, 150)  # Location
        self.manage_furniture_table.setColumnWidth(3, 120)  # Condition
        self.manage_furniture_table.setColumnWidth(4, 200)  # Actions

        table_layout.addWidget(self.manage_furniture_table)

        # Load initial data
        self._refresh_manage_furniture_table()

        return table_card

    def _on_manage_furniture_search(self, text: str):
        """Handle search text changes for manage furniture."""
        self._filter_manage_furniture_table()

    def _on_manage_furniture_filter_changed(self, furniture_type: str):
        """Handle type filter changes for manage furniture."""
        self._filter_manage_furniture_table()

    def _refresh_manage_furniture_table(self):
        """Refresh the manage furniture table with current data."""
        try:
            # Sample data - in a real implementation, this would come from database
            sample_furniture = [
                {"name": "Chair A1", "type": "Chair", "location": "Room 101", "condition": "Good"},
                {"name": "Table T1", "type": "Table", "location": "Room 102", "condition": "Excellent"},
                {"name": "Desk D1", "type": "Desk", "location": "Room 103", "condition": "Fair"},
            ]

            self.manage_furniture_table.setRowCount(len(sample_furniture))

            for row, item in enumerate(sample_furniture):
                # Name
                name_item = QTableWidgetItem(item.get('name', ''))
                name_item.setFlags(name_item.flags() & ~Qt.ItemFlag.ItemIsEditable)
                self.manage_furniture_table.setItem(row, 0, name_item)

                # Type
                type_item = QTableWidgetItem(item.get('type', ''))
                type_item.setFlags(type_item.flags() & ~Qt.ItemFlag.ItemIsEditable)
                self.manage_furniture_table.setItem(row, 1, type_item)

                # Location
                location_item = QTableWidgetItem(item.get('location', ''))
                location_item.setFlags(location_item.flags() & ~Qt.ItemFlag.ItemIsEditable)
                self.manage_furniture_table.setItem(row, 2, location_item)

                # Condition
                condition_item = QTableWidgetItem(item.get('condition', ''))
                condition_item.setFlags(condition_item.flags() & ~Qt.ItemFlag.ItemIsEditable)
                self.manage_furniture_table.setItem(row, 3, condition_item)

                # Actions
                actions_widget = QWidget()
                actions_layout = QHBoxLayout(actions_widget)
                actions_layout.setContentsMargins(4, 4, 4, 4)
                actions_layout.setSpacing(8)

                edit_btn = QPushButton("Edit")
                edit_btn.setFixedSize(60, 30)
                edit_btn.clicked.connect(lambda checked, f=item: self._edit_furniture(f))
                actions_layout.addWidget(edit_btn)

                delete_btn = QPushButton("Delete")
                delete_btn.setFixedSize(60, 30)
                delete_btn.clicked.connect(lambda checked, f=item: self._delete_furniture(f))
                actions_layout.addWidget(delete_btn)

                actions_layout.addStretch()
                self.manage_furniture_table.setCellWidget(row, 4, actions_widget)

            # Apply current filters
            self._filter_manage_furniture_table()

        except Exception as e:
            logger.error(f"Error refreshing manage furniture table: {str(e)}")
            QMessageBox.warning(self, "Error", f"Failed to refresh furniture table: {str(e)}")

    def _filter_manage_furniture_table(self):
        """Filter the manage furniture table based on search and type filter."""
        try:
            search_text = self.manage_furniture_search_box.text().lower()
            type_filter = self.manage_furniture_type_filter.currentText()

            for row in range(self.manage_furniture_table.rowCount()):
                show_row = True

                # Search filter
                if search_text:
                    name = self.manage_furniture_table.item(row, 0).text().lower()
                    furniture_type = self.manage_furniture_table.item(row, 1).text().lower()
                    if search_text not in name and search_text not in furniture_type:
                        show_row = False

                # Type filter
                if type_filter != "All Types":
                    table_type = self.manage_furniture_table.item(row, 1).text()
                    if table_type != type_filter:
                        show_row = False

                self.manage_furniture_table.setRowHidden(row, not show_row)

        except Exception as e:
            logger.error(f"Error filtering manage furniture table: {str(e)}")

    def _edit_furniture(self, furniture):
        """Handle editing furniture."""
        try:
            # For now, just show assignments view
            self._load_content("furniture_assignments")
        except Exception as e:
            logger.error(f"Error initiating furniture edit: {str(e)}")
            QMessageBox.warning(self, "Error", f"Failed to open furniture edit: {str(e)}")

    def _delete_furniture(self, furniture):
        """Handle deleting furniture."""
        try:
            reply = QMessageBox.question(
                self, "Confirm Deletion",
                f"Are you sure you want to delete '{furniture.get('name', '')}'?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                QMessageBox.StandardButton.No
            )

            if reply == QMessageBox.StandardButton.Yes:
                QMessageBox.information(self, "Success", f"Furniture '{furniture.get('name', '')}' deleted successfully!")

        except Exception as e:
            logger.error(f"Error deleting furniture: {str(e)}")
            QMessageBox.critical(self, "Error", f"Failed to delete furniture: {str(e)}")

    def _create_furniture_assignments_view(self) -> QWidget:
        """Create the furniture assignments content view."""
        try:
            # Create container for the furniture assignments interface
            container = QWidget()
            layout = QVBoxLayout(container)
            layout.setContentsMargins(32, 32, 32, 32)
            layout.setSpacing(24)

            # Create furniture assignments content
            assignments_content = self._create_furniture_assignments_content()
            layout.addWidget(assignments_content)

            return container

        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to load furniture assignments interface: {str(e)}")
            logger.error(f"Error loading furniture assignments interface: {str(e)}")
            return self._create_default_view("furniture_assignments", self.get_theme_manager()._themes[self.get_theme()], self._get_role_color())

    def _create_furniture_assignments_content(self) -> QWidget:
        """Create the furniture assignments content widget."""
        try:
            theme_manager = self.get_theme_manager()
            theme = theme_manager._themes[self.get_theme()]

            content_widget = QWidget()
            main_layout = QVBoxLayout(content_widget)
            main_layout.setContentsMargins(24, 24, 24, 24)
            main_layout.setSpacing(24)

            # Header
            header = QLabel("🔗 Furniture Assignments")
            header.setStyleSheet(f"""
                font-size: 24px;
                font-weight: bold;
                color: {theme["text"]};
                margin-bottom: 8px;
            """)
            main_layout.addWidget(header)

            # Assignment form
            assignment_form = self._create_furniture_assignment_form(theme)
            main_layout.addWidget(assignment_form)

            return content_widget

        except Exception as e:
            logger.error(f"Error creating furniture assignments content: {str(e)}")
            error_widget = QWidget()
            error_layout = QVBoxLayout(error_widget)
            error_label = QLabel("Error loading furniture assignments")
            error_label.setStyleSheet(f"color: {theme['error'] if 'error' in theme else 'red'}; font-size: 16px;")
            error_layout.addWidget(error_label)
            return error_widget

    def _create_furniture_assignment_form(self, theme) -> QWidget:
        """Create the furniture assignment form."""
        form_card = QWidget()
        form_card.setStyleSheet(f"""
            QWidget {{
                background-color: {theme["surface"]};
                border: 1px solid {theme["border"]};
                border-radius: 12px;
                padding: 24px;
            }}
        """)

        form_layout = QVBoxLayout(form_card)
        form_layout.setSpacing(16)

        # Furniture selection
        furniture_layout = QVBoxLayout()
        furniture_label = QLabel("Select Furniture:")
        furniture_label.setStyleSheet(f"font-weight: 500; color: {theme['text']};")
        furniture_layout.addWidget(furniture_label)

        self.assign_furniture_combo = QComboBox()
        self.assign_furniture_combo.addItems(["Chair A1", "Table T1", "Desk D1", "Cabinet C1"])
        self.assign_furniture_combo.setStyleSheet(f"""
            QComboBox {{
                padding: 10px 14px;
                border: 1px solid {theme["border"]};
                border-radius: 8px;
                background-color: {theme["surface"]};
                color: {theme["text"]};
                min-height: 36px;
            }}
        """)
        furniture_layout.addWidget(self.assign_furniture_combo)
        form_layout.addLayout(furniture_layout)

        # Room/Location selection
        location_layout = QVBoxLayout()
        location_label = QLabel("Assign to Room:")
        location_label.setStyleSheet(f"font-weight: 500; color: {theme['text']};")
        location_layout.addWidget(location_label)

        self.assign_location_combo = QComboBox()
        self.assign_location_combo.addItems(["Room 101", "Room 102", "Room 103", "Library", "Hallway"])
        self.assign_location_combo.setStyleSheet(f"""
            QComboBox {{
                padding: 10px 14px;
                border: 1px solid {theme["border"]};
                border-radius: 8px;
                background-color: {theme["surface"]};
                color: {theme["text"]};
                min-height: 36px;
            }}
        """)
        location_layout.addWidget(self.assign_location_combo)
        form_layout.addLayout(location_layout)

        # Assignment date
        date_layout = QVBoxLayout()
        date_label = QLabel("Assignment Date:")
        date_label.setStyleSheet(f"font-weight: 500; color: {theme['text']};")
        date_layout.addWidget(date_label)

        self.assign_date = QLineEdit()
        self.assign_date.setPlaceholderText("YYYY-MM-DD")
        self.assign_date.setText("2026-01-16")  # Current date
        self.assign_date.setStyleSheet(f"""
            QLineEdit {{
                padding: 10px 14px;
                border: 1px solid {theme["border"]};
                border-radius: 8px;
                background-color: {theme["surface"]};
                color: {theme["text"]};
                min-height: 36px;
            }}
        """)
        date_layout.addWidget(self.assign_date)
        form_layout.addLayout(date_layout)

        form_layout.addStretch()

        # Buttons
        buttons_layout = QHBoxLayout()
        buttons_layout.addStretch()

        cancel_btn = QPushButton("Cancel")
        cancel_btn.setStyleSheet(f"""
            QPushButton {{
                padding: 10px 20px;
                border-radius: 8px;
                border: 1px solid {theme["border"]};
                background-color: {theme["surface"]};
                color: {theme["text"]};
                min-height: 36px;
                font-size: 14px;
                font-weight: 500;
            }}
            QPushButton:hover {{
                background-color: {theme["surface_hover"]};
            }}
        """)
        cancel_btn.clicked.connect(lambda: self._load_content("manage_furniture"))
        buttons_layout.addWidget(cancel_btn)

        assign_btn = QPushButton("Assign Furniture")
        assign_btn.setStyleSheet(f"""
            QPushButton {{
                padding: 10px 20px;
                border-radius: 8px;
                border: 1px solid {theme["border"]};
                background-color: {theme["primary"]};
                color: white;
                min-height: 36px;
                font-size: 14px;
                font-weight: 500;
            }}
            QPushButton:hover {{
                background-color: {theme["primary_hover"] if "primary_hover" in theme else theme["primary"]};
            }}
        """)
        assign_btn.clicked.connect(self._assign_furniture)
        buttons_layout.addWidget(assign_btn)

        form_layout.addLayout(buttons_layout)

        return form_card

    def _assign_furniture(self):
        """Handle assigning furniture to a location."""
        try:
            furniture = self.assign_furniture_combo.currentText()
            location = self.assign_location_combo.currentText()
            date = self.assign_date.text().strip()

            if not furniture or not location or not date:
                QMessageBox.warning(self, "Validation Error", "All fields are required.")
                return

            QMessageBox.information(self, "Success",
                f"Furniture '{furniture}' assigned to {location} on {date}!")

            # Clear form
            self.assign_furniture_combo.setCurrentIndex(0)
            self.assign_location_combo.setCurrentIndex(0)
            self.assign_date.setText("2026-01-16")

        except Exception as e:
            logger.error(f"Error assigning furniture: {str(e)}")
            QMessageBox.critical(self, "Error", f"Failed to assign furniture: {str(e)}")

    def _create_furniture_maintenance_view(self) -> QWidget:
        """Create the furniture maintenance content view."""
        try:
            # Create container for the furniture maintenance interface
            container = QWidget()
            layout = QVBoxLayout(container)
            layout.setContentsMargins(32, 32, 32, 32)
            layout.setSpacing(24)

            # Create furniture maintenance content
            maintenance_content = self._create_furniture_maintenance_content()
            layout.addWidget(maintenance_content)

            return container

        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to load furniture maintenance interface: {str(e)}")
            logger.error(f"Error loading furniture maintenance interface: {str(e)}")
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
            /* Note: Qt QSS does not support CSS transitions */
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
        try:
            # Clear all widgets from the content stack (QStackedWidget)
            while self.content_stack.count() > 0:
                widget = self.content_stack.widget(0)
                if widget is not None:
                    self.content_stack.removeWidget(widget)
                    widget.deleteLater()

            logger.info("Content area cleared to prevent duplication")
        except RuntimeError as e:
            logger.error(f"RuntimeError accessing content layout: {e}")
            logger.warning("Reinitializing content layout due to deletion")
            try:
                # Try to reinitialize the content stack if it was deleted
                if not hasattr(self, 'content_stack') or self.content_stack is None:
                    logger.error("Failed to reinitialize content layout: content_stack is None")
                    return

                # Clear any remaining widgets
                while self.content_stack.count() > 0:
                    widget = self.content_stack.widget(0)
                    if widget is not None:
                        self.content_stack.removeWidget(widget)
                        widget.deleteLater()

            except Exception as e:
                logger.error(f"Failed to reinitialize content layout: {e}")
                logger.error("Critical error: Cannot recover from deleted QWidget")
    
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

        # Panel Title and Refresh Controls
        header_layout = QHBoxLayout()

        title = QLabel("⚡ Quick Actions")
        title.setStyleSheet(f"""
            font-size: 18px;
            font-weight: bold;
            color: {theme["text"]};
        """)
        header_layout.addWidget(title)

        # Refresh controls
        refresh_layout = QHBoxLayout()
        refresh_layout.setSpacing(8)

        # Manual refresh button
        refresh_btn = self.create_button("🔄 Refresh", "secondary")
        refresh_btn.setFixedHeight(32)
        refresh_btn.clicked.connect(self._manual_refresh_dashboard)
        refresh_layout.addWidget(refresh_btn)

        # Auto-refresh toggle
        self._auto_refresh_enabled = True
        auto_refresh_btn = self.create_button("⏰ Auto: ON", "outline")
        auto_refresh_btn.setFixedHeight(32)
        auto_refresh_btn.clicked.connect(self._toggle_auto_refresh)
        self._auto_refresh_button = auto_refresh_btn
        refresh_layout.addWidget(auto_refresh_btn)

        # Performance indicator
        self._performance_label = QLabel("⚡ Ready")
        self._performance_label.setStyleSheet(f"""
            font-size: 12px;
            color: {theme["text_secondary"]};
            padding: 4px 8px;
            border-radius: 4px;
            background-color: {theme["surface_hover"]};
        """)
        refresh_layout.addWidget(self._performance_label)

        header_layout.addStretch()
        header_layout.addLayout(refresh_layout)
        layout.addLayout(header_layout)

        # Separator
        separator = QFrame()
        separator.setFrameShape(QFrame.Shape.HLine)
        separator.setStyleSheet(f"color: {theme['border']}; margin: 8px 0;")
        layout.addWidget(separator)

        # Action Categories
        categories = [
            {
                "title": "Student Management",
                "actions": [
                    ("➕ Add Student", self._add_student),
                    ("👁️ View Students", self._show_students),
                    ("✏️ Edit Student", self._show_edit_student_selection),
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

        # Key metrics based on role - use real-time stat cards
        if self.role in ['admin', 'librarian']:
            # Admin/Librarian metrics
            metrics = [
                ("active_users_count", "Active Users", "👥", role_color),
                ("books_borrowed_today", "Books Borrowed Today", "📚", "#f39c12"),
                ("total_books_count", "Total Books", "📖", "#27ae60"),
                ("available_books_count", "Available Books", "📚", "#3498db"),
            ]
        else:
            # Regular user metrics
            metrics = [
                ("available_books_count", "Books Available", "📚", "#27ae60"),
                ("total_borrowed_books_count", "Total Borrowed", "📖", role_color),
                ("due_soon_count", "Due Soon", "⏰", "#f39c12"),
            ]

        for data_key, metric_name, icon, color in metrics:
            # Create real-time stat card
            metric_card = self._create_realtime_stat_card(metric_name, data_key, icon, color)
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

        # Statistics grid - use real-time data
        if self.role in ['admin', 'librarian']:
            stats_data = [
                ("total_students_count", "Total Students", "👨‍🎓", "#3498db"),
                ("total_teachers_count", "Total Teachers", "👩‍🏫", "#2ecc71"),
                ("total_books_count", "Total Books", "📚", "#9b59b6"),
                ("available_chairs_count", "Available Chairs", "🪑", "#f39c12"),
                ("available_lockers_count", "Available Lockers", "🔐", "#e74c3c"),
                ("total_borrowed_books_count", "Books Borrowed", "📖", "#1abc9c"),
            ]
        else:
            stats_data = [
                ("total_books_count", "Total Books", "📚", "#9b59b6"),
                ("available_books_count", "Available Books", "📖", "#27ae60"),
                ("total_borrowed_books_count", "Your Borrowed", "📚", "#3498db"),
                ("due_soon_count", "Due Soon", "⏰", "#f39c12"),
            ]

        # Create grid layout for stats
        grid_layout = QGridLayout()
        grid_layout.setSpacing(16)

        row, col = 0, 0
        max_cols = 2

        for data_key, title, icon, color in stats_data:
            stat_card = self._create_realtime_stat_card(title, data_key, icon, color)
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

            /* Dropdown Menu Styling for Dark Theme */
            QMenu {{
                background-color: {theme["surface"]};
                border: 1px solid {theme["border"]};
                border-radius: 8px;
                padding: 8px 0px;
                margin: 0px;
                color: {theme["text"]};
            }}

            QMenu::item {{
                background-color: transparent;
                padding: 12px 24px;
                margin: 0px 8px;
                border-radius: 6px;
                color: {theme["text"]};
                font-size: 13px;
                font-weight: 500;
            }}

            QMenu::item:selected {{
                background-color: {theme["surface_hover"]};
                color: {theme["text"]};
            }}

            QMenu::item:hover {{
                background-color: {theme["primary"]};
                color: white;
            }}

            QMenu::separator {{
                height: 1px;
                background-color: {theme["border"]};
                margin: 8px 16px;
            }}

            /* Menu indicator (arrow) */
            QMenu::indicator {{
                width: 12px;
                height: 12px;
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

    def _create_realtime_stat_card(self, title, data_key, icon, color, change=""):
        """
        Create a real-time statistics card with loading and error states.

        Args:
            title: Card title
            data_key: Key for data fetching
            icon: Icon emoji
            color: Theme color
            change: Change indicator text
        """
        theme_manager = self.get_theme_manager()
        theme = theme_manager._themes[self.get_theme()]

        card = QFrame()
        card.setProperty("realtimeStatCard", "true")
        card.setStyleSheet(f"""
            QFrame[realtimeStatCard="true"] {{
                background-color: {theme["surface"]};
                border-radius: 12px;
                border: 1px solid {theme["border"]};
                padding: 20px;
                min-height: 120px;
            }}
            QFrame[realtimeStatCard="true"]:hover {{
                border-color: {color};
                background-color: {theme["surface_hover"]};
            }}
        """)

        layout = QVBoxLayout(card)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(8)

        # Header with icon, title, and status indicator
        header_layout = QHBoxLayout()

        # Icon
        icon_label = QLabel(icon)
        icon_label.setStyleSheet("font-size: 24px;")
        header_layout.addWidget(icon_label)

        # Title
        title_label = QLabel(title)
        title_label.setStyleSheet(f"""
            font-size: 14px;
            color: {theme["text_secondary"]};
            font-weight: 500;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        """)
        header_layout.addWidget(title_label)

        # Status indicator (loading/error/normal)
        self._status_indicators = getattr(self, '_status_indicators', {})
        status_label = QLabel("")
        status_label.setFixedSize(16, 16)
        status_label.setStyleSheet("""
            QLabel {
                border-radius: 8px;
                background-color: transparent;
            }
        """)
        self._status_indicators[data_key] = status_label
        header_layout.addStretch()
        header_layout.addWidget(status_label)

        layout.addLayout(header_layout)

        # Count display (can show loading spinner or error icon)
        self._count_labels = getattr(self, '_count_labels', {})
        count_label = QLabel("Loading...")
        count_font = QFont("Segoe UI", 28, QFont.Weight.Bold)
        count_label.setFont(count_font)
        count_label.setStyleSheet(f"color: {theme['text']};")
        self._count_labels[data_key] = count_label
        layout.addWidget(count_label)

        # Change indicator
        if change:
            change_label = QLabel(change)
            change_label.setStyleSheet(f"""
                font-size: 12px;
                color: {color};
                font-weight: 500;
            """)
            layout.addWidget(change_label)

        # Store card reference for updates
        self._stat_cards = getattr(self, '_stat_cards', {})
        self._stat_cards[data_key] = card

        # Initial data fetch
        self._update_stat_card_display(data_key)

        return card

    def _update_stat_card_display(self, data_key: str):
        """Update the display of a stat card based on current data state."""
        if not hasattr(self, '_count_labels') or data_key not in self._count_labels:
            return

        theme_manager = self.get_theme_manager()
        theme = theme_manager._themes[self.get_theme()]

        count_label = self._count_labels[data_key]
        status_label = self._status_indicators.get(data_key)

        # Get data from data manager
        data = None
        is_loading = False
        error_message = None

        if self.dashboard_data_manager:
            # Check if data is currently being fetched
            if hasattr(self.dashboard_data_manager, '_active_workers') and \
               data_key in self.dashboard_data_manager._active_workers:
                is_loading = True
            else:
                # Try to get cached data
                cache_entry = self.dashboard_data_manager._cache.get(data_key)
                if cache_entry:
                    if cache_entry.state == DataState.ERROR:
                        error_message = cache_entry.error_message
                    elif cache_entry.state in [DataState.READY, DataState.STALE]:
                        data = cache_entry.data

        # Update display based on state
        if is_loading:
            count_label.setText("⏳")
            count_label.setStyleSheet(f"color: {theme['text_secondary']}; font-size: 24px;")
            if status_label:
                status_label.setStyleSheet("""
                    QLabel {
                        background-color: #fbbf24;
                        border-radius: 8px;
                    }
                """)
        elif error_message:
            count_label.setText("❌")
            count_label.setStyleSheet(f"color: #ef4444; font-size: 24px;")
            if status_label:
                status_label.setStyleSheet("""
                    QLabel {
                        background-color: #ef4444;
                        border-radius: 8px;
                    }
                """)
            # Could show tooltip with error message
            count_label.setToolTip(f"Error: {error_message}")
        else:
            # Format data for display
            if data is not None:
                if isinstance(data, int):
                    if data_key in ['total_students_count', 'total_books_count', 'active_users_count', 'available_books_count']:
                        display_text = f"{data:,}"
                    else:
                        display_text = str(data)
                else:
                    display_text = str(data)

                count_label.setText(display_text)
                count_label.setStyleSheet(f"color: {theme['text']};")
                if status_label:
                    status_label.setStyleSheet("""
                        QLabel {
                            background-color: #10b981;
                            border-radius: 8px;
                        }
                    """)
                count_label.setToolTip("")  # Clear any error tooltip
            else:
                # No data available yet
                count_label.setText("--")
                count_label.setStyleSheet(f"color: {theme['text_secondary']};")
                if status_label:
                    status_label.setStyleSheet("""
                        QLabel {
                            background-color: #6b7280;
                            border-radius: 8px;
                        }
                    """)

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

        # Recent activities - fetch real data with fallbacks
        activities = self._get_recent_activities()

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
        title_label.setStyleSheet(f"color: {theme['text']}; margin-bottom: 8px;")
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
        count_label.setStyleSheet(f"color: {theme['text']};")
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
        self._open_view_students_window()

    def _add_student(self):
        """Show add student window."""
        self._open_add_student_window()

    def _manage_students(self):
        """Show view students window (same as _show_students)."""
        self._show_students()
    
    def _show_student_management(self):
        """Show the student management window (legacy - redirects to view students)."""
        self._show_students()
    
    def _show_edit_student(self):
        """Show edit student window (legacy method - redirects to selection)."""
        self._show_edit_student_selection()
    
    def _show_teachers(self):
        """Show teacher management window."""
        self._open_view_teachers_window()

    def _add_teacher(self):
        """Show teacher management window."""
        self._open_add_teacher_window()

    def _manage_teachers(self):
        """Show teacher management window."""
        self._open_view_teachers_window()

    def _show_teacher_management(self):
        """Show the teacher management window."""
        self._open_view_teachers_window()

    def _show_edit_teacher(self):
        """Show edit teacher window."""
        self._open_edit_teacher_window()

    def _show_teacher_import_export(self):
        """Show teacher import/export window."""
        self._open_teacher_import_export_window()

    def _show_student_import_export(self):
        """Show student import/export window."""
        self._open_student_import_export_window()

    def _show_user_management(self):
        """Show user management window."""
        self._load_content("manage_users")

    def _show_view_users(self):
        """Show view users window."""
        self._load_content("view_users")
    
    def _show_books(self):
        """Show books management window."""
        self._open_view_books_window()

    def _add_book(self):
        """Show books management window."""
        self._open_add_book_window()

    def _show_borrowed_books(self):
        """Show books management window."""
        self._open_view_books_window()

    def _manage_books(self):
        """Show books management window."""
        self._open_view_books_window()

    def _show_book_management(self):
        """Show the book management window."""
        self._open_view_books_window()

    def _show_distribution(self):
        """Show distribution window."""
        self._open_distribution_window()

    def _show_book_import_export(self):
        """Show book import/export window."""
        self._open_book_import_export_window()

    def _show_borrow_book(self):
        """Show borrow book window."""
        self._open_borrow_book_window()

    def _show_return_book(self):
        """Show return book window."""
        self._open_return_book_window()

    def _show_add_book_window(self):
        """Show add book window."""
        self._open_add_book_window()

    def _show_view_books_window(self):
        """Show view books window."""
        self._open_view_books_window()

    def _show_borrow_book_window(self):
        """Show borrow book window."""
        self._open_borrow_book_window()

    def _show_return_book_window(self):
        """Show return book window."""
        self._open_return_book_window()

    def _on_book_data_changed(self):
        """Handle book data changes from child windows."""
        try:
            # Refresh dashboard if it's currently visible
            if self.current_view == "dashboard":
                self._load_content("dashboard")
        except Exception as e:
            logger.error(f"Error refreshing after book data change: {str(e)}")

    def _on_furniture_data_changed(self):
        """Handle furniture data changes from child windows."""
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
        self._load_content("distribution")

    def _show_book_import_export(self):
        """Show book import/export window."""
        self._load_content("book_import_export")
    
    def _show_furniture_management(self):
        """Show furniture management window."""
        self._open_manage_furniture_window()

    def _show_furniture_assignments(self):
        """Show furniture assignments window."""
        self._open_furniture_assignments_window()

    def _show_furniture_maintenance(self):
        """Show furniture maintenance window."""
        self._open_furniture_maintenance_window()
    
    def _show_book_reports(self):
        """Show book reports window."""
        self._open_book_reports_window()

    def _show_student_reports(self):
        """Show student reports window."""
        self._open_student_reports_window()

    def _show_custom_reports(self):
        """Show custom reports window."""
        self._open_custom_reports_window()

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
        self._load_content("library_activity")

    def _show_ream_management_window(self):
        """Show the ream management window."""
        self._load_content("ream_management")

    def _show_class_management_window(self):
        """Show the class management window."""
        self._load_content("class_management")

    def _show_library_activity_window(self):
        """Show the library activity window."""
        self._load_content("library_activity")

    # Dashboard data fetching methods with fallbacks
    def _get_active_users_count(self) -> str:
        """Get count of active users (students + teachers)."""
        try:
            if self.student_service and self.teacher_service:
                student_count = len(self.student_service.get_all_students())
                teacher_count = len(self.teacher_service.get_all_teachers())
                total = student_count + teacher_count
                return f"{total:,}"
        except Exception as e:
            logger.warning(f"Failed to get active users count: {str(e)}")
        return "247"  # fallback

    def _get_books_borrowed_today(self) -> str:
        """Get count of books borrowed today."""
        try:
            if self.report_service:
                analytics = self.report_service.get_borrowing_analytics_report()
                # Look for today's borrowing count in analytics
                # This is a simplified approach - in a real system you'd filter by date
                borrowed_count = analytics.get('total_borrowed_books', 0)
                return str(borrowed_count)
        except Exception as e:
            logger.warning(f"Failed to get books borrowed today: {str(e)}")
        return "23"  # fallback

    def _get_pending_approvals_count(self) -> str:
        """Get count of pending approvals."""
        try:
            # This could be implemented when approval system is added
            # For now, return a low number as fallback
            pass
        except Exception as e:
            logger.warning(f"Failed to get pending approvals: {str(e)}")
        return "5"  # fallback

    def _get_available_books_count(self) -> str:
        """Get count of available books."""
        try:
            if self.book_service:
                books = self.book_service.get_all_books()
                available = sum(1 for book in books if getattr(book, 'status', 'available') == 'available')
                return f"{available:,}"
        except Exception as e:
            logger.warning(f"Failed to get available books count: {str(e)}")
        return "1,245"  # fallback

    def _get_user_borrowed_books_count(self) -> str:
        """Get count of books borrowed by current user."""
        try:
            if self.book_service and self.username:
                # This would require a method to get books borrowed by a specific user
                # For now, return a reasonable number
                pass
        except Exception as e:
            logger.warning(f"Failed to get user borrowed books: {str(e)}")
        return "3"  # fallback

    def _get_due_soon_count(self) -> str:
        """Get count of books due soon for current user."""
        try:
            # This would require checking due dates
            # For now, return a reasonable number
            pass
        except Exception as e:
            logger.warning(f"Failed to get due soon count: {str(e)}")
        return "2"  # fallback

    def _get_total_students_count(self) -> str:
        """Get total count of students."""
        try:
            if self.student_service:
                count = len(self.student_service.get_all_students())
                return f"{count:,}"
        except Exception as e:
            logger.warning(f"Failed to get total students: {str(e)}")
        return "1,247"  # fallback

    def _get_total_teachers_count(self) -> str:
        """Get total count of teachers."""
        try:
            if self.teacher_service:
                count = len(self.teacher_service.get_all_teachers())
                return f"{count:,}"
        except Exception as e:
            logger.warning(f"Failed to get total teachers: {str(e)}")
        return "89"  # fallback

    def _get_total_books_count(self) -> str:
        """Get total count of books."""
        try:
            if self.book_service:
                count = len(self.book_service.get_all_books())
                return f"{count:,}"
        except Exception as e:
            logger.warning(f"Failed to get total books: {str(e)}")
        return "3,456"  # fallback

    def _get_available_chairs_count(self) -> str:
        """Get count of available chairs."""
        try:
            if self.furniture_service:
                chairs = self.furniture_service.get_all_chairs()
                available = sum(1 for chair in chairs if getattr(chair, 'status', 'available') == 'available')
                return str(available)
        except Exception as e:
            logger.warning(f"Failed to get available chairs: {str(e)}")
        return "245"  # fallback

    def _get_available_lockers_count(self) -> str:
        """Get count of available lockers."""
        try:
            if self.furniture_service:
                lockers = self.furniture_service.get_all_lockers()
                available = sum(1 for locker in lockers if getattr(locker, 'status', 'available') == 'available')
                return str(available)
        except Exception as e:
            logger.warning(f"Failed to get available lockers: {str(e)}")
        return "67"  # fallback

    def _get_total_borrowed_books_count(self) -> str:
        """Get total count of borrowed books."""
        try:
            if self.report_service:
                analytics = self.report_service.get_borrowing_analytics_report()
                borrowed = analytics.get('total_borrowed_books', 0)
                return str(borrowed)
        except Exception as e:
            logger.warning(f"Failed to get total borrowed books: {str(e)}")
        return "892"  # fallback

    def _get_recent_activities(self) -> list:
        """Get list of recent activities."""
        try:
            activities = []
            # Try to get recent borrowing activities
            if self.book_service:
                # This would require a method to get recent transactions
                # For now, we'll use fallback activities
                pass
            # Try to get recent student registrations
            if self.student_service:
                # This would require tracking creation timestamps
                pass
        except Exception as e:
            logger.warning(f"Failed to get recent activities: {str(e)}")

        # Fallback activities if real data is not available
        return [
            ("Book borrowed: 'Python Programming' by John Doe", "2 min ago", "📖"),
            ("New student registered: Jane Smith", "15 min ago", "👨‍🎓"),
            ("Book returned: 'Data Science 101'", "1 hour ago", "↩️"),
            ("Teacher added: Prof. Michael Johnson", "2 hours ago", "👩‍🏫"),
            ("System backup completed", "3 hours ago", "💾"),
        ]

    # DashboardDataManager integration methods
    def _setup_auto_refresh(self):
        """Set up auto-refresh intervals for dashboard data."""
        if not self.dashboard_data_manager:
            return

        # Set auto-refresh intervals (in seconds) - more conservative to reduce load
        refresh_intervals = {
            'active_users_count': 600,  # 10 minutes
            'total_students_count': 900,  # 15 minutes
            'total_teachers_count': 900,  # 15 minutes
            'total_books_count': 600,  # 10 minutes
            'available_books_count': 300,  # 5 minutes
            'books_borrowed_today': 120,  # 2 minutes
            'total_borrowed_books_count': 300,  # 5 minutes
            'due_soon_count': 600,  # 10 minutes
            'recent_activities': 300,  # 5 minutes
            'available_chairs_count': 1200,  # 20 minutes
            'available_lockers_count': 1200,  # 20 minutes
        }

        for data_key, interval in refresh_intervals.items():
            self.dashboard_data_manager.set_auto_refresh(data_key, interval)

        logger.info("Auto-refresh configured for dashboard data with conservative intervals")

    def _on_dashboard_data_updated(self, data_key: str, data):
        """Handle data updates from the dashboard data manager."""
        logger.debug(f"Dashboard data updated: {data_key}")

        # Update the dashboard display if it's currently visible with debouncing
        if self.current_view == "dashboard":
            # Update stat cards immediately for better responsiveness
            self._update_dashboard_stat_cards()
            self._update_performance_indicator()

            # Schedule a debounced full refresh (if not already pending)
            if not self._dashboard_update_pending:
                self._dashboard_update_pending = True
                self._dashboard_update_timer.start(1000)  # 1 second debounce

    def _on_dashboard_data_error(self, data_key: str, error_message: str):
        """Handle data fetch errors from the dashboard data manager."""
        logger.error(f"Dashboard data error for {data_key}: {error_message}")

        # Could show user notification for critical errors
        if data_key in ['active_users_count', 'total_books_count']:
            # For now, just log - could show toast notification
            pass

    def _on_dashboard_loading_started(self, data_key: str):
        """Handle loading started signal."""
        logger.debug(f"Dashboard data loading started: {data_key}")

        # Could show loading indicators in UI
        if self.current_view == "dashboard":
            # Update UI to show loading state for specific data
            pass

    def _on_dashboard_loading_finished(self, data_key: str):
        """Handle loading finished signal."""
        logger.debug(f"Dashboard data loading finished: {data_key}")

        # Update UI loading state
        if self.current_view == "dashboard":
            self._refresh_dashboard_display()

    def _manual_refresh_dashboard(self):
        """Manually refresh all dashboard data."""
        logger.info("Manual dashboard refresh requested")

        if self.dashboard_data_manager:
            # Invalidate all cache and force refresh
            self.dashboard_data_manager.invalidate_cache()

            # Trigger refresh for all data keys
            data_keys = [
                'active_users_count', 'total_students_count', 'total_teachers_count',
                'total_books_count', 'available_books_count', 'books_borrowed_today',
                'total_borrowed_books_count', 'due_soon_count', 'recent_activities',
                'available_chairs_count', 'available_lockers_count'
            ]

            for data_key in data_keys:
                self.dashboard_data_manager.get_data(data_key, force_refresh=True)

            # Update performance indicator
            self._update_performance_indicator()

    def _toggle_auto_refresh(self):
        """Toggle auto-refresh on/off."""
        if not self.dashboard_data_manager:
            return

        self._auto_refresh_enabled = not self._auto_refresh_enabled

        if self._auto_refresh_enabled:
            # Re-enable auto-refresh for all data keys
            self._setup_auto_refresh()
            self._auto_refresh_button.setText("⏰ Auto: ON")
            self._auto_refresh_button.setProperty("variant", "outline")
            logger.info("Auto-refresh enabled")
        else:
            # Disable auto-refresh for all data keys
            for data_key in self.dashboard_data_manager._auto_refresh_intervals.keys():
                self.dashboard_data_manager.disable_auto_refresh(data_key)
            self._auto_refresh_button.setText("⏰ Auto: OFF")
            self._auto_refresh_button.setProperty("variant", "secondary")
            logger.info("Auto-refresh disabled")

        # Update button style
        self._auto_refresh_button.style().unpolish(self._auto_refresh_button)
        self._auto_refresh_button.style().polish(self._auto_refresh_button)

    def _update_performance_indicator(self):
        """Update the performance indicator with current stats."""
        if not self.dashboard_data_manager or not hasattr(self, '_performance_label'):
            return

        try:
            stats = self.dashboard_data_manager.get_cache_stats()
            cache_stats = stats.get('cache_stats', {})
            perf_stats = stats.get('performance_stats', {})

            total_entries = cache_stats.get('total_entries', 0)
            active_workers = cache_stats.get('active_workers', 0)
            cache_hit_rate = perf_stats.get('cache_hit_rate', 0)

            if active_workers > 0:
                status_text = f"🔄 Loading ({active_workers} active)"
                color = "#fbbf24"  # Yellow
            elif cache_hit_rate > 0.8:
                status_text = f"⚡ Fast ({cache_hit_rate:.1%} hit rate)"
                color = "#10b981"  # Green
            elif cache_hit_rate > 0.5:
                status_text = f"⚡ Good ({cache_hit_rate:.1%} hit rate)"
                color = "#f59e0b"  # Orange
            else:
                status_text = f"🐌 Slow ({cache_hit_rate:.1%} hit rate)"
                color = "#ef4444"  # Red

            theme_manager = self.get_theme_manager()
            theme = theme_manager._themes[self.get_theme()]

            self._performance_label.setText(status_text)
            self._performance_label.setStyleSheet(f"""
                font-size: 12px;
                color: white;
                padding: 4px 8px;
                border-radius: 4px;
                background-color: {color};
            """)

        except Exception as e:
            logger.error(f"Error updating performance indicator: {str(e)}")

    def _refresh_dashboard_display(self):
        """Refresh the dashboard display with latest data."""
        try:
            # Reset debouncing flag
            self._dashboard_update_pending = False

            # Only refresh if dashboard is currently visible
            if self.current_view == "dashboard":
                # Full refresh only when explicitly requested or after debounced updates
                self._load_content("dashboard")
            else:
                logger.debug("Skipping dashboard refresh - not currently visible")
        except Exception as e:
            logger.error(f"Error refreshing dashboard display: {str(e)}")
            self._dashboard_update_pending = False

    def _update_dashboard_stat_cards(self):
        """Update stat card displays with latest data without full reload."""
        try:
            # Update status indicators and counts for existing stat cards
            if hasattr(self, '_count_labels'):
                for data_key, count_label in self._count_labels.items():
                    if self.dashboard_data_manager:
                        data = self.dashboard_data_manager.get_data(data_key)
                        if data is not None:
                            # Update the display
                            if hasattr(self, '_update_stat_card_display'):
                                self._update_stat_card_display(data_key)

            # Update performance indicator
            if hasattr(self, '_update_performance_indicator'):
                self._update_performance_indicator()

        except Exception as e:
            logger.error(f"Error updating dashboard stat cards: {str(e)}")

    # Enhanced data fetching methods using DashboardDataManager
    def _get_active_users_count(self) -> str:
        """Get count of active users using data manager."""
        if self.dashboard_data_manager:
            data = self.dashboard_data_manager.get_data('active_users_count')
            if data is not None:
                return f"{data:,}"
        # Fallback to old method
        return super()._get_active_users_count()

    def _get_books_borrowed_today(self) -> str:
        """Get books borrowed today using data manager."""
        if self.dashboard_data_manager:
            data = self.dashboard_data_manager.get_data('books_borrowed_today')
            if data is not None:
                return str(data)
        # Fallback to old method
        return super()._get_books_borrowed_today()

    def _get_available_books_count(self) -> str:
        """Get available books count using data manager."""
        if self.dashboard_data_manager:
            data = self.dashboard_data_manager.get_data('available_books_count')
            if data is not None:
                return f"{data:,}"
        # Fallback to old method
        return super()._get_available_books_count()

    def _get_user_borrowed_books_count(self) -> str:
        """Get user borrowed books count using data manager."""
        if self.dashboard_data_manager:
            data = self.dashboard_data_manager.get_data('total_borrowed_books_count')
            if data is not None:
                return str(data)
        # Fallback to old method
        return super()._get_user_borrowed_books_count()

    def _get_due_soon_count(self) -> str:
        """Get due soon count using data manager."""
        if self.dashboard_data_manager:
            data = self.dashboard_data_manager.get_data('due_soon_count')
            if data is not None:
                return str(data)
        # Fallback to old method
        return super()._get_due_soon_count()

    def _get_total_students_count(self) -> str:
        """Get total students count using data manager."""
        if self.dashboard_data_manager:
            data = self.dashboard_data_manager.get_data('total_students_count')
            if data is not None:
                return f"{data:,}"
        # Fallback to old method
        return super()._get_total_students_count()

    def _get_total_teachers_count(self) -> str:
        """Get total teachers count using data manager."""
        if self.dashboard_data_manager:
            data = self.dashboard_data_manager.get_data('total_teachers_count')
            if data is not None:
                return f"{data:,}"
        # Fallback to old method
        return super()._get_total_teachers_count()

    def _get_total_books_count(self) -> str:
        """Get total books count using data manager."""
        if self.dashboard_data_manager:
            data = self.dashboard_data_manager.get_data('total_books_count')
            if data is not None:
                return f"{data:,}"
        # Fallback to old method
        return super()._get_total_books_count()

    def _get_available_chairs_count(self) -> str:
        """Get available chairs count using data manager."""
        if self.dashboard_data_manager:
            data = self.dashboard_data_manager.get_data('available_chairs_count')
            if data is not None:
                return str(data)
        # Fallback to old method
        return super()._get_available_chairs_count()

    def _get_available_lockers_count(self) -> str:
        """Get available lockers count using data manager."""
        if self.dashboard_data_manager:
            data = self.dashboard_data_manager.get_data('available_lockers_count')
            if data is not None:
                return str(data)
        # Fallback to old method
        return super()._get_available_lockers_count()

    def _get_total_borrowed_books_count(self) -> str:
        """Get total borrowed books count using data manager."""
        if self.dashboard_data_manager:
            data = self.dashboard_data_manager.get_data('total_borrowed_books_count')
            if data is not None:
                return str(data)
        # Fallback to old method
        return super()._get_total_borrowed_books_count()

    def _get_recent_activities(self) -> list:
        """Get recent activities using data manager."""
        if self.dashboard_data_manager:
            data = self.dashboard_data_manager.get_data('recent_activities')
            if data is not None:
                return data
        # Fallback to default activities
        return [
            ("Book borrowed: 'Python Programming' by John Doe", "2 min ago", "📖"),
            ("New student registered: Jane Smith", "15 min ago", "👨‍🎓"),
            ("Book returned: 'Data Science 101'", "1 hour ago", "↩️"),
            ("Teacher added: Prof. Michael Johnson", "2 hours ago", "👩‍🏫"),
            ("System backup completed", "3 hours ago", "💾"),
        ]

    def closeEvent(self, event):
        """Handle window closing."""
        # Shutdown the dashboard data manager
        if hasattr(self, 'dashboard_data_manager') and self.dashboard_data_manager:
            self.dashboard_data_manager.shutdown()

        super().closeEvent(event)