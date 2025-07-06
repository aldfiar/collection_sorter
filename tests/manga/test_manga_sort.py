import shutil
import tempfile
import warnings
from pathlib import Path
from unittest import TestCase

# DEPRECATED TEST FILE
# This test file is testing a legacy module that has been replaced.
warnings.warn(
    "test_manga_sort.py uses the deprecated manga_sort function. "
    "Use the MangaProcessorTemplate from collection_sorter.templates.processors.manga "
    "or MangaCommandHandler from collection_sorter.cli_handlers.manga_handler instead. "
    "See test_manga_processor.py for the new tests.",
    DeprecationWarning,
    stacklevel=2
)

# Import the new implementation to use for compatibility
from collection_sorter.cli_handlers.manga_handler import MangaCommandHandlerTemplateMethod

# Define manga_sort function to provide backward compatibility
def manga_sort(source=None, destination=None, archive=False, move=False, author_folders=False):
    """Backward compatibility function that uses MangaCommandHandlerTemplateMethod.
    
    This function maintains compatibility with old tests by wrapping the new implementation.
    """
    # Create and execute handler
    handler = MangaCommandHandlerTemplateMethod(
        sources=source,
        destination=destination,
        archive=archive,
        move=move,
        dry_run=False,
        interactive=False,
        verbose=False,
        author_folders=author_folders
    )
    
    # Execute the handler
    result = handler.handle()
    
    # Return the result data for tests to use
    if result.is_success():
        return result.unwrap()
    else:
        # Use error() instead of unwrap_error() which doesn't exist in the new Result pattern API
        raise RuntimeError(f"Failed to process manga: {result.error()}")

# Test manga data with English fantasy/nature themed names
TEST_MANGAS = [
    "(C90) [Moonweaver Studio (Starlight)] Mystic Forest Symphony",
    "(C94) [Dreamforge (Silverleaf)] Ethereal Wings & Stardust [English] {Moonshadow}",
    "[Frostfire Works (Nightwhisper)] Crystal Gardens Saga 3 [English] {Dawnseeker} [Restored] [Digital]",
    "[Sunspire Workshop (Riverwind)] Dancing with Aurora Lights"
]

class TestMangaSort(TestCase):
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
        """Test basic manga sorting without archiving"""
        manga_sort(
            source=[str(self.source_dir)],
            destination=str(self.dest_dir),
            archive=False,
            move=False
        )

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
        """Test manga sorting with move option"""
        manga_sort(
            source=[str(self.source_dir)],
            destination=str(self.dest_dir),
            archive=False,
            move=True
        )

        # Check if files were moved (source should be empty)
        self.assertFalse((self.source_dir / TEST_MANGAS[0]).exists())
        
        # Check if files exist in destination
        self.assertTrue((self.dest_dir / "Starlight" / "Mystic Forest Symphony").exists())

    def test_manga_sort_with_archive(self):
        """Test manga sorting with archive option"""
        manga_sort(
            source=[str(self.source_dir)],
            destination=str(self.dest_dir),
            archive=True,
            move=False
        )

        # Check if zip files were created
        self.assertTrue(list(Path(self.dest_dir / "Starlight").glob("*.zip")))
        self.assertTrue(list(Path(self.dest_dir / "Nightwhisper").glob("*.zip")))

    def test_manga_sort_with_archive_and_move(self):
        """Test manga sorting with both archive and move options"""
        manga_sort(
            source=[str(self.source_dir)],
            destination=str(self.dest_dir),
            archive=True,
            move=True
        )

        # Check if source files were removed
        self.assertFalse((self.source_dir / TEST_MANGAS[0]).exists())
        
        # Check if zip files were created
        self.assertTrue(list(Path(self.dest_dir / "Starlight").glob("*.zip")))

    def test_author_folders(self):
        """Test processing of author folders containing multiple manga"""
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

        manga_sort(
            source=[str(author_dir)],
            destination=str(self.dest_dir),
            archive=False,
            move=False,
            author_folders=True
        )

        # Check if author directory was created in destination
        author_dest = self.dest_dir / author_name
        self.assertTrue(author_dest.exists())
        self.assertTrue(author_dest.is_dir())

        # Check if manga directories were properly sorted within author directory
        self.assertTrue((author_dest / "Mystic Forest Symphony").exists())
        self.assertTrue((author_dest / "Ethereal Wings & Stardust").exists())

    def test_author_folders_with_archive(self):
        """Test author folders processing with archive option"""
        author_name = "Test Author"
        author_dir = self.source_dir / author_name
        author_dir.mkdir()

        # Create test manga directory with proper structure
        manga_name = "(C90) [Moonweaver Studio (Starlight)] Mystic Forest Symphony"
        manga_dir = author_dir / manga_name
        manga_dir.mkdir(parents=True)
        (manga_dir / "page1.jpg").touch()

        manga_sort(
            source=[str(author_dir)],
            destination=str(self.dest_dir),
            archive=True,
            move=False,
            author_folders=True
        )

        # Check if zip files were created in author directory
        author_dest = self.dest_dir / author_name
        self.assertTrue(list(Path(author_dest).glob("*.zip")))
