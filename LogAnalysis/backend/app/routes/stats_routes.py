# -*- coding: utf-8 -*-
"""
统计分析API路由
"""
from flask import Blueprint, request, jsonify
from datetime import datetime, timedelta

from ..modules.log_aggregator import log_aggregator

stats_bp = Blueprint('stats', __name__)


def _parse_time_range():
    """
    解析时间范围参数
    
    Returns:
        (start_time, end_time)
    """
    hours = request.args.get('hours', type=int)
    days = request.args.get('days', type=int)
    start_time_str = request.args.get('start_time')
    end_time_str = request.args.get('end_time')
    
    end_time = datetime.utcnow()
    
    if start_time_str and end_time_str:
        try:
            start_time = datetime.fromisoformat(start_time_str)
            end_time = datetime.fromisoformat(end_time_str)
        except Exception:
            start_time = end_time - timedelta(hours=24)
    elif hours:
        start_time = end_time - timedelta(hours=hours)
    elif days:
        start_time = end_time - timedelta(days=days)
    else:
        start_time = end_time - timedelta(hours=24)
    
    return start_time, end_time


@stats_bp.route('/summary', methods=['GET'])
def get_summary():
    """
    获取汇总统计信息
    
    Query Parameters:
        hours: 查询最近N小时
        days: 查询最近N天
        start_time: 开始时间
        end_time: 结束时间
        service_name: 服务名称过滤
    
    Returns:
        汇总统计JSON
    """
    start_time, end_time = _parse_time_range()
    service_name = request.args.get('service_name')
    
    stats = log_aggregator.get_summary_stats(start_time, end_time, service_name)
    
    return jsonify({
        'success': True,
        'data': stats
    })


@stats_bp.route('/by-level', methods=['GET'])
def get_by_level():
    """
    按日志级别统计
    
    Query Parameters:
        同summary
    
    Returns:
        级别统计JSON
    """
    start_time, end_time = _parse_time_range()
    service_name = request.args.get('service_name')
    
    stats = log_aggregator.aggregate_by_level(start_time, end_time, service_name)
    
    return jsonify({
        'success': True,
        'data': {'by_level': stats}
    })


@stats_bp.route('/by-service', methods=['GET'])
def get_by_service():
    """
    按服务统计
    
    Query Parameters:
        同summary，以及level
    
    Returns:
        服务统计JSON
    """
    start_time, end_time = _parse_time_range()
    level = request.args.get('level')
    
    stats = log_aggregator.aggregate_by_service(start_time, end_time, level)
    
    return jsonify({
        'success': True,
        'data': {'by_service': stats}
    })


@stats_bp.route('/by-module', methods=['GET'])
def get_by_module():
    """
    按模块统计
    
    Query Parameters:
        同summary
    
    Returns:
        模块统计JSON
    """
    start_time, end_time = _parse_time_range()
    service_name = request.args.get('service_name')
    
    stats = log_aggregator.aggregate_by_module(start_time, end_time, service_name)
    
    return jsonify({
        'success': True,
        'data': {'by_module': stats}
    })


@stats_bp.route('/time-series', methods=['GET'])
def get_time_series():
    """
    获取时间序列统计
    
    Query Parameters:
        window: 时间窗口（1m/5m/15m/1h/6h/1d）
        level: 日志级别过滤
        service_name: 服务名称过滤
        其他同summary
    
    Returns:
        时间序列JSON
    """
    start_time, end_time = _parse_time_range()
    window = request.args.get('window', '1h')
    level = request.args.get('level')
    service_name = request.args.get('service_name')
    
    series = log_aggregator.aggregate_by_time_window(
        start_time, end_time, window, level, service_name
    )
    
    return jsonify({
        'success': True,
        'data': {'time_series': series}
    })


@stats_bp.route('/error-rate', methods=['GET'])
def get_error_rate():
    """
    获取错误率
    
    Query Parameters:
        同summary
    
    Returns:
        错误率JSON
    """
    start_time, end_time = _parse_time_range()
    service_name = request.args.get('service_name')
    
    rate = log_aggregator.calculate_error_rate(start_time, end_time, service_name)
    
    return jsonify({
        'success': True,
        'data': {
            'error_rate': round(rate, 2),
            'time_range': {
                'start': start_time.isoformat(),
                'end': end_time.isoformat()
            }
        }
    })


@stats_bp.route('/top-services', methods=['GET'])
def get_top_services():
    """
    获取Top服务统计
    
    Query Parameters:
        limit: 返回数量
        by_errors: 是否按错误数排序
        其他同summary
    
    Returns:
        Top服务JSON
    """
    start_time, end_time = _parse_time_range()
    limit = request.args.get('limit', 10, type=int)
    by_errors = request.args.get('by_errors', 'false').lower() == 'true'
    
    services = log_aggregator.get_top_services(
        start_time, end_time, limit, by_errors
    )
    
    return jsonify({
        'success': True,
        'data': {'top_services': services}
    })


@stats_bp.route('/trend', methods=['GET'])
def get_trend():
    """
    获取趋势分析
    
    Query Parameters:
        window: 时间窗口
        其他同summary
    
    Returns:
        趋势分析JSON
    """
    start_time, end_time = _parse_time_range()
    window = request.args.get('window', '1h')
    
    trend = log_aggregator.get_trend_analysis(start_time, end_time, window)
    
    return jsonify({
        'success': True,
        'data': trend
    })


@stats_bp.route('/overview', methods=['GET'])
def get_overview():
    """
    获取概览数据（仪表盘数据）
    
    Returns:
        概览JSON
    """
    hours = request.args.get('hours', 24, type=int)
    end_time = datetime.utcnow()
    start_time = end_time - timedelta(hours=hours)
    
    summary = log_aggregator.get_summary_stats(start_time, end_time)
    trend = log_aggregator.get_trend_analysis(start_time, end_time, '1h')
    top_services = log_aggregator.get_top_services(start_time, end_time, 5, False)
    top_errors = log_aggregator.get_top_services(start_time, end_time, 5, True)
    
    overview = {
        'time_range': {
            'start': start_time.isoformat(),
            'end': end_time.isoformat(),
            'hours': hours
        },
        'summary': {
            'total_logs': summary.get('total_count', 0),
            'error_count': summary.get('error_count', 0),
            'warning_count': summary.get('warning_count', 0),
            'error_rate': summary.get('error_rate', 0)
        },
        'by_level': summary.get('by_level', {}),
        'trend': trend,
        'top_services': top_services,
        'top_error_services': top_errors
    }
    
    return jsonify({
        'success': True,
        'data': overview
    })
