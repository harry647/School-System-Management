# Initialize the config package
from .database import engine, DATABASE_CONFIG, load_db_config, resource_path, prompt_for_db_config
from .logging import logger
from .settings import settings, get_settings, Settings
from .path_manager import (
    PathManager,
    PathType,
    get_path_manager,
    initialize_path_manager,
    ExecutionContext,
    PathValidationError,
    PathPermissionError,
    PathNotFoundError,
    NetworkPathUnavailableError
)

# Initialize path manager with application name
initialize_path_manager("School System Management")
