"""
Result pattern implementation for Collection Sorter.

This module implements the Result/Either pattern for more functional error handling,
reducing reliance on exceptions and providing better composability of operations.
"""

from __future__ import annotations

import functools
import traceback
from abc import ABC, abstractmethod
from dataclasses import dataclass
from enum import Enum, auto
from pathlib import Path
from typing import Any, Callable, Dict, Generic, List, Optional, TypeVar, Union, cast

T = TypeVar('T')  # Success type
E = TypeVar('E')  # Error type
U = TypeVar('U')  # New success type for mapping


class ResultError(Exception):
    """Exception raised for Result pattern errors."""
    pass


class Result(Generic[T, E], ABC):
    """
    Base class for the Result pattern.
    
    This represents either a successful operation with a value of type T,
    or a failed operation with an error of type E.
    """
    
    @abstractmethod
    def is_success(self) -> bool:
        """Check if this result is a success."""
        pass
    
    @abstractmethod
    def is_failure(self) -> bool:
        """Check if this result is a failure."""
        pass
    
    @abstractmethod
    def unwrap(self) -> T:
        """
        Get the success value if successful.
        
        Raises:
            ResultError: If this is a failure result
        """
        pass
    
    @abstractmethod
    def unwrap_or(self, default: T) -> T:
        """
        Get the success value or a default if failed.
        
        Args:
            default: Default value to return if this is a failure
            
        Returns:
            Success value or default
        """
        pass
    
    @abstractmethod
    def unwrap_or_else(self, func: Callable[[E], T]) -> T:
        """
        Get the success value or compute a default if failed.
        
        Args:
            func: Function to compute a default value from the error
            
        Returns:
            Success value or computed default
        """
        pass
    
    @abstractmethod
    def map(self, func: Callable[[T], U]) -> Result[U, E]:
        """
        Apply a function to the success value.
        
        Args:
            func: Function to apply to the success value
            
        Returns:
            New result with the mapped success value
        """
        pass
    
    @abstractmethod
    def map_error(self, func: Callable[[E], U]) -> Result[T, U]:
        """
        Apply a function to the error value.
        
        Args:
            func: Function to apply to the error value
            
        Returns:
            New result with the mapped error value
        """
        pass
    
    @abstractmethod
    def and_then(self, func: Callable[[T], Result[U, E]]) -> Result[U, E]:
        """
        Chain a function that returns a result.
        
        Args:
            func: Function to apply to the success value
            
        Returns:
            Result of the chained function or the original failure
        """
        pass
    
    @abstractmethod
    def or_else(self, func: Callable[[E], Result[T, U]]) -> Result[T, U]:
        """
        Chain a function on the error value.
        
        Args:
            func: Function to apply to the error value
            
        Returns:
            Result of the chained function or the original success
        """
        pass
    
    @abstractmethod
    def error(self) -> E:
        """
        Get the error value if failed.
        
        Raises:
            ResultError: If this is a success result
        """
        pass
    
    @staticmethod
    def success(value: T) -> Result[T, Any]:
        """
        Create a success result.
        
        Args:
            value: Success value
            
        Returns:
            Success result
        """
        return Success(value)
    
    @staticmethod
    def failure(error: E) -> Result[Any, E]:
        """
        Create a failure result.
        
        Args:
            error: Error value
            
        Returns:
            Failure result
        """
        return Failure(error)
    
    @staticmethod
    def from_exception(
        func: Callable[..., T], 
        *args, 
        **kwargs
    ) -> Result[T, Exception]:
        """
        Execute a function and return its result wrapped in a Result.
        
        Args:
            func: Function to execute
            *args: Positional arguments for the function
            **kwargs: Keyword arguments for the function
            
        Returns:
            Success result with the function result or failure with the exception
        """
        try:
            return Result.success(func(*args, **kwargs))
        except Exception as e:
            return Result.failure(e)
    
    @staticmethod
    def collect(results: List[Result[T, E]]) -> Result[List[T], List[E]]:
        """
        Collect a list of results into a single result.
        
        Args:
            results: List of results to collect
            
        Returns:
            Success with list of success values if all results are success,
            or failure with list of error values otherwise
        """
        success_values = []
        error_values = []
        
        for result in results:
            if result.is_success():
                success_values.append(result.unwrap())
            else:
                error_values.append(result.error())
        
        if error_values:
            return Result.failure(error_values)
        else:
            return Result.success(success_values)


