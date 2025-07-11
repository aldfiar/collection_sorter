# Collection Sorter

A powerful command-line tool for organizing and processing various file collections, including manga, videos, and general file renaming operations. Features include interactive mode, progress tracking, and customizable configuration.

## Features

- **Media Organization**: Organize manga, videos, and general files with intelligent sorting
- **Batch Operations**: Process multiple files and directories in a single command
- **Archive Support**: Create and manage ZIP archives from collections
- **Interactive Mode**: Preview changes with confirmation prompts
- **Dry Run Option**: Simulate operations without making changes
- **Rich Feedback**: Colorful console output with progress bars
- **Configuration System**: Use config files and environment variables to store preferences
- **Detailed Logging**: Configurable logging with file output support
- **Duplicate Handling**: Multiple strategies for handling duplicate files

## Architecture

Collection Sorter uses several design patterns to ensure maintainability and flexibility:

- **Command Pattern**: CLI commands are implemented as separate handlers
- **Template Method Pattern**: Common file processing steps defined in base classes with customizable steps
- **Factory Pattern**: Dynamic creation of processors based on configuration
- **Result Pattern**: Functional error handling without exceptions
- **Strategy Pattern**: Pluggable strategies for file operations
- **Validation Pattern**: Enhanced parameter validation with early error detection

### Enhanced Processors

The project features a modern processor architecture with:
- **Type-safe validation** using generics and Pydantic models
- **Comprehensive error handling** with detailed error messages
- **Extensible validation framework** for custom processors
- **Template method implementations** for manga, video, and rename operations

## Installation

### Using pip
```bash
pip install collection-sorter
```

### Using Poetry (recommended)
```bash
# Install Poetry if you haven't already
curl -sSL https://install.python-poetry.org | python3 -

# Clone the repository
git clone https://github.com/aldfiar/collection-sorter.git
cd collection-sorter

# Install with Poetry
poetry install

# Activate the virtual environment
poetry shell
```

### Dependencies

Collection Sorter requires Python 3.9 or later and the following dependencies:

- **Core Dependencies**:
  - pycountry: For language detection and formatting
  - parse: For pattern-based file name parsing
  - click: For command-line interface
  - rich: For colorful terminal output
  - python-dateutil: For date parsing and manipulation
  - pyyaml: For configuration file support
  - pydantic: For configuration validation
  - tomli: For TOML configuration support

- **Development Dependencies**:
  - pytest: For testing framework
  - black: For code formatting
  - isort: For import sorting
  - flake8: For code linting
  - mypy: For type checking

These dependencies are automatically installed when you install the package with pip or poetry.

## Basic Usage

The collection-sorter provides several commands for different file organization tasks:

```bash
# General help
collection-sorter --help

# Command-specific help
collection-sorter manga --help
```

## Commands

### Manga Sorting

Sort and organize manga collections:

```bash
collection-sorter manga <source_directories...> [OPTIONS]
```

The manga command parses manga filenames in formats like `[Group/Circle (Author)] Manga Title [Optional tags]` and organizes them by author and series.

### Batch Renaming

Rename files in bulk using patterns:

```bash
collection-sorter rename <source_directories...> [OPTIONS]
```

### Archive Creation

Create archives from collections:

```bash
collection-sorter zip <source_directories...> [OPTIONS]
```

### Video Renaming

Rename video files with standardized formatting:

```bash
collection-sorter video <source_directories...> [OPTIONS]
```

The video command detects season and episode information in formats like `S01E01` or `1x01`.

## Common Options

All commands support these options:

- `-d, --destination PATH`: Specify output directory
- `-a, --archive`: Create archives of processed files
- `-m, --move`: Remove source files after processing
- `--dry-run`: Simulate operations without making changes
- `-i, --interactive`: Enable interactive mode with confirmation prompts
- `-v, --verbose`: Enable verbose output
- `--log-file PATH`: Path to log file
- `--log-level LEVEL`: Set log level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
- `--config PATH`: Path to config file
- `--duplicate-strategy`: Strategy for handling duplicate files (skip, rename_new, rename_existing, overwrite, move_to_duplicates, ask)
- `--duplicates-dir`: Directory to move duplicates to when using move_to_duplicates strategy

## Configuration

You can configure Collection Sorter through:

1. **Command-line Arguments**: Highest priority
2. **Environment Variables**: Prefixed with `COLLECTION_SORTER_`
3. **Config Files**: YAML, TOML, or JSON format in:
   - `./collection_sorter.yaml` (current directory)
   - `~/.collection_sorter.yaml` (home directory)
   - `~/.config/collection_sorter/config.yaml` (config directory)

