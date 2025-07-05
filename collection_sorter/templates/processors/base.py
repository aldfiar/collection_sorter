"""
Base processor functionality for Collection Sorter with enhanced validation.

This module provides common base functionality and validation framework used 
across specialized processors.
"""

import logging
import os
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Any, Dict, List, Optional, Set, Tuple, Union, TypeVar, Generic

from collection_sorter.files import FilePath
from collection_sorter.files.duplicates import DuplicateHandler
from collection_sorter.result import Result, PathResult, OperationError, ErrorType
from collection_sorter.templates.templates import BatchProcessorTemplate

logger = logging.getLogger("processors.base")

T = TypeVar('T')  # For generic type handling in validation results

class ValidationResult(Generic[T]):
    """Result of a validation operation with success/failure status and payload."""
    
    def __init__(self, is_valid: bool, errors: List[str] = None, value: T = None):
        """
        Initialize the validation result.
        
        Args:
            is_valid: Whether the validation succeeded
            errors: List of error messages if validation failed
            value: The validated and possibly transformed value
        """
        self.is_valid = is_valid
        self.errors = errors or []
        self.value = value
    
    @classmethod
    def success(cls, value: T = None) -> 'ValidationResult[T]':
        """Create a successful validation result."""
        return cls(True, [], value)
    
    @classmethod
    def failure(cls, errors: Union[str, List[str]]) -> 'ValidationResult[T]':
        """Create a failed validation result."""
        if isinstance(errors, str):
            errors = [errors]
        return cls(False, errors)
    
    def __bool__(self) -> bool:
        """Allow using ValidationResult in boolean context."""
        return self.is_valid


class Validator(ABC):
    """Abstract base class for parameter validators."""
    
    @abstractmethod
    def validate(self, value: Any) -> ValidationResult:
        """
        Validate a value.
        
        Args:
            value: The value to validate
            
        Returns:
            ValidationResult with validation status and errors
        """
        pass


class PathValidator(Validator):
    """Validator for file path parameters."""
    
    def __init__(
        self, 
        must_exist: bool = True, 
        must_be_dir: bool = False,
        must_be_file: bool = False,
        create_if_missing: bool = False
    ):
        """
        Initialize the path validator.
        
        Args:
            must_exist: Whether the path must exist
            must_be_dir: Whether the path must be a directory
            must_be_file: Whether the path must be a file
            create_if_missing: Whether to create the path if it doesn't exist
        """
        self.must_exist = must_exist
        self.must_be_dir = must_be_dir
        self.must_be_file = must_be_file
        self.create_if_missing = create_if_missing
    
    def validate(self, value: Any) -> ValidationResult[FilePath]:
        """
        Validate a path.
        
        Args:
            value: The path to validate
            
        Returns:
            ValidationResult with validation status and FilePath
        """
        try:
            # Convert to FilePath
            file_path = FilePath(value, must_exist=False)
            errors = []
            
            # Check if path exists
            if self.must_exist and not file_path.exists:
                if self.create_if_missing:
                    try:
                        if self.must_be_dir:
                            file_path.path.mkdir(parents=True, exist_ok=True)
                        else:
                            file_path.parent.path.mkdir(parents=True, exist_ok=True)
                            if not file_path.exists:
                                with open(file_path.path, 'w') as f:
                                    pass
                    except Exception as e:
                        errors.append(f"Failed to create path {file_path}: {e}")
                else:
                    errors.append(f"Path does not exist: {file_path}")
            
            # Check if path is directory or file
            if file_path.exists:
                if self.must_be_dir and not file_path.is_directory:
                    errors.append(f"Path is not a directory: {file_path}")
                elif self.must_be_file and not file_path.is_file:
                    errors.append(f"Path is not a file: {file_path}")
            
            if errors:
                return ValidationResult.failure(errors)
            return ValidationResult.success(file_path)
            
        except Exception as e:
            return ValidationResult.failure(f"Invalid path {value}: {str(e)}")


