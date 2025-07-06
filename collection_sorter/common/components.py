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

# Forward references for type hints
FilePath = Union[str, Path, "FilePath"]
PathType = None  # Will be defined later after actual import

logger = logging.getLogger("components")


def _to_path(path) -> Path:
    """Convert a path-like object to a Path object."""
    if hasattr(path, "path"):  # FilePath-like object
        return path.path
    return Path(path).expanduser().resolve()


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

    def __init__(self, path: Union[str, Path, "FilePath"]):
        """
        Initialize the file collection component.

        Args:
            path: Root path for the collection
        """
        # Convert to Path directly to avoid circular import
        self._path = _to_path(path)

        # Will be replaced with actual FilePath once imports are resolved
        self.root_path = None

    def get_name(self) -> str:
        """Get the name of this component."""
        return "FileCollection"

    def get_files(self) -> List[Path]:
        """
        Get all files in the collection.

        Returns:
            List of file paths
        """
        if not self._path.is_dir():
            return [self._path] if self._path.is_file() else []

        return [p for p in self._path.iterdir() if p.is_file()]

    def get_directories(self) -> List[Path]:
        """
        Get all directories in the collection.

        Returns:
            List of directory paths
        """
        if not self._path.is_dir():
            return []

        return [p for p in self._path.iterdir() if p.is_dir()]

    def collect_all_files(self) -> List[Path]:
        """
        Recursively collect all files in the collection.

        Returns:
            List of all file paths
        """
        if not self._path.is_dir():
            return [self._path] if self._path.is_file() else []

        result = []

        # Add files in the root directory
        result.extend(self.get_files())

        # Recursively add files in subdirectories
        for directory in self.get_directories():
            subdir_component = FileCollectionComponent(directory)
            result.extend(subdir_component.collect_all_files())

        return result

    def map_files(self, function: Callable[[Path], None]) -> None:
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

    def __init__(self, dry_run: bool = False, create_parents: bool = True):
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
        source: Union[str, Path, "FilePath"],
        destination: Union[str, Path, "FilePath"],
    ) -> Path:
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
        src_path = _to_path(source)
        dest_path = _to_path(destination)

        # Verify source is a file
        if not src_path.is_file():
            raise FileOperationError(
                f"Source is not a file: {src_path}", path=str(src_path)
            )

        # Create parent directories if needed
        if self.create_parents:
            parent = dest_path.parent
            if not parent.exists() and not self.dry_run:
                parent.mkdir(parents=True, exist_ok=True)

        if self.dry_run:
            logger.info(f"Would move file: {src_path} -> {dest_path}")
            return dest_path

        try:
            import shutil

            return Path(shutil.move(src_path, dest_path))
        except Exception as e:
            raise FileOperationError(f"Failed to move file: {e}", path=str(src_path))

    def copy_file(
        self,
        source: Union[str, Path, "FilePath"],
        destination: Union[str, Path, "FilePath"],
    ) -> Path:
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
        src_path = _to_path(source)
        dest_path = _to_path(destination)

        # Verify source is a file
        if not src_path.is_file():
            raise FileOperationError(
                f"Source is not a file: {src_path}", path=str(src_path)
            )

        # Create parent directories if needed
        if self.create_parents:
            parent = dest_path.parent
            if not parent.exists() and not self.dry_run:
                parent.mkdir(parents=True, exist_ok=True)

        if self.dry_run:
            logger.info(f"Would copy file: {src_path} -> {dest_path}")
            return dest_path

        try:
            import shutil

            return Path(shutil.copy2(src_path, dest_path))
        except Exception as e:
            raise FileOperationError(f"Failed to copy file: {e}", path=str(src_path))

    def move_directory(
        self,
        source: Union[str, Path, "FilePath"],
        destination: Union[str, Path, "FilePath"],
    ) -> Path:
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
        src_path = _to_path(source)
        dest_path = _to_path(destination)

        # Verify source is a directory
        if not src_path.is_dir():
            raise FileOperationError(
                f"Source is not a directory: {src_path}", path=str(src_path)
            )

        # Create parent directories if needed
        if self.create_parents:
            parent = dest_path.parent
            if not parent.exists() and not self.dry_run:
                parent.mkdir(parents=True, exist_ok=True)

        if self.dry_run:
            logger.info(f"Would move directory: {src_path} -> {dest_path}")
            return dest_path

        try:
            import shutil

            return Path(shutil.move(src_path, dest_path))
        except Exception as e:
            raise FileOperationError(
                f"Failed to move directory: {e}", path=str(src_path)
            )

    def copy_directory(
        self,
        source: Union[str, Path, "FilePath"],
        destination: Union[str, Path, "FilePath"],
    ) -> Path:
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
        src_path = _to_path(source)
        dest_path = _to_path(destination)

        # Verify source is a directory
        if not src_path.is_dir():
            raise FileOperationError(
                f"Source is not a directory: {src_path}", path=str(src_path)
            )

        # Create parent directories if needed
        if self.create_parents:
            parent = dest_path.parent
            if not parent.exists() and not self.dry_run:
                parent.mkdir(parents=True, exist_ok=True)

        if self.dry_run:
            logger.info(f"Would copy directory: {src_path} -> {dest_path}")
            return dest_path

        try:
            import shutil

            return Path(shutil.copytree(src_path, dest_path))
        except Exception as e:
            raise FileOperationError(
                f"Failed to copy directory: {e}", path=str(src_path)
            )


