#!/usr/bin/env python3
"""
Test script to verify the foreign key constraint fix for ream operations.
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
    
    print("\nAll tests passed! The foreign key constraint fix is working correctly.")
    return True

if __name__ == "__main__":
    success = test_foreign_key_fix()
    sys.exit(0 if success else 1)