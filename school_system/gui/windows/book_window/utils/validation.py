"""
Validation utilities for the book management system.
"""

from typing import List, Dict, Tuple
from school_system.gui.windows.book_window.utils.constants import REQUIRED_FIELDS


class BookValidationHelper:
    """Helper class for book validation operations."""
    
    @staticmethod
    def validate_book_number(book_number: str, existing_books: List[Dict]) -> Tuple[bool, str]:
        """
        Validate book number for uniqueness and format.
        
        Args:
            book_number: The book number to validate
            existing_books: List of existing books for uniqueness check
            
        Returns:
            tuple: (is_valid, error_message)
        """
        if not book_number or not book_number.strip():
            return False, "Book number is required"
            
        # Normalize book number (uppercase, trim whitespace)
        normalized = book_number.strip().upper()
        
        # Check if book number already exists (case-insensitive)
        for book in existing_books:
            if book['book_number'].strip().upper() == normalized:
                return False, f"Book number '{book_number}' already exists"
                
        return True, ""
        
    @staticmethod
    def validate_required_fields(data: Dict[str, str], required_fields: List[str] = REQUIRED_FIELDS) -> Tuple[bool, str]:
        """Validate that required fields are present and not empty."""
        for field in required_fields:
            if not data.get(field) or not data[field].strip():
                return False, f"{field.replace('_', ' ').title()} is required"
        return True, ""
    
    @staticmethod
    def validate_book_data(book_data: Dict) -> Tuple[bool, str]:
        """Validate complete book data."""
        # Check required fields
        validation_result = BookValidationHelper.validate_required_fields(book_data)
        if not validation_result[0]:
            return validation_result
        
        # Additional validation logic can be added here
        # For example, validate ISBN format, publication date format, etc.
        
        return True, ""