Example config file:
```yaml
# collection_sorter.yaml
collection:
  destination: ~/Organized
  archive: true
  move: false
  dry_run: false

logging:
  verbose: false
  log_file: ~/.collection_sorter.log
  log_level: INFO

ui:
  interactive: true
  progress_bars: true
  color_output: true

# Command-specific settings
manga:
  author_folders: false
  template: null

video:
  subtitle_extensions:
    - .srt
    - .sub
    - .ass
  video_extensions:
    - .mp4
    - .mkv
    - .avi
    - .mov
```

Generate a configuration template:
```bash
collection-sorter generate-config --format yaml --output ~/.config/collection_sorter/config.yaml
```

## Examples

1. Sort manga collections and create archives:
```bash
collection-sorter manga ~/Downloads/manga -d ~/Manga -a
```

2. Rename video files in interactive mode:
```bash
collection-sorter video ~/Videos/unsorted -d ~/Videos/sorted -i
```

3. Create archives and remove sources (with confirmation):
```bash
collection-sorter zip ~/Collections -d ~/Archives -a -m -i
```

4. Batch rename files with dry run to preview changes:
```bash
collection-sorter rename ~/Documents/messy -d ~/Documents/organized --dry-run
```

5. Use verbose mode to see detailed progress:
```bash
collection-sorter manga ~/Downloads/manga -v
```

6. Configure duplicate handling:
```bash
collection-sorter rename ~/Files -d ~/Organized --duplicate-strategy rename_new
```

## Development

### Setting Up Development Environment

```bash
# Clone the repository
git clone https://github.com/aldfiar/collection-sorter.git
cd collection-sorter

# Install with development dependencies
poetry install

# Activate the virtual environment
poetry shell
```

### Code Quality Tools

The project uses several tools to maintain code quality:

```bash
# Format code with black
black collection_sorter/

# Sort imports with isort
isort collection_sorter/

# Lint code with flake8
flake8 collection_sorter/

# Type check with mypy
mypy collection_sorter/

# Run all quality checks
black collection_sorter/ && isort collection_sorter/ && flake8 collection_sorter/
```

### Running Tests

Collection Sorter has a comprehensive test suite. To run tests:

```bash
# Run all tests with pytest
pytest

# Run tests with coverage
pytest --cov=collection_sorter

# Run specific test file
pytest tests/templates/processors/test_manga.py

# Run tests with verbose output
pytest -v
```

#### Test Requirements

- **Unit Tests**: Most unit tests do not require external dependencies
- **Integration Tests**: Full integration tests require all dependencies to be installed
- **Validation Tests**: Tests for the enhanced processor validation framework
- **CLI Integration Tests**: End-to-end testing of command-line interface

If you're running tests without all dependencies installed, you'll see some tests skipped with messages indicating which dependencies are missing.

### Project Structure

The codebase is organized using clear separation of concerns:

```
collection_sorter/
├── cli.py                      # Main CLI entry point
├── cli_handlers/               # Command handler implementations
├── cli_patterns/               # Command dispatching
├── templates/processors/       # Enhanced processor implementations
│   ├── base.py                # Validation framework
│   ├── manga.py               # Manga processor with validation
│   ├── rename.py              # Rename processor with validation
│   └── video.py               # Video processor with validation
├── config/                     # Configuration management
├── files/                      # File handling utilities
├── result/                     # Result pattern implementation
└── tests/                      # Comprehensive test suite
```

### Contributing

Contributions are welcome! Here's how you can contribute:

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/my-new-feature`
3. Set up the development environment: `poetry install`
4. Make your changes and add tests
5. Ensure code quality standards:
   ```bash
   # Format and lint code
   black collection_sorter/ && isort collection_sorter/ && flake8 collection_sorter/
   
   # Run type checking
   mypy collection_sorter/
   
   # Run all tests
   pytest
   ```
6. Commit your changes: `git commit -am 'Add my new feature'`
7. Push to the branch: `git push origin feature/my-new-feature`
8. Submit a pull request

#### Code Style Guidelines

- Follow PEP 8 with 88-character line length (Black-compatible)
- Use type hints for all function parameters and return types
- Write comprehensive tests for new functionality
- Follow existing design patterns (Template Method, Result, Strategy)
- Add validation for new processor parameters

## License

This project is licensed under the Apache License 2.0 - see the LICENSE file for details.
