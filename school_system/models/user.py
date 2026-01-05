# User models
from .base import BaseModel

class User(BaseModel):
    __tablename__ = 'users'
    __pk__ = "username"
    
    def __init__(self, username, password, role="student"):
        super().__init__()
        self.username = username
        self.password = password
        self.role = role
    
    def save(self):
        """Save the user to the database."""
        db = get_db_session()
        cursor = db.cursor()
        cursor.execute(
            "INSERT INTO users (username, password, role) VALUES (?, ?, ?)",
            (self.username, self.password, self.role)
        )
        db.commit()
    
    def __repr__(self):
        return f"<User(username={self.username}, role={self.role})>"

class UserSetting(BaseModel):
    __tablename__ = 'settings'
    __pk__ = "user_id"
    def __init__(self, user_id, reminder_frequency="daily", sound_enabled=1):
        super().__init__()
        self.user_id = user_id
        self.reminder_frequency = reminder_frequency
        self.sound_enabled = sound_enabled
    
    def save(self):
        """Save the user setting to the database."""
        db = get_db_session()
        cursor = db.cursor()
        cursor.execute(
            "INSERT INTO settings (user_id, reminder_frequency, sound_enabled) VALUES (?, ?, ?)",
            (self.user_id, self.reminder_frequency, self.sound_enabled)
        )
        db.commit()
    
    def __repr__(self):
        return f"<UserSetting(user_id={self.user_id}, reminder_frequency={self.reminder_frequency})>"

class ShortFormMapping(BaseModel):
    __tablename__ = 'short_form_mappings'
    __pk__ = "short_form"
    def __init__(self, short_form, full_name, type):
        super().__init__()
        self.short_form = short_form
        self.full_name = full_name
        self.type = type
    
    def save(self):
        """Save the short form mapping to the database."""
        db = get_db_session()
        cursor = db.cursor()
        cursor.execute(
            "INSERT INTO short_form_mappings (short_form, full_name, type) VALUES (?, ?, ?)",
            (self.short_form, self.full_name, self.type)
        )
        db.commit()
    
    def __repr__(self):
        return f"<ShortFormMapping(short_form={self.short_form}, full_name={self.full_name})>"
