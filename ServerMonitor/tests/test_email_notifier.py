# -*- coding: utf-8 -*-
"""
邮件通知模块单元测试
"""

import pytest
import allure
import smtplib
from unittest.mock import patch, MagicMock
from monitor.notifier.email_notifier import EmailNotifier


@allure.feature("邮件通知模块")
class TestEmailNotifier:
    """邮件通知类测试"""

    @pytest.fixture
    def mock_config(self):
        """创建模拟配置"""
        config = MagicMock()
        config.get.side_effect = lambda key, default=None: {
            "smtp.enabled": True,
            "smtp.server": "smtp.test.com",
            "smtp.port": 587,
            "smtp.username": "test@test.com",
            "smtp.password": "password123",
            "smtp.from_email": "monitor@test.com",
            "smtp.to_emails": ["admin@test.com", "user@test.com"],
            "smtp.use_tls": True
        }.get(key, default)
        return config

    @pytest.fixture
    def email_notifier(self, mock_config):
        """创建邮件通知器实例"""
        return EmailNotifier(mock_config)

    @allure.story("邮件启用测试")
    @allure.title("测试邮件通知是否启用")
    def test_is_enabled(self, email_notifier):
        """测试邮件通知是否启用"""
        assert email_notifier.is_enabled() is True

    @allure.story("邮件发送测试")
    @allure.title("测试发送告警邮件")
    @patch('smtplib.SMTP')
    def test_send_alert(self, mock_smtp, email_notifier):
        """测试发送告警邮件"""
        mock_server = MagicMock()
        mock_smtp.return_value = mock_server

        alerts = [
            {
                "type": "cpu",
                "level": "warning",
                "threshold": 80.0,
                "current": 90.0,
                "message": "CPU使用率过高"
            }
        ]

        result = email_notifier.send_alert(alerts)

        assert result is True
        mock_smtp.assert_called_once_with("smtp.test.com", 587)
        mock_server.starttls.assert_called_once()
        mock_server.login.assert_called_once_with("test@test.com", "password123")
        mock_server.sendmail.assert_called_once()
        mock_server.quit.assert_called_once()

    @allure.story("邮件发送测试")
    @allure.title("测试发送报告邮件")
    @patch('smtplib.SMTP')
    def test_send_report(self, mock_smtp, email_notifier):
        """测试发送报告邮件"""
        mock_server = MagicMock()
        mock_smtp.return_value = mock_server

        result = email_notifier.send_report("./reports/report1")

        assert result is True
        mock_smtp.assert_called_once_with("smtp.test.com", 587)

    @allure.story("邮件发送测试")
    @allure.title("测试空告警列表不发送邮件")
    def test_send_alert_empty(self, email_notifier):
        """测试空告警列表不发送邮件"""
        alerts = []
        result = email_notifier.send_alert(alerts)

        assert result is False

    @allure.story("连接测试")
    @allure.title("测试SMTP服务器连接")
    @patch('smtplib.SMTP')
    def test_test_connection(self, mock_smtp, email_notifier):
        """测试SMTP服务器连接"""
        mock_server = MagicMock()
        mock_smtp.return_value = mock_server

        result = email_notifier.test_connection()

        assert result is True
        mock_smtp.assert_called_once_with("smtp.test.com", 587)
        mock_server.starttls.assert_called_once()
        mock_server.login.assert_called_once_with("test@test.com", "password123")
        mock_server.quit.assert_called_once()

    @allure.story("异常处理测试")
    @allure.title("测试SMTP认证失败处理")
    @patch('smtplib.SMTP')
    def test_authentication_failure(self, mock_smtp, email_notifier):
        """测试SMTP认证失败处理"""
        mock_server = MagicMock()
        mock_server.login.side_effect = smtplib.SMTPAuthenticationError(535, "Authentication failed")
        mock_smtp.return_value = mock_server

        result = email_notifier.test_connection()

        assert result is False

    @allure.story("异常处理测试")
    @allure.title("测试SMTP连接失败处理")
    @patch('smtplib.SMTP')
    def test_connection_failure(self, mock_smtp, email_notifier):
        """测试SMTP连接失败处理"""
        mock_smtp.side_effect = smtplib.SMTPConnectError(421, "Service not available")

        result = email_notifier.test_connection()

        assert result is False

    @allure.story("异常处理测试")
    @allure.title("测试发送邮件时的一般异常处理")
    @patch('smtplib.SMTP')
    def test_send_alert_exception(self, mock_smtp, email_notifier):
        """测试发送邮件时的一般异常处理"""
        mock_server = MagicMock()
        mock_server.sendmail.side_effect = Exception("Test exception")
        mock_smtp.return_value = mock_server

        alerts = [
            {
                "type": "cpu",
                "level": "warning",
                "message": "Test alert"
            }
        ]

        result = email_notifier.send_alert(alerts)

        assert result is False

    @allure.story("SSL连接测试")
    @allure.title("测试SSL加密连接")
    @patch('smtplib.SMTP_SSL')
    def test_ssl_connection(self, mock_smtp_ssl):
        """测试SSL加密连接"""
        config = MagicMock()
        config.get.side_effect = lambda key, default=None: {
            "smtp.enabled": True,
            "smtp.server": "smtp.test.com",
            "smtp.port": 465,
            "smtp.username": "test@test.com",
            "smtp.password": "password123",
            "smtp.from_email": "monitor@test.com",
            "smtp.to_emails": ["admin@test.com"],
            "smtp.use_tls": False
        }.get(key, default)

        notifier = EmailNotifier(config)
        mock_server = MagicMock()
        mock_smtp_ssl.return_value = mock_server

        result = notifier.test_connection()

        assert result is True
        mock_smtp_ssl.assert_called_once_with("smtp.test.com", 465)

    @allure.story("禁用测试")
    @allure.title("测试邮件通知禁用时不发送邮件")
    def test_disabled_email_notifier(self):
        """测试邮件通知禁用时不发送邮件"""
        config = MagicMock()
        config.get.side_effect = lambda key, default=None: {
            "smtp.enabled": False
        }.get(key, default)

        notifier = EmailNotifier(config)

        assert notifier.is_enabled() is False

        alerts = [{"type": "cpu", "level": "warning", "message": "Test"}]
        result = notifier.send_alert(alerts)

        assert result is False

    @allure.story("告警邮件构建测试")
    @allure.title("测试构建告警邮件内容")
    def test_build_alert_body(self, email_notifier):
        """测试构建告警邮件内容"""
        alerts = [
            {
                "type": "cpu",
                "level": "warning",
                "threshold": 80.0,
                "current": 90.0,
                "message": "CPU使用率过高"
            },
            {
                "type": "memory",
                "level": "warning",
                "threshold": 75.0,
                "current": 85.0,
                "message": "内存使用率过高"
            }
        ]

        body = email_notifier._build_alert_body(alerts)

        assert "CPU" in body
        assert "MEMORY" in body
        assert "warning" in body
        assert "90.0" in body
        assert "85.0" in body
        assert "请及时处理" in body
