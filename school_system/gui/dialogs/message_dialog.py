"""
Message Dialog Implementation for School System GUI Framework

This module provides a comprehensive message dialog that extends the BaseDialog
class with advanced message display capabilities.

Features:
    - Multiple message types (info, warning, error, success)
    - Rich text and HTML message support
    - Theming support through BaseDialog
    - Accessibility compliance
    - Event-driven architecture
    - Customizable icons and styling
"""

from PyQt6.QtWidgets import QLabel, QVBoxLayout, QHBoxLayout, QFrame, QDialogButtonBox
from PyQt6.QtCore import Qt, QSize
from PyQt6.QtGui import QIcon, QPixmap
import os

from school_system.gui.base.base_dialog import BaseDialog
from school_system.config.logging import logger
from school_system.config.settings import get_settings


class MessageDialog(BaseDialog):
    """
    Enhanced message dialog with comprehensive message display capabilities.
    
    This dialog extends BaseDialog to provide specialized functionality
    for displaying various types of messages to users.
    
    Features:
        - Multiple message types (info, warning, error, success)
        - Custom icons for different message types
        - Rich text and HTML support
        - Theming inheritance from parent window
        - Full accessibility compliance
        - Event-driven message handling
        - Support for detailed message content
    """
    
    # Message types
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    SUCCESS = "success"
    
    def __init__(
        self,
        title: str = "Message",
        message: str = "",
        parent=None,
        message_type: str = "info",
        rich_text: bool = False,
        show_icon: bool = True,
        button_text: str = "OK",
        scrollable: bool = False,
        resizable: bool = False
    ):
        """
        Initialize the message dialog.
        
        Args:
            title: Dialog title
            message: Message to display
            parent: Parent widget
            message_type: Type of message (info, warning, error, success)
            rich_text: Whether to enable rich text formatting
            show_icon: Whether to show message type icon
            button_text: Text for the OK button
            scrollable: Whether to make content area scrollable
            resizable: Whether to make dialog resizable
        """
        super().__init__(
            title=title,
            parent=parent,
            standard_buttons=None,  # We'll add custom buttons
            scrollable=scrollable
        )
        
        # Make dialog resizable if requested
        if resizable:
            self.setMinimumSize(400, 200)
            self.setSizeGripEnabled(True)
        
        # Store configuration
        self._message = message
        self._message_type = message_type
        self._rich_text = rich_text
        self._show_icon = show_icon
        self._button_text = button_text
        
        # Initialize UI
        self._initialize_ui()
        
        # Connect signals
        self._connect_signals()
        
        logger.info(f"MessageDialog '{title}' initialized with type: {message_type}")
        
        # Log the message content based on message type
        if message_type == MessageDialog.ERROR:
            logger.error(f"Error: {message}")
        elif message_type == MessageDialog.WARNING:
            logger.warning(f"Warning: {message}")
        elif message_type == MessageDialog.INFO:
            logger.info(f"Info: {message}")
        elif message_type == MessageDialog.SUCCESS:
            logger.info(f"Success: {message}")
    
    def _initialize_ui(self):
        """Initialize the user interface components."""
        # Main content layout
        content_layout = QVBoxLayout()
        content_layout.setSpacing(12)
        content_layout.setContentsMargins(0, 0, 0, 0)
        
        # Icon and message container
        message_container = QHBoxLayout()
        message_container.setSpacing(12)
        
        # Add icon if enabled
        if self._show_icon:
            self._icon_label = QLabel()
            self._set_message_icon()
            self._icon_label.setAccessibleName(f"{self._message_type} icon")
            message_container.addWidget(self._icon_label)
        
        # Message content
        self._message_label = QLabel(self._message)
        if self._rich_text:
            self._message_label.setTextFormat(Qt.TextFormat.RichText)
        else:
            self._message_label.setTextFormat(Qt.TextFormat.PlainText)
            
        self._message_label.setWordWrap(True)
        self._message_label.setStyleSheet(f"""
            font-size: 14px;
            color: {self._theme_manager.get_color('text')};
            padding: {10 if self._show_icon else 0}px;
        """)
        self._message_label.setAccessibleName("Message content")
        self._message_label.setAccessibleDescription("Message dialog content")
        
        message_container.addWidget(self._message_label, 1)
        content_layout.addLayout(message_container)
        
        # Add content layout to dialog
        self.add_content_layout(content_layout)
        
        # Create and add custom button using enhanced BaseDialog method
        self._ok_button = self.create_button(self._button_text, "primary")
        self._ok_button.setAccessibleName(f"{self._button_text} button")
        
        # Add button to button box
        self._button_box.addButton(self._ok_button, QDialogButtonBox.ButtonRole.AcceptRole)
        
        # Register button for centralized management
        self.register_widget("ok_button", self._ok_button)
        
        # Apply message type styling
        self._apply_message_type_styling()
    
    def _set_message_icon(self):
        """Set the appropriate icon based on message type."""
        icon_path = ""
        
        # Use centralized path management for icons
        settings = get_settings()
        icon_base = settings.resolve_path("school_system/gui/resources/icons")
        
        if self._message_type == self.INFO:
            icon_path = os.path.join(icon_base, "info.png")
        elif self._message_type == self.WARNING:
            icon_path = os.path.join(icon_base, "warning.png")
        elif self._message_type == self.ERROR:
            icon_path = os.path.join(icon_base, "error.png")
        elif self._message_type == self.SUCCESS:
            icon_path = os.path.join(icon_base, "success.png")
        
        if icon_path:
            try:
                pixmap = QIcon(icon_path).pixmap(QSize(32, 32))
                self._icon_label.setPixmap(pixmap)
            except Exception as e:
                logger.warning(f"Failed to load icon {icon_path}: {str(e)}")
                self._icon_label.setText(self._get_icon_fallback_text())
    
    def _get_icon_fallback_text(self) -> str:
        """Get fallback text for icon display."""
        if self._message_type == self.INFO:
            return "ℹ️"
        elif self._message_type == self.WARNING:
            return "⚠️"
        elif self._message_type == self.ERROR:
            return "❌"
        elif self._message_type == self.SUCCESS:
            return "✅"
        return ""
    
    def _apply_button_theme(self):
        """Apply theme-specific styling to button using enhanced BaseDialog functionality."""
        # Button is already themed through the create_button method
        # Just ensure it inherits the current theme
        current_theme = self.get_theme()
        self._ok_button.apply_theme(current_theme)
    
    def _apply_message_type_styling(self):
        """Apply styling based on message type."""
        # Get appropriate colors for message type
        if self._message_type == self.INFO:
            border_color = self._theme_manager.get_color('info')
        elif self._message_type == self.WARNING:
            border_color = self._theme_manager.get_color('warning')
        elif self._message_type == self.ERROR:
            border_color = self._theme_manager.get_color('error')
        elif self._message_type == self.SUCCESS:
            border_color = self._theme_manager.get_color('success')
        else:
            border_color = self._theme_manager.get_color('border')
        
        # Apply border styling to content frame
        self._content_frame.setStyleSheet(f"""
            border-left: 4px solid {border_color};
            background-color: {self._theme_manager.get_color('background')};
        """)
    
    def _connect_signals(self):
        """Connect signals for button actions."""
        self._ok_button.clicked.connect(self.accept)
        
        # Connect theme change signals
        if hasattr(self._theme_manager, 'theme_changed'):
            self._theme_manager.theme_changed.connect(self._on_theme_changed)
    
    def _on_theme_changed(self, theme_name: str):
        """Handle theme changes."""
        self._apply_button_theme()
        self._apply_message_type_styling()
    
    def set_message(self, message: str):
        """
        Set or update the message content.
        
        Args:
            message: New message content
        """
        self._message = message
        self._message_label.setText(message)
        logger.debug(f"Message updated: {message[:50]}...")
    
    def set_message_type(self, message_type: str):
        """
        Set the message type and update styling.
        
        Args:
            message_type: Type of message (info, warning, error, success)
        """
        self._message_type = message_type
        if self._show_icon:
            self._set_message_icon()
        self._apply_message_type_styling()
    
    def enable_rich_text(self, enabled: bool = True):
        """
        Enable or disable rich text formatting.
        
        Args:
            enabled: Whether to enable rich text
        """
        self._rich_text = enabled
        if enabled:
            self._message_label.setTextFormat(Qt.TextFormat.RichText)
        else:
            self._message_label.setTextFormat(Qt.TextFormat.PlainText)
    
    def show_icon(self, show: bool = True):
        """
        Show or hide the message type icon.
        
        Args:
            show: Whether to show the icon
        """
        self._show_icon = show
        # This would require rebuilding the layout to properly show/hide icon
        # For simplicity, we'll just show/hide the icon label
        if hasattr(self, '_icon_label'):
            self._icon_label.setVisible(show)
    
    def set_button_text(self, text: str):
        """
        Set the button text.
        
        Args:
            text: New button text
        """
        self._button_text = text
        self._ok_button.setText(text)
        self._ok_button.setAccessibleName(f"{text} button")
    
    def showEvent(self, event):
        """
        Handle dialog show events.
        
        Args:
            event: Show event
        """
        super().showEvent(event)
        # Focus the OK button by default for better UX
        self._ok_button.setFocus()
        logger.debug(f"MessageDialog '{self.windowTitle()}' shown")
    
    def accept(self):
        """Handle dialog acceptance."""
        logger.debug(f"MessageDialog '{self.windowTitle()}' accepted")
        super().accept()
    
    def reject(self):
        """Handle dialog rejection."""
        logger.debug(f"MessageDialog '{self.windowTitle()}' rejected")
        super().reject()
    
    # Expose QDialog methods for compatibility
    def sizeGripEnabled(self) -> bool:
        """Return whether the size grip is enabled."""
        return super().isSizeGripEnabled()
    
    def setSizeGripEnabled(self, enabled: bool):
        """Set whether the size grip should be enabled."""
        super().setSizeGripEnabled(enabled)


