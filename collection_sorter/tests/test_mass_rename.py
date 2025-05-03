import os
import tempfile
import warnings
from pathlib import Path
from unittest import TestCase

# DEPRECATED TEST FILE
# This test file is testing a legacy module that has been replaced.
warnings.warn(
    "test_mass_rename.py uses the deprecated mass_rename module. "
    "Use the RenameProcessorTemplate from collection_sorter.common.templates_extensions "
    "or RenameCommandHandler from collection_sorter.cli_handlers.rename_handler instead. "
    "See test_rename_processor.py for the new tests.",
    DeprecationWarning,
    stacklevel=2
)

# Mock the dependencies that have been removed
class SortExecutor:
    def __init__(self):
        pass
        
    def execute(self, task, sources):
        pass

class TestMassRename(TestCase):
    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
        self.test_files = [
            "Mystic_Vale_Chronicles_01_[1280-720][Frostweaver_eng_raw][66C845C4].mkv",
            "Starlight_Wanderer_01_[F2A5991E].mkv",
            "Crystal_Dreams_01.ass",
            "Moonweaver Tales Episode 1.mp4",
            "[Dawnseeker-Subs] Ethereal Whispers 01 [DVDRip 720x480 x264 AC3].mkv",
            "Aurora Symphony - 01 [720p-HEVC-WEBRip][69A3098A].mkv"
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
            "Mystic_Vale_Chronicles_01.mkv",
            "Starlight_Wanderer_01.mkv",
            "Crystal_Dreams_01.ass",
            "Moonweaver Tales Episode 1.mp4",
            "Ethereal Whispers 01.mkv",
            "Aurora Symphony - 01.mkv"
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
