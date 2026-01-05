# Book models
from .base import BaseModel

class Book(BaseModel):
    __tablename__ = 'books'
    
    def __init__(self, book_number, available=1, revision=0, book_condition="New"):
        super().__init__()
        self.book_number = book_number
        self.available = available
        self.revision = revision
        self.book_condition = book_condition
    
    def save(self):
        """Save the book to the database."""
        db = get_db_session()
        cursor = db.cursor()
        cursor.execute(
            "INSERT INTO books (book_number, available, revision, book_condition) VALUES (?, ?, ?, ?)",
            (self.book_number, self.available, self.revision, self.book_condition)
        )
        db.commit()
    
    def __repr__(self):
        return f"<Book(book_number={self.book_number}, available={self.available})>"

class BookTag(BaseModel):
    __tablename__ = 'book_tags'
    def __init__(self, book_id, tag):
        super().__init__()
        self.book_id = book_id
        self.tag = tag
    
    def save(self):
        """Save the book tag to the database."""
        db = get_db_session()
        cursor = db.cursor()
        cursor.execute(
            "INSERT INTO book_tags (book_id, tag) VALUES (?, ?)",
            (self.book_id, self.tag)
        )
        db.commit()
    
    def __repr__(self):
        return f"<BookTag(book_id={self.book_id}, tag={self.tag})>"

class BorrowedBookStudent(BaseModel):
    __tablename__ = 'borrowed_books_student'
    def __init__(self, student_id, book_id, borrowed_on, reminder_days=None):
        super().__init__()
        self.student_id = student_id
        self.book_id = book_id
        self.borrowed_on = borrowed_on
        self.reminder_days = reminder_days
    
    def save(self):
        """Save the borrowed book record to the database."""
        db = get_db_session()
        cursor = db.cursor()
        cursor.execute(
            "INSERT INTO borrowed_books_student (student_id, book_id, borrowed_on, reminder_days) VALUES (?, ?, ?, ?)",
            (self.student_id, self.book_id, self.borrowed_on, self.reminder_days)
        )
        db.commit()
    
    def __repr__(self):
        return f"<BorrowedBookStudent(student_id={self.student_id}, book_id={self.book_id})>"

class BorrowedBookTeacher(BaseModel):
    __tablename__ = 'borrowed_books_teacher'
    def __init__(self, teacher_id, book_id, borrowed_on):
        super().__init__()
        self.teacher_id = teacher_id
        self.book_id = book_id
        self.borrowed_on = borrowed_on
    
    def save(self):
        """Save the borrowed book record to the database."""
        db = get_db_session()
        cursor = db.cursor()
        cursor.execute(
            "INSERT INTO borrowed_books_teacher (teacher_id, book_id, borrowed_on) VALUES (?, ?, ?)",
            (self.teacher_id, self.book_id, self.borrowed_on)
        )
        db.commit()
    
    def __repr__(self):
        return f"<BorrowedBookTeacher(teacher_id={self.teacher_id}, book_id={self.book_id})>"

class QRBook(BaseModel):
    __tablename__ = 'qr_books'
    def __init__(self, book_number, details="", added_date=None):
        super().__init__()
        self.book_number = book_number
        self.details = details
        self.added_date = added_date
    
    def save(self):
        """Save the QR book to the database."""
        db = get_db_session()
        cursor = db.cursor()
        cursor.execute(
            "INSERT INTO qr_books (book_number, details, added_date) VALUES (?, ?, ?)",
            (self.book_number, self.details, self.added_date)
        )
        db.commit()
    
    def __repr__(self):
        return f"<QRBook(book_number={self.book_number})>"

class QRBorrowLog(BaseModel):
    __tablename__ = 'qr_borrow_log'
    def __init__(self, book_number, student_id, borrow_date, return_date=None):
        super().__init__()
        self.book_number = book_number
        self.student_id = student_id
        self.borrow_date = borrow_date
        self.return_date = return_date
    
    def save(self):
        """Save the QR borrow log to the database."""
        db = get_db_session()
        cursor = db.cursor()
        cursor.execute(
            "INSERT INTO qr_borrow_log (book_number, student_id, borrow_date, return_date) VALUES (?, ?, ?, ?)",
            (self.book_number, self.student_id, self.borrow_date, self.return_date)
        )
        db.commit()
    
    def __repr__(self):
        return f"<QRBorrowLog(book_number={self.book_number}, student_id={self.student_id})>"

class DistributionSession(BaseModel):
    __tablename__ = 'distribution_sessions'
    def __init__(self, class_name, stream, subject, term, created_by, distributed_by=None, status="DRAFT"):
        super().__init__()
        self.class_name = class_name
        self.stream = stream
        self.subject = subject
        self.term = term
        self.created_by = created_by
        self.distributed_by = distributed_by
        self.status = status
    
    def save(self):
        """Save the distribution session to the database."""
        db = get_db_session()
        cursor = db.cursor()
        cursor.execute(
            "INSERT INTO distribution_sessions (class, stream, subject, term, created_by, distributed_by, status) VALUES (?, ?, ?, ?, ?, ?, ?)",
            (self.class_name, self.stream, self.subject, self.term, self.created_by, self.distributed_by, self.status)
        )
        db.commit()
    
    def __repr__(self):
        return f"<DistributionSession(class={self.class_name}, subject={self.subject}, status={self.status})>"

class DistributionStudent(BaseModel):
    __tablename__ = 'distribution_students'
    def __init__(self, session_id, student_id, book_id=None, book_number=None, notes=None):
        super().__init__()
        self.session_id = session_id
        self.student_id = student_id
        self.book_id = book_id
        self.book_number = book_number
        self.notes = notes
    
    def save(self):
        """Save the distribution student record to the database."""
        db = get_db_session()
        cursor = db.cursor()
        cursor.execute(
            "INSERT INTO distribution_students (session_id, student_id, book_id, book_number, notes) VALUES (?, ?, ?, ?, ?)",
            (self.session_id, self.student_id, self.book_id, self.book_number, self.notes)
        )
        db.commit()
    
    def __repr__(self):
        return f"<DistributionStudent(session_id={self.session_id}, student_id={self.student_id})>"

class DistributionImportLog(BaseModel):
    __tablename__ = 'distribution_import_logs'
    def __init__(self, session_id, file_name, imported_by, status, message):
        super().__init__()
        self.session_id = session_id
        self.file_name = file_name
        self.imported_by = imported_by
        self.status = status
        self.message = message
    
    def save(self):
        """Save the distribution import log to the database."""
        db = get_db_session()
        cursor = db.cursor()
        cursor.execute(
            "INSERT INTO distribution_import_logs (session_id, file_name, imported_by, status, message) VALUES (?, ?, ?, ?, ?)",
            (self.session_id, self.file_name, self.imported_by, self.status, self.message)
        )
        db.commit()
    
    def __repr__(self):
        return f"<DistributionImportLog(session_id={self.session_id}, file_name={self.file_name})>"