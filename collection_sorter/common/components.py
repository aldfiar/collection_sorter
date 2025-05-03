"""
File operation components for Collection Sorter.

This module provides specialized components for file operations,
using composition instead of inheritance for better flexibility.
"""

import logging
import zipfile
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Callable, List, Optional, Union

from collection_sorter.common.exceptions import FileOperationError
from collection_sorter.common.paths import FilePath, PathType

logger = logging.getLogger("components")


class FileComponent(ABC):
    """Base class for file operation components."""
    
    @abstractmethod
    def get_name(self) -> str:
        """Get the name of this component."""
        pass


class FileCollectionComponent(FileComponent):
    """
    Component for managing a collection of files.
    
    This replaces the CollectionPath class with a more focused component
    that just handles file collection operations.
    """
    
    def __init__(self, path: Union[str, Path, FilePath]):
        """
        Initialize the file collection component.
        
        Args:
            path: Root path for the collection
        """
        self.root_path = FilePath(path)
    
    def get_name(self) -> str:
        """Get the name of this component."""
        return "FileCollection"
    
    def get_files(self) -> List[FilePath]:
        """
        Get all files in the collection.
        
        Returns:
            List of file paths
        """
        if not self.root_path.is_directory:
            return [self.root_path] if self.root_path.is_file else []
        
        return self.root_path.list_files()
    
    def get_directories(self) -> List[FilePath]:
        """
        Get all directories in the collection.
        
        Returns:
            List of directory paths
        """
        if not self.root_path.is_directory:
            return []
        
        return self.root_path.list_dirs()
    
    def collect_all_files(self) -> List[FilePath]:
        """
        Recursively collect all files in the collection.
        
        Returns:
            List of all file paths
        """
        if not self.root_path.is_directory:
            return [self.root_path] if self.root_path.is_file else []
        
        result = []
        
        # Add files in the root directory
        result.extend(self.get_files())
        
        # Recursively add files in subdirectories
        for directory in self.get_directories():
            subdir_component = FileCollectionComponent(directory)
            result.extend(subdir_component.collect_all_files())
        
        return result
    
    def map_files(self, function: Callable[[FilePath], None]) -> None:
        """
        Apply a function to each file in the collection.
        
        Args:
            function: Function to apply to each file
        """
        for file in self.get_files():
            function(file)


class FileMoverComponent(FileComponent):
    """
    Component for moving and copying files.
    
    This replaces the MovableCollection functionality with a more
    focused component that just handles moving and copying.
    """
    
    def __init__(
        self, 
        dry_run: bool = False,
        create_parents: bool = True
    ):
        """
        Initialize the file mover component.
        
        Args:
            dry_run: Whether to simulate operations without making changes
            create_parents: Whether to create parent directories when needed
        """
        self.dry_run = dry_run
        self.create_parents = create_parents
    
    def get_name(self) -> str:
        """Get the name of this component."""
        return "FileMover"
    
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
            Path to the moved file
            
        Raises:
            FileOperationError: If the move fails
        """
        src_path = FilePath(source, PathType.FILE)
        dest_path = FilePath(destination, must_exist=False)
        
        # Create parent directories if needed
        if self.create_parents:
            parent = dest_path.parent
            if not parent.exists and not self.dry_run:
                parent.path.mkdir(parents=True, exist_ok=True)
        
        if self.dry_run:
            logger.info(f"Would move file: {src_path} -> {dest_path}")
            return dest_path
        
        try:
            return src_path.move_to(dest_path)
        except Exception as e:
            raise FileOperationError(f"Failed to move file: {e}", path=str(src_path))
    
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
            Path to the copied file
            
        Raises:
            FileOperationError: If the copy fails
        """
        src_path = FilePath(source, PathType.FILE)
        dest_path = FilePath(destination, must_exist=False)
        
        # Create parent directories if needed
        if self.create_parents:
            parent = dest_path.parent
            if not parent.exists and not self.dry_run:
                parent.path.mkdir(parents=True, exist_ok=True)
        
        if self.dry_run:
            logger.info(f"Would copy file: {src_path} -> {dest_path}")
            return dest_path
        
        try:
            return src_path.copy_to(dest_path)
        except Exception as e:
            raise FileOperationError(f"Failed to copy file: {e}", path=str(src_path))
    
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
            Path to the moved directory
            
        Raises:
            FileOperationError: If the move fails
        """
        src_path = FilePath(source, PathType.DIRECTORY)
        dest_path = FilePath(destination, must_exist=False)
        
        # Create parent directories if needed
        if self.create_parents:
            parent = dest_path.parent
            if not parent.exists and not self.dry_run:
                parent.path.mkdir(parents=True, exist_ok=True)
        
        if self.dry_run:
            logger.info(f"Would move directory: {src_path} -> {dest_path}")
            return dest_path
        
        try:
            return src_path.move_to(dest_path)
        except Exception as e:
            raise FileOperationError(f"Failed to move directory: {e}", path=str(src_path))
    
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
            Path to the copied directory
            
        Raises:
            FileOperationError: If the copy fails
        """
        src_path = FilePath(source, PathType.DIRECTORY)
        dest_path = FilePath(destination, must_exist=False)
        
        # Create parent directories if needed
        if self.create_parents:
            parent = dest_path.parent
            if not parent.exists and not self.dry_run:
                parent.path.mkdir(parents=True, exist_ok=True)
        
        if self.dry_run:
            logger.info(f"Would copy directory: {src_path} -> {dest_path}")
            return dest_path
        
        try:
            return src_path.copy_to(dest_path)
        except Exception as e:
            raise FileOperationError(f"Failed to copy directory: {e}", path=str(src_path))


