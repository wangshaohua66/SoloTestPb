# -*- coding: utf-8 -*-
"""
CPU监控模块
负责采集CPU使用率数据，支持多核显示
"""

import psutil
import time
from typing import List, Dict, Any


class CPUMonitor:
    """CPU监控类"""

    def __init__(self, interval: int = 1):
        """
        初始化CPU监控器

        Args:
            interval: 采集间隔（秒）
        """
        self.interval = interval
        self._history = []
        self._per_cpu_history = []

    def get_current_usage(self) -> Dict[str, Any]:
        """
        获取当前CPU使用率

        Returns:
            包含总体和各核CPU使用率的字典
        """
        overall = psutil.cpu_percent(interval=self.interval)
        per_cpu = psutil.cpu_percent(percpu=True)
        cpu_count = psutil.cpu_count(logical=True)
        cpu_count_physical = psutil.cpu_count(logical=False)

        result = {
            "timestamp": time.time(),
            "overall": overall,
            "per_cpu": per_cpu,
            "cpu_count": cpu_count,
            "cpu_count_physical": cpu_count_physical,
            "avg": sum(per_cpu) / len(per_cpu) if per_cpu else 0.0,
            "max": max(per_cpu) if per_cpu else 0.0,
            "min": min(per_cpu) if per_cpu else 0.0
        }

        self._history.append({
            "timestamp": result["timestamp"],
            "overall": overall
        })

        self._per_cpu_history.append({
            "timestamp": result["timestamp"],
            "per_cpu": per_cpu
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

    def get_per_cpu_history(self, limit: int = None) -> List[Dict[str, Any]]:
        """
        获取多核历史数据

        Args:
            limit: 返回的历史数据条数限制

        Returns:
            多核历史数据列表
        """
        if limit:
            return self._per_cpu_history[-limit:]
        return self._per_cpu_history

    def clear_history(self) -> None:
        """清空历史数据"""
        self._history.clear()
        self._per_cpu_history.clear()

    def get_cpu_info(self) -> Dict[str, Any]:
        """
        获取CPU基本信息

        Returns:
            CPU信息字典
        """
        return {
            "logical_count": psutil.cpu_count(logical=True),
            "physical_count": psutil.cpu_count(logical=False),
            "frequency": psutil.cpu_freq().current if psutil.cpu_freq() else None,
            "frequency_max": psutil.cpu_freq().max if psutil.cpu_freq() else None
        }