class FileArchiverComponent(FileComponent):
    """
    Component for archiving files.

    This replaces the ArchivedCollection functionality with a more
    focused component that just handles archiving.
    """

    def __init__(self, compression_level: int = 6, dry_run: bool = False):
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

    def is_archive(self, path: Union[str, Path, "FilePath"]) -> bool:
        """
        Check if a path is an archive file.

        Args:
            path: Path to check

        Returns:
            True if the path is an archive file, False otherwise
        """
        file_path = _to_path(path)
        return (
            file_path.exists()
            and file_path.is_file()
            and file_path.suffix.lower() == ".zip"
        )

    def archive_directory(
        self,
        source: Union[str, Path, "FilePath"],
        destination: Optional[Union[str, Path, "FilePath"]] = None,
        archive_name: Optional[str] = None,
    ) -> Path:
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
        src_path = _to_path(source)

        # Verify source is a directory
        if not src_path.is_dir():
            raise FileOperationError(
                f"Source is not a directory: {src_path}", path=str(src_path)
            )

        # Determine archive name
        name = archive_name or src_path.name
        archive_filename = f"{name}.zip"

        # Determine destination path
        if destination:
            dest_path = _to_path(destination)
            if not dest_path.exists() and not self.dry_run:
                dest_path.mkdir(parents=True, exist_ok=True)
            archive_path = dest_path / archive_filename
        else:
            dest_path = src_path.parent
            archive_path = dest_path / archive_filename

        if self.dry_run:
            logger.info(f"Would archive directory: {src_path} -> {archive_path}")
            return archive_path

        try:
            # Create the archive
            with zipfile.ZipFile(
                archive_path,
                "w",
                compression=zipfile.ZIP_DEFLATED,
                compresslevel=self.compression_level,
            ) as zf:
                # Add files to the archive
                for file in FileCollectionComponent(src_path).collect_all_files():
                    # Calculate the path within the archive
                    if archive_name:
                        # Use custom name as root in archive
                        rel_path = Path(archive_name) / file.relative_to(src_path)
                    else:
                        # Use original directory structure
                        rel_path = file.relative_to(src_path.parent)

                    # Add to archive
                    zf.write(file, rel_path)

            logger.info(f"Archived directory: {src_path} -> {archive_path}")
            return archive_path

        except Exception as e:
            raise FileOperationError(
                f"Failed to create archive: {e}", path=str(src_path)
            )

    def extract_archive(
        self,
        source: Union[str, Path, "FilePath"],
        destination: Optional[Union[str, Path, "FilePath"]] = None,
    ) -> Path:
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
        src_path = _to_path(source)

        if not self.is_archive(src_path):
            raise FileOperationError(
                f"Not a ZIP archive: {src_path}", path=str(src_path)
            )

        # Determine destination path
        if destination:
            dest_path = _to_path(destination)
            if not dest_path.exists() and not self.dry_run:
                dest_path.mkdir(parents=True, exist_ok=True)
        else:
            # Extract to a directory with the same name as the archive (without extension)
            dest_path = src_path.parent / src_path.stem
            if not self.dry_run:
                dest_path.mkdir(parents=True, exist_ok=True)

        if self.dry_run:
            logger.info(f"Would extract archive: {src_path} -> {dest_path}")
            return dest_path

        try:
            # Extract the archive
            with zipfile.ZipFile(src_path) as zf:
                zf.extractall(dest_path)

            logger.info(f"Extracted archive: {src_path} -> {dest_path}")
            return dest_path

        except Exception as e:
            raise FileOperationError(
                f"Failed to extract archive: {e}", path=str(src_path)
            )


