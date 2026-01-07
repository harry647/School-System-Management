"""
Authentication service for handling user authentication and authorization.

This service serves as the single source of truth for all authentication
operations in the School System Management application.
"""

from typing import Optional, Tuple
from school_system.config.logging import logger
from school_system.config.settings import Settings
from school_system.core.exceptions import AuthenticationError, ValidationError
from school_system.core.utils import ValidationUtils, HashUtils
from school_system.models.user import User, UserSetting, ShortFormMapping
from school_system.database.repositories.user_repo import UserRepository
from school_system.database.repositories.user_repo import UserSettingRepository
from school_system.database.repositories.user_repo import ShortFormMappingRepository
from school_system.models.session import UserSession
from school_system.database.repositories.session_repo import UserSessionRepository
from school_system.models.audit_log import AuditLog
from school_system.database.repositories.audit_log_repo import AuditLogRepository
from school_system.models.user_activity import UserActivity
from school_system.database.repositories.user_activity_repo import UserActivityRepository


class AuthService:
    """Service for handling authentication and authorization."""
    
    def __init__(self):
        """Initialize the authentication service with required repositories."""
        self.user_repository = UserRepository()
        self.user_setting_repository = UserSettingRepository()
        self.short_form_mapping_repository = ShortFormMappingRepository()
        self.user_session_repository = UserSessionRepository()
        self.audit_log_repository = AuditLogRepository()
        self.user_activity_repository = UserActivityRepository()
    
    def authenticate_user(self, username: str, password: str) -> User:
        """
        Authenticate a user with the provided credentials.
        
        This method validates input and performs authentication against
        the user repository. It serves as the single entry point for
        user authentication in the application.
        
        Args:
            username: The username of the user.
            password: The password of the user.
            
        Returns:
            The authenticated User object.
            
        Raises:
            ValidationError: If username or password is empty.
            AuthenticationError: If authentication fails due to invalid credentials.
        """
        logger.info(f"Attempting to authenticate user: {username}")
        
        # Validate input
        if not username or not username.strip():
            logger.warning("Authentication failed: Empty username provided")
            raise ValidationError("Username cannot be empty")
        
        if not password:
            logger.warning(f"Authentication failed: Empty password for user: {username}")
            raise ValidationError("Password cannot be empty")
        
        # Normalize username
        username = username.strip()
        
        # Attempt to retrieve user
        user = self.user_repository.get_user_by_username(username)
        
        if not user:
            logger.warning(f"Authentication failed: User not found: {username}")
            raise AuthenticationError("Invalid username or password")
        
        # Verify password
        if not user.check_password(password):
            logger.warning(f"Authentication failed: Invalid password for user: {username}")
            raise AuthenticationError("Invalid username or password")
        
        logger.info(f"User {username} authenticated successfully")
        return user
    
    def create_user(self, username: str, password: str, role: str = "student") -> User:
        """
        Create a new user account.
        
        This method validates input, checks for existing users, and creates
        a new user with hashed password.
        
        Args:
            username: The username for the new account.
            password: The password for the new account.
            role: The role to assign (default: "student").
            
        Returns:
            The created User object.
            
        Raises:
            ValidationError: If username or password is empty.
            AuthenticationError: If username already exists.
        """
        logger.info(f"Creating new user account: {username}")
        
        # Validate input
        if not username or not username.strip():
            logger.warning("User creation failed: Empty username provided")
            raise ValidationError("Username cannot be empty")
        
        if not password:
            logger.warning(f"User creation failed: Empty password for user: {username}")
            raise ValidationError("Password cannot be empty")
        
        # Normalize username
        username = username.strip()
        
        # Check if user already exists
        existing_user = self.user_repository.get_user_by_username(username)
        if existing_user:
            logger.warning(f"User creation failed: Username already exists: {username}")
            raise AuthenticationError("Username already exists")
        
        # Hash the password
        hashed_password = HashUtils.hash_password(password)
        
        # Create the user
        user = User(username=username, password=hashed_password, role=role)
        user.save()
        
        # Log the user creation
        self.audit_log_repository.create(
            AuditLog(
                user_id=username,
                action="user_create",
                details=f"New user account created with role: {role}"
            )
        )
        
        logger.info(f"User account created successfully: {username}")
        return user
    
    def get_user_role(self, username: str) -> str:
        """
        Get the role of a user.
        
        Args:
            username: The username of the user.
            
        Returns:
            The role of the user.
            
        Raises:
            ValidationError: If username is empty.
            AuthenticationError: If the user does not exist.
        """
        ValidationUtils.validate_input(username, "Username cannot be empty")
        
        user = self.user_repository.get_user_by_username(username)
        if not user:
            raise AuthenticationError("User does not exist")
        return user.role
    
    def get_user_by_username(self, username: str) -> Optional[User]:
        """
        Get a user by username.
        
        Args:
            username: The username of the user.
            
        Returns:
            The User object if found, otherwise None.
        """
        ValidationUtils.validate_input(username, "Username cannot be empty")
        return self.user_repository.get_user_by_username(username)
    
    def get_user_setting(self, user_id: int) -> Optional[UserSetting]:
        """
        Get the user setting for a specific user.
        
        Args:
            user_id: The ID of the user.
            
        Returns:
            The UserSetting object if found, otherwise None.
        """
        logger.info(f"Retrieving user setting for user ID: {user_id}")
        return self.user_setting_repository.get_by_id(user_id)
    
    def create_user_setting(self, user_id: int, reminder_frequency: str = "daily", sound_enabled: bool = True) -> UserSetting:
        """
        Create a new user setting.
        
        Args:
            user_id: The ID of the user.
            reminder_frequency: The frequency of reminders.
            sound_enabled: Whether sound is enabled.
            
        Returns:
            The created UserSetting object.
        """
        logger.info(f"Creating user setting for user ID: {user_id}")
        ValidationUtils.validate_input(user_id, "User ID cannot be empty")
        
        user_setting = UserSetting(user_id=user_id, reminder_frequency=reminder_frequency, sound_enabled=sound_enabled)
        created_setting = self.user_setting_repository.create(user_setting)
        logger.info(f"User setting created successfully for user ID: {user_id}")
        return created_setting
    
    def update_user_setting(self, user_id: int, reminder_frequency: str = None, sound_enabled: bool = None) -> Optional[UserSetting]:
        """
        Update an existing user setting.
        
        Args:
            user_id: The ID of the user.
            reminder_frequency: The frequency of reminders.
            sound_enabled: Whether sound is enabled.
            
        Returns:
            The updated UserSetting object if successful, otherwise None.
        """
        logger.info(f"Updating user setting for user ID: {user_id}")
        user_setting = self.user_setting_repository.get_by_id(user_id)
        if not user_setting:
            return None
        
        if reminder_frequency:
            user_setting.reminder_frequency = reminder_frequency
        if sound_enabled is not None:
            user_setting.sound_enabled = sound_enabled
        
        updated_setting = self.user_setting_repository.update(user_setting)
        logger.info(f"User setting updated successfully for user ID: {user_id}")
        return updated_setting
    
    def get_short_form_mapping(self, short_form: str) -> Optional[ShortFormMapping]:
        """
        Get a short form mapping by its short form.
        
        Args:
            short_form: The short form to look up.
            
        Returns:
            The ShortFormMapping object if found, otherwise None.
        """
        logger.info(f"Retrieving short form mapping for: {short_form}")
        return self.short_form_mapping_repository.get_by_id(short_form)
    
    def create_short_form_mapping(self, short_form: str, full_name: str, mapping_type: str) -> ShortFormMapping:
        """
        Create a new short form mapping.
        
        Args:
            short_form: The short form.
            full_name: The full name.
            mapping_type: The type of mapping.
            
        Returns:
            The created ShortFormMapping object.
        """
        logger.info(f"Creating short form mapping for: {short_form}")
        ValidationUtils.validate_input(short_form, "Short form cannot be empty")
        ValidationUtils.validate_input(full_name, "Full name cannot be empty")
        ValidationUtils.validate_input(mapping_type, "Mapping type cannot be empty")
        
        short_form_mapping = ShortFormMapping(short_form=short_form, full_name=full_name, type=mapping_type)
        created_mapping = self.short_form_mapping_repository.create(short_form_mapping)
        logger.info(f"Short form mapping created successfully for: {short_form}")
        return created_mapping
    
    def update_short_form_mapping(self, short_form: str, full_name: str = None, mapping_type: str = None) -> Optional[ShortFormMapping]:
        """
        Update an existing short form mapping.
        
        Args:
            short_form: The short form to update.
            full_name: The new full name.
            mapping_type: The new mapping type.
            
        Returns:
            The updated ShortFormMapping object if successful, otherwise None.
        """
        logger.info(f"Updating short form mapping for: {short_form}")
        short_form_mapping = self.short_form_mapping_repository.get_by_id(short_form)
        if not short_form_mapping:
            return None
        
        if full_name:
            short_form_mapping.full_name = full_name
        if mapping_type:
            short_form_mapping.type = mapping_type
        
        updated_mapping = self.short_form_mapping_repository.update(short_form_mapping)
        logger.info(f"Short form mapping updated successfully for: {short_form}")
        return updated_mapping
    
    def request_password_reset(self, username: str) -> bool:
        """
        Request a password reset for a user.
        
        This method validates the username and initiates a password reset
        process by generating a reset token and logging the request.
        
        Args:
            username: The username of the user.
            
        Returns:
            True if the password reset request was successful, otherwise False.
            
        Raises:
            ValidationError: If username is empty.
        """
        logger.info(f"Requesting password reset for user: {username}")
        ValidationUtils.validate_input(username, "Username cannot be empty")
        
        user = self.user_repository.get_user_by_username(username)
        if not user:
            logger.warning(f"Password reset requested for non-existent user: {username}")
            return False
        
        # Generate and send a password reset token
        reset_token = self._generate_reset_token(username)
        logger.info(f"Password reset token generated for user: {username}")
        
        # Log the password reset request in the audit log
        self.audit_log_repository.create(
            AuditLog(
                user_id=user.username,
                action="password_reset_request",
                details=f"Password reset requested for user: {username}"
            )
        )
        
        return True
    
    def _generate_reset_token(self, username: str) -> str:
        """
        Generate a password reset token.
        
        Args:
            username: The username of the user.
            
        Returns:
            The generated reset token.
        """
        # Placeholder for token generation logic
        return f"RESET_TOKEN_{username}"
    
    def delete_user(self, username: str) -> bool:
        """
        Delete a user from the system.
        
        Args:
            username: The username of the user to delete.
            
        Returns:
            True if the user was deleted successfully, otherwise False.
        """
        logger.info(f"Deleting user: {username}")
        ValidationUtils.validate_input(username, "Username cannot be empty")
        
        user = self.user_repository.get_user_by_username(username)
        if not user:
            logger.warning(f"User not found for deletion: {username}")
            return False
        
        # Delete the user
        success = self.user_repository.delete(user)
        
        if success:
            # Log the user deletion in the audit log
            self.audit_log_repository.create(
                AuditLog(
                    user_id=username,
                    action="user_delete",
                    details=f"User account deleted: {username}"
                )
            )
            
            logger.info(f"User deleted successfully: {username}")
        else:
            logger.error(f"Failed to delete user: {username}")
        
        return success

    def update_user_role(self, username: str, new_role: str) -> bool:
        """
        Update the role of a user.
        
        Args:
            username: The username of the user.
            new_role: The new role to assign.
            
        Returns:
            True if the role was updated successfully, otherwise False.
        """
        logger.info(f"Updating role for user: {username} to {new_role}")
        ValidationUtils.validate_input(username, "Username cannot be empty")
        ValidationUtils.validate_input(new_role, "New role cannot be empty")
        
        user = self.user_repository.get_user_by_username(username)
        if not user:
            logger.warning(f"User not found for role update: {username}")
            return False
        
        user.role = new_role
        self.user_repository.update(user)
        
        # Log the role update in the audit log
        self.audit_log_repository.create(
            AuditLog(
                user_id=user.username,
                action="role_update",
                details=f"Role updated from {user.role} to {new_role} for user: {username}"
            )
        )
        
        logger.info(f"Role updated successfully for user: {username}")
        return True
    
    def create_user_session(self, username: str, ip_address: str) -> UserSession:
        """
        Create a new user session.
        
        Args:
            username: The username of the user.
            ip_address: The IP address of the user.
            
        Returns:
            The created UserSession object.
        """
        logger.info(f"Creating session for user: {username}")
        ValidationUtils.validate_input(username, "Username cannot be empty")
        ValidationUtils.validate_input(ip_address, "IP address cannot be empty")
        
        session = UserSession(username=username, ip_address=ip_address)
        created_session = self.user_session_repository.create(session)
        
        # Log the session creation in the audit log
        self.audit_log_repository.create(
            AuditLog(
                user_id=username,
                action="session_create",
                details=f"Session created for user: {username} from IP: {ip_address}"
            )
        )
        
        logger.info(f"Session created successfully for user: {username}")
        return created_session
    
    def expire_user_session(self, session_id: int) -> bool:
        """
        Expire a user session.
        
        Args:
            session_id: The ID of the session to expire.
            
        Returns:
            True if the session was expired successfully, otherwise False.
        """
        logger.info(f"Expiring session with ID: {session_id}")
        
        session = self.user_session_repository.get_by_id(session_id)
        if not session:
            logger.warning(f"Session not found for expiration: {session_id}")
            return False
        
        session.is_active = False
        self.user_session_repository.update(session)
        
        # Log the session expiration in the audit log
        self.audit_log_repository.create(
            AuditLog(
                user_id=session.username,
                action="session_expire",
                details=f"Session expired for user: {session.username}"
            )
        )
        
        logger.info(f"Session expired successfully with ID: {session_id}")
        return True
    
    def log_user_action(self, username: str, action: str, details: str) -> AuditLog:
        """
        Log a user action for audit purposes.
        
        Args:
            username: The username of the user.
            action: The action performed.
            details: Additional details about the action.
            
        Returns:
            The created AuditLog object.
        """
        logger.info(f"Logging action for user: {username}")
        ValidationUtils.validate_input(username, "Username cannot be empty")
        ValidationUtils.validate_input(action, "Action cannot be empty")
        
        audit_log = AuditLog(user_id=username, action=action, details=details)
        created_log = self.audit_log_repository.create(audit_log)
        
        logger.info(f"Action logged successfully for user: {username}")
        return created_log
    
    def track_user_activity(self, username: str, activity_type: str, details: str) -> UserActivity:
        """
        Track a user activity.
        
        Args:
            username: The username of the user.
            activity_type: The type of activity.
            details: Additional details about the activity.
            
        Returns:
            The created UserActivity object.
        """
        logger.info(f"Tracking activity for user: {username}")
        ValidationUtils.validate_input(username, "Username cannot be empty")
        ValidationUtils.validate_input(activity_type, "Activity type cannot be empty")
        
        user_activity = UserActivity(username=username, activity_type=activity_type, details=details)
        created_activity = self.user_activity_repository.create(user_activity)
        
        logger.info(f"Activity tracked successfully for user: {username}")
        return created_activity
