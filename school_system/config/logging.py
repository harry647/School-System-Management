import logging
import logging.handlers
import os
from datetime import datetime
from .settings import Settings


def setup_logging():
    """Configure logging for the application."""
    settings = Settings()
    
    # Create logs directory if it doesn't exist
    os.makedirs(os.path.dirname(settings.log_file_path), exist_ok=True)
    
    # Create a logger
    logger = logging.getLogger('school_system')
    logger.setLevel(getattr(logging, settings.log_level.upper(), logging.INFO))
    
    # Remove any existing handlers
    for handler in logger.handlers[:]:
        logger.removeHandler(handler)
    
    # Create formatter
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Create file handler
    file_handler = logging.handlers.RotatingFileHandler(
        settings.log_file_path,
        maxBytes=5*1024*1024,  # 5 MB
        backupCount=3,
        encoding='utf-8'
    )
    file_handler.setLevel(getattr(logging, settings.log_level.upper(), logging.INFO))
    file_handler.setFormatter(formatter)
    
    # Create console handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.DEBUG if settings.debug else logging.INFO)
    console_handler.setFormatter(formatter)
    
    # Add handlers
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)
    
    return logger


def get_logger(name: str = 'school_system') -> logging.Logger:
    """Get a configured logger instance."""
    return logging.getLogger(name)


# Initialize logging when this module is imported
logger = setup_logging()
