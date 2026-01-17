#!/usr/bin/env python3
"""
Test script to verify Distribution window alignment with services.
This script tests that all services and dependencies work correctly with the Distribution window.
"""

import sys
import os

# Add the project root to the Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_service_imports():
    """Test that all required services can be imported."""
    print("Testing Service Imports")
    print("=" * 30)

    try:
        from school_system.services.book_service import BookService
        from school_system.services.student_service import StudentService
        from school_system.services.class_management_service import ClassManagementService
        print("All services imported successfully")
        return True
    except Exception as e:
        print(f"Service import failed: {e}")
        return False


def test_service_initialization():
    """Test that services can be initialized without errors."""
    print("\nTesting Service Initialization")
    print("=" * 35)

    try:
        from school_system.services.book_service import BookService
        from school_system.services.student_service import StudentService
        from school_system.services.class_management_service import ClassManagementService

        book_service = BookService()
        student_service = StudentService()
        class_management_service = ClassManagementService()

        print("All services initialized successfully")
        return True
    except Exception as e:
        print(f"Service initialization failed: {e}")
        return False


def test_distribution_window_import():
    """Test that the Distribution window can be imported."""
    print("\nTesting Distribution Window Import")
    print("=" * 40)

    try:
        from school_system.gui.windows.book_window.distribution_window import DistributionWindow
        print("Distribution window imported successfully")
        return True
    except Exception as e:
        print(f"Distribution window import failed: {e}")
        return False


def test_template_dependencies():
    """Test that template generation dependencies are available."""
    print("\nTesting Template Generation Dependencies")
    print("=" * 45)

    dependencies = [
        ('pandas', 'DataFrame creation for Excel templates'),
        ('openpyxl', 'Excel file writing'),
        ('fpdf', 'PDF generation'),
    ]

    all_available = True

    for package, description in dependencies:
        try:
            __import__(package)
            print(f"{package}: Available - {description}")
        except ImportError:
            print(f"{package}: MISSING - {description}")
            print(f"   Install with: pip install {package}")
            all_available = False

    return all_available


def test_service_methods():
    """Test that all required service methods exist."""
    print("\nTesting Required Service Methods")
    print("=" * 35)

    try:
        from school_system.services.class_management_service import ClassManagementService
        from school_system.services.student_service import StudentService

        cms = ClassManagementService()
        ss = StudentService()

        # Test ClassManagementService methods
        methods_to_test = [
            ('get_all_class_levels', 'Get all class levels'),
            ('get_class_stream_combinations', 'Get class-stream combinations'),
            ('get_students_by_class_level', 'Get students by class level'),
            ('get_students_by_class_and_stream', 'Get students by class and stream'),
        ]

        for method_name, description in methods_to_test:
            if hasattr(cms, method_name):
                method = getattr(cms, method_name)
                if callable(method):
                    print(f"ClassManagementService.{method_name}: {description}")
                else:
                    print(f"ClassManagementService.{method_name}: Not callable")
                    return False
            else:
                print(f"ClassManagementService.{method_name}: Missing - {description}")
                return False

        # Test StudentService methods
        student_methods = [
            ('get_all_students', 'Get all students'),
            ('get_students_by_class_level', 'Get students by class level'),
            ('get_students_by_class_and_stream', 'Get students by class and stream'),
        ]

        for method_name, description in student_methods:
            if hasattr(ss, method_name):
                method = getattr(ss, method_name)
                if callable(method):
                    print(f"StudentService.{method_name}: {description}")
                else:
                    print(f"StudentService.{method_name}: Not callable")
                    return False
            else:
                print(f"StudentService.{method_name}: Missing - {description}")
                return False

        print("All required service methods available")
        return True

    except Exception as e:
        print(f"Service method test failed: {e}")
        return False


def test_model_compatibility():
    """Test that models are compatible with distribution window requirements."""
    print("\nTesting Model Compatibility")
    print("=" * 32)

    try:
        from school_system.models.student import Student

        # Test student model has required attributes
        test_student = Student("2024001", "Test Student", "Test Stream")

        required_attrs = ['student_id', 'admission_number', 'name', 'stream']
        for attr in required_attrs:
            if hasattr(test_student, attr):
                value = getattr(test_student, attr)
                print(f"Student.{attr}: {value}")
            else:
                print(f"Student.{attr}: Missing")
                return False

        print("Student model compatible with distribution requirements")
        return True

    except Exception as e:
        print(f"Model compatibility test failed: {e}")
        return False


def main():
    """Run all distribution alignment tests."""
    print("Distribution Window Service Alignment Test Suite")
    print("=" * 55)

    tests = [
        ("Service Imports", test_service_imports),
        ("Service Initialization", test_service_initialization),
        ("Distribution Window Import", test_distribution_window_import),
        ("Template Dependencies", test_template_dependencies),
        ("Service Methods", test_service_methods),
        ("Model Compatibility", test_model_compatibility),
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

    print("\n" + "=" * 55)
    print(f"Test Results: {passed}/{total} tests passed")

    if passed == total:
        print("All alignment tests passed!")
        print("\nDistribution window is properly aligned with services")
        print("All required methods and dependencies are available")
        print("Template generation should work seamlessly")
        return 0
    else:
        print("Some tests failed. Please check the implementation.")
        print("\nCommon fixes:")
        print("- Install missing dependencies: pip install pandas openpyxl fpdf")
        print("- Run database migrations: python -m school_system.database.migrations.run_all_migrations")
        print("- Check service method implementations")
        return 1


if __name__ == "__main__":
    sys.exit(main())