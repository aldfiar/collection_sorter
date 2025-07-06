"""
Base CLI handler for Collection Sorter.

This module provides a base class for CLI command handlers, defining
common functionality and interfaces.
"""

import logging
from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional

import click
from rich.console import Console

from collection_sorter.common.factories import create_duplicate_handler
from collection_sorter.files import FilePath
from collection_sorter.result import ErrorType, OperationError, Result

logger = logging.getLogger("base_handler")
console = Console()


class CommandHandler(ABC):
    """
    Abstract base class for CLI command handlers.

    This class defines the interface for command handlers and provides
    common functionality.
    """

    def __init__(
        self,
        sources: List[str],
        destination: Optional[str] = None,
        dry_run: bool = False,
        interactive: bool = False,
        duplicate_strategy: Optional[str] = None,
        duplicates_dir: Optional[str] = None,
        config: Optional[Dict[str, Any]] = None,
    ):
        """
        Initialize the command handler.

        Args:
            sources: List of source paths to process
            destination: Optional destination path
            dry_run: Whether to simulate operations without making changes
            interactive: Whether to prompt for confirmation
            duplicate_strategy: Strategy for handling duplicates
            duplicates_dir: Directory to move duplicates to
            config: Optional configuration dictionary
        """
        self.sources = sources
        self.destination = destination
        self.dry_run = dry_run
        self.interactive = interactive
        self.duplicate_strategy = duplicate_strategy
        self.duplicates_dir = duplicates_dir
        self.config = config or {}

        # Create duplicate handler
        self.duplicate_handler = create_duplicate_handler(
            strategy=duplicate_strategy
            or self.config.get("duplicate_strategy", "rename_new"),
            duplicates_dir=duplicates_dir or self.config.get("duplicates_dir"),
            interactive=interactive or self.config.get("interactive", False),
            dry_run=dry_run or self.config.get("dry_run", False),
        )

    @abstractmethod
    def handle(self) -> Result[Dict[str, Any], List[OperationError]]:
        """
        Handle the command.

        Returns:
            Result with success status and statistics or list of errors
        """
        pass

    @classmethod
    @abstractmethod
    def from_click_context(cls, ctx: click.Context) -> "CommandHandler":
        """
        Create a handler from a Click context.

        Args:
            ctx: Click context with command parameters

        Returns:
            Configured handler instance
        """
        pass

    def validate_sources(self) -> Result[List[FilePath], List[OperationError]]:
        """
        Validate the source paths.

        Returns:
            Result with list of valid paths or list of errors
        """
        valid_sources = []
        errors = []

        for source in self.sources:
            try:
                source_path = FilePath(source)
                if source_path.exists:
                    valid_sources.append(source_path)
                else:
                    error = OperationError(
                        type=ErrorType.FILE_NOT_FOUND,
                        message=f"Source does not exist: {source}",
                        path=str(source),
                    )
                    errors.append(error)
            except Exception as e:
                error = OperationError(
                    type=ErrorType.INVALID_PATH,
                    message=f"Invalid source path: {source} - {str(e)}",
                    path=str(source),
                    source_exception=e,
                )
                errors.append(error)

        if not valid_sources:
            return Result.failure(
                errors
                or [
                    OperationError(
                        type=ErrorType.VALIDATION_ERROR,
                        message="No valid source paths provided",
                    )
                ]
            )

        if errors and not self.config.get("continue_on_error", False):
            return Result.failure(errors)

        return Result.success(valid_sources)

    def prepare_destination(self) -> Result[Optional[FilePath], OperationError]:
        """
        Prepare the destination path.

        Returns:
            Result with destination path or error
        """
        if not self.destination:
            return Result.success(None)

        try:
            destination_path = FilePath(
                self.destination, must_exist=False, create_if_missing=not self.dry_run
            )

            return Result.success(destination_path)
        except Exception as e:
            error = OperationError(
                type=ErrorType.INVALID_PATH,
                message=f"Invalid destination path: {self.destination} - {str(e)}",
                path=str(self.destination),
                source_exception=e,
            )
            return Result.failure(error)

    def handle_result(
        self, result: Result[Dict[str, Any], List[OperationError]]
    ) -> Dict[str, Any]:
        """
        Handle the result of the command.

        Args:
            result: Result of the command

        Returns:
            Dictionary with success status and statistics
        """
        if result.is_success():
            stats = result.unwrap()

            # Print success message
            sources_processed = stats.get("processed_sources", 0)
            console.print(
                f"[green]Successfully processed {sources_processed} sources[/green]"
            )

            return stats
        else:
            errors = result.error()

            # Print error messages
            console.print(f"[red]Command failed with {len(errors)} errors:[/red]")
            for i, error in enumerate(errors):
                console.print(f"[red]{i+1}. {error}[/red]")

            return {"success": False, "errors": errors, "processed_sources": 0}


