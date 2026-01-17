"""
Class Management Service

This service provides comprehensive class and stream management functionality,
including parsing, categorization, filtering, and bulk operations.
"""

from typing import List, Dict, Optional, Tuple, Set
from collections import defaultdict
from school_system.config.logging import logger
from school_system.core.class_parser import ClassParser
from school_system.core.exceptions import ClassParsingException
from school_system.models.student import Student
from school_system.services.student_service import StudentService


class ClassManagementService:
    """
    Service for managing class and stream operations.
    Handles parsing, categorization, filtering, and bulk operations.
    """
    
    def __init__(self):
        self.class_parser = ClassParser()
        self.student_service = StudentService()
        self._class_cache: Optional[Dict] = None
        self._cache_valid = False
    
    def parse_student_stream(self, stream_identifier: str) -> Tuple[int, Optional[str]]:
        """
        Parse a student's stream identifier into class level and stream.
        
        Args:
            stream_identifier: The stream identifier from the database (e.g., "4 Red")
            
        Returns:
            A tuple containing (class_level, stream)
            
        Raises:
            ClassParsingException: If the identifier format is invalid
        """
        try:
            return self.class_parser.parse_class_identifier(stream_identifier)
        except ClassParsingException as e:
            logger.warning(f"Failed to parse stream identifier '{stream_identifier}': {e}")
            raise
    
    def categorize_all_students(self) -> Dict[int, Dict[str, List[Student]]]:
        """
        Categorize all students by class level and stream.
        
        Returns:
            A nested dictionary: {class_level: {stream: [students]}}
            Example: {4: {"Red": [student1, student2], "Blue": [student3]}}
        """
        try:
            all_students = self.student_service.get_all_students()
            categorized = defaultdict(lambda: defaultdict(list))
            
            for student in all_students:
                if not student.stream:
                    logger.warning(f"Student {student.student_id} has no stream identifier")
                    continue
                
                try:
                    class_level, stream = self.parse_student_stream(student.stream)
                    categorized[class_level][stream or "Unassigned"].append(student)
                except ClassParsingException:
                    # Store students with invalid formats in a special category
                    categorized[-1]["Invalid Format"].append(student)
                    logger.warning(f"Student {student.student_id} has invalid stream format: {student.stream}")
            
            return dict(categorized)
        except Exception as e:
            logger.error(f"Error categorizing students: {e}")
            return {}
    
    def get_all_class_levels(self) -> List[int]:
        """
        Get all unique class levels from the database.
        
        Returns:
            A sorted list of class levels (e.g., [1, 2, 3, 4, 10, 11, 12])
        """
        categorized = self.categorize_all_students()
        class_levels = [level for level in categorized.keys() if level > 0]
        return sorted(class_levels)
    
    def get_all_streams(self, class_level: Optional[int] = None) -> List[str]:
        """
        Get all unique streams, optionally filtered by class level.
        
        Args:
            class_level: Optional class level filter
            
        Returns:
            A sorted list of unique stream names
        """
        categorized = self.categorize_all_students()
        
        if class_level is not None:
            if class_level in categorized:
                return sorted(categorized[class_level].keys())
            return []
        
        # Get all streams across all class levels
        all_streams = set()
        for class_data in categorized.values():
            all_streams.update(class_data.keys())
        
        return sorted([s for s in all_streams if s != "Invalid Format"])
    
    def get_students_by_class_level(self, class_level: int) -> List[Student]:
        """
        Get all students in a specific class level.
        
        Args:
            class_level: The class level (e.g., 4 for Form 4)
            
        Returns:
            A list of students in that class level
        """
        categorized = self.categorize_all_students()
        students = []
        
        if class_level in categorized:
            for stream_students in categorized[class_level].values():
                students.extend(stream_students)
        
        return students
    
    def get_students_by_stream(self, stream: str, class_level: Optional[int] = None) -> List[Student]:
        """
        Get all students in a specific stream, optionally filtered by class level.
        
        Args:
            stream: The stream name (e.g., "Red")
            class_level: Optional class level filter
            
        Returns:
            A list of students in that stream
        """
        categorized = self.categorize_all_students()
        students = []
        
        if class_level is not None:
            if class_level in categorized and stream in categorized[class_level]:
                students = categorized[class_level][stream]
        else:
            # Search across all class levels
            for class_data in categorized.values():
                if stream in class_data:
                    students.extend(class_data[stream])
        
        return students
    
    def get_students_by_class_and_stream(self, class_level: int, stream: str) -> List[Student]:
        """
        Get all students in a specific class level and stream combination.
        
        Args:
            class_level: The class level (e.g., 4)
            stream: The stream name (e.g., "Red")
            
        Returns:
            A list of students matching both criteria
        """
        categorized = self.categorize_all_students()
        
        if class_level in categorized and stream in categorized[class_level]:
            return categorized[class_level][stream]
        
        return []
    
    def get_class_stream_combinations(self) -> List[Tuple[int, str, int]]:
        """
        Get all class-stream combinations with student counts.
        
        Returns:
            A list of tuples: (class_level, stream, student_count)
        """
        categorized = self.categorize_all_students()
        combinations = []
        
        for class_level, streams in categorized.items():
            if class_level < 0:  # Skip invalid formats
                continue
            for stream, students in streams.items():
                if stream != "Invalid Format":
                    combinations.append((class_level, stream, len(students)))
        
        return sorted(combinations, key=lambda x: (x[0], x[1]))
    
    def format_class_display_name(self, class_level: int, stream: Optional[str] = None) -> str:
        """
        Format a class display name for UI display.
        
        Args:
            class_level: The class level
            stream: Optional stream name
            
        Returns:
            A formatted display name (e.g., "Form 4 Red" or "Grade 10 Blue")
        """
        # Determine if it's a Form (1-4) or Grade (10-12)
        if 1 <= class_level <= 4:
            prefix = "Form"
        elif 10 <= class_level <= 12:
            prefix = "Grade"
        else:
            prefix = "Class"
        
        if stream:
            return f"{prefix} {class_level} {stream}"
        return f"{prefix} {class_level}"
    
    def validate_and_normalize_stream(self, stream_identifier: str) -> Optional[str]:
        """
        Validate and normalize a stream identifier.
        
        Args:
            stream_identifier: The stream identifier to validate
            
        Returns:
            Normalized stream identifier if valid, None otherwise
        """
        try:
            class_level, stream = self.parse_student_stream(stream_identifier)
            return self.class_parser.format_class_identifier(class_level, stream)
        except ClassParsingException:
            return None
    
    def get_class_statistics(self) -> Dict:
        """
        Get comprehensive statistics about classes and streams.
        
        Returns:
            A dictionary with statistics
        """
        categorized = self.categorize_all_students()
        
        total_students = sum(
            len(students)
            for class_data in categorized.values()
            for students in class_data.values()
            if "Invalid Format" not in str(class_data)
        )
        
        class_levels = self.get_all_class_levels()
        all_streams = self.get_all_streams()
        combinations = self.get_class_stream_combinations()
        
        # Count students with invalid formats
        invalid_count = 0
        if -1 in categorized:
            invalid_count = sum(len(students) for students in categorized[-1].values())
        
        return {
            "total_students": total_students,
            "total_class_levels": len(class_levels),
            "total_streams": len(all_streams),
            "total_combinations": len(combinations),
            "invalid_format_count": invalid_count,
            "class_levels": class_levels,
            "streams": all_streams,
            "combinations": combinations
        }
    
    def get_students_for_bulk_operation(
        self,
        class_level: Optional[int] = None,
        stream: Optional[str] = None
    ) -> List[Student]:
        """
        Get students for bulk operations (e.g., bulk book borrowing).
        
        Args:
            class_level: Optional class level filter
            stream: Optional stream filter
            
        Returns:
            A list of students matching the criteria
        """
        if class_level is not None and stream is not None:
            return self.get_students_by_class_and_stream(class_level, stream)
        elif class_level is not None:
            return self.get_students_by_class_level(class_level)
        elif stream is not None:
            return self.get_students_by_stream(stream)
        else:
            return self.student_service.get_all_students()
    
    def invalidate_cache(self):
        """Invalidate the class categorization cache."""
        self._cache_valid = False
        self._class_cache = None
