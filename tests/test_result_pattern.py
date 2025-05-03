"""
Tests for the Result pattern implementation.
"""

import shutil
import tempfile
import unittest
from pathlib import Path

from collection_sorter.files.operations import (
    check_path_exists, ensure_directory, list_files, move_file, copy_file, rename_file, archive_directory,
    extract_archive,
    delete_file, delete_directory
)
from collection_sorter.common.result import (
    Result, OperationError, ErrorType, result_handler
)
from collection_sorter.result.result_processor import ResultFileProcessor


class TestResultPattern(unittest.TestCase):
    """Test case for the Result pattern implementation."""
    
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
    
    def test_result_success(self):
        """Test the Success variant of Result."""
        # Create a success result
        result = Result.success(42)
        
        # Check result properties
        self.assertTrue(result.is_success())
        self.assertFalse(result.is_failure())
        self.assertEqual(result.unwrap(), 42)
        self.assertEqual(result.unwrap_or(0), 42)
        self.assertEqual(result.unwrap_or_else(lambda _: 0), 42)
        
        # Test map
        mapped_result = result.map(lambda x: x * 2)
        self.assertTrue(mapped_result.is_success())
        self.assertEqual(mapped_result.unwrap(), 84)
        
        # Test and_then
        chained_result = result.and_then(lambda x: Result.success(x + 10))
        self.assertTrue(chained_result.is_success())
        self.assertEqual(chained_result.unwrap(), 52)
    
    def test_result_failure(self):
        """Test the Failure variant of Result."""
        # Create a failure result
        error = OperationError(ErrorType.FILE_NOT_FOUND, "File not found", "/tmp/missing.txt")
        result = Result.failure(error)
        
        # Check result properties
        self.assertFalse(result.is_success())
        self.assertTrue(result.is_failure())
        self.assertEqual(result.error(), error)
        self.assertEqual(result.unwrap_or(42), 42)
        self.assertEqual(result.unwrap_or_else(lambda _: 84), 84)
        
        # Test map (should be a no-op for failure)
        mapped_result = result.map(lambda x: x * 2)
        self.assertTrue(mapped_result.is_failure())
        self.assertEqual(mapped_result.error(), error)
        
        # Test and_then (should be a no-op for failure)
        chained_result = result.and_then(lambda x: Result.success(x + 10))
        self.assertTrue(chained_result.is_failure())
        self.assertEqual(chained_result.error(), error)
        
        # Test or_else
        recovered_result = result.or_else(lambda _: Result.success(42))
        self.assertTrue(recovered_result.is_success())
        self.assertEqual(recovered_result.unwrap(), 42)
    
    def test_result_from_exception(self):
        """Test creating a result from an exception."""
        # Create a result from a function that raises an exception
        def failing_function():
            raise ValueError("Something went wrong")
        
        result = Result.from_exception(failing_function)
        
        # Check result properties
        self.assertFalse(result.is_success())
        self.assertTrue(result.is_failure())
        self.assertIsInstance(result.error(), ValueError)
        self.assertEqual(str(result.error()), "Something went wrong")
    
    def test_result_collect(self):
        """Test collecting multiple results."""
        # Create some results
        results = [
            Result.success(1),
            Result.success(2),
            Result.success(3)
        ]
        
        # Collect the results
        collected = Result.collect(results)
        
        # Check result properties
        self.assertTrue(collected.is_success())
        self.assertEqual(collected.unwrap(), [1, 2, 3])
        
        # Add a failure result
        error = OperationError(ErrorType.VALIDATION_ERROR, "Invalid value")
        results.append(Result.failure(error))
        
        # Collect the results again
        collected = Result.collect(results)
        
        # Check result properties
        self.assertFalse(collected.is_success())
        self.assertEqual(len(collected.error()), 1)
        self.assertEqual(collected.error()[0], error)
    
    def test_operation_error(self):
        """Test the OperationError class."""
        # Create an operation error
        error = OperationError(
            type=ErrorType.FILE_NOT_FOUND,
            message="File not found",
            path="/tmp/missing.txt"
        )
        
        # Check error properties
        self.assertEqual(error.type, ErrorType.FILE_NOT_FOUND)
        self.assertEqual(error.message, "File not found")
        self.assertEqual(error.path, "/tmp/missing.txt")
        
        # Test string representation
        self.assertEqual(str(error), "FILE_NOT_FOUND: File not found (path: /tmp/missing.txt)")
        
        # Test creating from an exception
        exception = FileNotFoundError("File not found")
        error_from_exception = OperationError.from_exception(exception, "/tmp/missing.txt")
        
        self.assertEqual(error_from_exception.type, ErrorType.FILE_NOT_FOUND)
        self.assertEqual(error_from_exception.message, "File not found")
        self.assertEqual(error_from_exception.path, "/tmp/missing.txt")
    
    def test_result_handler_decorator(self):
        """Test the result_handler decorator."""
        # Create a decorated function
        @result_handler
        def add(a, b):
            return a + b
        
        # Call the function
        result = add(1, 2)
        
        # Check result properties
        self.assertTrue(result.is_success())
        self.assertEqual(result.unwrap(), 3)
        
        # Create a decorated function that raises an exception
        @result_handler
        def divide(a, b):
            return a / b
        
        # Call the function with invalid arguments
        result = divide(1, 0)
        
        # Check result properties
        self.assertFalse(result.is_success())
        self.assertTrue(result.is_failure())
        self.assertIsInstance(result.error(), OperationError)
        self.assertEqual(result.error().type, ErrorType.UNKNOWN)
    
    def test_file_operations(self):
        """Test the file operations with the Result pattern."""
        # Test check_path_exists
        exists_result = check_path_exists(self.test_file)
        self.assertTrue(exists_result.is_success())
        self.assertTrue(exists_result.unwrap())
        
        # Test ensure_directory
        new_dir_path = self.source_dir / "new_dir"
        ensure_result = ensure_directory(new_dir_path)
        self.assertTrue(ensure_result.is_success())
        self.assertTrue(new_dir_path.exists())
        
        # Test list_files
        list_result = list_files(self.source_dir)
        self.assertTrue(list_result.is_success())
        self.assertEqual(len(list_result.unwrap()), 1)
        
        # Test move_file
        dest_file = self.dest_dir / "moved.txt"
        move_result = move_file(self.test_file, dest_file)
        self.assertTrue(move_result.is_success())
        self.assertTrue(dest_file.exists())
        self.assertFalse(self.test_file.exists())
        
        # Create a new test file for the remaining tests
        new_test_file = self.source_dir / "test2.txt"
        with open(new_test_file, "w") as f:
            f.write("Test content 2")
        
        # Test copy_file
        copy_dest = self.dest_dir / "copied.txt"
        copy_result = copy_file(new_test_file, copy_dest)
        self.assertTrue(copy_result.is_success())
        self.assertTrue(copy_dest.exists())
        self.assertTrue(new_test_file.exists())
        
        # Test rename_file
        renamed_file = self.source_dir / "renamed.txt"
        rename_result = rename_file(new_test_file, renamed_file)
        self.assertTrue(rename_result.is_success())
        self.assertTrue(renamed_file.exists())
        self.assertFalse(new_test_file.exists())
        
        # Create a subdirectory with files for archive testing
        subdir = self.source_dir / "subdir"
        subdir.mkdir()
        for i in range(3):
            with open(subdir / f"file{i}.txt", "w") as f:
                f.write(f"Content {i}")
        
        # Test archive_directory
        archive_path = self.dest_dir / "archive.zip"
        archive_result = archive_directory(subdir, self.dest_dir)
        self.assertTrue(archive_result.is_success())
        self.assertTrue(archive_path.exists())
        
        # Test extract_archive
        extract_dir = self.dest_dir / "extracted"
        extract_result = extract_archive(archive_path, extract_dir)
        self.assertTrue(extract_result.is_success())
        self.assertTrue(extract_dir.exists())
        self.assertTrue((extract_dir / "file0.txt").exists())
        
        # Test delete_file
        delete_result = delete_file(copy_dest)
        self.assertTrue(delete_result.is_success())
        self.assertFalse(copy_dest.exists())
        
        # Test delete_directory
        delete_dir_result = delete_directory(subdir)
        self.assertTrue(delete_dir_result.is_success())
        self.assertFalse(subdir.exists())
    
    def test_result_processor(self):
        """Test the ResultFileProcessor class."""
        # Create a processor
        processor = ResultFileProcessor(dry_run=False)
        
        # Create a test file
        test_file2 = self.source_dir / "processor_test.txt"
        with open(test_file2, "w") as f:
            f.write("Processor test content")
        
        # Test move_file
        dest_file = self.dest_dir / "moved_by_processor.txt"
        move_result = processor.move_file(test_file2, dest_file)
        self.assertTrue(move_result.is_success())
        self.assertTrue(dest_file.exists())
        self.assertFalse(test_file2.exists())
        
        # Create another test file
        test_file3 = self.source_dir / "processor_test2.txt"
        with open(test_file3, "w") as f:
            f.write("Processor test content 2")
        
        # Test copy_file
        copy_dest = self.dest_dir / "copied_by_processor.txt"
        copy_result = processor.copy_file(test_file3, copy_dest)
        self.assertTrue(copy_result.is_success())
        self.assertTrue(copy_dest.exists())
        
        # Test rename_file
        renamed_file = self.source_dir / "renamed_by_processor.txt"
        rename_result = processor.rename_file(test_file3, renamed_file)
        self.assertTrue(rename_result.is_success())
        self.assertTrue(renamed_file.exists())
        
        # Create a subdirectory with files for bulk operations
        bulk_dir = self.source_dir / "bulk"
        bulk_dir.mkdir()
        for i in range(5):
            with open(bulk_dir / f"bulk_file{i}.txt", "w") as f:
                f.write(f"Bulk content {i}")
        
        # Test bulk_copy
        bulk_dest = self.dest_dir / "bulk_dest"
        bulk_dest.mkdir()
        bulk_copy_result = processor.bulk_copy(bulk_dir, bulk_dest)
        self.assertTrue(bulk_copy_result.is_success())
        self.assertEqual(len(bulk_copy_result.unwrap()), 5)
        
        # Test move_and_rename
        move_rename_result = processor.move_and_rename(
            renamed_file,
            self.dest_dir,
            "moved_and_renamed.txt"
        )
        self.assertTrue(move_rename_result.is_success())
        self.assertTrue((self.dest_dir / "moved_and_renamed.txt").exists())
        
        # Test handle_failure
        # First with a success result
        success_path = processor.handle_failure(move_result)
        self.assertEqual(success_path, dest_file)
        
        # Then with a failure result
        error = OperationError(ErrorType.FILE_NOT_FOUND, "File not found", "/nonexistent")
        failure_result = Result.failure(error)
        default_path = Path(self.dest_dir)
        handled_path = processor.handle_failure(failure_result, default_path)
        self.assertEqual(handled_path, default_path)


if __name__ == "__main__":
    unittest.main()