"""
Example usage of the Template Method pattern for file processing.

This module demonstrates how to use the Template Method pattern to define
skeleton algorithms for file processing operations with customizable steps.
"""

import logging
import os
from pathlib import Path
from typing import Optional, Union

from collection_sorter.common.duplicates import DuplicateHandler, DuplicateStrategy
from collection_sorter.common.paths import FilePath
from collection_sorter.common.result import Result
from collection_sorter.common.templates import (
    FileProcessorTemplate,
    FileMoveTemplate,
    FileCopyTemplate,
    FileRenameTemplate,
    DirectoryProcessorTemplate,
    DirectoryCopyTemplate,
    DirectoryMoveTemplate,
    ArchiveDirectoryTemplate,
    BatchProcessorTemplate
)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("template_example")


def example_file_processor():
    """Example of using file processor templates."""
    # Create a move template
    mover = FileMoveTemplate(dry_run=False)
    
    # Process a file
    source_file = Path("/path/to/source.txt")
    destination_file = Path("/path/to/destination.txt")
    
    # Use the template method to process the file
    result = mover.process_file(source_file, destination_file)
    
    if result.is_success():
        moved_path = result.unwrap()
        logger.info(f"File moved to: {moved_path}")
    else:
        error = result.error()
        logger.error(f"Failed to move file: {error}")
    
    # Create a copy template with a duplicate handler
    duplicate_handler = DuplicateHandler(
        strategy=DuplicateStrategy.RENAME_NEW,
        dry_run=False
    )
    
    copier = FileCopyTemplate(dry_run=False, duplicate_handler=duplicate_handler)
    
    # Process a file with the copy template
    result = copier.process_file(source_file, destination_file)
    
    if result.is_success():
        copied_path = result.unwrap()
        logger.info(f"File copied to: {copied_path}")
    else:
        error = result.error()
        logger.error(f"Failed to copy file: {error}")


def example_directory_processor():
    """Example of using directory processor templates."""
    # Create an archive template
    archiver = ArchiveDirectoryTemplate(
        dry_run=False,
        compression_level=9,
        recursive=True
    )
    
    # Process a directory
    source_dir = Path("/path/to/source/dir")
    destination_dir = Path("/path/to/destination")
    
    # Use the template method to process the directory
    result = archiver.process_directory(
        source_dir, 
        destination_dir,
        archive_name="my_archive",
        remove_source=True  # Custom parameter for post-processing
    )
    
    if result.is_success():
        archive_path = result.unwrap()
        logger.info(f"Directory archived to: {archive_path}")
    else:
        error = result.error()
        logger.error(f"Failed to archive directory: {error}")
    
    # Create a directory move template
    mover = DirectoryMoveTemplate(dry_run=True, recursive=True)
    
    # Process a directory with the move template
    result = mover.process_directory(source_dir, destination_dir)
    
    if result.is_success():
        moved_path = result.unwrap()
        logger.info(f"Directory would be moved to: {moved_path}")
    else:
        error = result.error()
        logger.error(f"Failed to move directory: {error}")


def example_batch_processor():
    """Example of using batch processor templates."""
    # Create file and directory processors
    file_processor = FileCopyTemplate(dry_run=False)
    directory_processor = DirectoryCopyTemplate(dry_run=False, recursive=True)
    
    # Create a batch processor with these templates
    batch_processor = BatchProcessorTemplate(
        file_processor=file_processor,
        directory_processor=directory_processor,
        continue_on_error=True
    )
    
    # Process multiple sources
    sources = [
        Path("/path/to/file1.txt"),
        Path("/path/to/file2.txt"),
        Path("/path/to/dir1"),
        Path("/path/to/dir2")
    ]
    
    destination = Path("/path/to/batch/destination")
    
    # Use the template method to process the batch
    result = batch_processor.process_batch(sources, destination)
    
    if result.is_success():
        processed_paths = result.unwrap()
        logger.info(f"Batch processed {len(processed_paths)} items:")
        for path in processed_paths:
            logger.info(f"  - {path}")
    else:
        errors = result.error()
        logger.error(f"Batch processing failed with {len(errors)} errors:")
        for error in errors:
            logger.error(f"  - {error}")


class CustomFileProcessor(FileProcessorTemplate):
    """
    Custom file processor template with extended validation.
    
    This demonstrates how to extend the template by overriding specific steps.
    """
    
    def _validate_source(self, source):
        """Extended validation for source files."""
        # Call the parent validation first
        result = super()._validate_source(source)
        
        if result.is_failure():
            return result
            
        source_path = result.unwrap()
        
        # Add custom validation logic
        if source_path.path.stat().st_size == 0:
            return Result.failure(OperationError(
                type=ErrorType.VALIDATION_ERROR,
                message="Source file is empty",
                path=str(source_path)
            ))
            
        if source_path.suffix.lower() not in ['.txt', '.doc', '.pdf']:
            return Result.failure(OperationError(
                type=ErrorType.VALIDATION_ERROR,
                message=f"Unsupported file type: {source_path.suffix}",
                path=str(source_path)
            ))
            
        return result
    
    def _execute_operation(self, source_path, destination_path, **kwargs):
        """Custom file operation implementation."""
        try:
            # Custom operation logic
            if self.dry_run:
                logger.info(f"Would process file: {source_path} -> {destination_path}")
                return Result.success(destination_path)
                
            # Read the source file
            with open(source_path.path, 'r') as f:
                content = f.read()
                
            # Modify the content (e.g., add a header)
            modified_content = f"# Processed on {datetime.now()}\n\n{content}"
            
            # Write to the destination
            with open(destination_path.path, 'w') as f:
                f.write(modified_content)
                
            logger.info(f"Processed file: {source_path} -> {destination_path}")
            return Result.success(destination_path)
            
        except Exception as e:
            return Result.failure(OperationError(
                type=ErrorType.OPERATION_FAILED,
                message=f"Failed to process file: {str(e)}",
                path=str(source_path),
                source_exception=e
            ))
    
    def _post_process(self, source_path, processed_path, **kwargs):
        """Custom post-processing after the operation."""
        # Add a processing log entry
        log_file = processed_path.parent.join(f"{processed_path.stem}.log")
        
        if not self.dry_run:
            with open(log_file.path, 'w') as f:
                f.write(f"Processed {source_path} to {processed_path} at {datetime.now()}\n")
                f.write(f"Original size: {source_path.path.stat().st_size} bytes\n")
                f.write(f"Processed size: {processed_path.path.stat().st_size} bytes\n")
            
            logger.info(f"Created log file: {log_file}")
        else:
            logger.info(f"Would create log file: {log_file}")
            
        return Result.success(processed_path)


def example_custom_processor():
    """Example of using a custom processor template."""
    from datetime import datetime
    
    # Create a custom processor
    custom_processor = CustomFileProcessor(dry_run=False)
    
    # Process a file
    source_file = Path("/path/to/document.txt")
    destination_file = Path("/path/to/processed_document.txt")
    
    # Use the template method to process the file
    result = custom_processor.process_file(source_file, destination_file)
    
    if result.is_success():
        processed_path = result.unwrap()
        logger.info(f"File processed to: {processed_path}")
    else:
        error = result.error()
        logger.error(f"Failed to process file: {error}")


if __name__ == "__main__":
    # Uncomment the examples to run them
    # example_file_processor()
    # example_directory_processor()
    # example_batch_processor()
    # example_custom_processor()
    pass