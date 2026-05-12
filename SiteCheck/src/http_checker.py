"""
HTTP/HTTPS检测模块
负责检测网站的HTTP/HTTPS连接状态、响应时间和状态码
"""

import requests
import time
from typing import Dict, Any, Optional
import logging
from dataclasses import dataclass
from datetime import datetime


@dataclass
class CheckResult:
    """
    检测结果数据类
    存储单次网站检测的结果信息
    """
    site_name: str
    url: str
    success: bool
    status_code: Optional[int]
    response_time: float
    error_message: Optional[str]
    timestamp: datetime


class HTTPChecker:
    """
    HTTP/HTTPS检测类
    负责执行网站的健康检测
    """

    def __init__(self, timeout: int = 10):
        """
        初始化HTTP检测器

        Args:
            timeout: 请求超时时间（秒）
        """
        self.timeout = timeout
        self.logger = logging.getLogger(__name__)
        self.session = requests.Session()

    def check(self, site: Dict[str, Any]) -> CheckResult:
        """
        执行单个网站的健康检测

        Args:
            site: 站点配置字典，包含url、name、timeout等信息

        Returns:
            CheckResult对象，包含检测结果信息
        """
        url = site.get('url')
        site_name = site.get('name', url)
        timeout = site.get('timeout', self.timeout)

        self.logger.info(f"开始检测站点: {site_name} ({url})")

        start_time = time.perf_counter()
        success = False
        status_code = None
        error_message = None

        try:
            response = self.session.get(
                url,
                timeout=timeout,
                allow_redirects=True,
                headers={
                    'User-Agent': 'SiteChecker/1.0 (Health Monitoring Bot)'
                }
            )
            status_code = response.status_code
            success = 200 <= status_code < 400

            if not success:
                error_message = f"HTTP状态码异常: {status_code}"
                self.logger.warning(f"{site_name} 检测失败: {error_message}")
            else:
                self.logger.info(f"{site_name} 检测成功, 状态码: {status_code}")

        except requests.exceptions.Timeout:
            error_message = "请求超时"
            self.logger.error(f"{site_name} 检测失败: {error_message}")

        except requests.exceptions.ConnectionError:
            error_message = "连接失败"
            self.logger.error(f"{site_name} 检测失败: {error_message}")

        except requests.exceptions.SSLError:
            error_message = "SSL证书错误"
            self.logger.error(f"{site_name} 检测失败: {error_message}")

        except Exception as e:
            error_message = f"未知错误: {str(e)}"
            self.logger.error(f"{site_name} 检测失败: {error_message}")

        finally:
            end_time = time.perf_counter()
            response_time = round((end_time - start_time) * 1000, 2)

        result = CheckResult(
            site_name=site_name,
            url=url,
            success=success,
            status_code=status_code,
            response_time=response_time,
            error_message=error_message,
            timestamp=datetime.now()
        )

        self.logger.info(
            f"{site_name} 检测完成 - 响应时间: {response_time}ms, "
            f"状态: {'成功' if success else '失败'}"
        )

        return result

    def close(self) -> None:
        """
        关闭HTTP会话
        """
        self.session.close()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()
