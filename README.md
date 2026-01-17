# School System Management Application

A comprehensive school management system for managing students, teachers, books, furniture, and user accounts.

## Features

- **User Management**: Role-based authentication (Admin, Librarian, Student)
- **Student Management**: Add, view, and manage student records
- **Teacher Management**: Add, view, and manage teacher records  
- **Library Management**: Book inventory, borrowing, and tracking
- **Furniture Management**: Chairs, lockers, and equipment tracking
- **Reports**: Generate various system reports
- **Database**: Single SQLite database with automatic table creation

## Database

- **Single database file**: `school.db` (SQLite)
- **Configuration**: `config.json` (auto-generated on first run)
- **Tables**: All created automatically on first run
- **Size**: ~150KB with sample data
- **Admin user**: Created automatically (admin/harry123)

## Installation

### Prerequisites
- Python 3.7 or higher
- Windows/Linux/macOS

### Install Dependencies
```bash
pip install -r requirements.txt
```

### Verify Installation
```bash
python verify_requirements.py
```

### Running the Application

1. **Easy Method** (recommended):
   ```bash
   python run_school_system.py
   ```

2. **Manual Method**:
   ```bash
   set PYTHONPATH=%CD% && python school_system/src/main.py
   ```

3. **Windows Batch**:
   ```bash
   run_school_system.bat
   ```

### Default Login Credentials

- **Username**: `admin`
- **Password**: `harry123`

## Application Structure

```
school_system/
├── src/
│   ├── __init__.py
│   ├── main.py              # Application entry point
│   └── application.py       # Main application class
├── config/                  # Configuration files
├── database/               # Database connection and initialization
├── gui/                    # Graphical user interface
│   └── windows/            # Login and main windows
├── core/                   # Core utilities and validators
├── models/                 # Data models
├── services/               # Business logic services
└── tests/                  # Test files
```

## Database Schema

The application automatically creates the following tables:

- `users` - User accounts and authentication
- `students` - Student records
- `teachers` - Teacher records
- `books` - Book inventory
- `borrowed_books_student` - Student book borrowings
- `borrowed_books_teacher` - Teacher book borrowings
- `chairs` - Chair inventory and assignments
- `lockers` - Locker inventory and assignments
- `settings` - User preferences
- `furniture_categories` - Furniture categorization
- `qr_books` - QR code book tracking
- And additional supporting tables...

## User Roles

### Admin
- Full system access
- User management
- All reports
- System settings

### Librarian  
- Student and teacher management
- Book and library management
- Furniture management
- Most reports

### Student
- View borrowed books
- Basic profile information
- Limited access based on permissions

## Development

### Requirements
- Python 3.7+
- Dependencies listed in `requirements.txt`
- SQLite3 (included with Python)

### Install Development Dependencies
```bash
pip install -r requirements.txt
```

### Verify Dependencies
```bash
python verify_requirements.py
```

### Adding New Features

1. Create new GUI windows in `school_system/gui/windows/`
2. Add business logic in `school_system/services/`
3. Update database schema in `school_system/database/connection.py`
4. Add tests in `school_system/tests/`

### Logs

Application logs are stored in `logs/app.log` with rotation support.

## Troubleshooting

### Common Issues

1. **Module not found**: Make sure to run from the project root directory
2. **Database errors**: Check file permissions for database creation
3. **GUI issues**: Ensure tkinter is installed (usually default with Python)

### Database Files

- **school.db**: Main SQLite database (~150KB)
- **config.json**: Database configuration
- **logs/app.log**: Application logs

### Reset Database

To reset the database, simply delete the `school.db` file and restart the application. The database will be recreated with default settings.

## License

This project is developed for educational and administrative purposes.