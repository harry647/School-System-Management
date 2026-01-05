import sqlite3
from sqlite3 import Error as SQLiteError
from typing import Optional
from ..config.database import DATABASE_CONFIG
from ..config.logging import logger


class DatabaseConnection:
    """Database connection manager using SQLite."""
    
    def __init__(self):
        self._connection = None
        self._config = DATABASE_CONFIG
        
    def get_connection(self) -> Optional[sqlite3.Connection]:
        """Get a database connection, creating one if necessary."""
        if self._connection is None:
            self._connection = self._create_connection()
        return self._connection
    
    def _create_connection(self) -> Optional[sqlite3.Connection]:
        """Create a new database connection."""
        try:
            conn = sqlite3.connect(
                self._config['name'],
                check_same_thread=self._config['sqlite']['check_same_thread'],
                isolation_level=self._config['sqlite']['isolation_level'],
                timeout=self._config['sqlite']['timeout']
            )
            
            # Enable foreign key support
            conn.execute("PRAGMA foreign_keys = ON")
            
            logger.info(f"Database connection established to {self._config['name']}")
            return conn
            
        except SQLiteError as e:
            logger.error(f"Failed to create database connection: {e}")
            return None
    
    def close_connection(self):
        """Close the database connection."""
        if self._connection is not None:
            try:
                self._connection.close()
                logger.info("Database connection closed")
            except SQLiteError as e:
                logger.error(f"Error closing database connection: {e}")
            finally:
                self._connection = None
    
    def __enter__(self):
        """Context manager entry."""
        return self.get_connection()
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.close_connection()


# Global database connection instance
db_connection = DatabaseConnection()


def get_db_session():
    """Get a database session (connection)."""
    return db_connection.get_connection()