"""
批量文件重命名工具包
"""

__version__ = "1.0.0"
__author__ = "BatchRename Team"

from .core import (
    RenameStrategy,
    SequenceRenameStrategy,
    TimestampRenameStrategy,
    ReplaceRenameStrategy,
    PrefixRenameStrategy,
    SuffixRenameStrategy,
    RegexRenameStrategy,
    BatchRenamer,
)
from .cli import main

__all__ = [
    "RenameStrategy",
    "SequenceRenameStrategy",
    "TimestampRenameStrategy",
    "ReplaceRenameStrategy",
    "PrefixRenameStrategy",
    "SuffixRenameStrategy",
    "RegexRenameStrategy",
    "BatchRenamer",
    "main",
]
