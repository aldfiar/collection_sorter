from .result import Result, BoolResult, PathResult, StringResult, Success, FilesResult, Failure, OperationError, \
    ErrorType, result_handler

from .result_strategies import ArchiveResultStrategy, ExtractArchiveResultStrategy, RenameFileResultStrategy, \
    DeleteFileResultStrategy, DeleteDirectoryResultStrategy
