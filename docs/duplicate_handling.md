# Duplicate File Handling

Collection Sorter provides a flexible system for handling duplicate files during operations like moving, copying, renaming, and archiving.

## Duplicate Handling Strategies

You can configure how the application handles duplicate files using one of these strategies:

| Strategy | Description |
|----------|-------------|
| `skip` | Skip the file, don't process it |
| `rename_new` | Rename the new file (default) |
| `rename_existing` | Rename the existing file |
| `overwrite` | Overwrite the existing file |
| `move_to_duplicates` | Move to a duplicates folder |
| `ask` | Ask the user interactively |

## Configuration

You can set the duplicate handling strategy in your configuration file:

```yaml
collection:
  duplicate_strategy: rename_new  # Default strategy
  duplicates_dir: ~/Duplicates    # Directory for duplicates when using move_to_duplicates
```

## Command Line Options

You can set the duplicate handling strategy via command line:

```bash
collection-sorter manga ~/Downloads/manga -d ~/Manga --duplicate-strategy move_to_duplicates
```

You can also enable interactive mode to be prompted for each duplicate:

```bash
collection-sorter manga ~/Downloads/manga -d ~/Manga --interactive
```

## Environment Variables

You can set the duplicate handling strategy via environment variables:

```bash
export COLLECTION_SORTER_COLLECTION__DUPLICATE_STRATEGY=rename_existing
export COLLECTION_SORTER_COLLECTION__DUPLICATES_DIR=~/Duplicates
```

## Interactive Duplicate Resolution

When using the `ask` strategy or running in interactive mode, Collection Sorter will prompt you for each duplicate file with the following options:

- **s**: Skip (don't process this file)
- **n**: Rename new file
- **e**: Rename existing file
- **o**: Overwrite existing file
- **d**: Move to duplicates folder
- **a**: Apply this choice to all duplicates

This allows you to handle each duplicate file individually, or choose a strategy to apply to all duplicates.

## Programmatic Usage

If you're using Collection Sorter as a library, you can create and configure a `DuplicateHandler` instance:

```python
from collection_sorter.files.duplicates import DuplicateHandler, DuplicateStrategy
from collection_sorter.files.move import move_file

# Create a duplicate handler with specific strategy
handler = DuplicateHandler(
    strategy=DuplicateStrategy.MOVE_TO_DUPLICATES,
    duplicates_dir="~/Duplicates",
    interactive=False,
    dry_run=False
)

# Use the handler with file operations
move_file("source.txt", "destination.txt", duplicate_handler=handler)
```

## Examples

### Creating a Duplicates Directory

If you're using the `move_to_duplicates` strategy, Collection Sorter will automatically create a duplicates directory if it doesn't exist:

```yaml
collection:
  duplicate_strategy: move_to_duplicates
  duplicates_dir: ~/Documents/Duplicates
```

If `duplicates_dir` is not specified, it will create a `duplicates` subdirectory in the destination directory.

### Automatic Naming of Duplicate Files

When renaming duplicate files (using `rename_new` or `rename_existing` strategies), Collection Sorter adds a `_duplicate_[UUID]` suffix to the filename:

```
original.txt -> original_duplicate_a1b2c3d4.txt
```

This ensures unique filenames even with multiple duplicates.

### Overwriting Files

The `overwrite` strategy will replace existing files without confirmation. Use with caution!

```yaml
collection:
  duplicate_strategy: overwrite
```

### Skipping Duplicates

The `skip` strategy will leave existing files untouched and skip processing duplicates:

```yaml
collection:
  duplicate_strategy: skip
```