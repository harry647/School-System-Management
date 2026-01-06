"""
Modern Button Widget

A reusable, stylish button widget with consistent theming, animations, and hover/active states.
"""

from PyQt6.QtWidgets import QPushButton
from PyQt6.QtCore import QPropertyAnimation, QEasingCurve, pyqtProperty, QSize, Qt
from PyQt6.QtGui import QColor


class ModernButton(QPushButton):
    """
    A modern button widget with animations and theming support.
    
    Features:
        - Hover and active state animations
        - Customizable colors and styles
        - Smooth transitions
    """
    
    def __init__(self, text="", parent=None):
        super().__init__(text, parent)
        self._animation = QPropertyAnimation(self, b"geometry")
        self._animation.setDuration(150)
        self._animation.setEasingCurve(QEasingCurve.Type.InOutQuad)
        
        # Default styling
        self.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50;
                color: white;
                border: none;
                border-radius: 4px;
                padding: 8px 16px;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
            QPushButton:pressed {
                background-color: #3d8b40;
            }
            QPushButton:focus {
                outline: 2px solid #45a049;
            }
        """)
        
        # Keyboard navigation and accessibility
        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        self.setAccessibleName(text)
        self.setAccessibleDescription(f"Button: {text}")
        
        # Connect signals for animations
        self.enterEvent = self._on_hover_enter
        self.leaveEvent = self._on_hover_leave
    
    def _on_hover_enter(self, event):
        """Handle hover enter animation."""
        self._animate_scale(1.05)
    
    def _on_hover_leave(self, event):
        """Handle hover leave animation."""
        self._animate_scale(1.0)
    
    def _animate_scale(self, factor):
        """Animate the button scale."""
        current_geometry = self.geometry()
        target_width = int(current_geometry.width() * factor)
        target_height = int(current_geometry.height() * factor)
        
        self._animation.setStartValue(current_geometry)
        self._animation.setEndValue(
            current_geometry.adjusted(
                0, 0, target_width - current_geometry.width(),
                target_height - current_geometry.height()
            )
        )
        self._animation.start()
    
    def set_custom_style(self, bg_color, hover_color, pressed_color, text_color="white"):
        """Set custom colors for the button."""
        self.setStyleSheet(f"""
            QPushButton {{
                background-color: {bg_color};
                color: {text_color};
                border: none;
                border-radius: 4px;
                padding: 8px 16px;
                font-size: 14px;
            }}
            QPushButton:hover {{
                background-color: {hover_color};
            }}
            QPushButton:pressed {{
                background-color: {pressed_color};
            }}
        """)
    
    def sizeHint(self):
        """Override size hint for better default sizing."""
        return QSize(100, 40)