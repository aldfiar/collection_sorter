"""
File processor for Collection Sorter.

This module provides a flexible file processor that uses the Strategy pattern
to perform different file operations with consistent interface and error handling.
"""

import logging
from pathlib import Path
from typing import Dict, List, Optional, Set, Union, Any, Callable

from collection_sorter.common.duplicates import DuplicateHandler
from collection_sorter.common.exceptions import FileOperationError
from collection_sorter.common.paths import FilePath, DirectoryPath
from collection_sorter.common.strategies import (
    FileOperationStrategy, 
    FileOperationContext,
    MoveFileStrategy,
    CopyFileStrategy,
    ArchiveStrategy,
    ExtractArchiveStrategy,
    RenameFileStrategy,
    create_default_strategies
)

logger = logging.getLogger("file_processor")


class FileProcessor:
    """
    Processor for file operations with strategy support.
    
    This class provides a consistent interface for file operations
    using interchangeable strategies.
    """
    
    def __init__(
        self,
        dry_run: bool = False,
        compression_level: int = 6,
        duplicate_handler: Optional[DuplicateHandler] = None
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
        self.strategies = create_default_strategies(
            dry_run=dry_run,
            compression_level=compression_level,
            duplicate_handler=duplicate_handler
        )
        
        # Create the context with a default strategy
        self.context = FileOperationContext(self.strategies["move_file"])
    
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
    
    def add_strategy(self, name: str, strategy: FileOperationStrategy) -> None:
        """
        Add a new strategy.
        
        Args:
            name: Name for the strategy
            strategy: Strategy instance
        """
        self.strategies[name] = strategy
    
    def move_file(
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
        self.set_strategy("move_file")
        return self.context.execute(source, destination)
    
    def copy_file(
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
        self.set_strategy("copy_file")
        return self.context.execute(source, destination)
    
    def move_directory(
        self,
        source: Union[str, Path, FilePath],
        destination: Union[str, Path, FilePath]
    ) -> FilePath:
        """
        Move a directory to a new location.
        
        Args:
            source: Source directory path
            destination: Destination directory path
            
        Returns:
            Path to the destination directory
            
        Raises:
            FileOperationError: If the move operation fails
        """
        # Implementation using component composition
        from collection_sorter.common.components import FileCollectionComponent
        
        src_path = FilePath(source, DirectoryPath)
        dst_path = FilePath(destination, must_exist=False)
        
        # If destination doesn't exist, we can move the whole directory at once
        if not dst_path.exists:
            return self.move_file(src_path, dst_path)
        
        # If destination exists, we need to move files individually
        dst_path.path.mkdir(parents=True, exist_ok=True)
        
        # Get all files in the source directory
        collector = FileCollectionComponent(src_path)
        all_files = collector.collect_all_files()
        
        # Move each file individually
        for file in all_files:
            # Calculate relative path
            rel_path = file.path.relative_to(src_path.path)
            dest_file = dst_path.join(rel_path)
            
            # Create parent directories
            dest_file.parent.path.mkdir(parents=True, exist_ok=True)
            
            # Move the file
            self.move_file(file, dest_file)
        
        # Remove the source directory if it's empty
        if not self.dry_run and not any(src_path.path.iterdir()):
            src_path.path.rmdir()
            logger.info(f"Removed empty source directory: {src_path}")
        
        return dst_path
    
    def copy_directory(
        self,
        source: Union[str, Path, FilePath],
        destination: Union[str, Path, FilePath]
    ) -> FilePath:
        """
        Copy a directory to a new location.
        
        Args:
            source: Source directory path
            destination: Destination directory path
            
        Returns:
            Path to the destination directory
            
        Raises:
            FileOperationError: If the copy operation fails
        """
        # Implementation using component composition
        from collection_sorter.common.components import FileCollectionComponent
        
        src_path = FilePath(source, DirectoryPath)
        dst_path = FilePath(destination, must_exist=False)
        
        # Create destination directory
        dst_path.path.mkdir(parents=True, exist_ok=True)
        
        # Get all files in the source directory
        collector = FileCollectionComponent(src_path)
        all_files = collector.collect_all_files()
        
        # Copy each file individually
        for file in all_files:
            # Calculate relative path
            rel_path = file.path.relative_to(src_path.path)
            dest_file = dst_path.join(rel_path)
            
            # Create parent directories
            dest_file.parent.path.mkdir(parents=True, exist_ok=True)
            
            # Copy the file
            self.copy_file(file, dest_file)
        
        return dst_path
    
    def archive_directory(
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
        self.set_strategy("archive")
        return self.context.execute(source, destination, archive_name)
    
    def extract_archive(
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
        self.set_strategy("extract_archive")
        return self.context.execute(source, destination)
    
    def rename_file(
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
        self.set_strategy("rename_file")
        return self.context.execute(source, new_name)
    
    def process_collection(
        self,
        source: Union[str, Path, FilePath],
        operation: Callable,
        *args,
        **kwargs
    ) -> List[Any]:
        """
        Process all files in a collection with a given operation.
        
        Args:
            source: Source directory or file
            operation: Operation function to apply to each file
            *args: Additional positional arguments for the operation
            **kwargs: Additional keyword arguments for the operation
            
        Returns:
            List of operation results for each processed file
        """
        from collection_sorter.common.components import FileCollectionComponent
        
        # Create a collection component
        collector = FileCollectionComponent(source)
        
        # Get all files
        if isinstance(source, (str, Path)) and Path(source).is_file():
            files = [FilePath(source)]
        else:
            files = collector.collect_all_files()
        
        # Process each file
        results = []
        for file in files:
            try:
                result = operation(file, *args, **kwargs)
                results.append(result)
            except Exception as e:
                logger.error(f"Error processing {file}: {str(e)}")
                if not kwargs.get("continue_on_error", False):
                    raise
        
        return results
    
    def bulk_move(
        self,
        source: Union[str, Path, FilePath],
        destination: Union[str, Path, FilePath],
        continue_on_error: bool = False
    ) -> List[FilePath]:
        """
        Move all files in a collection to a new location.
        
        Args:
            source: Source directory or file
            destination: Destination directory
            continue_on_error: Whether to continue on error
            
        Returns:
            List of destination paths
        """
        return self.process_collection(
            source,
            self.move_file,
            destination,
            continue_on_error=continue_on_error
        )
    
    def bulk_copy(
        self,
        source: Union[str, Path, FilePath],
        destination: Union[str, Path, FilePath],
        continue_on_error: bool = False
    ) -> List[FilePath]:
        """
        Copy all files in a collection to a new location.
        
        Args:
            source: Source directory or file
            destination: Destination directory
            continue_on_error: Whether to continue on error
            
        Returns:
            List of destination paths
        """
        return self.process_collection(
            source,
            self.copy_file,
            destination,
            continue_on_error=continue_on_error
        )
    
    def bulk_archive(
        self,
        source: Union[str, Path, FilePath],
        destination: Optional[Union[str, Path, FilePath]] = None,
        continue_on_error: bool = False
    ) -> List[FilePath]:
        """
        Archive all directories in a collection.
        
        Args:
            source: Source directory
            destination: Optional destination for archives
            continue_on_error: Whether to continue on error
            
        Returns:
            List of archive paths
        """
        from collection_sorter.common.components import FileCollectionComponent
        
        # Create a collection component
        collector = FileCollectionComponent(source)
        
        # Get all directories
        directories = collector.get_directories()
        
        # Archive each directory
        results = []
        for directory in directories:
            try:
                result = self.archive_directory(directory, destination)
                results.append(result)
            except Exception as e:
                logger.error(f"Error archiving {directory}: {str(e)}")
                if not continue_on_error:
                    raise
        
        return results