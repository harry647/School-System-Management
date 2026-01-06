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

# Read and expose the stylesheets
with open('school_system/gui/resources/styles/dark_theme.qss', 'r') as f:
    dark_theme_qss = f.read()

with open('school_system/gui/resources/styles/light_theme.qss', 'r') as f:
    light_theme_qss = f.read()

__all__ = ['dark_theme_qss', 'light_theme_qss']
