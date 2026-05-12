"""
HTTP检测模块测试
"""

import pytest
from unittest.mock import Mock, patch
from datetime import datetime
from src.http_checker import HTTPChecker, CheckResult


class TestCheckResult:
    """
    CheckResult数据类测试
    """

    def test_check_result_creation(self):
        """测试创建CheckResult"""
        result = CheckResult(
            site_name='测试站点',
            url='https://example.com',
            success=True,
            status_code=200,
            response_time=100.5,
            error_message=None,
            timestamp=datetime.now()
        )

        assert result.site_name == '测试站点'
        assert result.success is True
        assert result.status_code == 200


class TestHTTPChecker:
    """
    HTTPChecker类测试
    """

    @pytest.fixture
    def http_checker(self):
        """创建HTTP检测器"""
        checker = HTTPChecker(timeout=5)
        yield checker
        checker.close()

    def test_http_checker_init(self, http_checker):
        """测试HTTP检测器初始化"""
        assert http_checker.timeout == 5

    @patch('requests.Session.get')
    def test_check_success(self, mock_get, http_checker):
        """测试成功检测"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_get.return_value = mock_response

        site = {
            'name': '测试站点',
            'url': 'https://example.com',
            'timeout': 5
        }

        result = http_checker.check(site)

        assert result.success is True
        assert result.status_code == 200
        assert result.site_name == '测试站点'

    @patch('requests.Session.get')
    def test_check_server_error(self, mock_get, http_checker):
        """测试服务器错误"""
        mock_response = Mock()
        mock_response.status_code = 500
        mock_get.return_value = mock_response

        site = {
            'name': '测试站点',
            'url': 'https://example.com'
        }

        result = http_checker.check(site)

        assert result.success is False
        assert result.status_code == 500

    @patch('requests.Session.get')
    def test_check_timeout(self, mock_get, http_checker):
        """测试请求超时"""
        from requests.exceptions import Timeout
        mock_get.side_effect = Timeout()

        site = {
            'name': '测试站点',
            'url': 'https://example.com'
        }

        result = http_checker.check(site)

        assert result.success is False
        assert result.status_code is None

    @patch('requests.Session.get')
    def test_check_connection_error(self, mock_get, http_checker):
        """测试连接错误"""
        from requests.exceptions import ConnectionError
        mock_get.side_effect = ConnectionError()

        site = {
            'name': '测试站点',
            'url': 'https://example.com'
        }

        result = http_checker.check(site)

        assert result.success is False

    @patch('requests.Session.get')
    def test_check_response_time(self, mock_get, http_checker):
        """测试响应时间记录"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_get.return_value = mock_response

        site = {
            'name': '测试站点',
            'url': 'https://example.com'
        }

        result = http_checker.check(site)

        assert result.response_time > 0

    def test_context_manager(self):
        """测试上下文管理器"""
        with HTTPChecker() as checker:
            assert checker is not None
