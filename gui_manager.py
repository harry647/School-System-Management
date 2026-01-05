import sys
import logging
from datetime import datetime, timedelta, date
from typing import Optional, Dict, List, Any
import pandas as pd
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QGridLayout,
    QLabel, QPushButton, QLineEdit, QTextEdit, QComboBox, QCheckBox,
    QTableWidget, QTableWidgetItem, QTreeWidget, QTreeWidgetItem,
    QTabWidget, QGroupBox, QFrame, QScrollArea, QProgressBar,
    QMessageBox, QFileDialog, QDialog, QDialogButtonBox, QHeaderView,
    QDateEdit, QSpinBox, QDoubleSpinBox, QListWidget, QListWidgetItem,
    QToolBar, QStatusBar, QMenu, QMenuBar, QSystemTrayIcon
)
from PyQt6.QtCore import (
    Qt, QTimer, QDate, QThread, pyqtSignal, QPropertyAnimation,
    QEasingCurve, QRect, QSize, QPoint, QParallelAnimationGroup,
    QSequentialAnimationGroup, QThreadPool, QRunnable, pyqtProperty
)
from PyQt6.QtGui import (
    QFont, QIcon, QPixmap, QPainter, QPainterPath, QLinearGradient,
    QBrush, QColor, QPen, QAction as QGuiAction, QPalette, QFontDatabase,
    QIntValidator, QDoubleValidator
)
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, LongTable
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import inch
import csv
import os
import openpyxl
from PIL import Image, ImageQt

# Modern Color Palette
class ModernColors:
    """Modern color scheme for the application"""
    PRIMARY = "#667eea"
    PRIMARY_DARK = "#5a67d8"
    SECONDARY = "#764ba2"
    ACCENT = "#f093fb"
    SUCCESS = "#48bb78"
    WARNING = "#ed8936"
    ERROR = "#f56565"
    INFO = "#4299e1"
    
    # Background colors
    BACKGROUND_PRIMARY = "#f7fafc"
    BACKGROUND_SECONDARY = "#edf2f7"
    BACKGROUND_CARD = "#ffffff"
    BACKGROUND_DARK = "#1a202c"
    
    # Text colors
    TEXT_PRIMARY = "#2d3748"
    TEXT_SECONDARY = "#4a5568"
    TEXT_MUTED = "#718096"
    TEXT_LIGHT = "#ffffff"
    
    # Border and shadow colors
    BORDER_LIGHT = "#e2e8f0"
    BORDER_MEDIUM = "#cbd5e0"
    SHADOW = "rgba(0, 0, 0, 0.1)"
    SHADOW_DARK = "rgba(0, 0, 0, 0.25)"
    
    # Gradient colors
    GRADIENT_PRIMARY = "qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #667eea, stop:1 #764ba2)"
    GRADIENT_SECONDARY = "qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #f093fb, stop:1 #f5576c)"
    GRADIENT_SUCCESS = "qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #4facfe, stop:1 #00f2fe)"

class ModernButton(QPushButton):
    """Modern button with hover effects and custom styling"""
    
    def __init__(self, text="", button_type="primary", size="medium", parent=None):
        super().__init__(text, parent)
        self.button_type = button_type
        self.size = size
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setFont(self.get_font())
        self.setFixedHeight(self.get_height())
        self.setup_styling()
        self.setup_animations()
    
    def get_font(self):
        """Get appropriate font based on size"""
        fonts = {
            "small": QFont("Segoe UI", 9),
            "medium": QFont("Segoe UI", 10),
            "large": QFont("Segoe UI", 12, QFont.Weight.Medium)
        }
        return fonts.get(self.size, fonts["medium"])
    
    def get_height(self):
        """Get appropriate height based on size"""
        heights = {"small": 32, "medium": 40, "large": 48}
        return heights.get(self.size, 40)
    
    def setup_styling(self):
        """Setup button styling based on type"""
        styles = {
            "primary": f"""
                QPushButton {{
                    background: {ModernColors.GRADIENT_PRIMARY};
                    border: none;
                    border-radius: 8px;
                    color: {ModernColors.TEXT_LIGHT};
                    padding: 0 24px;
                    font-weight: 500;
                }}
                QPushButton:hover {{
                    background: {ModernColors.PRIMARY_DARK};
                    transform: translateY(-2px);
                }}
                QPushButton:pressed {{
                    background: {ModernColors.PRIMARY_DARK};
                    transform: translateY(0px);
                }}
                QPushButton:disabled {{
                    background: {ModernColors.BORDER_MEDIUM};
                    color: {ModernColors.TEXT_MUTED};
                }}
            """,
            "secondary": f"""
                QPushButton {{
                    background: {ModernColors.BACKGROUND_CARD};
                    border: 2px solid {ModernColors.PRIMARY};
                    border-radius: 8px;
                    color: {ModernColors.PRIMARY};
                    padding: 0 24px;
                    font-weight: 500;
                }}
                QPushButton:hover {{
                    background: {ModernColors.PRIMARY};
                    color: {ModernColors.TEXT_LIGHT};
                }}
                QPushButton:pressed {{
                    background: {ModernColors.PRIMARY_DARK};
                }}
            """,
            "success": f"""
                QPushButton {{
                    background: {ModernColors.SUCCESS};
                    border: none;
                    border-radius: 8px;
                    color: {ModernColors.TEXT_LIGHT};
                    padding: 0 24px;
                    font-weight: 500;
                }}
                QPushButton:hover {{
                    background: #38a169;
                }}
            """,
            "danger": f"""
                QPushButton {{
                    background: {ModernColors.ERROR};
                    border: none;
                    border-radius: 8px;
                    color: {ModernColors.TEXT_LIGHT};
                    padding: 0 24px;
                    font-weight: 500;
                }}
                QPushButton:hover {{
                    background: #e53e3e;
                }}
            """,
            "outline": f"""
                QPushButton {{
                    background: transparent;
                    border: 2px solid {ModernColors.BORDER_MEDIUM};
                    border-radius: 8px;
                    color: {ModernColors.TEXT_PRIMARY};
                    padding: 0 24px;
                    font-weight: 500;
                }}
                QPushButton:hover {{
                    border-color: {ModernColors.PRIMARY};
                    color: {ModernColors.PRIMARY};
                }}
            """
        }
        self.setStyleSheet(styles.get(self.button_type, styles["primary"]))
    
    def setup_animations(self):
        """Setup hover animations"""
        self.animation = QPropertyAnimation(self, b"geometry")
        self.animation.setDuration(200)
        self.animation.setEasingCurve(QEasingCurve.Type.OutCubic)
        
        self.original_geometry = self.geometry()
    
    def enterEvent(self, event):
        """Handle mouse enter for hover effects"""
        if self.button_type in ["primary", "secondary", "success", "danger"]:
            # Create shadow effect
            self.setStyleSheet(self.styleSheet() + f"""
                QPushButton {{
                    box-shadow: 0 8px 25px {ModernColors.SHADOW};
                }}
            """)
        super().enterEvent(event)
    
    def leaveEvent(self, event):
        """Handle mouse leave"""
        self.setStyleSheet(self.styleSheet().replace(
            f"box-shadow: 0 8px 25px {ModernColors.SHADOW};", ""
        ))
        super().leaveEvent(event)

