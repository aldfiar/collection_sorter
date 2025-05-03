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