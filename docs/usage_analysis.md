# USAGE.md Analysis

## Current Commands vs Documentation

After comparing the CLI implementation in `cli.py` with the documentation in `USAGE.md`, here are the findings:

### Documented in USAGE.md and Present in Code:
- `manga` command
- `rename` command
- `zip` command
- `video` command

### Present in Code but Missing from USAGE.md:
- `generate-config` command - This command allows generating a configuration template with default values and comments, but is not mentioned in USAGE.md.

### General Options
The global options documented in USAGE.md match those in the code, but the duplicate handling options are missing from documentation:

Missing options:
- `--duplicate-strategy`: Strategy for handling duplicate files (skip, rename_new, rename_existing, overwrite, move_to_duplicates, ask)
- `--duplicates-dir`: Directory to move duplicate files to when using move_to_duplicates strategy

### Command-Specific Options

- **Video Command**: The documentation doesn't mention that the video command also supports the common collection options like archive and move.
- **Configuration**: The example configuration in USAGE.md is outdated and doesn't reflect the hierarchical structure used in the newer Pydantic-based config models.

## Suggested Updates

1. Add documentation for the `generate-config` command
2. Add the duplicate handling options to the global options list
3. Update the video command options to include archive and move
4. Update the configuration example to match the newer hierarchical Pydantic structure
5. Add information about author_folders option for manga command