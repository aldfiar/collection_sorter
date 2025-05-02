# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Build and Test Commands
- Install: `pip install -e .` or `poetry install`
- Run tests: `pytest collection_sorter/tests/`
- Run specific test: `pytest collection_sorter/tests/test_archive.py::TestArchivedCollection::test_exists`
- Lint code: `black collection_sorter/ && isort collection_sorter/ && flake8 collection_sorter/`
- Type check: `mypy collection_sorter/`

## Code Style Guidelines
- **Imports**: Group standard library, third-party, then local imports. Use specific imports (from x import y).
- **Formatting**: Follow Black (88 char line length) with isort for import sorting.
- **Types**: Use full type annotations from `typing` module. Function parameters and return types required.
- **Naming**: snake_case for functions/variables, CamelCase for classes. Constants in UPPER_CASE.
- **Error handling**: Extend from CollectionSorterError base class. Use specific exception subclasses.
- **Docstrings**: Use reStructuredText format docstrings with param and return descriptions.
- **OOP approach**: Use classes to encapsulate related functionality with clear responsibility boundaries.
- **Path handling**: Use pathlib.Path for all file system operations instead of os.path module.