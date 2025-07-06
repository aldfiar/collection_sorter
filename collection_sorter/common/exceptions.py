class CollectionSorterError(Exception):
    """Base exception for collection sorter errors."""

    def __init__(self, message: str, exit_code: int = 1):
        """
        Initialize exception with message and exit code.

        Args:
            message: Error message
            exit_code: Exit code to use when error terminates program
        """
        self.message = message
        self.exit_code = exit_code
        super().__init__(self.message)


class FileOperationError(CollectionSorterError):
    """Raised when file operations fail."""

    def __init__(self, message: str, path: str = None, exit_code: int = 2):
        """
        Initialize file operation error.

        Args:
            message: Error message
            path: File path that caused the error
            exit_code: Exit code to use when error terminates program
        """
        self.path = path
        file_info = f" [{path}]" if path else ""
        super().__init__(f"File operation error{file_info}: {message}", exit_code)


class ConfigurationError(CollectionSorterError):
    """Raised when configuration is invalid."""

    def __init__(self, message: str, param: str = None, exit_code: int = 3):
        """
        Initialize configuration error.

        Args:
            message: Error message
            param: Parameter that caused the error
            exit_code: Exit code to use when error terminates program
        """
        self.param = param
        param_info = f" parameter '{param}'" if param else ""
        super().__init__(f"Configuration error{param_info}: {message}", exit_code)


class ThreadingError(CollectionSorterError):
    """Raised when threading operations fail."""

    def __init__(self, message: str, thread_name: str = None, exit_code: int = 4):
        """
        Initialize threading error.

        Args:
            message: Error message
            thread_name: Name of the thread that caused the error
            exit_code: Exit code to use when error terminates program
        """
        self.thread_name = thread_name
        thread_info = f" in thread '{thread_name}'" if thread_name else ""
        super().__init__(f"Threading error{thread_info}: {message}", exit_code)


class ProcessingError(CollectionSorterError):
    """Raised when processing a collection fails."""

    def __init__(self, message: str, collection_type: str = None, exit_code: int = 5):
        """
        Initialize processing error.

        Args:
            message: Error message
            collection_type: Type of collection being processed
            exit_code: Exit code to use when error terminates program
        """
        self.collection_type = collection_type
        collection_info = f" for {collection_type}" if collection_type else ""
        super().__init__(f"Processing error{collection_info}: {message}", exit_code)


class ValidationError(CollectionSorterError):
    """Raised when input validation fails."""

    def __init__(self, message: str, field: str = None, exit_code: int = 6):
        """
        Initialize validation error.

        Args:
            message: Error message
            field: Field that failed validation
            exit_code: Exit code to use when error terminates program
        """
        self.field = field
        field_info = f" in '{field}'" if field else ""
        super().__init__(f"Validation error{field_info}: {message}", exit_code)


class UserInterruptError(CollectionSorterError):
    """Raised when user interrupts operation."""

    def __init__(
        self, message: str = "Operation interrupted by user", exit_code: int = 130
    ):
        """
        Initialize user interrupt error.

        Args:
            message: Error message
            exit_code: Exit code to use when error terminates program
        """
        super().__init__(message, exit_code)
