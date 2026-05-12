"""
网页数据采集工具
一个功能完整的自动化网页数据采集框架
"""

__version__ = "1.0.0"
__author__ = "Web Scraper Team"

from .scraper import WebScraper
from .config import (
    ScraperConfig,
    SelectorConfig,
    LoginConfig,
    PaginationConfig,
    RequestConfig,
    RateLimitConfig,
    ProxyConfig,
    ExportConfig,
    ConfigLoader,
)
from .request_manager import RequestManager
from .data_extractor import DataExtractor
from .pagination import PaginationHandler
from .authenticator import Authenticator
from .proxy_manager import ProxyManager, ProxyInfo
from .rate_limiter import RateLimiter
from .data_exporter import DataExporter

__all__ = [
    "WebScraper",
    "ScraperConfig",
    "SelectorConfig",
    "LoginConfig",
    "PaginationConfig",
    "RequestConfig",
    "RateLimitConfig",
    "ProxyConfig",
    "ExportConfig",
    "ConfigLoader",
    "RequestManager",
    "DataExtractor",
    "PaginationHandler",
    "Authenticator",
    "ProxyManager",
    "ProxyInfo",
    "RateLimiter",
    "DataExporter",
]
