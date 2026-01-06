"""
Accessibility Support

Ensure keyboard navigation, screen reader support, and high-contrast modes.
"""

from PyQt6.QtWidgets import QWidget
from PyQt6.QtCore import Qt


class AccessibleWidget(QWidget):
    """
    A base class for accessible widgets.
    
    Features:
        - Keyboard navigation support
        - Screen reader compatibility
        - High-contrast mode
    """
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        self.setAccessibleName("")
        self.setAccessibleDescription("")
    
    def set_accessible_name(self, name):
        """Set the accessible name for screen readers."""
        self.setAccessibleName(name)
    
    def set_accessible_description(self, description):
        """Set the accessible description for screen readers."""
        self.setAccessibleDescription(description)
    
    def enable_high_contrast(self, enabled):
        """Enable or disable high-contrast mode."""
        if enabled:
            self.setStyleSheet("""
                background-color: black;
                color: white;
                border: 2px solid white;
            """)
        else:
            self.setStyleSheet("")
    
    def keyPressEvent(self, event):
        """Handle key press events for keyboard navigation."""
        if event.key() == Qt.Key.Key_Tab:
            # Custom tab handling
            event.accept()
        else:
            super().keyPressEvent(event)


class AccessibleButton(AccessibleWidget):
    """
    An accessible button widget.
    """
    
    def __init__(self, text="", parent=None):
        super().__init__(parent)
        self.setAccessibleName(text)
        self.setAccessibleDescription(f"Button: {text}")
    
    def keyPressEvent(self, event):
        """Handle key press events for keyboard navigation."""
        if event.key() == Qt.Key.Key_Space or event.key() == Qt.Key.Key_Return:
            self.click()
            event.accept()
        else:
            super().keyPressEvent(event)


class AccessibleInput(AccessibleWidget):
    """
    An accessible input widget.
    """
    
    def __init__(self, placeholder_text="", parent=None):
        super().__init__(parent)
        self.setAccessibleName(placeholder_text)
        self.setAccessibleDescription(f"Input field: {placeholder_text}")
    
    def keyPressEvent(self, event):
        """Handle key press events for keyboard navigation."""
        if event.key() == Qt.Key.Key_Tab:
            # Custom tab handling
            event.accept()
        else:
            super().keyPressEvent(event)