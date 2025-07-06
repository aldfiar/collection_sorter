"""
File operation strategies using the Result pattern for Collection Sorter.

This module implements the Strategy Pattern for file operations using the
Result pattern for better error handling and composability.
"""

import logging
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Dict, Optional, Union

from collection_sorter.files import FilePath
from collection_sorter.files.duplicates import DuplicateHandler
from collection_sorter.operations import (
    archive_directory,
    copy_file,
    delete_directory,
    delete_file,
    extract_archive,
    move_file,
    rename_file,
)

from .result import PathResult

logger = logging.getLogger("result_strategies")


class ResultFileOperationStrategy(ABC):
    """
    Abstract base class for file operation strategies using the Result pattern.

    This defines the interface that all file operation strategies must implement.
    """

    @abstractmethod
    def execute(self, *args, **kwargs) -> PathResult:
        """
        Execute the file operation.

        Args:
            *args: Positional arguments
            **kwargs: Keyword arguments

        Returns:
            Result with path to the operation result or error
        """
        pass

    @property
    @abstractmethod
    def name(self) -> str:
        """Get the name of this strategy."""
        pass


class MoveFileResultStrategy(ResultFileOperationStrategy):
    """Strategy for moving a file to a new location using the Result pattern."""

    def __init__(
        self,
        dry_run: bool = False,
        duplicate_handler: Optional[DuplicateHandler] = None,
    ):
        """
        Initialize the strategy.

        Args:
            dry_run: Whether to simulate operations without making changes
            duplicate_handler: Optional handler for duplicates
        """
        self.dry_run = dry_run
        self.duplicate_handler = duplicate_handler

    @property
    def name(self) -> str:
        """Get the name of this strategy."""
        return "MoveFile"

    def execute(
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
        return move_file(
            source,
            destination,
            duplicate_handler=self.duplicate_handler,
            dry_run=self.dry_run,
        )


class CopyFileResultStrategy(ResultFileOperationStrategy):
    """Strategy for copying a file to a new location using the Result pattern."""

    def __init__(
        self,
        dry_run: bool = False,
        duplicate_handler: Optional[DuplicateHandler] = None,
    ):
        """
        Initialize the strategy.

        Args:
            dry_run: Whether to simulate operations without making changes
            duplicate_handler: Optional handler for duplicates
        """
        self.dry_run = dry_run
        self.duplicate_handler = duplicate_handler

    @property
    def name(self) -> str:
        """Get the name of this strategy."""
        return "CopyFile"

    def execute(
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
        return copy_file(
            source,
            destination,
            duplicate_handler=self.duplicate_handler,
            dry_run=self.dry_run,
        )


class RenameFileResultStrategy(ResultFileOperationStrategy):
    """Strategy for renaming files using the Result pattern."""

    def __init__(
        self,
        dry_run: bool = False,
        duplicate_handler: Optional[DuplicateHandler] = None,
    ):
        """
        Initialize the strategy.

        Args:
            dry_run: Whether to simulate operations without making changes
            duplicate_handler: Optional handler for duplicates
        """
        self.dry_run = dry_run
        self.duplicate_handler = duplicate_handler

    @property
    def name(self) -> str:
        """Get the name of this strategy."""
        return "RenameFile"

    def execute(
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
        return rename_file(
            source,
            new_name,
            duplicate_handler=self.duplicate_handler,
            dry_run=self.dry_run,
        )


class ArchiveResultStrategy(ResultFileOperationStrategy):
    """Strategy for archiving files and directories using the Result pattern."""

    def __init__(
        self,
        compression_level: int = 6,
        dry_run: bool = False,
        duplicate_handler: Optional[DuplicateHandler] = None,
    ):
        """
        Initialize the strategy.

        Args:
            compression_level: ZIP compression level (0-9)
            dry_run: Whether to simulate operations without making changes
            duplicate_handler: Optional handler for duplicates
        """
        self.compression_level = compression_level
        self.dry_run = dry_run
        self.duplicate_handler = duplicate_handler

    @property
    def name(self) -> str:
        """Get the name of this strategy."""
        return "Archive"

    def execute(
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
        return archive_directory(
            source,
            destination,
            archive_name=archive_name,
            compression_level=self.compression_level,
            duplicate_handler=self.duplicate_handler,
            dry_run=self.dry_run,
        )


class ExtractArchiveResultStrategy(ResultFileOperationStrategy):
    """Strategy for extracting ZIP archives using the Result pattern."""

    def __init__(
        self,
        dry_run: bool = False,
        duplicate_handler: Optional[DuplicateHandler] = None,
    ):
        """
        Initialize the strategy.

        Args:
            dry_run: Whether to simulate operations without making changes
            duplicate_handler: Optional handler for duplicates
        """
        self.dry_run = dry_run
        self.duplicate_handler = duplicate_handler

    @property
    def name(self) -> str:
        """Get the name of this strategy."""
        return "ExtractArchive"

    def execute(
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
        return extract_archive(
            source,
            destination,
            duplicate_handler=self.duplicate_handler,
            dry_run=self.dry_run,
        )


class DeleteFileResultStrategy(ResultFileOperationStrategy):
    """Strategy for deleting files using the Result pattern."""

    def __init__(self, dry_run: bool = False):
        """
        Initialize the strategy.

        Args:
            dry_run: Whether to simulate operations without making changes
        """
        self.dry_run = dry_run

    @property
    def name(self) -> str:
        """Get the name of this strategy."""
        return "DeleteFile"

    def execute(self, path: Union[str, Path, FilePath]) -> PathResult:
        """
        Delete a file.

        Args:
            path: Path to the file to delete

        Returns:
            Result with path to the deleted file or error
        """
        return delete_file(path, dry_run=self.dry_run)


class DeleteDirectoryResultStrategy(ResultFileOperationStrategy):
    """Strategy for deleting directories using the Result pattern."""

    def __init__(self, recursive: bool = True, dry_run: bool = False):
        """
        Initialize the strategy.

        Args:
            recursive: Whether to delete recursively
            dry_run: Whether to simulate operations without making changes
        """
        self.recursive = recursive
        self.dry_run = dry_run

    @property
    def name(self) -> str:
        """Get the name of this strategy."""
        return "DeleteDirectory"

    def execute(self, path: Union[str, Path, FilePath]) -> PathResult:
        """
        Delete a directory.

        Args:
            path: Path to the directory to delete

        Returns:
            Result with path to the deleted directory or error
        """
        return delete_directory(path, recursive=self.recursive, dry_run=self.dry_run)


class ResultFileOperationContext:
    """
    Context class for file operations using the Result pattern.

    This class maintains a reference to a strategy and delegates
    file operations to the appropriate strategy instance.
    """

    def __init__(self, strategy: ResultFileOperationStrategy):
        """
        Initialize the file operation context.

        Args:
            strategy: The initial strategy to use
        """
        self._strategy = strategy

    @property
    def strategy(self) -> ResultFileOperationStrategy:
        """Get the current strategy."""
        return self._strategy

    @strategy.setter
    def strategy(self, strategy: ResultFileOperationStrategy):
        """
        Set the strategy to use.

        Args:
            strategy: The new strategy to use
        """
        self._strategy = strategy

    def execute(self, *args, **kwargs) -> PathResult:
        """
        Execute the current strategy.

        Args:
            *args: Positional arguments to pass to the strategy
            **kwargs: Keyword arguments to pass to the strategy

        Returns:
            Result of the strategy execution
        """
        return self._strategy.execute(*args, **kwargs)


# Strategy registry for global access to strategies
result_strategy_registry: Dict[str, ResultFileOperationStrategy] = {}


def register_result_strategy(strategy: ResultFileOperationStrategy) -> None:
    """
    Register a strategy in the global registry.

    Args:
        strategy: Strategy to register
    """
    result_strategy_registry[strategy.name] = strategy


def get_result_strategy(name: str) -> ResultFileOperationStrategy:
    """
    Get a strategy from the global registry.

    Args:
        name: Name of the strategy to get

    Returns:
        The requested strategy

    Raises:
        KeyError: If the strategy is not registered
    """
    if name not in result_strategy_registry:
        raise KeyError(f"Strategy not registered: {name}")
    return result_strategy_registry[name]


def create_default_result_strategies(
    dry_run: bool = False,
    compression_level: int = 6,
    duplicate_handler: Optional[DuplicateHandler] = None,
) -> Dict[str, ResultFileOperationStrategy]:
    """
    Create and register default strategies.

    Args:
        dry_run: Whether to simulate operations without making changes
        compression_level: ZIP compression level (0-9)
        duplicate_handler: Optional handler for duplicates

    Returns:
        Dictionary of created strategies
    """
    strategies = {
        "move_file": MoveFileResultStrategy(dry_run, duplicate_handler),
        "copy_file": CopyFileResultStrategy(dry_run, duplicate_handler),
        "rename_file": RenameFileResultStrategy(dry_run, duplicate_handler),
        "archive": ArchiveResultStrategy(compression_level, dry_run, duplicate_handler),
        "extract_archive": ExtractArchiveResultStrategy(dry_run, duplicate_handler),
        "delete_file": DeleteFileResultStrategy(dry_run),
        "delete_directory": DeleteDirectoryResultStrategy(True, dry_run),
    }

    # Register the strategies
    for name, strategy in strategies.items():
        register_result_strategy(strategy)

    return strategies
