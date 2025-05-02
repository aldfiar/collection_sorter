"""
Factory methods for file handlers in Collection Sorter.

This module implements the Factory Method pattern for creating various
file processors, strategies, and handlers based on configuration.
"""

import logging
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Dict, List, Optional, Type, TypeVar, Union, Any

from collection_sorter.common.duplicates import DuplicateHandler, DuplicateStrategy
from collection_sorter.common.paths import FilePath
from collection_sorter.common.services import get_service, register_service
from collection_sorter.common.strategies import (
    FileOperationStrategy,
    MoveFileStrategy,
    CopyFileStrategy,
    ArchiveStrategy,
    ExtractArchiveStrategy,
    RenameFileStrategy
)
from collection_sorter.common.result_strategies import (
    ResultFileOperationStrategy,
    MoveFileResultStrategy,
    CopyFileResultStrategy,
    ArchiveResultStrategy,
    ExtractArchiveResultStrategy,
    RenameFileResultStrategy,
    DeleteFileResultStrategy,
    DeleteDirectoryResultStrategy
)
from collection_sorter.common.file_processor import FileProcessor
from collection_sorter.common.result_processor import ResultFileProcessor

logger = logging.getLogger("factories")


# Type variables for factory return types
T = TypeVar('T')
S = TypeVar('S', bound=FileOperationStrategy)
RS = TypeVar('RS', bound=ResultFileOperationStrategy)
P = TypeVar('P', bound=Union[FileProcessor, ResultFileProcessor])


class Factory(ABC, Generic[T]):
    """
    Abstract base class for factories.
    
    This defines the common interface for all factories.
    """
    
    @abstractmethod
    def create(self, *args, **kwargs) -> T:
        """
        Create an instance.
        
        Args:
            *args: Positional arguments
            **kwargs: Keyword arguments
            
        Returns:
            Created instance
        """
        pass


class StrategyFactory(Factory[S]):
    """Factory for creating file operation strategies."""
    
    def __init__(
        self,
        default_dry_run: bool = False,
        default_compression_level: int = 6
    ):
        """
        Initialize the strategy factory.
        
        Args:
            default_dry_run: Default value for dry_run
            default_compression_level: Default value for compression_level
        """
        self.default_dry_run = default_dry_run
        self.default_compression_level = default_compression_level
    
    def create(
        self,
        strategy_type: str,
        duplicate_handler: Optional[DuplicateHandler] = None,
        dry_run: Optional[bool] = None,
        compression_level: Optional[int] = None,
        **kwargs
    ) -> S:
        """
        Create a file operation strategy.
        
        Args:
            strategy_type: Type of strategy to create
            duplicate_handler: Optional handler for duplicates
            dry_run: Whether to simulate operations without making changes
            compression_level: ZIP compression level (0-9)
            **kwargs: Additional strategy-specific arguments
            
        Returns:
            Created strategy
            
        Raises:
            ValueError: If strategy_type is unknown
        """
        # Use provided values or defaults
        dry_run = dry_run if dry_run is not None else self.default_dry_run
        compression_level = compression_level if compression_level is not None else self.default_compression_level
        
        # Create the appropriate strategy
        if strategy_type == "move_file":
            return MoveFileStrategy(dry_run=dry_run, duplicate_handler=duplicate_handler)
        elif strategy_type == "copy_file":
            return CopyFileStrategy(dry_run=dry_run, duplicate_handler=duplicate_handler)
        elif strategy_type == "archive":
            return ArchiveStrategy(
                compression_level=compression_level,
                dry_run=dry_run,
                duplicate_handler=duplicate_handler
            )
        elif strategy_type == "extract_archive":
            return ExtractArchiveStrategy(dry_run=dry_run, duplicate_handler=duplicate_handler)
        elif strategy_type == "rename_file":
            return RenameFileStrategy(dry_run=dry_run, duplicate_handler=duplicate_handler)
        else:
            raise ValueError(f"Unknown strategy type: {strategy_type}")


