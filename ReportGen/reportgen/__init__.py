"""
自动化报表生成工具包。

提供从多种数据源读取数据、处理数据并生成各种格式报表的功能。
"""

__version__ = "1.0.0"
__author__ = "ReportGen Team"

from reportgen.core import ReportGenerator
from reportgen.data import DataReader, DataProcessor
from reportgen.output import ExcelOutput, HtmlOutput, PdfOutput
from reportgen.templates import TemplateEngine
from reportgen.scheduler import ReportScheduler

__all__ = [
    "ReportGenerator",
    "DataReader",
    "DataProcessor",
    "ExcelOutput",
    "HtmlOutput",
    "PdfOutput",
    "TemplateEngine",
    "ReportScheduler",
]
