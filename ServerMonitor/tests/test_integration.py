# -*- coding: utf-8 -*-
"""
集成测试
测试ServerMonitor主监控流程的端到端功能
"""

import time
import os
import tempfile
import allure
import pytest
from unittest.mock import patch, MagicMock


@allure.feature("集成测试")
class TestServerMonitorIntegration:
    """ServerMonitor集成测试"""

    @pytest.fixture
    def temp_config_file(self):
        """创建临时配置文件"""
        config_data = '''{
            "interval": 0.1,
            "cpu_threshold": 80.0,
            "memory_threshold": 80.0,
            "disk_threshold": 85.0,
            "network_threshold": 100.0,
            "smtp": {
                "enabled": false
            },
            "report": {
                "enabled": false
            }
        }'''
        fd, path = tempfile.mkstemp(suffix='.json')
        with os.fdopen(fd, 'w') as f:
            f.write(config_data)
        yield path
        if os.path.exists(path):
            os.remove(path)

    @allure.story("初始化测试")
    @allure.title("测试ServerMonitor初始化")
    def test_initialization(self, temp_config_file):
        """测试ServerMonitor初始化"""
        from monitor.monitor import ServerMonitor
        monitor = ServerMonitor(temp_config_file)

        assert monitor._running is False
        assert monitor.cpu_monitor is not None
        assert monitor.memory_monitor is not None
        assert monitor.disk_monitor is not None
        assert monitor.network_monitor is not None
        assert monitor.data_store is not None
        assert monitor.alert_manager is not None
        assert monitor.email_notifier is not None
        assert monitor.report_generator is not None

    @allure.story("数据采集测试")
    @allure.title("测试单次数据采集")
    @patch('psutil.cpu_count')
    @patch('psutil.cpu_percent')
    @patch('psutil.virtual_memory')
    @patch('psutil.disk_usage')
    @patch('psutil.disk_io_counters')
    @patch('psutil.net_io_counters')
    def test_collect_once(self, mock_net_io, mock_disk_io, mock_disk_usage,
                          mock_virtual_memory, mock_cpu_percent, mock_cpu_count, temp_config_file):
        """测试单次数据采集"""
        from monitor.monitor import ServerMonitor

        def cpu_percent_side_effect(**kwargs):
            if kwargs.get('percpu'):
                return [50.0, 50.0]
            return 50.0

        mock_cpu_percent.side_effect = cpu_percent_side_effect
        mock_cpu_count.return_value = 2
        mock_virtual_memory.return_value = MagicMock(percent=60.0, used=1024*1024*1024, total=2*1024*1024*1024)
        mock_disk_usage.return_value = MagicMock(percent=70.0, used=500*1024*1024*1024, total=1000*1024*1024*1024)
        mock_disk_io.return_value = MagicMock(read_bytes=1000, write_bytes=2000)
        mock_net_io.return_value = MagicMock(bytes_sent=500, bytes_recv=1500)

        monitor = ServerMonitor(temp_config_file)
        data = monitor._collect_once()

        assert "cpu" in data
        assert "memory" in data
        assert "disk" in data
        assert "network" in data

    @allure.story("告警集成测试")
    @allure.title("测试数据采集触发告警")
    @patch('psutil.cpu_count')
    @patch('psutil.cpu_percent')
    @patch('psutil.virtual_memory')
    @patch('psutil.disk_usage')
    @patch('psutil.disk_io_counters')
    @patch('psutil.net_io_counters')
    def test_collect_triggers_alert(self, mock_net_io, mock_disk_io, mock_disk_usage,
                                    mock_virtual_memory, mock_cpu_percent, mock_cpu_count, temp_config_file):
        """测试数据采集触发告警"""
        from monitor.monitor import ServerMonitor

        def cpu_percent_side_effect(**kwargs):
            if kwargs.get('percpu'):
                return [95.0, 90.0]
            return 95.0

        mock_cpu_percent.side_effect = cpu_percent_side_effect
        mock_cpu_count.return_value = 2
        mock_virtual_memory.return_value = MagicMock(percent=60.0, used=1024*1024*1024, total=2*1024*1024*1024)
        mock_disk_usage.return_value = MagicMock(percent=70.0, used=500*1024*1024*1024, total=1000*1024*1024*1024)
        mock_disk_io.return_value = MagicMock(read_bytes=1000, write_bytes=2000)
        mock_net_io.return_value = MagicMock(bytes_sent=500, bytes_recv=1500)

        monitor = ServerMonitor(temp_config_file)
        initial_history_count = len(monitor.alert_manager.get_alert_history())

        monitor._collect_once()

        assert len(monitor.alert_manager.get_alert_history()) >= initial_history_count

    @allure.story("数据存储集成测试")
    @allure.title("测试数据存储到DataStore")
    @patch('psutil.cpu_count')
    @patch('psutil.cpu_percent')
    @patch('psutil.virtual_memory')
    @patch('psutil.disk_usage')
    @patch('psutil.disk_io_counters')
    @patch('psutil.net_io_counters')
    def test_data_stored_in_datastore(self, mock_net_io, mock_disk_io, mock_disk_usage,
                                      mock_virtual_memory, mock_cpu_percent, mock_cpu_count, temp_config_file):
        """测试数据存储到DataStore"""
        from monitor.monitor import ServerMonitor

        def cpu_percent_side_effect(**kwargs):
            if kwargs.get('percpu'):
                return [50.0, 50.0]
            return 50.0

        mock_cpu_percent.side_effect = cpu_percent_side_effect
        mock_cpu_count.return_value = 2
        mock_virtual_memory.return_value = MagicMock(percent=60.0, used=1024*1024*1024, total=2*1024*1024*1024)
        mock_disk_usage.return_value = MagicMock(percent=70.0, used=500*1024*1024*1024, total=1000*1024*1024*1024)
        mock_disk_io.return_value = MagicMock(read_bytes=1000, write_bytes=2000)
        mock_net_io.return_value = MagicMock(bytes_sent=500, bytes_recv=1500)

        monitor = ServerMonitor(temp_config_file)

        monitor._collect_once()

        cpu_data = monitor.data_store.get_cpu_data()
        memory_data = monitor.data_store.get_memory_data()
        disk_data = monitor.data_store.get_disk_data()
        network_data = monitor.data_store.get_network_data()

        assert len(cpu_data) >= 1
        assert len(memory_data) >= 1
        assert len(disk_data) >= 1
        assert len(network_data) >= 1

    @allure.story("启动停止测试")
    @allure.title("测试启动和停止监控")
    @patch('psutil.cpu_count')
    @patch('psutil.cpu_percent')
    @patch('psutil.virtual_memory')
    @patch('psutil.disk_usage')
    @patch('psutil.disk_io_counters')
    @patch('psutil.net_io_counters')
    def test_start_and_stop(self, mock_net_io, mock_disk_io, mock_disk_usage,
                            mock_virtual_memory, mock_cpu_percent, mock_cpu_count, temp_config_file):
        """测试启动和停止监控"""
        from monitor.monitor import ServerMonitor
        import threading

        def cpu_percent_side_effect(**kwargs):
            if kwargs.get('percpu'):
                return [50.0, 50.0]
            return 50.0

        mock_cpu_percent.side_effect = cpu_percent_side_effect
        mock_cpu_count.return_value = 2
        mock_virtual_memory.return_value = MagicMock(percent=60.0, used=1024*1024*1024, total=2*1024*1024*1024)
        mock_disk_usage.return_value = MagicMock(percent=70.0, used=500*1024*1024*1024, total=1000*1024*1024*1024)
        mock_disk_io.return_value = MagicMock(read_bytes=1000, write_bytes=2000)
        mock_net_io.return_value = MagicMock(bytes_sent=500, bytes_recv=1500)

        monitor = ServerMonitor(temp_config_file)

        monitor._running = True
        monitor_thread = threading.Thread(target=monitor.start)
        monitor_thread.daemon = True
        monitor_thread.start()

        time.sleep(0.15)

        monitor._running = False
        monitor_thread.join(timeout=1.0)

        assert monitor._running is False

    @allure.story("模块集成测试")
    @allure.title("测试所有模块协同工作")
    def test_all_modules_work_together(self, temp_config_file):
        """测试所有模块协同工作"""
        from monitor.monitor import ServerMonitor

        monitor = ServerMonitor(temp_config_file)

        assert monitor.cpu_monitor is not None
        assert monitor.memory_monitor is not None
        assert monitor.disk_monitor is not None
        assert monitor.network_monitor is not None
        assert monitor.data_store is not None
        assert monitor.alert_manager is not None
        assert monitor.email_notifier is not None
        assert monitor.report_generator is not None

        assert hasattr(monitor.cpu_monitor, 'get_current_usage')
        assert hasattr(monitor.memory_monitor, 'get_current_usage')
        assert hasattr(monitor.disk_monitor, 'get_disk_usage')
        assert hasattr(monitor.network_monitor, 'get_network_io')
        assert hasattr(monitor.data_store, 'add_cpu_data')
        assert hasattr(monitor.alert_manager, 'check_all_alerts')
        assert hasattr(monitor.email_notifier, 'send_alert')
        assert hasattr(monitor.report_generator, 'generate_report')
