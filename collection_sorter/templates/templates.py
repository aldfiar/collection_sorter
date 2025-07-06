"""
Template Method Pattern implementation for file processing in Collection Sorter.

This module implements the Template Method pattern for file processing,
defining skeleton algorithms with customizable steps.
"""

import logging
import os
import shutil
from abc import ABC, abstractmethod
from datetime import datetime
from pathlib import Path
from typing import List, Optional, Union

from collection_sorter.files import FilePath
from collection_sorter.files.duplicates import DuplicateHandler, DuplicateStrategy
from collection_sorter.result import (
    ErrorType,
    OperationError,
    PathResult,
    Result,
    result_handler,
)

logger = logging.getLogger("templates")


class FileProcessorTemplate(ABC):
    """
    Abstract base class for file processors using the Template Method pattern.

    This class defines skeleton algorithms for file processing,
    with customizable steps for different operations.
    """

    def __init__(
        self,
        dry_run: bool = False,
        duplicate_handler: Optional[DuplicateHandler] = None,
    ):
        """
        Initialize the file processor template.

        Args:
            dry_run: Whether to simulate operations without making changes
            duplicate_handler: Optional handler for duplicates
        """
        self.dry_run = dry_run
        self.duplicate_handler = duplicate_handler

    def process_file(
        self,
        source: Union[str, Path, FilePath],
        destination: Union[str, Path, FilePath],
        **kwargs,
    ) -> PathResult:
        """
        Process a file (Template Method).

        This is the main template method defining the skeleton algorithm
        for file processing operations.

        Args:
            source: Source file path
            destination: Destination path
            **kwargs: Additional operation-specific arguments

        Returns:
            Result with path to the processed file or error
        """
        # The template method defines the skeleton of the algorithm
        try:
            # Step 1: Validate input paths
            source_path_result = self._validate_source(source)
            if source_path_result.is_failure():
                return source_path_result

            source_path = source_path_result.unwrap()

            # Step 2: Prepare destination path
            destination_path_result = self._prepare_destination(destination)
            if destination_path_result.is_failure():
                return destination_path_result

            destination_path = destination_path_result.unwrap()

            # Step 3: Handle duplicates if needed
            final_destination_result = self._handle_duplicates(
                source_path, destination_path
            )
            if final_destination_result.is_failure():
                return final_destination_result

            final_destination = final_destination_result.unwrap()

            # Step 4: Execute the operation (to be implemented by subclasses)
            operation_result = self._execute_operation(
                source_path, final_destination, **kwargs
            )
            if operation_result.is_failure():
                return operation_result

            processed_path = operation_result.unwrap()

            # Step 5: Perform post-processing (optional)
            post_result = self._post_process(source_path, processed_path, **kwargs)
            if post_result.is_failure():
                return post_result

            # Return the final processed path
            return Result.success(processed_path)

        except Exception as e:
            # Convert any unhandled exceptions to OperationError
            error = OperationError(
                type=ErrorType.OPERATION_FAILED,
                message=f"File processing failed: {str(e)}",
                path=str(source),
                source_exception=e,
            )
            return Result.failure(error)

    @result_handler
    def _validate_source(self, source: Union[str, Path, FilePath]) -> FilePath:
        """
        Validate the source path.

        Args:
            source: Source path to validate

        Returns:
            Validated source path

        Raises:
            FileNotFoundError: If source doesn't exist
            ValueError: If source is invalid
        """
        # Convert to FilePath and validate
        source_path = FilePath(source)

        # Additional validation logic can be added here
        if not source_path.exists:
            raise FileNotFoundError(f"Source path does not exist: {source_path}")

        return source_path

    @result_handler
    def _prepare_destination(self, destination: Union[str, Path, FilePath]) -> FilePath:
        """
        Prepare the destination path.

        Args:
            destination: Destination path to prepare

        Returns:
            Prepared destination path

        Raises:
            ValueError: If destination is invalid
        """
        # Convert to FilePath with must_exist=False
        destination_path = FilePath(destination, must_exist=False)

        # Make sure the parent directory exists
        if not destination_path.parent.exists:
            if not self.dry_run:
                destination_path.parent.path.mkdir(parents=True, exist_ok=True)
            else:
                logger.info(f"Would create directory: {destination_path.parent}")

        return destination_path

    def _handle_duplicates(
        self, source_path: FilePath, destination_path: FilePath
    ) -> PathResult:
        """
        Handle duplicate files.

        Args:
            source_path: Source file path
            destination_path: Destination file path

        Returns:
            Result with final destination path or error
        """
        # If destination doesn't exist, no need to handle duplicates
        if not destination_path.exists:
            return Result.success(destination_path)

        # Check if source and destination are the same file
        if source_path == destination_path:
            error = OperationError(
                type=ErrorType.ALREADY_EXISTS,
                message="Source and destination are the same file",
                path=str(destination_path),
            )
            return Result.failure(error)

        # If we have a duplicate handler, use it
        if self.duplicate_handler:
            try:
                final_path, is_duplicate = self.duplicate_handler.handle_duplicate(
                    destination_path.path,
                    destination_path.path,
                    context=f"Processing {source_path}",
                )

                # If the strategy is SKIP, return early
                if (
                    is_duplicate
                    and self.duplicate_handler.strategy == DuplicateStrategy.SKIP
                ):
                    logger.info(f"Skipping duplicate file: {source_path}")
                    return Result.success(destination_path)

                return Result.success(FilePath(final_path, must_exist=False))

            except Exception as e:
                error = OperationError(
                    type=ErrorType.OPERATION_FAILED,
                    message=f"Duplicate handling failed: {str(e)}",
                    path=str(destination_path),
                    source_exception=e,
                )
                return Result.failure(error)
        else:
            # Default behavior - rename the destination with timestamp
            try:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                new_name = (
                    f"{destination_path.stem}_{timestamp}{destination_path.suffix}"
                )
                new_path = destination_path.parent.join(new_name)

                return Result.success(new_path)

            except Exception as e:
                error = OperationError(
                    type=ErrorType.OPERATION_FAILED,
                    message=f"Failed to create unique destination: {str(e)}",
                    path=str(destination_path),
                    source_exception=e,
                )
                return Result.failure(error)

    @abstractmethod
    def _execute_operation(
        self, source_path: FilePath, destination_path: FilePath, **kwargs
    ) -> PathResult:
        """
        Execute the file operation.

        This is an abstract method that must be implemented by subclasses
        to provide the specific file operation logic.

        Args:
            source_path: Source file path
            destination_path: Destination file path
            **kwargs: Additional operation-specific arguments

        Returns:
            Result with path to the processed file or error
        """
        pass

    def _post_process(
        self, source_path: FilePath, processed_path: FilePath, **kwargs
    ) -> PathResult:
        """
        Perform post-processing after the operation.

        This is a hook method that can be overridden by subclasses
        to add additional steps after the main operation.

        Args:
            source_path: Original source file path
            processed_path: Processed file path
            **kwargs: Additional operation-specific arguments

        Returns:
            Result with path to the post-processed file or error
        """
        # Default implementation does nothing
        return Result.success(processed_path)


