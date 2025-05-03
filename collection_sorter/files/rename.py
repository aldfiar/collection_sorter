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


from collection_sorter.common.exceptions import FileOperationError

def rename_function(path: Path, symbol_from: str, symbol_to: str) -> Path:
    """
    Rename a file by replacing occurrences of a symbol with another symbol.

    Args:
        path: The path to the file to rename.
        symbol_from: The symbol to replace.
        symbol_to: The symbol to replace with.

    Returns:
        Path: The new path of the renamed file.

    Raises:
        FileOperationError: If the path doesn't exist or renaming fails.
    """
    if not path.exists():
        raise FileOperationError(f"Source path does not exist: {path}")

    try:
        name = path.name
        linux_name = name.replace(symbol_from, symbol_to)
        new_path = path.parent / linux_name
        
        if new_path.exists():
            logger.warning(f"Destination path already exists: {new_path}")
            
        logger.debug(f"Renaming file from {path} to {new_path}")
        return new_path
    except Exception as e:
        raise FileOperationError(f"Failed to rename {path}: {str(e)}") from e
