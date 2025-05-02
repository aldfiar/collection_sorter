"""
Example usage of the Factory pattern for file handlers.

This module demonstrates how to use the Factory pattern to create
file processors, strategies, and handlers.
"""

import logging
from pathlib import Path
from typing import Optional, Union

from collection_sorter.common.duplicates import DuplicateStrategy
from collection_sorter.common.paths import FilePath
from collection_sorter.common.factories import (
    strategy_factory,
    result_strategy_factory,
    duplicate_handler_factory,
    processor_factory,
    config_processor_factory,
    create_strategy,
    create_result_strategy,
    create_duplicate_handler,
    create_processor,
    create_processor_from_config
)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("factory_example")


def main():
    """Example of using the Factory pattern for file handlers."""
    
    # Example 1: Creating a strategy directly using the factory
    move_strategy = strategy_factory.create(
        strategy_type="move_file",
        dry_run=False
    )
    logger.info(f"Created move strategy: {move_strategy.name}")
    
    # Example 2: Creating a result strategy using the utility function
    copy_strategy = create_result_strategy(
        strategy_type="copy_file",
        dry_run=True
    )
    logger.info(f"Created copy strategy: {copy_strategy.name}")
    
    # Example 3: Creating a duplicate handler
    duplicate_handler = create_duplicate_handler(
        strategy=DuplicateStrategy.RENAME_NEW,
        dry_run=False
    )
    logger.info(f"Created duplicate handler with strategy: {duplicate_handler.strategy}")
    
    # Example 4: Creating a standard processor with the factory
    processor = processor_factory.create(
        processor_type="standard",
        dry_run=False,
        compression_level=9,
        duplicate_strategy=DuplicateStrategy.ASK,
        interactive=True
    )
    logger.info(f"Created processor with strategies: {processor.strategies.keys()}")
    
    # Example 5: Creating a result processor using the utility function
    result_processor = create_processor(
        processor_type="result",
        dry_run=True,
        duplicate_strategy=DuplicateStrategy.MOVE_TO_DUPLICATES,
        duplicates_dir="/path/to/duplicates"
    )
    logger.info(f"Created result processor with strategies: {result_processor.strategies.keys()}")
    
    # Example 6: Creating a processor from configuration
    # Normally this would use actual config, but we're using kwargs as a stand-in
    config_processor = create_processor_from_config(
        processor_type="result",
        dry_run=True,
        compression_level=6,
        duplicate_strategy=DuplicateStrategy.SKIP
    )
    logger.info(f"Created processor from config")
    
    # Example 7: Using the created processor with different strategies
    source_file = Path("/path/to/source/file.txt")
    destination_file = Path("/path/to/destination/file.txt")
    
    # Switch to a different strategy at runtime
    processor.set_strategy("copy_file")
    
    # Process files with different strategies
    logger.info("Processing files with different strategies:")
    for strategy_name in ["move_file", "copy_file", "rename_file"]:
        processor.set_strategy(strategy_name)
        logger.info(f"Using strategy: {strategy_name}")
        # In a real scenario, we would process files here
    
    # Example 8: Creating a custom factory subclass
    from collection_sorter.common.factories import ProcessorFactory, StrategyFactory
    
    class CustomStrategyFactory(StrategyFactory):
        """Custom strategy factory with specialized behavior."""
        
        def create(self, strategy_type, **kwargs):
            """Create a strategy with custom defaults."""
            # Always create strategies in dry-run mode for safety
            kwargs["dry_run"] = True
            return super().create(strategy_type, **kwargs)
    
    custom_factory = CustomStrategyFactory()
    safe_strategy = custom_factory.create("move_file")
    logger.info(f"Created safe strategy with dry_run={safe_strategy.dry_run}")


if __name__ == "__main__":
    main()