class FileMoveTemplate(FileProcessorTemplate):
    """Template implementation for moving files."""

    def _execute_operation(
        self, source_path: FilePath, destination_path: FilePath, **kwargs
    ) -> PathResult:
        """
        Move a file from source to destination.

        Args:
            source_path: Source file path
            destination_path: Destination file path
            **kwargs: Additional operation-specific arguments

        Returns:
            Result with path to the moved file or error
        """
        try:
            if self.dry_run:
                logger.info(f"Would move file: {source_path} -> {destination_path}")
                return Result.success(destination_path)

            # Perform the actual move
            moved_path = source_path.move_to(destination_path)
            logger.info(f"Moved file: {source_path} -> {moved_path}")

            return Result.success(moved_path)

        except Exception as e:
            error = OperationError(
                type=ErrorType.OPERATION_FAILED,
                message=f"Failed to move file: {str(e)}",
                path=str(source_path),
                source_exception=e,
            )
            return Result.failure(error)


class FileCopyTemplate(FileProcessorTemplate):
    """Template implementation for copying files."""

    def _execute_operation(
        self, source_path: FilePath, destination_path: FilePath, **kwargs
    ) -> PathResult:
        """
        Copy a file from source to destination.

        Args:
            source_path: Source file path
            destination_path: Destination file path
            **kwargs: Additional operation-specific arguments

        Returns:
            Result with path to the copied file or error
        """
        try:
            if self.dry_run:
                logger.info(f"Would copy file: {source_path} -> {destination_path}")
                return Result.success(destination_path)

            # Perform the actual copy
            copied_path = source_path.copy_to(destination_path)
            logger.info(f"Copied file: {source_path} -> {copied_path}")

            return Result.success(copied_path)

        except Exception as e:
            error = OperationError(
                type=ErrorType.OPERATION_FAILED,
                message=f"Failed to copy file: {str(e)}",
                path=str(source_path),
                source_exception=e,
            )
            return Result.failure(error)


