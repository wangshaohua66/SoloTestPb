# -*- coding: utf-8 -*-
"""
pytest配置文件
支持Allure报告生成和通用fixture
"""

import pytest
import allure
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


@pytest.fixture
def mock_config():
    """
    模拟配置对象fixture
    """
    class MockConfig:
        """模拟配置类"""
        interval = 1
        cpu_threshold = 80.0
        memory_threshold = 80.0
        disk_threshold = 85.0
        network_threshold = 100.0

        def __init__(self):
            self._data = {
                "smtp": {
                    "enabled": True,
                    "server": "smtp.test.com",
                    "port": 587,
                    "username": "test@test.com",
                    "password": "password",
                    "from_email": "monitor@test.com",
                    "to_emails": ["admin@test.com"],
                    "use_tls": True
                },
                "report": {
                    "enabled": True,
                    "interval": 3600,
                    "path": "./test_reports",
                    "format": "html"
                }
            }

        def get(self, key, default=None):
            """获取配置值"""
            keys = key.split('.')
            value = self._data
            try:
                for k in keys:
                    value = value[k]
                return value
            except (KeyError, TypeError):
                return default

    return MockConfig()


@pytest.fixture
def alert_manager(mock_config):
    """
    创建告警管理器实例
    """
    from monitor.notifier.alert_manager import AlertManager
    return AlertManager(mock_config)


@pytest.fixture
def cpu_monitor():
    """
    创建CPU监控实例
    """
    from monitor.core.cpu_monitor import CPUMonitor
    return CPUMonitor()


@pytest.fixture
def memory_monitor():
    """
    创建内存监控实例
    """
    from monitor.core.memory_monitor import MemoryMonitor
    return MemoryMonitor()


@pytest.fixture
def disk_monitor():
    """
    创建磁盘监控实例
    """
    from monitor.core.disk_monitor import DiskMonitor
    return DiskMonitor()


@pytest.fixture
def network_monitor():
    """
    创建网络监控实例
    """
    from monitor.core.network_monitor import NetworkMonitor
    return NetworkMonitor()


@pytest.fixture
def data_store():
    """
    创建数据存储实例
    """
    from monitor.core.data_store import DataStore
    return DataStore()


@pytest.fixture
def email_notifier(mock_config):
    """
    创建邮件通知实例
    """
    from monitor.notifier.email_notifier import EmailNotifier
    return EmailNotifier(mock_config)


@pytest.fixture
def report_generator(mock_config):
    """
    创建报告生成实例
    """
    from monitor.reporter.report_generator import ReportGenerator
    return ReportGenerator(mock_config)

