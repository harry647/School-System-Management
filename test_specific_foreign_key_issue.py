#!/usr/bin/env python3
"""
Test script to reproduce the specific foreign key constraint issue from the logs.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from school_system.services.student_service import StudentService
from school_system.core.exceptions import DatabaseException

def test_specific_issue():
    """Test the specific issue from the logs - adding reams to student 3902."""
    print("Testing specific foreign key constraint issue from logs...")
    
    student_service = StudentService()
    
    # Test the exact scenario from the logs
    print("\nTest: Reproducing the exact scenario from logs")
    
    try:
        # First check if student 3902 exists
        student = student_service.get_student_by_id("3902")
        if student:
            print(f"Found student 3902: {student.name}")
            
            # Try to add reams to this student (this was failing in the logs)
            print("Adding 2 reams to student 3902 from source: Distribution")
            entry = student_service.add_reams_to_student("3902", 2, "Distribution")
            print(f"SUCCESS: Added reams to student 3902, entry ID: {entry.id}")
            
            # Try to deduct reams from this student (this was also failing)
            print("Deducting 3 reams from student 3902 for purpose: Usage")
            entry = student_service.deduct_reams_from_student("3902", 3, "Usage")
            print(f"SUCCESS: Deducted reams from student 3902, entry ID: {entry.id}")
            
            # Try to transfer reams (this was also failing)
            print("Transferring 2 reams from student 2007 to student 3902")
            result = student_service.transfer_reams_between_students("2007", "3902", 2, "Test transfer")
            if result:
                print("SUCCESS: Transferred reams between students")
            else:
                print("FAILED: Transfer failed")
                
        else:
            print("Student 3902 not found in database")
            
            # Try to create the student first
            print("Creating student 3902...")
            student_data = {
                'admission_number': '3902',
                'name': 'Test Student 3902',
                'stream': 'Science'
            }
            new_student = student_service.create_student(student_data)
            print(f"Created student: {new_student.student_id} - {new_student.name}")
            
            # Now try the operations again
            print("Adding 2 reams to newly created student 3902")
            entry = student_service.add_reams_to_student("3902", 2, "Distribution")
            print(f"SUCCESS: Added reams to student 3902, entry ID: {entry.id}")
            
    except Exception as e:
        print(f"ERROR: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    print("\nTest completed!")
    return True

if __name__ == "__main__":
    success = test_specific_issue()
    sys.exit(0 if success else 1)