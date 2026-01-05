# Teacher model
from .base import BaseModel

class Teacher(BaseModel):
    __tablename__ = 'teachers'
    __pk__ = "teacher_id"
    
    def __init__(self, teacher_id, teacher_name):
        super().__init__()
        self.teacher_id = teacher_id
        self.teacher_name = teacher_name
    
    def save(self):
        """Save the teacher to the database."""
        db = get_db_session()
        cursor = db.cursor()
        cursor.execute(
            "INSERT INTO teachers (teacher_id, teacher_name) VALUES (?, ?)",
            (self.teacher_id, self.teacher_name)
        )
        db.commit()
    
    def __repr__(self):
        return f"<Teacher(teacher_id={self.teacher_id}, teacher_name={self.teacher_name})>"
