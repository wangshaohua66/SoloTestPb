"""
配置管理模块单元测试
"""

import allure
import pytest

from batch_mail.config.settings import (
    RetryConfig,
    SMTPConfig,
    load_retry_config,
    load_smtp_config,
)


@allure.feature("配置管理")
@allure.story("SMTP配置")
class TestSMTPConfig:
    """
    SMTPConfig测试类
    """

    @allure.title("测试SMTP配置初始化")
    def test_smtp_config_init(self):
        """
        测试SMTPConfig正常初始化
        """
        config = SMTPConfig(
            host="smtp.example.com",
            port=465,
            username="test@example.com",
            password="secret",
        )

        assert config.host == "smtp.example.com"
        assert config.port == 465
        assert config.username == "test@example.com"
        assert config.password == "secret"
        assert config.use_tls is True
        assert config.use_ssl is False
        assert config.timeout == 30

    @allure.title("测试SMTP配置自定义参数")
    def test_smtp_config_custom_params(self):
        """
        测试SMTPConfig自定义参数
        """
        config = SMTPConfig(
            host="smtp.gmail.com",
            port=587,
            username="user@gmail.com",
            password="pass",
            use_tls=True,
            use_ssl=False,
            timeout=60,
            sender_name="Test User",
        )

        assert config.host == "smtp.gmail.com"
        assert config.port == 587
        assert config.sender_name == "Test User"
        assert config.timeout == 60

    @allure.title("测试SMTP配置缺少host抛出异常")
    def test_smtp_config_missing_host(self):
        """
        测试缺少host时抛出ValueError
        """
        with pytest.raises(ValueError) as exc_info:
            SMTPConfig(
                host="",
                port=465,
                username="test@example.com",
                password="secret",
            )
        assert "SMTP服务器地址不能为空" in str(exc_info.value)

    @allure.title("测试SMTP配置缺少username抛出异常")
    def test_smtp_config_missing_username(self):
        """
        测试缺少username时抛出ValueError
        """
        with pytest.raises(ValueError) as exc_info:
            SMTPConfig(
                host="smtp.example.com",
                port=465,
                username="",
                password="secret",
            )
        assert "SMTP用户名不能为空" in str(exc_info.value)

    @allure.title("测试SMTP配置缺少password抛出异常")
    def test_smtp_config_missing_password(self):
        """
        测试缺少password时抛出ValueError
        """
        with pytest.raises(ValueError) as exc_info:
            SMTPConfig(
                host="smtp.example.com",
                port=465,
                username="test@example.com",
                password="",
            )
        assert "SMTP密码不能为空" in str(exc_info.value)

    @allure.title("测试SMTP配置无效端口抛出异常")
    def test_smtp_config_invalid_port(self):
        """
        测试无效端口时抛出ValueError
        """
        with pytest.raises(ValueError) as exc_info:
            SMTPConfig(
                host="smtp.example.com",
                port=0,
                username="test@example.com",
                password="secret",
            )
        assert "SMTP端口号必须在1-65535之间" in str(exc_info.value)


@allure.feature("配置管理")
@allure.story("重试配置")
class TestRetryConfig:
    """
    RetryConfig测试类
    """

    @allure.title("测试重试配置默认值")
    def test_retry_config_default(self):
        """
        测试RetryConfig默认值
        """
        config = RetryConfig()

        assert config.max_retries == 3
        assert config.retry_delay == 2.0
        assert config.backoff_multiplier == 2.0

    @allure.title("测试重试配置自定义值")
    def test_retry_config_custom(self):
        """
        测试RetryConfig自定义值
        """
        config = RetryConfig(
            max_retries=5,
            retry_delay=1.5,
            backoff_multiplier=1.5,
        )

        assert config.max_retries == 5
        assert config.retry_delay == 1.5
        assert config.backoff_multiplier == 1.5


@allure.feature("配置管理")
@allure.story("配置加载")
class TestLoadConfig:
    """
    配置加载函数测试类
    """

    @allure.title("测试从字典加载SMTP配置")
    def test_load_smtp_config_from_dict(self):
        """
        测试从字典加载SMTP配置
        """
        config_dict = {
            "smtp_host": "smtp.qq.com",
            "smtp_port": "465",
            "smtp_username": "test@qq.com",
            "smtp_password": "qq_auth_code",
            "smtp_use_ssl": "True",
            "sender_name": "发件人",
        }

        config = load_smtp_config(config_dict)

        assert config.host == "smtp.qq.com"
        assert config.port == 465
        assert config.username == "test@qq.com"
        assert config.password == "qq_auth_code"
        assert config.sender_name == "发件人"

    @allure.title("测试从字典加载重试配置")
    def test_load_retry_config_from_dict(self):
        """
        测试从字典加载重试配置
        """
        config_dict = {
            "max_retries": "5",
            "retry_delay": "3.0",
            "backoff_multiplier": "1.5",
        }

        config = load_retry_config(config_dict)

        assert config.max_retries == 5
        assert config.retry_delay == 3.0
        assert config.backoff_multiplier == 1.5

    @allure.title("测试重试配置默认值加载")
    def test_load_retry_config_default(self):
        """
        测试重试配置默认值
        """
        config = load_retry_config({})

        assert config.max_retries == 3
        assert config.retry_delay == 2.0
        assert config.backoff_multiplier == 2.0
