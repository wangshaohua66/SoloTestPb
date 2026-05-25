"""Logging utilities for CiteMaster."""

import logging
import sys
from pathlib import Path
from datetime import datetime
from typing import Optional


class CiteMasterLogger:
    """Custom logger for CiteMaster application."""

    _instance: Optional["CiteMasterLogger"] = None
    _logger: Optional[logging.Logger] = None

    def __new__(cls) -> "CiteMasterLogger":
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialize_logger()
        return cls._instance

    def _initialize_logger(self, log_dir: str = "logs", log_level: int = logging.INFO) -> None:
        """Initialize the logger with file and console handlers."""
        self._logger = logging.getLogger("citemaster")
        self._logger.setLevel(log_level)
        self._logger.propagate = False

        log_path = Path(log_dir)
        log_path.mkdir(exist_ok=True)

        log_file = log_path / f"citemaster_{datetime.now().strftime('%Y%m%d')}.log"

        formatter = logging.Formatter(
            "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S"
        )

        file_handler = logging.FileHandler(log_file, encoding="utf-8")
        file_handler.setLevel(log_level)
        file_handler.setFormatter(formatter)

        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(logging.WARNING)
        console_handler.setFormatter(formatter)

        self._logger.addHandler(file_handler)
        self._logger.addHandler(console_handler)

    def set_level(self, level: str) -> None:
        """Set the logging level."""
        level_map = {
            "DEBUG": logging.DEBUG,
            "INFO": logging.INFO,
            "WARNING": logging.WARNING,
            "ERROR": logging.ERROR,
            "CRITICAL": logging.CRITICAL
        }
        log_level = level_map.get(level.upper(), logging.INFO)
        self._logger.setLevel(log_level)
        for handler in self._logger.handlers:
            handler.setLevel(log_level)

    def debug(self, message: str) -> None:
        """Log a debug message."""
        self._logger.debug(message)

    def info(self, message: str) -> None:
        """Log an info message."""
        self._logger.info(message)

    def warning(self, message: str) -> None:
        """Log a warning message."""
        self._logger.warning(message)

    def error(self, message: str) -> None:
        """Log an error message."""
        self._logger.error(message)

    def critical(self, message: str) -> None:
        """Log a critical message."""
        self._logger.critical(message)

    def exception(self, message: str, exc: Exception) -> None:
        """Log an exception with traceback."""
        self._logger.exception(f"{message}: {str(exc)}")


def get_logger() -> CiteMasterLogger:
    """Get the singleton logger instance."""
    return CiteMasterLogger()