class FileArchiverComponent(FileComponent):
    """
    Component for archiving files.
    
    This replaces the ArchivedCollection functionality with a more
    focused component that just handles archiving.
    """
    
    def __init__(
        self,
        compression_level: int = 6,
        dry_run: bool = False
    ):
        """
        Initialize the file archiver component.
        
        Args:
            compression_level: ZIP compression level (0-9)
            dry_run: Whether to simulate operations without making changes
        """
        self.compression_level = compression_level
        self.dry_run = dry_run
    
    def get_name(self) -> str:
        """Get the name of this component."""
        return "FileArchiver"
    
    def is_archive(self, path: Union[str, Path, FilePath]) -> bool:
        """
        Check if a path is an archive file.
        
        Args:
            path: Path to check
            
        Returns:
            True if the path is an archive file, False otherwise
        """
        file_path = FilePath(path)
        return (
            file_path.exists and 
            file_path.is_file and 
            file_path.suffix.lower() == '.zip'
        )
    
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
        
        if self.dry_run:
            logger.info(f"Would archive directory: {src_path} -> {archive_path}")
            return FilePath(archive_path.path, must_exist=False)
        
        try:
            # Create the archive
            with zipfile.ZipFile(
                archive_path.path, 
                'w', 
                compression=zipfile.ZIP_DEFLATED,
                compresslevel=self.compression_level
            ) as zf:
                # Add files to the archive
                for file in FileCollectionComponent(src_path).collect_all_files():
                    # Calculate the path within the archive
                    if archive_name:
                        # Use custom name as root in archive
                        rel_path = Path(archive_name) / file.path.relative_to(src_path.path)
                    else:
                        # Use original directory structure
                        rel_path = file.path.relative_to(src_path.parent.path)
                    
                    # Add to archive
                    zf.write(file.path, rel_path)
            
            logger.info(f"Archived directory: {src_path} -> {archive_path}")
            return FilePath(archive_path.path)
            
        except Exception as e:
            raise FileOperationError(f"Failed to create archive: {e}", path=str(src_path))
    
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
        src_path = FilePath(source)
        
        if not self.is_archive(src_path):
            raise FileOperationError(f"Not a ZIP archive: {src_path}", path=str(src_path))
        
        # Determine destination path
        if destination:
            dest_dir = FilePath(destination, PathType.DIRECTORY, create_if_missing=True)
        else:
            # Extract to a directory with the same name as the archive (without extension)
            dest_dir = src_path.parent.join(src_path.stem)
            if not self.dry_run:
                dest_dir.path.mkdir(parents=True, exist_ok=True)
        
        if self.dry_run:
            logger.info(f"Would extract archive: {src_path} -> {dest_dir}")
            return dest_dir
        
        try:
            # Extract the archive
            with zipfile.ZipFile(src_path.path) as zf:
                zf.extractall(dest_dir.path)
            
            logger.info(f"Extracted archive: {src_path} -> {dest_dir}")
            return dest_dir
            
        except Exception as e:
            raise FileOperationError(f"Failed to extract archive: {e}", path=str(src_path))


