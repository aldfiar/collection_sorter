import os
import sys
from pathlib import Path
from typing import List, Optional, Tuple, Dict, Any

import click
from rich.console import Console

from collection_sorter.common.exceptions import CollectionSorterError, ConfigurationError
from collection_sorter.common.logging import setup_logging, log_exception, console
from collection_sorter.common.config_manager import config_manager
from collection_sorter.manga.manga_sorter import MangaCollection
from collection_sorter.common.archive import ArchivedCollection

def print_version(ctx, param, value):
    """Print the version and exit"""
    if not value or ctx.resilient_parsing:
        return
    from importlib.metadata import version
    try:
        ver = version("collection_sorter")
    except:
        ver = "0.1.1"  # Fallback version
    click.echo(f"Collection Sorter {ver}")
    ctx.exit()

# Common command options
common_options = [
    click.option(
        "--config", 
        help="Path to config file", 
        type=click.Path(exists=True, dir_okay=False)
    ),
    click.option(
        "--verbose", "-v", 
        is_flag=True, 
        help="Enable verbose output"
    ),
    click.option(
        "--log-file", 
        help="Path to log file", 
        type=click.Path(dir_okay=False)
    ),
    click.option(
        "--log-level", 
        help="Log level", 
        type=click.Choice(["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"], 
                          case_sensitive=False)
    ),
    click.option(
        "--interactive", "-i", 
        is_flag=True, 
        help="Enable interactive mode with confirmation prompts"
    ),
    click.option(
        "--dry-run", 
        is_flag=True, 
        help="Simulate operations without making changes"
    ),
    click.option(
        "--duplicate-strategy", 
        help="Strategy for handling duplicate files", 
        type=click.Choice(["skip", "rename_new", "rename_existing", "overwrite", "move_to_duplicates", "ask"], 
                          case_sensitive=False)
    ),
    click.option(
        "--duplicates-dir", 
        help="Directory to move duplicate files to", 
        type=click.Path(file_okay=False)
    ),
]

# Collection processing options
collection_options = [
    click.option(
        "--destination", "-d", 
        help="Output directory", 
        type=click.Path(file_okay=False)
    ),
    click.option(
        "--archive", "-a", 
        is_flag=True, 
        help="Create archives of processed files"
    ),
    click.option(
        "--move", "-m", 
        is_flag=True, 
        help="Remove source files after processing"
    ),
]

def add_options(options):
    """Add multiple options to a command"""
    def _add_options(func):
        for option in reversed(options):
            func = option(func)
        return func
    return _add_options

@click.group()
@click.option(
    "--version", 
    is_flag=True, 
    callback=print_version,
    expose_value=False, 
    is_eager=True, 
    help="Show version and exit"
)
def cli():
    """Collection Sorter - Organize and process various file collections."""
    pass

@cli.command()
@click.option(
    "--format", "-f",
    type=click.Choice(["yaml", "json", "toml"]),
    default="yaml",
    help="Output format for the configuration template",
)
@click.option(
    "--output", "-o",
    type=click.Path(file_okay=True, dir_okay=False),
    help="Output file for the configuration template. If not specified, prints to stdout.",
)
def generate_config(format, output):
    """
    Generate a configuration file template.
    
    Creates a configuration file template with default values and comments.
    """
    try:
        # Generate template
        template = config_manager.generate_template(format)
        
        if output:
            # Write to file
            output_path = Path(output)
            output_path.parent.mkdir(parents=True, exist_ok=True)
            with open(output_path, "w") as f:
                f.write(template)
            console.print(f"[green]Configuration template written to {output_path}[/green]")
        else:
            # Print to stdout
            click.echo(template)
            
    except Exception as e:
        log_exception(e)
        console.print(f"[red]Error generating configuration template: {str(e)}[/red]")
        sys.exit(1)

