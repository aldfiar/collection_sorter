import unittest
import tempfile
import shutil
from pathlib import Path
import zipfile
import warnings

# DEPRECATED TEST FILE
# This test file is for a deprecated module and should be rewritten to use the template-based implementation.
warnings.warn(
    "test_archive.py uses the deprecated ArchivedCollection class. "
    "Use ArchiveDirectoryTemplate from collection_sorter.common.templates instead.",
    DeprecationWarning,
    stacklevel=2
)

# Import using a try-except to prevent errors
try:
    from collection_sorter.common.archive import ArchivedCollection
except ImportError:
    from collection_sorter.common.templates import ArchiveDirectoryTemplate

class TestArchivedCollection(unittest.TestCase):
    def setUp(self):
        # Create a temporary directory
        self.test_dir = Path(tempfile.mkdtemp())
        
        # Create test file structure
        self.file1 = self.test_dir / "file1.txt"
        self.file2 = self.test_dir / "file2.txt"
        self.subdir = self.test_dir / "subdir"
        self.subfile = self.subdir / "subfile.txt"
        
        # Create the files and directories
        self.file1.write_text("test content 1")
        self.file2.write_text("test content 2")
        self.subdir.mkdir()
        self.subfile.write_text("test content 3")
        
        # Initialize ArchivedCollection
        self.collection = ArchivedCollection(self.test_dir)

    def tearDown(self):
        # Clean up the temporary directory
        shutil.rmtree(self.test_dir)

    def test_is_archive(self):
        """Test checking if path is an archive"""
        # Create a test zip file
        test_zip = self.test_dir / "test.zip"
        with zipfile.ZipFile(test_zip, 'w') as zf:
            zf.write(self.file1, self.file1.name)
        
        archive = ArchivedCollection(test_zip)
        self.assertTrue(archive.is_archive())
        
        non_archive = ArchivedCollection(self.file1)
        self.assertFalse(non_archive.is_archive())

    def test_archive_directory(self):
        """Test archiving a directory"""
        # Archive the subdirectory
        subdir_collection = ArchivedCollection(self.subdir)
        archived = subdir_collection.archive_directory()
        
        # Check that archive was created
        expected_archive = self.subdir.parent / f"{self.subdir.name}.zip"
        self.assertTrue(expected_archive.exists())
        
        # Verify archive contents
        with zipfile.ZipFile(expected_archive) as zf:
            self.assertEqual(len(zf.namelist()), 1)
            self.assertIn(self.subfile.name, zf.namelist()[0])

    def test_archive_directory_with_new_name(self):
        """Test archiving a directory with a custom name"""
        new_name = "custom_archive"
        subdir_collection = ArchivedCollection(self.subdir)
        archived = subdir_collection.archive_directory(new_name=new_name)
        
        expected_archive = self.subdir.parent / f"{new_name}.zip"
        self.assertTrue(expected_archive.exists())

    def test_archive_directory_with_destination(self):
        """Test archiving a directory to a specific destination"""
        dest_dir = self.test_dir / "destination"
        dest_dir.mkdir()
        
        subdir_collection = ArchivedCollection(self.subdir)
        archived = subdir_collection.archive_directory(destination=dest_dir)
        
        expected_archive = dest_dir / f"{self.subdir.name}.zip"
        self.assertTrue(expected_archive.exists())

    def test_archive_folders(self):
        """Test archiving multiple folders"""
        # Create additional test folders
        folder1 = self.test_dir / "folder1"
        folder2 = self.test_dir / "folder2"
        folder1.mkdir()
        folder2.mkdir()
        (folder1 / "test1.txt").write_text("test")
        (folder2 / "test2.txt").write_text("test")
        
        # Archive all folders
        self.collection.archive_folders()
        
        # Check that archives were created
        self.assertTrue((self.test_dir / "folder1.zip").exists())
        self.assertTrue((self.test_dir / "folder2.zip").exists())
        self.assertTrue((self.test_dir / "subdir.zip").exists())

    def test_exists(self):
        """Test exists method for archives"""
        # Create a test zip file
        test_zip = self.test_dir / "test.zip"
        with zipfile.ZipFile(test_zip, 'w') as zf:
            zf.write(self.file1, self.file1.name)
        
        archive = ArchivedCollection(test_zip)
        self.assertTrue(archive.exists())
        
        # Create an empty zip file
        empty_zip = self.test_dir / "empty.zip"
        empty_zip.touch()
        empty_archive = ArchivedCollection(empty_zip)
        self.assertFalse(empty_archive.exists())

if __name__ == '__main__':
    unittest.main()
