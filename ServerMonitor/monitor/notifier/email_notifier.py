# -*- coding: utf-8 -*-
"""
邮件通知模块
通过SMTP发送告警邮件通知
"""

import logging
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.header import Header
from typing import List, Dict, Any

logger = logging.getLogger(__name__)


class EmailNotifier:
    """邮件通知类"""

    def __init__(self, config):
        """
        初始化邮件通知器

        Args:
            config: 配置对象
        """
        self.config = config
        self._enabled = config.get("smtp.enabled", False)
        self._server = config.get("smtp.server", "")
        self._port = config.get("smtp.port", 587)
        self._username = config.get("smtp.username", "")
        self._password = config.get("smtp.password", "")
        self._from_email = config.get("smtp.from_email", "")
        self._to_emails = config.get("smtp.to_emails", [])
        self._use_tls = config.get("smtp.use_tls", True)

    def is_enabled(self) -> bool:
        """
        检查邮件通知是否启用

        Returns:
            是否启用
        """
        return self._enabled and bool(self._server) and bool(self._to_emails)

    def send_alert(self, alerts: List[Dict[str, Any]]) -> bool:
        """
        发送告警邮件

        Args:
            alerts: 告警列表

        Returns:
            是否发送成功
        """
        if not self.is_enabled():
            return False

        warning_alerts = [a for a in alerts if a.get("level") == "warning"]
        if not warning_alerts:
            return False

        subject = "服务器资源监控告警"
        body = self._build_alert_body(warning_alerts)

        return self._send_email(subject, body)

    def send_report(self, report_path: str) -> bool:
        """
        发送报告邮件

        Args:
            report_path: 报告文件路径

        Returns:
            是否发送成功
        """
        if not self.is_enabled():
            return False

        subject = "服务器资源监控报告"
        body = f"服务器资源监控报告已生成，请查看附件。\n报告路径: {report_path}"

        return self._send_email(subject, body)

    def _build_alert_body(self, alerts: List[Dict[str, Any]]) -> str:
        """
        构建告警邮件内容

        Args:
            alerts: 告警列表

        Returns:
            邮件内容
        """
        body = "服务器资源监控告警\n\n"
        body += "=" * 50 + "\n\n"

        for alert in alerts:
            body += f"告警类型: {alert.get('type', 'unknown').upper()}\n"
            body += f"告警级别: {alert.get('level', 'unknown')}\n"
            body += f"当前值: {alert.get('current', 0)}\n"
            body += f"阈值: {alert.get('threshold', 0)}\n"
            body += f"消息: {alert.get('message', '')}\n"
            body += "-" * 50 + "\n\n"

        body += "请及时处理！\n"

        return body

    def _send_email(self, subject: str, body: str) -> bool:
        """
        发送邮件

        Args:
            subject: 邮件主题
            body: 邮件内容

        Returns:
            是否发送成功
        """
        try:
            logger.info(f"准备发送邮件: 主题={subject}, 收件人={self._to_emails}")

            msg = MIMEMultipart()
            msg["From"] = self._from_email
            msg["To"] = ", ".join(self._to_emails)
            msg["Subject"] = Header(subject, "utf-8")

            text_part = MIMEText(body, "plain", "utf-8")
            msg.attach(text_part)

            if self._use_tls:
                logger.debug(f"使用TLS连接SMTP服务器: {self._server}:{self._port}")
                server = smtplib.SMTP(self._server, self._port)
                server.starttls()
            else:
                logger.debug(f"使用SSL连接SMTP服务器: {self._server}:{self._port}")
                server = smtplib.SMTP_SSL(self._server, self._port)

            if self._username and self._password:
                logger.debug(f"使用SMTP认证: {self._username}")
                server.login(self._username, self._password)

            server.sendmail(self._from_email, self._to_emails, msg.as_string())
            server.quit()

            logger.info(f"邮件发送成功: {subject}")
            return True
        except smtplib.SMTPAuthenticationError as e:
            logger.error(f"SMTP认证失败: 用户名={self._username}, 错误={str(e)}")
            return False
        except smtplib.SMTPConnectError as e:
            logger.error(f"SMTP连接失败: 服务器={self._server}:{self._port}, 错误={str(e)}")
            return False
        except Exception as e:
            logger.error(f"邮件发送失败: {str(e)}", exc_info=True)
            return False

    def test_connection(self) -> bool:
        """
        测试邮件服务器连接

        Returns:
            是否连接成功
        """
        try:
            logger.info(f"测试邮件服务器连接: {self._server}:{self._port}")

            if self._use_tls:
                server = smtplib.SMTP(self._server, self._port)
                server.starttls()
            else:
                server = smtplib.SMTP_SSL(self._server, self._port)

            if self._username and self._password:
                server.login(self._username, self._password)

            server.quit()
            logger.info("邮件服务器连接测试成功")
            return True
        except smtplib.SMTPAuthenticationError as e:
            logger.error(f"SMTP认证失败: {str(e)}")
            return False
        except smtplib.SMTPConnectError as e:
            logger.error(f"SMTP连接失败: {str(e)}")
            return False
        except Exception as e:
            logger.error(f"邮件服务器连接测试失败: {str(e)}", exc_info=True)
            return False
