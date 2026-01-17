# Student models
from .base import BaseModel, get_db_session
from datetime import datetime

class Student(BaseModel):
    __tablename__ = 'students'
    __pk__ = "student_id"
    
    def __init__(self, admission_number, name, stream, student_id=None, created_at=None, qr_code=None, qr_generated_at=None):
        super().__init__()
        # In this schema, student_id should be the same as admission_number
        self.student_id = admission_number if student_id is None else student_id
        self.admission_number = admission_number
        self.name = name
        self.stream = stream
        self.created_at = created_at if created_at is not None else datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        self.qr_code = qr_code
        self.qr_generated_at = qr_generated_at
    
    def save(self):
        """Save the student to the database."""
        db = get_db_session()
        cursor = db.cursor()
        cursor.execute(
            "INSERT INTO students (student_id, admission_number, name, stream, created_at, qr_code, qr_generated_at) VALUES (?, ?, ?, ?, ?, ?, ?)",
            (self.student_id, self.admission_number, self.name, self.stream, self.created_at, self.qr_code, self.qr_generated_at)
        )
        db.commit()
    
    def update(self):
        """Update the student in the database."""
        db = get_db_session()
        cursor = db.cursor()
        cursor.execute(
            """UPDATE students SET
               admission_number = ?, name = ?, stream = ?, created_at = ?,
               qr_code = ?, qr_generated_at = ?
               WHERE student_id = ?""",
            (self.admission_number, self.name, self.stream, self.created_at,
             self.qr_code, self.qr_generated_at, self.student_id)
        )
        db.commit()

    def generate_qr_code(self):
        """Generate a unique QR code for this student."""
        import hashlib
        import datetime
        unique_string = f"{self.admission_number}_{self.name}_{datetime.datetime.now().isoformat()}"
        self.qr_code = hashlib.sha256(unique_string.encode()).hexdigest()[:16].upper()
        self.qr_generated_at = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        return self.qr_code

    def __repr__(self):
        return f"<Student(student_id={self.student_id}, admission_number={self.admission_number}, qr_code={self.qr_code}, name={self.name})>"

class ReamEntry(BaseModel):
    __tablename__ = 'ream_entries'
    __pk__ = "id"
    def __init__(self, student_id, reams_count, date_added=None, created_at=None, id=None):
        super().__init__()
        self.id = id
        self.student_id = student_id
        self.reams_count = reams_count
        self.date_added = date_added
        self.created_at = created_at
    
    def save(self):
        """Save the ream entry to the database."""
        db = get_db_session()
        cursor = db.cursor()
        cursor.execute(
            "INSERT INTO ream_entries (student_id, reams_count, date_added, created_at) VALUES (?, ?, ?, ?)",
            (self.student_id, self.reams_count, self.date_added, self.created_at)
        )
        db.commit()
    
    def __repr__(self):
        return f"<ReamEntry(id={self.id}, student_id={self.student_id}, reams_count={self.reams_count})>"

class TotalReams(BaseModel):
    __tablename__ = 'total_reams'
    def __init__(self, total_available=0):
        super().__init__()
        self.total_available = total_available
    
    def save(self):
        """Save the total reams to the database."""
        db = get_db_session()
        cursor = db.cursor()
        cursor.execute(
            "INSERT INTO total_reams (total_available) VALUES (?)",
            (self.total_available,)
        )
        db.commit()
    
    def __repr__(self):
        return f"<TotalReams(total_available={self.total_available})>"
