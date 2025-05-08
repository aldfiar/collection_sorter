# Task: Update Manga Processing Components

## Goal
Update the manga processing components to fully utilize the modern pattern-based implementation, replacing deprecated code with the template method pattern and ensuring consistent use of the Result pattern for error handling.

## Final Result
- All manga-related tests should pass
- Consistent use of `MangaCommandHandler` using the template method pattern
- Proper inheritance from base classes with consistent constructors
- Compatibility layer for any legacy code as needed
- Appropriate deprecation warnings

## Files to Change
- `collection_sorter/cli_handlers/manga_handler.py`
- `collection_sorter/manga/manga.py`
- `collection_sorter/manga/manga_template.py` 
- `tests/test_manga_handler.py`
- `tests/test_manga_processor.py`
- `tests/test_manga_sort.py`
- `tests/test_manga_processor_template.py`

## Context
The manga processing components appear to be in transition from older procedural code to the newer template method pattern. The main issues are:

1. The `MangaCommandHandler` constructor has issues with its inheritance from `CommandHandler`:
```python
# Current problematic constructor
def __init__(
    self,
    sources: List[str],
    destination: Optional[str] = None,
    archive: bool = False,
    move: bool = False,
    dry_run: bool = False,
    interactive: bool = False,
    verbose: bool = False,
    author_folders: bool = False
):
    """Initialize the manga command handler."""
    super().__init__()  # Missing required parameters for the parent constructor
```

2. The test failures indicate missing parameters when calling the parent constructor:
```
TypeError: CommandHandler.__init__() missing 1 required positional argument: 'sources'
```

3. Pattern to follow:
   - Look at the `ZipCommandHandler` as a reference implementation
   - Ensure proper inheritance and constructor parameters
   - Use the template method pattern for processing steps
   - Use the Result pattern for error handling

Similar to how the ZIP functions were modernized, ensure proper use of the template method pattern while maintaining backward compatibility for testing.