"""Common utilities for collection sorting operations."""

from .archive import ArchivedCollection
from .files import CollectionPath
from .move import MovableCollection
from .rename import linux_rename_function, windows_rename_function
from .sorter import BaseCollection, MultiThreadTask, SortExecutor

# New refactored modules
from .paths import FilePath, DirectoryPath, PathType
from .services import get_service, register_service, register_instance, register_factory
from .components import FileCollection, FileCollectionComponent, FileMoverComponent, FileArchiverComponent
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
from .file_processor import FileProcessor

# Result pattern modules
from .result import (
    Result, Success, Failure,
    OperationError, ErrorType,
    PathResult, FilesResult, BoolResult, StringResult,
    result_handler
)
from .operations import (
    check_path_exists, ensure_directory, list_files, list_directories,
    move_file, copy_file, rename_file, archive_directory, extract_archive,
    delete_file, delete_directory, move_and_rename, archive_and_delete
)
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
from .result_processor import ResultFileProcessor

# Factory pattern modules
from .factories import (
    StrategyFactory,
    ResultStrategyFactory,
    DuplicateHandlerFactory,
    ProcessorFactory,
    ConfigBasedProcessorFactory,
    create_strategy,
    create_result_strategy,
    create_duplicate_handler,
    create_processor,
    create_processor_from_config
)

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
    "ArchivedCollection",
    "MovableCollection",
    "linux_rename_function",
    "windows_rename_function",
    "BaseCollection",
    "MultiThreadTask",
    "SortExecutor",
    
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
    
    # Factory pattern classes
    "StrategyFactory",
    "ResultStrategyFactory",
    "DuplicateHandlerFactory",
    "ProcessorFactory",
    "ConfigBasedProcessorFactory",
    "create_strategy",
    "create_result_strategy",
    "create_duplicate_handler",
    "create_processor",
    "create_processor_from_config",
    
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
