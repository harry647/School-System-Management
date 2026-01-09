#!/usr/bin/env python3
"""
Test script to verify that the ream transfer validation works correctly.
This tests the scenario where a student doesn't have enough reams to transfer.
"""

import sys
import os

# Add the school_system directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'school_system'))

from school_system.services.student_service import StudentService
from school_system.models.student import Student, ReamEntry
from school_system.database.repositories.student_repo import StudentRepository, ReamEntryRepository

def test_ream_transfer_validation():
    """Test the ream transfer validation with various scenarios."""
    
    print("Testing ream transfer validation...")
    print("=" * 50)
    
    # Create test students
    test_student1 = Student(
        admission_number="TEST001",
        name="Test Student 1",
        stream="Test Stream"
    )
    
    test_student2 = Student(
        admission_number="TEST002",
        name="Test Student 2",
        stream="Test Stream"
    )
    
    # Create student service
    service = StudentService()
    student_repo = StudentRepository()
    ream_repo = ReamEntryRepository()
    
    try:
        # Clean up any existing test students
        existing_students = student_repo.find_by_field('admission_number', 'TEST001')
        for student in existing_students:
            student_repo.delete(student.student_id)
            
        existing_students = student_repo.find_by_field('admission_number', 'TEST002')
        for student in existing_students:
            student_repo.delete(student.student_id)
            
        # Clean up any existing ream entries for these students
        existing_reams = ream_repo.find_by_field('student_id', 'TEST001')
        for ream in existing_reams:
            ream_repo.delete(ream.student_id)
            
        existing_reams = ream_repo.find_by_field('student_id', 'TEST002')
        for ream in existing_reams:
            ream_repo.delete(ream.student_id)
        
        # Create test students
        student1 = student_repo.create(test_student1)
        student2 = student_repo.create(test_student2)
        
        print(f"Created student 1: {student1.student_id} - {student1.name}")
        print(f"Created student 2: {student2.student_id} - {student2.name}")
        
        # Add some reams to student 1 (source student)
        service.add_reams_to_student(student1.student_id, 10, "Initial")
        
        balance1 = service.get_student_ream_balance(student1.student_id)
        balance2 = service.get_student_ream_balance(student2.student_id)
        
        print(f"\nInitial balances:")
        print(f"Student 1 balance: {balance1}")
        print(f"Student 2 balance: {balance2}")
        
        # Test 1: Transfer more reams than available (should transfer only what's available)
        print(f"\nTest 1: Attempting to transfer 15 reams from student 1 (who has {balance1}) to student 2")
        
        success = service.transfer_reams_between_students(
            student1.student_id, 
            student2.student_id, 
            15,  # Trying to transfer more than available
            "Test transfer"
        )
        
        if success:
            new_balance1 = service.get_student_ream_balance(student1.student_id)
            new_balance2 = service.get_student_ream_balance(student2.student_id)
            
            print(f"Transfer successful!")
            print(f"Student 1 new balance: {new_balance1}")
            print(f"Student 2 new balance: {new_balance2}")
            
            # Verify that only available reams were transferred
            if new_balance1 == 0 and new_balance2 == 10:
                print(" PASS: Only available reams (10) were transferred")
            else:
                print(f" FAIL: Expected student1=0, student2=10, got student1={new_balance1}, student2={new_balance2}")
                return False
        else:
            print(" FAIL: Transfer failed when it should have succeeded with available reams")
            return False
        
        # Test 2: Transfer with exactly available amount
        print(f"\nTest 2: Transferring exactly available amount")
        
        # First, add more reams to student 1
        service.add_reams_to_student(student1.student_id, 5, "Add more")
        balance1 = service.get_student_ream_balance(student1.student_id)
        print(f"Student 1 balance after adding more: {balance1}")
        
        success = service.transfer_reams_between_students(
            student1.student_id, 
            student2.student_id, 
            5,  # Transfer exactly what was added
            "Exact transfer"
        )
        
        if success:
            new_balance1 = service.get_student_ream_balance(student1.student_id)
            new_balance2 = service.get_student_ream_balance(student2.student_id)
            
            print(f"Transfer successful!")
            print(f"Student 1 new balance: {new_balance1}")
            print(f"Student 2 new balance: {new_balance2}")
            
            # Verify exact transfer
            if new_balance1 == 0 and new_balance2 == 15:
                print(" PASS: Exact amount transferred correctly")
            else:
                print(f" FAIL: Expected student1=0, student2=15, got student1={new_balance1}, student2={new_balance2}")
                return False
        else:
            print(" FAIL: Transfer failed when it should have succeeded")
            return False
        
        # Test 3: Transfer when source has zero balance
        print(f"\nTest 3: Attempting transfer when source has zero balance")
        
        success = service.transfer_reams_between_students(
            student1.student_id, 
            student2.student_id, 
            5,  # Try to transfer when source has 0
            "Zero balance transfer"
        )
        
        if not success:
            print(" PASS: Transfer correctly failed when source has insufficient reams")
        else:
            print(" FAIL: Transfer succeeded when it should have failed")
            return False
        
        print(f"\nAll tests passed! The ream transfer validation is working correctly.")
        return True
        
    except Exception as e:
        print(f"Error during testing: {e}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        # Clean up test data
        try:
            existing_students = student_repo.find_by_field('admission_number', 'TEST001')
            for student in existing_students:
                student_repo.delete(student.student_id)
                
            existing_students = student_repo.find_by_field('admission_number', 'TEST002')
            for student in existing_students:
                student_repo.delete(student.student_id)
                
            existing_reams = ream_repo.find_by_field('student_id', 'TEST001')
            for ream in existing_reams:
                ream_repo.delete(ream.student_id)
                
            existing_reams = ream_repo.find_by_field('student_id', 'TEST002')
            for ream in existing_reams:
                ream_repo.delete(ream.student_id)
                
        except Exception as cleanup_error:
            print(f"Warning: Error during cleanup: {cleanup_error}")

if __name__ == "__main__":
    print("Running ream transfer validation tests...")
    print("=" * 60)
    
    success = test_ream_transfer_validation()
    
    print("\n" + "=" * 60)
    if success:
        print("ALL TESTS PASSED! The ream transfer validation is working correctly.")
        sys.exit(0)
    else:
        print("Some tests failed. Please check the implementation.")
        sys.exit(1)