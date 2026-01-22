import sys
import os

# Add the project root to Python path
sys.path.insert(0, os.path.abspath('.'))

from PyQt6.QtWidgets import QApplication
from school_system.gui.windows.user_window.view_users_window import ViewUsersWindow

def test_view_users_window():
    """Test the view users window."""
    try:
        # Create QApplication if it doesn't exist
        app = QApplication.instance()
        if app is None:
            app = QApplication(sys.argv)

        # Create the window (but don't show it)
        window = ViewUsersWindow(current_user="admin", current_role="admin")

        # Check if the table was created and populated
        if hasattr(window, 'users_table') and window.users_table:
            print(f'Table created: {window.users_table}')
            print(f'Table row count: {window.users_table.rowCount()}')
            print(f'Table column count: {window.users_table.columnCount()}')

            # Check if data was populated
            if window.users_table.rowCount() > 0:
                print('Sample data from table:')
                for row in range(min(3, window.users_table.rowCount())):
                    row_data = []
                    for col in range(window.users_table.columnCount()):
                        item = window.users_table.item(row, col)
                        row_data.append(item.text() if item else 'N/A')
                    print(f'  Row {row}: {row_data}')

                print('User data is being displayed in the table!')
            else:
                print('No data rows found in table')

            # Check role filter
            if hasattr(window, 'role_filter'):
                print(f'Role filter items: {window.role_filter.count()}')
                roles = []
                for i in range(window.role_filter.count()):
                    roles.append(window.role_filter.itemText(i))
                print(f'Available roles in filter: {roles}')
        else:
            print('Users table not found')

        # Clean up
        window.close()
        print('View users window test completed!')

    except Exception as e:
        print(f'Error testing view users window: {e}')
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    test_view_users_window()