class FileRenameTemplate(FileProcessorTemplate):
    """Template implementation for renaming files."""

    def _execute_operation(
        self, source_path: FilePath, destination_path: FilePath, **kwargs
    ) -> PathResult:
        """
        Rename a file.

        Args:
            source_path: Source file path
            destination_path: New name or path
            **kwargs: Additional operation-specific arguments

        Returns:
            Result with path to the renamed file or error
        """
        try:
            if self.dry_run:
                logger.info(f"Would rename file: {source_path} -> {destination_path}")
                return Result.success(destination_path)

            # Perform the actual rename
            renamed_path = source_path.rename(destination_path)
            logger.info(f"Renamed file: {source_path} -> {renamed_path}")

            return Result.success(renamed_path)

        except Exception as e:
            error = OperationError(
                type=ErrorType.OPERATION_FAILED,
                message=f"Failed to rename file: {str(e)}",
                path=str(source_path),
                source_exception=e,
            )
            return Result.failure(error)


class DirectoryProcessorTemplate(ABC):
    """
    Abstract base class for directory processors using the Template Method pattern.

    This class defines skeleton algorithms for directory processing,
    with customizable steps for different operations.
    """

    def __init__(
        self,
        dry_run: bool = False,
        duplicate_handler: Optional[DuplicateHandler] = None,
        recursive: bool = True,
    ):
        """
        Initialize the directory processor template.

        Args:
            dry_run: Whether to simulate operations without making changes
            duplicate_handler: Optional handler for duplicates
            recursive: Whether to process subdirectories recursively
        """
        self.dry_run = dry_run
        self.duplicate_handler = duplicate_handler
        self.recursive = recursive

    def process_directory(
        self,
        source: Union[str, Path, FilePath],
        destination: Optional[Union[str, Path, FilePath]] = None,
        **kwargs,
    ) -> PathResult:
        """
        Process a directory (Template Method).

        This is the main template method defining the skeleton algorithm
        for directory processing operations.

        Args:
            source: Source directory path
            destination: Optional destination path
            **kwargs: Additional operation-specific arguments

        Returns:
            Result with path to the processed directory or error
        """
        # The template method defines the skeleton of the algorithm
        try:
            # Step 1: Validate input paths
            source_path_result = self._validate_source_directory(source)
            if source_path_result.is_failure():
                return source_path_result

            source_path = source_path_result.unwrap()

            # Step 2: Prepare destination path if provided
            if destination:
                destination_path_result = self._prepare_destination_directory(
                    destination
                )
                if destination_path_result.is_failure():
                    return destination_path_result

                destination_path = destination_path_result.unwrap()
            else:
                # Use a default destination if not provided
                destination_path = self._get_default_destination(source_path)

            # Step 3: Handle duplicates if needed
            final_destination_result = self._handle_directory_duplicates(
                source_path, destination_path
            )
            if final_destination_result.is_failure():
                return final_destination_result

            final_destination = final_destination_result.unwrap()

            # Step 4: Pre-process directory (optional)
            pre_result = self._pre_process_directory(
                source_path, final_destination, **kwargs
            )
            if pre_result.is_failure():
                return pre_result

            # Step 5: Execute the operation (to be implemented by subclasses)
            operation_result = self._execute_directory_operation(
                source_path, final_destination, **kwargs
            )
            if operation_result.is_failure():
                return operation_result

            processed_path = operation_result.unwrap()

            # Step 6: Process subdirectories if recursive
            if self.recursive:
                subdirs_result = self._process_subdirectories(
                    source_path, processed_path, **kwargs
                )
                if subdirs_result.is_failure():
                    return subdirs_result

            # Step 7: Perform post-processing (optional)
            post_result = self._post_process_directory(
                source_path, processed_path, **kwargs
            )
            if post_result.is_failure():
                return post_result

            # Return the final processed path
            return Result.success(processed_path)

        except Exception as e:
            # Convert any unhandled exceptions to OperationError
            error = OperationError(
                type=ErrorType.OPERATION_FAILED,
                message=f"Directory processing failed: {str(e)}",
                path=str(source),
                source_exception=e,
            )
            return Result.failure(error)

    @result_handler
    def _validate_source_directory(
        self, source: Union[str, Path, FilePath]
    ) -> FilePath:
        """
        Validate the source directory path.

        Args:
            source: Source directory path to validate

        Returns:
            Validated source directory path

        Raises:
            FileNotFoundError: If source doesn't exist
            NotADirectoryError: If source is not a directory
            ValueError: If source is invalid
        """
        # Convert to FilePath and validate
        source_path = FilePath(source)

        # Additional validation logic can be added here
        if not source_path.exists:
            raise FileNotFoundError(f"Source directory does not exist: {source_path}")

        if not source_path.is_directory:
            raise NotADirectoryError(f"Source is not a directory: {source_path}")

        return source_path

    @result_handler
    def _prepare_destination_directory(
        self, destination: Union[str, Path, FilePath]
    ) -> FilePath:
        """
        Prepare the destination directory path.

        Args:
            destination: Destination directory path to prepare

        Returns:
            Prepared destination directory path

        Raises:
            ValueError: If destination is invalid
        """
        # Convert to FilePath with must_exist=False
        destination_path = FilePath(destination, must_exist=False)

        # Make sure the directory exists
        if not destination_path.exists:
            if not self.dry_run:
                destination_path.path.mkdir(parents=True, exist_ok=True)
            else:
                logger.info(f"Would create directory: {destination_path}")

        return destination_path

    def _get_default_destination(self, source_path: FilePath) -> FilePath:
        """
        Get a default destination if none is provided.

        Args:
            source_path: Source directory path

        Returns:
            Default destination path
        """
        # Default implementation uses the source's parent directory
        return source_path.parent

    def _handle_directory_duplicates(
        self, source_path: FilePath, destination_path: FilePath
    ) -> PathResult:
        """
        Handle duplicate directories.

        Args:
            source_path: Source directory path
            destination_path: Destination directory path

        Returns:
            Result with final destination path or error
        """
        # Check if source and destination are the same directory
        if source_path == destination_path:
            error = OperationError(
                type=ErrorType.ALREADY_EXISTS,
                message="Source and destination are the same directory",
                path=str(destination_path),
            )
            return Result.failure(error)

        # For directories, we typically just create or use the existing directory
        # If destination exists but is not a directory, that's an error
        if destination_path.exists and not destination_path.is_directory:
            error = OperationError(
                type=ErrorType.INVALID_PATH,
                message=f"Destination exists but is not a directory: {destination_path}",
                path=str(destination_path),
            )
            return Result.failure(error)

        # If we have a duplicate handler and the directory already exists
        if self.duplicate_handler and destination_path.exists:
            try:
                if self.duplicate_handler.strategy == DuplicateStrategy.SKIP:
                    logger.info(f"Skipping duplicate directory: {destination_path}")
                    return Result.success(destination_path)

                if self.duplicate_handler.strategy in [
                    DuplicateStrategy.RENAME_NEW,
                    DuplicateStrategy.RENAME_EXISTING,
                ]:
                    # Create a unique name for the directory
                    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                    new_name = f"{destination_path.name}_{timestamp}"
                    new_path = destination_path.parent.join(new_name)

                    return Result.success(new_path)

            except Exception as e:
                error = OperationError(
                    type=ErrorType.OPERATION_FAILED,
                    message=f"Duplicate handling failed: {str(e)}",
                    path=str(destination_path),
                    source_exception=e,
                )
                return Result.failure(error)

        # No duplicate handling needed or custom handling is done
        return Result.success(destination_path)

    def _pre_process_directory(
        self, source_path: FilePath, destination_path: FilePath, **kwargs
    ) -> PathResult:
        """
        Perform pre-processing before the main operation.

        This is a hook method that can be overridden by subclasses
        to add additional steps before the main operation.

        Args:
            source_path: Source directory path
            destination_path: Destination directory path
            **kwargs: Additional operation-specific arguments

        Returns:
            Result with destination path or error
        """
        # Default implementation does nothing
        return Result.success(destination_path)

    @abstractmethod
    def _execute_directory_operation(
        self, source_path: FilePath, destination_path: FilePath, **kwargs
    ) -> PathResult:
        """
        Execute the directory operation.

        This is an abstract method that must be implemented by subclasses
        to provide the specific directory operation logic.

        Args:
            source_path: Source directory path
            destination_path: Destination directory path
            **kwargs: Additional operation-specific arguments

        Returns:
            Result with path to the processed directory or error
        """
        pass

    def _process_subdirectories(
        self, source_path: FilePath, destination_path: FilePath, **kwargs
    ) -> PathResult:
        """
        Process subdirectories recursively.

        Args:
            source_path: Source directory path
            destination_path: Destination directory path
            **kwargs: Additional operation-specific arguments

        Returns:
            Result with destination path or error
        """
        try:
            if not source_path.is_directory:
                return Result.success(destination_path)

            # Get all subdirectories
            subdirs = [d for d in source_path.list_dir() if d.is_directory]

            # Process each subdirectory
            for subdir in subdirs:
                # Create corresponding destination subdirectory path
                rel_path = subdir.path.relative_to(source_path.path)
                dest_subdir = destination_path.join(rel_path)

                # Recursively process the subdirectory
                result = self.process_directory(subdir, dest_subdir, **kwargs)
                if result.is_failure():
                    # Log the error but continue with other subdirectories
                    logger.error(
                        f"Failed to process subdirectory {subdir}: {result.error()}"
                    )

            return Result.success(destination_path)

        except Exception as e:
            error = OperationError(
                type=ErrorType.OPERATION_FAILED,
                message=f"Failed to process subdirectories: {str(e)}",
                path=str(source_path),
                source_exception=e,
            )
            return Result.failure(error)

    def _post_process_directory(
        self, source_path: FilePath, processed_path: FilePath, **kwargs
    ) -> PathResult:
        """
        Perform post-processing after the operation.

        This is a hook method that can be overridden by subclasses
        to add additional steps after the main operation.

        Args:
            source_path: Original source directory path
            processed_path: Processed directory path
            **kwargs: Additional operation-specific arguments

        Returns:
            Result with path to the post-processed directory or error
        """
        # Default implementation does nothing
        return Result.success(processed_path)


