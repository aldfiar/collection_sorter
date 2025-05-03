"""
File operation strategies for Collection Sorter.

This module implements the Strategy Pattern for file operations,
allowing different operation types to be encapsulated as interchangeable
strategy objects that can be selected at runtime.
"""

import logging
import shutil
import zipfile
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Dict, Optional, Union, Any

from collection_sorter.files.duplicates import DuplicateHandler, DuplicateStrategy
from collection_sorter.common.exceptions import FileOperationError
from collection_sorter.files import FilePath, PathType

logger = logging.getLogger("strategies")


class FileOperationStrategy(ABC):
    """
    Abstract base class for file operation strategies.
    
    This defines the interface that all file operation strategies must implement.
    """
    
    @abstractmethod
    def execute(self, *args, **kwargs) -> Any:
        """
        Execute the file operation.
        
        Args:
            *args: Positional arguments
            **kwargs: Keyword arguments
            
        Returns:
            Result of the operation (depends on the specific strategy)
        """
        pass
    
    @property
    @abstractmethod
    def name(self) -> str:
        """Get the name of this strategy."""
        pass


class MoveFileStrategy(FileOperationStrategy):
    """Strategy for moving a file to a new location."""
    
    def __init__(
        self,
        dry_run: bool = False,
        duplicate_handler: Optional[DuplicateHandler] = None
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
        destination: Union[str, Path, FilePath]
    ) -> FilePath:
        """
        Move a file to a new location.
        
        Args:
            source: Source file path
            destination: Destination file path
            
        Returns:
            Path to the destination file
            
        Raises:
            FileOperationError: If the move operation fails
        """
        src_path = FilePath(source, PathType.FILE)
        dst_path = FilePath(destination, must_exist=False)
        
        # Make sure the parent directory exists
        dst_path.parent.path.mkdir(parents=True, exist_ok=True)
        
        # Handle duplicates if the destination exists
        final_dst_path = dst_path
        is_duplicate = False
        
        if dst_path.exists:
            if self.duplicate_handler:
                # Use the duplicate handler
                final_dst_path, is_duplicate = self.duplicate_handler.handle_duplicate(
                    dst_path.path, 
                    dst_path.path,  # Existing path is the same as new path
                    context=f"Moving {src_path}"
                )
                final_dst_path = FilePath(final_dst_path, must_exist=False)
            else:
                # Default behavior - rename the destination
                identifier = "1"
                counter = 1
                while final_dst_path.exists:
                    stem = dst_path.stem
                    suffix = dst_path.suffix
                    final_dst_path = FilePath(dst_path.path.with_name(f"{stem}_{identifier}{suffix}"), must_exist=False)
                    counter += 1
                    identifier = str(counter)
                is_duplicate = True
        
        # If the duplicate strategy is SKIP, don't do anything
        if (is_duplicate and self.duplicate_handler and 
                self.duplicate_handler.strategy == DuplicateStrategy.SKIP):
            logger.info(f"Skipping duplicate file: {src_path}")
            return FilePath(dst_path.path)
        
        # Move the file
        try:
            # Check if we're using MOVE_TO_DUPLICATES strategy
            if (self.duplicate_handler and 
                self.duplicate_handler.strategy == DuplicateStrategy.MOVE_TO_DUPLICATES and
                self.duplicate_handler.duplicates_dir):
                # Create the duplicates directory if needed
                if not self.dry_run:
                    self.duplicate_handler.duplicates_dir.mkdir(parents=True, exist_ok=True)
            
            # Perform the actual move
            if not self.dry_run:
                shutil.move(src_path.path, final_dst_path.path)
                logger.info(f"Moved: {src_path} -> {final_dst_path}")
            else:
                logger.info(f"Would move: {src_path} -> {final_dst_path}")
                
            return final_dst_path
            
        except Exception as e:
            raise FileOperationError(f"Failed to move file: {str(e)}", path=str(src_path))


