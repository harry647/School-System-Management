"""
Resources Module

This module provides centralized access to all GUI resources for the School System Management Application.

Available Submodules:
    - icons: Application icons and visual assets
    - styles: Theme stylesheets (light and dark themes)
    - templates: HTML templates for emails and reports

Usage:
    from school_system.gui.resources import icons, styles, templates
    
    # Access icons
    error_icon = icons.error_icon_path
    
    # Access styles
    app.setStyleSheet(styles.light_theme_qss)
    
    # Access templates
    with open(templates.email_template_path, 'r') as f:
        email_content = f.read()
"""

# Import and expose submodules
from . import icons
from . import styles
from . import templates

__all__ = ['icons', 'styles', 'templates']
