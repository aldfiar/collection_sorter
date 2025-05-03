import sys
from pathlib import Path

import click

from collection_sorter.common.logging import log_exception, console


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
def manga(ctx, **kwargs):
    """
    Sort manga collections.
    
    Organizes manga files into a standardized structure, optionally creating archives.
    
    SOURCES: One or more source directories to process.
    """
    # Use pattern-based implementation
    from collection_sorter.cli_patterns import handle_manga_command
    handle_manga_command(ctx)

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
def rename(ctx, **kwargs):
    """
    Batch rename files.
    
    Renames files based on predefined patterns, with support for various media types.
    
    SOURCES: One or more source directories or files to process.
    """
    # Use pattern-based implementation
    from collection_sorter.cli_patterns import handle_rename_command
    handle_rename_command(ctx)

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
def zip(ctx, **kwargs):
    """
    Create archives from collections.
    
    Archives folders into zip files, with options for nested archiving.
    
    SOURCES: One or more source directories to archive.
    """
    # Use pattern-based implementation
    from collection_sorter.cli_patterns import handle_zip_command
    handle_zip_command(ctx)

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
def video(ctx, **kwargs):
    """
    Rename video files.
    
    Standardizes video filenames based on patterns, supporting various formats.
    
    SOURCES: One or more source directories or files to process.
    """
    # Use pattern-based implementation
    from collection_sorter.cli_patterns import handle_video_command
    handle_video_command(ctx)

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