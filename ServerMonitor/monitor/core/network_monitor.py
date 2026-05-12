# -*- coding: utf-8 -*-
"""
网络监控模块
负责监控网络流量，统计上传下载速度
"""

import psutil
import time
from typing import List, Dict, Any


class NetworkMonitor:
    """网络监控类"""

    def __init__(self):
        """初始化网络监控器"""
        self._history = []
        self._last_net_counters = None
        self._last_net_time = None

    def get_network_io(self) -> Dict[str, Any]:
        """
        获取网络IO速度

        Returns:
            网络IO统计信息
        """
        current_net = psutil.net_io_counters(pernic=True)
        current_time = time.time()

        result = {}
        total_upload_speed = 0.0
        total_download_speed = 0.0

        if self._last_net_counters is not None and self._last_net_time is not None:
            time_diff = current_time - self._last_net_time
            if time_diff > 0:
                for nic, net_counters in current_net.items():
                    if nic in self._last_net_counters:
                        last_counters = self._last_net_counters[nic]
                        upload_speed = (net_counters.bytes_sent - last_counters.bytes_sent) / time_diff
                        download_speed = (net_counters.bytes_recv - last_counters.bytes_recv) / time_diff

                        upload_speed_mb = upload_speed / (1024 ** 2)
                        download_speed_mb = download_speed / (1024 ** 2)

                        total_upload_speed += upload_speed
                        total_download_speed += download_speed

                        result[nic] = {
                            "upload_speed": upload_speed,
                            "download_speed": download_speed,
                            "upload_speed_mb": round(upload_speed_mb, 4),
                            "download_speed_mb": round(download_speed_mb, 4),
                            "total_upload": net_counters.bytes_sent,
                            "total_download": net_counters.bytes_recv,
                            "packets_sent": net_counters.packets_sent,
                            "packets_recv": net_counters.packets_recv
                        }

        self._last_net_counters = current_net
        self._last_net_time = current_time

        return {
            "interfaces": result,
            "total_upload_speed": total_upload_speed,
            "total_download_speed": total_download_speed,
            "total_upload_speed_mb": round(total_upload_speed / (1024 ** 2), 4),
            "total_download_speed_mb": round(total_download_speed / (1024 ** 2), 4)
        }

    def get_current_usage(self) -> Dict[str, Any]:
        """
        获取当前网络使用情况

        Returns:
            网络使用情况字典
        """
        io_data = self.get_network_io()

        result = {
            "timestamp": time.time(),
            "io": io_data
        }

        self._history.append({
            "timestamp": result["timestamp"],
            "upload_speed": io_data["total_upload_speed"],
            "download_speed": io_data["total_download_speed"]
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
        self._last_net_counters = None
        self._last_net_time = None

    def get_network_interfaces(self) -> Dict[str, Any]:
        """
        获取网络接口信息

        Returns:
            网络接口信息字典
        """
        interfaces = psutil.net_if_addrs()
        stats = psutil.net_if_stats()

        result = {}
        for nic, addrs in interfaces.items():
            result[nic] = {
                "addresses": [],
                "is_up": stats[nic].isup if nic in stats else False,
                "speed": stats[nic].speed if nic in stats else 0,
                "mtu": stats[nic].mtu if nic in stats else 0
            }
            for addr in addrs:
                result[nic]["addresses"].append({
                    "family": str(addr.family),
                    "address": addr.address,
                    "netmask": addr.netmask,
                    "broadcast": addr.broadcast
                })

        return result
