"""
Tests for the Template Method pattern implementation.
"""

import shutil
import tempfile
import unittest
from pathlib import Path

from collection_sorter.common.duplicates import DuplicateHandler, DuplicateStrategy
from collection_sorter.common.result import Result, OperationError, ErrorType
from collection_sorter.common.templates import (
    FileProcessorTemplate,
    FileMoveTemplate,
    FileCopyTemplate,
    FileRenameTemplate,
    DirectoryCopyTemplate,
    DirectoryMoveTemplate,
    ArchiveDirectoryTemplate,
    BatchProcessorTemplate
)


class CustomFileProcessor(FileProcessorTemplate):
    """Custom file processor for testing."""
    
    def _execute_operation(self, source_path, destination_path, **kwargs):
        """Custom operation implementation for testing."""
        try:
            if self.dry_run:
                return Result.success(destination_path)
                
            # Copy the file with some modification
            with open(source_path.path, 'r') as f:
                content = f.read()
                
            with open(destination_path.path, 'w') as f:
                f.write(f"MODIFIED: {content}")
                
            return Result.success(destination_path)
            
        except Exception as e:
            return Result.failure(OperationError(
                type=ErrorType.OPERATION_FAILED,
                message=f"Custom operation failed: {str(e)}",
                path=str(source_path),
                source_exception=e
            ))


