"""Tests for manga processor with validation."""

import unittest
from pathlib import Path
import tempfile
import os
import shutil
from unittest.mock import MagicMock, patch

from collection_sorter.files import FilePath
from collection_sorter.files.duplicates import DuplicateHandler, DuplicateStrategy
from collection_sorter.templates.processors import (
    MangaTemplateValidator,
    MangaProcessorValidator,
    MangaProcessorTemplate
)
from collection_sorter.result import ErrorType, OperationError


# Simple template function for testing
def simple_template_function(info, symbol_replace_function=None):
    return f"[{info['author']}] {info['name']}"


class TestMangaTemplateValidator(unittest.TestCase):
    """Tests for the MangaTemplateValidator class."""
    
    def setUp(self):
        self.validator = MangaTemplateValidator()
    
    def test_valid_template_function(self):
        """Test validation of a valid template function."""
        result = self.validator.validate(simple_template_function)
        
        self.assertTrue(result.is_valid)
        self.assertEqual(result.value, simple_template_function)
    
    def test_none_template(self):
        """Test validation of None template."""
        result = self.validator.validate(None)
        
        self.assertTrue(result.is_valid)
        self.assertIsNone(result.value)
    
    def test_non_callable_template(self):
        """Test validation of a non-callable template."""
        result = self.validator.validate("not a function")
        
        self.assertFalse(result.is_valid)
        self.assertIn("must be a callable function", result.errors[0])


class TestMangaProcessorValidator(unittest.TestCase):
    """Tests for the MangaProcessorValidator class."""
    
    def setUp(self):
        # Create temporary directories for testing
        self.temp_dir = tempfile.TemporaryDirectory()
        self.test_dir = Path(self.temp_dir.name)
        self.source_dir = self.test_dir / "source"
        self.source_dir.mkdir()
        self.dest_dir = self.test_dir / "destination"
        
        # Create test manga directories
        self.manga_dir = self.source_dir / "[Author] Manga Title"
        self.manga_dir.mkdir()
        (self.manga_dir / "page1.jpg").touch()
        
        # Create a file to test invalid source
        self.test_file = self.source_dir / "test_file.txt"
        self.test_file.touch()
        
        # Create a validator
        self.validator = MangaProcessorValidator()
    
    def tearDown(self):
        self.temp_dir.cleanup()
    
    def test_validate_valid_parameters(self):
        """Test validation of valid parameters."""
        result = self.validator.validate_parameters(
            source_path=self.source_dir,
            destination_path=self.dest_dir,
            template_func=simple_template_function,
            author_folders=True,
            archive=False,
            move_source=False
        )
        
        self.assertTrue(result.is_success())
        validated = result.unwrap()
        self.assertEqual(validated["template_func"], simple_template_function)
        self.assertTrue(validated["author_folders"])
        self.assertFalse(validated["archive"])
        self.assertFalse(validated["move_source"])
    
    def test_validate_invalid_template_func(self):
        """Test validation with an invalid template function."""
        result = self.validator.validate_parameters(
            source_path=self.source_dir,
            destination_path=self.dest_dir,
            template_func="not a function"
        )
        
        self.assertTrue(result.is_failure())
        errors = result.error()
        self.assertEqual(len(errors), 1)
        self.assertEqual(errors[0].type, ErrorType.VALIDATION_ERROR)
        self.assertIn("Invalid template function", errors[0].message)
    
    def test_validate_source_not_directory(self):
        """Test validation when source is not a directory."""
        result = self.validator.validate_parameters(
            source_path=self.test_file,
            destination_path=self.dest_dir,
            template_func=simple_template_function
        )
        
        self.assertTrue(result.is_failure())
        errors = result.error()
        self.assertEqual(len(errors), 1)
        self.assertEqual(errors[0].type, ErrorType.VALIDATION_ERROR)
        self.assertIn("must be a directory", errors[0].message)
    
    def test_validate_cannot_create_destination(self):
        """Test validation when destination cannot be created."""
        with patch('pathlib.Path.mkdir') as mock_mkdir:
            mock_mkdir.side_effect = PermissionError("Permission denied")
            
            result = self.validator.validate_parameters(
                source_path=self.source_dir,
                destination_path=self.test_dir / "cannot_create",
                template_func=simple_template_function,
                dry_run=False
            )
            
            self.assertTrue(result.is_failure())
            errors = result.error()
            self.assertEqual(len(errors), 1)
            self.assertEqual(errors[0].type, ErrorType.VALIDATION_ERROR)
            self.assertIn("Cannot create destination directory", errors[0].message)
    
    def test_validate_dry_run_skips_destination_creation(self):
        """Test validation in dry run mode skips destination creation."""
        result = self.validator.validate_parameters(
            source_path=self.source_dir,
            destination_path=self.test_dir / "does_not_need_creation",
            template_func=simple_template_function,
            dry_run=True
        )
        
        self.assertTrue(result.is_success())
        validated = result.unwrap()
        self.assertTrue(validated["dry_run"])
        self.assertFalse((self.test_dir / "does_not_need_creation").exists())