class TemplateMethodCommandHandler(CommandHandler):
    """
    Base class for command handlers using the Template Method pattern.

    This class defines a template method for handling commands with
    customizable steps.
    """

    def handle(self) -> Result[Dict[str, Any], List[OperationError]]:
        """
        Handle the command using the template method pattern.

        Returns:
            Result with success status and statistics or list of errors
        """
        try:
            # Step 1: Validate sources
            sources_result = self.validate_sources()
            if sources_result.is_failure():
                return sources_result

            source_paths = sources_result.unwrap()

            # Step 2: Prepare destination
            destination_result = self.prepare_destination()
            if destination_result.is_failure():
                return Result.failure([destination_result.error()])

            destination_path = destination_result.unwrap()

            # Step 3: Pre-process (can be overridden by subclasses)
            preprocess_result = self.pre_process(source_paths, destination_path)
            if preprocess_result.is_failure():
                return preprocess_result

            # Step 4: Process sources
            process_result = self.process_sources(source_paths, destination_path)
            if process_result.is_failure():
                return process_result

            processed_items = process_result.unwrap()

            # Step 5: Post-process (can be overridden by subclasses)
            postprocess_result = self.post_process(
                source_paths, destination_path, processed_items
            )
            if postprocess_result.is_failure():
                return postprocess_result

            # Return success with statistics
            return Result.success(
                {
                    "success": True,
                    "processed_sources": len(source_paths),
                    "processed_items": len(processed_items),
                    "skipped_sources": len(self.sources) - len(source_paths),
                }
            )

        except Exception as e:
            # Convert regular exceptions to OperationError
            error = OperationError(
                type=ErrorType.OPERATION_FAILED,
                message=f"Command failed: {str(e)}",
                source_exception=e,
            )
            return Result.failure([error])

    def pre_process(
        self, sources: List[FilePath], destination: Optional[FilePath]
    ) -> Result[bool, List[OperationError]]:
        """
        Pre-process the command.

        This is a hook method that can be overridden by subclasses
        to add additional steps before processing.

        Args:
            sources: Validated source paths
            destination: Prepared destination path

        Returns:
            Result with success flag or list of errors
        """
        # Default implementation does nothing
        return Result.success(True)

    @abstractmethod
    def process_sources(
        self, sources: List[FilePath], destination: Optional[FilePath]
    ) -> Result[List[Any], List[OperationError]]:
        """
        Process the sources.

        This is an abstract method that must be implemented by subclasses
        to provide specific processing logic.

        Args:
            sources: Validated source paths
            destination: Prepared destination path

        Returns:
            Result with list of processed items or list of errors
        """
        pass

    def post_process(
        self,
        sources: List[FilePath],
        destination: Optional[FilePath],
        processed_items: List[Any],
    ) -> Result[bool, List[OperationError]]:
        """
        Post-process the command.

        This is a hook method that can be overridden by subclasses
        to add additional steps after processing.

        Args:
            sources: Validated source paths
            destination: Prepared destination path
            processed_items: Items processed by process_sources

        Returns:
            Result with success flag or list of errors
        """
        # Default implementation does nothing
        return Result.success(True)


