#!/usr/bin/env python3
"""
Test script to verify that all models are correctly created and imports work properly.
This script tests:
1. All imports work without errors
2. All models can be instantiated
3. All models have proper save methods
4. Database tables exist and align with models
"""

import sys
import os

# Add the school_system directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'school_system'))

def test_imports():
    """Test that all models can be imported without errors."""
    print("Testing imports...")
    
    try:
        # Test main models package import
        from models import (
            BaseModel, Student, ReamEntry, TotalReams, Teacher,
            Book, BookTag, BorrowedBookStudent, BorrowedBookTeacher,
            QRBook, QRBorrowLog, DistributionSession, DistributionStudent, DistributionImportLog,
            Chair, Locker, FurnitureCategory, LockerAssignment, ChairAssignment,
            User, UserSetting, ShortFormMapping, get_db_session
        )
        
        print("All imports successful!")
        
        # Return all imported classes for further testing
        return {
            'BaseModel': BaseModel,
            'Student': Student,
            'ReamEntry': ReamEntry,
            'TotalReams': TotalReams,
            'Teacher': Teacher,
            'Book': Book,
            'BookTag': BookTag,
            'BorrowedBookStudent': BorrowedBookStudent,
            'BorrowedBookTeacher': BorrowedBookTeacher,
            'QRBook': QRBook,
            'QRBorrowLog': QRBorrowLog,
            'DistributionSession': DistributionSession,
            'DistributionStudent': DistributionStudent,
            'DistributionImportLog': DistributionImportLog,
            'Chair': Chair,
            'Locker': Locker,
            'FurnitureCategory': FurnitureCategory,
            'LockerAssignment': LockerAssignment,
            'ChairAssignment': ChairAssignment,
            'User': User,
            'UserSetting': UserSetting,
            'ShortFormMapping': ShortFormMapping,
            'get_db_session': get_db_session
        }
        
    except ImportError as e:
        print(f"Import error: {e}")
        return None
    except Exception as e:
        print(f"Unexpected error during imports: {e}")
        return None

def test_model_instantiation(models):
    """Test that all models can be instantiated."""
    print("\nTesting model instantiation...")
    
    test_cases = [
        # Basic models
        ('User', {'username': 'testuser', 'password': 'testpass', 'role': 'student'}),
        ('Student', {'student_id': 'S001', 'name': 'Test Student', 'stream': 'Science'}),
        ('Teacher', {'teacher_id': 'T001', 'teacher_name': 'Test Teacher'}),
        ('Book', {'book_number': 'B001', 'available': 1, 'revision': 0, 'book_condition': 'New'}),
        
        # Furniture models
        ('Chair', {'chair_id': 'CH001', 'color': 'Black'}),
        ('Locker', {'locker_id': 'LK001', 'color': 'Black'}),
        ('FurnitureCategory', {'category_name': 'Chairs', 'total_count': 10, 'needs_repair': 0}),
        
        # Book-related models
        ('BookTag', {'book_id': 1, 'tag': 'Science'}),
        ('BorrowedBookStudent', {'student_id': 'S001', 'book_id': 1, 'borrowed_on': '2023-01-01'}),
        ('BorrowedBookTeacher', {'teacher_id': 'T001', 'book_id': 1, 'borrowed_on': '2023-01-01'}),
        ('QRBook', {'book_number': 'QR001', 'details': 'Test QR Book'}),
        ('QRBorrowLog', {'book_number': 'QR001', 'student_id': 'S001', 'borrow_date': '2023-01-01'}),
        
        # Student-related models
        ('ReamEntry', {'student_id': 'S001', 'reams_count': 5}),
        ('TotalReams', {'total_available': 100}),
        
        # User-related models
        ('UserSetting', {'user_id': 'testuser', 'reminder_frequency': 'daily', 'sound_enabled': 1}),
        ('ShortFormMapping', {'short_form': 'SCI', 'full_name': 'Science', 'type': 'subject'}),
        
        # Distribution models
        ('DistributionSession', {'class_name': 'Form1', 'stream': 'East', 'subject': 'Math', 'term': 'Term1', 'created_by': 'admin'}),
        ('DistributionStudent', {'session_id': 1, 'student_id': 'S001'}),
        ('DistributionImportLog', {'session_id': 1, 'file_name': 'test.csv', 'imported_by': 'admin', 'status': 'success', 'message': 'Test import'}),
        
        # Furniture assignments
        ('LockerAssignment', {'student_id': 'S001', 'locker_id': 'LK001'}),
        ('ChairAssignment', {'student_id': 'S001', 'chair_id': 'CH001'}),
    ]
    
    success_count = 0
    total_count = len(test_cases)
    
    for model_name, kwargs in test_cases:
        try:
            model_class = models[model_name]
            instance = model_class(**kwargs)
            print(f"{model_name} instantiated successfully")
            success_count += 1
        except Exception as e:
            print(f"{model_name} instantiation failed: {e}")
    
    print(f"\nInstantiation Results: {success_count}/{total_count} models instantiated successfully")
    return success_count == total_count

