"""
报告生成模块
负责生成网站可用性统计报告和响应时间趋势图
"""

import os
from datetime import datetime, timedelta
from typing import Dict, List, Any
import logging
import json
from collections import defaultdict

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.dates as mdates

from .http_checker import CheckResult


class Reporter:
    """
    报告生成类
    负责生成统计报告和图表
    """

    def __init__(self, output_dir: str = './reports', history_days: int = 7):
        """
        初始化报告生成器

        Args:
            output_dir: 报告输出目录
            history_days: 统计历史天数
        """
        self.output_dir = output_dir
        self.history_days = history_days
        self.logger = logging.getLogger(__name__)
        self.history_data: Dict[str, List[CheckResult]] = defaultdict(list)

        os.makedirs(output_dir, exist_ok=True)

    def add_result(self, result: CheckResult) -> None:
        """
        添加检测结果到历史数据

        Args:
            result: 检测结果对象
        """
        site_name = result.site_name
        self.history_data[site_name].append(result)

        cutoff_time = datetime.now() - timedelta(days=self.history_days)
        self.history_data[site_name] = [
            r for r in self.history_data[site_name]
            if r.timestamp > cutoff_time
        ]

    def generate_report(self) -> str:
        """
        生成综合统计报告

        Returns:
            报告文件路径
        """
        self.logger.info("开始生成网站可用性统计报告")

        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        report_filename = f"report_{timestamp}.html"
        report_path = os.path.join(self.output_dir, report_filename)

        summary = self._calculate_summary()
        chart_path = self._generate_response_time_chart(timestamp)

        html_content = self._generate_html_content(summary, chart_path)

        with open(report_path, 'w', encoding='utf-8') as f:
            f.write(html_content)

        self._save_raw_data(timestamp)

        self.logger.info(f"报告已生成: {report_path}")
        return report_path

    def _calculate_summary(self) -> Dict[str, Any]:
        """
        计算各站点的统计摘要

        Returns:
            统计摘要字典
        """
        summary = {}

        for site_name, results in self.history_data.items():
            if not results:
                continue

            total_checks = len(results)
            successful_checks = sum(1 for r in results if r.success)
            availability_rate = (successful_checks / total_checks * 100) if total_checks > 0 else 0

            response_times = [r.response_time for r in results if r.response_time > 0]
            avg_response_time = sum(response_times) / len(response_times) if response_times else 0
            max_response_time = max(response_times) if response_times else 0
            min_response_time = min(response_times) if response_times else 0

            last_check = results[-1]

            summary[site_name] = {
                'url': last_check.url,
                'total_checks': total_checks,
                'successful_checks': successful_checks,
                'availability_rate': round(availability_rate, 2),
                'avg_response_time': round(avg_response_time, 2),
                'max_response_time': round(max_response_time, 2),
                'min_response_time': round(min_response_time, 2),
                'last_status': '正常' if last_check.success else '异常',
                'last_check_time': last_check.timestamp.strftime('%Y-%m-%d %H:%M:%S')
            }

        return summary

    def _generate_response_time_chart(self, timestamp: str) -> str:
        """
        生成响应时间趋势图

        Args:
            timestamp: 时间戳用于文件名

        Returns:
            图表文件路径
        """
        chart_filename = f"response_time_{timestamp}.png"
        chart_path = os.path.join(self.output_dir, chart_filename)

        plt.figure(figsize=(12, 6))

        for site_name, results in self.history_data.items():
            if not results:
                continue

            sorted_results = sorted(results, key=lambda x: x.timestamp)
            times = [r.timestamp for r in sorted_results]
            response_times = [r.response_time for r in sorted_results]

            plt.plot(times, response_times, marker='o', markersize=3, label=site_name, linewidth=2)

        plt.xlabel('检测时间', fontsize=12)
        plt.ylabel('响应时间 (ms)', fontsize=12)
        plt.title('网站响应时间趋势图', fontsize=14, fontweight='bold')
        plt.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
        plt.grid(True, alpha=0.3)

        plt.gcf().autofmt_xdate()
        date_format = mdates.DateFormatter('%m-%d %H:%M')
        plt.gca().xaxis.set_major_formatter(date_format)

        plt.tight_layout()
        plt.savefig(chart_path, dpi=150, bbox_inches='tight')
        plt.close()

        return chart_path

    def _generate_html_content(self, summary: Dict[str, Any], chart_path: str) -> str:
        """
        生成HTML报告内容

        Args:
            summary: 统计摘要
            chart_path: 图表文件路径

        Returns:
            HTML内容字符串
        """
        chart_filename = os.path.basename(chart_path)

        html = f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>网站健康检测报告</title>
    <style>
        body {{
            font-family: 'Microsoft YaHei', Arial, sans-serif;
            margin: 20px;
            background-color: #f5f5f5;
        }}
        h1 {{
            color: #333;
            text-align: center;
            margin-bottom: 30px;
        }}
        h2 {{
            color: #555;
            border-bottom: 2px solid #4CAF50;
            padding-bottom: 10px;
            margin-top: 30px;
        }}
        .summary-table {{
            width: 100%;
            border-collapse: collapse;
            margin-top: 20px;
            background-color: white;
            box-shadow: 0 2px 5px rgba(0,0,0,0.1);
        }}
        .summary-table th, .summary-table td {{
            padding: 12px 15px;
            text-align: left;
            border-bottom: 1px solid #ddd;
        }}
        .summary-table th {{
            background-color: #4CAF50;
            color: white;
            font-weight: bold;
        }}
        .summary-table tr:hover {{
            background-color: #f5f5f5;
        }}
        .status-normal {{
            color: #4CAF50;
            font-weight: bold;
        }}
        .status-error {{
            color: #f44336;
            font-weight: bold;
        }}
        .chart-container {{
            margin-top: 20px;
            text-align: center;
            background-color: white;
            padding: 20px;
            box-shadow: 0 2px 5px rgba(0,0,0,0.1);
        }}
        .chart-container img {{
            max-width: 100%;
            height: auto;
        }}
        .report-info {{
            background-color: #e3f2fd;
            padding: 15px;
            border-radius: 5px;
            margin-bottom: 20px;
        }}
    </style>
