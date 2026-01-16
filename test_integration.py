#!/usr/bin/env python3
"""
Integration test script for school management system report functionality.
"""

import sys
import os

# Add the project root to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'school_system'))

def test_imports():
    """Test all critical imports."""
    try:
        print("Testing imports...")
        from school_system.gui.windows.main_window import MainWindow
        from school_system.gui.windows.report_window.book_reports_window import BookReportsWindow
        from school_system.gui.windows.report_window.student_reports_window import StudentReportsWindow
        from school_system.gui.windows.report_window.custom_reports_window import CustomReportsWindow
        from school_system.services.report_service import ReportService
        from school_system.gui.windows.base_function_window import BaseFunctionWindow

        print("SUCCESS: All imports successful")
        return True
    except Exception as e:
        print(f"FAILED: Import test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_report_service():
    """Test ReportService functionality."""
    try:
        print("Testing ReportService...")
        from school_system.services.report_service import ReportService

        report_service = ReportService()
        print("SUCCESS: ReportService instantiated successfully")

        # Test basic report methods
        books_report = report_service.get_all_books_report()
        students_report = report_service.get_all_students_report()
        print("SUCCESS: Report methods executed successfully")

        return True
    except Exception as e:
        print(f"FAILED: ReportService test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Run all integration tests."""
    print("Running School Management System Integration Tests")
    print("=" * 60)

    tests_passed = 0
    total_tests = 2

    if test_imports():
        tests_passed += 1

    if test_report_service():
        tests_passed += 1

    print("=" * 60)
    if tests_passed == total_tests:
        print("SUCCESS: All integration tests passed!")
        return 0
    else:
        print(f"FAILED: {total_tests - tests_passed} test(s) failed")
        return 1

if __name__ == "__main__":
    sys.exit(main())