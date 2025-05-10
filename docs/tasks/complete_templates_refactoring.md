# Complete Templates Refactoring Task

## Goal
Complete the refactoring of the templates system by removing the deprecated `templates_extensions.py` file and fully transitioning all code to use the new modular processors package structure with enhanced validation.

## Background
The initial phase of refactoring has created a new package structure under `templates/processors/` with separate modules for each processor type and a robust validation framework. However, the old `templates_extensions.py` file still exists, and some parts of the codebase may still reference it directly. We need to complete the transition to make the codebase more maintainable.

## Final Result
When completed, the codebase should:
1. Have no references to `templates_extensions.py`
2. Use the new processor classes from `templates/processors/` package exclusively
3. Have updated tests that verify the enhanced validation functionality
4. Have documentation updated to reflect the new architecture

## Tasks

### 1. Update Direct Imports
Find and update all direct imports from `templates_extensions.py` to use the new package structure:

```python
# Old
from collection_sorter.templates.templates_extensions import MangaProcessorTemplate

# New
from collection_sorter.templates.processors import MangaProcessorTemplate
```

Files that likely need updating:
- `collection_sorter/cli_handlers/*.py` (all CLI handlers)
- `collection_sorter/common/factories.py`
- Any custom implementations that extend these classes

### 2. Update Factory Classes
The factory classes that create processor instances need to be updated to use the new classes with validation:

- `collection_sorter/common/factories.py`:
  - Update the `ProcessorFactory` class
  - Update the `ConfigBasedProcessorFactory` class
  - Ensure they use the new validation capabilities

### 3. Delete Deprecated File
After all usages are updated, remove the deprecated file:
- `collection_sorter/templates/templates_extensions.py`

### 4. Update Tests
Update existing tests to work with the new classes and add new tests for validation:

- Update existing tests in:
  - `tests/templates/test_templates.py`
  - `tests/cli_handlers/test_*_processor.py` files
  
- Create new validation-specific tests:
  - `tests/templates/test_processors_validation.py`

The new tests should verify:
- Basic functionality still works
- Validation correctly identifies invalid parameters
- Error messages are clear and helpful
- Edge cases are properly handled

### 5. Documentation Updates
Update relevant documentation:

- `docs/project_structure.md`: Update to reflect the new package structure
- Add validation documentation to explain how to use the validation framework

### 6. Integration Tests
Create or update integration tests to ensure the new components work together:

- `tests/test_cli_integration.py`: Ensure CLI commands correctly use the new processors

## Implementation Notes

### Validation Testing Strategy
The new tests should verify:

1. **Basic validation:** Test that valid inputs pass validation
2. **Invalid paths:** Test handling of non-existent or invalid paths
3. **Invalid extensions:** Test handling of unsupported file extensions
4. **Invalid patterns:** Test handling of malformed regex patterns
5. **Type safety:** Test handling of incorrect parameter types
6. **Error messages:** Verify error messages are clear and informative

### Backward Compatibility
While removing `templates_extensions.py`, we must maintain backward compatibility for any code that imports from `collection_sorter.templates`. The existing `__init__.py` already re-exports the necessary classes, so external code should continue to work.

## Testing
Before completing this task, run the full test suite to ensure nothing is broken:

```bash
pytest collection_sorter/tests/
```

## Completion Criteria
- All references to `templates_extensions.py` have been removed
- All tests pass, including new validation tests
- Documentation is updated to reflect the new architecture
- No regressions in functionality