class ResultStrategyFactory(Factory[RS]):
    """Factory for creating result-based file operation strategies."""
    
    def __init__(
        self,
        default_dry_run: bool = False,
        default_compression_level: int = 6
    ):
        """
        Initialize the result strategy factory.
        
        Args:
            default_dry_run: Default value for dry_run
            default_compression_level: Default value for compression_level
        """
        self.default_dry_run = default_dry_run
        self.default_compression_level = default_compression_level
    
    def create(
        self,
        strategy_type: str,
        duplicate_handler: Optional[DuplicateHandler] = None,
        dry_run: Optional[bool] = None,
        compression_level: Optional[int] = None,
        **kwargs
    ) -> RS:
        """
        Create a result-based file operation strategy.
        
        Args:
            strategy_type: Type of strategy to create
            duplicate_handler: Optional handler for duplicates
            dry_run: Whether to simulate operations without making changes
            compression_level: ZIP compression level (0-9)
            **kwargs: Additional strategy-specific arguments
            
        Returns:
            Created strategy
            
        Raises:
            ValueError: If strategy_type is unknown
        """
        # Use provided values or defaults
        dry_run = dry_run if dry_run is not None else self.default_dry_run
        compression_level = compression_level if compression_level is not None else self.default_compression_level
        
        # Create the appropriate strategy
        if strategy_type == "move_file":
            return MoveFileResultStrategy(dry_run=dry_run, duplicate_handler=duplicate_handler)
        elif strategy_type == "copy_file":
            return CopyFileResultStrategy(dry_run=dry_run, duplicate_handler=duplicate_handler)
        elif strategy_type == "archive":
            return ArchiveResultStrategy(
                compression_level=compression_level,
                dry_run=dry_run,
                duplicate_handler=duplicate_handler
            )
        elif strategy_type == "extract_archive":
            return ExtractArchiveResultStrategy(dry_run=dry_run, duplicate_handler=duplicate_handler)
        elif strategy_type == "rename_file":
            return RenameFileResultStrategy(dry_run=dry_run, duplicate_handler=duplicate_handler)
        elif strategy_type == "delete_file":
            return DeleteFileResultStrategy(dry_run=dry_run)
        elif strategy_type == "delete_directory":
            recursive = kwargs.get("recursive", True)
            return DeleteDirectoryResultStrategy(recursive=recursive, dry_run=dry_run)
        else:
            raise ValueError(f"Unknown strategy type: {strategy_type}")


class DuplicateHandlerFactory(Factory[DuplicateHandler]):
    """Factory for creating duplicate handlers."""
    
    def create(
        self,
        strategy: Union[str, DuplicateStrategy] = DuplicateStrategy.RENAME_NEW,
        duplicates_dir: Optional[Union[str, Path]] = None,
        interactive: bool = False,
        dry_run: bool = False
    ) -> DuplicateHandler:
        """
        Create a duplicate handler.
        
        Args:
            strategy: Strategy for handling duplicates
            duplicates_dir: Directory to move duplicates to (if using MOVE_TO_DUPLICATES)
            interactive: Whether to ask the user for each duplicate
            dry_run: Whether to simulate operations without making changes
            
        Returns:
            Created duplicate handler
        """
        return DuplicateHandler(
            strategy=strategy,
            duplicates_dir=duplicates_dir,
            interactive=interactive,
            dry_run=dry_run
        )


class ProcessorFactory(Factory[P]):
    """Factory for creating file processors."""
    
    def __init__(
        self,
        strategy_factory: Optional[Union[StrategyFactory, ResultStrategyFactory]] = None,
        duplicate_handler_factory: Optional[DuplicateHandlerFactory] = None,
        default_dry_run: bool = False,
        default_compression_level: int = 6,
        default_duplicate_strategy: Union[str, DuplicateStrategy] = DuplicateStrategy.RENAME_NEW
    ):
        """
        Initialize the processor factory.
        
        Args:
            strategy_factory: Factory for creating strategies
            duplicate_handler_factory: Factory for creating duplicate handlers
            default_dry_run: Default value for dry_run
            default_compression_level: Default value for compression_level
            default_duplicate_strategy: Default duplicate handling strategy
        """
        self.strategy_factory = strategy_factory
        self.duplicate_handler_factory = duplicate_handler_factory or DuplicateHandlerFactory()
        self.default_dry_run = default_dry_run
        self.default_compression_level = default_compression_level
        self.default_duplicate_strategy = default_duplicate_strategy
    
    def create(
        self,
        processor_type: str = "standard",
        dry_run: Optional[bool] = None,
        compression_level: Optional[int] = None,
        duplicate_strategy: Optional[Union[str, DuplicateStrategy]] = None,
        duplicates_dir: Optional[Union[str, Path]] = None,
        interactive: bool = False,
        **kwargs
    ) -> P:
        """
        Create a file processor.
        
        Args:
            processor_type: Type of processor to create ("standard" or "result")
            dry_run: Whether to simulate operations without making changes
            compression_level: ZIP compression level (0-9)
            duplicate_strategy: Strategy for handling duplicates
            duplicates_dir: Directory to move duplicates to
            interactive: Whether to ask the user for each duplicate
            **kwargs: Additional processor-specific arguments
            
        Returns:
            Created processor
            
        Raises:
            ValueError: If processor_type is unknown
        """
        # Use provided values or defaults
        dry_run = dry_run if dry_run is not None else self.default_dry_run
        compression_level = compression_level if compression_level is not None else self.default_compression_level
        duplicate_strategy = duplicate_strategy if duplicate_strategy is not None else self.default_duplicate_strategy
        
        # Create duplicate handler
        duplicate_handler = self.duplicate_handler_factory.create(
            strategy=duplicate_strategy,
            duplicates_dir=duplicates_dir,
            interactive=interactive,
            dry_run=dry_run
        )
        
        # Create the appropriate processor
        if processor_type == "standard":
            # If no strategy factory is provided, create a standard one
            if not self.strategy_factory or not isinstance(self.strategy_factory, StrategyFactory):
                self.strategy_factory = StrategyFactory(
                    default_dry_run=dry_run,
                    default_compression_level=compression_level
                )
                
            return FileProcessor(
                dry_run=dry_run,
                compression_level=compression_level,
                duplicate_handler=duplicate_handler
            )
        elif processor_type == "result":
            # If no strategy factory is provided, create a result one
            if not self.strategy_factory or not isinstance(self.strategy_factory, ResultStrategyFactory):
                self.strategy_factory = ResultStrategyFactory(
                    default_dry_run=dry_run,
                    default_compression_level=compression_level
                )
                
            return ResultFileProcessor(
                dry_run=dry_run,
                compression_level=compression_level,
                duplicate_handler=duplicate_handler
            )
        else:
            raise ValueError(f"Unknown processor type: {processor_type}")


