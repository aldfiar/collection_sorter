from dataclasses import dataclass
from pathlib import Path
from typing import Callable, Optional


from dataclasses import dataclass, field
from .exceptions import ConfigurationError

@dataclass
class SortConfig:
    """Configuration for sorting operations."""

    source_path: Path
    destination_path: Optional[Path] = None
    archive: bool = False
    remove_source: bool = False
    rename_function: Optional[Callable[[Path], Path]] = None
    thread_count: int = field(default=0)  # 0 means use CPU count

    def __post_init__(self):
        """Validate configuration after initialization."""
        if not isinstance(self.source_path, Path):
            self.source_path = Path(self.source_path)
            
        if self.destination_path and not isinstance(self.destination_path, Path):
            self.destination_path = Path(self.destination_path)

        if self.thread_count < 0:
            raise ConfigurationError("Thread count cannot be negative")

        if not self.source_path.exists():
            raise ConfigurationError(f"Source path does not exist: {self.source_path}")

        if self.destination_path and self.destination_path == self.source_path:
            raise ConfigurationError("Destination path cannot be the same as source path")
