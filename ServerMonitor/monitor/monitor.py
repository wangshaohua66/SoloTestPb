# -*- coding: utf-8 -*-
"""
服务器资源监控主程序
整合所有监控模块，提供统一的监控入口
"""

import time
import signal
import sys
from typing import Dict, Any
from datetime import datetime

from .config import Config
from .core.cpu_monitor import CPUMonitor
from .core.memory_monitor import MemoryMonitor
from .core.disk_monitor import DiskMonitor
from .core.network_monitor import NetworkMonitor
from .core.data_store import DataStore
from .notifier.alert_manager import AlertManager
from .notifier.email_notifier import EmailNotifier
from .reporter.report_generator import ReportGenerator


class ServerMonitor:
    """服务器监控主类"""

    def __init__(self, config_path: str = "config.json"):
        """
        初始化服务器监控器

        Args:
            config_path: 配置文件路径
        """
        self.config = Config(config_path)
        self.interval = self.config.interval

        self.cpu_monitor = CPUMonitor(self.interval)
        self.memory_monitor = MemoryMonitor()
        self.disk_monitor = DiskMonitor()
        self.network_monitor = NetworkMonitor()

        self.data_store = DataStore(self.config.get("data_retention", 86400))

        self.alert_manager = AlertManager(self.config)
        self.email_notifier = EmailNotifier(self.config)
        self.report_generator = ReportGenerator(self.config)

        self._running = False
        self._last_report_time = 0
        self._report_interval = self.config.get("report.interval", 3600)

        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)

    def _signal_handler(self, signum, frame):
        """信号处理函数"""
        print("\n收到停止信号，正在停止监控...")
        self._running = False

    def start(self):
        """启动监控"""
        print("=" * 60)
        print("服务器资源监控工具")
        print("=" * 60)
        print(f"监控间隔: {self.interval} 秒")
        print(f"报告间隔: {self._report_interval} 秒")
        print(f"邮件通知: {'已启用' if self.email_notifier.is_enabled() else '未启用'}")
        print("=" * 60)
        print("按 Ctrl+C 停止监控")
        print()

        self._running = True

        while self._running:
            try:
                self._collect_once()
                self._check_report()
                time.sleep(self.interval)
            except Exception as e:
                print(f"监控出错: {e}")
                time.sleep(self.interval)

        print("监控已停止。")

    def _collect_once(self) -> Dict[str, Any]:
        """
        执行一次数据采集

        Returns:
            采集到的数据
        """
        cpu_data = self.cpu_monitor.get_current_usage()
        memory_data = self.memory_monitor.get_current_usage()
        disk_data = self.disk_monitor.get_current_usage()
        network_data = self.network_monitor.get_current_usage()

        self.data_store.add_cpu_data(cpu_data)
        self.data_store.add_memory_data(memory_data)
        self.data_store.add_disk_data(disk_data)
        self.data_store.add_network_data(network_data)

        data = {
            "cpu": cpu_data,
            "memory": memory_data,
            "disk": disk_data,
            "network": network_data
        }

        alerts = self.alert_manager.check_all_alerts(data)

        self._print_status(data, alerts)

        warning_alerts = [a for a in alerts if a.get("level") == "warning"]
        if warning_alerts:
            self.email_notifier.send_alert(warning_alerts)

        return data

    def _print_status(self, data: Dict[str, Any], alerts: list):
        """
        打印监控状态

        Args:
            data: 监控数据
            alerts: 告警列表
        """
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        cpu = data["cpu"]["overall"]
        memory = data["memory"]["virtual"]["percent"]
        disk = data["disk"]["max_percent"]
        net_up = data["network"]["io"]["total_upload_speed_mb"]
        net_down = data["network"]["io"]["total_download_speed_mb"]

        warning_alerts = [a for a in alerts if a.get("level") == "warning"]
        status = "⚠ WARNING" if warning_alerts else "✓ OK"

        print(
            f"[{timestamp}] [{status}] "
            f"CPU: {cpu:5.1f}% | "
            f"内存: {memory:5.1f}% | "
            f"磁盘: {disk:5.1f}% | "
            f"网络: ↑{net_up:.2f} ↓{net_down:.2f} MB/s"
        )

    def _check_report(self):
        """检查是否需要生成报告"""
        current_time = time.time()
        if current_time - self._last_report_time >= self._report_interval:
            try:
                report_path = self.report_generator.generate_report(self.data_store)
                print(f"报告已生成: {report_path}")
                self._last_report_time = current_time
                self.email_notifier.send_report(report_path)
            except Exception as e:
                print(f"生成报告失败: {e}")

    def get_latest_data(self) -> Dict[str, Any]:
        """
        获取最新的监控数据

        Returns:
            最新的监控数据
        """
        return {
            "cpu": self.data_store.get_cpu_data(limit=1)[0] if self.data_store.get_cpu_data() else None,
            "memory": self.data_store.get_memory_data(limit=1)[0] if self.data_store.get_memory_data() else None,
            "disk": self.data_store.get_disk_data(limit=1)[0] if self.data_store.get_disk_data() else None,
            "network": self.data_store.get_network_data(limit=1)[0] if self.data_store.get_network_data() else None
        }

    def generate_manual_report(self) -> str:
        """
        手动生成报告

        Returns:
            报告文件路径
        """
        report_path = self.report_generator.generate_report(self.data_store)
        print(f"报告已生成: {report_path}")
        return report_path


def main():
    """主函数入口"""
    monitor = ServerMonitor()
    monitor.start()


if __name__ == "__main__":
    main()
