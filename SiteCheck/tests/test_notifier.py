"""
告警通知模块测试
"""

import pytest
from unittest.mock import Mock, patch
from datetime import datetime
from src.notifier import EmailNotifier, WebhookNotifier, NotificationManager
from src.http_checker import CheckResult


class TestEmailNotifier:
    """
    EmailNotifier类测试
    """

    @pytest.fixture
    def email_config(self):
        """邮件配置"""
        return {
            'enabled': True,
            'smtp_server': 'smtp.example.com',
            'smtp_port': 587,
            'use_tls': True,
            'username': 'test@example.com',
            'password': 'password',
            'recipients': ['admin@example.com']
        }

    def test_email_notifier_init(self, email_config):
        """测试邮件通知器初始化"""
        notifier = EmailNotifier(email_config)
        assert notifier.enabled is True
        assert notifier.smtp_server == 'smtp.example.com'

    def test_email_notifier_disabled(self, email_config):
        """测试禁用邮件通知"""
        email_config['enabled'] = False
        notifier = EmailNotifier(email_config)

        result = CheckResult(
            site_name='测试',
            url='https://example.com',
            success=False,
            status_code=500,
            response_time=100,
            error_message='Server error',
            timestamp=datetime.now()
        )

        assert notifier.send_alert(result, 'http') is False

    @patch('smtplib.SMTP')
    def test_send_email_alert(self, mock_smtp, email_config):
        """测试发送邮件告警"""
        mock_server = Mock()
        mock_smtp.return_value.__enter__.return_value = mock_server

        notifier = EmailNotifier(email_config)

        result = CheckResult(
            site_name='测试站点',
            url='https://example.com',
            success=False,
            status_code=500,
            response_time=100,
            error_message='Server error',
            timestamp=datetime.now()
        )

        result = notifier.send_alert(result, 'http')

        assert result is True


