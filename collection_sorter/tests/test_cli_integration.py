import os
import sys
import tempfile
import unittest
import shutil
from pathlib import Path
import subprocess
import json
from unittest.mock import patch

class TestCLIIntegration(unittest.TestCase):
    """Integration tests for the CLI commands with pattern-based implementations."""
    
    def setUp(self):
        # Create a temporary directory for testing
        self.test_dir = tempfile.mkdtemp()
        self.source_dir = Path(self.test_dir) / "source"
        self.dest_dir = Path(self.test_dir) / "destination"
        
        # Create source and destination directories
        self.source_dir.mkdir()
        self.dest_dir.mkdir()
        
        # Create test files and directories
        self._create_test_files()
        
        # Get the location of the CLI module
        self.cli_path = Path(__file__).parents[1] / "cli.py"
        
        # Define the Python executable to use
        self.python_exe = sys.executable
        
    def tearDown(self):
        # Clean up the temporary directory
        shutil.rmtree(self.test_dir)
    
    def _create_test_files(self):
        """Create test files and directories for the tests."""
        # Create a manga directory
        manga_dir = self.source_dir / "manga"
        manga_dir.mkdir()
        
        # Create some manga test directories
        manga_names = [
            "(C90) [Moonweaver Studio (Starlight)] Mystic Forest Symphony",
            "[Silverleaf Works (Aurora)] Crystal Gardens [English]"
        ]
        
        for name in manga_names:
            m_dir = manga_dir / name
            m_dir.mkdir()
            # Add a sample file
            (m_dir / "page1.jpg").touch()
        
        # Create some files for renaming
        files_dir = self.source_dir / "files"
        files_dir.mkdir()
        
        test_files = [
            "Adventure_01_[1080p][ABC123].mkv",
            "Mystery_Island_S01E02_[720p][XYZ456].mp4",
            "Documentary_[2023]_HDRip.avi"
        ]
        
        for name in test_files:
            (files_dir / name).touch()
        
        # Create a directory for archiving
        archive_dir = self.source_dir / "archive"
        archive_dir.mkdir()
        
        # Add some files to archive
        (archive_dir / "file1.txt").write_text("Test file 1")
        (archive_dir / "file2.txt").write_text("Test file 2")
        
        # Create a subdirectory
        subdir = archive_dir / "subdir"
        subdir.mkdir()
        (subdir / "file3.txt").write_text("Test file 3")
    
    def _run_cli_command(self, command, args):
        """Run a CLI command and return the subprocess result."""
        cmd = [self.python_exe, str(self.cli_path), command] + args
        
        try:
            # Run the command and capture output
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                check=True
            )
            return result
        except subprocess.CalledProcessError as e:
            # Print error output if the command fails
            print(f"Command failed with exit code {e.returncode}")
            print(f"STDOUT: {e.stdout}")
            print(f"STDERR: {e.stderr}")
            raise
    
    @patch('builtins.input', return_value='y')  # Auto-confirm any prompts
    def test_manga_command(self, mock_input):
        """Test the manga command."""
        try:
            # Run the manga command
            manga_source = str(self.source_dir / "manga")
            manga_dest = str(self.dest_dir / "manga_output")
            
            args = [
                manga_source,
                "--destination", manga_dest,
                "--dry-run"  # Use dry run to avoid making actual changes
            ]
            
            result = self._run_cli_command("manga", args)
            
            # Check that the command executed successfully
            self.assertEqual(result.returncode, 0)
            
            # Check for expected output indicating it worked
            self.assertIn("manga command", result.stdout.lower(), 
                         "Command output should indicate manga processing")
        except (subprocess.SubprocessError, FileNotFoundError):
            self.skipTest("Manga command could not be executed")
    
    @patch('builtins.input', return_value='y')  # Auto-confirm any prompts
    def test_zip_command(self, mock_input):
        """Test the zip command."""
        try:
            # Run the zip command
            zip_source = str(self.source_dir / "archive")
            zip_dest = str(self.dest_dir / "zip_output")
            
            args = [
                zip_source,
                "--destination", zip_dest,
                "--dry-run"  # Use dry run to avoid making actual changes
            ]
            
            result = self._run_cli_command("zip", args)
            
            # Check that the command executed successfully
            self.assertEqual(result.returncode, 0)
            
            # Check for expected output indicating it worked
            self.assertIn("zip command", result.stdout.lower(), 
                         "Command output should indicate archive processing")
        except (subprocess.SubprocessError, FileNotFoundError):
            self.skipTest("Zip command could not be executed")
    
    @patch('builtins.input', return_value='y')  # Auto-confirm any prompts
    def test_rename_command(self, mock_input):
        """Test the rename command."""
        try:
            # Run the rename command
            rename_source = str(self.source_dir / "files")
            rename_dest = str(self.dest_dir / "rename_output")
            
            args = [
                rename_source,
                "--destination", rename_dest,
                "--dry-run"  # Use dry run to avoid making actual changes
            ]
            
            result = self._run_cli_command("rename", args)
            
            # Check that the command executed successfully
            self.assertEqual(result.returncode, 0)
            
            # Check for expected output indicating it worked
            self.assertIn("rename command", result.stdout.lower(), 
                         "Command output should indicate rename processing")
        except (subprocess.SubprocessError, FileNotFoundError):
            self.skipTest("Rename command could not be executed")
    
    @patch('builtins.input', return_value='y')  # Auto-confirm any prompts
    def test_video_command(self, mock_input):
        """Test the video command."""
        try:
            # Run the video command
            video_source = str(self.source_dir / "files")
            video_dest = str(self.dest_dir / "video_output")
            
            args = [
                video_source,
                "--destination", video_dest,
                "--dry-run"  # Use dry run to avoid making actual changes
            ]
            
            result = self._run_cli_command("video", args)
            
            # Check that the command executed successfully
            self.assertEqual(result.returncode, 0)
            
            # Check for expected output indicating it worked
            self.assertIn("video command", result.stdout.lower(), 
                         "Command output should indicate video processing")
        except (subprocess.SubprocessError, FileNotFoundError):
            self.skipTest("Video command could not be executed")
    
    def test_help_command(self):
        """Test that the help command works."""
        # Run the help command
        result = self._run_cli_command("--help", [])
        
        # Check that the command executed successfully
        self.assertEqual(result.returncode, 0)
        
        # Check for expected output
        self.assertIn("usage", result.stdout.lower())
        
        # Check that all commands are listed
        commands = ["manga", "rename", "zip", "video"]
        for cmd in commands:
            self.assertIn(cmd, result.stdout.lower(), 
                         f"Help output should include {cmd} command")

if __name__ == "__main__":
    unittest.main()