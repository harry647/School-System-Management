"""
Teacher service for managing teacher-related operations.
"""

from typing import List, Optional
from school_system.config.logging import logger
from school_system.config.settings import Settings
from school_system.core.exceptions import DatabaseException
from school_system.core.utils import ValidationUtils
from school_system.services.import_export_service import ImportExportService
from school_system.models.teacher import Teacher
from school_system.models.book import BorrowedBookTeacher
from school_system.database.repositories.teacher_repo import TeacherRepository
from school_system.database.repositories.book_repo import BorrowedBookTeacherRepository


class TeacherService:
    """Service for managing teacher-related operations."""

    def __init__(self):
        self.teacher_repository = TeacherRepository()
        self.import_export_service = ImportExportService()

    def get_all_teachers(self) -> List[Teacher]:
        """
        Retrieve all teachers.

        Returns:
            A list of all Teacher objects.
        """
        return self.teacher_repository.get_all()

    def get_teacher_by_id(self, teacher_id: int) -> Optional[Teacher]:
        """
        Retrieve a teacher by their ID.

        Args:
            teacher_id: The ID of the teacher.

        Returns:
            The Teacher object if found, otherwise None.
        """
        return self.teacher_repository.get_by_id(teacher_id)

    def create_teacher(self, teacher_data: dict) -> Teacher:
        """
        Create a new teacher.

        Args:
            teacher_data: A dictionary containing teacher data.

        Returns:
            The created Teacher object.
        """
        logger.info(f"Creating a new teacher with data: {teacher_data}")
        ValidationUtils.validate_input(teacher_data.get('name'), "Teacher name cannot be empty")
        
        teacher = Teacher(**teacher_data)
        created_teacher = self.teacher_repository.create(teacher)
        logger.info(f"Teacher created successfully with ID: {created_teacher.id}")
        return created_teacher

    def update_teacher(self, teacher_id: int, teacher_data: dict) -> Optional[Teacher]:
        """
        Update an existing teacher.

        Args:
            teacher_id: The ID of the teacher to update.
            teacher_data: A dictionary containing updated teacher data.

        Returns:
            The updated Teacher object if successful, otherwise None.
        """
        teacher = self.teacher_repository.get_by_id(teacher_id)
        if not teacher:
            return None

        for key, value in teacher_data.items():
            setattr(teacher, key, value)

        return self.teacher_repository.update(teacher)

    def delete_teacher(self, teacher_id: int) -> bool:
        """
        Delete a teacher.

        Args:
            teacher_id: The ID of the teacher to delete.

        Returns:
            True if the teacher was deleted, otherwise False.
        """
        teacher = self.teacher_repository.get_by_id(teacher_id)
        if not teacher:
            return False

        self.teacher_repository.delete(teacher)
        return True

    def get_all_borrowed_books_teacher(self) -> List[BorrowedBookTeacher]:
        """
        Retrieve all borrowed books by teachers.

        Returns:
            A list of all BorrowedBookTeacher objects.
        """
        borrowed_book_teacher_repository = BorrowedBookTeacherRepository()
        return borrowed_book_teacher_repository.get_all()

    def get_borrowed_book_teacher_by_id(self, teacher_id: int) -> Optional[BorrowedBookTeacher]:
        """
        Retrieve a borrowed book by teacher ID.

        Args:
            teacher_id: The ID of the teacher.

        Returns:
            The BorrowedBookTeacher object if found, otherwise None.
        """
        borrowed_book_teacher_repository = BorrowedBookTeacherRepository()
        return borrowed_book_teacher_repository.get_by_id(teacher_id)

    def create_borrowed_book_teacher(self, borrowed_data: dict) -> BorrowedBookTeacher:
        """
        Create a new borrowed book record for a teacher.

        Args:
            borrowed_data: A dictionary containing borrowed book data.

        Returns:
            The created BorrowedBookTeacher object.
        """
        logger.info(f"Creating a new borrowed book record for teacher with data: {borrowed_data}")
        ValidationUtils.validate_input(borrowed_data.get('teacher_id'), "Teacher ID cannot be empty")
        ValidationUtils.validate_input(borrowed_data.get('book_id'), "Book ID cannot be empty")

        borrowed_book = BorrowedBookTeacher(**borrowed_data)
        borrowed_book_teacher_repository = BorrowedBookTeacherRepository()
        created_borrowed_book = borrowed_book_teacher_repository.create(borrowed_book)
        logger.info(f"Borrowed book record created successfully for teacher ID: {created_borrowed_book.teacher_id}")
        return created_borrowed_book

    def update_borrowed_book_teacher(self, teacher_id: int, borrowed_data: dict) -> Optional[BorrowedBookTeacher]:
        """
        Update an existing borrowed book record for a teacher.

        Args:
            teacher_id: The ID of the teacher whose borrowed book record to update.
            borrowed_data: A dictionary containing updated borrowed book data.

        Returns:
            The updated BorrowedBookTeacher object if successful, otherwise None.
        """
        borrowed_book_teacher_repository = BorrowedBookTeacherRepository()
        borrowed_book = borrowed_book_teacher_repository.get_by_id(teacher_id)
        if not borrowed_book:
            return None

        for key, value in borrowed_data.items():
            setattr(borrowed_book, key, value)

        return borrowed_book_teacher_repository.update(borrowed_book)

    def delete_borrowed_book_teacher(self, teacher_id: int) -> bool:
        """
        Delete a borrowed book record for a teacher.

        Args:
            teacher_id: The ID of the teacher whose borrowed book record to delete.

        Returns:
            True if the borrowed book record was deleted, otherwise False.
        """
        borrowed_book_teacher_repository = BorrowedBookTeacherRepository()
        borrowed_book = borrowed_book_teacher_repository.get_by_id(teacher_id)
        if not borrowed_book:
            return False

        borrowed_book_teacher_repository.delete(borrowed_book)
        return True

    def import_teachers_from_excel(self, filename: str) -> List[Teacher]:
        """
        Import teachers from an Excel file.

        Args:
            filename: The name of the Excel file.

        Returns:
            A list of imported Teacher objects.
        """
        logger.info(f"Importing teachers from Excel file: {filename}")
        ValidationUtils.validate_input(filename, "Filename cannot be empty")
        
        try:
            data = self.import_export_service.import_from_excel(filename)
            teachers = []
            
            for teacher_data in data:
                teacher = Teacher(**teacher_data)
                created_teacher = self.teacher_repository.create(teacher)
                teachers.append(created_teacher)
            
            logger.info(f"Successfully imported {len(teachers)} teachers from {filename}")
            return teachers
        except Exception as e:
            logger.error(f"Error importing teachers from Excel: {e}")
            return []

    def export_teachers_to_excel(self, filename: str) -> bool:
        """
        Export teachers to an Excel file.

        Args:
            filename: The name of the Excel file.

        Returns:
            True if the export was successful, otherwise False.
        """
        logger.info(f"Exporting teachers to Excel file: {filename}")
        ValidationUtils.validate_input(filename, "Filename cannot be empty")
        
        try:
            teachers = self.teacher_repository.get_all()
            data = [teacher.__dict__ for teacher in teachers]
            return self.import_export_service.export_to_excel(data, filename)
        except Exception as e:
            logger.error(f"Error exporting teachers to Excel: {e}")
            return False