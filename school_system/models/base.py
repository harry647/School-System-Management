# Base model for all database models
from datetime import datetime
 
class BaseModel:
    __tablename__ = None
    __pk__ = "id"  # Default primary key
    
    def __init__(self):
        self.created_at = datetime.utcnow()
        self.updated_at = datetime.utcnow()
    
    def save(self):
        """Save the model to the database."""
        from school_system.database.connection import get_db_session as db_get_db_session
        db = db_get_db_session()
        # Implement save logic here
        pass
    
    def __repr__(self):
        return f"<{self.__class__.__name__}>"
 
def get_db_session():
    """Get a database session (connection)."""
    from school_system.database.connection import get_db_session as db_get_db_session
    return db_get_db_session()