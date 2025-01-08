import logging
from pathlib import Path
from typing import Callable, Optional, Type, Dict, Any

from collection_sorter.common.sorter import BaseCollection, MultiThreadTask

from .manga import MangaParser
from .manga_template import manga_template_function

logger = logging.getLogger("manga_sorter")


class MangaCollection(BaseCollection):
    """Collection specifically for manga files and directories."""
    pass


class MangaSorter(MultiThreadTask):
    """Sorts manga files and directories according to a template.
    
    Handles parsing manga names, applying templates, and performing file operations
    like moving, copying and archiving.
    """

    def __init__(
        self,
        template: Callable[[Dict[str, Any], Optional[Callable]], str] = manga_template_function,
        archive: bool = False,
        replace_function: Optional[Callable[[str], str]] = None,
        parser: Type[MangaParser] = MangaParser,
        remove: bool = False,
    ) -> None:
        """Initialize the manga sorter.
    
        Args:
            template: Function to format manga info into a filename
            archive: Whether to create archives instead of directories
            replace_function: Optional function to clean up filenames
            parser: Class to parse manga filenames
            remove: Whether to remove source files after processing
        """
        super().__init__()
        self._config = None
        if not callable(template):
            raise ValueError("Template must be a callable")
        
        self._template = template
        self._archive = archive
        self._replace_function = replace_function
        self._parser = parser
        self._remove = remove

    def _create_destination(self, destination: Path, author: str) -> Path:
        """Creates and returns the destination directory for an author.
        
        Args:
            destination: Base destination directory
            author: Author name for subdirectory
            
        Returns:
            Path to the author's destination directory
        """
        manga_destination = destination.joinpath(author)
        with self._lock:
            if not manga_destination.exists():
                manga_destination.mkdir(parents=True, exist_ok=True)
        return manga_destination

    def _process_directory(
        self,
        directory: Path,
        manga_info: Dict[str, Any],
        collection: MangaCollection,
        destination: Path
    ) -> None:
        """Process a single directory.
        
        Args:
            directory: Directory to process
            manga_info: Parsed manga information
            collection: Collection being processed
            destination: Destination path
        """
        updated = manga_info.copy()
        updated["name"] = directory.name
        new_name = self._template(
            updated, symbol_replace_function=self._replace_function
        )
        self._directory_action(
            name=new_name,
            collection=collection,
            destination=destination,
        )

    def execute(self, source: Path, destination: Path) -> None:
        """Execute the sorting operation.
        
        Args:
            source: Source path to process
            destination: Destination for processed files
        """
        from collection_sorter.common.config import SortConfig
        
        # Create config for this execution
        self._config = SortConfig(
            source_path=source,
            destination_path=destination,
            archive=self._archive,
            remove_source=self._remove,
            rename_function=self._replace_function
        )
        
        try:
            collection = MangaCollection(source)
            
            # Process each directory in the source
            for directory in collection.get_folders():
                # Parse manga info from directory name
                manga_info = self._parser.parse(directory.name)
                
                # Create destination directory for this author
                manga_destination = self._create_destination(
                    destination, manga_info["author"]
                )

                # Create a collection for this specific manga directory
                manga_collection = MangaCollection(directory)
                
                # Generate new name from manga info
                new_name = self._template(
                    manga_info, symbol_replace_function=self._replace_function
                )
                
                if self._archive:
                    # Archive the directory
                    manga_collection.archive_directory(
                        destination=manga_destination,
                        new_name=new_name
                    )
                    if self._remove:
                        manga_collection.delete()
                else:
                    # Move or copy the directory
                    dest_path = manga_destination / new_name
                    if self._remove:
                        manga_collection.move(dest_path)
                    else:
                        manga_collection.copy(dest_path)
                
        except Exception as e:
            logger.error(f"Failed to process {source}: {str(e)}")
            raise

    def _directory_action(
        self, 
        name: str, 
        collection: MangaCollection, 
        destination: Path
    ) -> None:
        """Perform the requested action on a directory.
        
        Args:
            name: New name for the directory
            collection: Collection being processed
            destination: Destination path
        """
        logger.info(f"Processing collection: {collection}")

        try:
            if self._archive:
                archive = collection.archive_directory(
                    destination=destination, new_name=name
                )
                if archive.exists() and self._remove:
                    collection.delete()
            else:
                file_destination = destination.joinpath(name)
                if self._remove:
                    collection.move(file_destination)
                else:
                    collection.copy(file_destination)
        except Exception as e:
            logger.error(f"Directory action failed for {name}: {str(e)}")
            raise
