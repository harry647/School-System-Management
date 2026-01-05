"""
Student service for managing student-related operations.
"""

from typing import List, Optional
from school_system.config.logging import logger
from school_system.config.settings import Settings
from school_system.core.exceptions import DatabaseException
from school_system.core.utils import ValidationUtils
from school_system.services.import_export_service import ImportExportService
from school_system.models.student import Student, ReamEntry, TotalReams
from school_system.models.book import DistributionStudent
from school_system.database.repositories.student_repo import StudentRepository, ReamEntryRepository, TotalReamsRepository
from school_system.database.repositories.book_repo import DistributionStudentRepository


class StudentService:
    """Service for managing student-related operations."""

    def __init__(self):
        self.student_repository = StudentRepository()
        self.import_export_service = ImportExportService()

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
                student = Student(**student_data)
                created_student = self.student_repository.create(student)
                students.append(created_student)
            
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