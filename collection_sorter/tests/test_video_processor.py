import os
import shutil
import tempfile
import unittest
from pathlib import Path

from collection_sorter.cli_handlers.video_handler import VideoCommandHandler
from collection_sorter.common.templates_extensions import VideoProcessorTemplate


class TestVideoProcessor(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
        self.dest_dir = Path(self.temp_dir) / "destination"
        self.dest_dir.mkdir()
        
        self.test_files = [
            # TV shows with different formats
            "Mystic Forest S01E01 [1080p].mkv",
            "Crystal Dreams 1x02 [720p].mkv",
            "Starlight Chronicles - 03.mp4",
            # Movies with noise
            "Aurora Symphony (2023) [BluRay-1080p].mkv",
            "Ethereal Whispers [2022] [Web-DL].mp4",
            # Subtitles
            "Mystic Forest S01E01.srt",
            "Crystal Dreams 1x02.ass",
        ]
        
        # Create test files
        for filename in self.test_files:
            Path(self.temp_dir, filename).touch()

    def tearDown(self):
        # Clean up temp directory
        shutil.rmtree(self.temp_dir)

    def test_template_video_processor(self):
        """Test video processing with VideoProcessorTemplate"""
        # Create the template processor
        template = VideoProcessorTemplate(
            source_path=self.temp_dir,
            destination_path=self.dest_dir,
            video_extensions={'.mkv', '.mp4'},
            subtitle_extensions={'.srt', '.ass'},
            dry_run=False,
            interactive=False
        )
        
        # Execute the template
        result = template.execute()
        
        # Verify successful execution
        self.assertTrue(result.is_success())
        stats = result.unwrap()
        
        # Count the number of video files (not subtitles)
        video_count = len([f for f in self.test_files if f.endswith(('.mkv', '.mp4'))])
        self.assertEqual(stats["processed"], video_count)
        self.assertGreater(stats["renamed"], 0)
        
        # Check if files were processed correctly
        self.assertTrue((self.dest_dir / "Mystic Forest - S01E01.mkv").exists())
        self.assertTrue((self.dest_dir / "Crystal Dreams - S01E02.mkv").exists())
        self.assertTrue((self.dest_dir / "Starlight Chronicles - 03.mp4").exists())
        
        # Check that subtitles were renamed to match video files
        self.assertTrue((self.dest_dir / "Mystic Forest - S01E01.srt").exists())
        
    def test_video_processor_with_dry_run(self):
        """Test video processing with dry run mode"""
        # Create the template processor with dry_run=True
        template = VideoProcessorTemplate(
            source_path=self.temp_dir,
            destination_path=self.dest_dir,
            video_extensions={'.mkv', '.mp4'},
            subtitle_extensions={'.srt', '.ass'},
            dry_run=True,
            interactive=False
        )
        
        # Execute the template
        result = template.execute()
        
        # Verify successful execution
        self.assertTrue(result.is_success())
        
        # Check that no files were created in destination (since dry_run=True)
        self.assertEqual(len(os.listdir(self.dest_dir)), 0)
        
        # Check that source files still exist
        self.assertTrue((Path(self.temp_dir) / self.test_files[0]).exists())
        
    def test_handler_video_processor(self):
        """Test video processing with VideoCommandHandler"""
        try:
            # Create the handler
            handler = VideoCommandHandler(
                sources=[str(self.temp_dir)],
                destination=str(self.dest_dir),
                dry_run=False,
                interactive=False,
                verbose=False,
                video_extensions={'.mkv', '.mp4'},
                subtitle_extensions={'.srt', '.ass'}
            )
            
            # Execute the handler
            result = handler.handle()
            
            # Verify successful execution
            self.assertTrue(result.is_success())
            stats = result.unwrap()
            
            # Check if files were processed correctly
            self.assertTrue((self.dest_dir / "Mystic Forest - S01E01.mkv").exists())
            self.assertTrue((self.dest_dir / "Crystal Dreams - S01E02.mkv").exists())
            self.assertTrue((self.dest_dir / "Starlight Chronicles - 03.mp4").exists())
            
            # Check that subtitles were renamed to match video files
            self.assertTrue((self.dest_dir / "Mystic Forest - S01E01.srt").exists())
        except (ImportError, AttributeError):
            # Skip if handler dependencies aren't available
            self.skipTest("VideoCommandHandler dependencies not available")
            
    def test_different_formats(self):
        """Test that VideoProcessorTemplate handles different TV show formats"""
        # Create test directory with different formats
        formats_dir = Path(self.temp_dir) / "formats"
        formats_dir.mkdir()
        
        # Different TV show naming formats
        test_formats = [
            "Show S01E01.mkv",  # Standard format
            "Show 1x01.mkv",    # Alternative format
            "Show - 01.mkv",    # Episode only format
            "Show E01.mkv",     # Episode only alt format
        ]
        
        for filename in test_formats:
            (formats_dir / filename).touch()
            
        # Create the template processor
        template = VideoProcessorTemplate(
            source_path=formats_dir,
            destination_path=self.dest_dir,
            video_extensions={'.mkv', '.mp4'},
            subtitle_extensions={'.srt', '.ass'},
            dry_run=False,
            interactive=False
        )
        
        # Execute the template
        result = template.execute()
        
        # Verify successful execution
        self.assertTrue(result.is_success())
        
        # Check if files were processed correctly
        self.assertTrue((self.dest_dir / "Show - S01E01.mkv").exists())
        self.assertTrue((self.dest_dir / "Show - S01E01.mkv").exists())
        self.assertTrue((self.dest_dir / "Show - 01.mkv").exists())
            
if __name__ == "__main__":
    unittest.main()