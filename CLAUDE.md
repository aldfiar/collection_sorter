# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview
Collection Sorter is a command-line tool for organizing file collections with a focus on:
- Manga collection organization (parsing filenames and organizing by author)
- Video file renaming (detecting season/episode information)
- Batch renaming operations (pattern-based file renaming)
- Archive creation (ZIP files from directories)

## Architecture
- **Design Patterns**:
  - Command Pattern: Each CLI command has a dedicated handler
  - Template Method Pattern: Base processing classes define workflow with customizable steps
  - Factory Pattern: Processors are created dynamically based on configuration
  - Result Pattern: Functional error handling without exceptions
  - Strategy Pattern: Pluggable strategies for file operations

- **Key Components**:
  - CLI handlers: Handle command-line arguments and dispatch to processors
  - Processors: Perform file/directory operations
  - Templates: Define common processing workflows
  - Results: Handle success/failure states cleanly

## Build and Test Commands
- Install: `pip install -e .` or `poetry install`
- Run tests: `pytest collection_sorter/tests/`
- Run specific test: `pytest collection_sorter/tests/test_archive.py::TestArchivedCollection::test_exists`
- Lint code: `black collection_sorter/ && isort collection_sorter/ && flake8 collection_sorter/`
- Type check: `mypy collection_sorter/`
- Generate config template: `python -m collection_sorter.cli generate-config --format yaml`

## Code Style Guidelines
- **Imports**: Group standard library, third-party, then local imports. Use specific imports (from x import y).
- **Formatting**: Follow Black (88 char line length) with isort for import sorting.
- **Types**: Use full type annotations from `typing` module. Function parameters and return types required.
- **Naming**: snake_case for functions/variables, CamelCase for classes. Constants in UPPER_CASE.
- **Error handling**: Prefer the Result pattern over exceptions. Wrap existing exceptions in OperationError.
- **Docstrings**: Use reStructuredText format docstrings with param and return descriptions.
- **OOP approach**: Use classes to encapsulate related functionality with clear responsibility boundaries.
- **Path handling**: Use pathlib.Path for all file system operations instead of os.path module.

## Code Writing
- Prefer simple, clean, maintainable solutions over clever or complex ones. Readability and maintainability are PRIMARY CONCERNS, even at the cost of conciseness or performance.
- Make the SMALLEST reasonable changes to achieve the desired outcome.
- MUST NEVER make code changes unrelated to your current task. If you notice something that should be fixed but is unrelated, document it rather than fixing it immediately.
- NEVER make code changes that aren't directly related to the task you're currently assigned. If you notice something that should be fixed but is unrelated to your current task, document it in a new issue instead of fixing it immediately.
## Key Files
- **CLI**:
  - `collection_sorter/cli.py`: Main CLI entry point using Click
  - `collection_sorter/cli_patterns/__init__.py`: Command dispatching
  - `collection_sorter/cli_handlers/`: Command handler implementations

- **Core Logic**:
  - `collection_sorter/manga/manga.py`: Manga file parsing and processing
  - `collection_sorter/templates/templates.py`: Template method implementations
  - `collection_sorter/files/`: File and path handling utilities

- **Error Handling**:
  - `collection_sorter/result/result.py`: Result pattern implementation

- **Configuration**:
  - `collection_sorter/config/config.py`: Configuration data models
  - `collection_sorter/config/config_manager.py`: Configuration loading and management

## Best Practices
- Create unit tests for any new functionality. Write ONLY enough code to make the failing test pas
- Use the Result pattern for error handling rather than raising exceptions
- Update typing for all new code
- Follow existing design patterns when adding new features
- Keep responsibility boundaries clear between components

## Testing
- Tests MUST comprehensively cover ALL implemented functionality.
- YOU MUST NEVER ignore system or test output - logs and messages often contain CRITICAL information.
- Test output MUST BE PRISTINE TO PASS.
- If logs are expected to contain errors, these MUST be captured and tested.
- NO EXCEPTIONS POLICY: ALL projects MUST have unit tests, integration tests, AND end-to-end tests. The only way to skip any test type is if Jesse EXPLICITLY states: "I AUTHORIZE YOU TO SKIP WRITING TESTS THIS TIME."

## Version Control

- For non-trivial edits, all changes MUST be tracked in git.
- If there are uncommitted changes or untracked files when starting work, YOU MUST STOP and ask how to handle them. Suggest committing existing work first.