class ConfigBasedProcessorFactory(ProcessorFactory):
    """
    Factory for creating processors based on configuration.
    
    This factory reads configuration from a provided config object
    or from global application configuration.
    """
    
    def __init__(
        self,
        config: Optional[Any] = None,
        strategy_factory: Optional[Union[StrategyFactory, ResultStrategyFactory]] = None,
        duplicate_handler_factory: Optional[DuplicateHandlerFactory] = None
    ):
        """
        Initialize the config-based processor factory.
        
        Args:
            config: Configuration object or None to use global config
            strategy_factory: Factory for creating strategies
            duplicate_handler_factory: Factory for creating duplicate handlers
        """
        self.config = config
        
        # Load defaults from config
        default_dry_run = self._get_config_value("dry_run", False)
        default_compression_level = self._get_config_value("compression_level", 6)
        default_duplicate_strategy = self._get_config_value("duplicate_strategy", DuplicateStrategy.RENAME_NEW)
        
        super().__init__(
            strategy_factory=strategy_factory,
            duplicate_handler_factory=duplicate_handler_factory,
            default_dry_run=default_dry_run,
            default_compression_level=default_compression_level,
            default_duplicate_strategy=default_duplicate_strategy
        )
    
    def _get_config_value(self, key: str, default: Any) -> Any:
        """
        Get a value from configuration.
        
        Args:
            key: Configuration key
            default: Default value if key is not found
            
        Returns:
            Configuration value or default
        """
        if self.config is None:
            # Try to get from global config
            try:
                from collection_sorter.common.config import get_config
                config = get_config()
                
                # Navigate nested config structure based on dot notation
                keys = key.split(".")
                value = config
                for k in keys:
                    if hasattr(value, k):
                        value = getattr(value, k)
                    elif isinstance(value, dict) and k in value:
                        value = value[k]
                    else:
                        return default
                        
                return value
            except (ImportError, AttributeError):
                return default
        else:
            # Get from provided config
            try:
                # Navigate nested config structure based on dot notation
                keys = key.split(".")
                value = self.config
                for k in keys:
                    if hasattr(value, k):
                        value = getattr(value, k)
                    elif isinstance(value, dict) and k in value:
                        value = value[k]
                    else:
                        return default
                        
                return value
            except (AttributeError, KeyError):
                return default
    
    def create(
        self,
        processor_type: Optional[str] = None,
        **kwargs
    ) -> P:
        """
        Create a processor based on configuration.
        
        Args:
            processor_type: Type of processor to create
            **kwargs: Additional processor-specific arguments
            
        Returns:
            Created processor
        """
        # Get processor type from config if not provided
        if processor_type is None:
            processor_type = self._get_config_value("processor_type", "standard")
            
        # Get other config values
        dry_run = kwargs.get("dry_run", self._get_config_value("dry_run", self.default_dry_run))
        compression_level = kwargs.get("compression_level", self._get_config_value("compression_level", self.default_compression_level))
        duplicate_strategy = kwargs.get("duplicate_strategy", self._get_config_value("duplicate_strategy", self.default_duplicate_strategy))
        duplicates_dir = kwargs.get("duplicates_dir", self._get_config_value("duplicates_dir", None))
        interactive = kwargs.get("interactive", self._get_config_value("interactive", False))
        
        # Create the processor
        return super().create(
            processor_type=processor_type,
            dry_run=dry_run,
            compression_level=compression_level,
            duplicate_strategy=duplicate_strategy,
            duplicates_dir=duplicates_dir,
            interactive=interactive,
            **kwargs
        )


