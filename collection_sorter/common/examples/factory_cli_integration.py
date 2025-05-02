"""
Example integration of Factory pattern with CLI commands.

This module demonstrates how the Factory pattern can be used
to create file processors in CLI commands.
"""

import logging
from pathlib import Path
from typing import Optional, Union, Any

import click

from collection_sorter.common.duplicates import DuplicateStrategy
from collection_sorter.common.paths import FilePath
from collection_sorter.common.factories import create_processor_from_config


# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("factory_cli")


class AppContext:
    """Application context for CLI commands."""
    
    def __init__(self):
        """Initialize the application context."""
        self.config = {
            "processor_type": "standard",
            "dry_run": False,
            "compression_level": 6,
            "duplicate_strategy": DuplicateStrategy.RENAME_NEW,
            "interactive": False
        }


@click.group()
@click.option('--dry-run', is_flag=True, help='Simulate operations without making changes')
@click.option('--interactive', is_flag=True, help='Ask before handling duplicates')
@click.option('--duplicate-strategy', type=click.Choice(['skip', 'rename_new', 'rename_existing', 'overwrite', 'move_to_duplicates', 'ask']),
              default='rename_new', help='Strategy for handling duplicates')
@click.option('--duplicates-dir', type=click.Path(), help='Directory for storing duplicates')
@click.option('--compression-level', type=int, default=6, help='ZIP compression level (0-9)')
@click.option('--use-result', is_flag=True, help='Use Result pattern for error handling')
@click.pass_context
def cli(ctx, dry_run, interactive, duplicate_strategy, duplicates_dir, compression_level, use_result):
    """Collection Sorter CLI example using Factory pattern."""
    ctx.obj = AppContext()
    
    # Update context with command-line options
    ctx.obj.config['dry_run'] = dry_run
    ctx.obj.config['interactive'] = interactive
    ctx.obj.config['duplicate_strategy'] = duplicate_strategy
    
    if duplicates_dir:
        ctx.obj.config['duplicates_dir'] = Path(duplicates_dir)
        
    ctx.obj.config['compression_level'] = compression_level
    
    if use_result:
        ctx.obj.config['processor_type'] = 'result'


@cli.command()
@click.argument('source', type=click.Path(exists=True))
@click.argument('destination', type=click.Path())
@click.pass_context
def move(ctx, source, destination):
    """Move files from source to destination."""
    # Create a processor from configuration
    processor = create_processor_from_config(
        config=ctx.obj.config,
        # Override or add specific options if needed
        # dry_run=True  # Example override
    )
    
    # Process the operation
    source_path = Path(source)
    dest_path = Path(destination)
    
    if processor.__class__.__name__ == 'ResultFileProcessor':
        # Handle with Result pattern
        result = processor.move_file(source_path, dest_path)
        if result.is_success():
            moved_path = result.unwrap()
            click.echo(f"Moved: {source_path} -> {moved_path}")
        else:
            error = result.error()
            click.echo(f"Error: {error}", err=True)
    else:
        # Handle with traditional exception handling
        try:
            moved_path = processor.move_file(source_path, dest_path)
            click.echo(f"Moved: {source_path} -> {moved_path}")
        except Exception as e:
            click.echo(f"Error: {e}", err=True)


@cli.command()
@click.argument('source', type=click.Path(exists=True))
@click.argument('destination', type=click.Path())
@click.pass_context
def copy(ctx, source, destination):
    """Copy files from source to destination."""
    # Create a processor from configuration
    processor = create_processor_from_config(
        config=ctx.obj.config
    )
    
    # Process the operation
    source_path = Path(source)
    dest_path = Path(destination)
    
    if processor.__class__.__name__ == 'ResultFileProcessor':
        # Handle with Result pattern
        result = processor.copy_file(source_path, dest_path)
        if result.is_success():
            copied_path = result.unwrap()
            click.echo(f"Copied: {source_path} -> {copied_path}")
        else:
            error = result.error()
            click.echo(f"Error: {error}", err=True)
    else:
        # Handle with traditional exception handling
        try:
            copied_path = processor.copy_file(source_path, dest_path)
            click.echo(f"Copied: {source_path} -> {copied_path}")
        except Exception as e:
            click.echo(f"Error: {e}", err=True)


