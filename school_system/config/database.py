DATABASE_CONFIG = {
    'engine': 'sqlite',
    'name': 'school.db',
    'backup_interval': 3600,  # 1 hour in seconds
    'connection_pool_size': 10,
    'connection_timeout': 30,
    'max_overflow': 20,
    'pool_recycle': 3600,  # Recycle connections after 1 hour
    'echo': False,  # Set to True for debugging SQL queries
    
    # SQLite specific settings
    'sqlite': {
        'check_same_thread': False,
        'isolation_level': None,
        'timeout': 10.0
    },
    
    # Backup settings
    'backup': {
        'enabled': True,
        'max_backups': 5,
        'backup_on_startup': True
    }
}