class TestTemplateMethod(unittest.TestCase):
    """Test case for the Template Method pattern implementation."""
    
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
        
        # Create a subdirectory with files
        self.sub_dir = self.source_dir / "subdir"
        self.sub_dir.mkdir()
        
        for i in range(3):
            file_path = self.sub_dir / f"file{i}.txt"
            with open(file_path, "w") as f:
                f.write(f"Content {i}")
    
    def tearDown(self):
        """Clean up test environment."""
        # Remove temporary directories
        shutil.rmtree(self.temp_dir)
    
    def test_file_move_template(self):
        """Test the FileMoveTemplate class."""
        # Create a move template
        mover = FileMoveTemplate(dry_run=False)
        
        # Process a file
        destination_file = self.dest_dir / "moved.txt"
        result = mover.process_file(self.test_file, destination_file)
        
        # Check the result
        self.assertTrue(result.is_success())
        self.assertEqual(str(result.unwrap()), str(destination_file))
        self.assertTrue(destination_file.exists())
        self.assertFalse(self.test_file.exists())
        
        # Test with dry_run=True
        # First restore the test file
        test_file2 = self.source_dir / "test2.txt"
        with open(test_file2, "w") as f:
            f.write("Test content 2")
            
        dry_mover = FileMoveTemplate(dry_run=True)
        destination_file2 = self.dest_dir / "moved2.txt"
        result = dry_mover.process_file(test_file2, destination_file2)
        
        # Check the result
        self.assertTrue(result.is_success())
        self.assertEqual(str(result.unwrap()), str(destination_file2))
        self.assertFalse(destination_file2.exists())  # Not actually moved
        self.assertTrue(test_file2.exists())  # Source still exists
    
    def test_file_copy_template(self):
        """Test the FileCopyTemplate class."""
        # Create a copy template
        copier = FileCopyTemplate(dry_run=False)
        
        # Process a file
        destination_file = self.dest_dir / "copied.txt"
        result = copier.process_file(self.test_file, destination_file)
        
        # Check the result
        self.assertTrue(result.is_success())
        self.assertEqual(str(result.unwrap()), str(destination_file))
        self.assertTrue(destination_file.exists())
        self.assertTrue(self.test_file.exists())  # Source still exists
        
        # Verify content
        with open(destination_file, "r") as f:
            content = f.read()
        self.assertEqual(content, "Test content")
    
    def test_file_rename_template(self):
        """Test the FileRenameTemplate class."""
        # Create a rename template
        renamer = FileRenameTemplate(dry_run=False)
        
        # Process a file
        new_name = self.source_dir / "renamed.txt"
        result = renamer.process_file(self.test_file, new_name)
        
        # Check the result
        self.assertTrue(result.is_success())
        self.assertEqual(str(result.unwrap()), str(new_name))
        self.assertTrue(new_name.exists())
        self.assertFalse(self.test_file.exists())
    
    def test_directory_copy_template(self):
        """Test the DirectoryCopyTemplate class."""
        # Create a directory copy template
        copier = DirectoryCopyTemplate(dry_run=False, recursive=True)
        
        # Process a directory
        destination_dir = self.dest_dir / "subdir_copy"
        result = copier.process_directory(self.sub_dir, destination_dir)
        
        # Check the result
        self.assertTrue(result.is_success())
        self.assertEqual(str(result.unwrap()), str(destination_dir))
        self.assertTrue(destination_dir.exists())
        self.assertTrue(self.sub_dir.exists())  # Source still exists
        
        # Verify copied files
        for i in range(3):
            file_path = destination_dir / f"file{i}.txt"
            self.assertTrue(file_path.exists())
            
            with open(file_path, "r") as f:
                content = f.read()
            self.assertEqual(content, f"Content {i}")
    
    def test_directory_move_template(self):
        """Test the DirectoryMoveTemplate class."""
        # Create a directory move template
        mover = DirectoryMoveTemplate(dry_run=False, recursive=True)
        
        # Process a directory
        destination_dir = self.dest_dir / "subdir_moved"
        result = mover.process_directory(self.sub_dir, destination_dir)
        
        # Check the result
        self.assertTrue(result.is_success())
        self.assertEqual(str(result.unwrap()), str(destination_dir))
        self.assertTrue(destination_dir.exists())
        self.assertFalse(self.sub_dir.exists())  # Source should be gone
        
        # Verify moved files
        for i in range(3):
            file_path = destination_dir / f"file{i}.txt"
            self.assertTrue(file_path.exists())
            
            with open(file_path, "r") as f:
                content = f.read()
            self.assertEqual(content, f"Content {i}")
    
    def test_archive_directory_template(self):
        """Test the ArchiveDirectoryTemplate class."""
        # Create test files first since previous test moved them
        self.sub_dir = self.source_dir / "archive_test"
        self.sub_dir.mkdir()
        
        for i in range(3):
            file_path = self.sub_dir / f"archive{i}.txt"
            with open(file_path, "w") as f:
                f.write(f"Archive content {i}")
                
        # Create an archive template
        archiver = ArchiveDirectoryTemplate(
            dry_run=False,
            recursive=True,
            compression_level=6
        )
        
        # Process a directory
        archive_name = "custom_archive"
        result = archiver.process_directory(
            self.sub_dir,
            self.dest_dir,
            archive_name=archive_name
        )
        
        # Check the result
        self.assertTrue(result.is_success())
        expected_path = self.dest_dir / f"{archive_name}.zip"
        self.assertEqual(str(result.unwrap()), str(expected_path))
        self.assertTrue(expected_path.exists())
        self.assertTrue(self.sub_dir.exists())  # Source still exists by default
        
        # Test with remove_source=True
        archiver2 = ArchiveDirectoryTemplate(
            dry_run=False,
            recursive=True
        )
        
        # Process the directory again with remove_source=True
        result = archiver2.process_directory(
            self.sub_dir,
            self.dest_dir,
            archive_name="archive_and_remove",
            remove_source=True
        )
        
        # Check the result
        self.assertTrue(result.is_success())
        expected_path = self.dest_dir / "archive_and_remove.zip"
        self.assertEqual(str(result.unwrap()), str(expected_path))
        self.assertTrue(expected_path.exists())
        self.assertFalse(self.sub_dir.exists())  # Source should be gone
    
    def test_batch_processor_template(self):
        """Test the BatchProcessorTemplate class."""
        # Create multiple source files and directories
        sources = []
        
        for i in range(3):
            file_path = self.source_dir / f"batch{i}.txt"
            with open(file_path, "w") as f:
                f.write(f"Batch content {i}")
            sources.append(file_path)
            
        for i in range(2):
            dir_path = self.source_dir / f"batch_dir{i}"
            dir_path.mkdir()
            with open(dir_path / "file.txt", "w") as f:
                f.write(f"Directory {i} content")
            sources.append(dir_path)
        
        # Create processors
        file_processor = FileCopyTemplate(dry_run=False)
        dir_processor = DirectoryCopyTemplate(dry_run=False, recursive=True)
        
        # Create a batch processor
        batch_processor = BatchProcessorTemplate(
            file_processor=file_processor,
            directory_processor=dir_processor,
            continue_on_error=True
        )
        
        # Process the batch
        destination_dir = self.dest_dir / "batch"
        result = batch_processor.process_batch(sources, destination_dir)
        
        # Check the result
        self.assertTrue(result.is_success())
        processed_paths = result.unwrap()
        self.assertEqual(len(processed_paths), len(sources))
        
        # Verify the processed files and directories
        for i in range(3):
            file_path = destination_dir / f"batch{i}.txt"
            self.assertTrue(file_path.exists())
            
        for i in range(2):
            dir_path = destination_dir / f"batch_dir{i}"
            self.assertTrue(dir_path.exists())
            self.assertTrue((dir_path / "file.txt").exists())
    
    def test_custom_file_processor(self):
        """Test a custom file processor."""
        # Create a custom processor
        processor = CustomFileProcessor(dry_run=False)
        
        # Process a file
        destination_file = self.dest_dir / "custom.txt"
        result = processor.process_file(self.test_file, destination_file)
        
        # Check the result
        self.assertTrue(result.is_success())
        self.assertEqual(str(result.unwrap()), str(destination_file))
        self.assertTrue(destination_file.exists())
        self.assertTrue(self.test_file.exists())  # Source still exists (not moved)
        
        # Verify the modified content
        with open(destination_file, "r") as f:
            content = f.read()
        self.assertEqual(content, "MODIFIED: Test content")
    
    def test_duplicate_handling(self):
        """Test duplicate handling in templates."""
        # Create a duplicate handler
        duplicate_handler = DuplicateHandler(
            strategy=DuplicateStrategy.RENAME_NEW,
            dry_run=False
        )
        
        # Create a copy template with the duplicate handler
        copier = FileCopyTemplate(
            dry_run=False,
            duplicate_handler=duplicate_handler
        )
        
        # Copy a file
        destination_file = self.dest_dir / "duplicate.txt"
        
        # First copy
        result1 = copier.process_file(self.test_file, destination_file)
        self.assertTrue(result1.is_success())
        self.assertEqual(str(result1.unwrap()), str(destination_file))
        self.assertTrue(destination_file.exists())
        
        # Second copy (should rename)
        result2 = copier.process_file(self.test_file, destination_file)
        self.assertTrue(result2.is_success())
        self.assertNotEqual(str(result2.unwrap()), str(destination_file))
        self.assertTrue("duplicate" in str(result2.unwrap()))
        
        # Test with SKIP strategy
        skip_handler = DuplicateHandler(
            strategy=DuplicateStrategy.SKIP,
            dry_run=False
        )
        
        skip_copier = FileCopyTemplate(
            dry_run=False,
            duplicate_handler=skip_handler
        )
        
        # Try to copy again (should skip)
        result3 = skip_copier.process_file(self.test_file, destination_file)
        self.assertTrue(result3.is_success())
        self.assertEqual(str(result3.unwrap()), str(destination_file))
        
        # Should have the same number of files as before
        existing_files = list(self.dest_dir.glob("*.txt"))
        self.assertEqual(len(existing_files), 2)  # Original + renamed
    
    def test_error_handling(self):
        """Test error handling in templates."""
        # Test with non-existent source
        mover = FileMoveTemplate(dry_run=False)
        result = mover.process_file(
            self.source_dir / "nonexistent.txt",
            self.dest_dir / "error.txt"
        )
        
        # Check the result
        self.assertTrue(result.is_failure())
        self.assertEqual(result.error().type, ErrorType.FILE_NOT_FOUND)
        
        # Test with read/write errors
        class ReadErrorProcessor(FileProcessorTemplate):
            def _execute_operation(self, source_path, destination_path, **kwargs):
                raise PermissionError("Read error")
        
        processor = ReadErrorProcessor(dry_run=False)
        result = processor.process_file(self.test_file, self.dest_dir / "error.txt")
        
        # Check the result
        self.assertTrue(result.is_failure())
        self.assertEqual(result.error().type, ErrorType.OPERATION_FAILED)
        self.assertIsInstance(result.error().source_exception, PermissionError)


if __name__ == "__main__":
    unittest.main()