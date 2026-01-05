"""
Teacher service for managing teacher-related operations.
"""

from typing import List, Optional
from school_system.config.logging import logger
from school_system.config.settings import Settings
from school_system.core.exceptions import DatabaseException
from school_system.core.utils import validate_input
from school_system.models.teacher import Teacher
from school_system.database.repositories.teacher_repository import TeacherRepository


class TeacherService:
    """Service for managing teacher-related operations."""

    def __init__(self):
        self.teacher_repository = TeacherRepository()

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
        validate_input(teacher_data.get('name'), "Teacher name cannot be empty")
        
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