class Success(Result[T, Any]):
    """Success variant of Result, containing a value."""
    
    def __init__(self, value: T):
        """
        Initialize a success result.
        
        Args:
            value: Success value
        """
        self._value = value
    
    def is_success(self) -> bool:
        """Check if this result is a success."""
        return True
    
    def is_failure(self) -> bool:
        """Check if this result is a failure."""
        return False
    
    def unwrap(self) -> T:
        """Get the success value."""
        return self._value
    
    def unwrap_or(self, default: T) -> T:
        """Get the success value or a default if failed."""
        return self._value
    
    def unwrap_or_else(self, func: Callable[[Any], T]) -> T:
        """Get the success value or compute a default if failed."""
        return self._value
    
    def map(self, func: Callable[[T], U]) -> Result[U, Any]:
        """
        Apply a function to the success value.
        
        Args:
            func: Function to apply to the success value
            
        Returns:
            New result with the mapped success value
        """
        try:
            return Success(func(self._value))
        except Exception as e:
            return Failure(e)
    
    def map_error(self, func: Callable[[Any], U]) -> Result[T, U]:
        """
        Apply a function to the error value.
        
        Args:
            func: Function to apply to the error value
            
        Returns:
            This result unchanged
        """
        return cast(Result[T, U], self)
    
    def and_then(self, func: Callable[[T], Result[U, Any]]) -> Result[U, Any]:
        """
        Chain a function that returns a result.
        
        Args:
            func: Function to apply to the success value
            
        Returns:
            Result of the chained function
        """
        try:
            return func(self._value)
        except Exception as e:
            return Failure(e)
    
    def or_else(self, func: Callable[[Any], Result[T, U]]) -> Result[T, U]:
        """
        Chain a function on the error value.
        
        Args:
            func: Function to apply to the error value
            
        Returns:
            This result unchanged
        """
        return cast(Result[T, U], self)
    
    def error(self) -> Any:
        """
        Get the error value if failed.
        
        Raises:
            ResultError: Always, since this is a success result
        """
        raise ResultError("Cannot get error from success result")
    
    def __str__(self) -> str:
        """Get string representation."""
        return f"Success({self._value})"
    
    def __repr__(self) -> str:
        """Get debug representation."""
        return f"Success({repr(self._value)})"


class Failure(Result[Any, E]):
    """Failure variant of Result, containing an error."""
    
    def __init__(self, error: E):
        """
        Initialize a failure result.
        
        Args:
            error: Error value
        """
        self._error = error
    
    def is_success(self) -> bool:
        """Check if this result is a success."""
        return False
    
    def is_failure(self) -> bool:
        """Check if this result is a failure."""
        return True
    
    def unwrap(self) -> Any:
        """
        Get the success value if successful.
        
        Raises:
            ResultError: Always, since this is a failure result
        """
        if isinstance(self._error, Exception):
            raise ResultError(f"Unwrapped failure result: {self._error}") from self._error
        else:
            raise ResultError(f"Unwrapped failure result: {self._error}")
    
    def unwrap_or(self, default: T) -> T:
        """
        Get the success value or a default if failed.
        
        Args:
            default: Default value to return
            
        Returns:
            Default value
        """
        return default
    
    def unwrap_or_else(self, func: Callable[[E], T]) -> T:
        """
        Get the success value or compute a default if failed.
        
        Args:
            func: Function to compute a default value from the error
            
        Returns:
            Computed default value
        """
        return func(self._error)
    
    def map(self, func: Callable[[Any], U]) -> Result[U, E]:
        """
        Apply a function to the success value.
        
        Args:
            func: Function to apply to the success value
            
        Returns:
            This result unchanged
        """
        return cast(Result[U, E], self)
    
    def map_error(self, func: Callable[[E], U]) -> Result[Any, U]:
        """
        Apply a function to the error value.
        
        Args:
            func: Function to apply to the error value
            
        Returns:
            New result with the mapped error value
        """
        try:
            return Failure(func(self._error))
        except Exception as e:
            return Failure(e)
    
    def and_then(self, func: Callable[[Any], Result[U, E]]) -> Result[U, E]:
        """
        Chain a function that returns a result.
        
        Args:
            func: Function to apply to the success value
            
        Returns:
            This result unchanged
        """
        return cast(Result[U, E], self)
    
    def or_else(self, func: Callable[[E], Result[T, U]]) -> Result[T, U]:
        """
        Chain a function on the error value.
        
        Args:
            func: Function to apply to the error value
            
        Returns:
            Result of the chained function
        """
        try:
            return func(self._error)
        except Exception as e:
            return Failure(e)
    
    def error(self) -> E:
        """Get the error value."""
        return self._error
    
    def __str__(self) -> str:
        """Get string representation."""
        return f"Failure({self._error})"
    
    def __repr__(self) -> str:
        """Get debug representation."""
        return f"Failure({repr(self._error)})"