@cli.command()
@click.argument(
    "sources", 
    nargs=-1, 
    required=True, 
    type=click.Path(exists=True)
)
@add_options(common_options)
@add_options(collection_options)
@click.pass_context
def manga(ctx, sources, config, verbose, log_file, log_level, interactive, dry_run,
          destination, archive, move):
    """
    Sort manga collections.
    
    Organizes manga files into a standardized structure, optionally creating archives.
    
    SOURCES: One or more source directories to process.
    """
    try:
        # Apply Click context to configuration manager
        config_manager.apply_click_context(ctx)
        
        # Get command-specific configuration
        cmd_config = config_manager.get_command_config("manga")
        
        # Setup logging using configuration
        logging_config = config_manager.config.logging
        setup_logging(
            log_file=logging_config.log_file, 
            log_level=logging_config.log_level, 
            verbose=logging_config.verbose
        )
        
        # Process manga collections
        for source in sources:
            manga = MangaCollection(
                source=source,
                destination=cmd_config.get("destination"),
                archive=cmd_config.get("archive", False),
                move=cmd_config.get("move", False),
                dry_run=cmd_config.get("dry_run", False),
                interactive=config_manager.config.ui.interactive,
                verbose=logging_config.verbose,
                author_folders=config_manager.config.manga.author_folders
            )
            result = manga.process_single_source(source)
            
            if result.get("success", False):
                console.print(f"[green]Successfully processed {source}[/green]")
            else:
                error = result.get("error", "Unknown error")
                console.print(f"[red]Error processing {source}: {error}[/red]")
                
    except ConfigurationError as e:
        console.print(f"[red]Configuration error: {str(e)}[/red]")
        sys.exit(e.exit_code)
    except CollectionSorterError as e:
        console.print(f"[red]Error: {str(e)}[/red]")
        sys.exit(e.exit_code)
    except Exception as e:
        log_exception(e)
        console.print(f"[red]Unexpected error: {str(e)}[/red]")
        sys.exit(1)

@cli.command()
@click.argument(
    "sources", 
    nargs=-1, 
    required=True, 
    type=click.Path(exists=True)
)
@add_options(common_options)
@add_options(collection_options)
@click.pass_context
def rename(ctx, sources, config, verbose, log_file, log_level, interactive, dry_run,
          destination, archive, move):
    """
    Batch rename files.
    
    Renames files based on predefined patterns, with support for various media types.
    
    SOURCES: One or more source directories or files to process.
    """
    try:
        # Apply Click context to configuration manager
        config_manager.apply_click_context(ctx)
        
        # Get command-specific configuration
        cmd_config = config_manager.get_command_config("rename")
        
        # Setup logging using configuration
        logging_config = config_manager.config.logging
        setup_logging(
            log_file=logging_config.log_file, 
            log_level=logging_config.log_level, 
            verbose=logging_config.verbose
        )
        
        # Import here to avoid circular imports
        from collection_sorter.mass_rename import RenameCollection
        
        # Process each source
        for source in sources:
            rename_processor = RenameCollection(
                source=source,
                destination=cmd_config.get("destination"),
                archive=cmd_config.get("archive", False),
                move=cmd_config.get("move", False),
                dry_run=cmd_config.get("dry_run", False),
                interactive=config_manager.config.ui.interactive,
                verbose=logging_config.verbose,
                recursive=config_manager.config.rename.recursive,
                patterns=config_manager.config.rename.patterns
            )
            result = rename_processor.process_single_source(source)
            
            if result.get("success", False):
                console.print(f"[green]Successfully renamed {source}[/green]")
            else:
                error = result.get("error", "Unknown error")
                console.print(f"[red]Error renaming {source}: {error}[/red]")
                
    except ConfigurationError as e:
        console.print(f"[red]Configuration error: {str(e)}[/red]")
        sys.exit(e.exit_code)
    except CollectionSorterError as e:
        console.print(f"[red]Error: {str(e)}[/red]")
        sys.exit(e.exit_code)
    except Exception as e:
        log_exception(e)
        console.print(f"[red]Unexpected error: {str(e)}[/red]")
        sys.exit(1)

