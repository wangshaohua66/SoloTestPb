"""
批量邮件发送工具包
"""

__version__ = "1.0.0"

from .batch_mailer import BatchMailer, BatchResult
from .config.settings import (
    AppConfig,
    RetryConfig,
    SMTPConfig,
    load_retry_config,
    load_smtp_config,
)
from .data_reader import DataReader, Recipient
from .email_sender import EmailMessage, EmailSender
from .logger import SendLog, setup_logger
from .template_renderer import TemplateRenderer

__all__ = [
    "BatchMailer",
    "BatchResult",
    "DataReader",
    "Recipient",
    "TemplateRenderer",
    "EmailMessage",
    "EmailSender",
    "SendLog",
    "SMTPConfig",
    "RetryConfig",
    "AppConfig",
    "setup_logger",
    "load_smtp_config",
    "load_retry_config",
]
