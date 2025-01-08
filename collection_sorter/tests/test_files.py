import unittest
import tempfile
import shutil
from pathlib import Path

from collection_sorter.common.files import CollectionPath

class TestCollectionPath(unittest.TestCase):
    def setUp(self):
        # Create a temporary directory
        self.test_dir = Path(tempfile.mkdtemp()).resolve()
        
        # Create test file structure
        self.file1 = (self.test_dir / "file1.txt").resolve()
        self.file2 = (self.test_dir / "file2.txt").resolve()
        self.subdir = (self.test_dir / "subdir").resolve()
        self.subfile = (self.subdir / "subfile.txt").resolve()
        
        # Create the files and directories
        self.file1.touch()
        self.file2.touch()
        self.subdir.mkdir()
        self.subfile.touch()
        
        # Initialize CollectionPath
        self.collection = CollectionPath(self.test_dir)

    def tearDown(self):
        # Clean up the temporary directory
        shutil.rmtree(self.test_dir)

    def test_path_property(self):
        """Test that path property returns correct Path object"""
        self.assertEqual(self.collection.path, self.test_dir)

    def test_get_files(self):
        """Test getting files from the collection"""
        files = set(self.collection.get_files())
        expected = {self.file1, self.file2}
        self.assertEqual(files, expected)

    def test_get_folders(self):
        """Test getting folders from the collection"""
        folders = set(self.collection.get_folders())
        expected = {self.subdir}
        self.assertEqual(folders, expected)

    def test_collect_all(self):
        """Test collecting all files recursively"""
        all_files = self.collection.collect_all()
        expected = {self.file1, self.file2, self.subfile}
        self.assertEqual(all_files, expected)

    def test_exists(self):
        """Test exists property"""
        self.assertTrue(self.collection.exists)
        non_existent = CollectionPath(self.test_dir / "nonexistent")
        self.assertFalse(non_existent.exists)

    def test_map(self):
        """Test mapping function to files"""
        processed_files = set()
        
        def collect_files(filepath: str):
            processed_files.add(Path(filepath))
            
        self.collection.map(collect_files)
        expected = {self.file1, self.file2}
        self.assertEqual(processed_files, expected)

    def test_delete(self):
        """Test deleting the collection"""
        subpath = CollectionPath(self.subdir)
        subpath.delete()
        self.assertFalse(self.subdir.exists())

if __name__ == '__main__':
    unittest.main()