@cli.command()
@click.argument(
    "sources", 
    nargs=-1, 
    required=True, 
    type=click.Path(exists=True)
)
@add_options(common_options)
@add_options(collection_options)
@click.pass_context
def zip(ctx, sources, config, verbose, log_file, log_level, interactive, dry_run,
        destination, archive, move, duplicate_strategy, duplicates_dir):
    """
    Create archives from collections.
    
    Archives folders into zip files, with options for nested archiving.
    
    SOURCES: One or more source directories to archive.
    """
    try:
        # Apply Click context to configuration manager
        config_manager.apply_click_context(ctx)
        
        # Get command-specific configuration
        cmd_config = config_manager.get_command_config("zip")
        
        # Setup logging using configuration
        logging_config = config_manager.config.logging
        setup_logging(
            log_file=logging_config.log_file, 
            log_level=logging_config.log_level, 
            verbose=logging_config.verbose
        )
        
        # Create duplicate handler from configuration
        from collection_sorter.common.duplicates import DuplicateHandler
        
        # Use command-line arguments if provided, otherwise use config values
        dup_strategy = duplicate_strategy or config_manager.config.collection.duplicate_strategy
        dup_dir = duplicates_dir or config_manager.config.collection.duplicates_dir
        
        duplicate_handler = DuplicateHandler(
            strategy=dup_strategy,
            duplicates_dir=dup_dir,
            interactive=interactive or config_manager.config.ui.interactive,
            dry_run=dry_run or cmd_config.get("dry_run", False)
        )
        
        # Process each source
        for source in sources:
            zip_processor = ArchivedCollection(
                path=source,
                destination=cmd_config.get("destination"),
                move_source=cmd_config.get("move", False),
                dry_run=cmd_config.get("dry_run", False),
                interactive=config_manager.config.ui.interactive,
                verbose=logging_config.verbose,
                compression_level=config_manager.config.zip.compression_level,
                duplicate_handler=duplicate_handler
            )
            
            if Path(source).is_dir():
                # Use nested setting from zip config if available
                nested = archive if archive is not None else config_manager.config.zip.nested
                
                if nested:  # Nested archiving
                    result = zip_processor.archive_folders()
                else:
                    result = zip_processor.archive_directory()
                
                if result:
                    console.print(f"[green]Successfully archived {source}[/green]")
                else:
                    console.print(f"[red]Error archiving {source}[/red]")
            else:
                console.print(f"[yellow]Skipping file {source} - only directories can be archived[/yellow]")
                
    except ConfigurationError as e:
        console.print(f"[red]Configuration error: {str(e)}[/red]")
        sys.exit(e.exit_code)
    except CollectionSorterError as e:
        console.print(f"[red]Error: {str(e)}[/red]")
        sys.exit(e.exit_code)
    except Exception as e:
        log_exception(e)
        console.print(f"[red]Unexpected error: {str(e)}[/red]")
        sys.exit(1)

@cli.command()
@click.argument(
    "sources", 
    nargs=-1, 
    required=True, 
    type=click.Path(exists=True)
)
@add_options(common_options)
@click.option(
    "--destination", "-d", 
    help="Output directory", 
    type=click.Path(file_okay=False)
)
@click.pass_context
def video(ctx, sources, config, verbose, log_file, log_level, interactive, dry_run,
         destination):
    """
    Rename video files.
    
    Standardizes video filenames based on patterns, supporting various formats.
    
    SOURCES: One or more source directories or files to process.
    """
    try:
        # Apply Click context to configuration manager
        config_manager.apply_click_context(ctx)
        
        # Get command-specific configuration
        cmd_config = config_manager.get_command_config("video")
        
        # Setup logging using configuration
        logging_config = config_manager.config.logging
        setup_logging(
            log_file=logging_config.log_file, 
            log_level=logging_config.log_level, 
            verbose=logging_config.verbose
        )
        
        # Import here to avoid circular imports
        from collection_sorter.video_rename import VideoCollection
        
        # Process each source
        for source in sources:
            video_processor = VideoCollection(
                source=source,
                destination=cmd_config.get("destination"),
                dry_run=cmd_config.get("dry_run", False),
                interactive=config_manager.config.ui.interactive,
                verbose=logging_config.verbose,
                video_extensions=config_manager.config.video.video_extensions,
                subtitle_extensions=config_manager.config.video.subtitle_extensions
            )
            result = video_processor.process_single_source(source)
            
            if result.get("success", False):
                console.print(f"[green]Successfully processed video files in {source}[/green]")
            else:
                error = result.get("error", "Unknown error")
                console.print(f"[red]Error processing {source}: {error}[/red]")
                
    except ConfigurationError as e:
        console.print(f"[red]Configuration error: {str(e)}[/red]")
        sys.exit(e.exit_code)
    except CollectionSorterError as e:
        console.print(f"[red]Error: {str(e)}[/red]")
        sys.exit(e.exit_code)
    except Exception as e:
        log_exception(e)
        console.print(f"[red]Unexpected error: {str(e)}[/red]")
        sys.exit(1)

def main():
    """Entry point for the application"""
    try:
        # Initialize the config manager
        config_manager.load_configuration()
        
        # Run the CLI
        cli()
    except Exception as e:
        log_exception(e)
        console.print(f"[red]Fatal error: {str(e)}[/red]")
        sys.exit(1)

if __name__ == "__main__":
    main()