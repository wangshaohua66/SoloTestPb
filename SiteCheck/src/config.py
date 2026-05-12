"""
配置管理模块
负责加载和管理系统配置文件
"""

import yaml
import os
from typing import Dict, List, Any
import logging
from logging.handlers import RotatingFileHandler


class Config:
    """
    配置管理类
    负责加载、解析和访问配置文件
    """

    def __init__(self, config_path: str = "config.yaml"):
        """
        初始化配置管理器

        Args:
            config_path: 配置文件路径
        """
        self.config_path = config_path
        self.config: Dict[str, Any] = {}
        self._load_config()

    def _load_config(self) -> None:
        """
        加载配置文件
        如果配置文件不存在，使用默认配置
        """
        if not os.path.exists(self.config_path):
            raise FileNotFoundError(f"配置文件不存在: {self.config_path}")

        try:
            with open(self.config_path, 'r', encoding='utf-8') as f:
                self.config = yaml.safe_load(f)
        except yaml.YAMLError as e:
            raise ValueError(f"配置文件格式错误: {e}")

    def get_sites(self) -> List[Dict[str, Any]]:
        """
        获取所有检测站点配置，并按优先级排序

        Returns:
            按优先级排序的站点列表
        """
        sites = self.config.get('sites', [])
        return sorted(sites, key=lambda x: x.get('priority', 999))

    def get_notifications(self) -> Dict[str, Any]:
        """
        获取通知配置

        Returns:
            通知配置字典
        """
        return self.config.get('notifications', {})

    def get_ssl_config(self) -> Dict[str, Any]:
        """
        获取SSL证书检测配置

        Returns:
            SSL配置字典
        """
        return self.config.get('ssl', {})

    def get_report_config(self) -> Dict[str, Any]:
        """
        获取报告生成配置

        Returns:
            报告配置字典
        """
        return self.config.get('report', {})

    def get_logging_config(self) -> Dict[str, Any]:
        """
        获取日志配置

        Returns:
            日志配置字典
        """
        return self.config.get('logging', {})


def setup_logging(config: Config) -> None:
    """
    设置日志系统

    Args:
        config: 配置管理器实例
    """
    log_config = config.get_logging_config()
    log_level = getattr(logging, log_config.get('level', 'INFO').upper(), logging.INFO)
    log_file = log_config.get('file', './logs/sitecheck.log')
    max_size = log_config.get('max_size', 10485760)
    backup_count = log_config.get('backup_count', 5)

    os.makedirs(os.path.dirname(log_file), exist_ok=True)

    logger = logging.getLogger()
    logger.setLevel(log_level)

    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

    file_handler = RotatingFileHandler(
        log_file,
        maxBytes=max_size,
        backupCount=backup_count,
        encoding='utf-8'
    )
    file_handler.setFormatter(formatter)
    file_handler.setLevel(log_level)

    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    console_handler.setLevel(log_level)

    logger.addHandler(file_handler)
    logger.addHandler(console_handler)
