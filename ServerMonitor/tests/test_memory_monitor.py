# -*- coding: utf-8 -*-
"""
内存监控模块单元测试
"""

import pytest
import allure
from unittest.mock import patch, MagicMock
from monitor.core.memory_monitor import MemoryMonitor


@allure.feature("内存监控模块")
class TestMemoryMonitor:
    """内存监控类测试"""

    @pytest.fixture
    def memory_monitor(self):
        """创建内存监控器实例"""
        return MemoryMonitor()

    @allure.story("初始化测试")
    @allure.title("测试内存监控器初始化")
    def test_initialization(self, memory_monitor):
        """测试初始化"""
        assert len(memory_monitor.get_history()) == 0

    @allure.story("获取当前使用率测试")
    @allure.title("测试获取当前内存使用率")
    @patch('psutil.swap_memory')
    @patch('psutil.virtual_memory')
    def test_get_current_usage(self, mock_virtual, mock_swap):
        """测试获取当前内存使用率"""
        virtual_mem = MagicMock()
        virtual_mem.total = 8 * 1024 ** 3
        virtual_mem.available = 4 * 1024 ** 3
        virtual_mem.used = 4 * 1024 ** 3
        virtual_mem.free = 4 * 1024 ** 3
        virtual_mem.percent = 50.0
        mock_virtual.return_value = virtual_mem

        swap_mem = MagicMock()
        swap_mem.total = 2 * 1024 ** 3
        swap_mem.used = 1 * 1024 ** 3
        swap_mem.free = 1 * 1024 ** 3
        swap_mem.percent = 50.0
        mock_swap.return_value = swap_mem

        monitor = MemoryMonitor()
        result = monitor.get_current_usage()

        assert result["virtual"]["total"] == 8 * 1024 ** 3
        assert result["virtual"]["percent"] == 50.0
        assert result["virtual"]["used_gb"] == 4.0
        assert result["virtual"]["total_gb"] == 8.0
        assert result["swap"]["percent"] == 50.0
        assert result["swap"]["used_gb"] == 1.0

    @allure.story("获取历史数据测试")
    @allure.title("测试获取历史数据")
    @patch('psutil.swap_memory')
    @patch('psutil.virtual_memory')
    def test_get_history(self, mock_virtual, mock_swap):
        """测试获取历史数据"""
        virtual_mem1 = MagicMock()
        virtual_mem1.percent = 50.0
        virtual_mem1.total = 8 * 1024 ** 3
        virtual_mem1.available = 4 * 1024 ** 3
        virtual_mem1.used = 4 * 1024 ** 3
        virtual_mem1.free = 4 * 1024 ** 3

        virtual_mem2 = MagicMock()
        virtual_mem2.percent = 60.0
        virtual_mem2.total = 8 * 1024 ** 3
        virtual_mem2.available = 3.2 * 1024 ** 3
        virtual_mem2.used = 4.8 * 1024 ** 3
        virtual_mem2.free = 3.2 * 1024 ** 3

        swap_mem = MagicMock()
        swap_mem.percent = 50.0
        swap_mem.total = 2 * 1024 ** 3
        swap_mem.used = 1 * 1024 ** 3
        swap_mem.free = 1 * 1024 ** 3

        mock_virtual.side_effect = [virtual_mem1, virtual_mem2]
        mock_swap.side_effect = [swap_mem, swap_mem]

        monitor = MemoryMonitor()
        monitor.get_current_usage()
        monitor.get_current_usage()

        history = monitor.get_history()
        assert len(history) == 2

        limited_history = monitor.get_history(limit=1)
        assert len(limited_history) == 1

    @allure.story("清空历史数据测试")
    @allure.title("测试清空历史数据")
    @patch('psutil.swap_memory')
    @patch('psutil.virtual_memory')
    def test_clear_history(self, mock_virtual, mock_swap):
        """测试清空历史数据"""
        virtual_mem = MagicMock()
        virtual_mem.percent = 50.0
        virtual_mem.total = 8 * 1024 ** 3
        virtual_mem.available = 4 * 1024 ** 3
        virtual_mem.used = 4 * 1024 ** 3
        virtual_mem.free = 4 * 1024 ** 3
        mock_virtual.return_value = virtual_mem

        swap_mem = MagicMock()
        swap_mem.percent = 50.0
        swap_mem.total = 2 * 1024 ** 3
        swap_mem.used = 1 * 1024 ** 3
        swap_mem.free = 1 * 1024 ** 3
        mock_swap.return_value = swap_mem

        monitor = MemoryMonitor()
        monitor.get_current_usage()

        assert len(monitor.get_history()) == 1

        monitor.clear_history()

        assert len(monitor.get_history()) == 0

    @allure.story("数据时间戳测试")
    @allure.title("测试数据包含时间戳")
    @patch('psutil.swap_memory')
    @patch('psutil.virtual_memory')
    def test_data_has_timestamp(self, mock_virtual, mock_swap):
        """测试数据包含时间戳"""
        virtual_mem = MagicMock()
        virtual_mem.percent = 50.0
        virtual_mem.total = 8 * 1024 ** 3
        virtual_mem.available = 4 * 1024 ** 3
        virtual_mem.used = 4 * 1024 ** 3
        virtual_mem.free = 4 * 1024 ** 3
        mock_virtual.return_value = virtual_mem

        swap_mem = MagicMock()
        swap_mem.percent = 50.0
        swap_mem.total = 2 * 1024 ** 3
        swap_mem.used = 1 * 1024 ** 3
        swap_mem.free = 1 * 1024 ** 3
        mock_swap.return_value = swap_mem

        monitor = MemoryMonitor()
        result = monitor.get_current_usage()

        assert "timestamp" in result
        assert isinstance(result["timestamp"], float)
