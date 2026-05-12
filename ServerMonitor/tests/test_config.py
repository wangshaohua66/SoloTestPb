# -*- coding: utf-8 -*-
"""
配置模块单元测试
"""

import os
import json
import allure
import pytest
from monitor.config import Config


@allure.feature("配置管理模块")
class TestConfig:
    """配置类测试"""

    @allure.story("配置创建测试")
    @allure.title("测试默认配置文件创建")
    def test_default_config_creation(self, tmp_path):
        """测试默认配置文件创建"""
        config_path = tmp_path / "default_config.json"
        config = Config(str(config_path))

        assert os.path.exists(config_path)
        assert config.interval == 1
        assert config.cpu_threshold == 80.0
        assert config.memory_threshold == 80.0

    @allure.story("配置加载测试")
    @allure.title("测试加载用户配置")
    def test_load_user_config(self, temp_config_file):
        """测试加载用户配置"""
        config = Config(temp_config_file)

        assert config.interval == 2
        assert config.cpu_threshold == 70.0
        assert config.memory_threshold == 75.0
        assert config.get("smtp.enabled") is True
        assert config.get("smtp.server") == "smtp.test.com"

    @allure.story("配置获取测试")
    @allure.title("测试获取默认值")
    def test_get_default_value(self, temp_config_file):
        """测试获取默认值"""
        config = Config(temp_config_file)

        assert config.get("non_existent_key", "default") == "default"
        assert config.get("disk_threshold") == 85.0

    @allure.story("配置设置测试")
    @allure.title("测试设置配置值")
    def test_set_config_value(self, temp_config_file):
        """测试设置配置值"""
        config = Config(temp_config_file)
        config.set("cpu_threshold", 90.0)
        config.set("new_key.sub_key", "value")

        assert config.get("cpu_threshold") == 90.0
        assert config.get("new_key.sub_key") == "value"

    @allure.story("配置保存测试")
    @allure.title("测试保存配置")
    def test_save_config(self, temp_config_file):
        """测试保存配置"""
        config = Config(temp_config_file)
        config.set("test_key", "test_value")
        config.save()

        new_config = Config(temp_config_file)
        assert new_config.get("test_key") == "test_value"

    @allure.story("配置属性测试")
    @allure.title("测试阈值属性")
    def test_threshold_properties(self, temp_config_file):
        """测试阈值属性"""
        config = Config(temp_config_file)

        assert isinstance(config.cpu_threshold, float)
        assert isinstance(config.memory_threshold, float)
        assert isinstance(config.disk_threshold, float)
        assert isinstance(config.network_threshold, float)

    @allure.story("配置异常测试")
    @allure.title("测试无效配置文件")
    def test_invalid_config_file(self, tmp_path):
        """测试无效配置文件"""
        invalid_path = tmp_path / "invalid.json"
        with open(invalid_path, "w", encoding="utf-8") as f:
            f.write("invalid json content")

        config = Config(str(invalid_path))
        assert config.interval == 1


@pytest.fixture
def temp_config_file(tmp_path):
    """创建临时配置文件"""
    config_path = tmp_path / "test_config.json"
    config_data = {
        "interval": 2,
        "cpu_threshold": 70.0,
        "memory_threshold": 75.0,
        "smtp": {
            "enabled": True,
            "server": "smtp.test.com"
        }
    }
    with open(config_path, "w", encoding="utf-8") as f:
        json.dump(config_data, f)
    return str(config_path)
