"""Common utilities for collection sorting operations."""

from .components import FileCollection, FileCollectionComponent, FileMoverComponent, FileArchiverComponent
from .file_processor import FileProcessor
from .files import CollectionPath
from .move import MovableCollection
from .operations import (
    check_path_exists, ensure_directory, list_files, list_directories,
    move_file, copy_file, rename_file, archive_directory, extract_archive,
    delete_file, delete_directory, move_and_rename, archive_and_delete
)
# New refactored modules
from .paths import FilePath, DirectoryPath, PathType
from .rename import linux_rename_function, windows_rename_function
# Result pattern modules
from .result import (
    Result, Success, Failure,
    OperationError, ErrorType,
    PathResult, FilesResult, BoolResult, StringResult,
    result_handler
)
from .result_processor import ResultFileProcessor
from .result_strategies import (
    ResultFileOperationStrategy,
    ResultFileOperationContext,
    MoveFileResultStrategy,
    CopyFileResultStrategy,
    RenameFileResultStrategy,
    ArchiveResultStrategy,
    ExtractArchiveResultStrategy,
    DeleteFileResultStrategy,
    DeleteDirectoryResultStrategy
)
from .services import get_service, register_service, register_instance, register_factory
from .strategies import (
    FileOperationStrategy,
    FileOperationContext,
    MoveFileStrategy,
    CopyFileStrategy,
    ArchiveStrategy,
    ExtractArchiveStrategy,
    RenameFileStrategy,
    get_strategy,
    register_strategy
)

# Comment out the automatic import of factory modules to avoid circular imports
# and issues with Generic type registration - these will be imported as needed
# Users of the library should import specific factories directly from .factories
# when they need them.

# Define factory names for __all__ but don't import them automatically
_factory_names = [
    "StrategyFactory",
    "ResultStrategyFactory",
    "DuplicateHandlerFactory",
    "ProcessorFactory",
    "ConfigBasedProcessorFactory",
    "create_strategy",
    "create_result_strategy",
    "create_duplicate_handler",
    "create_processor",
    "create_processor_from_config"
]

# Template method pattern modules
from .templates import (
    FileProcessorTemplate,
    FileMoveTemplate,
    FileCopyTemplate,
    FileRenameTemplate,
    DirectoryProcessorTemplate,
    DirectoryCopyTemplate,
    DirectoryMoveTemplate,
    ArchiveDirectoryTemplate,
    BatchProcessorTemplate
)

__all__ = [
    # Legacy classes
    "CollectionPath",
    "MovableCollection",
    "linux_rename_function",
    "windows_rename_function",
    
    # New refactored classes
    "FilePath",
    "DirectoryPath",
    "PathType",
    "get_service",
    "register_service",
    "register_instance",
    "register_factory",
    "FileCollection",
    "FileCollectionComponent",
    "FileMoverComponent",
    "FileArchiverComponent",
    "FileOperationStrategy",
    "FileOperationContext",
    "MoveFileStrategy",
    "CopyFileStrategy",
    "ArchiveStrategy",
    "ExtractArchiveStrategy",
    "RenameFileStrategy",
    "get_strategy",
    "register_strategy",
    "FileProcessor",
    
    # Result pattern classes
    "Result",
    "Success",
    "Failure",
    "OperationError",
    "ErrorType",
    "PathResult",
    "FilesResult",
    "BoolResult",
    "StringResult",
    "result_handler",
    "check_path_exists",
    "ensure_directory",
    "list_files",
    "list_directories",
    "move_file",
    "copy_file",
    "rename_file",
    "archive_directory",
    "extract_archive",
    "delete_file",
    "delete_directory",
    "move_and_rename",
    "archive_and_delete",
    "ResultFileOperationStrategy",
    "ResultFileOperationContext",
    "MoveFileResultStrategy",
    "CopyFileResultStrategy",
    "RenameFileResultStrategy",
    "ArchiveResultStrategy",
    "ExtractArchiveResultStrategy",
    "DeleteFileResultStrategy",
    "DeleteDirectoryResultStrategy",
    "ResultFileProcessor",
    
    # Factory pattern classes - imported only as needed
    *_factory_names,
    
    # Template method pattern classes
    "FileProcessorTemplate",
    "FileMoveTemplate",
    "FileCopyTemplate", 
    "FileRenameTemplate",
    "DirectoryProcessorTemplate",
    "DirectoryCopyTemplate",
    "DirectoryMoveTemplate",
    "ArchiveDirectoryTemplate",
    "BatchProcessorTemplate",
]
