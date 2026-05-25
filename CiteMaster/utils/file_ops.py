"""File operation utilities for CiteMaster."""

import json
import os
from pathlib import Path
from typing import Dict, Any, List, Optional

from utils.logger import get_logger
from utils.config import Config

logger = get_logger()


class FileOperationError(Exception):
    """Raised when file operations fail."""
    pass


class FileManager:
    """Handles file I/O operations with validation and error handling."""

    def __init__(self, config: Config):
        self.config = config
        self.encoding = config.output_encoding

    def check_file_size(self, file_path: Path) -> bool:
        """Check if file size is within limits."""
        if not file_path.exists():
            return True

        size = file_path.stat().st_size
        max_size = self.config.max_file_size

        if size > max_size:
            logger.warning(f"File {file_path} size {size / (1024*1024):.2f}MB exceeds limit {max_size / (1024*1024):.2f}MB")
            return False

        return True

    def ensure_dir_exists(self, dir_path: Path) -> None:
        """Ensure directory exists, creating it if necessary."""
        try:
            dir_path = Path(dir_path)
            dir_path.mkdir(parents=True, exist_ok=True)
            logger.debug(f"Ensured directory exists: {dir_path}")
        except Exception as e:
            logger.exception("Failed to create directory", e)
            raise FileOperationError(f"Failed to create directory {dir_path}: {e}")

    def read_json(self, file_path: Path) -> Dict[str, Any]:
        """Read and parse a JSON file."""
        file_path = Path(file_path)

        try:
            if not file_path.exists():
                logger.info(f"JSON file not found: {file_path}, returning empty dict")
                return {}

            if not self.check_file_size(file_path):
                raise FileOperationError(f"File {file_path} exceeds maximum size limit")

            with open(file_path, "r", encoding=self.encoding) as f:
                data = json.load(f)

            logger.info(f"Successfully read JSON from {file_path}")
            return data

        except json.JSONDecodeError as e:
            logger.error(f"Invalid JSON in {file_path}: {e}")
            raise FileOperationError(f"Invalid JSON in {file_path}: {e}")
        except UnicodeDecodeError as e:
            logger.error(f"Encoding error reading {file_path}: {e}")
            raise FileOperationError(f"Encoding error reading {file_path}. Expected {self.encoding}: {e}")
        except Exception as e:
            logger.exception(f"Failed to read JSON file {file_path}", e)
            raise FileOperationError(f"Failed to read {file_path}: {e}")

    def write_json(self, file_path: Path, data: Dict[str, Any], indent: int = 2) -> None:
        """Write data to a JSON file."""
        file_path = Path(file_path)

        try:
            self.ensure_dir_exists(file_path.parent)

            with open(file_path, "w", encoding=self.encoding) as f:
                json.dump(data, f, indent=indent, ensure_ascii=False)

            logger.info(f"Successfully wrote JSON to {file_path}")

        except (TypeError, ValueError) as e:
            logger.error(f"Invalid data for JSON serialization: {e}")
            raise FileOperationError(f"Data is not JSON serializable: {e}")
        except Exception as e:
            logger.exception(f"Failed to write JSON file {file_path}", e)
            raise FileOperationError(f"Failed to write {file_path}: {e}")

    def read_text(self, file_path: Path) -> str:
        """Read text from a file."""
        file_path = Path(file_path)

        try:
            if not file_path.exists():
                raise FileOperationError(f"File not found: {file_path}")

            if not self.check_file_size(file_path):
                raise FileOperationError(f"File {file_path} exceeds maximum size limit")

            with open(file_path, "r", encoding=self.encoding) as f:
                content = f.read()

            logger.info(f"Successfully read text from {file_path} ({len(content)} chars)")
            return content

        except UnicodeDecodeError as e:
            logger.error(f"Encoding error reading {file_path}: {e}")
            raise FileOperationError(f"Encoding error reading {file_path}. Expected {self.encoding}: {e}")
        except Exception as e:
            logger.exception(f"Failed to read text file {file_path}", e)
            raise FileOperationError(f"Failed to read {file_path}: {e}")

    def write_text(self, file_path: Path, content: str) -> None:
        """Write text to a file."""
        file_path = Path(file_path)

        try:
            self.ensure_dir_exists(file_path.parent)

            with open(file_path, "w", encoding=self.encoding) as f:
                f.write(content)

            logger.info(f"Successfully wrote text to {file_path} ({len(content)} chars)")

        except Exception as e:
            logger.exception(f"Failed to write text file {file_path}", e)
            raise FileOperationError(f"Failed to write {file_path}: {e}")

    def append_text(self, file_path: Path, content: str) -> None:
        """Append text to a file."""
        file_path = Path(file_path)

        try:
            self.ensure_dir_exists(file_path.parent)

            with open(file_path, "a", encoding=self.encoding) as f:
                f.write(content)

            logger.info(f"Successfully appended text to {file_path}")

        except Exception as e:
            logger.exception(f"Failed to append to text file {file_path}", e)
            raise FileOperationError(f"Failed to append to {file_path}: {e}")

    def file_exists(self, file_path: Path) -> bool:
        """Check if a file exists."""
        return Path(file_path).exists()

    def get_file_size(self, file_path: Path) -> int:
        """Get file size in bytes."""
        if not self.file_exists(file_path):
            return 0
        return Path(file_path).stat().st_size

    def backup_file(self, file_path: Path) -> Optional[Path]:
        """Create a backup of a file."""
        file_path = Path(file_path)

        try:
            if not file_path.exists():
                logger.warning(f"Cannot backup non-existent file: {file_path}")
                return None

            backup_path = file_path.with_suffix(file_path.suffix + ".bak")
            counter = 1
            while backup_path.exists():
                backup_path = file_path.with_suffix(f"{file_path.suffix}.bak{counter}")
                counter += 1

            with open(file_path, "rb") as src, open(backup_path, "wb") as dst:
                dst.write(src.read())

            logger.info(f"Created backup: {backup_path}")
            return backup_path

        except Exception as e:
            logger.exception(f"Failed to backup file {file_path}", e)
            raise FileOperationError(f"Failed to backup {file_path}: {e}")

    def list_files(self, dir_path: Path, pattern: str = "*") -> List[Path]:
        """List files in a directory matching a pattern."""
        dir_path = Path(dir_path)

        try:
            if not dir_path.exists():
                return []

            files = sorted(dir_path.glob(pattern))
            logger.debug(f"Found {len(files)} files matching '{pattern}' in {dir_path}")
            return files

        except Exception as e:
            logger.exception(f"Failed to list files in {dir_path}", e)
            raise FileOperationError(f"Failed to list files in {dir_path}: {e}")

    def delete_file(self, file_path: Path) -> None:
        """Delete a file."""
        file_path = Path(file_path)

        try:
            if file_path.exists():
                file_path.unlink()
                logger.info(f"Deleted file: {file_path}")
            else:
                logger.warning(f"Attempted to delete non-existent file: {file_path}")

        except Exception as e:
            logger.exception(f"Failed to delete file {file_path}", e)
            raise FileOperationError(f"Failed to delete {file_path}: {e}")
