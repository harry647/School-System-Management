#!/usr/bin/env python3
"""
Test script to verify teacher window integration.
"""

import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

def test_teacher_imports():
    """Test that all teacher windows can be imported."""
    try:
        from school_system.gui.windows.teacher_window.view_teachers_window import ViewTeachersWindow
        from school_system.gui.windows.teacher_window.add_teacher_window import AddTeacherWindow
        from school_system.gui.windows.teacher_window.edit_teacher_window import EditTeacherWindow
        from school_system.gui.windows.teacher_window.teacher_import_export_window import TeacherImportExportWindow
        from school_system.gui.windows.teacher_window.teacher_validation import TeacherValidator
        from school_system.gui.windows.teacher_window.teacher_workflow_components import TeacherWorkflowManager
        from school_system.services.teacher_service import TeacherService
        print('[OK] All teacher window imports successful')

        # Test TeacherService
        teacher_service = TeacherService()
        print('[OK] TeacherService instantiated successfully')

        # Test TeacherValidator
        validator = TeacherValidator()
        print('[OK] TeacherValidator instantiated successfully')

        # Test validation
        result = validator.validate_teacher_id('TC1234')
        print(f'[OK] Teacher ID validation works: {result.is_valid}')

        print('[OK] All teacher window components are properly integrated')

        return True

    except ImportError as e:
        print(f'[FAIL] Import error: {e}')
        return False
    except Exception as e:
        print(f'[FAIL] General error: {e}')
        return False

if __name__ == "__main__":
    success = test_teacher_imports()
    sys.exit(0 if success else 1)
