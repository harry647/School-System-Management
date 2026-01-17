"""
Class Parser Module

This module provides functionality to parse composite class identifiers like "4 Red" 
into their constituent parts: class level (Form 4) and stream (Red).
"""

import re
from typing import Tuple, Optional
from school_system.core.exceptions import ClassParsingException


class ClassParser:
    """
    A utility class for parsing composite class identifiers into class level and stream.
    """
    
    def __init__(self):
        # Define regex pattern for parsing class identifiers
        # Pattern matches: numeric prefix (class level) followed by optional stream name
        # Handles formats like "4 Red", "10 Blue", "11", "Form 4 Red", "Grade 10 Blue"
        self.class_pattern = re.compile(r'^(?:Form\s+|Grade\s+)?(\d+)\s*(.*)$', re.IGNORECASE)
    
    def parse_class_identifier(self, identifier: str) -> Tuple[int, Optional[str]]:
        """
        Parse a composite class identifier into class level and stream.
        
        Args:
            identifier: The composite class identifier (e.g., "4 Red", "10 Blue", "11")
            
        Returns:
            A tuple containing (class_level, stream) where class_level is an integer
            and stream is a string (or None if no stream is specified)
            
        Raises:
            ClassParsingException: If the identifier format is invalid
        """
        if not identifier or not isinstance(identifier, str):
            raise ClassParsingException("Invalid class identifier: must be a non-empty string")
        
        identifier = identifier.strip()
        
        # Match the pattern
        match = self.class_pattern.match(identifier)
        
        if not match:
            raise ClassParsingException(
                f"Invalid class identifier format: '{identifier}'. "
                f"Expected format: 'class_level stream' (e.g., '4 Red', '10 Blue')"
            )
        
        class_level_str, stream = match.groups()
        
        try:
            class_level = int(class_level_str)
        except ValueError:
            raise ClassParsingException(
                f"Invalid class level in identifier: '{identifier}'. "
                f"Class level must be a numeric value."
            )
        
        # Clean up stream name (remove extra whitespace)
        stream = stream.strip() if stream else None
        
        # Validate class level is within reasonable range (1-12)
        if class_level < 1 or class_level > 12:
            raise ClassParsingException(
                f"Invalid class level: {class_level}. Class level must be between 1 and 12."
            )
        
        return class_level, stream
    
    def validate_class_identifier(self, identifier: str) -> bool:
        """
        Validate that a class identifier follows the expected format.
        
        Args:
            identifier: The class identifier to validate
            
        Returns:
            True if the identifier is valid, False otherwise
        """
        try:
            self.parse_class_identifier(identifier)
            return True
        except ClassParsingException:
            return False
    
    def format_class_identifier(self, class_level: int, stream: Optional[str] = None) -> str:
        """
        Format a class identifier from its components.
        
        Args:
            class_level: The class level (e.g., 4 for Form 4)
            stream: Optional stream name (e.g., "Red")
            
        Returns:
            A formatted class identifier string
        """
        if stream:
            return f"{class_level} {stream}"
        return str(class_level)
    
    def extract_class_level(self, identifier: str) -> int:
        """
        Extract just the class level from a composite identifier.
        
        Args:
            identifier: The composite class identifier
            
        Returns:
            The class level as an integer
            
        Raises:
            ClassParsingException: If the identifier format is invalid
        """
        class_level, _ = self.parse_class_identifier(identifier)
        return class_level
    
    def extract_stream(self, identifier: str) -> Optional[str]:
        """
        Extract just the stream from a composite identifier.
        
        Args:
            identifier: The composite class identifier
            
        Returns:
            The stream name as a string, or None if no stream is specified
            
        Raises:
            ClassParsingException: If the identifier format is invalid
        """
        _, stream = self.parse_class_identifier(identifier)
        return stream