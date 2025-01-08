import tempfile
from pathlib import Path
from unittest import TestCase
import shutil

from collection_sorter.manga_sort import manga_sort

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
        self.assertTrue((self.dest_dir / "Zanzi" / "GRANCHANGE FANTASY").exists())

    def test_manga_sort_with_archive(self):
        """Test manga sorting with archive option"""
        manga_sort(
            source=[str(self.source_dir)],
            destination=str(self.dest_dir),
            archive=True,
            move=False
        )

        # Check if zip files were created
        self.assertTrue(list(Path(self.dest_dir / "Zanzi").glob("*.zip")))
        self.assertTrue(list(Path(self.dest_dir / "MUK").glob("*.zip")))

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
        self.assertTrue(list(Path(self.dest_dir / "Zanzi").glob("*.zip")))

    def test_author_folders(self):
        """Test processing of author folders containing multiple manga"""
        # Create author folder structure
        author_name = "Test Author"
        author_dir = self.source_dir / author_name
        author_dir.mkdir()

        # Create multiple manga folders inside author directory
        for manga_name in TEST_MANGAS[:2]:  # Use first two test mangas
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
        self.assertTrue((author_dest / "GRANCHANGE FANTASY").exists())
        self.assertTrue((author_dest / "Having Sex With Your Little Sister That's Gross!").exists())

    def test_author_folders_with_archive(self):
        """Test author folders processing with archive option"""
        author_name = "Test Author"
        author_dir = self.source_dir / author_name
        author_dir.mkdir()

        # Create test manga directory
        manga_dir = author_dir / TEST_MANGAS[0]
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
