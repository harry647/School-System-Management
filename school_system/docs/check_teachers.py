import sqlite3
import os
import sys

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config.database import load_db_config

# Get database path from centralized config
db_config = load_db_config()
db_path = db_config.get('database', 'school_db')
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