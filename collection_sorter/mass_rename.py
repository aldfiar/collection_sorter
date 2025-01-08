import argparse
import logging
import re
import uuid
from pathlib import Path
from typing import List, Optional

from .common.sorter import BaseCollection, MultiThreadTask, SortExecutor

logger = logging.getLogger(__name__)

class FileNameCleaner:
    """Handles cleaning and standardizing file names."""
    
    @staticmethod
    def clean_name(filename: str) -> str:
        """
        Clean filename by removing bracketed content and dates.
        
        Args:
            filename: Original filename
            
        Returns:
            Cleaned filename
        """
        # Remove extension temporarily
        name_parts = filename.rsplit('.', 1)
        name = name_parts[0]
        extension = name_parts[1] if len(name_parts) > 1 else ''
        
        # Remove content in brackets and dates
        name = re.sub(r'\[[^\]]*\]', '', name)  # Remove [content]
        name = re.sub(r'\([0-9]{4}\)', '', name)  # Remove (YYYY)
        name = re.sub(r'_+', '_', name)  # Replace multiple underscores
        name = name.strip('_').strip()  # Remove leading/trailing underscores and spaces
        
        # Preserve existing hyphens between words
        name = re.sub(r'\s*-\s*', ' - ', name)  # Standardize spacing around hyphens
        
        # Reconstruct filename with extension
        return f"{name}.{extension}" if extension else name

    @staticmethod
    def get_unique_name(path: Path) -> Path:
        """
        Generate unique filename if file already exists.
        
        Args:
            path: Original file path
            
        Returns:
            Path with unique filename
        """
        if not path.exists():
            return path
            
        name = path.stem
        suffix = path.suffix
        parent = path.parent
        
        new_name = f"{name}_duplicate_{uuid.uuid4().hex[:8]}{suffix}"
        return parent / new_name


class FileRenameTask(MultiThreadTask):
    """Task for renaming files according to cleaning rules."""

    def __init__(self, config=None) -> None:
        super().__init__(config or {})
        self.cleaner = FileNameCleaner()

    def execute(self, source: Path, destination: Optional[Path] = None) -> None:
        """
        Execute renaming task on source path.
        
        Args:
            source: Source path to process
            destination: Optional destination path (unused)
        """
        collection = BaseCollection(source)
        files = collection.collect_all()
        
        for file_path in files:
            if not file_path.is_file():
                continue
                
            # Clean the filename
            new_name = self.cleaner.clean_name(file_path.name)
            new_path = file_path.parent / new_name
            
            # Handle duplicates
            if new_path != file_path:
                new_path = self.cleaner.get_unique_name(new_path)
                try:
                    file_path.rename(new_path)
                    logger.info(f"Renamed: {file_path.name} -> {new_path.name}")
                except Exception as e:
                    logger.error(f"Failed to rename {file_path}: {e}")


def parse_args(args: Optional[List[str]] = None) -> argparse.Namespace:
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description="Rename files by cleaning names and removing unnecessary information"
    )
    parser.add_argument(
        "sources",
        nargs="+",
        help="Source directories or files to process"
    )
    return parser.parse_args(args)


def rename_files(sources: List[str]) -> None:
    """
    Rename files in the given source paths.
    
    Args:
        sources: List of source paths to process
    """
    logger.info(f"Processing sources: {sources}")
    sorter = SortExecutor()
    task = FileRenameTask()
    
    for source in sources:
        try:
            collection = BaseCollection(source)
            sorter.sort(collection=collection, task=task)
        except Exception as e:
            logger.error(f"Failed to process {source}: {e}")


def main() -> None:
    """Main entry point for the script."""
    args = parse_args()
    rename_files(args.sources)


if __name__ == "__main__":
    main()
