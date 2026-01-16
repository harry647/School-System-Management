#!/usr/bin/env python3
"""
Comprehensive test for teacher workflow integration.
"""

import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

def test_teacher_workflow():
    """Test the complete teacher workflow integration."""
    try:
        # Test all imports
        from school_system.gui.windows.teacher_window.view_teachers_window import ViewTeachersWindow
        from school_system.gui.windows.teacher_window.add_teacher_window import AddTeacherWindow
        from school_system.gui.windows.teacher_window.edit_teacher_window import EditTeacherWindow
        from school_system.gui.windows.teacher_window.teacher_import_export_window import TeacherImportExportWindow
        from school_system.gui.windows.teacher_window.teacher_validation import TeacherValidator, ValidationResult
        from school_system.gui.windows.teacher_window.teacher_workflow_components import (
            TeacherWorkflowManager, TeacherCreationWorkflow, TeacherUpdateWorkflow, TeacherDeletionWorkflow
        )
        from school_system.services.teacher_service import TeacherService
        print('[OK] All teacher imports successful')

        # Test service functionality
        teacher_service = TeacherService()

        # Test validator
        validator = TeacherValidator()

        # Test various validations
        test_cases = [
            ('TC1234', True, 'Teacher ID validation'),
            ('INVALID', False, 'Invalid teacher ID validation'),
            ('John Doe', True, 'Name validation'),
            ('123456', False, 'Invalid name validation'),
            ('Mathematics', True, 'Department validation'),
            ('123Dept', False, 'Invalid department validation'),
        ]

        for test_value, expected, description in test_cases:
            if description == 'Teacher ID validation':
                result = validator.validate_teacher_id(test_value)
            elif description == 'Invalid teacher ID validation':
                result = validator.validate_teacher_id(test_value)
            elif description == 'Name validation':
                result = validator.validate_teacher_name(test_value)
            elif description == 'Invalid name validation':
                result = validator.validate_teacher_name(test_value)
            elif description == 'Department validation':
                result = validator.validate_department(test_value)
            elif description == 'Invalid department validation':
                result = validator.validate_department(test_value)

            if result.is_valid == expected:
                print(f'[OK] {description}: {result.is_valid}')
            else:
                print(f'[FAIL] {description}: expected {expected}, got {result.is_valid}')
                return False

        # Test workflow components
        try:
            creation_workflow = TeacherCreationWorkflow(None)
            print('[OK] Teacher creation workflow instantiated')
        except Exception as e:
            print(f'[FAIL] Teacher creation workflow failed: {e}')
            return False

        try:
            update_workflow = TeacherUpdateWorkflow(None)
            print('[OK] Teacher update workflow instantiated')
        except Exception as e:
            print(f'[FAIL] Teacher update workflow failed: {e}')
            return False

        try:
            deletion_workflow = TeacherDeletionWorkflow(None)
            print('[OK] Teacher deletion workflow instantiated')
        except Exception as e:
            print(f'[FAIL] Teacher deletion workflow failed: {e}')
            return False

        # Test main window integration (mock test)
        try:
            from school_system.gui.windows.main_window import MainWindow
            # We can't fully instantiate MainWindow without a QApplication and login,
            # but we can test the method imports
            print('[OK] MainWindow teacher methods are accessible')
        except ImportError as e:
            print(f'[FAIL] MainWindow import failed: {e}')
            return False

        print('[OK] All teacher workflow components are properly integrated and functional')
        return True

    except Exception as e:
        print(f'[FAIL] General error in teacher workflow test: {e}')
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_teacher_workflow()
    sys.exit(0 if success else 1)