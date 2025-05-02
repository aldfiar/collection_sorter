import logging
import uuid
from pathlib import Path
from typing import Optional, Union
from zipfile import ZIP_DEFLATED, ZipFile

from collection_sorter.common.files import CollectionPath
from collection_sorter.common.duplicates import DuplicateHandler
from collection_sorter.common.exceptions import FileOperationError

logger = logging.getLogger("archive")


class ArchivedCollection(CollectionPath):
    """
    A collection that can be archived.
    
    Extends CollectionPath with archive operations.
    """
    
    def __init__(
        self, 
        path: Union[Path, str],
        destination: Optional[Path] = None,
        move_source: bool = False,
        dry_run: bool = False,
        interactive: bool = False,
        verbose: bool = False,
        compression_level: int = 6,
        duplicate_handler: Optional[DuplicateHandler] = None
    ):
        """
        Initialize an archived collection.
        
        Args:
            path: Path to the collection
            destination: Optional destination for archives
            move_source: Whether to remove source after archiving
            dry_run: Whether to simulate operations without making changes
            interactive: Whether to use interactive mode
            verbose: Whether to use verbose logging
            compression_level: Compression level for ZIP files
            duplicate_handler: Optional handler for duplicates
        """
        super().__init__(path)
        self.destination = Path(destination) if destination else None
        self.move_source = move_source
        self.dry_run = dry_run
        self.interactive = interactive
        self.verbose = verbose
        self.compression_level = compression_level
        self.duplicate_handler = duplicate_handler

    def is_archive(self) -> bool:
        """
        Check if the path is an archive file.
        
        Returns:
            True if the path is a ZIP archive, False otherwise
        """
        return self._path.exists() and self._path.is_file() and self._path.suffix.lower() == '.zip'

    def archive_directory(
        self, 
        destination: Optional[Path] = None, 
        new_name: Optional[str] = None
    ) -> "ArchivedCollection":
        """
        Archive a directory to a ZIP file.
        
        Args:
            destination: Optional destination for the archive
            new_name: Optional name for the archive
            
        Returns:
            ArchivedCollection for the created archive
            
        Raises:
            FileOperationError: If archiving fails
        """
        # Determine the archive name
        if new_name:
            override_path = Path(new_name)
            name = new_name
        else:
            name = self._path.name

        # Create the zip filename
        zfn = f"{name}.zip"

        # Determine the destination path
        if destination:
            fzp = destination.joinpath(zfn)
        else:
            dest = self.destination if self.destination else self._path.parent
            fzp = dest.joinpath(zfn)

        # Handle duplicates if the destination exists
        if fzp.exists():
            if self.duplicate_handler:
                # Use the duplicate handler
                fzp, is_duplicate = self.duplicate_handler.handle_duplicate(
                    fzp, 
                    fzp,  # Existing path is the same as new path
                    context=f"Creating archive for {self._path}"
                )
                
                # If the duplicate strategy is SKIP, don't do anything
                if is_duplicate and self.duplicate_handler.strategy == "skip":
                    logger.info(f"Skipping duplicate archive: {fzp}")
                    return ArchivedCollection(fzp)
            else:
                # Default behavior - rename the existing file
                identifier = str(uuid.uuid4())
                ozfp = fzp.parent.joinpath(f"{name}_duplicate_{identifier}.zip")
                
                if not self.dry_run:
                    fzp.rename(ozfp)
                    logger.info(f"Renamed existing archive: {fzp} -> {ozfp}")
                else:
                    logger.info(f"Would rename existing archive: {fzp} -> {ozfp}")

        try:
            # Create the archive
            if not self.dry_run:
                # Make sure the parent directory exists
                fzp.parent.mkdir(parents=True, exist_ok=True)
                
                with ZipFile(fzp, "w", ZIP_DEFLATED, compresslevel=self.compression_level) as zf:
                    for file in self._path.iterdir():
                        arc = (
                            file.relative_to(self._path.parent)
                            if new_name is None
                            else override_path.joinpath(file.name)
                        )
                        zf.write(file, arc)
                        
                logger.info(f"Archived files from: {self._path} to {fzp}")
                
                # Remove source if requested
                if self.move_source:
                    if self._path.is_dir():
                        for item in list(self._path.iterdir()):
                            if item.is_file():
                                item.unlink()
                            elif item.is_dir():
                                import shutil
                                shutil.rmtree(item)
                        self._path.rmdir()
                        logger.info(f"Removed source directory: {self._path}")
            else:
                logger.info(f"Would archive files from: {self._path} to {fzp}")
                if self.move_source:
                    logger.info(f"Would remove source directory: {self._path}")
                    
            return ArchivedCollection(
                fzp,
                destination=self.destination,
                move_source=self.move_source,
                dry_run=self.dry_run,
                interactive=self.interactive,
                verbose=self.verbose,
                compression_level=self.compression_level,
                duplicate_handler=self.duplicate_handler
            )
            
        except Exception as e:
            raise FileOperationError(f"Failed to create archive: {str(e)}", path=str(self._path))

    def exists(self) -> bool:
        """
        Check if the archive exists and is not empty.
        
        Returns:
            True if the archive exists and is not empty, False otherwise
        """
        return self._path.exists() and self._path.stat().st_size > 0

    def archive_folders(self, zip_parent: bool = False) -> "ArchivedCollection":
        """
        Archive all folders in the directory.
        
        Args:
            zip_parent: Whether to archive the parent directory as well
            
        Returns:
            ArchivedCollection for the current directory
            
        Raises:
            FileOperationError: If archiving fails
        """
        try:
            # Get all folders in the directory
            folders = self.get_folders()
            
            # Archive each folder
            for directory in folders:
                # Create an ArchivedCollection for the folder
                folder_archive = ArchivedCollection(
                    directory,
                    destination=self.destination if self.destination else self._path,
                    move_source=self.move_source,
                    dry_run=self.dry_run,
                    interactive=self.interactive,
                    verbose=self.verbose,
                    compression_level=self.compression_level,
                    duplicate_handler=self.duplicate_handler
                )
                
                # Archive the folder
                folder_archive.archive_directory()
                
            # Archive the parent directory if requested
            if zip_parent:
                self.archive_directory(self._path.parent)
                
            logger.info(f"Archived {len(folders)} folders in {self._path}")
            
            return self
            
        except Exception as e:
            raise FileOperationError(f"Failed to archive folders: {str(e)}", path=str(self._path))
