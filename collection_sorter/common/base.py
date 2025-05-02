from pathlib import Path
from typing import List, Optional, Union, Dict, Any
import logging
from abc import ABC, abstractmethod

from collection_sorter.common.exceptions import ConfigurationError
from collection_sorter.common.files import CollectionPath
from collection_sorter.common.move import move_file, move_folder

class BaseCollection(ABC):
    """
    Base class for all collection types.
    
    This abstract class provides common functionality for all collection types
    including file operations, moving, and archiving.
    
    Attributes:
        sources: List of source paths
        destination: Optional destination path
        dry_run: Flag to simulate operations without making changes
        logger: Logger instance
    """
    
    def __init__(
        self, 
        source: Union[List[str], str], 
        destination: Optional[str] = None,
        archive: bool = False,
        move: bool = False,
        dry_run: bool = False,
        interactive: bool = False,
        verbose: bool = False
    ):
        """
        Initialize a collection processor.
        
        Args:
            source: Source path(s) as string or list of strings
            destination: Optional destination path
            archive: Flag to create archives
            move: Flag to move files (remove source after processing)
            dry_run: Flag to simulate operations without making changes
            interactive: Flag to enable interactive prompts
            verbose: Flag to enable verbose logging
        """
        self.sources = [source] if isinstance(source, str) else source
        self.destination = Path(destination) if destination else None
        self.archive = archive
        self.move = move
        self.dry_run = dry_run
        self.interactive = interactive
        
        # Setup logging
        self.logger = logging.getLogger(self.__class__.__name__)
        self.logger.setLevel(logging.DEBUG if verbose else logging.INFO)
        
        # Validate configuration
        self._validate_config()
    
    def _validate_config(self) -> None:
        """
        Validate the collection configuration.
        
        Raises:
            ConfigurationError: If the configuration is invalid
        """
        # Check if source paths exist
        for source_path in self.sources:
            path = Path(source_path)
            if not path.exists():
                raise ConfigurationError(f"Source path does not exist: {source_path}")
        
        # Check if destination exists if provided
        if self.destination and not self.destination.exists():
            raise ConfigurationError(f"Destination path does not exist: {self.destination}")
    
    def process_sources(self) -> Dict[str, Any]:
        """
        Process all source paths.
        
        Returns:
            Dict with processing results
        """
        results = {}
        
        for source_path in self.sources:
            try:
                result = self.process_single_source(source_path)
                results[source_path] = result
            except Exception as e:
                self.logger.error(f"Error processing {source_path}: {str(e)}")
                results[source_path] = {"error": str(e), "success": False}
        
        return results
    
    @abstractmethod
    def process_single_source(self, source_path: str) -> Dict[str, Any]:
        """
        Process a single source path.
        
        Args:
            source_path: Source path as string
            
        Returns:
            Dict with processing results
        """
        pass
    
    def move_to_destination(self, source_path: str, processed_path: str) -> None:
        """
        Move processed files to destination if needed.
        
        Args:
            source_path: Original source path
            processed_path: Path with processed files
        """
        if not self.destination:
            return
        
        source = Path(source_path)
        processed = Path(processed_path)
        
        if source.is_file():
            if self.dry_run:
                self.logger.info(f"Would move {processed} to {self.destination}")
                return
            
            move_file(str(processed), str(self.destination))
        else:
            if self.dry_run:
                self.logger.info(f"Would move {processed} to {self.destination}")
                return
                
            move_folder(str(processed), str(self.destination))
    
    def cleanup_source(self, source_path: str) -> None:
        """
        Remove source files/folders if move flag is set.
        
        Args:
            source_path: Path to clean up
        """
        if not self.move:
            return
            
        path = Path(source_path)
        
        if self.dry_run:
            self.logger.info(f"Would remove {path}")
            return
            
        if path.is_file():
            path.unlink()
        else:
            collection = CollectionPath(path)
            collection.delete()