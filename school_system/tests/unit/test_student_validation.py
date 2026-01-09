"""
Unit tests for student validation logic.

This module tests the validation components to ensure data integrity
and proper error handling in student operations.
"""

import unittest
from school_system.gui.windows.student_validation import StudentValidator, ValidationResult


class TestStudentValidation(unittest.TestCase):
    """Test cases for student validation logic."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.validator = StudentValidator()
    
    def test_validate_student_id_format(self):
       """Test student ID format validation."""
       # Valid student IDs
       valid_ids = ["ST1234", "SCI5678", "ART123456", "AB1234", "123456", "1234", "12345678"]
       for student_id in valid_ids:
           result = self.validator.validate_student_id(student_id)
           self.assertTrue(result.is_valid, f"Valid ID {student_id} failed validation")
       
       # Invalid student IDs
       invalid_ids = ["", "ABC", "ST", "ST1234567", "ST@1234", "123", "123456789"]
       for student_id in invalid_ids:
           result = self.validator.validate_student_id(student_id)
           self.assertFalse(result.is_valid, f"Invalid ID {student_id} passed validation")
    
    def test_validate_student_name(self):
        """Test student name validation."""
        # Valid names
        valid_names = ["John Doe", "Mary Smith", "Jean-Claude Van Damme", "O'Connor"]
        for name in valid_names:
            result = self.validator.validate_student_name(name)
            self.assertTrue(result.is_valid, f"Valid name {name} failed validation")
        
        # Invalid names
        invalid_names = ["", "John123", "Mary@Smith", "Dr. Smith"]
        for name in invalid_names:
            result = self.validator.validate_student_name(name)
            self.assertFalse(result.is_valid, f"Invalid name {name} passed validation")
    
    def test_validate_stream(self):
        """Test stream validation."""
        # Valid streams
        valid_streams = ["Science", "Arts", "Commerce", "Computer Science"]
        for stream in valid_streams:
            result = self.validator.validate_stream(stream)
            self.assertTrue(result.is_valid, f"Valid stream {stream} failed validation")
        
        # Invalid streams
        invalid_streams = ["", "Science123", "Arts@School", "123Commerce"]
        for stream in invalid_streams:
            result = self.validator.validate_stream(stream)
            self.assertFalse(result.is_valid, f"Invalid stream {stream} passed validation")
    
    def test_validate_age(self):
        """Test age validation based on date of birth."""
        # Valid ages (5-18 years old)
        valid_dobs = ["2010-01-01", "2005-06-15", "2015-12-31"]
        for dob in valid_dobs:
            result = self.validator.validate_age(dob)
            self.assertTrue(result.is_valid, f"Valid DOB {dob} failed validation")
        
        # Invalid ages
        invalid_dobs = ["", "2020-01-01", "1990-01-01", "invalid-date", "2010/01/01"]
        for dob in invalid_dobs:
            result = self.validator.validate_age(dob)
            self.assertFalse(result.is_valid, f"Invalid DOB {dob} passed validation")
    
    def test_validation_result_structure(self):
        """Test ValidationResult structure."""
        # Test valid result
        valid_result = ValidationResult(True, "Valid", "test_field")
        self.assertTrue(valid_result.is_valid)
        self.assertEqual(valid_result.message, "Valid")
        self.assertEqual(valid_result.field, "test_field")
        
        # Test invalid result
        invalid_result = ValidationResult(False, "Invalid", "test_field")
        self.assertFalse(invalid_result.is_valid)
        self.assertEqual(invalid_result.message, "Invalid")
        self.assertEqual(invalid_result.field, "test_field")


if __name__ == '__main__':
    unittest.main()