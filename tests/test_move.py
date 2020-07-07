import tempfile
from pathlib import Path
from unittest import TestCase

from collection_sorter.move import Mover


class TestMover(TestCase):

    def setUp(self) -> None:
        self.source = Path(tempfile.TemporaryDirectory().name)
        self.source.mkdir()
        self.destination = Path(tempfile.TemporaryDirectory().name)
        self.destination.mkdir()

    def test_move_file_to_dest(self):
        stf = tempfile.TemporaryFile(dir=str(self.source.absolute()))
        ftm = Path(stf.name)
        Mover.move(ftm, self.destination)
        expected = self.destination.joinpath(ftm.name)
        self.assertTrue(expected.exists())

