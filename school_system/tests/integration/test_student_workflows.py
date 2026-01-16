"""
Integration tests for student workflows.

This module tests the complete student management workflows to ensure
end-to-end functionality and integration between components.
"""

import unittest
from unittest.mock import Mock, patch
from PyQt6.QtWidgets import QApplication

from school_system.gui.windows.student_workflow_components import (
    StudentCreationWorkflow, StudentUpdateWorkflow, 
    StudentDeletionWorkflow, StudentWorkflowManager
)
from school_system.gui.base.base_window import BaseWindow


class TestStudentWorkflows(unittest.TestCase):
    """Integration tests for student workflows."""
    
    def setUp(self):
        """Set up test fixtures."""
        # Create a mock QApplication for testing
        self.app = QApplication([])
        
        # Create a mock parent window
        self.parent_window = Mock(spec=BaseWindow)
        self.parent_window.add_widget_to_content = Mock()
        
        # Mock student service
        self.mock_student_service = Mock()
        
        # Create workflow instances
        self.creation_workflow = StudentCreationWorkflow(self.parent_window)
        self.update_workflow = StudentUpdateWorkflow(self.parent_window)
        self.deletion_workflow = StudentDeletionWorkflow(self.parent_window)
    
    def tearDown(self):
        """Clean up after tests."""
        del self.app
    
    def test_creation_workflow_structure(self):
        """Test that creation workflow has required components."""
        # Check that workflow has expected attributes
        self.assertIsNotNone(self.creation_workflow)
        self.assertEqual(self.creation_workflow.operation_type, "Create Student")
        
        # Check that form fields exist
        self.assertTrue(hasattr(self.creation_workflow, 'student_id_input'))
        self.assertTrue(hasattr(self.creation_workflow, 'name_input'))
        self.assertTrue(hasattr(self.creation_workflow, 'stream_input'))
        self.assertTrue(hasattr(self.creation_workflow, 'date_of_birth_input'))
    
    def test_update_workflow_structure(self):
        """Test that update workflow has required components."""
        # Check that workflow has expected attributes
        self.assertIsNotNone(self.update_workflow)
        self.assertEqual(self.update_workflow.operation_type, "Update Student")
        
        # Check that form fields exist
        self.assertTrue(hasattr(self.update_workflow, 'student_id_input'))
        self.assertTrue(hasattr(self.update_workflow, 'new_name_input'))
        self.assertTrue(hasattr(self.update_workflow, 'new_stream_input'))
    
    def test_deletion_workflow_structure(self):
        """Test that deletion workflow has required components."""
        # Check that workflow has expected attributes
        self.assertIsNotNone(self.deletion_workflow)
        self.assertEqual(self.deletion_workflow.operation_type, "Delete Student")
        
        # Check that form fields exist
        self.assertTrue(hasattr(self.deletion_workflow, 'student_id_input'))
        self.assertTrue(hasattr(self.deletion_workflow, 'reason_for_deletion_input'))
    
    @patch('school_system.gui.windows.student_workflow_components.StudentOperationPreviewDialog')
    def test_creation_workflow_confirmation(self, mock_preview):
        """Test creation workflow confirmation dialog."""
        # Mock the preview dialog to return accepted
        mock_preview_instance = Mock()
        mock_preview_instance.exec.return_value = True
        mock_preview.return_value = mock_preview_instance
        
        # Mock the student service
        self.creation_workflow.student_service = self.mock_student_service
        self.mock_student_service.create_student.return_value = Mock(student_id="TEST123")
        
        # Set form values
        if hasattr(self.creation_workflow, 'student_id_input'):
            self.creation_workflow.student_id_input.setText("TEST123")
        if hasattr(self.creation_workflow, 'name_input'):
            self.creation_workflow.name_input.setText("Test Student")
        if hasattr(self.creation_workflow, 'stream_input'):
            self.creation_workflow.stream_input.setText("Science")
        if hasattr(self.creation_workflow, 'date_of_birth_input'):
            self.creation_workflow.date_of_birth_input.setText("2010-01-01")
        
        # Mock validation to always return valid
        self.creation_workflow.validator.validate_student_id = Mock(return_value=Mock(is_valid=True))
        self.creation_workflow.validator.validate_student_name = Mock(return_value=Mock(is_valid=True))
        self.creation_workflow.validator.validate_stream = Mock(return_value=Mock(is_valid=True))
        self.creation_workflow.validator.validate_age = Mock(return_value=Mock(is_valid=True))
        
        # Trigger the creation process
        self.creation_workflow._on_create_student()
        
        # Verify that student service was called
        self.mock_student_service.create_student.assert_called_once()
        
        # Verify that success feedback was shown
        self.assertTrue(self.creation_workflow.show_success_feedback.called)
    
    def test_workflow_manager(self):
        """Test workflow manager functionality."""
        workflow_manager = StudentWorkflowManager(self.parent_window)
        
        # Test starting a workflow
        workflow_manager.start_workflow("create")
        self.assertIsNotNone(workflow_manager.current_workflow)
        self.assertEqual(workflow_manager.current_workflow.operation_type, "Create Student")
        
        # Test ending current workflow
        workflow_manager.end_current_workflow()
        self.assertIsNone(workflow_manager.current_workflow)
    
    def test_workflow_error_handling(self):
        """Test error handling in workflows."""
        # Test creation workflow with invalid data
        if hasattr(self.creation_workflow, 'student_id_input'):
            self.creation_workflow.student_id_input.setText("")  # Empty ID
        
        # Trigger creation - should show error
        self.creation_workflow._on_create_student()
        
        # Verify that error feedback was shown
        self.assertTrue(self.creation_workflow.show_error_feedback.called)


if __name__ == '__main__':
    unittest.main()
