"""
日志工具模块
提供日志记录功能
"""

import os
import logging
from logging.handlers import RotatingFileHandler
from typing import Optional

from core.config import Config


class LoggerManager:
    """
    日志管理类
    负责配置和管理日志记录
    """

    _loggers = {}

    @classmethod
    def get_logger(cls, name: str, config: Config = None) -> logging.Logger:
        """
        获取或创建日志记录器

        :param name: 日志记录器名称
        :param config: 配置对象
        :return: 日志记录器
        """
        if name in cls._loggers:
            return cls._loggers[name]

        config = config or Config()
        logger = logging.getLogger(name)
        
        if logger.handlers:
            cls._loggers[name] = logger
            return logger

        log_level = cls._parse_log_level(config.get("logging.level", "INFO"))
        log_format = config.get(
            "logging.format",
            "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        )
        log_dir = config.get("logging.log_dir", "logs")

        logger.setLevel(log_level)
        formatter = logging.Formatter(log_format)

        console_handler = logging.StreamHandler()
        console_handler.setLevel(log_level)
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)

        if log_dir:
            os.makedirs(log_dir, exist_ok=True)
            log_file = os.path.join(log_dir, f"{name}.log")
            file_handler = RotatingFileHandler(
                log_file,
                maxBytes=10 * 1024 * 1024,
                backupCount=5,
                encoding="utf-8",
            )
            file_handler.setLevel(log_level)
            file_handler.setFormatter(formatter)
            logger.addHandler(file_handler)

        cls._loggers[name] = logger
        return logger

    @staticmethod
    def _parse_log_level(level_str: str) -> int:
        """
        解析日志级别字符串

        :param level_str: 日志级别字符串
        :return: 日志级别整数
        """
        level_map = {
            "DEBUG": logging.DEBUG,
            "INFO": logging.INFO,
            "WARNING": logging.WARNING,
            "ERROR": logging.ERROR,
            "CRITICAL": logging.CRITICAL,
        }
        return level_map.get(level_str.upper(), logging.INFO)

    @classmethod
    def shutdown(cls) -> None:
        """
        关闭所有日志记录器
        """
        for logger in cls._loggers.values():
            for handler in logger.handlers:
                handler.close()
                logger.removeHandler(handler)
        cls._loggers.clear()


def get_logger(name: str, config: Config = None) -> logging.Logger:
    """
    获取日志记录器的便捷函数

    :param name: 日志记录器名称
    :param config: 配置对象
    :return: 日志记录器
    """
    return LoggerManager.get_logger(name, config)
