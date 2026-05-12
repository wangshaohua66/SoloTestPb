"""
pytest配置文件
提供测试fixture和配置
"""

import os
import pytest
import tempfile

from core.config import Config
from core.database import DatabaseManager


@pytest.fixture
def test_config():
    """
    测试配置fixture
    使用内存SQLite数据库

    :return: 测试配置对象
    """
    return Config({
        "database": {
            "url": "sqlite:///:memory:",
            "echo": False,
        },
        "scheduler": {
            "timezone": "Asia/Shanghai",
            "max_concurrent_jobs": 50,
            "misfire_grace_time": 30,
        },
        "logging": {
            "level": "DEBUG",
            "log_dir": tempfile.mkdtemp(),
        },
        "alert": {
            "enabled": False,
        },
    })


@pytest.fixture
def db_manager(test_config):
    """
    数据库管理器fixture

    :param test_config: 测试配置
    :return: 数据库管理器实例
    """
    # 重置单例
    DatabaseManager._instance = None
    
    db = DatabaseManager(test_config)
    db.create_tables()
    
    yield db
    
    db.drop_tables()
    db.close()


@pytest.fixture
def temp_db_path():
    """
    临时数据库路径fixture

    :return: 临时数据库文件路径
    """
    fd, path = tempfile.mkstemp(suffix=".db")
    os.close(fd)
    
    yield path
    
    if os.path.exists(path):
        os.remove(path)
