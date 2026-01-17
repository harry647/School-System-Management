"""
Repository for student operations.
"""

from .base import BaseRepository
from ...models.student import Student, ReamEntry, TotalReams


class StudentRepository(BaseRepository):
    """Repository for student operations."""

    def __init__(self):
        super().__init__(Student)

    def validate_student_data(self, student_id: str, name: str, stream: str) -> bool:
        """Validate student data before operations."""
        try:
            from ...core.validators import StudentValidator
            StudentValidator.validate_student_id(student_id)
            StudentValidator.validate_name(name)
            # Add stream validation if available
            return True
        except Exception as e:
            raise Exception(f"Student validation failed: {e}")


class ReamEntryRepository(BaseRepository):
    """Repository for ream entry operations."""

    def __init__(self):
        super().__init__(ReamEntry)

    def add_ream_entry(self, student_id: str, reams_count: int):
        """Add a ream entry for a student."""
        from datetime import datetime
        ream_entry = ReamEntry(
            student_id=student_id,
            reams_count=reams_count,
            date_added=datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            created_at=datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        )
        return self.create(ream_entry)


class TotalReamsRepository(BaseRepository):
    """Repository for total reams operations."""

    def __init__(self):
        super().__init__(TotalReams)
