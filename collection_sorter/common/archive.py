"""
Deprecated compatibility module for ArchivedCollection.

This module provides a thin compatibility layer for legacy tests.
In real applications, use ArchiveDirectoryTemplate from collection_sorter.templates.templates instead.
"""

import warnings
import zipfile
from pathlib import Path
from typing import Optional, Union, List

# Warn about deprecation
warnings.warn(
    "ArchivedCollection is deprecated. Use ArchiveDirectoryTemplate from collection_sorter.templates.templates instead.",
    DeprecationWarning,
    stacklevel=2
)

# Import new implementation for compatibility
from collection_sorter.templates.templates import ArchiveDirectoryTemplate
from collection_sorter.files.duplicates import DuplicateHandler


class ArchivedCollection:
    """
    Legacy class for compatibility with test_archive.py.
    
    This class provides a basic API that maps to the new ArchiveDirectoryTemplate API.
    """
    
    def __init__(self, path: Union[str, Path]):
        """
        Initialize the ArchivedCollection class.
        
        Args:
            path: Path to a directory or zip file
        """
        self.path = Path(path)
        self._is_archive = self.path.suffix.lower() == ".zip" and self.path.exists()
        
        # Create a template for archive operations
        self.template = ArchiveDirectoryTemplate(
            dry_run=False,
            duplicate_handler=DuplicateHandler(
                strategy="rename_new",
                interactive=False,
                dry_run=False
            ),
            recursive=True,
            compression_level=6
        )
        
    def is_archive(self) -> bool:
        """
        Check if the path is an archive.
        
        Returns:
            True if the path is a zip file, False otherwise
        """
        return self._is_archive
    
    def exists(self) -> bool:
        """
        Check if the path exists.
        
        Returns:
            True if the path exists and is a valid archive or directory, False otherwise
        """
        if self._is_archive:
            # For empty zip files (just touched), return false
            return self.path.exists() and self.path.stat().st_size > 0
        return self.path.exists()
        
    def archive_directory(
        self,
        destination: Optional[Union[str, Path]] = None,
        archive_name: Optional[str] = None,
        new_name: Optional[str] = None,  # For backward compatibility
        remove_source: bool = False
    ) -> Path:
        """
        Archive the directory.
        
        Args:
            destination: Optional destination directory
            archive_name: Optional name for the archive file
            new_name: Optional new name for the archive (backward compatibility)
            remove_source: Whether to remove the source directory after archiving
            
        Returns:
            Path to the created archive
        """
        if self._is_archive:
            raise ValueError("Path is already an archive")
            
        # Determine destination path
        if destination:
            dest_path = Path(destination)
        else:
            dest_path = self.path.parent
        
        # Ensure directories exist for test compatibility
        if not self.path.exists():
            raise ValueError(f"Source path does not exist: {self.path}")
        
        if not self.path.is_dir():
            raise ValueError(f"Source path is not a directory: {self.path}")
            
        dest_path.mkdir(parents=True, exist_ok=True)
        
        # Manually create the zip file for compatibility
        if archive_name:
            zip_name = f"{archive_name}.zip"
        elif new_name:  # For backward compatibility
            zip_name = f"{new_name}.zip"
        else:
            zip_name = f"{self.path.name}.zip"
            
        zip_path = dest_path / zip_name
        
        # Direct zipfile implementation 
        with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
            for file in self.path.glob('**/*'):
                if file.is_file():
                    zipf.write(file, file.relative_to(self.path.parent))
        
        # Remove source if requested
        if remove_source and self.path.exists():
            import shutil
            if self.path.is_dir():
                shutil.rmtree(self.path)
            else:
                self.path.unlink()
                
        return zip_path
    
    def archive_folders(self) -> List[Path]:
        """
        Archive all folders in the directory.
        
        Returns:
            List of created archives
        """
        if self._is_archive:
            raise ValueError("Path is already an archive")
            
        archives = []
        
        # Process each directory
        for directory in self.path.glob('*'):
            if directory.is_dir():
                # Create an ArchivedCollection for the directory
                collection = ArchivedCollection(directory)
                
                # Archive the directory
                archive_path = collection.archive_directory()
                archives.append(archive_path)
                
        return archives
        
    def extract(self, destination: Optional[Union[str, Path]] = None) -> Path:
        """
        Extract the archive.
        
        Args:
            destination: Optional destination directory
            
        Returns:
            Path to the extraction directory
        """
        if not self._is_archive:
            raise ValueError("Path is not an archive")
            
        # Determine destination path
        if destination:
            dest_path = Path(destination)
        else:
            dest_path = self.path.parent / self.path.stem
            
        # Create the destination directory
        dest_path.mkdir(parents=True, exist_ok=True)
        
        # Extract the archive
        with zipfile.ZipFile(self.path, 'r') as zip_ref:
            zip_ref.extractall(dest_path)
            
        return dest_path