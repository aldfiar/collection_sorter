"""
Template processor implementations for Collection Sorter.

This module provides processors for various file types using the Template Method pattern.
"""

from collection_sorter.templates.processors.base import (
    BaseFileProcessor,
    BaseProcessorValidator,
    ValidationResult,
    Validator,
    PathValidator,
    ExtensionsValidator
)

from collection_sorter.templates.processors.rename import (
    RenameProcessorTemplate,
    RenameProcessorValidator,
    PatternValidator
)

from collection_sorter.templates.processors.manga import (
    MangaProcessorTemplate,
    MangaProcessorValidator,
    MangaTemplateValidator
)

from collection_sorter.templates.processors.video import (
    VideoProcessorTemplate,
    VideoProcessorValidator
)

__all__ = [
    # Base classes
    'BaseFileProcessor',
    'BaseProcessorValidator',
    'ValidationResult',
    'Validator',
    'PathValidator',
    'ExtensionsValidator',
    
    # Rename processor
    'RenameProcessorTemplate',
    'RenameProcessorValidator',
    'PatternValidator',
    
    # Manga processor
    'MangaProcessorTemplate',
    'MangaProcessorValidator',
    'MangaTemplateValidator',
    
    # Video processor
    'VideoProcessorTemplate',
    'VideoProcessorValidator'
]