"""
Styles Module

This module provides access to the theme stylesheets for the School System Management Application.

Available Stylesheets:
    - dark_theme.qss: Dark theme stylesheet
    - light_theme.qss: Light theme stylesheet

Usage:
    from school_system.gui.resources.styles import dark_theme_qss, light_theme_qss
    
    # Apply a theme
    app.setStyleSheet(light_theme_qss)
"""

import os

# Get the directory where this module is located
_STYLES_DIR = os.path.dirname(os.path.abspath(__file__))

# Read and expose the stylesheets using absolute paths based on module location
with open(os.path.join(_STYLES_DIR, 'dark_theme.qss'), 'r') as f:
    dark_theme_qss = f.read()

with open(os.path.join(_STYLES_DIR, 'light_theme.qss'), 'r') as f:
    light_theme_qss = f.read()

__all__ = ['dark_theme_qss', 'light_theme_qss']