class FileCollection:
    """
    A collection of files with operations.

    This class demonstrates the composition approach, using specialized
    components for different aspects of file handling instead of inheritance.
    """

    def __init__(
        self,
        path: Union[str, Path, "FilePath"],
        dry_run: bool = False,
        compression_level: int = 6,
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
            compression_level=compression_level, dry_run=dry_run
        )

        # Store the root path
        self._path = _to_path(path)

    @property
    def path(self) -> Path:
        """Get the root path of the collection."""
        return self._path

    @property
    def name(self) -> str:
        """Get the name of the root path."""
        return self._path.name

    def get_files(self) -> List[Path]:
        """Get all files in the collection."""
        return self.collector.get_files()

    def get_directories(self) -> List[Path]:
        """Get all directories in the collection."""
        return self.collector.get_directories()

    def collect_all_files(self) -> List[Path]:
        """Recursively collect all files in the collection."""
        return self.collector.collect_all_files()

    def move_to(self, destination: Union[str, Path, "FilePath"]) -> "FileCollection":
        """
        Move the collection to a new location.

        Args:
            destination: Destination path

        Returns:
            New FileCollection at the destination
        """
        dest_path = _to_path(destination)

        if self._path.is_file():
            # Move a single file
            moved_path = self.mover.move_file(self._path, dest_path)
        else:
            # Move a directory
            moved_path = self.mover.move_directory(self._path, dest_path)

        # Return a new collection at the destination
        return FileCollection(
            moved_path,
            dry_run=self.mover.dry_run,
            compression_level=self.archiver.compression_level,
        )

    def copy_to(self, destination: Union[str, Path, "FilePath"]) -> "FileCollection":
        """
        Copy the collection to a new location.

        Args:
            destination: Destination path

        Returns:
            New FileCollection at the destination
        """
        dest_path = _to_path(destination)

        if self._path.is_file():
            # Copy a single file
            copied_path = self.mover.copy_file(self._path, dest_path)
        else:
            # Copy a directory
            copied_path = self.mover.copy_directory(self._path, dest_path)

        # Return a new collection at the destination
        return FileCollection(
            copied_path,
            dry_run=self.mover.dry_run,
            compression_level=self.archiver.compression_level,
        )

    def archive_to(
        self,
        destination: Optional[Union[str, Path, "FilePath"]] = None,
        archive_name: Optional[str] = None,
    ) -> Path:
        """
        Archive the collection to a ZIP file.

        Args:
            destination: Optional destination for the archive
            archive_name: Optional name for the archive

        Returns:
            Path to the created archive
        """
        if self._path.is_file():
            # Create a temporary directory with just this file
            import tempfile

            temp_dir = tempfile.mkdtemp()
            temp_path = Path(temp_dir)
            if not temp_path.exists():
                temp_path.mkdir(parents=True, exist_ok=True)

            # Copy the file to the temporary directory
            self.mover.copy_file(self._path, temp_path / self._path.name)

            # Archive the temporary directory
            archive_path = self.archiver.archive_directory(
                temp_path, destination, archive_name or self._path.stem
            )

            # Clean up
            if not self.mover.dry_run:
                import shutil

                shutil.rmtree(temp_dir)

            return archive_path
        else:
            # Archive the directory
            return self.archiver.archive_directory(
                self._path, destination, archive_name
            )

    def map_files(self, function: Callable[[Path], None]) -> None:
        """
        Apply a function to each file in the collection.

        Args:
            function: Function to apply to each file
        """
        self.collector.map_files(function)
