import requests
import time
from typing import Dict, Any, Optional, Tuple
from urllib.parse import urljoin


class HttpClient:
    """HTTP请求客户端，支持多种HTTP方法和请求配置"""

    def __init__(self, base_url: str = '', timeout: int = 30):
        """
        初始化HTTP客户端

        Args:
            base_url: 基础URL，用于拼接相对路径
            timeout: 默认超时时间（秒）
        """
        self.base_url = base_url
        self.timeout = timeout
        self.session = requests.Session()
        self.last_response = None
        self.last_request_time = 0

    def set_base_url(self, base_url: str):
        """
        设置基础URL

        Args:
            base_url: 基础URL
        """
        self.base_url = base_url

    def set_default_headers(self, headers: Dict[str, str]):
        """
        设置默认请求头

        Args:
            headers: 默认请求头字典
        """
        self.session.headers.update(headers)

    def set_timeout(self, timeout: int):
        """
        设置默认超时时间

        Args:
            timeout: 超时时间（秒）
        """
        self.timeout = timeout

    def _build_url(self, url: str, base_url: Optional[str] = None) -> str:
        """
        构建完整URL

        Args:
            url: 请求URL，可以是相对路径或完整URL
            base_url: 可选的基础URL，覆盖实例的base_url

        Returns:
            完整的URL字符串
        """
        base = base_url or self.base_url
        if base and not url.startswith(('http://', 'https://')):
            return urljoin(base, url)
        return url

    def request(self, method: str, url: str, **kwargs) -> Dict[str, Any]:
        """
        发送HTTP请求

        Args:
            method: HTTP方法（GET, POST, PUT, DELETE等）
            url: 请求URL
            **kwargs: 其他请求参数（headers, params, json, data等）

        Returns:
            包含请求和响应信息的字典

        Raises:
            requests.RequestException: 请求失败时抛出
        """
        method = method.upper()
        full_url = self._build_url(
            url,
            kwargs.pop('base_url', None)
        )

        timeout = kwargs.pop('timeout', self.timeout)

        request_info = {
            'method': method,
            'url': full_url,
            'headers': kwargs.get('headers', {}),
            'params': kwargs.get('params', {}),
            'data': kwargs.get('data', {}),
            'json': kwargs.get('json', {}),
            'timeout': timeout
        }

        start_time = time.time()

        try:
            response = self.session.request(
                method=method,
                url=full_url,
                timeout=timeout,
                **kwargs
            )
            end_time = time.time()
            response_time = round((end_time - start_time) * 1000, 2)

            self.last_response = response
            self.last_request_time = response_time

            result = {
                'success': True,
                'request': request_info,
                'response': {
                    'status_code': response.status_code,
                    'headers': dict(response.headers),
                    'body': self._parse_response_body(response),
                    'text': response.text,
                    'response_time_ms': response_time,
                    'cookies': dict(response.cookies)
                },
                'error': None
            }

        except requests.RequestException as e:
            end_time = time.time()
            response_time = round((end_time - start_time) * 1000, 2)

            result = {
                'success': False,
                'request': request_info,
                'response': None,
                'error': {
                    'type': type(e).__name__,
                    'message': str(e),
                    'response_time_ms': response_time
                }
            }

        return result

    def _parse_response_body(self, response: requests.Response) -> Any:
        """
        解析响应体

        Args:
            response: requests响应对象

        Returns:
            解析后的响应体，JSON格式则返回字典，否则返回文本
        """
        try:
            return response.json()
        except ValueError:
            return response.text

    def get(self, url: str, **kwargs) -> Dict[str, Any]:
        """
        发送GET请求

        Args:
            url: 请求URL
            **kwargs: 其他请求参数

        Returns:
            响应结果字典
        """
        return self.request('GET', url, **kwargs)

    def post(self, url: str, **kwargs) -> Dict[str, Any]:
        """
        发送POST请求

        Args:
            url: 请求URL
            **kwargs: 其他请求参数

        Returns:
            响应结果字典
        """
        return self.request('POST', url, **kwargs)

    def put(self, url: str, **kwargs) -> Dict[str, Any]:
        """
        发送PUT请求

        Args:
            url: 请求URL
            **kwargs: 其他请求参数

        Returns:
            响应结果字典
        """
        return self.request('PUT', url, **kwargs)

    def delete(self, url: str, **kwargs) -> Dict[str, Any]:
        """
        发送DELETE请求

        Args:
            url: 请求URL
            **kwargs: 其他请求参数

        Returns:
            响应结果字典
        """
        return self.request('DELETE', url, **kwargs)

    def patch(self, url: str, **kwargs) -> Dict[str, Any]:
        """
        发送PATCH请求

        Args:
            url: 请求URL
            **kwargs: 其他请求参数

        Returns:
            响应结果字典
        """
        return self.request('PATCH', url, **kwargs)

    def head(self, url: str, **kwargs) -> Dict[str, Any]:
        """
        发送HEAD请求

        Args:
            url: 请求URL
            **kwargs: 其他请求参数

        Returns:
            响应结果字典
        """
        return self.request('HEAD', url, **kwargs)

    def options(self, url: str, **kwargs) -> Dict[str, Any]:
        """
        发送OPTIONS请求

        Args:
            url: 请求URL
            **kwargs: 其他请求参数

        Returns:
            响应结果字典
        """
        return self.request('OPTIONS', url, **kwargs)

    def close(self):
        """关闭会话，释放资源"""
        self.session.close()

    def __enter__(self):
        """上下文管理器入口"""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """上下文管理器出口"""
        self.close()
