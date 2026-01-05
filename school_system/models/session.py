"""
Session models for managing user sessions.
"""

from .base import BaseModel


class UserSession(BaseModel):
    """Model for user sessions."""

    __tablename__ = 'user_sessions'
    __pk__ = "session_id"

    def __init__(self, username: str, ip_address: str, is_active: bool = True):
        super().__init__()
        self.username = username
        self.ip_address = ip_address
        self.is_active = is_active

    def __repr__(self):
        return f"<UserSession(username={self.username}, ip_address={self.ip_address}, is_active={self.is_active})>"