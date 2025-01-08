# Collection Sorter

A command-line tool for organizing and processing various file collections, including manga, videos, and general file renaming operations.

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

## Usage

The collection-sorter provides several commands for different file organization tasks:

### Manga Sorting

Sort and organize manga collections:

```bash
collection-sorter manga <source_directories...> [-d DESTINATION] [-a] [-m]
```

Options:
- `-d, --destination`: Specify output directory
- `-a, --archive`: Create archives of sorted collections
- `-m, --move`: Remove source files after processing

### Batch Renaming

Rename files in bulk:

```bash
collection-sorter rename <source_directories...> [-d DESTINATION] [-a] [-m]
```

Options:
- `-d, --destination`: Specify output directory
- `-a, --archive`: Create archives of renamed files
- `-m, --move`: Remove source files after processing

### Archive Creation

Create archives from collections:

```bash
collection-sorter zip <source_directories...> [-d DESTINATION] [-a] [-m]
```

Options:
- `-d, --destination`: Specify output directory
- `-a, --archive`: Create nested archives
- `-m, --move`: Remove source files after processing

### Video Renaming

Rename video files with standardized formatting:

```bash
collection-sorter video <source_directories...> [-d DESTINATION]
```

Options:
- `-d, --destination`: Specify output directory

## Examples

1. Sort manga and create archives:
```bash
collection-sorter manga ~/Downloads/manga -d ~/Manga -a
```

2. Rename video files:
```bash
collection-sorter video ~/Videos/unsorted -d ~/Videos/sorted
```

3. Create archives and remove sources:
```bash
collection-sorter zip ~/Collections -d ~/Archives -a -m
```

4. Batch rename files:
```bash
collection-sorter rename ~/Documents/messy -d ~/Documents/organized -m
```

## License

This project is licensed under the Apache License 2.0 - see the LICENSE file for details.
