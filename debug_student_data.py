#!/usr/bin/env python3
"""
Debug script to check the actual student data in the database.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from school_system.database.connection import get_db_session
from school_system.services.student_service import StudentService

def debug_student_data():
    """Debug the student data to understand the foreign key issue."""
    print("Debugging student data...")
    
    db = get_db_session()
    cursor = db.cursor()
    
    # Check student 3902 in the database
    print("\nChecking student 3902 in database:")
    cursor.execute("SELECT student_id, admission_number, name, stream FROM students WHERE student_id = ? OR admission_number = ?", ("3902", "3902"))
    student_data = cursor.fetchone()
    if student_data:
        print(f"Found student: {student_data}")
        student_id, admission_number, name, stream = student_data
        print(f"  student_id: {student_id} (type: {type(student_id)})")
        print(f"  admission_number: {admission_number} (type: {type(admission_number)})")
        print(f"  name: {name}")
        print(f"  stream: {stream}")
    else:
        print("Student 3902 not found in database")
    
    # Check all students to see the pattern
    print("\nAll students in database:")
    cursor.execute("SELECT student_id, admission_number, name FROM students LIMIT 10")
    students = cursor.fetchall()
    for student in students:
        print(f"  {student}")
    
    # Test the student service
    print("\nTesting student service:")
    student_service = StudentService()
    student = student_service.get_student_by_id("3902")
    if student:
        print(f"Student service found: {student.student_id} - {student.name}")
        print(f"  student_id: {student.student_id} (type: {type(student.student_id)})")
        print(f"  admission_number: {student.admission_number} (type: {type(student.admission_number)})")
    else:
        print("Student service did not find student 3902")
    
    # Try to create a ream entry manually to see what happens
    print("\nTrying to create ream entry manually:")
    try:
        # Try with the student_id from the database
        if student_data:
            db_student_id = student_data[0]
            print(f"Trying with student_id from database: {db_student_id}")
            cursor.execute("INSERT INTO ream_entries (student_id, reams_count, date_added) VALUES (?, ?, DATE('now'))", (db_student_id, 2))
            db.commit()
            print("SUCCESS: Manual ream entry creation worked!")
        else:
            print("Cannot test manual creation - no student found")
    except Exception as e:
        print(f"Manual creation failed: {e}")
    
    cursor.close()

if __name__ == "__main__":
    debug_student_data()
