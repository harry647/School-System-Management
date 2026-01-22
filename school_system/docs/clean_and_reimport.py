#!/usr/bin/env python3
"""
Script to clean the database and reimport students from Excel.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from school_system.database.connection import get_db_session
from school_system.services.student_service import StudentService

def clean_and_reimport():
    """Clean the database and reimport students."""
    print("Cleaning database and reimporting students...")
    
    db = get_db_session()
    cursor = db.cursor()
    
    try:
        # First, let's see what students are currently in the database
        print("\nCurrent students in database:")
        cursor.execute("SELECT student_id, admission_number, name FROM students")
        current_students = cursor.fetchall()
        for student in current_students:
            print(f"  {student}")
        
        # Clear all students
        print("\nClearing all students...")
        cursor.execute("DELETE FROM students")
        db.commit()
        print("All students cleared.")
        
        # Clear all ream entries
        print("\nClearing all ream entries...")
        cursor.execute("DELETE FROM ream_entries")
        db.commit()
        print("All ream entries cleared.")
        
        # Reimport students from Excel
        print("\nReimporting students from Excel...")
        student_service = StudentService()
        students = student_service.import_students_from_excel("students_excel.xlsx")
        print(f"Imported {len(students)} students:")
        for student in students:
            print(f"  {student.student_id} - {student.name} (admission: {student.admission_number})")
        
        # Verify the data is consistent
        print("\nVerifying data consistency:")
        cursor.execute("SELECT student_id, admission_number, name FROM students LIMIT 5")
        verified_students = cursor.fetchall()
        for student in verified_students:
            print(f"  {student}")
        
        # Test ream operations with the new clean data
        print("\nTesting ream operations with clean data:")
        if students:
            test_student = students[0]
            print(f"Testing with student: {test_student.student_id} - {test_student.name}")
            
            # Test adding reams
            print(f"Adding 5 reams to student {test_student.student_id}")
            entry = student_service.add_reams_to_student(test_student.student_id, 5, "Test")
            print(f"SUCCESS: Added reams, entry ID: {entry.id}")
            
            # Test deducting reams
            print(f"Deducting 2 reams from student {test_student.student_id}")
            entry = student_service.deduct_reams_from_student(test_student.student_id, 2, "Test")
            print(f"SUCCESS: Deducted reams, entry ID: {entry.id}")
            
            # Test balance
            balance = student_service.get_student_ream_balance(test_student.student_id)
            print(f"Final balance for student {test_student.student_id}: {balance}")
        
        print("\nClean and reimport completed successfully!")
        return True
        
    except Exception as e:
        print(f"ERROR: {e}")
        import traceback
        traceback.print_exc()
        db.rollback()
        return False
    finally:
        cursor.close()

if __name__ == "__main__":
    success = clean_and_reimport()
    sys.exit(0 if success else 1)
