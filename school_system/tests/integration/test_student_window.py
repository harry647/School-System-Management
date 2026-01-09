"""
Integration tests for StudentWindow functionality.

This module tests the complete student management window to ensure
end-to-end functionality and integration between components.
"""

import unittest
from unittest.mock import Mock, patch, MagicMock
from PyQt6.QtWidgets import QApplication, QMainWindow, QTableWidgetItem, QDialog
from PyQt6.QtCore import Qt

from school_system.gui.windows.student_window import StudentWindow
from school_system.models.student import Student


class TestStudentWindow(unittest.TestCase):
    """Integration tests for StudentWindow."""
    
    def setUp(self):
        """Set up test fixtures."""
        # Create a QApplication instance for testing
        self.app = QApplication([])

        # Create a real parent window for testing
        self.parent_window = QMainWindow()
        self.parent_window.add_widget_to_content = Mock()

        # Create StudentWindow instance
        self.student_window = StudentWindow(self.parent_window, "test_user", "admin")

        # Show the window to ensure widgets are properly initialized
        self.student_window.show()
        self.app.processEvents()

        # Mock the student service
        self.mock_student_service = Mock()
        self.student_window.student_service = self.mock_student_service

        # Mock validator
        self.mock_validator = Mock()
        self.student_window.validator = self.mock_validator

        # Mock workflow manager
        self.mock_workflow_manager = Mock()
        self.student_window.workflow_manager = self.mock_workflow_manager

    def tearDown(self):
        """Clean up after tests."""
        del self.app

    def test_student_window_initialization(self):
        """Test that StudentWindow initializes correctly."""
        self.assertIsNotNone(self.student_window)
        self.assertEqual(self.student_window.windowTitle(), "School System - Student Management")
        self.assertEqual(self.student_window.current_user, "test_user")
        self.assertEqual(self.student_window.current_role, "admin")

    def test_student_window_access_control(self):
        """Test that StudentWindow enforces access control."""
        # Test with non-admin role
        non_admin_window = StudentWindow(self.parent_window, "test_user", "student")
        # The window should close itself for non-admin roles
        self.assertFalse(non_admin_window.isVisible())

    def test_import_excel_functionality(self):
        """Test the import Excel functionality."""
        # Mock file dialog
        with patch('PyQt6.QtWidgets.QFileDialog.getOpenFileName') as mock_file_dialog:
            mock_file_dialog.return_value = ("/path/to/test.xlsx", "Excel Files (*.xlsx *.xls)")
            
            # Set the import file path
            self.student_window.import_file_path = "/path/to/test.xlsx"
            
            # Mock the import service
            mock_students = [
                Student(student_id=1, admission_number="S001", name="John Doe", stream="Science"),
                Student(student_id=2, admission_number="S002", name="Jane Smith", stream="Arts")
            ]
            self.mock_student_service.import_students_from_excel.return_value = mock_students
            
            # Trigger import
            self.student_window._on_import_students()
            
            # Verify import was called
            self.mock_student_service.import_students_from_excel.assert_called_once_with("/path/to/test.xlsx")
            
            # Verify table refresh was called
            self.mock_student_service.get_all_students.assert_called()
            
            # Verify status update
            self.assertIn("Successfully imported", self.student_window.import_status_label.text())

    def test_add_student_functionality(self):
        """Test the add student functionality."""
        # Mock the student creation
        mock_student = Student(student_id=1, admission_number="S003", name="Test Student", stream="Commerce")
        self.mock_student_service.create_student.return_value = mock_student
        
        # Mock the dialog - InputDialog is imported from dialogs module
        with patch('school_system.gui.dialogs.input_dialog.InputDialog') as mock_dialog_class:
            mock_dialog_instance = Mock()
            mock_dialog_instance.exec.return_value = QDialog.DialogCode.Accepted
            
            # Mock input fields
            mock_student_id_input = Mock()
            mock_student_id_input.text.return_value = "S003"
            mock_name_input = Mock()
            mock_name_input.text.return_value = "Test Student"
            mock_stream_input = Mock()
            mock_stream_input.text.return_value = "Commerce"
            
            mock_dialog_instance.add_input_field.side_effect = [
                mock_student_id_input,
                mock_name_input,
                mock_stream_input
            ]
            
            mock_dialog_class.return_value = mock_dialog_instance
            
            # Trigger add student
            self.student_window._show_create_student_dialog()
            
            # Verify student creation was called
            self.mock_student_service.create_student.assert_called_once()
            
            # Verify table refresh was called
            self.mock_student_service.get_all_students.assert_called()

    def test_edit_student_functionality(self):
        """Test the edit student functionality."""
        # Mock existing student
        mock_student = Student(student_id=1, admission_number="S001", name="John Doe", stream="Science")
        self.mock_student_service.get_student_by_id.return_value = mock_student
        
        # Mock the workflow manager's start_workflow method to return a mock workflow
        mock_update_workflow = Mock()
        mock_update_workflow.operation_completed = Mock()
        
        # Assign the mock workflow manager to the student window and mock the start_workflow method
        self.student_window.workflow_manager = self.mock_workflow_manager
        self.student_window.workflow_manager.start_workflow = Mock(return_value=mock_update_workflow)
        
        # Trigger edit workflow
        self.student_window._start_edit_workflow("S001")
        
        # Verify workflow was started
        self.student_window.workflow_manager.start_workflow.assert_called_once_with("update")
        
        # Verify student data was retrieved
        self.mock_student_service.get_student_by_id.assert_called_once_with("S001")

    def test_delete_student_functionality(self):
        """Test the delete student functionality."""
        # Mock existing student
        mock_student = Student(student_id=1, admission_number="S001", name="John Doe", stream="Science")
        self.mock_student_service.get_student_by_id.return_value = mock_student
        
        # Mock the delete workflow
        mock_delete_workflow = Mock()
        mock_delete_workflow.operation_completed = Mock()
        
        # Mock the workflow manager to return our mock workflow
        self.student_window.workflow_manager.start_workflow = Mock(return_value=mock_delete_workflow)
        
        # Trigger delete workflow
        self.student_window._start_delete_workflow("S001")
        
        # Verify workflow was started
        self.student_window.workflow_manager.start_workflow.assert_called_once_with("delete")
        
        # Verify student data was retrieved
        self.mock_student_service.get_student_by_id.assert_called_once_with("S001")

    def test_data_display_functionality(self):
        """Test that student data is properly displayed in the table."""
        # Mock student data
        mock_students = [
            Student(student_id=1, admission_number="S001", name="John Doe", stream="Science"),
            Student(student_id=2, admission_number="S002", name="Jane Smith", stream="Arts")
        ]
        
        # Call the populate method
        self.student_window._populate_students_table(mock_students)
        
        # Verify table was populated
        self.assertEqual(self.student_window.students_table.rowCount(), 2)
        
        self.student_window.students_table.update()
        self.app.processEvents()
        
        # Verify action buttons exist
        for row in range(2):
            action_widget = self.student_window.students_table.cellWidget(row, 3)
            self.assertIsNotNone(action_widget)

    def test_search_functionality(self):
        """Test the search functionality."""
        # Mock student data
        mock_students = [
            Student(student_id=1, admission_number="S001", name="John Doe", stream="Science"),
            Student(student_id=2, admission_number="S002", name="Jane Smith", stream="Arts")
        ]
        self.mock_student_service.get_all_students.return_value = mock_students
        
        # Trigger search
        self.student_window._on_search_students("S001")
        
        # Verify search was performed (reset to page 1)
        self.assertEqual(self.student_window.current_page, 1)
        
        # Verify table refresh was called
        self.mock_student_service.get_all_students.assert_called()

    def test_pagination_functionality(self):
        """Test the pagination functionality."""
        # Mock many students
        mock_students = [
            Student(student_id=i, admission_number=f"S{i:03d}", name=f"Student {i}", stream="Science")
            for i in range(1, 51)  # 50 students
        ]
        self.mock_student_service.get_all_students.return_value = mock_students
        
        # Set items per page to 10
        self.student_window.items_per_page = 10
        self.student_window._refresh_students_table()
        
        # Verify pagination controls
        self.assertEqual(self.student_window.total_pages, 5)
        self.assertEqual(self.student_window.current_page, 1)
        self.assertEqual(self.student_window.students_table.rowCount(), 10)  # Only first page shown
        
        # Test next page
        self.student_window._on_next_page()
        self.assertEqual(self.student_window.current_page, 2)
        
        # Test previous page
        self.student_window._on_previous_page()
        self.assertEqual(self.student_window.current_page, 1)

    def test_export_functionality(self):
        """Test the export functionality."""
        # Mock file dialog
        with patch('PyQt6.QtWidgets.QFileDialog.getSaveFileName') as mock_file_dialog:
            mock_file_dialog.return_value = ("/path/to/export.xlsx", "Excel Files (*.xlsx)")
            
            # Mock export service
            self.mock_student_service.export_students_to_excel.return_value = True
            
            # Trigger export
            self.student_window._on_export_students()
            
            # Verify export was called
            self.mock_student_service.export_students_to_excel.assert_called_once_with("/path/to/export.xlsx")
            
            # Verify status update
            self.assertIn("Students exported successfully", self.student_window.export_status_label.text())

    def test_ream_management_functionality(self):
        """Test the ream management functionality."""
        # Mock student for ream operations
        mock_student = Student(student_id=1, admission_number="S001", name="John Doe", stream="Science")
        self.mock_student_service.get_student_by_id.return_value = mock_student
        
        # Mock ream entry
        mock_ream_entry = Mock()
        self.mock_student_service.add_reams_to_student.return_value = mock_ream_entry
        
        # Set input values
        self.student_window.add_ream_student_id_input.setText("S001")
        self.student_window.add_ream_count_input.setText("10")
        
        # Trigger add reams
        self.student_window._on_add_reams()
        
        # Verify ream addition was called
        self.mock_student_service.add_reams_to_student.assert_called_once()
        
        # Verify inputs were cleared
        self.assertEqual(self.student_window.add_ream_student_id_input.text(), "")
        self.assertEqual(self.student_window.add_ream_count_input.text(), "")

    def test_library_activity_functionality(self):
        """Test the library activity functionality."""
        # Mock student for library operations
        mock_student = Student(student_id=1, admission_number="S001", name="John Doe", stream="Science")
        self.mock_student_service.get_student_by_id.return_value = mock_student
        
        # Mock borrowed books
        mock_books = [
            Mock(book_id=1, title="Book 1", borrowed_on="2023-01-01", due_date="2023-01-15", returned_on=None),
            Mock(book_id=2, title="Book 2", borrowed_on="2023-01-10", due_date="2023-01-24", returned_on=None)
        ]
        self.mock_student_service.get_student_current_borrowed_books.return_value = mock_books
        
        # Set input value
        self.student_window.borrowed_student_id_input.setText("S001")
        
        # Trigger view borrowed books
        self.student_window._on_view_borrowed_books()
        
        # Verify borrowed books were retrieved
        self.mock_student_service.get_student_current_borrowed_books.assert_called_once_with("S001")
        
        # Verify table was populated
        self.assertEqual(self.student_window.borrowed_books_table.rowCount(), 2)

    def test_report_generation_functionality(self):
        """Test the report generation functionality."""
        # Mock student for reports
        mock_student = Student(student_id=1, admission_number="S001", name="John Doe", stream="Science")
        self.mock_student_service.get_student_by_id.return_value = mock_student
        
        # Mock library summary
        mock_summary = {
            'total_books_borrowed': 5,
            'current_books_borrowed': 2,
            'overdue_books': 0,
            'books_read': 3
        }
        self.mock_student_service.get_student_library_activity_summary.return_value = mock_summary
        
        # Mock ream balance
        self.mock_student_service.get_student_ream_balance.return_value = 15
        
        # Set input value
        self.student_window.summary_student_id_input.setText("S001")
        
        # Trigger report generation
        self.student_window._on_generate_student_summary()
        
        # Verify report data was retrieved
        self.mock_student_service.get_student_library_activity_summary.assert_called_once_with(1)
        self.mock_student_service.get_student_ream_balance.assert_called_once_with("S001")
        
        # Verify report was displayed
        report_text = self.student_window.summary_results_display.toPlainText()
        self.assertIn("Student Summary Report", report_text)
        self.assertIn("John Doe", report_text)
        self.assertIn("Ream Balance: 15", report_text)

    def test_error_handling_in_operations(self):
        """Test error handling in various operations."""
        # Test import error handling
        self.mock_student_service.import_students_from_excel.side_effect = Exception("Import failed")
        
        with patch('PyQt6.QtWidgets.QFileDialog.getOpenFileName') as mock_file_dialog:
            mock_file_dialog.return_value = ("/path/to/test.xlsx", "Excel Files (*.xlsx *.xls)")
            self.student_window.import_file_path = "/path/to/test.xlsx"
            
            self.student_window._on_import_students()
            
            # Verify error status
            self.assertIn("Import failed", self.student_window.import_status_label.text())
        
        # Test add student error handling
        self.mock_student_service.create_student.side_effect = Exception("Create failed")
        
        with patch('school_system.gui.dialogs.input_dialog.InputDialog') as mock_dialog_class:
            mock_dialog_instance = Mock()
            mock_dialog_instance.exec.return_value = QDialog.DialogCode.Accepted
            
            mock_student_id_input = Mock()
            mock_student_id_input.text.return_value = "S003"
            mock_name_input = Mock()
            mock_name_input.text.return_value = "Test Student"
            mock_stream_input = Mock()
            mock_stream_input.text.return_value = "Commerce"
            
            mock_dialog_instance.add_input_field.side_effect = [
                mock_student_id_input,
                mock_name_input,
                mock_stream_input
            ]
            
            mock_dialog_class.return_value = mock_dialog_instance
            
            self.student_window._show_create_student_dialog()
            
            # Verify error was handled (no exception should be raised)
            self.assertTrue(True)  # If we get here, error was handled

    def test_undo_functionality(self):
        """Test the undo functionality."""
        # Mock student for undo operations
        mock_student = Student(student_id=1, admission_number="S001", name="John Doe", stream="Science")
        
        # Add an operation to undo stack
        self.student_window._track_operation('create', {
            'student_id': 'S001',
            'student_data': {'admission_number': 'S001', 'name': 'John Doe', 'stream': 'Science'}
        })
        
        # Verify undo stack has items
        self.assertEqual(len(self.student_window.undo_stack), 1)
        
        # Verify undo action is enabled
        self.assertTrue(self.student_window.undo_action.isEnabled())
        
        # Mock the delete operation for undo
        self.mock_student_service.delete_student.return_value = True
        
        # Trigger undo
        self.student_window._on_undo_operation()
        
        # Verify undo was performed
        self.mock_student_service.delete_student.assert_called_once_with('S001')
        
        # Verify undo stack is now empty
        self.assertEqual(len(self.student_window.undo_stack), 0)


if __name__ == '__main__':
    unittest.main()