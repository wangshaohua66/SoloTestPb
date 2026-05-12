"""
告警服务单元测试
测试邮件和Webhook告警发送逻辑
"""

import pytest
from unittest.mock import patch, MagicMock, call

from core.config import Config
from core.services.alert_service import AlertService


class TestAlertService:
    """
    告警服务测试类
    """

    def test_init_alert_service_disabled(self):
        """
        测试初始化告警服务（默认禁用）
        """
        config = Config()
        alert_service = AlertService(config)
        
        assert alert_service.config == config
        assert alert_service.enabled is False

    def test_init_alert_service_enabled(self):
        """
        测试初始化告警服务（启用）
        """
        config = Config({
            "alert": {
                "enabled": True,
            }
        })
        alert_service = AlertService(config)
        
        assert alert_service.enabled is True

    def test_send_alert_disabled(self):
        """
        测试告警功能禁用时不发送告警
        """
        config = Config({
            "alert": {
                "enabled": False,
            }
        })
        alert_service = AlertService(config)
        
        result = alert_service.send_alert("测试消息", "测试标题")
        
        assert result is False

    def test_send_alert_no_configured(self):
        """
        测试告警功能启用但未配置任何告警方式
        """
        config = Config({
            "alert": {
                "enabled": True,
            }
        })
        alert_service = AlertService(config)
        
        result = alert_service.send_alert("测试消息", "测试标题")
        
        assert result is False

    def test_email_configured(self):
        """
        测试检查邮件配置是否完整
        """
        config = Config({
            "alert": {
                "enabled": True,
                "email": {
                    "smtp_server": "smtp.example.com",
                    "sender": "alert@example.com",
                    "recipients": ["admin@example.com"],
                }
            }
        })
        alert_service = AlertService(config)
        
        assert alert_service._email_configured() is True

    def test_email_not_configured_missing_server(self):
        """
        测试检查邮件配置不完整（缺少SMTP服务器）
        """
        config = Config({
            "alert": {
                "enabled": True,
                "email": {
                    "sender": "alert@example.com",
                    "recipients": ["admin@example.com"],
                }
            }
        })
        alert_service = AlertService(config)
        
        assert alert_service._email_configured() is False

    def test_email_not_configured_missing_sender(self):
        """
        测试检查邮件配置不完整（缺少发件人）
        """
        config = Config({
            "alert": {
                "enabled": True,
                "email": {
                    "smtp_server": "smtp.example.com",
                    "recipients": ["admin@example.com"],
                }
            }
        })
        alert_service = AlertService(config)
        
        assert alert_service._email_configured() is False

    def test_email_not_configured_missing_recipients(self):
        """
        测试检查邮件配置不完整（缺少收件人）
        """
        config = Config({
            "alert": {
                "enabled": True,
                "email": {
                    "smtp_server": "smtp.example.com",
                    "sender": "alert@example.com",
                    "recipients": [],
                }
            }
        })
        alert_service = AlertService(config)
        
        assert alert_service._email_configured() is False

    def test_webhook_configured(self):
        """
        测试检查Webhook配置是否完整
        """
        config = Config({
            "alert": {
                "enabled": True,
                "webhook": {
                    "url": "https://example.com/webhook",
                }
            }
        })
        alert_service = AlertService(config)
        
        assert alert_service._webhook_configured() is True

    def test_webhook_not_configured(self):
        """
        测试检查Webhook配置不完整
        """
        config = Config({
            "alert": {
                "enabled": True,
                "webhook": {
                    "url": "",
                }
            }
        })
        alert_service = AlertService(config)
        
        assert alert_service._webhook_configured() is False

    @patch('smtplib.SMTP')
    def test_send_email_alert_success(self, mock_smtp):
        """
        测试发送邮件告警成功
        """
        config = Config({
            "alert": {
                "enabled": True,
                "email": {
                    "smtp_server": "smtp.example.com",
                    "smtp_port": 587,
                    "sender": "alert@example.com",
                    "recipients": ["admin@example.com", "dev@example.com"],
                    "username": "alert@example.com",
                    "password": "password123",
                }
            }
        })
        alert_service = AlertService(config)
        
        result = alert_service._send_email_alert("测试消息内容", "测试标题")
        
        assert result is True
        mock_smtp.assert_called_once_with("smtp.example.com", 587)
        
        mock_server = mock_smtp.return_value.__enter__.return_value
        mock_server.starttls.assert_called_once()
        mock_server.login.assert_called_once_with("alert@example.com", "password123")
        mock_server.sendmail.assert_called_once()

    @patch('smtplib.SMTP')
    def test_send_email_alert_no_auth(self, mock_smtp):
        """
        测试发送邮件告警（无需认证）
        """
        config = Config({
            "alert": {
                "enabled": True,
                "email": {
                    "smtp_server": "smtp.example.com",
                    "smtp_port": 587,
                    "sender": "alert@example.com",
                    "recipients": ["admin@example.com"],
                }
            }
        })
        alert_service = AlertService(config)
        
        result = alert_service._send_email_alert("测试消息", "测试标题")
        
        assert result is True
        
        mock_server = mock_smtp.return_value.__enter__.return_value
        mock_server.login.assert_not_called()

    @patch('smtplib.SMTP')
    def test_send_email_alert_failure(self, mock_smtp):
        """
        测试发送邮件告警失败
        """
        config = Config({
            "alert": {
                "enabled": True,
                "email": {
                    "smtp_server": "smtp.example.com",
                    "sender": "alert@example.com",
                    "recipients": ["admin@example.com"],
                }
            }
        })
        
        mock_smtp.side_effect = Exception("连接失败")
        alert_service = AlertService(config)
        
        result = alert_service._send_email_alert("测试消息", "测试标题")
        
        assert result is False

    @patch('urllib.request.urlopen')
    def test_send_webhook_alert_success(self, mock_urlopen):
        """
        测试发送Webhook告警成功
        """
        config = Config({
            "alert": {
                "enabled": True,
                "webhook": {
                    "url": "https://example.com/webhook",
                    "headers": {"X-Custom-Header": "value"},
                }
            }
        })
        
        mock_response = MagicMock()
        mock_response.getcode.return_value = 200
        mock_urlopen.return_value.__enter__.return_value = mock_response
        
        alert_service = AlertService(config)
        result = alert_service._send_webhook_alert("测试消息内容", "测试标题")
        
        assert result is True
        mock_urlopen.assert_called_once()

    @patch('urllib.request.urlopen')
    def test_send_webhook_alert_status_error(self, mock_urlopen):
        """
        测试发送Webhook告警返回错误状态码
        """
        config = Config({
            "alert": {
                "enabled": True,
                "webhook": {
                    "url": "https://example.com/webhook",
                }
            }
        })
        
        mock_response = MagicMock()
        mock_response.getcode.return_value = 500
        mock_urlopen.return_value.__enter__.return_value = mock_response
        
        alert_service = AlertService(config)
        result = alert_service._send_webhook_alert("测试消息", "测试标题")
        
        assert result is False

    @patch('urllib.request.urlopen')
    def test_send_webhook_alert_network_error(self, mock_urlopen):
        """
        测试发送Webhook告警网络错误
        """
        import urllib.error
        
        config = Config({
            "alert": {
                "enabled": True,
                "webhook": {
                    "url": "https://example.com/webhook",
                }
            }
        })
        
        mock_urlopen.side_effect = urllib.error.URLError("网络错误")
        alert_service = AlertService(config)
        
        result = alert_service._send_webhook_alert("测试消息", "测试标题")
        
        assert result is False

    @patch('urllib.request.urlopen')
    def test_send_webhook_alert_exception(self, mock_urlopen):
        """
        测试发送Webhook告警异常
        """
        config = Config({
            "alert": {
                "enabled": True,
                "webhook": {
                    "url": "https://example.com/webhook",
                }
            }
        })
        
        mock_urlopen.side_effect = Exception("未知错误")
        alert_service = AlertService(config)
        
        result = alert_service._send_webhook_alert("测试消息", "测试标题")
        
        assert result is False

    def test_send_alert_email_only(self):
        """
        测试发送告警（仅配置邮件）
        """
        config = Config({
            "alert": {
                "enabled": True,
                "email": {
                    "smtp_server": "smtp.example.com",
                    "sender": "alert@example.com",
                    "recipients": ["admin@example.com"],
                }
            }
        })
        
        alert_service = AlertService(config)
        
        with patch.object(alert_service, '_send_email_alert', return_value=True) as mock_email:
            result = alert_service.send_alert("测试消息", "测试标题")
            
            assert result is True
            mock_email.assert_called_once_with("测试消息", "测试标题")

    def test_send_alert_webhook_only(self):
        """
        测试发送告警（仅配置Webhook）
        """
        config = Config({
            "alert": {
                "enabled": True,
                "webhook": {
                    "url": "https://example.com/webhook",
                }
            }
        })
        
        alert_service = AlertService(config)
        
        with patch.object(alert_service, '_send_webhook_alert', return_value=True) as mock_webhook:
            result = alert_service.send_alert("测试消息", "测试标题")
            
            assert result is True
            mock_webhook.assert_called_once_with("测试消息", "测试标题")

    def test_send_alert_both_email_and_webhook(self):
        """
        测试发送告警（同时配置邮件和Webhook）
        """
        config = Config({
            "alert": {
                "enabled": True,
                "email": {
                    "smtp_server": "smtp.example.com",
                    "sender": "alert@example.com",
                    "recipients": ["admin@example.com"],
                },
                "webhook": {
                    "url": "https://example.com/webhook",
                }
            }
        })
        
        alert_service = AlertService(config)
        
        with patch.object(alert_service, '_send_email_alert', return_value=True) as mock_email, \
             patch.object(alert_service, '_send_webhook_alert', return_value=True) as mock_webhook:
            
            result = alert_service.send_alert("测试消息", "测试标题")
            
            assert result is True
            mock_email.assert_called_once()
            mock_webhook.assert_called_once()

    def test_send_task_failure_alert(self):
        """
        测试发送任务失败告警
        """
        config = Config({
            "alert": {
                "enabled": True,
                "email": {
                    "smtp_server": "smtp.example.com",
                    "sender": "alert@example.com",
                    "recipients": ["admin@example.com"],
                }
            }
        })
        
        alert_service = AlertService(config)
        
        with patch.object(alert_service, 'send_alert', return_value=True) as mock_send:
            result = alert_service.send_task_failure_alert(
                task_name="测试任务",
                task_id="task-123",
                error_message="测试错误",
                retry_count=2,
            )
            
            assert result is True
            mock_send.assert_called_once()
            call_args = mock_send.call_args
            assert "测试任务" in call_args[0][0]
            assert "task-123" in call_args[0][0]
            assert "测试错误" in call_args[0][0]
            assert "2" in call_args[0][0]

    def test_get_current_timestamp(self):
        """
        测试获取当前时间戳
        """
        from datetime import datetime
        
        timestamp = AlertService._get_current_timestamp()
        
        assert isinstance(timestamp, str)
        parsed = datetime.fromisoformat(timestamp)
        assert isinstance(parsed, datetime)
