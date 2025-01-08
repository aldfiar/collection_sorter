import logging
import sys
from pathlib import Path
from typing import Optional


def setup_logging(log_file: Optional[Path] = None, level: int = logging.INFO) -> None:
    """Configure logging for the application.

    Args:
        log_file: Optional path to log file
        level: Logging level
    """
    handlers = [logging.StreamHandler(sys.stdout)]
    if log_file:
        handlers.append(logging.FileHandler(log_file))

    logging.basicConfig(
        level=level,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        handlers=handlers,
    )