class FactoryBasedCommandHandler(CommandHandler):
    """
    Base class for command handlers using the Factory pattern.

    This class uses factories to create processors for handling commands.
    """

    def __init__(
        self,
        sources: List[str],
        destination: Optional[str] = None,
        dry_run: bool = False,
        interactive: bool = False,
        duplicate_strategy: Optional[str] = None,
        duplicates_dir: Optional[str] = None,
        config: Optional[Dict[str, Any]] = None,
        processor_type: str = "result",
    ):
        """
        Initialize the factory-based command handler.

        Args:
            sources: List of source paths to process
            destination: Optional destination path
            dry_run: Whether to simulate operations without making changes
            interactive: Whether to prompt for confirmation
            duplicate_strategy: Strategy for handling duplicates
            duplicates_dir: Directory to move duplicates to
            config: Optional configuration dictionary
            processor_type: Type of processor to create ("standard" or "result")
        """
        super().__init__(
            sources=sources,
            destination=destination,
            dry_run=dry_run,
            interactive=interactive,
            duplicate_strategy=duplicate_strategy,
            duplicates_dir=duplicates_dir,
            config=config,
        )
        self.processor_type = processor_type

        # Create a processor factory
        from collection_sorter.common.factories import ConfigBasedProcessorFactory

        # Create a dynamic configuration object
        self.dynamic_config = {
            "processor_type": processor_type,
            "dry_run": dry_run,
            "duplicate_strategy": duplicate_strategy
            or self.config.get("duplicate_strategy", "rename_new"),
            "duplicates_dir": duplicates_dir or self.config.get("duplicates_dir"),
            "interactive": interactive or self.config.get("interactive", False),
        }

        # Add additional configuration from config
        for key, value in self.config.items():
            if key not in self.dynamic_config:
                self.dynamic_config[key] = value

        # Create the factory
        self.factory = ConfigBasedProcessorFactory(config=self.dynamic_config)

        # Create the processor
        self.processor = self.factory.create()

    def handle(self) -> Result[Dict[str, Any], List[OperationError]]:
        """
        Handle the command using the factory-created processor.

        Returns:
            Result with success status and statistics or list of errors
        """
        try:
            # Step 1: Validate sources
            sources_result = self.validate_sources()
            if sources_result.is_failure():
                return sources_result

            source_paths = sources_result.unwrap()

            # Step 2: Prepare destination
            destination_result = self.prepare_destination()
            if destination_result.is_failure():
                return Result.failure([destination_result.error()])

            destination_path = destination_result.unwrap()

            # Step 3: Process using the processor
            processed_items = []
            errors = []

            # Process each source using the processor
            for source_path in source_paths:
                result = self.process_source(source_path, destination_path)

                if result.is_success():
                    processed_items.append(result.unwrap())
                else:
                    errors.append(result.error())
                    if not self.config.get("continue_on_error", False):
                        return Result.failure(errors)

            # Return success with statistics
            if not errors:
                return Result.success(
                    {
                        "success": True,
                        "processed_sources": len(source_paths),
                        "processed_items": len(processed_items),
                        "skipped_sources": len(self.sources) - len(source_paths),
                    }
                )
            else:
                # Return partial success with errors
                return Result.success(
                    {
                        "success": True,
                        "processed_sources": len(source_paths) - len(errors),
                        "processed_items": len(processed_items),
                        "skipped_sources": len(self.sources) - len(source_paths),
                        "errors": errors,
                        "failed_sources": len(errors),
                    }
                )

        except Exception as e:
            # Convert regular exceptions to OperationError
            error = OperationError(
                type=ErrorType.OPERATION_FAILED,
                message=f"Command failed: {str(e)}",
                source_exception=e,
            )
            return Result.failure([error])

    @abstractmethod
    def process_source(
        self, source: FilePath, destination: Optional[FilePath]
    ) -> Result[Any, OperationError]:
        """
        Process a single source using the processor.

        This is an abstract method that must be implemented by subclasses
        to provide specific processing logic.

        Args:
            source: Source path to process
            destination: Destination path

        Returns:
            Result with processed item or error
        """
        pass
