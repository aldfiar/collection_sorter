"""
Video processor implementation for Collection Sorter.

This module implements template classes for video processing operations
with enhanced parameter validation.
"""

import logging
import os
import re
from pathlib import Path
from typing import Any, Dict, List, Optional, Set, Union

from collection_sorter.files.duplicates import DuplicateHandler
from collection_sorter.files import FilePath
from collection_sorter.result import Result, PathResult, OperationError, ErrorType
from collection_sorter.templates.processors.base import (
    BaseFileProcessor, 
    BaseProcessorValidator,
    ValidationResult,
    Validator,
    ExtensionsValidator
)

logger = logging.getLogger("processors.video")


class VideoProcessorValidator(BaseProcessorValidator):
    """Validator for video processor parameters."""
    
    def validate_parameters(self, **kwargs) -> Result[Dict[str, Any], List[OperationError]]:
        """
        Validate video processor parameters.
        
        Args:
            **kwargs: Parameters to validate
            
        Returns:
            Result with validated parameters or errors
        """
        # First, validate common parameters
        base_result = super().validate_parameters(**kwargs)
        if base_result.is_failure():
            return base_result
            
        validated = base_result.unwrap()
        errors = []
        
        # Validate video-specific parameters
        # 1. Validate video extensions
        video_extensions_result = self._validate_video_extensions(kwargs.get('video_extensions'))
        if not video_extensions_result:
            errors.append(OperationError(
                type=ErrorType.VALIDATION_ERROR,
                message=f"Invalid video extensions: {'; '.join(video_extensions_result.errors)}"
            ))
        else:
            validated['video_extensions'] = video_extensions_result.value
            
        # 2. Validate subtitle extensions
        subtitle_extensions_result = self._validate_subtitle_extensions(kwargs.get('subtitle_extensions'))
        if not subtitle_extensions_result:
            errors.append(OperationError(
                type=ErrorType.VALIDATION_ERROR,
                message=f"Invalid subtitle extensions: {'; '.join(subtitle_extensions_result.errors)}"
            ))
        else:
            validated['subtitle_extensions'] = subtitle_extensions_result.value
            
        # 3. Validate source type (file or directory)
        if 'source_path' in validated:
            if not (validated['source_path'].is_file or validated['source_path'].is_directory):
                errors.append(OperationError(
                    type=ErrorType.VALIDATION_ERROR,
                    message=f"Source path must be a file or directory: {validated['source_path']}",
                    path=str(validated['source_path'])
                ))
            elif validated['source_path'].is_file:
                # If it's a file, check if it has a valid video extension
                if not any(str(validated['source_path'].path).lower().endswith(ext) 
                          for ext in validated['video_extensions']):
                    errors.append(OperationError(
                        type=ErrorType.VALIDATION_ERROR,
                        message=f"Source file does not have a valid video extension: {validated['source_path']}",
                        path=str(validated['source_path'])
                    ))
            
        # 4. Validate destination can be created if needed
        if 'destination_path' in validated and not validated['destination_path'].exists and not kwargs.get('dry_run', False):
            try:
                validated['destination_path'].path.mkdir(parents=True, exist_ok=True)
            except Exception as e:
                errors.append(OperationError(
                    type=ErrorType.VALIDATION_ERROR,
                    message=f"Cannot create destination directory: {e}",
                    path=str(validated['destination_path']),
                    source_exception=e
                ))
        
        # Return validation result
        if errors:
            return Result.failure(errors)
        return Result.success(validated)
    
    def _validate_video_extensions(self, extensions) -> ValidationResult[Set[str]]:
        """
        Validate video file extensions.
        
        Args:
            extensions: Extensions to validate
            
        Returns:
            ValidationResult with validation status and set of extensions
        """
        # Default video extensions if none provided
        if extensions is None:
            return ValidationResult.success({'.mp4', '.mkv', '.avi', '.mov'})
            
        # Common video extensions for validation
        common_video_exts = {
            '.mp4', '.mkv', '.avi', '.mov', '.wmv', '.flv', '.webm', '.m4v', 
            '.mpg', '.mpeg', '.3gp', '.3g2', '.m2ts', '.mts', '.ts', '.vob'
        }
        
        validator = ExtensionsValidator(valid_extensions=common_video_exts)
        result = validator.validate(extensions)
        
        # If no common extensions found, warn but accept
        if result.is_valid and not any(ext.lower() in common_video_exts for ext in result.value):
            logger.warning(f"No common video extensions found in {result.value}")
            
        return result
    
    def _validate_subtitle_extensions(self, extensions) -> ValidationResult[Set[str]]:
        """
        Validate subtitle file extensions.
        
        Args:
            extensions: Extensions to validate
            
        Returns:
            ValidationResult with validation status and set of extensions
        """
        # Default subtitle extensions if none provided
        if extensions is None:
            return ValidationResult.success({'.srt', '.sub', '.idx', '.ass'})
            
        # Common subtitle extensions for validation
        common_subtitle_exts = {
            '.srt', '.sub', '.idx', '.ass', '.ssa', '.vtt', '.sbv', '.smi', '.sami',
            '.rt', '.aqt', '.jss', '.js', '.pjs', '.mpsub', '.tt', '.usf'
        }
        
        validator = ExtensionsValidator(valid_extensions=common_subtitle_exts)
        result = validator.validate(extensions)
        
        # If no common extensions found, warn but accept
        if result.is_valid and not any(ext.lower() in common_subtitle_exts for ext in result.value):
            logger.warning(f"No common subtitle extensions found in {result.value}")
            
        return result


class VideoProcessorTemplate(BaseFileProcessor):
    """Template implementation for processing video files with enhanced validation."""
    
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
        Initialize the video processor template with validation.
        
        Args:
            source_path: Source path to process
            destination_path: Optional destination path
            video_extensions: Set of video file extensions
            subtitle_extensions: Set of subtitle file extensions
            dry_run: Whether to simulate operations
            interactive: Whether to prompt for confirmation
            duplicate_handler: Optional handler for duplicates
        """
        # Create video-specific validator
        validator = VideoProcessorValidator()
        
        # Initialize base processor with validator
        super().__init__(
            source_path=source_path,
            destination_path=destination_path,
            dry_run=dry_run,
            interactive=interactive,
            duplicate_handler=duplicate_handler,
            validator=validator
        )
        
        # Validate and store video-specific parameters
        validation_result = validator.validate_parameters(
            source_path=source_path,
            destination_path=destination_path,
            video_extensions=video_extensions,
            subtitle_extensions=subtitle_extensions,
            dry_run=dry_run,
            interactive=interactive,
            duplicate_handler=duplicate_handler
        )
        
        if validation_result.is_success():
            validated = validation_result.unwrap()
            self.video_extensions = validated['video_extensions']
            self.subtitle_extensions = validated['subtitle_extensions']
        else:
            # Use defaults if validation failed (errors already logged)
            self.video_extensions = {'.mp4', '.mkv', '.avi', '.mov'}
            self.subtitle_extensions = {'.srt', '.sub', '.idx', '.ass'}
        
        # Extend stats for video-specific metrics
        self.stats.update({
            "renamed": 0
        })
    
    def _execute_implementation(self) -> Result[Dict[str, Any], List[OperationError]]:
        """
        Execute the video processing operation with validation.
        
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
                    return Result.failure([OperationError(
                        type=ErrorType.VALIDATION_ERROR,
                        message=f"Source file is not a valid video: {self.source_path}",
                        path=str(self.source_path)
                    )])
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