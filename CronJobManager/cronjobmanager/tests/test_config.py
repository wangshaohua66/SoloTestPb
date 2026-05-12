"""
配置管理模块单元测试
"""

import pytest
from core.config import Config


class TestConfig:
    """
    配置管理类测试
    """

    def test_init_default_config(self):
        """
        测试默认配置初始化
        """
        config = Config()
        
        assert config.get("database.url") is not None
        assert config.get("scheduler.timezone") == "Asia/Shanghai"
        assert config.get("scheduler.max_concurrent_jobs") == 100

    def test_init_with_overrides(self):
        """
        测试带覆盖配置的初始化
        """
        overrides = {
            "scheduler": {
                "timezone": "UTC",
                "max_concurrent_jobs": 50,
            }
        }
        config = Config(overrides)
        
        assert config.get("scheduler.timezone") == "UTC"
        assert config.get("scheduler.max_concurrent_jobs") == 50

    def test_get_nested_key(self):
        """
        测试获取嵌套配置值
        """
        config = Config()
        
        assert config.get("scheduler.timezone") is not None
        assert config.get("logging.level") is not None

    def test_get_with_default(self):
        """
        测试获取配置值时使用默认值
        """
        config = Config()
        
        assert config.get("non.existent.key", "default_value") == "default_value"

    def test_set_nested_key(self):
        """
        测试设置嵌套配置值
        """
        config = Config()
        
        config.set("new.nested.key", "test_value")
        assert config.get("new.nested.key") == "test_value"

    def test_update_config(self):
        """
        测试批量更新配置
        """
        config = Config()
        
        config.update({
            "scheduler": {
                "timezone": "America/New_York",
            },
            "new_section": {
                "key": "value",
            },
        })
        
        assert config.get("scheduler.timezone") == "America/New_York"
        assert config.get("new_section.key") == "value"

    def test_to_dict(self):
        """
        测试转换为字典
        """
        config = Config()
        config_dict = config.to_dict()
        
        assert isinstance(config_dict, dict)
        assert "database" in config_dict
        assert "scheduler" in config_dict

    def test_deep_update(self):
        """
        测试深度更新配置
        """
        config = Config({
            "level1": {
                "level2": {
                    "key1": "value1",
                    "key2": "value2",
                }
            }
        })
        
        config.update({
            "level1": {
                "level2": {
                    "key1": "updated_value",
                    "key3": "new_value",
                }
            }
        })
        
        assert config.get("level1.level2.key1") == "updated_value"
        assert config.get("level1.level2.key2") == "value2"
        assert config.get("level1.level2.key3") == "new_value"
