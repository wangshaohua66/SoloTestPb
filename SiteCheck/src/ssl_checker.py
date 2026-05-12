"""
SSL证书检测模块
负责检测网站SSL证书的有效期并在即将过期时发出提醒
"""

import ssl
import socket
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, Tuple
import logging
from dataclasses import dataclass
from urllib.parse import urlparse


@dataclass
class SSLCheckResult:
    """
    SSL证书检测结果数据类
    存储SSL证书检测的结果信息
    """
    site_name: str
    url: str
    success: bool
    valid: bool
    expiry_date: Optional[datetime]
    days_until_expiry: Optional[int]
    issuer: Optional[str]
    subject: Optional[str]
    error_message: Optional[str]
    timestamp: datetime


class SSLChecker:
    """
    SSL证书检测类
    负责检测网站SSL证书的有效期
    """

    def __init__(self, timeout: int = 10, alert_days: int = 30):
        """
        初始化SSL检测器

        Args:
            timeout: 连接超时时间（秒）
            alert_days: 到期前多少天开始告警
        """
        self.timeout = timeout
        self.alert_days = alert_days
        self.logger = logging.getLogger(__name__)

    def _parse_url(self, url: str) -> Tuple[str, int]:
        """
        解析URL获取主机名和端口

        Args:
            url: 网站URL

        Returns:
            (主机名, 端口)元组
        """
        parsed = urlparse(url)
        hostname = parsed.hostname or parsed.path
        port = parsed.port or 443

        if not hostname:
            raise ValueError(f"无法解析URL中的主机名: {url}")

        return hostname, port

    def _get_cert(self, hostname: str, port: int) -> Dict[str, Any]:
        """
        获取服务器SSL证书信息

        Args:
            hostname: 主机名
            port: 端口号

        Returns:
            证书信息字典
        """
        context = ssl.create_default_context()

        with socket.create_connection((hostname, port), timeout=self.timeout) as sock:
            with context.wrap_socket(sock, server_hostname=hostname) as secure_sock:
                cert = secure_sock.getpeercert()

        if not cert:
            raise ValueError("无法获取服务器证书")

        return cert

    def check(self, site: Dict[str, Any]) -> SSLCheckResult:
        """
        执行单个网站的SSL证书检测

        Args:
            site: 站点配置字典，包含url、name等信息

        Returns:
            SSLCheckResult对象，包含SSL检测结果信息
        """
        url = site.get('url')
        site_name = site.get('name', url)

        self.logger.info(f"开始检测SSL证书: {site_name} ({url})")

        success = False
        valid = False
        expiry_date = None
        days_until_expiry = None
        issuer = None
        subject = None
        error_message = None

        try:
            if not url.startswith('https://'):
                error_message = "非HTTPS协议，跳过SSL检测"
                self.logger.info(f"{site_name}: {error_message}")
                return SSLCheckResult(
                    site_name=site_name,
                    url=url,
                    success=True,
                    valid=True,
                    expiry_date=None,
                    days_until_expiry=None,
                    issuer=None,
                    subject=None,
                    error_message=error_message,
                    timestamp=datetime.now()
                )

            hostname, port = self._parse_url(url)
            cert = self._get_cert(hostname, port)

            not_after_str = cert.get('notAfter')
            if not_after_str:
                expiry_date = datetime.strptime(not_after_str, '%b %d %H:%M:%S %Y %Z')
                days_until_expiry = (expiry_date - datetime.now()).days

            issuer_components = cert.get('issuer', [])
            issuer = ', '.join([f"{k}={v}" for comp in issuer_components for k, v in comp])

            subject_components = cert.get('subject', [])
            subject = ', '.join([f"{k}={v}" for comp in subject_components for k, v in comp])

            if days_until_expiry is not None and days_until_expiry > 0:
                valid = True
                success = True
                if days_until_expiry <= self.alert_days:
                    self.logger.warning(
                        f"{site_name} SSL证书将在 {days_until_expiry} 天后过期"
                    )
                else:
                    self.logger.info(
                        f"{site_name} SSL证书有效，剩余 {days_until_expiry} 天"
                    )
            else:
                valid = False
                success = True
                error_message = "SSL证书已过期"
                self.logger.error(f"{site_name} {error_message}")

        except socket.timeout:
            error_message = "连接超时"
            self.logger.error(f"{site_name} SSL检测失败: {error_message}")

        except ssl.SSLError as e:
            error_message = f"SSL错误: {str(e)}"
            self.logger.error(f"{site_name} SSL检测失败: {error_message}")

        except Exception as e:
            error_message = f"未知错误: {str(e)}"
            self.logger.error(f"{site_name} SSL检测失败: {error_message}")

        result = SSLCheckResult(
            site_name=site_name,
            url=url,
            success=success,
            valid=valid,
            expiry_date=expiry_date,
            days_until_expiry=days_until_expiry,
            issuer=issuer,
            subject=subject,
            error_message=error_message,
            timestamp=datetime.now()
        )

        return result

    def needs_alert(self, result: SSLCheckResult) -> bool:
        """
        判断是否需要发出告警

        Args:
            result: SSL检测结果

        Returns:
            是否需要告警
        """
        if not result.success:
            return True

        if result.days_until_expiry is not None:
            return result.days_until_expiry <= self.alert_days

        return False
