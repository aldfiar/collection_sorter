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
            "Sunset_valley_dreams_01_[1280-720][Summer_eng_raw][66C845C4].mkv",
            "Moonlight_whispers_through_autumn_leaves_01_[F2A5991E].mkv",
            "Sunset Valley Dreams_01.ass",
            "Crystal Garden Episode 1.mp4",
            "[Stardust-Subs] Dancing Fireflies 01 [DVDRip 720x480 x264 AC3].mkv",
            "Midnight Symphony Orchestra - 01 [720p-HEVC-WEBRip][69A3098A].mkv"
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
                "Sunset_valley_dreams_01_[1280-720][Summer_eng_raw][66C845C4].mkv",
                "Sunset_valley_dreams_01.mkv"
            ),
            (
                "Crystal Garden Episode 1.mp4",
                "Crystal Garden Episode 1.mp4"
            ),
            (
                "[Stardust-Subs] Dancing Fireflies 01 [DVDRip 720x480 x264 AC3].mkv",
                "Dancing Fireflies 01.mkv"
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
            "Sunset_valley_dreams_01.mkv",
            "Moonlight_whispers_through_autumn_leaves_01.mkv",
            "Sunset Valley Dreams_01.ass",
            "Crystal Garden Episode 1.mp4",
            "Dancing Fireflies 01.mkv",
            "Midnight Symphony Orchestra - 01.mkv"
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
