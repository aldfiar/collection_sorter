import tempfile
from pathlib import Path
from random import random
from unittest import TestCase

from collection_sorter.common.move import MovableCollection


def reverse(st):
    return '0' if st == '1' else '0'


class TestMover(TestCase):

    def setUp(self) -> None:
        self.source_temp = tempfile.TemporaryDirectory()
        self.source = Path(self.source_temp.name)
        self.destination_temp = tempfile.TemporaryDirectory()
        self.destination = Path(self.destination_temp.name)
        self.files = []





    def test_move_file_to_dest(self):
        stf = tempfile.TemporaryFile(dir=str(self.source.absolute()))
        self.files.append(stf)
        ftm = Path(stf.name)
        collection = MovableCollection(self.source)
        collection.move(self.destination)
        expected = self.destination.joinpath(ftm.name)
        self.assertTrue(expected.exists())


    def test_copy_file_to_dest(self):
        stf = tempfile.TemporaryFile(dir=str(self.source.absolute()))
        ftm = Path(stf.name)
        collection = MovableCollection(self.source)
        collection.copy(self.destination)
        expected = self.destination.joinpath(ftm.name)
        self.assertTrue(expected.exists())
        self.assertTrue(ftm.exists())

    def tearDown(self) -> None:
        self.source_temp.cleanup()
        self.destination_temp.cleanup()
        for file in self.files:
            file.close()


