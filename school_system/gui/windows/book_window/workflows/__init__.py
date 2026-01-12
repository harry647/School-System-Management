"""
Workflow components package initialization.

This package provides standardized workflow classes for book operations:
- BookAddWorkflow: Add new books with validation
- BookEditWorkflow: Edit existing book details
- BookRemoveWorkflow: Remove books from the system
- BookBorrowWorkflow: Handle book borrowing transactions
- BookReturnWorkflow: Handle book return transactions
- BookSearchWorkflow: Search and filter books

Each workflow implements a standardized pattern with:
- Undo functionality
- Audit logging
- Validation
- Error handling
"""

from .book_workflows import (
    BookWorkflowBase,
    BookAddWorkflow,
    BookEditWorkflow,
    BookRemoveWorkflow,
    BookBorrowWorkflow,
    BookReturnWorkflow,
    BookSearchWorkflow,
    BulkReturnWorkflow
)

__all__ = [
    'BookWorkflowBase',
    'BookAddWorkflow',
    'BookEditWorkflow',
    'BookRemoveWorkflow',
    'BookBorrowWorkflow',
    'BookReturnWorkflow',
    'BookSearchWorkflow',
    'BulkReturnWorkflow'
]
