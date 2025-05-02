"""
Configuration models for collection sorter.

This module contains Pydantic models that define the configuration
structure and provide validation for different parts of the application.
"""

from typing import Optional, List, Dict, Any, Union, Literal
from pathlib import Path
from pydantic import BaseModel, Field, validator, root_validator


class CollectionConfig(BaseModel):
    """Core configuration for collection processing."""
    
    destination: Optional[Path] = Field(
        None, 
        description="Output directory for processed files"
    )
    archive: bool = Field(
        False, 
        description="Create archives of processed files"
    )
    move: bool = Field(
        False, 
        description="Remove source files after processing"
    )
    dry_run: bool = Field(
        False, 
        description="Simulate operations without making changes"
    )
    duplicate_strategy: str = Field(
        "rename_new",
        description="Strategy for handling duplicate files (skip, rename_new, rename_existing, overwrite, move_to_duplicates, ask)"
    )
    duplicates_dir: Optional[Path] = Field(
        None,
        description="Directory to move duplicate files to when using move_to_duplicates strategy"
    )
    
    @validator('destination', 'duplicates_dir', pre=True)
    def validate_paths(cls, v, values, **kwargs):
        """Convert string to Path and expand user directory."""
        if v is None:
            return None
        if isinstance(v, str):
            return Path(v).expanduser()
        return v
    
    @validator('duplicate_strategy')
    def validate_duplicate_strategy(cls, v):
        """Validate duplicate strategy."""
        valid_strategies = ["skip", "rename_new", "rename_existing", "overwrite", "move_to_duplicates", "ask"]
        if v.lower() not in valid_strategies:
            raise ValueError(f"Duplicate strategy must be one of: {', '.join(valid_strategies)}")
        return v.lower()


class LoggingConfig(BaseModel):
    """Logging configuration."""
    
    verbose: bool = Field(
        False, 
        description="Enable verbose output"
    )
    log_file: Optional[Path] = Field(
        None, 
        description="Path to log file"
    )
    log_level: str = Field(
        "INFO", 
        description="Log level"
    )
    
    @validator('log_level')
    def validate_log_level(cls, v):
        """Validate log level."""
        valid_levels = ("DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL")
        if v.upper() not in valid_levels:
            raise ValueError(f"Log level must be one of {valid_levels}")
        return v.upper()
    
    @validator('log_file', pre=True)
    def validate_log_file(cls, v):
        """Convert string to Path and expand user directory."""
        if v is None:
            return None
        if isinstance(v, str):
            return Path(v).expanduser()
        return v


class UIConfig(BaseModel):
    """User interface configuration."""
    
    interactive: bool = Field(
        False, 
        description="Enable interactive mode with confirmation prompts"
    )
    progress_bars: bool = Field(
        True, 
        description="Show progress bars during operations"
    )
    color_output: bool = Field(
        True, 
        description="Use colored terminal output"
    )


class MangaConfig(BaseModel):
    """Manga-specific configuration."""
    
    author_folders: bool = Field(
        False, 
        description="Organize manga by author"
    )
    template: Optional[str] = Field(
        None, 
        description="Template for manga folder naming"
    )


class VideoConfig(BaseModel):
    """Video-specific configuration."""
    
    subtitle_extensions: List[str] = Field(
        default_factory=lambda: [".srt", ".sub", ".ass"],
        description="File extensions to consider as subtitles"
    )
    video_extensions: List[str] = Field(
        default_factory=lambda: [".mp4", ".mkv", ".avi", ".mov"],
        description="File extensions to consider as videos"
    )


class RenameConfig(BaseModel):
    """Rename-specific configuration."""
    
    patterns: Dict[str, str] = Field(
        default_factory=dict,
        description="Regex patterns to use for renaming"
    )
    recursive: bool = Field(
        True,
        description="Process subdirectories recursively"
    )


class ZipConfig(BaseModel):
    """Archive-specific configuration."""
    
    nested: bool = Field(
        False,
        description="Create nested archives"
    )
    compression_level: int = Field(
        6,
        description="Compression level (0-9)"
    )
    

class AppConfig(BaseModel):
    """Main application configuration."""
    
    collection: CollectionConfig = Field(
        default_factory=CollectionConfig,
        description="Core collection processing configuration"
    )
    logging: LoggingConfig = Field(
        default_factory=LoggingConfig,
        description="Logging configuration"
    )
    ui: UIConfig = Field(
        default_factory=UIConfig,
        description="User interface configuration"
    )
    
    # Command-specific configurations
    manga: MangaConfig = Field(
        default_factory=MangaConfig,
        description="Manga-specific configuration"
    )
    video: VideoConfig = Field(
        default_factory=VideoConfig,
        description="Video-specific configuration"
    )
    rename: RenameConfig = Field(
        default_factory=RenameConfig,
        description="Rename-specific configuration"
    )
    zip: ZipConfig = Field(
        default_factory=ZipConfig,
        description="Archive-specific configuration"
    )
    
    class Config:
        """Pydantic model configuration."""
        validate_assignment = True
        extra = "ignore"
        
    def model_dump(self, **kwargs):
        """
        Compatibility for older versions of pydantic.
        
        This provides a consistent interface across different pydantic versions.
        """
        if hasattr(super(), "model_dump"):
            return super().model_dump(**kwargs)
        return self.dict(**kwargs)