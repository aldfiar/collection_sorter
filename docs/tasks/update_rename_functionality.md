# Task: Update Rename Functionality

## Goal
Refactor the file renaming functionality to fully utilize the modern pattern-based implementation, replacing any deprecated or legacy code with the template method pattern and ensuring consistent error handling with the Result pattern.

## Final Result
- All rename-related tests should pass
- Consistent use of `RenameCommandHandler` with the template method pattern
- Proper inheritance from base classes with consistent constructors
- Compatibility layer for legacy code with appropriate deprecation warnings
- File renaming using the modern template approach

## Files to Change
- `collection_sorter/cli_handlers/rename_handler.py`
- `collection_sorter/files/rename.py`
- `tests/test_mass_rename.py`
- `tests/test_rename_processor.py`
- Any legacy `mass_rename.py` files (if present)

## Context
The rename functionality seems to have similar issues to what we observed with the mass_zip module, where older procedural-style code needs to be replaced with the modern pattern-based approach.

1. The failing tests in `test_mass_rename.py` indicate potential use of deprecated functions:
```
FAILED tests/test_mass_rename.py::TestMassRename::test_clean_name - NameError...
FAILED tests/test_mass_rename.py::TestMassRename::test_rename_task - NameError...
FAILED tests/test_mass_rename.py::TestMassRename::test_unique_names - NameError...
```

2. The `test_rename_processor.py` tests are also failing, suggesting issues with the current implementation:
```
FAILED tests/test_rename_processor.py::TestRenameProcessor::test_handler_rename
FAILED tests/test_rename_processor.py::TestRenameProcessor::test_template_basic_rename
FAILED tests/test_rename_processor.py::TestRenameProcessor::test_template_with_move
```

3. Pattern to follow:
   - Use the successful refactoring of the ZIP functionality as a reference
   - Update the `RenameCommandHandler` to properly inherit from base classes
   - Implement the template method pattern for rename operations
   - Create a compatibility layer with deprecation warnings
   - Update tests to work with both old and new implementations during transition

The rename functionality should follow similar patterns to the ZipCommandHandler, using the template method pattern for file rename operations and consistent error handling with the Result pattern.