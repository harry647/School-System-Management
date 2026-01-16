"""
Book workflow components for the book management system.
"""

from typing import Dict, List, Optional, Tuple, Union
from PyQt6.QtWidgets import QMessageBox
import time

from school_system.services.book_service import BookService
from school_system.core.exceptions import DatabaseException, ValidationError
from school_system.gui.dialogs.message_dialog import show_error_message, show_success_message
from school_system.gui.windows.book_window.utils.validation import BookValidationHelper


class BookWorkflowBase:
    """Base class for book workflows."""
    
    def __init__(self, book_service: BookService, current_user: str):
        self.book_service = book_service
        self.current_user = current_user
        self.last_action = None
        
    def _log_user_action(self, action_type: str, details: str):
        """Log user action to audit trail."""
        try:
            self.book_service.log_user_action(
                self.current_user,
                action_type,
                details
            )
        except Exception as e:
            print(f"Failed to log user action: {str(e)}")
    
    def _store_undo_action(self, action_type: str, data: dict):
        """Store action for undo functionality."""
        self.last_action = {
            'type': action_type,
            'data': data,
            'timestamp': time.time()
        }


class BookAddWorkflow(BookWorkflowBase):
    """Workflow for adding new books."""
    
    def execute_add_book(self, book_data: Dict) -> Optional[object]:
        """Execute the complete add book workflow."""
        try:
            # Step 1: Validate required fields
            validation_result = BookValidationHelper.validate_required_fields(book_data)
            if not validation_result[0]:
                return None, validation_result[1]
            
            # Step 2: Validate book number uniqueness
            existing_books = self.book_service.get_all_books()
            existing_book_data = [{'book_number': book.book_number} for book in existing_books]
            
            is_valid, validation_message = BookValidationHelper.validate_book_number(
                book_data['book_number'].strip(), 
                existing_book_data
            )
            
            if not is_valid:
                return None, validation_message
            
            # Step 3: Create the book
            book_data['available'] = 1
            book = self.book_service.create_book(book_data)
            
            # Step 4: Log action and store for undo
            self._log_user_action(
                "book_add", 
                f"Added book {book.id}: {book.title}"
            )
            
            self._store_undo_action('add', {'book_id': book.id})
            
            return book, "Book created successfully"
            
        except (ValidationError, DatabaseException) as e:
            return None, str(e)
        except Exception as e:
            return None, f"An error occurred: {str(e)}"


class BookEditWorkflow(BookWorkflowBase):
    """Workflow for editing existing books."""
    
    def execute_edit_book(self, book_id: int, update_data: Dict) -> Tuple[bool, str]:
        """Execute the complete edit book workflow."""
        try:
            # Get current book for comparison
            current_book = self.book_service.get_book_by_id(book_id)
            if not current_book:
                return False, "Book not found"
            
            # Validate that at least one field is being updated
            if not update_data:
                return False, "Please provide at least one field to update"
            
            # Execute the update
            book = self.book_service.update_book(book_id, update_data)
            
            if book:
                # Log action and store for undo
                self._log_user_action(
                    "book_edit",
                    f"Updated book {book_id}: {update_data}"
                )
                
                old_data = {
                    'title': current_book.title,
                    'author': current_book.author,
                    'book_condition': current_book.book_condition
                }
                
                self._store_undo_action('edit', {
                    'book_id': book_id,
                    'old_data': old_data
                })
                
                return True, "Book updated successfully"
            else:
                return False, "Book not found"
                
        except Exception as e:
            return False, f"An error occurred: {str(e)}"


class BookRemoveWorkflow(BookWorkflowBase):
    """Workflow for removing books."""
    
    def execute_remove_book(self, book_id: int, reason: str, notes: str = "") -> Tuple[bool, str]:
        """Execute the complete remove book workflow."""
        try:
            # Get book details first
            book = self.book_service.get_book_by_id(book_id)
            if not book:
                return False, "Book not found"
            
            # Check if book is currently borrowed
            if not book.available:
                return False, "Cannot remove a book that is currently borrowed. Please return it first."
            
            # Execute the removal
            success = self.book_service.delete_book(book_id)
            
            if success:
                # Log action and store book data for potential undo
                self._log_user_action(
                    "book_remove",
                    f"Removed book {book_id}: {book.title}. Reason: {reason}"
                )
                
                book_data = {
                    'book_number': book.book_number,
                    'title': book.title,
                    'author': book.author,
                    'category': book.category,
                    'subject': getattr(book, 'subject', ''),
                    'class': getattr(book, 'class', ''),
                    'isbn': book.isbn,
                    'publication_date': book.publication_date,
                    'available': book.available,
                    'book_condition': book.book_condition
                }
                
                self._store_undo_action('remove', {'book_data': book_data})
                
                return True, "Book removed successfully"
            else:
                return False, "Failed to remove book"
                
        except Exception as e:
            return False, f"An error occurred: {str(e)}"


