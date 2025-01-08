class CollectionSorterError(Exception):
    """Base exception for collection sorter errors."""
    pass

class FileOperationError(CollectionSorterError):
    """Raised when file operations fail."""
    pass

class ConfigurationError(CollectionSorterError):
    """Raised when configuration is invalid."""
    pass

class ThreadingError(CollectionSorterError):
    """Raised when threading operations fail."""
    pass
