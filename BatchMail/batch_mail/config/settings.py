"""
SMTP配置管理模块
用于加载和管理SMTP邮件服务器的配置信息
"""

import os
from dataclasses import dataclass, field
from typing import Any, Dict, Optional

from dotenv import load_dotenv


@dataclass
class SMTPConfig:
    """
    SMTP服务器配置数据类
    封装SMTP连接所需的所有参数
    """

    host: str
    port: int
    username: str
    password: str
    use_tls: bool = True
    use_ssl: bool = False
    timeout: int = 30
    sender_name: Optional[str] = None

    def __post_init__(self) -> None:
        """
        初始化后校验配置
        """
        if not self.host:
            raise ValueError("SMTP服务器地址不能为空")
        if not self.username:
            raise ValueError("SMTP用户名不能为空")
        if not self.password:
            raise ValueError("SMTP密码不能为空")
        if self.port <= 0 or self.port > 65535:
            raise ValueError("SMTP端口号必须在1-65535之间")


@dataclass
class RetryConfig:
    """
    重试策略配置
    """

    max_retries: int = 3
    retry_delay: float = 2.0
    backoff_multiplier: float = 2.0


@dataclass
class AppConfig:
    """
    应用全局配置
    """

    smtp: SMTPConfig
    retry: RetryConfig = field(default_factory=RetryConfig)
    batch_size: int = 50
    log_level: str = "INFO"
    log_file: Optional[str] = None


def load_smtp_config(config_dict: Optional[Dict[str, Any]] = None) -> SMTPConfig:
    """
    从配置字典或环境变量加载SMTP配置

    Args:
        config_dict: 配置字典，如果为None则从环境变量加载

    Returns:
        SMTPConfig: SMTP配置对象

    Raises:
        ValueError: 当必要的配置缺失时
    """
    load_dotenv()

    if config_dict is None:
        config_dict = {}

    host = config_dict.get("smtp_host") or os.getenv("SMTP_HOST")
    port = int(config_dict.get("smtp_port") or os.getenv("SMTP_PORT", "465"))
    username = config_dict.get("smtp_username") or os.getenv("SMTP_USERNAME")
    password = config_dict.get("smtp_password") or os.getenv("SMTP_PASSWORD")
    use_tls = bool(config_dict.get("smtp_use_tls") or os.getenv("SMTP_USE_TLS", "True"))
    use_ssl = bool(config_dict.get("smtp_use_ssl") or os.getenv("SMTP_USE_SSL", "False"))
    timeout = int(config_dict.get("smtp_timeout") or os.getenv("SMTP_TIMEOUT", "30"))
    sender_name = config_dict.get("sender_name") or os.getenv("SENDER_NAME")

    return SMTPConfig(
        host=host,
        port=port,
        username=username,
        password=password,
        use_tls=use_tls,
        use_ssl=use_ssl,
        timeout=timeout,
        sender_name=sender_name,
    )


def load_retry_config(config_dict: Optional[Dict[str, Any]] = None) -> RetryConfig:
    """
    加载重试配置

    Args:
        config_dict: 配置字典

    Returns:
        RetryConfig: 重试配置对象
    """
    load_dotenv()

    if config_dict is None:
        config_dict = {}

    max_retries = int(config_dict.get("max_retries") or os.getenv("MAX_RETRIES", "3"))
    retry_delay = float(config_dict.get("retry_delay") or os.getenv("RETRY_DELAY", "2.0"))
    backoff_multiplier = float(
        config_dict.get("backoff_multiplier") or os.getenv("BACKOFF_MULTIPLIER", "2.0")
    )

    return RetryConfig(
        max_retries=max_retries,
        retry_delay=retry_delay,
        backoff_multiplier=backoff_multiplier,
    )
