"""
Rename processor implementation for Collection Sorter.

This module implements template classes for rename processing operations
with enhanced parameter validation.
"""

import logging
import re
from pathlib import Path
from typing import Any, Dict, List, Optional, Pattern, Set, Union

from collection_sorter.files import FilePath
from collection_sorter.files.duplicates import DuplicateHandler
from collection_sorter.result import ErrorType, OperationError, PathResult, Result
from collection_sorter.templates.processors.base import (
    BaseFileProcessor,
    BaseProcessorValidator,
    ValidationResult,
    Validator,
)

logger = logging.getLogger("processors.rename")


class PatternValidator(Validator):
    """Validator for rename pattern mappings."""

    def validate(self, value: Any) -> ValidationResult[Dict[str, str]]:
        """
        Validate rename patterns.

        Args:
            value: Patterns to validate (dict mapping regex to replacement)

        Returns:
            ValidationResult with validation status and patterns
        """
        if value is None:
            return ValidationResult.success({})

        if not isinstance(value, dict):
            return ValidationResult.failure(
                f"Patterns must be a dictionary, got {type(value)}"
            )

        patterns = {}
        errors = []

        for pattern, replacement in value.items():
            if not isinstance(pattern, str):
                errors.append(f"Pattern key must be a string, got {type(pattern)}")
                continue

            if not isinstance(replacement, str):
                errors.append(
                    f"Replacement for '{pattern}' must be a string, got {type(replacement)}"
                )
                continue

            # Try to compile the regex to validate it
            try:
                re.compile(pattern)
                patterns[pattern] = replacement
            except re.error as e:
                errors.append(f"Invalid regex pattern '{pattern}': {e}")

        if errors:
            return ValidationResult.failure(errors)

        return ValidationResult.success(patterns)


class RenameProcessorValidator(BaseProcessorValidator):
    """Validator for rename processor parameters."""

    def validate_parameters(
        self, **kwargs
    ) -> Result[Dict[str, Any], List[OperationError]]:
        """
        Validate rename processor parameters.

        Args:
            **kwargs: Parameters to validate

        Returns:
            Result with validated parameters or errors
        """
        # First, validate common parameters
        base_result = super().validate_parameters(**kwargs)
        if base_result.is_failure():
            return base_result

        validated = base_result.unwrap()
        errors = []

        # Validate rename-specific parameters
        # 1. Validate patterns
        patterns_result = self._validate_patterns(kwargs.get("patterns"))
        if not patterns_result:
            errors.append(
                OperationError(
                    type=ErrorType.VALIDATION_ERROR,
                    message=f"Invalid rename patterns: {'; '.join(patterns_result.errors)}",
                )
            )
        else:
            validated["patterns"] = patterns_result.value

        # 2. Validate recursive flag
        validated["recursive"] = bool(kwargs.get("recursive", True))

        # 3. Validate archive and move flags
        validated["archive"] = bool(kwargs.get("archive", False))
        validated["move_source"] = bool(kwargs.get("move_source", False))

        # 4. Check for conflicting options
        if validated.get("archive", False) and validated.get("move_source", False):
            logger.warning(
                "Both archive and move_source are set to True - files will be archived and sources removed"
            )

        # Return validation result
        if errors:
            return Result.failure(errors)
        return Result.success(validated)

    def _validate_patterns(self, patterns) -> ValidationResult[Dict[str, str]]:
        """
        Validate rename patterns.

        Args:
            patterns: Patterns to validate

        Returns:
            ValidationResult with validation status and patterns
        """
        validator = PatternValidator()
        return validator.validate(patterns)


