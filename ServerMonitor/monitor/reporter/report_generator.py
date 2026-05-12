# -*- coding: utf-8 -*-
"""
报告生成模块
生成包含历史趋势图的资源使用报告
"""

import os
import time
from datetime import datetime
from typing import Dict, Any, List
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt


class ReportGenerator:
    """报告生成类"""

    def __init__(self, config):
        """
        初始化报告生成器

        Args:
            config: 配置对象
        """
        self.config = config
        self._report_path = config.get("report.path", "./reports")
        self._ensure_report_dir()

    def _ensure_report_dir(self) -> None:
        """确保报告目录存在"""
        if not os.path.exists(self._report_path):
            os.makedirs(self._report_path, exist_ok=True)

    def generate_report(self, data_store) -> str:
        """
        生成完整报告

        Args:
            data_store: 数据存储对象

        Returns:
            报告文件路径
        """
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        report_dir = os.path.join(self._report_path, f"report_{timestamp}")
        os.makedirs(report_dir, exist_ok=True)

        cpu_data = data_store.get_cpu_data()
        memory_data = data_store.get_memory_data()
        disk_data = data_store.get_disk_data()
        network_data = data_store.get_network_data()

        self._generate_cpu_chart(cpu_data, report_dir)
        self._generate_memory_chart(memory_data, report_dir)
        self._generate_disk_chart(disk_data, report_dir)
        self._generate_network_chart(network_data, report_dir)

        html_path = self._generate_html_report(
            cpu_data, memory_data, disk_data, network_data, report_dir
        )

        return html_path

    def _generate_cpu_chart(self, data: List[Dict[str, Any]], report_dir: str) -> None:
        """
        生成CPU趋势图

        Args:
            data: CPU数据
            report_dir: 报告目录
        """
        if not data:
            return

        timestamps = [d.get("timestamp", 0) for d in data]
        overall = [d.get("overall", 0) for d in data]

        plt.figure(figsize=(10, 6))
        plt.plot(timestamps, overall, label="Overall CPU", color="blue")
        plt.xlabel("Time")
        plt.ylabel("CPU Usage (%)")
        plt.title("CPU Usage Trend")
        plt.legend()
        plt.grid(True, alpha=0.3)
        plt.ylim(0, 100)

        chart_path = os.path.join(report_dir, "cpu_trend.png")
        plt.savefig(chart_path, dpi=100, bbox_inches="tight")
        plt.close()

    def _generate_memory_chart(self, data: List[Dict[str, Any]], report_dir: str) -> None:
        """
        生成内存趋势图

        Args:
            data: 内存数据
            report_dir: 报告目录
        """
        if not data:
            return

        timestamps = [d.get("timestamp", 0) for d in data]
        virtual_percent = [d.get("virtual", {}).get("percent", 0) for d in data]
        swap_percent = [d.get("swap", {}).get("percent", 0) for d in data]

        plt.figure(figsize=(10, 6))
        plt.plot(timestamps, virtual_percent, label="Virtual Memory", color="green")
        plt.plot(timestamps, swap_percent, label="Swap Memory", color="orange")
        plt.xlabel("Time")
        plt.ylabel("Memory Usage (%)")
        plt.title("Memory Usage Trend")
        plt.legend()
        plt.grid(True, alpha=0.3)
        plt.ylim(0, 100)

        chart_path = os.path.join(report_dir, "memory_trend.png")
        plt.savefig(chart_path, dpi=100, bbox_inches="tight")
        plt.close()

    def _generate_disk_chart(self, data: List[Dict[str, Any]], report_dir: str) -> None:
        """
        生成磁盘趋势图

        Args:
            data: 磁盘数据
            report_dir: 报告目录
        """
        if not data:
            return

        timestamps = [d.get("timestamp", 0) for d in data]
        max_percent = [d.get("max_percent", 0) for d in data]

        plt.figure(figsize=(10, 6))
        plt.plot(timestamps, max_percent, label="Max Disk Usage", color="red")
        plt.xlabel("Time")
        plt.ylabel("Disk Usage (%)")
        plt.title("Disk Usage Trend")
        plt.legend()
        plt.grid(True, alpha=0.3)
        plt.ylim(0, 100)

        chart_path = os.path.join(report_dir, "disk_trend.png")
        plt.savefig(chart_path, dpi=100, bbox_inches="tight")
        plt.close()

    def _generate_network_chart(self, data: List[Dict[str, Any]], report_dir: str) -> None:
        """
        生成网络趋势图

        Args:
            data: 网络数据
            report_dir: 报告目录
        """
        if not data:
            return

        timestamps = [d.get("timestamp", 0) for d in data]
        upload_speed = [d.get("io", {}).get("total_upload_speed_mb", 0) for d in data]
        download_speed = [d.get("io", {}).get("total_download_speed_mb", 0) for d in data]

        plt.figure(figsize=(10, 6))
        plt.plot(timestamps, upload_speed, label="Upload Speed", color="purple")
        plt.plot(timestamps, download_speed, label="Download Speed", color="blue")
        plt.xlabel("Time")
        plt.ylabel("Speed (MB/s)")
        plt.title("Network Traffic Trend")
        plt.legend()
        plt.grid(True, alpha=0.3)

        chart_path = os.path.join(report_dir, "network_trend.png")
        plt.savefig(chart_path, dpi=100, bbox_inches="tight")
        plt.close()

    def _generate_html_report(
        self,
        cpu_data: List[Dict[str, Any]],
        memory_data: List[Dict[str, Any]],
        disk_data: List[Dict[str, Any]],
        network_data: List[Dict[str, Any]],
        report_dir: str
    ) -> str:
        """
        生成HTML报告

        Args:
            cpu_data: CPU数据
            memory_data: 内存数据
            disk_data: 磁盘数据
            network_data: 网络数据
            report_dir: 报告目录

        Returns:
            HTML报告路径
        """
        html_content = f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>服务器资源监控报告</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 20px; }}
        h1 {{ color: #333; text-align: center; }}
        h2 {{ color: #555; margin-top: 30px; }}
        .summary {{ background-color: #f5f5f5; padding: 20px; border-radius: 5px; }}
        .chart {{ margin: 20px 0; text-align: center; }}
        .chart img {{ max-width: 800px; border: 1px solid #ddd; border-radius: 5px; }}
        table {{ width: 100%; border-collapse: collapse; margin: 20px 0; }}
        th, td {{ border: 1px solid #ddd; padding: 10px; text-align: left; }}
        th {{ background-color: #4CAF50; color: white; }}
        tr:nth-child(even) {{ background-color: #f2f2f2; }}
        .timestamp {{ color: #666; text-align: center; }}
    </style>
</head>
<body>
    <h1>服务器资源监控报告</h1>
    <p class="timestamp">生成时间: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}</p>

    <div class="summary">
        <h2>数据摘要</h2>
        <table>
            <tr>
                <th>指标</th>
                <th>数据点数量</th>
                <th>平均值</th>
                <th>最大值</th>
                <th>最小值</th>
            </tr>
            {self._generate_summary_row("CPU", cpu_data, "overall")}
            {self._generate_summary_row("内存", memory_data, "virtual.percent")}
            {self._generate_disk_summary_row(disk_data)}
            {self._generate_network_summary_row(network_data)}
        </table>
    </div>

    <div class="chart">
        <h2>CPU使用率趋势</h2>
        <img src="cpu_trend.png" alt="CPU Usage Trend">
    </div>

    <div class="chart">
        <h2>内存使用率趋势</h2>
        <img src="memory_trend.png" alt="Memory Usage Trend">
    </div>

    <div class="chart">
        <h2>磁盘使用率趋势</h2>
        <img src="disk_trend.png" alt="Disk Usage Trend">
    </div>

    <div class="chart">
        <h2>网络流量趋势</h2>
        <img src="network_trend.png" alt="Network Traffic Trend">
    </div>

</body>
</html>
        """

        html_path = os.path.join(report_dir, "report.html")
        with open(html_path, "w", encoding="utf-8") as f:
            f.write(html_content)

        return html_path

    def _generate_summary_row(self, name: str, data: List[Dict[str, Any]], key: str) -> str:
        """
        生成摘要表格行

        Args:
            name: 指标名称
            data: 数据列表
            key: 数据键

        Returns:
            HTML表格行
        """
        if not data:
            return f"<tr><td>{name}</td><td>0</td><td>-</td><td>-</td><td>-</td></tr>"

        values = []
        for d in data:
            if "." in key:
                k1, k2 = key.split(".")
                val = d.get(k1, {}).get(k2, 0)
            else:
                val = d.get(key, 0)
            values.append(val)

        count = len(values)
        avg = sum(values) / count if count > 0 else 0
        max_val = max(values) if values else 0
        min_val = min(values) if values else 0

        return f"""
        <tr>
            <td>{name}</td>
            <td>{count}</td>
            <td>{avg:.2f}%</td>
            <td>{max_val:.2f}%</td>
            <td>{min_val:.2f}%</td>
        </tr>
        """

    def _generate_disk_summary_row(self, data: List[Dict[str, Any]]) -> str:
        """生成磁盘摘要行"""
        if not data:
            return "<tr><td>磁盘</td><td>0</td><td>-</td><td>-</td><td>-</td></tr>"

        values = [d.get("max_percent", 0) for d in data]
        count = len(values)
        avg = sum(values) / count if count > 0 else 0
        max_val = max(values) if values else 0
        min_val = min(values) if values else 0

        return f"""
        <tr>
            <td>磁盘</td>
            <td>{count}</td>
            <td>{avg:.2f}%</td>
            <td>{max_val:.2f}%</td>
            <td>{min_val:.2f}%</td>
        </tr>
        """

    def _generate_network_summary_row(self, data: List[Dict[str, Any]]) -> str:
        """生成网络摘要行"""
        if not data:
            return "<tr><td>网络</td><td>0</td><td>-</td><td>-</td><td>-</td></tr>"

        upload_values = [d.get("io", {}).get("total_upload_speed_mb", 0) for d in data]
        download_values = [d.get("io", {}).get("total_download_speed_mb", 0) for d in data]

        count = len(data)
        avg_upload = sum(upload_values) / count if count > 0 else 0
        avg_download = sum(download_values) / count if count > 0 else 0
        max_upload = max(upload_values) if upload_values else 0
        max_download = max(download_values) if download_values else 0

        return f"""
        <tr>
            <td>网络</td>
            <td>{count}</td>
            <td>↑{avg_upload:.2f} / ↓{avg_download:.2f} MB/s</td>
            <td>↑{max_upload:.2f} / ↓{max_download:.2f} MB/s</td>
            <td>-</td>
        </tr>
        """
