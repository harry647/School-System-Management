"""
Unit tests for TeacherService CRUD operations.

This module tests the teacher service layer to ensure
CRUD operations work correctly.
"""

import unittest
from unittest.mock import Mock, patch
from school_system.services.teacher_service import TeacherService
from school_system.models.teacher import Teacher


class TestTeacherService(unittest.TestCase):
    """Unit tests for TeacherService CRUD operations."""

    def setUp(self):
        """Set up test fixtures."""
        self.teacher_service = TeacherService()
        self.mock_repository = Mock()
        self.teacher_service.teacher_repository = self.mock_repository

    def test_create_teacher(self):
        """Test creating a new teacher."""
        # Mock data
        teacher_data = {
            'teacher_id': 'TC001',
            'teacher_name': 'John Doe',
            'department': 'Mathematics'
        }
        expected_teacher = Teacher(**teacher_data)

        # Mock repository
        self.mock_repository.create.return_value = expected_teacher

        # Call service
        result = self.teacher_service.create_teacher(teacher_data)

        # Verify
        self.assertEqual(result, expected_teacher)
        self.mock_repository.create.assert_called_once()

    def test_get_all_teachers(self):
        """Test retrieving all teachers."""
        # Mock data
        mock_teachers = [
            Teacher(teacher_id='TC001', teacher_name='John Doe', department='Mathematics'),
            Teacher(teacher_id='TC002', teacher_name='Jane Smith', department='Science')
        ]

        # Mock repository
        self.mock_repository.get_all.return_value = mock_teachers

        # Call service
        result = self.teacher_service.get_all_teachers()

        # Verify
        self.assertEqual(result, mock_teachers)
        self.mock_repository.get_all.assert_called_once()

    def test_get_teacher_by_id(self):
        """Test retrieving a teacher by ID."""
        # Mock data
        teacher_id = 'TC001'
        expected_teacher = Teacher(teacher_id=teacher_id, teacher_name='John Doe', department='Mathematics')

        # Mock repository
        self.mock_repository.get_by_id.return_value = expected_teacher

        # Call service
        result = self.teacher_service.get_teacher_by_id(teacher_id)

        # Verify
        self.assertEqual(result, expected_teacher)
        self.mock_repository.get_by_id.assert_called_once_with(teacher_id)

    def test_get_teacher_by_id_not_found(self):
        """Test retrieving a non-existent teacher by ID."""
        # Mock repository to return None
        self.mock_repository.get_by_id.return_value = None

        # Call service
        result = self.teacher_service.get_teacher_by_id('TC999')

        # Verify
        self.assertIsNone(result)
        self.mock_repository.get_by_id.assert_called_once_with('TC999')

    def test_update_teacher(self):
        """Test updating an existing teacher."""
        # Mock existing teacher
        teacher_id = 'TC001'
        existing_teacher = Teacher(teacher_id=teacher_id, teacher_name='John Doe', department='Mathematics')
        updated_teacher = Teacher(teacher_id=teacher_id, teacher_name='John Smith', department='Mathematics')

        # Mock repository
        self.mock_repository.get_by_id.return_value = existing_teacher
        self.mock_repository.update.return_value = updated_teacher

        # Update data
        update_data = {'teacher_name': 'John Smith'}

        # Call service
        result = self.teacher_service.update_teacher(teacher_id, update_data)

        # Verify
        self.assertEqual(result, updated_teacher)
        self.mock_repository.get_by_id.assert_called_once_with(teacher_id)
        self.mock_repository.update.assert_called_once()

    def test_update_teacher_not_found(self):
        """Test updating a non-existent teacher."""
        # Mock repository to return None
        self.mock_repository.get_by_id.return_value = None

        # Call service
        result = self.teacher_service.update_teacher('TC999', {'teacher_name': 'New Name'})

        # Verify
        self.assertIsNone(result)
        self.mock_repository.get_by_id.assert_called_once_with('TC999')
        self.mock_repository.update.assert_not_called()

    def test_delete_teacher(self):
        """Test deleting a teacher."""
        # Mock existing teacher
        teacher_id = 'TC001'
        existing_teacher = Teacher(teacher_id=teacher_id, teacher_name='John Doe', department='Mathematics')

        # Mock repository
        self.mock_repository.get_by_id.return_value = existing_teacher

        # Call service
        result = self.teacher_service.delete_teacher(teacher_id)

        # Verify
        self.assertTrue(result)
        self.mock_repository.get_by_id.assert_called_once_with(teacher_id)
        self.mock_repository.delete.assert_called_once_with(existing_teacher)

    def test_delete_teacher_not_found(self):
        """Test deleting a non-existent teacher."""
        # Mock repository to return None
        self.mock_repository.get_by_id.return_value = None

        # Call service
        result = self.teacher_service.delete_teacher('TC999')

        # Verify
        self.assertFalse(result)
        self.mock_repository.get_by_id.assert_called_once_with('TC999')
        self.mock_repository.delete.assert_not_called()

    def test_track_operation(self):
        """Test tracking operations for undo."""
        # Call service
        self.teacher_service.track_operation('create', {'teacher_id': 'TC001'})

        # Verify operation is tracked
        self.assertEqual(len(self.teacher_service.undo_stack), 1)
        self.assertEqual(self.teacher_service.undo_stack[0]['type'], 'create')
        self.assertEqual(self.teacher_service.undo_stack[0]['data'], {'teacher_id': 'TC001'})

    def test_undo_create_operation(self):
        """Test undoing a create operation."""
        # Setup undo stack
        operation = {
            'type': 'create',
            'data': {'teacher_id': 'TC001'}
        }
        self.teacher_service.undo_stack.append(operation)

        # Mock delete method
        self.teacher_service.delete_teacher = Mock(return_value=True)

        # Call undo
        self.teacher_service.undo_operation(operation)

        # Verify delete was called
        self.teacher_service.delete_teacher.assert_called_once_with('TC001')

    def test_undo_delete_operation(self):
        """Test undoing a delete operation."""
        # Setup undo stack
        operation = {
            'type': 'delete',
            'data': {
                'teacher_id': 'TC001',
                'teacher_name': 'John Doe',
                'department': 'Mathematics'
            }
        }
        self.teacher_service.undo_stack.append(operation)

        # Mock create method
        self.teacher_service.create_teacher = Mock()

        # Call undo
        self.teacher_service.undo_operation(operation)

        # Verify create was called
        self.teacher_service.create_teacher.assert_called_once_with(operation['data'])

    def test_undo_update_operation(self):
        """Test undoing an update operation."""
        # Setup undo stack
        operation = {
            'type': 'update',
            'data': {
                'teacher_id': 'TC001',
                'old_data': {'teacher_name': 'John Doe'},
                'new_data': {'teacher_name': 'John Smith'}
            }
        }
        self.teacher_service.undo_stack.append(operation)

        # Mock update method
        self.teacher_service.update_teacher = Mock()

        # Call undo
        self.teacher_service.undo_operation(operation)

        # Verify update was called with old data
        self.teacher_service.update_teacher.assert_called_once_with('TC001', {'teacher_name': 'John Doe'})

    def test_clear_undo_stack(self):
        """Test clearing the undo stack."""
        # Add operations to stack
        self.teacher_service.undo_stack = [{'type': 'create', 'data': {}}]

        # Clear stack
        self.teacher_service.clear_undo_stack()

        # Verify stack is empty
        self.assertEqual(len(self.teacher_service.undo_stack), 0)

    def test_get_teacher_details(self):
        """Test getting formatted teacher details."""
        # Mock teacher
        teacher = Teacher(teacher_id='TC001', teacher_name='John Doe', department='Mathematics')

        # Call service
        result = self.teacher_service.get_teacher_details(teacher)

        # Verify
        expected = "Teacher Details:\n\nID: TC001\nName: John Doe\nDepartment: Mathematics"
        self.assertEqual(result, expected)

    def test_import_teachers_from_excel(self):
        """Test importing teachers from Excel."""
        # Mock import export service
        mock_import_export = Mock()
        self.teacher_service.import_export_service = mock_import_export

        # Mock data
        excel_data = [
            {'teacher_id': 'TC001', 'teacher_name': 'John Doe', 'department': 'Mathematics'},
            {'teacher_id': 'TC002', 'teacher_name': 'Jane Smith', 'department': 'Science'}
        ]
        mock_import_export.import_from_excel.return_value = excel_data

        # Mock created teachers
        created_teachers = [
            Teacher(**data) for data in excel_data
        ]
        self.mock_repository.create.side_effect = created_teachers

        # Call service
        result = self.teacher_service.import_teachers_from_excel('test.xlsx')

        # Verify
        self.assertEqual(len(result), 2)
        self.assertEqual(result[0].teacher_id, 'TC001')
        self.assertEqual(result[1].teacher_id, 'TC002')
        mock_import_export.import_from_excel.assert_called_once_with('test.xlsx')
        self.assertEqual(self.mock_repository.create.call_count, 2)

    def test_export_teachers_to_excel(self):
        """Test exporting teachers to Excel."""
        # Mock import export service
        mock_import_export = Mock()
        self.teacher_service.import_export_service = mock_import_export

        # Mock teachers
        mock_teachers = [
            Teacher(teacher_id='TC001', teacher_name='John Doe', department='Mathematics'),
            Teacher(teacher_id='TC002', teacher_name='Jane Smith', department='Science')
        ]
        self.mock_repository.get_all.return_value = mock_teachers
        expected_data = [teacher.__dict__ for teacher in mock_teachers]
        mock_import_export.export_to_excel.return_value = True

        # Call service
        result = self.teacher_service.export_teachers_to_excel('export.xlsx')

        # Verify
        self.assertTrue(result)
        self.mock_repository.get_all.assert_called_once()
        mock_import_export.export_to_excel.assert_called_once_with(expected_data, 'export.xlsx')

    def test_create_teacher_validation_error(self):
        """Test create teacher with validation error."""
        # Test with empty name
        with self.assertRaises(ValueError):
            self.teacher_service.create_teacher({
                'teacher_id': 'TC001',
                'teacher_name': '',
                'department': 'Mathematics'
            })

        # Test with empty ID
        with self.assertRaises(ValueError):
            self.teacher_service.create_teacher({
                'teacher_id': '',
                'teacher_name': 'John Doe',
                'department': 'Mathematics'
            })


if __name__ == '__main__':
    unittest.main()