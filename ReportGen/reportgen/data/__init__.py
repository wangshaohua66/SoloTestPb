"""
数据处理模块。

提供从多种数据源读取数据以及数据处理功能。
"""

from reportgen.data.reader import DataReader
from reportgen.data.processor import DataProcessor

__all__ = ["DataReader", "DataProcessor"]
