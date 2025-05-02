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
git clone https://github.com/yourusername/collection-sorter.git
cd collection-sorter

# Install with Poetry
poetry install

# Activate the virtual environment
poetry shell
```

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

### Batch Renaming

Rename files in bulk:

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

## Configuration

You can configure Collection Sorter through:

1. **Command-line Arguments**: Highest priority
2. **Environment Variables**: Prefixed with `COLLECTION_SORTER_`
3. **Config Files**: YAML format in:
   - `./collection_sorter.yaml` (current directory)
   - `~/.collection_sorter.yaml` (home directory)
   - `~/.config/collection_sorter/config.yaml` (config directory)

Example config file:
```yaml
# collection_sorter.yaml
destination: ~/Organized
archive: true
move: false
dry_run: false
interactive: true
verbose: false
log_file: ~/.collection_sorter.log
log_level: INFO
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

## License

This project is licensed under the Apache License 2.0 - see the LICENSE file for details.
