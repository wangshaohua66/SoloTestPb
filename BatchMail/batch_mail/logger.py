"""
日志系统模块
用于记录邮件发送过程中的所有操作和错误
"""

import logging
import os
from datetime import datetime
from typing import Optional


def setup_logger(
    name: str = "batch_mail",
    log_level: str = "INFO",
    log_file: Optional[str] = None,
    log_dir: Optional[str] = None,
) -> logging.Logger:
    """
    设置并返回配置好的日志器

    Args:
        name: 日志器名称
        log_level: 日志级别（DEBUG、INFO、WARNING、ERROR、CRITICAL）
        log_file: 日志文件名（不包含路径）
        log_dir: 日志目录路径

    Returns:
        logging.Logger: 配置好的日志器
    """
    logger = logging.getLogger(name)

    if logger.handlers:
        logger.setLevel(_get_log_level(log_level))
        return logger

    logger.setLevel(_get_log_level(log_level))

    formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    if log_file is not None:
        if log_dir is None:
            log_dir = os.path.join(os.getcwd(), "logs")

        os.makedirs(log_dir, exist_ok=True)

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename, ext = os.path.splitext(log_file)
        full_log_file = os.path.join(log_dir, f"{filename}_{timestamp}{ext}")

        file_handler = logging.FileHandler(full_log_file, encoding="utf-8")
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)

    return logger


def _get_log_level(level_str: str) -> int:
    """
    将日志级别字符串转换为logging模块的常量

    Args:
        level_str: 日志级别字符串

    Returns:
        int: 对应的logging级别常量
    """
    level_map = {
        "DEBUG": logging.DEBUG,
        "INFO": logging.INFO,
        "WARNING": logging.WARNING,
        "ERROR": logging.ERROR,
        "CRITICAL": logging.CRITICAL,
    }
    return level_map.get(level_str.upper(), logging.INFO)


class SendLog:
    """
    发送日志记录类
    封装单封邮件的发送结果
    """

    def __init__(
        self,
        email: str,
        success: bool,
        attempt: int = 1,
        error_message: Optional[str] = None,
        timestamp: Optional[datetime] = None,
    ) -> None:
        """
        初始化发送日志记录

        Args:
            email: 收件人邮箱
            success: 是否发送成功
            attempt: 尝试次数
            error_message: 错误信息（如果失败）
            timestamp: 时间戳
        """
        self.email = email
        self.success = success
        self.attempt = attempt
        self.error_message = error_message
        self.timestamp = timestamp or datetime.now()

    def to_dict(self) -> dict:
        """
        转换为字典格式

        Returns:
            dict: 日志字典
        """
        return {
            "email": self.email,
            "success": self.success,
            "attempt": self.attempt,
            "error_message": self.error_message,
            "timestamp": self.timestamp.strftime("%Y-%m-%d %H:%M:%S"),
        }

    def __str__(self) -> str:
        """
        字符串表示

        Returns:
            str: 日志字符串
        """
        status = "成功" if self.success else "失败"
        base = f"[{self.timestamp}] {self.email} - {status} (尝试次数: {self.attempt})"
        if self.error_message:
            base += f" - 错误: {self.error_message}"
        return base
