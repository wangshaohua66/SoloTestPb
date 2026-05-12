"""
请求管理模块
负责处理HTTP请求，包括重试、超时等
"""
import time
import random
from typing import Optional, Dict, Any
import requests
from requests import Response, Session


class RequestManager:
    """
    请求管理器
    处理HTTP请求的发送、重试和错误处理
    """

    def __init__(
        self,
        timeout: int = 30,
        headers: Optional[Dict[str, str]] = None,
        cookies: Optional[Dict[str, str]] = None,
        verify_ssl: bool = True,
        allow_redirects: bool = True,
        retry_times: int = 3,
        retry_delay: float = 2.0,
        session: Optional[Session] = None,
    ):
        """
        初始化请求管理器

        Args:
            timeout: 请求超时时间(秒)
            headers: 默认请求头
            cookies: 默认Cookie
            verify_ssl: 是否验证SSL证书
            allow_redirects: 是否允许重定向
            retry_times: 重试次数
            retry_delay: 重试间隔(秒)
            session: 自定义Session对象
        """
        self.timeout = timeout
        self.headers = headers or {}
        self.cookies = cookies or {}
        self.verify_ssl = verify_ssl
        self.allow_redirects = allow_redirects
        self.retry_times = retry_times
        self.retry_delay = retry_delay
        self.session = session or Session()
        self._default_headers()

    def _default_headers(self):
        """
        设置默认的浏览器请求头
        模拟真实浏览器访问，避免被封禁
        """
        default_headers = {
            "User-Agent": (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/120.0.0.0 Safari/537.36"
            ),
            "Accept": (
                "text/html,application/xhtml+xml,application/xml;"
                "q=0.9,image/webp,*/*;q=0.8"
            ),
            "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
            "Accept-Encoding": "gzip, deflate, br",
            "Connection": "keep-alive",
        }
        for key, value in default_headers.items():
            if key not in self.headers:
                self.headers[key] = value

    def _build_request_params(
        self,
        headers: Optional[Dict[str, str]] = None,
        cookies: Optional[Dict[str, str]] = None,
        proxies: Optional[Dict[str, str]] = None,
    ) -> Dict[str, Any]:
        """
        构建请求参数

        Args:
            headers: 额外的请求头
            cookies: 额外的Cookie
            proxies: 代理配置

        Returns:
            请求参数字典
        """
        params = {
            "headers": {**self.headers, **(headers or {})},
            "cookies": {**self.cookies, **(cookies or {})},
            "timeout": self.timeout,
            "verify": self.verify_ssl,
            "allow_redirects": self.allow_redirects,
        }
        if proxies:
            params["proxies"] = proxies
        return params

    def get(
        self,
        url: str,
        headers: Optional[Dict[str, str]] = None,
        cookies: Optional[Dict[str, str]] = None,
        proxies: Optional[Dict[str, str]] = None,
        params: Optional[Dict[str, Any]] = None,
    ) -> Optional[Response]:
        """
        发送GET请求

        Args:
            url: 请求URL
            headers: 额外的请求头
            cookies: 额外的Cookie
            proxies: 代理配置
            params: URL查询参数

        Returns:
            Response对象或None
        """
        return self._request("get", url, headers, cookies, proxies, params=params)

    def post(
        self,
        url: str,
        data: Optional[Dict[str, Any]] = None,
        json: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None,
        cookies: Optional[Dict[str, str]] = None,
        proxies: Optional[Dict[str, str]] = None,
    ) -> Optional[Response]:
        """
        发送POST请求

        Args:
            url: 请求URL
            data: 表单数据
            json: JSON数据
            headers: 额外的请求头
            cookies: 额外的Cookie
            proxies: 代理配置

        Returns:
            Response对象或None
        """
        return self._request(
            "post", url, headers, cookies, proxies, data=data, json=json
        )

    def _request(
        self,
        method: str,
        url: str,
        headers: Optional[Dict[str, str]] = None,
        cookies: Optional[Dict[str, str]] = None,
        proxies: Optional[Dict[str, str]] = None,
        **kwargs,
    ) -> Optional[Response]:
        """
        内部请求方法，包含重试逻辑

        Args:
            method: HTTP方法
            url: 请求URL
            headers: 额外的请求头
            cookies: 额外的Cookie
            proxies: 代理配置
            **kwargs: 其他请求参数

        Returns:
            Response对象或None
        """
        request_params = self._build_request_params(headers, cookies, proxies)
        request_params.update(kwargs)

        last_exception = None
        for attempt in range(self.retry_times + 1):
            try:
                response = self.session.request(
                    method.upper(), url, **request_params
                )
                response.raise_for_status()
                return response
            except requests.RequestException as e:
                last_exception = e
                if attempt < self.retry_times:
                    delay = self.retry_delay * (2 ** attempt) + random.uniform(0, 1)
                    time.sleep(delay)
                else:
                    break

        if last_exception:
            print(f"请求失败: {url}, 错误: {last_exception}")

        return None

    def set_session_cookies(self, cookies: Dict[str, str]):
        """
        设置Session的Cookie

        Args:
            cookies: Cookie字典
        """
        for key, value in cookies.items():
            self.session.cookies.set(key, value)

    def get_session_cookies(self) -> Dict[str, str]:
        """
        获取当前Session的Cookie

        Returns:
            Cookie字典
        """
        return {cookie.name: cookie.value for cookie in self.session.cookies}

    def close(self):
        """
        关闭Session连接
        """
        self.session.close()
