"""
Teacher service for managing teacher-related operations.
"""

from typing import List, Optional
import datetime
from school_system.config.logging import logger
from school_system.config.settings import Settings
from school_system.core.exceptions import DatabaseException
from school_system.core.utils import ValidationUtils
from school_system.services.import_export_service import ImportExportService
from school_system.models.teacher import Teacher
from school_system.database.repositories.teacher_repo import TeacherRepository


class TeacherService:
    """Service for managing teacher-related operations."""

    def __init__(self):
        self.teacher_repository = TeacherRepository()
        self.import_export_service = ImportExportService()
        self.undo_stack = []

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
        ValidationUtils.validate_input(teacher_data.get('teacher_name'), "Teacher name cannot be empty")
        ValidationUtils.validate_input(teacher_data.get('teacher_id'), "Teacher ID cannot be empty")
        
        teacher = Teacher(**teacher_data)
        created_teacher = self.teacher_repository.create(teacher)
        logger.info(f"Teacher created successfully with ID: {created_teacher.teacher_id}")
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


    def track_operation(self, operation_type: str, operation_data: dict):
        """Track an operation for potential undo."""
        # Add to undo stack (limit to last 10 operations)
        self.undo_stack.append({
            'type': operation_type,
            'data': operation_data,
            'timestamp': datetime.datetime.now().isoformat()
        })
        
        # Limit stack size
        if len(self.undo_stack) > 10:
            self.undo_stack.pop(0)

    def undo_operation(self, operation: dict):
        """Undo an operation."""
        if operation['type'] == 'create':
            # Undo create by deleting
            teacher_id = operation['data']['teacher_id']
            self.delete_teacher(teacher_id)
        elif operation['type'] == 'delete':
            # Undo delete by recreating
            teacher_data = operation['data']
            self.create_teacher(teacher_data)
        elif operation['type'] == 'update':
            # Undo update by reverting to old data
            operation_data = operation['data']
            teacher_id = operation_data['teacher_id']
            old_data = operation_data['old_data']
            
            # Revert to old data
            self.update_teacher(teacher_id, old_data)

    def clear_undo_stack(self):
        """Clear the undo stack."""
        self.undo_stack.clear()

    def get_teacher_details(self, teacher):
        """Get formatted teacher details."""
        return f"Teacher Details:\n\nID: {teacher.teacher_id}\nName: {teacher.teacher_name}\nDepartment: {getattr(teacher, 'department', 'N/A')}"

    def assign_subject_to_teacher(self, teacher_id: str, subject_id: str) -> bool:
        """Assign a subject to a teacher."""
        # Placeholder implementation
        return True

    def assign_class_to_teacher(self, teacher_id: str, class_id: str) -> bool:
        """Assign a class to a teacher."""
        # Placeholder implementation
        return True

    def update_teacher_availability(self, teacher_id: str, availability_data: dict) -> bool:
        """Update teacher availability."""
        # Placeholder implementation
        return True

    def add_teacher_performance_record(self, teacher_id: str, performance_data: dict) -> bool:
        """Add a performance record for a teacher."""
        # Placeholder implementation
        return True

    def validate_teacher_qualifications(self, teacher_id: str, qualifications: list) -> bool:
        """Validate teacher qualifications."""
        # Placeholder implementation
        return True

    def send_teacher_notification(self, teacher_id: str, message: str) -> bool:
        """Send a notification to a teacher."""
        # Placeholder implementation
        return True

    def get_teacher_statistics(self, teacher_id: str) -> dict:
        """Get statistics for a teacher."""
        # Placeholder implementation
        return {
            'teacher_name': 'N/A',
            'subjects_taught': 0,
            'classes_assigned': 0,
            'performance_records': 0,
            'qualifications': 0
        }
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
