class SchoolSystemException(Exception):
    """Base exception for the school system."""
    pass


class ValidationError(SchoolSystemException):
    """Data validation error."""
    pass


class DatabaseException(SchoolSystemException):
    """Database operation error."""
    pass


class AuthenticationError(SchoolSystemException):
    """Authentication failure."""
    pass


class AuthorizationError(SchoolSystemException):
    """Authorization failure."""
    pass


class NotFoundError(SchoolSystemException):
    """Resource not found error."""
    pass


class ConfigurationError(SchoolSystemException):
    """Configuration error."""
    pass


class ServiceError(SchoolSystemException):
    """Service layer error."""
    pass


class FileOperationException(SchoolSystemException):
    """File operation error."""
    pass