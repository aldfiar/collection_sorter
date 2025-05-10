# Sample Validation Tests

This document provides examples of tests for the new validation framework in the processors package. These examples should guide the implementation of comprehensive validation tests.

## Basic Validation Test Structure

```python
import unittest
from pathlib import Path
import tempfile
import os

from collection_sorter.templates.processors import (
    BaseFileProcessor,
    RenameProcessorTemplate,
    MangaProcessorTemplate,
    VideoProcessorTemplate
)
from collection_sorter.result import ErrorType

class TestProcessorValidation(unittest.TestCase):
    
    def setUp(self):
        # Create temp directories for testing
        self.temp_dir = tempfile.TemporaryDirectory()
        self.source_dir = Path(self.temp_dir.name) / "source"
        self.dest_dir = Path(self.temp_dir.name) / "dest"
        self.source_dir.mkdir()
        
        # Create some test files
        (self.source_dir / "test_file.txt").touch()
        manga_dir = self.source_dir / "[Author] Manga Title"
        manga_dir.mkdir()
        (manga_dir / "page1.jpg").touch()
        
        video_dir = self.source_dir / "videos"
        video_dir.mkdir()
        (video_dir / "Show S01E01.mp4").touch()
        (video_dir / "Show S01E01.srt").touch()
    
    def tearDown(self):
        self.temp_dir.cleanup()
        
    # Common validation tests
    
    def test_nonexistent_source_validation(self):
        """Test validation for nonexistent source path."""
        non_existent = Path(self.temp_dir.name) / "does_not_exist"
        result = RenameProcessorTemplate(
            source_path=non_existent,
            destination_path=self.dest_dir
        ).execute()
        
        self.assertTrue(result.is_failure())
        errors = result.error()
        self.assertEqual(len(errors), 1)
        self.assertEqual(errors[0].type, ErrorType.VALIDATION_ERROR)
        self.assertIn("does not exist", errors[0].message)
        
    # Rename processor tests
    
    def test_rename_invalid_pattern(self):
        """Test validation for invalid regex pattern."""
        # Pattern with unclosed parenthesis
        patterns = {"([0-9]+": "number-$1"}
        
        # Validation should catch this at initialization
        processor = RenameProcessorTemplate(
            source_path=self.source_dir,
            destination_path=self.dest_dir,
            patterns=patterns
        )
        
        result = processor.execute()
        self.assertTrue(result.is_failure())
        errors = result.error()
        self.assertIn("Invalid regex pattern", errors[0].message)
    
    # Manga processor tests
    
    def test_manga_non_directory_source(self):
        """Test validation for manga processor with a file as source (should be directory)."""
        file_path = self.source_dir / "test_file.txt"
        processor = MangaProcessorTemplate(
            source_path=file_path,
            destination_path=self.dest_dir
        )
        
        result = processor.execute()
        self.assertTrue(result.is_failure())
        errors = result.error()
        self.assertIn("must be a directory", errors[0].message)
    
    # Video processor tests
    
    def test_video_invalid_extensions(self):
        """Test validation for invalid video extensions."""
        processor = VideoProcessorTemplate(
            source_path=self.source_dir / "videos",
            destination_path=self.dest_dir,
            video_extensions=[123, 456]  # Invalid - should be strings
        )
        
        result = processor.execute()
        self.assertTrue(result.is_failure())
        errors = result.error()
        self.assertIn("Invalid video extensions", errors[0].message)
```

## Additional Test Cases to Implement

### Base Validator Tests
- Test all common validators (PathValidator, ExtensionsValidator)
- Test the ValidationResult class

### Rename Processor Tests
- Test validation for different pattern types
- Test recursive flag validation
- Test pattern compilation

### Manga Processor Tests
- Test author_folders validation
- Test template function validation
- Test validation with missing destination

### Video Processor Tests
- Test subtitle extensions validation
- Test single video file processing
- Test mixed file types validation

## Integration with Existing Tests

Existing tests should be updated to use the new validation-aware processors. Key points to consider:

1. Mock inputs that would fail validation during tests
2. Test dry-run mode with validation
3. Verify the stats returned from processors include validation errors
4. Test validation behavior when duplicate_handler is provided

## Edge Cases to Test

1. Empty directories
2. Very long paths (platform-dependent)
3. Files with special characters
4. Unicode in filenames and paths
5. Files with no extensions
6. Files with multiple extensions (e.g., `.tar.gz`)
7. Validation with interactive mode enabled