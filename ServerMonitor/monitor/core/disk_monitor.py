# -*- coding: utf-8 -*-
"""
磁盘监控模块
负责采集磁盘使用率和IO速度
"""

import psutil
import time
from typing import List, Dict, Any


class DiskMonitor:
    """磁盘监控类"""

    def __init__(self):
        """初始化磁盘监控器"""
        self._history = []
        self._last_io_counters = None
        self._last_io_time = None

    def get_disk_usage(self) -> Dict[str, Any]:
        """
        获取磁盘使用率

        Returns:
            各磁盘分区的使用情况
        """
        partitions = psutil.disk_partitions()
        disk_usage = {}

        for partition in partitions:
            try:
                usage = psutil.disk_usage(partition.mountpoint)
                disk_usage[partition.device] = {
                    "mountpoint": partition.mountpoint,
                    "fstype": partition.fstype,
                    "total": usage.total,
                    "used": usage.used,
                    "free": usage.free,
                    "percent": usage.percent,
                    "used_gb": round(usage.used / (1024 ** 3), 2),
                    "total_gb": round(usage.total / (1024 ** 3), 2),
                    "free_gb": round(usage.free / (1024 ** 3), 2)
                }
            except (PermissionError, OSError):
                continue

        return disk_usage

    def get_disk_io(self) -> Dict[str, Any]:
        """
        获取磁盘IO速度

        Returns:
            磁盘IO统计信息
        """
        current_io = psutil.disk_io_counters(perdisk=True)
        current_time = time.time()

        result = {}

        if self._last_io_counters is not None and self._last_io_time is not None:
            time_diff = current_time - self._last_io_time
            if time_diff > 0:
                for disk, io_counters in current_io.items():
                    if disk in self._last_io_counters:
                        last_counters = self._last_io_counters[disk]
                        read_speed = (io_counters.read_bytes - last_counters.read_bytes) / time_diff
                        write_speed = (io_counters.write_bytes - last_counters.write_bytes) / time_diff
                        read_count_speed = (io_counters.read_count - last_counters.read_count) / time_diff
                        write_count_speed = (io_counters.write_count - last_counters.write_count) / time_diff

                        result[disk] = {
                            "read_speed": read_speed,
                            "write_speed": write_speed,
                            "read_speed_mb": round(read_speed / (1024 ** 2), 2),
                            "write_speed_mb": round(write_speed / (1024 ** 2), 2),
                            "read_count_speed": round(read_count_speed, 2),
                            "write_count_speed": round(write_count_speed, 2),
                            "total_read_bytes": io_counters.read_bytes,
                            "total_write_bytes": io_counters.write_bytes
                        }

        self._last_io_counters = current_io
        self._last_io_time = current_time

        return result

    def get_current_usage(self) -> Dict[str, Any]:
        """
        获取当前磁盘使用情况（包括使用率和IO）

        Returns:
            磁盘使用情况字典
        """
        usage = self.get_disk_usage()
        io = self.get_disk_io()

        max_percent = 0.0
        for disk_data in usage.values():
            if disk_data["percent"] > max_percent:
                max_percent = disk_data["percent"]

        result = {
            "timestamp": time.time(),
            "usage": usage,
            "io": io,
            "max_percent": max_percent
        }

        self._history.append({
            "timestamp": result["timestamp"],
            "max_percent": max_percent
        })

        return result

    def get_history(self, limit: int = None) -> List[Dict[str, Any]]:
        """
        获取历史数据

        Args:
            limit: 返回的历史数据条数限制

        Returns:
            历史数据列表
        """
        if limit:
            return self._history[-limit:]
        return self._history

    def clear_history(self) -> None:
        """清空历史数据"""
        self._history.clear()
        self._last_io_counters = None
        self._last_io_time = None
