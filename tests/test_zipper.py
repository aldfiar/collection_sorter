import tempfile
from pathlib import Path
from unittest import TestCase

from collection_sorter.common.archive import ArchivedCollection


class TestZipper(TestCase):

    def setUp(self) -> None:
        self.source = Path(tempfile.TemporaryDirectory().name)
        self.source.mkdir()
        for i in range(10):
            stf = tempfile.TemporaryFile(dir=str(self.source.absolute()))
        self.destination = Path(tempfile.TemporaryDirectory().name)
        self.destination.mkdir()

    def test_archive_folder(self):
        collection = ArchivedCollection(self.source)
        collection.archive_folders(zip_parent=True)
        self.assertTrue(collection.path.is_file())
