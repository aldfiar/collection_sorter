import tempfile
from pathlib import Path
from unittest import TestCase

from collection_sorter.common.move import MovableCollection


class TestMover(TestCase):

    def setUp(self) -> None:
        self.source_temp = tempfile.TemporaryDirectory()
        self.source = Path(self.source_temp.name)
        self.destination_temp = tempfile.TemporaryDirectory()
        self.destination = Path(self.destination_temp.name)

    def tearDown(self) -> None:
        self.source_temp.cleanup()
        self.destination_temp.cleanup()

    def test_move_file_to_dest(self):
        source_file = self.source / 'testfile.txt'
        source_file.write_text('Hello, World!')
        collection = MovableCollection(self.source)
        collection.move(self.destination)
        expected_path = self.destination / 'testfile.txt'
        self.assertTrue(expected_path.exists())
        self.assertFalse(source_file.exists())

    def test_copy_file_to_dest(self):
        source_file = self.source / 'testfile.txt'
        source_file.write_text('Hello, World!')
        collection = MovableCollection(self.source)
        collection.copy(self.destination)
        expected_path = self.destination / 'testfile.txt'
        self.assertTrue(expected_path.exists())
        self.assertTrue(source_file.exists())

    def test_move_directory_to_dest(self):
        subdirectory = self.source / 'subdir'
        subdirectory.mkdir()
        (subdirectory / 'testfile.txt').write_text('Hello, World!')
        collection = MovableCollection(self.source)
        collection.move(self.destination)
        expected_path = self.destination / 'subdir' / 'testfile.txt'
        self.assertTrue(expected_path.exists())
        self.assertFalse(subdirectory.exists())

    def test_copy_directory_to_dest(self):
        subdirectory = self.source / 'subdir'
        subdirectory.mkdir()
        (subdirectory / 'testfile.txt').write_text('Hello, World!')
        collection = MovableCollection(self.source)
        collection.copy(self.destination)
        expected_path = self.destination / 'subdir' / 'testfile.txt'
        self.assertTrue(expected_path.exists())
        self.assertTrue(subdirectory.exists())
