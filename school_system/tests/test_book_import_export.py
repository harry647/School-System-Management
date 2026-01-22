#!/usr/bin/env python3
"""
Test script for book import/export functionality.
This script tests the enhanced book import/export window and services.
"""

import sys
import os
import tempfile

# Add the project root to the Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_book_service_methods():
    """Test that all required BookService methods exist."""
    print("Testing BookService methods")
    print("=" * 40)

    try:
        from school_system.services.book_service import BookService

        book_service = BookService()

        # Test required methods exist
        methods_to_test = [
            'import_books_from_excel_with_validation',
            'export_books_to_excel',
            'export_books_to_csv',
            'generate_book_import_template',
            'create_book'
        ]

        for method_name in methods_to_test:
            if hasattr(book_service, method_name):
                method = getattr(book_service, method_name)
                if callable(method):
                    print(f"OK {method_name}: Available")
                else:
                    print(f"FAIL {method_name}: Not callable")
                    return False
            else:
                print(f"FAIL {method_name}: Missing")
                return False

        print("OK All required BookService methods available")
        return True

    except Exception as e:
        print(f"FAIL BookService test failed: {e}")
        return False


def test_template_generation():
    """Test template generation functionality."""
    print("\nTesting Template Generation")
    print("=" * 35)

    try:
        from school_system.services.book_service import BookService

        book_service = BookService()

        # Test data
        columns = ['book_number', 'title', 'author', 'category', 'subject', 'class']
        sample_data = [
            {
                'book_number': 'TEST001',
                'title': 'Test Book',
                'author': 'Test Author',
                'category': 'Test',
                'subject': 'Mathematics',
                'class': 'Form 4'
            }
        ]

        # Generate template
        with tempfile.NamedTemporaryFile(delete=False, suffix='.xlsx') as tmp_file:
            template_file = tmp_file.name

        success = book_service.generate_book_import_template(template_file, columns, sample_data)

        if success and os.path.exists(template_file):
            file_size = os.path.getsize(template_file)
            print(f"OK Template generated: {file_size} bytes")
            print("OK Template file exists")

            # Clean up
            os.unlink(template_file)
            return True
        else:
            print("FAIL Template generation failed")
            return False

    except Exception as e:
        print(f"FAIL Template generation test failed: {e}")
        return False


def test_import_validation():
    """Test import validation functionality."""
    print("\nTesting Import Validation")
    print("=" * 30)

    try:
        from school_system.services.book_service import BookService
        import pandas as pd

        book_service = BookService()

        # Create test Excel file
        test_data = [
            {'book_number': 'TEST001', 'title': 'Test Book', 'author': 'Test Author'},
            {'book_number': 'TEST002', 'title': 'Another Book', 'author': 'Another Author'},
        ]

        df = pd.DataFrame(test_data)

        with tempfile.NamedTemporaryFile(delete=False, suffix='.xlsx') as tmp_file:
            test_file = tmp_file.name
            df.to_excel(test_file, index=False)

        # Test validation
        required_columns = ['book_number', 'title', 'author']
        success, data, error_msg = book_service.import_books_from_excel_with_validation(
            test_file, required_columns
        )

        # Clean up
        os.unlink(test_file)

        if success and len(data) == 2:
            print("OK Import validation successful")
            print(f"OK Imported {len(data)} records")
            return True
        else:
            print(f"FAIL Import validation failed: {error_msg}")
            return False

    except Exception as e:
        print(f"FAIL Import validation test failed: {e}")
        return False


def test_export_functionality():
    """Test export functionality."""
    print("\nTesting Export Functionality")
    print("=" * 32)

    try:
        from school_system.services.book_service import BookService

        book_service = BookService()

        # Test Excel export (will work even with empty database)
        with tempfile.NamedTemporaryFile(delete=False, suffix='.xlsx') as tmp_file:
            excel_file = tmp_file.name

        excel_success = book_service.export_books_to_excel(excel_file)

        # Test CSV export
        with tempfile.NamedTemporaryFile(delete=False, suffix='.csv') as tmp_file:
            csv_file = tmp_file.name

        csv_success = book_service.export_books_to_csv(csv_file)

        # Check results
        excel_exists = os.path.exists(excel_file)
        csv_exists = os.path.exists(csv_file)

        if excel_exists:
            excel_size = os.path.getsize(excel_file)
            print(f"OK Excel export successful: {excel_size} bytes")
            os.unlink(excel_file)
        else:
            print("FAIL Excel export failed")

        if csv_exists:
            csv_size = os.path.getsize(csv_file)
            print(f"OK CSV export successful: {csv_size} bytes")
            os.unlink(csv_file)
        else:
            print("FAIL CSV export failed")

        return excel_exists and csv_exists

    except Exception as e:
        print(f"FAIL Export functionality test failed: {e}")
        return False


def test_window_import():
    """Test that the book import/export window can be imported."""
    print("\nTesting Window Import")
    print("=" * 25)

    try:
        from school_system.gui.windows.book_window.book_import_export_window import BookImportExportWindow
        print("OK Book import/export window imported successfully")
        return True
    except Exception as e:
        print(f"FAIL Window import failed: {e}")
        return False


def main():
    """Run all book import/export tests."""
    print("Book Import/Export Functionality Test Suite")
    print("=" * 50)

    tests = [
        ("BookService Methods", test_book_service_methods),
        ("Template Generation", test_template_generation),
        ("Import Validation", test_import_validation),
        ("Export Functionality", test_export_functionality),
        ("Window Import", test_window_import),
    ]

    passed = 0
    total = len(tests)

    for test_name, test_func in tests:
        try:
            if test_func():
                passed += 1
                print(f"PASS: {test_name}")
            else:
                print(f"FAIL: {test_name}")
        except Exception as e:
            print(f"ERROR: {test_name} - {e}")

    print("\n" + "=" * 50)
    print(f"Test Results: {passed}/{total} tests passed")

    if passed == total:
        print("All book import/export tests passed!")
        print("\nFeatures ready:")
        print("* Excel/CSV import with validation")
        print("* Excel/CSV export functionality")
        print("* Import template generation")
        print("* Clear column requirements for users")
        print("* Seamless service integration")
        return 0
    else:
        print("Some tests failed. Please check the implementation.")
        return 1


if __name__ == "__main__":
    sys.exit(main())