"""
Example usage of the Result pattern for file operations.

This module demonstrates how to use the Result pattern with
the ResultFileProcessor class for file operations.
"""

import logging
from pathlib import Path
from typing import Optional, Union

from collection_sorter.common.duplicates import DuplicateHandler, DuplicateStrategy
from collection_sorter.common.paths import FilePath
from collection_sorter.common.result import Result, OperationError, ErrorType
from collection_sorter.common.result_processor import ResultFileProcessor

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("result_example")


def main():
    """Example of using the ResultFileProcessor with the Result pattern."""
    
    # Create a duplicate handler with RENAME_NEW strategy
    duplicate_handler = DuplicateHandler(
        strategy=DuplicateStrategy.RENAME_NEW,
        dry_run=False
    )
    
    # Create the file processor
    processor = ResultFileProcessor(
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
    
    # Example 1: Basic usage with direct result handling
    move_result = processor.move_file(source_file, destination_file)
    
    if move_result.is_success():
        moved_file = move_result.unwrap()
        logger.info(f"File moved successfully to: {moved_file}")
    else:
        error = move_result.error()
        logger.error(f"Failed to move file: {error}")
    
    # Example 2: Using map for transformations
    copy_result = processor.copy_file(source_file, destination_file)
    
    # Transform the result (e.g., convert the path to a string)
    path_str_result = copy_result.map(lambda path: str(path))
    
    # Continue processing with the transformed result
    path_str = path_str_result.unwrap_or("Operation failed")
    logger.info(f"Copy operation result: {path_str}")
    
    # Example 3: Using and_then for chaining operations
    def rename_after_copy(path):
        return processor.rename_file(path, f"{path.stem}_renamed{path.suffix}")
    
    # Copy and then rename the file
    copy_and_rename_result = processor.copy_file(source_file, destination_file).and_then(rename_after_copy)
    
    if copy_and_rename_result.is_success():
        final_path = copy_and_rename_result.unwrap()
        logger.info(f"File copied and renamed to: {final_path}")
    else:
        error = copy_and_rename_result.error()
        logger.error(f"Failed to copy and rename: {error}")
    
    # Example 4: Handling errors with unwrap_or and unwrap_or_else
    delete_result = processor.delete_file(source_file)
    
    # Provide a default value if the operation fails
    deleted_path = delete_result.unwrap_or(source_file)
    
    # Compute a different result based on the error
    def handle_delete_error(error):
        if error.type == ErrorType.FILE_NOT_FOUND:
            logger.warning(f"File already deleted: {error.path}")
            return Path(error.path)
        else:
            logger.error(f"Delete failed: {error}")
            return Path(".")
    
    fallback_path = delete_result.unwrap_or_else(handle_delete_error)
    
    # Example 5: Using bulk operations with result collection
    bulk_move_result = processor.bulk_move(source_dir, destination_dir)
    
    if bulk_move_result.is_success():
        moved_files = bulk_move_result.unwrap()
        logger.info(f"Moved {len(moved_files)} files")
        for file in moved_files:
            logger.info(f"  - {file}")
    else:
        errors = bulk_move_result.error()
        logger.error(f"Failed to move files, {len(errors)} errors:")
        for error in errors:
            logger.error(f"  - {error}")
    
    # Example 6: Creating custom operations with result_handler decorator
    from collection_sorter.common.result import result_handler
    
    @result_handler
    def count_files(directory):
        """Count the number of files in a directory."""
        return len(list(Path(directory).glob('*')))
    
    count_result = count_files(source_dir)
    file_count = count_result.unwrap_or(0)
    logger.info(f"Number of files: {file_count}")
    
    # Example 7: Composing multiple operations
    archive_result = processor.archive_directory(source_dir)
    
    # Chain operations using and_then
    def extract_after_archive(archive_path):
        extract_dir = archive_path.parent / "extracted"
        return processor.extract_archive(archive_path, extract_dir)
    
    archive_and_extract_result = archive_result.and_then(extract_after_archive)
    
    # Process the final result
    if archive_and_extract_result.is_success():
        extract_dir = archive_and_extract_result.unwrap()
        logger.info(f"Archive extracted to: {extract_dir}")
    else:
        error = archive_and_extract_result.error()
        logger.error(f"Failed to archive and extract: {error}")


if __name__ == "__main__":
    main()