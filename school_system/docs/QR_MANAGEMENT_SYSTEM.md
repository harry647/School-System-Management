# QR Code Management System

## Overview

The QR Code Management System enables seamless library operations through QR code-based book and student identification. This system allows for:

- **Book QR Code Generation**: Unique QR codes for each book
- **Student QR Code Generation**: Unique QR codes for student borrowing cards
- **QR-Based Borrowing**: Scan book and student QR codes to borrow
- **QR-Based Returning**: Scan QR codes to return books with condition tracking
- **Batch Operations**: Generate QR codes for entire collections
- **Visual QR Display**: View and print QR codes for books and student cards

## Features

### 📚 Book QR Management
- Generate unique QR codes for individual books
- Batch generation for entire book collections
- View QR codes in popup dialogs
- Filter books by QR code status
- Export QR codes for printing

### 👨‍🎓 Student QR Management
- Generate unique QR codes for students
- Create printable student borrowing cards
- Batch generation for entire student populations
- Preview student borrowing cards with QR codes

### 📖 QR-Based Borrowing
- Scan book QR code
- Scan student QR code
- Instant borrowing with real-time validation
- Status updates and error handling

### ↩️ QR-Based Returning
- Scan book QR code
- Scan student QR code
- Select return condition (Good/Fair/Poor/Lost/Damaged)
- Automatic availability updates

## Database Schema

### Books Table Extensions
```sql
ALTER TABLE books ADD COLUMN qr_code TEXT UNIQUE;
ALTER TABLE books ADD COLUMN qr_generated_at TIMESTAMP;
```

### Students Table Extensions
```sql
ALTER TABLE students ADD COLUMN qr_code TEXT UNIQUE;
ALTER TABLE students ADD COLUMN qr_generated_at TIMESTAMP;
```

## Model Updates

### Book Model
- Added `qr_code` and `qr_generated_at` attributes
- Added `generate_qr_code()` method for unique code generation
- Updated `save()` and `update()` methods

### Student Model
- Added `qr_code` and `qr_generated_at` attributes
- Added `generate_qr_code()` method for unique code generation
- Updated `save()` and `update()` methods

## Service Layer

### BookService Enhancements
- `generate_qr_code_for_book(book_id)` - Generate QR for specific book
- `get_book_by_qr_code(qr_code)` - Find book by QR code
- `borrow_book_by_qr(book_qr, student_qr)` - QR-based borrowing
- `return_book_by_qr(book_qr, student_qr, condition)` - QR-based returning

### StudentService Enhancements
- `generate_qr_code_for_student(admission_number)` - Generate QR for student
- `get_student_by_qr_code(qr_code)` - Find student by QR code

## User Interface

### QR Management Window (`QRManagementWindow`)

#### Books QR Tab
- **Table Columns**: Book Number, Title, Author, Subject, Class, Available, QR Code, Generated Date, Actions
- **Actions**: Generate QR, View QR Code
- **Filters**: Search by title/author/book number, Filter by QR status
- **Batch Operations**: Generate QR for all books, Export QR codes

#### Students QR Tab
- **Table Columns**: Admission Number, Name, Stream, QR Code, Generated Date, Actions, Card Preview
- **Actions**: Generate QR, View QR Code
- **Filters**: Search by name/admission number, Filter by QR status
- **Batch Operations**: Generate QR for all students, Export QR codes

#### QR Borrow Tab
- **Inputs**: Book QR code, Student QR code
- **Validation**: Real-time QR code validation
- **Status Display**: Live operation results and error messages

#### QR Return Tab
- **Inputs**: Book QR code, Student QR code, Return condition
- **Validation**: Real-time QR code validation
- **Status Display**: Live operation results and error messages

### Student Borrowing Card

The system generates printable student borrowing cards containing:
- Student name
- Admission number
- Stream/class information
- QR code for identification
- Card validity instructions

## QR Code Generation

### Algorithm
```python
unique_string = f"{identifier}_{name}_{timestamp}"
qr_code = hashlib.sha256(unique_string.encode()).hexdigest()[:16].upper()
```

