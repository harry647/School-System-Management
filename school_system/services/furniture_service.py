"""
Furniture service for managing furniture-related operations.
"""

from typing import List, Optional
from school_system.config.logging import logger
from school_system.config.settings import Settings
from school_system.core.exceptions import DatabaseException
from school_system.core.utils import ValidationUtils
from school_system.models.furniture import Chair, Locker, FurnitureCategory, LockerAssignment, ChairAssignment
from school_system.database.repositories.furniture_repo import ChairRepository, LockerRepository, FurnitureCategoryRepository, LockerAssignmentRepository, ChairAssignmentRepository


class FurnitureService:
    """Service for managing furniture-related operations."""
 
    def __init__(self):
        self.chair_repository = ChairRepository()

    def get_all_chairs(self) -> List[Chair]:
        """
        Retrieve all chairs.
 
        Returns:
            A list of all Chair objects.
        """
        return self.chair_repository.get_all()
 
    def get_chair_by_id(self, chair_id: int) -> Optional[Chair]:
        """
        Retrieve a chair by its ID.
 
        Args:
            chair_id: The ID of the chair.
 
        Returns:
            The Chair object if found, otherwise None.
        """
        return self.chair_repository.get_by_id(chair_id)
 
    def create_chair(self, chair_data: dict) -> Chair:
        """
        Create a new chair.
 
        Args:
            chair_data: A dictionary containing chair data.
 
        Returns:
            The created Chair object.
        """
        logger.info(f"Creating a new chair with data: {chair_data}")
        ValidationUtils.validate_input(chair_data.get('name'), "Chair name cannot be empty")
         
        chair = Chair(**chair_data)
        created_chair = self.chair_repository.create(chair)
        logger.info(f"Chair created successfully with ID: {created_chair.id}")
        return created_chair
 
    def update_chair(self, chair_id: int, chair_data: dict) -> Optional[Chair]:
        """
        Update an existing chair.
 
        Args:
            chair_id: The ID of the chair to update.
            chair_data: A dictionary containing updated chair data.
 
        Returns:
            The updated Chair object if successful, otherwise None.
        """
        chair = self.chair_repository.get_by_id(chair_id)
        if not chair:
            return None
 
        for key, value in chair_data.items():
            setattr(chair, key, value)
 
        return self.chair_repository.update(chair)
 
    def delete_chair(self, chair_id: int) -> bool:
        """
        Delete a chair.
 
        Args:
            chair_id: The ID of the chair to delete.
 
        Returns:
            True if the chair was deleted, otherwise False.
        """
        chair = self.chair_repository.get_by_id(chair_id)
        if not chair:
            return False
 
        self.chair_repository.delete(chair)
        return True