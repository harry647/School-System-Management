"""
Database package initialization.

This module provides access to database connection and repository classes.
"""

from .connection import (
    DatabaseConnection,
    create_db_connection,
    close_db_connection,
    initialize_database,
    get_db_session,
    db_connection
)

from .repositories.base import (
    BaseRepository,
    StudentRepository,
    TeacherRepository,
    BookRepository,
    UserRepository
)

__all__ = [
    'DatabaseConnection',
    'create_db_connection', 
    'close_db_connection',
    'initialize_database',
    'get_db_session',
    'db_connection',
    'BaseRepository',
    'StudentRepository',
    'TeacherRepository', 
    'BookRepository',
    'UserRepository'
]
