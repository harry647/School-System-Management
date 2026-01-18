# User models
from .base import BaseModel, get_db_session

class User(BaseModel):
    __tablename__ = 'users'
    __pk__ = "username"
    
    def __init__(self, username, password, role="student", **kwargs):
        super().__init__()
        self.username = username
        self.password = password
        self.role = role
        # Handle additional fields that might be returned from database
        for key, value in kwargs.items():
            setattr(self, key, value)
    
    def save(self):
        """Save the user to the database."""
        db = get_db_session()
        cursor = db.cursor()
        cursor.execute(
            "INSERT INTO users (username, password, role) VALUES (?, ?, ?)",
            (self.username, self.password, self.role)
        )
        db.commit()

    def check_password(self, password: str) -> bool:
        """Check if the provided password matches the user's password."""
        from ..core.utils import HashUtils
        return HashUtils.verify_password(password, self.password)
    
    def __repr__(self):
        return f"<User(username={self.username}, role={self.role})>"

class UserSetting(BaseModel):
    __tablename__ = 'settings'
    __pk__ = "user_id"

    def __init__(self, user_id, settings_json=None, reminder_frequency="daily", sound_enabled=1, created_at=None, updated_at=None):
        super().__init__()
        self.user_id = user_id
        self.settings_json = settings_json
        # Backward compatibility fields
        self.reminder_frequency = reminder_frequency
        self.sound_enabled = sound_enabled
        self.created_at = created_at or datetime.datetime.now()
        self.updated_at = updated_at or created_at or datetime.datetime.now()

    def save(self):
        """Save the user setting to the database."""
        db = get_db_session()
        cursor = db.cursor()
        cursor.execute(
            "INSERT INTO settings (user_id, settings_json, reminder_frequency, sound_enabled, created_at, updated_at) VALUES (?, ?, ?, ?, ?, ?)",
            (self.user_id, self.settings_json, self.reminder_frequency, self.sound_enabled, self.created_at, self.updated_at)
        )
        db.commit()

    def __repr__(self):
        return f"<UserSetting(user_id={self.user_id}, has_settings_json={self.settings_json is not None})>"

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


class GlobalSetting(BaseModel):
    __tablename__ = 'global_settings'
    __pk__ = "key"

    def __init__(self, key, value_json, created_at=None, updated_at=None):
        super().__init__()
        self.key = key
        self.value_json = value_json
        self.created_at = created_at or datetime.datetime.now()
        self.updated_at = updated_at or created_at or datetime.datetime.now()

    def save(self):
        """Save the global setting to the database."""
        db = get_db_session()
        cursor = db.cursor()
        cursor.execute(
            "INSERT INTO global_settings (key, value_json, created_at, updated_at) VALUES (?, ?, ?, ?)",
            (self.key, self.value_json, self.created_at, self.updated_at)
        )
        db.commit()

    def __repr__(self):
        return f"<GlobalSetting(key={self.key}, value_json_length={len(self.value_json) if self.value_json else 0})>"
