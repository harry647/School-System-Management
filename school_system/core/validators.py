import re
from typing import Optional
from datetime import datetime
from .exceptions import ValidationError


class StudentValidator:
    """Validator for student data."""
    
    @staticmethod
    def validate_student_id(student_id: str) -> bool:
        """Validate student ID format."""
        if not student_id or len(student_id.strip()) == 0:
            raise ValidationError("Student ID cannot be empty")
        
        # Basic validation - student ID should be alphanumeric
        if not re.match(r'^[a-zA-Z0-9\-]+$', student_id):
            raise ValidationError("Student ID can only contain letters, numbers, and hyphens")
        
        return True
    
    @staticmethod
    def validate_email(email: str) -> bool:
        """Validate email format."""
        if not email or len(email.strip()) == 0:
            raise ValidationError("Email cannot be empty")
        
        # Basic email validation
        if not re.match(r'^[^@]+@[^@]+\.[^@]+$', email):
            raise ValidationError("Invalid email format")
        
        return True
    
    @staticmethod
    def validate_name(name: str) -> bool:
        """Validate student name."""
        if not name or len(name.strip()) == 0:
            raise ValidationError("Name cannot be empty")
        
        # Name should only contain letters, spaces, and common punctuation
        if not re.match(r'^[a-zA-Z\s\-\.\',]+$', name):
            raise ValidationError("Name contains invalid characters")
        
        return True


class TeacherValidator:
    """Validator for teacher data."""
    
    @staticmethod
    def validate_teacher_id(teacher_id: str) -> bool:
        """Validate teacher ID format."""
        if not teacher_id or len(teacher_id.strip()) == 0:
            raise ValidationError("Teacher ID cannot be empty")
        
        # Basic validation - teacher ID should be alphanumeric
        if not re.match(r'^[a-zA-Z0-9\-]+$', teacher_id):
            raise ValidationError("Teacher ID can only contain letters, numbers, and hyphens")
        
        return True


class BookValidator:
    """Validator for book data."""
    
    @staticmethod
    def validate_book_number(book_number: str) -> bool:
        """Validate book number format."""
        if not book_number or len(book_number.strip()) == 0:
            raise ValidationError("Book number cannot be empty")
        
        # Book number should be alphanumeric
        if not re.match(r'^[a-zA-Z0-9\-\.]+$', book_number):
            raise ValidationError("Book number can only contain letters, numbers, hyphens, and periods")
        
        return True


class UserValidator:
    """Validator for user data."""
    
    @staticmethod
    def validate_username(username: str) -> bool:
        """Validate username format."""
        if not username or len(username.strip()) == 0:
            raise ValidationError("Username cannot be empty")
        
        # Username should be alphanumeric with limited special characters
        if not re.match(r'^[a-zA-Z0-9_]+$', username):
            raise ValidationError("Username can only contain letters, numbers, and underscores")
        
        if len(username) < 3:
            raise ValidationError("Username must be at least 3 characters long")
        
        return True
    
    @staticmethod
    def validate_password(password: str) -> bool:
        """Validate password strength."""
        if not password or len(password) == 0:
            raise ValidationError("Password cannot be empty")
        
        # Password should be at least 8 characters
        if len(password) < 8:
            raise ValidationError("Password must be at least 8 characters long")
        
        # Password should contain at least one uppercase, one lowercase, and one digit
        if not re.search(r'[A-Z]', password):
            raise ValidationError("Password must contain at least one uppercase letter")
        
        if not re.search(r'[a-z]', password):
            raise ValidationError("Password must contain at least one lowercase letter")
        
        if not re.search(r'[0-9]', password):
            raise ValidationError("Password must contain at least one digit")
        
        return True


class DateValidator:
    """Validator for date data."""
    
    @staticmethod
    def validate_date(date_str: str, date_format: str = "%Y-%m-%d") -> bool:
        """Validate date format."""
        if not date_str or len(date_str.strip()) == 0:
            raise ValidationError("Date cannot be empty")
        
        try:
            datetime.strptime(date_str, date_format)
            return True
        except ValueError:
            raise ValidationError(f"Date must be in {date_format} format")
