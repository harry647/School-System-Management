"""
Repository for user session operations.
"""

from .base import BaseRepository
from ...models.session import UserSession


class UserSessionRepository(BaseRepository):
    """Repository for user session operations."""

    def __init__(self):
        super().__init__(UserSession)