import tempfile
from pathlib import Path
from unittest import TestCase

from collection_sorter.manga import MangaExtractor

mangas = ["(C90) [ASGO (Zanzi)] GRANCHANGE FANTASY (Granblue Fantasy)",
          "(C94) [squeezecandyheaven (Ichihaya)] Imouto to Sex Suru nante Kimochi Warui Having Sex With Your Little Sister That's Gross! [English] [sneikkimies]",
          "[MonsieuR (MUK)] Tiny Evil 3 [English] {Hennojin} [Decensored] [Digital]",
          "[Shoujo Kishidan (Oyari Ashito)] Uchi no Meishimai ga Yuuwaku Shite Kuru"]
names = ["GRANCHANGE FANTASY",
         "Tiny Evil 3",
         "Imouto to Sex Suru nante Kimochi Warui Having Sex With Your Little Sister That's Gross!",
         "Uchi no Meishimai ga Yuuwaku Shite Kuru"]
names_with_tags = ["GRANCHANGE FANTASY [Granblue Fantasy]",
                   "Imouto to Sex Suru nante Kimochi Warui Having Sex With Your Little Sister That's Gross! [English] [sneikkimies]",
                   "Tiny Evil 3 [English] [Hennojin] [Decensored] [Digital]",
                   "Uchi no Meishimai ga Yuuwaku Shite Kuru"]
authors_full = ["ASGO (Zanzi)", "squeezecandyheaven (Ichihaya)", "MonsieuR (MUK)", "Shoujo Kishidan (Oyari Ashito)"]
authors = ["Zanzi", "Ichihaya", "MUK", "Oyari Ashito"]
groups = ["ASGO", "squeezecandyheaven", "MonsieuR", "Shoujo Kishidan"]


class TestManga(TestCase):

    def setUp(self) -> None:
        self.extractor = MangaExtractor()

    def test_name_with_lower(self):
        manga = "[Gentsuki_(Gentsuki)]_Kimi_Omou_Koi_-_I_think_of_you"
        p = Path(manga)
        info = self.extractor.extract(p)
        self.assertEqual("Kimi Omou Koi - I think of you", info["name"])
        self.assertEqual("Gentsuki", info["author"])

    def test_extract_name_without_tags(self):
        for manga in mangas:
            name = self.extractor.extract_name(manga, keep_tags=False)
            self.assertIn(name, names)

    def test_extract_name_with_tags(self):
        for manga in mangas:
            name = self.extractor.extract_name(manga)
            self.assertIn(name, names_with_tags)

    def test_extract_author_info(self):
        for manga in mangas:
            info = self.extractor.extract_author_info(manga)
            self.assertIn(info, authors_full)

    def test_extract_group(self):
        for manga in mangas:
            group = self.extractor.extract_group(manga)
            self.assertIn(group, groups)

    def test_extract_author(self):
        for manga in mangas:
            author = self.extractor.extract_author(manga)
            self.assertIn(author, authors)

    def test_folder_which_contains_subfolders(self):
        source = Path(tempfile.TemporaryDirectory().name)
        source.mkdir()
        subfile = tempfile.TemporaryDirectory(dir=str(source.absolute()))
        d = self.extractor.extract(source)
        self.assertEqual(source.name, d["author"])

    def test_folder_which_contains_files(self):
        source = Path(tempfile.TemporaryDirectory().name)
        source.mkdir()
        stf = tempfile.TemporaryFile(dir=str(source.absolute()))
        d = self.extractor.extract(source)
        self.assertEqual(source.name, d["name"])

