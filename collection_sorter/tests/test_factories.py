"""
Tests for the Factory pattern implementation.
"""

import unittest
from pathlib import Path

from collection_sorter.common.duplicates import DuplicateStrategy
from collection_sorter.common.factories import (
    StrategyFactory,
    ResultStrategyFactory,
    DuplicateHandlerFactory,
    ProcessorFactory,
    ConfigBasedProcessorFactory,
    create_strategy,
    create_result_strategy,
    create_duplicate_handler,
    create_processor,
    create_processor_from_config
)
from collection_sorter.common.file_processor import FileProcessor
from collection_sorter.common.result_processor import ResultFileProcessor
from collection_sorter.common.result_strategies import (
    MoveFileResultStrategy,
    CopyFileResultStrategy,
    RenameFileResultStrategy,
    DeleteFileResultStrategy
)
from collection_sorter.common.strategies import (
    MoveFileStrategy,
    CopyFileStrategy,
    ArchiveStrategy
)


class TestFactories(unittest.TestCase):
    """Test case for the Factory pattern implementation."""
    
    def test_strategy_factory(self):
        """Test the StrategyFactory class."""
        # Create a factory
        factory = StrategyFactory(
            default_dry_run=False,
            default_compression_level=6
        )
        
        # Create strategies
        move_strategy = factory.create("move_file")
        copy_strategy = factory.create("copy_file", dry_run=True)
        archive_strategy = factory.create(
            "archive",
            compression_level=9
        )
        
        # Check strategy types
        self.assertIsInstance(move_strategy, MoveFileStrategy)
        self.assertIsInstance(copy_strategy, CopyFileStrategy)
        self.assertIsInstance(archive_strategy, ArchiveStrategy)
        
        # Check strategy properties
        self.assertFalse(move_strategy.dry_run)
        self.assertTrue(copy_strategy.dry_run)
        self.assertEqual(archive_strategy.compression_level, 9)
        
        # Test invalid strategy type
        with self.assertRaises(ValueError):
            factory.create("invalid_strategy")
    
    def test_result_strategy_factory(self):
        """Test the ResultStrategyFactory class."""
        # Create a factory
        factory = ResultStrategyFactory(
            default_dry_run=True,
            default_compression_level=7
        )
        
        # Create strategies
        move_strategy = factory.create("move_file")
        rename_strategy = factory.create("rename_file", dry_run=False)
        delete_strategy = factory.create("delete_file")
        
        # Check strategy types
        self.assertIsInstance(move_strategy, MoveFileResultStrategy)
        self.assertIsInstance(rename_strategy, RenameFileResultStrategy)
        self.assertIsInstance(delete_strategy, DeleteFileResultStrategy)
        
        # Check strategy properties
        self.assertTrue(move_strategy.dry_run)
        self.assertFalse(rename_strategy.dry_run)
    
    def test_duplicate_handler_factory(self):
        """Test the DuplicateHandlerFactory class."""
        # Create a factory
        factory = DuplicateHandlerFactory()
        
        # Create handlers
        handler1 = factory.create(DuplicateStrategy.RENAME_NEW)
        handler2 = factory.create(
            strategy=DuplicateStrategy.MOVE_TO_DUPLICATES,
            duplicates_dir="/tmp/duplicates",
            interactive=True
        )
        
        # Check handler properties
        self.assertEqual(handler1.strategy, DuplicateStrategy.RENAME_NEW)
        self.assertEqual(handler2.strategy, DuplicateStrategy.MOVE_TO_DUPLICATES)
        self.assertEqual(handler2.duplicates_dir, Path("/tmp/duplicates"))
        self.assertTrue(handler2.interactive)  # Should be overridden by the strategy
    
    def test_processor_factory(self):
        """Test the ProcessorFactory class."""
        # Create a factory
        factory = ProcessorFactory(
            default_dry_run=False,
            default_compression_level=6,
            default_duplicate_strategy=DuplicateStrategy.RENAME_NEW
        )
        
        # Create processors
        processor1 = factory.create("standard")
        processor2 = factory.create(
            "result",
            dry_run=True,
            duplicate_strategy=DuplicateStrategy.SKIP
        )
        
        # Check processor types
        self.assertIsInstance(processor1, FileProcessor)
        self.assertIsInstance(processor2, ResultFileProcessor)
        
        # Check processor properties
        self.assertFalse(processor1.dry_run)
        self.assertTrue(processor2.dry_run)
        self.assertEqual(processor2.duplicate_handler.strategy, DuplicateStrategy.SKIP)
        
        # Test invalid processor type
        with self.assertRaises(ValueError):
            factory.create("invalid_processor")
    
    def test_config_based_processor_factory(self):
        """Test the ConfigBasedProcessorFactory class."""
        # Create a factory with a simple dictionary config
        config = {
            "processor_type": "result",
            "dry_run": True,
            "compression_level": 9,
            "duplicate_strategy": "skip",
            "interactive": True
        }
        
        factory = ConfigBasedProcessorFactory(config=config)
        
        # Create a processor using the config
        processor = factory.create()
        
        # Check processor type and properties
        self.assertIsInstance(processor, ResultFileProcessor)
        self.assertTrue(processor.dry_run)
        self.assertEqual(processor.compression_level, 9)
        self.assertEqual(processor.duplicate_handler.strategy, DuplicateStrategy.SKIP)
        
        # Create a processor with overrides
        processor2 = factory.create(
            processor_type="standard",
            dry_run=False
        )
        
        # Check that overrides were applied
        self.assertIsInstance(processor2, FileProcessor)
        self.assertFalse(processor2.dry_run)
        self.assertEqual(processor2.compression_level, 9)  # From config
    
    def test_utility_functions(self):
        """Test the utility functions for creating instances."""
        # Test create_strategy
        strategy = create_strategy("move_file", dry_run=True)
        self.assertIsInstance(strategy, MoveFileStrategy)
        self.assertTrue(strategy.dry_run)
        
        # Test create_result_strategy
        result_strategy = create_result_strategy("copy_file")
        self.assertIsInstance(result_strategy, CopyFileResultStrategy)
        
        # Test create_duplicate_handler
        handler = create_duplicate_handler(DuplicateStrategy.RENAME_EXISTING)
        self.assertEqual(handler.strategy, DuplicateStrategy.RENAME_EXISTING)
        
        # Test create_processor
        processor = create_processor("standard")
        self.assertIsInstance(processor, FileProcessor)
        
        # Test create_processor_from_config
        # We don't have a real config, so just test with overrides
        config_processor = create_processor_from_config(
            processor_type="result",
            dry_run=True
        )
        self.assertIsInstance(config_processor, ResultFileProcessor)
        self.assertTrue(config_processor.dry_run)


if __name__ == "__main__":
    unittest.main()