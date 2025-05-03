"""
File operations using the Result pattern for Collection Sorter.

This module provides file operations that use the Result pattern
for better error handling and composability.
"""

import logging
import os
import shutil
import zipfile
from pathlib import Path
from typing import Callable, List, Optional, Union

from collection_sorter.files.duplicates import DuplicateHandler, DuplicateStrategy
from .paths import FilePath, PathType
from collection_sorter.result import (
    Result, OperationError, ErrorType, PathResult, result_handler
)

logger = logging.getLogger("operations")


@result_handler
def check_path_exists(path: Union[str, Path, FilePath]) -> bool:
    """
    Check if a path exists.
    
    Args:
        path: Path to check
        
    Returns:
        True if the path exists, False otherwise
    """
    if isinstance(path, FilePath):
        return path.exists
    else:
        return Path(path).exists()


@result_handler
def ensure_directory(path: Union[str, Path, FilePath]) -> Path:
    """
    Ensure a directory exists, creating it if needed.
    
    Args:
        path: Directory path
        
    Returns:
        Path to the directory
    """
    if isinstance(path, FilePath):
        dir_path = path.path
    else:
        dir_path = Path(path)
        
    dir_path.mkdir(parents=True, exist_ok=True)
    return dir_path


@result_handler
def list_files(path: Union[str, Path, FilePath]) -> List[Path]:
    """
    List all files in a directory.
    
    Args:
        path: Directory path
        
    Returns:
        List of file paths
    """
    if isinstance(path, FilePath):
        dir_path = path.path
    else:
        dir_path = Path(path)
    
    if not dir_path.exists():
        raise FileNotFoundError(f"Directory not found: {dir_path}")
    
    if not dir_path.is_dir():
        raise NotADirectoryError(f"Not a directory: {dir_path}")
    
    return [f for f in dir_path.iterdir() if f.is_file()]


@result_handler
def list_directories(path: Union[str, Path, FilePath]) -> List[Path]:
    """
    List all subdirectories in a directory.
    
    Args:
        path: Directory path
        
    Returns:
        List of directory paths
    """
    if isinstance(path, FilePath):
        dir_path = path.path
    else:
        dir_path = Path(path)
    
    if not dir_path.exists():
        raise FileNotFoundError(f"Directory not found: {dir_path}")
    
    if not dir_path.is_dir():
        raise NotADirectoryError(f"Not a directory: {dir_path}")
    
    return [d for d in dir_path.iterdir() if d.is_dir()]


@result_handler
def move_file(
    source: Union[str, Path, FilePath],
    destination: Union[str, Path, FilePath],
    duplicate_handler: Optional[DuplicateHandler] = None,
    dry_run: bool = False
) -> Path:
    """
    Move a file to a new location with result-based error handling.
    
    Args:
        source: Source file path
        destination: Destination file path
        duplicate_handler: Optional handler for duplicates
        dry_run: Whether to simulate operations without making changes
        
    Returns:
        Path to the destination file
    """
    # Convert to Path objects
    src_path = FilePath(source, PathType.FILE).path
    dst_path = FilePath(destination, must_exist=False).path
    
    # Make sure the destination directory exists
    dst_path.parent.mkdir(parents=True, exist_ok=True)
    
    # Handle duplicates if the destination exists
    final_dst_path = dst_path
    is_duplicate = False
    
    if dst_path.exists():
        if duplicate_handler:
            # Use the duplicate handler
            final_dst_path, is_duplicate = duplicate_handler.handle_duplicate(
                dst_path, 
                dst_path,  # Existing path is the same as new path
                context=f"Moving {src_path}"
            )
        else:
            # Default behavior - rename the destination
            identifier = "1"
            counter = 1
            while final_dst_path.exists():
                stem = dst_path.stem
                suffix = dst_path.suffix
                final_dst_path = dst_path.with_name(f"{stem}_{identifier}{suffix}")
                counter += 1
                identifier = str(counter)
            is_duplicate = True
    
    # If the duplicate strategy is SKIP, don't do anything
    if is_duplicate and duplicate_handler and duplicate_handler.strategy == DuplicateStrategy.SKIP:
        logger.info(f"Skipping duplicate file: {src_path}")
        return dst_path
    
    # Move the file
    if dry_run:
        logger.info(f"Would move: {src_path} -> {final_dst_path}")
        return final_dst_path
    
    # Perform the actual move
    shutil.move(src_path, final_dst_path)
    logger.info(f"Moved: {src_path} -> {final_dst_path}")
    return final_dst_path


