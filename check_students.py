import sqlite3
import os

# Check if database exists
db_path = 'school.db'
if os.path.exists(db_path):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Check if students table exists
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='students'")
    table_exists = cursor.fetchone()

    if table_exists:
        # Get table schema
        cursor.execute('PRAGMA table_info(students)')
        columns = cursor.fetchall()
        print('Students table schema:')
        for col in columns:
            print(f'  {col[1]}: {col[2]}')

        # Count students
        cursor.execute('SELECT COUNT(*) FROM students')
        count = cursor.fetchone()[0]
        print(f'\nTotal students: {count}')

        if count > 0:
            # Show first few students
            cursor.execute('SELECT * FROM students LIMIT 5')
            students = cursor.fetchall()
            print('\nFirst 5 students:')
            for student in students:
                print(f'  {student}')

            # Show streams
            cursor.execute('SELECT DISTINCT stream FROM students WHERE stream IS NOT NULL')
            streams = cursor.fetchall()
            print(f'\nAvailable streams: {[s[0] for s in streams]}')
        else:
            print('No student data found in database')
    else:
        print('Students table does not exist')

    conn.close()
else:
    print('Database file not found')