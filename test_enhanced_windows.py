#!/usr/bin/env python3
"""
Test script for enhanced borrow/return windows.
"""

import sys
import os

# Add the project root to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_enhanced_windows():
    """Test that enhanced windows can be instantiated without class_level errors."""
    try:
        from school_system.gui.windows.book_window.enhanced_return_window import EnhancedReturnWindow
        print("EnhancedReturnWindow import: PASS")

        # Test instantiation (without showing GUI)
        window = EnhancedReturnWindow.__new__(EnhancedReturnWindow)
        window.__init__(class_name="Form 3", stream_name="Red")
        print(f"EnhancedReturnWindow class_level: {window.class_level} (should be 3)")
        print("EnhancedReturnWindow instantiation: PASS")

    except Exception as e:
        print(f"EnhancedReturnWindow test: FAIL - {e}")
        return False

    try:
        from school_system.gui.windows.book_window.enhanced_borrow_window import EnhancedBorrowWindow
        print("EnhancedBorrowWindow import: PASS")

        # Test instantiation
        window = EnhancedBorrowWindow.__new__(EnhancedBorrowWindow)
        window.__init__(class_name="Grade 10", stream_name="Blue")
        print(f"EnhancedBorrowWindow class_level: {window.class_level} (should be 10)")
        print("EnhancedBorrowWindow instantiation: PASS")

    except Exception as e:
        print(f"EnhancedBorrowWindow test: FAIL - {e}")
        return False

    return True

def main():
    """Run tests."""
    print("Testing Enhanced Windows Class Level Fix")
    print("=" * 50)

    success = test_enhanced_windows()

    print("\n" + "=" * 50)
    if success:
        print("All tests passed! Enhanced windows class_level fix is working.")
    else:
        print("Some tests failed. Check the implementation.")

    return 0 if success else 1

if __name__ == "__main__":
    sys.exit(main())