class DirectoryCopyTemplate(DirectoryProcessorTemplate):
    """Template implementation for copying directories."""

    def _execute_directory_operation(
        self, source_path: FilePath, destination_path: FilePath, **kwargs
    ) -> PathResult:
        """
        Copy a directory.

        Args:
            source_path: Source directory path
            destination_path: Destination directory path
            **kwargs: Additional operation-specific arguments

        Returns:
            Result with path to the copied directory or error
        """
        try:
            # Make sure the destination directory exists
            if not destination_path.exists:
                if not self.dry_run:
                    destination_path.path.mkdir(parents=True, exist_ok=True)
                else:
                    logger.info(f"Would create directory: {destination_path}")

            # Copy all files in the source directory (not recursively)
            for file in source_path.list_files():
                dest_file = destination_path.join(file.name)

                if self.dry_run:
                    logger.info(f"Would copy file: {file} -> {dest_file}")
                else:
                    # Handle duplicates if needed
                    if dest_file.exists and self.duplicate_handler:
                        final_path, is_duplicate = (
                            self.duplicate_handler.handle_duplicate(
                                dest_file.path,
                                dest_file.path,
                                context=f"Copying {file}",
                            )
                        )

                        if (
                            is_duplicate
                            and self.duplicate_handler.strategy
                            == DuplicateStrategy.SKIP
                        ):
                            logger.info(f"Skipping duplicate file: {file}")
                            continue

                        dest_file = FilePath(final_path, must_exist=False)

                    # Copy the file
                    file.copy_to(dest_file)
                    logger.info(f"Copied file: {file} -> {dest_file}")

            return Result.success(destination_path)

        except Exception as e:
            error = OperationError(
                type=ErrorType.OPERATION_FAILED,
                message=f"Failed to copy directory: {str(e)}",
                path=str(source_path),
                source_exception=e,
            )
            return Result.failure(error)


