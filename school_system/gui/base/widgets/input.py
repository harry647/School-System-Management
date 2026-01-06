"""
Modern Input Widget

A reusable, stylish input widget with consistent theming and animations.
"""

from PyQt6.QtWidgets import QLineEdit
from PyQt6.QtCore import QPropertyAnimation, QEasingCurve, Qt
from PyQt6.QtGui import QColor


class ModernInput(QLineEdit):
    """
    A modern input widget with animations and theming support.
    
    Features:
        - Focus and hover state animations
        - Customizable colors and styles
        - Smooth transitions
    """
    
    def __init__(self, placeholder_text="", parent=None):
        super().__init__("", parent)
        self.setPlaceholderText(placeholder_text)
        
        # Default styling
        self.setStyleSheet("""
            QLineEdit {
                background-color: #f5f5f5;
                color: #333;
                border: 1px solid #ccc;
                border-radius: 4px;
                padding: 8px 12px;
                font-size: 14px;
            }
            QLineEdit:hover {
                border: 1px solid #888;
            }
            QLineEdit:focus {
                border: 1px solid #4CAF50;
                background-color: #fff;
                outline: 2px solid #4CAF50;
            }
        """)
        
        # Keyboard navigation and accessibility
        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        self.setAccessibleName(placeholder_text)
        self.setAccessibleDescription(f"Input field: {placeholder_text}")
        
        # Connect signals for animations
        self.enterEvent = self._on_hover_enter
        self.leaveEvent = self._on_hover_leave
    
    def _on_hover_enter(self, event):
        """Handle hover enter animation."""
        self._animate_border_color(QColor(136, 136, 136))
    
    def _on_hover_leave(self, event):
        """Handle hover leave animation."""
        if not self.hasFocus():
            self._animate_border_color(QColor(204, 204, 204))
    
    def _animate_border_color(self, color):
        """Animate the border color."""
        animation = QPropertyAnimation(self, b"styleSheet")
        animation.setDuration(150)
        animation.setEasingCurve(QEasingCurve.Type.InOutQuad)
        animation.setStartValue(self.styleSheet())
        animation.setEndValue(
            f"""
                QLineEdit {{
                    background-color: #f5f5f5;
                    color: #333;
                    border: 1px solid {color.name()};
                    border-radius: 4px;
                    padding: 8px 12px;
                    font-size: 14px;
                }}
                QLineEdit:hover {{
                    border: 1px solid #888;
                }}
                QLineEdit:focus {{
                    border: 1px solid #4CAF50;
                    background-color: #fff;
                }}
            """
        )
        animation.start()
    
    def focusInEvent(self, event):
        """Override focus in event for custom styling."""
        super().focusInEvent(event)
        self.setStyleSheet("""
            QLineEdit {
                background-color: #fff;
                color: #333;
                border: 1px solid #4CAF50;
                border-radius: 4px;
                padding: 8px 12px;
                font-size: 14px;
            }
        """)
    
    def focusOutEvent(self, event):
        """Override focus out event for custom styling."""
        super().focusOutEvent(event)
        self.setStyleSheet("""
            QLineEdit {
                background-color: #f5f5f5;
                color: #333;
                border: 1px solid #ccc;
                border-radius: 4px;
                padding: 8px 12px;
                font-size: 14px;
            }
            QLineEdit:hover {
                border: 1px solid #888;
            }
        """)