# -*- coding: utf-8 -*-
"""
配置管理模块
负责加载和管理监控工具的配置信息
"""

import json
import os
from typing import Dict, Any


class Config:
    """配置管理类"""

    DEFAULT_CONFIG = {
        "interval": 1,
        "cpu_threshold": 80.0,
        "memory_threshold": 80.0,
        "disk_threshold": 85.0,
        "network_threshold": 100.0,
        "smtp": {
            "enabled": False,
            "server": "smtp.example.com",
            "port": 587,
            "username": "user@example.com",
            "password": "password",
            "from_email": "monitor@example.com",
            "to_emails": ["admin@example.com"],
            "use_tls": True
        },
        "report": {
            "enabled": True,
            "interval": 3600,
            "path": "./reports",
            "format": "html"
        },
        "data_retention": 86400
    }

    def __init__(self, config_path: str = "config.json"):
        """
        初始化配置管理器

        Args:
            config_path: 配置文件路径
        """
        self.config_path = config_path
        self._config = self._load_config()

    def _load_config(self) -> Dict[str, Any]:
        """
        加载配置文件，如果不存在则创建默认配置

        Returns:
            配置字典
        """
        if os.path.exists(self.config_path):
            try:
                with open(self.config_path, 'r', encoding='utf-8') as f:
                    user_config = json.load(f)
                    return self._merge_config(self.DEFAULT_CONFIG, user_config)
            except Exception:
                return self.DEFAULT_CONFIG.copy()
        else:
            self._save_default_config()
            return self.DEFAULT_CONFIG.copy()

    def _merge_config(self, default: Dict, user: Dict) -> Dict:
        """
        合并用户配置和默认配置

        Args:
            default: 默认配置
            user: 用户配置

        Returns:
            合并后的配置
        """
        result = default.copy()
        for key, value in user.items():
            if key in result and isinstance(result[key], dict) and isinstance(value, dict):
                result[key] = self._merge_config(result[key], value)
            else:
                result[key] = value
        return result

    def _save_default_config(self) -> None:
        """保存默认配置文件"""
        try:
            with open(self.config_path, 'w', encoding='utf-8') as f:
                json.dump(self.DEFAULT_CONFIG, f, indent=4, ensure_ascii=False)
        except Exception:
            pass

    def get(self, key: str, default: Any = None) -> Any:
        """
        获取配置值

        Args:
            key: 配置键，支持点号分隔，如 "smtp.server"
            default: 默认值

        Returns:
            配置值
        """
        keys = key.split('.')
        value = self._config
        try:
            for k in keys:
                value = value[k]
            return value
        except (KeyError, TypeError):
            return default

    def set(self, key: str, value: Any) -> None:
        """
        设置配置值

        Args:
            key: 配置键，支持点号分隔
            value: 配置值
        """
        keys = key.split('.')
        config = self._config
        for k in keys[:-1]:
            if k not in config:
                config[k] = {}
            config = config[k]
        config[keys[-1]] = value

    def save(self) -> None:
        """保存当前配置到文件"""
        try:
            with open(self.config_path, 'w', encoding='utf-8') as f:
                json.dump(self._config, f, indent=4, ensure_ascii=False)
        except Exception:
            pass

    @property
    def interval(self) -> int:
        """采集间隔（秒）"""
        return self.get("interval", 1)

    @property
    def cpu_threshold(self) -> float:
        """CPU告警阈值（%）"""
        return self.get("cpu_threshold", 80.0)

    @property
    def memory_threshold(self) -> float:
        """内存告警阈值（%）"""
        return self.get("memory_threshold", 80.0)

    @property
    def disk_threshold(self) -> float:
        """磁盘告警阈值（%）"""
        return self.get("disk_threshold", 85.0)

    @property
    def network_threshold(self) -> float:
        """网络告警阈值（MB/s）"""
        return self.get("network_threshold", 100.0)
