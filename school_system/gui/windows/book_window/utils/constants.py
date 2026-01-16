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
    'ISBN',
    'Title',
    'Author',
    'Book_Number',
    'Subject',
    'Class',
    'Category',
    'Publication_Date',
    'Condition'
]

EXCEL_BORROWED_BOOKS_COLUMNS = [
    'Book_ID',
    'Student_ID',
    'Due_Date',
    'Borrow_Date',
    'Condition'
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

# Standard classes
STANDARD_CLASSES = ["Form 1", "Form 2", "Form 3", "Form 4"]

# Standard streams
STANDARD_STREAMS = ["East", "West", "North", "South"]

# Standard terms
STANDARD_TERMS = ["Term 1", "Term 2", "Term 3"]

# Export formats
EXPORT_FORMATS = ["Excel", "PDF"]
