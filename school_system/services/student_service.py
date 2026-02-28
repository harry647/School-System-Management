"""
Student service for managing student-related operations.
"""

from typing import List, Optional, Tuple
from datetime import datetime
from school_system.config.logging import logger
from school_system.config.settings import Settings
from school_system.core.exceptions import DatabaseException
from school_system.core.utils import ValidationUtils
from school_system.services.import_export_service import ImportExportService
from school_system.models.student import Student, ReamEntry, TotalReams
from school_system.models.book import DistributionStudent, BorrowedBookStudent
from school_system.database.repositories.student_repo import StudentRepository, ReamEntryRepository, TotalReamsRepository
from school_system.database.repositories.book_repo import DistributionStudentRepository, BorrowedBookStudentRepository
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from school_system.services.class_management_service import ClassManagementService


class StudentService:
    """Service for managing student-related operations."""

    def __init__(self):
        self.student_repository = StudentRepository()
        self.import_export_service = ImportExportService()
        self.class_management_service: Optional[ClassManagementService] = None

    def get_all_students(self, stream: Optional[str] = None) -> List[Student]:
        """
        Retrieve all students, optionally filtered by stream.

        Args:
            stream: Optional stream filter. If provided, only return students from this stream.

        Returns:
            A list of Student objects, optionally filtered by stream.
        """
        students = self.student_repository.get_all()
        if stream:
            students = [s for s in students if s.stream == stream]
        return students

    def get_all_streams(self) -> List[str]:
        """
        Get all unique streams from existing students (legacy method for backward compatibility).

        Returns:
            A list of unique stream names (old format like "4 Red").
        """
        students = self.student_repository.get_all()
        streams = list(set(s.stream for s in students if s.stream))
        return sorted(streams)

    def get_all_classes(self) -> List[str]:
        """
        Get all unique class names from existing students.

        Returns:
            A list of unique class names (e.g., "Form 3", "Form 4", "Grade 10").
        """
        students = self.student_repository.get_all()
        classes = list(set(s.class_name for s in students if s.class_name))
        return sorted(classes)

    def get_all_stream_names(self) -> List[str]:
        """
        Get all unique stream names from existing students.

        Returns:
            A list of unique stream names (e.g., "Red", "Blue", "Orange").
        """
        students = self.student_repository.get_all()
        stream_names = list(set(s.stream_name for s in students if s.stream_name))
        return sorted(stream_names)

    def get_streams_for_class(self, class_name: str) -> List[str]:
        """
        Get all unique stream names for a specific class.

        Args:
            class_name: The class name to get streams for

        Returns:
            A list of unique stream names for the specified class.
        """
        students = self.get_students_by_class(class_name)
        stream_names = list(set(s.stream_name for s in students if s.stream_name))
        return sorted(stream_names)

    def get_students_by_admission_number(self, admission_number: str) -> List[Student]:
        """
        Get students by admission number.

        Args:
            admission_number: The admission number to search for

        Returns:
            List of Student objects matching the admission number
        """
        try:
            return self.student_repository.find_by_field('admission_number', admission_number)
        except Exception as e:
            logger.warning(f"admission_number column not available: {e}")
            return []

    def generate_qr_code_for_student(self, admission_number: str) -> str:
        """
        Generate a unique QR code for a student.

        Args:
            admission_number: Admission number of the student

        Returns:
            The generated QR code string
        """
        try:
            student = self.get_student_by_id(admission_number)
            if not student:
                return None

            qr_code = student.generate_qr_code()
            student.update()
            logger.info(f"Generated QR code {qr_code} for student {admission_number}")
            return qr_code
        except Exception as e:
            logger.error(f"Error generating QR code for student {admission_number}: {e}")
            return None

    def get_student_by_qr_code(self, qr_code: str) -> Optional[Student]:
        """
        Get a student by their QR code.

        Args:
            qr_code: The QR code to search for

        Returns:
            Student object if found, None otherwise
        """
        try:
            students = self.student_repository.find_by_field('qr_code', qr_code)
            return students[0] if students else None
        except Exception as e:
            logger.error(f"Error finding student by QR code {qr_code}: {e}")
            return None

    def get_student_by_id(self, student_id: str) -> Optional[Student]:
        """
        Retrieve a student by their student ID or admission number.

        Args:
            student_id: The student ID or admission number of the student.

        Returns:
            The Student object if found, otherwise None.
        """
        # First try to find by student_id (which should be the same as admission_number in our schema)
        student = self.student_repository.get_by_id(student_id)
        if student:
            return student

        # If not found by student_id, try to find by admission_number (for backward compatibility)
        try:
            students = self.student_repository.find_by_field('admission_number', student_id)
            if students:
                return students[0]
        except Exception:
            # Column might not exist in older databases
            pass

        return None

    def create_student(self, student_data: dict) -> Student:
        """
        Create a new student.

        Args:
            student_data: A dictionary containing student data.

        Returns:
            The created Student object.
        """
        logger.info(f"Creating a new student with data: {student_data}")
        ValidationUtils.validate_input(student_data.get('name'), "Student name cannot be empty")
        ValidationUtils.validate_input(student_data.get('admission_number'), "Admission number cannot be empty")
        
        # Ensure admission_number is provided
        admission_number = student_data.get('admission_number')
        if not admission_number:
            admission_number = student_data.get('student_id')
            if not admission_number:
                raise ValueError("Admission number cannot be empty")
        
        # Remove 'created_at' from student_data if it exists to avoid passing it to the Student constructor
        # Keep student_id if provided, otherwise it will be set to admission_number in Student model
        student_data_copy = student_data.copy()
        student_data_copy.pop('created_at', None)
        # Don't remove student_id - let the Student model handle it
          
        student = Student(**student_data_copy)
        student.save()
        logger.info(f"Student created successfully with ID: {student.student_id}")
        return student

    def update_student(self, admission_number: str, student_data: dict) -> Optional[Student]:
        """
        Update an existing student.

        Args:
            admission_number: The admission number of the student to update.
            student_data: A dictionary containing updated student data.

        Returns:
            The updated Student object if successful, otherwise None.
        """
        # Find student by admission_number first
        students = self.student_repository.find_by_field('admission_number', admission_number)
        if not students:
            return None
        
        student = students[0]

        for key, value in student_data.items():
            setattr(student, key, value)

        student.update()
        return student

    def delete_student(self, admission_number: str) -> bool:
        """
        Delete a student.

        Args:
            admission_number: The admission number of the student to delete.

        Returns:
            True if the student was deleted, otherwise False.
        """
        # Find student by admission_number first
        students = self.student_repository.find_by_field('admission_number', admission_number)
        if not students:
            return False
        
        student = students[0]

        self.student_repository.delete(student.student_id)
        return True


    def get_all_distribution_students(self) -> List[DistributionStudent]:
        """
        Retrieve all distribution student records.

        Returns:
            A list of all DistributionStudent objects.
        """
        distribution_student_repository = DistributionStudentRepository()
        return distribution_student_repository.get_all()

    def get_distribution_student_by_id(self, student_id: int) -> Optional[DistributionStudent]:
        """
        Retrieve a distribution student record by student ID.

        Args:
            student_id: The ID of the student.

        Returns:
            The DistributionStudent object if found, otherwise None.
        """
        distribution_student_repository = DistributionStudentRepository()
        return distribution_student_repository.get_by_id(student_id)

    def create_distribution_student(self, distribution_data: dict) -> DistributionStudent:
        """
        Create a new distribution student record.

        Args:
            distribution_data: A dictionary containing distribution student data.

        Returns:
            The created DistributionStudent object.
        """
        logger.info(f"Creating a new distribution student record with data: {distribution_data}")
        ValidationUtils.validate_input(distribution_data.get('session_id'), "Session ID cannot be empty")
        ValidationUtils.validate_input(distribution_data.get('student_id'), "Student ID cannot be empty")

        distribution_student = DistributionStudent(**distribution_data)
        distribution_student_repository = DistributionStudentRepository()
        created_distribution_student = distribution_student_repository.create(distribution_student)
        logger.info(f"Distribution student record created successfully for student ID: {created_distribution_student.student_id}")
        return created_distribution_student

    def update_distribution_student(self, student_id: int, distribution_data: dict) -> Optional[DistributionStudent]:
        """
        Update an existing distribution student record.

        Args:
            student_id: The ID of the student whose distribution record to update.
            distribution_data: A dictionary containing updated distribution student data.

        Returns:
            The updated DistributionStudent object if successful, otherwise None.
        """
        distribution_student_repository = DistributionStudentRepository()
        distribution_student = distribution_student_repository.get_by_id(student_id)
        if not distribution_student:
            return None

        for key, value in distribution_data.items():
            setattr(distribution_student, key, value)

        return distribution_student_repository.update(distribution_student)

    def delete_distribution_student(self, student_id: int) -> bool:
        """
        Delete a distribution student record.

        Args:
            student_id: The ID of the student whose distribution record to delete.

        Returns:
            True if the distribution student record was deleted, otherwise False.
        """
        distribution_student_repository = DistributionStudentRepository()
        distribution_student = distribution_student_repository.get_by_id(student_id)
        if not distribution_student:
            return False

        distribution_student_repository.delete(distribution_student)
        return True

    def import_students_from_excel(self, filename: str) -> List[Student]:
        """
        Import students from an Excel file.

        Args:
            filename: The name of the Excel file.

        Returns:
            A list of imported Student objects.
        """
        logger.info(f"Importing students from Excel file: {filename}")
        ValidationUtils.validate_input(filename, "Filename cannot be empty")
         
        try:
            data = self.import_export_service.import_from_excel(filename)
            students = []
             
            for student_data in data:
                # Remove 'created_at' from student_data if it exists to avoid passing it to the Student constructor
                # Keep student_id if provided, otherwise it will be set to admission_number in Student model
                student_data_copy = student_data.copy()
                student_data_copy.pop('created_at', None)
                # Don't remove student_id - let the Student model handle it
                
                # Map Excel column names to Student model attributes
                # Excel uses 'Student_ID' but Student model expects 'admission_number'
                if 'Student_ID' in student_data_copy:
                    student_data_copy['admission_number'] = student_data_copy.pop('Student_ID')
                 
                # Excel uses 'Name' (capital N) but Student model expects 'name' (lowercase n)
                if 'Name' in student_data_copy:
                    student_data_copy['name'] = student_data_copy.pop('Name')
                 
                # Excel uses 'Stream' (capital S) but Student model expects 'stream' (lowercase s)
                if 'Stream' in student_data_copy:
                    student_data_copy['stream'] = student_data_copy.pop('Stream')
                 
                student = Student(**student_data_copy)
                student.save()
                students.append(student)
             
            logger.info(f"Successfully imported {len(students)} students from {filename}")
            return students
        except Exception as e:
            logger.error(f"Error importing students from Excel: {e}")
            return []

    def export_students_to_excel(self, filename: str) -> bool:
        """
        Export students to an Excel file.

        Args:
            filename: The name of the Excel file.

        Returns:
            True if the export was successful, otherwise False.
        """
        logger.info(f"Exporting students to Excel file: {filename}")
        ValidationUtils.validate_input(filename, "Filename cannot be empty")
        
        try:
            students = self.student_repository.get_all()
            data = [student.__dict__ for student in students]
            return self.import_export_service.export_to_excel(data, filename)
        except Exception as e:
            logger.error(f"Error exporting students to Excel: {e}")
            return False
    
    # Library-Related Methods

    def get_books_borrowed_by_student(self, admission_number: str) -> List[BorrowedBookStudent]:
        """
        Get all books currently borrowed by a student.
        
        Args:
            admission_number: Admission number of the student
                
        Returns:
            List of books currently borrowed by the student
        """
        # First get the student to find their student_id
        student = self.get_student_by_id(admission_number)
        if not student:
            return []
        
        borrowed_book_repository = BorrowedBookStudentRepository()
        return borrowed_book_repository.find_by_field('student_id', student.student_id)

    def get_student_borrowing_history(self, admission_number: str) -> List[BorrowedBookStudent]:
        """
        Get complete borrowing history for a student.
        
        Args:
            admission_number: Admission number of the student
                
        Returns:
            List of all borrowing records for the student
        """
        # First get the student to find their student_id
        student = self.get_student_by_id(admission_number)
        if not student:
            return []
        
        borrowed_book_repository = BorrowedBookStudentRepository()
        return borrowed_book_repository.find_by_field('student_id', student.student_id)

    def get_student_current_borrowed_books(self, admission_number: str) -> List[BorrowedBookStudent]:
        """
        Get books currently borrowed (not returned) by a student.
        
        Args:
            admission_number: Admission number of the student
                
        Returns:
            List of currently borrowed books
        """
        # First get the student to find their student_id
        student = self.get_student_by_id(admission_number)
        if not student:
            return []
        
        borrowed_book_repository = BorrowedBookStudentRepository()
        # Assuming there's a returned_on field that's NULL for currently borrowed books
        return borrowed_book_repository.get_by_fields(student_id=student.student_id, returned_on=None)

    def get_student_overdue_books(self, admission_number: str) -> List[BorrowedBookStudent]:
        """
        Get overdue books for a student.
        
        Args:
            admission_number: Admission number of the student
                
        Returns:
            List of overdue books
        """
        # First get the student to find their student_id
        student = self.get_student_by_id(admission_number)
        if not student:
            return []
        
        borrowed_book_repository = BorrowedBookStudentRepository()
        # This would need implementation based on due dates
        # For now, return empty list as placeholder
        return []

    def get_student_borrowing_patterns(self, student_id: int) -> dict:
        """
        Analyze student's borrowing patterns and preferences.
        
        Args:
            student_id: ID of the student
                
        Returns:
            Dictionary with borrowing pattern analysis
        """
        borrowing_history = self.get_student_borrowing_history(student_id)
        patterns = {
            'total_books_borrowed': len(borrowing_history),
            'favorite_categories': [],
            'favorite_authors': []
        }
        return patterns

    def record_student_reading_progress(self, progress_data: dict) -> dict:
        """
        Record reading progress for a student on a specific book.
        
        Args:
            progress_data: Dictionary containing progress data
                
        Returns:
            Dictionary with the recorded progress data
        """
        logger.info(f"Recording reading progress for student {progress_data.get('student_id')} on book {progress_data.get('book_id')}")
        # This would need a proper repository and model for reading progress
        # For now, return the data as placeholder
        return progress_data

    def get_student_reading_progress(self, student_id: int, book_id: int = None) -> List[dict]:
        """
        Get reading progress for a student, optionally filtered by book.
        
        Args:
            student_id: ID of the student
            book_id: Optional book ID filter
                
        Returns:
            List of reading progress records
        """
        # This would need proper implementation with a reading progress repository
        return []

    def mark_book_as_read(self, student_id: int, book_id: int, completion_date: str) -> bool:
        """
        Mark a book as completed by a student.
        
        Args:
            student_id: ID of the student
            book_id: ID of the book
            completion_date: Date when book was completed
                
        Returns:
            True if successful, False otherwise
        """
        logger.info(f"Marking book {book_id} as read by student {student_id} on {completion_date}")
        # This would need proper implementation
        return True

    def get_student_reading_history(self, student_id: int) -> List[dict]:
        """
        Get complete reading history for a student.
        
        Args:
            student_id: ID of the student
                
        Returns:
            List of completed books with dates
        """
        # This would need proper implementation
        return []

    def get_student_reading_statistics(self, student_id: int) -> dict:
        """
        Get reading statistics for a student.
        
        Args:
            student_id: ID of the student
                
        Returns:
            Dictionary with reading statistics
        """
        reading_history = self.get_student_reading_history(student_id)
        stats = {
            'total_books_read': len(reading_history),
            'total_pages_read': 0,
            'average_reading_time': 0
        }
        return stats

    def get_student_library_usage(self, student_id: int) -> dict:
        """
        Get comprehensive library usage statistics for a student.
        
        Args:
            student_id: ID of the student
                
        Returns:
            Dictionary with library usage statistics
        """
        borrowing_history = self.get_student_borrowing_history(student_id)
        stats = {
            'total_books_borrowed': len(borrowing_history),
            'total_library_visits': 0,
            'average_books_per_visit': 0
        }
        return stats

    def get_student_library_visits(self, student_id: int, date_range: tuple = None) -> List[dict]:
        """
        Get library visit history for a student.
        
        Args:
            student_id: ID of the student
            date_range: Optional tuple of (start_date, end_date)
                
        Returns:
            List of library visit records
        """
        # This would need proper implementation with a library visits repository
        return []

    def get_student_favorite_categories(self, student_id: int) -> List[str]:
        """
        Get favorite book categories for a student based on borrowing history.
        
        Args:
            student_id: ID of the student
                
        Returns:
            List of favorite categories
        """
        borrowing_history = self.get_student_borrowing_history(student_id)
        # This would need implementation to analyze categories from borrowed books
        return []

    def get_student_favorite_authors(self, student_id: int) -> List[str]:
        """
        Get favorite authors for a student based on borrowing history.
        
        Args:
            student_id: ID of the student
                
        Returns:
            List of favorite authors
        """
        borrowing_history = self.get_student_borrowing_history(student_id)
        # This would need implementation to analyze authors from borrowed books
        return []

    def get_students_by_stream(self, stream: str) -> List[Student]:
        """
        Get students filtered by stream (legacy method for backward compatibility).

        Args:
            stream: Stream to filter by (old format like "4 Red")

        Returns:
            List of students in the specified stream
        """
        return self.student_repository.find_by_field('stream', stream)

    def get_students_by_class(self, class_name: str) -> List[Student]:
        """
        Get students filtered by class.

        Args:
            class_name: Class name to filter by (e.g., "Form 4", "Grade 10")

        Returns:
            List of students in the specified class
        """
        return self.student_repository.find_by_field('class', class_name)

    def get_students_by_stream_name(self, stream_name: str) -> List[Student]:
        """
        Get students filtered by stream name.

        Args:
            stream_name: Stream name to filter by (e.g., "Red", "Blue")

        Returns:
            List of students in the specified stream
        """
        return self.student_repository.find_by_field('stream_name', stream_name)

    def get_students_by_class_and_stream(self, class_name: str, stream_name: str) -> List[Student]:
        """
        Get students filtered by both class and stream.

        Args:
            class_name: Class name to filter by (e.g., "Form 4")
            stream_name: Stream name to filter by (e.g., "Red")

        Returns:
            List of students in the specified class and stream
        """
        return self.student_repository.find_by_multiple_fields({
            'class': class_name,
            'stream_name': stream_name
        })
    
    def get_students_by_class_level(self, class_level: int) -> List[Student]:
        """
        Get all students in a specific class level.
         
        Args:
            class_level: The class level (e.g., 4 for Form 4)
             
        Returns:
            A list of students in that class level
        """
        if self.class_management_service is None:
            from school_system.services.class_management_service import ClassManagementService
            self.class_management_service = ClassManagementService()
        return self.class_management_service.get_students_by_class_level(class_level)
    
    def get_students_by_class_and_stream(self, class_level: int, stream: str) -> List[Student]:
        """
        Get all students in a specific class level and stream combination.
         
        Args:
            class_level: The class level (e.g., 4)
            stream: The stream name (e.g., "Red")
             
        Returns:
            A list of students matching both criteria
        """
        if self.class_management_service is None:
            from school_system.services.class_management_service import ClassManagementService
            self.class_management_service = ClassManagementService()
        return self.class_management_service.get_students_by_class_and_stream(class_level, stream)
    
    def get_all_class_levels(self) -> List[int]:
        """
        Get all unique class levels from the database.
         
        Returns:
            A sorted list of class levels
        """
        if self.class_management_service is None:
            from school_system.services.class_management_service import ClassManagementService
            self.class_management_service = ClassManagementService()
        return self.class_management_service.get_all_class_levels()
    
    def get_all_streams_for_class(self, class_level: Optional[int] = None) -> List[str]:
        """
        Get all unique streams, optionally filtered by class level.
         
        Args:
            class_level: Optional class level filter
             
        Returns:
            A sorted list of unique stream names
        """
        if self.class_management_service is None:
            from school_system.services.class_management_service import ClassManagementService
            self.class_management_service = ClassManagementService()
        return self.class_management_service.get_all_streams(class_level)
    
    def get_class_stream_combinations(self) -> List[Tuple[int, str, int]]:
        """
        Get all class-stream combinations with student counts.
         
        Returns:
            A list of tuples: (class_level, stream, student_count)
        """
        if self.class_management_service is None:
            from school_system.services.class_management_service import ClassManagementService
            self.class_management_service = ClassManagementService()
        return self.class_management_service.get_class_stream_combinations()
    
    def get_class_statistics(self) -> dict:
        """
        Get comprehensive statistics about classes and streams.
         
        Returns:
            A dictionary with statistics
        """
        if self.class_management_service is None:
            from school_system.services.class_management_service import ClassManagementService
            self.class_management_service = ClassManagementService()
        return self.class_management_service.get_class_statistics()

    def get_student_library_activity_summary(self, student_id: int) -> dict:
        """
        Get a summary of student's library activity.
        
        Args:
            student_id: ID of the student
                
        Returns:
            Dictionary with activity summary
        """
        summary = {
            'total_books_borrowed': len(self.get_student_borrowing_history(student_id)),
            'current_books_borrowed': len(self.get_student_current_borrowed_books(student_id)),
            'overdue_books': len(self.get_student_overdue_books(student_id)),
            'books_read': len(self.get_student_reading_history(student_id))
        }
        return summary

    # Ream-Related Methods

    def get_student_ream_balance(self, admission_number: str) -> int:
        """
        Get the current ream balance for a student.
            
        Args:
            admission_number: Admission number of the student
                
        Returns:
            Current ream balance
        """
        # First get the student to find their student_id
        student = self.get_student_by_id(admission_number)
        if not student:
            return 0
            
        ream_entry_repository = ReamEntryRepository()
        ream_entries = ream_entry_repository.find_by_field('student_id', student.student_id)
            
        balance = 0
        for entry in ream_entries:
            balance += entry.reams_count
            
        return balance

    def add_reams_to_student(self, student_id: str, reams_count: int, source: str = "Distribution") -> ReamEntry:
        """
        Add reams to a student's account with source tracking.
           
        Args:
            student_id: Student ID or admission number of the student
            reams_count: Number of reams to add
            source: Source of the reams (Distribution, Purchase, Transfer, etc.)
                
        Returns:
            The created ream entry
        """
        # First get the student to find their student_id
        # Try to find by student_id first, then by admission_number
        student = self.get_student_by_id(student_id)
        if not student:
            # If not found by student_id, try to find by admission_number
            students = self.student_repository.find_by_field('admission_number', student_id)
            student = students[0] if students else None
         
        if not student:
            logger.error(f"Student with ID {student_id} not found in database")
            raise ValueError(f"Student with ID {student_id} not found in database. Please ensure the student exists before adding reams.")
         
        logger.info(f"Adding {reams_count} reams to student {student_id} from source: {source}")
           
        ream_entry = ReamEntry(
            student_id=student.student_id,
            reams_count=reams_count,
            date_added=datetime.now().strftime('%Y-%m-%d')
        )
           
        ream_entry_repository = ReamEntryRepository()
        created_entry = ream_entry_repository.create(ream_entry)
           
        logger.info(f"Successfully added {reams_count} reams to student {student_id}")
        return created_entry

    def record_ream_distribution(self, distribution_data: dict) -> dict:
        """
        Record a ream distribution event.
         
        Args:
            distribution_data: Dictionary containing distribution data
              
        Returns:
            Dictionary with the recorded distribution data
        """
        logger.info(f"Recording ream distribution: {distribution_data}")
        # This would need proper implementation with a distribution repository
        return distribution_data

    def get_student_ream_distribution_history(self, student_id: int) -> List[dict]:
        """
        Get ream distribution history for a student.
         
        Args:
            student_id: ID of the student
              
        Returns:
            List of ream distribution records
        """
        # This would need proper implementation
        return []

    def record_ream_usage(self, usage_data: dict) -> dict:
        """
        Record ream usage by a student.
         
        Args:
            usage_data: Dictionary containing usage data
              
        Returns:
            Dictionary with the recorded usage data
        """
        logger.info(f"Recording ream usage: {usage_data}")
        # This would need proper implementation with a usage repository
        return usage_data

    def get_student_ream_usage_history(self, student_id: int) -> List[dict]:
        """
        Get ream usage history for a student.
         
        Args:
            student_id: ID of the student
              
        Returns:
            List of ream usage records
        """
        # This would need proper implementation
        return []

    def get_student_ream_usage_by_purpose(self, student_id: int) -> dict:
        """
        Get ream usage breakdown by purpose for a student.
         
        Args:
            student_id: ID of the student
              
        Returns:
            Dictionary with usage breakdown by purpose
        """
        usage_history = self.get_student_ream_usage_history(student_id)
        breakdown = {}
        
        for usage in usage_history:
            purpose = usage.get('purpose', 'Unknown')
            reams_used = usage.get('reams_used', 0)
            breakdown[purpose] = breakdown.get(purpose, 0) + reams_used
        
        return breakdown

    def get_student_ream_transaction_history(self, admission_number: str, date_range: tuple = None) -> List[ReamEntry]:
        """
        Get complete ream transaction history for a student.
         
        Args:
            admission_number: Admission number of the student
            date_range: Optional tuple of (start_date, end_date)
               
        Returns:
            List of ream transaction records
        """
        # First get the student to find their student_id
        student = self.get_student_by_id(admission_number)
        if not student:
            return []
        
        ream_entry_repository = ReamEntryRepository()
        transactions = ream_entry_repository.find_by_field('student_id', student.student_id)
        
        # Filter by date range if provided
        if date_range:
            start_date, end_date = date_range
            filtered_transactions = []
            for transaction in transactions:
                if start_date <= transaction.date_added <= end_date:
                    filtered_transactions.append(transaction)
            return filtered_transactions
        
        return transactions

    def get_student_ream_summary(self, student_id: int) -> dict:
        """
        Get ream usage summary for a student.
         
        Args:
            student_id: ID of the student
              
        Returns:
            Dictionary with ream usage summary statistics
        """
        transactions = self.get_student_ream_transaction_history(student_id)
        
        if not transactions:
            return {
                'current_balance': 0,
                'total_reams_added': 0,
                'total_reams_used': 0,
                'total_transactions': 0,
                'average_daily_usage': 0
            }
        
        total_added = sum(t.reams_count for t in transactions if t.reams_count > 0)
        total_used = abs(sum(t.reams_count for t in transactions if t.reams_count < 0))
        current_balance = self.get_student_ream_balance(student_id)
        
        return {
            'current_balance': current_balance,
            'total_reams_added': total_added,
            'total_reams_used': total_used,
            'total_transactions': len(transactions),
            'average_daily_usage': total_used / len(transactions) if transactions else 0
        }

    def get_class_ream_usage(self, class_id: int) -> dict:
        """
        Get ream usage statistics for an entire class.
        
        Args:
            class_id: ID of the class
                
        Returns:
            Dictionary with class ream usage statistics
        """
        # This would need implementation to get students in a class
        # For now, return placeholder data
        return {
            'total_class_usage': 0,
            'average_per_student': 0,
            'top_users': []
        }

    def get_stream_ream_usage(self, stream: str) -> dict:
        """
        Get ream usage statistics for a specific stream.
        
        Args:
            stream: Name of the stream
                
        Returns:
            Dictionary with stream ream usage statistics
        """
        students_in_stream = self.get_students_by_stream(stream)
        total_usage = 0
        
        for student in students_in_stream:
            balance = self.get_student_ream_balance(student.student_id)
            total_usage += balance
        
        return {
            'stream': stream,
            'total_students': len(students_in_stream),
            'total_ream_usage': total_usage,
            'average_per_student': total_usage / len(students_in_stream) if students_in_stream else 0
        }

    def get_ream_usage_trends(self, time_period: str = "monthly") -> dict:
        """
        Get ream usage trends over time.
        
        Args:
            time_period: Time period for trends (daily, weekly, monthly, yearly)
                
        Returns:
            Dictionary with usage trends data
        """
        # This would need proper implementation with date analysis
        return {
            'time_period': time_period,
            'trend_data': [],
            'overall_trend': 'stable'
        }

    def generate_ream_usage_report(self, report_type: str, parameters: dict = None) -> dict:
        """
        Generate a comprehensive ream usage report.
        
        Args:
            report_type: Type of report to generate
            parameters: Optional report parameters
                
        Returns:
            Dictionary containing the generated report
        """
        report_data = {
            'report_type': report_type,
            'generated_on': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'parameters': parameters or {}
        }
        
        if report_type == 'student_summary':
            student_id = parameters.get('student_id')
            if student_id:
                report_data['student_data'] = self.get_student_ream_summary(student_id)
        
        elif report_type == 'stream_summary':
            stream = parameters.get('stream')
            if stream:
                report_data['stream_data'] = self.get_stream_ream_usage(stream)
        
        return report_data

    def deduct_reams_from_student(self, student_id: str, reams_count: int, purpose: str = "Usage") -> ReamEntry:
        """
        Deduct reams from a student's account with purpose tracking.
             
        Args:
            student_id: Student ID or admission number of the student
            reams_count: Number of reams to deduct
            purpose: Purpose of the deduction (Usage, Transfer, Loss, etc.)
                 
        Returns:
            The created ream entry
        """
        # First get the student to find their student_id
        # Try to find by student_id first, then by admission_number
        student = self.get_student_by_id(student_id)
        if not student:
            # If not found by student_id, try to find by admission_number
            students = self.student_repository.find_by_field('admission_number', student_id)
            student = students[0] if students else None
         
        if not student:
            logger.error(f"Student with ID {student_id} not found in database")
            raise ValueError(f"Student with ID {student_id} not found in database. Please ensure the student exists before deducting reams.")
              
        logger.info(f"Deducting {reams_count} reams from student {student_id} for purpose: {purpose}")
             
        # Use negative value to represent deduction
        ream_entry = ReamEntry(
            student_id=student.student_id,
            reams_count=-reams_count,
            date_added=datetime.now().strftime('%Y-%m-%d')
        )
             
        ream_entry_repository = ReamEntryRepository()
        created_entry = ream_entry_repository.create(ream_entry)
             
        logger.info(f"Successfully deducted {reams_count} reams from student {student_id}")
        return created_entry

    def transfer_reams_between_students(self, from_student_id: str, to_student_id: str, reams_count: int, reason: str = "") -> bool:
        """
        Transfer reams between two students with reason tracking.
             
        Args:
            from_student_id: ID or admission number of the student sending reams
            to_student_id: ID or admission number of the student receiving reams
            reams_count: Number of reams to transfer
            reason: Reason for the transfer
                 
        Returns:
            True if transfer was successful, False otherwise
        """
        logger.info(f"Transferring {reams_count} reams from student {from_student_id} to student {to_student_id}")
             
        try:
            # Check if source student has enough reams
            source_balance = self.get_student_ream_balance(from_student_id)
            
            if source_balance < reams_count:
                logger.warning(f"Source student {from_student_id} only has {source_balance} reams, cannot transfer {reams_count}")
                # Transfer only what's available
                actual_transfer_amount = source_balance
                if actual_transfer_amount <= 0:
                    logger.error(f"Source student {from_student_id} has insufficient reams for transfer")
                    return False
                
                logger.info(f"Adjusting transfer amount from {reams_count} to {actual_transfer_amount} due to insufficient balance")
                reams_count = actual_transfer_amount
            
            # Deduct from source student
            self.deduct_reams_from_student(from_student_id, reams_count, f"Transfer to {to_student_id}")
                 
            # Add to destination student
            self.add_reams_to_student(to_student_id, reams_count, f"Transfer from {from_student_id}")
                 
            logger.info(f"Successfully transferred {reams_count} reams from student {from_student_id} to student {to_student_id}")
            return True
        except Exception as e:
            logger.error(f"Error transferring reams: {e}")
            return False

    def adjust_student_ream_balance(self, student_id: int, adjustment: int, reason: str) -> ReamEntry:
        """
        Adjust student ream balance with reason tracking.
        
        Args:
            student_id: ID of the student
            adjustment: Positive or negative adjustment amount
            reason: Reason for the adjustment
                
        Returns:
            The created ream entry
        """
        logger.info(f"Adjusting student {student_id} ream balance by {adjustment} for reason: {reason}")
        
        ream_entry = ReamEntry(
            student_id=student_id,
            reams_count=adjustment,
            date_added=datetime.now().strftime('%Y-%m-%d')
        )
        
        ream_entry_repository = ReamEntryRepository()
        created_entry = ream_entry_repository.create(ream_entry)
        
        logger.info(f"Successfully adjusted student {student_id} ream balance by {adjustment}")
        return created_entry

    # ============================================================================
    # STUDENT PROMOTION METHODS
    # ============================================================================

    def get_next_class(self, current_class: str) -> Optional[str]:
        """
        Get the next class for promotion based on current class.

        Args:
            current_class: Current class name (e.g., "Form 1", "Grade 10")

        Returns:
            Next class name or None if no promotion available
        """
        class_progression = {
            "Form 1": "Form 2",
            "Form 2": "Form 3",
            "Form 3": "Form 4",
            "Grade 10": "Grade 11",
            "Grade 11": "Grade 12"
        }

        return class_progression.get(current_class)

    def promote_student(self, admission_number: str, target_class: Optional[str] = None) -> bool:
        """
        Promote a single student to the next class or specified class.

        Args:
            admission_number: The admission number of the student to promote
            target_class: Optional target class. If None, promotes to next class

        Returns:
            True if promotion was successful, False otherwise
        """
        try:
            # Find student
            students = self.student_repository.find_by_field('admission_number', admission_number)
            if not students:
                logger.warning(f"Student with admission number {admission_number} not found")
                return False

            student = students[0]

            # Determine target class
            if target_class is None:
                target_class = self.get_next_class(student.class_name)
                if target_class is None:
                    logger.warning(f"No promotion available for class {student.class_name}")
                    return False

            # Update student's class
            student_data = {
                'class_name': target_class,
                'stream': f"{self._extract_class_level(target_class)} {student.stream_name}" if student.stream_name else ""
            }

            success = self.update_student(admission_number, student_data)
            if success:
                logger.info(f"Successfully promoted student {admission_number} from {student.class_name} to {target_class}")
                return True
            else:
                logger.error(f"Failed to update student {admission_number} during promotion")
                return False

        except Exception as e:
            logger.error(f"Error promoting student {admission_number}: {e}")
            return False

    def promote_students_by_class(self, current_class: str, target_class: Optional[str] = None) -> tuple[int, int]:
        """
        Promote all students in a specific class.

        Args:
            current_class: The class to promote students from
            target_class: Optional target class. If None, promotes to next class

        Returns:
            tuple: (successful_promotions, total_students)
        """
        try:
            # Get all students in the current class
            students = self.get_students_by_class(current_class)
            if not students:
                logger.info(f"No students found in class {current_class}")
                return 0, 0

            # Determine target class
            if target_class is None:
                target_class = self.get_next_class(current_class)
                if target_class is None:
                    logger.warning(f"No promotion available for class {current_class}")
                    return 0, 0

            successful_promotions = 0

            for student in students:
                try:
                    success = self.promote_student(student.admission_number, target_class)
                    if success:
                        successful_promotions += 1
                except Exception as e:
                    logger.error(f"Error promoting student {student.admission_number}: {e}")

            logger.info(f"Promoted {successful_promotions} out of {len(students)} students from {current_class} to {target_class}")
            return successful_promotions, len(students)

        except Exception as e:
            logger.error(f"Error promoting students by class {current_class}: {e}")
            return 0, 0

    def promote_all_students_yearly(self) -> dict:
        """
        Perform yearly promotion for all eligible students.

        Returns:
            dict: Summary of promotions by class
        """
        try:
            promotion_summary = {}
            total_promoted = 0
            total_processed = 0

            # Classes that can be promoted
            promotable_classes = ["Form 1", "Form 2", "Form 3", "Grade 10", "Grade 11"]

            for current_class in promotable_classes:
                promoted, total = self.promote_students_by_class(current_class)
                if total > 0:
                    promotion_summary[current_class] = {
                        'promoted': promoted,
                        'total': total,
                        'target_class': self.get_next_class(current_class)
                    }
                    total_promoted += promoted
                    total_processed += total

            logger.info(f"Yearly promotion completed: {total_promoted} out of {total_processed} students promoted")
            return {
                'summary': promotion_summary,
                'total_promoted': total_promoted,
                'total_processed': total_processed,
                'success_rate': (total_promoted / total_processed * 100) if total_processed > 0 else 0
            }

        except Exception as e:
            logger.error(f"Error performing yearly promotion: {e}")
            return {
                'summary': {},
                'total_promoted': 0,
                'total_processed': 0,
                'success_rate': 0,
                'error': str(e)
            }

    def _extract_class_level(self, class_name: str) -> Optional[int]:
        """
        Extract numeric class level from class name (e.g., 'Form 4' -> 4).

        Args:
            class_name: The class name

        Returns:
            The numeric level, or None if extraction fails
        """
        if not class_name:
            return None

        class_name = class_name.lower()
        if 'form' in class_name:
            parts = class_name.split()
            for part in parts:
                if part.isdigit():
                    return int(part)
        elif 'grade' in class_name:
            parts = class_name.split()
            for part in parts:
                if part.isdigit():
                    return int(part)
        elif class_name.isdigit():
            return int(class_name)

        return None