@result_handler
def copy_file(
    source: Union[str, Path, FilePath],
    destination: Union[str, Path, FilePath],
    duplicate_handler: Optional[DuplicateHandler] = None,
    dry_run: bool = False
) -> Path:
    """
    Copy a file to a new location with result-based error handling.
    
    Args:
        source: Source file path
        destination: Destination file path
        duplicate_handler: Optional handler for duplicates
        dry_run: Whether to simulate operations without making changes
        
    Returns:
        Path to the destination file
    """
    # Convert to Path objects
    src_path = FilePath(source, PathType.FILE).path
    dst_path = FilePath(destination, must_exist=False).path
    
    # Make sure the destination directory exists
    dst_path.parent.mkdir(parents=True, exist_ok=True)
    
    # Handle duplicates if the destination exists
    final_dst_path = dst_path
    is_duplicate = False
    
    if dst_path.exists():
        if duplicate_handler:
            # Use the duplicate handler
            final_dst_path, is_duplicate = duplicate_handler.handle_duplicate(
                dst_path, 
                dst_path,  # Existing path is the same as new path
                context=f"Copying {src_path}"
            )
        else:
            # Default behavior - rename the destination
            identifier = "1"
            counter = 1
            while final_dst_path.exists():
                stem = dst_path.stem
                suffix = dst_path.suffix
                final_dst_path = dst_path.with_name(f"{stem}_{identifier}{suffix}")
                counter += 1
                identifier = str(counter)
            is_duplicate = True
    
    # If the duplicate strategy is SKIP, don't do anything
    if is_duplicate and duplicate_handler and duplicate_handler.strategy == DuplicateStrategy.SKIP:
        logger.info(f"Skipping duplicate file: {src_path}")
        return dst_path
    
    # Copy the file
    if dry_run:
        logger.info(f"Would copy: {src_path} -> {final_dst_path}")
        return final_dst_path
    
    # Perform the actual copy
    shutil.copy2(src_path, final_dst_path)
    logger.info(f"Copied: {src_path} -> {final_dst_path}")
    return final_dst_path


@result_handler
def rename_file(
    source: Union[str, Path, FilePath],
    new_name: Union[str, Path, FilePath],
    duplicate_handler: Optional[DuplicateHandler] = None,
    dry_run: bool = False
) -> Path:
    """
    Rename a file with result-based error handling.
    
    Args:
        source: Source file path
        new_name: New file name or path
        duplicate_handler: Optional handler for duplicates
        dry_run: Whether to simulate operations without making changes
        
    Returns:
        Path to the renamed file
    """
    # Convert to Path objects
    src_path = FilePath(source).path
    
    # Handle new_name as either a name or a full path
    if isinstance(new_name, (str, Path)) and ('/' not in str(new_name) and '\\' not in str(new_name)):
        # Just a name, not a path
        dst_path = src_path.parent / new_name
    else:
        # Full path
        dst_path = FilePath(new_name, must_exist=False).path
    
    # Make sure the destination directory exists
    dst_path.parent.mkdir(parents=True, exist_ok=True)
    
    # Handle duplicates if the destination exists
    final_dst_path = dst_path
    is_duplicate = False
    
    if dst_path.exists() and dst_path != src_path:
        if duplicate_handler:
            # Use the duplicate handler
            final_dst_path, is_duplicate = duplicate_handler.handle_duplicate(
                dst_path, 
                dst_path,  # Existing path is the same as new path
                context=f"Renaming {src_path}"
            )
        else:
            # Default behavior - rename the destination
            identifier = "1"
            counter = 1
            while final_dst_path.exists() and final_dst_path != src_path:
                stem = dst_path.stem
                suffix = dst_path.suffix
                final_dst_path = dst_path.with_name(f"{stem}_{identifier}{suffix}")
                counter += 1
                identifier = str(counter)
            is_duplicate = True
    
    # If the duplicate strategy is SKIP, don't do anything
    if is_duplicate and duplicate_handler and duplicate_handler.strategy == DuplicateStrategy.SKIP:
        logger.info(f"Skipping rename due to duplicate: {src_path}")
        return src_path
    
    # Rename the file
    if dry_run:
        logger.info(f"Would rename: {src_path} -> {final_dst_path}")
        return final_dst_path
    
    # Perform the actual rename
    os.rename(src_path, final_dst_path)
    logger.info(f"Renamed: {src_path} -> {final_dst_path}")
    return final_dst_path