class ExtensionsValidator(Validator):
    """Validator for file extensions."""
    
    def __init__(self, valid_extensions: Optional[Set[str]] = None):
        """
        Initialize the extensions validator.
        
        Args:
            valid_extensions: Set of valid file extensions
        """
        self.valid_extensions = valid_extensions or set()
    
    def validate(self, value: Any) -> ValidationResult[Set[str]]:
        """
        Validate file extensions.
        
        Args:
            value: Extensions to validate (string, list, or set)
            
        Returns:
            ValidationResult with normalized set of extensions
        """
        try:
            extensions = set()
            
            if isinstance(value, str):
                # Single extension as string
                extensions.add(value if value.startswith('.') else f'.{value}')
            elif isinstance(value, (list, tuple, set)):
                # Collection of extensions
                for ext in value:
                    if not isinstance(ext, str):
                        return ValidationResult.failure(f"Invalid extension type: {type(ext)}")
                    extensions.add(ext if ext.startswith('.') else f'.{ext}')
            else:
                return ValidationResult.failure(f"Invalid extensions type: {type(value)}")
            
            # Validate against allowed extensions if provided
            if self.valid_extensions and not extensions.issubset(self.valid_extensions):
                invalid = extensions - self.valid_extensions
                return ValidationResult.failure(f"Invalid extensions: {', '.join(invalid)}")
            
            return ValidationResult.success(extensions)
            
        except Exception as e:
            return ValidationResult.failure(f"Invalid extensions {value}: {str(e)}")


class BaseProcessorValidator:
    """Base class for processor parameter validation."""
    
    def validate_parameters(self, **kwargs) -> Result[Dict[str, Any], List[OperationError]]:
        """
        Validate processor parameters.
        
        Args:
            **kwargs: Parameters to validate
            
        Returns:
            Result with validated parameters or errors
        """
        errors = []
        validated = {}
        
        # Validate common parameters
        source_result = self._validate_source(kwargs.get('source_path'))
        if not source_result:
            errors.append(OperationError(
                type=ErrorType.VALIDATION_ERROR,
                message=f"Invalid source path: {'; '.join(source_result.errors)}",
                path=str(kwargs.get('source_path', ''))
            ))
        else:
            validated['source_path'] = source_result.value
        
        # Validate destination if provided
        if 'destination_path' in kwargs:
            dest_result = self._validate_destination(kwargs.get('destination_path'))
            if not dest_result:
                errors.append(OperationError(
                    type=ErrorType.VALIDATION_ERROR,
                    message=f"Invalid destination path: {'; '.join(dest_result.errors)}",
                    path=str(kwargs.get('destination_path', ''))
                ))
            else:
                validated['destination_path'] = dest_result.value
        
        # Validate duplicate handler if provided
        if 'duplicate_handler' in kwargs:
            dup_result = self._validate_duplicate_handler(kwargs.get('duplicate_handler'))
            if not dup_result:
                errors.append(OperationError(
                    type=ErrorType.VALIDATION_ERROR,
                    message=f"Invalid duplicate handler: {'; '.join(dup_result.errors)}"
                ))
            else:
                validated['duplicate_handler'] = dup_result.value
        
        # Add other common parameters
        validated.update({
            'dry_run': bool(kwargs.get('dry_run', False)),
            'interactive': bool(kwargs.get('interactive', False)),
        })
        
        # Return validation result
        if errors:
            return Result.failure(errors)
        return Result.success(validated)
    
    def _validate_source(self, source_path) -> ValidationResult[FilePath]:
        """
        Validate source path.
        
        Args:
            source_path: Source path to validate
            
        Returns:
            ValidationResult with validation status and FilePath
        """
        validator = PathValidator(must_exist=True)
        return validator.validate(source_path)
    
    def _validate_destination(self, destination_path) -> ValidationResult[FilePath]:
        """
        Validate destination path.
        
        Args:
            destination_path: Destination path to validate
            
        Returns:
            ValidationResult with validation status and FilePath
        """
        # Allow None destination paths
        if destination_path is None:
            return ValidationResult.success(None)
            
        validator = PathValidator(must_exist=False, create_if_missing=True, must_be_dir=True)
        return validator.validate(destination_path)
    
    def _validate_duplicate_handler(self, duplicate_handler) -> ValidationResult[DuplicateHandler]:
        """
        Validate duplicate handler.
        
        Args:
            duplicate_handler: Duplicate handler to validate
            
        Returns:
            ValidationResult with validation status and DuplicateHandler
        """
        if duplicate_handler is None:
            return ValidationResult.success(None)
        if not isinstance(duplicate_handler, DuplicateHandler):
            return ValidationResult.failure("Duplicate handler must be an instance of DuplicateHandler")
        return ValidationResult.success(duplicate_handler)


