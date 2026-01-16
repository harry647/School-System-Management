"""
Modern Card Widget

A reusable, stylish card widget with consistent theming and animations.
"""

from PyQt6.QtWidgets import QFrame, QVBoxLayout, QLabel
from PyQt6.QtCore import QPropertyAnimation, QEasingCurve, Qt
from PyQt6.QtGui import QColor


class ModernCard(QFrame):
    """
    A modern card widget with animations and theming support.
    
    Features:
        - Hover and active state animations
        - Customizable colors and styles
        - Smooth transitions
    """
    
    def __init__(self, title="", content="", parent=None):
        super().__init__(parent)
        self.setFrameShape(QFrame.Shape.StyledPanel)
        self.setFrameShadow(QFrame.Shadow.Raised)
        
        # Layout
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(12, 12, 12, 12)
        self.layout.setSpacing(8)
        
        # Title label
        self.title_label = QLabel(title)
        self.title_label.setStyleSheet("""
            font-size: 16px;
            font-weight: bold;
            color: #333;
        """)
        self.layout.addWidget(self.title_label)
        
        # Content label
        self.content_label = QLabel(content)
        self.content_label.setStyleSheet("""
            font-size: 14px;
            color: #666;
        """)
        self.layout.addWidget(self.content_label)
        
        # Default styling
        self.setStyleSheet("""
            ModernCard {
                background-color: #fff;
                border: 1px solid #ddd;
                border-radius: 8px;
            }
            ModernCard:focus {
                border: 1px solid #4CAF50;
                outline: 2px solid #4CAF50;
            }
        """)
        
        # Keyboard navigation and accessibility
        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        self.setAccessibleName(title)
        self.setAccessibleDescription(f"Card: {title}")
        
        # Connect signals for animations
        self.enterEvent = self._on_hover_enter
        self.leaveEvent = self._on_hover_leave
    
    def _on_hover_enter(self, event):
        """Handle hover enter animation."""
        self._animate_shadow(20)
    
    def _on_hover_leave(self, event):
        """Handle hover leave animation."""
        self._animate_shadow(10)
    
    def _animate_shadow(self, radius):
        """Animate the shadow effect."""
        animation = QPropertyAnimation(self, b"styleSheet")
        animation.setDuration(150)
        animation.setEasingCurve(QEasingCurve.Type.InOutQuad)
        animation.setStartValue(self.styleSheet())
        animation.setEndValue(
            f"""
                ModernCard {{
                    background-color: #fff;
                    border: 1px solid #ddd;
                    border-radius: 8px;
                    box-shadow: 0 0 {radius}px rgba(0, 0, 0, 0.1);
                }}
            """
        )
        animation.start()
    
    def set_title(self, title):
        """Set the card title."""
        self.title_label.setText(title)
    
    def set_content(self, content):
        """Set the card content."""
        self.content_label.setText(content)
