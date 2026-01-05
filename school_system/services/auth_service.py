"""
Authentication service for handling user authentication and authorization.
"""

from school_system.config.logging import logger
from school_system.config.settings import Settings
from school_system.core.exceptions import AuthenticationException
from school_system.core.utils import validate_input
from school_system.models.user import User
from school_system.database.repositories.user_repository import UserRepository


class AuthService:
    """Service for handling authentication and authorization."""

    def __init__(self):
        self.user_repository = UserRepository()

    def authenticate_user(self, username: str, password: str) -> User:
        """
        Authenticate a user with the provided credentials.

        Args:
            username: The username of the user.
            password: The password of the user.

        Returns:
            The authenticated User object.

        Raises:
            AuthenticationException: If authentication fails.
        """
        logger.info(f"Attempting to authenticate user: {username}")
        validate_input(username, "Username cannot be empty")
        validate_input(password, "Password cannot be empty")
        
        user = self.user_repository.get_user_by_username(username)
        if not user or not user.check_password(password):
            logger.warning(f"Failed authentication attempt for user: {username}")
            raise AuthenticationException("Invalid username or password")
        
        logger.info(f"User {username} authenticated successfully")
        return user

    def get_user_role(self, username: str) -> str:
        """
        Get the role of a user.

        Args:
            username: The username of the user.

        Returns:
            The role of the user.

        Raises:
            AuthenticationException: If the user does not exist.
        """
        user = self.user_repository.get_user_by_username(username)
        if not user:
            raise AuthenticationException("User does not exist")
        return user.role