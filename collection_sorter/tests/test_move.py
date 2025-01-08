import unittest
import tempfile
import shutil
from pathlib import Path

from collection_sorter.common.move import MovableCollection

class TestMovableCollection(unittest.TestCase):
    def setUp(self):
        # Create a temporary directory
        self.test_dir = Path(tempfile.mkdtemp())
        self.dest_dir = Path(tempfile.mkdtemp())
        
        # Create test file structure
        self.file1 = self.test_dir / "file1.txt"
        self.file2 = self.test_dir / "file2.txt"
        self.subdir = self.test_dir / "subdir"
        
        # Create the files and directories
        self.file1.write_text("test content 1")
        self.file2.write_text("test content 2")
        self.subdir.mkdir()
        
        # Initialize MovableCollection
        self.collection = MovableCollection(self.test_dir)

    def tearDown(self):
        # Clean up the temporary directories
        shutil.rmtree(self.test_dir)
        shutil.rmtree(self.dest_dir)

    def test_copy_files(self):
        """Test copying files to a new location"""
        # Copy files to destination
        new_collection = self.collection.copy(self.dest_dir)
        
        # Check that files were copied
        self.assertTrue((self.dest_dir / "file1.txt").exists())
        self.assertTrue((self.dest_dir / "file2.txt").exists())
        
        # Check that original files still exist
        self.assertTrue(self.file1.exists())
        self.assertTrue(self.file2.exists())
        
        # Verify file contents
        self.assertEqual((self.dest_dir / "file1.txt").read_text(), "test content 1")
        self.assertEqual((self.dest_dir / "file2.txt").read_text(), "test content 2")

    def test_move_files(self):
        """Test moving files to a new location"""
        # Move files to destination
        new_collection = self.collection.move(self.dest_dir)
        
        # Check that files were moved to new location
        self.assertTrue((self.dest_dir / "file1.txt").exists())
        self.assertTrue((self.dest_dir / "file2.txt").exists())
        
        # Check that original files no longer exist
        self.assertFalse(self.file1.exists())
        self.assertFalse(self.file2.exists())
        
        # Verify file contents in new location
        self.assertEqual((self.dest_dir / "file1.txt").read_text(), "test content 1")
        self.assertEqual((self.dest_dir / "file2.txt").read_text(), "test content 2")

    def test_copy_to_nonexistent_directory(self):
        """Test copying files to a directory that doesn't exist yet"""
        new_dir = self.dest_dir / "new_subdir"
        self.assertFalse(new_dir.exists())
        
        # Copy should create the directory
        new_collection = self.collection.copy(new_dir)
        
        # Check that directory was created and files were copied
        self.assertTrue(new_dir.exists())
        self.assertTrue((new_dir / "file1.txt").exists())
        self.assertTrue((new_dir / "file2.txt").exists())

    def test_move_to_nonexistent_directory(self):
        """Test moving files to a directory that doesn't exist yet"""
        new_dir = self.dest_dir / "new_subdir"
        self.assertFalse(new_dir.exists())
        
        # Move should create the directory
        new_collection = self.collection.move(new_dir)
        
        # Check that directory was created and files were moved
        self.assertTrue(new_dir.exists())
        self.assertTrue((new_dir / "file1.txt").exists())
        self.assertTrue((new_dir / "file2.txt").exists())
        self.assertFalse(self.file1.exists())
        self.assertFalse(self.file2.exists())

if __name__ == '__main__':
    unittest.main()