# Convenience functions for common message types

def show_info_message(title: str, message: str, parent=None):
    """
    Show an information message dialog.
    
    Args:
        title: Dialog title
        message: Message content
        parent: Parent widget
        
    Returns:
        Dialog result
    """
    dialog = MessageDialog(
        title=title,
        message=message,
        parent=parent,
        message_type=MessageDialog.INFO
    )
    return dialog.exec()


def show_warning_message(title: str, message: str, parent=None):
    """
    Show a warning message dialog.
     
    Args:
        title: Dialog title
        message: Message content
        parent: Parent widget
         
    Returns:
        Dialog result
    """
    # Log the warning message before showing the dialog
    logger.warning(f"Warning Dialog - {title}: {message}")
    
    dialog = MessageDialog(
        title=title,
        message=message,
        parent=parent,
        message_type=MessageDialog.WARNING
    )
    return dialog.exec()


def show_error_message(title: str, message: str, parent=None):
    """
    Show an error message dialog.
     
    Args:
        title: Dialog title
        message: Message content
        parent: Parent widget
         
    Returns:
        Dialog result
    """
    # Log the error message before showing the dialog
    logger.error(f"Error Dialog - {title}: {message}")
    
    dialog = MessageDialog(
        title=title,
        message=message,
        parent=parent,
        message_type=MessageDialog.ERROR
    )
    return dialog.exec()


def show_success_message(title: str, message: str, parent=None):
    """
    Show a success message dialog.
    
    Args:
        title: Dialog title
        message: Message content
        parent: Parent widget
        
    Returns:
        Dialog result
    """
    dialog = MessageDialog(
        title=title,
        message=message,
        parent=parent,
        message_type=MessageDialog.SUCCESS
    )
    return dialog.exec()
