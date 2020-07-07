import logging
import shutil
from pathlib import Path

from collection_sorter.files import get_content

logger = logging.getLogger('move')


class Mover(object):
    @classmethod
    def full_path(cls, path: Path) -> str:
        return str(path.absolute())

    @classmethod
    def copy(cls, file_path: Path, new_path: Path):
        if not new_path.exists():
            new_path.mkdir(parents=True, mode=755)

        logger.info(f'Copy file {file_path} to {new_path}')

        files = get_content(file_path)
        for file in files:
            fp = cls.full_path(file)
            dest = cls.full_path(new_path.joinpath(file.name))
            shutil.copy(fp, dest)

    @classmethod
    def move(cls, file_path: Path, new_path: Path):
        if not new_path.exists():
            new_path.mkdir(parents=True, mode=755)

        logger.info(f'Move file {file_path} to {new_path}')

        files = get_content(file_path)
        for file in files:
            fp = cls.full_path(file)
            dest = cls.full_path(new_path.joinpath(file.name))
            shutil.move(fp, dest)
