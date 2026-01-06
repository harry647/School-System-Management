"""
Confirmation Dialog Implementation for School System GUI Framework

This module provides a comprehensive confirmation dialog that extends the BaseDialog
class with additional features for confirmation scenarios.

Features:
    - Customizable confirmation messages
    - Configurable button labels
    - Theming support through BaseDialog
    - Accessibility compliance
    - Event-driven architecture
    - Support for rich text formatting
"""

from PyQt6.QtWidgets import QLabel, QVBoxLayout, QDialogButtonBox
from PyQt6.QtCore import Qt

from school_system.gui.base.base_dialog import BaseDialog
from school_system.config.logging import logger


class ConfirmationDialog(BaseDialog):
    """
    Enhanced confirmation dialog with comprehensive features.
    
    This dialog extends BaseDialog to provide specialized functionality
    for confirmation scenarios with customizable options.
    
    Features:
        - Custom confirmation messages with rich text support
        - Configurable button labels and actions
        - Theming inheritance from parent window
        - Full accessibility compliance
        - Event-driven confirmation handling
        - Support for detailed confirmation scenarios
    """
    
    def __init__(
        self,
        title: str = "Confirm Action",
        message: str = "Are you sure you want to proceed?",
        parent=None,
        confirm_text: str = "Confirm",
        cancel_text: str = "Cancel",
        rich_text: bool = False,
        scrollable: bool = False,
        resizable: bool = False
    ):
        """
        Initialize the confirmation dialog.
        
        Args:
            title: Dialog title
            message: Confirmation message to display
            parent: Parent widget
            confirm_text: Text for confirm button
            cancel_text: Text for cancel button
            rich_text: Whether to enable rich text formatting
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
        self._confirm_text = confirm_text
        self._cancel_text = cancel_text
        self._rich_text = rich_text
        
        # Initialize UI
        self._initialize_ui(message)
        
        # Connect signals
        self._connect_signals()
        
        logger.info(f"ConfirmationDialog '{title}' initialized")
    
    def _initialize_ui(self, message: str):
        """
        Initialize the user interface components.
        
        Args:
            message: Confirmation message to display
        """
        # Create message label
        self._message_label = QLabel(message)
        if self._rich_text:
            self._message_label.setTextFormat(Qt.TextFormat.RichText)
        else:
            self._message_label.setTextFormat(Qt.TextFormat.PlainText)
            
        self._message_label.setWordWrap(True)
        self._message_label.setStyleSheet(f"""
            font-size: 14px;
            color: {self._theme_manager.get_color('text')};
            padding: 10px;
        """)
        self._message_label.setAccessibleName("Confirmation message")
        self._message_label.setAccessibleDescription("Confirmation dialog message content")
        
        # Add message to content
        self.add_content_widget(self._message_label)
        
        # Create and add custom buttons
        self._confirm_button = self.add_custom_button(
            self._confirm_text,
            QDialogButtonBox.ButtonRole.AcceptRole
        )
        self._cancel_button = self.add_custom_button(
            self._cancel_text,
            QDialogButtonBox.ButtonRole.RejectRole
        )
        
        # Set button properties
        self._confirm_button.setAccessibleName(f"{self._confirm_text} button")
        self._cancel_button.setAccessibleName(f"{self._cancel_text} button")
        
        # Apply theme to buttons
        self._apply_button_theme()
    
    def _apply_button_theme(self):
        """Apply theme-specific styling to buttons."""
        primary_color = self._theme_manager.get_color('primary')
        text_color = self._theme_manager.get_color('text')
        
        self._confirm_button.set_custom_style(
            bg_color=primary_color,
            hover_color=self._theme_manager.get_color('secondary'),
            pressed_color=self._theme_manager.get_color('primary'),
            text_color=text_color
        )
        
        self._cancel_button.set_custom_style(
            bg_color=self._theme_manager.get_color('secondary'),
            hover_color=self._theme_manager.get_color('primary'),
            pressed_color=self._theme_manager.get_color('secondary'),
            text_color=text_color
        )
    
    def _connect_signals(self):
        """Connect signals for button actions."""
        self._confirm_button.clicked.connect(self.accept)
        self._cancel_button.clicked.connect(self.reject)
        
        # Connect theme change signals
        if hasattr(self._theme_manager, 'theme_changed'):
            self._theme_manager.theme_changed.connect(self._apply_button_theme)
    
    def set_message(self, message: str):
        """
        Set or update the confirmation message.
        
        Args:
            message: New confirmation message
        """
        self._message_label.setText(message)
        logger.debug(f"Confirmation message updated: {message[:50]}...")
    
    def set_confirm_button_text(self, text: str):
        """
        Set the confirm button text.
        
        Args:
            text: New button text
        """
        self._confirm_button.setText(text)
        self._confirm_button.setAccessibleName(f"{text} button")
    
    def set_cancel_button_text(self, text: str):
        """
        Set the cancel button text.
        
        Args:
            text: New button text
        """
        self._cancel_button.setText(text)
        self._cancel_button.setAccessibleName(f"{text} button")
    
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
    
    def showEvent(self, event):
        """
        Handle dialog show events.
        
        Args:
            event: Show event
        """
        super().showEvent(event)
        # Focus the confirm button by default for better UX
        self._confirm_button.setFocus()
        logger.debug(f"ConfirmationDialog '{self.windowTitle()}' shown")
    
    def accept(self):
        """Handle dialog acceptance (confirm action)."""
        logger.info(f"ConfirmationDialog '{self.windowTitle()}' confirmed")
        super().accept()
    
    def reject(self):
        """Handle dialog rejection (cancel action)."""
        logger.info(f"ConfirmationDialog '{self.windowTitle()}' cancelled")
        super().reject()
    
    # Expose QDialog methods for compatibility
    def sizeGripEnabled(self) -> bool:
        """Return whether the size grip is enabled."""
        return super().isSizeGripEnabled()
    
    def setSizeGripEnabled(self, enabled: bool):
        """Set whether the size grip should be enabled."""
        super().setSizeGripEnabled(enabled)