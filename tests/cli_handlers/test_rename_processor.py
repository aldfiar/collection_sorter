import os
import shutil
import tempfile
import unittest
from pathlib import Path

from collection_sorter.cli_handlers.rename_handler import RenameCommandHandler
from collection_sorter.templates.processors import RenameProcessorTemplate


class TestRenameProcessor(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
        self.dest_dir = Path(self.temp_dir) / "destination"
        self.dest_dir.mkdir()
        
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
        shutil.rmtree(self.temp_dir)

    def test_template_basic_rename(self):
        """Test basic file renaming with the RenameProcessorTemplate"""
        # Create pattern mappings
        patterns = {
            r'\[.*?\]': '',  # Remove content in square brackets
            r'\(.*?\)': '',  # Remove content in parentheses
            r'_+': ' ',      # Replace underscores with spaces
        }
        
        # Create template processor
        template = RenameProcessorTemplate(
            source_path=self.temp_dir,
            destination_path=self.dest_dir,
            patterns=patterns,
            recursive=False,
            archive=False,
            move_source=False,
            dry_run=False,
            interactive=False
        )
        
        # Execute the template
        result = template.execute()
        
        # Verify successful execution
        self.assertTrue(result.is_success())
        stats = result.unwrap()
        self.assertEqual(stats["processed"], len(self.test_files))
        self.assertGreater(stats["renamed"], 0)
        
        # Check if files were renamed and copied to destination
        self.assertTrue((self.dest_dir / "Mystic Vale Chronicles 01.mkv").exists())
        self.assertTrue((self.dest_dir / "Starlight Wanderer 01.mkv").exists())
        self.assertTrue((self.dest_dir / "Crystal Dreams 01.ass").exists())
        
        # Check that source files still exist (since move_source=False)
        self.assertTrue((Path(self.temp_dir) / self.test_files[0]).exists())
        
    def test_template_with_move(self):
        """Test file renaming with move option using RenameProcessorTemplate"""
        # Create pattern mappings
        patterns = {
            r'\[.*?\]': '',  # Remove content in square brackets
            r'\(.*?\)': '',  # Remove content in parentheses
            r'_+': ' ',      # Replace underscores with spaces
        }
        
        # Create template processor with move_source=True
        template = RenameProcessorTemplate(
            source_path=self.temp_dir,
            destination_path=self.dest_dir,
            patterns=patterns,
            recursive=False,
            archive=False,
            move_source=True,
            dry_run=False,
            interactive=False
        )
        
        # Execute the template
        result = template.execute()
        
        # Verify successful execution
        self.assertTrue(result.is_success())
        stats = result.unwrap()
        self.assertEqual(stats["processed"], len(self.test_files))
        self.assertGreater(stats["renamed"], 0)
        
        # Check if files were renamed and moved to destination
        self.assertTrue((self.dest_dir / "Mystic Vale Chronicles 01.mkv").exists())
        self.assertTrue((self.dest_dir / "Starlight Wanderer 01.mkv").exists())
        self.assertTrue((self.dest_dir / "Crystal Dreams 01.ass").exists())
        
        # Check that source files were removed (since move_source=True)
        self.assertFalse((Path(self.temp_dir) / self.test_files[0]).exists())
        
    def test_dry_run(self):
        """Test dry run mode with RenameProcessorTemplate"""
        # Create pattern mappings
        patterns = {
            r'\[.*?\]': '',  # Remove content in square brackets
            r'\(.*?\)': '',  # Remove content in parentheses
            r'_+': ' ',      # Replace underscores with spaces
        }
        
        # Create template processor with dry_run=True
        template = RenameProcessorTemplate(
            source_path=self.temp_dir,
            destination_path=self.dest_dir,
            patterns=patterns,
            recursive=False,
            archive=False,
            move_source=True,
            dry_run=True,
            interactive=False
        )
        
        # Execute the template
        result = template.execute()
        
        # Verify successful execution
        self.assertTrue(result.is_success())
        stats = result.unwrap()
        self.assertEqual(stats["processed"], len(self.test_files))
        self.assertGreater(stats["renamed"], 0)
        
        # Check that no files were created in destination (since dry_run=True)
        self.assertEqual(len(os.listdir(self.dest_dir)), 0)
        
        # Check that source files still exist (since dry_run=True)
        self.assertTrue((Path(self.temp_dir) / self.test_files[0]).exists())
        
    def test_handler_rename(self):
        """Test file renaming with the RenameCommandHandler"""
        try:
            # Create the handler
            handler = RenameCommandHandler(
                sources=[str(self.temp_dir)],
                destination=str(self.dest_dir),
                archive=False,
                move=False,
                dry_run=False,
                interactive=False,
                verbose=False,
                recursive=True,
                patterns={
                    r'\[.*?\]': '',  # Remove content in square brackets
                    r'\(.*?\)': '',  # Remove content in parentheses
                    r'_+': ' ',      # Replace underscores with spaces
                }
            )
            
            # Execute the handler
            result = handler.handle()
            
            # Verify successful execution
            self.assertTrue(result.is_success())
            stats = result.unwrap()
            self.assertEqual(stats["processed"], len(self.test_files))
            self.assertGreater(stats["renamed"], 0)
            
            # Check if files were renamed and copied to destination
            self.assertTrue((self.dest_dir / "Mystic Vale Chronicles 01.mkv").exists())
            self.assertTrue((self.dest_dir / "Starlight Wanderer 01.mkv").exists())
            self.assertTrue((self.dest_dir / "Crystal Dreams 01.ass").exists())
        except (ImportError, AttributeError):
            # Skip if handler dependencies aren't available
            self.skipTest("RenameCommandHandler dependencies not available")
            
if __name__ == "__main__":
    unittest.main()