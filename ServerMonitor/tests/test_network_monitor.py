# -*- coding: utf-8 -*-
"""
网络监控模块单元测试
"""

import pytest
import allure
from unittest.mock import patch, MagicMock
from monitor.core.network_monitor import NetworkMonitor


@allure.feature("网络监控模块")
class TestNetworkMonitor:
    """网络监控类测试"""

    @pytest.fixture
    def network_monitor(self):
        """创建网络监控器实例"""
        return NetworkMonitor()

    @allure.story("初始化测试")
    @allure.title("测试网络监控器初始化")
    def test_initialization(self, network_monitor):
        """测试初始化"""
        assert len(network_monitor.get_history()) == 0

    @allure.story("获取网络接口测试")
    @allure.title("测试获取网络接口信息")
    @patch('psutil.net_if_stats')
    @patch('psutil.net_if_addrs')
    def test_get_network_interfaces(self, mock_addrs, mock_stats):
        """测试获取网络接口信息"""
        addr = MagicMock()
        addr.family = "AF_INET"
        addr.address = "192.168.1.100"
        addr.netmask = "255.255.255.0"
        addr.broadcast = "192.168.1.255"
        mock_addrs.return_value = {"eth0": [addr]}

        stat = MagicMock()
        stat.isup = True
        stat.speed = 1000
        stat.mtu = 1500
        mock_stats.return_value = {"eth0": stat}

        monitor = NetworkMonitor()
        result = monitor.get_network_interfaces()

        assert "eth0" in result
        assert result["eth0"]["is_up"] is True
        assert result["eth0"]["speed"] == 1000
        assert len(result["eth0"]["addresses"]) == 1

    @allure.story("获取网络IO测试")
    @allure.title("测试获取网络IO速度")
    @patch('psutil.net_io_counters')
    def test_get_network_io(self, mock_net_io):
        """测试获取网络IO速度"""
        io1 = {
            "eth0": MagicMock(
                bytes_sent=100 * 1024 ** 2,
                bytes_recv=200 * 1024 ** 2,
                packets_sent=1000,
                packets_recv=2000
            )
        }
        io2 = {
            "eth0": MagicMock(
                bytes_sent=300 * 1024 ** 2,
                bytes_recv=600 * 1024 ** 2,
                packets_sent=3000,
                packets_recv=6000
            )
        }
        mock_net_io.side_effect = [io1, io2]

        monitor = NetworkMonitor()
        monitor.get_network_io()
        result = monitor.get_network_io()

        assert "interfaces" in result
        assert "total_upload_speed" in result
        assert "total_download_speed" in result
        assert "eth0" in result["interfaces"]
        assert result["interfaces"]["eth0"]["upload_speed_mb"] > 0
        assert result["interfaces"]["eth0"]["download_speed_mb"] > 0

    @allure.story("获取当前使用率测试")
    @allure.title("测试获取当前网络使用情况")
    @patch('psutil.net_io_counters')
    def test_get_current_usage(self, mock_net_io):
        """测试获取当前网络使用情况"""
        io1 = {
            "eth0": MagicMock(
                bytes_sent=100 * 1024 ** 2,
                bytes_recv=200 * 1024 ** 2,
                packets_sent=1000,
                packets_recv=2000
            )
        }
        io2 = {
            "eth0": MagicMock(
                bytes_sent=300 * 1024 ** 2,
                bytes_recv=600 * 1024 ** 2,
                packets_sent=3000,
                packets_recv=6000
            )
        }
        mock_net_io.side_effect = [io1, io2]

        monitor = NetworkMonitor()
        monitor.get_network_io()
        result = monitor.get_current_usage()

        assert "timestamp" in result
        assert "io" in result

    @allure.story("获取历史数据测试")
    @allure.title("测试获取历史数据")
    @patch('psutil.net_io_counters')
    def test_get_history(self, mock_net_io):
        """测试获取历史数据"""
        io1 = {
            "eth0": MagicMock(
                bytes_sent=100 * 1024 ** 2,
                bytes_recv=200 * 1024 ** 2,
                packets_sent=1000,
                packets_recv=2000
            )
        }
        io2 = {
            "eth0": MagicMock(
                bytes_sent=300 * 1024 ** 2,
                bytes_recv=600 * 1024 ** 2,
                packets_sent=3000,
                packets_recv=6000
            )
        }
        io3 = {
            "eth0": MagicMock(
                bytes_sent=500 * 1024 ** 2,
                bytes_recv=1000 * 1024 ** 2,
                packets_sent=5000,
                packets_recv=10000
            )
        }
        mock_net_io.side_effect = [io1, io2, io1, io3]

        monitor = NetworkMonitor()
        monitor.get_network_io()
        monitor.get_current_usage()
        monitor.get_current_usage()

        history = monitor.get_history()
        assert len(history) == 2

        limited_history = monitor.get_history(limit=1)
        assert len(limited_history) == 1

    @allure.story("清空历史数据测试")
    @allure.title("测试清空历史数据")
    @patch('psutil.net_io_counters')
    def test_clear_history(self, mock_net_io):
        """测试清空历史数据"""
        io1 = {
            "eth0": MagicMock(
                bytes_sent=100 * 1024 ** 2,
                bytes_recv=200 * 1024 ** 2,
                packets_sent=1000,
                packets_recv=2000
            )
        }
        io2 = {
            "eth0": MagicMock(
                bytes_sent=300 * 1024 ** 2,
                bytes_recv=600 * 1024 ** 2,
                packets_sent=3000,
                packets_recv=6000
            )
        }
        mock_net_io.side_effect = [io1, io2]

        monitor = NetworkMonitor()
        monitor.get_network_io()
        monitor.get_current_usage()

        assert len(monitor.get_history()) == 1

        monitor.clear_history()

        assert len(monitor.get_history()) == 0

    @allure.story("数据时间戳测试")
    @allure.title("测试数据包含时间戳")
    @patch('psutil.net_io_counters')
    def test_data_has_timestamp(self, mock_net_io):
        """测试数据包含时间戳"""
        io1 = {
            "eth0": MagicMock(
                bytes_sent=100 * 1024 ** 2,
                bytes_recv=200 * 1024 ** 2,
                packets_sent=1000,
                packets_recv=2000
            )
        }
        io2 = {
            "eth0": MagicMock(
                bytes_sent=300 * 1024 ** 2,
                bytes_recv=600 * 1024 ** 2,
                packets_sent=3000,
                packets_recv=6000
            )
        }
        mock_net_io.side_effect = [io1, io2]

        monitor = NetworkMonitor()
        monitor.get_network_io()
        result = monitor.get_current_usage()

        assert "timestamp" in result
        assert isinstance(result["timestamp"], float)
