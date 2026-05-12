"""
配置管理模块
负责管理系统的全局配置
"""

import os
from typing import Any, Dict


class Config:
    """
    配置管理类
    集中管理系统的各项配置参数
    """

    def __init__(self, config_overrides: Dict[str, Any] = None):
        """
        初始化配置管理类

        :param config_overrides: 配置覆盖项，用于覆盖默认配置
        """
        self._config = self._get_default_config()
        if config_overrides:
            self._config.update(config_overrides)

    def _get_default_config(self) -> Dict[str, Any]:
        """
        获取默认配置

        :return: 默认配置字典
        """
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        return {
            "database": {
                "url": os.environ.get(
                    "CRONJOB_DB_URL",
                    f"sqlite:///{os.path.join(base_dir, 'cronjobs.db')}"
                ),
                "echo": False,
            },
            "scheduler": {
                "timezone": "Asia/Shanghai",
                "max_concurrent_jobs": 100,
                "misfire_grace_time": 30,
            },
            "logging": {
                "level": os.environ.get("LOG_LEVEL", "INFO"),
                "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
                "log_dir": os.environ.get("LOG_DIR", os.path.join(base_dir, "logs")),
            },
            "retry": {
                "default_max_retries": 3,
                "default_retry_interval": 5,
                "default_backoff_factor": 2,
            },
            "alert": {
                "enabled": False,
                "email": {
                    "smtp_server": "",
                    "smtp_port": 587,
                    "sender": "",
                    "recipients": [],
                    "username": "",
                    "password": "",
                },
                "webhook": {
                    "url": "",
                    "headers": {},
                },
            },
        }

    def get(self, key: str, default: Any = None) -> Any:
        """
        获取配置值

        :param key: 配置键名，支持点号分隔的层级访问
        :param default: 默认值
        :return: 配置值
        """
        keys = key.split(".")
        value = self._config
        for k in keys:
            if isinstance(value, dict) and k in value:
                value = value[k]
            else:
                return default
        return value

    def set(self, key: str, value: Any) -> None:
        """
        设置配置值

        :param key: 配置键名，支持点号分隔的层级访问
        :param value: 配置值
        """
        keys = key.split(".")
        config = self._config
        for k in keys[:-1]:
            if k not in config:
                config[k] = {}
            config = config[k]
        config[keys[-1]] = value

    def update(self, config_dict: Dict[str, Any]) -> None:
        """
        批量更新配置

        :param config_dict: 配置字典
        """
        self._deep_update(self._config, config_dict)

    def _deep_update(self, target: Dict[str, Any], source: Dict[str, Any]) -> None:
        """
        深度更新字典

        :param target: 目标字典
        :param source: 源字典
        """
        for key, value in source.items():
            if key in target and isinstance(target[key], dict) and isinstance(value, dict):
                self._deep_update(target[key], value)
            else:
                target[key] = value

    def to_dict(self) -> Dict[str, Any]:
        """
        将配置转换为字典

        :return: 配置字典
        """
        import copy
        return copy.deepcopy(self._config)
