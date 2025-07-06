# Collection Sorter Project Structure

This document provides an overview of the Collection Sorter project architecture and codebase organization.

## High-Level Architecture

Collection Sorter uses multiple design patterns to ensure maintainability and flexibility:

1. **Command Pattern**: CLI commands are implemented as separate handlers
2. **Template Method Pattern**: Common workflows defined in base classes with customizable steps
3. **Factory Pattern**: Dynamic creation of processors based on configuration
4. **Result Pattern**: Functional error handling without exceptions
5. **Strategy Pattern**: Pluggable strategies for file operations
6. **Validation Pattern**: Enhanced parameter validation for processors

## Directory Structure

```
collection_sorter/
├── __init__.py
├── cli.py                      # Main CLI entry point
├── cli_handlers/               # Command handler implementations
│   ├── __init__.py
│   ├── base_handler.py         # Base handler classes
│   ├── manga_handler.py
│   ├── rename_handler.py
│   ├── video_handler.py
│   └── zip_handler.py
├── cli_patterns/               # Command dispatching
│   └── __init__.py
├── common/                     # Shared components
│   ├── __init__.py
│   ├── components.py
│   ├── exceptions.py
│   ├── factories.py            # Factory implementations
│   └── services.py
├── config/                     # Configuration management
│   ├── __init__.py
│   ├── config.py               # Legacy config compatibility
│   ├── config_manager.py       # Central config management
│   └── config_models.py        # Pydantic models for config
├── files/                      # File handling utilities
│   ├── __init__.py
│   ├── duplicates.py
│   ├── file_processor.py
│   ├── files.py
│   ├── move.py
│   ├── paths.py
│   └── rename.py
├── manga/                      # Manga-specific logic
│   ├── __init__.py
│   ├── manga.py                # Manga parsing
│   └── manga_template.py       # Manga formatting templates
├── music/                      # Music collection handling
│   ├── __init__.py
│   └── music_collection.py
├── operations.py               # Core operations
├── project_logging.py          # Logging setup
├── result/                     # Result pattern implementation
│   ├── __init__.py
│   ├── result.py               # Core Result class
│   ├── result_processor.py     # Result-aware processors
│   └── result_strategies.py    # Result handling strategies
├── strategies/                 # Strategy pattern implementations
│   ├── __init__.py
│   └── strategies.py
├── templates/                  # Template method implementations
│   ├── __init__.py
│   ├── templates.py
│   └── processors/             # Enhanced processor implementations
│       ├── __init__.py         # Processor exports
│       ├── base.py             # Base validation framework
│       ├── manga.py            # Manga processor with validation
│       ├── rename.py           # Rename processor with validation
│       └── video.py            # Video processor with validation
└── visualize/                  # User interface components
    ├── __init__.py
    ├── interactive.py          # Interactive mode
    └── progress.py             # Progress tracking
```

## Documentation Structure

```
docs/
├── configuration.md            # Configuration system documentation
├── patterns/                   # Design pattern documentation
│   └── manga_migration.md      # Manga processor migration guide
├── project_structure.md        # This file
├── tasks/                      # Task and feature documentation
├── usage_analysis.md           # Usage patterns and analysis
└── validation_framework.md     # Validation framework guide
```

## Key Components

### CLI System

- `cli.py`: Entry point using Click for command-line parsing
- `cli_patterns/__init__.py`: Dispatches commands to appropriate handlers
- `cli_handlers/`: Implementation of command handlers

### Configuration System

- `config/config_models.py`: Pydantic models for strongly-typed configuration
- `config/config_manager.py`: Manages loading config from multiple sources
- `config/config.py`: Legacy compatibility layer

### Core Logic

- `manga/manga.py`: Manga file parsing and processing
- `templates/templates.py`: Template method implementations
- `templates/processors/`: Enhanced processor implementations with validation
- `files/`: File and path handling utilities
- `result/result.py`: Result pattern for error handling

### File Processing

- `files/file_processor.py`: Base file processing logic
- `files/rename.py`: Filename renaming logic
- `files/move.py`: File movement operations
- `files/duplicates.py`: Duplicate file handling

### Validation Framework

- `templates/processors/base.py`: Core validation framework
- `templates/processors/[processor]_validator.py`: Processor-specific validators
- Provides early detection of configuration errors with helpful messages

## Data Flow

1. User invokes a command via CLI
2. `cli.py` parses arguments and passes to `cli_patterns`
3. `cli_patterns` creates appropriate command handler
4. Command handler validates inputs and creates processors
5. Processors validate parameters and apply operations
6. Processors return results (success with data or failure with errors)
7. Command handler processes results and displays output

## Testing

The `tests/` directory mirrors the structure of the main package:

```
tests/
├── __init__.py
├── cli_handlers/           # Tests for command handlers
│   ├── __init__.py
│   ├── test_direct_manga_processor.py
│   ├── test_rename_processor.py
│   ├── test_video_processor.py
│   └── test_zip_processor.py
├── common/                 # Tests for common components
│   ├── __init__.py
│   └── test_factories.py
├── files/                  # Tests for file operations
│   ├── __init__.py
│   └── test_files.py
├── manga/                  # Tests for manga processing
│   ├── __init__.py
│   ├── test_manga_handler.py
│   ├── test_manga_processor.py
│   ├── test_manga_processor_template.py
│   └── test_manga_sort.py
├── result/                 # Tests for result pattern
│   ├── __init__.py
│   └── test_result_pattern.py
├── strategies/             # Tests for strategies
│   ├── __init__.py
│   └── test_strategies.py
├── templates/              # Tests for templates
│   ├── __init__.py
│   ├── test_templates.py   # Tests for base templates
│   └── processors/         # Tests for enhanced processors
│       ├── __init__.py
│       ├── test_base.py    # Tests for validation framework
│       ├── test_manga.py   # Tests for manga processor
│       ├── test_rename.py  # Tests for rename processor
│       └── test_video.py   # Tests for video processor
├── test_cli_integration.py # End-to-end CLI tests
├── test_cli_manga_integration.py
└── test_cli_zip_integration.py
```

## Migration Status

The codebase migration is complete:

- Enhanced processors in `templates/processors/` are now the standard
- Legacy `templates_extensions.py` has been removed
- All processors use the validation framework from `templates/processors/base.py`
- See `docs/validation_framework.md` for guidance on using the validation framework