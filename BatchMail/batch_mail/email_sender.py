"""
邮件发送模块
负责构建和发送邮件，支持附件和HTML格式
"""

import mimetypes
import os
import smtplib
import time
from dataclasses import dataclass, field
from email import encoders
from email.header import Header
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.utils import formataddr
from typing import List, Optional

from .config.settings import RetryConfig, SMTPConfig
from .data_reader import Recipient
from .logger import SendLog


@dataclass
class EmailMessage:
    """
    邮件消息数据类
    封装一封待发送邮件的所有信息
    """

    subject: str
    body: str
    recipient: Recipient
    is_html: bool = True
    attachments: List[str] = field(default_factory=list)


class EmailSender:
    """
    邮件发送器类
    负责管理SMTP连接并发送邮件
    """

    def __init__(
        self,
        smtp_config: SMTPConfig,
        retry_config: Optional[RetryConfig] = None,
    ) -> None:
        """
        初始化邮件发送器

        Args:
            smtp_config: SMTP配置
            retry_config: 重试配置，默认使用默认配置
        """
        self.smtp_config = smtp_config
        self.retry_config = retry_config or RetryConfig()
        self._connection: Optional[smtplib.SMTP] = None

    def connect(self) -> None:
        """
        建立SMTP连接

        Raises:
            smtplib.SMTPException: 连接失败时
        """
        if self._connection is not None:
            try:
                self._connection.noop()
                return
            except smtplib.SMTPException:
                self._connection = None

        config = self.smtp_config

        if config.use_ssl:
            self._connection = smtplib.SMTP_SSL(
                config.host,
                config.port,
                timeout=config.timeout,
            )
        else:
            self._connection = smtplib.SMTP(
                config.host,
                config.port,
                timeout=config.timeout,
            )

            if config.use_tls:
                self._connection.starttls()

        self._connection.login(config.username, config.password)

    def disconnect(self) -> None:
        """
        关闭SMTP连接
        """
        if self._connection is not None:
            try:
                self._connection.quit()
            except smtplib.SMTPException:
                pass
            self._connection = None

    def build_message(self, email_msg: EmailMessage) -> MIMEMultipart:
        """
        构建邮件消息对象

        Args:
            email_msg: 邮件消息数据

        Returns:
            MIMEMultipart: 邮件消息对象
        """
        config = self.smtp_config
        msg = MIMEMultipart()

        sender_name = config.sender_name or config.username
        msg["From"] = formataddr((sender_name, config.username))
        msg["To"] = self._format_recipient(email_msg.recipient)
        msg["Subject"] = Header(email_msg.subject, "utf-8")

        body_content_type = "html" if email_msg.is_html else "plain"
        msg.attach(MIMEText(email_msg.body, body_content_type, "utf-8"))

        all_attachments = list(email_msg.attachments) + list(email_msg.recipient.attachments)
        for attachment_path in all_attachments:
            if attachment_path and os.path.exists(attachment_path):
                msg.attach(self._build_attachment(attachment_path))

        return msg

    def send(self, email_msg: EmailMessage) -> SendLog:
        """
        发送单封邮件（带重试机制）

        Args:
            email_msg: 邮件消息数据

        Returns:
            SendLog: 发送结果日志
        """
        last_error: Optional[str] = None
        attempt = 0

        while attempt < self.retry_config.max_retries:
            attempt += 1
            try:
                self.connect()
                msg = self.build_message(email_msg)
                recipients = [email_msg.recipient.email]
                self._connection.sendmail(
                    self.smtp_config.username,
                    recipients,
                    msg.as_string(),
                )
                return SendLog(
                    email=email_msg.recipient.email,
                    success=True,
                    attempt=attempt,
                    error_message=None,
                )
            except smtplib.SMTPAuthenticationError as e:
                last_error = f"SMTP认证失败: {e}"
                break
            except smtplib.SMTPException as e:
                last_error = f"SMTP错误: {e}"
                self.disconnect()
            except Exception as e:
                last_error = f"未知错误: {e}"
                self.disconnect()

            if attempt < self.retry_config.max_retries:
                delay = self.retry_config.retry_delay * (
                    self.retry_config.backoff_multiplier ** (attempt - 1)
                )
                time.sleep(delay)

        return SendLog(
            email=email_msg.recipient.email,
            success=False,
            attempt=attempt,
            error_message=last_error,
        )

    def _format_recipient(self, recipient: Recipient) -> str:
        """
        格式化收件人地址

        Args:
            recipient: 收件人对象

        Returns:
            str: 格式化后的收件人地址
        """
        if recipient.name:
            return formataddr((recipient.name, recipient.email))
        return recipient.email

    def _build_attachment(self, file_path: str) -> MIMEBase:
        """
        构建邮件附件

        Args:
            file_path: 附件文件路径

        Returns:
            MIMEBase: 附件对象

        Raises:
            FileNotFoundError: 文件不存在时
        """
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"附件文件不存在: {file_path}")

        filename = os.path.basename(file_path)
        content_type, _ = mimetypes.guess_type(filename)

        if content_type is None:
            content_type = "application/octet-stream"

        maintype, subtype = content_type.split("/", 1)

        with open(file_path, "rb") as f:
            part = MIMEBase(maintype, subtype)
            part.set_payload(f.read())

        encoders.encode_base64(part)
        part.add_header(
            "Content-Disposition",
            f'attachment; filename="{filename}"',
        )

        return part

    def __enter__(self) -> "EmailSender":
        """
        上下文管理器入口

        Returns:
            EmailSender: 自身实例
        """
        self.connect()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb) -> bool:
        """
        上下文管理器出口

        Args:
            exc_type: 异常类型
            exc_val: 异常值
            exc_tb: 异常追踪

        Returns:
            bool: 是否抑制异常
        """
        self.disconnect()
        return False
