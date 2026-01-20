"""
Furniture service for managing furniture-related operations.
"""

from typing import List, Optional, Union, Dict
import datetime
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
        ValidationUtils.validate_input(chair_data.get('chair_id'), "Chair ID cannot be empty")

        chair = Chair(**chair_data)
        created_chair = self.chair_repository.create(chair)
        logger.info(f"Chair created successfully with ID: {created_chair.chair_id}")
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

    def search_furniture(self, query: str, furniture_type: str = 'all') -> List[Union[Chair, Locker]]:
        """
        Search furniture by various criteria.

        Args:
            query: The search query.
            furniture_type: The type of furniture to search ('all', 'chair', 'locker').

        Returns:
            A list of furniture items matching the criteria.
        """
        logger.info(f"Searching furniture with query: {query}, type: {furniture_type}")
        
        results = []
        
        try:
            if furniture_type in ['all', 'chair']:
                chairs = self.chair_repository.get_all()
                for chair in chairs:
                    if (query.lower() in str(chair.chair_id).lower() or
                        (chair.location and query.lower() in chair.location.lower()) or
                        (chair.form and query.lower() in chair.form.lower())):
                        results.append(chair)
            
            if furniture_type in ['all', 'locker']:
                lockers = self.locker_repository.get_all()
                for locker in lockers:
                    if (query.lower() in str(locker.locker_id).lower() or
                        (locker.location and query.lower() in locker.location.lower()) or
                        (locker.form and query.lower() in locker.form.lower())):
                        results.append(locker)
            
            logger.info(f"Found {len(results)} furniture items matching query: {query}")
            return results
        except Exception as e:
            logger.error(f"Error searching furniture: {e}")
            return []

    def report_maintenance_issue(self, furniture_id: int, furniture_type: str, issue: str) -> bool:
        """
        Report maintenance issue for furniture.

        Args:
            furniture_id: The ID of the furniture item.
            furniture_type: The type of furniture ('chair' or 'locker').
            issue: Description of the maintenance issue.

        Returns:
            True if the issue was reported successfully, otherwise False.
        """
        logger.info(f"Reporting maintenance issue for {furniture_type} {furniture_id}: {issue}")

        try:
            if furniture_type == 'chair':
                furniture_item = self.chair_repository.get_by_id(furniture_id)
            elif furniture_type == 'locker':
                furniture_item = self.locker_repository.get_by_id(furniture_id)
            else:
                return False

            if not furniture_item:
                return False

            # Store maintenance issue
            if not hasattr(furniture_item, 'maintenance_issues'):
                furniture_item.maintenance_issues = []

            furniture_item.maintenance_issues.append({
                'issue': issue,
                'reported_date': datetime.datetime.now().isoformat(),
                'status': 'reported'
            })

            # Update condition if needed
            if furniture_item.cond != 'Needs Repair':
                furniture_item.cond = 'Needs Repair'

            if furniture_type == 'chair':
                self.chair_repository.update(furniture_item)
            else:
                self.locker_repository.update(furniture_item)

            logger.info(f"Maintenance issue reported successfully for {furniture_type} {furniture_id}")
            return True
        except Exception as e:
            logger.error(f"Error reporting maintenance issue: {e}")
            return False

    def record_maintenance_activity(self, furniture_id: str, maintenance_type: str, notes: str) -> bool:
        """
        Record a maintenance activity for furniture by updating its condition.

        Args:
            furniture_id: The furniture ID (e.g., "CH1" or "LK1")
            maintenance_type: The type of maintenance performed.
            notes: Additional notes about the maintenance (stored in logs).

        Returns:
            True if the maintenance was recorded successfully, otherwise False.
        """
        logger.info(f"Recording maintenance activity for {furniture_id}: {maintenance_type} - {notes}")

        try:
            # Determine furniture type and extract ID
            if furniture_id.startswith('CH'):
                furniture_type = 'chair'
                item_id = int(furniture_id[2:])
                furniture_item = self.chair_repository.get_by_id(item_id)
            elif furniture_id.startswith('LK'):
                furniture_type = 'locker'
                item_id = int(furniture_id[2:])
                furniture_item = self.locker_repository.get_by_id(item_id)
            else:
                return False

            if not furniture_item:
                return False

            # Update condition based on maintenance type
            if maintenance_type.lower() in ['repair', 'replacement']:
                furniture_item.cond = 'Good'
            elif maintenance_type.lower() == 'cleaning':
                # Cleaning improves condition slightly
                if furniture_item.cond == 'Poor':
                    furniture_item.cond = 'Fair'
                elif furniture_item.cond == 'Fair':
                    furniture_item.cond = 'Good'
            elif maintenance_type.lower() == 'inspection':
                # Inspection might reveal issues or confirm good condition
                if furniture_item.cond == 'Needs Repair':
                    furniture_item.cond = 'Fair'  # Assumed fixed during inspection
            # Other maintenance types don't change condition

            # Save the updated furniture item
            if furniture_type == 'chair':
                self.chair_repository.update(furniture_item)
            else:
                self.locker_repository.update(furniture_item)

            logger.info(f"Maintenance activity recorded successfully for {furniture_id} - condition updated to {furniture_item.cond}")
            return True
        except Exception as e:
            logger.error(f"Error recording maintenance activity: {e}")
            return False

    def get_maintenance_records(self) -> List[dict]:
        """
        Get maintenance summary for furniture items that have been maintained.

        Returns:
            A list of dictionaries containing maintenance summary information.
        """
        logger.info("Retrieving maintenance summary")

        try:
            records = []

            # Get chairs that have been maintained (condition changed from Needs Repair)
            chairs = self.chair_repository.get_all()
            for chair in chairs:
                if chair.cond == 'Good':  # Assume recently maintained
                    records.append({
                        'furniture_id': f"CH{chair.chair_id}",
                        'type': 'Maintenance Completed',
                        'date': 'Recent',
                        'notes': f'Condition: {chair.cond}'
                    })

            # Get lockers that have been maintained
            lockers = self.locker_repository.get_all()
            for locker in lockers:
                if locker.cond == 'Good':  # Assume recently maintained
                    records.append({
                        'furniture_id': f"LK{locker.locker_id}",
                        'type': 'Maintenance Completed',
                        'date': 'Recent',
                        'notes': f'Condition: {locker.cond}'
                    })

            logger.info(f"Retrieved {len(records)} maintenance summaries")
            return records
        except Exception as e:
            logger.error(f"Error retrieving maintenance records: {e}")
            return []

    def assign_furniture_batch(self, assignments: List[dict], furniture_type: str) -> List[bool]:
        """
        Assign multiple furniture items in batch.

        Args:
            assignments: A list of assignment dictionaries.
            furniture_type: The type of furniture ('chair' or 'locker').

        Returns:
            A list of boolean values indicating success/failure for each assignment.
        """
        logger.info(f"Assigning {len(assignments)} {furniture_type} items in batch")
        
        results = []
        
        try:
            for assignment in assignments:
                try:
                    if furniture_type == 'chair':
                        ValidationUtils.validate_input(assignment.get('student_id'), "Student ID cannot be empty")
                        ValidationUtils.validate_input(assignment.get('chair_id'), "Chair ID cannot be empty")
                        
                        # Check if chair exists and is available
                        chair = self.chair_repository.get_by_id(assignment['chair_id'])
                        if not chair or chair.assigned:
                            results.append(False)
                            continue
                        
                        # Create assignment
                        assignment_obj = ChairAssignment(**assignment)
                        created_assignment = self.chair_assignment_repository.create(assignment_obj)
                        
                        # Update chair status
                        chair.assigned = 1
                        self.chair_repository.update(chair)
                        
                        results.append(True)
                    elif furniture_type == 'locker':
                        ValidationUtils.validate_input(assignment.get('student_id'), "Student ID cannot be empty")
                        ValidationUtils.validate_input(assignment.get('locker_id'), "Locker ID cannot be empty")
                        
                        # Check if locker exists and is available
                        locker = self.locker_repository.get_by_id(assignment['locker_id'])
                        if not locker or locker.assigned:
                            results.append(False)
                            continue
                        
                        # Create assignment
                        assignment_obj = LockerAssignment(**assignment)
                        created_assignment = self.locker_assignment_repository.create(assignment_obj)
                        
                        # Update locker status
                        locker.assigned = 1
                        self.locker_repository.update(locker)
                        
                        results.append(True)
                    else:
                        results.append(False)
                except Exception as e:
                    logger.error(f"Error in batch assignment: {e}")
                    results.append(False)
            
            logger.info(f"Batch assignment completed: {sum(results)}/{len(results)} successful")
            return results
        except Exception as e:
            logger.error(f"Error in batch furniture assignment: {e}")
            return []

    def get_available_furniture(self, furniture_type: str, location: str = None) -> List[Union[Chair, Locker]]:
        """
        Get available furniture by type and location.

        Args:
            furniture_type: The type of furniture ('chair' or 'locker').
            location: Optional location filter.

        Returns:
            A list of available furniture items.
        """
        logger.info(f"Getting available {furniture_type} items" + (f" in {location}" if location else ""))
        
        try:
            available_items = []
            
            if furniture_type == 'chair':
                all_chairs = self.chair_repository.get_all()
                for chair in all_chairs:
                    if chair.assigned == 0 and (not location or (chair.location and chair.location == location)):
                        available_items.append(chair)
            elif furniture_type == 'locker':
                all_lockers = self.locker_repository.get_all()
                for locker in all_lockers:
                    if locker.assigned == 0 and (not location or (locker.location and locker.location == location)):
                        available_items.append(locker)
            
            logger.info(f"Found {len(available_items)} available {furniture_type} items")
            return available_items
        except Exception as e:
            logger.error(f"Error getting available furniture: {e}")
            return []

    def get_furniture_statistics(self) -> dict:
        """
        Get overall furniture statistics.

        Returns:
            A dictionary containing furniture statistics.
        """
        logger.info("Generating furniture statistics")
        
        try:
            chairs = self.chair_repository.get_all()
            lockers = self.locker_repository.get_all()
            categories = self.furniture_category_repository.get_all()
            
            stats = {
                'total_chairs': len(chairs),
                'assigned_chairs': len([c for c in chairs if c.assigned]),
                'available_chairs': len([c for c in chairs if not c.assigned]),
                'chairs_needing_repair': len([c for c in chairs if c.cond == 'Needs Repair']),
                
                'total_lockers': len(lockers),
                'assigned_lockers': len([l for l in lockers if l.assigned]),
                'available_lockers': len([l for l in lockers if not l.assigned]),
                'lockers_needing_repair': len([l for l in lockers if l.cond == 'Needs Repair']),
                
                'total_furniture': len(chairs) + len(lockers),
                'assigned_furniture': len([c for c in chairs if c.assigned]) + len([l for l in lockers if l.assigned]),
                'available_furniture': len([c for c in chairs if not c.assigned]) + len([l for l in lockers if not l.assigned]),
                'furniture_needing_repair': len([c for c in chairs if c.cond == 'Needs Repair']) + len([l for l in lockers if l.cond == 'Needs Repair']),
                
                'categories': {cat.category_name: {'total': cat.total_count, 'needs_repair': cat.needs_repair} for cat in categories}
            }
            
            logger.info(f"Furniture statistics generated: {stats}")
            return stats
        except Exception as e:
            logger.error(f"Error generating furniture statistics: {e}")
            return {}

    def analyze_furniture_condition(self) -> dict:
        """
        Analyze condition of all furniture.

        Returns:
            A dictionary containing furniture condition analysis.
        """
        logger.info("Analyzing furniture condition")
        
        try:
            chairs = self.chair_repository.get_all()
            lockers = self.locker_repository.get_all()
            
            # Analyze chairs
            chair_conditions = {}
            for chair in chairs:
                condition = chair.cond
                chair_conditions[condition] = chair_conditions.get(condition, 0) + 1
            
            # Analyze lockers
            locker_conditions = {}
            for locker in lockers:
                condition = locker.cond
                locker_conditions[condition] = locker_conditions.get(condition, 0) + 1
            
            analysis = {
                'chairs': chair_conditions,
                'lockers': locker_conditions,
                'overall': {
                    'Good': chair_conditions.get('Good', 0) + locker_conditions.get('Good', 0),
                    'Fair': chair_conditions.get('Fair', 0) + locker_conditions.get('Fair', 0),
                    'Needs Repair': chair_conditions.get('Needs Repair', 0) + locker_conditions.get('Needs Repair', 0),
                    'Poor': chair_conditions.get('Poor', 0) + locker_conditions.get('Poor', 0)
                }
            }
            
            logger.info(f"Furniture condition analysis: {analysis}")
            return analysis
        except Exception as e:
            logger.error(f"Error analyzing furniture condition: {e}")
            return {}

    def reassign_furniture(self, student_id: int, new_furniture_id: int, furniture_type: str) -> bool:
        """
        Reassign furniture from one student to another.

        Args:
            student_id: The ID of the student to reassign.
            new_furniture_id: The ID of the new furniture item.
            furniture_type: The type of furniture ('chair' or 'locker').

        Returns:
            True if the reassignment was successful, otherwise False.
        """
        logger.info(f"Reassigning {furniture_type} for student {student_id} to {new_furniture_id}")
        
        try:
            # Get current assignment
            if furniture_type == 'chair':
                current_assignment = self.chair_assignment_repository.get_by_id(student_id)
                new_furniture = self.chair_repository.get_by_id(new_furniture_id)
            elif furniture_type == 'locker':
                current_assignment = self.locker_assignment_repository.get_by_id(student_id)
                new_furniture = self.locker_repository.get_by_id(new_furniture_id)
            else:
                return False
            
            if not current_assignment or not new_furniture:
                return False
            
            # Check if new furniture is available
            if new_furniture.assigned:
                return False
            
            # Get old furniture and mark as available
            if furniture_type == 'chair':
                old_furniture = self.chair_repository.get_by_id(current_assignment.chair_id)
            else:
                old_furniture = self.locker_repository.get_by_id(current_assignment.locker_id)
            
            if old_furniture:
                old_furniture.assigned = 0
                if furniture_type == 'chair':
                    self.chair_repository.update(old_furniture)
                else:
                    self.locker_repository.update(old_furniture)
            
            # Update assignment with new furniture
            if furniture_type == 'chair':
                current_assignment.chair_id = new_furniture_id
                self.chair_assignment_repository.update(current_assignment)
            else:
                current_assignment.locker_id = new_furniture_id
                self.locker_assignment_repository.update(current_assignment)
            
            # Mark new furniture as assigned
            new_furniture.assigned = 1
            if furniture_type == 'chair':
                self.chair_repository.update(new_furniture)
            else:
                self.locker_repository.update(new_furniture)
            
            logger.info(f"Successfully reassigned {furniture_type} for student {student_id}")
            return True
        except Exception as e:
            logger.error(f"Error reassigning furniture: {e}")
            return False

    def generate_inventory_report(self) -> dict:
        """
        Generate comprehensive furniture inventory report.

        Returns:
            A dictionary containing inventory report.
        """
        logger.info("Generating furniture inventory report")
        
        try:
            chairs = self.chair_repository.get_all()
            lockers = self.locker_repository.get_all()
            
            # Group by location
            inventory_by_location = {}
            
            for chair in chairs:
                location = chair.location or 'Unassigned'
                if location not in inventory_by_location:
                    inventory_by_location[location] = {'chairs': [], 'lockers': []}
                inventory_by_location[location]['chairs'].append({
                    'id': chair.chair_id,
                    'form': chair.form,
                    'color': chair.color,
                    'condition': chair.cond,
                    'assigned': bool(chair.assigned)
                })
            
            for locker in lockers:
                location = locker.location or 'Unassigned'
                if location not in inventory_by_location:
                    inventory_by_location[location] = {'chairs': [], 'lockers': []}
                inventory_by_location[location]['lockers'].append({
                    'id': locker.locker_id,
                    'form': locker.form,
                    'color': locker.color,
                    'condition': locker.cond,
                    'assigned': bool(locker.assigned)
                })
            
            report = {
                'generated_at': datetime.datetime.now().isoformat(),
                'total_items': len(chairs) + len(lockers),
                'locations': inventory_by_location,
                'summary': self.get_furniture_statistics()
            }
            
            logger.info(f"Furniture inventory report generated")
            return report
        except Exception as e:
            logger.error(f"Error generating inventory report: {e}")
            return {}

    def update_furniture_location(self, furniture_id: int, furniture_type: str, new_location: str) -> bool:
        """
        Update location of furniture item.

        Args:
            furniture_id: The ID of the furniture item.
            furniture_type: The type of furniture ('chair' or 'locker').
            new_location: The new location.

        Returns:
            True if the location was updated successfully, otherwise False.
        """
        logger.info(f"Updating location for {furniture_type} {furniture_id} to {new_location}")
        
        try:
            if furniture_type == 'chair':
                furniture_item = self.chair_repository.get_by_id(furniture_id)
            elif furniture_type == 'locker':
                furniture_item = self.locker_repository.get_by_id(furniture_id)
            else:
                return False
            
            if not furniture_item:
                return False
            
            furniture_item.location = new_location
            
            if furniture_type == 'chair':
                self.chair_repository.update(furniture_item)
            else:
                self.locker_repository.update(furniture_item)
            
            logger.info(f"Successfully updated location for {furniture_type} {furniture_id}")
            return True
        except Exception as e:
            logger.error(f"Error updating furniture location: {e}")
            return False

    def get_furniture_usage_history(self, furniture_id: int, furniture_type: str) -> List[dict]:
        """
        Get usage history for a furniture item.

        Args:
            furniture_id: The ID of the furniture item.
            furniture_type: The type of furniture ('chair' or 'locker').

        Returns:
            A list of dictionaries containing usage history.
        """
        logger.info(f"Getting usage history for {furniture_type} {furniture_id}")
        
        try:
            usage_history = []
            
            if furniture_type == 'chair':
                assignments = self.chair_assignment_repository.get_all()
                furniture_id_field = 'chair_id'
            elif furniture_type == 'locker':
                assignments = self.locker_assignment_repository.get_all()
                furniture_id_field = 'locker_id'
            else:
                return []
            
            # Filter assignments for this specific furniture item
            item_assignments = [a for a in assignments if getattr(a, furniture_id_field) == furniture_id]
            
            for assignment in item_assignments:
                usage_entry = {
                    'student_id': assignment.student_id,
                    'assigned_date': assignment.assigned_date,
                    'furniture_id': furniture_id,
                    'furniture_type': furniture_type
                }
                usage_history.append(usage_entry)
            
            logger.info(f"Retrieved {len(usage_history)} usage records for {furniture_type} {furniture_id}")
            return usage_history
        except Exception as e:
            logger.error(f"Error getting furniture usage history: {e}")
            return []

    def get_all_furniture(self) -> List[dict]:
        """
        Get all furniture items (chairs and lockers) as unified list.

        Returns:
            A list of dictionaries containing furniture information.
        """
        logger.info("Retrieving all furniture items")

        try:
            furniture_items = []

            # Get all chairs
            chairs = self.chair_repository.get_all()
            for chair in chairs:
                furniture_items.append({
                    'furniture_id': f"CH{chair.chair_id}",
                    'type': 'Chair',
                    'location': chair.location or "",
                    'status': 'Assigned' if chair.assigned else 'Available',
                    'assigned_to': "",  # Would need to join with assignments table
                    'condition': chair.cond or "Good",
                    'form': chair.form or "",
                    'color': chair.color or ""
                })

            # Get all lockers
            lockers = self.locker_repository.get_all()
            for locker in lockers:
                furniture_items.append({
                    'furniture_id': f"LK{locker.locker_id}",
                    'type': 'Locker',
                    'location': locker.location or "",
                    'status': 'Assigned' if locker.assigned else 'Available',
                    'assigned_to': "",  # Would need to join with assignments table
                    'condition': locker.cond or "Good",
                    'form': locker.form or "",
                    'color': locker.color or ""
                })

            logger.info(f"Retrieved {len(furniture_items)} furniture items")
            return furniture_items
        except Exception as e:
            logger.error(f"Error retrieving all furniture: {e}")
            return []

    def assign_furniture_to_user(self, furniture_id: str, user_id: int, furniture_type: str) -> bool:
        """
        Assign furniture to a user.

        Args:
            furniture_id: The furniture ID (e.g., "CH1" or "LK1")
            user_id: The user ID (student ID)
            furniture_type: The type of furniture ('chair' or 'locker')

        Returns:
            True if assignment was successful, otherwise False.
        """
        logger.info(f"Assigning {furniture_type} {furniture_id} to user {user_id}")

        try:
            if furniture_type.lower() == 'chair':
                # Extract chair ID from furniture_id (remove "CH" prefix)
                if not furniture_id.startswith('CH'):
                    return False
                chair_id = int(furniture_id[2:])

                # Check if chair exists and is available
                chair = self.chair_repository.get_by_id(chair_id)
                if not chair or chair.assigned:
                    return False

                # Check if student already has a chair assigned
                existing_assignment = self.chair_assignment_repository.get_by_id(user_id)
                if existing_assignment:
                    return False  # Student already has a chair

                # Create assignment
                assignment_data = {
                    'student_id': user_id,
                    'chair_id': chair_id,
                    'assigned_date': datetime.datetime.now().date()
                }
                assignment = self.chair_assignment_repository.create(ChairAssignment(**assignment_data))

                # Update chair status
                chair.assigned = 1
                self.chair_repository.update(chair)

                logger.info(f"Successfully assigned chair {chair_id} to student {user_id}")
                return True

            elif furniture_type.lower() == 'locker':
                # Extract locker ID from furniture_id (remove "LK" prefix)
                if not furniture_id.startswith('LK'):
                    return False
                locker_id = int(furniture_id[2:])

                # Check if locker exists and is available
                locker = self.locker_repository.get_by_id(locker_id)
                if not locker or locker.assigned:
                    return False

                # Check if student already has a locker assigned
                existing_assignment = self.locker_assignment_repository.get_by_id(user_id)
                if existing_assignment:
                    return False  # Student already has a locker

                # Create assignment
                assignment_data = {
                    'student_id': user_id,
                    'locker_id': locker_id,
                    'assigned_date': datetime.datetime.now().date()
                }
                assignment = self.locker_assignment_repository.create(LockerAssignment(**assignment_data))

                # Update locker status
                locker.assigned = 1
                self.locker_repository.update(locker)

                logger.info(f"Successfully assigned locker {locker_id} to student {user_id}")
                return True

            return False
        except Exception as e:
            logger.error(f"Error assigning furniture: {e}")
            return False

    def get_all_assignments(self) -> List[dict]:
        """
        Get all furniture assignments as unified list.

        Returns:
            A list of dictionaries containing assignment information.
        """
        logger.info("Retrieving all furniture assignments")

        try:
            assignments = []

            # Get chair assignments
            chair_assignments = self.chair_assignment_repository.get_all()
            for assignment in chair_assignments:
                assignments.append({
                    'furniture_id': f"CH{assignment.chair_id}",
                    'user_id': assignment.student_id,
                    'assigned_date': assignment.assigned_date,
                    'status': 'Active',
                    'type': 'Chair'
                })

            # Get locker assignments
            locker_assignments = self.locker_assignment_repository.get_all()
            for assignment in locker_assignments:
                assignments.append({
                    'furniture_id': f"LK{assignment.locker_id}",
                    'user_id': assignment.student_id,
                    'assigned_date': assignment.assigned_date,
                    'status': 'Active',
                    'type': 'Locker'
                })

            logger.info(f"Retrieved {len(assignments)} furniture assignments")
            return assignments
        except Exception as e:
            logger.error(f"Error retrieving assignments: {e}")
            return []
