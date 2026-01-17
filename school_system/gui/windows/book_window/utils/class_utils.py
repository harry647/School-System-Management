"""
Class Name Utilities

Utilities for standardizing and validating class names across the system.
"""

from typing import Optional, List
from school_system.config.logging import logger
from .constants import STANDARD_CLASSES, CLASS_NAME_MAPPINGS


def normalize_class_name(class_name: str) -> str:
    """
    Normalize a class name to standard format using mappings.

    Args:
        class_name: The class name to normalize

    Returns:
        Normalized class name, or original if no mapping found
    """
    if not class_name:
        return ""

    # Clean and normalize the input
    cleaned = class_name.strip().lower()

    # Check for exact matches in mappings
    if cleaned in CLASS_NAME_MAPPINGS:
        return CLASS_NAME_MAPPINGS[cleaned]

    # Try partial matching for common variations
    for key, value in CLASS_NAME_MAPPINGS.items():
        if key in cleaned or cleaned in key:
            return value

    # If no mapping found, check if it's already in standard format
    if class_name in STANDARD_CLASSES:
        return class_name

    # Log warning for unmapped class names
    logger.warning(f"Unmapped class name: '{class_name}' - using as-is")

    return class_name


def validate_class_name(class_name: str) -> tuple[bool, str]:
    """
    Validate that a class name is in the standard format.

    Args:
        class_name: The class name to validate

    Returns:
        tuple: (is_valid, normalized_name_or_error_message)
    """
    if not class_name or not class_name.strip():
        return False, "Class name cannot be empty"

    normalized = normalize_class_name(class_name)

    if normalized in STANDARD_CLASSES:
        return True, normalized
    else:
        return False, f"Invalid class name '{class_name}'. Must be one of: {', '.join(STANDARD_CLASSES)}"


def get_available_classes() -> List[str]:
    """
    Get list of all available standard classes.

    Returns:
        List of standard class names
    """
    return STANDARD_CLASSES.copy()


def extract_class_level(class_name: str) -> Optional[int]:
    """
    Extract the numeric level from a class name.

    Args:
        class_name: The class name (e.g., "Form 4", "Grade 10")

    Returns:
        The numeric level, or None if extraction fails
    """
    if not class_name:
        return None

    normalized = normalize_class_name(class_name)

    # Extract number from normalized name
    import re
    match = re.search(r'\d+', normalized)
    if match:
        return int(match.group())

    return None


def is_form_class(class_name: str) -> bool:
    """
    Check if a class name represents a Form class (1-4).

    Args:
        class_name: The class name to check

    Returns:
        True if it's a Form class
    """
    level = extract_class_level(class_name)
    return level is not None and 1 <= level <= 4


def is_grade_class(class_name: str) -> bool:
    """
    Check if a class name represents a Grade class (10-12).

    Args:
        class_name: The class name to check

    Returns:
        True if it's a Grade class
    """
    level = extract_class_level(class_name)
    return level is not None and 10 <= level <= 12