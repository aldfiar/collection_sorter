from pathlib import Path
from unittest import TestCase

from collection_sorter import SortExecutor, MangaSorter
from collection_sorter.manga.manga_template import manga_template_function


class TestMangaSorter(TestCase):
    def test_sort(self):
        path = Path("G:\Test")
        destination = Path("G:\Filtered")
        sorter = SortExecutor()
        task = MangaSorter(archive=False)
        sorter.sort(path, destination, task=task)
