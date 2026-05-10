# -*- coding: utf-8 -*-
"""
报表导出模块
生成日志分析报告，支持导出文本和JSON格式
"""
import json
from datetime import datetime, timedelta
from typing import Dict, List, Optional

from .. import db
from ..models import LogEntry, Alert
from .log_aggregator import log_aggregator


class ReportGenerator:
    """
    报表生成器
    生成日志分析报告，支持多种输出格式
    """
    
    def generate_summary_report(self, start_time: datetime, end_time: datetime,
                                 service_name: Optional[str] = None) -> Dict:
        """
        生成汇总报告
        
        Args:
            start_time: 开始时间
            end_time: 结束时间
            service_name: 服务名称（可选）
        
        Returns:
            报表数据字典
        """
        summary = log_aggregator.get_summary_stats(start_time, end_time, service_name)
        
        top_services = log_aggregator.get_top_services(
            start_time, end_time, limit=10, by_errors=False
        )
        top_error_services = log_aggregator.get_top_services(
            start_time, end_time, limit=10, by_errors=True
        )
        
        trend = log_aggregator.get_trend_analysis(start_time, end_time, window='1h')
        
        active_alerts = Alert.query.filter(
            Alert.created_at >= start_time,
            Alert.created_at <= end_time,
            Alert.is_resolved == False
        ).count()
        
        total_alerts = Alert.query.filter(
            Alert.created_at >= start_time,
            Alert.created_at <= end_time
        ).count()
        
        report = {
            'report_type': 'summary',
            'generated_at': datetime.utcnow().isoformat(),
            'time_range': summary['time_range'],
            'summary': {
                'total_logs': summary['total_count'],
                'error_count': summary['error_count'],
                'warning_count': summary['warning_count'],
                'error_rate': summary['error_rate']
            },
            'level_distribution': summary['by_level'],
            'service_distribution': summary['by_service'],
            'top_services': top_services,
            'top_error_services': top_error_services,
            'alerts': {
                'total': total_alerts,
                'active': active_alerts
            },
            'trend': {
                'error_rate_series': trend['error_rate_series'],
                'total_series': trend['total_series']
            }
        }
        
        return report
    
    def generate_detailed_report(self, start_time: datetime, end_time: datetime,
                                  service_name: Optional[str] = None,
                                  limit: int = 1000) -> Dict:
        """
        生成详细报告（包含日志列表）
        
        Args:
            start_time: 开始时间
            end_time: 结束时间
            service_name: 服务名称（可选）
            limit: 日志数量限制
        
        Returns:
            报表数据字典
        """
        summary = self.generate_summary_report(start_time, end_time, service_name)
        
        query = LogEntry.query.filter(
            LogEntry.timestamp >= start_time,
            LogEntry.timestamp <= end_time
        )
        
        if service_name:
            query = query.filter(LogEntry.service_name == service_name)
        
        logs = query.order_by(
            LogEntry.timestamp.desc()
        ).limit(limit).all()
        
        error_logs = LogEntry.query.filter(
            LogEntry.timestamp >= start_time,
            LogEntry.timestamp <= end_time,
            LogEntry.level.in_(['ERROR', 'FATAL', 'ERR'])
        ).order_by(
            LogEntry.timestamp.desc()
        ).limit(100).all()
        
        alerts = Alert.query.filter(
            Alert.created_at >= start_time,
            Alert.created_at <= end_time
        ).order_by(
            Alert.created_at.desc()
        ).all()
        
        detailed_report = {
            **summary,
            'report_type': 'detailed',
            'logs': [log.to_dict() for log in logs],
            'error_logs': [log.to_dict() for log in error_logs],
            'alerts': [alert.to_dict() for alert in alerts]
        }
        
        return detailed_report
    
    def export_to_json(self, report_data: Dict, pretty: bool = True) -> str:
        """
        导出为JSON格式
        
        Args:
            report_data: 报表数据
            pretty: 是否格式化输出
        
        Returns:
            JSON字符串
        """
        indent = 2 if pretty else None
        return json.dumps(report_data, ensure_ascii=False, indent=indent)
    
    def export_to_text(self, report_data: Dict) -> str:
        """
        导出为文本格式
        
        Args:
            report_data: 报表数据
        
        Returns:
            文本字符串
        """
        lines = []
        
        lines.append("=" * 60)
        lines.append("日志分析报告")
        lines.append(f"生成时间: {report_data.get('generated_at', '')}")
        lines.append("=" * 60)
        lines.append("")
        
        time_range = report_data.get('time_range', {})
        lines.append(f"时间范围: {time_range.get('start', '')} - {time_range.get('end', '')}")
        lines.append("")
        
        summary = report_data.get('summary', {})
        lines.append("-" * 60)
        lines.append("汇总统计")
        lines.append("-" * 60)
        lines.append(f"总日志数: {summary.get('total_logs', 0)}")
        lines.append(f"错误数: {summary.get('error_count', 0)}")
        lines.append(f"警告数: {summary.get('warning_count', 0)}")
        lines.append(f"错误率: {summary.get('error_rate', 0)}%")
        lines.append("")
        
        level_dist = report_data.get('level_distribution', {})
        if level_dist:
            lines.append("-" * 60)
            lines.append("日志级别分布")
            lines.append("-" * 60)
            for level, count in sorted(level_dist.items()):
                lines.append(f"  {level}: {count}")
            lines.append("")
        
        alerts = report_data.get('alerts', {})
        if alerts:
            lines.append("-" * 60)
            lines.append("告警统计")
            lines.append("-" * 60)
            lines.append(f"总告警数: {alerts.get('total', 0)}")
            lines.append(f"活跃告警数: {alerts.get('active', 0)}")
            lines.append("")
        
        top_services = report_data.get('top_services', [])
        if top_services:
            lines.append("-" * 60)
            lines.append("Top服务（按日志量）")
            lines.append("-" * 60)
            for i, svc in enumerate(top_services, 1):
                lines.append(f"  {i}. {svc.get('service', 'unknown')}: {svc.get('count', 0)}")
            lines.append("")
        
        top_errors = report_data.get('top_error_services', [])
        if top_errors:
            lines.append("-" * 60)
            lines.append("Top错误服务")
            lines.append("-" * 60)
            for i, svc in enumerate(top_errors, 1):
                lines.append(f"  {i}. {svc.get('service', 'unknown')}: {svc.get('count', 0)}")
            lines.append("")
        
        logs = report_data.get('logs', [])
        if logs:
            lines.append("-" * 60)
            lines.append(f"日志列表（共{len(logs)}条）")
            lines.append("-" * 60)
            for log in logs[:100]:
                timestamp = log.get('timestamp', '')
                level = log.get('level', 'INFO')
                service = log.get('service_name', 'unknown')
                message = log.get('message', '')
                lines.append(f"[{timestamp}] [{level}] [{service}] {message}")
            lines.append("")
        
        lines.append("=" * 60)
        lines.append("报告结束")
        lines.append("=" * 60)
        
        return '\n'.join(lines)
    
    def generate_hourly_report(self, hours: int = 24, service_name: Optional[str] = None) -> Dict:
        """
        生成小时级报告
        
        Args:
            hours: 小时数
            service_name: 服务名称（可选）
        
        Returns:
            报表数据字典
        """
        end_time = datetime.utcnow()
        start_time = end_time - timedelta(hours=hours)
        
        return self.generate_summary_report(start_time, end_time, service_name)
    
    def generate_daily_report(self, service_name: Optional[str] = None) -> Dict:
        """
        生成日报
        
        Args:
            service_name: 服务名称（可选）
        
        Returns:
            报表数据字典
        """
        return self.generate_hourly_report(24, service_name)
    
    def generate_weekly_report(self, service_name: Optional[str] = None) -> Dict:
        """
        生成周报
        
        Args:
            service_name: 服务名称（可选）
        
        Returns:
            报表数据字典
        """
        return self.generate_hourly_report(168, service_name)


report_generator = ReportGenerator()