class BaseFileProcessor(BatchProcessorTemplate):
    """Base class for file processing templates with common functionality and validation."""
    
    def __init__(
        self,
        source_path: Union[str, Path, FilePath],
        destination_path: Optional[Union[str, Path, FilePath]] = None,
        dry_run: bool = False,
        interactive: bool = False,
        duplicate_handler: Optional[DuplicateHandler] = None,
        validator: Optional[BaseProcessorValidator] = None
    ):
        """
        Initialize the base file processor.
        
        Args:
            source_path: Source path to process
            destination_path: Optional destination path
            dry_run: Whether to simulate operations
            interactive: Whether to prompt for confirmation
            duplicate_handler: Optional handler for duplicates
            validator: Optional parameter validator
        """
        super().__init__(
            file_processor=None,
            directory_processor=None,
            dry_run=dry_run,
            duplicate_handler=duplicate_handler,
            continue_on_error=True
        )
        
        # Set up validator
        self.validator = validator or BaseProcessorValidator()
        
        # Validate parameters
        validation_result = self.validator.validate_parameters(
            source_path=source_path,
            destination_path=destination_path,
            dry_run=dry_run,
            interactive=interactive,
            duplicate_handler=duplicate_handler
        )
        
        # If validation failed, log errors but continue (will be handled in execute)
        if validation_result.is_failure():
            self.validation_errors = validation_result.error()
            logger.error(f"Validation errors: {self.validation_errors}")
            # Set default values
            self.source_path = FilePath(source_path) if source_path else None
            self.destination_path = FilePath(destination_path) if destination_path else None
        else:
            # Use validated parameters
            validated = validation_result.unwrap()
            self.source_path = validated['source_path']
            self.destination_path = validated.get('destination_path')
            self.validation_errors = []
        
        self.interactive = interactive
        self.stats = {
            "processed": 0,
            "errors": 0
        }
    
    def execute(self) -> Result[Dict[str, Any], List[OperationError]]:
        """
        Execute the processing operation with validation.
        
        Returns:
            Result with statistics or errors
        """
        # If there were validation errors, return them immediately
        if hasattr(self, 'validation_errors') and self.validation_errors:
            return Result.failure(self.validation_errors)
            
        try:
            # Implementation specific execution logic
            return self._execute_implementation()
        except Exception as e:
            error = OperationError(
                type=ErrorType.OPERATION_FAILED,
                message=f"Processing failed: {str(e)}",
                path=str(self.source_path),
                source_exception=e
            )
            return Result.failure([error])
    
    @abstractmethod
    def _execute_implementation(self) -> Result[Dict[str, Any], List[OperationError]]:
        """
        Implement processor-specific execution logic.
        
        This abstract method must be implemented by subclasses.
        
        Returns:
            Result with statistics or errors
        """
        pass
    
    def _collect_files(self, directory: FilePath, recursive: bool = True) -> List[FilePath]:
        """
        Collect files to process from a directory.
        
        Args:
            directory: Directory to collect files from
            recursive: Whether to collect files from subdirectories
            
        Returns:
            List of file paths to process
        """
        files = []
        
        try:
            # Get all files in the directory
            for path in directory.path.iterdir():
                if path.is_file():
                    files.append(FilePath(path))
                elif path.is_dir() and recursive:
                    # Recursively collect files from subdirectories
                    files.extend(self._collect_files(FilePath(path), recursive))
                    
            return files
            
        except Exception as e:
            logger.error(f"Failed to collect files from {directory}: {e}")
            return []