class FileCollection:
    """
    A collection of files with operations.
    
    This class demonstrates the composition approach, using specialized
    components for different aspects of file handling instead of inheritance.
    """
    
    def __init__(
        self,
        path: Union[str, Path, FilePath],
        dry_run: bool = False,
        compression_level: int = 6
    ):
        """
        Initialize a file collection.
        
        Args:
            path: Root path for the collection
            dry_run: Whether to simulate operations without making changes
            compression_level: ZIP compression level (0-9)
        """
        # Create specialized components
        self.collector = FileCollectionComponent(path)
        self.mover = FileMoverComponent(dry_run=dry_run)
        self.archiver = FileArchiverComponent(
            compression_level=compression_level,
            dry_run=dry_run
        )
        
        # Store the root path
        self.root_path = self.collector.root_path
    
    @property
    def path(self) -> Path:
        """Get the root path of the collection."""
        return self.root_path.path
    
    @property
    def name(self) -> str:
        """Get the name of the root path."""
        return self.root_path.name
    
    def get_files(self) -> List[FilePath]:
        """Get all files in the collection."""
        return self.collector.get_files()
    
    def get_directories(self) -> List[FilePath]:
        """Get all directories in the collection."""
        return self.collector.get_directories()
    
    def collect_all_files(self) -> List[FilePath]:
        """Recursively collect all files in the collection."""
        return self.collector.collect_all_files()
    
    def move_to(self, destination: Union[str, Path, FilePath]) -> "FileCollection":
        """
        Move the collection to a new location.
        
        Args:
            destination: Destination path
            
        Returns:
            New FileCollection at the destination
        """
        dest_path = FilePath(destination, must_exist=False)
        
        if self.root_path.is_file:
            # Move a single file
            moved_path = self.mover.move_file(self.root_path, dest_path)
        else:
            # Move a directory
            moved_path = self.mover.move_directory(self.root_path, dest_path)
        
        # Return a new collection at the destination
        return FileCollection(
            moved_path,
            dry_run=self.mover.dry_run,
            compression_level=self.archiver.compression_level
        )
    
    def copy_to(self, destination: Union[str, Path, FilePath]) -> "FileCollection":
        """
        Copy the collection to a new location.
        
        Args:
            destination: Destination path
            
        Returns:
            New FileCollection at the destination
        """
        dest_path = FilePath(destination, must_exist=False)
        
        if self.root_path.is_file:
            # Copy a single file
            copied_path = self.mover.copy_file(self.root_path, dest_path)
        else:
            # Copy a directory
            copied_path = self.mover.copy_directory(self.root_path, dest_path)
        
        # Return a new collection at the destination
        return FileCollection(
            copied_path,
            dry_run=self.mover.dry_run,
            compression_level=self.archiver.compression_level
        )
    
    def archive_to(
        self,
        destination: Optional[Union[str, Path, FilePath]] = None,
        archive_name: Optional[str] = None
    ) -> FilePath:
        """
        Archive the collection to a ZIP file.
        
        Args:
            destination: Optional destination for the archive
            archive_name: Optional name for the archive
            
        Returns:
            Path to the created archive
        """
        if self.root_path.is_file:
            # Create a temporary directory with just this file
            import tempfile
            temp_dir = tempfile.mkdtemp()
            temp_path = FilePath(temp_dir, PathType.DIRECTORY, create_if_missing=True)
            
            # Copy the file to the temporary directory
            self.mover.copy_file(self.root_path, temp_path.join(self.root_path.name))
            
            # Archive the temporary directory
            archive_path = self.archiver.archive_directory(
                temp_path,
                destination,
                archive_name or self.root_path.stem
            )
            
            # Clean up
            if not self.mover.dry_run:
                import shutil
                shutil.rmtree(temp_dir)
            
            return archive_path
        else:
            # Archive the directory
            return self.archiver.archive_directory(
                self.root_path,
                destination,
                archive_name
            )
    
    def map_files(self, function: Callable[[FilePath], None]) -> None:
        """
        Apply a function to each file in the collection.
        
        Args:
            function: Function to apply to each file
        """
        self.collector.map_files(function)