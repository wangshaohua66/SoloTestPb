# -*- coding: utf-8 -*-
"""
告警管理模块
负责监控各项指标，超过阈值时触发告警
"""

import time
from typing import Dict, Any, List, Callable


class AlertManager:
    """告警管理类"""

    def __init__(self, config):
        """
        初始化告警管理器

        Args:
            config: 配置对象
        """
        self.config = config
        self._alert_history = []
        self._cooldown_period = 300
        self._last_alert_time = {}

    def check_cpu_alert(self, cpu_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        检查CPU告警

        Args:
            cpu_data: CPU数据

        Returns:
            告警信息
        """
        threshold = self.config.cpu_threshold
        current = cpu_data.get("overall", 0)

        alert = {
            "type": "cpu",
            "level": "warning" if current >= threshold else "normal",
            "threshold": threshold,
            "current": current,
            "message": "",
            "timestamp": time.time()
        }

        if current >= threshold:
            alert["message"] = f"CPU使用率过高: {current}% (阈值: {threshold}%)"
            if self._check_cooldown("cpu"):
                self._add_alert(alert)
        else:
            alert["message"] = "CPU使用率正常"

        return alert

    def check_memory_alert(self, memory_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        检查内存告警

        Args:
            memory_data: 内存数据

        Returns:
            告警信息
        """
        threshold = self.config.memory_threshold
        current = memory_data.get("virtual", {}).get("percent", 0)

        alert = {
            "type": "memory",
            "level": "warning" if current >= threshold else "normal",
            "threshold": threshold,
            "current": current,
            "message": "",
            "timestamp": time.time()
        }

        if current >= threshold:
            alert["message"] = f"内存使用率过高: {current}% (阈值: {threshold}%)"
            if self._check_cooldown("memory"):
                self._add_alert(alert)
        else:
            alert["message"] = "内存使用率正常"

        return alert

    def check_disk_alert(self, disk_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        检查磁盘告警

        Args:
            disk_data: 磁盘数据

        Returns:
            告警信息
        """
        threshold = self.config.disk_threshold
        current = disk_data.get("max_percent", 0)

        alert = {
            "type": "disk",
            "level": "warning" if current >= threshold else "normal",
            "threshold": threshold,
            "current": current,
            "message": "",
            "timestamp": time.time()
        }

        if current >= threshold:
            alert["message"] = f"磁盘使用率过高: {current}% (阈值: {threshold}%)"
            if self._check_cooldown("disk"):
                self._add_alert(alert)
        else:
            alert["message"] = "磁盘使用率正常"

        return alert

    def check_network_alert(self, network_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        检查网络告警

        Args:
            network_data: 网络数据

        Returns:
            告警信息
        """
        threshold = self.config.network_threshold
        io_data = network_data.get("io", {})
        upload_speed = io_data.get("total_upload_speed_mb", 0)
        download_speed = io_data.get("total_download_speed_mb", 0)
        current = max(upload_speed, download_speed)

        alert = {
            "type": "network",
            "level": "warning" if current >= threshold else "normal",
            "threshold": threshold,
            "current": current,
            "message": "",
            "timestamp": time.time()
        }

        if current >= threshold:
            alert["message"] = f"网络流量过高: {current:.2f} MB/s (阈值: {threshold} MB/s)"
            if self._check_cooldown("network"):
                self._add_alert(alert)
        else:
            alert["message"] = "网络流量正常"

        return alert

    def check_all_alerts(self, data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        检查所有告警

        Args:
            data: 所有监控数据

        Returns:
            告警列表
        """
        alerts = []

        if "cpu" in data:
            alerts.append(self.check_cpu_alert(data["cpu"]))
        if "memory" in data:
            alerts.append(self.check_memory_alert(data["memory"]))
        if "disk" in data:
            alerts.append(self.check_disk_alert(data["disk"]))
        if "network" in data:
            alerts.append(self.check_network_alert(data["network"]))

        return alerts

    def _check_cooldown(self, alert_type: str) -> bool:
        """
        检查告警冷却期

        Args:
            alert_type: 告警类型

        Returns:
            是否可以发送告警
        """
        current_time = time.time()
        last_time = self._last_alert_time.get(alert_type, 0)

        if current_time - last_time >= self._cooldown_period:
            self._last_alert_time[alert_type] = current_time
            return True
        return False

    def _add_alert(self, alert: Dict[str, Any]) -> None:
        """
        添加告警到历史记录

        Args:
            alert: 告警信息
        """
        self._alert_history.append(alert)
        if len(self._alert_history) > 1000:
            self._alert_history = self._alert_history[-1000:]

    def get_alert_history(self, limit: int = None) -> List[Dict[str, Any]]:
        """
        获取告警历史

        Args:
            limit: 返回的历史记录条数限制

        Returns:
            告警历史列表
        """
        if limit:
            return self._alert_history[-limit:]
        return self._alert_history

    def clear_alert_history(self) -> None:
        """清空告警历史"""
        self._alert_history.clear()
        self._last_alert_time.clear()

    def set_cooldown_period(self, seconds: int) -> None:
        """
        设置告警冷却期

        Args:
            seconds: 冷却期秒数
        """
        self._cooldown_period = max(60, seconds)
