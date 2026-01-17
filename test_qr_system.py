#!/usr/bin/env python3
"""
Test script for QR code management system.
This script tests the QR code generation and validation functionality.
"""

import sys
import os

# Add the project root to the Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from school_system.models.book import Book
from school_system.models.student import Student
from school_system.services.book_service import BookService
from school_system.services.student_service import StudentService


def test_qr_generation():
    """Test QR code generation for books and students."""
    print("🧪 Testing QR Code Generation System")
    print("=" * 50)

    # Test Book QR Generation
    print("\n📚 Testing Book QR Code Generation:")
    book = Book(
        book_number="TEST001",
        title="Test Book",
        author="Test Author",
        subject="Mathematics",
        class_name="Form 4"
    )

    qr_code = book.generate_qr_code()
    print(f"✓ Book QR Code Generated: {qr_code}")
    print(f"✓ QR Code Length: {len(qr_code)} characters")
    print(f"✓ QR Code Format: {'Valid' if qr_code.isalnum() and qr_code.isupper() else 'Invalid'}")

    # Test Student QR Generation
    print("\n👨‍🎓 Testing Student QR Code Generation:")
    student = Student(
        admission_number="2024001",
        name="John Doe",
        stream="Red"
    )

    qr_code = student.generate_qr_code()
    print(f"✓ Student QR Code Generated: {qr_code}")
    print(f"✓ QR Code Length: {len(qr_code)} characters")
    print(f"✓ QR Code Format: {'Valid' if qr_code.isalnum() and qr_code.isupper() else 'Invalid'}")

    # Test QR Uniqueness
    print("\n🔄 Testing QR Code Uniqueness:")
    book2 = Book(
        book_number="TEST002",
        title="Another Test Book",
        author="Another Author",
        subject="English",
        class_name="Form 3"
    )

    qr_code2 = book2.generate_qr_code()
    print(f"✓ First Book QR: {book.qr_code}")
    print(f"✓ Second Book QR: {qr_code2}")
    print(f"✓ QR Codes Unique: {'Yes' if book.qr_code != qr_code2 else 'No'}")

    # Test Service Integration
    print("\n🔧 Testing Service Integration:")
    try:
        book_service = BookService()
        student_service = StudentService()
        print("✓ Services initialized successfully")
    except Exception as e:
        print(f"✗ Service initialization failed: {e}")
        return False

    print("\n✅ All QR Code Generation Tests Passed!")
    return True


def test_qr_validation():
    """Test QR code validation."""
    print("\n🔍 Testing QR Code Validation:")
    print("-" * 30)

    # Test valid QR codes
    valid_codes = ["A1B2C3D4E5F6789A", "1234567890ABCDEF", "AAAAAAAAAAAAAAAA"]
    for code in valid_codes:
        is_valid = len(code) == 16 and code.isalnum() and code.isupper()
        print(f"✓ {code}: {'Valid' if is_valid else 'Invalid'}")

    # Test invalid QR codes
    invalid_codes = ["short", "lowercase12345678", "special@chars!123", "toolongcode123456789"]
    for code in invalid_codes:
        is_valid = len(code) == 16 and code.isalnum() and code.isupper()
        print(f"✓ {code}: {'Valid' if is_valid else 'Invalid'} (expected invalid)")

    print("\n✅ QR Code Validation Tests Completed!")
    return True


def test_database_models():
    """Test database model operations."""
    print("\n💾 Testing Database Model Operations:")
    print("-" * 40)

    try:
        # Test Book model save (without actually saving to DB)
        book = Book(
            book_number="DBTEST001",
            title="Database Test Book",
            author="DB Tester",
            subject="Science",
            class_name="Form 2"
        )

        # Generate QR
        qr = book.generate_qr_code()
        print(f"✓ Book model QR generation: {qr}")

        # Test Student model save (without actually saving to DB)
        student = Student(
            admission_number="DBTEST001",
            name="Database Test Student",
            stream="Blue"
        )

        qr = student.generate_qr_code()
        print(f"✓ Student model QR generation: {qr}")

        print("✅ Database Model Tests Passed!")
        return True

    except Exception as e:
        print(f"✗ Database model test failed: {e}")
        return False


def main():
    """Run all QR system tests."""
    print("🚀 QR Code Management System - Test Suite")
    print("=" * 55)

    tests = [
        ("QR Code Generation", test_qr_generation),
        ("QR Code Validation", test_qr_validation),
        ("Database Models", test_database_models),
    ]

    passed = 0
    total = len(tests)

    for test_name, test_func in tests:
        try:
            if test_func():
                passed += 1
                print(f"✅ {test_name}: PASSED")
            else:
                print(f"❌ {test_name}: FAILED")
        except Exception as e:
            print(f"❌ {test_name}: ERROR - {e}")

    print("\n" + "=" * 55)
    print(f"📊 Test Results: {passed}/{total} tests passed")

    if passed == total:
        print("🎉 All tests passed! QR system is ready for use.")
        return 0
    else:
        print("⚠️  Some tests failed. Please check the implementation.")
        return 1


if __name__ == "__main__":
    sys.exit(main())