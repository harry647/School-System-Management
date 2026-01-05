"""
Repository for user operations.
"""

from .base import BaseRepository
from ...models.user import User, UserSetting, ShortFormMapping


class UserRepository(BaseRepository):
    """Repository for user operations."""

    def __init__(self):
        super().__init__(User)

    def validate_user_data(self, username: str, password: str) -> bool:
        """Validate user data before operations."""
        try:
            from ...core.validators import UserValidator
            UserValidator.validate_username(username)
            UserValidator.validate_password(password)
            return True
        except Exception as e:
            raise Exception(f"User validation failed: {e}")


class UserSettingRepository(BaseRepository):
    """Repository for user setting operations."""

    def __init__(self):
        super().__init__(UserSetting)


class ShortFormMappingRepository(BaseRepository):
    """Repository for short form mapping operations."""

    def __init__(self):
        super().__init__(ShortFormMapping)