class CopyFileStrategy(FileOperationStrategy):
    """Strategy for copying a file to a new location."""
    
    def __init__(
        self,
        dry_run: bool = False,
        duplicate_handler: Optional[DuplicateHandler] = None
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
        destination: Union[str, Path, FilePath]
    ) -> FilePath:
        """
        Copy a file to a new location.
        
        Args:
            source: Source file path
            destination: Destination file path
            
        Returns:
            Path to the destination file
            
        Raises:
            FileOperationError: If the copy operation fails
        """
        src_path = FilePath(source, PathType.FILE)
        dst_path = FilePath(destination, must_exist=False)
        
        # Make sure the parent directory exists
        dst_path.parent.path.mkdir(parents=True, exist_ok=True)
        
        # Handle duplicates if the destination exists
        final_dst_path = dst_path
        is_duplicate = False
        
        if dst_path.exists:
            if self.duplicate_handler:
                # Use the duplicate handler
                final_dst_path, is_duplicate = self.duplicate_handler.handle_duplicate(
                    dst_path.path, 
                    dst_path.path,  # Existing path is the same as new path
                    context=f"Copying {src_path}"
                )
                final_dst_path = FilePath(final_dst_path, must_exist=False)
            else:
                # Default behavior - rename the destination
                identifier = "1"
                counter = 1
                while final_dst_path.exists:
                    stem = dst_path.stem
                    suffix = dst_path.suffix
                    final_dst_path = FilePath(dst_path.path.with_name(f"{stem}_{identifier}{suffix}"), must_exist=False)
                    counter += 1
                    identifier = str(counter)
                is_duplicate = True
        
        # If the duplicate strategy is SKIP, don't do anything
        if (is_duplicate and self.duplicate_handler and 
                self.duplicate_handler.strategy == DuplicateStrategy.SKIP):
            logger.info(f"Skipping duplicate file: {src_path}")
            return FilePath(dst_path.path)
        
        # Copy the file
        try:
            # Check if we're using MOVE_TO_DUPLICATES strategy
            if (self.duplicate_handler and 
                self.duplicate_handler.strategy == DuplicateStrategy.MOVE_TO_DUPLICATES and
                self.duplicate_handler.duplicates_dir):
                # Create the duplicates directory if needed
                if not self.dry_run:
                    self.duplicate_handler.duplicates_dir.mkdir(parents=True, exist_ok=True)
            
            # Perform the actual copy
            if not self.dry_run:
                shutil.copy2(src_path.path, final_dst_path.path)
                logger.info(f"Copied: {src_path} -> {final_dst_path}")
            else:
                logger.info(f"Would copy: {src_path} -> {final_dst_path}")
                
            return final_dst_path
            
        except Exception as e:
            raise FileOperationError(f"Failed to copy file: {str(e)}", path=str(src_path))


class ArchiveStrategy(FileOperationStrategy):
    """Strategy for archiving files and directories."""
    
    def __init__(
        self,
        compression_level: int = 6,
        dry_run: bool = False,
        duplicate_handler: Optional[DuplicateHandler] = None
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
        archive_name: Optional[str] = None
    ) -> FilePath:
        """
        Archive a directory to a ZIP file.
        
        Args:
            source: Source directory to archive
            destination: Optional destination for the archive
            archive_name: Optional name for the archive
            
        Returns:
            Path to the created archive
            
        Raises:
            FileOperationError: If archiving fails
        """
        src_path = FilePath(source, PathType.DIRECTORY)
        
        # Determine archive name
        name = archive_name or src_path.name
        archive_filename = f"{name}.zip"
        
        # Determine destination path
        if destination:
            dest_dir = FilePath(destination, PathType.DIRECTORY, create_if_missing=True)
            archive_path = dest_dir.join(archive_filename)
        else:
            dest_dir = src_path.parent
            archive_path = dest_dir.join(archive_filename)
        
        # Handle duplicates if the destination exists
        final_archive_path = archive_path
        is_duplicate = False
        
        if archive_path.exists:
            if self.duplicate_handler:
                # Use the duplicate handler
                final_path, is_duplicate = self.duplicate_handler.handle_duplicate(
                    archive_path.path, 
                    archive_path.path,  # Existing path is the same as new path
                    context=f"Creating archive for {src_path}"
                )
                final_archive_path = FilePath(final_path, must_exist=False)
            else:
                # Default behavior - rename the destination
                identifier = "1"
                counter = 1
                while final_archive_path.exists:
                    stem = archive_path.stem
                    suffix = archive_path.suffix
                    final_archive_path = FilePath(archive_path.path.with_name(f"{stem}_{identifier}{suffix}"), must_exist=False)
                    counter += 1
                    identifier = str(counter)
                is_duplicate = True
        
        # If the duplicate strategy is SKIP, don't do anything
        if (is_duplicate and self.duplicate_handler and 
                self.duplicate_handler.strategy == DuplicateStrategy.SKIP):
            logger.info(f"Skipping duplicate archive: {archive_path}")
            return FilePath(archive_path.path)
        
        if self.dry_run:
            logger.info(f"Would archive directory: {src_path} -> {final_archive_path}")
            return FilePath(final_archive_path.path, must_exist=False)
        
        try:
            # Create the archive
            with zipfile.ZipFile(
                final_archive_path.path, 
                'w', 
                compression=zipfile.ZIP_DEFLATED,
                compresslevel=self.compression_level
            ) as zf:
                # Get all files in the source directory
                from collection_sorter.common.components import FileCollectionComponent
                collector = FileCollectionComponent(src_path)
                for file in collector.collect_all_files():
                    # Calculate the path within the archive
                    if archive_name:
                        # Use custom name as root in archive
                        rel_path = Path(archive_name) / file.path.relative_to(src_path.path)
                    else:
                        # Use original directory structure
                        rel_path = file.path.relative_to(src_path.parent.path)
                    
                    # Add to archive
                    zf.write(file.path, rel_path)
            
            logger.info(f"Archived directory: {src_path} -> {final_archive_path}")
            return final_archive_path
            
        except Exception as e:
            raise FileOperationError(f"Failed to create archive: {e}", path=str(src_path))


