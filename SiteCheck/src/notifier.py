"""
告警通知模块
支持邮件和Webhook两种告警通知方式
"""

import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Dict, Any
import logging
import requests
from datetime import datetime
import json

from .http_checker import CheckResult
from .ssl_checker import SSLCheckResult


class Notifier:
    """
    告警通知基类
    定义通知接口
    """

    def send_alert(self, result: Any, alert_type: str) -> bool:
        """
        发送告警通知

        Args:
            result: 检测结果对象
            alert_type: 告警类型（'http'或'ssl'）

        Returns:
            是否发送成功
        """
        raise NotImplementedError("子类必须实现send_alert方法")


class EmailNotifier(Notifier):
    """
    邮件通知类
    通过SMTP发送告警邮件
    """

    def __init__(self, config: Dict[str, Any]):
        """
        初始化邮件通知器

        Args:
            config: 邮件配置字典
        """
        self.config = config
        self.enabled = config.get('enabled', False)
        self.smtp_server = config.get('smtp_server')
        self.smtp_port = config.get('smtp_port', 587)
        self.use_tls = config.get('use_tls', True)
        self.username = config.get('username')
        self.password = config.get('password')
        self.recipients = config.get('recipients', [])
        self.logger = logging.getLogger(__name__)

    def send_alert(self, result: Any, alert_type: str) -> bool:
        """
        发送邮件告警

        Args:
            result: 检测结果对象
            alert_type: 告警类型

        Returns:
            是否发送成功
        """
        if not self.enabled:
            self.logger.debug("邮件通知未启用，跳过发送")
            return False

        if not self.recipients:
            self.logger.warning("邮件收件人列表为空，跳过发送")
            return False

        try:
            subject, body = self._generate_email_content(result, alert_type)
            msg = MIMEMultipart()
            msg['From'] = self.username
            msg['To'] = ', '.join(self.recipients)
            msg['Subject'] = subject

            msg.attach(MIMEText(body, 'plain', 'utf-8'))

            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                if self.use_tls:
                    server.starttls()
                server.login(self.username, self.password)
                server.send_message(msg)

            self.logger.info(f"邮件告警已发送至: {', '.join(self.recipients)}")
            return True

        except Exception as e:
            self.logger.error(f"发送邮件告警失败: {e}")
            return False

    def _generate_email_content(self, result: Any, alert_type: str) -> tuple:
        """
        生成邮件主题和内容

        Args:
            result: 检测结果对象
            alert_type: 告警类型

        Returns:
            (主题, 内容)元组
        """
        if alert_type == 'http':
            subject = f"【告警】网站 {result.site_name} 访问异常"
            body = f"""
网站健康检测告警通知

站点名称: {result.site_name}
站点URL: {result.url}
检测时间: {result.timestamp.strftime('%Y-%m-%d %H:%M:%S')}
检测状态: 失败
HTTP状态码: {result.status_code or 'N/A'}
响应时间: {result.response_time}ms
错误信息: {result.error_message or '未知错误'}

请及时处理此问题。

--
网站健康检测系统
"""
        elif alert_type == 'ssl':
            subject = f"【告警】网站 {result.site_name} SSL证书异常"
            expiry_info = f"{result.days_until_expiry}天后过期" if result.days_until_expiry else "已过期"
            body = f"""
SSL证书检测告警通知

站点名称: {result.site_name}
站点URL: {result.url}
检测时间: {result.timestamp.strftime('%Y-%m-%d %H:%M:%S')}
证书状态: {'即将过期' if result.days_until_expiry and result.days_until_expiry > 0 else '已过期'}
过期时间: {result.expiry_date.strftime('%Y-%m-%d %H:%M:%S') if result.expiry_date else 'N/A'}
剩余天数: {expiry_info}
签发者: {result.issuer or 'N/A'}

请及时更新SSL证书。

--
网站健康检测系统
"""
        else:
            subject = "【告警】网站健康检测系统异常"
            body = "未知类型的告警通知。"

        return subject, body