def test_model_methods(models):
    """Test that all models have proper save methods."""
    print("\nTesting model methods...")
    
    success_count = 0
    total_count = 0
    
    for model_name, model_class in models.items():
        if model_name == 'BaseModel' or model_name == 'get_db_session':
            continue
            
        total_count += 1
        if hasattr(model_class, 'save') and callable(getattr(model_class, 'save')):
            print(f"{model_name} has save method")
            success_count += 1
        else:
            print(f"{model_name} missing save method")
    
    print(f"\nMethod Results: {success_count}/{total_count} models have save methods")
    return success_count == total_count

def test_database_tables():
    """Test that database tables exist and align with models."""
    print("\nTesting database tables...")
    
    try:
        from school_system.database.connection import get_db_session
        
        db = get_db_session()
        cursor = db.cursor()
        
        # Get all tables in the database
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")
        tables = [row[0] for row in cursor.fetchall()]
        
        print(f"Found {len(tables)} tables in database:")
        for table in tables:
            print(f"  - {table}")
        
        # Expected tables based on our models
        expected_tables = [
            'users', 'students', 'teachers', 'books',
            'chairs', 'lockers', 'furniture_categories',
            'book_tags', 'borrowed_books_student', 'borrowed_books_teacher',
            'settings', 'short_form_mappings',
            'locker_assignments', 'chair_assignments',
            'ream_entries', 'total_reams',
            'qr_books', 'qr_borrow_log',
            'distribution_sessions', 'distribution_students', 'distribution_import_logs'
        ]
        
        missing_tables = []
        for expected_table in expected_tables:
            if expected_table not in tables:
                missing_tables.append(expected_table)
        
        if missing_tables:
            print(f"Missing tables: {missing_tables}")
            return False
        else:
            print("All expected tables found in database")
            return True
            
    except Exception as e:
        print(f"Database table test failed: {e}")
        return False

def main():
    """Main test function."""
    print("Starting model verification tests...\n")
    
    # Test imports
    models = test_imports()
    if not models:
        print("Tests failed due to import errors")
        return False
    
    # Test instantiation
    instantiation_success = test_model_instantiation(models)
    
    # Test methods
    methods_success = test_model_methods(models)
    
    # Test database tables
    database_success = test_database_tables()
    
    # Summary
    print(f"\n{'='*50}")
    print("TEST SUMMARY")
    print(f"{'='*50}")
    print(f"Imports: {'PASS' if models else 'FAIL'}")
    print(f"Instantiation: {'PASS' if instantiation_success else 'FAIL'}")
    print(f" Methods: {'PASS' if methods_success else 'FAIL'}")
    print(f"Database Tables: {'PASS' if database_success else 'FAIL'}")
    
    overall_success = all([
        models is not None,
        instantiation_success,
        methods_success,
        database_success
    ])
    
    print(f"\nOverall: {'ALL TESTS PASSED' if overall_success else 'SOME TESTS FAILED'}")
    
    return overall_success

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)