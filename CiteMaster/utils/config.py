"""Configuration management for CiteMaster using YAML."""

import os
from pathlib import Path
from typing import Dict, Any, Optional
import yaml

from utils.logger import get_logger

logger = get_logger()


class ConfigError(Exception):
    """Raised when there is an error with configuration."""
    pass


class Config:
    """Configuration manager for CiteMaster."""

    DEFAULT_CONFIG: Dict[str, Any] = {
        "default_citation_format": "apa",
        "library_path": "data/library.json",
        "bibtex_path": "data/library.bib",
        "output_encoding": "utf-8",
        "max_file_size_mb": 10,
        "log_level": "INFO",
        "graph_output_path": "data/citation_graph.html",
        "supported_formats": ["apa", "mla", "chicago", "ieee"],
        "required_fields": ["title", "author", "year"],
        "templates_dir": "templates"
    }

    def __init__(self, config_path: Optional[str] = None):
        """Initialize configuration from file or defaults."""
        self.config_path = Path(config_path) if config_path else Path("config.yaml")
        self._config: Dict[str, Any] = {}
        self._load_config()

    def _load_config(self) -> None:
        """Load configuration from YAML file, merging with defaults."""
        try:
            if self.config_path.exists():
                logger.info(f"Loading configuration from {self.config_path}")
                with open(self.config_path, "r", encoding="utf-8") as f:
                    user_config = yaml.safe_load(f) or {}
                self._config = {**self.DEFAULT_CONFIG, **user_config}
            else:
                logger.warning(f"Config file not found at {self.config_path}, using defaults")
                self._config = self.DEFAULT_CONFIG.copy()
                self._save_default_config()
        except yaml.YAMLError as e:
            logger.error(f"Error parsing YAML configuration: {e}")
            raise ConfigError(f"Invalid YAML in config file: {e}")
        except Exception as e:
            logger.exception("Failed to load configuration", e)
            raise ConfigError(f"Failed to load configuration: {e}")

    def _save_default_config(self) -> None:
        """Save default configuration to file."""
        try:
            self.config_path.parent.mkdir(parents=True, exist_ok=True)
            with open(self.config_path, "w", encoding="utf-8") as f:
                yaml.dump(self.DEFAULT_CONFIG, f, default_flow_style=False, allow_unicode=True)
            logger.info(f"Default configuration saved to {self.config_path}")
        except Exception as e:
            logger.exception("Failed to save default configuration", e)
            raise ConfigError(f"Failed to save default configuration: {e}")

    def get(self, key: str, default: Any = None) -> Any:
        """Get a configuration value."""
        value = self._config.get(key, default)
        logger.debug(f"Config get: {key} = {value}")
        return value

    def set(self, key: str, value: Any) -> None:
        """Set a configuration value and persist to file."""
        try:
            self._config[key] = value
            with open(self.config_path, "w", encoding="utf-8") as f:
                yaml.dump(self._config, f, default_flow_style=False, allow_unicode=True)
            logger.info(f"Configuration updated: {key} = {value}")
        except Exception as e:
            logger.exception("Failed to update configuration", e)
            raise ConfigError(f"Failed to update configuration: {e}")

    def reload(self) -> None:
        """Reload configuration from file."""
        logger.info("Reloading configuration")
        self._load_config()

    @property
    def default_citation_format(self) -> str:
        """Get the default citation format."""
        return self.get("default_citation_format")

    @property
    def library_path(self) -> Path:
        """Get the library file path."""
        return Path(self.get("library_path"))

    @property
    def bibtex_path(self) -> Path:
        """Get the BibTeX file path."""
        return Path(self.get("bibtex_path"))

    @property
    def output_encoding(self) -> str:
        """Get the output encoding."""
        return self.get("output_encoding")

    @property
    def max_file_size(self) -> int:
        """Get the maximum file size in bytes."""
        return self.get("max_file_size_mb", 10) * 1024 * 1024

    @property
    def supported_formats(self) -> list:
        """Get supported citation formats."""
        return self.get("supported_formats", [])

    @property
    def required_fields(self) -> list:
        """Get required fields for entries."""
        return self.get("required_fields", [])