class DirectoryMoveTemplate(DirectoryProcessorTemplate):
    """Template implementation for moving directories."""

    def _execute_directory_operation(
        self, source_path: FilePath, destination_path: FilePath, **kwargs
    ) -> PathResult:
        """
        Move a directory.

        Args:
            source_path: Source directory path
            destination_path: Destination directory path
            **kwargs: Additional operation-specific arguments

        Returns:
            Result with path to the moved directory or error
        """
        try:
            # If destination parent directory doesn't exist, create it
            if not destination_path.parent.exists:
                if not self.dry_run:
                    destination_path.parent.path.mkdir(parents=True, exist_ok=True)
                else:
                    logger.info(f"Would create directory: {destination_path.parent}")

            # If the destination doesn't exist, we can move the whole directory at once
            if not destination_path.exists:
                if self.dry_run:
                    logger.info(
                        f"Would move directory: {source_path} -> {destination_path}"
                    )
                    return Result.success(destination_path)
                else:
                    moved_path = source_path.move_to(destination_path)
                    logger.info(f"Moved directory: {source_path} -> {moved_path}")
                    return Result.success(moved_path)

            # If destination exists, we need to move files individually
            if not self.dry_run:
                destination_path.path.mkdir(parents=True, exist_ok=True)

            # Move all files in the source directory (not recursively)
            for file in source_path.list_files():
                dest_file = destination_path.join(file.name)

                if self.dry_run:
                    logger.info(f"Would move file: {file} -> {dest_file}")
                else:
                    # Handle duplicates if needed
                    if dest_file.exists and self.duplicate_handler:
                        final_path, is_duplicate = (
                            self.duplicate_handler.handle_duplicate(
                                dest_file.path, dest_file.path, context=f"Moving {file}"
                            )
                        )

                        if (
                            is_duplicate
                            and self.duplicate_handler.strategy
                            == DuplicateStrategy.SKIP
                        ):
                            logger.info(f"Skipping duplicate file: {file}")
                            continue

                        dest_file = FilePath(final_path, must_exist=False)

                    # Move the file
                    file.move_to(dest_file)
                    logger.info(f"Moved file: {file} -> {dest_file}")

            # Remove the source directory if it's empty
            if not self.dry_run and source_path.exists:
                # Check if empty
                remaining_items = list(source_path.path.iterdir())
                if not remaining_items:
                    source_path.path.rmdir()
                    logger.info(f"Removed empty source directory: {source_path}")

            return Result.success(destination_path)

        except Exception as e:
            error = OperationError(
                type=ErrorType.OPERATION_FAILED,
                message=f"Failed to move directory: {str(e)}",
                path=str(source_path),
                source_exception=e,
            )
            return Result.failure(error)


