"""
Constants for the book management system.
"""

# Spacing constants
SPACING_SMALL = 8
SPACING_MEDIUM = 12
SPACING_LARGE = 20

# Card constants
CARD_PADDING = 20
CARD_SPACING = 15

# Form field constants
REQUIRED_FIELDS = [
    'subject',
    'class',
    'book_number',
    'title',
    'author'
]

# Excel import/export constants
EXCEL_BOOK_IMPORT_COLUMNS = [
    'Book_Number',      # Required - unique identifier
    'Title',           # Required - book title
    'Author',          # Required - book author
    'Subject',         # Optional - subject/topic
    'Class',           # Optional - class level (Form 1, Grade 10, etc.)
    'Category',        # Optional - category (Fiction, Non-Fiction, etc.)
    'ISBN',            # Optional - ISBN number
    'Publication_Date', # Optional - publication date (YYYY-MM-DD)
    'Book_Condition',  # Optional - condition (New, Good, Torn, Damaged)
    'Available',       # Optional - availability (1=available, 0=borrowed)
    'Book_Type',       # Optional - book type ('course' or 'revision')
    'QR_Code',         # Optional - QR code data
    'QR_Generated_At'  # Optional - QR generation timestamp
]

EXCEL_BOOK_EXPORT_COLUMNS = [
    'Book_Number',
    'Title',
    'Author',
    'Subject',
    'Class',
    'Category',
    'ISBN',
    'Publication_Date',
    'Book_Condition',
    'Available',
    'Book_Type',
    'QR_Code',
    'QR_Generated_At',
    'Created_At'
]

EXCEL_BORROWED_BOOKS_COLUMNS = [
    'Book_ID',
    'Student_ID',
    'Due_Date',
    'Borrow_Date',
    'Condition'
]

EXCEL_STUDENT_IMPORT_COLUMNS = [
    'Student_ID',      # Required - unique student identifier (same as Admission_Number)
    'Admission_Number', # Required - admission number
    'Name',            # Required - full name
    'Class_Name',      # Required - class (Form 1, Grade 10, etc.)
    'Stream_Name',     # Required - stream (Red, Blue, etc.)
    'Stream',          # Optional - legacy stream field (e.g., "4 Red")
    'QR_Code',         # Optional - QR code data
    'QR_Generated_At', # Optional - QR generation timestamp
    'Created_At'       # Optional - creation timestamp
]

EXCEL_STUDENT_EXPORT_COLUMNS = [
    'Student_ID',
    'Admission_Number',
    'Name',
    'Class_Name',
    'Stream_Name',
    'Stream',
    'QR_Code',
    'QR_Generated_At',
    'Created_At'
]

EXCEL_BULK_BORROW_COLUMNS = [
    'Admission_Number',
    'Student_Name',
    'Book_Number'
]

# Book conditions
BOOK_CONDITIONS = ["New", "Good", "Torn", "Damaged"]

# Removal reasons
REMOVAL_REASONS = [
    "Damaged beyond repair",
    "Lost",
    "Obsolete curriculum",
    "Duplicate entry",
    "Other"
]

# User types
USER_TYPES = ["student", "teacher"]

# Return conditions
RETURN_CONDITIONS = ["Good", "Torn", "Damaged", "Lost"]

# Distribution session statuses
SESSION_STATUSES = ["DRAFT", "IMPORTED", "VERIFIED", "POSTED", "REJECTED"]

# Standard subjects
STANDARD_SUBJECTS = ["Mathematics", "Science", "English", "History", "Geography"]

# Standard classes - these should be used consistently across the system
STANDARD_CLASSES = ["Form 1", "Form 2", "Form 3", "Form 4", "Grade 10", "Grade 11", "Grade 12"]

# Class name mappings for normalization
CLASS_NAME_MAPPINGS = {
    # Form variations
    "form1": "Form 1", "form 1": "Form 1", "f1": "Form 1", "1": "Form 1",
    "form2": "Form 2", "form 2": "Form 2", "f2": "Form 2", "2": "Form 2",
    "form3": "Form 3", "form 3": "Form 3", "f3": "Form 3", "3": "Form 3",
    "form4": "Form 4", "form 4": "Form 4", "f4": "Form 4", "4": "Form 4",

    # Grade variations
    "grade10": "Grade 10", "grade 10": "Grade 10", "g10": "Grade 10", "10": "Grade 10",
    "grade11": "Grade 11", "grade 11": "Grade 11", "g11": "Grade 11", "11": "Grade 11",
    "grade12": "Grade 12", "grade 12": "Grade 12", "g12": "Grade 12", "12": "Grade 12",

    # Case variations and typos
    "Form1": "Form 1", "Form2": "Form 2", "Form3": "Form 3", "Form4": "Form 4",
    "Grade10": "Grade 10", "Grade11": "Grade 11", "Grade12": "Grade 12",
}

# Standard streams (can be expanded based on school needs)
STANDARD_STREAMS = ["Red", "Blue", "Green", "Yellow", "Orange", "White"]

# Standard terms
STANDARD_TERMS = ["Term 1", "Term 2", "Term 3"]

# Book types
BOOK_TYPES = ["course", "revision"]

# Export formats
EXPORT_FORMATS = ["Excel", "PDF"]
