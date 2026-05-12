"""
认证模块
处理网站登录和会话管理
"""
from typing import Dict, Optional, Any
import requests
from bs4 import BeautifulSoup


class Authenticator:
    """
    认证管理器
    处理网站登录、Cookie管理等
    """

    def __init__(
        self,
        session: Optional[requests.Session] = None,
        request_manager=None,
    ):
        """
        初始化认证管理器

        Args:
            session: requests Session对象
            request_manager: 请求管理器
        """
        self.session = session or requests.Session()
        self.request_manager = request_manager
        self._is_logged_in = False
        self._login_info: Dict[str, Any] = {}

    def form_login(
        self,
        login_url: str,
        username: str,
        password: str,
        username_field: str = "username",
        password_field: str = "password",
        submit_field: Optional[str] = None,
        extra_fields: Optional[Dict[str, str]] = None,
        headers: Optional[Dict[str, str]] = None,
        success_indicator: str = "",
    ) -> bool:
        """
        表单登录

        Args:
            login_url: 登录页面URL
            username: 用户名
            password: 密码
            username_field: 用户名字段名
            password_field: 密码字段名
            submit_field: 提交按钮字段名
            extra_fields: 额外的表单字段
            headers: 请求头
            success_indicator: 登录成功标志

        Returns:
            是否登录成功
        """
        try:
            get_response = self.session.get(
                login_url, headers=headers, timeout=30
            )
            if get_response.status_code != 200:
                print(f"获取登录页面失败: {get_response.status_code}")
                return False

            soup = BeautifulSoup(get_response.text, "html.parser")
            form = soup.find("form")

            form_data: Dict[str, str] = {}
            if form:
                hidden_inputs = form.find_all(
                    "input", type=["hidden", "submit"]
                )
                for inp in hidden_inputs:
                    if inp.get("name"):
                        form_data[inp["name"]] = inp.get("value", "")

            form_data[username_field] = username
            form_data[password_field] = password

            if submit_field:
                form_data[submit_field] = "submit"

            if extra_fields:
                form_data.update(extra_fields)

            login_response = self.session.post(
                login_url,
                data=form_data,
                headers=headers,
                timeout=30,
                allow_redirects=True,
            )

            if login_response.status_code in [200, 301, 302]:
                self._is_logged_in = True
                self._login_info = {
                    "login_url": login_url,
                    "username": username,
                    "login_time": login_response.elapsed,
                }

                if success_indicator:
                    if success_indicator not in login_response.text:
                        print(f"登录失败: 未找到成功标志 '{success_indicator}'")
                        self._is_logged_in = False
                        return False

                return True
            else:
                print(f"登录请求失败: {login_response.status_code}")
                return False

        except Exception as e:
            print(f"登录异常: {e}")
            return False

    def token_login(
        self,
        auth_url: str,
        username: str,
        password: str,
        token_field: str = "token",
        headers: Optional[Dict[str, str]] = None,
    ) -> bool:
        """
        Token登录

        Args:
            auth_url: 认证API URL
            username: 用户名
            password: 密码
            token_field: Token字段名
            headers: 请求头

        Returns:
            是否登录成功
        """
        try:
            payload = {"username": username, "password": password}
            default_headers = {"Content-Type": "application/json"}
            if headers:
                default_headers.update(headers)

            response = self.session.post(
                auth_url, json=payload, headers=default_headers, timeout=30
            )

            if response.status_code == 200:
                try:
                    data = response.json()
                    token = data.get(token_field) or data.get("access_token")
                    if token:
                        self.session.headers.update(
                            {"Authorization": f"Bearer {token}"}
                        )
                        self._is_logged_in = True
                        return True
                except ValueError:
                    pass

            print(f"Token登录失败: {response.status_code}")
            return False

        except Exception as e:
            print(f"Token登录异常: {e}")
            return False

    def set_cookies(
        self, cookies: Dict[str, str], domain: Optional[str] = None
    ):
        """
        设置Cookie

        Args:
            cookies: Cookie字典
            domain: Cookie域名
        """
        for name, value in cookies.items():
            self.session.cookies.set(name, value, domain=domain)

    def get_cookies(self) -> Dict[str, str]:
        """
        获取当前Cookie

        Returns:
            Cookie字典
        """
        return {
            cookie.name: cookie.value for cookie in self.session.cookies
        }

    def save_cookies(self, file_path: str) -> bool:
        """
        保存Cookie到文件

        Args:
            file_path: 文件路径

        Returns:
            是否保存成功
        """
        try:
            import json

            cookies_dict = self.get_cookies()
            with open(file_path, "w", encoding="utf-8") as f:
                json.dump(cookies_dict, f, ensure_ascii=False, indent=2)
            return True
        except Exception as e:
            print(f"保存Cookie失败: {e}")
            return False

    def load_cookies(self, file_path: str) -> bool:
        """
        从文件加载Cookie

        Args:
            file_path: 文件路径

        Returns:
            是否加载成功
        """
        try:
            import json

            with open(file_path, "r", encoding="utf-8") as f:
                cookies_dict = json.load(f)
                self.set_cookies(cookies_dict)
            return True
        except Exception as e:
            print(f"加载Cookie失败: {e}")
            return False

    def verify_login(
        self,
        verify_url: str,
        success_indicator: str,
        headers: Optional[Dict[str, str]] = None,
    ) -> bool:
        """
        验证登录状态

        Args:
            verify_url: 验证URL
            success_indicator: 成功标志文本
            headers: 请求头

        Returns:
            是否登录有效
        """
        try:
            response = self.session.get(
                verify_url, headers=headers, timeout=30
            )
            if response.status_code == 200:
                if success_indicator in response.text:
                    return True
            return False
        except Exception as e:
            print(f"验证登录失败: {e}")
            return False

    def is_logged_in(self) -> bool:
        """
        检查是否已登录

        Returns:
            是否已登录
        """
        return self._is_logged_in

    def logout(self):
        """
        登出，清除会话
        """
        self.session.cookies.clear()
        self.session.headers.clear()
        self._is_logged_in = False
        self._login_info = {}
