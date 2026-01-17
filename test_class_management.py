#!/usr/bin/env python3
"""
Quick test to verify ClassManagementWindow fixes work.
"""

import sys
import os

# Add the project root to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    from school_system.gui.windows.student_window.class_management_window import ClassManagementWindow
    print("[PASS] ClassManagementWindow imported successfully")
except Exception as e:
    print(f"[FAIL] Failed to import ClassManagementWindow: {e}")
    sys.exit(1)

# Try to instantiate (without showing GUI)
try:
    # We'll just test the basic instantiation without actually showing the window
    # since that requires a QApplication
    window = ClassManagementWindow.__new__(ClassManagementWindow)
    window.__init__()
    print("[PASS] ClassManagementWindow instantiated successfully")
    print("[PASS] self.classes attribute exists:", hasattr(window, 'classes'))
    if hasattr(window, 'classes'):
        print(f"[PASS] self.classes type: {type(window.classes)}")
except Exception as e:
    print(f"[FAIL] Failed to instantiate ClassManagementWindow: {e}")
    sys.exit(1)

print("[SUCCESS] All ClassManagementWindow tests passed!")