import hashlib
import re
from typing import Any, Dict, List, Optional
from datetime import datetime, date
import json
import os


class StringUtils:
    """String utility functions."""
    
    @staticmethod
    def normalize_string(text: str) -> str:
        """Normalize string by removing extra whitespace and converting to lowercase."""
        if not text:
            return ""
        return re.sub(r'\s+', ' ', text.strip()).lower()
    
    @staticmethod
    def truncate(text: str, max_length: int = 50, suffix: str = "...") -> str:
        """Truncate string to maximum length."""
        if not text:
            return ""
        if len(text) <= max_length:
            return text
        return text[:max_length - len(suffix)] + suffix
    
    @staticmethod
    def generate_slug(text: str) -> str:
        """Generate URL-friendly slug from text."""
        if not text:
            return ""
        # Convert to lowercase
        slug = text.lower()
        # Remove special characters
        slug = re.sub(r'[^\w\s-]', '', slug)
        # Replace whitespace with hyphens
        slug = re.sub(r'\s+', '-', slug)
        # Remove leading/trailing hyphens
        slug = slug.strip('-')
        return slug


class HashUtils:
    """Hashing utility functions."""
    
    @staticmethod
    def hash_password(password: str, algorithm: str = "sha256") -> str:
        """Hash password using specified algorithm."""
        if algorithm == "sha256":
            return hashlib.sha256(password.encode()).hexdigest()
        elif algorithm == "md5":
            return hashlib.md5(password.encode()).hexdigest()
        else:
            raise ValueError(f"Unsupported hashing algorithm: {algorithm}")
    
    @staticmethod
    def verify_password(password: str, hashed_password: str, algorithm: str = "sha256") -> bool:
        """Verify password against hashed password."""
        return HashUtils.hash_password(password, algorithm) == hashed_password


class DateUtils:
    """Date utility functions."""
    
    @staticmethod
    def format_date(date_obj: date, format_str: str = "%Y-%m-%d") -> str:
        """Format date object as string."""
        if not date_obj:
            return ""
        return date_obj.strftime(format_str)
    
    @staticmethod
    def parse_date(date_str: str, format_str: str = "%Y-%m-%d") -> Optional[date]:
        """Parse date string to date object."""
        if not date_str:
            return None
        try:
            return datetime.strptime(date_str, format_str).date()
        except ValueError:
            return None
    
    @staticmethod
    def get_current_date() -> date:
        """Get current date."""
        return datetime.now().date()
    
    @staticmethod
    def calculate_age(birth_date: date) -> int:
        """Calculate age from birth date."""
        if not birth_date:
            return 0
        today = datetime.now().date()
        age = today.year - birth_date.year
        if today.month < birth_date.month or (today.month == birth_date.month and today.day < birth_date.day):
            age -= 1
        return age


class FileUtils:
    """File utility functions."""
    
    @staticmethod
    def read_json_file(file_path: str) -> Dict[str, Any]:
        """Read JSON file."""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError, IOError) as e:
            raise ValueError(f"Failed to read JSON file: {e}")
    
    @staticmethod
    def write_json_file(file_path: str, data: Dict[str, Any], indent: int = 4) -> bool:
        """Write JSON file."""
        try:
            # Create directory if it doesn't exist
            os.makedirs(os.path.dirname(file_path), exist_ok=True)
            
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=indent, ensure_ascii=False)
            return True
        except (IOError, TypeError) as e:
            raise ValueError(f"Failed to write JSON file: {e}")
    
    @staticmethod
    def get_file_extension(file_path: str) -> str:
        """Get file extension from path."""
        return os.path.splitext(file_path)[1].lower()


class DataUtils:
    """Data utility functions."""
    
    @staticmethod
    def filter_dict(data: Dict[str, Any], keys: List[str]) -> Dict[str, Any]:
        """Filter dictionary to include only specified keys."""
        return {k: v for k, v in data.items() if k in keys}
    
    @staticmethod
    def merge_dicts(dict1: Dict[str, Any], dict2: Dict[str, Any]) -> Dict[str, Any]:
        """Merge two dictionaries, with dict2 values taking precedence."""
        result = dict1.copy()
        result.update(dict2)
        return result
    
    @staticmethod
    def deep_merge_dicts(dict1: Dict[str, Any], dict2: Dict[str, Any]) -> Dict[str, Any]:
        """Deep merge two dictionaries."""
        result = dict1.copy()
        for key, value in dict2.items():
            if key in result and isinstance(result[key], dict) and isinstance(value, dict):
                result[key] = DataUtils.deep_merge_dicts(result[key], value)
            else:
                result[key] = value
        return result