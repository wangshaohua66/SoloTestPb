"""
配置管理模块
负责加载、保存和管理文件夹整理工具的配置
"""

import json
import os
from typing import Dict, Any, Optional


class ConfigManager:
    """
    配置管理器类
    负责配置文件的加载、保存和验证
    """

    def __init__(self, config_path: Optional[str] = None):
        """
        初始化配置管理器

        Args:
            config_path: 配置文件路径，如果为None则使用默认路径
        """
        if config_path is None:
            config_path = os.path.join(
                os.path.dirname(os.path.dirname(__file__)),
                "config",
                "default_config.json"
            )
        self.config_path = config_path
        self.config: Dict[str, Any] = {}
        self._load_config()

    def _load_config(self) -> None:
        """
        从文件加载配置
        """
        if os.path.exists(self.config_path):
            with open(self.config_path, "r", encoding="utf-8") as f:
                self.config = json.load(f)
        else:
            self.config = self._get_default_config()
            self.save_config()

    @staticmethod
    def _get_default_config() -> Dict[str, Any]:
        """
        获取默认配置

        Returns:
            默认配置字典
        """
        return {
            "source_dir": "",
            "categories": {
                "documents": {
                    "extensions": [".pdf", ".doc", ".docx", ".xls", ".xlsx", ".ppt", ".pptx", ".txt", ".md", ".rtf"],
                    "target_dir": "Documents"
                },
                "images": {
                    "extensions": [".jpg", ".jpeg", ".png", ".gif", ".bmp", ".tiff", ".tif", ".webp", ".svg"],
                    "target_dir": "Images"
                },
                "videos": {
                    "extensions": [".mp4", ".avi", ".mkv", ".mov", ".wmv", ".flv", ".webm", ".m4v"],
                    "target_dir": "Videos"
                },
                "audio": {
                    "extensions": [".mp3", ".wav", ".flac", ".aac", ".ogg", ".wma", ".m4a"],
                    "target_dir": "Audio"
                },
                "archives": {
                    "extensions": [".zip", ".rar", ".7z", ".tar", ".gz", ".bz2", ".xz"],
                    "target_dir": "Archives"
                },
                "programs": {
                    "extensions": [".exe", ".msi", ".dmg", ".pkg", ".deb", ".rpm", ".apk"],
                    "target_dir": "Programs"
                },
                "others": {
                    "extensions": [],
                    "target_dir": "Others"
                }
            },
            "schedule": {
                "enabled": False,
                "interval": {
                    "type": "daily",
                    "value": "00:00"
                }
            },
            "logging": {
                "log_dir": "logs",
                "log_level": "INFO",
                "max_log_size": 10485760,
                "backup_count": 5
            }
        }

    def get_config(self) -> Dict[str, Any]:
        """
        获取当前配置

        Returns:
            配置字典的副本
        """
        return self.config.copy()

    def set_config(self, key: str, value: Any) -> None:
        """
        设置配置项

        Args:
            key: 配置键，支持点号分隔的嵌套键（如 "schedule.enabled"）
            value: 配置值
        """
        keys = key.split(".")
        config = self.config
        for k in keys[:-1]:
            if k not in config:
                config[k] = {}
            config = config[k]
        config[keys[-1]] = value

    def get(self, key: str, default: Any = None) -> Any:
        """
        获取配置项

        Args:
            key: 配置键，支持点号分隔的嵌套键
            default: 默认值，如果键不存在则返回该值

        Returns:
            配置值或默认值
        """
        keys = key.split(".")
        config = self.config
        for k in keys:
            if not isinstance(config, dict) or k not in config:
                return default
            config = config[k]
        return config

    def save_config(self, path: Optional[str] = None) -> None:
        """
        保存配置到文件

        Args:
            path: 保存路径，如果为None则使用初始化时的路径
        """
        save_path = path or self.config_path
        os.makedirs(os.path.dirname(save_path), exist_ok=True)
        with open(save_path, "w", encoding="utf-8") as f:
            json.dump(self.config, f, ensure_ascii=False, indent=4)

    def add_category(self, name: str, extensions: list, target_dir: str) -> None:
        """
        添加新的文件分类

        Args:
            name: 分类名称
            extensions: 该分类对应的文件扩展名列表
            target_dir: 目标目录名称
        """
        if "categories" not in self.config:
            self.config["categories"] = {}
        self.config["categories"][name] = {
            "extensions": extensions,
            "target_dir": target_dir
        }

    def remove_category(self, name: str) -> bool:
        """
        删除文件分类

        Args:
            name: 要删除的分类名称

        Returns:
            是否成功删除
        """
        if "categories" in self.config and name in self.config["categories"]:
            del self.config["categories"][name]
            return True
        return False

    def validate_config(self) -> bool:
        """
        验证配置是否有效

        Returns:
            配置是否有效
        """
        required_keys = ["categories"]
        for key in required_keys:
            if key not in self.config:
                return False
        
        if not isinstance(self.config["categories"], dict):
            return False
        
        for category_name, category_config in self.config["categories"].items():
            if not isinstance(category_config, dict):
                return False
            if "extensions" not in category_config or "target_dir" not in category_config:
                return False
            if not isinstance(category_config["extensions"], list):
                return False
        
        return True
