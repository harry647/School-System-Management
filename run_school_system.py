#!/usr/bin/env python3
"""
Run script for the School System Management application.

This script sets up the environment and runs the application.
"""

import os
import sys

def main():
    """Run the School System Management application."""
    # Add the current directory to Python path
    current_dir = os.path.dirname(os.path.abspath(__file__))
    sys.path.insert(0, current_dir)
    
    print("Starting School System Management Application...")
    print("Default login credentials:")
    print("  Username: admin")
    print("  Password: harry123")
    print()
    
    try:
        # Import and run the main application
        from school_system.src.main import main
        return main()
    except ImportError as e:
        print(f"Import error: {e}")
        print("Make sure you're running this from the correct directory.")
        return 1
    except Exception as e:
        print(f"Application error: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(main())