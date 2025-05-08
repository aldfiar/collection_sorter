# Circular Import Resolution

## Problem

The Collection Sorter codebase had a circular import issue that was causing test failures. The specific circular dependency was:

1. `collection_sorter/files/__init__.py` imported from `move.py`
2. `collection_sorter/files/move.py` imported from `duplicates.py` 
3. `duplicates.py` imported from `common/exceptions.py`
4. `common/exceptions.py` imported from `common/components.py`
5. `common/components.py` imported `FilePath` from `files` package, creating a circular dependency

This circular import pattern caused errors like:
```
ImportError: cannot import name 'FilePath' from partially initialized module 'collection_sorter.files'
```

Additional circular imports were found between:
- `operations.py` and `result_strategies.py`

## Solution

### First Circular Import Fix

1. **Updated files/__init__.py**: Modified to directly expose `FilePath` from `paths.py`
   ```python
   from .files import CollectionPath
   from .paths import FilePath, PathType, DirectoryPath
   from .move import MovableCollection
   ```

2. **Modified common/components.py**: Changed to avoid direct imports from the `files` package
   - Added a helper function `_to_path()` to handle path conversion
   - Used direct `Path` objects instead of `FilePath` within components
   - Replaced `self.root_path` with `self._path` in `FileCollection`

3. **Updated test_factories.py**: Fixed imports due to module relocation
   ```python
   from collection_sorter.result.result_strategies import (
       MoveFileResultStrategy,
       # ...
   )
   ```

4. **Fixed DuplicateHandler settings**: Modified tests to account for the behavior where `interactive=True` would set `strategy=DuplicateStrategy.ASK`

### Best Practices to Avoid Circular Imports

1. **Use Forward References**: When you need types from modules that might cause circular dependencies, use string literals as type hints:
   ```python
   def function(param: "Type") -> "ReturnType":
       pass
   ```

2. **Restructure Module Hierarchy**: Design your module hierarchy to avoid circular dependencies
   - Move shared code to a common module that both dependent modules can import
   - Consider using composition over inheritance where possible

3. **Import Where Needed**: Import modules inside functions or methods rather than at the module level when appropriate

4. **Deferred Imports**: Place imports inside functions when they're only needed by that function

5. **Interface Segregation**: Create smaller, focused interfaces to reduce interdependencies

## Additional Considerations

- The codebase should be further reviewed for any other potential circular imports
- Consider a more comprehensive refactoring to better separate concerns and reduce coupling between modules
- Document dependency relationships to help prevent future circular import issues

By implementing these changes, we've managed to fix the circular import issues and allow the tests to run successfully.