@result_handler
def archive_directory(
    source: Union[str, Path, FilePath],
    destination: Optional[Union[str, Path, FilePath]] = None,
    archive_name: Optional[str] = None,
    compression_level: int = 6,
    duplicate_handler: Optional[DuplicateHandler] = None,
    dry_run: bool = False
) -> Path:
    """
    Archive a directory to a ZIP file with result-based error handling.
    
    Args:
        source: Source directory to archive
        destination: Optional destination for the archive
        archive_name: Optional name for the archive
        compression_level: ZIP compression level (0-9)
        duplicate_handler: Optional handler for duplicates
        dry_run: Whether to simulate operations without making changes
        
    Returns:
        Path to the created archive
    """
    # Convert to Path objects
    src_path = FilePath(source, PathType.DIRECTORY).path
    
    # Determine archive name
    name = archive_name or src_path.name
    archive_filename = f"{name}.zip"
    
    # Determine destination path
    if destination:
        dest_dir = FilePath(destination, PathType.DIRECTORY, create_if_missing=True).path
        archive_path = dest_dir / archive_filename
    else:
        dest_dir = src_path.parent
        archive_path = dest_dir / archive_filename
    
    # Handle duplicates if the destination exists
    final_archive_path = archive_path
    is_duplicate = False
    
    if archive_path.exists():
        if duplicate_handler:
            # Use the duplicate handler
            final_archive_path, is_duplicate = duplicate_handler.handle_duplicate(
                archive_path, 
                archive_path,  # Existing path is the same as new path
                context=f"Creating archive for {src_path}"
            )
        else:
            # Default behavior - rename the destination
            identifier = "1"
            counter = 1
            while final_archive_path.exists():
                stem = archive_path.stem
                suffix = archive_path.suffix
                final_archive_path = archive_path.with_name(f"{stem}_{identifier}{suffix}")
                counter += 1
                identifier = str(counter)
            is_duplicate = True
    
    # If the duplicate strategy is SKIP, don't do anything
    if is_duplicate and duplicate_handler and duplicate_handler.strategy == DuplicateStrategy.SKIP:
        logger.info(f"Skipping duplicate archive: {archive_path}")
        return archive_path
    
    # Archive the directory
    if dry_run:
        logger.info(f"Would archive directory: {src_path} -> {final_archive_path}")
        return final_archive_path
    
    # Make sure the parent directory exists
    final_archive_path.parent.mkdir(parents=True, exist_ok=True)
    
    # Create the archive
    with zipfile.ZipFile(
        final_archive_path, 
        'w', 
        compression=zipfile.ZIP_DEFLATED,
        compresslevel=compression_level
    ) as zf:
        # Add files to the archive
        for root, dirs, files in os.walk(src_path):
            root_path = Path(root)
            for file in files:
                file_path = root_path / file
                # Calculate the path within the archive
                if archive_name:
                    # Use custom name as root in archive
                    rel_path = Path(archive_name) / file_path.relative_to(src_path)
                else:
                    # Use original directory structure
                    rel_path = file_path.relative_to(src_path.parent)
                # Add to archive
                zf.write(file_path, rel_path)
    
    logger.info(f"Archived directory: {src_path} -> {final_archive_path}")
    return final_archive_path


@result_handler
def extract_archive(
    source: Union[str, Path, FilePath],
    destination: Optional[Union[str, Path, FilePath]] = None,
    duplicate_handler: Optional[DuplicateHandler] = None,
    dry_run: bool = False
) -> Path:
    """
    Extract a ZIP archive with result-based error handling.
    
    Args:
        source: Source archive to extract
        destination: Optional destination directory
        duplicate_handler: Optional handler for duplicates
        dry_run: Whether to simulate operations without making changes
        
    Returns:
        Path to the extraction directory
    """
    # Convert to Path objects
    src_path = FilePath(source).path
    
    # Check that the source is a valid ZIP file
    if not src_path.exists():
        raise FileNotFoundError(f"Archive not found: {src_path}")
    
    if not src_path.is_file():
        raise IsADirectoryError(f"Not a file: {src_path}")
    
    if src_path.suffix.lower() != '.zip':
        raise ValueError(f"Not a ZIP archive: {src_path}")
    
    # Determine destination path
    if destination:
        dest_dir = FilePath(destination, PathType.DIRECTORY, must_exist=False).path
    else:
        # Extract to a directory with the same name as the archive (without extension)
        dest_dir = src_path.parent / src_path.stem
    
    # Handle duplicates if the destination exists
    final_dest_dir = dest_dir
    is_duplicate = False
    
    if dest_dir.exists():
        if duplicate_handler:
            # Use the duplicate handler
            final_dest_dir, is_duplicate = duplicate_handler.handle_duplicate(
                dest_dir, 
                dest_dir,  # Existing path is the same as new path
                context=f"Extracting archive {src_path}"
            )
        else:
            # Default behavior - rename the destination
            identifier = "1"
            counter = 1
            while final_dest_dir.exists():
                final_dest_dir = dest_dir.parent / f"{dest_dir.name}_{identifier}"
                counter += 1
                identifier = str(counter)
            is_duplicate = True
    
    # If the duplicate strategy is SKIP, don't do anything
    if is_duplicate and duplicate_handler and duplicate_handler.strategy == DuplicateStrategy.SKIP:
        logger.info(f"Skipping extraction to existing directory: {dest_dir}")
        return dest_dir
    
    # Extract the archive
    if dry_run:
        logger.info(f"Would extract archive: {src_path} -> {final_dest_dir}")
        return final_dest_dir
    
    # Make sure the destination directory exists
    final_dest_dir.mkdir(parents=True, exist_ok=True)
    
    # Extract the archive
    with zipfile.ZipFile(src_path) as zf:
        zf.extractall(final_dest_dir)
    
    logger.info(f"Extracted archive: {src_path} -> {final_dest_dir}")
    return final_dest_dir


