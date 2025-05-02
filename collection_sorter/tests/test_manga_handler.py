import tempfile
import unittest
from pathlib import Path
import shutil
import sys
from unittest.mock import patch, MagicMock

# Mock the services module to prevent the error with Factory registration
sys.modules['collection_sorter.common.services'] = MagicMock()

# Import after mocking services
from collection_sorter.cli_handlers.manga_handler import MangaCommandHandler
from collection_sorter.common.paths import FilePath
from collection_sorter.manga.manga_template import manga_template_function

# Test manga data with English fantasy/nature themed names
TEST_MANGAS = [
    "(C90) [Moonweaver Studio (Starlight)] Mystic Forest Symphony",
    "(C94) [Dreamforge (Silverleaf)] Ethereal Wings & Stardust [English] {Moonshadow}",
    "[Frostfire Works (Nightwhisper)] Crystal Gardens Saga 3 [English] {Dawnseeker} [Restored] [Digital]",
    "[Sunspire Workshop (Riverwind)] Dancing with Aurora Lights"
]

class TestMangaCommandHandler(unittest.TestCase):
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

    def test_basic_manga_sort(self):
        """Test basic manga sorting without archiving using MangaCommandHandler"""
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
        
        result = handler.handle()
        
        # Verify successful execution
        self.assertTrue(result.is_success())
        stats = result.unwrap()
        self.assertGreater(stats["processed"], 0)
        
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

    def test_manga_sort_with_move(self):
        """Test manga sorting with move option using MangaCommandHandler"""
        # Create and execute the handler
        handler = MangaCommandHandler(
            sources=[str(self.source_dir)],
            destination=str(self.dest_dir),
            archive=False,
            move=True,
            dry_run=False,
            interactive=False,
            verbose=False
        )
        
        result = handler.handle()
        
        # Verify successful execution
        self.assertTrue(result.is_success())
        stats = result.unwrap()
        self.assertGreater(stats["moved"], 0)
        
        # Check if files were moved (source should be empty)
        self.assertFalse((self.source_dir / TEST_MANGAS[0]).exists())
        
        # Check if files exist in destination
        self.assertTrue((self.dest_dir / "Starlight" / "Mystic Forest Symphony").exists())

    def test_manga_sort_with_archive(self):
        """Test manga sorting with archive option using MangaCommandHandler"""
        # Create and execute the handler
        handler = MangaCommandHandler(
            sources=[str(self.source_dir)],
            destination=str(self.dest_dir),
            archive=True,
            move=False,
            dry_run=False,
            interactive=False,
            verbose=False
        )
        
        result = handler.handle()
        
        # Verify successful execution
        self.assertTrue(result.is_success())
        stats = result.unwrap()
        self.assertGreater(stats["archived"], 0)
        
        # Check if zip files were created
        self.assertTrue(list(Path(self.dest_dir / "Starlight").glob("*.zip")))
        self.assertTrue(list(Path(self.dest_dir / "Nightwhisper").glob("*.zip")))

    def test_manga_sort_with_archive_and_move(self):
        """Test manga sorting with both archive and move options using MangaCommandHandler"""
        # Create and execute the handler
        handler = MangaCommandHandler(
            sources=[str(self.source_dir)],
            destination=str(self.dest_dir),
            archive=True,
            move=True,
            dry_run=False,
            interactive=False,
            verbose=False
        )
        
        result = handler.handle()
        
        # Verify successful execution
        self.assertTrue(result.is_success())
        stats = result.unwrap()
        self.assertGreater(stats["archived"], 0)
        self.assertGreater(stats["moved"], 0)
        
        # Check if source files were removed
        self.assertFalse((self.source_dir / TEST_MANGAS[0]).exists())
        
        # Check if zip files were created
        self.assertTrue(list(Path(self.dest_dir / "Starlight").glob("*.zip")))

    def test_author_folders(self):
        """Test processing of author folders containing multiple manga using MangaCommandHandler"""
        # Create author folder structure
        author_name = "Test Author"
        author_dir = self.source_dir / author_name
        author_dir.mkdir()

        # Create manga folders with proper author structure
        manga1 = "(C90) [Moonweaver Studio (Starlight)] Mystic Forest Symphony"
        manga2 = "(C94) [Dreamforge (Silverleaf)] Ethereal Wings & Stardust"
        
        for manga_name in [manga1, manga2]:
            manga_dir = author_dir / manga_name
            manga_dir.mkdir(parents=True)
            (manga_dir / "page1.jpg").touch()

        # Create and execute the handler
        handler = MangaCommandHandler(
            sources=[str(author_dir)],
            destination=str(self.dest_dir),
            archive=False,
            move=False,
            dry_run=False,
            interactive=False,
            verbose=False,
            author_folders=True
        )
        
        result = handler.handle()
        
        # Verify successful execution
        self.assertTrue(result.is_success())
        
        # Check if author directory was created in destination
        author_dest = self.dest_dir / author_name
        self.assertTrue(author_dest.exists())
        self.assertTrue(author_dest.is_dir())

        # Check if manga directories were properly sorted within author directory
        self.assertTrue((author_dest / "Mystic Forest Symphony").exists())
        self.assertTrue((author_dest / "Ethereal Wings & Stardust").exists())

    def test_author_folders_with_archive(self):
        """Test author folders processing with archive option using MangaCommandHandler"""
        author_name = "Test Author"
        author_dir = self.source_dir / author_name
        author_dir.mkdir()

        # Create test manga directory with proper structure
        manga_name = "(C90) [Moonweaver Studio (Starlight)] Mystic Forest Symphony"
        manga_dir = author_dir / manga_name
        manga_dir.mkdir(parents=True)
        (manga_dir / "page1.jpg").touch()

        # Create and execute the handler
        handler = MangaCommandHandler(
            sources=[str(author_dir)],
            destination=str(self.dest_dir),
            archive=True,
            move=False,
            dry_run=False,
            interactive=False,
            verbose=False,
            author_folders=True
        )
        
        result = handler.handle()
        
        # Verify successful execution
        self.assertTrue(result.is_success())
        stats = result.unwrap()
        self.assertGreater(stats["archived"], 0)
        
        # Check if zip files were created in author directory
        author_dest = self.dest_dir / author_name
        self.assertTrue(list(Path(author_dest).glob("*.zip")))

    def test_dry_run_mode(self):
        """Test manga sorting in dry run mode using MangaCommandHandler"""
        # Create and execute the handler in dry run mode
        handler = MangaCommandHandler(
            sources=[str(self.source_dir)],
            destination=str(self.dest_dir),
            archive=True,
            move=True,
            dry_run=True,
            interactive=False,
            verbose=False
        )
        
        result = handler.handle()
        
        # Verify successful execution
        self.assertTrue(result.is_success())
        
        # In dry run mode, nothing should be created in destination
        self.assertFalse(list(self.dest_dir.glob("*")))
        
        # Source files should still exist
        self.assertTrue((self.source_dir / TEST_MANGAS[0]).exists())

    def test_invalid_source(self):
        """Test handling of non-existent source directory using MangaCommandHandler"""
        # Create a handler with a non-existent source
        invalid_source = str(self.test_dir / "nonexistent")
        handler = MangaCommandHandler(
            sources=[invalid_source],
            destination=str(self.dest_dir),
            archive=False,
            move=False,
            dry_run=False,
            interactive=False,
            verbose=False
        )
        
        result = handler.handle()
        
        # Should fail with validation error
        self.assertTrue(result.is_failure())
        errors = result.unwrap_error()
        self.assertTrue(any("does not exist" in str(err) for err in errors))

if __name__ == "__main__":
    unittest.main()