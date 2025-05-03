"""
File path value objects for Collection Sorter.

This module provides value objects for working with file paths consistently
throughout the application, with proper validation and error handling.
"""

import shutil
from enum import Enum, auto
from pathlib import Path
from typing import List, Union

from collection_sorter.common.exceptions import FileOperationError


class PathType(Enum):
    """Types of paths that can be handled."""
    
    FILE = auto()
    DIRECTORY = auto()
    ANY = auto()  # Either file or directory
    NONEXISTENT = auto()  # Path that may not exist yet


class FilePath:
    """
    Value object representing a file path.
    
    This class encapsulates a path with validation and provides
    a consistent interface for path operations.
    """
    
    def __init__(
        self, 
        path: Union[str, Path, "FilePath"],
        path_type: PathType = PathType.ANY,
        must_exist: bool = True,
        create_if_missing: bool = False
    ):
        """
        Initialize a file path.
        
        Args:
            path: Path as string, Path object, or another FilePath
            path_type: Expected type of path (file, directory, or any)
            must_exist: Whether the path must exist
            create_if_missing: Whether to create the path if it doesn't exist
            
        Raises:
            FileOperationError: If validation fails
        """
        # Extract the raw path if given a FilePath
        if isinstance(path, FilePath):
            path = path.path
            
        # Convert to Path object and normalize
        self._path = Path(path).expanduser().resolve()
        
        # Handle creation if needed
        if create_if_missing and not self._path.exists():
            try:
                if path_type == PathType.DIRECTORY:
                    self._path.mkdir(parents=True, exist_ok=True)
                elif path_type == PathType.FILE:
                    self._path.parent.mkdir(parents=True, exist_ok=True)
                    self._path.touch()
            except Exception as e:
                raise FileOperationError(f"Failed to create path: {e}", path=str(self._path))
        
        # Validate existence if required
        if must_exist and not self._path.exists():
            raise FileOperationError(f"Path does not exist: {self._path}", path=str(self._path))
            
        # Validate path type if it exists
        if self._path.exists():
            if path_type == PathType.FILE and not self._path.is_file():
                raise FileOperationError(
                    f"Expected a file but got a directory: {self._path}", 
                    path=str(self._path)
                )
            elif path_type == PathType.DIRECTORY and not self._path.is_dir():
                raise FileOperationError(
                    f"Expected a directory but got a file: {self._path}", 
                    path=str(self._path)
                )
        
    @property
    def path(self) -> Path:
        """Get the underlying Path object."""
        return self._path
    
    @property
    def exists(self) -> bool:
        """Check if the path exists."""
        return self._path.exists()
    
    @property
    def is_file(self) -> bool:
        """Check if the path is a file."""
        return self._path.is_file()
    
    @property
    def is_directory(self) -> bool:
        """Check if the path is a directory."""
        return self._path.is_dir()
    
    @property
    def name(self) -> str:
        """Get the name component of the path."""
        return self._path.name
    
    @property
    def stem(self) -> str:
        """Get the stem (filename without extension) of the path."""
        return self._path.stem
    
    @property
    def suffix(self) -> str:
        """Get the suffix (extension) of the path."""
        return self._path.suffix
    
    @property
    def parent(self) -> "FilePath":
        """Get the parent directory of the path."""
        return FilePath(self._path.parent, PathType.DIRECTORY)
    
    def with_name(self, name: str) -> "FilePath":
        """
        Return a new path with the name changed.
        
        Args:
            name: New filename
            
        Returns:
            New FilePath with changed name
        """
        return FilePath(
            self._path.with_name(name), 
            must_exist=False
        )
    
    def with_suffix(self, suffix: str) -> "FilePath":
        """
        Return a new path with the suffix changed.
        
        Args:
            suffix: New suffix (extension)
            
        Returns:
            New FilePath with changed suffix
        """
        return FilePath(
            self._path.with_suffix(suffix), 
            must_exist=False
        )
    
    def join(self, *parts: Union[str, Path]) -> "FilePath":
        """
        Join this path with additional parts.
        
        Args:
            *parts: Path parts to join
            
        Returns:
            New FilePath with joined parts
        """
        new_path = self._path.joinpath(*parts)
        return FilePath(new_path, must_exist=False)
    
    def list_dir(self) -> List["FilePath"]:
        """
        List all items in a directory.
        
        Returns:
            List of FilePath objects for all items in the directory
            
        Raises:
            FileOperationError: If not a directory or listing fails
        """
        if not self.is_directory:
            raise FileOperationError(f"Not a directory: {self._path}", path=str(self._path))
            
        try:
            return [FilePath(item) for item in self._path.iterdir()]
        except Exception as e:
            raise FileOperationError(f"Failed to list directory: {e}", path=str(self._path))
    
    def list_files(self) -> List["FilePath"]:
        """
        List all files in a directory.
        
        Returns:
            List of FilePath objects for all files in the directory
            
        Raises:
            FileOperationError: If not a directory or listing fails
        """
        return [item for item in self.list_dir() if item.is_file]
    
    def list_dirs(self) -> List["FilePath"]:
        """
        List all subdirectories in a directory.
        
        Returns:
            List of FilePath objects for all subdirectories in the directory
            
        Raises:
            FileOperationError: If not a directory or listing fails
        """
        return [item for item in self.list_dir() if item.is_directory]
    
    def delete(self) -> None:
        """
        Delete the file or directory.
        
        Raises:
            FileOperationError: If deletion fails
        """
        try:
            if not self.exists:
                return
                
            if self.is_file:
                self._path.unlink()
            else:
                shutil.rmtree(self._path)
        except Exception as e:
            raise FileOperationError(f"Failed to delete: {e}", path=str(self._path))
    
    def rename(self, new_name: Union[str, Path, "FilePath"]) -> "FilePath":
        """
        Rename this file or directory.
        
        Args:
            new_name: New name or path
            
        Returns:
            FilePath to the new location
            
        Raises:
            FileOperationError: If rename fails
        """
        try:
            if isinstance(new_name, FilePath):
                new_path = new_name.path
            else:
                new_path = Path(new_name)
                
            # Make sure the parent directory exists
            new_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Perform the rename
            renamed_path = self._path.rename(new_path)
            return FilePath(renamed_path)
            
        except Exception as e:
            raise FileOperationError(f"Failed to rename: {e}", path=str(self._path))
    
    def copy_to(self, destination: Union[str, Path, "FilePath"]) -> "FilePath":
        """
        Copy this file or directory to a new location.
        
        Args:
            destination: Destination path
            
        Returns:
            FilePath to the new copy
            
        Raises:
            FileOperationError: If copy fails
        """
        try:
            if isinstance(destination, FilePath):
                dest_path = destination.path
            else:
                dest_path = Path(destination)
                
            # Make sure the parent directory exists
            dest_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Copy file or directory
            if self.is_file:
                copied_path = shutil.copy2(self._path, dest_path)
                return FilePath(copied_path)
            else:
                copied_path = shutil.copytree(self._path, dest_path)
                return FilePath(copied_path)
                
        except Exception as e:
            raise FileOperationError(f"Failed to copy: {e}", path=str(self._path))
    
    def move_to(self, destination: Union[str, Path, "FilePath"]) -> "FilePath":
        """
        Move this file or directory to a new location.
        
        Args:
            destination: Destination path
            
        Returns:
            FilePath to the new location
            
        Raises:
            FileOperationError: If move fails
        """
        try:
            if isinstance(destination, FilePath):
                dest_path = destination.path
            else:
                dest_path = Path(destination)
                
            # Make sure the parent directory exists
            dest_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Move file or directory
            moved_path = shutil.move(self._path, dest_path)
            return FilePath(moved_path)
                
        except Exception as e:
            raise FileOperationError(f"Failed to move: {e}", path=str(self._path))
    
    def relative_to(self, other: Union[str, Path, "FilePath"]) -> Path:
        """
        Get this path relative to another path.
        
        Args:
            other: Base path
            
        Returns:
            Relative path
            
        Raises:
            FileOperationError: If relative path cannot be computed
        """
        try:
            if isinstance(other, FilePath):
                other_path = other.path
            else:
                other_path = Path(other)
                
            return self._path.relative_to(other_path)
                
        except Exception as e:
            raise FileOperationError(f"Failed to compute relative path: {e}", path=str(self._path))
    
    def __str__(self) -> str:
        """Get string representation of the path."""
        return str(self._path)
    
    def __repr__(self) -> str:
        """Get debug representation of the FilePath."""
        return f"FilePath({repr(str(self._path))})"
    
    def __eq__(self, other) -> bool:
        """Check if two FilePaths are equal."""
        if isinstance(other, FilePath):
            return self._path == other._path
        elif isinstance(other, (str, Path)):
            return self._path == Path(other).expanduser().resolve()
        return False
    
    def __hash__(self) -> int:
        """Get hash of the FilePath."""
        return hash(self._path)


