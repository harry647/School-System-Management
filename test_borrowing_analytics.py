#!/usr/bin/env python3
"""
Test script for borrowing analytics functionality.
This script tests the comprehensive borrowing analytics features.
"""

import sys
import os

# Add the project root to the Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_report_service_analytics():
    """Test that ReportService analytics methods exist and work."""
    print("Testing ReportService Analytics Methods")
    print("=" * 45)

    try:
        from school_system.services.report_service import ReportService

        report_service = ReportService()

        # Test required methods exist
        methods_to_test = [
            'get_borrowing_analytics_report',
            '_get_borrowing_summary_by_subject_stream_form',
            '_get_borrowing_percentage_by_class',
            '_get_inventory_summary',
            '_get_books_categorized_by_subject_form',
            '_get_students_not_borrowed_by_stream_subject',
            '_get_students_not_borrowed_any_books'
        ]

        for method_name in methods_to_test:
            if hasattr(report_service, method_name):
                method = getattr(report_service, method_name)
                if callable(method):
                    print(f"OK {method_name}: Available")
                else:
                    print(f"FAIL {method_name}: Not callable")
                    return False
            else:
                print(f"FAIL {method_name}: Missing")
                return False

        print("OK All required analytics methods available")
        return True

    except Exception as e:
        print(f"FAIL ReportService analytics test failed: {e}")
        return False


def test_analytics_data_generation():
    """Test that analytics data can be generated."""
    print("\nTesting Analytics Data Generation")
    print("=" * 38)

    try:
        from school_system.services.report_service import ReportService

        report_service = ReportService()

        # Test generating analytics report
        print("Generating borrowing analytics report...")
        analytics_data = report_service.get_borrowing_analytics_report()

        if analytics_data and isinstance(analytics_data, dict):
            print("OK Analytics report generated successfully")

            # Check expected keys
            expected_keys = [
                'borrowing_summary_by_subject_stream_form',
                'borrowing_percentage_by_class',
                'inventory_summary',
                'books_categorized_by_subject_form',
                'students_not_borrowed_by_stream_subject',
                'students_not_borrowed_any_books'
            ]

            missing_keys = []
            for key in expected_keys:
                if key in analytics_data:
                    data = analytics_data[key]
                    if isinstance(data, (list, dict)):
                        print(f"OK {key}: {type(data).__name__} with {len(data) if isinstance(data, (list, dict)) and hasattr(data, '__len__') else 'N/A'} items")
                    else:
                        print(f"OK {key}: {type(data).__name__}")
                else:
                    missing_keys.append(key)
                    print(f"FAIL {key}: Missing")

            if missing_keys:
                print(f"FAIL Missing keys: {missing_keys}")
                return False

            return True
        else:
            print("FAIL Analytics report generation failed or returned invalid data")
            return False

    except Exception as e:
        print(f"FAIL Analytics data generation failed: {e}")
        return False


def test_inventory_summary():
    """Test inventory summary generation."""
    print("\nTesting Inventory Summary")
    print("=" * 27)

    try:
        from school_system.services.report_service import ReportService

        report_service = ReportService()

        # Test inventory summary
        inventory = report_service._get_inventory_summary()

        if inventory and isinstance(inventory, dict):
            print("OK Inventory summary generated")

            expected_fields = ['total_books', 'available_books', 'borrowed_books', 'borrowed_percentage']
            for field in expected_fields:
                if field in inventory:
                    print(f"OK {field}: {inventory[field]}")
                else:
                    print(f"FAIL {field}: Missing")
                    return False

            return True
        else:
            print("FAIL Inventory summary generation failed")
            return False

    except Exception as e:
        print(f"FAIL Inventory summary test failed: {e}")
        return False


def test_borrowing_percentage():
    """Test borrowing percentage calculation."""
    print("\nTesting Borrowing Percentage Calculation")
    print("=" * 42)

    try:
        from school_system.services.report_service import ReportService

        report_service = ReportService()

        # Test borrowing percentage calculation
        percentages = report_service._get_borrowing_percentage_by_class()

        if isinstance(percentages, list):
            print(f"OK Borrowing percentages calculated: {len(percentages)} classes")

            if percentages:
                # Check structure of first item
                first_item = percentages[0]
                expected_fields = ['form', 'total_students', 'students_borrowed', 'student_borrowing_percentage']

                for field in expected_fields:
                    if field in first_item:
                        print(f"OK {field}: {first_item[field]}")
                    else:
                        print(f"FAIL {field}: Missing in percentage data")
                        return False

            return True
        else:
            print("FAIL Borrowing percentage calculation failed")
            return False

    except Exception as e:
        print(f"FAIL Borrowing percentage test failed: {e}")
        return False


