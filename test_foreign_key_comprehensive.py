#!/usr/bin/env python3
"""
Comprehensive test script to verify the foreign key constraint fix for ream operations.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from school_system.services.student_service import StudentService
from school_system.core.exceptions import DatabaseException

def test_foreign_key_fix():
    """Test that the foreign key constraint fix works correctly."""
    print("Testing foreign key constraint fix...")
    
    student_service = StudentService()
    
    # Test 1: Try to add reams to a non-existent student
    print("\nTest 1: Adding reams to non-existent student (should fail gracefully)")
    try:
        result = student_service.add_reams_to_student("9999", 5, "Distribution")
        print("ERROR: Should have failed but succeeded!")
        return False
    except ValueError as e:
        print(f"SUCCESS: Caught expected error: {e}")
        if "not found in database" in str(e):
            print("SUCCESS: Error message is descriptive")
        else:
            print("WARNING: Error message could be more descriptive")
    except Exception as e:
        print(f"ERROR: Unexpected exception type: {e}")
        return False
    
    # Test 2: Try to deduct reams from a non-existent student
    print("\nTest 2: Deducting reams from non-existent student (should fail gracefully)")
    try:
        result = student_service.deduct_reams_from_student("9999", 5, "Usage")
        print("ERROR: Should have failed but succeeded!")
        return False
    except ValueError as e:
        print(f"SUCCESS: Caught expected error: {e}")
        if "not found in database" in str(e):
            print("SUCCESS: Error message is descriptive")
        else:
            print("WARNING: Error message could be more descriptive")
    except Exception as e:
        print(f"ERROR: Unexpected exception type: {e}")
        return False
    
    # Test 3: Try to transfer reams involving non-existent students
    print("\nTest 3: Transferring reams with non-existent student (should fail gracefully)")
    try:
        result = student_service.transfer_reams_between_students("9999", "2007", 1, "Test")
        if result:
            print("ERROR: Should have failed but succeeded!")
            return False
        else:
            print("SUCCESS: Transfer correctly returned False for non-existent student")
    except Exception as e:
        print(f"ERROR: Unexpected exception type: {e}")
        return False
    
    # Test 4: Test with a valid student (if any exist in the database)
    print("\nTest 4: Testing with valid student (if available)")
    try:
        # Try to get a student that exists
        all_students = student_service.get_all_students()
        if all_students:
            test_student = all_students[0]
            print(f"Found test student: {test_student.student_id} - {test_student.name}")
            
            # Test adding reams to valid student
            print(f"Adding 2 reams to valid student {test_student.student_id}")
            entry = student_service.add_reams_to_student(test_student.student_id, 2, "Test")
            print(f"SUCCESS: Added reams to valid student, entry ID: {entry.id}")
            
            # Test deducting reams from valid student
            print(f"Deducting 1 ream from valid student {test_student.student_id}")
            entry = student_service.deduct_reams_from_student(test_student.student_id, 1, "Test")
            print(f"SUCCESS: Deducted reams from valid student, entry ID: {entry.id}")
            
            # Test balance
            balance = student_service.get_student_ream_balance(test_student.student_id)
            print(f"SUCCESS: Student {test_student.student_id} has balance: {balance}")
        else:
            print("No students found in database, skipping positive test cases")
    except Exception as e:
        print(f"ERROR: Unexpected exception in positive test: {e}")
        return False
    
    print("\nAll tests passed! The foreign key constraint fix is working correctly.")
    return True

if __name__ == "__main__":
    success = test_foreign_key_fix()
    sys.exit(0 if success else 1)