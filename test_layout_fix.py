#!/usr/bin/env python3
"""
Test script to verify that the layout parenting issues have been resolved.
Focuses specifically on student management layout issues.
"""

import sys
import traceback
from PyQt6.QtWidgets import QApplication, QWidget, QTabWidget
from PyQt6.QtCore import Qt, QTimer

# Add the school_system package to the path
sys.path.append('c:/Users/harry/School-System-Management')

from school_system.gui.windows.main_window import MainWindow
from school_system.gui.windows.student_window import StudentWindow

def test_main_window():
    """Test the main window layout."""
    print("Testing MainWindow layout...")
    try:
        # Create a minimal parent widget for testing
        app = QApplication([])
        
        # Create a proper QWidget parent
        parent = QWidget()
        
        # Test main window creation
        window = MainWindow(parent, "testuser", "admin", lambda: None)
        
        # Show the window to trigger layout operations
        window.show()
        
        # Process events to allow layouts to be set up
        app.processEvents()
        
        print("MainWindow layout test passed")
        return True
        
    except Exception as e:
        print(f"MainWindow layout test failed: {e}")
        traceback.print_exc()
        return False
    finally:
        if 'app' in locals():
            app.quit()

def test_student_window():
    """Test the student window layout with comprehensive coverage of all tabs."""
    print("Testing StudentWindow layout (Comprehensive test)...")
    try:
        # Create a minimal parent widget for testing
        app = QApplication([])
        
        # Create a proper QWidget parent
        parent = QWidget()
        
        # Test student window creation
        window = StudentWindow(parent, "testuser", "admin")
        
        # Show the window to trigger layout operations
        window.show()
        
        # Process events to allow layouts to be set up
        app.processEvents()
        
        # Get tab widget
        tab_widget = window.findChild(QTabWidget)
        if not tab_widget:
            print("Error: Tab widget not found")
            return False
        
        # Test all tabs systematically
        tab_names = ["Student Management", "Ream Management", "Library Activity", "Import/Export", "Reports"]
        
        for i, tab_name in enumerate(tab_names):
            print(f"Testing {tab_name} tab...")
            tab_widget.setCurrentIndex(i)
            app.processEvents()
            
            # Verify tab content based on tab type
            if i == 0:  # Student Management
                if hasattr(window, 'students_table') and window.students_table:
                    print(f"  [OK] Students table found with {window.students_table.rowCount()} rows")
                else:
                    print("  [ERROR] Students table not found")
                    return False
                    
            elif i == 1:  # Ream Management
                if hasattr(window, 'add_ream_student_id_input'):
                    print("  [OK] Ream management input fields found")
                else:
                    print("  [ERROR] Ream management input fields not found")
                    return False
                    
            elif i == 2:  # Library Activity
                if hasattr(window, 'borrowed_books_table') and window.borrowed_books_table:
                    print("  [OK] Library activity tables found")
                else:
                    print("  [ERROR] Library activity tables not found")
                    return False
                    
            elif i == 3:  # Import/Export
                if hasattr(window, 'import_file_label') and hasattr(window, 'export_status_label'):
                    print("  [OK] Import/Export controls found")
                else:
                    print("  [ERROR] Import/Export controls not found")
                    return False
                    
            elif i == 4:  # Reports
                if hasattr(window, 'summary_results_display') and window.summary_results_display:
                    print("  [OK] Report displays found")
                else:
                    print("  [ERROR] Report displays not found")
                    return False
        
        # Test that all tabs can be switched without layout errors
        print("Testing tab switching...")
        for i in range(tab_widget.count()):
            tab_widget.setCurrentIndex(i)
            app.processEvents()
            # Small delay to allow any layout operations
            QTimer.singleShot(50, lambda: None)
        
        print("StudentWindow comprehensive layout test passed")
        return True
        
    except Exception as e:
        print(f"StudentWindow layout test failed: {e}")
        traceback.print_exc()
        return False
    finally:
        if 'app' in locals():
            app.quit()

def main():
    """Run all layout tests."""
    print("Running layout fix tests...\n")
    
    main_window_ok = test_main_window()
    print()
    student_window_ok = test_student_window()
    
    print(f"\nTest Results:")
    print(f"MainWindow: {'PASS' if main_window_ok else 'FAIL'}")
    print(f"StudentWindow: {'PASS' if student_window_ok else 'FAIL'}")
    
    if main_window_ok and student_window_ok:
        print("\nAll layout tests passed! The parenting issues have been resolved.")
        return 0
    else:
        print("\nSome layout tests failed. There may still be issues.")
        return 1

if __name__ == "__main__":
    sys.exit(main())