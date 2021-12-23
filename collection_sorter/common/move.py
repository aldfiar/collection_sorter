import logging
import shutil
from pathlib import Path
from typing import Callable

from collection_sorter.common.files import CollectionPath

logger = logging.getLogger('move')


class MovableCollection(CollectionPath):

    def _change(self, new_path: Path, command: Callable) -> CollectionPath:
        if not new_path.exists():
            new_path.mkdir(parents=True, mode=755)

        files = self.get_files()
        for file in files:
            source_path = str(file.absolute())
            destination_path = str(new_path.joinpath(file.name).absolute())
            command(source_path, destination_path)

        logger.info(f'{command} from: {self._path} to: {new_path}')

        return CollectionPath(new_path)

    def copy(self, new_path: Path) -> CollectionPath:
        return self._change(new_path, shutil.copy)

    def move(self, new_path: Path) -> CollectionPath:
        return self._change(new_path, shutil.move)
