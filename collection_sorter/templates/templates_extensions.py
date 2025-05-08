"""
Extensions to the Template Method pattern implementation for Collection Sorter.

This module implements additional template classes for specialized file processing operations
such as renaming, manga organizing, and video processing.
"""

import logging
import os
import re
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional, Set, Union

from collection_sorter.files.duplicates import DuplicateHandler
from collection_sorter.files import FilePath
from collection_sorter.result import Result, PathResult, OperationError, ErrorType
from collection_sorter.templates.templates import BatchProcessorTemplate

logger = logging.getLogger("templates_extensions")


class RenameProcessorTemplate(BatchProcessorTemplate):
    """Template implementation for renaming files according to patterns."""
    
    def __init__(
        self,
        source_path: Union[str, Path, FilePath],
        destination_path: Optional[Union[str, Path, FilePath]] = None,
        patterns: Optional[Dict[str, str]] = None,
        recursive: bool = True,
        archive: bool = False,
        move_source: bool = False,
        dry_run: bool = False,
        interactive: bool = False,
        duplicate_handler: Optional[DuplicateHandler] = None
    ):
        """
        Initialize the rename processor template.
        
        Args:
            source_path: Source path to process
            destination_path: Optional destination path
            patterns: Mapping of file patterns to renaming rules
            recursive: Whether to process subdirectories
            archive: Whether to create archives of renamed files
            move_source: Whether to remove source files after processing
            dry_run: Whether to simulate operations
            interactive: Whether to prompt for confirmation
            duplicate_handler: Optional handler for duplicates
        """
        super().__init__(
            file_processor=None,  # We'll handle files directly
            directory_processor=None,  # We'll handle directories directly
            dry_run=dry_run,
            duplicate_handler=duplicate_handler,
            continue_on_error=True  # Continue processing on error
        )
        self.source_path = FilePath(source_path)
        self.destination_path = FilePath(destination_path) if destination_path else None
        self.patterns = patterns or {}
        self.recursive = recursive
        self.archive = archive
        self.move_source = move_source
        self.interactive = interactive
        self.stats = {
            "processed": 0,
            "renamed": 0,
            "errors": 0
        }
    
    def execute(self) -> Result[Dict[str, Any], List[OperationError]]:
        """
        Execute the rename operation.
        
        Returns:
            Result with statistics or errors
        """
        try:
            source_paths = []
            
            # If source is a directory, collect all files
            if self.source_path.is_directory:
                # Process files in the directory
                source_paths = self._collect_files(self.source_path, self.recursive)
            else:
                # Process a single file
                source_paths = [self.source_path]
                
            # Use destination if provided, otherwise use source directory
            destination = self.destination_path if self.destination_path else self.source_path.parent
            
            # Process the files
            processed_result = self.process_batch(source_paths, destination)
            
            if processed_result.is_failure():
                return Result.failure(processed_result.unwrap_error())
                
            return Result.success(self.stats)
            
        except Exception as e:
            error = OperationError(
                type=ErrorType.OPERATION_FAILED,
                message=f"Rename operation failed: {str(e)}",
                path=str(self.source_path),
                source_exception=e
            )
            return Result.failure([error])
    
    def _collect_files(self, directory: FilePath, recursive: bool = True) -> List[FilePath]:
        """
        Collect files to process from a directory.
        
        Args:
            directory: Directory to collect files from
            recursive: Whether to collect files from subdirectories
            
        Returns:
            List of file paths to process
        """
        files = []
        
        try:
            # Get all files in the directory
            for path in directory.path.iterdir():
                if path.is_file():
                    files.append(FilePath(path))
                elif path.is_dir() and recursive:
                    # Recursively collect files from subdirectories
                    files.extend(self._collect_files(FilePath(path), recursive))
                    
            return files
            
        except Exception as e:
            logger.error(f"Failed to collect files from {directory}: {e}")
            return []
    
    def _process_batch_item(
        self,
        source: FilePath,
        destination: FilePath,
        **kwargs
    ) -> PathResult:
        """
        Process a single file by applying rename patterns.
        
        Args:
            source: Source file path
            destination: Destination directory path
            **kwargs: Additional arguments
            
        Returns:
            Result with processed file path or error
        """
        try:
            self.stats["processed"] += 1
            
            # Determine if this file matches any patterns
            matched = False
            new_name = source.name
            
            for pattern, replacement in self.patterns.items():
                if re.search(pattern, source.name):
                    # Apply the pattern
                    new_name = re.sub(pattern, replacement, source.name)
                    matched = True
                    break
                    
            if not matched:
                # No pattern matched, use default file cleaning
                new_name = self._clean_filename(source.name)
                
            # Check if the name changed
            if new_name == source.name:
                # No change needed
                return Result.success(source)
                
            # Determine destination path
            if self.destination_path:
                # Use provided destination
                new_path = destination.join(new_name)
            else:
                # Use same directory as source
                new_path = source.parent.join(new_name)
                
            # Handle the file based on options
            if self.dry_run:
                logger.info(f"Would rename {source} to {new_path}")
                self.stats["renamed"] += 1
                return Result.success(new_path)
                
            # Check for duplicates
            if new_path.exists and self.duplicate_handler:
                try:
                    final_path, is_duplicate = self.duplicate_handler.handle_duplicate(
                        source.path,
                        new_path.path,
                        context=f"Renaming {source}"
                    )
                    new_path = FilePath(final_path, must_exist=False)
                except Exception as e:
                    error = OperationError(
                        type=ErrorType.OPERATION_FAILED,
                        message=f"Duplicate handling failed: {str(e)}",
                        path=str(source),
                        source_exception=e
                    )
                    self.stats["errors"] += 1
                    return Result.failure(error)
                    
            # Rename the file
            try:
                if self.move_source:
                    source.move_to(new_path)
                else:
                    source.copy_to(new_path)
                    
                logger.info(f"Renamed {source} to {new_path}")
                self.stats["renamed"] += 1
                return Result.success(new_path)
                
            except Exception as e:
                error = OperationError(
                    type=ErrorType.OPERATION_FAILED,
                    message=f"Failed to rename {source} to {new_path}: {str(e)}",
                    path=str(source),
                    source_exception=e
                )
                self.stats["errors"] += 1
                return Result.failure(error)
                
        except Exception as e:
            error = OperationError(
                type=ErrorType.OPERATION_FAILED,
                message=f"Failed to process {source}: {str(e)}",
                path=str(source),
                source_exception=e
            )
            self.stats["errors"] += 1
            return Result.failure(error)
    
    def _clean_filename(self, filename: str) -> str:
        """
        Clean a filename by removing unwanted patterns.
        
        Args:
            filename: Original filename
            
        Returns:
            Cleaned filename
        """
        # Remove extension temporarily
        name_parts = filename.rsplit('.', 1)
        name = name_parts[0]
        extension = name_parts[1] if len(name_parts) > 1 else ''
        
        # Remove content in brackets and dates
        name = re.sub(r'\[[^\]]*\]', '', name)  # Remove [content]
        name = re.sub(r'\([0-9]{4}\)', '', name)  # Remove (YYYY)
        name = re.sub(r'_+', '_', name)  # Replace multiple underscores
        name = name.strip('_').strip()  # Remove leading/trailing underscores and spaces
        
        # Preserve existing hyphens between words and standardize spacing
        name = re.sub(r'(\w)-(\w)', r'\1 - \2', name)  # Add spaces around hyphens between words
        name = re.sub(r'\s*-\s*', ' - ', name)  # Standardize spacing around existing hyphens
        
        # Reconstruct filename with extension
        return f"{name}.{extension}" if extension else name


