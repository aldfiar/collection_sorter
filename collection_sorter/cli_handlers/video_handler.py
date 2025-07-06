from pathlib import Path
from typing import Any, Dict, List, Optional, Set

import click
from rich.console import Console

from collection_sorter.common.factories import ConfigBasedProcessorFactory
from collection_sorter.config.config_manager import config_manager
from collection_sorter.files import FilePath
from collection_sorter.result import OperationError, Result
from collection_sorter.templates.processors import VideoProcessorTemplate

from .base_handler import FactoryBasedCommandHandler, TemplateMethodCommandHandler

console = Console()


class VideoCommandHandler(TemplateMethodCommandHandler):
    """
    Handler for the video command using the Template Method pattern.
    """

    def __init__(
        self,
        sources: List[str],
        destination: Optional[str] = None,
        dry_run: bool = False,
        interactive: bool = False,
        verbose: bool = False,
        video_extensions: Optional[Set[str]] = None,
        subtitle_extensions: Optional[Set[str]] = None,
    ):
        """Initialize the video command handler.

        Args:
            sources: List of source paths to process
            destination: Optional destination path
            dry_run: Whether to simulate operations
            interactive: Whether to prompt for confirmation
            verbose: Whether to use verbose logging
            video_extensions: File extensions for video files
            subtitle_extensions: File extensions for subtitle files
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
        self.dry_run = dry_run
        self.interactive = interactive
        self.verbose = verbose
        self.video_extensions = video_extensions or set()
        self.subtitle_extensions = subtitle_extensions or set()
        self.stats = {"processed": 0, "renamed": 0, "errors": 0}

    @classmethod
    def from_click_context(cls, ctx: click.Context) -> "VideoCommandHandler":
        """Create a handler from a Click context.

        Args:
            ctx: Click context

        Returns:
            A configured VideoCommandHandler
        """
        # Get command-specific configuration
        cmd_config = config_manager.get_command_config("video")

        # Create handler
        return cls(
            sources=ctx.params.get("sources", []),
            destination=ctx.params.get("destination") or cmd_config.get("destination"),
            dry_run=ctx.params.get("dry_run") or cmd_config.get("dry_run", False),
            interactive=ctx.params.get("interactive")
            or config_manager.config.ui.interactive,
            verbose=ctx.params.get("verbose") or config_manager.config.logging.verbose,
            video_extensions=set(config_manager.config.video.video_extensions),
            subtitle_extensions=set(config_manager.config.video.subtitle_extensions),
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
        """Prepare the destination directory if specified.

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
        """Pre-process steps before renaming video files.

        Args:
            source_paths: Valid source paths
            destination_path: Prepared destination path

        Returns:
            Success result or error
        """
        # No specific pre-processing needed
        return Result.success(None)

    def process_sources(
        self, source_paths: List[FilePath], destination_path: Optional[FilePath]
    ) -> Result[Dict[str, Any], List[OperationError]]:
        """Process source paths using the video processor template.

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
            # Create the video processor template
            template = VideoProcessorTemplate(
                source_path=source.path,
                destination_path=destination_path.path if destination_path else None,
                video_extensions=self.video_extensions,
                subtitle_extensions=self.subtitle_extensions,
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
        """Post-process steps after renaming video files.

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


class VideoCommandHandlerAlternative(FactoryBasedCommandHandler):
    """
    Alternative handler for the video command using the Factory pattern.
    """

    def __init__(
        self,
        sources: List[str],
        destination: Optional[str] = None,
        dry_run: bool = False,
        interactive: bool = False,
        verbose: bool = False,
        video_extensions: Optional[Set[str]] = None,
        subtitle_extensions: Optional[Set[str]] = None,
    ):
        """Initialize the video command handler.

        Args:
            sources: List of source paths to process
            destination: Optional destination path
            dry_run: Whether to simulate operations
            interactive: Whether to prompt for confirmation
            verbose: Whether to use verbose logging
            video_extensions: File extensions for video files
            subtitle_extensions: File extensions for subtitle files
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
        self.dry_run = dry_run
        self.interactive = interactive
        self.verbose = verbose
        self.video_extensions = video_extensions or set()
        self.subtitle_extensions = subtitle_extensions or set()
        self.factory = ConfigBasedProcessorFactory()
        self.stats = {"processed": 0, "renamed": 0, "errors": 0}

    @classmethod
    def from_click_context(cls, ctx: click.Context) -> "VideoCommandHandlerAlternative":
        """Create a handler from a Click context.

        Args:
            ctx: Click context

        Returns:
            A configured VideoCommandHandler
        """
        # Get command-specific configuration
        cmd_config = config_manager.get_command_config("video")

        # Create handler
        return cls(
            sources=ctx.params.get("sources", []),
            destination=ctx.params.get("destination") or cmd_config.get("destination"),
            dry_run=ctx.params.get("dry_run") or cmd_config.get("dry_run", False),
            interactive=ctx.params.get("interactive")
            or config_manager.config.ui.interactive,
            verbose=ctx.params.get("verbose") or config_manager.config.logging.verbose,
            video_extensions=set(config_manager.config.video.video_extensions),
            subtitle_extensions=set(config_manager.config.video.subtitle_extensions),
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
            # Create video processor from factory
            processor = self.factory.create_video_processor(
                source_path=source.path,
                destination_path=destination.path if destination else None,
                dry_run=self.dry_run,
                interactive=self.interactive,
            )

            # Process video files
            result = processor.process_videos(
                video_extensions=self.video_extensions,
                subtitle_extensions=self.subtitle_extensions,
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
