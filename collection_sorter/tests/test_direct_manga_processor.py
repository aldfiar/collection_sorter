import tempfile
import unittest
from pathlib import Path
import shutil
import os
import sys

# Directly import the template class to bypass service registration
sys.path.append(str(Path(__file__).parents[2]))
from collection_sorter.common.templates_extensions import MangaProcessorTemplate

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

class TestDirectMangaProcessor(unittest.TestCase):
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
        """Test basic manga sorting without archiving using MangaProcessorTemplate directly"""
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

    def test_manga_sort_with_move(self):
        """Test manga sorting with move option using MangaProcessorTemplate directly"""
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

    def test_manga_sort_with_archive(self):
        """Test manga sorting with archive option using MangaProcessorTemplate directly"""
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

    def test_dry_run_mode(self):
        """Test manga sorting in dry run mode using MangaProcessorTemplate directly"""
        # Create the template processor
        template = MangaProcessorTemplate(
            source_path=str(self.source_dir),
            destination_path=str(self.dest_dir),
            template_func=simple_template_function,
            author_folders=False,
            archive=True,
            move_source=True,
            dry_run=True,
            interactive=False
        )
        
        # Execute the template
        result = template.execute()
        
        # Verify successful execution
        self.assertTrue(result.is_success())
        
        # In dry run mode, nothing should be created in destination
        self.assertEqual(len(os.listdir(self.dest_dir)), 0)
        
        # Source files should still exist
        self.assertTrue((self.source_dir / TEST_MANGAS[0]).exists())

if __name__ == "__main__":
    unittest.main()