class TestMangaProcessorTemplate(unittest.TestCase):
    """Tests for the MangaProcessorTemplate class."""
    
    def setUp(self):
        # Create temporary directories for testing
        self.temp_dir = tempfile.TemporaryDirectory()
        self.test_dir = Path(self.temp_dir.name)
        self.source_dir = self.test_dir / "source"
        self.source_dir.mkdir()
        self.dest_dir = self.test_dir / "destination"
        
        # Create test manga directories and files
        self.manga_dirs = []
        for manga_name in [
            "[StarAuthor] Space Manga",
            "[EarthAuthor] Earth Manga",
            "(C88) [GroupName (MoonAuthor)] Moon Manga"
        ]:
            manga_dir = self.source_dir / manga_name
            manga_dir.mkdir()
            (manga_dir / "page1.jpg").touch()
            (manga_dir / "page2.jpg").touch()
            self.manga_dirs.append(manga_dir)
        
        # Create a file to test invalid source
        self.test_file = self.source_dir / "test_file.txt"
        self.test_file.touch()
    
    def tearDown(self):
        self.temp_dir.cleanup()
    
    def test_init_with_valid_parameters(self):
        """Test initialization with valid parameters."""
        processor = MangaProcessorTemplate(
            source_path=self.source_dir,
            destination_path=self.dest_dir,
            template_func=simple_template_function,
            author_folders=True
        )
        
        self.assertFalse(hasattr(processor, 'validation_errors') or processor.validation_errors)
        self.assertEqual(processor.template_func, simple_template_function)
        self.assertTrue(processor.author_folders)
    
    def test_init_with_invalid_template_func(self):
        """Test initialization with an invalid template function."""
        processor = MangaProcessorTemplate(
            source_path=self.source_dir,
            destination_path=self.dest_dir,
            template_func="not a function"
        )
        
        self.assertTrue(hasattr(processor, 'validation_errors'))
        self.assertTrue(processor.validation_errors)
        self.assertEqual(processor.validation_errors[0].type, ErrorType.VALIDATION_ERROR)
        self.assertIn("Invalid template function", processor.validation_errors[0].message)
    
    def test_init_with_source_not_directory(self):
        """Test initialization when source is not a directory."""
        processor = MangaProcessorTemplate(
            source_path=self.test_file,
            destination_path=self.dest_dir,
            template_func=simple_template_function
        )
        
        self.assertTrue(hasattr(processor, 'validation_errors'))
        self.assertTrue(processor.validation_errors)
        self.assertEqual(processor.validation_errors[0].type, ErrorType.VALIDATION_ERROR)
        self.assertIn("must be a directory", processor.validation_errors[0].message)
    
    def test_execute_with_validation_errors(self):
        """Test execute method with validation errors."""
        # Using a mock class to avoid real validation
        class MockProcessor(MangaProcessorTemplate):
            def __init__(self):
                self.validation_errors = [
                    OperationError(
                        type=ErrorType.VALIDATION_ERROR,
                        message="Source path must be a directory",
                        path="test"
                    )
                ]
                self.source_path = None
                self.destination_path = None
                self.template_func = None

        processor = MockProcessor()
        result = processor.execute()
        self.assertTrue(result.is_failure())
        errors = result.error()
        self.assertEqual(len(errors), 1)
        self.assertEqual(errors[0].type, ErrorType.VALIDATION_ERROR)
    
    def test_dry_run(self):
        """Test execute method in dry_run mode."""
        processor = MangaProcessorTemplate(
            source_path=self.source_dir,
            destination_path=self.dest_dir,
            template_func=simple_template_function,
            dry_run=True
        )
        
        result = processor.execute()
        self.assertTrue(result.is_success())
        stats = result.unwrap()
        
        # Mangas should be processed but not actually moved
        self.assertGreater(stats["processed"], 0)
        self.assertFalse((self.dest_dir / "StarAuthor").exists())
    
    def test_missing_destination(self):
        """Test execute method with missing destination."""
        with patch('collection_sorter.templates.processors.manga.MangaProcessorValidator._validate_destination') as mock_validate:
            mock_validate.return_value.is_valid = False
            mock_validate.return_value.errors = ["Destination validation failed"]
            
            processor = MangaProcessorTemplate(
                source_path=self.source_dir,
                destination_path=None,  # Missing destination
                template_func=simple_template_function
            )
            
            result = processor.execute()
            self.assertTrue(result.is_failure())
            errors = result.error()
            self.assertEqual(len(errors), 1)
            self.assertEqual(errors[0].type, ErrorType.VALIDATION_ERROR)
    
    def test_with_author_folders(self):
        """Test execute method with author_folders=True."""
        # Run in non-dry-run mode to actually create files
        processor = MangaProcessorTemplate(
            source_path=self.source_dir,
            destination_path=self.dest_dir,
            template_func=simple_template_function,
            author_folders=True
        )
        
        result = processor.execute()
        self.assertTrue(result.is_success())
        stats = result.unwrap()
        
        # Author folders should be created
        self.assertGreater(stats["processed"], 0)
        self.assertTrue((self.dest_dir / "StarAuthor").exists())
        self.assertTrue((self.dest_dir / "EarthAuthor").exists())
        self.assertTrue((self.dest_dir / "MoonAuthor").exists())
        
        # Manga folders should be inside author folders
        self.assertTrue((self.dest_dir / "StarAuthor" / "Space Manga").exists())
        self.assertTrue((self.dest_dir / "EarthAuthor" / "Earth Manga").exists())
        self.assertTrue((self.dest_dir / "MoonAuthor" / "Moon Manga").exists())
    
    def test_without_author_folders(self):
        """Test execute method with author_folders=False."""
        processor = MangaProcessorTemplate(
            source_path=self.source_dir,
            destination_path=self.dest_dir,
            template_func=simple_template_function,
            author_folders=False
        )
        
        result = processor.execute()
        self.assertTrue(result.is_success())
        stats = result.unwrap()
        
        # Manga folders should be created directly in destination
        self.assertGreater(stats["processed"], 0)
        self.assertTrue((self.dest_dir / "Space Manga").exists())
        self.assertTrue((self.dest_dir / "Earth Manga").exists())
        self.assertTrue((self.dest_dir / "Moon Manga").exists())
    
    def test_with_archive(self):
        """Test execute method with archive=True."""
        processor = MangaProcessorTemplate(
            source_path=self.source_dir,
            destination_path=self.dest_dir,
            template_func=simple_template_function,
            archive=True
        )
        
        result = processor.execute()
        self.assertTrue(result.is_success())
        stats = result.unwrap()
        
        # Archives should be created
        self.assertGreater(stats["archived"], 0)
        self.assertTrue(list(Path(self.dest_dir).glob("**/*.zip")))
    
    def test_with_move_source(self):
        """Test execute method with move_source=True."""
        processor = MangaProcessorTemplate(
            source_path=self.source_dir,
            destination_path=self.dest_dir,
            template_func=simple_template_function,
            move_source=True
        )
        
        result = processor.execute()
        self.assertTrue(result.is_success())
        stats = result.unwrap()
        
        # Source directories should be moved
        self.assertGreater(stats["moved"], 0)
        for manga_dir in self.manga_dirs:
            self.assertFalse(manga_dir.exists())
    
    def test_edge_case_unicode_manga_names(self):
        """Test processing manga with unicode characters in names."""
        # Create manga with unicode characters
        unicode_manga = self.source_dir / "[ÜniçödeAuthor] Mångå Tïtłę"
        unicode_manga.mkdir()
        (unicode_manga / "page1.jpg").touch()
        
        processor = MangaProcessorTemplate(
            source_path=self.source_dir,
            destination_path=self.dest_dir,
            template_func=simple_template_function,
            author_folders=True
        )
        
        result = processor.execute()
        self.assertTrue(result.is_success())
        
        # Unicode author folder and manga name should be preserved
        self.assertTrue((self.dest_dir / "ÜniçödeAuthor").exists())
        self.assertTrue((self.dest_dir / "ÜniçödeAuthor" / "Mångå Tïtłę").exists())


if __name__ == "__main__":
    unittest.main()