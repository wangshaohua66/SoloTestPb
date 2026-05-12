"""
CLI模块单元测试
"""

import allure

from batch_mail.cli import build_retry_config_dict, build_smtp_config_dict


@allure.feature("命令行接口")
@allure.story("配置字典构建")
class TestBuildConfigDict:
    """
    配置字典构建测试类
    """

    @allure.title("测试构建SMTP配置字典")
    def test_build_smtp_config_dict(self):
        """
        测试构建SMTP配置字典
        """
        from argparse import Namespace

        args = Namespace(
            smtp_host="smtp.example.com",
            smtp_port=465,
            smtp_username="user@example.com",
            smtp_password="secret",
            sender_name="发件人",
            use_tls=True,
            use_ssl=False,
        )

        config = build_smtp_config_dict(args)

        assert config["smtp_host"] == "smtp.example.com"
        assert config["smtp_port"] == "465"
        assert config["smtp_username"] == "user@example.com"
        assert config["smtp_password"] == "secret"
        assert config["sender_name"] == "发件人"
        assert config["smtp_use_tls"] == "True"
        assert config["smtp_use_ssl"] == "False"

    @allure.title("测试构建重试配置字典")
    def test_build_retry_config_dict(self):
        """
        测试构建重试配置字典
        """
        from argparse import Namespace

        args = Namespace(
            max_retries=5,
            retry_delay=1.5,
        )

        config = build_retry_config_dict(args)

        assert config["max_retries"] == "5"
        assert config["retry_delay"] == "1.5"

    @allure.title("测试None值处理")
    def test_none_values_not_included(self):
        """
        测试None值不会被包含在配置字典中
        """
        from argparse import Namespace

        args = Namespace(
            smtp_host=None,
            smtp_port=None,
            smtp_username=None,
            smtp_password=None,
            sender_name=None,
            use_tls=True,
            use_ssl=False,
        )

        config = build_smtp_config_dict(args)

        assert "smtp_host" not in config
        assert "smtp_port" not in config
        assert "smtp_username" not in config
        assert "smtp_password" not in config
        assert "sender_name" not in config
