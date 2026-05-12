"""
SSL证书检测模块测试
"""

import pytest
from unittest.mock import Mock, patch
from datetime import datetime, timedelta
from src.ssl_checker import SSLChecker, SSLCheckResult


class TestSSLCheckResult:
    """
    SSLCheckResult数据类测试
    """

    def test_ssl_check_result_creation(self):
        """测试创建SSLCheckResult"""
        result = SSLCheckResult(
            site_name='测试站点',
            url='https://example.com',
            success=True,
            valid=True,
            expiry_date=datetime.now() + timedelta(days=60),
            days_until_expiry=60,
            issuer='Test CA',
            subject='example.com',
            error_message=None,
            timestamp=datetime.now()
        )

        assert result.site_name == '测试站点'
        assert result.valid is True


class TestSSLChecker:
    """
    SSLChecker类测试
    """

    @pytest.fixture
    def ssl_checker(self):
        """创建SSL检测器"""
        return SSLChecker(timeout=5, alert_days=30)

    def test_ssl_checker_init(self, ssl_checker):
        """测试SSL检测器初始化"""
        assert ssl_checker.alert_days == 30

    def test_parse_url(self, ssl_checker):
        """测试URL解析"""
        hostname, port = ssl_checker._parse_url('https://example.com:8443/path')
        assert hostname == 'example.com'
        assert port == 8443

    def test_parse_url_default_port(self, ssl_checker):
        """测试默认端口"""
        hostname, port = ssl_checker._parse_url('https://example.com')
        assert hostname == 'example.com'
        assert port == 443

    def test_check_non_https(self, ssl_checker):
        """测试非HTTPS协议跳过检测"""
        site = {
            'name': '测试站点',
            'url': 'http://example.com'
        }

        result = ssl_checker.check(site)
        assert result.success is True
        assert result.valid is True

    @patch('socket.create_connection')
    @patch('ssl.create_default_context')
    def test_check_ssl_valid(self, mock_context, mock_socket, ssl_checker):
        """测试有效SSL证书"""
        mock_secure_socket = Mock()
        cert = {
            'notAfter': (datetime.now() + timedelta(days=60)).strftime('%b %d %H:%M:%S %Y GMT'),
            'issuer': [[('organizationName', 'Test CA')]],
            'subject': [[('commonName', 'example.com')]]
        }
        mock_secure_socket.getpeercert.return_value = cert

        mock_context_instance = Mock()
        mock_wrap_result = Mock()
        mock_wrap_result.__enter__ = Mock(return_value=mock_secure_socket)
        mock_wrap_result.__exit__ = Mock(return_value=None)
        mock_context_instance.wrap_socket.return_value = mock_wrap_result
        mock_context.return_value = mock_context_instance

        site = {
            'name': '测试站点',
            'url': 'https://example.com'
        }

        result = ssl_checker.check(site)

        assert result.success is True
        assert result.valid is True

    @patch('socket.create_connection')
    @patch('ssl.create_default_context')
    def test_check_ssl_expired(self, mock_context, mock_socket, ssl_checker):
        """测试过期SSL证书"""
        mock_secure_socket = Mock()
        cert = {
            'notAfter': (datetime.now() - timedelta(days=1)).strftime('%b %d %H:%M:%S %Y GMT'),
            'issuer': [[('organizationName', 'Test CA')]],
            'subject': [[('commonName', 'example.com')]]
        }
        mock_secure_socket.getpeercert.return_value = cert

        mock_context_instance = Mock()
        mock_wrap_result = Mock()
        mock_wrap_result.__enter__ = Mock(return_value=mock_secure_socket)
        mock_wrap_result.__exit__ = Mock(return_value=None)
        mock_context_instance.wrap_socket.return_value = mock_wrap_result
        mock_context.return_value = mock_context_instance

        site = {
            'name': '测试站点',
            'url': 'https://example.com'
        }

        result = ssl_checker.check(site)

        assert result.success is True
        assert result.valid is False

    def test_needs_alert_expiring_soon(self, ssl_checker):
        """测试即将过期需要告警"""
        result = SSLCheckResult(
            site_name='测试',
            url='https://example.com',
            success=True,
            valid=True,
            expiry_date=datetime.now() + timedelta(days=10),
            days_until_expiry=10,
            issuer='Test',
            subject='Test',
            error_message=None,
            timestamp=datetime.now()
        )

        assert ssl_checker.needs_alert(result) is True

    def test_needs_alert_not_expiring_soon(self, ssl_checker):
        """测试不需要告警"""
        result = SSLCheckResult(
            site_name='测试',
            url='https://example.com',
            success=True,
            valid=True,
            expiry_date=datetime.now() + timedelta(days=60),
            days_until_expiry=60,
            issuer='Test',
            subject='Test',
            error_message=None,
            timestamp=datetime.now()
        )

        assert ssl_checker.needs_alert(result) is False

    def test_needs_alert_failed(self, ssl_checker):
        """测试检测失败需要告警"""
        result = SSLCheckResult(
            site_name='测试',
            url='https://example.com',
            success=False,
            valid=False,
            expiry_date=None,
            days_until_expiry=None,
            issuer=None,
            subject=None,
            error_message='Connection failed',
            timestamp=datetime.now()
        )

        assert ssl_checker.needs_alert(result) is True

    def test_parse_url_invalid(self, ssl_checker):
        """测试无法解析URL的情况"""
        with pytest.raises(ValueError):
            ssl_checker._parse_url('')

    @patch('socket.create_connection')
    @patch('ssl.create_default_context')
    def test_check_no_cert(self, mock_context, mock_socket, ssl_checker):
        """测试无法获取证书的情况"""
        mock_secure_socket = Mock()
        mock_secure_socket.getpeercert.return_value = None

        mock_context_instance = Mock()
        mock_wrap_result = Mock()
        mock_wrap_result.__enter__ = Mock(return_value=mock_secure_socket)
        mock_wrap_result.__exit__ = Mock(return_value=None)
        mock_context_instance.wrap_socket.return_value = mock_wrap_result
        mock_context.return_value = mock_context_instance

        site = {
            'name': '测试站点',
            'url': 'https://example.com'
        }

        result = ssl_checker.check(site)

        assert result.success is False
        assert result.valid is False

    @patch('socket.create_connection')
    @patch('ssl.create_default_context')
    def test_check_timeout(self, mock_context, mock_socket, ssl_checker):
        """测试连接超时的情况"""
        import socket
        mock_socket.side_effect = socket.timeout('连接超时')

        site = {
            'name': '测试站点',
            'url': 'https://example.com'
        }

        result = ssl_checker.check(site)

        assert result.success is False
        assert result.valid is False

    @patch('socket.create_connection')
    @patch('ssl.create_default_context')
    def test_check_ssl_error(self, mock_context, mock_socket, ssl_checker):
        """测试SSL错误的情况"""
        import ssl
        mock_context_instance = Mock()
        mock_context_instance.wrap_socket.side_effect = ssl.SSLError('SSL错误')
        mock_context.return_value = mock_context_instance

        site = {
            'name': '测试站点',
            'url': 'https://example.com'
        }

        result = ssl_checker.check(site)

        assert result.success is False
        assert result.valid is False

    @patch('socket.create_connection')
    @patch('ssl.create_default_context')
    def test_check_general_exception(self, mock_context, mock_socket, ssl_checker):
        """测试通用异常的情况"""
        mock_socket.side_effect = Exception('未知错误')

        site = {
            'name': '测试站点',
            'url': 'https://example.com'
        }

        result = ssl_checker.check(site)

        assert result.success is False
        assert result.valid is False