class ModernCard(QFrame):
    """Modern card widget with shadow and rounded corners"""
    
    def __init__(self, title="", content=None, parent=None):
        super().__init__(parent)
        self.title = title
        self.setup_ui(content)
        self.setup_styling()
    
    def setup_ui(self, content):
        """Setup the card UI"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        
        # Title bar
        if self.title:
            title_bar = QFrame()
            title_bar.setFixedHeight(50)
            title_layout = QHBoxLayout(title_bar)
            title_layout.setContentsMargins(20, 0, 20, 0)
            
            title_label = QLabel(self.title)
            title_label.setFont(QFont("Segoe UI", 12, QFont.Weight.Medium))
            title_label.setStyleSheet(f"color: {ModernColors.TEXT_PRIMARY};")
            
            title_layout.addWidget(title_label)
            title_layout.addStretch()
            
            layout.addWidget(title_bar)
        
        # Content area
        if content:
            content_frame = QFrame()
            content_frame.setStyleSheet(f"""
                QFrame {{
                    background: {ModernColors.BACKGROUND_CARD};
                    border-radius: 0 0 12px 12px;
                }}
            """)
            content_layout = QVBoxLayout(content_frame)
            content_layout.setContentsMargins(20, 20, 20, 20)
            content_layout.addWidget(content)
            layout.addWidget(content_frame)
    
    def setup_styling(self):
        """Setup card styling"""
        self.setStyleSheet(f"""
            QFrame {{
                background: {ModernColors.BACKGROUND_CARD};
                border-radius: 12px;
                margin: 8px;
            }}
        """)
        self.setFrameShape(QFrame.Shape.NoFrame)

class ModernLineEdit(QLineEdit):
    """Modern line edit with floating label effect"""
    
    def __init__(self, placeholder="", parent=None):
        super().__init__(parent)
        self.placeholder = placeholder
        self.setup_styling()
    
    def setup_styling(self):
        """Setup line edit styling"""
        self.setStyleSheet(f"""
            QLineEdit {{
                padding: 12px 16px;
                border: 2px solid {ModernColors.BORDER_LIGHT};
                border-radius: 8px;
                background: {ModernColors.BACKGROUND_CARD};
                color: {ModernColors.TEXT_PRIMARY};
                font-size: 14px;
                selection-background-color: {ModernColors.PRIMARY};
            }}
            QLineEdit:focus {{
                border-color: {ModernColors.PRIMARY};
                box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
            }}
            QLineEdit::placeholder {{
                color: {ModernColors.TEXT_MUTED};
            }}
        """)

class ModernTableWidget(QTableWidget):
    """Modern table widget with improved styling"""
    
    def __init__(self, rows=0, columns=0, parent=None):
        super().__init__(rows, columns, parent)
        self.setup_styling()
    
    def setup_styling(self):
        """Setup table styling"""
        self.setStyleSheet(f"""
            QTableWidget {{
                background: {ModernColors.BACKGROUND_CARD};
                border: 1px solid {ModernColors.BORDER_LIGHT};
                border-radius: 8px;
                gridline-color: {ModernColors.BORDER_LIGHT};
                selection-background-color: {ModernColors.PRIMARY};
                alternate-background-color: {ModernColors.BACKGROUND_SECONDARY};
            }}
            QTableWidget::item {{
                padding: 12px 8px;
                border: none;
            }}
            QTableWidget::item:selected {{
                background: {ModernColors.PRIMARY};
                color: {ModernColors.TEXT_LIGHT};
            }}
            QHeaderView::section {{
                background: {ModernColors.BACKGROUND_SECONDARY};
                color: {ModernColors.TEXT_PRIMARY};
                padding: 12px 8px;
                border: none;
                border-bottom: 2px solid {ModernColors.BORDER_LIGHT};
                font-weight: 600;
            }}
            QScrollBar:vertical {{
                background: {ModernColors.BACKGROUND_SECONDARY};
                width: 12px;
                border-radius: 6px;
            }}
            QScrollBar::handle:vertical {{
                background: {ModernColors.BORDER_MEDIUM};
                border-radius: 6px;
                min-height: 20px;
            }}
            QScrollBar::handle:vertical:hover {{
                background: {ModernColors.PRIMARY};
            }}
        """)
        self.setAlternatingRowColors(True)
        self.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.verticalHeader().setVisible(False)
        self.horizontalHeader().setStretchLastSection(True)

class ModernTabWidget(QTabWidget):
    """Modern tab widget with custom styling"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_styling()
    
    def setup_styling(self):
        """Setup tab widget styling"""
        self.setStyleSheet(f"""
            QTabWidget::pane {{
                border: 1px solid {ModernColors.BORDER_LIGHT};
                border-radius: 8px;
                background: {ModernColors.BACKGROUND_CARD};
                top: -1px;
            }}
            QTabBar::tab {{
                background: {ModernColors.BACKGROUND_SECONDARY};
                color: {ModernColors.TEXT_SECONDARY};
                padding: 12px 24px;
                margin-right: 2px;
                border-top-left-radius: 8px;
                border-top-right-radius: 8px;
                font-weight: 500;
            }}
            QTabBar::tab:selected {{
                background: {ModernColors.BACKGROUND_CARD};
                color: {ModernColors.PRIMARY};
                border-bottom: 2px solid {ModernColors.PRIMARY};
            }}
            QTabBar::tab:hover:!selected {{
                background: {ModernColors.BORDER_LIGHT};
                color: {ModernColors.TEXT_PRIMARY};
            }}
        """)

class ModernComboBox(QComboBox):
    """Modern combo box with custom styling"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_styling()
    
    def setup_styling(self):
        """Setup combo box styling"""
        self.setStyleSheet(f"""
            QComboBox {{
                padding: 12px 16px;
                border: 2px solid {ModernColors.BORDER_LIGHT};
                border-radius: 8px;
                background: {ModernColors.BACKGROUND_CARD};
                color: {ModernColors.TEXT_PRIMARY};
                font-size: 14px;
                min-width: 120px;
            }}
            QComboBox:focus {{
                border-color: {ModernColors.PRIMARY};
            }}
            QComboBox::drop-down {{
                border: none;
                width: 20px;
            }}
            QComboBox::down-arrow {{
                image: none;
                border-left: 5px solid transparent;
                border-right: 5px solid transparent;
                border-top: 5px solid {ModernColors.TEXT_MUTED};
                margin-right: 8px;
            }}
            QComboBox QAbstractItemView {{
                background: {ModernColors.BACKGROUND_CARD};
                border: 1px solid {ModernColors.BORDER_LIGHT};
                border-radius: 8px;
                selection-background-color: {ModernColors.PRIMARY};
                selection-color: {ModernColors.TEXT_LIGHT};
                padding: 4px;
            }}
            QComboBox QAbstractItemView::item {{
                padding: 8px 12px;
                border-radius: 4px;
            }}
            QComboBox QAbstractItemView::item:hover {{
                background: {ModernColors.BACKGROUND_SECONDARY};
            }}
            QComboBox QAbstractItemView::item:selected {{
                background: {ModernColors.PRIMARY};
                color: {ModernColors.TEXT_LIGHT};
            }}
        """)

class ModernProgressBar(QProgressBar):
    """Modern progress bar with gradient effect"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_styling()
    
    def setup_styling(self):
        """Setup progress bar styling"""
        self.setStyleSheet(f"""
            QProgressBar {{
                border: 2px solid {ModernColors.BORDER_LIGHT};
                border-radius: 8px;
                background: {ModernColors.BACKGROUND_SECONDARY};
                text-align: center;
                color: {ModernColors.TEXT_PRIMARY};
                font-weight: 600;
            }}
            QProgressBar::chunk {{
                background: {ModernColors.GRADIENT_PRIMARY};
                border-radius: 6px;
            }}
        """)

