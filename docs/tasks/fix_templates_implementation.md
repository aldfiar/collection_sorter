# Task: Fix Templates Implementation

## Goal
Fix the template method implementation issues in the `collection_sorter/templates` module to ensure all template-related tests pass and maintain consistent behavior across all processor types.

## Final Result
- All template-related tests should pass
- Consistent behavior across all template implementations
- Correct error handling using the Result pattern
- Properly functioning directory and file operation templates

## Files to Change
- `collection_sorter/templates/templates.py`
- `collection_sorter/templates/templates_extensions.py`
- `tests/test_templates.py`

## Context
The template module is a core part of the codebase, providing the skeleton for file operations using the template method pattern. Several tests are failing, suggesting issues with the implementation:

1. Multiple failures in the templates test file:
```
FAILED tests/test_templates.py::TestTemplateMethod::test_archive_directory_template
FAILED tests/test_templates.py::TestTemplateMethod::test_custom_file_processor
FAILED tests/test_templates.py::TestTemplateMethod::test_directory_copy_template
FAILED tests/test_templates.py::TestTemplateMethod::test_directory_move_template
FAILED tests/test_templates.py::TestTemplateMethod::test_duplicate_handling
FAILED tests/test_templates.py::TestTemplateMethod::test_error_handling
FAILED tests/test_templates.py::TestTemplateMethod::test_file_copy_template
FAILED tests/test_templates.py::TestTemplateMethod::test_file_move_template
FAILED tests/test_templates.py::TestTemplateMethod::test_file_rename_template
```

2. Potential issues to look for:
   - Constructor parameter mismatches
   - Inheritance issues
   - Error handling inconsistencies
   - FilePath usage inconsistencies
   - DuplicateHandler integration problems

3. Key template classes to focus on:
```python
class FileProcessorTemplate(ABC):
    """Abstract base class for file processors using the Template Method pattern."""
    # Check initialization and hook methods

class DirectoryProcessorTemplate(ABC):
    """Abstract base class for directory processors using the Template Method pattern."""
    # Check initialization and hook methods

class ArchiveDirectoryTemplate(DirectoryProcessorTemplate):
    """Template implementation for archiving directories."""
    # Check for errors in implementation
```

4. Pattern to follow:
   - Ensure consistent initialization across all template implementations
   - Verify that hook methods are properly implemented
   - Confirm Result pattern is used correctly for error handling
   - Check that file path handling is consistent

The templates are the foundation for the pattern-based implementation, so fixing these issues is critical for ensuring consistent behavior across all components.