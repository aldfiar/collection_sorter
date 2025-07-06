"""
File processor using the Result pattern for Collection Sorter.

This module provides a file processor that uses both the Strategy pattern
and the Result pattern for better error handling and composability.
"""

import logging
from pathlib import Path
from typing import Callable, List, Optional, Union

from collection_sorter.files import FilePath
from collection_sorter.files.duplicates import DuplicateHandler
from collection_sorter.operations import (
    archive_and_delete,
    check_path_exists,
    ensure_directory,
    list_directories,
    list_files,
    move_and_rename,
)
from collection_sorter.result.result_strategies import (
    ResultFileOperationContext,
    ResultFileOperationStrategy,
    create_default_result_strategies,
)

from .result import BoolResult, OperationError, PathResult, Result

logger = logging.getLogger("result_processor")


class ResultFileProcessor:
    """
    Processor for file operations with Strategy pattern and Result pattern support.

    This class provides a consistent interface for file operations
    using interchangeable strategies and functional error handling.
    """

    def __init__(
        self,
        dry_run: bool = False,
        compression_level: int = 6,
        duplicate_handler: Optional[DuplicateHandler] = None,
    ):
        """
        Initialize the file processor.

        Args:
            dry_run: Whether to simulate operations without making changes
            compression_level: ZIP compression level (0-9)
            duplicate_handler: Optional handler for duplicates
        """
        self.dry_run = dry_run
        self.compression_level = compression_level
        self.duplicate_handler = duplicate_handler

        # Create default strategies
        self.strategies = create_default_result_strategies(
            dry_run=dry_run,
            compression_level=compression_level,
            duplicate_handler=duplicate_handler,
        )

        # Create the context with a default strategy
        self.context = ResultFileOperationContext(self.strategies["move_file"])

    def set_strategy(self, operation: str) -> None:
        """
        Set the current strategy by name.

        Args:
            operation: Name of the strategy to use

        Raises:
            KeyError: If the strategy is not registered
        """
        if operation not in self.strategies:
            raise KeyError(f"Strategy not registered: {operation}")

        self.context.strategy = self.strategies[operation]

    def add_strategy(self, name: str, strategy: ResultFileOperationStrategy) -> None:
        """
        Add a new strategy.

        Args:
            name: Name for the strategy
            strategy: Strategy instance
        """
        self.strategies[name] = strategy

    def check_path_exists(self, path: Union[str, Path, FilePath]) -> BoolResult:
        """
        Check if a path exists.

        Args:
            path: Path to check

        Returns:
            Result with boolean indicating existence or error
        """
        return check_path_exists(path)

    def ensure_directory(self, path: Union[str, Path, FilePath]) -> PathResult:
        """
        Ensure a directory exists, creating it if needed.

        Args:
            path: Directory path

        Returns:
            Result with path to the directory or error
        """
        return ensure_directory(path)

    def list_files(
        self, path: Union[str, Path, FilePath]
    ) -> Result[List[Path], OperationError]:
        """
        List all files in a directory.

        Args:
            path: Directory path

        Returns:
            Result with list of file paths or error
        """
        return list_files(path)

    def list_directories(
        self, path: Union[str, Path, FilePath]
    ) -> Result[List[Path], OperationError]:
        """
        List all subdirectories in a directory.

        Args:
            path: Directory path

        Returns:
            Result with list of directory paths or error
        """
        return list_directories(path)

    def move_file(
        self,
        source: Union[str, Path, FilePath],
        destination: Union[str, Path, FilePath],
    ) -> PathResult:
        """
        Move a file to a new location.

        Args:
            source: Source file path
            destination: Destination file path

        Returns:
            Result with path to the destination file or error
        """
        self.set_strategy("move_file")
        return self.context.execute(source, destination)

    def copy_file(
        self,
        source: Union[str, Path, FilePath],
        destination: Union[str, Path, FilePath],
    ) -> PathResult:
        """
        Copy a file to a new location.

        Args:
            source: Source file path
            destination: Destination file path

        Returns:
            Result with path to the destination file or error
        """
        self.set_strategy("copy_file")
        return self.context.execute(source, destination)

    def rename_file(
        self, source: Union[str, Path, FilePath], new_name: Union[str, Path, FilePath]
    ) -> PathResult:
        """
        Rename a file.

        Args:
            source: Source file path
            new_name: New name or path for the file

        Returns:
            Result with path to the renamed file or error
        """
        self.set_strategy("rename_file")
        return self.context.execute(source, new_name)

    def archive_directory(
        self,
        source: Union[str, Path, FilePath],
        destination: Optional[Union[str, Path, FilePath]] = None,
        archive_name: Optional[str] = None,
    ) -> PathResult:
        """
        Archive a directory to a ZIP file.

        Args:
            source: Source directory to archive
            destination: Optional destination for the archive
            archive_name: Optional name for the archive

        Returns:
            Result with path to the created archive or error
        """
        self.set_strategy("archive")
        return self.context.execute(source, destination, archive_name)

    def extract_archive(
        self,
        source: Union[str, Path, FilePath],
        destination: Optional[Union[str, Path, FilePath]] = None,
    ) -> PathResult:
        """
        Extract a ZIP archive to a directory.

        Args:
            source: Source archive to extract
            destination: Optional destination directory

        Returns:
            Result with path to the extraction directory or error
        """
        self.set_strategy("extract_archive")
        return self.context.execute(source, destination)

    def delete_file(self, path: Union[str, Path, FilePath]) -> PathResult:
        """
        Delete a file.

        Args:
            path: Path to the file to delete

        Returns:
            Result with path to the deleted file or error
        """
        self.set_strategy("delete_file")
        return self.context.execute(path)

    def delete_directory(self, path: Union[str, Path, FilePath]) -> PathResult:
        """
        Delete a directory.

        Args:
            path: Path to the directory to delete

        Returns:
            Result with path to the deleted directory or error
        """
        self.set_strategy("delete_directory")
        return self.context.execute(path)

    def move_and_rename(
        self,
        source: Union[str, Path, FilePath],
        destination: Union[str, Path, FilePath],
        new_name: str,
    ) -> PathResult:
        """
        Move a file and rename it.

        Args:
            source: Source file path
            destination: Destination directory
            new_name: New file name

        Returns:
            Result with path to the renamed file or error
        """
        return move_and_rename(
            source,
            destination,
            new_name,
            duplicate_handler=self.duplicate_handler,
            dry_run=self.dry_run,
        )

    def archive_and_delete(
        self,
        source: Union[str, Path, FilePath],
        destination: Optional[Union[str, Path, FilePath]] = None,
        archive_name: Optional[str] = None,
    ) -> PathResult:
        """
        Archive a directory and then delete it.

        Args:
            source: Source directory to archive
            destination: Optional destination for the archive
            archive_name: Optional name for the archive

        Returns:
            Result with path to the created archive or error
        """
        return archive_and_delete(
            source,
            destination,
            archive_name=archive_name,
            compression_level=self.compression_level,
            duplicate_handler=self.duplicate_handler,
            dry_run=self.dry_run,
        )

    def process_collection(
        self,
        source: Union[str, Path, FilePath],
        operation: Callable[[Union[str, Path, FilePath], ...], PathResult],
        *args,
        **kwargs,
    ) -> Result[List[Path], List[OperationError]]:
        """
        Process all files in a collection with a given operation.

        Args:
            source: Source directory or file
            operation: Operation function to apply to each file
            *args: Additional positional arguments for the operation
            **kwargs: Additional keyword arguments for the operation

        Returns:
            Result with list of operation results or list of errors
        """
        # List files in the source
        if isinstance(source, (str, Path)) and Path(source).is_file():
            files_result = Result.success([Path(source)])
        else:
            files_result = self.list_files(source)

        if files_result.is_failure():
            return Result.failure([files_result.error()])

        # Process each file
        results = []
        for file in files_result.unwrap():
            result = operation(file, *args, **kwargs)
            results.append(result)

        # Collect all results
        return Result.collect(results)

    def bulk_move(
        self,
        source: Union[str, Path, FilePath],
        destination: Union[str, Path, FilePath],
    ) -> Result[List[Path], List[OperationError]]:
        """
        Move all files in a collection to a new location.

        Args:
            source: Source directory or file
            destination: Destination directory

        Returns:
            Result with list of destination paths or list of errors
        """
        return self.process_collection(source, self.move_file, destination)

    def bulk_copy(
        self,
        source: Union[str, Path, FilePath],
        destination: Union[str, Path, FilePath],
    ) -> Result[List[Path], List[OperationError]]:
        """
        Copy all files in a collection to a new location.

        Args:
            source: Source directory or file
            destination: Destination directory

        Returns:
            Result with list of destination paths or list of errors
        """
        return self.process_collection(source, self.copy_file, destination)

    def bulk_archive(
        self,
        source: Union[str, Path, FilePath],
        destination: Optional[Union[str, Path, FilePath]] = None,
    ) -> Result[List[Path], List[OperationError]]:
        """
        Archive all directories in a collection.

        Args:
            source: Source directory
            destination: Optional destination for archives

        Returns:
            Result with list of archive paths or list of errors
        """
        # List directories in the source
        directories_result = self.list_directories(source)

        if directories_result.is_failure():
            return Result.failure([directories_result.error()])

        # Archive each directory
        results = []
        for directory in directories_result.unwrap():
            result = self.archive_directory(directory, destination)
            results.append(result)

        # Collect all results
        return Result.collect(results)

    def handle_failure(
        self,
        result: PathResult,
        default_path: Optional[Path] = None,
        log_error: bool = True,
        raise_exception: bool = False,
    ) -> Path:
        """
        Handle a failure result.

        Args:
            result: The result to handle
            default_path: Optional default path to return on failure
            log_error: Whether to log the error
            raise_exception: Whether to raise an exception on failure

        Returns:
            The success value or default path

        Raises:
            FileOperationError: If raise_exception is True and the result is a failure
        """
        if result.is_success():
            return result.unwrap()

        # Handle failure
        error = result.error()

        if log_error:
            logger.error(f"Operation failed: {error}")

        if raise_exception:
            from collection_sorter.common.exceptions import FileOperationError

            raise FileOperationError(
                message=error.message, path=str(error.path) if error.path else None
            )

        if default_path is not None:
            return default_path

        # If no default path is provided and we're not raising an exception,
        # return a reasonable default based on the error context
        if error.path:
            if isinstance(error.path, (str, Path)):
                return Path(error.path)

        # Last resort default
        return Path("../common")
