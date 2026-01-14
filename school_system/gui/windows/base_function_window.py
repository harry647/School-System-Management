"""
Base Function Window

A base class for dedicated function windows that provides consistent styling
and structure for single-purpose windows.
"""

from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QFrame
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont
from typing import Optional

from school_system.gui.base.base_window import BaseWindow
from school_system.config.logging import logger


class BaseFunctionWindow(BaseWindow):
    """
    Base class for dedicated function windows.
    
    Provides consistent structure and styling for single-purpose windows
    that focus on one specific function or operation.
    """
    
    def __init__(self, title: str, parent=None, current_user: str = "", current_role: str = ""):
        """
        Initialize the base function window.
        
        Args:
            title: Window title
            parent: Parent window
            current_user: Current logged-in user
            current_role: Current user role
        """
        super().__init__(title, parent)
        
        self.current_user = current_user
        self.current_role = current_role
        
        # Set minimum size for function windows
        self.setMinimumSize(900, 600)
        
        # Apply modern styling
        self._apply_modern_styling()
        
        # Setup header
        self._setup_header()
        
        logger.info(f"Function window '{title}' initialized")
    
    def _apply_modern_styling(self):
        """Apply modern web-style styling to the function window."""
        theme_manager = self.get_theme_manager()
        theme = theme_manager._themes[self.get_theme()]
        
        self.setStyleSheet(f"""
            /* Base styling */
            QWidget {{
                font-family: 'Segoe UI', -apple-system, BlinkMacSystemFont, 'Roboto', sans-serif;
                font-size: 14px;
                background-color: {theme["background"]};
                color: {theme["text"]};
            }}
            
            /* Window styling */
            BaseFunctionWindow {{
                background-color: {theme["background"]};
            }}
            
            /* Button styling */
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
                border-color: {theme["text_secondary"]};
            }}
            
            /* Input field styling */
            QLineEdit, QComboBox, QTextEdit, QPlainTextEdit {{
                padding: 10px 14px;
                border: 1px solid {theme["border"]};
                border-radius: 8px;
                background-color: {theme["surface"]};
                color: {theme["text"]};
                min-height: 36px;
            }}
            
            QLineEdit:hover, QComboBox:hover, QTextEdit:hover, QPlainTextEdit:hover {{
                border-color: {theme["text_secondary"]};
            }}
            
            QLineEdit:focus, QComboBox:focus, QTextEdit:focus, QPlainTextEdit:focus {{
                border: 2px solid {theme["border_focus"]};
                background-color: {theme["surface"]};
            }}
            
            /* Table styling */
            QTableView, QTableWidget {{
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
            
            QTableView::item:selected, QTableWidget::item:selected {{
                background-color: {theme["primary"]};
                color: white;
            }}
            
            QTableView::item:hover, QTableWidget::item:hover {{
                background-color: {theme["surface_hover"]};
            }}
            
            /* Card styling */
            QFrame[card="true"] {{
                background-color: {theme["surface"]};
                border: 1px solid {theme["border"]};
                border-radius: 12px;
                padding: 24px;
            }}
            
            QGroupBox {{
                border: 1px solid {theme["border"]};
                border-radius: 12px;
                background-color: {theme["surface"]};
                margin-top: 12px;
                padding: 20px;
            }}
            
            QGroupBox::title {{
                subcontrol-origin: margin;
                left: 16px;
                padding: 0 8px;
                color: {theme["text"]};
                font-weight: 600;
                font-size: 15px;
            }}
        """)
    
    def _setup_header(self):
        """Setup the window header with title and optional actions."""
        theme_manager = self.get_theme_manager()
        theme = theme_manager._themes[self.get_theme()]
        
        header_frame = QFrame()
        header_frame.setProperty("header", "true")
        header_frame.setFixedHeight(80)
        header_frame.setStyleSheet(f"""
            QFrame[header="true"] {{
                background-color: {theme["surface"]};
                border-bottom: 1px solid {theme["border"]};
                padding: 0 24px;
            }}
        """)
        
        header_layout = QHBoxLayout(header_frame)
        header_layout.setContentsMargins(24, 0, 24, 0)
        header_layout.setSpacing(16)
        
        # Title
        title_label = QLabel(self.windowTitle())
        title_font = QFont("Segoe UI", 20, QFont.Weight.Bold)
        title_label.setFont(title_font)
        title_label.setStyleSheet(f"color: {theme["text"]};")
        header_layout.addWidget(title_label)
        
        header_layout.addStretch()
        
        # Store header for subclasses to add action buttons
        self.header_layout = header_layout
        self.header_frame = header_frame
        
        # Add header to content
        self.add_widget_to_content(header_frame)
    
    def add_header_action(self, button: QPushButton):
        """Add an action button to the header."""
        self.header_layout.addWidget(button)
    
    def setup_content(self):
        """
        Setup the main content area.
        
        Subclasses should override this method to add their specific content.
        """
        pass
