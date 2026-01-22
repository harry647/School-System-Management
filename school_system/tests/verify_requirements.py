#!/usr/bin/env python3
"""
Script to verify that all required dependencies are installed correctly.
Run this after installing requirements.txt to verify everything is working.
"""

import sys
import importlib

def check_dependency(name, import_name=None):
    """Check if a dependency is available."""
    if import_name is None:
        import_name = name

    try:
        importlib.import_module(import_name)
        print(f"[OK] {name}")
        return True
    except ImportError as e:
        print(f"[MISSING] {name} - {e}")
        return False

def main():
    """Check all dependencies."""
    print("Checking School System Management Dependencies...")
    print("=" * 50)

    dependencies = [
        ("PyQt6", "PyQt6.QtWidgets"),
        ("SQLAlchemy", "sqlalchemy"),
        ("pandas", None),
        ("openpyxl", None),
        ("fpdf", None),
    ]

    standard_lib = [
        ("sqlite3", None),
        ("tkinter", None),
        ("csv", None),
        ("json", None),
        ("hashlib", None),
        ("datetime", None),
        ("os", None),
        ("sys", None),
        ("logging", None),
        ("typing", None),
    ]

    print("Third-party dependencies:")
    missing_count = 0
    for name, import_name in dependencies:
        if not check_dependency(name, import_name):
            missing_count += 1

    print("\nStandard library modules:")
    for name, import_name in standard_lib:
        check_dependency(name, import_name)

    print("\n" + "=" * 50)
    if missing_count == 0:
        print("[SUCCESS] All required dependencies are installed!")
        print("You can now run the application with: python run_school_system.py")
        return 0
    else:
        print(f"[ERROR] {missing_count} dependencies are missing.")
        print("Run: pip install -r requirements.txt")
        return 1

if __name__ == "__main__":
    sys.exit(main())