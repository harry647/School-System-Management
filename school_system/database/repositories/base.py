from typing import List, Optional, Type, TypeVar, Generic
from sqlalchemy.orm import Session
from ...database.connection import get_db_session

T = TypeVar('T')


class BaseRepository(Generic[T]):
    """Base repository class implementing CRUD operations."""
    
    def __init__(self, model: Type[T]):
        self.model = model
        self.db: Session = get_db_session()
    
    def get_by_id(self, id: int) -> Optional[T]:
        """Get entity by ID."""
        return self.db.query(self.model).filter(self.model.id == id).first()
    
    def get_all(self) -> List[T]:
        """Get all entities."""
        return self.db.query(self.model).all()
    
    def create(self, **kwargs) -> T:
        """Create a new entity."""
        instance = self.model(**kwargs)
        self.db.add(instance)
        self.db.commit()
        self.db.refresh(instance)
        return instance
    
    def update(self, id: int, **kwargs) -> Optional[T]:
        """Update an existing entity."""
        instance = self.get_by_id(id)
        if instance:
            for key, value in kwargs.items():
                setattr(instance, key, value)
            self.db.commit()
            self.db.refresh(instance)
        return instance
    
    def delete(self, id: int) -> bool:
        """Delete an entity."""
        instance = self.get_by_id(id)
        if instance:
            self.db.delete(instance)
            self.db.commit()
            return True
        return False
    
    def find_by_field(self, field_name: str, value) -> List[T]:
        """Find entities by a specific field."""
        return self.db.query(self.model).filter(getattr(self.model, field_name) == value).all()
    
    def count(self) -> int:
        """Count all entities."""
        return self.db.query(self.model).count()