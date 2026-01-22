import sys
import os

# Add the project root to Python path
sys.path.insert(0, os.path.abspath('.'))

from PyQt6.QtWidgets import QApplication
from school_system.gui.windows.student_window.view_students_window import ViewStudentsWindow

def test_view_students_window():
    """Test the view students window."""
    try:
        # Create QApplication if it doesn't exist
        app = QApplication.instance()
        if app is None:
            app = QApplication(sys.argv)

        # Create the window (but don't show it)
        window = ViewStudentsWindow(current_user="admin", current_role="admin")

        # Check if the table was created and populated
        if hasattr(window, 'students_table') and window.students_table:
            print(f'Table created: {window.students_table}')
            print(f'Table row count: {window.students_table.rowCount()}')
            print(f'Table column count: {window.students_table.columnCount()}')

            # Check if data was populated
            if window.students_table.rowCount() > 0:
                print('Sample data from table:')
                for row in range(min(3, window.students_table.rowCount())):
                    row_data = []
                    for col in range(window.students_table.columnCount()):
                        item = window.students_table.item(row, col)
                        row_data.append(item.text() if item else 'N/A')
                    print(f'  Row {row}: {row_data}')

                print('Student data is being displayed in the table!')
            else:
                print('No data rows found in table')

            # Check stream filter
            if hasattr(window, 'stream_filter'):
                print(f'Stream filter items: {window.stream_filter.count()}')
                streams = []
                for i in range(window.stream_filter.count()):
                    streams.append(window.stream_filter.itemText(i))
                print(f'Available streams in filter: {streams}')
        else:
            print('❌ Students table not found')

        # Clean up
        window.close()
        print('View students window test completed!')

    except Exception as e:
        print(f'Error testing view students window: {e}')
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    test_view_students_window()