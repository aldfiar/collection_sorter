import logging
from pathlib import Path

logger = logging.getLogger("rename")


def linux_rename_function(path: Path) -> Path:
    """
    Rename a file by replacing spaces with underscores.

    :param path: The path to the file to rename.
    :return: The new path of the renamed file.
    """
    return rename_function(path, " ", "_")


def windows_rename_function(path: Path) -> Path:
    """
    Rename a file by replacing underscores with spaces.

    :param path: The path to the file to rename.
    :return: The new path of the renamed file.
    """
    return rename_function(path, "_", " ")


def rename_function(path: Path, symbol_from: str, symbol_to: str) -> Path:
    """
    Rename a file by replacing occurrences of a symbol with another symbol.

    :param path: The path to the file to rename.
    :param symbol_from: The symbol to replace.
    :param symbol_to: The symbol to replace with.
    :return: The new path of the renamed file.
    """
    name = path.name
    linux_name = name.replace(symbol_from, symbol_to)
    new_path = path.parent / linux_name
    logger.debug(f"Change name for file {path} to {new_path}")
    return new_path