class TestWebhookNotifier:
    """
    WebhookNotifier类测试
    """

    @pytest.fixture
    def webhook_config(self):
        """Webhook通知配置"""
        return {
            'enabled': True,
            'url': 'https://webhook.example.com/alert',
            'method': 'POST',
            'headers': {'Content-Type': 'application/json'}
        }

    def test_webhook_notifier_init(self, webhook_config):
        """测试Webhook通知器初始化"""
        notifier = WebhookNotifier(webhook_config)
        assert notifier.enabled is True
        assert notifier.url == 'https://webhook.example.com/alert'

    def test_webhook_notifier_disabled(self, webhook_config):
        """测试禁用Webhook通知"""
        webhook_config['enabled'] = False
        notifier = WebhookNotifier(webhook_config)

        result = CheckResult(
            site_name='测试',
            url='https://example.com',
            success=False,
            status_code=500,
            response_time=100,
            error_message='Server error',
            timestamp=datetime.now()
        )

        assert notifier.send_alert(result, 'http') is False

    @patch('requests.request')
    def test_send_webhook_alert(self, mock_request, webhook_config):
        """测试发送Webhook告警"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_request.return_value = mock_response

        notifier = WebhookNotifier(webhook_config)

        result = CheckResult(
            site_name='测试站点',
            url='https://example.com',
            success=False,
            status_code=500,
            response_time=100,
            error_message='Server error',
            timestamp=datetime.now()
        )

        result = notifier.send_alert(result, 'http')

        assert result is True


class TestNotificationManager:
    """
    NotificationManager类测试
    """

    @pytest.fixture
    def notification_config(self):
        """通知配置"""
        return {
            'email': {
                'enabled': False
            },
            'webhook': {
                'enabled': False
            }
        }

    def test_notification_manager_init(self, notification_config):
        """测试通知管理器初始化"""
        manager = NotificationManager(notification_config)
        assert len(manager.notifiers) == 0

    def test_notification_manager_with_notifiers(self, notification_config):
        """测试带通知器的管理器"""
        notification_config['email']['enabled'] = True
        notification_config['email']['smtp_server'] = 'smtp.example.com'
        notification_config['email']['username'] = 'test@example.com'
        notification_config['email']['password'] = 'password'
        notification_config['email']['recipients'] = ['admin@example.com']

        manager = NotificationManager(notification_config)
        assert len(manager.notifiers) == 1

    def test_notification_manager_with_multiple_notifiers(self, notification_config):
        """测试带多个通知器的管理器"""
        notification_config['email']['enabled'] = True
        notification_config['email']['smtp_server'] = 'smtp.example.com'
        notification_config['email']['username'] = 'test@example.com'
        notification_config['email']['password'] = 'password'
        notification_config['email']['recipients'] = ['admin@example.com']
        
        notification_config['webhook']['enabled'] = True
        notification_config['webhook']['url'] = 'https://webhook.example.com/alert'

        manager = NotificationManager(notification_config)
        assert len(manager.notifiers) == 2

    def test_send_http_alert_without_notifiers(self, notification_config):
        """测试没有通知器时发送HTTP告警"""
        from src.http_checker import CheckResult
        
        manager = NotificationManager(notification_config)
        result = CheckResult(
            site_name='测试站点',
            url='https://example.com',
            success=False,
            status_code=500,
            response_time=100,
            error_message='服务器错误',
            timestamp=datetime.now()
        )
        
        manager.send_http_alert(result)
        assert len(manager.notifiers) == 0

    def test_send_http_alert_with_success_result(self, notification_config):
        """测试成功结果不发送告警"""
        from src.http_checker import CheckResult
        
        notification_config['email']['enabled'] = True
        notification_config['email']['smtp_server'] = 'smtp.example.com'
        notification_config['email']['username'] = 'test@example.com'
        notification_config['email']['password'] = 'password'
        notification_config['email']['recipients'] = ['admin@example.com']
        
        manager = NotificationManager(notification_config)
        result = CheckResult(
            site_name='测试站点',
            url='https://example.com',
            success=True,
            status_code=200,
            response_time=100,
            error_message=None,
            timestamp=datetime.now()
        )
        
        manager.send_http_alert(result)

    def test_notifier_send_alert_exception(self, notification_config):
        """测试通知器发送异常"""
        from src.http_checker import CheckResult
        from src.notifier import Notifier
        
        class FaultyNotifier(Notifier):
            def send_alert(self, result, alert_type):
                raise Exception('发送失败')
        
        manager = NotificationManager(notification_config)
        manager.notifiers = [FaultyNotifier()]
        
        result = CheckResult(
            site_name='测试站点',
            url='https://example.com',
            success=False,
            status_code=500,
            response_time=100,
            error_message='服务器错误',
            timestamp=datetime.now()
        )
        
        manager.send_http_alert(result)

    def test_email_notifier_without_recipients(self, notification_config):
        """测试邮件通知器没有收件人"""
        email_config = {
            'enabled': True,
            'smtp_server': 'smtp.example.com',
            'username': 'test@example.com',
            'password': 'password',
            'recipients': []
        }
        
        from src.notifier import EmailNotifier
        
        notifier = EmailNotifier(email_config)
        result = CheckResult(
            site_name='测试站点',
            url='https://example.com',
            success=False,
            status_code=500,
            response_time=100,
            error_message='服务器错误',
            timestamp=datetime.now()
        )
        
        assert notifier.send_alert(result, 'http') is False

    def test_webhook_notifier_send_exception(self, notification_config):
        """测试Webhook通知发送异常"""
        from requests.exceptions import RequestException
        
        webhook_config = {
            'enabled': True,
            'url': 'https://webhook.example.com/alert',
            'method': 'POST',
            'headers': {}
        }
        
        from src.notifier import WebhookNotifier
        from unittest.mock import patch
        
        with patch('requests.request', side_effect=RequestException('连接失败')):
            notifier = WebhookNotifier(webhook_config)
            result = CheckResult(
                site_name='测试站点',
                url='https://example.com',
                success=False,
                status_code=500,
                response_time=100,
                error_message='服务器错误',
                timestamp=datetime.now()
            )
            
            assert notifier.send_alert(result, 'http') is False

    def test_send_ssl_alert(self, notification_config):
        """测试发送SSL告警"""
        from src.ssl_checker import SSLCheckResult
        
        manager = NotificationManager(notification_config)
        result = SSLCheckResult(
            site_name='测试站点',
            url='https://example.com',
            success=False,
            valid=False,
            expiry_date=None,
            days_until_expiry=None,
            issuer=None,
            subject=None,
            error_message='SSL证书错误',
            timestamp=datetime.now()
        )
        
        manager.send_ssl_alert(result)

    def test_notifier_base_class_raises(self):
        """测试Notifier基类抛出NotImplementedError"""
        from src.notifier import Notifier
        
        notifier = Notifier()
        with pytest.raises(NotImplementedError):
            notifier.send_alert(None, 'http')

    def test_email_notifier_generate_ssl_content(self, notification_config):
        """测试生成SSL告警邮件内容"""
        email_config = {
            'enabled': True,
            'smtp_server': 'smtp.example.com',
            'username': 'test@example.com',
            'password': 'password',
            'recipients': ['admin@example.com']
        }
        
        from src.notifier import EmailNotifier
        from src.ssl_checker import SSLCheckResult
        
        notifier = EmailNotifier(email_config)
        result = SSLCheckResult(
            site_name='测试站点',
            url='https://example.com',
            success=True,
            valid=True,
            expiry_date=datetime.now(),
            days_until_expiry=10,
            issuer='Test CA',
            subject='example.com',
            error_message=None,
            timestamp=datetime.now()
        )
        
        subject, body = notifier._generate_email_content(result, 'ssl')
        assert 'SSL' in subject
        assert len(body) > 0

    def test_email_notifier_generate_unknown_type(self, notification_config):
        """测试生成未知类型告警邮件内容"""
        email_config = {
            'enabled': True,
            'smtp_server': 'smtp.example.com',
            'username': 'test@example.com',
            'password': 'password',
            'recipients': ['admin@example.com']
        }
        
        from src.notifier import EmailNotifier
        
        notifier = EmailNotifier(email_config)
        result = Mock()
        subject, body = notifier._generate_email_content(result, 'unknown')
        
        assert len(subject) > 0
        assert len(body) > 0
