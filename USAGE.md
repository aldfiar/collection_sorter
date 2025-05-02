# Collection Sorter Usage Guide

This guide provides detailed information on how to use Collection Sorter effectively.

## Command Reference

### Global Options

These options are available for all commands:

```
--config PATH                Path to config file
-v, --verbose                Enable verbose output
--log-file PATH              Path to log file
--log-level [DEBUG|INFO|WARNING|ERROR|CRITICAL]
                            Log level
-i, --interactive            Enable interactive mode with confirmation prompts
--dry-run                    Simulate operations without making changes
--version                    Show version and exit
--help                       Show help message and exit
```

### Manga Sorting Command

```
collection-sorter manga [OPTIONS] SOURCES...
```

The manga command organizes manga collections into a standardized structure, detecting series names, chapters, and volumes.

**Options:**
- `-d, --destination PATH`: Output directory
- `-a, --archive`: Create archives of sorted collections
- `-m, --move`: Remove source files after processing

**Example:**
```bash
collection-sorter manga ~/Downloads/manga -d ~/Manga -a -i
```

This command will:
1. Process all manga in the `~/Downloads/manga` directory
2. Sort and organize them into the `~/Manga` directory
3. Create archives for each series
4. Use interactive mode to confirm actions

### Batch Renaming Command

```
collection-sorter rename [OPTIONS] SOURCES...
```

The rename command renames files based on predefined patterns, with support for various media types.

**Options:**
- `-d, --destination PATH`: Output directory
- `-a, --archive`: Create archives of renamed files
- `-m, --move`: Remove source files after processing

**Example:**
```bash
collection-sorter rename ~/Music/Unsorted -d ~/Music/Organized --dry-run
```

This command will:
1. Identify files in `~/Music/Unsorted`
2. Show what renames would be performed without making changes (dry run)
3. Preview the reorganization into `~/Music/Organized`

### Archive Creation Command

```
collection-sorter zip [OPTIONS] SOURCES...
```

The zip command creates archives from collections, with options for nested archiving.

**Options:**
- `-d, --destination PATH`: Output directory
- `-a, --archive`: Create nested archives
- `-m, --move`: Remove source files after processing

**Example:**
```bash
collection-sorter zip ~/Documents/Projects -d ~/Backups -a -m
```

This command will:
1. Create ZIP archives for all directories in `~/Documents/Projects`
2. Store the archives in `~/Backups`
3. Create nested archives (with `-a` flag)
4. Remove the original source files after successful archiving

### Video Renaming Command

```
collection-sorter video [OPTIONS] SOURCES...
```

The video command standardizes video filenames based on patterns, supporting various formats.

**Options:**
- `-d, --destination PATH`: Output directory

**Example:**
```bash
collection-sorter video ~/Videos/Shows -v
```

This command will:
1. Process video files in `~/Videos/Shows`
2. Standardize their filenames according to recognized patterns
3. Show verbose output during processing

## Advanced Usage

### Configuration Files

Create a configuration file to store default settings:

```yaml
# ~/.collection_sorter.yaml
destination: ~/Organized
archive: true
move: false
dry_run: false
interactive: true
verbose: false
log_file: ~/.collection_sorter.log
log_level: INFO
```

### Environment Variables

You can also set configuration through environment variables prefixed with `COLLECTION_SORTER_`:

```bash
export COLLECTION_SORTER_DESTINATION=~/Organized
export COLLECTION_SORTER_ARCHIVE=true
export COLLECTION_SORTER_MOVE=false
export COLLECTION_SORTER_INTERACTIVE=true
```

### Logging

Configure detailed logging to a file:

```bash
collection-sorter manga ~/Downloads/manga --log-file ~/logs/collection_sorter.log --log-level DEBUG
```

### Interactive Mode with Progress Bars

For the best user experience with rich output:

```bash
collection-sorter rename ~/Downloads/various -i -v
```

This will:
1. Show rich progress bars during processing
2. Ask for confirmation before making changes
3. Provide detailed output during operation

### Dry Run Mode

Preview changes without modifying files:

```bash
collection-sorter zip ~/Important/Documents --dry-run
```

This allows you to:
1. See exactly what would be archived
2. Verify the operations before committing to them
3. Ensure no unexpected changes will occur