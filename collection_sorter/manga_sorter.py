import logging
import multiprocessing
import shutil
import threading
from multiprocessing.pool import ThreadPool
from pathlib import Path
from typing import Callable

from collection_sorter.files import get_folders
from collection_sorter.manga import MangaExtractor
from collection_sorter.move import Mover
from collection_sorter.zipper import Zipper

logger = logging.getLogger('sorter')


class Sorter(object):

    def __init__(self) -> None:
        cpus = multiprocessing.cpu_count()
        self._pool = ThreadPool(cpus)


class MangaSorter(Sorter):

    def __init__(self) -> None:
        super().__init__()
        self.extractor = MangaExtractor()
        self.lock = threading.Lock()

    def _directory_action(self, name: str, source: Path, destination: Path, zip_files,
                          remove_original):
        try:
            if zip_files:
                zip_file = Zipper.zip_directory(source, destination, override_name=name)
                if zip_file.exists() and zip_file.stat().st_size > 0 and remove_original:
                    shutil.rmtree(str(source))
            else:
                file_destination = destination.joinpath(name)
                if remove_original:
                    Mover.move(source, file_destination)
                else:
                    Mover.copy(source, file_destination)
        except Exception as e:
            logger.error("Directory action failed with: {}".format(e))

    def _task(self, path: Path, destination: Path, template_function: Callable, zip_files: bool,
              remove_original: bool):
        has_author = False
        info = self.extractor.extract(path)
        if 'author' in info:
            has_author = True
            new_root = info['author']
            task_destination = destination.joinpath(new_root)
            with self.lock:
                if not task_destination.exists():
                    task_destination.mkdir()
        else:
            task_destination = destination

        if len(info) == 1:
            if has_author:
                directories = get_folders(path)
                for directory in directories:
                    updated = dict()
                    updated.update(**info)
                    updated["name"] = directory.name
                    new_name = template_function(updated)
                    self._directory_action(new_name, source=directory, destination=task_destination,
                                           zip_files=zip_files,
                                           remove_original=remove_original)
            else:
                # for monthly comics with out author
                index = 0
                find_digit = False
                name = info['name']
                for character in name:
                    if character.isdigit():
                        find_digit = True
                        break
                    index += 1
                if find_digit:
                    author = name[0:index - 1].strip()
                else:
                    author = name.strip()
                info['author'] = author
                new_root = author
                with self.lock:
                    task_destination = destination.joinpath(new_root)
                    if not task_destination.exists():
                        task_destination.mkdir()
                new_name = template_function(info)
                self._directory_action(new_name, source=path, destination=task_destination, zip_files=zip_files,
                                       remove_original=remove_original)
        else:
            new_name = template_function(info)
            self._directory_action(new_name, source=path, destination=task_destination, zip_files=zip_files,
                                   remove_original=remove_original)

    def sort(self, folder: Path, destination: Path, template_function: Callable, zip_files=False,
             remove_original=False):
        with self.lock:
            if not destination.exists():
                destination.mkdir()

        directories = get_folders(folder)

        def create_tasks(directory_path: Path):
            return self._task(path=directory_path, destination=destination, template_function=template_function,
                              zip_files=zip_files, remove_original=remove_original)

        self._pool.map(create_tasks, directories)
