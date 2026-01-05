"""
Student service for managing student-related operations.
"""

from typing import List, Optional
from school_system.config.logging import logger
from school_system.config.settings import Settings
from school_system.core.exceptions import DatabaseException
from school_system.core.utils import ValidationUtils
from school_system.models.student import Student, ReamEntry, TotalReams
from school_system.database.repositories.student_repo import StudentRepository, ReamEntryRepository, TotalReamsRepository


class StudentService:
    """Service for managing student-related operations."""

    def __init__(self):
        self.student_repository = StudentRepository()

    def get_all_students(self) -> List[Student]:
        """
        Retrieve all students.

        Returns:
            A list of all Student objects.
        """
        return self.student_repository.get_all()

    def get_student_by_id(self, student_id: int) -> Optional[Student]:
        """
        Retrieve a student by their ID.

        Args:
            student_id: The ID of the student.

        Returns:
            The Student object if found, otherwise None.
        """
        return self.student_repository.get_by_id(student_id)

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
        
        student = Student(**student_data)
        created_student = self.student_repository.create(student)
        logger.info(f"Student created successfully with ID: {created_student.id}")
        return created_student

    def update_student(self, student_id: int, student_data: dict) -> Optional[Student]:
        """
        Update an existing student.

        Args:
            student_id: The ID of the student to update.
            student_data: A dictionary containing updated student data.

        Returns:
            The updated Student object if successful, otherwise None.
        """
        student = self.student_repository.get_by_id(student_id)
        if not student:
            return None

        for key, value in student_data.items():
            setattr(student, key, value)

        return self.student_repository.update(student)

    def delete_student(self, student_id: int) -> bool:
        """
        Delete a student.

        Args:
            student_id: The ID of the student to delete.

        Returns:
            True if the student was deleted, otherwise False.
        """
        student = self.student_repository.get_by_id(student_id)
        if not student:
            return False

        self.student_repository.delete(student)
        return True