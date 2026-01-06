"""
Modern Status Bar Widget

A dynamic status bar with progress indicators and notifications.
"""

from PyQt6.QtWidgets import QStatusBar, QProgressBar, QLabel, QFrame, QHBoxLayout, QWidget
from PyQt6.QtCore import Qt, QTimer, pyqtSignal
from PyQt6.QtGui import QColor
from typing import Optional


class ModernStatusBar(QStatusBar):
    """
    A modern status bar with progress indicators and notifications.
    
    Features:
        - Progress indicators for ongoing operations
        - Temporary and permanent messages
        - Customizable styling
        - Accessibility support
    """
    
    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__(parent)
        
        # Configure status bar
        self.setSizeGripEnabled(True)
        self.setStyleSheet("""
            ModernStatusBar {
                padding: 4px 8px;
                font-size: 13px;
            }
        """)
        
        # Accessibility
        self.setAccessibleName("Status Bar")
        self.setAccessibleDescription("Application status and progress information")
        
        # Create progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setValue(0)
        self.progress_bar.setTextVisible(True)
        self.progress_bar.setStyleSheet("""
            QProgressBar {
                border: 1px solid #ddd;
                border-radius: 4px;
                background-color: #fff;
                text-align: center;
                min-width: 150px;
                max-width: 200px;
            }
            QProgressBar::chunk {
                background-color: #4CAF50;
                border-radius: 4px;
            }
        """)
        self.progress_bar.setAccessibleName("Progress Bar")
        self.progress_bar.setAccessibleDescription("Operation progress indicator")
        
        # Add progress bar to status bar
        self.addPermanentWidget(self.progress_bar)
        
        # Create message label
        self.message_label = QLabel()
        self.message_label.setStyleSheet("""
            QLabel {
                padding: 0 8px;
                color: #333;
            }
        """)
        self.message_label.setAccessibleName("Status Message")
        self.message_label.setAccessibleDescription("Current status message")
        
        # Add message label to status bar
        self.addWidget(self.message_label)
        
        # Timer for temporary messages
        self._message_timer = QTimer()
        self._message_timer.setSingleShot(True)
        self._message_timer.timeout.connect(self.clear_message)
    
    def show_progress(self, value: int, max_value: int = 100):
        """
        Show progress in the status bar.
        
        Args:
            value: Current progress value
            max_value: Maximum progress value (default: 100)
        """
        self.progress_bar.setRange(0, max_value)
        self.progress_bar.setValue(value)
        self.progress_bar.setVisible(True)
    
    def hide_progress(self):
        """Hide the progress bar."""
        self.progress_bar.setVisible(False)
    
    def show_message(self, message: str, timeout: int = 0):
        """
        Show a message in the status bar.
        
        Args:
            message: Message to display
            timeout: Duration in milliseconds (0 for permanent)
        """
        self.message_label.setText(message)
        
        if timeout > 0:
            self._message_timer.start(timeout)
    
    def clear_message(self):
        """Clear the current status message."""
        self.message_label.clear()
    
    def show_temporary_message(self, message: str, duration: int = 3000):
        """
        Show a temporary message.
        
        Args:
            message: Message to display
            duration: Duration in milliseconds (default: 3000)
        """
        self.show_message(message, duration)
    
    def show_permanent_message(self, message: str):
        """
        Show a permanent message.
        
        Args:
            message: Message to display
        """
        self.show_message(message, 0)

    def apply_theme(self, theme_name: str):
        """
        Apply theme to the status bar.
        
        Args:
            theme_name: Name of the theme to apply
        """
        # The status bar styling is handled by QSS from the theme manager,
        # but we can add theme-specific logic here if needed in the future
        pass


class ProgressIndicator(QWidget):
    """
    A circular progress indicator widget.
    
    Features:
        - Circular progress animation
        - Customizable colors
        - Size control
    """
    
    def __init__(self, size: int = 24, parent: Optional[QWidget] = None):
        super().__init__(parent)
        
        self._size = size
        self._value = 0
        self._max_value = 100
        self._color = QColor("#4CAF50")
        
        # Configure widget
        self.setFixedSize(size, size)
        self.setStyleSheet("""
            ProgressIndicator {
                background-color: transparent;
            }
        """)
        
        # Accessibility
        self.setAccessibleName("Progress Indicator")
        self.setAccessibleDescription("Circular progress indicator")
    
    def set_value(self, value: int):
        """
        Set the current progress value.
        
        Args:
            value: Current progress value
        """
        self._value = value
        self.update()
    
    def set_max_value(self, max_value: int):
        """
        Set the maximum progress value.
        
        Args:
            max_value: Maximum progress value
        """
        self._max_value = max_value
        self.update()
    
    def set_color(self, color: QColor):
        """
        Set the progress indicator color.
        
        Args:
            color: Color for the progress indicator
        """
        self._color = color
        self.update()
    
    def paintEvent(self, event):
        """Override paint event to draw the progress indicator."""
        import math
        from PyQt6.QtGui import QPainter, QPen, QBrush
        
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        # Draw background circle
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(QColor(240, 240, 240))
        painter.drawEllipse(0, 0, self._size, self._size)
        
        # Calculate progress
        progress = min(max(self._value / self._max_value, 0), 1)
        angle = int(360 * progress)
        
        # Draw progress arc
        painter.setPen(QPen(self._color, 2))
        painter.setBrush(QBrush(self._color))
        painter.drawPie(2, 2, self._size - 4, self._size - 4, 90 * 16, -angle * 16)
        
        painter.end()