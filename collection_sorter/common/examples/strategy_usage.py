"""
Example usage of the Strategy pattern for file operations.

This module demonstrates how to use the Strategy pattern with
the FileProcessor class for file operations.
"""

import logging
from pathlib import Path
from typing import Optional, Union

from collection_sorter.common.file_processor import FileProcessor
from collection_sorter.common.duplicates import DuplicateHandler, DuplicateStrategy
from collection_sorter.common.paths import FilePath
from collection_sorter.common.strategies import FileOperationStrategy

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("strategy_example")


def main():
    """Example of using the FileProcessor with strategies."""
    
    # Create a duplicate handler with RENAME_NEW strategy
    duplicate_handler = DuplicateHandler(
        strategy=DuplicateStrategy.RENAME_NEW,
        dry_run=False
    )
    
    # Create the file processor
    processor = FileProcessor(
        dry_run=False,
        compression_level=6,
        duplicate_handler=duplicate_handler
    )
    
    # Define some example paths
    source_dir = Path("/path/to/source")
    destination_dir = Path("/path/to/destination")
    
    # Move a file with move_file strategy
    source_file = source_dir / "example.txt"
    destination_file = destination_dir / "example.txt"
    moved_file = processor.move_file(source_file, destination_file)
    logger.info(f"Moved file: {source_file} -> {moved_file}")
    
    # Copy a file with copy_file strategy
    source_file = source_dir / "example2.txt"
    destination_file = destination_dir / "example2.txt"
    copied_file = processor.copy_file(source_file, destination_file)
    logger.info(f"Copied file: {source_file} -> {copied_file}")
    
    # Archive a directory with archive strategy
    archived_file = processor.archive_directory(source_dir, destination_dir)
    logger.info(f"Archived directory: {source_dir} -> {archived_file}")
    
    # Custom strategy example: Create a new strategy that logs operations
    class LoggingStrategy(FileOperationStrategy):
        """Strategy that logs operations but doesn't perform them."""
        
        def __init__(self, operation_name: str):
            """Initialize with an operation name."""
            self._operation_name = operation_name
        
        @property
        def name(self) -> str:
            """Get the name of this strategy."""
            return f"Logging{self._operation_name}"
        
        def execute(
            self,
            source: Union[str, Path, FilePath],
            destination: Optional[Union[str, Path, FilePath]] = None,
            *args, **kwargs
        ) -> FilePath:
            """
            Log the operation without performing it.
            
            Args:
                source: Source path
                destination: Destination path
                
            Returns:
                Source path (unchanged)
            """
            logger.info(f"LOGGING ONLY - Would {self._operation_name}: {source} -> {destination}")
            return FilePath(source) if isinstance(source, (str, Path)) else source
    
    # Add the custom strategy to the processor
    processor.add_strategy("logging_move", LoggingStrategy("Move"))
    
    # Use the custom strategy
    processor.set_strategy("logging_move")
    result = processor.context.execute(source_file, destination_file)
    logger.info(f"Logging result: {result}")
    
    # Bulk operations example
    moved_files = processor.bulk_move(source_dir, destination_dir)
    logger.info(f"Moved {len(moved_files)} files")


if __name__ == "__main__":
    main()