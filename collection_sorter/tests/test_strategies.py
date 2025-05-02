"""
Tests for the Strategy pattern implementation.
"""

import os
import shutil
import tempfile
import unittest
from pathlib import Path

from collection_sorter.common.duplicates import DuplicateHandler, DuplicateStrategy
from collection_sorter.common.paths import FilePath
from collection_sorter.common.strategies import (
    MoveFileStrategy,
    CopyFileStrategy,
    FileOperationContext
)
from collection_sorter.common.file_processor import FileProcessor


class TestFileStrategies(unittest.TestCase):
    """Test case for file operation strategies."""
    
    def setUp(self):
        """Set up test environment."""
        # Create temporary directories
        self.temp_dir = tempfile.mkdtemp()
        self.source_dir = Path(self.temp_dir) / "source"
        self.dest_dir = Path(self.temp_dir) / "dest"
        
        # Create directories
        self.source_dir.mkdir()
        self.dest_dir.mkdir()
        
        # Create a test file
        self.test_file = self.source_dir / "test.txt"
        with open(self.test_file, "w") as f:
            f.write("Test content")
    
    def tearDown(self):
        """Clean up test environment."""
        # Remove temporary directories
        shutil.rmtree(self.temp_dir)
    
    def test_move_strategy(self):
        """Test the move file strategy."""
        # Create a strategy
        strategy = MoveFileStrategy(dry_run=False)
        
        # Create a context
        context = FileOperationContext(strategy)
        
        # Define paths
        source = FilePath(self.test_file)
        destination = FilePath(self.dest_dir / "test.txt", must_exist=False)
        
        # Execute the strategy
        result = context.execute(source, destination)
        
        # Check that the file was moved
        self.assertFalse(self.test_file.exists())
        self.assertTrue((self.dest_dir / "test.txt").exists())
        self.assertEqual(str(result), str(destination))
    
    def test_copy_strategy(self):
        """Test the copy file strategy."""
        # Create a strategy
        strategy = CopyFileStrategy(dry_run=False)
        
        # Create a context
        context = FileOperationContext(strategy)
        
        # Define paths
        source = FilePath(self.test_file)
        destination = FilePath(self.dest_dir / "test.txt", must_exist=False)
        
        # Execute the strategy
        result = context.execute(source, destination)
        
        # Check that the file was copied
        self.assertTrue(self.test_file.exists())
        self.assertTrue((self.dest_dir / "test.txt").exists())
        self.assertEqual(str(result), str(destination))
    
    def test_file_processor(self):
        """Test the file processor with strategies."""
        # Create a processor
        processor = FileProcessor(dry_run=False)
        
        # Create another test file
        test_file2 = self.source_dir / "test2.txt"
        with open(test_file2, "w") as f:
            f.write("Test content 2")
        
        # Move a file
        moved_file = processor.move_file(self.test_file, self.dest_dir / "test.txt")
        
        # Copy a file
        copied_file = processor.copy_file(test_file2, self.dest_dir / "test2.txt")
        
        # Check results
        self.assertFalse(self.test_file.exists())
        self.assertTrue((self.dest_dir / "test.txt").exists())
        self.assertTrue(test_file2.exists())
        self.assertTrue((self.dest_dir / "test2.txt").exists())
    
    def test_duplicate_handling(self):
        """Test duplicate handling with strategies."""
        # Create a duplicate handler
        handler = DuplicateHandler(strategy=DuplicateStrategy.RENAME_NEW)
        
        # Create a processor with the handler
        processor = FileProcessor(duplicate_handler=handler)
        
        # Create a test file in both source and destination
        with open(self.dest_dir / "test.txt", "w") as f:
            f.write("Existing content")
        
        # Copy the file (should handle the duplicate)
        copied_file = processor.copy_file(self.test_file, self.dest_dir / "test.txt")
        
        # Check that both files exist
        self.assertTrue(self.test_file.exists())
        self.assertTrue((self.dest_dir / "test.txt").exists())
        
        # The new file should have been renamed
        self.assertNotEqual(str(copied_file), str(self.dest_dir / "test.txt"))
        self.assertTrue("duplicate" in str(copied_file))


if __name__ == "__main__":
    unittest.main()