@result_handler
def delete_file(
    path: Union[str, Path, FilePath],
    dry_run: bool = False
) -> Path:
    """
    Delete a file with result-based error handling.
    
    Args:
        path: Path to the file to delete
        dry_run: Whether to simulate operations without making changes
        
    Returns:
        Path to the deleted file
    """
    # Convert to Path object
    file_path = FilePath(path, PathType.FILE).path
    
    # Delete the file
    if dry_run:
        logger.info(f"Would delete file: {file_path}")
        return file_path
    
    # Perform the actual deletion
    os.unlink(file_path)
    logger.info(f"Deleted file: {file_path}")
    return file_path


@result_handler
def delete_directory(
    path: Union[str, Path, FilePath],
    recursive: bool = True,
    dry_run: bool = False
) -> Path:
    """
    Delete a directory with result-based error handling.
    
    Args:
        path: Path to the directory to delete
        recursive: Whether to delete recursively
        dry_run: Whether to simulate operations without making changes
        
    Returns:
        Path to the deleted directory
    """
    # Convert to Path object
    dir_path = FilePath(path, PathType.DIRECTORY).path
    
    # Delete the directory
    if dry_run:
        logger.info(f"Would delete directory: {dir_path}")
        return dir_path
    
    # Perform the actual deletion
    if recursive:
        shutil.rmtree(dir_path)
    else:
        os.rmdir(dir_path)
    
    logger.info(f"Deleted directory: {dir_path}")
    return dir_path


def chain_operations(operations: List[Callable[..., PathResult]]) -> Callable[..., PathResult]:
    """
    Chain multiple file operations together.
    
    Args:
        operations: List of operations to chain
        
    Returns:
        Function that executes the operations in sequence
    """
    def chained_operation(*args, **kwargs) -> PathResult:
        result = operations[0](*args, **kwargs)
        
        for op in operations[1:]:
            if result.is_failure():
                return result
            
            result = op(result.unwrap(), **kwargs)
        
        return result
    
    return chained_operation


# Composite operations using the chaining mechanism

def move_and_rename(
    source: Union[str, Path, FilePath],
    destination: Union[str, Path, FilePath],
    new_name: str,
    duplicate_handler: Optional[DuplicateHandler] = None,
    dry_run: bool = False
) -> PathResult:
    """
    Move a file and rename it.
    
    Args:
        source: Source file path
        destination: Destination directory
        new_name: New file name
        duplicate_handler: Optional handler for duplicates
        dry_run: Whether to simulate operations without making changes
        
    Returns:
        Result with path to the renamed file or error
    """
    # Move the file to the destination
    move_result = move_file(
        source, 
        destination, 
        duplicate_handler=duplicate_handler, 
        dry_run=dry_run
    )
    
    if move_result.is_failure():
        return move_result
    
    # Get the moved file path
    moved_path = move_result.unwrap()
    
    # Rename the file
    return rename_file(
        moved_path, 
        new_name, 
        duplicate_handler=duplicate_handler, 
        dry_run=dry_run
    )


def archive_and_delete(
    source: Union[str, Path, FilePath],
    destination: Optional[Union[str, Path, FilePath]] = None,
    archive_name: Optional[str] = None,
    compression_level: int = 6,
    duplicate_handler: Optional[DuplicateHandler] = None,
    dry_run: bool = False
) -> PathResult:
    """
    Archive a directory and then delete it.
    
    Args:
        source: Source directory to archive
        destination: Optional destination for the archive
        archive_name: Optional name for the archive
        compression_level: ZIP compression level (0-9)
        duplicate_handler: Optional handler for duplicates
        dry_run: Whether to simulate operations without making changes
        
    Returns:
        Result with path to the created archive or error
    """
    # Archive the directory
    archive_result = archive_directory(
        source, 
        destination, 
        archive_name=archive_name, 
        compression_level=compression_level, 
        duplicate_handler=duplicate_handler, 
        dry_run=dry_run
    )
    
    if archive_result.is_failure():
        return archive_result
    
    # Delete the directory if archiving was successful
    delete_result = delete_directory(source, recursive=True, dry_run=dry_run)
    
    if delete_result.is_failure():
        return Result.failure(OperationError(
            type=ErrorType.OPERATION_FAILED,
            message=f"Archive created but source directory could not be deleted: {delete_result.error()}",
            path=str(source)
        ))
    
    return archive_result