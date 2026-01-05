class Settings:
    """Application-wide settings and configuration."""
    
    def __init__(self):
        # Database configuration
        self.database_url = "sqlite:///school.db"
        self.debug = False
        self.log_level = "INFO"
        
        # QR Code settings
        self.qr_code_size = (200, 200)
        self.qr_code_version = 1
        self.qr_code_error_correction = 1
        
        # Security settings
        self.max_login_attempts = 3
        self.session_timeout = 3600  # 1 hour in seconds
        self.password_min_length = 8
        
        # Application settings
        self.app_name = "School System Management"
        self.app_version = "1.0.0"
        self.default_language = "en"
        
        # File paths
        self.data_backup_path = "data/backup/"
        self.data_export_path = "data/exports/"
        self.log_file_path = "logs/app.log"
        
        # GUI settings
        self.default_window_size = (1024, 768)
        self.default_font = ("Arial", 10)
        self.theme = "light"  # 'light' or 'dark'