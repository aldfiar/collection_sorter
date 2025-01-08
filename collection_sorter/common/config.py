from dataclasses import dataclass
from pathlib import Path
from typing import Callable, Optional


@dataclass
class SortConfig:
    """Configuration for sorting operations."""

    source_path: Path
    destination_path: Optional[Path] = None
    archive: bool = False
    remove_source: bool = False
    rename_function: Optional[Callable[[Path], Path]] = None
    thread_count: int = 0  # 0 means use CPU count