class ArchiveDirectoryTemplate(DirectoryProcessorTemplate):
    """Template implementation for archiving directories."""

    def __init__(
        self,
        dry_run: bool = False,
        duplicate_handler: Optional[DuplicateHandler] = None,
        recursive: bool = True,
        compression_level: int = 6,
    ):
        """
        Initialize the archive directory template.

        Args:
            dry_run: Whether to simulate operations without making changes
            duplicate_handler: Optional handler for duplicates
            recursive: Whether to process subdirectories recursively
            compression_level: ZIP compression level (0-9)
        """
        super().__init__(dry_run, duplicate_handler, recursive)
        self.compression_level = compression_level

    def _execute_directory_operation(
        self,
        source_path: FilePath,
        destination_path: FilePath,
        archive_name: Optional[str] = None,
        **kwargs,
    ) -> PathResult:
        """
        Archive a directory.

        Args:
            source_path: Source directory path
            destination_path: Destination directory path for the archive
            archive_name: Optional name for the archive
            **kwargs: Additional operation-specific arguments

        Returns:
            Result with path to the created archive or error
        """
        import zipfile

        try:
            # Determine archive name
            name = archive_name or source_path.name
            archive_filename = f"{name}.zip"

            # Create the archive path
            archive_path = destination_path.join(archive_filename)

            # Handle duplicates if needed
            if archive_path.exists and self.duplicate_handler:
                try:
                    final_path, is_duplicate = self.duplicate_handler.handle_duplicate(
                        archive_path.path,
                        archive_path.path,
                        context=f"Creating archive for {source_path}",
                    )

                    if (
                        is_duplicate
                        and self.duplicate_handler.strategy == DuplicateStrategy.SKIP
                    ):
                        logger.info(f"Skipping duplicate archive: {archive_path}")
                        return Result.success(archive_path)

                    archive_path = FilePath(final_path, must_exist=False)

                except Exception as e:
                    error = OperationError(
                        type=ErrorType.OPERATION_FAILED,
                        message=f"Duplicate handling failed: {str(e)}",
                        path=str(archive_path),
                        source_exception=e,
                    )
                    return Result.failure(error)

            if self.dry_run:
                logger.info(f"Would archive directory: {source_path} -> {archive_path}")
                return Result.success(archive_path)

            # Make sure the parent directory exists
            if not archive_path.parent.exists:
                archive_path.parent.path.mkdir(parents=True, exist_ok=True)

            # Create the archive
            with zipfile.ZipFile(
                archive_path.path,
                "w",
                compression=zipfile.ZIP_DEFLATED,
                compresslevel=self.compression_level,
            ) as zf:
                # Add all files to the archive
                for root, dirs, files in os.walk(source_path.path):
                    root_path = Path(root)
                    for file in files:
                        file_path = root_path / file
                        # Calculate the path within the archive
                        if archive_name:
                            # Use custom name as root in archive
                            rel_path = Path(archive_name) / file_path.relative_to(
                                source_path.path
                            )
                        else:
                            # Use original directory structure
                            rel_path = file_path.relative_to(source_path.parent.path)
                        # Add to archive
                        zf.write(file_path, rel_path)

            logger.info(f"Archived directory: {source_path} -> {archive_path}")
            return Result.success(archive_path)

        except Exception as e:
            error = OperationError(
                type=ErrorType.OPERATION_FAILED,
                message=f"Failed to archive directory: {str(e)}",
                path=str(source_path),
                source_exception=e,
            )
            return Result.failure(error)

    def _post_process_directory(
        self,
        source_path: FilePath,
        processed_path: FilePath,
        remove_source: bool = False,
        **kwargs,
    ) -> PathResult:
        """
        Perform post-processing after archiving.

        Args:
            source_path: Original source directory path
            processed_path: Archive file path
            remove_source: Whether to remove the source directory after archiving
            **kwargs: Additional operation-specific arguments

        Returns:
            Result with path to the archive or error
        """
        # Remove source directory if requested
        if remove_source and source_path.exists and not self.dry_run:
            try:
                shutil.rmtree(source_path.path)
                logger.info(f"Removed source directory after archiving: {source_path}")
            except Exception as e:
                # Log error but don't fail the operation
                logger.error(f"Failed to remove source directory: {e}")
        elif remove_source and self.dry_run:
            logger.info(f"Would remove source directory after archiving: {source_path}")

        return Result.success(processed_path)