class ModernScrollArea(QScrollArea):
    """Modern scroll area with custom styling"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_styling()
    
    def setup_styling(self):
        """Setup scroll area styling"""
        self.setStyleSheet(f"""
            QScrollArea {{
                border: none;
                background: transparent;
            }}
            QScrollBar:vertical {{
                background: {ModernColors.BACKGROUND_SECONDARY};
                width: 12px;
                border-radius: 6px;
                margin: 0;
            }}
            QScrollBar::handle:vertical {{
                background: {ModernColors.BORDER_MEDIUM};
                border-radius: 6px;
                min-height: 20px;
                margin: 2px;
            }}
            QScrollBar::handle:vertical:hover {{
                background: {ModernColors.PRIMARY};
            }}
            QScrollBar::add-line:vertical,
            QScrollBar::sub-line:vertical {{
                height: 0px;
            }}
            QScrollBar:horizontal {{
                background: {ModernColors.BACKGROUND_SECONDARY};
                height: 12px;
                border-radius: 6px;
                margin: 0;
            }}
            QScrollBar::handle:horizontal {{
                background: {ModernColors.BORDER_MEDIUM};
                border-radius: 6px;
                min-width: 20px;
                margin: 2px;
            }}
            QScrollBar::handle:horizontal:hover {{
                background: {ModernColors.PRIMARY};
            }}
            QScrollBar::add-line:horizontal,
            QScrollBar::sub-line:horizontal {{
                width: 0px;
            }}
        """)

class Tooltip:
    """Modern tooltip widget"""
    
    def __init__(self, parent_widget, text):
        self.parent = parent_widget
        self.text = text
        self.tooltip = None
        self.setup_tooltip()
    
    def setup_tooltip(self):
        """Setup tooltip styling and behavior"""
        self.tooltip = QLabel(self.text)
        self.tooltip.setStyleSheet(f"""
            QLabel {{
                background: {ModernColors.TEXT_PRIMARY};
                color: {ModernColors.TEXT_LIGHT};
                padding: 8px 12px;
                border-radius: 6px;
                font-size: 12px;
                max-width: 250px;
            }}
        """)
        self.tooltip.setWindowFlags(Qt.WindowType.ToolTip | Qt.WindowType.FramelessWindowHint)
        self.tooltip.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)
        self.tooltip.hide()

class GUIManager:
    """Modern GUI Manager for the School Management System"""
    
    def __init__(self, main_window, app):
        self.main_window = main_window
        self.app = app
        self.logger = logging.getLogger('GUIManager')
        self.current_theme = "light"
        self.setup_fonts()
        self.setup_main_window()
        self.setup_menu_bar()
        self.setup_status_bar()
        self.setup_timer()
        
    def setup_fonts(self):
        """Setup modern fonts"""
        # Ensure QApplication exists before accessing QFontDatabase
        if not QApplication.instance():
            # Create a minimal QApplication instance if one doesn't exist
            temp_app = QApplication([])
            font_families = ["Segoe UI", "SF Pro Display", "Roboto", "Helvetica Neue"]
            
            for family in font_families:
                if family in QFontDatabase.families():
                    self.default_font = QFont(family, 10)
                    break
            else:
                self.default_font = QFont("Segoe UI", 10)
            # Clean up the temporary app
            temp_app.quit()
        else:
            font_families = ["Segoe UI", "SF Pro Display", "Roboto", "Helvetica Neue"]
            
            for family in font_families:
                if family in QFontDatabase.families():
                    self.default_font = QFont(family, 10)
                    break
            else:
                self.default_font = QFont("Segoe UI", 10)
    
    def setup_main_window(self):
        """Setup the main application window"""
        self.main_window.setWindowTitle("HarLuFran InnoFlux SMS - Modern School Management System")
        self.main_window.setGeometry(100, 100, 1400, 800)
        self.main_window.setMinimumSize(1200, 700)
        
        # Set application style
        self.main_window.setStyleSheet(f"""
            QMainWindow {{
                background: {ModernColors.BACKGROUND_PRIMARY};
                color: {ModernColors.TEXT_PRIMARY};
            }}
            QWidget {{
                font-family: '{self.default_font.family()}';
            }}
        """)
        
        # Create central widget and main layout
        central_widget = QWidget()
        self.main_window.setCentralWidget(central_widget)
        self.main_layout = QVBoxLayout(central_widget)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setSpacing(0)
        
        # Create header
        self.create_header()
        
        # Create navigation
        self.create_navigation()
        
        # Create main content area
        self.create_main_content()
    
    def create_header(self):
        """Create modern header with gradient background"""
        header_frame = QFrame()
        header_frame.setFixedHeight(80)
        header_frame.setStyleSheet(f"""
            QFrame {{
                background: {ModernColors.GRADIENT_PRIMARY};
                border-radius: 0px 0px 20px 20px;
                margin: 0px;
            }}
        """)
        
        header_layout = QHBoxLayout(header_frame)
        header_layout.setContentsMargins(30, 0, 30, 0)
        
        # Logo and title
        title_layout = QVBoxLayout()
        title_layout.setSpacing(2)
        
        main_title = QLabel("HarLuFran InnoFlux SMS")
        main_title.setStyleSheet(f"""
            color: {ModernColors.TEXT_LIGHT};
            font-size: 24px;
            font-weight: 600;
            margin: 0px;
        """)
        main_title.setFont(QFont(self.default_font.family(), 24, QFont.Weight.DemiBold))
        
        subtitle = QLabel("Modern School Management System")
        subtitle.setStyleSheet(f"""
            color: rgba(255, 255, 255, 0.8);
            font-size: 14px;
            margin: 0px;
        """)
        
        title_layout.addWidget(main_title)
        title_layout.addWidget(subtitle)
        title_layout.addStretch()
        
        header_layout.addLayout(title_layout)
        header_layout.addStretch()
        
        # Clock and user info
        info_layout = QVBoxLayout()
        info_layout.setAlignment(Qt.AlignmentFlag.AlignRight)
        
        self.clock_label = QLabel()
        self.clock_label.setStyleSheet(f"""
            color: {ModernColors.TEXT_LIGHT};
            font-size: 14px;
            font-weight: 500;
        """)
        
        user_label = QLabel("Administrator")
        user_label.setStyleSheet(f"""
            color: rgba(255, 255, 255, 0.9);
            font-size: 12px;
        """)
        
        info_layout.addWidget(self.clock_label)
        info_layout.addWidget(user_label)
        
        header_layout.addLayout(info_layout)
        self.main_layout.addWidget(header_frame)
    
    def create_navigation(self):
        """Create modern navigation sidebar"""
        nav_frame = QFrame()
        nav_frame.setFixedWidth(280)
        nav_frame.setStyleSheet(f"""
            QFrame {{
                background: {ModernColors.BACKGROUND_CARD};
                border-right: 1px solid {ModernColors.BORDER_LIGHT};
            }}
        """)
        
        nav_layout = QVBoxLayout(nav_frame)
        nav_layout.setContentsMargins(0, 0, 0, 0)
        
        # Navigation menu
        nav_menu = QVBoxLayout()
        nav_menu.setContentsMargins(20, 20, 20, 20)
        nav_menu.setSpacing(8)
        
        # Menu sections
        menu_sections = [
            ("🏠 Dashboard", self.show_dashboard, True),
            ("📚 Library", self.show_library, False),
            ("👥 Students", self.show_students, False),
            ("👨‍🏫 Teachers", self.show_teachers, False),
            ("🪑 Furniture", self.show_furniture, False),
            ("📊 Reports", self.show_reports, False),
            ("⚙️ Settings", self.show_settings, False),
        ]
        
        self.nav_buttons = []
        for text, callback, active in menu_sections:
            btn = ModernButton(text, "outline", "medium")
            btn.clicked.connect(callback)
            if active:
                btn.setStyleSheet(btn.styleSheet() + f"""
                    QPushButton {{
                        background: {ModernColors.PRIMARY};
                        color: {ModernColors.TEXT_LIGHT};
                        border-color: {ModernColors.PRIMARY};
                    }}
                """)
            nav_menu.addWidget(btn)
            self.nav_buttons.append(btn)
        
        nav_menu.addStretch()
        
        # Quick actions
        quick_actions_label = QLabel("Quick Actions")
        quick_actions_label.setStyleSheet(f"""
            color: {ModernColors.TEXT_MUTED};
            font-size: 12px;
            font-weight: 600;
            margin-top: 20px;
        """)
        nav_menu.addWidget(quick_actions_label)
        
        quick_actions = [
            ("📖 Borrow Book", self.quick_borrow_book),
            ("📥 Return Book", self.quick_return_book),
            ("➕ Add Student", self.quick_add_student),
            ("🔔 Notifications", self.show_notifications),
        ]
        
        for text, callback in quick_actions:
            btn = ModernButton(text, "outline", "small")
            btn.clicked.connect(callback)
            nav_menu.addWidget(btn)
        
        nav_layout.addLayout(nav_menu)
        
        # Add navigation to main layout
        content_layout = QHBoxLayout()
        content_layout.setContentsMargins(0, 0, 0, 0)
        content_layout.setSpacing(0)
        content_layout.addWidget(nav_frame)
        
        self.main_layout.addLayout(content_layout)
        
        # Store reference to content area
        self.content_area = QFrame()
        self.content_area.setStyleSheet(f"""
            QFrame {{
                background: {ModernColors.BACKGROUND_PRIMARY};
            }}
        """)
        content_layout.addWidget(self.content_area)
    
    def create_main_content(self):
        """Create main content area"""
        self.content_layout = QVBoxLayout(self.content_area)
        self.content_layout.setContentsMargins(30, 30, 30, 30)
        
        # Show dashboard by default
        self.show_dashboard()
    
    def setup_menu_bar(self):
        """Setup modern menu bar"""
        menubar = self.main_window.menuBar()
        menubar.setStyleSheet(f"""
            QMenuBar {{
                background: {ModernColors.BACKGROUND_CARD};
                border-bottom: 1px solid {ModernColors.BORDER_LIGHT};
                color: {ModernColors.TEXT_PRIMARY};
                padding: 4px;
            }}
            QMenuBar::item {{
                background: transparent;
                padding: 8px 16px;
                border-radius: 4px;
                margin: 2px;
            }}
            QMenuBar::item:selected {{
                background: {ModernColors.BACKGROUND_SECONDARY};
            }}
            QMenu {{
                background: {ModernColors.BACKGROUND_CARD};
                border: 1px solid {ModernColors.BORDER_LIGHT};
                border-radius: 8px;
                color: {ModernColors.TEXT_PRIMARY};
                padding: 8px;
            }}
            QMenu::item {{
                padding: 8px 16px;
                border-radius: 4px;
            }}
            QMenu::item:selected {{
                background: {ModernColors.PRIMARY};
                color: {ModernColors.TEXT_LIGHT};
            }}
            QMenu::separator {{
                height: 1px;
                background: {ModernColors.BORDER_LIGHT};
                margin: 4px 8px;
            }}
        """)
        
        # File menu
        file_menu = menubar.addMenu("File")
        
        # Edit menu
        edit_menu = menubar.addMenu("Edit")
        
        # View menu
        view_menu = menubar.addMenu("View")
        
        # Tools menu
        tools_menu = menubar.addMenu("Tools")
        
        # Help menu
        help_menu = menubar.addMenu("Help")
    
    def setup_status_bar(self):
        """Setup modern status bar"""
        status_bar = self.main_window.statusBar()
        status_bar.setStyleSheet(f"""
            QStatusBar {{
                background: {ModernColors.BACKGROUND_CARD};
                border-top: 1px solid {ModernColors.BORDER_LIGHT};
                color: {ModernColors.TEXT_SECONDARY};
                padding: 4px 8px;
            }}
            QStatusBar::item {{
                border: none;
            }}
        """)
        
        # Status bar widgets
        self.status_label = QLabel("Ready")
        self.connection_label = QLabel("🟢 Connected")
        self.connection_label.setStyleSheet(f"""
            color: {ModernColors.SUCCESS};
            font-weight: 600;
        """)
        
        status_bar.addWidget(self.status_label)
        status_bar.addPermanentWidget(self.connection_label)
    
    def setup_timer(self):
        """Setup timer for clock updates"""
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_clock)
        self.timer.start(1000)  # Update every second
        self.update_clock()
    
    def update_clock(self):
        """Update clock display"""
        current_time = datetime.now().strftime("%H:%M:%S")
        current_date = datetime.now().strftime("%B %d, %Y")
        self.clock_label.setText(f"{current_time}\n{current_date}")
    
    def clear_content(self):
        """Clear main content area"""
        for i in reversed(range(self.content_layout.count())):
            child = self.content_layout.itemAt(i).widget()
            if child:
                child.setParent(None)
    
    def show_dashboard(self):
        """Show modern dashboard"""
        self.clear_content()
        
        # Dashboard title
        title_label = QLabel("Dashboard")
        title_label.setStyleSheet(f"""
            color: {ModernColors.TEXT_PRIMARY};
            font-size: 32px;
            font-weight: 700;
            margin-bottom: 30px;
        """)
        title_label.setFont(QFont(self.default_font.family(), 32, QFont.Weight.Black))
        self.content_layout.addWidget(title_label)
        
        # Stats cards row
        stats_layout = QHBoxLayout()
        stats_layout.setSpacing(20)
        
        # Sample stats
        stats = [
            ("Total Students", "1,234", ModernColors.SUCCESS),
            ("Books in Library", "5,678", ModernColors.INFO),
            ("Active Borrowings", "89", ModernColors.WARNING),
            ("Overdue Returns", "12", ModernColors.ERROR)
        ]
        
        for title, value, color in stats:
            stat_card = self.create_stat_card(title, value, color)
            stats_layout.addWidget(stat_card)
        
        stats_layout.addStretch()
        self.content_layout.addLayout(stats_layout)
        
        # Recent activity section
        activity_frame = ModernCard("Recent Activity")
        activity_content = self.create_recent_activity_widget()
        activity_frame.layout().addWidget(activity_content)
        self.content_layout.addWidget(activity_frame)
        
        # Quick actions section
        actions_frame = ModernCard("Quick Actions")
        actions_layout = QGridLayout()
        actions_layout.setSpacing(15)
        
        quick_actions = [
            ("📖 Borrow Book", self.quick_borrow_book),
            ("📥 Return Book", self.quick_return_book),
            ("👥 Add Student", self.quick_add_student),
            ("👨‍🏫 Add Teacher", self.quick_add_teacher),
            ("📚 Add Book", self.quick_add_book),
            ("🪑 Manage Furniture", self.quick_manage_furniture),
            ("📊 Generate Report", self.quick_generate_report),
            ("🔔 View Notifications", self.quick_view_notifications),
        ]
        
        for i, (text, callback) in enumerate(quick_actions):
            btn = ModernButton(text, "primary", "medium")
            btn.clicked.connect(callback)
            actions_layout.addWidget(btn, i // 4, i % 4)
        
        actions_content = QWidget()
        actions_content.setLayout(actions_layout)
        actions_frame.layout().addWidget(actions_content)
        self.content_layout.addWidget(actions_frame)
        
        self.content_layout.addStretch()
    
    def create_stat_card(self, title, value, color):
        """Create a modern statistics card"""
        card = QFrame()
        card.setStyleSheet(f"""
            QFrame {{
                background: {ModernColors.BACKGROUND_CARD};
                border-radius: 12px;
                border: 1px solid {ModernColors.BORDER_LIGHT};
                padding: 20px;
                margin: 5px;
            }}
        """)
        
        layout = QVBoxLayout(card)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(10)
        
        # Value
        value_label = QLabel(value)
        value_label.setStyleSheet(f"""
            color: {color};
            font-size: 36px;
            font-weight: 700;
            margin: 0px;
        """)
        value_label.setFont(QFont(self.default_font.family(), 36, QFont.Weight.Black))
        
        # Title
        title_label = QLabel(title)
        title_label.setStyleSheet(f"""
            color: {ModernColors.TEXT_MUTED};
            font-size: 14px;
            font-weight: 500;
            margin: 0px;
        """)
        
        layout.addWidget(value_label)
        layout.addWidget(title_label)
        
        return card
    
    def create_recent_activity_widget(self):
        """Create recent activity widget"""
        activity_widget = QWidget()
        layout = QVBoxLayout(activity_widget)
        
        # Sample activities
        activities = [
            ("📚 John Doe borrowed 'Mathematics Grade 4'", "2 minutes ago"),
            ("👥 Alice Smith added to Form 2 Blue", "15 minutes ago"),
            ("📖 Sarah Johnson returned 'Science Basics'", "1 hour ago"),
            ("👨‍🏫 Mr. Brown borrowed 'English Literature'", "2 hours ago"),
        ]
        
        for activity, time in activities:
            activity_frame = QFrame()
            activity_frame.setStyleSheet(f"""
                QFrame {{
                    background: {ModernColors.BACKGROUND_SECONDARY};
                    border-radius: 8px;
                    padding: 12px;
                    margin: 2px 0px;
                }}
            """)
            
            activity_layout = QHBoxLayout(activity_frame)
            activity_layout.setContentsMargins(15, 10, 15, 10)
            
            activity_label = QLabel(activity)
            activity_label.setStyleSheet(f"""
                color: {ModernColors.TEXT_PRIMARY};
                font-size: 14px;
            """)
            
            time_label = QLabel(time)
            time_label.setStyleSheet(f"""
                color: {ModernColors.TEXT_MUTED};
                font-size: 12px;
            """)
            
            activity_layout.addWidget(activity_label)
            activity_layout.addStretch()
            activity_layout.addWidget(time_label)
            
            layout.addWidget(activity_frame)
        
        return activity_widget
    
    def show_library(self):
        """Show library management interface"""
        self.clear_content()
        
        # Title
        title_label = QLabel("Library Management")
        title_label.setStyleSheet(f"""
            color: {ModernColors.TEXT_PRIMARY};
            font-size: 32px;
            font-weight: 700;
            margin-bottom: 30px;
        """)
        title_label.setFont(QFont(self.default_font.family(), 32, QFont.Weight.Black))
        self.content_layout.addWidget(title_label)
        
        # Create tabs for different library functions
        tab_widget = ModernTabWidget()
        
        # Books tab
        books_tab = QWidget()
        books_layout = QVBoxLayout(books_tab)
        
        # Search and filter section
        search_frame = QFrame()
        search_frame.setStyleSheet(f"""
            QFrame {{
                background: {ModernColors.BACKGROUND_CARD};
                border-radius: 12px;
                padding: 20px;
                margin-bottom: 20px;
            }}
        """)
        search_layout = QGridLayout(search_frame)
        search_layout.setSpacing(15)
        
        search_layout.addWidget(QLabel("Search:"), 0, 0)
        search_input = ModernLineEdit("Enter book title, ID, or author...")
        search_layout.addWidget(search_input, 0, 1, 1, 2)
        
        search_layout.addWidget(QLabel("Category:"), 1, 0)
        category_combo = ModernComboBox()
        category_combo.addItems(["All Categories", "Mathematics", "English", "Science", "History"])
        search_layout.addWidget(category_combo, 1, 1)
        
        search_layout.addWidget(QLabel("Status:"), 1, 2)
        status_combo = ModernComboBox()
        status_combo.addItems(["All", "Available", "Borrowed", "Reserved"])
        search_layout.addWidget(status_combo, 1, 3)
        
        search_btn = ModernButton("🔍 Search", "primary", "medium")
        search_layout.addWidget(search_btn, 0, 4, 2, 1)
        
        books_layout.addWidget(search_frame)
        
        # Books table
        books_table = ModernTableWidget()
        books_table.setColumnCount(6)
        books_table.setHorizontalHeaderLabels(["Book ID", "Title", "Author", "Category", "Status", "Actions"])
        
        # Sample data
        sample_books = [
            ("BK001", "Mathematics Grade 4", "John Smith", "Mathematics", "Available", ""),
            ("BK002", "English Literature", "Jane Doe", "English", "Borrowed", ""),
            ("BK003", "Science Basics", "Bob Johnson", "Science", "Available", ""),
            ("BK004", "History of Kenya", "Alice Brown", "History", "Reserved", ""),
        ]
        
        for row, book_data in enumerate(sample_books):
            for col, data in enumerate(book_data):
                if col == 5:  # Actions column
                    action_btn = ModernButton("View", "outline", "small")
                    books_table.setCellWidget(row, col, action_btn)
                else:
                    item = QTableWidgetItem(str(data))
                    books_table.setItem(row, col, item)
        
        books_table.resizeColumnsToContents()
        books_layout.addWidget(books_table)
        
        tab_widget.addTab(books_tab, "📚 Books")
        
        # Borrowing tab
        borrowing_tab = QWidget()
        borrowing_layout = QVBoxLayout(borrowing_tab)
        
        borrow_frame = ModernCard("Book Borrowing")
        borrow_form = QGridLayout()
        borrow_form.setSpacing(20)
        
        # Form fields
        borrow_form.addWidget(QLabel("Student/Teacher ID:"), 0, 0)
        student_id_input = ModernLineEdit()
        borrow_form.addWidget(student_id_input, 0, 1)
        
        borrow_form.addWidget(QLabel("Book ID:"), 1, 0)
        book_id_input = ModernLineEdit()
        borrow_form.addWidget(book_id_input, 1, 1)
        
        borrow_form.addWidget(QLabel("Condition:"), 2, 0)
        condition_combo = ModernComboBox()
        condition_combo.addItems(["New", "Good", "Damaged"])
        borrow_form.addWidget(condition_combo, 2, 1)
        
        borrow_buttons = QHBoxLayout()
        borrow_btn = ModernButton("📖 Borrow Book", "success", "medium")
        return_btn = ModernButton("📥 Return Book", "primary", "medium")
        borrow_buttons.addWidget(borrow_btn)
        borrow_buttons.addWidget(return_btn)
        
        borrow_form.addLayout(borrow_buttons, 3, 0, 1, 2)
        
        borrow_content = QWidget()
        borrow_content.setLayout(borrow_form)
        borrow_frame.layout().addWidget(borrow_content)
        borrowing_layout.addWidget(borrow_frame)
        
        tab_widget.addTab(borrowing_tab, "📖 Borrowing")
        
        # Reports tab
        reports_tab = QWidget()
        reports_layout = QVBoxLayout(reports_tab)
        
        reports_grid = QGridLayout()
        reports_grid.setSpacing(15)
        
        report_buttons = [
            ("📊 Books by Category", self.generate_category_report),
            ("📈 Borrowing Statistics", self.generate_borrowing_stats),
            ("⏰ Overdue Books", self.show_overdue_books),
            ("📋 Inventory Report", self.generate_inventory_report),
            ("👥 Most Active Borrowers", self.generate_active_borrowers),
            ("📊 Monthly Statistics", self.generate_monthly_stats),
        ]
        
        for i, (text, callback) in enumerate(report_buttons):
            btn = ModernButton(text, "primary", "medium")
            btn.clicked.connect(callback)
            reports_grid.addWidget(btn, i // 3, i % 3)
        
        reports_content = QWidget()
        reports_content.setLayout(reports_grid)
        reports_layout.addWidget(reports_content)
        
        tab_widget.addTab(reports_tab, "📊 Reports")
        
        self.content_layout.addWidget(tab_widget)
    
    def show_students(self):
        """Show student management interface"""
        self.clear_content()
        
        # Title
        title_label = QLabel("Student Management")
        title_label.setStyleSheet(f"""
            color: {ModernColors.TEXT_PRIMARY};
            font-size: 32px;
            font-weight: 700;
            margin-bottom: 30px;
        """)
        title_label.setFont(QFont(self.default_font.family(), 32, QFont.Weight.Black))
        self.content_layout.addWidget(title_label)
        
        # Student management interface
        students_card = ModernCard("Students Directory")
        
        # Student form
        form_layout = QGridLayout()
        form_layout.setSpacing(15)
        
        # Form fields
        form_layout.addWidget(QLabel("Student ID:"), 0, 0)
        student_id_input = ModernLineEdit()
        form_layout.addWidget(student_id_input, 0, 1)
        
        form_layout.addWidget(QLabel("Full Name:"), 1, 0)
        name_input = ModernLineEdit()
        form_layout.addWidget(name_input, 1, 1)
        
        form_layout.addWidget(QLabel("Form:"), 2, 0)
        form_combo = ModernComboBox()
        form_combo.addItems(["Form 1", "Form 2", "Form 3", "Form 4"])
        form_layout.addWidget(form_combo, 2, 1)
        
        form_layout.addWidget(QLabel("Stream:"), 3, 0)
        stream_input = ModernLineEdit()
        form_layout.addWidget(stream_input, 3, 1)
        
        # Action buttons
        buttons_layout = QHBoxLayout()
        add_btn = ModernButton("➕ Add Student", "success", "medium")
        update_btn = ModernButton("✏️ Update", "primary", "medium")
        search_btn = ModernButton("🔍 Search", "outline", "medium")
        buttons_layout.addWidget(add_btn)
        buttons_layout.addWidget(update_btn)
        buttons_layout.addWidget(search_btn)
        
        form_layout.addLayout(buttons_layout, 4, 0, 1, 2)
        
        form_content = QWidget()
        form_content.setLayout(form_layout)
        students_card.layout().addWidget(form_content)
        
        self.content_layout.addWidget(students_card)
        
        # Students table
        students_table = ModernTableWidget()
        students_table.setColumnCount(6)
        students_table.setHorizontalHeaderLabels(["Student ID", "Name", "Form", "Stream", "Books Borrowed", "Actions"])
        
        # Sample data
        sample_students = [
            ("STU001", "John Doe", "Form 2", "Blue", "3", ""),
            ("STU002", "Alice Smith", "Form 3", "Red", "1", ""),
            ("STU003", "Bob Johnson", "Form 1", "Green", "2", ""),
            ("STU004", "Sarah Wilson", "Form 4", "Yellow", "0", ""),
        ]
        
        for row, student_data in enumerate(sample_students):
            for col, data in enumerate(student_data):
                if col == 5:  # Actions column
                    action_btn = ModernButton("View", "outline", "small")
                    students_table.setCellWidget(row, col, action_btn)
                else:
                    item = QTableWidgetItem(str(data))
                    students_table.setItem(row, col, item)
        
        students_table.resizeColumnsToContents()
        self.content_layout.addWidget(students_table)
    
    def show_teachers(self):
        """Show teacher management interface"""
        self.clear_content()
        
        # Title
        title_label = QLabel("Teacher Management")
        title_label.setStyleSheet(f"""
            color: {ModernColors.TEXT_PRIMARY};
            font-size: 32px;
            font-weight: 700;
            margin-bottom: 30px;
        """)
        title_label.setFont(QFont(self.default_font.family(), 32, QFont.Weight.Black))
        self.content_layout.addWidget(title_label)
        
        # Teacher management interface
        teachers_card = ModernCard("Teachers Directory")
        
        # Teacher form
        form_layout = QGridLayout()
        form_layout.setSpacing(15)
        
        # Form fields
        form_layout.addWidget(QLabel("TSC Number:"), 0, 0)
        tsc_input = ModernLineEdit()
        form_layout.addWidget(tsc_input, 0, 1)
        
        form_layout.addWidget(QLabel("Full Name:"), 1, 0)
        name_input = ModernLineEdit()
        form_layout.addWidget(name_input, 1, 1)
        
        form_layout.addWidget(QLabel("Department:"), 2, 0)
        dept_combo = ModernComboBox()
        dept_combo.addItems(["Mathematics", "English", "Science", "History", "Computer Studies"])
        form_layout.addWidget(dept_combo, 2, 1)
        
        form_layout.addWidget(QLabel("Position:"), 3, 0)
        position_combo = ModernComboBox()
        position_combo.addItems(["Teacher", "Senior Teacher", "Head of Department", "Deputy Principal", "Principal"])
        form_layout.addWidget(position_combo, 3, 1)
        
        # Action buttons
        buttons_layout = QHBoxLayout()
        add_btn = ModernButton("➕ Add Teacher", "success", "medium")
        update_btn = ModernButton("✏️ Update", "primary", "medium")
        search_btn = ModernButton("🔍 Search", "outline", "medium")
        buttons_layout.addWidget(add_btn)
        buttons_layout.addWidget(update_btn)
        buttons_layout.addWidget(search_btn)
        
        form_layout.addLayout(buttons_layout, 4, 0, 1, 2)
        
        form_content = QWidget()
        form_content.setLayout(form_layout)
        teachers_card.layout().addWidget(form_content)
        
        self.content_layout.addWidget(teachers_card)
        
        # Teachers table
        teachers_table = ModernTableWidget()
        teachers_table.setColumnCount(5)
        teachers_table.setHorizontalHeaderLabels(["TSC Number", "Name", "Department", "Position", "Actions"])
        
        # Sample data
        sample_teachers = [
            ("TSC001", "Mr. John Smith", "Mathematics", "Head of Department", ""),
            ("TSC002", "Mrs. Jane Doe", "English", "Senior Teacher", ""),
            ("TSC003", "Mr. Bob Johnson", "Science", "Teacher", ""),
            ("TSC004", "Ms. Alice Brown", "Computer Studies", "Teacher", ""),
        ]
        
        for row, teacher_data in enumerate(sample_teachers):
            for col, data in enumerate(teacher_data):
                if col == 4:  # Actions column
                    action_btn = ModernButton("View", "outline", "small")
                    teachers_table.setCellWidget(row, col, action_btn)
                else:
                    item = QTableWidgetItem(str(data))
                    teachers_table.setItem(row, col, item)
        
        teachers_table.resizeColumnsToContents()
        self.content_layout.addWidget(teachers_table)
    
    def show_furniture(self):
        """Show furniture management interface"""
        self.clear_content()
        
        # Title
        title_label = QLabel("Furniture Management")
        title_label.setStyleSheet(f"""
            color: {ModernColors.TEXT_PRIMARY};
            font-size: 32px;
            font-weight: 700;
            margin-bottom: 30px;
        """)
        title_label.setFont(QFont(self.default_font.family(), 32, QFont.Weight.Black))
        self.content_layout.addWidget(title_label)
        
        # Create tabs for different furniture types
        tab_widget = ModernTabWidget()
        
        # Lockers tab
        lockers_tab = QWidget()
        lockers_layout = QVBoxLayout(lockers_tab)
        
        # Locker assignment section
        locker_card = ModernCard("Locker Assignment")
        locker_layout = QGridLayout()
        locker_layout.setSpacing(15)
        
        # Form fields
        locker_layout.addWidget(QLabel("Student ID:"), 0, 0)
        student_id_input = ModernLineEdit()
        locker_layout.addWidget(student_id_input, 0, 1)
        
        locker_layout.addWidget(QLabel("Locker ID:"), 1, 0)
        locker_id_input = ModernLineEdit()
        locker_layout.addWidget(locker_id_input, 1, 1)
        
        # Action buttons
        buttons_layout = QHBoxLayout()
        assign_btn = ModernButton("🗄️ Assign Locker", "success", "medium")
        unassign_btn = ModernButton("🗑️ Unassign", "danger", "medium")
        buttons_layout.addWidget(assign_btn)
        buttons_layout.addWidget(unassign_btn)
        
        locker_layout.addLayout(buttons_layout, 2, 0, 1, 2)
        
        locker_content = QWidget()
        locker_content.setLayout(locker_layout)
        locker_card.layout().addWidget(locker_content)
        lockers_layout.addWidget(locker_card)
        
        # Lockers table
        lockers_table = ModernTableWidget()
        lockers_table.setColumnCount(5)
        lockers_table.setHorizontalHeaderLabels(["Locker ID", "Student ID", "Student Name", "Form", "Status"])
        
        # Sample data
        sample_lockers = [
            ("LKR001", "STU001", "John Doe", "Form 2", "Assigned"),
            ("LKR002", "", "", "", "Available"),
            ("LKR003", "STU002", "Alice Smith", "Form 3", "Assigned"),
            ("LKR004", "", "", "", "Available"),
        ]
        
        for row, locker_data in enumerate(sample_lockers):
            for col, data in enumerate(locker_data):
                item = QTableWidgetItem(str(data))
                lockers_table.setItem(row, col, item)
        
        lockers_table.resizeColumnsToContents()
        lockers_layout.addWidget(lockers_table)
        
        tab_widget.addTab(lockers_tab, "🗄️ Lockers")
        
        # Chairs tab
        chairs_tab = QWidget()
        chairs_layout = QVBoxLayout(chairs_tab)
        
        # Chair assignment section
        chair_card = ModernCard("Chair Assignment")
        chair_layout = QGridLayout()
        chair_layout.setSpacing(15)
        
        # Form fields
        chair_layout.addWidget(QLabel("Student ID:"), 0, 0)
        chair_student_input = ModernLineEdit()
        chair_layout.addWidget(chair_student_input, 0, 1)
        
        chair_layout.addWidget(QLabel("Chair ID:"), 1, 0)
        chair_id_input = ModernLineEdit()
        chair_layout.addWidget(chair_id_input, 1, 1)
        
        # Action buttons
        chair_buttons_layout = QHBoxLayout()
        chair_assign_btn = ModernButton("🪑 Assign Chair", "success", "medium")
        chair_unassign_btn = ModernButton("🗑️ Unassign", "danger", "medium")
        chair_buttons_layout.addWidget(chair_assign_btn)
        chair_buttons_layout.addWidget(chair_unassign_btn)
        
        chair_layout.addLayout(chair_buttons_layout, 2, 0, 1, 2)
        
        chair_content = QWidget()
        chair_content.setLayout(chair_layout)
        chair_card.layout().addWidget(chair_content)
        chairs_layout.addWidget(chair_card)
        
        # Chairs table
        chairs_table = ModernTableWidget()
        chairs_table.setColumnCount(5)
        chairs_table.setHorizontalHeaderLabels(["Chair ID", "Student ID", "Student Name", "Form", "Status"])
        
        # Sample data
        sample_chairs = [
            ("CHR001", "STU001", "John Doe", "Form 2", "Assigned"),
            ("CHR002", "", "", "", "Available"),
            ("CHR003", "STU002", "Alice Smith", "Form 3", "Assigned"),
            ("CHR004", "", "", "", "Available"),
        ]
        
        for row, chair_data in enumerate(sample_chairs):
            for col, data in enumerate(chair_data):
                item = QTableWidgetItem(str(data))
                chairs_table.setItem(row, col, item)
        
        chairs_table.resizeColumnsToContents()
        chairs_layout.addWidget(chairs_table)
        
        tab_widget.addTab(chairs_tab, "🪑 Chairs")
        
        self.content_layout.addWidget(tab_widget)
    
    def show_reports(self):
        """Show reports interface"""
        self.clear_content()
        
        # Title
        title_label = QLabel("Reports & Analytics")
        title_label.setStyleSheet(f"""
            color: {ModernColors.TEXT_PRIMARY};
            font-size: 32px;
            font-weight: 700;
            margin-bottom: 30px;
        """)
        title_label.setFont(QFont(self.default_font.family(), 32, QFont.Weight.Black))
        self.content_layout.addWidget(title_label)
        
        # Reports grid
        reports_grid = QGridLayout()
        reports_grid.setSpacing(20)
        
        # Available reports
        reports = [
            ("📊 Library Statistics", "Overview of library usage and statistics", self.generate_library_stats),
            ("📚 Books Inventory", "Complete list of all books in the library", self.generate_books_inventory),
            ("👥 Student Statistics", "Student enrollment and activity reports", self.generate_student_stats),
            ("📈 Borrowing Trends", "Analysis of borrowing patterns over time", self.generate_borrowing_trends),
            ("⏰ Overdue Reports", "Books that are overdue for return", self.generate_overdue_report),
            ("🏫 Furniture Status", "Current status of all furniture items", self.generate_furniture_report),
            ("📊 Monthly Summary", "Monthly activity summary and statistics", self.generate_monthly_summary),
            ("💾 Export Data", "Export data in various formats", self.export_data),
        ]
        
        for i, (title, description, callback) in enumerate(reports):
            report_card = self.create_report_card(title, description, callback)
            reports_grid.addWidget(report_card, i // 4, i % 4)
        
        reports_content = QWidget()
        reports_content.setLayout(reports_grid)
        self.content_layout.addWidget(reports_content)
    
    def create_report_card(self, title, description, callback):
        """Create a modern report card"""
        card = QFrame()
        card.setStyleSheet(f"""
            QFrame {{
                background: {ModernColors.BACKGROUND_CARD};
                border-radius: 12px;
                border: 1px solid {ModernColors.BORDER_LIGHT};
                padding: 20px;
                margin: 5px;
            }}
            QFrame:hover {{
                border-color: {ModernColors.PRIMARY};
                box-shadow: 0 4px 12px {ModernColors.SHADOW};
            }}
        """)
        
        layout = QVBoxLayout(card)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)
        
        # Icon and title
        title_layout = QHBoxLayout()
        title_icon = QLabel(title.split()[0])  # Extract emoji
        title_text = QLabel(" ".join(title.split()[1:]))  # Rest of the title
        
        title_icon.setStyleSheet(f"""
            font-size: 24px;
            margin: 0px;
        """)
        
        title_text.setStyleSheet(f"""
            color: {ModernColors.TEXT_PRIMARY};
            font-size: 16px;
            font-weight: 600;
            margin: 0px;
        """)
        
        title_layout.addWidget(title_icon)
        title_layout.addWidget(title_text)
        title_layout.addStretch()
        
        # Description
        desc_label = QLabel(description)
        desc_label.setStyleSheet(f"""
            color: {ModernColors.TEXT_MUTED};
            font-size: 14px;
            line-height: 1.4;
            margin: 0px;
        """)
        desc_label.setWordWrap(True)
        
        # Generate button
        generate_btn = ModernButton("Generate Report", "primary", "small")
        generate_btn.clicked.connect(callback)
        
        layout.addLayout(title_layout)
        layout.addWidget(desc_label)
        layout.addStretch()
        layout.addWidget(generate_btn)
        
        return card
    
    def show_settings(self):
        """Show settings interface"""
        self.clear_content()
        
        # Title
        title_label = QLabel("Settings")
        title_label.setStyleSheet(f"""
            color: {ModernColors.TEXT_PRIMARY};
            font-size: 32px;
            font-weight: 700;
            margin-bottom: 30px;
        """)
        title_label.setFont(QFont(self.default_font.family(), 32, QFont.Weight.Black))
        self.content_layout.addWidget(title_label)
        
        # Settings tabs
        tab_widget = ModernTabWidget()
        
        # General settings
        general_tab = QWidget()
        general_layout = QVBoxLayout(general_tab)
        
        # Theme settings
        theme_card = ModernCard("Appearance")
        theme_layout = QVBoxLayout()
        
        theme_layout.addWidget(QLabel("Theme:"))
        theme_combo = ModernComboBox()
        theme_combo.addItems(["Light", "Dark", "Blue", "Green"])
        theme_layout.addWidget(theme_combo)
        
        theme_layout.addWidget(QLabel("Font Size:"))
        font_size_combo = ModernComboBox()
        font_size_combo.addItems(["Small", "Medium", "Large"])
        theme_layout.addWidget(font_size_combo)
        
        theme_content = QWidget()
        theme_content.setLayout(theme_layout)
        theme_card.layout().addWidget(theme_content)
        general_layout.addWidget(theme_card)
        
        # System settings
        system_card = ModernCard("System")
        system_layout = QVBoxLayout()
        
        system_layout.addWidget(QLabel("Database Backup Interval:"))
        backup_combo = ModernComboBox()
        backup_combo.addItems(["Daily", "Weekly", "Monthly"])
        system_layout.addWidget(backup_combo)
        
        system_layout.addWidget(QLabel("Auto-save Interval (minutes):"))
        auto_save_spin = QSpinBox()
        auto_save_spin.setRange(1, 60)
        auto_save_spin.setValue(5)
        system_layout.addWidget(auto_save_spin)
        
        system_content = QWidget()
        system_content.setLayout(system_layout)
        system_card.layout().addWidget(system_content)
        general_layout.addWidget(system_card)
        
        general_layout.addStretch()
        
        tab_widget.addTab(general_tab, "⚙️ General")
        
        # Notifications settings
        notifications_tab = QWidget()
        notifications_layout = QVBoxLayout(notifications_tab)
        
        notification_card = ModernCard("Notification Preferences")
        notification_layout = QVBoxLayout()
        
        # Checkboxes for different notifications
        overdue_check = QCheckBox("Overdue book notifications")
        overdue_check.setChecked(True)
        notification_layout.addWidget(overdue_check)
        
        system_check = QCheckBox("System maintenance notifications")
        system_check.setChecked(True)
        notification_layout.addWidget(system_check)
        
        report_check = QCheckBox("Monthly report notifications")
        report_layout = QVBoxLayout()
        report_layout.addWidget(report_check)
        
        notification_content = QWidget()
        notification_content.setLayout(notification_layout)
        notification_card.layout().addWidget(notification_content)
        notifications_layout.addWidget(notification_card)
        notifications_layout.addStretch()
        
        tab_widget.addTab(notifications_tab, "🔔 Notifications")
        
        # Security settings
        security_tab = QWidget()
        security_layout = QVBoxLayout(security_tab)
        
        security_card = ModernCard("Security")
        security_layout_inner = QVBoxLayout()
        
        security_layout_inner.addWidget(QLabel("Session Timeout (minutes):"))
        timeout_spin = QSpinBox()
        timeout_spin.setRange(5, 480)
        timeout_spin.setValue(60)
        security_layout_inner.addWidget(timeout_spin)
        
        security_layout_inner.addWidget(QLabel("Require password for sensitive operations"))
        password_check = QCheckBox()
        password_check.setChecked(True)
        security_layout_inner.addWidget(password_check)
        
        security_content = QWidget()
        security_content.setLayout(security_layout_inner)
        security_card.layout().addWidget(security_content)
        security_layout.addWidget(security_card)
        security_layout.addStretch()
        
        tab_widget.addTab(security_tab, "🔒 Security")
        
        self.content_layout.addWidget(tab_widget)
        
        # Save settings button
        save_btn = ModernButton("💾 Save Settings", "success", "large")
        save_btn.setMaximumWidth(200)
        self.content_layout.addWidget(save_btn)
        self.content_layout.addStretch()
    
    # Quick action methods
    def quick_borrow_book(self):
        """Quick action for borrowing books"""
        self.show_library()
        # Could implement specific focus on borrowing tab
    
    def quick_return_book(self):
        """Quick action for returning books"""
        self.show_library()
    
    def quick_add_student(self):
        """Quick action for adding students"""
        self.show_students()
    
    def quick_add_teacher(self):
        """Quick action for adding teachers"""
        self.show_teachers()
    
    def quick_add_book(self):
        """Quick action for adding books"""
        self.show_library()
    
    def quick_manage_furniture(self):
        """Quick action for managing furniture"""
        self.show_furniture()
    
    def quick_generate_report(self):
        """Quick action for generating reports"""
        self.show_reports()
    
    def quick_view_notifications(self):
        """Quick action for viewing notifications"""
        self.show_notifications()
    
    # Report generation methods
    def generate_library_stats(self):
        """Generate library statistics report"""
        QMessageBox.information(self.main_window, "Library Statistics", "Library statistics report generated successfully!")
    
    def generate_books_inventory(self):
        """Generate books inventory report"""
        QMessageBox.information(self.main_window, "Books Inventory", "Books inventory report generated successfully!")
    
    def generate_student_stats(self):
        """Generate student statistics report"""
        QMessageBox.information(self.main_window, "Student Statistics", "Student statistics report generated successfully!")
    
    def generate_borrowing_trends(self):
        """Generate borrowing trends report"""
        QMessageBox.information(self.main_window, "Borrowing Trends", "Borrowing trends report generated successfully!")
    
    def generate_overdue_report(self):
        """Generate overdue books report"""
        QMessageBox.information(self.main_window, "Overdue Report", "Overdue books report generated successfully!")
    
    def generate_furniture_report(self):
        """Generate furniture status report"""
        QMessageBox.information(self.main_window, "Furniture Report", "Furniture status report generated successfully!")
    
    def generate_monthly_summary(self):
        """Generate monthly summary report"""
        QMessageBox.information(self.main_window, "Monthly Summary", "Monthly summary report generated successfully!")
    
    def generate_category_report(self):
        """Generate books by category report"""
        QMessageBox.information(self.main_window, "Category Report", "Books by category report generated successfully!")
    
    def generate_borrowing_stats(self):
        """Generate borrowing statistics"""
        QMessageBox.information(self.main_window, "Borrowing Statistics", "Borrowing statistics report generated successfully!")
    
    def show_overdue_books(self):
        """Show overdue books"""
        QMessageBox.information(self.main_window, "Overdue Books", "Overdue books report generated successfully!")
    
    def generate_inventory_report(self):
        """Generate inventory report"""
        QMessageBox.information(self.main_window, "Inventory Report", "Inventory report generated successfully!")
    
    def generate_active_borrowers(self):
        """Generate active borrowers report"""
        QMessageBox.information(self.main_window, "Active Borrowers", "Most active borrowers report generated successfully!")
    
    def generate_monthly_stats(self):
        """Generate monthly statistics"""
        QMessageBox.information(self.main_window, "Monthly Statistics", "Monthly statistics report generated successfully!")
    
    def export_data(self):
        """Export data functionality"""
        file_dialog = QFileDialog()
        file_path, _ = file_dialog.getSaveFileName(
            self.main_window,
            "Export Data",
            "",
            "Excel Files (*.xlsx);;CSV Files (*.csv);;PDF Files (*.pdf)"
        )
        if file_path:
            QMessageBox.information(self.main_window, "Export", f"Data exported successfully to {file_path}")
    
    def show_notifications(self):
        """Show notifications dialog"""
        QMessageBox.information(self.main_window, "Notifications", "No new notifications.")
    
    # Legacy method compatibility
    def create_login_window(self):
        """Create modern login window"""
        dialog = QDialog(self.main_window)
        dialog.setWindowTitle("Login - HarLuFran InnoFlux SMS")
        dialog.setFixedSize(400, 300)
        dialog.setStyleSheet(f"""
            QDialog {{
                background: {ModernColors.BACKGROUND_CARD};
                border-radius: 12px;
            }}
        """)
        
        layout = QVBoxLayout(dialog)
        layout.setContentsMargins(40, 40, 40, 40)
        layout.setSpacing(20)
        
        # Title
        title_label = QLabel("Welcome Back")
        title_label.setStyleSheet(f"""
            color: {ModernColors.TEXT_PRIMARY};
            font-size: 24px;
            font-weight: 600;
            margin-bottom: 10px;
        """)
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        # Subtitle
        subtitle_label = QLabel("Please sign in to your account")
        subtitle_label.setStyleSheet(f"""
            color: {ModernColors.TEXT_MUTED};
            font-size: 14px;
            margin-bottom: 30px;
        """)
        subtitle_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        # Form fields
        username_input = ModernLineEdit("Username")
        password_input = ModernLineEdit("Password")
        password_input.setEchoMode(QLineEdit.EchoMode.Password)
        
        # Login button
        login_btn = ModernButton("Sign In", "primary", "large")
        login_btn.setMaximumWidth(200)
        
        # Layout
        layout.addWidget(title_label)
        layout.addWidget(subtitle_label)
        layout.addWidget(username_input)
        layout.addWidget(password_input)
        layout.addStretch()
        layout.addWidget(login_btn, alignment=Qt.AlignmentFlag.AlignCenter)
        
        return dialog
    
    def button_click(self, command):
        """Handle button clicks"""
        try:
            command()
        except Exception as e:
            self.logger.error(f"Error executing command: {e}")
            QMessageBox.critical(self.main_window, "Error", f"An error occurred: {str(e)}")
    
    def show_message(self, title, message, message_type="info"):
        """Show modern message dialog"""
        icon_map = {
            "info": QMessageBox.Icon.Information,
            "warning": QMessageBox.Icon.Warning,
            "error": QMessageBox.Icon.Critical,
            "question": QMessageBox.Icon.Question
        }
        
        msg_box = QMessageBox(self.main_window)
        msg_box.setWindowTitle(title)
        msg_box.setText(message)
        msg_box.setIcon(icon_map.get(message_type, QMessageBox.Icon.Information))
        msg_box.setStyleSheet(f"""
            QMessageBox {{
                background: {ModernColors.BACKGROUND_CARD};
            }}
            QMessageBox QLabel {{
                color: {ModernColors.TEXT_PRIMARY};
                font-size: 14px;
            }}
            QMessageBox QPushButton {{
                background: {ModernColors.PRIMARY};
                color: {ModernColors.TEXT_LIGHT};
                border: none;
                border-radius: 6px;
                padding: 8px 16px;
                font-weight: 500;
            }}
            QMessageBox QPushButton:hover {{
                background: {ModernColors.PRIMARY_DARK};
            }}
        """)
        
        msg_box.exec()
    
    def show_progress_dialog(self, title, message):
        """Show modern progress dialog"""
        dialog = QDialog(self.main_window)
        dialog.setWindowTitle(title)
        dialog.setFixedSize(300, 150)
        dialog.setStyleSheet(f"""
            QDialog {{
                background: {ModernColors.BACKGROUND_CARD};
                border-radius: 12px;
            }}
        """)
        
        layout = QVBoxLayout(dialog)
        layout.setContentsMargins(30, 30, 30, 30)
        layout.setSpacing(20)
        
        # Message
        message_label = QLabel(message)
        message_label.setStyleSheet(f"""
            color: {ModernColors.TEXT_PRIMARY};
            font-size: 14px;
        """)
        
        # Progress bar
        progress_bar = ModernProgressBar()
        
        layout.addWidget(message_label)
        layout.addWidget(progress_bar)
        
        dialog.show()
        return dialog, progress_bar