"""
请求管理模块单元测试
"""
import pytest
from unittest.mock import MagicMock, patch, Mock
from requests import Session, Response
from requests.exceptions import RequestException, ConnectionError, Timeout

from auto_web_scraper.request_manager import RequestManager


class TestRequestManager:
    """
    请求管理器测试类
    """

    def setup_method(self):
        """
        每个测试方法前的准备
        """
        self.mock_session = MagicMock(spec=Session)
        self.manager = RequestManager(
            timeout=10,
            retry_times=2,
            retry_delay=0.01,
            session=self.mock_session,
        )

    def test_init_defaults(self):
        """
        测试默认初始化
        """
        manager = RequestManager()

        assert manager.timeout == 30
        assert manager.verify_ssl is True
        assert manager.allow_redirects is True
        assert manager.retry_times == 3
        assert manager.retry_delay == 2.0

    def test_init_custom(self):
        """
        测试自定义初始化
        """
        custom_headers = {"X-Custom": "value"}
        custom_cookies = {"session_id": "123"}

        manager = RequestManager(
            timeout=60,
            headers=custom_headers,
            cookies=custom_cookies,
            verify_ssl=False,
            allow_redirects=False,
            retry_times=5,
            retry_delay=1.0,
        )

        assert manager.timeout == 60
        assert manager.verify_ssl is False
        assert manager.allow_redirects is False
        assert manager.retry_times == 5
        assert manager.retry_delay == 1.0
        assert "X-Custom" in manager.headers
        assert manager.cookies == custom_cookies

    def test_default_headers(self):
        """
        测试默认浏览器请求头
        """
        manager = RequestManager()

        assert "User-Agent" in manager.headers
        assert "Accept" in manager.headers
        assert "Accept-Language" in manager.headers
        assert "Chrome" in manager.headers["User-Agent"]

    def test_custom_headers_preserved(self):
        """
        测试自定义请求头被保留
        """
        custom_ua = "CustomBot/1.0"
        manager = RequestManager(headers={"User-Agent": custom_ua})

        assert manager.headers["User-Agent"] == custom_ua

    def test_build_request_params(self):
        """
        测试构建请求参数
        """
        extra_headers = {"X-Extra": "test"}
        extra_cookies = {"extra_cookie": "value"}
        proxies = {"http": "http://proxy:8080"}

        params = self.manager._build_request_params(
            headers=extra_headers,
            cookies=extra_cookies,
            proxies=proxies,
        )

        assert params["timeout"] == 10
        assert params["verify"] is True
        assert params["allow_redirects"] is True
        assert params["headers"]["X-Extra"] == "test"
        assert params["cookies"]["extra_cookie"] == "value"
        assert "proxies" in params

    def test_build_request_params_without_proxies(self):
        """
        测试构建请求参数不包含代理
        """
        params = self.manager._build_request_params()

        assert "proxies" not in params

    def test_get_success(self):
        """
        测试GET请求成功
        """
        mock_response = MagicMock(spec=Response)
        mock_response.status_code = 200
        mock_response.raise_for_status.return_value = None
        self.mock_session.request.return_value = mock_response

        response = self.manager.get("https://example.com")

        assert response is not None
        assert response.status_code == 200
        self.mock_session.request.assert_called_once()

    def test_post_success(self):
        """
        测试POST请求成功
        """
        mock_response = MagicMock(spec=Response)
        mock_response.status_code = 200
        mock_response.raise_for_status.return_value = None
        self.mock_session.request.return_value = mock_response

        response = self.manager.post(
            "https://example.com/api",
            data={"key": "value"},
        )

        assert response is not None
        self.mock_session.request.assert_called_once()

    def test_post_with_json(self):
        """
        测试POST请求发送JSON数据
        """
        mock_response = MagicMock(spec=Response)
        mock_response.status_code = 200
        mock_response.raise_for_status.return_value = None
        self.mock_session.request.return_value = mock_response

        response = self.manager.post(
            "https://example.com/api",
            json={"key": "value"},
        )

        assert response is not None

    def test_retry_on_failure(self):
        """
        测试失败时自动重试
        """
        self.mock_session.request.side_effect = ConnectionError("Connection failed")

        response = self.manager.get("https://example.com")

        assert response is None
        assert self.mock_session.request.call_count == 3

    def test_retry_with_http_error(self):
        """
        测试HTTP错误时自动重试
        """
        mock_response = MagicMock(spec=Response)
        mock_response.status_code = 500
        mock_response.raise_for_status.side_effect = RequestException("Server Error")
        self.mock_session.request.return_value = mock_response

        response = self.manager.get("https://example.com")

        assert response is None
        assert self.mock_session.request.call_count == 3

    def test_get_with_params(self):
        """
        测试GET请求带URL参数
        """
        mock_response = MagicMock(spec=Response)
        mock_response.status_code = 200
        mock_response.raise_for_status.return_value = None
        self.mock_session.request.return_value = mock_response

        response = self.manager.get(
            "https://example.com",
            params={"page": 1, "limit": 10},
        )

        assert response is not None

    def test_get_with_proxies(self):
        """
        测试GET请求使用代理
        """
        mock_response = MagicMock(spec=Response)
        mock_response.status_code = 200
        mock_response.raise_for_status.return_value = None
        self.mock_session.request.return_value = mock_response

        proxies = {"http": "http://proxy:8080", "https": "https://proxy:8080"}
        response = self.manager.get("https://example.com", proxies=proxies)

        assert response is not None

    def test_set_session_cookies(self):
        """
        测试设置Session Cookie
        """
        mock_cookie_jar = MagicMock()
        self.mock_session.cookies = mock_cookie_jar

        self.manager.set_session_cookies({"test": "value"})

        mock_cookie_jar.set.assert_called_with("test", "value")

    def test_get_session_cookies(self):
        """
        测试获取Session Cookie
        """
        mock_cookie = MagicMock()
        mock_cookie.name = "session_id"
        mock_cookie.value = "abc123"
        self.mock_session.cookies = [mock_cookie]

        cookies = self.manager.get_session_cookies()

        assert cookies["session_id"] == "abc123"

    def test_close_session(self):
        """
        测试关闭Session
        """
        self.manager.close()

        self.mock_session.close.assert_called_once()

    def test_no_retry_after_success(self):
        """
        测试成功后不重试
        """
        mock_response = MagicMock(spec=Response)
        mock_response.status_code = 200
        mock_response.raise_for_status.return_value = None
        self.mock_session.request.return_value = mock_response

        self.manager.get("https://example.com")

        assert self.mock_session.request.call_count == 1

    def test_request_exception_handling(self):
        """
        测试请求异常处理
        """
        self.mock_session.request.side_effect = Timeout("Request timed out")

        response = self.manager.get("https://example.com")

        assert response is None

    @patch("auto_web_scraper.request_manager.print")
    def test_error_message_printed(self, mock_print):
        """
        测试错误消息被打印
        """
        self.mock_session.request.side_effect = ConnectionError("Connection failed")

        self.manager.get("https://example.com")

        mock_print.assert_called()
