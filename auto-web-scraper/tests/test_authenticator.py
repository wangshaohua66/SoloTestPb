"""
认证管理模块单元测试
"""
import pytest
import json
import tempfile
import os
from unittest.mock import MagicMock, patch
from requests import Session
from requests.exceptions import RequestException

from auto_web_scraper.authenticator import Authenticator


LOGIN_HTML = """
<!DOCTYPE html>
<html>
<head><title>Login</title></head>
<body>
    <form action="/login" method="post">
        <input type="hidden" name="csrf_token" value="abc123">
        <input type="text" name="username">
        <input type="password" name="password">
        <button type="submit">Login</button>
    </form>
</body>
</html>
"""

SUCCESS_HTML = """
<!DOCTYPE html>
<html>
<head><title>Dashboard</title></head>
<body>
    <div class="welcome">欢迎回来，测试用户</div>
</body>
</html>
"""


class TestAuthenticator:
    """
    认证管理器测试类
    """

    def setup_method(self):
        """
        每个测试方法前的准备
        """
        self.mock_session = MagicMock(spec=Session)
        self.authenticator = Authenticator(session=self.mock_session)

    def test_init_defaults(self):
        """
        测试默认初始化
        """
        authenticator = Authenticator()

        assert authenticator._is_logged_in is False
        assert authenticator._login_info == {}
        assert authenticator.session is not None

    def test_init_with_session(self):
        """
        测试使用自定义Session初始化
        """
        authenticator = Authenticator(session=self.mock_session)

        assert authenticator.session is self.mock_session
        assert authenticator._is_logged_in is False

    def test_form_login_success(self):
        """
        测试表单登录成功
        """
        mock_get_response = MagicMock()
        mock_get_response.status_code = 200
        mock_get_response.text = LOGIN_HTML

        mock_post_response = MagicMock()
        mock_post_response.status_code = 200
        mock_post_response.text = SUCCESS_HTML

        self.mock_session.get.return_value = mock_get_response
        self.mock_session.post.return_value = mock_post_response

        success = self.authenticator.form_login(
            login_url="https://example.com/login",
            username="testuser",
            password="testpass",
        )

        assert success is True
        assert self.authenticator._is_logged_in is True
        assert self.mock_session.get.called
        assert self.mock_session.post.called

    def test_form_login_with_extra_fields(self):
        """
        测试表单登录带额外字段
        """
        mock_get_response = MagicMock()
        mock_get_response.status_code = 200
        mock_get_response.text = LOGIN_HTML

        mock_post_response = MagicMock()
        mock_post_response.status_code = 200
        mock_post_response.text = SUCCESS_HTML

        self.mock_session.get.return_value = mock_get_response
        self.mock_session.post.return_value = mock_post_response

        success = self.authenticator.form_login(
            login_url="https://example.com/login",
            username="testuser",
            password="testpass",
            extra_fields={"remember": "1", "timezone": "Asia/Shanghai"},
        )

        assert success is True

    def test_form_login_with_success_indicator(self):
        """
        测试表单登录带成功标志验证
        """
        mock_get_response = MagicMock()
        mock_get_response.status_code = 200
        mock_get_response.text = LOGIN_HTML

        mock_post_response = MagicMock()
        mock_post_response.status_code = 200
        mock_post_response.text = SUCCESS_HTML

        self.mock_session.get.return_value = mock_get_response
        self.mock_session.post.return_value = mock_post_response

        success = self.authenticator.form_login(
            login_url="https://example.com/login",
            username="testuser",
            password="testpass",
            success_indicator="欢迎回来",
        )

        assert success is True
        assert self.authenticator._is_logged_in is True

    def test_form_login_success_indicator_failed(self):
        """
        测试表单登录成功标志验证失败
        """
        mock_get_response = MagicMock()
        mock_get_response.status_code = 200
        mock_get_response.text = LOGIN_HTML

        mock_post_response = MagicMock()
        mock_post_response.status_code = 200
        mock_post_response.text = "<html>错误页面</html>"

        self.mock_session.get.return_value = mock_get_response
        self.mock_session.post.return_value = mock_post_response

        success = self.authenticator.form_login(
            login_url="https://example.com/login",
            username="testuser",
            password="testpass",
            success_indicator="欢迎回来",
        )

        assert success is False
        assert self.authenticator._is_logged_in is False

    def test_form_login_get_page_failed(self):
        """
        测试表单登录获取页面失败
        """
        mock_get_response = MagicMock()
        mock_get_response.status_code = 404

        self.mock_session.get.return_value = mock_get_response

        success = self.authenticator.form_login(
            login_url="https://example.com/login",
            username="testuser",
            password="testpass",
        )

        assert success is False

    def test_form_login_post_failed(self):
        """
        测试表单登录提交失败
        """
        mock_get_response = MagicMock()
        mock_get_response.status_code = 200
        mock_get_response.text = LOGIN_HTML

        mock_post_response = MagicMock()
        mock_post_response.status_code = 401

        self.mock_session.get.return_value = mock_get_response
        self.mock_session.post.return_value = mock_post_response

        success = self.authenticator.form_login(
            login_url="https://example.com/login",
            username="testuser",
            password="testpass",
        )

        assert success is False

    @patch("auto_web_scraper.authenticator.print")
    def test_form_login_exception(self, mock_print):
        """
        测试表单登录异常处理
        """
        self.mock_session.get.side_effect = RequestException("Network error")

        success = self.authenticator.form_login(
            login_url="https://example.com/login",
            username="testuser",
            password="testpass",
        )

        assert success is False
        mock_print.assert_called()

    def test_token_login_success(self):
        """
        测试Token登录成功
        """
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"token": "abc123def456"}

        self.mock_session.post.return_value = mock_response

        success = self.authenticator.token_login(
            auth_url="https://example.com/api/auth",
            username="testuser",
            password="testpass",
        )

        assert success is True
        assert self.authenticator._is_logged_in is True

    def test_token_login_access_token(self):
        """
        测试Token登录使用access_token字段
        """
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"access_token": "xyz789"}

        self.mock_session.post.return_value = mock_response

        success = self.authenticator.token_login(
            auth_url="https://example.com/api/auth",
            username="testuser",
            password="testpass",
        )

        assert success is True

    def test_token_login_failed(self):
        """
        测试Token登录失败
        """
        mock_response = MagicMock()
        mock_response.status_code = 401
        mock_response.json.return_value = {"error": "Unauthorized"}

        self.mock_session.post.return_value = mock_response

        success = self.authenticator.token_login(
            auth_url="https://example.com/api/auth",
            username="testuser",
            password="testpass",
        )

        assert success is False

    def test_token_login_no_token(self):
        """
        测试Token登录无Token返回
        """
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"status": "ok"}

        self.mock_session.post.return_value = mock_response

        success = self.authenticator.token_login(
            auth_url="https://example.com/api/auth",
            username="testuser",
            password="testpass",
        )

        assert success is False

    @patch("auto_web_scraper.authenticator.print")
    def test_token_login_exception(self, mock_print):
        """
        测试Token登录异常处理
        """
        self.mock_session.post.side_effect = RequestException("Network error")

        success = self.authenticator.token_login(
            auth_url="https://example.com/api/auth",
            username="testuser",
            password="testpass",
        )

        assert success is False

    def test_set_cookies(self):
        """
        测试设置Cookie
        """
        mock_cookie_jar = MagicMock()
        self.mock_session.cookies = mock_cookie_jar

        self.authenticator.set_cookies(
            {"session_id": "123", "token": "abc"},
            domain="example.com",
        )

        assert mock_cookie_jar.set.call_count == 2

    def test_get_cookies(self):
        """
        测试获取Cookie
        """
        mock_cookie1 = MagicMock()
        mock_cookie1.name = "session_id"
        mock_cookie1.value = "123"

        mock_cookie2 = MagicMock()
        mock_cookie2.name = "user"
        mock_cookie2.value = "test"

        self.mock_session.cookies = [mock_cookie1, mock_cookie2]

        cookies = self.authenticator.get_cookies()

        assert cookies["session_id"] == "123"
        assert cookies["user"] == "test"

    def test_save_and_load_cookies(self):
        """
        测试保存和加载Cookie
        """
        mock_cookie = MagicMock()
        mock_cookie.name = "session_id"
        mock_cookie.value = "saved123"
        self.mock_session.cookies = [mock_cookie]

        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".json", delete=False, encoding="utf-8"
        ) as f:
            temp_path = f.name

        try:
            save_success = self.authenticator.save_cookies(temp_path)
            assert save_success is True

            mock_cookie_jar = MagicMock()
            new_session = MagicMock(spec=Session)
            new_session.cookies = mock_cookie_jar
            new_authenticator = Authenticator(session=new_session)

            load_success = new_authenticator.load_cookies(temp_path)
            assert load_success is True
            assert mock_cookie_jar.set.called

        finally:
            if os.path.exists(temp_path):
                os.unlink(temp_path)

    def test_save_cookies_failed(self):
        """
        测试保存Cookie失败
        """
        success = self.authenticator.save_cookies("/invalid/path/cookies.json")
        assert success is False

    def test_load_cookies_failed(self):
        """
        测试加载Cookie失败
        """
        success = self.authenticator.load_cookies("/nonexistent/file.json")
        assert success is False

    def test_verify_login_success(self):
        """
        测试验证登录成功
        """
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.text = '<div>欢迎回来</div>'

        self.mock_session.get.return_value = mock_response

        success = self.authenticator.verify_login(
            verify_url="https://example.com/profile",
            success_indicator="欢迎回来",
        )

        assert success is True

    def test_verify_login_failed(self):
        """
        测试验证登录失败
        """
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.text = '<div>请登录</div>'

        self.mock_session.get.return_value = mock_response

        success = self.authenticator.verify_login(
            verify_url="https://example.com/profile",
            success_indicator="欢迎回来",
        )

        assert success is False

    def test_verify_login_http_error(self):
        """
        测试验证登录HTTP错误
        """
        mock_response = MagicMock()
        mock_response.status_code = 401

        self.mock_session.get.return_value = mock_response

        success = self.authenticator.verify_login(
            verify_url="https://example.com/profile",
            success_indicator="欢迎回来",
        )

        assert success is False

    @patch("auto_web_scraper.authenticator.print")
    def test_verify_login_exception(self, mock_print):
        """
        测试验证登录异常处理
        """
        self.mock_session.get.side_effect = RequestException("Network error")

        success = self.authenticator.verify_login(
            verify_url="https://example.com/profile",
            success_indicator="欢迎回来",
        )

        assert success is False

    def test_is_logged_in(self):
        """
        测试检查登录状态
        """
        assert self.authenticator.is_logged_in() is False

        self.authenticator._is_logged_in = True
        assert self.authenticator.is_logged_in() is True

    def test_logout(self):
        """
        测试登出
        """
        mock_cookie_jar = MagicMock()
        mock_headers = MagicMock()
        self.mock_session.cookies = mock_cookie_jar
        self.mock_session.headers = mock_headers

        self.authenticator._is_logged_in = True
        self.authenticator._login_info = {"test": "value"}

        self.authenticator.logout()

        mock_cookie_jar.clear.assert_called_once()
        mock_headers.clear.assert_called_once()
        assert self.authenticator._is_logged_in is False
        assert self.authenticator._login_info == {}
