"""
日志记录模块
负责记录文件整理操作的日志信息
"""

import logging
import os
from logging.handlers import RotatingFileHandler
from typing import Optional


class Logger:
    """
    日志记录器类
    提供统一的日志记录功能，支持控制台和文件输出
    """

    def __init__(
        self,
        log_dir: str = "logs",
        log_level: str = "INFO",
        max_log_size: int = 10485760,
        backup_count: int = 5
    ):
        """
        初始化日志记录器

        Args:
            log_dir: 日志文件目录
            log_level: 日志级别（DEBUG, INFO, WARNING, ERROR, CRITICAL）
            max_log_size: 单个日志文件的最大大小（字节）
            backup_count: 保留的备份日志文件数量
        """
        self.log_dir = log_dir
        self.log_level = log_level
        self.max_log_size = max_log_size
        self.backup_count = backup_count
        self.logger: Optional[logging.Logger] = None
        self._setup_logger()

    def _setup_logger(self) -> None:
        """
        配置日志记录器
        """
        os.makedirs(self.log_dir, exist_ok=True)
        log_file = os.path.join(self.log_dir, "organizer.log")
        
        self.logger = logging.getLogger("FolderOrganizer")
        self.logger.setLevel(self._get_log_level(self.log_level))
        self.logger.handlers.clear()
        
        formatter = logging.Formatter(
            "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S"
        )
        
        file_handler = RotatingFileHandler(
            log_file,
            maxBytes=self.max_log_size,
            backupCount=self.backup_count,
            encoding="utf-8"
        )
        file_handler.setFormatter(formatter)
        self.logger.addHandler(file_handler)
        
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(formatter)
        self.logger.addHandler(console_handler)

    @staticmethod
    def _get_log_level(level: str) -> int:
        """
        将字符串日志级别转换为logging模块的级别

        Args:
            level: 日志级别字符串

        Returns:
            logging模块的日志级别常量
        """
        levels = {
            "DEBUG": logging.DEBUG,
            "INFO": logging.INFO,
            "WARNING": logging.WARNING,
            "ERROR": logging.ERROR,
            "CRITICAL": logging.CRITICAL
        }
        return levels.get(level.upper(), logging.INFO)

    def info(self, message: str) -> None:
        """
        记录INFO级别的日志

        Args:
            message: 日志消息
        """
        if self.logger:
            self.logger.info(message)

    def debug(self, message: str) -> None:
        """
        记录DEBUG级别的日志

        Args:
            message: 日志消息
        """
        if self.logger:
            self.logger.debug(message)

    def warning(self, message: str) -> None:
        """
        记录WARNING级别的日志

        Args:
            message: 日志消息
        """
        if self.logger:
            self.logger.warning(message)

    def error(self, message: str) -> None:
        """
        记录ERROR级别的日志

        Args:
            message: 日志消息
        """
        if self.logger:
            self.logger.error(message)

    def critical(self, message: str) -> None:
        """
        记录CRITICAL级别的日志

        Args:
            message: 日志消息
        """
        if self.logger:
            self.logger.critical(message)

    def log_organize_result(self, result: dict) -> None:
        """
        记录整理结果到日志

        Args:
            result: organize()方法返回的结果字典
        """
        self.info("=" * 50)
        self.info("文件整理完成")
        self.info(f"总文件数: {result.get('total_files', 0)}")
        self.info(f"成功移动: {result.get('moved_files', 0)}")
        self.info(f"移动失败: {result.get('failed_files', 0)}")
        self.info(f"耗时: {result.get('elapsed_time', 0):.2f}秒")
        
        category_stats = result.get('category_stats', {})
        if category_stats:
            self.info("分类统计:")
            for category, count in category_stats.items():
                if count > 0:
                    self.info(f"  - {category}: {count}个文件")
        self.info("=" * 50)

    def log_file_moved(self, source: str, target: str, category: str) -> None:
        """
        记录单个文件移动的日志

        Args:
            source: 源文件路径
            target: 目标文件路径
            category: 文件分类
        """
        self.info(f"文件移动: {source} -> {target} [分类: {category}]")

    def log_file_restore(self, source: str, target: str) -> None:
        """
        记录单个文件还原的日志

        Args:
            source: 源文件路径（当前位置）
            target: 目标文件路径（原位置）
        """
        self.info(f"文件还原: {source} -> {target}")

    def log_schedule_start(self) -> None:
        """
        记录定时任务开始的日志
        """
        self.info("定时整理任务已启动")

    def log_schedule_stop(self) -> None:
        """
        记录定时任务停止的日志
        """
        self.info("定时整理任务已停止")
