import sqlite3
import os

db_path = 'school.db'
if os.path.exists(db_path):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    cursor.execute("PRAGMA table_info(teachers)")
    columns = cursor.fetchall()
    print('Teachers table schema:')
    for col in columns:
        print(f'  {col[1]}: {col[2]}')

    conn.close()
else:
    print('Database not found')