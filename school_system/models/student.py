# Student models
from .base import BaseModel
from datetime import datetime

class Student(BaseModel):
    __tablename__ = 'students'
    __pk__ = "student_id"
    
    def __init__(self, admission_number, name, stream, student_id=None, created_at=None):
        super().__init__()
        self.student_id = student_id
        self.admission_number = admission_number
        self.name = name
        self.stream = stream
        self.created_at = created_at if created_at is not None else datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    
    def save(self):
        """Save the student to the database."""
        db = get_db_session()
        cursor = db.cursor()
        cursor.execute(
            "INSERT INTO students (admission_number, name, stream, created_at) VALUES (?, ?, ?, ?)",
            (self.admission_number, self.name, self.stream, self.created_at)
        )
        db.commit()
        # Retrieve the auto-generated student_id
        self.student_id = cursor.lastrowid
    
    def __repr__(self):
        return f"<Student(student_id={self.student_id}, name={self.name})>"

class ReamEntry(BaseModel):
    __tablename__ = 'ream_entries'
    __pk__ = "student_id"
    def __init__(self, student_id, reams_count, date_added=None):
        super().__init__()
        self.student_id = student_id
        self.reams_count = reams_count
        self.date_added = date_added
    
    def save(self):
        """Save the ream entry to the database."""
        db = get_db_session()
        cursor = db.cursor()
        cursor.execute(
            "INSERT INTO ream_entries (student_id, reams_count, date_added) VALUES (?, ?, ?)",
            (self.student_id, self.reams_count, self.date_added)
        )
        db.commit()
    
    def __repr__(self):
        return f"<ReamEntry(student_id={self.student_id}, reams_count={self.reams_count})>"

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