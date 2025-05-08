from .result import Result, BoolResult, PathResult, StringResult, Success, FilesResult, Failure, OperationError, \
    ErrorType, result_handler

from .result_strategies import (
    ResultFileOperationStrategy,
    MoveFileResultStrategy,
    CopyFileResultStrategy,
    ArchiveResultStrategy, 
    ExtractArchiveResultStrategy, 
    RenameFileResultStrategy,
    DeleteFileResultStrategy, 
    DeleteDirectoryResultStrategy
)
