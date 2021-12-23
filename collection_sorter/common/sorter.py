import multiprocessing
import threading
from functools import partial
from multiprocessing.pool import ThreadPool
from pathlib import Path

from collection_sorter.common.archive import ArchivedCollection
from collection_sorter.common.files import CollectionPath
from collection_sorter.common.move import MovableCollection


class BaseCollection(MovableCollection, ArchivedCollection):
    pass


class MultiThreadTask(object):

    def __init__(self) -> None:
        self._lock = threading.Lock()

    def execute(self, source: BaseCollection, destination: Path):
        pass


class SortExecutor(object):

    def __init__(self) -> None:
        cpus = multiprocessing.cpu_count()
        self._pool = ThreadPool(cpus)
        self._lock = threading.Lock()

    def sort(self, collection: CollectionPath, destination: str = None, task=None):
        if destination:
            destination = Path(destination)
            with self._lock:
                if not destination.exists():
                    destination.mkdir()

        directories = collection.get_folders()
        if not directories:
            directories = [collection.path]

        self._pool.map(partial(task.execute, destination=destination), directories)
