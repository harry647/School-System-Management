"""
Furniture service for managing furniture-related operations.
"""

from typing import List, Optional
from school_system.config.logging import logger
from school_system.config.settings import Settings
from school_system.core.exceptions import DatabaseException
from school_system.core.utils import validate_input
from school_system.models.furniture import Furniture
from school_system.database.repositories.furniture_repository import FurnitureRepository


class FurnitureService:
    """Service for managing furniture-related operations."""

    def __init__(self):
        self.furniture_repository = FurnitureRepository()

    def get_all_furniture(self) -> List[Furniture]:
        """
        Retrieve all furniture items.

        Returns:
            A list of all Furniture objects.
        """
        return self.furniture_repository.get_all()

    def get_furniture_by_id(self, furniture_id: int) -> Optional[Furniture]:
        """
        Retrieve a furniture item by its ID.

        Args:
            furniture_id: The ID of the furniture item.

        Returns:
            The Furniture object if found, otherwise None.
        """
        return self.furniture_repository.get_by_id(furniture_id)

    def create_furniture(self, furniture_data: dict) -> Furniture:
        """
        Create a new furniture item.

        Args:
            furniture_data: A dictionary containing furniture data.

        Returns:
            The created Furniture object.
        """
        logger.info(f"Creating a new furniture item with data: {furniture_data}")
        validate_input(furniture_data.get('name'), "Furniture name cannot be empty")
        
        furniture = Furniture(**furniture_data)
        created_furniture = self.furniture_repository.create(furniture)
        logger.info(f"Furniture item created successfully with ID: {created_furniture.id}")
        return created_furniture

    def update_furniture(self, furniture_id: int, furniture_data: dict) -> Optional[Furniture]:
        """
        Update an existing furniture item.

        Args:
            furniture_id: The ID of the furniture item to update.
            furniture_data: A dictionary containing updated furniture data.

        Returns:
            The updated Furniture object if successful, otherwise None.
        """
        furniture = self.furniture_repository.get_by_id(furniture_id)
        if not furniture:
            return None

        for key, value in furniture_data.items():
            setattr(furniture, key, value)

        return self.furniture_repository.update(furniture)

    def delete_furniture(self, furniture_id: int) -> bool:
        """
        Delete a furniture item.

        Args:
            furniture_id: The ID of the furniture item to delete.

        Returns:
            True if the furniture item was deleted, otherwise False.
        """
        furniture = self.furniture_repository.get_by_id(furniture_id)
        if not furniture:
            return False

        self.furniture_repository.delete(furniture)
        return True