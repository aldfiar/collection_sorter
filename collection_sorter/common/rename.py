import logging
from pathlib import Path

logger = logging.getLogger('rename')


def linux_rename_function(path: Path):
    return rename_function(path, " ", "_")


def windows_rename_function(path: Path):
    return rename_function(path, "_", " ")


def rename_function(path: Path, symbolFrom: str, symbolTo: str):
    name = path.name
    linux_name = name.replace(symbolFrom, symbolTo)
    new_path = path.parent.joinpath(linux_name)
    logger.debug(f'Change name for file {path} to {new_path}')
    return new_path
