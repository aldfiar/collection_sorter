from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple

import click
from rich.console import Console

from collection_sorter.common.paths import FilePath
from collection_sorter.common.result import Result, OperationError
from collection_sorter.common.factories import ConfigBasedProcessorFactory
from collection_sorter.common.templates_extensions import MangaProcessorTemplate
from collection_sorter.common.config_manager import config_manager
from collection_sorter.manga.manga_template import manga_template_function

from .base_handler import TemplateMethodCommandHandler, FactoryBasedCommandHandler

console = Console()

class MangaCommandHandler(TemplateMethodCommandHandler):
    """
    Handler for the manga command using the Template Method pattern.
    """

    def __init__(
        self, 
        sources: List[str],
        destination: Optional[str] = None,
        archive: bool = False,
        move: bool = False,
        dry_run: bool = False,
        interactive: bool = False,
        verbose: bool = False,
        author_folders: bool = False
    ):
        """Initialize the manga command handler.
        
        Args:
            sources: List of source paths to process
            destination: Optional destination path
            archive: Whether to create archives
            move: Whether to move files after processing
            dry_run: Whether to simulate operations
            interactive: Whether to prompt for confirmation
            verbose: Whether to use verbose logging
            author_folders: Whether to organize by author folders
        """
        super().__init__()
        self.sources = [FilePath(src) for src in sources]
        self.destination = FilePath(destination) if destination else None
        self.archive = archive
        self.move = move
        self.dry_run = dry_run
        self.interactive = interactive
        self.verbose = verbose
        self.author_folders = author_folders
        self.stats = {
            "processed": 0,
            "archived": 0,
            "moved": 0,
            "errors": 0
        }

    @classmethod
    def from_click_context(cls, ctx: click.Context) -> "MangaCommandHandler":
        """Create a handler from a Click context.
        
        Args:
            ctx: Click context
            
        Returns:
            A configured MangaCommandHandler
        """
        # Get command-specific configuration
        cmd_config = config_manager.get_command_config("manga")
        
        # Create handler
        return cls(
            sources=ctx.params.get("sources", []),
            destination=ctx.params.get("destination") or cmd_config.get("destination"),
            archive=ctx.params.get("archive") or cmd_config.get("archive", False),
            move=ctx.params.get("move") or cmd_config.get("move", False),
            dry_run=ctx.params.get("dry_run") or cmd_config.get("dry_run", False),
            interactive=ctx.params.get("interactive") or config_manager.config.ui.interactive,
            verbose=ctx.params.get("verbose") or config_manager.config.logging.verbose,
            author_folders=config_manager.config.manga.author_folders
        )

    def validate_sources(self) -> Result[List[FilePath], List[OperationError]]:
        """Validate source paths.
        
        Returns:
            Result containing valid source paths or errors
        """
        errors = []
        valid_sources = []
        
        for source in self.sources:
            path = Path(source.value)
            if not path.exists():
                errors.append(OperationError(f"Source path does not exist: {source}", path=str(source)))
            elif not path.is_dir():
                errors.append(OperationError(f"Source path is not a directory: {source}", path=str(source)))
            else:
                valid_sources.append(source)
                
        if not valid_sources:
            return Result.failure(errors)
            
        return Result.success(valid_sources)

    def prepare_destination(self) -> Result[FilePath, OperationError]:
        """Prepare the destination directory.
        
        Returns:
            Result containing the destination path or an error
        """
        if not self.destination:
            return Result.failure(OperationError(
                "Destination path is required for manga processing",
                path="N/A"
            ))
            
        dest_path = Path(self.destination.value)
        
        try:
            if not dest_path.exists():
                if not self.dry_run:
                    dest_path.mkdir(parents=True, exist_ok=True)
            elif not dest_path.is_dir():
                return Result.failure(OperationError(
                    f"Destination exists but is not a directory: {self.destination}",
                    path=str(self.destination)
                ))
                
            return Result.success(self.destination)
            
        except Exception as e:
            return Result.failure(OperationError(
                f"Failed to prepare destination directory: {str(e)}",
                path=str(self.destination)
            ))

    def pre_process(self, 
                  source_paths: List[FilePath], 
                  destination_path: FilePath) -> Result[None, OperationError]:
        """Pre-process steps before organizing manga.
        
        Args:
            source_paths: Valid source paths
            destination_path: Prepared destination path
            
        Returns:
            Success result or error
        """
        # No specific pre-processing needed
        return Result.success(None)

    def process_sources(self, 
                      source_paths: List[FilePath], 
                      destination_path: FilePath) -> Result[Dict[str, Any], List[OperationError]]:
        """Process source paths using the manga template.
        
        Args:
            source_paths: Valid source paths
            destination_path: Prepared destination path
            
        Returns:
            Result containing processing statistics or errors
        """
        errors = []
        processed_count = 0
        archived_count = 0
        moved_count = 0
        
        for source in source_paths:
            # Create the manga processor template
            template = MangaProcessorTemplate(
                source_path=source.value,
                destination_path=destination_path.value,
                template_func=manga_template_function,
                author_folders=self.author_folders,
                archive=self.archive,
                move_source=self.move,
                dry_run=self.dry_run,
                interactive=self.interactive
            )
            
            try:
                # Execute the template
                result = template.execute()
                if result.is_success():
                    data = result.unwrap()
                    processed_count += data.get("processed", 0)
                    archived_count += data.get("archived", 0)
                    moved_count += data.get("moved", 0)
                else:
                    errors.extend(result.unwrap_error())
            except Exception as e:
                errors.append(OperationError(
                    f"Failed to process {source}: {str(e)}",
                    path=str(source)
                ))
                
        if errors:
            return Result.failure(errors)
            
        return Result.success({
            "processed": processed_count,
            "archived": archived_count,
            "moved": moved_count,
            "errors": len(errors)
        })

    def post_process(self, 
                   source_paths: List[FilePath], 
                   destination_path: FilePath, 
                   processed_data: Dict[str, Any]) -> Result[None, OperationError]:
        """Post-process steps after organizing manga.
        
        Args:
            source_paths: Valid source paths
            destination_path: Prepared destination path
            processed_data: Data from processing stage
            
        Returns:
            Success result or error
        """
        # Update statistics
        self.stats.update(processed_data)
        return Result.success(None)