class ExtractArchiveStrategy(FileOperationStrategy):
    """Strategy for extracting ZIP archives."""
    
    def __init__(
        self,
        dry_run: bool = False,
        duplicate_handler: Optional[DuplicateHandler] = None
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
        destination: Optional[Union[str, Path, FilePath]] = None
    ) -> FilePath:
        """
        Extract a ZIP archive to a directory.
        
        Args:
            source: Source archive to extract
            destination: Optional destination directory
            
        Returns:
            Path to the extraction directory
            
        Raises:
            FileOperationError: If extraction fails
        """
        src_path = FilePath(source)
        
        if not src_path.is_file or src_path.suffix.lower() != '.zip':
            raise FileOperationError(f"Not a ZIP archive: {src_path}", path=str(src_path))
        
        # Determine destination path
        if destination:
            dest_dir = FilePath(destination, PathType.DIRECTORY, create_if_missing=True)
        else:
            # Extract to a directory with the same name as the archive (without extension)
            dest_dir = src_path.parent.join(src_path.stem)
            if not self.dry_run:
                dest_dir.path.mkdir(parents=True, exist_ok=True)
        
        # Handle duplicates if the destination directory exists
        final_dest_dir = dest_dir
        is_duplicate = False
        
        if dest_dir.exists:
            if self.duplicate_handler:
                # Use the duplicate handler
                final_path, is_duplicate = self.duplicate_handler.handle_duplicate(
                    dest_dir.path, 
                    dest_dir.path,  # Existing path is the same as new path
                    context=f"Extracting archive {src_path}"
                )
                final_dest_dir = FilePath(final_path, PathType.DIRECTORY, must_exist=False, create_if_missing=True)
            else:
                # Default behavior - rename the destination
                identifier = "1"
                counter = 1
                while final_dest_dir.exists:
                    final_dest_dir = FilePath(dest_dir.parent.path / f"{dest_dir.name}_{identifier}", 
                                             PathType.DIRECTORY, must_exist=False, create_if_missing=True)
                    counter += 1
                    identifier = str(counter)
                is_duplicate = True
        
        # If the duplicate strategy is SKIP, don't do anything
        if (is_duplicate and self.duplicate_handler and 
                self.duplicate_handler.strategy == DuplicateStrategy.SKIP):
            logger.info(f"Skipping extraction to existing directory: {dest_dir}")
            return FilePath(dest_dir.path)
        
        if self.dry_run:
            logger.info(f"Would extract archive: {src_path} -> {final_dest_dir}")
            return final_dest_dir
        
        try:
            # Extract the archive
            with zipfile.ZipFile(src_path.path) as zf:
                zf.extractall(final_dest_dir.path)
            
            logger.info(f"Extracted archive: {src_path} -> {final_dest_dir}")
            return final_dest_dir
            
        except Exception as e:
            raise FileOperationError(f"Failed to extract archive: {e}", path=str(src_path))


