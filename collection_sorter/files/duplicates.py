"""
Centralized duplicate file handling for Collection Sorter.

This module provides utilities for handling duplicate files during operations
like moving, copying, renaming, and archiving. It supports different strategies
for handling duplicates and interactive resolution.
"""

import logging
import uuid
from enum import Enum
from pathlib import Path
from typing import Dict, Optional, Tuple, Union

from rich.prompt import Prompt

from collection_sorter.common.exceptions import FileOperationError, UserInterruptError
from collection_sorter.config.config_models import AppConfig
from collection_sorter.project_logging import console

logger = logging.getLogger("duplicates")


class DuplicateStrategy(Enum):
    """
    Strategies for handling duplicate files.
    """

    SKIP = "skip"  # Skip the file, don't process it
    RENAME_NEW = "rename_new"  # Rename the new file
    RENAME_EXISTING = "rename_existing"  # Rename the existing file
    OVERWRITE = "overwrite"  # Overwrite the existing file
    MOVE_TO_DUPLICATES = "move_to_duplicates"  # Move to a duplicates folder
    ASK = "ask"  # Ask the user interactively

    def __str__(self) -> str:
        """
        Get the string representation of the strategy.

        Returns:
            String representation
        """
        return self.value


class DuplicateHandler:
    """
    Centralized handler for duplicate files.

    This class provides methods for detecting and handling duplicate files
    with different strategies.
    """

    def __init__(
        self,
        strategy: Union[str, DuplicateStrategy] = DuplicateStrategy.RENAME_NEW,
        duplicates_dir: Optional[Union[str, Path]] = None,
        interactive: bool = False,
        dry_run: bool = False,
    ):
        """
        Initialize the duplicate handler.

        Args:
            strategy: Strategy for handling duplicates
            duplicates_dir: Directory to move duplicates to (if using MOVE_TO_DUPLICATES)
            interactive: Whether to ask the user for each duplicate
            dry_run: Whether to simulate operations without making changes
        """
        # Convert string strategy to enum
        if isinstance(strategy, str):
            try:
                self.strategy = DuplicateStrategy(strategy.lower())
            except ValueError:
                logger.warning(
                    f"Invalid duplicate strategy: {strategy}, using {DuplicateStrategy.RENAME_NEW}"
                )
                self.strategy = DuplicateStrategy.RENAME_NEW
        else:
            self.strategy = strategy

        # If interactive is enabled, set strategy to ASK
        if interactive:
            self.strategy = DuplicateStrategy.ASK

        # Set up duplicates directory if using MOVE_TO_DUPLICATES
        if duplicates_dir and self.strategy == DuplicateStrategy.MOVE_TO_DUPLICATES:
            self.duplicates_dir = Path(duplicates_dir).expanduser().resolve()
        else:
            self.duplicates_dir = None

        # Remember if we're in dry run mode
        self.dry_run = dry_run

        # Keep track of the interaction history
        self.interaction_history: Dict[str, DuplicateStrategy] = {}

    @classmethod
    def from_config(cls, config: AppConfig) -> "DuplicateHandler":
        """
        Create a duplicate handler from application configuration.

        Args:
            config: Application configuration

        Returns:
            Configured duplicate handler
        """
        # Extract duplicate handling settings from config
        duplicate_strategy = config.collection.duplicate_strategy
        duplicates_dir = config.collection.duplicates_dir
        interactive = config.ui.interactive
        dry_run = config.collection.dry_run

        return cls(
            strategy=duplicate_strategy,
            duplicates_dir=duplicates_dir,
            interactive=interactive,
            dry_run=dry_run,
        )

    def handle_duplicate(
        self, new_path: Path, existing_path: Optional[Path] = None, context: str = ""
    ) -> Tuple[Path, bool]:
        """
        Handle a potential duplicate file.

        Args:
            new_path: Path to the new file or planned destination
            existing_path: Path to the existing file (if known)
            context: Optional context string for logging and user interaction

        Returns:
            Tuple of (resolved_path, was_duplicate)
        """
        # Check if the path exists (if existing_path not provided)
        if existing_path is None:
            if not new_path.exists():
                # No duplicate
                return new_path, False

            existing_path = new_path

        # Determine what to do based on strategy
        strategy = self._get_strategy(new_path, existing_path, context)

        # Handle the duplicate according to the chosen strategy
        if strategy == DuplicateStrategy.SKIP:
            # Skip the file
            logger.info(f"Skipping duplicate file: {new_path}")
            return existing_path, True

        elif strategy == DuplicateStrategy.RENAME_NEW:
            # Rename the new file
            resolved_path = self._generate_unique_path(new_path)
            logger.info(f"Renaming new file to avoid duplicate: {resolved_path}")
            return resolved_path, True

        elif strategy == DuplicateStrategy.RENAME_EXISTING:
            # Rename the existing file
            if not self.dry_run:
                try:
                    renamed_path = self._generate_unique_path(existing_path)
                    existing_path.rename(renamed_path)
                    logger.info(
                        f"Renamed existing file to avoid duplicate: {renamed_path}"
                    )
                except OSError as e:
                    raise FileOperationError(
                        f"Failed to rename existing file: {str(e)}", str(existing_path)
                    )
            else:
                logger.info(
                    f"Would rename existing file to avoid duplicate: {existing_path}"
                )

            return new_path, True

        elif strategy == DuplicateStrategy.OVERWRITE:
            # Overwrite the existing file
            logger.info(f"Will overwrite existing file: {existing_path}")
            return new_path, True

        elif strategy == DuplicateStrategy.MOVE_TO_DUPLICATES:
            # Move to duplicates folder
            if not self.duplicates_dir:
                # Fall back to renaming if no duplicates directory specified
                logger.warning(
                    "No duplicates directory specified, falling back to renaming"
                )
                return self._generate_unique_path(new_path), True

            # Create the duplicates directory if it doesn't exist
            if not self.dry_run:
                self.duplicates_dir.mkdir(parents=True, exist_ok=True)

            # Create path in duplicates directory
            duplicate_path = self.duplicates_dir / new_path.name

            # Handle duplicates within the duplicates directory
            if duplicate_path.exists():
                duplicate_path = self._generate_unique_path(duplicate_path)

            logger.info(f"Moving duplicate to: {duplicate_path}")
            return duplicate_path, True

        # Shouldn't get here, but return new_path as a fallback
        return new_path, False

    def _get_strategy(
        self, new_path: Path, existing_path: Path, context: str
    ) -> DuplicateStrategy:
        """
        Get the strategy to use for a specific duplicate.

        Args:
            new_path: Path to the new file
            existing_path: Path to the existing file
            context: Context string for user interaction

        Returns:
            Strategy to use
        """
        # If we're not asking, just use the configured strategy
        if self.strategy != DuplicateStrategy.ASK:
            return self.strategy

        # Check if we've already asked about this file
        path_key = str(new_path.resolve())
        if path_key in self.interaction_history:
            return self.interaction_history[path_key]

        # Ask the user
        return self._ask_user(new_path, existing_path, context)

    def _ask_user(
        self, new_path: Path, existing_path: Path, context: str
    ) -> DuplicateStrategy:
        """
        Ask the user how to handle a duplicate.

        Args:
            new_path: Path to the new file
            existing_path: Path to the existing file
            context: Context string for user interaction

        Returns:
            Strategy chosen by the user

        Raises:
            UserInterruptError: If user cancels with Ctrl+C
        """
        try:
            console.print(
                f"\n[bold yellow]Duplicate file detected:[/bold yellow] {context}"
            )
            console.print(f"  Existing: [cyan]{existing_path}[/cyan]")
            console.print(f"  New:      [green]{new_path}[/green]")

            choices = {
                "s": (DuplicateStrategy.SKIP, "Skip (don't process this file)"),
                "n": (DuplicateStrategy.RENAME_NEW, "Rename new file"),
                "e": (DuplicateStrategy.RENAME_EXISTING, "Rename existing file"),
                "o": (DuplicateStrategy.OVERWRITE, "Overwrite existing file"),
                "d": (
                    DuplicateStrategy.MOVE_TO_DUPLICATES,
                    "Move to duplicates folder",
                ),
                "a": (None, "Apply this choice to all duplicates"),
            }

            choice_text = "\n".join(
                [f"[bold]{k}[/bold]: {v[1]}" for k, v in choices.items()]
            )
            console.print(
                f"\nHow would you like to handle this duplicate?\n{choice_text}"
            )

            while True:
                response = Prompt.ask(
                    "Enter your choice", choices=list(choices.keys()), default="s"
                ).lower()

                if response == "a":
                    # Apply to all - ask for the strategy to apply
                    console.print(
                        "\n[bold]Select the strategy to apply to all duplicates:[/bold]"
                    )
                    sub_choices = {k: v for k, v in choices.items() if k != "a"}
                    sub_choice_text = "\n".join(
                        [f"[bold]{k}[/bold]: {v[1]}" for k, v in sub_choices.items()]
                    )
                    console.print(sub_choice_text)

                    sub_response = Prompt.ask(
                        "Enter your choice",
                        choices=list(sub_choices.keys()),
                        default="s",
                    ).lower()

                    strategy = choices[sub_response][0]

                    # Update all existing history entries and the global strategy
                    self.strategy = strategy
                    self.interaction_history = {
                        k: strategy for k in self.interaction_history
                    }
                    return strategy
                else:
                    strategy = choices[response][0]
                    # Remember this choice for this path
                    path_key = str(new_path.resolve())
                    self.interaction_history[path_key] = strategy
                    return strategy

        except KeyboardInterrupt:
            raise UserInterruptError("Duplicate resolution interrupted by user")

    def _generate_unique_path(self, path: Path) -> Path:
        """
        Generate a unique path by adding a suffix.

        Args:
            path: Original path

        Returns:
            Unique path
        """
        stem = path.stem
        suffix = path.suffix
        parent = path.parent

        # Generate a unique identifier
        identifier = uuid.uuid4().hex[:8]

        # Create the new path
        new_path = parent / f"{stem}_duplicate_{identifier}{suffix}"

        # Ensure it's really unique (theoretically could have a collision)
        if new_path.exists():
            return self._generate_unique_path(path)

        return new_path

    def prepare_duplicate_dir(self, base_dir: Optional[Path] = None) -> Optional[Path]:
        """
        Prepare the duplicates directory if using MOVE_TO_DUPLICATES strategy.

        Args:
            base_dir: Optional base directory to create duplicates dir in

        Returns:
            Path to the duplicates directory or None if not using MOVE_TO_DUPLICATES
        """
        if self.strategy != DuplicateStrategy.MOVE_TO_DUPLICATES:
            return None

        # If we already have a duplicates dir, use that
        if self.duplicates_dir:
            if not self.dry_run:
                self.duplicates_dir.mkdir(parents=True, exist_ok=True)
            return self.duplicates_dir

        # Otherwise, create one in the base directory
        if base_dir:
            duplicates_dir = base_dir / "duplicates"
            if not self.dry_run:
                duplicates_dir.mkdir(parents=True, exist_ok=True)
            return duplicates_dir

        return None
