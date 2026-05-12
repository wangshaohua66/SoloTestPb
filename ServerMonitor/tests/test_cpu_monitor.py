# -*- coding: utf-8 -*-
"""
CPU监控模块单元测试
"""

import pytest
import allure
from unittest.mock import patch, MagicMock
from monitor.core.cpu_monitor import CPUMonitor


@allure.feature("CPU监控模块")
class TestCPUMonitor:
    """CPU监控类测试"""

    @pytest.fixture
    def cpu_monitor(self):
        """创建CPU监控器实例"""
        return CPUMonitor(interval=0.1)

    @allure.story("初始化测试")
    @allure.title("测试CPU监控器初始化")
    def test_initialization(self, cpu_monitor):
        """测试初始化"""
        assert cpu_monitor.interval == 0.1
        assert len(cpu_monitor.get_history()) == 0
        assert len(cpu_monitor.get_per_cpu_history()) == 0

    @allure.story("获取CPU信息测试")
    @allure.title("测试获取CPU基本信息")
    @patch('psutil.cpu_count')
    @patch('psutil.cpu_freq')
    def test_get_cpu_info(self, mock_cpu_freq, mock_cpu_count):
        """测试获取CPU基本信息"""
        mock_cpu_count.return_value = 4
        mock_freq = MagicMock()
        mock_freq.current = 2500
        mock_freq.max = 3500
        mock_cpu_freq.return_value = mock_freq

        monitor = CPUMonitor(interval=0.1)
        info = monitor.get_cpu_info()

        assert info["logical_count"] == 4
        assert info["physical_count"] == 4
        assert info["frequency"] == 2500
        assert info["frequency_max"] == 3500

    @allure.story("获取CPU信息测试")
    @allure.title("测试获取CPU基本信息（无频率信息）")
    @patch('psutil.cpu_count')
    @patch('psutil.cpu_freq')
    def test_get_cpu_info_no_freq(self, mock_cpu_freq, mock_cpu_count):
        """测试获取CPU基本信息（无频率信息）"""
        mock_cpu_count.return_value = 4
        mock_cpu_freq.return_value = None

        monitor = CPUMonitor(interval=0.1)
        info = monitor.get_cpu_info()

        assert info["logical_count"] == 4
        assert info["frequency"] is None
        assert info["frequency_max"] is None

    @allure.story("获取当前使用率测试")
    @allure.title("测试获取当前CPU使用率")
    @patch('psutil.cpu_percent')
    @patch('psutil.cpu_count')
    def test_get_current_usage(self, mock_cpu_count, mock_cpu_percent):
        """测试获取当前CPU使用率"""
        mock_cpu_count.return_value = 4
        mock_cpu_percent.side_effect = [50.0, [25.0, 50.0, 75.0, 50.0]]

        monitor = CPUMonitor(interval=0.1)
        result = monitor.get_current_usage()

        assert result["overall"] == 50.0
        assert result["per_cpu"] == [25.0, 50.0, 75.0, 50.0]
        assert result["cpu_count"] == 4
        assert result["avg"] == 50.0
        assert result["max"] == 75.0
        assert result["min"] == 25.0

    @allure.story("获取历史数据测试")
    @allure.title("测试获取历史数据")
    @patch('psutil.cpu_percent')
    @patch('psutil.cpu_count')
    def test_get_history(self, mock_cpu_count, mock_cpu_percent):
        """测试获取历史数据"""
        mock_cpu_count.return_value = 4
        mock_cpu_percent.side_effect = [
            30.0, [20.0, 30.0, 40.0, 30.0],
            40.0, [30.0, 40.0, 50.0, 40.0],
            50.0, [40.0, 50.0, 60.0, 50.0]
        ]

        monitor = CPUMonitor(interval=0.1)
        monitor.get_current_usage()
        monitor.get_current_usage()
        monitor.get_current_usage()

        history = monitor.get_history()
        assert len(history) == 3

        limited_history = monitor.get_history(limit=2)
        assert len(limited_history) == 2

    @allure.story("获取多核历史数据测试")
    @allure.title("测试获取多核历史数据")
    @patch('psutil.cpu_percent')
    @patch('psutil.cpu_count')
    def test_get_per_cpu_history(self, mock_cpu_count, mock_cpu_percent):
        """测试获取多核历史数据"""
        mock_cpu_count.return_value = 4
        mock_cpu_percent.side_effect = [
            30.0, [20.0, 30.0, 40.0, 30.0],
            40.0, [30.0, 40.0, 50.0, 40.0]
        ]

        monitor = CPUMonitor(interval=0.1)
        monitor.get_current_usage()
        monitor.get_current_usage()

        per_cpu_history = monitor.get_per_cpu_history()
        assert len(per_cpu_history) == 2

        limited_history = monitor.get_per_cpu_history(limit=1)
        assert len(limited_history) == 1

    @allure.story("清空历史数据测试")
    @allure.title("测试清空历史数据")
    @patch('psutil.cpu_percent')
    @patch('psutil.cpu_count')
    def test_clear_history(self, mock_cpu_count, mock_cpu_percent):
        """测试清空历史数据"""
        mock_cpu_count.return_value = 4
        mock_cpu_percent.side_effect = [30.0, [20.0, 30.0, 40.0, 30.0]]

        monitor = CPUMonitor(interval=0.1)
        monitor.get_current_usage()

        assert len(monitor.get_history()) == 1
        assert len(monitor.get_per_cpu_history()) == 1

        monitor.clear_history()

        assert len(monitor.get_history()) == 0
        assert len(monitor.get_per_cpu_history()) == 0

    @allure.story("空多核数据测试")
    @allure.title("测试空多核数据处理")
    @patch('psutil.cpu_percent')
    @patch('psutil.cpu_count')
    def test_empty_per_cpu_data(self, mock_cpu_count, mock_cpu_percent):
        """测试空多核数据处理"""
        mock_cpu_count.return_value = 4
        mock_cpu_percent.side_effect = [50.0, []]

        monitor = CPUMonitor(interval=0.1)
        result = monitor.get_current_usage()

        assert result["overall"] == 50.0
        assert result["avg"] == 0.0
        assert result["max"] == 0.0
        assert result["min"] == 0.0
