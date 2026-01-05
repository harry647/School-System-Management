"""
User activity models for tracking user activities.
"""

from .base import BaseModel


class UserActivity(BaseModel):
    """Model for user activities."""

    __tablename__ = 'user_activities'
    __pk__ = "activity_id"

    def __init__(self, username: str, activity_type: str, details: str):
        super().__init__()
        self.username = username
        self.activity_type = activity_type
        self.details = details

    def __repr__(self):
        return f"<UserActivity(username={self.username}, activity_type={self.activity_type}, details={self.details})>"