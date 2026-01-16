"""
Repository for teacher operations.
"""

from .base import BaseRepository
from ...models.teacher import Teacher


class TeacherRepository(BaseRepository):
    """Repository for teacher operations."""

    def __init__(self):
        super().__init__(Teacher)

    def validate_teacher_data(self, teacher_id: str, teacher_name: str) -> bool:
        """Validate teacher data before operations."""
        try:
            from ...core.validators import TeacherValidator
            TeacherValidator.validate_teacher_id(teacher_id)
            TeacherValidator.validate_name(teacher_name)
            return True
        except Exception as e:
            raise Exception(f"Teacher validation failed: {e}")
