import logging
import shutil
from pathlib import Path
from typing import Callable, Optional, Dict, List, Set, Union

from .files import CollectionPath
from .duplicates import DuplicateHandler, DuplicateStrategy
from .exceptions import FileOperationError, UserInterruptError

logger = logging.getLogger("move")


def move_file(
    source_path: Union[str, Path], 
    destination_path: Union[str, Path],
    duplicate_handler: Optional[DuplicateHandler] = None
) -> Path:
    """
    Move a file to a new location with duplicate handling.
    
    Args:
        source_path: Source file path
        destination_path: Destination file path
        duplicate_handler: Optional handler for duplicates
        
    Returns:
        Path to the destination file (may be different if duplicate)
        
    Raises:
        FileOperationError: If the move operation fails
    """
    src_path = Path(source_path).resolve()
    dst_path = Path(destination_path).resolve()
    
    # Make sure the source exists
    if not src_path.exists():
        raise FileOperationError(f"Source file does not exist: {src_path}", path=str(src_path))
    
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
    try:
        # Check if we're using MOVE_TO_DUPLICATES strategy
        if (duplicate_handler and 
            duplicate_handler.strategy == DuplicateStrategy.MOVE_TO_DUPLICATES and
            duplicate_handler.duplicates_dir):
            # Create the duplicates directory if needed
            if not duplicate_handler.dry_run:
                duplicate_handler.duplicates_dir.mkdir(parents=True, exist_ok=True)
        
        # Perform the actual move
        if not (duplicate_handler and duplicate_handler.dry_run):
            shutil.move(src_path, final_dst_path)
            logger.info(f"Moved: {src_path} -> {final_dst_path}")
        else:
            logger.info(f"Would move: {src_path} -> {final_dst_path}")
            
        return final_dst_path
        
    except Exception as e:
        raise FileOperationError(f"Failed to move file: {str(e)}", path=str(src_path))


def copy_file(
    source_path: Union[str, Path], 
    destination_path: Union[str, Path],
    duplicate_handler: Optional[DuplicateHandler] = None
) -> Path:
    """
    Copy a file to a new location with duplicate handling.
    
    Args:
        source_path: Source file path
        destination_path: Destination file path
        duplicate_handler: Optional handler for duplicates
        
    Returns:
        Path to the destination file (may be different if duplicate)
        
    Raises:
        FileOperationError: If the copy operation fails
    """
    src_path = Path(source_path).resolve()
    dst_path = Path(destination_path).resolve()
    
    # Make sure the source exists
    if not src_path.exists():
        raise FileOperationError(f"Source file does not exist: {src_path}", path=str(src_path))
    
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
    try:
        # Check if we're using MOVE_TO_DUPLICATES strategy
        if (duplicate_handler and 
            duplicate_handler.strategy == DuplicateStrategy.MOVE_TO_DUPLICATES and
            duplicate_handler.duplicates_dir):
            # Create the duplicates directory if needed
            if not duplicate_handler.dry_run:
                duplicate_handler.duplicates_dir.mkdir(parents=True, exist_ok=True)
        
        # Perform the actual copy
        if not (duplicate_handler and duplicate_handler.dry_run):
            shutil.copy2(src_path, final_dst_path)
            logger.info(f"Copied: {src_path} -> {final_dst_path}")
        else:
            logger.info(f"Would copy: {src_path} -> {final_dst_path}")
            
        return final_dst_path
        
    except Exception as e:
        raise FileOperationError(f"Failed to copy file: {str(e)}", path=str(src_path))


