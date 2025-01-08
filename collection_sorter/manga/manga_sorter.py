import logging
import shutil
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
        author_folders: bool = False,
    ) -> None:
        """Initialize the manga sorter.
    
        Args:
            template: Function to format manga info into a filename
            archive: Whether to create archives instead of directories
            replace_function: Optional function to clean up filenames
            parser: Class to parse manga filenames
            remove: Whether to remove source files after processing
        """
        from collection_sorter.common.config import SortConfig
        # Initialize with a dummy path that will be replaced during execute()
        config = SortConfig(
            source_path=Path("."),
            archive=archive,
            remove_source=remove,
            rename_function=replace_function
        )
        super().__init__(config=config)
        if not callable(template):
            raise ValueError("Template must be a callable")
        
        self._template = template
        self._archive = archive
        self._replace_function = replace_function
        self._parser = parser
        self._remove = remove
        self._author_folders = author_folders

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

    def execute(self, source: Path, destination: Optional[Path] = None) -> None:
        """Execute the sorting operation.
        
        Args:
            source: Source path to process
            destination: Destination for processed files
        """
        if not destination:
            raise ValueError("Destination path is required")
            
        from collection_sorter.common.config import SortConfig
        
        # Create config for this execution
        self._config = SortConfig(
            source_path=source,
            destination_path=destination,
            archive=self._archive,
            remove_source=self._remove,
            rename_function=self._replace_function
        )

        if self._author_folders:
            # When processing author folders, preserve original names
            try:
                if self._archive:
                    collection = MangaCollection(source)
                    collection.archive_directory(
                        destination=destination,
                        new_name=source.name.replace(" ", "_")
                    )
                    if self._remove:
                        collection.delete()
                return
            except Exception as e:
                logger.error(f"Failed to process author folder {source}: {str(e)}")
                raise
        
        try:
            collection = MangaCollection(source)
            
            # Process each directory in the source
            for directory in collection.get_folders():
                try:
                    # Parse manga info from directory name
                    manga_info = self._parser.parse(directory.name)
                    
                    # Create destination directory for this author
                    manga_destination = self._create_destination(
                        destination, manga_info["author"]
                    )
                    
                    # Create a collection for this specific manga directory
                    manga_collection = MangaCollection(directory)
                    
                    # Use manga name directly from parsed info
                    new_name = manga_info["name"]
                    
                    if self._archive:
                        # Archive the directory
                        archive = manga_collection.archive_directory(
                            destination=manga_destination,
                            new_name=new_name
                        )
                        if self._remove and archive.exists:
                            manga_collection.delete()
                    else:
                        # Move or copy the directory
                        dest_path = manga_destination / new_name
                        if self._remove:
                            shutil.move(str(directory), str(dest_path))
                        else:
                            shutil.copytree(str(directory), str(dest_path))
                            
                except Exception as e:
                    logger.error(f"Failed to process directory {directory}: {str(e)}")
                    continue
                    
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
