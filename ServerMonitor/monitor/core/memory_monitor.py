# -*- coding: utf-8 -*-
"""
内存监控模块
负责采集物理内存和虚拟内存使用情况
"""

import psutil
import time
from typing import List, Dict, Any


class MemoryMonitor:
    """内存监控类"""

    def __init__(self):
        """初始化内存监控器"""
        self._history = []

    def get_current_usage(self) -> Dict[str, Any]:
        """
        获取当前内存使用情况

        Returns:
            包含物理内存和虚拟内存的字典
        """
        virtual = psutil.virtual_memory()
        swap = psutil.swap_memory()

        result = {
            "timestamp": time.time(),
            "virtual": {
                "total": virtual.total,
                "available": virtual.available,
                "used": virtual.used,
                "free": virtual.free,
                "percent": virtual.percent,
                "used_gb": round(virtual.used / (1024 ** 3), 2),
                "total_gb": round(virtual.total / (1024 ** 3), 2),
                "available_gb": round(virtual.available / (1024 ** 3), 2)
            },
            "swap": {
                "total": swap.total,
                "used": swap.used,
                "free": swap.free,
                "percent": swap.percent,
                "used_gb": round(swap.used / (1024 ** 3), 2),
                "total_gb": round(swap.total / (1024 ** 3), 2)
            }
        }

        self._history.append({
            "timestamp": result["timestamp"],
            "virtual_percent": virtual.percent,
            "swap_percent": swap.percent
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
