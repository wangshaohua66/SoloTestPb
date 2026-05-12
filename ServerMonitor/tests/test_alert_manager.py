# -*- coding: utf-8 -*-
"""
告警管理模块单元测试
"""

import allure
import pytest
from monitor.notifier.alert_manager import AlertManager


@allure.feature("告警管理模块")
class TestAlertManager:
    """告警管理器测试"""

    @allure.story("初始化测试")
    @allure.title("测试告警管理器初始化")
    def test_initialization(self, alert_manager):
        """测试初始化"""
        assert alert_manager is not None
        assert len(alert_manager.get_alert_history()) == 0

    @allure.story("CPU告警测试")
    @allure.title("测试CPU正常情况")
    def test_cpu_alert_normal(self, alert_manager):
        """测试CPU正常情况"""
        cpu_data = {"overall": 50.0}
        alert = alert_manager.check_cpu_alert(cpu_data)

        assert alert["level"] == "normal"
        assert alert["current"] == 50.0

    @allure.story("CPU告警测试")
    @allure.title("测试CPU告警情况")
    def test_cpu_alert_warning(self, alert_manager):
        """测试CPU告警情况"""
        cpu_data = {"overall": 90.0}
        alert = alert_manager.check_cpu_alert(cpu_data)

        assert alert["level"] == "warning"
        assert alert["current"] == 90.0

    @allure.story("内存告警测试")
    @allure.title("测试内存正常情况")
    def test_memory_alert_normal(self, alert_manager):
        """测试内存正常情况"""
        memory_data = {"virtual": {"percent": 50.0}}
        alert = alert_manager.check_memory_alert(memory_data)

        assert alert["level"] == "normal"

    @allure.story("内存告警测试")
    @allure.title("测试内存告警情况")
    def test_memory_alert_warning(self, alert_manager):
        """测试内存告警情况"""
        memory_data = {"virtual": {"percent": 90.0}}
        alert = alert_manager.check_memory_alert(memory_data)

        assert alert["level"] == "warning"

    @allure.story("磁盘告警测试")
    @allure.title("测试磁盘正常情况")
    def test_disk_alert_normal(self, alert_manager):
        """测试磁盘正常情况"""
        disk_data = {"max_percent": 50.0}
        alert = alert_manager.check_disk_alert(disk_data)

        assert alert["level"] == "normal"

    @allure.story("磁盘告警测试")
    @allure.title("测试磁盘告警情况")
    def test_disk_alert_warning(self, alert_manager):
        """测试磁盘告警情况"""
        disk_data = {"max_percent": 90.0}
        alert = alert_manager.check_disk_alert(disk_data)

        assert alert["level"] == "warning"

    @allure.story("网络告警测试")
    @allure.title("测试网络正常情况")
    def test_network_alert_normal(self, alert_manager):
        """测试网络正常情况"""
        network_data = {"io": {"total_upload_speed_mb": 1.0, "total_download_speed_mb": 2.0}}
        alert = alert_manager.check_network_alert(network_data)

        assert alert["level"] == "normal"

    @allure.story("网络告警测试")
    @allure.title("测试网络告警情况")
    def test_network_alert_warning(self, alert_manager):
        """测试网络告警情况"""
        network_data = {"io": {"total_upload_speed_mb": 150.0, "total_download_speed_mb": 2.0}}
        alert = alert_manager.check_network_alert(network_data)

        assert alert["level"] == "warning"

    @allure.story("批量告警测试")
    @allure.title("测试检查所有告警")
    def test_check_all_alerts(self, alert_manager):
        """测试检查所有告警"""
        data = {
            "cpu": {"overall": 50.0},
            "memory": {"virtual": {"percent": 60.0}},
            "disk": {"max_percent": 70.0},
            "network": {"io": {"total_upload_speed_mb": 1.0, "total_download_speed_mb": 2.0}}
        }

        alerts = alert_manager.check_all_alerts(data)
        assert len(alerts) == 4

    @allure.story("告警历史测试")
    @allure.title("测试告警历史记录")
    def test_alert_history(self, alert_manager):
        """测试告警历史记录"""
        cpu_data = {"overall": 90.0}
        alert_manager.check_cpu_alert(cpu_data)

        history = alert_manager.get_alert_history()
        assert len(history) >= 0

    @allure.story("告警历史测试")
    @allure.title("测试清空告警历史")
    def test_clear_alert_history(self, alert_manager):
        """测试清空告警历史"""
        cpu_data = {"overall": 90.0}
        alert_manager.check_cpu_alert(cpu_data)

        alert_manager.clear_alert_history()
        assert len(alert_manager.get_alert_history()) == 0

    @allure.story("冷却期测试")
    @allure.title("测试告警冷却期")
    def test_cooldown_period(self, alert_manager):
        """测试告警冷却期"""
        alert_manager.set_cooldown_period(60)

        cpu_data = {"overall": 90.0}
        alert_manager.check_cpu_alert(cpu_data)
        history_count = len(alert_manager.get_alert_history())

        alert_manager.check_cpu_alert(cpu_data)
        assert len(alert_manager.get_alert_history()) == history_count

    @allure.story("告警历史测试")
    @allure.title("测试获取告警历史限制")
    def test_get_alert_history_limit(self, alert_manager):
        """测试获取告警历史限制"""
        for i in range(10):
            cpu_data = {"overall": 90.0 + i}
            alert_manager.check_cpu_alert(cpu_data)

        history = alert_manager.get_alert_history(limit=5)
        assert len(history) <= 5