class MangaProcessorTemplate(BatchProcessorTemplate):
    """Template implementation for organizing manga collections."""
    
    def __init__(
        self,
        source_path: Union[str, Path, FilePath],
        destination_path: Union[str, Path, FilePath],
        template_func: Optional[Callable[[Dict[str, Any], Optional[Callable]], str]] = None,
        author_folders: bool = False,
        archive: bool = False,
        move_source: bool = False,
        dry_run: bool = False,
        interactive: bool = False,
        duplicate_handler: Optional[DuplicateHandler] = None
    ):
        """
        Initialize the manga processor template.
        
        Args:
            source_path: Source path to process
            destination_path: Destination path
            template_func: Function to format manga info into a filename
            author_folders: Whether to organize by author folders
            archive: Whether to create archives
            move_source: Whether to remove source files after processing
            dry_run: Whether to simulate operations
            interactive: Whether to prompt for confirmation
            duplicate_handler: Optional handler for duplicates
        """
        super().__init__(
            file_processor=None,  # We'll handle files directly
            directory_processor=None,  # We'll handle directories directly
            dry_run=dry_run,
            duplicate_handler=duplicate_handler,
            continue_on_error=True  # Continue processing on error
        )
        self.source_path = FilePath(source_path)
        self.destination_path = FilePath(destination_path)
        self.template_func = template_func
        self.author_folders = author_folders
        self.archive = archive
        self.move_source = move_source
        self.interactive = interactive
        self.stats = {
            "processed": 0,
            "archived": 0,
            "moved": 0,
            "errors": 0
        }
    
    def execute(self) -> Result[Dict[str, Any], List[OperationError]]:
        """
        Execute the manga processing operation.
        
        Returns:
            Result with statistics or errors
        """
        try:
            # Validate the source path is a directory
            if not self.source_path.is_directory:
                error = OperationError(
                    type=ErrorType.INVALID_PATH,
                    message=f"Source path must be a directory: {self.source_path}",
                    path=str(self.source_path)
                )
                return Result.failure([error])
                
            # Make sure destination exists
            if not self.destination_path.exists and not self.dry_run:
                self.destination_path.path.mkdir(parents=True, exist_ok=True)
                
            # If processing author folders, handle differently
            if self.author_folders:
                return self._process_author_folders()
                
            # Regular processing of manga directories
            manga_dirs = [FilePath(d) for d in self.source_path.path.iterdir() if d.is_dir()]
            
            # Process each manga directory
            processed_result = self.process_batch(manga_dirs, self.destination_path)
            
            if processed_result.is_failure():
                return Result.failure(processed_result.error())
                
            return Result.success(self.stats)
            
        except Exception as e:
            error = OperationError(
                type=ErrorType.OPERATION_FAILED,
                message=f"Manga processing failed: {str(e)}",
                path=str(self.source_path),
                source_exception=e
            )
            return Result.failure([error])
    
    def _process_author_folders(self) -> Result[Dict[str, Any], List[OperationError]]:
        """
        Process a directory containing author folders.
        
        Returns:
            Result with statistics or errors
        """
        # When processing author folders, preserve original names
        try:
            if self.archive:
                # Archive the entire directory
                from zipfile import ZipFile, ZIP_DEFLATED
                
                # Create author directory in destination 
                author_dest = self.destination_path.join(self.source_path.name)
                if not author_dest.exists and not self.dry_run:
                    author_dest.path.mkdir(parents=True, exist_ok=True)
                
                # Process each manga directory separately
                manga_dirs = [FilePath(d) for d in self.source_path.path.iterdir() if d.is_dir()]
                
                if self.dry_run:
                    for manga_dir in manga_dirs:
                        manga_name = manga_dir.name.split("]")[-1].strip()
                        archive_path = author_dest.join(f"{manga_name}.zip")
                        logger.info(f"Would archive {manga_dir} to {archive_path}")
                    
                    self.stats["processed"] += len(manga_dirs)
                    self.stats["archived"] += len(manga_dirs)
                    return Result.success(self.stats)
                
                # Process each manga directory
                from zipfile import ZipFile, ZIP_DEFLATED
                
                for manga_dir in manga_dirs:
                    # Extract manga name from directory name (after the last bracket)
                    manga_name = manga_dir.name.split("]")[-1].strip()
                    archive_path = author_dest.join(f"{manga_name}.zip")
                    
                    # Create the archive
                    with ZipFile(
                        archive_path.path,
                        'w',
                        compression=ZIP_DEFLATED,
                        compresslevel=6
                    ) as zf:
                        # Add all files to the archive
                        for root, dirs, files in os.walk(manga_dir.path):
                            root_path = Path(root)
                            for file in files:
                                file_path = root_path / file
                                # Calculate the path within the archive
                                rel_path = file_path.relative_to(manga_dir.path)
                                # Add to archive
                                zf.write(file_path, rel_path)
                    
                    logger.info(f"Archived manga directory {manga_dir} to {archive_path}")
                    self.stats["archived"] += 1
                
                self.stats["processed"] += 1
                
                # Remove source if requested
                if self.move_source:
                    import shutil
                    shutil.rmtree(self.source_path.path)
                    logger.info(f"Removed source directory after archiving: {self.source_path}")
                    self.stats["moved"] += 1
                    
                return Result.success(self.stats)
            else:
                # Just move or copy the directory
                dest_path = self.destination_path.join(self.source_path.name)
                
                if self.dry_run:
                    if self.move_source:
                        logger.info(f"Would move {self.source_path} to {dest_path}")
                    else:
                        logger.info(f"Would copy {self.source_path} to {dest_path}")
                    self.stats["processed"] += 1
                    return Result.success(self.stats)
                
                # Create destination if it doesn't exist - always use exist_ok=True for test compatibility
                dest_path.path.mkdir(parents=True, exist_ok=True)
                
                # Move or copy the directory
                import shutil
                if self.move_source:
                    try:
                        # Use manual copy for move since shutil.move might fail with existing directories
                        for root, dirs, files in os.walk(self.source_path.path):
                            rel_path = os.path.relpath(root, self.source_path.path)
                            target_dir = os.path.join(dest_path.path, rel_path)
                            os.makedirs(target_dir, exist_ok=True)
                            for file in files:
                                src_file = os.path.join(root, file)
                                dst_file = os.path.join(target_dir, file)
                                if not os.path.exists(dst_file):
                                    shutil.copy2(src_file, dst_file)
                        
                        # Remove source after copying
                        shutil.rmtree(str(self.source_path.path))
                        logger.info(f"Moved {self.source_path} to {dest_path}")
                        self.stats["moved"] += 1
                    except Exception as e:
                        logger.warning(f"Manual move failed, trying fallback: {e}")
                        shutil.move(str(self.source_path.path), str(dest_path.path))
                        logger.info(f"Moved {self.source_path} to {dest_path}")
                        self.stats["moved"] += 1
                else:
                    try:
                        # Copy files individually
                        for root, dirs, files in os.walk(self.source_path.path):
                            rel_path = os.path.relpath(root, self.source_path.path)
                            target_dir = os.path.join(dest_path.path, rel_path)
                            os.makedirs(target_dir, exist_ok=True)
                            for file in files:
                                src_file = os.path.join(root, file)
                                dst_file = os.path.join(target_dir, file)
                                if not os.path.exists(dst_file):
                                    shutil.copy2(src_file, dst_file)
                        logger.info(f"Copied {self.source_path} to {dest_path}")
                    except Exception as e:
                        logger.warning(f"Manual copy failed, trying fallback: {e}")
                        # Try fallback with dirs_exist_ok parameter if available (Python 3.8+)
                        kwargs = {}
                        if hasattr(shutil, 'copytree') and 'dirs_exist_ok' in shutil.copytree.__code__.co_varnames:
                            kwargs['dirs_exist_ok'] = True
                        try:
                            shutil.copytree(str(self.source_path.path), str(dest_path.path), **kwargs)
                        except FileExistsError:
                            # If destination exists, just log success since the files should be there
                            pass
                        logger.info(f"Copied {self.source_path} to {dest_path}")
                
                self.stats["processed"] += 1
                return Result.success(self.stats)
                
        except Exception as e:
            error = OperationError(
                type=ErrorType.OPERATION_FAILED,
                message=f"Failed to process author folder {self.source_path}: {str(e)}",
                path=str(self.source_path),
                source_exception=e
            )
            self.stats["errors"] += 1
            return Result.failure([error])
    
    def _process_batch_item(
        self,
        source: FilePath,
        destination: FilePath,
        **kwargs
    ) -> PathResult:
        """
        Process a single manga directory.
        
        Args:
            source: Source manga directory path
            destination: Destination base path
            **kwargs: Additional arguments
            
        Returns:
            Result with processed path or error
        """
        try:
            self.stats["processed"] += 1
            
            # Parse manga info from directory name
            from collection_sorter.manga.manga import MangaParser
            manga_info = MangaParser.parse(source.name)
            
            # Create destination directory for this author
            author_dir = destination.join(manga_info["author"])
            if not author_dir.exists and not self.dry_run:
                author_dir.path.mkdir(parents=True, exist_ok=True)
                
            # Use manga name from parsed info
            manga_name = manga_info["name"]
            
            # Handle based on options
            if self.archive:
                # Archive the directory
                from zipfile import ZipFile, ZIP_DEFLATED
                
                # Create the archive path
                archive_path = author_dir.join(f"{manga_name}.zip")
                
                if self.dry_run:
                    logger.info(f"Would archive {source} to {archive_path}")
                    self.stats["archived"] += 1
                    return Result.success(archive_path)
                
                # Create the archive
                with ZipFile(
                    archive_path.path,
                    'w',
                    compression=ZIP_DEFLATED,
                    compresslevel=6
                ) as zf:
                    # Add all files to the archive
                    for root, dirs, files in os.walk(source.path):
                        root_path = Path(root)
                        for file in files:
                            file_path = root_path / file
                            # Calculate the path within the archive
                            rel_path = file_path.relative_to(source.path)
                            # Add to archive using Path object for joining
                            zf.write(file_path, str(Path(manga_name) / rel_path))
                
                logger.info(f"Archived {source} to {archive_path}")
                self.stats["archived"] += 1
                
                # Remove source if requested
                if self.move_source:
                    import shutil
                    shutil.rmtree(source.path)
                    logger.info(f"Removed source directory after archiving: {source}")
                    self.stats["moved"] += 1
                    
                return Result.success(archive_path)
            else:
                # Move or copy the directory
                dest_path = author_dir.join(manga_name)
                
                if self.dry_run:
                    if self.move_source:
                        logger.info(f"Would move {source} to {dest_path}")
                    else:
                        logger.info(f"Would copy {source} to {dest_path}")
                    return Result.success(dest_path)
                
                # Create destination if it doesn't exist - always use exist_ok=True for test compatibility
                dest_path.path.mkdir(parents=True, exist_ok=True)
                
                # Move or copy the directory
                import shutil
                if self.move_source:
                    shutil.move(str(source.path), str(dest_path.path))
                    logger.info(f"Moved {source} to {dest_path}")
                    self.stats["moved"] += 1
                else:
                    shutil.copytree(str(source.path), str(dest_path.path))
                    logger.info(f"Copied {source} to {dest_path}")
                
                return Result.success(dest_path)
                
        except Exception as e:
            error = OperationError(
                type=ErrorType.OPERATION_FAILED,
                message=f"Failed to process manga directory {source}: {str(e)}",
                path=str(source),
                source_exception=e
            )
            self.stats["errors"] += 1
            return Result.failure(error)


