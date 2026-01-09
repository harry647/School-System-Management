#!/usr/bin/env python3
"""
Test script to verify that the automatic transactions population feature works.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from school_system.database.repositories.student_repo import ReamEntryRepository
from school_system.services.student_service import StudentService

def test_automatic_transactions_population():
    """Test that automatic transactions population works correctly."""
    print("Testing automatic transactions population feature...")
    
    try:
        # First, let's add some test transactions to make sure we have data
        student_service = StudentService()
        
        # Get a student to work with (use the first student from the database)
        all_students = student_service.get_all_students()
        if not all_students:
            print("No students found in database. Creating a test student...")
            # Create a test student
            student_data = {
                'admission_number': 'TEST123',
                'name': 'Test Student',
                'stream': 'Science'
            }
            test_student = student_service.create_student(student_data)
            student_id = test_student.student_id
        else:
            student_id = all_students[0].student_id
            print(f"Using existing student: {student_id} - {all_students[0].name}")
        
        # Add some test transactions
        print(f"\nAdding test transactions for student {student_id}...")
        
        # Add some reams
        entry1 = student_service.add_reams_to_student(student_id, 5, "Test Addition 1")
        print(f"Added 5 reams: {entry1.id}")
        
        entry2 = student_service.add_reams_to_student(student_id, 3, "Test Addition 2")
        print(f"Added 3 reams: {entry2.id}")
        
        # Deduct some reams
        entry3 = student_service.deduct_reams_from_student(student_id, 2, "Test Deduction")
        print(f"Deducted 2 reams: {entry3.id}")
        
        # Test the automatic population logic
        print(f"\nTesting automatic population logic...")
        
        # Create ream entry repository
        ream_repo = ReamEntryRepository()
        
        # Get all transactions
        all_transactions = ream_repo.get_all()
        print(f"Found {len(all_transactions)} total transactions in database")
        
        # Sort by date (newest first) and limit to 20
        sorted_transactions = sorted(
            all_transactions,
            key=lambda x: x.date_added if x.date_added else '',
            reverse=True
        )[:20]
        
        print(f"Sorted and limited to {len(sorted_transactions)} most recent transactions")
        
        # Display the transactions that would be shown
        print("\nTransactions that would be displayed in recent transactions table:")
        for i, transaction in enumerate(sorted_transactions):
            balance = student_service.get_student_ream_balance(transaction.student_id)
            transaction_type = "Add" if transaction.reams_count > 0 else "Deduct"
            print(f"{i+1}. Student: {transaction.student_id}, Reams: {transaction.reams_count}, "
                  f"Date: {transaction.date_added}, Type: {transaction_type}, Balance: {balance}")
        
        # Verify the balance calculation works for multiple students
        print(f"\nVerifying balance calculation for multiple students...")
        for transaction in sorted_transactions:
            balance = student_service.get_student_ream_balance(transaction.student_id)
            print(f"Student {transaction.student_id}: Current balance = {balance}")
        
        print("\nAutomatic transactions population test completed successfully!")
        return True
        
    except Exception as e:
        print(f"Error during test: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_automatic_transactions_population()
    sys.exit(0 if success else 1)