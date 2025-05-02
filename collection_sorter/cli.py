import os
import sys
from pathlib import Path
from typing import List, Optional, Tuple

import click
from rich.console import Console

from collection_sorter.common.config import Config
from collection_sorter.common.exceptions import CollectionSorterError, ConfigurationError
from collection_sorter.common.logging import setup_logging, log_exception, console
from collection_sorter.manga.manga_sorter import MangaCollection
from collection_sorter.common.archive import ArchivedCollection

# Create global config object
config = Config()

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
@click.argument(
    "sources", 
    nargs=-1, 
    required=True, 
    type=click.Path(exists=True)
)
@add_options(common_options)
@add_options(collection_options)
def manga(sources, config, verbose, log_file, log_level, interactive, dry_run,
          destination, archive, move):
    """
    Sort manga collections.
    
    Organizes manga files into a standardized structure, optionally creating archives.
    
    SOURCES: One or more source directories to process.
    """
    try:
        # Setup logging
        setup_logging(log_file, log_level, verbose)
        
        # Update config with command line arguments
        config.update_from_args({
            "destination": destination,
            "archive": archive,
            "move": move,
            "dry_run": dry_run,
            "interactive": interactive,
            "verbose": verbose,
        })
        
        # Process manga collections
        for source in sources:
            manga = MangaCollection(
                source=source,
                destination=destination,
                archive=archive,
                move=move,
                dry_run=dry_run,
                interactive=interactive,
                verbose=verbose
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
def rename(sources, config, verbose, log_file, log_level, interactive, dry_run,
          destination, archive, move):
    """
    Batch rename files.
    
    Renames files based on predefined patterns, with support for various media types.
    
    SOURCES: One or more source directories or files to process.
    """
    try:
        # Setup logging
        setup_logging(log_file, log_level, verbose)
        
        # Update config with command line arguments
        config.update_from_args({
            "destination": destination,
            "archive": archive,
            "move": move,
            "dry_run": dry_run,
            "interactive": interactive,
            "verbose": verbose,
        })
        
        # Import here to avoid circular imports
        from collection_sorter.mass_rename import RenameCollection
        
        # Process each source
        for source in sources:
            rename_processor = RenameCollection(
                source=source,
                destination=destination,
                archive=archive,
                move=move,
                dry_run=dry_run,
                interactive=interactive,
                verbose=verbose
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
def zip(sources, config, verbose, log_file, log_level, interactive, dry_run,
        destination, archive, move):
    """
    Create archives from collections.
    
    Archives folders into zip files, with options for nested archiving.
    
    SOURCES: One or more source directories to archive.
    """
    try:
        # Setup logging
        setup_logging(log_file, log_level, verbose)
        
        # Update config with command line arguments
        config.update_from_args({
            "destination": destination,
            "archive": archive,
            "move": move,
            "dry_run": dry_run,
            "interactive": interactive,
            "verbose": verbose,
        })
        
        # Process each source
        for source in sources:
            zip_processor = ArchivedCollection(
                source_path=source,
                destination=destination,
                move_source=move,
                dry_run=dry_run,
                interactive=interactive,
                verbose=verbose
            )
            
            if Path(source).is_dir():
                if archive:  # Nested archiving
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
def video(sources, config, verbose, log_file, log_level, interactive, dry_run,
         destination):
    """
    Rename video files.
    
    Standardizes video filenames based on patterns, supporting various formats.
    
    SOURCES: One or more source directories or files to process.
    """
    try:
        # Setup logging
        setup_logging(log_file, log_level, verbose)
        
        # Update config with command line arguments
        config.update_from_args({
            "destination": destination,
            "dry_run": dry_run,
            "interactive": interactive,
            "verbose": verbose,
        })
        
        # Import here to avoid circular imports
        from collection_sorter.video_rename import VideoCollection
        
        # Process each source
        for source in sources:
            video_processor = VideoCollection(
                source=source,
                destination=destination,
                dry_run=dry_run,
                interactive=interactive,
                verbose=verbose
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
        cli()
    except Exception as e:
        console.print(f"[red]Fatal error: {str(e)}[/red]")
        sys.exit(1)

if __name__ == "__main__":
    main()