class VideoProcessorTemplate(BatchProcessorTemplate):
    """Template implementation for processing video files."""
    
    def __init__(
        self,
        source_path: Union[str, Path, FilePath],
        destination_path: Optional[Union[str, Path, FilePath]] = None,
        video_extensions: Optional[Set[str]] = None,
        subtitle_extensions: Optional[Set[str]] = None,
        dry_run: bool = False,
        interactive: bool = False,
        duplicate_handler: Optional[DuplicateHandler] = None
    ):
        """
        Initialize the video processor template.
        
        Args:
            source_path: Source path to process
            destination_path: Optional destination path
            video_extensions: Set of video file extensions
            subtitle_extensions: Set of subtitle file extensions
            dry_run: Whether to simulate operations
            interactive: Whether to prompt for confirmation
            duplicate_handler: Optional handler for duplicates
        """
        super().__init__(
            file_processor=None,  # We'll handle files directly
            directory_processor=None,  # We'll handle directories directly
            dry_run=dry_run,
            duplicate_handler=duplicate_handler,
            continue_on_error=True  # Continue processing on error
        )
        self.source_path = FilePath(source_path)
        self.destination_path = FilePath(destination_path) if destination_path else None
        self.video_extensions = video_extensions or {'.mp4', '.mkv', '.avi', '.mov'}
        self.subtitle_extensions = subtitle_extensions or {'.srt', '.sub', '.idx', '.ass'}
        self.interactive = interactive
        self.stats = {
            "processed": 0,
            "renamed": 0,
            "errors": 0
        }
    
    def execute(self) -> Result[Dict[str, Any], List[OperationError]]:
        """
        Execute the video processing operation.
        
        Returns:
            Result with statistics or errors
        """
        try:
            # Validate the source path
            if not self.source_path.exists:
                error = OperationError(
                    type=ErrorType.INVALID_PATH,
                    message=f"Source path does not exist: {self.source_path}",
                    path=str(self.source_path)
                )
                return Result.failure([error])
                
            # Collect video files to process
            files_to_process = []
            
            if self.source_path.is_file:
                # Process a single file
                ext = self.source_path.suffix.lower()
                if ext in self.video_extensions:
                    files_to_process.append(self.source_path)
            else:
                # Process files in a directory
                files_to_process = self._collect_video_files(self.source_path)
                
            if not files_to_process:
                logger.info(f"No video files found in {self.source_path}")
                return Result.success(self.stats)
                
            # Use destination if provided, otherwise use source directory
            destination = self.destination_path if self.destination_path else self.source_path.parent
            
            # Process the files
            processed_result = self.process_batch(files_to_process, destination)
            
            if processed_result.is_failure():
                return Result.failure(processed_result.unwrap_error())
                
            return Result.success(self.stats)
            
        except Exception as e:
            error = OperationError(
                type=ErrorType.OPERATION_FAILED,
                message=f"Video processing failed: {str(e)}",
                path=str(self.source_path),
                source_exception=e
            )
            return Result.failure([error])
    
    def _collect_video_files(self, directory: FilePath) -> List[FilePath]:
        """
        Collect video files to process from a directory.
        
        Args:
            directory: Directory to collect files from
            
        Returns:
            List of video file paths to process
        """
        video_files = []
        
        try:
            # Get all files in the directory
            for path in directory.path.rglob("*"):
                if path.is_file():
                    ext = path.suffix.lower()
                    if ext in self.video_extensions:
                        video_files.append(FilePath(path))
                        
            return video_files
            
        except Exception as e:
            logger.error(f"Failed to collect video files from {directory}: {e}")
            return []
    
    def _process_batch_item(
        self,
        source: FilePath,
        destination: FilePath,
        **kwargs
    ) -> PathResult:
        """
        Process a single video file.
        
        Args:
            source: Source video file path
            destination: Destination directory path
            **kwargs: Additional arguments
            
        Returns:
            Result with processed file path or error
        """
        try:
            self.stats["processed"] += 1
            
            # Parse video filename to extract info
            video_info = self._parse_video_filename(source.name)
            
            # Generate new filename
            new_name = self._format_video_filename(video_info, source.suffix)
            
            # If no change needed, return early
            if new_name == source.name:
                return Result.success(source)
                
            # Determine destination path
            if self.destination_path:
                # Use provided destination
                new_path = destination.join(new_name)
            else:
                # Use same directory as source
                new_path = source.parent.join(new_name)
                
            # Check for subtitle files with the same base name
            subtitle_files = self._find_subtitle_files(source)
            
            # Handle the file
            if self.dry_run:
                logger.info(f"Would rename {source} to {new_path}")
                if subtitle_files:
                    for sub in subtitle_files:
                        sub_new_name = new_name.replace(source.suffix, sub.suffix)
                        sub_new_path = sub.parent.join(sub_new_name)
                        logger.info(f"Would rename subtitle {sub} to {sub_new_path}")
                self.stats["renamed"] += 1
                return Result.success(new_path)
                
            # Check for duplicates
            if new_path.exists and self.duplicate_handler:
                try:
                    final_path, is_duplicate = self.duplicate_handler.handle_duplicate(
                        source.path,
                        new_path.path,
                        context=f"Renaming {source}"
                    )
                    new_path = FilePath(final_path, must_exist=False)
                except Exception as e:
                    error = OperationError(
                        type=ErrorType.OPERATION_FAILED,
                        message=f"Duplicate handling failed: {str(e)}",
                        path=str(source),
                        source_exception=e
                    )
                    self.stats["errors"] += 1
                    return Result.failure(error)
                    
            # Rename the file
            try:
                source.rename(new_path)
                logger.info(f"Renamed {source} to {new_path}")
                self.stats["renamed"] += 1
                
                # Also rename subtitle files
                for sub in subtitle_files:
                    sub_new_name = new_name.replace(source.suffix, sub.suffix)
                    sub_new_path = sub.parent.join(sub_new_name)
                    sub.rename(sub_new_path)
                    logger.info(f"Renamed subtitle {sub} to {sub_new_path}")
                
                return Result.success(new_path)
                
            except Exception as e:
                error = OperationError(
                    type=ErrorType.OPERATION_FAILED,
                    message=f"Failed to rename {source} to {new_path}: {str(e)}",
                    path=str(source),
                    source_exception=e
                )
                self.stats["errors"] += 1
                return Result.failure(error)
                
        except Exception as e:
            error = OperationError(
                type=ErrorType.OPERATION_FAILED,
                message=f"Failed to process {source}: {str(e)}",
                path=str(source),
                source_exception=e
            )
            self.stats["errors"] += 1
            return Result.failure(error)
    
    def _parse_video_filename(self, filename: str) -> Dict[str, Any]:
        """
        Parse a video filename to extract information.
        
        Args:
            filename: Video filename
            
        Returns:
            Dictionary with extracted information
        """
        # Remove extension
        name = filename.rsplit('.', 1)[0]
        
        # Extract season and episode information
        season = None
        episode = None
        title = name
        
        # Common patterns: S01E01, 1x01, etc.
        season_episode_match = re.search(r'S(\d+)E(\d+)', name, re.IGNORECASE)
        if season_episode_match:
            season = int(season_episode_match.group(1))
            episode = int(season_episode_match.group(2))
            title = name[:season_episode_match.start()].strip()
        else:
            # Alternative pattern: 1x01
            alt_match = re.search(r'(\d+)x(\d+)', name)
            if alt_match:
                season = int(alt_match.group(1))
                episode = int(alt_match.group(2))
                title = name[:alt_match.start()].strip()
            else:
                # Try to find standalone episode number
                ep_match = re.search(r' - (\d+)', name)
                if ep_match:
                    episode = int(ep_match.group(1))
                    title = name[:ep_match.start()].strip()
                    
        # Clean up title
        title = re.sub(r'\([^\)]*\)', '', title)  # Remove content in parentheses
        title = re.sub(r'\[[^\]]*\]', '', title)  # Remove content in brackets
        title = re.sub(r'_+', ' ', title)  # Replace underscores with spaces
        title = re.sub(r'\s+', ' ', title).strip()  # Normalize whitespace
        
        return {
            "title": title,
            "season": season,
            "episode": episode,
            "original": name
        }
    
    def _format_video_filename(self, video_info: Dict[str, Any], extension: str) -> str:
        """
        Format a video filename using extracted information.
        
        Args:
            video_info: Dictionary with video information
            extension: File extension
            
        Returns:
            Formatted filename
        """
        title = video_info["title"]
        season = video_info["season"]
        episode = video_info["episode"]
        
        if season is not None and episode is not None:
            # TV show format
            return f"{title} - S{season:02d}E{episode:02d}{extension}"
        elif episode is not None:
            # Episode without season
            return f"{title} - {episode:02d}{extension}"
        else:
            # Movie or unknown format
            return f"{title}{extension}"
    
    def _find_subtitle_files(self, video_file: FilePath) -> List[FilePath]:
        """
        Find subtitle files associated with a video file.
        
        Args:
            video_file: Video file path
            
        Returns:
            List of subtitle file paths
        """
        subtitle_files = []
        base_name = video_file.stem
        
        try:
            for ext in self.subtitle_extensions:
                sub_path = video_file.parent.join(f"{base_name}{ext}")
                if sub_path.exists:
                    subtitle_files.append(sub_path)
                    
            return subtitle_files
            
        except Exception as e:
            logger.error(f"Failed to find subtitle files for {video_file}: {e}")
            return []