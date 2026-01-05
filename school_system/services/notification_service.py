"""
Notification service for managing notifications and alerts.
"""

from typing import List, Dict
from school_system.config.logging import logger
from school_system.config.settings import Settings
from school_system.core.exceptions import DatabaseException
from school_system.core.utils import validate_input
from school_system.models.notification import Notification
from school_system.database.repositories.notification_repository import NotificationRepository


class NotificationService:
    """Service for managing notifications and alerts."""

    def __init__(self):
        self.notification_repository = NotificationRepository()

    def create_notification(self, title: str, message: str, recipient: str) -> Notification:
        """
        Create a new notification.

        Args:
            title: The title of the notification.
            message: The message content of the notification.
            recipient: The recipient of the notification.

        Returns:
            The created Notification object.
        """
        logger.info(f"Creating a new notification for recipient: {recipient}")
        validate_input(title, "Notification title cannot be empty")
        validate_input(message, "Notification message cannot be empty")
        validate_input(recipient, "Notification recipient cannot be empty")
        
        notification = Notification(title=title, message=message, recipient=recipient)
        created_notification = self.notification_repository.create(notification)
        logger.info(f"Notification created successfully with ID: {created_notification.id}")
        return created_notification

    def get_notifications_for_user(self, user_id: int) -> List[Notification]:
        """
        Retrieve notifications for a specific user.

        Args:
            user_id: The ID of the user.

        Returns:
            A list of Notification objects for the user.
        """
        return self.notification_repository.get_notifications_for_user(user_id)

    def mark_as_read(self, notification_id: int) -> bool:
        """
        Mark a notification as read.

        Args:
            notification_id: The ID of the notification.

        Returns:
            True if the notification was marked as read, otherwise False.
        """
        notification = self.notification_repository.get_by_id(notification_id)
        if not notification:
            return False

        notification.is_read = True
        self.notification_repository.update(notification)
        return True

    def delete_notification(self, notification_id: int) -> bool:
        """
        Delete a notification.

        Args:
            notification_id: The ID of the notification.

        Returns:
            True if the notification was deleted, otherwise False.
        """
        notification = self.notification_repository.get_by_id(notification_id)
        if not notification:
            return False

        self.notification_repository.delete(notification)
        return True