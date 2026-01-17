#!/usr/bin/env python3
"""
Test script for book type functionality.
"""

import sys
import os

# Add the project root to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_book_type_functionality():
    """Test book type creation and retrieval."""
    from school_system.services.book_service import BookService
    from school_system.models.book import Book

    # Test Book model book_type property
    print("Testing Book model book_type property:")

    # Create a course book
    course_book = Book(
        book_number="TEST001",
        title="Test Course Book",
        author="Test Author",
        book_type="course"
    )
    print(f"Course book type: {course_book.book_type} (revision: {course_book.revision})")
    assert course_book.book_type == "course"
    assert course_book.revision == 0

    # Create a revision book
    revision_book = Book(
        book_number="TEST002",
        title="Test Revision Book",
        author="Test Author",
        book_type="revision"
    )
    print(f"Revision book type: {revision_book.book_type} (revision: {revision_book.revision})")
    assert revision_book.book_type == "revision"
    assert revision_book.revision == 1

    # Test backward compatibility with revision parameter
    legacy_book = Book(
        book_number="TEST003",
        title="Legacy Book",
        author="Test Author",
        revision=1  # Old way
    )
    print(f"Legacy book type: {legacy_book.book_type} (revision: {legacy_book.revision})")
    assert legacy_book.book_type == "revision"
    assert legacy_book.revision == 1

    # Test basic service functionality
    print("\nTesting BookService basic functionality:")
    service = BookService()

    try:
        # Test getting all books
        books = service.get_all_books()
        print(f"Successfully retrieved {len(books)} books from database")
        return True

    except Exception as e:
        print(f"Error testing book service: {e}")
        return False

def test_constants():
    """Test that constants are properly defined."""
    from school_system.gui.windows.book_window.utils.constants import BOOK_TYPES, EXCEL_BOOK_IMPORT_COLUMNS

    print("\nTesting constants:")
    print(f"BOOK_TYPES: {BOOK_TYPES}")
    assert "course" in BOOK_TYPES
    assert "revision" in BOOK_TYPES

    print(f"Book_Type in import columns: {'Book_Type' in EXCEL_BOOK_IMPORT_COLUMNS}")
    assert "Book_Type" in EXCEL_BOOK_IMPORT_COLUMNS

    return True

def main():
    """Run all tests."""
    print("Testing Book Type Functionality")
    print("=" * 40)

    success = True

    success &= test_book_type_functionality()
    success &= test_constants()

    print("\n" + "=" * 40)
    if success:
        print("All book type tests passed!")
    else:
        print("Some tests failed.")

    return 0 if success else 1

if __name__ == "__main__":
    sys.exit(main())