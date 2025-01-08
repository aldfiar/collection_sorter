import multiprocessing
import threading
from functools import partial
from multiprocessing.pool import ThreadPool
from pathlib import Path
from typing import Optional

from .archive import ArchivedCollection
from .config import SortConfig
from .files import CollectionPath
from .move import MovableCollection


class BaseCollection(MovableCollection, ArchivedCollection):
    pass


class MultiThreadTask:
    """Base class for multi-threaded tasks."""

    def __init__(self, config: SortConfig) -> None:
        self._lock = threading.Lock()
        self._config = config

    def execute(
        self, source: BaseCollection, destination: Optional[Path] = None
    ) -> None:
        """Execute the task on the given source.

        Args:
            source: The collection to process
            destination: Optional destination path, overrides config
        """
        raise NotImplementedError("Subclasses must implement execute()")


class SortExecutor:
    """Executes sorting tasks using a thread pool."""

    def __init__(self, thread_count: int = 0) -> None:
        """Initialize the executor.

        Args:
            thread_count: Number of threads to use. 0 means use CPU count.
        """
        self._thread_count = thread_count or multiprocessing.cpu_count()
        self._pool = ThreadPool(self._thread_count)
        self._lock = threading.Lock()

    def sort(
        self,
        collection: CollectionPath,
        destination: Optional[Path] = None,
        task: Optional[MultiThreadTask] = None,
    ) -> None:
        """Sort the collection using the given task.

        Args:
            collection: The collection to sort
            destination: Optional destination path
            task: The task to execute

        Raises:
            ValueError: If no task is provided
        """
        if task is None:
            raise ValueError("A task must be provided")

        if destination:
            destination = Path(destination)
            with self._lock:
                destination.mkdir(parents=True, exist_ok=True)

        directories = collection.get_folders() or [collection.path]

        try:
            self._pool.map(partial(task.execute, destination=destination), directories)
        finally:
            self._pool.close()
