"""
Book window package initialization.

This package provides a complete book management interface including:
- Book CRUD operations
- Book borrowing and return workflows
- Distribution session management
- Import/export functionality
- Reports and analytics

All components are organized into subpackages:
- components: Reusable UI components (Card, Button, InputField, etc.)
- utils: Utilities including constants and validation helpers
- workflows: Standardized workflow classes for book operations
- tabs: Tab-based UI components for different book management sections
"""

# Main window class
from .book_window import BookWindow

# UI Components
from .components import (
    FlexLayout,
    Card,
    InputField,
    TextArea,
    Button,
    ComboBox,
    Table,
    SearchBox,
    ValidationLabel
)

# Utilities
from .utils import (
    SPACING_SMALL,
    SPACING_MEDIUM,
    SPACING_LARGE,
    CARD_PADDING,
    CARD_SPACING,
    REQUIRED_FIELDS,
    BOOK_CONDITIONS,
    REMOVAL_REASONS,
    USER_TYPES,
    RETURN_CONDITIONS,
    SESSION_STATUSES,
    STANDARD_SUBJECTS,
    STANDARD_CLASSES,
    STANDARD_STREAMS,
    STANDARD_TERMS,
    EXPORT_FORMATS,
    BookValidationHelper
)

# Workflows
from .workflows import (
    BookAddWorkflow,
    BookEditWorkflow,
    BookRemoveWorkflow,
    BookBorrowWorkflow,
    BookReturnWorkflow,
    BookSearchWorkflow
)

__all__ = [
    # Main window
    'BookWindow',
    
    # UI Components
    'FlexLayout',
    'Card',
    'InputField',
    'TextArea',
    'Button',
    'ComboBox',
    'Table',
    'SearchBox',
    'ValidationLabel',
    
    # Constants
    'SPACING_SMALL',
    'SPACING_MEDIUM',
    'SPACING_LARGE',
    'CARD_PADDING',
    'CARD_SPACING',
    'REQUIRED_FIELDS',
    'BOOK_CONDITIONS',
    'REMOVAL_REASONS',
    'USER_TYPES',
    'RETURN_CONDITIONS',
    'SESSION_STATUSES',
    'STANDARD_SUBJECTS',
    'STANDARD_CLASSES',
    'STANDARD_STREAMS',
    'STANDARD_TERMS',
    'EXPORT_FORMATS',
    
    # Validation
    'BookValidationHelper',
    
    # Workflows
    'BookAddWorkflow',
    'BookEditWorkflow',
    'BookRemoveWorkflow',
    'BookBorrowWorkflow',
    'BookReturnWorkflow',
    'BookSearchWorkflow'
]
