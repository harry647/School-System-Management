"""
Validation Utilities

This module provides utility functions for validating various types of data
such as emails, phone numbers, IDs, and other common validation tasks.
"""

import re
import datetime
from typing import Optional, Union


class ValidationUtils:
    """A utility class for data validation."""

    @staticmethod
    def validate_email(email: str) -> bool:
        """
        Validate an email address format.

        Args:
            email: Email address to validate

        Returns:
            True if the email is valid, False otherwise
        """
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return re.match(pattern, email) is not None

    @staticmethod
    def validate_phone_number(phone: str) -> bool:
        """
        Validate a phone number format.

        Args:
            phone: Phone number to validate

        Returns:
            True if the phone number is valid, False otherwise
        """
        # Remove any non-digit characters
        digits = re.sub(r'\D', '', phone)
        # Should have between 10-15 digits
        return len(digits) >= 10 and len(digits) <= 15

    @staticmethod
    def validate_id_number(id_number: str) -> bool:
        """
        Validate a Kenyan ID number format.

        Args:
            id_number: ID number to validate

        Returns:
            True if the ID number is valid, False otherwise
        """
        # Kenyan ID format: 8 digits (may start with 0)
        pattern = r'^\d{8}$'
        return re.match(pattern, id_number) is not None

    @staticmethod
    def validate_student_id(student_id: str) -> bool:
        """
        Validate a student ID format.

        Args:
            student_id: Student ID to validate

        Returns:
            True if the student ID is valid, False otherwise
        """
        # Common student ID format: letters followed by numbers OR numeric-only
        pattern = r'^([A-Za-z]{2,4}\d{4,6}|\d{4,8})$'
        return re.match(pattern, student_id) is not None

    @staticmethod
    def validate_teacher_id(teacher_id: str) -> bool:
        """
        Validate a teacher ID format.

        Args:
            teacher_id: Teacher ID to validate

        Returns:
            True if the teacher ID is valid, False otherwise
        """
        # Teacher ID format: 2-4 letters followed by 4-6 digits (e.g., TC1234) OR numeric-only (e.g., 123456)
        pattern = r'^([A-Za-z]{2,4}\d{4,6}|\d{4,8})$'
        return re.match(pattern, teacher_id) is not None

    @staticmethod
    def validate_date(date_str: str, format_str: str = '%Y-%m-%d') -> bool:
        """
        Validate a date string format.

        Args:
            date_str: Date string to validate
            format_str: Expected date format

        Returns:
            True if the date is valid, False otherwise
        """
        try:
            datetime.datetime.strptime(date_str, format_str)
            return True
        except ValueError:
            return False

    @staticmethod
    def validate_username(username: str) -> bool:
        """
        Validate username format.

        Args:
            username: Username to validate

        Returns:
            True if the username is valid, False otherwise
        """
        # Username should be 3-20 characters, alphanumeric with underscores
        pattern = r'^[a-zA-Z0-9_]{3,20}$'
        return re.match(pattern, username) is not None

    @staticmethod
    def validate_password(password: str) -> bool:
        """
        Validate password strength.

        Args:
            password: Password to validate

        Returns:
            True if the password meets strength requirements, False otherwise
        """
        # At least 8 characters, with uppercase, lowercase, digit, and special character
        pattern = r'^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]{8,}$'
        return re.match(pattern, password) is not None

    @staticmethod
    def validate_password_strength(password: str) -> bool:
        """
        Validate basic password strength (without special character requirement).

        Args:
            password: Password to validate

        Returns:
            True if the password meets basic strength requirements, False otherwise
        """
        # At least 8 characters, with uppercase, lowercase, and digit
        pattern = r'^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)[A-Za-z\d@$!%*?&]{8,}$'
        return re.match(pattern, password) is not None

    @staticmethod
    def validate_name(name: str) -> bool:
        """
        Validate a person's name.

        Args:
            name: Name to validate

        Returns:
            True if the name is valid, False otherwise
        """
        # Should contain only letters, spaces, hyphens, and apostrophes
        pattern = r'^[A-Za-z\s\-\'\']{2,50}$'
        return re.match(pattern, name) is not None

    @staticmethod
    def validate_required_fields(data: dict, required_fields: list) -> bool:
        """
        Validate that required fields are present in a dictionary.

        Args:
            data: Dictionary containing the data
            required_fields: List of required field names

        Returns:
            True if all required fields are present and non-empty, False otherwise
        """
        for field in required_fields:
            if field not in data or not data[field]:
                return False
        return True

    @staticmethod
    def validate_length(
        text: str, 
        min_length: Optional[int] = None,
        max_length: Optional[int] = None
    ) -> bool:
        """
        Validate the length of a string.

        Args:
            text: Text to validate
            min_length: Minimum allowed length
            max_length: Maximum allowed length

        Returns:
            True if the text length is within bounds, False otherwise
        """
        length = len(text)
        
        if min_length is not None and length < min_length:
            return False
        if max_length is not None and length > max_length:
            return False
        
        return True

    @staticmethod
    def validate_number_range(
        number: Union[int, float], 
        min_value: Optional[Union[int, float]] = None,
        max_value: Optional[Union[int, float]] = None
    ) -> bool:
        """
        Validate that a number is within a specified range.

        Args:
            number: Number to validate
            min_value: Minimum allowed value
            max_value: Maximum allowed value

        Returns:
            True if the number is within range, False otherwise
        """
        if min_value is not None and number < min_value:
            return False
        if max_value is not None and number > max_value:
            return False
        
        return True

    @staticmethod
    def validate_url(url: str) -> bool:
        """
        Validate a URL format.

        Args:
            url: URL to validate

        Returns:
            True if the URL is valid, False otherwise
        """
        pattern = r'^https?://(?:www\.)?[a-zA-Z0-9-]+(?:\.[a-zA-Z]{2,})+[/?].*$'
        return re.match(pattern, url) is not None

    @staticmethod
    def validate_alphanumeric(text: str) -> bool:
        """
        Validate that a string contains only alphanumeric characters.

        Args:
            text: Text to validate

        Returns:
            True if the text is alphanumeric, False otherwise
        """
        return text.isalnum()

    @staticmethod
    def validate_alphabetic(text: str) -> bool:
        """
        Validate that a string contains only alphabetic characters.

        Args:
            text: Text to validate

        Returns:
            True if the text is alphabetic, False otherwise
        """
        return text.isalpha()

    @staticmethod
    def validate_numeric(text: str) -> bool:
        """
        Validate that a string contains only numeric characters.

        Args:
            text: Text to validate

        Returns:
            True if the text is numeric, False otherwise
        """
        return text.isdigit()

    @staticmethod
    def validate_positive_number(number: Union[int, float]) -> bool:
        """
        Validate that a number is positive.

        Args:
            number: Number to validate

        Returns:
            True if the number is positive, False otherwise
        """
        return number > 0

    @staticmethod
    def validate_furniture_id(furniture_id: str) -> bool:
        """
        Validate a furniture ID format.

        Args:
            furniture_id: Furniture ID to validate

        Returns:
            True if the furniture ID is valid, False otherwise
        """
        # Furniture ID format: letters followed by numbers (e.g., CH1234, LK5678)
        pattern = r'^[A-Za-z]{2,4}\d{4,6}$'
        return re.match(pattern, furniture_id) is not None

    @staticmethod
    def validate_location(location: str) -> bool:
        """
        Validate a location format.

        Args:
            location: Location to validate

        Returns:
            True if the location is valid, False otherwise
        """
        # Location should be alphanumeric with optional spaces and hyphens
        pattern = r'^[A-Za-z0-9\s\-]{2,50}$'
        return re.match(pattern, location) is not None

    @staticmethod
    def validate_form(form: str) -> bool:
        """
        Validate a form format.

        Args:
            form: Form to validate

        Returns:
            True if the form is valid, False otherwise
        """
        # Form should be alphanumeric with optional spaces
        pattern = r'^[A-Za-z0-9\s]{1,20}$'
        return re.match(pattern, form) is not None

    @staticmethod
    def validate_color(color: str) -> bool:
        """
        Validate a color format.

        Args:
            color: Color to validate

        Returns:
            True if the color is valid, False otherwise
        """
        # Color should be alphabetic with optional spaces
        pattern = r'^[A-Za-z\s]{2,20}$'
        return re.match(pattern, color) is not None
