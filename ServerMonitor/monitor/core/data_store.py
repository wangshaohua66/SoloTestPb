# -*- coding: utf-8 -*-
"""
数据存储模块
负责存储和管理所有监控数据
"""

import time
from typing import List, Dict, Any


class DataStore:
    """数据存储类"""

    def __init__(self, retention: int = 86400):
        """
        初始化数据存储

        Args:
            retention: 数据保留时间（秒），默认24小时
        """
        self.retention = retention
        self._data = {
            "cpu": [],
            "memory": [],
            "disk": [],
            "network": []
        }

    def add_cpu_data(self, data: Dict[str, Any]) -> None:
        """
        添加CPU数据

        Args:
            data: CPU数据
        """
        self._data["cpu"].append(data)
        self._cleanup_old_data("cpu")

    def add_memory_data(self, data: Dict[str, Any]) -> None:
        """
        添加内存数据

        Args:
            data: 内存数据
        """
        self._data["memory"].append(data)
        self._cleanup_old_data("memory")

    def add_disk_data(self, data: Dict[str, Any]) -> None:
        """
        添加磁盘数据

        Args:
            data: 磁盘数据
        """
        self._data["disk"].append(data)
        self._cleanup_old_data("disk")

    def add_network_data(self, data: Dict[str, Any]) -> None:
        """
        添加网络数据

        Args:
            data: 网络数据
        """
        self._data["network"].append(data)
        self._cleanup_old_data("network")

    def _cleanup_old_data(self, data_type: str) -> None:
        """
        清理过期数据

        Args:
            data_type: 数据类型
        """
        current_time = time.time()
        cutoff_time = current_time - self.retention

        self._data[data_type] = [
            item for item in self._data[data_type]
            if item.get("timestamp", 0) >= cutoff_time
        ]

    def get_cpu_data(self, limit: int = None) -> List[Dict[str, Any]]:
        """
        获取CPU数据

        Args:
            limit: 返回数据条数限制

        Returns:
            CPU数据列表
        """
        if limit:
            return self._data["cpu"][-limit:]
        return self._data["cpu"]

    def get_memory_data(self, limit: int = None) -> List[Dict[str, Any]]:
        """
        获取内存数据

        Args:
            limit: 返回数据条数限制

        Returns:
            内存数据列表
        """
        if limit:
            return self._data["memory"][-limit:]
        return self._data["memory"]

    def get_disk_data(self, limit: int = None) -> List[Dict[str, Any]]:
        """
        获取磁盘数据

        Args:
            limit: 返回数据条数限制

        Returns:
            磁盘数据列表
        """
        if limit:
            return self._data["disk"][-limit:]
        return self._data["disk"]

    def get_network_data(self, limit: int = None) -> List[Dict[str, Any]]:
        """
        获取网络数据

        Args:
            limit: 返回数据条数限制

        Returns:
            网络数据列表
        """
        if limit:
            return self._data["network"][-limit:]
        return self._data["network"]

    def get_all_data(self) -> Dict[str, List[Dict[str, Any]]]:
        """
        获取所有数据

        Returns:
            所有监控数据
        """
        return self._data.copy()

    def clear_all(self) -> None:
        """清空所有数据"""
        for key in self._data:
            self._data[key].clear()
