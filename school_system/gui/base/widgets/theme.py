"""
Theming Engine

A theming engine for dynamic theming support using QSS.
"""

from PyQt6.QtCore import QObject, pyqtSignal
from PyQt6.QtGui import QColor


class ThemeManager(QObject):
    """
    A theming engine for dynamic theming support.
    
    Features:
        - Light and dark mode support
        - Custom palette management
        - Dynamic theme switching
    """
    
    theme_changed = pyqtSignal(str)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self._themes = {
            "light": {
                # Modern web-style color palette
                "primary": "#2563eb",  # Modern blue
                "primary_hover": "#1d4ed8",
                "primary_pressed": "#1e40af",
                "secondary": "#64748b",  # Slate gray
                "success": "#10b981",  # Emerald green
                "warning": "#f59e0b",  # Amber
                "danger": "#ef4444",  # Red
                "background": "#f8fafc",  # Very light gray
                "surface": "#ffffff",  # White cards
                "surface_hover": "#f1f5f9",  # Light gray hover
                "text": "#1e293b",  # Dark slate
                "text_secondary": "#64748b",  # Medium gray
                "text_muted": "#94a3b8",  # Light gray
                "border": "#e2e8f0",  # Light border
                "border_focus": "#2563eb",  # Blue focus
                "shadow": "rgba(0, 0, 0, 0.08)",
                "shadow_hover": "rgba(0, 0, 0, 0.12)",
            },
            "dark": {
                # Modern dark theme palette
                "primary": "#3b82f6",  # Bright blue
                "primary_hover": "#2563eb",
                "primary_pressed": "#1d4ed8",
                "secondary": "#64748b",
                "success": "#10b981",
                "warning": "#f59e0b",
                "danger": "#ef4444",
                "background": "#0f172a",  # Very dark blue
                "surface": "#1e293b",  # Dark slate
                "surface_hover": "#334155",  # Medium dark
                "text": "#f1f5f9",  # Light gray
                "text_secondary": "#cbd5e1",  # Medium light
                "text_muted": "#94a3b8",  # Muted gray
                "border": "#334155",  # Dark border
                "border_focus": "#3b82f6",  # Blue focus
                "shadow": "rgba(0, 0, 0, 0.3)",
                "shadow_hover": "rgba(0, 0, 0, 0.4)",
            }
        }
        self._current_theme = "light"
    
    def set_theme(self, theme_name):
        """Set the current theme."""
        if theme_name in self._themes:
            self._current_theme = theme_name
            self.theme_changed.emit(theme_name)
        else:
            raise ValueError(f"Theme '{theme_name}' not found")
    
    def get_theme(self):
        """Get the current theme."""
        return self._current_theme
    
    def get_color(self, color_name):
        """Get a color from the current theme."""
        return self._themes[self._current_theme].get(color_name, "#000")
    
    def add_theme(self, theme_name, theme_dict):
        """Add a custom theme."""
        self._themes[theme_name] = theme_dict
    
    def generate_qss(self):
        """Generate comprehensive modern web-style QSS for the current theme."""
        theme = self._themes[self._current_theme]
        return f"""
            /* ===== BASE STYLES ===== */
            QWidget {{
                font-family: 'Segoe UI', -apple-system, BlinkMacSystemFont, 'Roboto', 'Helvetica Neue', Arial, sans-serif;
                font-size: 14px;
                color: {theme["text"]};
                background-color: {theme["background"]};
            }}
            
            /* ===== BUTTONS ===== */
            QPushButton {{
                background-color: {theme["primary"]};
                color: white;
                border: none;
                border-radius: 8px;
                padding: 10px 20px;
                font-size: 14px;
                font-weight: 500;
                min-width: 100px;
                min-height: 36px;
            }}
            QPushButton:hover {{
                background-color: {theme["primary_hover"]};
            }}
            QPushButton:pressed {{
                background-color: {theme["primary_pressed"]};
            }}
            QPushButton:disabled {{
                background-color: {theme["border"]};
                color: {theme["text_muted"]};
            }}
            QPushButton[buttonType="secondary"] {{
                background-color: {theme["secondary"]};
            }}
            QPushButton[buttonType="secondary"]:hover {{
                background-color: {theme["text_secondary"]};
            }}
            QPushButton[buttonType="success"] {{
                background-color: {theme["success"]};
            }}
            QPushButton[buttonType="danger"] {{
                background-color: {theme["danger"]};
            }}
            QPushButton[buttonType="outline"] {{
                background-color: transparent;
                border: 2px solid {theme["primary"]};
                color: {theme["primary"]};
            }}
            QPushButton[buttonType="outline"]:hover {{
                background-color: {theme["primary"]};
                color: white;
            }}
            
            /* ===== INPUT FIELDS ===== */
            QLineEdit, QTextEdit, QPlainTextEdit {{
                background-color: {theme["surface"]};
                color: {theme["text"]};
                border: 1px solid {theme["border"]};
                border-radius: 8px;
                padding: 10px 14px;
                font-size: 14px;
                selection-background-color: {theme["primary"]};
                selection-color: white;
            }}
            QLineEdit:hover, QTextEdit:hover, QPlainTextEdit:hover {{
                border-color: {theme["text_secondary"]};
            }}
            QLineEdit:focus, QTextEdit:focus, QPlainTextEdit:focus {{
                border: 2px solid {theme["border_focus"]};
                background-color: {theme["surface"]};
            }}
            QLineEdit:disabled, QTextEdit:disabled, QPlainTextEdit:disabled {{
                background-color: {theme["surface_hover"]};
                color: {theme["text_muted"]};
                border-color: {theme["border"]};
            }}
            
            /* ===== COMBOBOX ===== */
            QComboBox {{
                background-color: {theme["surface"]};
                color: {theme["text"]};
                border: 1px solid {theme["border"]};
                border-radius: 8px;
                padding: 10px 14px;
                font-size: 14px;
                min-height: 36px;
            }}
            QComboBox:hover {{
                border-color: {theme["text_secondary"]};
            }}
            QComboBox:focus {{
                border: 2px solid {theme["border_focus"]};
            }}
            QComboBox::drop-down {{
                border: none;
                width: 30px;
            }}
            QComboBox::down-arrow {{
                image: none;
                border-left: 5px solid transparent;
                border-right: 5px solid transparent;
                border-top: 6px solid {theme["text"]};
                width: 0;
                height: 0;
            }}
            QComboBox QAbstractItemView {{
                background-color: {theme["surface"]};
                border: 1px solid {theme["border"]};
                border-radius: 8px;
                selection-background-color: {theme["primary"]};
                selection-color: white;
                padding: 4px;
            }}
            
            /* ===== TABLES ===== */
            QTableWidget, CustomTableWidget {{
                background-color: {theme["surface"]};
                border: 1px solid {theme["border"]};
                border-radius: 12px;
                gridline-color: {theme["border"]};
                font-size: 14px;
                selection-background-color: {theme["primary"]};
                selection-color: white;
            }}
            QTableWidget::item, CustomTableWidget::item {{
                padding: 12px 16px;
                border: none;
            }}
            QTableWidget::item:selected, CustomTableWidget::item:selected {{
                background-color: {theme["primary"]};
                color: white;
            }}
            QTableWidget::item:hover, CustomTableWidget::item:hover {{
                background-color: {theme["surface_hover"]};
            }}
            QHeaderView::section {{
                background-color: {theme["surface"]};
                color: {theme["text"]};
                padding: 12px 16px;
                border: none;
                border-bottom: 2px solid {theme["border"]};
                font-weight: 600;
                font-size: 13px;
                text-transform: uppercase;
                letter-spacing: 0.5px;
            }}
            QHeaderView::section:first {{
                border-top-left-radius: 12px;
            }}
            QHeaderView::section:last {{
                border-top-right-radius: 12px;
            }}
            
            /* ===== CARDS ===== */
            QFrame[card="true"] {{
                background-color: {theme["surface"]};
                border: 1px solid {theme["border"]};
                border-radius: 12px;
                padding: 20px;
            }}
            QFrame[card="true"]:hover {{
                border-color: {theme["text_secondary"]};
            }}
            QGroupBox {{
                background-color: {theme["surface"]};
                border: 1px solid {theme["border"]};
                border-radius: 12px;
                padding: 20px;
                margin-top: 12px;
                font-weight: 600;
                font-size: 15px;
            }}
            QGroupBox::title {{
                subcontrol-origin: margin;
                subcontrol-position: top left;
                left: 16px;
                padding: 0 8px;
                color: {theme["text"]};
            }}
            
            /* ===== TABS ===== */
            QTabWidget::pane {{
                background-color: {theme["surface"]};
                border: 1px solid {theme["border"]};
                border-radius: 12px;
                padding: 20px;
            }}
            QTabBar::tab {{
                background-color: transparent;
                color: {theme["text_secondary"]};
                border: none;
                border-bottom: 2px solid transparent;
                padding: 12px 24px;
                font-size: 14px;
                font-weight: 500;
                margin-right: 4px;
            }}
            QTabBar::tab:hover {{
                color: {theme["text"]};
                background-color: {theme["surface_hover"]};
            }}
            QTabBar::tab:selected {{
                color: {theme["primary"]};
                border-bottom: 2px solid {theme["primary"]};
                background-color: {theme["surface"]};
            }}
            
            /* ===== SCROLLBARS ===== */
            QScrollBar:vertical {{
                background-color: {theme["surface"]};
                width: 12px;
                border: none;
                border-radius: 6px;
            }}
            QScrollBar::handle:vertical {{
                background-color: {theme["border"]};
                border-radius: 6px;
                min-height: 30px;
                margin: 2px;
            }}
            QScrollBar::handle:vertical:hover {{
                background-color: {theme["text_secondary"]};
            }}
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
                height: 0px;
            }}
            QScrollBar:horizontal {{
                background-color: {theme["surface"]};
                height: 12px;
                border: none;
                border-radius: 6px;
            }}
            QScrollBar::handle:horizontal {{
                background-color: {theme["border"]};
                border-radius: 6px;
                min-width: 30px;
                margin: 2px;
            }}
            QScrollBar::handle:horizontal:hover {{
                background-color: {theme["text_secondary"]};
            }}
            QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {{
                width: 0px;
            }}
            
            /* ===== SEARCH BOX ===== */
            SearchBox {{
                background-color: {theme["surface"]};
                border: 1px solid {theme["border"]};
                border-radius: 8px;
            }}
            
            /* ===== STATUS BAR ===== */
            ModernStatusBar {{
                background-color: {theme["surface"]};
                border-top: 1px solid {theme["border"]};
                padding: 8px 16px;
                font-size: 13px;
                color: {theme["text_secondary"]};
            }}
            
            /* ===== PROGRESS BAR ===== */
            QProgressBar {{
                border: none;
                border-radius: 8px;
                background-color: {theme["surface_hover"]};
                text-align: center;
                color: {theme["text"]};
                font-size: 13px;
                font-weight: 500;
                min-height: 8px;
            }}
            QProgressBar::chunk {{
                background-color: {theme["primary"]};
                border-radius: 8px;
            }}
            
            /* ===== CHECKBOX & RADIO ===== */
            QCheckBox, QRadioButton {{
                color: {theme["text"]};
                font-size: 14px;
                spacing: 8px;
            }}
            QCheckBox::indicator, QRadioButton::indicator {{
                width: 20px;
                height: 20px;
                border: 2px solid {theme["border"]};
                border-radius: 4px;
                background-color: {theme["surface"]};
            }}
            QCheckBox::indicator:hover, QRadioButton::indicator:hover {{
                border-color: {theme["primary"]};
            }}
            QCheckBox::indicator:checked, QRadioButton::indicator:checked {{
                background-color: {theme["primary"]};
                border-color: {theme["primary"]};
            }}
            QRadioButton::indicator {{
                border-radius: 10px;
            }}
            
            /* ===== MENU BAR ===== */
            QMenuBar {{
                background-color: {theme["surface"]};
                color: {theme["text"]};
                border-bottom: 1px solid {theme["border"]};
                padding: 8px;
            }}
            QMenuBar::item {{
                padding: 8px 16px;
                border-radius: 6px;
            }}
            QMenuBar::item:selected {{
                background-color: {theme["surface_hover"]};
            }}
            QMenu {{
                background-color: {theme["surface"]};
                border: 1px solid {theme["border"]};
                border-radius: 8px;
                padding: 4px;
            }}
            QMenu::item {{
                padding: 8px 24px;
                border-radius: 6px;
            }}
            QMenu::item:selected {{
                background-color: {theme["primary"]};
                color: white;
            }}
            
            /* ===== TOOL BUTTONS ===== */
            QToolButton {{
                background-color: transparent;
                color: {theme["text"]};
                border: none;
                border-radius: 8px;
                padding: 8px 12px;
                font-size: 14px;
            }}
            QToolButton:hover {{
                background-color: {theme["surface_hover"]};
            }}
            QToolButton:pressed {{
                background-color: {theme["border"]};
            }}
        """