# Global factory instances for easy access
strategy_factory = StrategyFactory()
result_strategy_factory = ResultStrategyFactory()
duplicate_handler_factory = DuplicateHandlerFactory()
processor_factory = ProcessorFactory(
    strategy_factory=strategy_factory,
    duplicate_handler_factory=duplicate_handler_factory
)
config_processor_factory = ConfigBasedProcessorFactory(
    strategy_factory=strategy_factory,
    duplicate_handler_factory=duplicate_handler_factory
)


# Register factories with the service provider
register_service(Factory[FileOperationStrategy], strategy_factory)
register_service(Factory[ResultFileOperationStrategy], result_strategy_factory)
register_service(Factory[DuplicateHandler], duplicate_handler_factory)
register_service(Factory[FileProcessor], processor_factory)
register_service(Factory[ResultFileProcessor], config_processor_factory)


# Utility functions for creating instances
def create_strategy(
    strategy_type: str,
    duplicate_handler: Optional[DuplicateHandler] = None,
    dry_run: Optional[bool] = None,
    compression_level: Optional[int] = None,
    **kwargs
) -> FileOperationStrategy:
    """
    Create a file operation strategy.
    
    Args:
        strategy_type: Type of strategy to create
        duplicate_handler: Optional handler for duplicates
        dry_run: Whether to simulate operations without making changes
        compression_level: ZIP compression level (0-9)
        **kwargs: Additional strategy-specific arguments
        
    Returns:
        Created strategy
    """
    return strategy_factory.create(
        strategy_type=strategy_type,
        duplicate_handler=duplicate_handler,
        dry_run=dry_run,
        compression_level=compression_level,
        **kwargs
    )


def create_result_strategy(
    strategy_type: str,
    duplicate_handler: Optional[DuplicateHandler] = None,
    dry_run: Optional[bool] = None,
    compression_level: Optional[int] = None,
    **kwargs
) -> ResultFileOperationStrategy:
    """
    Create a result-based file operation strategy.
    
    Args:
        strategy_type: Type of strategy to create
        duplicate_handler: Optional handler for duplicates
        dry_run: Whether to simulate operations without making changes
        compression_level: ZIP compression level (0-9)
        **kwargs: Additional strategy-specific arguments
        
    Returns:
        Created strategy
    """
    return result_strategy_factory.create(
        strategy_type=strategy_type,
        duplicate_handler=duplicate_handler,
        dry_run=dry_run,
        compression_level=compression_level,
        **kwargs
    )


def create_duplicate_handler(
    strategy: Union[str, DuplicateStrategy] = DuplicateStrategy.RENAME_NEW,
    duplicates_dir: Optional[Union[str, Path]] = None,
    interactive: bool = False,
    dry_run: bool = False
) -> DuplicateHandler:
    """
    Create a duplicate handler.
    
    Args:
        strategy: Strategy for handling duplicates
        duplicates_dir: Directory to move duplicates to (if using MOVE_TO_DUPLICATES)
        interactive: Whether to ask the user for each duplicate
        dry_run: Whether to simulate operations without making changes
        
    Returns:
        Created duplicate handler
    """
    return duplicate_handler_factory.create(
        strategy=strategy,
        duplicates_dir=duplicates_dir,
        interactive=interactive,
        dry_run=dry_run
    )


def create_processor(
    processor_type: str = "standard",
    dry_run: bool = False,
    compression_level: int = 6,
    duplicate_strategy: Union[str, DuplicateStrategy] = DuplicateStrategy.RENAME_NEW,
    duplicates_dir: Optional[Union[str, Path]] = None,
    interactive: bool = False,
    **kwargs
) -> Union[FileProcessor, ResultFileProcessor]:
    """
    Create a file processor.
    
    Args:
        processor_type: Type of processor to create ("standard" or "result")
        dry_run: Whether to simulate operations without making changes
        compression_level: ZIP compression level (0-9)
        duplicate_strategy: Strategy for handling duplicates
        duplicates_dir: Directory to move duplicates to
        interactive: Whether to ask the user for each duplicate
        **kwargs: Additional processor-specific arguments
        
    Returns:
        Created processor
    """
    return processor_factory.create(
        processor_type=processor_type,
        dry_run=dry_run,
        compression_level=compression_level,
        duplicate_strategy=duplicate_strategy,
        duplicates_dir=duplicates_dir,
        interactive=interactive,
        **kwargs
    )


def create_processor_from_config(
    processor_type: Optional[str] = None,
    **kwargs
) -> Union[FileProcessor, ResultFileProcessor]:
    """
    Create a processor based on configuration.
    
    Args:
        processor_type: Type of processor to create
        **kwargs: Additional processor-specific arguments
        
    Returns:
        Created processor
    """
    return config_processor_factory.create(
        processor_type=processor_type,
        **kwargs
    )