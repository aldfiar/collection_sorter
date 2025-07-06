"""
CLI patterns module for the Collection Sorter CLI.

This module bridges the CLI commands in cli.py with the command handlers
in the cli_handlers package. It provides functions that dispatch CLI commands
to the appropriate handlers.
"""

from typing import Any, Dict

import click

# Import handlers from cli_handlers package
from collection_sorter.cli_handlers import (
    MangaCommandHandler,
    RenameCommandHandler,
    VideoCommandHandler,
    ZipCommandHandler,
)


def handle_manga_command(ctx: click.Context) -> Dict[str, Any]:
    """
    Handle the manga command.

    Args:
        ctx: Click context with command parameters

    Returns:
        Dictionary with success status and statistics
    """
    handler = MangaCommandHandler.from_click_context(ctx)
    result = handler.handle()
    return handler.handle_result(result)


def handle_rename_command(ctx: click.Context) -> Dict[str, Any]:
    """
    Handle the rename command.

    Args:
        ctx: Click context with command parameters

    Returns:
        Dictionary with success status and statistics
    """
    handler = RenameCommandHandler.from_click_context(ctx)
    result = handler.handle()
    return handler.handle_result(result)


def handle_zip_command(ctx: click.Context) -> Dict[str, Any]:
    """
    Handle the zip command.

    Args:
        ctx: Click context with command parameters

    Returns:
        Dictionary with success status and statistics
    """
    handler = ZipCommandHandler.from_click_context(ctx)
    result = handler.handle()
    return handler.handle_result(result)


def handle_video_command(ctx: click.Context) -> Dict[str, Any]:
    """
    Handle the video command.

    Args:
        ctx: Click context with command parameters

    Returns:
        Dictionary with success status and statistics
    """
    handler = VideoCommandHandler.from_click_context(ctx)
    result = handler.handle()
    return handler.handle_result(result)
