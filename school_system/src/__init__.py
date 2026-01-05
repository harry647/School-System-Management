"""
Source code package for the School System Management application.

This package contains the main application logic and entry points.
"""

from .application import SchoolSystemApplication
from .main import main

__all__ = [
    'SchoolSystemApplication',
    'main'
]

# Convenience function to run the application
def run():
    """Run the School System Management application."""
    return main()

# Add to __all__
__all__.append('run')