class DirectoryPath(FilePath):
    """
    Value object representing a directory path.
    
    This is a convenience subclass of FilePath that enforces
    the path to be a directory.
    """
    
    def __init__(
        self, 
        path: Union[str, Path, FilePath],
        must_exist: bool = True,
        create_if_missing: bool = False
    ):
        """
        Initialize a directory path.
        
        Args:
            path: Path as string, Path object, or FilePath
            must_exist: Whether the path must exist
            create_if_missing: Whether to create the directory if it doesn't exist
            
        Raises:
            FileOperationError: If validation fails
        """
        super().__init__(
            path, 
            path_type=PathType.DIRECTORY,
            must_exist=must_exist,
            create_if_missing=create_if_missing
        )


class FileLike:
    """
    Interface for file-like objects.
    
    This provides a common interface for working with files,
    whether they're actual files or other objects that behave like files.
    """
    
    @property
    def path(self) -> Path:
        """Get the path to the file."""
        raise NotImplementedError
    
    @property
    def name(self) -> str:
        """Get the name of the file."""
        raise NotImplementedError
    
    def read_text(self) -> str:
        """Read the contents of the file as text."""
        raise NotImplementedError
    
    def read_bytes(self) -> bytes:
        """Read the contents of the file as bytes."""
        raise NotImplementedError
    
    def write_text(self, content: str) -> None:
        """Write text content to the file."""
        raise NotImplementedError
    
    def write_bytes(self, content: bytes) -> None:
        """Write binary content to the file."""
        raise NotImplementedError
    
    def delete(self) -> None:
        """Delete the file."""
        raise NotImplementedError