class BookBorrowWorkflow(BookWorkflowBase):
    """Workflow for borrowing books."""
    
    def execute_borrow_book(self, user_type: str, user_id: str, book_id: int) -> Tuple[bool, str]:
        """Execute the complete borrow book workflow."""
        try:
            # Check if book is available
            if not self.book_service.check_book_availability(book_id):
                return False, "Book is not available for borrowing"
            
            # Reserve the book
            success = self.book_service.reserve_book(user_id, user_type, book_id)
            
            if success:
                self._log_user_action(
                    "book_borrow",
                    f"Borrowed book {book_id} to {user_type} {user_id}"
                )
                return True, "Book borrowed successfully"
            else:
                return False, "Failed to borrow book"
                
        except Exception as e:
            return False, f"An error occurred: {str(e)}"


class BookReturnWorkflow(BookWorkflowBase):
    """Workflow for returning books."""
    
    def execute_return_book(self, user_type: str, user_id: str, book_id: int, 
                           condition: str, fine_amount: float = 0.0) -> Tuple[bool, str]:
        """Execute the complete return book workflow."""
        try:
            if user_type == "student":
                success = self.book_service.return_book_student(
                    user_id, book_id, condition, fine_amount, self.current_user
                )
            else:
                success = self.book_service.return_book_teacher(user_id, book_id)
            
            if success:
                self._log_user_action(
                    "book_return",
                    f"Returned book {book_id} from {user_type} {user_id}"
                )
                return True, "Book returned successfully"
            else:
                return False, "Failed to return book"
                
        except Exception as e:
            return False, f"An error occurred: {str(e)}"


class BookSearchWorkflow(BookWorkflowBase):
    """Workflow for searching books."""

    def execute_search_books(self, query: str) -> Tuple[List, str]:
        """Execute book search."""
        try:
            if query.strip():
                books = self.book_service.search_books(query)
            else:
                books = self.book_service.get_all_books()

            return books, ""

        except Exception as e:
            return [], f"Search failed: {str(e)}"


class BulkReturnWorkflow(BookWorkflowBase):
    """Workflow for bulk book returns with checkbox selection."""

    def execute_bulk_return(self, return_data: List[Dict]) -> Tuple[bool, str, dict]:
        """
        Execute the complete bulk return workflow.

        Args:
            return_data: List of dictionaries containing return information

        Returns:
            Tuple of (success, message, statistics)
        """
        try:
            # Validate input data
            if not return_data or len(return_data) == 0:
                return False, "No books selected for return", {}

            # Validate each return item
            validation_errors = []
            for item in return_data:
                if not item.get('book_id'):
                    validation_errors.append("Missing book ID")
                elif not isinstance(item['book_id'], int):
                    validation_errors.append(f"Invalid book ID type: {type(item['book_id'])}")
                
                if not item.get('borrower_id'):
                    validation_errors.append("Missing borrower ID")
                elif not isinstance(item['borrower_id'], str):
                    validation_errors.append(f"Invalid borrower ID type: {type(item['borrower_id'])}")
                
                if not item.get('borrower_type'):
                    validation_errors.append("Missing borrower type")
                elif item['borrower_type'] not in ['student', 'teacher']:
                    validation_errors.append(f"Invalid borrower type: {item['borrower_type']}")
                
                # Validate condition
                condition = item.get('condition', 'Good')
                if condition not in ['Good', 'Torn', 'Lost']:
                    validation_errors.append(f"Invalid condition: {condition}")
                
                # Validate fine amount
                fine_amount = item.get('fine_amount', 0.0)
                if not isinstance(fine_amount, (int, float)) or fine_amount < 0:
                    validation_errors.append(f"Invalid fine amount: {fine_amount}")

            if validation_errors:
                return False, "Validation errors: " + ", ".join(validation_errors), {}

            # Execute bulk return
            success, message, statistics = self.book_service.bulk_return_books(
                return_data, self.current_user
            )

            if success:
                # Log the action
                self._log_user_action(
                    "bulk_return",
                    f"Bulk return of {len(return_data)} books"
                )

                return True, message, statistics
            else:
                return False, message, statistics

        except Exception as e:
            return False, f"Bulk return failed: {str(e)}", {}
