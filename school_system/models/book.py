# Book models
from .base import BaseModel, get_db_session

class Book(BaseModel):
    __tablename__ = 'books'
    __pk__ = "book_number"
    
    def __init__(self, book_number, title, author, category=None,
                 isbn=None, publication_date=None, available=1,
                 revision=0, book_condition="New", id=None, subject=None, class_name=None,
                 qr_code=None, qr_generated_at=None, **kwargs):
        super().__init__()
        self.id = id
        self.book_number = book_number
        self.title = title
        self.author = author
        self.category = category
        self.isbn = isbn
        self.publication_date = publication_date
        self.available = available

        # Handle book_type from kwargs (for import) and convert to revision
        if 'book_type' in kwargs:
            book_type_value = kwargs['book_type'].lower() if kwargs['book_type'] else "course"
            self.revision = 1 if book_type_value == "revision" else 0
        else:
            self.revision = revision

        self.book_condition = book_condition
        self.subject = subject
        # Handle both 'class_name' and 'class' (database column name)
        self.class_name = class_name or kwargs.get('class')
        self.qr_code = qr_code
        self.qr_generated_at = qr_generated_at

    @property
    def book_type(self):
        """Get book type as string ('course' or 'revision')."""
        return "revision" if self.revision == 1 or self.revision == "1" else "course"

    @book_type.setter
    def book_type(self, value):
        """Set book type from string ('course' or 'revision')."""
        if isinstance(value, str):
            self.revision = 1 if value.lower() == "revision" else 0
        else:
            self.revision = value

    def save(self):
        """Save the book to the database."""
        db = get_db_session()
        cursor = db.cursor()
        cursor.execute(
            """INSERT INTO books
               (book_number, title, author, category, isbn, publication_date,
                available, revision, book_condition, subject, class, qr_code, qr_generated_at)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (self.book_number, self.title, self.author, self.category, self.isbn,
             self.publication_date, self.available, self.revision, self.book_condition,
             self.subject, self.class_name, self.qr_code, self.qr_generated_at)
        )
        db.commit()
    
    def update(self):
        """Update the book in the database."""
        db = get_db_session()
        cursor = db.cursor()
        cursor.execute(
            """UPDATE books SET
               title = ?, author = ?, category = ?, isbn = ?, publication_date = ?,
               available = ?, revision = ?, book_condition = ?, subject = ?, class = ?,
               qr_code = ?, qr_generated_at = ?
               WHERE book_number = ?""",
            (self.title, self.author, self.category, self.isbn, self.publication_date,
             self.available, self.revision, self.book_condition, self.subject, self.class_name,
             self.qr_code, self.qr_generated_at, self.book_number)
        )
        db.commit()

    def generate_qr_code(self):
        """Generate a unique QR code for this book."""
        try:
            from school_system.services.qr_service import QRService
            qr_service = QRService()

            # Generate QR code containing book information
            qr_data = f"BOOK:{self.book_number}|{self.title}|{self.author}"
            self.qr_code = qr_service.generate_qr_code(qr_data)

            import datetime
            self.qr_generated_at = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            return self.qr_code
        except Exception as e:
            # Fallback to simple hash if QR generation fails
            import hashlib
            import datetime
            unique_string = f"{self.book_number}_{self.title}_{datetime.datetime.now().isoformat()}"
            self.qr_code = hashlib.sha256(unique_string.encode()).hexdigest()[:16].upper()
            self.qr_generated_at = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            return self.qr_code

    def __repr__(self):
        return f"<Book(book_number={self.book_number}, title={self.title}, qr_code={self.qr_code}, available={self.available})>"

class BookTag(BaseModel):
    __tablename__ = 'book_tags'
    __pk__ = "book_id"
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
    __pk__ = "student_id"
    def __init__(self, student_id=None, book_id=None, borrowed_on=None, reminder_days=None,
                 returned_on=None, return_condition=None, fine_amount=0, returned_by=None, **kwargs):
        super().__init__()
        # Handle both direct arguments and kwargs (for database instantiation)
        self.student_id = student_id or kwargs.get('student_id')
        self.book_id = book_id or kwargs.get('book_id')
        self.borrowed_on = borrowed_on or kwargs.get('borrowed_on')
        self.reminder_days = reminder_days if reminder_days is not None else kwargs.get('reminder_days')
        self.returned_on = returned_on if returned_on is not None else kwargs.get('returned_on')
        self.return_condition = return_condition if return_condition is not None else kwargs.get('return_condition')
        self.fine_amount = fine_amount if fine_amount != 0 else kwargs.get('fine_amount', 0)
        self.returned_by = returned_by if returned_by is not None else kwargs.get('returned_by')
    
    def save(self):
        """Save the borrowed book record to the database."""
        db = get_db_session()
        cursor = db.cursor()
        cursor.execute(
            "INSERT INTO borrowed_books_student (student_id, book_id, borrowed_on, reminder_days, returned_on, return_condition, fine_amount, returned_by) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
            (self.student_id, self.book_id, self.borrowed_on, self.reminder_days, self.returned_on, self.return_condition, self.fine_amount, self.returned_by)
        )
        db.commit()
    
    def __repr__(self):
        return f"<BorrowedBookStudent(student_id={self.student_id}, book_id={self.book_id})>"
    
    def return_book(self, return_condition="Good", fine_amount=0, returned_by=None):
        """Mark this borrowed book as returned and update return information."""
        from datetime import date
        db = get_db_session()
        cursor = db.cursor()
        
        # Update the borrow record
        cursor.execute(
            """UPDATE borrowed_books_student
               SET returned_on = ?, return_condition = ?, fine_amount = ?, returned_by = ?
               WHERE student_id = ? AND book_id = ? AND returned_on IS NULL""",
            (date.today(), return_condition, fine_amount, returned_by, self.student_id, self.book_id)
        )
        
        # Mark the book as available
        cursor.execute(
            "UPDATE books SET available = 1 WHERE id = ?",
            (self.book_id,)
        )
        
        db.commit()
        
        # Update the model instance
        self.returned_on = date.today()
        self.return_condition = return_condition
        self.fine_amount = fine_amount
        self.returned_by = returned_by

class BorrowedBookTeacher(BaseModel):
    __tablename__ = 'borrowed_books_teacher'
    __pk__ = "teacher_id"
    def __init__(self, teacher_id=None, book_id=None, borrowed_on=None, returned_on=None, **kwargs):
        super().__init__()
        # Handle both direct arguments and kwargs (for database instantiation)
        self.teacher_id = teacher_id or kwargs.get('teacher_id')
        self.book_id = book_id or kwargs.get('book_id')
        self.borrowed_on = borrowed_on or kwargs.get('borrowed_on')
        self.returned_on = returned_on if returned_on is not None else kwargs.get('returned_on')
    
    def save(self):
        """Save the borrowed book record to the database."""
        db = get_db_session()
        cursor = db.cursor()
        cursor.execute(
            "INSERT INTO borrowed_books_teacher (teacher_id, book_id, borrowed_on, returned_on) VALUES (?, ?, ?, ?)",
            (self.teacher_id, self.book_id, self.borrowed_on, self.returned_on)
        )
        db.commit()
    
    def __repr__(self):
        return f"<BorrowedBookTeacher(teacher_id={self.teacher_id}, book_id={self.book_id})>"
    
    def return_book(self):
        """Mark this borrowed book as returned by teacher."""
        from datetime import date
        db = get_db_session()
        cursor = db.cursor()
        
        # Update the borrow record
        cursor.execute(
            """UPDATE borrowed_books_teacher
               SET returned_on = ?
               WHERE teacher_id = ? AND book_id = ? AND returned_on IS NULL""",
            (date.today(), self.teacher_id, self.book_id)
        )
        
        # Mark the book as available
        cursor.execute(
            "UPDATE books SET available = 1 WHERE id = ?",
            (self.book_id,)
        )
        
        db.commit()
        
        # Update the model instance
        self.returned_on = date.today()

class QRBook(BaseModel):
    __tablename__ = 'qr_books'
    __pk__ = "book_number"
    def __init__(self, book_number=None, details="", added_date=None, **kwargs):
        super().__init__()
        # Handle both direct arguments and kwargs (for database instantiation)
        self.book_number = book_number or kwargs.get('book_number')
        self.details = details if details != "" else kwargs.get('details', "")
        self.added_date = added_date if added_date is not None else kwargs.get('added_date')
    
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
    __pk__ = "book_number"
    def __init__(self, book_number=None, student_id=None, borrow_date=None, return_date=None, **kwargs):
        super().__init__()
        # Handle both direct arguments and kwargs (for database instantiation)
        self.book_number = book_number or kwargs.get('book_number')
        self.student_id = student_id or kwargs.get('student_id')
        self.borrow_date = borrow_date or kwargs.get('borrow_date')
        self.return_date = return_date if return_date is not None else kwargs.get('return_date')
    
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
    __pk__ = "class_name"
    def __init__(self, class_name=None, stream=None, subject=None, term=None, created_by=None, distributed_by=None, status="DRAFT", **kwargs):
        super().__init__()
        # Handle both direct arguments and kwargs (for database instantiation)
        self.class_name = class_name or kwargs.get('class_name')
        self.stream = stream or kwargs.get('stream')
        self.subject = subject or kwargs.get('subject')
        self.term = term or kwargs.get('term')
        self.created_by = created_by or kwargs.get('created_by')
        self.distributed_by = distributed_by if distributed_by is not None else kwargs.get('distributed_by')
        self.status = status if status != "DRAFT" else kwargs.get('status', "DRAFT")
    
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
    __pk__ = "session_id"
    def __init__(self, session_id=None, student_id=None, book_id=None, book_number=None, notes=None, **kwargs):
        super().__init__()
        # Handle both direct arguments and kwargs (for database instantiation)
        self.session_id = session_id or kwargs.get('session_id')
        self.student_id = student_id or kwargs.get('student_id')
        self.book_id = book_id if book_id is not None else kwargs.get('book_id')
        self.book_number = book_number if book_number is not None else kwargs.get('book_number')
        self.notes = notes if notes is not None else kwargs.get('notes')
    
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
    __pk__ = "session_id"
    def __init__(self, session_id=None, file_name=None, imported_by=None, status=None, message=None, **kwargs):
        super().__init__()
        # Handle both direct arguments and kwargs (for database instantiation)
        self.session_id = session_id or kwargs.get('session_id')
        self.file_name = file_name or kwargs.get('file_name')
        self.imported_by = imported_by or kwargs.get('imported_by')
        self.status = status or kwargs.get('status')
        self.message = message or kwargs.get('message')
    
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
