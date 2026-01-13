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

    def search_teachers(self, name: str = None, subject: str = None) -> List[Teacher]:
        """
        Search teachers by name or subject.

        Args:
            name: Optional name to search for.
            subject: Optional subject to filter by.

        Returns:
            A list of Teacher objects matching the criteria.
        """
        teachers = self.teacher_repository.get_all()
        results = []

        for teacher in teachers:
            match = True
            if name and name.lower() not in teacher.teacher_name.lower():
                match = False
            # Note: This assumes the Teacher model has a subject field
            # If not, this would need to be added to the model
            # if subject and teacher.subject and subject.lower() not in teacher.subject.lower():
            #     match = False

            if match:
                results.append(teacher)

        return results

    def create_teachers_batch(self, teachers_data: List[dict]) -> List[Teacher]:
        """
        Create multiple teachers in a single operation.

        Args:
            teachers_data: A list of dictionaries containing teacher data.

        Returns:
            A list of created Teacher objects.
        """
        created_teachers = []
        for teacher_data in teachers_data:
            try:
                ValidationUtils.validate_input(teacher_data.get('name'), "Teacher name cannot be empty")
                teacher = Teacher(**teacher_data)
                created_teacher = self.teacher_repository.create(teacher)
                created_teachers.append(created_teacher)
            except Exception as e:
                logger.error(f"Error creating teacher in batch: {e}")
                continue

        logger.info(f"Successfully created {len(created_teachers)} teachers in batch")
        return created_teachers

    def assign_subject_to_teacher(self, teacher_id: int, subject_id: int) -> bool:
        """
        Assign a subject to a teacher.

        Args:
            teacher_id: The ID of the teacher.
            subject_id: The ID of the subject to assign.

        Returns:
            True if the assignment was successful, otherwise False.
        """
        teacher = self.teacher_repository.get_by_id(teacher_id)
        if not teacher:
            return False

        # This would require a teacher_subjects association table
        # For now, we'll simulate this by adding to a subjects list
        # In a real implementation, this would use a proper relationship
        try:
            if not hasattr(teacher, 'subjects'):
                teacher.subjects = []
            if subject_id not in teacher.subjects:
                teacher.subjects.append(subject_id)
                self.teacher_repository.update(teacher)
            return True
        except Exception as e:
            logger.error(f"Error assigning subject to teacher: {e}")
            return False

    def assign_class_to_teacher(self, teacher_id: int, class_id: int) -> bool:
        """
        Assign a class to a teacher.

        Args:
            teacher_id: The ID of the teacher.
            class_id: The ID of the class to assign.

        Returns:
            True if the assignment was successful, otherwise False.
        """
        teacher = self.teacher_repository.get_by_id(teacher_id)
        if not teacher:
            return False

        # This would require a teacher_classes association table
        # For now, we'll simulate this by adding to a classes list
        try:
            if not hasattr(teacher, 'classes'):
                teacher.classes = []
            if class_id not in teacher.classes:
                teacher.classes.append(class_id)
                self.teacher_repository.update(teacher)
            return True
        except Exception as e:
            logger.error(f"Error assigning class to teacher: {e}")
            return False

    def update_teacher_availability(self, teacher_id: int, availability: dict) -> bool:
        """
        Update teacher's availability schedule.

        Args:
            teacher_id: The ID of the teacher.
            availability: A dictionary containing availability data.

        Returns:
            True if the update was successful, otherwise False.
        """
        teacher = self.teacher_repository.get_by_id(teacher_id)
        if not teacher:
            return False

        try:
            teacher.availability = availability
            self.teacher_repository.update(teacher)
            return True
        except Exception as e:
            logger.error(f"Error updating teacher availability: {e}")
            return False

    def add_teacher_performance_record(self, teacher_id: int, performance_data: dict) -> bool:
        """
        Add performance record for a teacher.

        Args:
            teacher_id: The ID of the teacher.
            performance_data: A dictionary containing performance data.

        Returns:
            True if the record was added successfully, otherwise False.
        """
        teacher = self.teacher_repository.get_by_id(teacher_id)
        if not teacher:
            return False

        try:
            if not hasattr(teacher, 'performance_records'):
                teacher.performance_records = []
            teacher.performance_records.append(performance_data)
            self.teacher_repository.update(teacher)
            return True
        except Exception as e:
            logger.error(f"Error adding performance record: {e}")
            return False

    def validate_teacher_qualifications(self, teacher_id: int, qualifications: List[str]) -> bool:
        """
        Validate teacher qualifications.

        Args:
            teacher_id: The ID of the teacher.
            qualifications: A list of qualifications to validate.

        Returns:
            True if qualifications are valid, otherwise False.
        """
        teacher = self.teacher_repository.get_by_id(teacher_id)
        if not teacher:
            return False

        try:
            # Basic validation - in a real system, this would be more comprehensive
            if not qualifications or len(qualifications) == 0:
                return False

            # Store validated qualifications
            teacher.qualifications = qualifications
            self.teacher_repository.update(teacher)
            return True
        except Exception as e:
            logger.error(f"Error validating teacher qualifications: {e}")
            return False

    def get_teacher_statistics(self, teacher_id: int) -> dict:
        """
        Get statistics for a specific teacher.

        Args:
            teacher_id: The ID of the teacher.

        Returns:
            A dictionary containing teacher statistics.
        """
        teacher = self.teacher_repository.get_by_id(teacher_id)
        if not teacher:
            return {}

        try:
            stats = {
                'teacher_id': teacher.teacher_id,
                'teacher_name': teacher.teacher_name,
                'subjects_taught': len(getattr(teacher, 'subjects', [])),
                'classes_assigned': len(getattr(teacher, 'classes', [])),
                'performance_records': len(getattr(teacher, 'performance_records', [])),
                'qualifications': len(getattr(teacher, 'qualifications', []))
            }
            return stats
        except Exception as e:
            logger.error(f"Error getting teacher statistics: {e}")
            return {}

    def assign_department(self, teacher_id: int, department_id: int) -> bool:
        """
        Assign teacher to a department.

        Args:
            teacher_id: The ID of the teacher.
            department_id: The ID of the department.

        Returns:
            True if the assignment was successful, otherwise False.
        """
        teacher = self.teacher_repository.get_by_id(teacher_id)
        if not teacher:
            return False

        try:
            teacher.department_id = department_id
            self.teacher_repository.update(teacher)
            return True
        except Exception as e:
            logger.error(f"Error assigning department to teacher: {e}")
            return False

    def send_teacher_notification(self, teacher_id: int, message: str) -> bool:
        """
        Send notification to a teacher.

        Args:
            teacher_id: The ID of the teacher.
            message: The notification message.

        Returns:
            True if the notification was sent successfully, otherwise False.
        """
        teacher = self.teacher_repository.get_by_id(teacher_id)
        if not teacher:
            return False

        try:
            # This would integrate with a notification service
            # For now, we'll simulate by storing the notification
            if not hasattr(teacher, 'notifications'):
                teacher.notifications = []
            teacher.notifications.append({
                'message': message,
                'timestamp': datetime.datetime.now().isoformat(),
                'read': False
            })
            self.teacher_repository.update(teacher)
            return True
        except Exception as e:
            logger.error(f"Error sending teacher notification: {e}")
            return False