import os
import yaml
from pathlib import Path
from typing import Dict, Any, Optional, Union
import logging

from collection_sorter.common.exceptions import ConfigurationError

logger = logging.getLogger("config")

DEFAULT_CONFIG_PATHS = [
    Path("~/.config/collection_sorter/config.yaml").expanduser(),
    Path("~/.collection_sorter.yaml").expanduser(),
    Path(os.getcwd()) / "collection_sorter.yaml",
]

DEFAULT_CONFIG = {
    "destination": None,
    "archive": False,
    "move": False,
    "dry_run": False,
    "interactive": False,
    "verbose": False,
    "log_file": None,
    "log_level": "INFO",
}

# Legacy configuration class for backward compatibility
class SortConfig:
    """
    Legacy configuration class for sorting operations.
    
    This class is kept for backward compatibility with existing code.
    New code should use the Config class instead.
    """
    
    def __init__(
        self,
        destination: Optional[Union[str, Path]] = None,
        archive: bool = False,
        move: bool = False
    ):
        """
        Initialize sort configuration.
        
        Args:
            destination: Optional destination path
            archive: Whether to create archives
            move: Whether to move files (removing source after processing)
        """
        self.destination = Path(destination) if destination else None
        self.archive = archive
        self.move = move

class Config:
    """
    Configuration manager for collection sorter.
    
    Loads configuration from multiple sources with precedence:
    1. Command line arguments (highest priority)
    2. Environment variables
    3. Config file
    4. Default values (lowest priority)
    """
    
    def __init__(self, config_path: Optional[str] = None):
        """
        Initialize configuration manager.
        
        Args:
            config_path: Optional path to config file. If not provided,
                         default locations will be checked.
        """
        self.config = DEFAULT_CONFIG.copy()
        
        # Load from config file
        self._load_from_file(config_path)
        
        # Load from environment variables
        self._load_from_env()
    
    def _load_from_file(self, config_path: Optional[str] = None) -> None:
        """
        Load configuration from YAML file.
        
        Args:
            config_path: Optional specific config file path
            
        Raises:
            ConfigurationError: If config file format is invalid
        """
        # Check specified config path first
        if config_path:
            path = Path(config_path).expanduser()
            if path.exists():
                try:
                    with open(path, "r") as f:
                        config = yaml.safe_load(f)
                        if isinstance(config, dict):
                            self.config.update(config)
                            logger.debug(f"Loaded configuration from {path}")
                            return
                        else:
                            raise ConfigurationError(f"Invalid config file format: {path}")
                except Exception as e:
                    raise ConfigurationError(f"Error loading config file {path}: {str(e)}")
            else:
                logger.warning(f"Specified config file not found: {path}")
        
        # Check default config locations
        for path in DEFAULT_CONFIG_PATHS:
            if path.exists():
                try:
                    with open(path, "r") as f:
                        config = yaml.safe_load(f)
                        if isinstance(config, dict):
                            self.config.update(config)
                            logger.debug(f"Loaded configuration from {path}")
                            return
                except Exception as e:
                    logger.warning(f"Error loading config file {path}: {str(e)}")
                    continue
        
        logger.debug("No configuration file found, using defaults")
    
    def _load_from_env(self) -> None:
        """
        Load configuration from environment variables.
        
        Environment variables should be prefixed with COLLECTION_SORTER_
        (e.g., COLLECTION_SORTER_DESTINATION)
        """
        env_prefix = "COLLECTION_SORTER_"
        
        for key in self.config.keys():
            env_key = f"{env_prefix}{key.upper()}"
            if env_key in os.environ:
                value = os.environ[env_key]
                
                # Convert string representations to proper types
                if value.lower() in ("true", "yes", "1"):
                    value = True
                elif value.lower() in ("false", "no", "0"):
                    value = False
                elif value.lower() in ("none", "null"):
                    value = None
                
                self.config[key] = value
                logger.debug(f"Loaded {key}={value} from environment variable {env_key}")
    
    def update_from_args(self, args: Dict[str, Any]) -> None:
        """
        Update configuration from command line arguments.
        
        Args:
            args: Dictionary of command line arguments
        """
        for key, value in args.items():
            if key in self.config and value is not None:
                self.config[key] = value
                logger.debug(f"Updated {key}={value} from command line arguments")
    
    def get(self, key: str, default: Any = None) -> Any:
        """
        Get configuration value.
        
        Args:
            key: Configuration key
            default: Default value if key is not found
            
        Returns:
            Configuration value or default
        """
        return self.config.get(key, default)
    
    def __getitem__(self, key: str) -> Any:
        """
        Get configuration value using dictionary-like access.
        
        Args:
            key: Configuration key
            
        Returns:
            Configuration value
            
        Raises:
            KeyError: If key is not found
        """
        return self.config[key]
    
    def __contains__(self, key: str) -> bool:
        """
        Check if configuration contains a key.
        
        Args:
            key: Configuration key
            
        Returns:
            True if key exists, False otherwise
        """
        return key in self.config