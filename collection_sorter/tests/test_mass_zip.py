import os
import shutil
import tempfile
from pathlib import Path
import unittest
import warnings

# DEPRECATED TEST FILE
# This test file is testing code that was using the deprecated ArchivedCollection class.
warnings.warn(
    "test_mass_zip.py tests code that used the deprecated ArchivedCollection class. "
    "The actual implementation now uses ArchiveDirectoryTemplate from collection_sorter.common.templates.",
    DeprecationWarning,
    stacklevel=2
)

from collection_sorter.common.templates import ArchiveDirectoryTemplate
from collection_sorter.mass_zip import ZipCollections, zip_collections, parse_args


class TestMassZip(unittest.TestCase):
    def setUp(self):
        # Create a temporary directory
        self.test_dir = tempfile.mkdtemp()
        self.source_dir = Path(self.test_dir) / "source"
        self.dest_dir = Path(self.test_dir) / "destination"
        
        # Create test directory structure
        self.source_dir.mkdir()
        self.dest_dir.mkdir()
        
        # Create some test files
        (self.source_dir / "test1.txt").write_text("test1")
        (self.source_dir / "subdir").mkdir()
        (self.source_dir / "subdir" / "test2.txt").write_text("test2")

    def tearDown(self):
        # Clean up the temporary directory
        shutil.rmtree(self.test_dir)

    def test_parse_args(self):
        args = parse_args(["source1", "source2", "-d", "dest", "-a", "-m"])
        self.assertEqual(args.sources, ["source1", "source2"])
        self.assertEqual(args.destination, "dest")
        self.assertTrue(args.archive)
        self.assertTrue(args.move)

    def test_zip_collections_basic(self):
        zip_collections(
            sources=[str(self.source_dir)],
            destination=str(self.dest_dir)
        )
        # Check if zip file was created and is valid
        zip_files = list(self.dest_dir.glob("*.zip"))
        self.assertEqual(len(zip_files), 1)
        self.assertTrue(zip_files[0].stat().st_size > 0)
        
        # Verify it's a valid archive
        collection = ArchivedCollection(zip_files[0])
        self.assertTrue(collection.is_archive())

    def test_zip_collections_with_move(self):
        zip_collections(
            sources=[str(self.source_dir)],
            destination=str(self.dest_dir),
            move=True
        )
        # Check if source files were removed
        self.assertFalse((self.source_dir / "test1.txt").exists())
        
    def test_nonexistent_source(self):
        with self.assertRaises(FileNotFoundError):
            task = ZipCollections()
            task.execute(Path("nonexistent"))

if __name__ == '__main__':
    unittest.main()
