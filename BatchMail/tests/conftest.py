"""
pytest配置和fixture
"""

import os
import tempfile
from typing import List

import pytest
import pandas as pd

from batch_mail.config.settings import RetryConfig, SMTPConfig
from batch_mail.data_reader import Recipient


@pytest.fixture
def temp_dir() -> str:
    """
    创建临时目录fixture

    Returns:
        str: 临时目录路径
    """
    with tempfile.TemporaryDirectory() as tmpdir:
        yield tmpdir


@pytest.fixture
def sample_csv_path(temp_dir: str) -> str:
    """
    创建示例CSV文件fixture

    Args:
        temp_dir: 临时目录

    Returns:
        str: CSV文件路径
    """
    csv_path = os.path.join(temp_dir, "recipients.csv")
    df = pd.DataFrame({
        "email": ["test1@example.com", "test2@example.com", "test3@example.com"],
        "name": ["张三", "李四", "王五"],
        "company": ["科技公司", "贸易公司", "咨询公司"],
    })
    df.to_csv(csv_path, index=False)
    return csv_path


@pytest.fixture
def sample_excel_path(temp_dir: str) -> str:
    """
    创建示例Excel文件fixture

    Args:
        temp_dir: 临时目录

    Returns:
        str: Excel文件路径
    """
    xlsx_path = os.path.join(temp_dir, "recipients.xlsx")
    df = pd.DataFrame({
        "email": ["test1@example.com", "test2@example.com"],
        "name": ["张三", "李四"],
        "discount": ["10%", "20%"],
    })
    df.to_excel(xlsx_path, index=False)
    return xlsx_path


@pytest.fixture
def sample_recipients() -> List[Recipient]:
    """
    示例收件人列表fixture

    Returns:
        List[Recipient]: 收件人列表
    """
    return [
        Recipient(
            email="test1@example.com",
            name="张三",
            variables={"company": "科技公司"},
        ),
        Recipient(
            email="test2@example.com",
            name="李四",
            variables={"company": "贸易公司"},
        ),
    ]


@pytest.fixture
def smtp_config() -> SMTPConfig:
    """
    SMTP配置fixture

    Returns:
        SMTPConfig: SMTP配置
    """
    return SMTPConfig(
        host="smtp.example.com",
        port=465,
        username="test@example.com",
        password="test_password",
        use_ssl=True,
    )


@pytest.fixture
def retry_config() -> RetryConfig:
    """
    重试配置fixture

    Returns:
        RetryConfig: 重试配置
    """
    return RetryConfig(
        max_retries=2,
        retry_delay=0.1,
        backoff_multiplier=1.0,
    )
