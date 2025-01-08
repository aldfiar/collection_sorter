import logging
import multiprocessing
import threading
from functools import partial
from multiprocessing.pool import ThreadPool
from pathlib import Path
from typing import Optional

from .archive import ArchivedCollection
from .config import SortConfig
from .exceptions import ConfigurationError, FileOperationError, ThreadingError
from .files import CollectionPath
from .move import MovableCollection

logger = logging.getLogger(__name__)


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
            ConfigurationError: If no task is provided or configuration is invalid
            ThreadingError: If thread pool operations fail
            FileOperationError: If file operations fail
        """
        if task is None:
            raise ConfigurationError("A task must be provided")

        if not collection.exists:
            raise FileOperationError(f"Source collection does not exist: {collection}")

        if destination:
            destination = Path(destination)
            try:
                with self._lock:
                    destination.mkdir(parents=True, exist_ok=True)
            except Exception as e:
                raise FileOperationError(f"Failed to create destination directory: {str(e)}") from e

        directories = collection.get_folders() or [collection.path]
        logger.info(f"Starting sort operation with {len(directories)} directories")

        try:
            results = self._pool.map_async(
                partial(task.execute, destination=destination), 
                directories
            )
            results.wait(timeout=3600)  # 1 hour timeout
            if not results.successful():
                raise ThreadingError("Sort operation failed to complete successfully")
        except Exception as e:
            raise ThreadingError(f"Thread pool operation failed: {str(e)}") from e
        finally:
            self._pool.close()
            self._pool.join()
            
        logger.info("Sort operation completed successfully")
