"""
Input Dialog Implementation for School System GUI Framework

This module provides a comprehensive input dialog that extends the BaseDialog
class with advanced input handling capabilities.

Features:
    - Multiple input field types
    - Input validation and error handling
    - Theming support through BaseDialog
    - Accessibility compliance
    - Event-driven architecture
    - Support for custom validation rules
"""

from PyQt6.QtWidgets import QLabel, QVBoxLayout, QHBoxLayout, QFrame, QDialogButtonBox
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QIcon

from school_system.gui.base.base_dialog import BaseDialog
from school_system.gui.base.widgets import ModernInput
from school_system.config.logging import logger


class InputDialog(BaseDialog):
    """
    Enhanced input dialog with comprehensive input handling.
    
    This dialog extends BaseDialog to provide specialized functionality
    for collecting user input with validation and error handling.
    
    Features:
        - Multiple input field support
        - Custom validation rules
        - Real-time validation feedback
        - Theming inheritance from parent window
        - Full accessibility compliance
        - Event-driven input handling
        - Support for required fields and error states
    """
    
    # Signal for input validation status changes
    input_validated = pyqtSignal(bool)  # True if valid, False if invalid
    
    def __init__(
        self,
        title: str = "Input Required",
        label: str = "Please enter your input:",
        parent=None,
        placeholder: str = "",
        validation_func=None,
        required: bool = True,
        input_type: str = "text",
        icon: QIcon = None,
        scrollable: bool = False,
        resizable: bool = False
    ):
        """
        Initialize the input dialog.
        
        Args:
            title: Dialog title
            label: Input field label
            parent: Parent widget
            placeholder: Placeholder text for input field
            validation_func: Function to validate input (returns bool, error_message)
            required: Whether input is required
            input_type: Type of input ('text', 'password', 'email', etc.)
            icon: Optional icon for the dialog
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
            self.setMinimumSize(400, 250)
            self.setSizeGripEnabled(True)
        
        # Store configuration
        self._label_text = label
        self._placeholder = placeholder
        self._validation_func = validation_func
        self._required = required
        self._input_type = input_type
        self._icon = icon
        self._is_valid = False
        
        # Initialize UI
        self._initialize_ui()
        
        # Connect signals
        self._connect_signals()
        
        # Set dialog icon if provided
        if icon:
            self.set_dialog_icon(icon)
        
        logger.info(f"InputDialog '{title}' initialized")
    
    def _initialize_ui(self):
        """Initialize the user interface components."""
        # Create label
        self._label_widget = QLabel(self._label_text)
        self._label_widget.setStyleSheet(f"""
            font-size: 14px;
            color: {self._theme_manager.get_color('text')};
            margin-bottom: 8px;
        """)
        self._label_widget.setAccessibleName("Input label")
        self._label_widget.setAccessibleDescription("Label for input field")
        
        # Add label to content
        self.add_content_widget(self._label_widget)
        
        # Create input field
        self._input_field = ModernInput()
        self._input_field.setPlaceholderText(self._placeholder)
        
        # Configure input type
        if self._input_type == "password":
            self._input_field.setEchoMode(ModernInput.EchoMode.Password)
        elif self._input_type == "email":
            self._input_field.setInputMask("email")
        
        self._input_field.setAccessibleName("Input field")
        self._input_field.setAccessibleDescription("Input field for user data")
        
        # Add input field to content
        self.add_content_widget(self._input_field)
        
        # Create error message area (hidden by default)
        self._error_frame = QFrame()
        self._error_frame.setVisible(False)
        self._error_layout = QHBoxLayout(self._error_frame)
        self._error_layout.setContentsMargins(0, 0, 0, 0)
        
        self._error_icon = QLabel()
        self._error_icon.setPixmap(QIcon("icons/error.png").pixmap(16, 16))
        self._error_icon.setAccessibleName("Error icon")
        
        self._error_message = QLabel()
        self._error_message.setStyleSheet(f"""
            color: {self._theme_manager.get_color('error')};
            font-size: 12px;
            margin-left: 4px;
        """)
        self._error_message.setAccessibleName("Error message")
        
        self._error_layout.addWidget(self._error_icon)
        self._error_layout.addWidget(self._error_message)
        self._error_layout.addStretch()
        
        self.add_content_widget(self._error_frame)
        
        # Create and add custom buttons
        self._ok_button = self.add_custom_button("OK", QDialogButtonBox.ButtonRole.AcceptRole)
        self._cancel_button = self.add_custom_button("Cancel", QDialogButtonBox.ButtonRole.RejectRole)
        
        # Set button properties
        self._ok_button.setAccessibleName("OK button")
        self._cancel_button.setAccessibleName("Cancel button")
        
        # Disable OK button initially if required
        if self._required:
            self._ok_button.setEnabled(False)
        
        # Apply theme to buttons
        self._apply_button_theme()
    
    def _apply_button_theme(self):
        """Apply theme-specific styling to buttons."""
        primary_color = self._theme_manager.get_color('primary')
        text_color = self._theme_manager.get_color('text')
        
        self._ok_button.set_custom_style(
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
        """Connect signals for button actions and input validation."""
        self._ok_button.clicked.connect(self._handle_ok)
        self._cancel_button.clicked.connect(self.reject)
        self._input_field.textChanged.connect(self._validate_input)
        
        # Connect theme change signals
        if hasattr(self._theme_manager, 'theme_changed'):
            self._theme_manager.theme_changed.connect(self._apply_button_theme)
    
    def _validate_input(self, text: str):
        """
        Validate the input text and update UI accordingly.
        
        Args:
            text: Current input text
        """
        error_message = None
        is_valid = True
        
        # Check if required field is empty
        if self._required and not text.strip():
            error_message = "This field is required"
            is_valid = False
        
        # Apply custom validation if provided
        elif self._validation_func:
            try:
                validation_result = self._validation_func(text)
                if isinstance(validation_result, tuple):
                    is_valid, error_message = validation_result
                else:
                    is_valid = validation_result
                    error_message = "Invalid input" if not is_valid else None
            except Exception as e:
                error_message = f"Validation error: {str(e)}"
                is_valid = False
        
        # Update validation state
        self._is_valid = is_valid
        
        # Update UI based on validation
        if error_message:
            self._show_error(error_message)
            self._ok_button.setEnabled(False)
        else:
            self._hide_error()
            self._ok_button.setEnabled(True)
        
        # Emit validation signal
        self.input_validated.emit(is_valid)
        
        logger.debug(f"Input validation: {is_valid} (text: '{text[:20]}...')")
        
        return is_valid
    
    def _show_error(self, message: str):
        """
        Show error message.
        
        Args:
            message: Error message to display
        """
        self._error_message.setText(message)
        self._error_frame.setVisible(True)
        self._input_field.setStyleSheet(f"""
            border: 1px solid {self._theme_manager.get_color('error')};
            border-radius: 4px;
            padding: 8px;
        """)
    
    def _hide_error(self):
        """Hide error message."""
        self._error_frame.setVisible(False)
        self._input_field.setStyleSheet("")
    
    def _handle_ok(self):
        """Handle OK button click with validation."""
        # Final validation before accepting
        if self._validate_input(self._input_field.text()):
            logger.info(f"InputDialog '{self.windowTitle()}' accepted with input: '{self._input_field.text()[:50]}...'")
            self.accept()
    
    def get_input_value(self) -> str:
        """
        Get the input value.
        
        Returns:
            The input field text
        """
        return self._input_field.text()
    
    def set_input_value(self, value: str):
        """
        Set the input value.
        
        Args:
            value: Value to set
        """
        self._input_field.setText(value)
        # Re-validate after setting value
        self._validate_input(value)
    
    def set_validation_function(self, validation_func):
        """
        Set or update the validation function.
        
        Args:
            validation_func: Function to validate input (returns bool, error_message)
        """
        self._validation_func = validation_func
        # Re-validate with new function
        self._validate_input(self._input_field.text())
    
    def set_required(self, required: bool):
        """
        Set whether the input is required.
        
        Args:
            required: Whether input is required
        """
        self._required = required
        # Re-validate with new requirement
        self._validate_input(self._input_field.text())
    
    def showEvent(self, event):
        """
        Handle dialog show events.
        
        Args:
            event: Show event
        """
        super().showEvent(event)
        # Focus the input field by default for better UX
        self._input_field.setFocus()
        logger.debug(f"InputDialog '{self.windowTitle()}' shown")
    
    def accept(self):
        """Handle dialog acceptance."""
        logger.debug(f"InputDialog '{self.windowTitle()}' accepted")
        super().accept()
    
    def reject(self):
        """Handle dialog rejection."""
        logger.debug(f"InputDialog '{self.windowTitle()}' rejected")
        super().reject()
    
    # Expose QDialog methods for compatibility
    def sizeGripEnabled(self) -> bool:
        """Return whether the size grip is enabled."""
        return super().isSizeGripEnabled()
    
    def setSizeGripEnabled(self, enabled: bool):
        """Set whether the size grip should be enabled."""
        super().setSizeGripEnabled(enabled)