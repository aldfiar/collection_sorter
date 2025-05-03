import logging
from logging.handlers import RotatingFileHandler
from pathlib import Path
from typing import Optional, Union

from rich.console import Console
from rich.logging import RichHandler

# Create console for rich output
console = Console()

# Create logger
logger = logging.getLogger("collection_sorter")

# Mapping of string log levels to their numeric values
LOG_LEVELS = {
    "DEBUG": logging.DEBUG,
    "INFO": logging.INFO,
    "WARNING": logging.WARNING,
    "ERROR": logging.ERROR,
    "CRITICAL": logging.CRITICAL,
}

def get_log_level(level: Union[str, int]) -> int:
    """
    Convert string log level to numeric value.
    
    Args:
        level: Log level as string or int
        
    Returns:
        Numeric log level
        
    Raises:
        ValueError: If log level is invalid
    """
    if isinstance(level, int):
        return level
    
    if level.upper() in LOG_LEVELS:
        return LOG_LEVELS[level.upper()]
    
    raise ValueError(f"Invalid log level: {level}")

def setup_logging(
    log_file: Optional[Union[str, Path]] = None, 
    log_level: Union[str, int] = "INFO",
    verbose: bool = False,
) -> None:
    """
    Configure logging for the application.
    
    Args:
        log_file: Optional path to log file
        log_level: Log level as string or int
        verbose: Enable verbose logging (overrides log_level to DEBUG)
    """
    # Set log level
    level = logging.DEBUG if verbose else get_log_level(log_level)
    
    # Configure root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(level)
    
    # Remove existing handlers
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)
    
    # Configure console handler with rich formatter
    console_handler = RichHandler(
        rich_tracebacks=True,
        markup=True,
        show_time=True,
        show_path=False,
    )
    console_handler.setLevel(level)
    root_logger.addHandler(console_handler)
    
    # Add file handler if log file specified
    if log_file:
        log_path = Path(log_file) if isinstance(log_file, str) else log_file
        
        # Create parent directory if it doesn't exist
        log_path.parent.mkdir(parents=True, exist_ok=True)
        
        file_handler = RotatingFileHandler(
            log_path,
            maxBytes=10 * 1024 * 1024,  # 10 MB
            backupCount=5,
            encoding="utf-8",
        )
        file_formatter = logging.Formatter(
            "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        )
        file_handler.setFormatter(file_formatter)
        file_handler.setLevel(level)
        root_logger.addHandler(file_handler)
    
    # Set level for other common loggers to reduce noise
    logging.getLogger("urllib3").setLevel(logging.WARNING)
    logging.getLogger("requests").setLevel(logging.WARNING)

def get_logger(name: str) -> logging.Logger:
    """
    Get a logger with the specified name.
    
    Args:
        name: Logger name
        
    Returns:
        Logger instance
    """
    return logging.getLogger(f"collection_sorter.{name}")

def log_exception(e: Exception, logger: logging.Logger = None) -> None:
    """
    Log an exception with appropriate level and details.
    
    Args:
        e: Exception to log
        logger: Logger to use, defaults to root logger
    """
    if logger is None:
        logger = logging.getLogger()
    
    logger.error(f"Exception: {e.__class__.__name__}: {str(e)}", exc_info=True)