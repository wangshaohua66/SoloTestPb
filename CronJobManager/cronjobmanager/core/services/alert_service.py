"""
告警服务模块
负责任务状态异常时的告警通知
"""

import smtplib
import json
from email.mime.text import MIMEText
from email.header import Header
from typing import Optional

import urllib.request
import urllib.error

from core.config import Config
from core.utils.logger import get_logger


logger = get_logger(__name__)


class AlertService:
    """
    告警服务类
    提供邮件和Webhook两种告警方式
    """

    def __init__(self, config: Config = None):
        """
        初始化告警服务

        :param config: 配置对象
        """
        self.config = config or Config()
        self.enabled = self.config.get("alert.enabled", False)

    def send_alert(self, message: str, title: str = "任务告警") -> bool:
        """
        发送告警通知

        :param message: 告警消息内容
        :param title: 告警标题
        :return: 是否发送成功
        """
        if not self.enabled:
            logger.debug("告警功能未启用，跳过告警发送")
            return False

        email_success = False
        webhook_success = False

        if self._email_configured():
            email_success = self._send_email_alert(message, title)

        if self._webhook_configured():
            webhook_success = self._send_webhook_alert(message, title)

        return email_success or webhook_success

    def _email_configured(self) -> bool:
        """
        检查邮件配置是否完整

        :return: 邮件配置是否完整
        """
        smtp_server = self.config.get("alert.email.smtp_server")
        sender = self.config.get("alert.email.sender")
        recipients = self.config.get("alert.email.recipients", [])

        return bool(smtp_server and sender and recipients)

    def _webhook_configured(self) -> bool:
        """
        检查Webhook配置是否完整

        :return: Webhook配置是否完整
        """
        webhook_url = self.config.get("alert.webhook.url")
        return bool(webhook_url)

    def _send_email_alert(self, message: str, title: str) -> bool:
        """
        发送邮件告警

        :param message: 告警消息内容
        :param title: 邮件标题
        :return: 是否发送成功
        """
        try:
            smtp_server = self.config.get("alert.email.smtp_server")
            smtp_port = self.config.get("alert.email.smtp_port", 587)
            sender = self.config.get("alert.email.sender")
            recipients = self.config.get("alert.email.recipients", [])
            username = self.config.get("alert.email.username")
            password = self.config.get("alert.email.password")

            msg = MIMEText(message, "plain", "utf-8")
            msg["From"] = Header(sender, "utf-8")
            msg["To"] = Header(", ".join(recipients), "utf-8")
            msg["Subject"] = Header(title, "utf-8")

            with smtplib.SMTP(smtp_server, smtp_port) as server:
                server.starttls()
                if username and password:
                    server.login(username, password)
                server.sendmail(sender, recipients, msg.as_string())

            logger.info(f"邮件告警发送成功，收件人: {recipients}")
            return True

        except Exception as e:
            logger.error(f"邮件告警发送失败: {str(e)}")
            return False

    def _send_webhook_alert(self, message: str, title: str) -> bool:
        """
        发送Webhook告警

        :param message: 告警消息内容
        :param title: 告警标题
        :return: 是否发送成功
        """
        try:
            webhook_url = self.config.get("alert.webhook.url")
            headers = self.config.get("alert.webhook.headers", {})

            payload = json.dumps({
                "title": title,
                "message": message,
                "timestamp": self._get_current_timestamp(),
            }).encode("utf-8")

            req = urllib.request.Request(
                webhook_url,
                data=payload,
                headers=headers,
                method="POST",
            )
            req.add_header("Content-Type", "application/json")

            with urllib.request.urlopen(req, timeout=10) as response:
                status_code = response.getcode()
                if 200 <= status_code < 300:
                    logger.info("Webhook告警发送成功")
                    return True
                else:
                    logger.error(f"Webhook告警发送失败，状态码: {status_code}")
                    return False

        except urllib.error.URLError as e:
            logger.error(f"Webhook告警请求失败: {str(e)}")
            return False
        except Exception as e:
            logger.error(f"Webhook告警发送异常: {str(e)}")
            return False

    def send_task_failure_alert(
        self,
        task_name: str,
        task_id: str,
        error_message: str,
        retry_count: int,
    ) -> bool:
        """
        发送任务失败告警

        :param task_name: 任务名称
        :param task_id: 任务ID
        :param error_message: 错误信息
        :param retry_count: 已重试次数
        :return: 是否发送成功
        """
        message = (
            f"任务执行失败告警\n"
            f"任务名称: {task_name}\n"
            f"任务ID: {task_id}\n"
            f"错误信息: {error_message}\n"
            f"已重试次数: {retry_count}\n"
        )
        title = f"任务失败告警 - {task_name}"
        return self.send_alert(message, title)

    @staticmethod
    def _get_current_timestamp() -> str:
        """
        获取当前时间戳字符串

        :return: ISO格式的时间戳
        """
        from datetime import datetime
        return datetime.utcnow().isoformat()
