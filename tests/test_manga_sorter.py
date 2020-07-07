from pathlib import Path
from unittest import TestCase

from collection_sorter.manga_sorter import MangaSorter
from collection_sorter.templates import base_manga_template


class TestMangaSorter(TestCase):
    def test_sort(self):
        path = Path("G:\Test")
        destination = Path("G:\Filtered")
        sorter = MangaSorter()
        sorter.sort(path, destination, template_function=base_manga_template, zip_files=False)
