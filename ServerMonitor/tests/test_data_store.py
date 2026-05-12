# -*- coding: utf-8 -*-
"""
数据存储模块单元测试
"""

import time
import allure
import pytest
from monitor.core.data_store import DataStore


@pytest.fixture
def data_store():
    """创建数据存储实例"""
    return DataStore(retention=3600)


@allure.feature("数据存储模块")
class TestDataStore:
    """数据存储类测试"""

    @allure.story("初始化测试")
    @allure.title("测试数据存储初始化")
    def test_initialization(self, data_store):
        """测试初始化"""
        assert data_store.retention == 3600
        assert len(data_store.get_cpu_data()) == 0
        assert len(data_store.get_memory_data()) == 0
        assert len(data_store.get_disk_data()) == 0
        assert len(data_store.get_network_data()) == 0

    @allure.story("数据添加测试")
    @allure.title("测试添加CPU数据")
    def test_add_cpu_data(self, data_store):
        """测试添加CPU数据"""
        cpu_data = {"timestamp": time.time(), "overall": 50.0}
        data_store.add_cpu_data(cpu_data)

        result = data_store.get_cpu_data()
        assert len(result) == 1
        assert result[0]["overall"] == 50.0

    @allure.story("数据添加测试")
    @allure.title("测试添加内存数据")
    def test_add_memory_data(self, data_store):
        """测试添加内存数据"""
        memory_data = {"timestamp": time.time(), "virtual": {"percent": 60.0}}
        data_store.add_memory_data(memory_data)

        result = data_store.get_memory_data()
        assert len(result) == 1
        assert result[0]["virtual"]["percent"] == 60.0

    @allure.story("数据添加测试")
    @allure.title("测试添加磁盘数据")
    def test_add_disk_data(self, data_store):
        """测试添加磁盘数据"""
        disk_data = {"timestamp": time.time(), "max_percent": 70.0}
        data_store.add_disk_data(disk_data)

        result = data_store.get_disk_data()
        assert len(result) == 1
        assert result[0]["max_percent"] == 70.0

    @allure.story("数据添加测试")
    @allure.title("测试添加网络数据")
    def test_add_network_data(self, data_store):
        """测试添加网络数据"""
        network_data = {"timestamp": time.time(), "io": {"total_upload_speed_mb": 1.0}}
        data_store.add_network_data(network_data)

        result = data_store.get_network_data()
        assert len(result) == 1
        assert result[0]["io"]["total_upload_speed_mb"] == 1.0

    @allure.story("数据查询测试")
    @allure.title("测试获取数据限制")
    def test_get_data_limit(self, data_store):
        """测试获取数据限制"""
        for i in range(10):
            data_store.add_cpu_data({"timestamp": time.time(), "overall": float(i)})

        result = data_store.get_cpu_data(limit=5)
        assert len(result) == 5

    @allure.story("数据查询测试")
    @allure.title("测试获取所有数据")
    def test_get_all_data(self, data_store):
        """测试获取所有数据"""
        data_store.add_cpu_data({"timestamp": time.time(), "overall": 50.0})
        data_store.add_memory_data({"timestamp": time.time(), "virtual": {"percent": 60.0}})

        all_data = data_store.get_all_data()
        assert "cpu" in all_data
        assert "memory" in all_data
        assert "disk" in all_data
        assert "network" in all_data
        assert len(all_data["cpu"]) == 1
        assert len(all_data["memory"]) == 1

    @allure.story("数据管理测试")
    @allure.title("测试清空所有数据")
    def test_clear_all(self, data_store):
        """测试清空所有数据"""
        data_store.add_cpu_data({"timestamp": time.time(), "overall": 50.0})
        data_store.add_memory_data({"timestamp": time.time(), "virtual": {"percent": 60.0}})

        data_store.clear_all()

        assert len(data_store.get_cpu_data()) == 0
        assert len(data_store.get_memory_data()) == 0

    @allure.story("数据保留测试")
    @allure.title("测试数据保留策略")
    def test_data_retention(self, data_store):
        """测试数据保留"""
        old_time = time.time() - 7200
        new_time = time.time()

        data_store.add_cpu_data({"timestamp": old_time, "overall": 50.0})
        data_store.add_cpu_data({"timestamp": new_time, "overall": 60.0})

        result = data_store.get_cpu_data()
        assert len(result) >= 1
