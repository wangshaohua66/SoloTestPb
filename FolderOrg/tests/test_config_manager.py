"""
配置管理模块单元测试
"""

import os
import json
import tempfile
import pytest
from folder_organizer.config_manager import ConfigManager


class TestConfigManager:
    """
    配置管理器测试类
    """

    def test_init_default_path(self):
        """
        测试使用默认路径初始化
        """
        manager = ConfigManager()
        assert manager.config_path is not None
        assert os.path.exists(manager.config_path)

    def test_init_custom_path(self, temp_dir):
        """
        测试使用自定义路径初始化
        """
        config_path = os.path.join(temp_dir, "test_config.json")
        manager = ConfigManager(config_path)
        assert manager.config_path == config_path
        assert os.path.exists(config_path)

    def test_get_default_config(self):
        """
        测试获取默认配置
        """
        manager = ConfigManager()
        config = manager.get_config()
        assert "categories" in config
        assert "schedule" in config
        assert "logging" in config

    def test_set_and_get_config(self, temp_dir):
        """
        测试设置和获取配置
        """
        config_path = os.path.join(temp_dir, "test_config.json")
        manager = ConfigManager(config_path)
        
        manager.set_config("schedule.enabled", True)
        assert manager.get("schedule.enabled") is True
        
        manager.set_config("custom.key", "test_value")
        assert manager.get("custom.key") == "test_value"

    def test_get_default_value(self, temp_dir):
        """
        测试获取不存在的键时返回默认值
        """
        config_path = os.path.join(temp_dir, "test_config.json")
        manager = ConfigManager(config_path)
        
        assert manager.get("non.existent.key", "default") == "default"
        assert manager.get("non.existent.key") is None

    def test_add_category(self, temp_dir):
        """
        测试添加新分类
        """
        config_path = os.path.join(temp_dir, "test_config.json")
        manager = ConfigManager(config_path)
        
        manager.add_category("ebooks", [".epub", ".mobi"], "EBooks")
        categories = manager.get("categories", {})
        
        assert "ebooks" in categories
        assert categories["ebooks"]["extensions"] == [".epub", ".mobi"]
        assert categories["ebooks"]["target_dir"] == "EBooks"

    def test_remove_category(self, temp_dir):
        """
        测试删除分类
        """
        config_path = os.path.join(temp_dir, "test_config.json")
        manager = ConfigManager(config_path)
        
        manager.add_category("test_cat", [".test"], "TestDir")
        assert manager.remove_category("test_cat") is True
        assert manager.remove_category("non_existent") is False

    def test_validate_config_valid(self, temp_dir):
        """
        测试验证有效配置
        """
        config_path = os.path.join(temp_dir, "test_config.json")
        manager = ConfigManager(config_path)
        
        assert manager.validate_config() is True

    def test_validate_config_invalid(self, temp_dir):
        """
        测试验证无效配置
        """
        config_path = os.path.join(temp_dir, "test_config.json")
        manager = ConfigManager(config_path)
        
        manager.config = {"invalid": "config"}
        assert manager.validate_config() is False

    def test_save_and_load_config(self, temp_dir):
        """
        测试保存和加载配置
        """
        config_path = os.path.join(temp_dir, "test_config.json")
        manager = ConfigManager(config_path)
        
        manager.set_config("test.key", "test_value")
        manager.save_config()
        
        new_manager = ConfigManager(config_path)
        assert new_manager.get("test.key") == "test_value"

    def test_config_persistence(self, temp_dir):
        """
        测试配置持久化
        """
        config_path = os.path.join(temp_dir, "test_config.json")
        manager = ConfigManager(config_path)
        
        manager.add_category("temp", [".tmp"], "TempFiles")
        manager.set_config("schedule.enabled", True)
        manager.save_config()
        
        with open(config_path, "r", encoding="utf-8") as f:
            saved_config = json.load(f)
        
        assert "temp" in saved_config["categories"]
        assert saved_config["schedule"]["enabled"] is True
