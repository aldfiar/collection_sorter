import logging
import shutil
from pathlib import Path
from typing import Callable

from .files import CollectionPath

logger = logging.getLogger("move")


class MovableCollection(CollectionPath):

    def _change(
        self, new_path: Path, command: Callable[[Path, Path], None]
    ) -> CollectionPath:
        if not new_path.exists():
            new_path.mkdir(parents=True, mode=755)

        for file in self.get_files():
            source_path = file.resolve()
            destination_path = new_path.joinpath(file.name).resolve()
            command(source_path, destination_path)

        logger.info(f"{command.__name__} from: {self._path} to: {new_path}")

        return CollectionPath(new_path)

    def copy(self, new_path: Path) -> CollectionPath:
        return self._change(new_path, shutil.copy)

    def move(self, new_path: Path) -> CollectionPath:
        return self._change(new_path, shutil.move)
