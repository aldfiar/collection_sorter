from pathlib import Path
from unittest import TestCase

from collection_sorter.zipper import Zipper


class TestZipper(TestCase):
    def test_zip_folder(self):
        p = Path("G:\Test\(C90) [ASGO (Zanzi)] GRANCHANGE FANTASY (Granblue Fantasy)")
        Zipper.zip_directory(p)

    def test_zip_folder_overide(self):
        p = Path("G:\Test\(C90) [ASGO (Zanzi)] GRANCHANGE FANTASY (Granblue Fantasy)")
        Zipper.zip_directory(p, override_name="[Zanzi]GRANCHANGE FANTASY")
