# Furniture models
from .base import BaseModel, get_db_session

class Chair(BaseModel):
    __tablename__ = 'chairs'
    __pk__ = "chair_id"
    def __init__(self, chair_id, location=None, form=None, color="Black", cond="Good", assigned=0):
        super().__init__()
        self.chair_id = chair_id
        self.location = location
        self.form = form
        self.color = color
        self.cond = cond
        self.assigned = assigned
    
    def save(self):
        """Save the chair to the database."""
        db = get_db_session()
        cursor = db.cursor()
        cursor.execute(
            "INSERT INTO chairs (chair_id, location, form, color, cond, assigned) VALUES (?, ?, ?, ?, ?, ?)",
            (self.chair_id, self.location, self.form, self.color, self.cond, self.assigned)
        )
        db.commit()
    
    def __repr__(self):
        return f"<Chair(chair_id={self.chair_id}, location={self.location})>"

class Locker(BaseModel):
    __tablename__ = 'lockers'
    __pk__ = "locker_id"
    def __init__(self, locker_id, location=None, form=None, color="Black", cond="Good", assigned=0):
        super().__init__()
        self.locker_id = locker_id
        self.location = location
        self.form = form
        self.color = color
        self.cond = cond
        self.assigned = assigned
    
    def save(self):
        """Save the locker to the database."""
        db = get_db_session()
        cursor = db.cursor()
        cursor.execute(
            "INSERT INTO lockers (locker_id, location, form, color, cond, assigned) VALUES (?, ?, ?, ?, ?, ?)",
            (self.locker_id, self.location, self.form, self.color, self.cond, self.assigned)
        )
        db.commit()
    
    def __repr__(self):
        return f"<Locker(locker_id={self.locker_id}, location={self.location})>"

class FurnitureCategory(BaseModel):
    __tablename__ = 'furniture_categories'
    __pk__ = "category_name"
    def __init__(self, category_name, total_count=0, needs_repair=0):
        super().__init__()
        self.category_name = category_name
        self.total_count = total_count
        self.needs_repair = needs_repair
    
    def save(self):
        """Save the furniture category to the database."""
        db = get_db_session()
        cursor = db.cursor()
        cursor.execute(
            "INSERT INTO furniture_categories (category_name, total_count, needs_repair) VALUES (?, ?, ?)",
            (self.category_name, self.total_count, self.needs_repair)
        )
        db.commit()
    
    def __repr__(self):
        return f"<FurnitureCategory(category_name={self.category_name}, total_count={self.total_count})>"

class LockerAssignment(BaseModel):
    __tablename__ = 'locker_assignments'
    __pk__ = "student_id"
    def __init__(self, student_id, locker_id, assigned_date=None):
        super().__init__()
        self.student_id = student_id
        self.locker_id = locker_id
        self.assigned_date = assigned_date
    
    def save(self):
        """Save the locker assignment to the database."""
        db = get_db_session()
        cursor = db.cursor()
        cursor.execute(
            "INSERT INTO locker_assignments (student_id, locker_id, assigned_date) VALUES (?, ?, ?)",
            (self.student_id, self.locker_id, self.assigned_date)
        )
        db.commit()
    
    def __repr__(self):
        return f"<LockerAssignment(student_id={self.student_id}, locker_id={self.locker_id})>"

class ChairAssignment(BaseModel):
    __tablename__ = 'chair_assignments'
    __pk__ = "student_id"
    def __init__(self, student_id, chair_id, assigned_date=None):
        super().__init__()
        self.student_id = student_id
        self.chair_id = chair_id
        self.assigned_date = assigned_date
    
    def save(self):
        """Save the chair assignment to the database."""
        db = get_db_session()
        cursor = db.cursor()
        cursor.execute(
            "INSERT INTO chair_assignments (student_id, chair_id, assigned_date) VALUES (?, ?, ?)",
            (self.student_id, self.chair_id, self.assigned_date)
        )
        db.commit()
    
    def __repr__(self):
        return f"<ChairAssignment(student_id={self.student_id}, chair_id={self.chair_id})>"
