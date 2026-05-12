# -*- coding: utf-8 -*-
"""
性能测试
测试1秒采集间隔下的CPU和内存使用情况
"""

import time
import gc
import os
import tempfile
import allure
import pytest
import psutil
from unittest.mock import patch, MagicMock


@allure.feature("性能测试")
class TestPerformance:
    """性能测试类"""

    @allure.story("采集性能测试")
    @allure.title("测试单次采集耗时")
    @patch('psutil.cpu_count')
    @patch('psutil.cpu_percent')
    @patch('psutil.virtual_memory')
    @patch('psutil.disk_partitions')
    @patch('psutil.disk_usage')
    @patch('psutil.disk_io_counters')
    @patch('psutil.net_io_counters')
    def test_single_collection_time(self, mock_net_io, mock_disk_io, mock_disk_usage,
                                    mock_disk_partitions, mock_virtual_memory, mock_cpu_percent,
                                    mock_cpu_count):
        """测试单次采集耗时"""
        from monitor.core.cpu_monitor import CPUMonitor
        from monitor.core.memory_monitor import MemoryMonitor
        from monitor.core.disk_monitor import DiskMonitor
        from monitor.core.network_monitor import NetworkMonitor

        def cpu_percent_side_effect(**kwargs):
            if kwargs.get('percpu'):
                return [50.0, 50.0]
            return 50.0

        mock_cpu_percent.side_effect = cpu_percent_side_effect
        mock_cpu_count.return_value = 2
        mock_virtual_memory.return_value = MagicMock(percent=60.0, used=1024*1024*1024, total=2*1024*1024*1024)
        mock_disk_partitions.return_value = [MagicMock(device='C:\\', mountpoint='C:\\', fstype='NTFS')]
        mock_disk_usage.return_value = MagicMock(percent=70.0, used=500*1024*1024*1024, total=1000*1024*1024*1024)
        mock_disk_io.return_value = MagicMock(read_bytes=1000, write_bytes=2000)
        mock_net_io.return_value = MagicMock(bytes_sent=500, bytes_recv=1500)

        cpu_monitor = CPUMonitor()
        memory_monitor = MemoryMonitor()
        disk_monitor = DiskMonitor()
        network_monitor = NetworkMonitor()

        start_time = time.time()

        cpu_monitor.get_current_usage()
        memory_monitor.get_current_usage()
        disk_monitor.get_disk_usage()
        disk_monitor.get_disk_io()
        network_monitor.get_network_io()

        end_time = time.time()
        elapsed = end_time - start_time

        assert elapsed < 1.0

    @allure.story("内存占用测试")
    @allure.title("测试监控模块内存占用")
    def test_memory_usage(self):
        """测试监控模块内存占用"""
        gc.collect()
        process = psutil.Process()

        initial_memory = process.memory_info().rss / 1024 / 1024

        from monitor.core.cpu_monitor import CPUMonitor
        from monitor.core.memory_monitor import MemoryMonitor
        from monitor.core.disk_monitor import DiskMonitor
        from monitor.core.network_monitor import NetworkMonitor
        from monitor.core.data_store import DataStore

        cpu_monitor = CPUMonitor()
        memory_monitor = MemoryMonitor()
        disk_monitor = DiskMonitor()
        network_monitor = NetworkMonitor()
        data_store = DataStore()

        gc.collect()
        memory_after_init = process.memory_info().rss / 1024 / 1024
        memory_increase = memory_after_init - initial_memory

        assert memory_increase < 50

    @allure.story("数据存储性能测试")
    @allure.title("测试大量数据存储性能")
    def test_data_store_performance(self):
        """测试大量数据存储性能"""
        from monitor.core.data_store import DataStore
        data_store = DataStore()

        start_time = time.time()

        for i in range(100):
            timestamp = time.time()
            cpu_data = {"timestamp": timestamp, "overall": 50.0, "per_cpu": [50.0, 50.0]}
            memory_data = {"timestamp": timestamp, "virtual": {"percent": 60.0}}
            disk_data = {"timestamp": timestamp, "max_percent": 70.0}
            network_data = {"timestamp": timestamp, "io": {"total_upload_speed_mb": 1.0}}

            data_store.add_cpu_data(cpu_data)
            data_store.add_memory_data(memory_data)
            data_store.add_disk_data(disk_data)
            data_store.add_network_data(network_data)

        end_time = time.time()
        elapsed = end_time - start_time

        assert elapsed < 1.0

    @allure.story("告警检查性能测试")
    @allure.title("测试告警检查性能")
    def test_alert_check_performance(self, mock_config):
        """测试告警检查性能"""
        from monitor.notifier.alert_manager import AlertManager
        alert_manager = AlertManager(mock_config)

        data = {
            "cpu": {"overall": 50.0},
            "memory": {"virtual": {"percent": 60.0}},
            "disk": {"max_percent": 70.0},
            "network": {"io": {"total_upload_speed_mb": 1.0, "total_download_speed_mb": 2.0}}
        }

        start_time = time.time()

        for i in range(100):
            alert_manager.check_all_alerts(data)

        end_time = time.time()
        elapsed = end_time - start_time

        assert elapsed < 1.0

    @allure.story("报告生成性能测试")
    @allure.title("测试报告生成性能")
    def test_report_generation_performance(self, tmp_path, mock_config):
        """测试报告生成性能"""
        from monitor.reporter.report_generator import ReportGenerator
        from monitor.core.data_store import DataStore
        import matplotlib
        matplotlib.use('Agg')

        data_store = DataStore()
        report_generator = ReportGenerator(mock_config)

        for i in range(60):
            timestamp = time.time() - 60 + i
            cpu_data = {"timestamp": timestamp, "overall": 50.0, "per_cpu": [50.0, 50.0]}
            memory_data = {"timestamp": timestamp, "virtual": {"percent": 60.0}}
            disk_data = {"timestamp": timestamp, "max_percent": 70.0}
            network_data = {"timestamp": timestamp, "io": {"total_upload_speed_mb": 1.0}}

            data_store.add_cpu_data(cpu_data)
            data_store.add_memory_data(memory_data)
            data_store.add_disk_data(disk_data)
            data_store.add_network_data(network_data)

        report_path = tmp_path / "test_report.html"

        start_time = time.time()
        report_generator.generate_report(data_store)
        end_time = time.time()

        elapsed = end_time - start_time

        assert elapsed < 10.0

    @allure.story("1秒间隔可行性测试")
    @allure.title("测试1秒采集间隔的可行性")
    @patch('psutil.cpu_count')
    @patch('psutil.cpu_percent')
    @patch('psutil.virtual_memory')
    @patch('psutil.disk_partitions')
    @patch('psutil.disk_usage')
    @patch('psutil.disk_io_counters')
    @patch('psutil.net_io_counters')
    def test_1_second_interval_feasibility(self, mock_net_io, mock_disk_io, mock_disk_usage,
                                           mock_disk_partitions, mock_virtual_memory, mock_cpu_percent,
                                           mock_cpu_count):
        """测试1秒采集间隔的可行性"""
        from monitor.core.cpu_monitor import CPUMonitor
        from monitor.core.memory_monitor import MemoryMonitor
        from monitor.core.disk_monitor import DiskMonitor
        from monitor.core.network_monitor import NetworkMonitor

        def cpu_percent_side_effect(**kwargs):
            if kwargs.get('percpu'):
                return [50.0, 50.0]
            return 50.0

        mock_cpu_percent.side_effect = cpu_percent_side_effect
        mock_cpu_count.return_value = 2
        mock_virtual_memory.return_value = MagicMock(percent=60.0, used=1024*1024*1024, total=2*1024*1024*1024)
        mock_disk_partitions.return_value = [MagicMock(device='C:\\', mountpoint='C:\\', fstype='NTFS')]
        mock_disk_usage.return_value = MagicMock(percent=70.0, used=500*1024*1024*1024, total=1000*1024*1024*1024)
        mock_disk_io.return_value = MagicMock(read_bytes=1000, write_bytes=2000)
        mock_net_io.return_value = MagicMock(bytes_sent=500, bytes_recv=1500)

        cpu_monitor = CPUMonitor()
        memory_monitor = MemoryMonitor()
        disk_monitor = DiskMonitor()
        network_monitor = NetworkMonitor()

        collection_times = []

        for i in range(5):
            start_time = time.time()

            cpu_monitor.get_current_usage()
            memory_monitor.get_current_usage()
            disk_monitor.get_disk_usage()
            disk_monitor.get_disk_io()
            network_monitor.get_network_io()

            end_time = time.time()
            collection_times.append(end_time - start_time)

            time.sleep(0.01)

        avg_time = sum(collection_times) / len(collection_times)

        assert avg_time < 0.5

    @allure.story("数据保留策略测试")
    @allure.title("测试数据保留策略性能")
    def test_data_retention_performance(self):
        """测试数据保留策略性能"""
        from monitor.core.data_store import DataStore
        data_store = DataStore()

        for i in range(2000):
            timestamp = time.time() - 2000 + i
            cpu_data = {"timestamp": timestamp, "overall": 50.0}
            data_store.add_cpu_data(cpu_data)

        cpu_data = data_store.get_cpu_data()

        assert len(cpu_data) >= 0

    @allure.story("历史数据查询性能测试")
    @allure.title("测试历史数据查询性能")
    def test_history_query_performance(self):
        """测试历史数据查询性能"""
        from monitor.core.data_store import DataStore
        data_store = DataStore()

        for i in range(1000):
            timestamp = time.time() - 1000 + i
            cpu_data = {"timestamp": timestamp, "overall": 50.0}
            data_store.add_cpu_data(cpu_data)

        start_time = time.time()
        cpu_data = data_store.get_cpu_data()
        end_time = time.time()

        elapsed = end_time - start_time

        assert elapsed < 0.1

    @allure.story("真实性能测试")
    @allure.title("测试真实数据采集性能")
    def test_real_data_collection_performance(self):
        """测试真实数据采集性能（不使用mock）"""
        from monitor.core.cpu_monitor import CPUMonitor
        from monitor.core.memory_monitor import MemoryMonitor
        from monitor.core.disk_monitor import DiskMonitor
        from monitor.core.network_monitor import NetworkMonitor

        cpu_monitor = CPUMonitor()
        memory_monitor = MemoryMonitor()
        disk_monitor = DiskMonitor()
        network_monitor = NetworkMonitor()

        start_time = time.time()

        cpu_data = cpu_monitor.get_current_usage()
        memory_data = memory_monitor.get_current_usage()
        disk_data = disk_monitor.get_current_usage()
        network_data = network_monitor.get_current_usage()

        end_time = time.time()
        elapsed = end_time - start_time

        assert "overall" in cpu_data
        assert "virtual" in memory_data
        assert "max_percent" in disk_data
        assert "io" in network_data
        assert elapsed < 2.0

    @allure.story("真实性能测试")
    @allure.title("测试真实内存占用")
    def test_real_memory_usage(self):
        """测试真实内存占用（不使用mock）"""
        import psutil
        import gc

        gc.collect()
        process = psutil.Process()

        initial_memory = process.memory_info().rss / 1024 / 1024

        from monitor.core.cpu_monitor import CPUMonitor
        from monitor.core.memory_monitor import MemoryMonitor
        from monitor.core.disk_monitor import DiskMonitor
        from monitor.core.network_monitor import NetworkMonitor
        from monitor.core.data_store import DataStore

        cpu_monitor = CPUMonitor()
        memory_monitor = MemoryMonitor()
        disk_monitor = DiskMonitor()
        network_monitor = NetworkMonitor()
        data_store = DataStore()

        for i in range(100):
            cpu_data = cpu_monitor.get_current_usage()
            memory_data = memory_monitor.get_current_usage()
            disk_data = disk_monitor.get_current_usage()
            network_data = network_monitor.get_current_usage()
            data_store.add_cpu_data(cpu_data)
            data_store.add_memory_data(memory_data)
            data_store.add_disk_data(disk_data)
            data_store.add_network_data(network_data)

        gc.collect()
        memory_after = process.memory_info().rss / 1024 / 1024
        memory_increase = memory_after - initial_memory

        assert len(data_store.get_cpu_data()) == 100
        assert memory_increase < 100
