# -*- coding: utf-8 -*-
"""
日志聚合模块
按时间窗口、服务、级别等维度聚合日志，统计错误率、响应时间等指标
"""
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any

from sqlalchemy import func, and_, or_

from .. import db
from ..models import LogEntry, StatsRecord


class LogAggregator:
    """
    日志聚合器
    提供多维度的日志聚合和统计分析功能
    """
    
    def __init__(self):
        """
        初始化聚合器
        """
        self.time_windows = {
            '1m': timedelta(minutes=1),
            '5m': timedelta(minutes=5),
            '15m': timedelta(minutes=15),
            '1h': timedelta(hours=1),
            '6h': timedelta(hours=6),
            '1d': timedelta(days=1)
        }
    
    def aggregate_by_level(self, start_time: datetime, end_time: datetime,
                            service_name: Optional[str] = None) -> Dict[str, int]:
        """
        按日志级别聚合
        
        Args:
            start_time: 开始时间
            end_time: 结束时间
            service_name: 服务名称（可选）
        
        Returns:
            按级别统计的字典，如 {'INFO': 100, 'ERROR': 5, ...}
        """
        query = db.session.query(
            LogEntry.level,
            func.count(LogEntry.id).label('count')
        ).filter(
            LogEntry.timestamp >= start_time,
            LogEntry.timestamp <= end_time
        )
        
        if service_name:
            query = query.filter(LogEntry.service_name == service_name)
        
        query = query.group_by(LogEntry.level).all()
        
        result = {}
        for row in query:
            result[row[0]] = int(row[1])
        
        return result
    
    def aggregate_by_service(self, start_time: datetime, end_time: datetime,
                              level: Optional[str] = None) -> Dict[str, int]:
        """
        按服务名称聚合
        
        Args:
            start_time: 开始时间
            end_time: 结束时间
            level: 日志级别（可选）
        
        Returns:
            按服务统计的字典
        """
        query = db.session.query(
            func.coalesce(LogEntry.service_name, 'unknown'),
            func.count(LogEntry.id).label('count')
        ).filter(
            LogEntry.timestamp >= start_time,
            LogEntry.timestamp <= end_time
        )
        
        if level:
            query = query.filter(LogEntry.level == level)
        
        query = query.group_by(LogEntry.service_name).all()
        
        result = {}
        for row in query:
            result[row[0] or 'unknown'] = int(row[1])
        
        return result
    
    def aggregate_by_module(self, start_time: datetime, end_time: datetime,
                             service_name: Optional[str] = None) -> Dict[str, int]:
        """
        按模块聚合
        
        Args:
            start_time: 开始时间
            end_time: 结束时间
            service_name: 服务名称（可选）
        
        Returns:
            按模块统计的字典
        """
        query = db.session.query(
            func.coalesce(LogEntry.module, 'unknown'),
            func.count(LogEntry.id).label('count')
        ).filter(
            LogEntry.timestamp >= start_time,
            LogEntry.timestamp <= end_time
        )
        
        if service_name:
            query = query.filter(LogEntry.service_name == service_name)
        
        query = query.group_by(LogEntry.module).all()
        
        result = {}
        for row in query:
            result[row[0] or 'unknown'] = int(row[1])
        
        return result
    
    def aggregate_by_time_window(self, start_time: datetime, end_time: datetime,
                                   window: str = '5m', level: Optional[str] = None,
                                   service_name: Optional[str] = None) -> List[Dict]:
        """
        按时间窗口聚合
        
        Args:
            start_time: 开始时间
            end_time: 结束时间
            window: 时间窗口大小（1m/5m/15m/1h/6h/1d）
            level: 日志级别（可选）
            service_name: 服务名称（可选）
        
        Returns:
            时间窗口统计列表
        """
        window_delta = self.time_windows.get(window, timedelta(minutes=5))
        
        windows = []
        current = start_time
        while current < end_time:
            windows.append({
                'start': current,
                'end': min(current + window_delta, end_time)
            })
            current += window_delta
        
        results = []
        
        for win in windows:
            query = db.session.query(
                LogEntry.level,
                func.count(LogEntry.id).label('count')
            ).filter(
                LogEntry.timestamp >= win['start'],
                LogEntry.timestamp < win['end']
            )
            
            if level:
                query = query.filter(LogEntry.level == level)
            if service_name:
                query = query.filter(LogEntry.service_name == service_name)
            
            query = query.group_by(LogEntry.level).all()
            
            window_stats = {}
            total = 0
            for row in query:
                window_stats[row[0]] = int(row[1])
                total += int(row[1])
            
            results.append({
                'window_start': win['start'].isoformat(),
                'window_end': win['end'].isoformat(),
                'counts': window_stats,
                'total': total
            })
        
        return results
    
    def calculate_error_rate(self, start_time: datetime, end_time: datetime,
                              service_name: Optional[str] = None) -> float:
        """
        计算错误率
        
        Args:
            start_time: 开始时间
            end_time: 结束时间
            service_name: 服务名称（可选）
        
        Returns:
            错误率（0-100）
        """
        query = db.session.query(
            func.count(LogEntry.id).label('total')
        ).filter(
            LogEntry.timestamp >= start_time,
            LogEntry.timestamp <= end_time
        )
        
        if service_name:
            query = query.filter(LogEntry.service_name == service_name)
        
        total = query.scalar() or 0
        
        if total == 0:
            return 0.0
        
        error_query = db.session.query(
            func.count(LogEntry.id).label('error_count')
        ).filter(
            LogEntry.timestamp >= start_time,
            LogEntry.timestamp <= end_time,
            LogEntry.level.in_(['ERROR', 'FATAL', 'ERR'])
        )
        
        if service_name:
            error_query = error_query.filter(LogEntry.service_name == service_name)
        
        error_count = error_query.scalar() or 0
        
        return (error_count / total) * 100
    
    def get_summary_stats(self, start_time: datetime, end_time: datetime,
                          service_name: Optional[str] = None) -> Dict[str, Any]:
        """
        获取汇总统计数据
        
        Args:
            start_time: 开始时间
            end_time: 结束时间
            service_name: 服务名称（可选）
        
        Returns:
            汇总统计字典
        """
        level_stats = self.aggregate_by_level(start_time, end_time, service_name)
        service_stats = self.aggregate_by_service(start_time, end_time)
        error_rate = self.calculate_error_rate(start_time, end_time, service_name)
        
        total = sum(level_stats.values())
        error_count = sum(
            count for level, count in level_stats.items()
            if level in ['ERROR', 'FATAL', 'ERR']
        )
        warn_count = sum(
            count for level, count in level_stats.items()
            if level in ['WARNING', 'WARN']
        )
        
        return {
            'time_range': {
                'start': start_time.isoformat(),
                'end': end_time.isoformat()
            },
            'total_count': total,
            'error_count': error_count,
            'warning_count': warn_count,
            'error_rate': round(error_rate, 2),
            'by_level': level_stats,
            'by_service': service_stats
        }
    
    def get_top_services(self, start_time: datetime, end_time: datetime,
                          limit: int = 10, by_errors: bool = False) -> List[Dict]:
        """
        获取Top服务统计
        
        Args:
            start_time: 开始时间
            end_time: 结束时间
            limit: 返回数量限制
            by_errors: 是否按错误数排序
        
        Returns:
            服务统计列表
        """
        query = db.session.query(
            func.coalesce(LogEntry.service_name, 'unknown').label('service'),
            func.count(LogEntry.id).label('total')
        ).filter(
            LogEntry.timestamp >= start_time,
            LogEntry.timestamp <= end_time
        )
        
        if by_errors:
            query = query.filter(
                LogEntry.level.in_(['ERROR', 'FATAL', 'ERR'])
            )
        
        query = query.group_by(
            func.coalesce(LogEntry.service_name, 'unknown')
        ).order_by(
            db.desc('total')
        ).limit(limit).all()
        
        return [
            {
                'service': row.service,
                'count': int(row.total)
            }
            for row in query
        ]
    
    def get_trend_analysis(self, start_time: datetime, end_time: datetime,
                            window: str = '1h') -> Dict[str, Any]:
        """
        获取趋势分析数据
        
        Args:
            start_time: 开始时间
            end_time: 结束时间
            window: 时间窗口大小
        
        Returns:
            趋势分析结果
        """
        time_series = self.aggregate_by_time_window(start_time, end_time, window)
        
        error_rate_series = []
        total_series = []
        for item in time_series:
            total = item['total']
            errors = item['counts'].get('ERROR', 0) + item['counts'].get('FATAL', 0)
            error_rate = (errors / total * 100) if total > 0 else 0
            
            error_rate_series.append({
                'time': item['window_start'],
                'value': round(error_rate, 2)
            })
            total_series.append({
                'time': item['window_start'],
                'value': total
            })
        
        return {
            'error_rate_series': error_rate_series,
            'total_series': total_series,
            'raw_series': time_series
        }


log_aggregator = LogAggregator()