</head>
<body>
    <h1>网站健康检测报告</h1>

    <div class="report-info">
        <p><strong>生成时间:</strong> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
        <p><strong>统计周期:</strong> 最近 {self.history_days} 天</p>
    </div>

    <h2>站点统计摘要</h2>
    <table class="summary-table">
        <thead>
            <tr>
                <th>站点名称</th>
                <th>URL</th>
                <th>检测次数</th>
                <th>成功次数</th>
                <th>可用性(%)</th>
                <th>平均响应时间(ms)</th>
                <th>最大响应时间(ms)</th>
                <th>最小响应时间(ms)</th>
                <th>最新状态</th>
                <th>最后检测时间</th>
            </tr>
        </thead>
        <tbody>
"""

        for site_name, data in summary.items():
            status_class = 'status-normal' if data['last_status'] == '正常' else 'status-error'
            html += f"""
            <tr>
                <td><strong>{site_name}</strong></td>
                <td><a href="{data['url']}" target="_blank">{data['url']}</a></td>
                <td>{data['total_checks']}</td>
                <td>{data['successful_checks']}</td>
                <td>{data['availability_rate']}%</td>
                <td>{data['avg_response_time']}</td>
                <td>{data['max_response_time']}</td>
                <td>{data['min_response_time']}</td>
                <td class="{status_class}">{data['last_status']}</td>
                <td>{data['last_check_time']}</td>
            </tr>
"""

        html += f"""
        </tbody>
    </table>

    <h2>响应时间趋势图</h2>
    <div class="chart-container">
        <img src="{chart_filename}" alt="响应时间趋势图">
    </div>

</body>
</html>
"""

        return html

    def _save_raw_data(self, timestamp: str) -> None:
        """
        保存原始检测数据为JSON格式

        Args:
            timestamp: 时间戳
        """
        data_filename = f"raw_data_{timestamp}.json"
        data_path = os.path.join(self.output_dir, data_filename)

        export_data = {}
        for site_name, results in self.history_data.items():
            export_data[site_name] = []
            for result in results:
                export_data[site_name].append({
                    'timestamp': result.timestamp.strftime('%Y-%m-%d %H:%M:%S'),
                    'success': result.success,
                    'status_code': result.status_code,
                    'response_time': result.response_time,
                    'error_message': result.error_message
                })

        with open(data_path, 'w', encoding='utf-8') as f:
            json.dump(export_data, f, ensure_ascii=False, indent=2)