class WebhookNotifier(Notifier):
    """
    Webhook通知类
    通过HTTP Webhook发送告警通知
    """

    def __init__(self, config: Dict[str, Any]):
        """
        初始化Webhook通知器

        Args:
            config: Webhook配置字典
        """
        self.config = config
        self.enabled = config.get('enabled', False)
        self.url = config.get('url')
        self.method = config.get('method', 'POST').upper()
        self.headers = config.get('headers', {})
        self.body_template = config.get('body_template', '{}')
        self.logger = logging.getLogger(__name__)

    def send_alert(self, result: Any, alert_type: str) -> bool:
        """
        发送Webhook告警

        Args:
            result: 检测结果对象
            alert_type: 告警类型

        Returns:
            是否发送成功
        """
        if not self.enabled:
            self.logger.debug("Webhook通知未启用，跳过发送")
            return False

        try:
            payload = self._generate_payload(result, alert_type)
            response = requests.request(
                self.method,
                self.url,
                headers=self.headers,
                json=payload,
                timeout=10
            )
            response.raise_for_status()
            self.logger.info(f"Webhook告警已发送至: {self.url}")
            return True

        except Exception as e:
            self.logger.error(f"发送Webhook告警失败: {e}")
            return False

    def _generate_payload(self, result: Any, alert_type: str) -> Dict[str, Any]:
        """
        生成Webhook请求负载

        Args:
            result: 检测结果对象
            alert_type: 告警类型

        Returns:
            请求字典
        """
        base_payload = {
            'site_name': result.site_name,
            'url': result.url,
            'alert_type': alert_type,
            'timestamp': result.timestamp.strftime('%Y-%m-%d %H:%M:%S'),
            'status': 'error'
        }

        if alert_type == 'http':
            base_payload.update({
                'status_code': result.status_code,
                'response_time': result.response_time,
                'error_message': result.error_message,
                'success': result.success
            })
        elif alert_type == 'ssl':
            base_payload.update({
                'ssl_valid': result.valid,
                'expiry_date': result.expiry_date.strftime('%Y-%m-%d %H:%M:%S') if result.expiry_date else None,
                'days_until_expiry': result.days_until_expiry,
                'issuer': result.issuer
            })

        return base_payload


class NotificationManager:
    """
    通知管理器
    管理所有通知渠道并统一发送告警
    """

    def __init__(self, config: Dict[str, Any]):
        """
        初始化通知管理器

        Args:
            config: 通知配置字典
        """
        self.config = config
        self.notifiers: list[Notifier] = []
        self.logger = logging.getLogger(__name__)
        self._setup_notifiers()

    def _setup_notifiers(self) -> None:
        """
        设置通知渠道
        """
        email_config = self.config.get('email', {})
        if email_config.get('enabled', False):
            self.notifiers.append(EmailNotifier(email_config))

        webhook_config = self.config.get('webhook', {})
        if webhook_config.get('enabled', False):
            self.notifiers.append(WebhookNotifier(webhook_config))

        self.logger.info(f"已配置 {len(self.notifiers)} 个通知渠道")

    def send_http_alert(self, result: CheckResult) -> None:
        """
        发送HTTP检测告警

        Args:
            result: HTTP检测结果
        """
        if result.success:
            return

        self.logger.info(f"准备发送HTTP告警: {result.site_name}")
        for notifier in self.notifiers:
            try:
                notifier.send_alert(result, 'http')
            except Exception as e:
                self.logger.error(f"通知渠道发送失败: {e}")

    def send_ssl_alert(self, result: SSLCheckResult) -> None:
        """
        发送SSL证书检测告警

        Args:
            result: SSL检测结果
        """
        self.logger.info(f"准备发送SSL告警: {result.site_name}")
        for notifier in self.notifiers:
            try:
                notifier.send_alert(result, 'ssl')
            except Exception as e:
                self.logger.error(f"通知渠道发送失败: {e}")
