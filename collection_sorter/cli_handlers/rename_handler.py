from pathlib import Path
from typing import Any, Dict, List, Optional

import click
from rich.console import Console

from collection_sorter.common.factories import ConfigBasedProcessorFactory
from collection_sorter.config.config_manager import config_manager
from collection_sorter.files import FilePath
from collection_sorter.result import OperationError, Result
from collection_sorter.templates.processors import RenameProcessorTemplate

from .base_handler import FactoryBasedCommandHandler, TemplateMethodCommandHandler

console = Console()


class RenameCommandHandler(TemplateMethodCommandHandler):
    """
    Handler for the rename command using the Template Method pattern.
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
        recursive: bool = True,
        patterns: Optional[Dict[str, str]] = None,
    ):
        """Initialize the rename command handler.

        Args:
            sources: List of source paths to process
            destination: Optional destination path
            archive: Whether to create archives
            move: Whether to move files after processing
            dry_run: Whether to simulate operations
            interactive: Whether to prompt for confirmation
            verbose: Whether to use verbose logging
            recursive: Whether to process directories recursively
            patterns: Rename patterns to apply
        """
        super().__init__(
            sources=sources,
            destination=destination,
            dry_run=dry_run,
            interactive=interactive,
            duplicate_strategy=None,
            duplicates_dir=None,
            config={},
        )
        self.sources = [FilePath(src) for src in sources]
        self.destination = FilePath(destination) if destination else None
        self.archive = archive
        self.move = move
        self.dry_run = dry_run
        self.interactive = interactive
        self.verbose = verbose
        self.recursive = recursive
        self.patterns = patterns or {}
        self.stats = {"processed": 0, "renamed": 0, "errors": 0}

    @classmethod
    def from_click_context(cls, ctx: click.Context) -> "RenameCommandHandler":
        """Create a handler from a Click context.

        Args:
            ctx: Click context

        Returns:
            A configured RenameCommandHandler
        """
        # Get command-specific configuration
        cmd_config = config_manager.get_command_config("rename")

        # Create handler
        return cls(
            sources=ctx.params.get("sources", []),
            destination=ctx.params.get("destination") or cmd_config.get("destination"),
            archive=ctx.params.get("archive") or cmd_config.get("archive", False),
            move=ctx.params.get("move") or cmd_config.get("move", False),
            dry_run=ctx.params.get("dry_run") or cmd_config.get("dry_run", False),
            interactive=ctx.params.get("interactive")
            or config_manager.config.ui.interactive,
            verbose=ctx.params.get("verbose") or config_manager.config.logging.verbose,
            recursive=config_manager.config.rename.recursive,
            patterns=config_manager.config.rename.patterns,
        )

    def validate_sources(self) -> Result[List[FilePath], List[OperationError]]:
        """Validate source paths.

        Returns:
            Result containing valid source paths or errors
        """
        errors = []
        valid_sources = []

        for source in self.sources:
            path = Path(source.path)
            if not path.exists():
                errors.append(
                    OperationError(
                        f"Source path does not exist: {source}", path=str(source)
                    )
                )
            else:
                valid_sources.append(source)

        if not valid_sources:
            return Result.failure(errors)

        return Result.success(valid_sources)

    def prepare_destination(self) -> Result[Optional[FilePath], OperationError]:
        """Prepare the destination directory.

        Returns:
            Result containing the destination path or an error
        """
        if not self.destination:
            return Result.success(None)

        dest_path = Path(self.destination.path)

        try:
            if not dest_path.exists():
                if not self.dry_run:
                    dest_path.mkdir(parents=True, exist_ok=True)
            elif not dest_path.is_dir():
                return Result.failure(
                    OperationError(
                        f"Destination exists but is not a directory: {self.destination}",
                        path=str(self.destination),
                    )
                )

            return Result.success(self.destination)

        except Exception as e:
            return Result.failure(
                OperationError(
                    f"Failed to prepare destination directory: {str(e)}",
                    path=str(self.destination),
                )
            )

    def pre_process(
        self, source_paths: List[FilePath], destination_path: Optional[FilePath]
    ) -> Result[None, OperationError]:
        """Pre-process steps before renaming files.

        Args:
            source_paths: Valid source paths
            destination_path: Prepared destination path

        Returns:
            Success result or error
        """
        # No specific pre-processing needed for rename command
        return Result.success(None)

    def process_sources(
        self, source_paths: List[FilePath], destination_path: Optional[FilePath]
    ) -> Result[Dict[str, Any], List[OperationError]]:
        """Process source paths using the rename template.

        Args:
            source_paths: Valid source paths
            destination_path: Prepared destination path

        Returns:
            Result containing processing statistics or errors
        """
        errors = []
        processed_count = 0
        renamed_count = 0

        for source in source_paths:
            # Create the rename processor template
            template = RenameProcessorTemplate(
                source_path=source.path,
                destination_path=destination_path.path if destination_path else None,
                patterns=self.patterns,
                recursive=self.recursive,
                archive=self.archive,
                move_source=self.move,
                dry_run=self.dry_run,
                interactive=self.interactive,
            )

            try:
                # Execute the template
                result = template.execute()
                if result.is_success():
                    data = result.unwrap()
                    processed_count += data.get("processed", 0)
                    renamed_count += data.get("renamed", 0)
                else:
                    errors.extend(result.unwrap_error())
            except Exception as e:
                errors.append(
                    OperationError(
                        f"Failed to process {source}: {str(e)}", path=str(source)
                    )
                )

        if errors:
            return Result.failure(errors)

        return Result.success(
            {
                "processed": processed_count,
                "renamed": renamed_count,
                "errors": len(errors),
            }
        )

    def post_process(
        self,
        source_paths: List[FilePath],
        destination_path: Optional[FilePath],
        processed_data: Dict[str, Any],
    ) -> Result[None, OperationError]:
        """Post-process steps after renaming files.

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


