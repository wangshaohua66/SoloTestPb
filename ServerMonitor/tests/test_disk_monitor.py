# -*- coding: utf-8 -*-
"""
磁盘监控模块单元测试
"""

import pytest
import allure
from unittest.mock import patch, MagicMock
from monitor.core.disk_monitor import DiskMonitor


@allure.feature("磁盘监控模块")
class TestDiskMonitor:
    """磁盘监控类测试"""

    @pytest.fixture
    def disk_monitor(self):
        """创建磁盘监控器实例"""
        return DiskMonitor()

    @allure.story("初始化测试")
    @allure.title("测试磁盘监控器初始化")
    def test_initialization(self, disk_monitor):
        """测试初始化"""
        assert len(disk_monitor.get_history()) == 0

    @allure.story("获取磁盘使用率测试")
    @allure.title("测试获取磁盘使用率")
    @patch('psutil.disk_partitions')
    @patch('psutil.disk_usage')
    def test_get_disk_usage(self, mock_disk_usage, mock_disk_partitions):
        """测试获取磁盘使用率"""
        partition = MagicMock()
        partition.device = "/dev/sda1"
        partition.mountpoint = "/"
        partition.fstype = "ext4"
        mock_disk_partitions.return_value = [partition]

        usage = MagicMock()
        usage.total = 100 * 1024 ** 3
        usage.used = 50 * 1024 ** 3
        usage.free = 50 * 1024 ** 3
        usage.percent = 50.0
        mock_disk_usage.return_value = usage

        monitor = DiskMonitor()
        result = monitor.get_disk_usage()

        assert "/dev/sda1" in result
        assert result["/dev/sda1"]["percent"] == 50.0
        assert result["/dev/sda1"]["used_gb"] == 50.0
        assert result["/dev/sda1"]["total_gb"] == 100.0

    @allure.story("获取磁盘IO测试")
    @allure.title("测试获取磁盘IO速度")
    @patch('psutil.disk_io_counters')
    def test_get_disk_io(self, mock_disk_io):
        """测试获取磁盘IO速度"""
        io1 = {
            "sda1": MagicMock(
                read_bytes=1000 * 1024 ** 2,
                write_bytes=500 * 1024 ** 2,
                read_count=1000,
                write_count=500
            )
        }
        io2 = {
            "sda1": MagicMock(
                read_bytes=2000 * 1024 ** 2,
                write_bytes=1000 * 1024 ** 2,
                read_count=2000,
                write_count=1000
            )
        }
        mock_disk_io.side_effect = [io1, io2]

        monitor = DiskMonitor()
        monitor.get_disk_io()
        result = monitor.get_disk_io()

        assert "sda1" in result
        assert result["sda1"]["read_speed_mb"] > 0
        assert result["sda1"]["write_speed_mb"] > 0

    @allure.story("获取当前使用率测试")
    @allure.title("测试获取当前磁盘使用率和IO")
    @patch('psutil.disk_io_counters')
    @patch('psutil.disk_usage')
    @patch('psutil.disk_partitions')
    def test_get_current_usage(self, mock_partitions, mock_usage, mock_io):
        """测试获取当前磁盘使用率和IO"""
        partition = MagicMock()
        partition.device = "/dev/sda1"
        partition.mountpoint = "/"
        partition.fstype = "ext4"
        mock_partitions.return_value = [partition]

        usage = MagicMock()
        usage.total = 100 * 1024 ** 3
        usage.used = 50 * 1024 ** 3
        usage.free = 50 * 1024 ** 3
        usage.percent = 50.0
        mock_usage.return_value = usage

        io1 = {"sda1": MagicMock(read_bytes=1000 * 1024 ** 2, write_bytes=500 * 1024 ** 2, read_count=1000, write_count=500)}
        io2 = {"sda1": MagicMock(read_bytes=2000 * 1024 ** 2, write_bytes=1000 * 1024 ** 2, read_count=2000, write_count=1000)}
        mock_io.side_effect = [io1, io2]

        monitor = DiskMonitor()
        monitor.get_disk_io()
        result = monitor.get_current_usage()

        assert "timestamp" in result
        assert "usage" in result
        assert "io" in result
        assert result["max_percent"] == 50.0

    @allure.story("获取历史数据测试")
    @allure.title("测试获取历史数据")
    @patch('psutil.disk_io_counters')
    @patch('psutil.disk_usage')
    @patch('psutil.disk_partitions')
    def test_get_history(self, mock_partitions, mock_usage, mock_io):
        """测试获取历史数据"""
        partition = MagicMock()
        partition.device = "/dev/sda1"
        partition.mountpoint = "/"
        partition.fstype = "ext4"
        mock_partitions.return_value = [partition]

        usage = MagicMock()
        usage.total = 100 * 1024 ** 3
        usage.used = 50 * 1024 ** 3
        usage.free = 50 * 1024 ** 3
        usage.percent = 50.0
        mock_usage.return_value = usage

        io1 = {"sda1": MagicMock(read_bytes=1000 * 1024 ** 2, write_bytes=500 * 1024 ** 2, read_count=1000, write_count=500)}
        io2 = {"sda1": MagicMock(read_bytes=2000 * 1024 ** 2, write_bytes=1000 * 1024 ** 2, read_count=2000, write_count=1000)}
        io3 = {"sda1": MagicMock(read_bytes=3000 * 1024 ** 2, write_bytes=1500 * 1024 ** 2, read_count=3000, write_count=1500)}
        mock_io.side_effect = [io1, io2, io1, io3]

        monitor = DiskMonitor()
        monitor.get_disk_io()
        monitor.get_current_usage()
        monitor.get_current_usage()

        history = monitor.get_history()
        assert len(history) == 2

        limited_history = monitor.get_history(limit=1)
        assert len(limited_history) == 1

    @allure.story("清空历史数据测试")
    @allure.title("测试清空历史数据")
    @patch('psutil.disk_io_counters')
    @patch('psutil.disk_usage')
    @patch('psutil.disk_partitions')
    def test_clear_history(self, mock_partitions, mock_usage, mock_io):
        """测试清空历史数据"""
        partition = MagicMock()
        partition.device = "/dev/sda1"
        partition.mountpoint = "/"
        partition.fstype = "ext4"
        mock_partitions.return_value = [partition]

        usage = MagicMock()
        usage.total = 100 * 1024 ** 3
        usage.used = 50 * 1024 ** 3
        usage.free = 50 * 1024 ** 3
        usage.percent = 50.0
        mock_usage.return_value = usage

        io1 = {"sda1": MagicMock(read_bytes=1000 * 1024 ** 2, write_bytes=500 * 1024 ** 2, read_count=1000, write_count=500)}
        io2 = {"sda1": MagicMock(read_bytes=2000 * 1024 ** 2, write_bytes=1000 * 1024 ** 2, read_count=2000, write_count=1000)}
        mock_io.side_effect = [io1, io2]

        monitor = DiskMonitor()
        monitor.get_disk_io()
        monitor.get_current_usage()

        assert len(monitor.get_history()) == 1

        monitor.clear_history()

        assert len(monitor.get_history()) == 0

    @allure.story("权限错误测试")
    @allure.title("测试权限错误处理")
    @patch('psutil.disk_usage')
    @patch('psutil.disk_partitions')
    def test_permission_error(self, mock_partitions, mock_usage):
        """测试权限错误处理"""
        partition = MagicMock()
        partition.device = "/dev/sda1"
        partition.mountpoint = "/"
        partition.fstype = "ext4"
        mock_partitions.return_value = [partition]

        mock_usage.side_effect = PermissionError("Permission denied")

        monitor = DiskMonitor()
        result = monitor.get_disk_usage()

        assert len(result) == 0
