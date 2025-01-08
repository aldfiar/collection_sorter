import os
import tempfile
from pathlib import Path
from unittest import TestCase

from collection_sorter.mass_rename import FileNameCleaner, FileRenameTask
from collection_sorter.common.sorter import BaseCollection, SortExecutor

class TestMassRename(TestCase):
    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
        self.test_files = [
            "Ane_chijo_max_heart_01_[1280-720][Galan_rus_raw][66C845C4].mkv",
            "Baka_na_Imouto_o_Rikou_ni_Suru_no_wa_Ore_no_XX_Dake_na_Ken_ni_Tsuite_01_[F2A5991E].mkv",
            "Ane Chijo Max Heart_01.ass",
            "Bible Black Gaiden OVA 1.mp4",
            "[Beatrice-Raws] Shoujo Ramune 01 [DVDRip 720x480 x264 AC3].mkv",
            "Ecchi na Onee-chan ni Shiboraretai - 01 [720p-HEVC-WEBRip][69A3098A].mkv"
        ]
        
        # Create test files
        for filename in self.test_files:
            Path(self.temp_dir, filename).touch()

    def tearDown(self):
        # Clean up temp directory
        for file in Path(self.temp_dir).iterdir():
            file.unlink()
        os.rmdir(self.temp_dir)

    def test_clean_name(self):
        cleaner = FileNameCleaner()
        test_cases = [
            (
                "Ane_chijo_max_heart_01_[1280-720][Galan_rus_raw][66C845C4].mkv",
                "Ane_chijo_max_heart_01.mkv"
            ),
            (
                "Bible Black Gaiden OVA 1.mp4",
                "Bible Black Gaiden OVA 1.mp4"
            ),
            (
                "[Beatrice-Raws] Shoujo Ramune 01 [DVDRip 720x480 x264 AC3].mkv",
                "Shoujo Ramune 01.mkv"
            )
        ]

        for input_name, expected in test_cases:
            result = cleaner.clean_name(input_name)
            self.assertEqual(result, expected)

    def test_rename_task(self):
        # Set up and execute rename task
        task = FileRenameTask()
        sorter = SortExecutor()
        collection = BaseCollection(self.temp_dir)
        sorter.sort(collection=collection, task=task)

        # Check results
        renamed_files = set(f.name for f in Path(self.temp_dir).iterdir())
        expected_files = {
            "Ane_chijo_max_heart_01.mkv",
            "Baka_na_Imouto_o_Rikou_ni_Suru_no_wa_Ore_no_XX_Dake_na_Ken_ni_Tsuite_01.mkv",
            "Ane Chijo Max Heart_01.ass",
            "Bible Black Gaiden OVA 1.mp4",
            "Shoujo Ramune 01.mkv",
            "Ecchi na Onee - chan ni Shiboraretai - 01.mkv"
        }

        self.assertEqual(renamed_files, expected_files)

    def test_unique_names(self):
        # Create duplicate scenario
        duplicate_name = "duplicate_test_[123].mkv"
        clean_name = "duplicate_test.mkv"
        
        Path(self.temp_dir, duplicate_name).touch()
        Path(self.temp_dir, clean_name).touch()

        task = FileRenameTask()
        sorter = SortExecutor()
        collection = BaseCollection(self.temp_dir)
        sorter.sort(collection=collection, task=task)

        # Verify duplicate handling
        files = list(Path(self.temp_dir).glob("duplicate_test*.mkv"))
        self.assertEqual(len(files), 2)
        self.assertTrue(any(f.name.startswith("duplicate_test_duplicate_") for f in files))
