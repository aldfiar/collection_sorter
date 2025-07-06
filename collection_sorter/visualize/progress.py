from contextlib import contextmanager
from typing import Iterable, Optional, TypeVar

from rich.progress import (
    BarColumn,
    Progress,
    SpinnerColumn,
    TaskProgressColumn,
    TextColumn,
    TimeRemainingColumn,
)
from tqdm import tqdm

from collection_sorter.project_logging import console

# Type variable for generic iterables
T = TypeVar("T")


def get_progress(
    description: str = "Processing", total: Optional[int] = None, use_rich: bool = True
) -> Progress:
    """
    Create a progress bar.

    Args:
        description: Description of the progress bar
        total: Total number of items to process
        use_rich: Use rich progress bar instead of tqdm

    Returns:
        Progress bar object
    """
    if use_rich:
        return Progress(
            SpinnerColumn(),
            TextColumn("[bold blue]{task.description}"),
            BarColumn(),
            TaskProgressColumn(),
            TimeRemainingColumn(),
            console=console,
        )
    else:
        return tqdm(
            total=total,
            desc=description,
            unit="items",
        )


@contextmanager
def progress_bar(
    description: str = "Processing", total: Optional[int] = None, use_rich: bool = True
):
    """
    Context manager for progress bars.

    Args:
        description: Description of the progress bar
        total: Total number of items to process
        use_rich: Use rich progress bar instead of tqdm

    Yields:
        Progress bar object
    """
    if use_rich:
        with get_progress(description, total, use_rich) as progress:
            task_id = progress.add_task(description, total=total)
            yield progress, task_id
    else:
        progress = tqdm(total=total, desc=description)
        try:
            yield progress, None
        finally:
            progress.close()


def track_progress(
    iterable: Iterable[T], description: str = "Processing", use_rich: bool = True
) -> Iterable[T]:
    """
    Track progress of an iterable.

    Args:
        iterable: Iterable to track
        description: Description of the progress bar
        use_rich: Use rich progress bar instead of tqdm

    Yields:
        Items from the iterable
    """
    # Get the length of the iterable if possible
    total = None
    if hasattr(iterable, "__len__"):
        try:
            total = len(iterable)
        except (TypeError, AttributeError):
            pass

    if use_rich:
        with get_progress(description, total, use_rich) as progress:
            task_id = progress.add_task(description, total=total)
            for item in iterable:
                yield item
                progress.update(task_id, advance=1)
    else:
        for item in tqdm(iterable, desc=description, total=total):
            yield item
