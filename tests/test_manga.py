import tempfile
from pathlib import Path
from unittest import TestCase

from collection_sorter.manga import MangaParser

mangas = [
    "(C90) [ASGO (Zanzi)] GRANCHANGE FANTASY (Granblue Fantasy)",
    "(C94) [squeezecandyheaven (Ichihaya)] Imouto to Sex Suru nante Kimochi Warui Having Sex With Your Little Sister That's Gross! [English] [sneikkimies]",
    "[MonsieuR (MUK)] Tiny Evil 3 [English] {Hennojin} [Decensored] [Digital]",
    "[Shoujo Kishidan (Oyari Ashito)] Uchi no Meishimai ga Yuuwaku Shite Kuru"
]
names = [
    "GRANCHANGE FANTASY",
    "Imouto to Sex Suru nante Kimochi Warui Having Sex With Your Little Sister That's Gross!",
    "Tiny Evil 3",
    "Uchi no Meishimai ga Yuuwaku Shite Kuru"
]
authors = [
    "Zanzi",
    "Ichihaya",
    "MUK",
    "Oyari Ashito"
]
groups = [
    "ASGO",
    "squeezecandyheaven",
    "MonsieuR",
    "Shoujo Kishidan"
]

class TestManga(TestCase):

    def setUp(self) -> None:
        self.parser = MangaParser

    def test_name_with_lower(self):
        manga = "[Gentsuki (Gentsuki)] Kimi Omou Koi - I think of you"
        info = self.parser.parse(manga)
        self.assertEqual('Gentsuki', info['author'])
        self.assertEqual('Gentsuki', info['group'])
        self.assertEqual('Kimi Omou Koi - I think of you', info['name'])
        self.assertFalse(info['tags'])

    def test_without_author(self):
        manga = "Towako 4 [English] {CapableScoutMan & bigk40k} [Digital]"
        info = self.parser.parse(manga)
        self.assertEqual('Towako', info['author'])
        self.assertEqual('Towako 4', info['name'])
        self.assertIn('English', info['tags'])

    def test_bracket_position(self):
        manga = 'Towako 2 (Complete) [English] {CapableScoutMan & B E C Scans & S T A L K E R & bigk40k}'
        info = self.parser.parse(manga)
        self.assertEqual('Towako', info['author'])
        self.assertEqual('Towako 2', info['name'])
        self.assertIn('English', info['tags'])

    def test_parser(self):
        counter = 0
        for manga in mangas:
            info = self.parser.parse(manga)
            self.assertEqual(authors[counter], info['author'])
            self.assertEqual(names[counter], info['name'])
            self.assertIn(groups[counter], info['group'])
            counter += 1
