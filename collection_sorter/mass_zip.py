import logging
import argparse
from pathlib import Path
from typing import List, Optional, Sequence

from collection_sorter.common.sorter import MultiThreadTask, SortExecutor
from collection_sorter.common.config import SortConfig
from collection_sorter.common.archive import ArchivedCollection

logger = logging.getLogger(__name__)

def parse_args(args: Optional[Sequence[str]] = None) -> argparse.Namespace:
    """Parse command line arguments for zip operations.
    
    Args:
        args: Command line arguments to parse. If None, sys.argv[1:] is used.
    
    Returns:
        Parsed command line arguments.
    """
    parser = argparse.ArgumentParser(
        description="Create archives from collections of files and directories"
    )
    parser.add_argument(
        "sources",
        nargs="+",
        type=str,
        help="Source directories to process"
    )
    parser.add_argument(
        "-d", "--destination",
        help="Destination folder for archives",
        type=str,
        default=None
    )
    parser.add_argument(
        "-a", "--archive",
        help="Create nested archives",
        action="store_true"
    )
    parser.add_argument(
        "-m", "--move",
        help="Remove source files after processing",
        action="store_true"
    )
    
    return parser.parse_args(args)


class ZipCollections(MultiThreadTask):
    """Task for creating archives from collections of files.
    
    Handles creating zip archives from directories, with options for nested archives
    and cleanup of source files.
    """
    
    def __init__(
        self,
        archive: bool = False,
        remove: bool = False
    ) -> None:
        """Initialize the zip collections task.
        
        Args:
            archive: Whether to create nested archives
            remove: Whether to remove source files after processing
        """
        self._archive = archive
        self._remove = remove
        # Config will be initialized in execute() when we have the source path
        self._config = None

    def execute(self, source: Path, destination: Optional[Path] = None) -> None:
        """Execute the zip operation on a single source.
        
        Args:
            source: Source directory to process
            destination: Optional destination directory for the archive
        
        Raises:
            FileNotFoundError: If source directory doesn't exist
        """
        if not source.exists():
            raise FileNotFoundError(f"Source directory not found: {source}")
        
        # Initialize config with source path
        if self._config is None:
            self._config = SortConfig(source_path=source)
            super().__init__(config=self._config)
            
        try:
            collection = ArchivedCollection(source)
            logger.info(f"Processing collection: {source}")
            collection = collection.archive_folders(zip_parent=True)
            logger.info(f"Successfully archived: {source}")
        except Exception as e:
            logger.error(f"Failed to process {source}: {str(e)}")
            raise


def zip_collections(
    sources: List[str],
    destination: Optional[str] = None,
    archive: bool = False,
    move: bool = False
) -> None:
    """Process multiple collections for archiving.
    
    Args:
        sources: List of source directory paths
        destination: Optional destination directory
        archive: Whether to create nested archives
        move: Whether to remove source files after processing
    """
    logger.info(f"Processing sources: {sources}")
    logger.info(f"Destination: {destination}")
    
    task = ZipCollections(archive=archive, remove=move)
    sorter = SortExecutor()
    
    for source in sources:
        try:
            root = Path(source)
            collection = ArchivedCollection(root)
            sorter.sort(
                collection=collection,
                destination=Path(destination) if destination else None,
                task=task
            )
            logger.info(f"Successfully processed: {source}")
        except Exception as e:
            logger.error(f"Failed to process {source}: {str(e)}")
            continue


