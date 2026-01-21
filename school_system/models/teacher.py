# Teacher model
from .base import BaseModel, get_db_session

class Teacher(BaseModel):
    __tablename__ = 'teachers'
    __pk__ = "teacher_id"
    
    def __init__(self, teacher_id=None, teacher_name=None, department=None, **kwargs):
        super().__init__()
        # Handle both direct arguments and kwargs (for database instantiation)
        self.teacher_id = teacher_id or kwargs.get('teacher_id')
        self.teacher_name = teacher_name or kwargs.get('teacher_name')
        self.department = department if department is not None else kwargs.get('department')
    
    def save(self):
        """Save the teacher to the database."""
        db = get_db_session()
        cursor = db.cursor()
        cursor.execute(
            "INSERT INTO teachers (teacher_id, teacher_name, department) VALUES (?, ?, ?)",
            (self.teacher_id, self.teacher_name, self.department)
        )
        db.commit()
    
    def __repr__(self):
        return f"<Teacher(teacher_id={self.teacher_id}, teacher_name={self.teacher_name})>"