def move_folder(
    source_path: Union[str, Path], 
    destination_path: Union[str, Path],
    duplicate_handler: Optional[DuplicateHandler] = None
) -> Path:
    """
    Move a folder to a new location with duplicate handling.
    
    Args:
        source_path: Source folder path
        destination_path: Destination folder path
        duplicate_handler: Optional handler for duplicates
        
    Returns:
        Path to the destination folder
        
    Raises:
        FileOperationError: If the move operation fails
    """
    src_path = Path(source_path).resolve()
    dst_path = Path(destination_path).resolve()
    
    # Make sure the source exists
    if not src_path.exists():
        raise FileOperationError(f"Source folder does not exist: {src_path}", path=str(src_path))
    
    # If the destination doesn't exist, just move the folder directly
    if not dst_path.exists():
        try:
            # Make sure parent directory exists
            dst_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Perform the move
            if not (duplicate_handler and duplicate_handler.dry_run):
                shutil.move(src_path, dst_path)
                logger.info(f"Moved folder: {src_path} -> {dst_path}")
            else:
                logger.info(f"Would move folder: {src_path} -> {dst_path}")
                
            return dst_path
                
        except Exception as e:
            raise FileOperationError(f"Failed to move folder: {str(e)}", path=str(src_path))
    
    # The destination exists, move files individually with duplicate handling
    try:
        # Create the destination folder if it doesn't exist
        folder_name = src_path.name
        folder_dst = dst_path / folder_name
        
        # Handle folder duplicates
        final_folder_dst = folder_dst
        is_duplicate = False
        
        if folder_dst.exists():
            if duplicate_handler:
                # Use the duplicate handler
                final_folder_dst, is_duplicate = duplicate_handler.handle_duplicate(
                    folder_dst, 
                    folder_dst,  # Existing path is the same as new path 
                    context=f"Moving folder {src_path}"
                )
            else:
                # Default behavior - rename the destination
                identifier = "1"
                counter = 1
                while final_folder_dst.exists():
                    final_folder_dst = dst_path / f"{folder_name}_{identifier}"
                    counter += 1
                    identifier = str(counter)
                is_duplicate = True
                
        # If the duplicate strategy is SKIP, don't do anything
        if is_duplicate and duplicate_handler and duplicate_handler.strategy == DuplicateStrategy.SKIP:
            logger.info(f"Skipping duplicate folder: {src_path}")
            return folder_dst
                
        # Create the destination folder
        if not (duplicate_handler and duplicate_handler.dry_run):
            final_folder_dst.mkdir(parents=True, exist_ok=True)
            
            # Get all files and subfolders in the source folder
            for item in src_path.rglob('*'):
                if item.is_file():
                    # Calculate the relative path and create the destination path
                    rel_path = item.relative_to(src_path)
                    item_dst = final_folder_dst / rel_path
                    
                    # Create parent directories
                    item_dst.parent.mkdir(parents=True, exist_ok=True)
                    
                    # Move the file
                    move_file(item, item_dst, duplicate_handler)
                    
            # Remove the source folder if it's empty
            if not any(src_path.iterdir()):
                src_path.rmdir()
                logger.info(f"Removed empty source folder: {src_path}")
        else:
            logger.info(f"Would move folder contents: {src_path} -> {final_folder_dst}")
            
        return final_folder_dst
            
    except Exception as e:
        raise FileOperationError(f"Failed to move folder contents: {str(e)}", path=str(src_path))


class MovableCollection(CollectionPath):
    """
    A collection that can be moved or copied.
    
    Extends CollectionPath with move and copy operations.
    """
    
    def __init__(
        self, 
        path: Union[Path, str],
        duplicate_handler: Optional[DuplicateHandler] = None
    ) -> None:
        """
        Initialize a movable collection.
        
        Args:
            path: Path to the collection
            duplicate_handler: Optional handler for duplicates
        """
        super().__init__(path)
        self.duplicate_handler = duplicate_handler

    def _change(
        self, 
        new_path: Path, 
        command: Callable[[Path, Path, Optional[DuplicateHandler]], Path]
    ) -> "CollectionPath":
        """
        Apply a change command to all files in the collection.
        
        Args:
            new_path: Destination path
            command: Function to apply to each file
            
        Returns:
            CollectionPath to the destination
        """
        # Make sure the destination exists
        if not new_path.exists():
            new_path.mkdir(parents=True, mode=0o755)

        # Process each file
        for file in self.get_files():
            source_path = file.resolve()
            destination_path = new_path.joinpath(file.name).resolve()
            command(source_path, destination_path, self.duplicate_handler)

        logger.info(f"{command.__name__} from: {self._path} to: {new_path}")

        return CollectionPath(new_path)

    def copy(self, new_path: Path) -> CollectionPath:
        """
        Copy all files to a new location.
        
        Args:
            new_path: Destination path
            
        Returns:
            CollectionPath to the destination
        """
        return self._change(new_path, copy_file)

    def move(self, new_path: Path) -> CollectionPath:
        """
        Move all files to a new location.
        
        Args:
            new_path: Destination path
            
        Returns:
            CollectionPath to the destination
        """
        return self._change(new_path, move_file)
