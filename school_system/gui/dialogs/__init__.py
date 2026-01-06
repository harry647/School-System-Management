"""
School System GUI Dialogs Module

This module provides specialized dialog implementations that extend the base framework
with enhanced functionality for various use cases.

Core Components:
    - ConfirmationDialog: Enhanced confirmation dialog with customizable options
    - InputDialog: Advanced input dialog with validation and error handling
    - MessageDialog: Comprehensive message dialog with multiple message types
    - Convenience functions: show_info_message, show_warning_message, etc.

Usage:
    from school_system.gui.dialogs import (
        ConfirmationDialog, InputDialog, MessageDialog,
        show_info_message, show_warning_message, show_error_message, show_success_message
    )
"""

from .confirm_dialog import ConfirmationDialog
from .input_dialog import InputDialog
from .message_dialog import (
    MessageDialog, 
    show_info_message, show_warning_message, 
    show_error_message, show_success_message
)

__all__ = [
    # Dialog classes
    "ConfirmationDialog",
    "InputDialog", 
    "MessageDialog",
    
    # Convenience functions
    "show_info_message",
    "show_warning_message", 
    "show_error_message",
    "show_success_message"
]
