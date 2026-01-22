import sys
import os

# Add the project root to Python path
sys.path.insert(0, os.path.abspath('.'))

from PyQt6.QtWidgets import QApplication
from school_system.gui.dialogs.confirm_dialog import ConfirmationDialog

def test_confirmation_dialog():
    """Test the confirmation dialog."""
    try:
        # Create QApplication if it doesn't exist
        app = QApplication.instance()
        if app is None:
            app = QApplication(sys.argv)

        # Test creating the dialog with correct parameters
        dialog = ConfirmationDialog(
            title="Test Delete",
            message="Are you sure you want to delete this item?\n\nThis action cannot be undone.",
            confirm_text="Delete",
            cancel_text="Cancel"
        )

        print("ConfirmationDialog created successfully!")
        print(f"Title: {dialog.windowTitle()}")

        # Don't actually show the dialog, just test creation
        dialog.close()

        print("ConfirmationDialog test completed successfully!")

    except Exception as e:
        print(f'Error testing confirmation dialog: {e}')
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    test_confirmation_dialog()