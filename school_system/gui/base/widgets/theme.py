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
                "primary": "#4CAF50",
                "secondary": "#45a049",
                "background": "#f5f5f5",
                "text": "#333",
                "border": "#ccc",
            },
            "dark": {
                "primary": "#4CAF50",
                "secondary": "#45a049",
                "background": "#333",
                "text": "#f5f5f5",
                "border": "#666",
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
        """Generate QSS for the current theme."""
        theme = self._themes[self._current_theme]
        return f"""
            QWidget {{
                background-color: {theme["background"]};
                color: {theme["text"]};
            }}
            QPushButton {{
                background-color: {theme["primary"]};
                color: white;
                border: none;
                border-radius: 4px;
                padding: 8px 16px;
                font-size: 14px;
            }}
            QPushButton:hover {{
                background-color: {theme["secondary"]};
            }}
            QLineEdit {{
                background-color: {theme["background"]};
                color: {theme["text"]};
                border: 1px solid {theme["border"]};
                border-radius: 4px;
                padding: 8px 12px;
                font-size: 14px;
            }}
            QLineEdit:focus {{
                border: 1px solid {theme["primary"]};
            }}
            /* Custom Table Widget */
            CustomTableWidget {{
                background-color: {theme["background"]};
                border: 1px solid {theme["border"]};
                border-radius: 4px;
                font-size: 14px;
            }}
            CustomTableWidget::item {{
                padding: 8px;
            }}
            CustomTableWidget::item:selected {{
                background-color: {theme["primary"]};
                color: white;
            }}
            QHeaderView::section {{
                background-color: {theme["background"]};
                padding: 8px;
                border: 1px solid {theme["border"]};
                font-weight: bold;
            }}
            /* Search Box */
            SearchBox {{
                background-color: {theme["background"]};
                border-radius: 4px;
            }}
            /* Status Bar */
            ModernStatusBar {{
                background-color: {theme["background"]};
                border-top: 1px solid {theme["border"]};
                padding: 4px 8px;
                font-size: 13px;
            }}
            /* Progress Bar */
            QProgressBar {{
                border: 1px solid {theme["border"]};
                border-radius: 4px;
                background-color: {theme["background"]};
                text-align: center;
                min-width: 150px;
                max-width: 200px;
            }}
            QProgressBar::chunk {{
                background-color: {theme["primary"]};
                border-radius: 4px;
            }}
        """