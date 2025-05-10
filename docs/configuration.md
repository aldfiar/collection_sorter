# Collection Sorter Configuration Guide

Collection Sorter provides a flexible configuration system that allows you to customize its behavior through multiple methods:

1. **Command-line arguments** (highest priority)
2. **Environment variables**
3. **Configuration files** (YAML, TOML, or JSON)
4. **Default values** (lowest priority)

## Configuration File Locations

Collection Sorter will look for configuration files in the following locations (in order):

1. Path specified with the `--config` command-line option
2. `./collection_sorter.yaml` (current directory)
3. `~/.collection_sorter.yaml` (home directory)
4. `~/.config/collection_sorter/config.yaml` (config directory)

The same pattern applies for TOML (.toml) and JSON (.json) files.

## Generating a Configuration Template

You can generate a configuration template using the `generate-config` command:

```bash
collection-sorter generate-config --format yaml --output ~/.config/collection_sorter/config.yaml
```

Supported formats:
- `yaml` (default)
- `json`
- `toml`

## Configuration Structure

The configuration is organized into sections:

### Collection Configuration

Global settings for collection operations:

```yaml
collection:
  destination: ~/Organized  # Output directory for processed files
  archive: false            # Create archives of processed files
  move: false               # Remove source files after processing
  dry_run: false            # Simulate operations without making changes
```

### Logging Configuration

Control logging behavior:

```yaml
logging:
  verbose: false                  # Enable verbose output
  log_file: ~/.collection_sorter.log  # Path to log file
  log_level: INFO                 # Log level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
```

### UI Configuration

Configure user interface behavior:

```yaml
ui:
  interactive: false    # Enable interactive mode with confirmation prompts
  progress_bars: true   # Show progress bars during operations
  color_output: true    # Use colored terminal output
```

### Command-Specific Configuration

Each command can have its own specific configuration:

#### Manga Configuration

```yaml
manga:
  author_folders: false     # Organize manga by author
  template: null            # Template for manga folder naming
```

#### Video Configuration

```yaml
video:
  subtitle_extensions:       # File extensions to consider as subtitles
    - .srt
    - .sub
    - .ass
  video_extensions:         # File extensions to consider as videos
    - .mp4
    - .mkv
    - .avi
    - .mov
```

#### Rename Configuration

```yaml
rename:
  patterns: {}             # Regex patterns to use for renaming
  recursive: true          # Process subdirectories recursively
```

#### Zip Configuration

```yaml
zip:
  nested: false            # Create nested archives
  compression_level: 6     # Compression level (0-9)
```

## Using Environment Variables

You can set configuration values using environment variables prefixed with `COLLECTION_SORTER_`. 
Use double underscores (`__`) to indicate nesting levels.

Examples:

```bash
# Set destination directory
export COLLECTION_SORTER_COLLECTION__DESTINATION=~/Organized

# Enable archive creation
export COLLECTION_SORTER_COLLECTION__ARCHIVE=true

# Set log level
export COLLECTION_SORTER_LOGGING__LOG_LEVEL=DEBUG

# Configure manga options
export COLLECTION_SORTER_MANGA__AUTHOR_FOLDERS=true
```

## Command-Line Arguments

Command-line arguments have the highest priority and will override any settings from environment variables or configuration files:

```bash
collection-sorter manga ~/Downloads/manga -d ~/Manga --archive --interactive
```

## Configuration Precedence

When multiple configuration sources define the same setting, the precedence is:

1. Command-line arguments (highest priority)
2. Environment variables
3. Configuration file
4. Default values (lowest priority)

This allows you to have default settings in your configuration file but override them when needed for specific operations.

## Advanced Usage

### Command-Specific Configuration Files

You can create command-specific configuration files by using the command name as the section name in your configuration file:

```yaml
# Global settings
collection:
  destination: ~/Default

# Command-specific settings (overrides global settings for that command)
manga:
  destination: ~/Manga
  author_folders: true

zip:
  destination: ~/Archives
  nested: true
  compression_level: 9
```

### Using with Shell Aliases

For frequently used configurations, you can create shell aliases:

```bash
# Add to your .bashrc or .zshrc
alias manga-sort='collection-sorter manga --config ~/.config/collection_sorter/manga_config.yaml'
alias zip-collections='collection-sorter zip --config ~/.config/collection_sorter/zip_config.yaml'
```