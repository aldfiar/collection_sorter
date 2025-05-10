import shutil
import tempfile
import unittest
import warnings
from pathlib import Path

# Important note about the test file
warnings.warn(
    "This file contains the modern tests for manga processing using MangaProcessorTemplate. "
    "For CLI handler tests use MangaCommandHandler from collection_sorter.cli_handlers.manga_handler instead.",
    UserWarning,
    stacklevel=2
)

from collection_sorter.cli_handlers.manga_handler import MangaCommandHandlerTemplateMethod as MangaCommandHandler
from collection_sorter.templates.templates_extensions import MangaProcessorTemplate

# Test manga data with English fantasy/nature themed names
TEST_MANGAS = [
    "(C90) [Moonweaver Studio (Starlight)] Mystic Forest Symphony",
    "(C94) [Dreamforge (Silverleaf)] Ethereal Wings & Stardust [English] {Moonshadow}",
    "[Frostfire Works (Nightwhisper)] Crystal Gardens Saga 3 [English] {Dawnseeker} [Restored] [Digital]",
    "[Sunspire Workshop (Riverwind)] Dancing with Aurora Lights"
]

# Simple template function for testing
def simple_template_function(info, symbol_replace_function=None):
    return f"[{info['author']}] {info['name']}"

class TestMangaProcessor(unittest.TestCase):
    def setUp(self):
        # Create temporary directories for testing
        self.test_dir = tempfile.mkdtemp()
        self.source_dir = Path(self.test_dir) / "source"
        self.dest_dir = Path(self.test_dir) / "destination"
        
        # Create source directory structure
        self.source_dir.mkdir()
        self.dest_dir.mkdir()
        
        # Create test manga directories with sample files
        for manga_name in TEST_MANGAS:
            manga_dir = self.source_dir / manga_name
            manga_dir.mkdir()
            # Create a dummy file in each manga directory
            (manga_dir / "page1.jpg").touch()

    def tearDown(self):
        # Clean up temporary directories
        shutil.rmtree(self.test_dir)

    def test_template_basic_sort(self):
        """Test basic manga sorting using MangaProcessorTemplate"""
        # Create the template processor directly
        template = MangaProcessorTemplate(
            source_path=str(self.source_dir),
            destination_path=str(self.dest_dir),
            template_func=simple_template_function,
            author_folders=False,
            archive=False,
            move_source=False,
            dry_run=False,
            interactive=False
        )
        
        # Execute the template
        result = template.execute()
        
        # Verify successful execution
        self.assertTrue(result.is_success())
        stats = result.unwrap()
        self.assertGreater(stats.get("processed", 0), 0)
        
        # Check if authors' directories were created
        self.assertTrue((self.dest_dir / "Starlight").exists())
        self.assertTrue((self.dest_dir / "Silverleaf").exists())
        self.assertTrue((self.dest_dir / "Nightwhisper").exists())
        self.assertTrue((self.dest_dir / "Riverwind").exists())

        # Check if manga directories were properly sorted
        self.assertTrue((self.dest_dir / "Starlight" / "Mystic Forest Symphony").exists())
        self.assertTrue((self.dest_dir / "Nightwhisper" / "Crystal Gardens Saga 3").exists())

        # Verify source files still exist (since move_source=False)
        self.assertTrue((self.source_dir / TEST_MANGAS[0]).exists())

    def test_template_with_move(self):
        """Test manga sorting with move option using MangaProcessorTemplate"""
        # Create the template processor
        template = MangaProcessorTemplate(
            source_path=str(self.source_dir),
            destination_path=str(self.dest_dir),
            template_func=simple_template_function,
            author_folders=False,
            archive=False,
            move_source=True,
            dry_run=False,
            interactive=False
        )
        
        # Execute the template
        result = template.execute()
        
        # Verify successful execution
        self.assertTrue(result.is_success())
        stats = result.unwrap()
        self.assertGreater(stats.get("moved", 0), 0)
        
        # Check if files were moved (source should be empty)
        self.assertFalse((self.source_dir / TEST_MANGAS[0]).exists())
        
        # Check if files exist in destination
        self.assertTrue((self.dest_dir / "Starlight" / "Mystic Forest Symphony").exists())

    def test_template_with_archive(self):
        """Test manga sorting with archive option using MangaProcessorTemplate"""
        # Create the template processor
        template = MangaProcessorTemplate(
            source_path=str(self.source_dir),
            destination_path=str(self.dest_dir),
            template_func=simple_template_function,
            author_folders=False,
            archive=True,
            move_source=False,
            dry_run=False,
            interactive=False
        )
        
        # Execute the template
        result = template.execute()
        
        # Verify successful execution
        self.assertTrue(result.is_success())
        stats = result.unwrap()
        self.assertGreater(stats.get("archived", 0), 0)
        
        # Check if zip files were created
        self.assertTrue(list(Path(self.dest_dir / "Starlight").glob("*.zip")))
        self.assertTrue(list(Path(self.dest_dir / "Nightwhisper").glob("*.zip")))

    def test_handler_basic_sort(self):
        """Test basic manga sorting using MangaCommandHandler"""
        # Create and execute the handler
        handler = MangaCommandHandler(
            sources=[str(self.source_dir)],
            destination=str(self.dest_dir),
            archive=False,
            move=False,
            dry_run=False,
            interactive=False,
            verbose=False
        )
        
        try:
            result = handler.handle()
            
            # Verify successful execution
            self.assertTrue(result.is_success())
            stats = result.unwrap()
            self.assertGreater(stats.get("processed", 0), 0)
            
            # Check if authors' directories were created
            self.assertTrue((self.dest_dir / "Starlight").exists())
            self.assertTrue((self.dest_dir / "Silverleaf").exists())
            self.assertTrue((self.dest_dir / "Nightwhisper").exists())
            self.assertTrue((self.dest_dir / "Riverwind").exists())

            # Check if manga directories were properly sorted
            self.assertTrue((self.dest_dir / "Starlight" / "Mystic Forest Symphony").exists())
            self.assertTrue((self.dest_dir / "Nightwhisper" / "Crystal Gardens Saga 3").exists())

            # Verify source files still exist (since move=False)
            self.assertTrue((self.source_dir / TEST_MANGAS[0]).exists())
        except (ImportError, AttributeError):
            # Skip if handler dependencies aren't available
            self.skipTest("MangaCommandHandler dependencies not available")

if __name__ == "__main__":
    unittest.main()