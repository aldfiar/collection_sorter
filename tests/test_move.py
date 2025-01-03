import tempfile
from pathlib import Path
from random import random
from unittest import TestCase

from collection_sorter.common.move import MovableCollection


def reverse(st):
    return '0' if st == '1' else '0'

def flipTwo(some, i):
    some[i] = reverse(some[i])
    next_symbol = i + 1
    some[next_symbol] = reverse((some[next_symbol]))

def getMinimumOperations(binaryStr):
    maxConverts = 0
    for i in range(0, len(binaryStr))

class TestMover(TestCase):

    # def setUp(self) -> None:
    #     self.source_temp = tempfile.TemporaryDirectory()
    #     self.source = Path(self.source_temp.name)
    #     self.destination_temp = tempfile.TemporaryDirectory()
    #     self.destination = Path(self.destination_temp.name)
    #     self.files = []



    def test_flip(self):
        string = "1011"
        f

    def test_some(self):
        b = [[2, 3], [5, 7]]
        after = [[2, 5], [7, 17]]

        for i in range(len(after) - 1, 0, -1):
            temp = after[i]
            for j in range(0, len(after[i])):
                print(after[i][j])

    #
    # def test_move_file_to_dest(self):
    #     stf = tempfile.TemporaryFile(dir=str(self.source.absolute()))
    #     self.files.append(stf)
    #     ftm = Path(stf.name)
    #     collection = MovableCollection(self.source)
    #     collection.move(self.destination)
    #     expected = self.destination.joinpath(ftm.name)
    #     self.assertTrue(expected.exists())
    #
    #
    # def test_copy_file_to_dest(self):
    #     stf = tempfile.TemporaryFile(dir=str(self.source.absolute()))
    #     ftm = Path(stf.name)
    #     collection = MovableCollection(self.source)
    #     collection.copy(self.destination)
    #     expected = self.destination.joinpath(ftm.name)
    #     self.assertTrue(expected.exists())
    #     self.assertTrue(ftm.exists())
    #
    # def tearDown(self) -> None:
    #     self.source_temp.cleanup()
    #     self.destination_temp.cleanup()
    #     for file in self.files:
    #         file.close()
    #
    #
