"""
邮件发送模块单元测试
"""

import os
from unittest.mock import MagicMock, patch

import allure
import pytest

from batch_mail.config.settings import RetryConfig, SMTPConfig
from batch_mail.data_reader import Recipient
from batch_mail.email_sender import EmailMessage, EmailSender


@allure.feature("邮件发送")
@allure.story("EmailMessage数据类")
class TestEmailMessage:
    """
    EmailMessage测试类
    """

    @allure.title("测试EmailMessage初始化")
    def test_email_message_init(self, sample_recipients):
        """
        测试EmailMessage正常初始化
        """
        msg = EmailMessage(
            subject="测试邮件",
            body="<h1>Hello</h1>",
            recipient=sample_recipients[0],
            is_html=True,
            attachments=["file.pdf"],
        )

        assert msg.subject == "测试邮件"
        assert msg.body == "<h1>Hello</h1>"
        assert msg.is_html is True
        assert msg.attachments == ["file.pdf"]

    @allure.title("测试EmailMessage默认值")
    def test_email_message_defaults(self, sample_recipients):
        """
        测试EmailMessage默认值
        """
        msg = EmailMessage(
            subject="Test",
            body="Hello",
            recipient=sample_recipients[0],
        )

        assert msg.is_html is True
        assert msg.attachments == []


@allure.feature("邮件发送")
@allure.story("邮件构建")
class TestEmailSenderBuild:
    """
    EmailSender构建消息测试类
    """

    @allure.title("测试构建HTML邮件")
    def test_build_html_message(self, smtp_config, sample_recipients):
        """
        测试构建HTML格式邮件
        """
        sender = EmailSender(smtp_config=smtp_config)
        email_msg = EmailMessage(
            subject="HTML测试",
            body="<h1>Hello World</h1>",
            recipient=sample_recipients[0],
            is_html=True,
        )

        msg = sender.build_message(email_msg)

        assert msg["Subject"] is not None
        assert msg["To"] is not None
        assert msg["From"] is not None

        payload = msg.get_payload()
        assert len(payload) > 0

    @allure.title("测试构建纯文本邮件")
    def test_build_plain_message(self, smtp_config, sample_recipients):
        """
        测试构建纯文本邮件
        """
        sender = EmailSender(smtp_config=smtp_config)
        email_msg = EmailMessage(
            subject="纯文本测试",
            body="Hello World",
            recipient=sample_recipients[0],
            is_html=False,
        )

        msg = sender.build_message(email_msg)

        assert msg["Subject"] is not None

    @allure.title("测试构建带附件的邮件")
    def test_build_message_with_attachment(self, smtp_config, sample_recipients, temp_dir):
        """
        测试构建带附件的邮件
        """
        attachment_path = os.path.join(temp_dir, "test_file.txt")
        with open(attachment_path, "w") as f:
            f.write("测试附件内容")

        sender = EmailSender(smtp_config=smtp_config)
        email_msg = EmailMessage(
            subject="附件测试",
            body="见附件",
            recipient=sample_recipients[0],
            attachments=[attachment_path],
        )

        msg = sender.build_message(email_msg)

        payload = msg.get_payload()
        assert len(payload) > 1

    @allure.title("测试不存在的附件抛出异常")
    def test_build_attachment_not_found(self, smtp_config):
        """
        测试附件不存在时抛出FileNotFoundError
        """
        sender = EmailSender(smtp_config=smtp_config)

        with pytest.raises(FileNotFoundError):
            sender._build_attachment("/nonexistent/file.pdf")

    @allure.title("测试格式化收件人有名字")
    def test_format_recipient_with_name(self, smtp_config):
        """
        测试格式化有名字的收件人
        """
        from email.header import decode_header

        sender = EmailSender(smtp_config=smtp_config)
        recipient = Recipient(email="test@example.com", name="张三")

        formatted = sender._format_recipient(recipient)

        assert "test@example.com" in formatted
        assert "<" in formatted and ">" in formatted

        name_part = formatted.split("<")[0].strip()
        decoded = decode_header(name_part)
        decoded_name = "".join(
            part[0].decode(part[1] or "utf-8") if isinstance(part[0], bytes) else part[0]
            for part in decoded
        )
        assert "张三" in decoded_name

    @allure.title("测试格式化收件人无名字")
    def test_format_recipient_without_name(self, smtp_config):
        """
        测试格式化无名字的收件人
        """
        sender = EmailSender(smtp_config=smtp_config)
        recipient = Recipient(email="test@example.com")

        formatted = sender._format_recipient(recipient)

        assert formatted == "test@example.com"


