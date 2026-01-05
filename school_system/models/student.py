# Student models
from .base import BaseModel

class Student(BaseModel):
    __tablename__ = 'students'
    __pk__ = "student_id"
    
    def __init__(self, student_id, name, stream):
        super().__init__()
        self.student_id = student_id
        self.name = name
        self.stream = stream
    
    def save(self):
        """Save the student to the database."""
        db = get_db_session()
        cursor = db.cursor()
        cursor.execute(
            "INSERT INTO students (student_id, name, stream) VALUES (?, ?, ?)",
            (self.student_id, self.name, self.stream)
        )
        db.commit()
    
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