class RenameFileStrategy(FileOperationStrategy):
    """Strategy for renaming files."""
    
    def __init__(
        self,
        dry_run: bool = False,
        duplicate_handler: Optional[DuplicateHandler] = None
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
        self,
        source: Union[str, Path, FilePath],
        new_name: Union[str, Path, FilePath]
    ) -> FilePath:
        """
        Rename a file.
        
        Args:
            source: Source file path
            new_name: New name or path for the file
            
        Returns:
            Path to the renamed file
            
        Raises:
            FileOperationError: If renaming fails
        """
        src_path = FilePath(source)
        
        # Convert new_name to Path if needed
        if isinstance(new_name, FilePath):
            dst_path = new_name
        elif isinstance(new_name, str) and '/' not in new_name and '\\' not in new_name:
            # Just a new filename, not a path
            dst_path = FilePath(src_path.parent.path / new_name, must_exist=False)
        else:
            # Full path
            dst_path = FilePath(new_name, must_exist=False)
        
        # Make sure the parent directory exists
        dst_path.parent.path.mkdir(parents=True, exist_ok=True)
        
        # Handle duplicates if the destination exists
        final_dst_path = dst_path
        is_duplicate = False
        
        if dst_path.exists:
            if self.duplicate_handler:
                # Use the duplicate handler
                final_path, is_duplicate = self.duplicate_handler.handle_duplicate(
                    dst_path.path, 
                    dst_path.path,  # Existing path is the same as new path
                    context=f"Renaming {src_path}"
                )
                final_dst_path = FilePath(final_path, must_exist=False)
            else:
                # Default behavior - rename the destination
                identifier = "1"
                counter = 1
                while final_dst_path.exists:
                    stem = dst_path.stem
                    suffix = dst_path.suffix
                    final_dst_path = FilePath(dst_path.path.with_name(f"{stem}_{identifier}{suffix}"), must_exist=False)
                    counter += 1
                    identifier = str(counter)
                is_duplicate = True
        
        # If the duplicate strategy is SKIP, don't do anything
        if (is_duplicate and self.duplicate_handler and 
                self.duplicate_handler.strategy == DuplicateStrategy.SKIP):
            logger.info(f"Skipping rename due to existing destination: {dst_path}")
            return FilePath(src_path.path)
        
        # Rename the file
        try:
            if not self.dry_run:
                src_path.path.rename(final_dst_path.path)
                logger.info(f"Renamed: {src_path} -> {final_dst_path}")
            else:
                logger.info(f"Would rename: {src_path} -> {final_dst_path}")
                
            return final_dst_path
            
        except Exception as e:
            raise FileOperationError(f"Failed to rename file: {str(e)}", path=str(src_path))


class FileOperationContext:
    """
    Context class for file operations.
    
    This class maintains a reference to a strategy and delegates
    file operations to the appropriate strategy instance.
    """
    
    def __init__(self, strategy: FileOperationStrategy):
        """
        Initialize the file operation context.
        
        Args:
            strategy: The initial strategy to use
        """
        self._strategy = strategy
    
    @property
    def strategy(self) -> FileOperationStrategy:
        """Get the current strategy."""
        return self._strategy
    
    @strategy.setter
    def strategy(self, strategy: FileOperationStrategy):
        """
        Set the strategy to use.
        
        Args:
            strategy: The new strategy to use
        """
        self._strategy = strategy
    
    def execute(self, *args, **kwargs) -> Any:
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
strategy_registry: Dict[str, FileOperationStrategy] = {}


def register_strategy(strategy: FileOperationStrategy) -> None:
    """
    Register a strategy in the global registry.
    
    Args:
        strategy: Strategy to register
    """
    strategy_registry[strategy.name] = strategy


def get_strategy(name: str) -> FileOperationStrategy:
    """
    Get a strategy from the global registry.
    
    Args:
        name: Name of the strategy to get
        
    Returns:
        The requested strategy
        
    Raises:
        KeyError: If the strategy is not registered
    """
    if name not in strategy_registry:
        raise KeyError(f"Strategy not registered: {name}")
    return strategy_registry[name]


def create_default_strategies(
    dry_run: bool = False, 
    compression_level: int = 6,
    duplicate_handler: Optional[DuplicateHandler] = None
) -> Dict[str, FileOperationStrategy]:
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
        "move_file": MoveFileStrategy(dry_run, duplicate_handler),
        "copy_file": CopyFileStrategy(dry_run, duplicate_handler),
        "archive": ArchiveStrategy(compression_level, dry_run, duplicate_handler),
        "extract_archive": ExtractArchiveStrategy(dry_run, duplicate_handler),
        "rename_file": RenameFileStrategy(dry_run, duplicate_handler)
    }
    
    # Register the strategies
    for name, strategy in strategies.items():
        register_strategy(strategy)
    
    return strategies