class RenameProcessorTemplate(BaseFileProcessor):
    """Template implementation for renaming files according to patterns with enhanced validation."""

    def __init__(
        self,
        source_path: Union[str, Path, FilePath],
        destination_path: Optional[Union[str, Path, FilePath]] = None,
        patterns: Optional[Dict[str, str]] = None,
        recursive: bool = True,
        archive: bool = False,
        move_source: bool = False,
        dry_run: bool = False,
        interactive: bool = False,
        duplicate_handler: Optional[DuplicateHandler] = None,
    ):
        """
        Initialize the rename processor template with validation.

        Args:
            source_path: Source path to process
            destination_path: Optional destination path
            patterns: Mapping of file patterns to renaming rules
            recursive: Whether to process subdirectories
            archive: Whether to create archives of renamed files
            move_source: Whether to remove source files after processing
            dry_run: Whether to simulate operations
            interactive: Whether to prompt for confirmation
            duplicate_handler: Optional handler for duplicates
        """
        # Create rename-specific validator
        validator = RenameProcessorValidator()

        # Initialize base processor with validator
        super().__init__(
            source_path=source_path,
            destination_path=destination_path,
            dry_run=dry_run,
            interactive=interactive,
            duplicate_handler=duplicate_handler,
            validator=validator,
        )

        # Validate and store rename-specific parameters
        validation_result = validator.validate_parameters(
            source_path=source_path,
            destination_path=destination_path,
            patterns=patterns,
            recursive=recursive,
            archive=archive,
            move_source=move_source,
            dry_run=dry_run,
            interactive=interactive,
            duplicate_handler=duplicate_handler,
        )

        if validation_result.is_success():
            validated = validation_result.unwrap()
            self.patterns = validated["patterns"]
            self.recursive = validated["recursive"]
            self.archive = validated["archive"]
            self.move_source = validated["move_source"]
        else:
            # Use defaults if validation failed (errors already logged)
            self.patterns = {}
            self.recursive = recursive
            self.archive = archive
            self.move_source = move_source

        # Pre-compile patterns for performance
        self.compiled_patterns = {}
        for pattern, replacement in self.patterns.items():
            try:
                self.compiled_patterns[re.compile(pattern)] = replacement
            except re.error as e:
                logger.error(f"Failed to compile pattern '{pattern}': {e}")

        # Extend stats for rename-specific metrics
        self.stats.update({"renamed": 0})

    def _execute_implementation(self) -> Result[Dict[str, Any], List[OperationError]]:
        """
        Execute the rename operation with validation.

        Returns:
            Result with statistics or errors
        """
        try:
            source_paths = []

            # If source is a directory, collect all files
            if self.source_path.is_directory:
                # Process files in the directory
                source_paths = self._collect_files(self.source_path, self.recursive)
            else:
                # Process a single file
                source_paths = [self.source_path]

            # Validate that we have files to process
            if not source_paths:
                logger.info(f"No files found to process in {self.source_path}")
                return Result.success(self.stats)

            # Use destination if provided, otherwise use source directory
            destination = (
                self.destination_path
                if self.destination_path
                else self.source_path.parent
            )

            # Process the files
            processed_result = self.process_batch(source_paths, destination)

            if processed_result.is_failure():
                return Result.failure(processed_result.unwrap_error())

            return Result.success(self.stats)

        except Exception as e:
            error = OperationError(
                type=ErrorType.OPERATION_FAILED,
                message=f"Rename operation failed: {str(e)}",
                path=str(self.source_path),
                source_exception=e,
            )
            return Result.failure([error])

    def _process_batch_item(
        self, source: FilePath, destination: FilePath, **kwargs
    ) -> PathResult:
        """
        Process a single file by applying rename patterns.

        Args:
            source: Source file path
            destination: Destination directory path
            **kwargs: Additional arguments

        Returns:
            Result with processed file path or error
        """
        try:
            self.stats["processed"] += 1

            # Determine if this file matches any patterns
            matched = False
            new_name = source.name

            # Use compiled patterns for better performance
            for pattern, replacement in self.compiled_patterns.items():
                if pattern.search(source.name):
                    # Apply the pattern
                    new_name = pattern.sub(replacement, source.name)
                    matched = True
                    break

            if not matched:
                # No pattern matched, use default file cleaning
                new_name = self._clean_filename(source.name)

            # Check if the name changed
            if new_name == source.name:
                # No change needed
                return Result.success(source)

            # Determine destination path
            if self.destination_path:
                # Use provided destination
                new_path = destination.join(new_name)
            else:
                # Use same directory as source
                new_path = source.parent.join(new_name)

            # Handle the file based on options
            if self.dry_run:
                logger.info(f"Would rename {source} to {new_path}")
                self.stats["renamed"] += 1
                return Result.success(new_path)

            # Check for duplicates
            if new_path.exists and self.duplicate_handler:
                try:
                    final_path, is_duplicate = self.duplicate_handler.handle_duplicate(
                        source.path, new_path.path, context=f"Renaming {source}"
                    )
                    new_path = FilePath(final_path, must_exist=False)
                except Exception as e:
                    error = OperationError(
                        type=ErrorType.OPERATION_FAILED,
                        message=f"Duplicate handling failed: {str(e)}",
                        path=str(source),
                        source_exception=e,
                    )
                    self.stats["errors"] += 1
                    return Result.failure(error)

            # Rename the file
            try:
                if self.move_source:
                    source.move_to(new_path)
                else:
                    source.copy_to(new_path)

                logger.info(f"Renamed {source} to {new_path}")
                self.stats["renamed"] += 1
                return Result.success(new_path)

            except Exception as e:
                error = OperationError(
                    type=ErrorType.OPERATION_FAILED,
                    message=f"Failed to rename {source} to {new_path}: {str(e)}",
                    path=str(source),
                    source_exception=e,
                )
                self.stats["errors"] += 1
                return Result.failure(error)

        except Exception as e:
            error = OperationError(
                type=ErrorType.OPERATION_FAILED,
                message=f"Failed to process {source}: {str(e)}",
                path=str(source),
                source_exception=e,
            )
            self.stats["errors"] += 1
            return Result.failure(error)

    def _clean_filename(self, filename: str) -> str:
        """
        Clean a filename by removing unwanted patterns.

        Args:
            filename: Original filename

        Returns:
            Cleaned filename
        """
        # Remove extension temporarily
        name_parts = filename.rsplit(".", 1)
        name = name_parts[0]
        extension = name_parts[1] if len(name_parts) > 1 else ""

        # Remove content in brackets and dates
        name = re.sub(r"\[[^\]]*\]", "", name)  # Remove [content]
        name = re.sub(r"\([0-9]{4}\)", "", name)  # Remove (YYYY)
        name = re.sub(r"_+", "_", name)  # Replace multiple underscores
        name = name.strip("_").strip()  # Remove leading/trailing underscores and spaces

        # Preserve existing hyphens between words and standardize spacing
        name = re.sub(
            r"(\w)-(\w)", r"\1 - \2", name
        )  # Add spaces around hyphens between words
        name = re.sub(
            r"\s*-\s*", " - ", name
        )  # Standardize spacing around existing hyphens

        # Reconstruct filename with extension
        return f"{name}.{extension}" if extension else name
