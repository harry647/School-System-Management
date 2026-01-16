"""
Audit log models for tracking user actions.
"""

from .base import BaseModel


class AuditLog(BaseModel):
    """Model for audit logs."""

    __tablename__ = 'audit_logs'
    __pk__ = "log_id"

    def __init__(self, user_id: str, action: str, details: str, **kwargs):
        super().__init__()
        self.user_id = user_id
        self.action = action
        self.details = details
        # Set any additional attributes from kwargs
        for key, value in kwargs.items():
            setattr(self, key, value)

    def __repr__(self):
        return f"<AuditLog(user_id={self.user_id}, action={self.action}, details={self.details})>"
