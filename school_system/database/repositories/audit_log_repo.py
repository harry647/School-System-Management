"""
Repository for audit log operations.
"""

from .base import BaseRepository
from ...models.audit_log import AuditLog


class AuditLogRepository(BaseRepository):
    """Repository for audit log operations."""

    def __init__(self):
        super().__init__(AuditLog)
