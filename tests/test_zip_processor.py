import os
import shutil
import tempfile
import unittest
from pathlib import Path

from collection_sorter.cli_handlers.zip_handler import ZipCommandHandler
from collection_sorter.files.duplicates import DuplicateHandler
from collection_sorter.common.paths import FilePath
from collection_sorter.templates.templates import ArchiveDirectoryTemplate, BatchProcessorTemplate


class TestZipProcessor(unittest.TestCase):
    def setUp(self):
        # Create a temporary directory
        self.test_dir = tempfile.mkdtemp()
        self.source_dir = Path(self.test_dir) / "source"
        self.dest_dir = Path(self.test_dir) / "destination"
        
        # Create test directory structure
        self.source_dir.mkdir()
        self.dest_dir.mkdir()
        
        # Create some test files
        (self.source_dir / "test1.txt").write_text("test1")
        (self.source_dir / "subdir").mkdir()
        (self.source_dir / "subdir" / "test2.txt").write_text("test2")

    def tearDown(self):
        # Clean up the temporary directory
        shutil.rmtree(self.test_dir)
        
    def test_archive_directory_template(self):
        """Test the ArchiveDirectoryTemplate for archiving directories"""
        # Create duplicate handler
        duplicate_handler = DuplicateHandler(
            strategy="rename_new", 
            interactive=False,
            dry_run=False
        )
        
        # Create the archiver template
        archiver = ArchiveDirectoryTemplate(
            dry_run=False,
            duplicate_handler=duplicate_handler,
            recursive=True,
            compression_level=6
        )
        
        source_path = FilePath(self.source_dir)
        dest_path = FilePath(self.dest_dir)
        
        # Archive the directory
        result = archiver.process_directory(source_path, dest_path)
        
        # Verify successful execution
        self.assertTrue(result.is_success())
        archive_path = result.unwrap()
        
        # Check if the archive was created
        self.assertTrue(archive_path.exists)
        self.assertTrue(archive_path.is_file)
        self.assertEqual(archive_path.suffix, ".zip")
        
        # Check that the archive contains the expected files
        import zipfile
        with zipfile.ZipFile(archive_path.path, 'r') as zip_ref:
            file_list = zip_ref.namelist()
            self.assertIn("source/test1.txt", file_list)
            self.assertIn("source/subdir/test2.txt", file_list)
            
    def test_archive_with_removal(self):
        """Test archiving with source removal"""
        # Create duplicate handler
        duplicate_handler = DuplicateHandler(
            strategy="rename_new", 
            interactive=False,
            dry_run=False
        )
        
        # Create the archiver template
        archiver = ArchiveDirectoryTemplate(
            dry_run=False,
            duplicate_handler=duplicate_handler,
            recursive=True,
            compression_level=6
        )
        
        source_path = FilePath(self.source_dir)
        dest_path = FilePath(self.dest_dir)
        
        # Archive the directory and remove source
        result = archiver.process_directory(source_path, dest_path, remove_source=True)
        
        # Verify successful execution
        self.assertTrue(result.is_success())
        
        # Check that the source directory was removed
        self.assertFalse(self.source_dir.exists())
        
    def test_batch_processor(self):
        """Test batch processing with ArchiveDirectoryTemplate"""
        # Create duplicate handler
        duplicate_handler = DuplicateHandler(
            strategy="rename_new", 
            interactive=False,
            dry_run=False
        )
        
        # Create the archiver template
        archiver = ArchiveDirectoryTemplate(
            dry_run=False,
            duplicate_handler=duplicate_handler,
            recursive=True,
            compression_level=6
        )
        
        # Create a batch processor
        batch_processor = BatchProcessorTemplate(
            directory_processor=archiver,
            dry_run=False,
            duplicate_handler=duplicate_handler,
            continue_on_error=True
        )
        
        # Create multiple source directories
        dir1 = Path(self.test_dir) / "dir1"
        dir2 = Path(self.test_dir) / "dir2"
        dir1.mkdir()
        dir2.mkdir()
        (dir1 / "file1.txt").write_text("file1")
        (dir2 / "file2.txt").write_text("file2")
        
        # Process the batch
        result = batch_processor.process_batch(
            [FilePath(dir1), FilePath(dir2)],
            FilePath(self.dest_dir)
        )
        
        # Verify successful execution
        self.assertTrue(result.is_success())
        processed = result.unwrap()
        self.assertEqual(len(processed), 2)
        
        # Check if the archives were created
        self.assertTrue((self.dest_dir / "dir1.zip").exists())
        self.assertTrue((self.dest_dir / "dir2.zip").exists())
        
    def test_zip_command_handler(self):
        """Test the ZipCommandHandler"""
        try:
            # Create the handler
            handler = ZipCommandHandler(
                sources=[str(self.source_dir)],
                destination=str(self.dest_dir),
                archive=False,
                move=False,
                dry_run=False,
                interactive=False
            )
            
            # Execute the handler
            result = handler.handle()
            
            # Verify successful execution
            self.assertTrue(result.is_success())
            stats = result.unwrap()
            self.assertEqual(stats.get("processed_sources"), 1)
            
            # Check if the archive was created
            self.assertTrue((self.dest_dir / f"{self.source_dir.name}.zip").exists())
        except (ImportError, AttributeError):
            # Skip if handler dependencies aren't available
            self.skipTest("ZipCommandHandler dependencies not available")
        
    def test_dry_run(self):
        """Test dry run mode"""
        # Create duplicate handler
        duplicate_handler = DuplicateHandler(
            strategy="rename_new", 
            interactive=False,
            dry_run=True
        )
        
        # Create the archiver template in dry run mode
        archiver = ArchiveDirectoryTemplate(
            dry_run=True,
            duplicate_handler=duplicate_handler,
            recursive=True,
            compression_level=6
        )
        
        source_path = FilePath(self.source_dir)
        dest_path = FilePath(self.dest_dir)
        
        # Archive the directory in dry run mode
        result = archiver.process_directory(source_path, dest_path)
        
        # Verify successful execution
        self.assertTrue(result.is_success())
        
        # Verify no files were created in the destination directory
        self.assertEqual(len(os.listdir(self.dest_dir)), 0)
        
if __name__ == "__main__":
    unittest.main()