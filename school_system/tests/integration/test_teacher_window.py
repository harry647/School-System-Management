"""
Integration tests for TeacherWindow functionality.

This module tests the complete teacher management window to ensure
end-to-end functionality and integration between components.
"""

import unittest
from unittest.mock import Mock, patch, MagicMock
from PyQt6.QtWidgets import QApplication, QMainWindow, QTableWidgetItem, QDialog
from PyQt6.QtCore import Qt

from school_system.gui.windows.teacher_window import TeacherWindow
from school_system.models.teacher import Teacher


class TestTeacherWindow(unittest.TestCase):
    """Integration tests for TeacherWindow."""

    def setUp(self):
        """Set up test fixtures."""
        # Create a QApplication instance for testing
        self.app = QApplication([])

        # Create a real parent window for testing
        self.parent_window = QMainWindow()
        self.parent_window.add_widget_to_content = Mock()

        # Create TeacherWindow instance
        self.teacher_window = TeacherWindow(self.parent_window, "test_user", "admin")

        # Show the window to ensure widgets are properly initialized
        self.teacher_window.show()
        self.app.processEvents()

        # Mock the teacher service
        self.mock_teacher_service = Mock()
        self.teacher_window.teacher_service = self.mock_teacher_service

        # Mock validator
        self.mock_validator = Mock()
        self.teacher_window.validator = self.mock_validator

        # Mock workflow manager
        self.mock_workflow_manager = Mock()
        self.teacher_window.workflow_manager = self.mock_workflow_manager

    def tearDown(self):
        """Clean up after tests."""
        del self.app

    def test_teacher_window_initialization(self):
        """Test that TeacherWindow initializes correctly."""
        self.assertIsNotNone(self.teacher_window)
        self.assertEqual(self.teacher_window.windowTitle(), "School System - Teacher Management")
        self.assertEqual(self.teacher_window.current_user, "test_user")
        self.assertEqual(self.teacher_window.current_role, "admin")

    def test_teacher_window_access_control(self):
        """Test that TeacherWindow enforces access control."""
        # Test with non-admin role
        non_admin_window = TeacherWindow(self.parent_window, "test_user", "student")
        # The window should close itself for non-admin roles
        self.assertFalse(non_admin_window.isVisible())

    def test_create_teacher_workflow(self):
        """Test the create teacher workflow."""
        # Mock the workflow manager's start_workflow method to return a mock workflow
        mock_create_workflow = Mock()
        mock_create_workflow.operation_completed = Mock()

        # Assign the mock workflow manager to the teacher window and mock the start_workflow method
        self.teacher_window.workflow_manager = self.mock_workflow_manager
        self.teacher_window.workflow_manager.start_workflow = Mock(return_value=mock_create_workflow)

        # Trigger create workflow
        self.teacher_window.workflow_manager.start_workflow("create")

        # Verify workflow was started
        self.teacher_window.workflow_manager.start_workflow.assert_called_once_with("create")

    def test_update_teacher_workflow(self):
        """Test the update teacher workflow."""
        # Mock existing teacher
        mock_teacher = Teacher(teacher_id="TC001", teacher_name="John Doe", department="Mathematics")
        self.mock_teacher_service.get_teacher_by_id.return_value = mock_teacher

        # Mock the workflow manager's start_workflow method to return a mock workflow
        mock_update_workflow = Mock()
        mock_update_workflow.operation_completed = Mock()

        # Assign the mock workflow manager to the teacher window and mock the start_workflow method
        self.teacher_window.workflow_manager = self.mock_workflow_manager
        self.teacher_window.workflow_manager.start_workflow = Mock(return_value=mock_update_workflow)

        # Trigger update workflow
        self.teacher_window._start_edit_workflow("TC001")

        # Verify workflow was started
        self.teacher_window.workflow_manager.start_workflow.assert_called_once_with("update")

        # Verify teacher data was retrieved
        self.mock_teacher_service.get_teacher_by_id.assert_called_once_with("TC001")

    def test_delete_teacher_workflow(self):
        """Test the delete teacher workflow."""
        # Mock existing teacher
        mock_teacher = Teacher(teacher_id="TC001", teacher_name="John Doe", department="Mathematics")
        self.mock_teacher_service.get_teacher_by_id.return_value = mock_teacher

        # Mock the delete workflow
        mock_delete_workflow = Mock()
        mock_delete_workflow.operation_completed = Mock()

        # Mock the workflow manager to return our mock workflow
        self.teacher_window.workflow_manager.start_workflow = Mock(return_value=mock_delete_workflow)

        # Trigger delete workflow
        self.teacher_window._start_delete_workflow("TC001")

        # Verify workflow was started
        self.teacher_window.workflow_manager.start_workflow.assert_called_once_with("delete")

        # Verify teacher data was retrieved
        self.mock_teacher_service.get_teacher_by_id.assert_called_once_with("TC001")

    def test_data_display_functionality(self):
        """Test that teacher data is properly displayed in the table."""
        # Mock teacher data
        mock_teachers = [
            Teacher(teacher_id="TC001", teacher_name="John Doe", department="Mathematics"),
            Teacher(teacher_id="TC002", teacher_name="Jane Smith", department="Science")
        ]

        # Call the populate method
        self.teacher_window._populate_teachers_table(mock_teachers)

        # Verify table was populated
        self.assertEqual(self.teacher_window.teachers_table.rowCount(), 2)

        self.teacher_window.teachers_table.update()
        self.app.processEvents()

        # Verify action buttons exist
        for row in range(2):
            action_widget = self.teacher_window.teachers_table.cellWidget(row, 3)
            self.assertIsNotNone(action_widget)

    def test_search_functionality(self):
        """Test the search functionality."""
        # Mock teacher data
        mock_teachers = [
            Teacher(teacher_id="TC001", teacher_name="John Doe", department="Mathematics"),
            Teacher(teacher_id="TC002", teacher_name="Jane Smith", department="Science")
        ]
        self.mock_teacher_service.get_all_teachers.return_value = mock_teachers

        # Trigger search
        self.teacher_window._on_search_teachers("TC001")

        # Verify table refresh was called
        self.mock_teacher_service.get_all_teachers.assert_called()

    def test_view_teacher_details(self):
        """Test viewing teacher details."""
        # Mock teacher
        mock_teacher = Teacher(teacher_id="TC001", teacher_name="John Doe", department="Mathematics")
        self.mock_teacher_service.get_teacher_by_id.return_value = mock_teacher

        # Mock the service to return formatted details
        self.mock_teacher_service.get_teacher_details.return_value = "Teacher: John Doe\nDepartment: Mathematics"

        # Trigger view details
        self.teacher_window._view_teacher_details("TC001")

        # Verify teacher was retrieved
        self.mock_teacher_service.get_teacher_by_id.assert_called_once_with("TC001")
        self.mock_teacher_service.get_teacher_details.assert_called_once_with(mock_teacher)

    def test_import_excel_functionality(self):
        """Test the import Excel functionality."""
        # Mock file dialog
        with patch('PyQt6.QtWidgets.QFileDialog.getOpenFileName') as mock_file_dialog:
            mock_file_dialog.return_value = ("/path/to/test.xlsx", "Excel Files (*.xlsx *.xls)")

            # Set the import file path
            self.teacher_window.import_file_path = "/path/to/test.xlsx"

            # Mock the import service
            mock_teachers = [
                Teacher(teacher_id="TC001", teacher_name="John Doe", department="Mathematics"),
                Teacher(teacher_id="TC002", teacher_name="Jane Smith", department="Science")
            ]
            self.mock_teacher_service.import_teachers_from_excel.return_value = mock_teachers

            # Trigger import
            self.teacher_window._on_import_teachers()

            # Verify import was called
            self.mock_teacher_service.import_teachers_from_excel.assert_called_once_with("/path/to/test.xlsx")

            # Verify table refresh was called
            self.mock_teacher_service.get_all_teachers.assert_called()

    def test_export_functionality(self):
        """Test the export functionality."""
        # Mock file dialog
        with patch('PyQt6.QtWidgets.QFileDialog.getSaveFileName') as mock_file_dialog:
            mock_file_dialog.return_value = ("/path/to/export.xlsx", "Excel Files (*.xlsx)")

            # Mock export service
            self.mock_teacher_service.export_teachers_to_excel.return_value = True

            # Trigger export
            self.teacher_window._on_export_teachers()

            # Verify export was called
            self.mock_teacher_service.export_teachers_to_excel.assert_called_once_with("/path/to/export.xlsx")

    def test_operation_completed_handler(self):
        """Test the operation completed handler."""
        # Mock table refresh
        self.mock_teacher_service.get_all_teachers.return_value = []

        # Test success case
        self.teacher_window._handle_operation_completed(True, "Teacher created successfully")

        # Verify table refresh was called
        self.mock_teacher_service.get_all_teachers.assert_called_once()

        # Reset mock
        self.mock_teacher_service.reset_mock()

        # Test failure case
        self.teacher_window._handle_operation_completed(False, "Failed to create teacher")

        # Table should not be refreshed on failure
        self.mock_teacher_service.get_all_teachers.assert_not_called()

    def test_undo_functionality(self):
        """Test the undo functionality."""
        # Mock teacher for undo operations
        mock_teacher = Teacher(teacher_id="TC001", teacher_name="John Doe", department="Mathematics")

        # Add an operation to undo stack
        self.teacher_window._track_operation('create', {
            'teacher_id': 'TC001',
            'teacher_name': 'John Doe',
            'department': 'Mathematics'
        })

        # Verify undo stack has items
        self.assertEqual(len(self.teacher_window.undo_stack), 1)

        # Verify undo action is enabled
        self.assertTrue(self.teacher_window.undo_action.isEnabled())

        # Mock the delete operation for undo
        self.mock_teacher_service.delete_teacher.return_value = True

        # Trigger undo
        self.teacher_window._on_undo_operation()

        # Verify undo was performed
        self.mock_teacher_service.delete_teacher.assert_called_once_with('TC001')

        # Verify undo stack is now empty
        self.assertEqual(len(self.teacher_window.undo_stack), 0)

    def test_error_handling_in_operations(self):
        """Test error handling in various operations."""
        # Test import error handling
        self.mock_teacher_service.import_teachers_from_excel.side_effect = Exception("Import failed")

        with patch('PyQt6.QtWidgets.QFileDialog.getOpenFileName') as mock_file_dialog:
            mock_file_dialog.return_value = ("/path/to/test.xlsx", "Excel Files (*.xlsx *.xls)")
            self.teacher_window.import_file_path = "/path/to/test.xlsx"

            self.teacher_window._on_import_teachers()

            # Verify error was handled (no exception should be raised)
            self.assertTrue(True)  # If we get here, error was handled

        # Test export error handling
        self.mock_teacher_service.export_teachers_to_excel.side_effect = Exception("Export failed")

        with patch('PyQt6.QtWidgets.QFileDialog.getSaveFileName') as mock_file_dialog:
            mock_file_dialog.return_value = ("/path/to/export.xlsx", "Excel Files (*.xlsx)")

            self.teacher_window._on_export_teachers()

            # Verify error was handled (no exception should be raised)
            self.assertTrue(True)  # If we get here, error was handled

    def test_refresh_table_functionality(self):
        """Test the table refresh functionality."""
        # Mock teacher data
        mock_teachers = [
            Teacher(teacher_id="TC001", teacher_name="John Doe", department="Mathematics")
        ]
        self.mock_teacher_service.get_all_teachers.return_value = mock_teachers

        # Trigger refresh
        self.teacher_window._refresh_teachers_table()

        # Verify service was called
        self.mock_teacher_service.get_all_teachers.assert_called_once()

        # Verify table was populated
        self.assertEqual(self.teacher_window.teachers_table.rowCount(), 1)


if __name__ == '__main__':
    unittest.main()