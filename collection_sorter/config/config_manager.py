"""
Centralized configuration management for collection sorter.

This module provides a configuration manager that handles loading, merging,
and providing access to configuration from different sources with proper precedence.
"""

import json
import logging
import os
from pathlib import Path
from typing import Dict, Any, Optional

import yaml

try:
    import tomli
except ImportError:
    tomli = None

from pydantic import ValidationError

from collection_sorter.common.exceptions import ConfigurationError
from collection_sorter.config.config import SortConfig
from collection_sorter.config.config_models import AppConfig

logger = logging.getLogger("config_manager")

DEFAULT_CONFIG_PATHS = [
    Path("~/.config/collection_sorter/config.yaml").expanduser(),
    Path("~/.config/collection_sorter/config.toml").expanduser(),
    Path("~/.config/collection_sorter/config.json").expanduser(),
    Path("~/.collection_sorter.yaml").expanduser(),
    Path("~/.collection_sorter.toml").expanduser(),
    Path("~/.collection_sorter.json").expanduser(),
    Path(os.getcwd()) / "collection_sorter.yaml",
    Path(os.getcwd()) / "collection_sorter.toml",
    Path(os.getcwd()) / "collection_sorter.json",
]


class ConfigManager:
    """
    Centralized configuration manager that handles loading and merging
    configuration from different sources with proper precedence.
    """
    
    def __init__(self):
        self._config = AppConfig()
        self._config_loaded = False
        self._config_path = None
    
    def load_configuration(
        self, 
        config_file: Optional[str] = None,
        cli_args: Optional[dict] = None,
        env_prefix: str = "COLLECTION_SORTER_"
    ) -> AppConfig:
        """
        Load configuration from different sources with precedence:
        1. CLI arguments (highest)
        2. Environment variables
        3. Config file
        4. Default values (lowest)
        
        Args:
            config_file: Optional path to config file
            cli_args: Optional CLI arguments
            env_prefix: Prefix for environment variables
            
        Returns:
            Loaded configuration
            
        Raises:
            ConfigurationError: If loading or validation fails
        """
        # Start with defaults from Pydantic model
        config_data = {}
        
        # Load from config file (lowest priority)
        file_config = self._load_from_file(config_file)
        if file_config:
            self._deep_update(config_data, file_config)
        
        # Load from environment variables (middle priority)
        env_config = self._load_from_env(env_prefix)
        if env_config:
            self._deep_update(config_data, env_config)
        
        # Apply CLI arguments (highest priority)
        if cli_args:
            cli_config = self._process_cli_args(cli_args)
            if cli_config:
                self._deep_update(config_data, cli_config)
        
        try:
            # Create a new config with merged data
            if config_data:
                self._config = AppConfig.parse_obj(config_data)
            else:
                self._config = AppConfig()
                
            self._config_loaded = True
            
        except ValidationError as e:
            raise ConfigurationError(f"Configuration validation failed: {str(e)}")
        
        return self._config
    
    def _load_from_file(self, config_path: Optional[str] = None) -> Dict[str, Any]:
        """
        Load configuration from file.
        
        Args:
            config_path: Optional path to config file
            
        Returns:
            Dictionary with configuration from file
            
        Raises:
            ConfigurationError: If file format is invalid
        """
        result = {}
        
        # Try specific config file first
        if config_path:
            path = Path(config_path).expanduser()
            if path.exists():
                try:
                    result = self._read_config_file(path)
                    self._config_path = path
                    logger.debug(f"Loaded configuration from {path}")
                except Exception as e:
                    raise ConfigurationError(f"Error loading config file {path}: {str(e)}")
            else:
                logger.warning(f"Specified config file not found: {path}")
        
        # Fall back to default locations if no result yet
        if not result:
            for path in DEFAULT_CONFIG_PATHS:
                if path.exists():
                    try:
                        result = self._read_config_file(path)
                        self._config_path = path
                        logger.debug(f"Loaded configuration from {path}")
                        break
                    except Exception as e:
                        logger.warning(f"Error loading config file {path}: {str(e)}")
                        continue
        
        if not result:
            logger.debug("No configuration file found, using defaults")
            
        return result
    
    def _read_config_file(self, path: Path) -> Dict[str, Any]:
        """
        Read configuration from file based on extension.
        
        Args:
            path: Path to config file
            
        Returns:
            Dictionary with configuration from file
            
        Raises:
            ConfigurationError: If file format is not supported or invalid
        """
        suffix = path.suffix.lower()
        
        try:
            with open(path, "r") as f:
                if suffix == ".yaml" or suffix == ".yml":
                    return yaml.safe_load(f) or {}
                elif suffix == ".json":
                    return json.load(f)
                elif suffix == ".toml":
                    if tomli is None:
                        raise ConfigurationError("tomli package not installed, cannot read TOML files")
                    return tomli.loads(f.read())
                else:
                    raise ConfigurationError(f"Unsupported config file format: {suffix}")
        except Exception as e:
            raise ConfigurationError(f"Error reading config file {path}: {str(e)}")
    
    def _load_from_env(self, prefix: str = "COLLECTION_SORTER_") -> Dict[str, Any]:
        """
        Load configuration from environment variables.
        
        Environment variables should be prefixed with the specified prefix
        and use double underscores to indicate nesting.
        
        Examples:
            COLLECTION_SORTER_COLLECTION__ARCHIVE=true
            COLLECTION_SORTER_LOGGING__LOG_LEVEL=DEBUG
        
        Args:
            prefix: Prefix for environment variables
            
        Returns:
            Dictionary with configuration from environment variables
        """
        result = {}
        
        for key, value in os.environ.items():
            if not key.startswith(prefix):
                continue
                
            # Remove prefix and split by double underscore to get nested keys
            config_key = key[len(prefix):].lower()
            parts = config_key.split("__")
            
            # Convert value to appropriate type
            processed_value = self._convert_env_value(value)
            
            # Build nested dictionary
            current = result
            for part in parts[:-1]:
                if part not in current:
                    current[part] = {}
                current = current[part]
                
            current[parts[-1]] = processed_value
            logger.debug(f"Loaded {key}={processed_value} from environment")
            
        return result
    
    def _convert_env_value(self, value: str) -> Any:
        """
        Convert environment variable string to appropriate type.
        
        Args:
            value: String value from environment variable
            
        Returns:
            Converted value
        """
        # Boolean values
        if value.lower() in ("true", "yes", "1", "y"):
            return True
        elif value.lower() in ("false", "no", "0", "n"):
            return False
        
        # None value
        elif value.lower() in ("none", "null"):
            return None
            
        # Try to convert to integer or float
        try:
            if "." in value:
                return float(value)
            else:
                return int(value)
        except ValueError:
            # Leave as string if not a number
            return value
    
    def _process_cli_args(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process CLI arguments into a configuration dictionary.
        
        Args:
            args: Dictionary of CLI arguments
            
        Returns:
            Dictionary with configuration from CLI arguments
        """
        result = {"collection": {}, "logging": {}, "ui": {}}
        
        # Map command line arguments to configuration structure
        cli_to_config = {
            # Collection settings
            "destination": ("collection", "destination"),
            "archive": ("collection", "archive"),
            "move": ("collection", "move"),
            "dry_run": ("collection", "dry_run"),
            
            # Logging settings
            "verbose": ("logging", "verbose"),
            "log_file": ("logging", "log_file"),
            "log_level": ("logging", "log_level"),
            
            # UI settings
            "interactive": ("ui", "interactive"),
            
            # Command-specific settings can be added here
        }
        
        # Process each argument
        for arg_name, value in args.items():
            if arg_name in cli_to_config and value is not None:
                section, key = cli_to_config[arg_name]
                
                # Ensure section exists
                if section not in result:
                    result[section] = {}
                    
                result[section][key] = value
                logger.debug(f"Set {section}.{key}={value} from CLI argument")
                
        return result
    
    def _deep_update(self, target: Dict[str, Any], source: Dict[str, Any]) -> None:
        """
        Deep update a nested dictionary.
        
        Args:
            target: Target dictionary to update
            source: Source dictionary with updates
        """
        for key, value in source.items():
            if isinstance(value, dict) and key in target and isinstance(target[key], dict):
                self._deep_update(target[key], value)
            else:
                target[key] = value
    
    @property
    def config(self) -> AppConfig:
        """
        Get the current configuration.
        
        Returns:
            Current configuration
        """
        if not self._config_loaded:
            self.load_configuration()
        return self._config
    
    def get_command_config(self, command: str) -> Dict[str, Any]:
        """
        Get configuration for a specific command, merging global and
        command-specific settings with command settings taking precedence.
        
        Args:
            command: Command name
            
        Returns:
            Dictionary with merged configuration for the command
        """
        if not self._config_loaded:
            self.load_configuration()
            
        # Start with global collection settings
        result = self._config.collection.model_dump()
        
        # Override with command-specific settings if available
        if hasattr(self._config, command):
            command_config = getattr(self._config, command)
            command_dict = command_config.model_dump() if hasattr(command_config, "model_dump") else {}
            result.update(command_dict)
            
        return result
    
    def to_sort_config(self) -> SortConfig:
        """
        Convert to legacy SortConfig for backward compatibility.
        
        Returns:
            Legacy SortConfig instance
        """
        if not self._config_loaded:
            self.load_configuration()
            
        return SortConfig(
            destination=self._config.collection.destination,
            archive=self._config.collection.archive,
            move=self._config.collection.move
        )
    
    def generate_template(self, format: str = "yaml") -> str:
        """
        Generate a configuration file template with documentation.
        
        Args:
            format: Output format ("yaml", "toml", or "json")
        
        Returns:
            Configuration template as string
            
        Raises:
            ValueError: If format is not supported
        """
        schema = AppConfig.schema()
        template = self._schema_to_template(schema)
        
        if format.lower() == "yaml":
            return yaml.dump(template, sort_keys=False)
        elif format.lower() == "json":
            return json.dumps(template, indent=2)
        elif format.lower() == "toml":
            if tomli is None:
                raise ValueError("tomli package not installed, cannot generate TOML template")
            import toml
            return toml.dumps(template)
        else:
            raise ValueError(f"Unsupported format: {format}")
    
    def _schema_to_template(self, schema: Dict[str, Any]) -> Dict[str, Any]:
        """
        Convert a Pydantic schema to a template.
        
        Args:
            schema: Pydantic schema
            
        Returns:
            Template dictionary
        """
        result = {}
        
        # Process properties and add comments
        for prop, details in schema.get("properties", {}).items():
            # Skip if not a proper property
            if not isinstance(details, dict):
                continue
                
            if details.get("type") == "object" and "properties" in details:
                # Recursively process nested objects
                result[prop] = self._schema_to_template(details)
            else:
                # Get default value
                default = details.get("default")
                
                # Add property with default or example value
                if default is not None:
                    result[prop] = default
                elif "examples" in details and details["examples"]:
                    result[prop] = details["examples"][0]
                elif details.get("type") == "string":
                    result[prop] = ""
                elif details.get("type") == "array":
                    result[prop] = []
                elif details.get("type") == "object":
                    result[prop] = {}
                elif details.get("type") == "boolean":
                    result[prop] = False
                elif details.get("type") == "number":
                    result[prop] = 0
                elif details.get("type") == "integer":
                    result[prop] = 0
                else:
                    result[prop] = None
        
        return result
    
    def apply_click_context(self, ctx) -> None:
        """
        Update configuration from Click context.
        
        This allows using the standard Click options approach while
        still benefiting from our config system.
        
        Args:
            ctx: Click context
        """
        if ctx.params:
            self.load_configuration(
                config_file=ctx.params.get("config"),
                cli_args=ctx.params
            )

# Global configuration manager instance
config_manager = ConfigManager()