### Format
- **Length**: 16 characters
- **Characters**: Uppercase hexadecimal (0-9, A-F)
- **Uniqueness**: SHA256 hash ensures uniqueness
- **Example**: `A1B2C3D4E5F6789A`

## Installation & Setup

### Requirements
```txt
qrcode[pil]>=7.3.1
Pillow>=9.0.0
```

### Database Migration
Run the migration script to add QR columns:
```bash
python -m school_system.database.migrations.add_qr_codes_migration
```

Or run all migrations:
```bash
python -m school_system.database.migrations.run_all_migrations
```

## Usage Guide

### 1. Accessing QR Management
- Open main application
- Navigate to **Library Management** → **📱 QR Code Management**

### 2. Setting Up Book QR Codes
1. Go to **Books QR Codes** tab
2. Select books without QR codes
3. Click **Generate QR** for individual books
4. Or use **Generate QR for All** for batch operation
5. View QR codes by clicking **View QR**

### 3. Setting Up Student QR Codes
1. Go to **Students QR Codes** tab
2. Select students without QR codes
3. Click **Generate QR** for individual students
4. Or use **Generate QR for All** for batch operation
5. Preview student cards by clicking **Preview Card**

### 4. QR-Based Borrowing
1. Go to **QR Borrow** tab
2. Scan or enter book QR code
3. Scan or enter student QR code
4. Click **Borrow Book**
5. Check status in the results area

### 5. QR-Based Returning
1. Go to **QR Return** tab
2. Scan or enter book QR code
3. Scan or enter student QR code
4. Select return condition
5. Click **Return Book**
6. Check status in the results area

## Technical Implementation

### QR Code Generation
```python
def generate_qr_code(self, data: str) -> str:
    """Generate unique QR code using SHA256 hash"""
    unique_string = f"{data}_{datetime.now().isoformat()}"
    return hashlib.sha256(unique_string.encode()).hexdigest()[:16].upper()
```

### QR Code Display
```python
def _generate_qr_pixmap(self, data: str, size: int = 200) -> QPixmap:
    """Generate QR code image using qrcode library"""
    qr = qrcode.QRCode(version=1, box_size=10, border=5)
    qr.add_data(data)
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white")
    # Convert to QPixmap for Qt display
```

### Validation
- **Book QR**: Must exist in books table and be available
- **Student QR**: Must exist in students table
- **Borrowing**: Student cannot have overdue books
- **Returning**: Book must be borrowed by that student

## Security Considerations

### QR Code Uniqueness
- SHA256 hashing ensures uniqueness
- Timestamp inclusion prevents collisions
- Database UNIQUE constraints prevent duplicates

### Data Privacy
- QR codes contain only identification data
- No personal information encoded in QR codes
- Secure hash generation prevents reverse engineering

## Future Enhancements

### Planned Features
- **Bulk QR Printing**: Print QR code sheets for books
- **QR Reader Integration**: Hardware scanner support
- **Mobile App**: QR scanning via mobile devices
- **Analytics**: QR usage statistics and reports
- **Offline Mode**: QR validation without network

### API Endpoints (Future)
- `POST /api/qr/generate` - Generate QR codes
- `GET /api/qr/validate/{code}` - Validate QR codes
- `POST /api/qr/borrow` - QR-based borrowing
- `POST /api/qr/return` - QR-based returning

## Troubleshooting

### Common Issues

#### QR Code Not Generating
- Check database connection
- Ensure required columns exist (run migrations)
- Verify write permissions

#### QR Code Not Scanning
- Ensure good lighting
- Check QR code quality
- Verify code format (16-character uppercase hex)

#### Borrow/Return Operations Failing
- Verify QR codes exist and are valid
- Check book availability status
- Confirm student borrowing eligibility

### Logs
Check application logs for detailed error information:
- QR generation failures
- Database operation errors
- Validation failures

## Support

For technical support or feature requests, please refer to the main application documentation or contact the development team.