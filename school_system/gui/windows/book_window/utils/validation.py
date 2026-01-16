"""
Validation utilities for the book management system.
"""

from typing import List, Dict, Tuple
from school_system.gui.windows.book_window.utils.constants import (
    REQUIRED_FIELDS,
    EXCEL_BOOK_IMPORT_COLUMNS,
    EXCEL_BORROWED_BOOKS_COLUMNS,
    EXCEL_BULK_BORROW_COLUMNS
)


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
    def validate_excel_columns(headers: List[str], required_columns: List[str]) -> Tuple[bool, str]:
        """
        Validate that Excel file contains all required columns.
        
        Args:
            headers: List of column headers from Excel file
            required_columns: List of required column names
            
        Returns:
            tuple: (is_valid, error_message)
        """
        missing_columns = []
        for column in required_columns:
            if column not in headers:
                missing_columns.append(column)
        
        if missing_columns:
            return False, f"Missing required columns: {', '.join(missing_columns)}"
        
        return True, ""
    
    @staticmethod
    def validate_bulk_borrow_data(data: List[Dict], student_service, book_service) -> Tuple[bool, List[str]]:
        """
        Validate bulk borrow data from Excel.
        
        Args:
            data: List of dictionaries containing borrow data
            student_service: Student service for validation
            book_service: Book service for validation
            
        Returns:
            tuple: (is_valid, error_messages)
        """
        errors = []
        
        for i, row in enumerate(data, 1):
            admission_number = row.get('Admission_Number', '').strip()
            book_number = row.get('Book_Number', '').strip()
            
            # Validate admission number
            if not admission_number:
                errors.append(f"Row {i}: Missing admission number")
                continue
            
            # Check if student exists
            student_exists = student_service.get_student_by_admission_number(admission_number)
            if not student_exists:
                errors.append(f"Row {i}: Student with admission number '{admission_number}' not found")
            
            # Validate book number
            if not book_number:
                errors.append(f"Row {i}: Missing book number")
                continue
            
            # Check if book exists and is available
            book = book_service.get_book_by_number(book_number)
            if not book:
                errors.append(f"Row {i}: Book with number '{book_number}' not found")
            elif not book.available:
                errors.append(f"Row {i}: Book '{book_number}' is not available")
        
        return len(errors) == 0, errors
        
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