class MangaCommandHandlerAlternative(FactoryBasedCommandHandler):
    """
    Alternative handler for the manga command using the Factory pattern.
    """

    def __init__(
        self, 
        sources: List[str],
        destination: Optional[str] = None,
        archive: bool = False,
        move: bool = False,
        dry_run: bool = False,
        interactive: bool = False,
        verbose: bool = False,
        author_folders: bool = False
    ):
        """Initialize the manga command handler.
        
        Args:
            sources: List of source paths to process
            destination: Optional destination path
            archive: Whether to create archives
            move: Whether to move files after processing
            dry_run: Whether to simulate operations
            interactive: Whether to prompt for confirmation
            verbose: Whether to use verbose logging
            author_folders: Whether to organize by author folders
        """
        super().__init__()
        self.sources = [FilePath(src) for src in sources]
        self.destination = FilePath(destination) if destination else None
        self.archive = archive
        self.move = move
        self.dry_run = dry_run
        self.interactive = interactive
        self.verbose = verbose
        self.author_folders = author_folders
        self.factory = ConfigBasedProcessorFactory()
        self.stats = {
            "processed": 0,
            "archived": 0,
            "moved": 0,
            "errors": 0
        }

    @classmethod
    def from_click_context(cls, ctx: click.Context) -> "MangaCommandHandlerAlternative":
        """Create a handler from a Click context.
        
        Args:
            ctx: Click context
            
        Returns:
            A configured MangaCommandHandler
        """
        # Get command-specific configuration
        cmd_config = config_manager.get_command_config("manga")
        
        # Create handler
        return cls(
            sources=ctx.params.get("sources", []),
            destination=ctx.params.get("destination") or cmd_config.get("destination"),
            archive=ctx.params.get("archive") or cmd_config.get("archive", False),
            move=ctx.params.get("move") or cmd_config.get("move", False),
            dry_run=ctx.params.get("dry_run") or cmd_config.get("dry_run", False),
            interactive=ctx.params.get("interactive") or config_manager.config.ui.interactive,
            verbose=ctx.params.get("verbose") or config_manager.config.logging.verbose,
            author_folders=config_manager.config.manga.author_folders
        )

    def process_source(self, source: FilePath, destination: Optional[FilePath]) -> Result[Dict[str, Any], OperationError]:
        """Process a single source path.
        
        Args:
            source: Source path to process
            destination: Optional destination path
            
        Returns:
            Result with processing statistics or error
        """
        if not destination:
            return Result.failure(OperationError(
                "Destination path is required for manga processing",
                path=str(source)
            ))
            
        try:
            # Create manga processor from factory
            processor = self.factory.create_manga_processor(
                source_path=source.value,
                destination_path=destination.value,
                template_func=manga_template_function,
                dry_run=self.dry_run,
                interactive=self.interactive
            )
            
            # Process manga collection
            result = processor.process_manga(
                author_folders=self.author_folders,
                archive=self.archive,
                move_source=self.move
            )
            
            if result.is_success():
                # Update statistics
                data = result.unwrap()
                self.stats["processed"] += data.get("processed", 0)
                self.stats["archived"] += data.get("archived", 0)
                self.stats["moved"] += data.get("moved", 0)
                return Result.success(data)
            else:
                return result
                
        except Exception as e:
            self.stats["errors"] += 1
            return Result.failure(OperationError(
                f"Failed to process {source}: {str(e)}",
                path=str(source)
            ))