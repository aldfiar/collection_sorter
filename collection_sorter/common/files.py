import shutil
from pathlib import Path
from typing import List, Union, Set, Iterator, Callable


class CollectionPath(object):
    def __init__(self, path: Union[Path, str]) -> None:
        self._path = Path(path).expanduser().resolve(strict=True)

    @property
    def path(self):
        return self._path

    def _recursive_collect(self, path: Path) -> Set[Path]:
        cur_files = self._get_files(path)
        unique_files = set(cur_files)
        folders = self._get_folders(path)
        for folder in folders:
            result = self._recursive_collect(folder)
            unique_files = unique_files.union(result)
        return unique_files

    @classmethod
    def _get_elements(cls, path: Path, condition: Callable) -> List[Path]:
        for f in path.iterdir():
            if condition(f):
                yield f

    def _get_files(self, path) -> Iterator[Path]:
        return self._get_elements(path, lambda x: x.is_file())

    def _get_folders(self, path) -> Iterator[Path]:
        return self._get_elements(path, lambda x: x.is_dir())

    def collect_all(self) -> Set[Path]:
        return self._recursive_collect(self._path)

    def get_folders(self) -> List[Path]:
        folders = list(self._get_folders(self._path))
        return folders

    def get_files(self) -> List[Path]:
        files = list(self._get_files(self._path))
        return files

    @property
    def exist(self):
        return self._path.exists()

    def delete(self):
        shutil.rmtree(str(self._path))

    def map(self, function):
        files = self.get_files()
        for file in files:
            source_path = str(file.absolute())
            function(source_path)

    def __str__(self) -> str:
        return str(self._path)
