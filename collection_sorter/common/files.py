import logging
import shutil
from pathlib import Path
from typing import Callable, Iterator, List, Set, Union

logger = logging.getLogger("files")


class CollectionPath:
    """
    A class to handle file and folder operations on a given path.

    :param path: The path to the directory or file.
    """

    def __init__(self, path: Union[Path, str]) -> None:
        self._path = Path(path).expanduser().resolve(strict=True)

    @property
    def path(self) -> Path:
        """
        Get the resolved path.

        :return: The resolved path.
        """
        return self._path

    def _recursive_collect(self, path: Path) -> Set[Path]:
        """
        Recursively collect all files and folders in the given path.

        :param path: The path to start collecting from.
        :return: A set of unique paths.
        """
        cur_files = self._get_files(path)
        unique_files = set(cur_files)
        folders = self._get_folders(path)
        for folder in folders:
            result = self._recursive_collect(folder)
            unique_files.update(result)
        return unique_files

    @classmethod
    def _get_elements(cls, path: Path, condition: Callable) -> Iterator[Path]:
        """
        Get elements that match the given condition.

        :param path: The path to search in.
        :param condition: A callable that returns True if an element matches the condition.
        :return: An iterator of matching elements.
        """
        for f in path.iterdir():
            if condition(f):
                yield f

    def _get_files(self, path: Path) -> Iterator[Path]:
        """
        Get all files in the given path.

        :param path: The path to search in.
        :return: An iterator of file paths.
        """
        return self._get_elements(path, lambda x: x.is_file())

    def _get_folders(self, path: Path) -> Iterator[Path]:
        """
        Get all folders in the given path.

        :param path: The path to search in.
        :return: An iterator of folder paths.
        """
        return self._get_elements(path, lambda x: x.is_dir())

    def collect_all(self) -> Set[Path]:
        """
        Collect all files and folders recursively.

        :return: A set of unique file and folder paths.
        """
        return self._recursive_collect(self._path)

    def get_folders(self) -> List[Path]:
        """
        Get all folders in the current path.

        :return: A list of folder paths.
        """
        return list(self._get_folders(self._path))

    def get_files(self) -> List[Path]:
        """
        Get all files in the current path.

        :return: A list of file paths.
        """
        return list(self._get_files(self._path))

    @property
    def exists(self) -> bool:
        """
        Check if the path exists.

        :return: True if the path exists, False otherwise.
        """
        return self._path.exists()

    def delete(self):
        """
        Delete the directory and all its contents recursively.
        """
        shutil.rmtree(str(self._path))

    def map(self, function: Callable[[str], None]):
        """
        Apply a function to each file in the current path.

        :param function: A callable that takes a file path as an argument.
        """
        files = self.get_files()
        for file in files:
            source_path = str(file.absolute())
            function(source_path)

    def __str__(self) -> str:
        """
        Get the string representation of the path.

        :return: The string representation of the path.
        """
        return str(self._path)
