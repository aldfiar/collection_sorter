import unittest
from tempfile import TemporaryDirectory
from pathlib import Path
from collection_sorter.common.files import CollectionPath

class TestCollectionPath(unittest.TestCase):
    def setUp(self):
        self.temp_dir = TemporaryDirectory()
        self.collection_path = CollectionPath(self.temp_dir.name)

    def tearDown(self):
        self.temp_dir.cleanup()

    def test_empty_directory(self):
        paths = self.collection_path.collect_all()
        self.assertEqual(len(paths), 0)

    def test_directory_with_file(self):
        file_path = Path(self.temp_dir.name) / 'test.txt'
        file_path.write_text('Hello, world!')
        
        paths = self.collection_path.collect_all()
        self.assertEqual(len(paths), 1)
        self.assertIn(file_path, paths)

    def test_directory_with_empty_subdirectories(self):
        sub_dir = Path(self.temp_dir.name) / 'subdir'
        sub_dir.mkdir()

        paths = self.collection_path.collect_all()
        self.assertEqual(len(paths), 0)

    def test_directory_with_subdirectories_with_files(self):
        subdir1 = Path(self.temp_dir.name) / 'subdir1'
        subdir2 = Path(self.temp_dir.name) / 'subdir2'
        
        subdir1.mkdir()
        subdir2.mkdir()

        file1_path = subdir1 / 'test1.txt'
        file1_path.write_text('Hello, world!')

        file2_path = subdir2 / 'test2.txt'
        file2_path.write_text('Goodbye, world!')

        paths = self.collection_path.collect_all()
        self.assertEqual(len(paths), 2)
        self.assertIn(file1_path, paths)
        self.assertIn(file2_path, paths)

if __name__ == '__main__':
    unittest.main()
