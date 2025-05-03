"""
ZIP command handler for Collection Sorter.

This module provides a modernized handler for the CLI's 'zip' command,
using the various patterns we've implemented.
"""

import logging
from pathlib import Path
from typing import Any, Dict, List, Optional

import click
from rich.console import Console

from collection_sorter.common.factories import (
    create_duplicate_handler,
    ConfigBasedProcessorFactory
)
from collection_sorter.files import FilePath
from collection_sorter.result import Result, OperationError, ErrorType
from collection_sorter.templates import ArchiveDirectoryTemplate, BatchProcessorTemplate

logger = logging.getLogger("zip_handler")
console = Console()


class ZipCommandHandler:
    """
    Handler for the ZIP command using modern patterns.
    
    This handler leverages:
    - Template Method pattern for the archiving process
    - Factory Method pattern for creating the processors
    - Result pattern for error handling
    - Value Objects for file paths
    """
    
    def __init__(
        self,
        sources: List[str],
        destination: Optional[str] = None,
        archive: bool = False,
        move: bool = False,
        dry_run: bool = False,
        interactive: bool = False,
        duplicate_strategy: Optional[str] = None,
        duplicates_dir: Optional[str] = None,
        compression_level: int = 6,
        config: Optional[Dict[str, Any]] = None
    ):
        """
        Initialize the ZIP command handler.
        
        Args:
            sources: List of source directories to archive
            destination: Optional destination directory
            archive: Whether to create nested archives
            move: Whether to remove source files after processing
            dry_run: Whether to simulate operations without making changes
            interactive: Whether to prompt for confirmation
            duplicate_strategy: Strategy for handling duplicates
            duplicates_dir: Directory to move duplicates to
            compression_level: ZIP compression level (0-9)
            config: Optional configuration dictionary
        """
        self.sources = sources
        self.destination = destination
        self.archive = archive
        self.move = move
        self.dry_run = dry_run
        self.interactive = interactive
        self.duplicate_strategy = duplicate_strategy
        self.duplicates_dir = duplicates_dir
        self.compression_level = compression_level
        self.config = config or {}
        
        # Create duplicate handler
        self.duplicate_handler = create_duplicate_handler(
            strategy=duplicate_strategy or self.config.get("duplicate_strategy", "rename_new"),
            duplicates_dir=duplicates_dir or self.config.get("duplicates_dir"),
            interactive=interactive or self.config.get("interactive", False),
            dry_run=dry_run or self.config.get("dry_run", False)
        )
    
    def handle(self) -> Result[Dict[str, Any], List[OperationError]]:
        """
        Handle the ZIP command.
        
        Returns:
            Result with success status and statistics or list of errors
        """
        try:
            # Create the directory processor template for archiving
            archiver = ArchiveDirectoryTemplate(
                dry_run=self.dry_run,
                duplicate_handler=self.duplicate_handler,
                recursive=True,
                compression_level=self.compression_level
            )
            
            # Create the batch processor for processing multiple directories
            processor = BatchProcessorTemplate(
                directory_processor=archiver,
                dry_run=self.dry_run,
                duplicate_handler=self.duplicate_handler,
                continue_on_error=True
            )
            
            # Process sources
            source_paths = [Path(src) for src in self.sources]
            dest_path = Path(self.destination) if self.destination else None
            
            # Process the batch
            result = processor.process_batch(
                source_paths,
                dest_path,
                archive_name=None,
                remove_source=self.move
            )
            
            if result.is_success():
                # Return success with statistics
                return Result.success({
                    "success": True,
                    "processed_sources": len(self.sources),
                    "archived_files": len(result.unwrap()),
                    "removed_sources": len(self.sources) if self.move else 0
                })
            else:
                # Return failure with errors
                errors = result.error()
                return Result.failure(errors)
                
        except Exception as e:
            # Convert regular exceptions to OperationError
            error = OperationError(
                type=ErrorType.OPERATION_FAILED,
                message=f"Failed to process ZIP command: {str(e)}",
                source_exception=e
            )
            return Result.failure([error])
    
    @classmethod
    def from_click_context(cls, ctx: click.Context) -> "ZipCommandHandler":
        """
        Create a handler from a Click context.
        
        Args:
            ctx: Click context with command parameters
            
        Returns:
            Configured handler instance
        """
        # Extract parameters from context
        params = ctx.params
        
        # Extract common parameters
        sources = params.get("sources", [])
        destination = params.get("destination")
        archive = params.get("archive", False)
        move = params.get("move", False)
        dry_run = params.get("dry_run", False)
        interactive = params.get("interactive", False)
        duplicate_strategy = params.get("duplicate_strategy")
        duplicates_dir = params.get("duplicates_dir")
        
        # Get configuration
        from collection_sorter.common.config_manager import config_manager
        config_manager.apply_click_context(ctx)
        
        # Get command-specific configuration
        zip_config = config_manager.get_command_config("zip")
        compression_level = zip_config.get("compression_level", 6)
        
        # Create the handler
        return cls(
            sources=sources,
            destination=destination,
            archive=archive,
            move=move,
            dry_run=dry_run,
            interactive=interactive,
            duplicate_strategy=duplicate_strategy,
            duplicates_dir=duplicates_dir,
            compression_level=compression_level,
            config=zip_config
        )