class RenameCommandHandlerAlternative(FactoryBasedCommandHandler):
    """
    Alternative handler for the rename command using the Factory pattern.
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
        recursive: bool = True,
        patterns: Optional[Dict[str, str]] = None,
    ):
        """Initialize the rename command handler.

        Args:
            sources: List of source paths to process
            destination: Optional destination path
            archive: Whether to create archives
            move: Whether to move files after processing
            dry_run: Whether to simulate operations
            interactive: Whether to prompt for confirmation
            verbose: Whether to use verbose logging
            recursive: Whether to process directories recursively
            patterns: Rename patterns to apply
        """
        super().__init__(
            sources=sources,
            destination=destination,
            dry_run=dry_run,
            interactive=interactive,
            duplicate_strategy=None,
            duplicates_dir=None,
            config={},
        )
        self.sources = [FilePath(src) for src in sources]
        self.destination = FilePath(destination) if destination else None
        self.archive = archive
        self.move = move
        self.dry_run = dry_run
        self.interactive = interactive
        self.verbose = verbose
        self.recursive = recursive
        self.patterns = patterns or {}
        self.factory = ConfigBasedProcessorFactory()
        self.stats = {"processed": 0, "renamed": 0, "errors": 0}

    @classmethod
    def from_click_context(
        cls, ctx: click.Context
    ) -> "RenameCommandHandlerAlternative":
        """Create a handler from a Click context.

        Args:
            ctx: Click context

        Returns:
            A configured RenameCommandHandler
        """
        # Get command-specific configuration
        cmd_config = config_manager.get_command_config("rename")

        # Create handler
        return cls(
            sources=ctx.params.get("sources", []),
            destination=ctx.params.get("destination") or cmd_config.get("destination"),
            archive=ctx.params.get("archive") or cmd_config.get("archive", False),
            move=ctx.params.get("move") or cmd_config.get("move", False),
            dry_run=ctx.params.get("dry_run") or cmd_config.get("dry_run", False),
            interactive=ctx.params.get("interactive")
            or config_manager.config.ui.interactive,
            verbose=ctx.params.get("verbose") or config_manager.config.logging.verbose,
            recursive=config_manager.config.rename.recursive,
            patterns=config_manager.config.rename.patterns,
        )

    def process_source(
        self, source: FilePath, destination: Optional[FilePath]
    ) -> Result[Dict[str, Any], OperationError]:
        """Process a single source path.

        Args:
            source: Source path to process
            destination: Optional destination path

        Returns:
            Result with processing statistics or error
        """
        try:
            # Create file processor from factory
            processor = self.factory.create_file_processor(
                source_path=source.path,
                destination_path=destination.path if destination else None,
                dry_run=self.dry_run,
                interactive=self.interactive,
            )

            # Apply rename patterns
            result = processor.rename_files(
                patterns=self.patterns,
                recursive=self.recursive,
                archive=self.archive,
                move_source=self.move,
            )

            if result.is_success():
                # Update statistics
                data = result.unwrap()
                self.stats["processed"] += data.get("processed", 0)
                self.stats["renamed"] += data.get("renamed", 0)
                return Result.success(data)
            else:
                return result

        except Exception as e:
            self.stats["errors"] += 1
            return Result.failure(
                OperationError(
                    f"Failed to process {source}: {str(e)}", path=str(source)
                )
            )