class ErrorType(Enum):
    """Types of errors that can occur in file operations."""
    
    FILE_NOT_FOUND = auto()
    PERMISSION_DENIED = auto()
    ALREADY_EXISTS = auto()
    IO_ERROR = auto()
    INVALID_PATH = auto()
    OPERATION_FAILED = auto()
    USER_CANCELLED = auto()
    VALIDATION_ERROR = auto()
    UNKNOWN = auto()


@dataclass
class OperationError:
    """
    Structured error information for file operations.
    
    This provides more context than just an exception or message.
    """
    
    type: ErrorType
    message: str
    path: Optional[Union[str, Path]] = None
    source_exception: Optional[Exception] = None
    details: Optional[Dict[str, Any]] = None
    
    def __str__(self) -> str:
        """Get string representation."""
        result = f"{self.type.name}: {self.message}"
        if self.path:
            result += f" (path: {self.path})"
        return result
    
    @staticmethod
    def from_exception(exception: Exception, path: Optional[Union[str, Path]] = None) -> 'OperationError':
        """
        Create an operation error from an exception.
        
        Args:
            exception: Source exception
            path: Optional path related to the error
            
        Returns:
            Structured operation error
        """
        # Determine error type from exception
        import errno

        if isinstance(exception, FileNotFoundError):
            error_type = ErrorType.FILE_NOT_FOUND
        elif isinstance(exception, PermissionError):
            error_type = ErrorType.PERMISSION_DENIED
        elif isinstance(exception, FileExistsError):
            error_type = ErrorType.ALREADY_EXISTS
        elif isinstance(exception, IsADirectoryError) or isinstance(exception, NotADirectoryError):
            error_type = ErrorType.INVALID_PATH
        elif isinstance(exception, OSError):
            # More specific OSError cases
            if exception.errno == errno.ENOENT:
                error_type = ErrorType.FILE_NOT_FOUND
            elif exception.errno == errno.EACCES:
                error_type = ErrorType.PERMISSION_DENIED
            elif exception.errno == errno.EEXIST:
                error_type = ErrorType.ALREADY_EXISTS
            else:
                error_type = ErrorType.IO_ERROR
        elif hasattr(exception, 'errno') and getattr(exception, 'errno') is not None:
            # Handle errno attribute if available
            errno_value = getattr(exception, 'errno')
            if errno_value == errno.ENOENT:
                error_type = ErrorType.FILE_NOT_FOUND
            elif errno_value == errno.EACCES:
                error_type = ErrorType.PERMISSION_DENIED
            elif errno_value == errno.EEXIST:
                error_type = ErrorType.ALREADY_EXISTS
            else:
                error_type = ErrorType.IO_ERROR
        elif isinstance(exception, ValueError) or isinstance(exception, TypeError):
            error_type = ErrorType.VALIDATION_ERROR
        elif isinstance(exception, KeyboardInterrupt) or isinstance(exception, EOFError):
            error_type = ErrorType.USER_CANCELLED
        else:
            # Default case
            error_type = ErrorType.UNKNOWN
            
        return OperationError(
            type=error_type,
            message=str(exception),
            path=path,
            source_exception=exception,
            details={
                "traceback": traceback.format_exc(),
                "exception_type": type(exception).__name__
            }
        )


# Type aliases for common result types
PathResult = Result[Path, OperationError]
FilesResult = Result[List[Path], OperationError]
BoolResult = Result[bool, OperationError]
StringResult = Result[str, OperationError]


def result_handler(func: Callable[..., T]) -> Callable[..., Result[T, OperationError]]:
    """
    Decorator that wraps a function's result in a Result object.
    
    This decorator catches exceptions and returns them as Failure results.
    
    Args:
        func: Function to wrap
        
    Returns:
        Wrapped function that returns a Result
    """
    @functools.wraps(func)
    def wrapper(*args, **kwargs) -> Result[T, OperationError]:
        try:
            return Result.success(func(*args, **kwargs))
        except Exception as e:
            # Try to extract path information from the arguments
            path = None
            for arg in args:
                if isinstance(arg, (str, Path)):
                    path = arg
                    break
            
            if path is None:
                # Check kwargs for path-like arguments
                for param_name in ['path', 'file_path', 'source', 'destination']:
                    if param_name in kwargs and isinstance(kwargs[param_name], (str, Path)):
                        path = kwargs[param_name]
                        break
            
            return Result.failure(OperationError.from_exception(e, path))
    
    return wrapper