@cli.command()
@click.argument('source', type=click.Path(exists=True))
@click.option('--destination', type=click.Path(), help='Optional destination directory')
@click.option('--archive-name', help='Optional name for the archive')
@click.pass_context
def archive(ctx, source, destination, archive_name):
    """Archive a directory."""
    # Create a processor from configuration
    processor = create_processor_from_config(
        config=ctx.obj.config
    )
    
    # Process the operation
    source_path = Path(source)
    dest_path = Path(destination) if destination else None
    
    if processor.__class__.__name__ == 'ResultFileProcessor':
        # Handle with Result pattern
        result = processor.archive_directory(source_path, dest_path, archive_name)
        if result.is_success():
            archive_path = result.unwrap()
            click.echo(f"Archived: {source_path} -> {archive_path}")
        else:
            error = result.error()
            click.echo(f"Error: {error}", err=True)
    else:
        # Handle with traditional exception handling
        try:
            archive_path = processor.archive_directory(source_path, dest_path, archive_name)
            click.echo(f"Archived: {source_path} -> {archive_path}")
        except Exception as e:
            click.echo(f"Error: {e}", err=True)


# Factory pattern simplifies the creation of specialized processors
class SpecializedProcessorFactory:
    """Factory for creating specialized processors for specific tasks."""
    
    @staticmethod
    def create_backup_processor(config):
        """
        Create a processor for backup operations.
        
        This processor is always in dry-run mode first to validate operations.
        """
        from copy import deepcopy
        
        # Clone the config and force dry-run
        dry_run_config = deepcopy(config)
        dry_run_config["dry_run"] = True
        
        # Create a processor with the modified config
        return create_processor_from_config(config=dry_run_config)
    
    @staticmethod
    def create_archive_processor(config):
        """
        Create a processor specialized for archiving.
        
        This processor uses maximum compression level.
        """
        from copy import deepcopy
        
        # Clone the config and set maximum compression
        archive_config = deepcopy(config)
        archive_config["compression_level"] = 9
        
        # Create a processor with the modified config
        return create_processor_from_config(config=archive_config)


@cli.command()
@click.argument('source', type=click.Path(exists=True))
@click.argument('destination', type=click.Path())
@click.pass_context
def backup(ctx, source, destination):
    """Backup directory by archiving it and then copying to destination."""
    # Create a specialized processor for backup
    backup_processor = SpecializedProcessorFactory.create_backup_processor(ctx.obj.config)
    
    # Run backup in dry-run mode first to validate
    source_path = Path(source)
    dest_path = Path(destination)
    
    click.echo("Validating backup operation (dry run)...")
    
    # Process the operation in dry run mode first
    if backup_processor.__class__.__name__ == 'ResultFileProcessor':
        # Handle with Result pattern
        result = backup_processor.archive_directory(source_path)
        if result.is_failure():
            error = result.error()
            click.echo(f"Validation error: {error}", err=True)
            return
    else:
        # Handle with traditional exception handling
        try:
            backup_processor.archive_directory(source_path)
        except Exception as e:
            click.echo(f"Validation error: {e}", err=True)
            return
    
    # If validation passed, create a real processor
    # Create a processor for the real operation
    processor = create_processor_from_config(config=ctx.obj.config)
    
    # Perform the actual backup
    if processor.__class__.__name__ == 'ResultFileProcessor':
        # Handle with Result pattern
        result = processor.archive_directory(source_path)
        if result.is_success():
            archive_path = result.unwrap()
            copy_result = processor.copy_file(archive_path, dest_path)
            if copy_result.is_success():
                click.echo(f"Backup completed: {source_path} -> {copy_result.unwrap()}")
            else:
                click.echo(f"Error copying archive: {copy_result.error()}", err=True)
        else:
            click.echo(f"Error creating archive: {result.error()}", err=True)
    else:
        # Handle with traditional exception handling
        try:
            archive_path = processor.archive_directory(source_path)
            copied_path = processor.copy_file(archive_path, dest_path)
            click.echo(f"Backup completed: {source_path} -> {copied_path}")
        except Exception as e:
            click.echo(f"Error: {e}", err=True)


if __name__ == "__main__":
    cli()