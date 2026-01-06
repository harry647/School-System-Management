"""
Templates Module

This module provides access to the HTML templates for the School System Management Application.

Available Templates:
    - email_template.html: Email notification template
    - report_template.html: Report generation template

Usage:
    from school_system.gui.resources.templates import email_template_path, report_template_path
    
    # Load a template
    with open(email_template_path, 'r') as f:
        template_content = f.read()
"""

import os

# Define template paths relative to this module
_TEMPLATE_DIR = os.path.dirname(__file__)

email_template_path = os.path.join(_TEMPLATE_DIR, 'email_template.html')
report_template_path = os.path.join(_TEMPLATE_DIR, 'report_template.html')

__all__ = ['email_template_path', 'report_template_path']
