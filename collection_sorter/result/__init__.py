from .result import (
    BoolResult,
    ErrorType,
    Failure,
    FilesResult,
    OperationError,
    PathResult,
    Result,
    StringResult,
    Success,
    result_handler,
)
from .result_strategies import (
    ArchiveResultStrategy,
    CopyFileResultStrategy,
    DeleteDirectoryResultStrategy,
    DeleteFileResultStrategy,
    ExtractArchiveResultStrategy,
    MoveFileResultStrategy,
    RenameFileResultStrategy,
    ResultFileOperationStrategy,
)