def test_books_categorization():
    """Test books categorization by subject and form."""
    print("\nTesting Books Categorization")
    print("=" * 30)

    try:
        from school_system.services.report_service import ReportService

        report_service = ReportService()

        # Test books categorization
        categorized = report_service._get_books_categorized_by_subject_form()

        if isinstance(categorized, list):
            print(f"OK Books categorization completed: {len(categorized)} categories")

            if categorized:
                # Check structure of first item
                first_item = categorized[0]
                expected_fields = ['form', 'subject', 'total_books', 'available_books', 'borrowed_books']

                for field in expected_fields:
                    if field in first_item:
                        print(f"OK {field}: {first_item[field]}")
                    else:
                        print(f"FAIL {field}: Missing in categorization data")
                        return False

            return True
        else:
            print("FAIL Books categorization failed")
            return False

    except Exception as e:
        print(f"FAIL Books categorization test failed: {e}")
        return False


def test_students_not_borrowed():
    """Test students not borrowed analytics."""
    print("\nTesting Students Not Borrowed Analytics")
    print("=" * 41)

    try:
        from school_system.services.report_service import ReportService

        report_service = ReportService()

        # Test students not borrowed
        not_borrowed = report_service._get_students_not_borrowed_any_books()

        if isinstance(not_borrowed, dict):
            print("OK Students not borrowed analytics generated")

            expected_fields = ['total_students_not_borrowed', 'students_by_stream', 'all_students_not_borrowed']
            for field in expected_fields:
                if field in not_borrowed:
                    data = not_borrowed[field]
                    if isinstance(data, (list, dict)):
                        print(f"OK {field}: {len(data) if hasattr(data, '__len__') else 'N/A'} items")
                    else:
                        print(f"OK {field}: {data}")
                else:
                    print(f"FAIL {field}: Missing")
                    return False

            return True
        else:
            print("FAIL Students not borrowed analytics failed")
            return False

    except Exception as e:
        print(f"FAIL Students not borrowed analytics test failed: {e}")
        return False


def test_book_reports_window():
    """Test that the BookReportsWindow can be imported."""
    print("\nTesting BookReportsWindow Import")
    print("=" * 35)

    try:
        from school_system.gui.windows.report_window.book_reports_window import BookReportsWindow
        print("OK BookReportsWindow imported successfully")

        # Check for new analytics methods
        methods_to_check = ['_display_borrowing_analytics', '_create_analytics_summary_area']
        for method_name in methods_to_check:
            if hasattr(BookReportsWindow, method_name):
                print(f"OK {method_name}: Available")
            else:
                print(f"FAIL {method_name}: Missing")
                return False

        return True
    except Exception as e:
        print(f"FAIL BookReportsWindow import failed: {e}")
        return False


def main():
    """Run all borrowing analytics tests."""
    print("Borrowing Analytics Functionality Test Suite")
    print("=" * 50)

    tests = [
        ("ReportService Analytics Methods", test_report_service_analytics),
        ("Analytics Data Generation", test_analytics_data_generation),
        ("Inventory Summary", test_inventory_summary),
        ("Borrowing Percentage Calculation", test_borrowing_percentage),
        ("Books Categorization", test_books_categorization),
        ("Students Not Borrowed Analytics", test_students_not_borrowed),
        ("BookReportsWindow", test_book_reports_window),
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
        print("All borrowing analytics tests passed!")
        print("\nFeatures ready:")
        print("* Comprehensive borrowing analytics report")
        print("* Subject/stream/form borrowing summaries")
        print("* Class borrowing percentages")
        print("* Inventory and categorization reports")
        print("* Student borrowing gap analysis")
        print("* Enhanced reports window with analytics display")
        return 0
    else:
        print("Some tests failed. Please check the implementation.")
        return 1


if __name__ == "__main__":
    sys.exit(main())