class BatchProcessorTemplate(ABC):
    """
    Abstract base class for batch file processing using the Template Method pattern.

    This class defines skeleton algorithms for processing multiple files,
    with customizable steps for different operations.
    """

    def __init__(
        self,
        file_processor: Optional[FileProcessorTemplate] = None,
        directory_processor: Optional[DirectoryProcessorTemplate] = None,
        dry_run: bool = False,
        duplicate_handler: Optional[DuplicateHandler] = None,
        continue_on_error: bool = False,
    ):
        """
        Initialize the batch processor template.

        Args:
            file_processor: Processor for individual files
            directory_processor: Processor for directories
            dry_run: Whether to simulate operations without making changes
            duplicate_handler: Optional handler for duplicates
            continue_on_error: Whether to continue processing on error
        """
        self.file_processor = file_processor
        self.directory_processor = directory_processor
        self.dry_run = dry_run
        self.duplicate_handler = duplicate_handler
        self.continue_on_error = continue_on_error

    def process_batch(
        self,
        sources: List[Union[str, Path, FilePath]],
        destination: Union[str, Path, FilePath],
        **kwargs,
    ) -> Result[List[Path], List[OperationError]]:
        """
        Process multiple files or directories (Template Method).

        This is the main template method defining the skeleton algorithm
        for batch processing operations.

        Args:
            sources: List of source paths
            destination: Destination path
            **kwargs: Additional operation-specific arguments

        Returns:
            Result with list of processed paths or list of errors
        """
        # The template method defines the skeleton of the algorithm
        try:
            # Step 1: Validate input paths
            sources_result = self._validate_sources(sources)
            if sources_result.is_failure():
                return sources_result

            valid_sources = sources_result.unwrap()

            # Step 2: Prepare destination
            destination_result = self._prepare_batch_destination(destination)
            if destination_result.is_failure():
                return destination_result

            dest_path = destination_result.unwrap()

            # Step 3: Pre-process batch (optional)
            pre_result = self._pre_process_batch(valid_sources, dest_path, **kwargs)
            if pre_result.is_failure() and not self.continue_on_error:
                return pre_result

            # Step 4: Process each item
            results = []
            errors = []

            for source in valid_sources:
                result = self._process_batch_item(source, dest_path, **kwargs)

                if result.is_success():
                    results.append(result.unwrap())
                else:
                    errors.append(result.error())
                    if not self.continue_on_error:
                        # Return the first error if not continuing on error
                        return Result.failure([result.error()])

            # Step 5: Post-process batch (optional)
            post_result = self._post_process_batch(results, dest_path, **kwargs)
            if post_result.is_failure() and not self.continue_on_error:
                errors.append(post_result.error())

            # Return the results or errors
            if errors and not self.continue_on_error:
                return Result.failure(errors)
            elif errors and self.continue_on_error:
                logger.warning(f"Completed with {len(errors)} errors")
                return Result.success(results)
            else:
                return Result.success(results)

        except Exception as e:
            # Convert any unhandled exceptions to OperationError
            error = OperationError(
                type=ErrorType.OPERATION_FAILED,
                message=f"Batch processing failed: {str(e)}",
                source_exception=e,
            )
            return Result.failure([error])

    @result_handler
    def _validate_sources(
        self, sources: List[Union[str, Path, FilePath]]
    ) -> List[FilePath]:
        """
        Validate the source paths.

        Args:
            sources: List of source paths to validate

        Returns:
            List of validated source paths

        Raises:
            ValueError: If no valid sources are provided
        """
        if not sources:
            raise ValueError("No source paths provided")

        # Convert to FilePath objects and validate
        valid_sources = []
        for source in sources:
            try:
                path = FilePath(source)
                if path.exists:
                    valid_sources.append(path)
                else:
                    logger.warning(f"Source does not exist: {path}")
            except Exception as e:
                logger.warning(f"Invalid source path: {source} - {e}")

        if not valid_sources:
            raise ValueError("No valid source paths found")

        return valid_sources

    @result_handler
    def _prepare_batch_destination(
        self, destination: Union[str, Path, FilePath]
    ) -> FilePath:
        """
        Prepare the batch destination.

        Args:
            destination: Destination path to prepare

        Returns:
            Prepared destination path

        Raises:
            ValueError: If destination is invalid
        """
        # Convert to FilePath with must_exist=False
        destination_path = FilePath(destination, must_exist=False)

        # Make sure the destination directory exists
        if not destination_path.exists:
            if not self.dry_run:
                destination_path.path.mkdir(parents=True, exist_ok=True)
            else:
                logger.info(f"Would create directory: {destination_path}")

        elif not destination_path.is_directory:
            raise ValueError(
                f"Destination exists but is not a directory: {destination_path}"
            )

        return destination_path

    def _pre_process_batch(
        self, sources: List[FilePath], destination: FilePath, **kwargs
    ) -> Result[bool, OperationError]:
        """
        Perform pre-processing before the batch operation.

        This is a hook method that can be overridden by subclasses
        to add additional steps before the batch operation.

        Args:
            sources: List of source paths
            destination: Destination path
            **kwargs: Additional operation-specific arguments

        Returns:
            Result with success flag or error
        """
        # Default implementation does nothing
        return Result.success(True)

    def _process_batch_item(
        self, source: FilePath, destination: FilePath, **kwargs
    ) -> PathResult:
        """
        Process a single item in the batch.

        Args:
            source: Source path
            destination: Destination path
            **kwargs: Additional operation-specific arguments

        Returns:
            Result with processed path or error
        """
        try:
            # Choose the appropriate processor based on the source type
            if source.is_file:
                if self.file_processor:
                    # Calculate the destination file path
                    dest_file = destination.join(source.name)
                    return self.file_processor.process_file(source, dest_file, **kwargs)
                else:
                    error = OperationError(
                        type=ErrorType.OPERATION_FAILED,
                        message="No file processor available",
                        path=str(source),
                    )
                    return Result.failure(error)

            elif source.is_directory:
                if self.directory_processor:
                    # Calculate the destination directory path
                    dest_dir = destination.join(source.name)
                    return self.directory_processor.process_directory(
                        source, dest_dir, **kwargs
                    )
                else:
                    error = OperationError(
                        type=ErrorType.OPERATION_FAILED,
                        message="No directory processor available",
                        path=str(source),
                    )
                    return Result.failure(error)

            else:
                error = OperationError(
                    type=ErrorType.INVALID_PATH,
                    message=f"Source is neither a file nor a directory: {source}",
                    path=str(source),
                )
                return Result.failure(error)

        except Exception as e:
            error = OperationError(
                type=ErrorType.OPERATION_FAILED,
                message=f"Failed to process batch item: {str(e)}",
                path=str(source),
                source_exception=e,
            )
            return Result.failure(error)

    def _post_process_batch(
        self, results: List[Path], destination: FilePath, **kwargs
    ) -> Result[bool, OperationError]:
        """
        Perform post-processing after the batch operation.

        This is a hook method that can be overridden by subclasses
        to add additional steps after the batch operation.

        Args:
            results: List of processed paths
            destination: Destination path
            **kwargs: Additional operation-specific arguments

        Returns:
            Result with success flag or error
        """
        # Default implementation does nothing
        return Result.success(True)