@allure.feature("邮件发送")
@allure.story("SMTP连接管理")
class TestEmailSenderConnection:
    """
    EmailSender连接管理测试类
    """

    @allure.title("测试SSL连接")
    @patch("batch_mail.email_sender.smtplib.SMTP_SSL")
    def test_connect_ssl(self, mock_smtp_ssl, smtp_config):
        """
        测试SSL连接
        """
        mock_conn = MagicMock()
        mock_smtp_ssl.return_value = mock_conn

        sender = EmailSender(smtp_config=smtp_config)
        sender.connect()

        mock_smtp_ssl.assert_called_once()
        mock_conn.login.assert_called_once_with(smtp_config.username, smtp_config.password)

    @allure.title("测试TLS连接")
    @patch("batch_mail.email_sender.smtplib.SMTP")
    def test_connect_tls(self, mock_smtp):
        """
        测试TLS连接
        """
        mock_conn = MagicMock()
        mock_smtp.return_value = mock_conn

        smtp_config = SMTPConfig(
            host="smtp.example.com",
            port=587,
            username="test@example.com",
            password="secret",
            use_tls=True,
            use_ssl=False,
        )

        sender = EmailSender(smtp_config=smtp_config)
        sender.connect()

        mock_smtp.assert_called_once()
        mock_conn.starttls.assert_called_once()

    @allure.title("测试断开连接")
    @patch("batch_mail.email_sender.smtplib.SMTP_SSL")
    def test_disconnect(self, mock_smtp_ssl, smtp_config):
        """
        测试断开连接
        """
        mock_conn = MagicMock()
        mock_smtp_ssl.return_value = mock_conn

        sender = EmailSender(smtp_config=smtp_config)
        sender.connect()
        sender.disconnect()

        mock_conn.quit.assert_called_once()

    @allure.title("测试上下文管理器")
    @patch("batch_mail.email_sender.smtplib.SMTP_SSL")
    def test_context_manager(self, mock_smtp_ssl, smtp_config):
        """
        测试上下文管理器
        """
        mock_conn = MagicMock()
        mock_smtp_ssl.return_value = mock_conn

        with EmailSender(smtp_config=smtp_config) as sender:
            assert sender._connection is not None

        mock_conn.quit.assert_called_once()


@allure.feature("邮件发送")
@allure.story("邮件发送")
class TestEmailSenderSend:
    """
    EmailSender发送测试类
    """

    @allure.title("测试发送成功")
    @patch("batch_mail.email_sender.smtplib.SMTP_SSL")
    def test_send_success(self, mock_smtp_ssl, smtp_config, sample_recipients):
        """
        测试发送成功
        """
        mock_conn = MagicMock()
        mock_smtp_ssl.return_value = mock_conn

        sender = EmailSender(smtp_config=smtp_config, retry_config=RetryConfig(max_retries=1))
        email_msg = EmailMessage(
            subject="测试",
            body="内容",
            recipient=sample_recipients[0],
        )

        result = sender.send(email_msg)

        assert result.success is True
        assert result.attempt == 1
        assert result.email == sample_recipients[0].email

    @allure.title("测试发送失败重试")
    @patch("batch_mail.email_sender.smtplib.SMTP_SSL")
    def test_send_failure_retry(self, mock_smtp_ssl, smtp_config, sample_recipients):
        """
        测试发送失败后重试
        """
        import smtplib

        mock_conn = MagicMock()
        mock_conn.sendmail.side_effect = smtplib.SMTPException("Connection error")
        mock_smtp_ssl.return_value = mock_conn

        retry_config = RetryConfig(max_retries=3, retry_delay=0.01, backoff_multiplier=1.0)
        sender = EmailSender(smtp_config=smtp_config, retry_config=retry_config)
        email_msg = EmailMessage(
            subject="测试",
            body="内容",
            recipient=sample_recipients[0],
        )

        result = sender.send(email_msg)

        assert result.success is False
        assert result.attempt == 3
        assert result.error_message is not None

    @allure.title("测试认证失败不重试")
    @patch("batch_mail.email_sender.smtplib.SMTP_SSL")
    def test_auth_failure_no_retry(self, mock_smtp_ssl, smtp_config, sample_recipients):
        """
        测试认证失败时不重试
        """
        import smtplib

        mock_conn = MagicMock()
        mock_conn.login.side_effect = smtplib.SMTPAuthenticationError(535, "Auth failed")
        mock_smtp_ssl.return_value = mock_conn

        retry_config = RetryConfig(max_retries=3, retry_delay=0.01)
        sender = EmailSender(smtp_config=smtp_config, retry_config=retry_config)
        email_msg = EmailMessage(
            subject="测试",
            body="内容",
            recipient=sample_recipients[0],
        )

        result = sender.send(email_msg)

        assert result.success is False
        assert result.attempt == 1
        assert "SMTP认证失败" in result.error_message
