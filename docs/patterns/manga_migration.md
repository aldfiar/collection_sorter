# Manga Processing Migration

## Overview

This document outlines the migration of the manga processing components to fully utilize the modern pattern-based implementation, replacing deprecated code with the template method pattern and ensuring consistent use of the Result pattern for error handling.

## Changes Made

### MangaCommandHandler

1. Refactored `MangaCommandHandler` to properly inherit from `CommandHandler` base class
   - Fixed constructor signature to match parent class
   - Added required parameters for parent constructor
   - Added proper error typing
   - Implemented full template method pattern with clear steps

2. Added compatibility layer for tests
   - Created `MangaCommandHandlerTemplateMethod` for backward compatibility
   - This class extends `TemplateMethodCommandHandler` and maintains the previous API
   - Added deprecation warnings to encourage new code to use the primary `MangaCommandHandler`

3. Fixed implementation details
   - Improved error handling with proper error types
   - Added duplicate handling support
   - Fixed issues with file path handling and consistency

### Tests

1. Updated test imports
   - Changed imports to use the compatibility layer (`MangaCommandHandlerTemplateMethod`) 
   - Added deprecation warnings for older test files

2. Added documentation
   - Created this migration guide
   - Added deprecation warnings to guide users toward the modern implementation

## Usage

### New Code

For new code, use the main `MangaCommandHandler` class:

```python
from collection_sorter.cli_handlers.manga_handler import MangaCommandHandler

handler = MangaCommandHandler(
    sources=["path/to/manga"],
    destination="path/to/destination",
    archive=False,
    move=False,
    dry_run=False,
    interactive=False,
    duplicate_strategy="rename_new",
    duplicates_dir=None,
    verbose=False,
    author_folders=False
)

result = handler.handle()
if result.is_success():
    data = result.unwrap()
    print(f"Processed {data['processed']} files")
else:
    print(f"Errors: {result.unwrap_error()}")
```

### Legacy Code

For backward compatibility with existing code, use `MangaCommandHandlerTemplateMethod`:

```python
from collection_sorter.cli_handlers.manga_handler import MangaCommandHandlerTemplateMethod

# This class maintains the old API for compatibility
handler = MangaCommandHandlerTemplateMethod(
    sources=["path/to/manga"],
    destination="path/to/destination",
    archive=False,
    move=False,
    dry_run=False,
    interactive=False,
    verbose=False,
    author_folders=False
)

result = handler.handle()
```

## Future Work

- Complete migration of all tests to use the new implementation
- Fix issues with author folders processing in `MangaProcessorTemplate`
- Implement more template method patterns for other functionality
- Improve duplicate handling strategies