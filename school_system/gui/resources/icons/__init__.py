"""
Icons Module

This module provides access to the application icons for the School System Management Application.

Available Icons:
    - error.png: Error icon
    - info.png: Information icon
    - success.png: Success icon
    - warning.png: Warning icon

Usage:
    from school_system.gui.resources.icons import error_icon_path, info_icon_path, success_icon_path, warning_icon_path
    
    # Use an icon
    icon = QIcon(error_icon_path)
"""

import os

# Define icon paths relative to this module
_ICON_DIR = os.path.dirname(__file__)

error_icon_path = os.path.join(_ICON_DIR, 'error.png')
info_icon_path = os.path.join(_ICON_DIR, 'info.png')
success_icon_path = os.path.join(_ICON_DIR, 'success.png')
warning_icon_path = os.path.join(_ICON_DIR, 'warning.png')

__all__ = ['error_icon_path', 'info_icon_path', 'success_icon_path', 'warning_icon_path']
