# Task: Fix Path Handling

## Goal
Ensure consistent and correct path handling throughout the codebase, standardizing the use of FilePath and Path objects and fixing any issues with path resolution or manipulation.

## Final Result
- Consistent use of pathlib.Path for all file system operations
- Proper usage of FilePath wrapper classes where needed
- Correct handling of absolute vs. relative paths
- Path-related operations properly handling errors

## Files to Change
- `collection_sorter/files/paths.py`
- `collection_sorter/files/files.py`
- Other files with path handling issues identified during testing

## Context
Path handling is a fundamental aspect of a file processing application. Based on the failing tests and the codebase structure, there may be inconsistencies in how paths are handled across different components.

1. The project uses pathlib.Path as noted in the CLAUDE.md guidance:
```
- **Path handling**: Use pathlib.Path for all file system operations instead of os.path module.
```

2. The project appears to use wrapper classes for paths:
```python
# Potential implementation in collection_sorter/files/paths.py
class FilePath:
    """Wrapper class for file paths with additional functionality."""
    # Check implementation for consistency

class DirectoryPath:
    """Wrapper class for directory paths with additional functionality."""
    # Check implementation for consistency
```

3. Issues to look for:
   - Inconsistent use of string paths vs. Path objects
   - Incorrect handling of absolute vs. relative paths
   - Path resolution issues in different components
   - Error handling when paths don't exist or permissions are denied

4. Pattern to follow:
   - Ensure all path handling uses pathlib.Path consistently
   - Verify that FilePath and other wrapper classes are used appropriately
   - Check that error handling for paths follows the Result pattern
   - Verify that path joining and resolution is done correctly

Consistent path handling is essential for reliable file operations across all components of the application.