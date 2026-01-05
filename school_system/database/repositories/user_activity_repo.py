"""
Repository for user activity operations.
"""

from .base import BaseRepository
from ...models.user_activity import UserActivity


class UserActivityRepository(BaseRepository):
    """Repository for user activity operations."""

    def __init__(self):
        super().__init__(UserActivity)