# Alternative implementation using the Factory pattern and Result processor
class ZipCommandHandlerAlternative:
    """
    Alternative handler for the ZIP command using the Factory pattern.
    
    This handler leverages the Factory pattern to create a ResultFileProcessor
    with the appropriate configuration.
    """
    
    def __init__(
        self,
        sources: List[str],
        destination: Optional[str] = None,
        archive: bool = False,
        move: bool = False,
        dry_run: bool = False,
        interactive: bool = False,
        duplicate_strategy: Optional[str] = None,
        duplicates_dir: Optional[str] = None,
        compression_level: int = 6,
        config: Optional[Dict[str, Any]] = None
    ):
        """
        Initialize the ZIP command handler.
        
        Args:
            sources: List of source directories to archive
            destination: Optional destination directory
            archive: Whether to create nested archives
            move: Whether to remove source files after processing
            dry_run: Whether to simulate operations without making changes
            interactive: Whether to prompt for confirmation
            duplicate_strategy: Strategy for handling duplicates
            duplicates_dir: Directory to move duplicates to
            compression_level: ZIP compression level (0-9)
            config: Optional configuration dictionary
        """
        self.sources = sources
        self.destination = destination
        self.archive = archive
        self.move = move
        self.dry_run = dry_run
        self.interactive = interactive
        self.duplicate_strategy = duplicate_strategy
        self.duplicates_dir = duplicates_dir
        self.compression_level = compression_level
        self.config = config or {}
        
        # Create a dynamic configuration object
        self.dynamic_config = {
            "processor_type": "result",
            "dry_run": dry_run,
            "compression_level": compression_level,
            "duplicate_strategy": duplicate_strategy or self.config.get("duplicate_strategy", "rename_new"),
            "duplicates_dir": duplicates_dir or self.config.get("duplicates_dir"),
            "interactive": interactive or self.config.get("interactive", False)
        }
        
        # Create the factory
        self.factory = ConfigBasedProcessorFactory(config=self.dynamic_config)
    
    def handle(self) -> Result[Dict[str, Any], List[OperationError]]:
        """
        Handle the ZIP command.
        
        Returns:
            Result with success status and statistics or list of errors
        """
        try:
            # Create a processor using the factory
            processor = self.factory.create()
            
            # Process each source
            successful_sources = []
            failed_sources = []
            errors = []
            
            for source in self.sources:
                source_path = FilePath(source)
                if not source_path.is_directory:
                    error = OperationError(
                        type=ErrorType.INVALID_PATH,
                        message=f"Source is not a directory: {source}",
                        path=str(source)
                    )
                    errors.append(error)
                    failed_sources.append(source)
                    continue
                
                # Process based on archive flag
                dest_path = FilePath(self.destination) if self.destination else source_path.parent
                
                if self.archive:
                    # Archive and optionally delete the source
                    result = processor.archive_and_delete(
                        source_path,
                        dest_path,
                        archive_name=None,
                        remove_source=self.move
                    )
                else:
                    # Just archive the directory
                    result = processor.archive_directory(
                        source_path,
                        dest_path
                    )
                
                if result.is_success():
                    successful_sources.append(source)
                else:
                    failed_sources.append(source)
                    errors.append(result.error())
            
            # Return success if all sources were processed successfully
            if not errors:
                return Result.success({
                    "success": True,
                    "processed_sources": len(successful_sources),
                    "failed_sources": 0,
                    "removed_sources": len(successful_sources) if self.move else 0
                })
            else:
                # Return partial success with errors
                return Result.success({
                    "success": True,
                    "processed_sources": len(successful_sources),
                    "failed_sources": len(failed_sources),
                    "errors": errors,
                    "removed_sources": len(successful_sources) if self.move else 0
                })
                
        except Exception as e:
            # Convert regular exceptions to OperationError
            error = OperationError(
                type=ErrorType.OPERATION_FAILED,
                message=f"Failed to process ZIP command: {str(e)}",
                source_exception=e
            )
            return Result.failure([error])
    
    @classmethod
    def from_click_context(cls, ctx: click.Context) -> "ZipCommandHandlerAlternative":
        """
        Create a handler from a Click context.
        
        Args:
            ctx: Click context with command parameters
            
        Returns:
            Configured handler instance
        """
        # Extract parameters from context
        params = ctx.params
        
        # Extract common parameters
        sources = params.get("sources", [])
        destination = params.get("destination")
        archive = params.get("archive", False)
        move = params.get("move", False)
        dry_run = params.get("dry_run", False)
        interactive = params.get("interactive", False)
        duplicate_strategy = params.get("duplicate_strategy")
        duplicates_dir = params.get("duplicates_dir")
        
        # Get configuration
        from collection_sorter.common.config_manager import config_manager
        config_manager.apply_click_context(ctx)
        
        # Get command-specific configuration
        zip_config = config_manager.get_command_config("zip")
        compression_level = zip_config.get("compression_level", 6)
        
        # Create the handler
        return cls(
            sources=sources,
            destination=destination,
            archive=archive,
            move=move,
            dry_run=dry_run,
            interactive=interactive,
            duplicate_strategy=duplicate_strategy,
            duplicates_dir=duplicates_dir,
            compression_level=compression_level,
            config=zip_config
        )