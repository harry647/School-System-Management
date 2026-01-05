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
        self.locker_repository = LockerRepository()
        self.furniture_category_repository = FurnitureCategoryRepository()
        self.locker_assignment_repository = LockerAssignmentRepository()
        self.chair_assignment_repository = ChairAssignmentRepository()

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

    def get_all_lockers(self) -> List[Locker]:
        """
        Retrieve all lockers.
  
        Returns:
            A list of all Locker objects.
        """
        return self.locker_repository.get_all()
  
    def get_locker_by_id(self, locker_id: int) -> Optional[Locker]:
        """
        Retrieve a locker by its ID.
  
        Args:
            locker_id: The ID of the locker.
  
        Returns:
            The Locker object if found, otherwise None.
        """
        return self.locker_repository.get_by_id(locker_id)
  
    def create_locker(self, locker_data: dict) -> Locker:
        """
        Create a new locker.
  
        Args:
            locker_data: A dictionary containing locker data.
  
        Returns:
            The created Locker object.
        """
        logger.info(f"Creating a new locker with data: {locker_data}")
        ValidationUtils.validate_input(locker_data.get('locker_id'), "Locker ID cannot be empty")
        
        locker = Locker(**locker_data)
        created_locker = self.locker_repository.create(locker)
        logger.info(f"Locker created successfully with ID: {created_locker.locker_id}")
        return created_locker
  
    def update_locker(self, locker_id: int, locker_data: dict) -> Optional[Locker]:
        """
        Update an existing locker.
  
        Args:
            locker_id: The ID of the locker to update.
            locker_data: A dictionary containing updated locker data.
  
        Returns:
            The updated Locker object if successful, otherwise None.
        """
        locker = self.locker_repository.get_by_id(locker_id)
        if not locker:
            return None
  
        for key, value in locker_data.items():
            setattr(locker, key, value)
  
        return self.locker_repository.update(locker)
  
    def delete_locker(self, locker_id: int) -> bool:
        """
        Delete a locker.
  
        Args:
            locker_id: The ID of the locker to delete.
  
        Returns:
            True if the locker was deleted, otherwise False.
        """
        locker = self.locker_repository.get_by_id(locker_id)
        if not locker:
            return False
  
        self.locker_repository.delete(locker)
        return True

    def get_all_furniture_categories(self) -> List[FurnitureCategory]:
        """
        Retrieve all furniture categories.
  
        Returns:
            A list of all FurnitureCategory objects.
        """
        return self.furniture_category_repository.get_all()
  
    def get_furniture_category_by_name(self, category_name: str) -> Optional[FurnitureCategory]:
        """
        Retrieve a furniture category by its name.
  
        Args:
            category_name: The name of the furniture category.
  
        Returns:
            The FurnitureCategory object if found, otherwise None.
        """
        return self.furniture_category_repository.get_by_id(category_name)
  
    def create_furniture_category(self, category_data: dict) -> FurnitureCategory:
        """
        Create a new furniture category.
  
        Args:
            category_data: A dictionary containing furniture category data.
  
        Returns:
            The created FurnitureCategory object.
        """
        logger.info(f"Creating a new furniture category with data: {category_data}")
        ValidationUtils.validate_input(category_data.get('category_name'), "Category name cannot be empty")
        
        category = FurnitureCategory(**category_data)
        created_category = self.furniture_category_repository.create(category)
        logger.info(f"Furniture category created successfully with name: {created_category.category_name}")
        return created_category
  
    def update_furniture_category(self, category_name: str, category_data: dict) -> Optional[FurnitureCategory]:
        """
        Update an existing furniture category.
  
        Args:
            category_name: The name of the furniture category to update.
            category_data: A dictionary containing updated furniture category data.
  
        Returns:
            The updated FurnitureCategory object if successful, otherwise None.
        """
        category = self.furniture_category_repository.get_by_id(category_name)
        if not category:
            return None
  
        for key, value in category_data.items():
            setattr(category, key, value)
  
        return self.furniture_category_repository.update(category)
  
    def delete_furniture_category(self, category_name: str) -> bool:
        """
        Delete a furniture category.
  
        Args:
            category_name: The name of the furniture category to delete.
  
        Returns:
            True if the furniture category was deleted, otherwise False.
        """
        category = self.furniture_category_repository.get_by_id(category_name)
        if not category:
            return False
  
        self.furniture_category_repository.delete(category)
        return True

    def get_all_locker_assignments(self) -> List[LockerAssignment]:
        """
        Retrieve all locker assignments.
  
        Returns:
            A list of all LockerAssignment objects.
        """
        return self.locker_assignment_repository.get_all()
  
    def get_locker_assignment_by_student_id(self, student_id: int) -> Optional[LockerAssignment]:
        """
        Retrieve a locker assignment by student ID.
  
        Args:
            student_id: The ID of the student.
  
        Returns:
            The LockerAssignment object if found, otherwise None.
        """
        return self.locker_assignment_repository.get_by_id(student_id)
  
    def create_locker_assignment(self, assignment_data: dict) -> LockerAssignment:
        """
        Create a new locker assignment.
  
        Args:
            assignment_data: A dictionary containing locker assignment data.
  
        Returns:
            The created LockerAssignment object.
        """
        logger.info(f"Creating a new locker assignment with data: {assignment_data}")
        ValidationUtils.validate_input(assignment_data.get('student_id'), "Student ID cannot be empty")
        ValidationUtils.validate_input(assignment_data.get('locker_id'), "Locker ID cannot be empty")
        
        assignment = LockerAssignment(**assignment_data)
        created_assignment = self.locker_assignment_repository.create(assignment)
        logger.info(f"Locker assignment created successfully for student ID: {created_assignment.student_id}")
        return created_assignment
  
    def update_locker_assignment(self, student_id: int, assignment_data: dict) -> Optional[LockerAssignment]:
        """
        Update an existing locker assignment.
  
        Args:
            student_id: The ID of the student whose locker assignment to update.
            assignment_data: A dictionary containing updated locker assignment data.
  
        Returns:
            The updated LockerAssignment object if successful, otherwise None.
        """
        assignment = self.locker_assignment_repository.get_by_id(student_id)
        if not assignment:
            return None
  
        for key, value in assignment_data.items():
            setattr(assignment, key, value)
  
        return self.locker_assignment_repository.update(assignment)
  
    def delete_locker_assignment(self, student_id: int) -> bool:
        """
        Delete a locker assignment.
  
        Args:
            student_id: The ID of the student whose locker assignment to delete.
  
        Returns:
            True if the locker assignment was deleted, otherwise False.
        """
        assignment = self.locker_assignment_repository.get_by_id(student_id)
        if not assignment:
            return False
  
        self.locker_assignment_repository.delete(assignment)
        return True

    def get_all_chair_assignments(self) -> List[ChairAssignment]:
        """
        Retrieve all chair assignments.
  
        Returns:
            A list of all ChairAssignment objects.
        """
        return self.chair_assignment_repository.get_all()
  
    def get_chair_assignment_by_student_id(self, student_id: int) -> Optional[ChairAssignment]:
        """
        Retrieve a chair assignment by student ID.
  
        Args:
            student_id: The ID of the student.
  
        Returns:
            The ChairAssignment object if found, otherwise None.
        """
        return self.chair_assignment_repository.get_by_id(student_id)
  
    def create_chair_assignment(self, assignment_data: dict) -> ChairAssignment:
        """
        Create a new chair assignment.
  
        Args:
            assignment_data: A dictionary containing chair assignment data.
  
        Returns:
            The created ChairAssignment object.
        """
        logger.info(f"Creating a new chair assignment with data: {assignment_data}")
        ValidationUtils.validate_input(assignment_data.get('student_id'), "Student ID cannot be empty")
        ValidationUtils.validate_input(assignment_data.get('chair_id'), "Chair ID cannot be empty")
        
        assignment = ChairAssignment(**assignment_data)
        created_assignment = self.chair_assignment_repository.create(assignment)
        logger.info(f"Chair assignment created successfully for student ID: {created_assignment.student_id}")
        return created_assignment
  
    def update_chair_assignment(self, student_id: int, assignment_data: dict) -> Optional[ChairAssignment]:
        """
        Update an existing chair assignment.
  
        Args:
            student_id: The ID of the student whose chair assignment to update.
            assignment_data: A dictionary containing updated chair assignment data.
  
        Returns:
            The updated ChairAssignment object if successful, otherwise None.
        """
        assignment = self.chair_assignment_repository.get_by_id(student_id)
        if not assignment:
            return None
  
        for key, value in assignment_data.items():
            setattr(assignment, key, value)
  
        return self.chair_assignment_repository.update(assignment)
  
    def delete_chair_assignment(self, student_id: int) -> bool:
        """
        Delete a chair assignment.
  
        Args:
            student_id: The ID of the student whose chair assignment to delete.
  
        Returns:
            True if the chair assignment was deleted, otherwise False.
        """
        assignment = self.chair_assignment_repository.get_by_id(student_id)
        if not assignment:
            return False
  
        self.chair_assignment_repository.delete(assignment)
        return True