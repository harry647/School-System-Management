"""
Repository for furniture operations.
"""

from .base import BaseRepository
from ...models.furniture import Chair, Locker, FurnitureCategory, LockerAssignment, ChairAssignment


class ChairRepository(BaseRepository):
    """Repository for chair operations."""

    def __init__(self):
        super().__init__(Chair)


class LockerRepository(BaseRepository):
    """Repository for locker operations."""

    def __init__(self):
        super().__init__(Locker)


class FurnitureCategoryRepository(BaseRepository):
    """Repository for furniture category operations."""

    def __init__(self):
        super().__init__(FurnitureCategory)


class LockerAssignmentRepository(BaseRepository):
    """Repository for locker assignment operations."""

    def __init__(self):
        super().__init__(LockerAssignment)


class ChairAssignmentRepository(BaseRepository):
    """Repository for chair assignment operations."""

    def __init__(self):
        super().__init__(ChairAssignment)
