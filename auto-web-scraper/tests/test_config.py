"""
配置管理模块单元测试
"""
import pytest
import os
import json
import tempfile

from auto_web_scraper.config import (
    ConfigLoader,
    ScraperConfig,
    SelectorConfig,
    LoginConfig,
    PaginationConfig,
    RequestConfig,
    RateLimitConfig,
    ProxyConfig,
    ExportConfig,
)


class TestSelectorConfig:
    """
    选择器配置测试类
    """

    def test_selector_config_defaults(self):
        """
        测试选择器配置默认值
        """
        selector = SelectorConfig(name="test", selector=".test")
        assert selector.name == "test"
        assert selector.selector == ".test"
        assert selector.selector_type == "css"
        assert selector.attribute is None
        assert selector.is_list is False
        assert selector.default_value is None

    def test_selector_config_custom(self):
        """
        测试选择器配置自定义值
        """
        selector = SelectorConfig(
            name="title",
            selector="//h1",
            selector_type="xpath",
            attribute="data-id",
            is_list=True,
            default_value="N/A",
        )
        assert selector.name == "title"
        assert selector.selector == "//h1"
        assert selector.selector_type == "xpath"
        assert selector.attribute == "data-id"
        assert selector.is_list is True
        assert selector.default_value == "N/A"


class TestConfigLoader:
    """
    配置加载器测试类
    """

    def test_from_dict_basic(self):
        """
        测试从字典加载基本配置
        """
        config_dict = {
            "name": "test_scraper",
            "start_urls": ["https://example.com"],
            "selectors": [
                {
                    "name": "title",
                    "selector": "h1",
                    "selector_type": "css",
                }
            ],
        }

        config = ConfigLoader.from_dict(config_dict)

        assert config.name == "test_scraper"
        assert config.start_urls == ["https://example.com"]
        assert len(config.selectors) == 1
        assert config.selectors[0].name == "title"

    def test_from_dict_with_all_sections(self):
        """
        测试从字典加载所有配置段
        """
        config_dict = {
            "name": "full_test",
            "start_urls": ["https://example.com/page1"],
            "selectors": [
                {"name": "title", "selector": "h1", "selector_type": "css"}
            ],
            "login": {
                "login_url": "https://example.com/login",
                "username": "user",
                "password": "pass",
            },
            "pagination": {
                "enabled": True,
                "max_pages": 5,
            },
            "request": {
                "timeout": 60,
                "headers": {"X-Custom": "value"},
            },
            "rate_limit": {
                "min_delay": 2.0,
                "max_delay": 5.0,
            },
            "proxy": {
                "enabled": True,
                "proxies": ["http://proxy1:8080"],
            },
            "export": {
                "formats": ["json", "csv"],
                "output_dir": "./custom_output",
            },
            "retry_times": 5,
            "retry_delay": 3.0,
        }

        config = ConfigLoader.from_dict(config_dict)

        assert config.name == "full_test"
        assert config.login is not None
        assert config.login.username == "user"
        assert config.pagination.enabled is True
        assert config.pagination.max_pages == 5
        assert config.request.timeout == 60
        assert config.rate_limit.min_delay == 2.0
        assert config.proxy.enabled is True
        assert config.export.formats == ["json", "csv"]
        assert config.retry_times == 5

    def test_from_json(self):
        """
        测试从JSON文件加载配置
        """
        config_dict = {
            "name": "json_test",
            "start_urls": ["https://test.com"],
            "selectors": [{"name": "name", "selector": ".name"}],
        }

        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".json", delete=False, encoding="utf-8"
        ) as f:
            json.dump(config_dict, f)
            temp_path = f.name

        try:
            config = ConfigLoader.from_json(temp_path)
            assert config.name == "json_test"
            assert config.start_urls == ["https://test.com"]
        finally:
            os.unlink(temp_path)

    def test_from_yaml(self):
        """
        测试从YAML文件加载配置
        """
        yaml_content = """
name: yaml_test
start_urls:
  - https://test.com
selectors:
  - name: title
    selector: h1
    selector_type: css
"""

        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".yaml", delete=False, encoding="utf-8"
        ) as f:
            f.write(yaml_content)
            temp_path = f.name

        try:
            config = ConfigLoader.from_yaml(temp_path)
            assert config.name == "yaml_test"
            assert config.start_urls == ["https://test.com"]
        finally:
            os.unlink(temp_path)


class TestScraperConfigDefault:
    """
    采集器配置默认值测试类
    """

    def test_default_config(self):
        """
        测试默认配置
        """
        config = ScraperConfig()

        assert config.name == "default"
        assert config.start_urls == []
        assert config.selectors == []
        assert config.login is None
        assert isinstance(config.pagination, PaginationConfig)
        assert isinstance(config.request, RequestConfig)
        assert isinstance(config.rate_limit, RateLimitConfig)
        assert isinstance(config.proxy, ProxyConfig)
        assert isinstance(config.export, ExportConfig)
        assert config.retry_times == 3
        assert config.retry_delay == 2.0
