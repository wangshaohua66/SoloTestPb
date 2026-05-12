# -*- coding: utf-8 -*-
"""
报表导出API路由
"""
from flask import Blueprint, request, jsonify, make_response
from datetime import datetime, timedelta

from ..modules.report_generator import report_generator

report_bp = Blueprint('report', __name__)


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


@report_bp.route('/summary', methods=['GET'])
def get_summary_report():
    """
    获取汇总报表
    
    Query Parameters:
        hours: 查询最近N小时
        days: 查询最近N天
        start_time: 开始时间
        end_time: 结束时间
        service_name: 服务名称过滤
        format: 输出格式（json/text）
    
    Returns:
        报表数据
    """
    start_time, end_time = _parse_time_range()
    service_name = request.args.get('service_name')
    output_format = request.args.get('format', 'json')
    
    report = report_generator.generate_summary_report(start_time, end_time, service_name)
    
    if output_format == 'text':
        text_report = report_generator.export_to_text(report)
        response = make_response(text_report)
        response.headers['Content-Type'] = 'text/plain; charset=utf-8'
        response.headers['Content-Disposition'] = 'attachment; filename=report_summary.txt'
        return response
    
    return jsonify({
        'success': True,
        'data': report
    })


@report_bp.route('/detailed', methods=['GET'])
def get_detailed_report():
    """
    获取详细报表（包含日志列表）
    
    Query Parameters:
        同summary
        limit: 日志数量限制
    
    Returns:
        报表数据
    """
    start_time, end_time = _parse_time_range()
    service_name = request.args.get('service_name')
    limit = request.args.get('limit', 1000, type=int)
    output_format = request.args.get('format', 'json')
    
    report = report_generator.generate_detailed_report(
        start_time, end_time, service_name, limit
    )
    
    if output_format == 'text':
        text_report = report_generator.export_to_text(report)
        response = make_response(text_report)
        response.headers['Content-Type'] = 'text/plain; charset=utf-8'
        response.headers['Content-Disposition'] = 'attachment; filename=report_detailed.txt'
        return response
    
    return jsonify({
        'success': True,
        'data': report
    })


@report_bp.route('/export', methods=['GET'])
def export_report():
    """
    导出报表
    
    Query Parameters:
        type: 报表类型（summary/detailed/hourly/daily/weekly）
        hours: 小时数
        days: 天数
        service_name: 服务名称
        format: 导出格式（json/text）
        download: 是否下载（1/0）
    
    Returns:
        报表文件或数据
    """
    report_type = request.args.get('type', 'summary')
    output_format = request.args.get('format', 'json')
    service_name = request.args.get('service_name')
    as_download = request.args.get('download', '0') == '1'
    hours = request.args.get('hours', 24, type=int)
    
    if report_type == 'detailed':
        start_time, end_time = _parse_time_range()
        report = report_generator.generate_detailed_report(
            start_time, end_time, service_name
        )
        filename = 'detailed_report'
    elif report_type == 'hourly':
        report = report_generator.generate_hourly_report(hours, service_name)
        filename = 'hourly_report'
    elif report_type == 'daily':
        report = report_generator.generate_daily_report(service_name)
        filename = 'daily_report'
    elif report_type == 'weekly':
        report = report_generator.generate_weekly_report(service_name)
        filename = 'weekly_report'
    else:
        start_time, end_time = _parse_time_range()
        report = report_generator.generate_summary_report(
            start_time, end_time, service_name
        )
        filename = 'summary_report'
    
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    
    if output_format == 'text':
        content = report_generator.export_to_text(report)
        mimetype = 'text/plain; charset=utf-8'
        filename = f'{filename}_{timestamp}.txt'
    else:
        content = report_generator.export_to_json(report, pretty=True)
        mimetype = 'application/json; charset=utf-8'
        filename = f'{filename}_{timestamp}.json'
    
    response = make_response(content)
    response.headers['Content-Type'] = mimetype
    
    if as_download:
        response.headers['Content-Disposition'] = f'attachment; filename={filename}'
    
    return response


@report_bp.route('/daily', methods=['GET'])
def get_daily_report():
    """
    获取日报
    
    Query Parameters:
        service_name: 服务名称
        format: 输出格式
    
    Returns:
        日报数据
    """
    service_name = request.args.get('service_name')
    output_format = request.args.get('format', 'json')
    
    report = report_generator.generate_daily_report(service_name)
    
    if output_format == 'text':
        text_report = report_generator.export_to_text(report)
        response = make_response(text_report)
        response.headers['Content-Type'] = 'text/plain; charset=utf-8'
        return response
    
    return jsonify({
        'success': True,
        'data': report
    })


@report_bp.route('/weekly', methods=['GET'])
def get_weekly_report():
    """
    获取周报
    
    Query Parameters:
        service_name: 服务名称
        format: 输出格式
    
    Returns:
        周报数据
    """
    service_name = request.args.get('service_name')
    output_format = request.args.get('format', 'json')
    
    report = report_generator.generate_weekly_report(service_name)
    
    if output_format == 'text':
        text_report = report_generator.export_to_text(report)
        response = make_response(text_report)
        response.headers['Content-Type'] = 'text/plain; charset=utf-8'
        return response
    
    return jsonify({
        'success': True,
        'data': report
    })


@report_bp.route('/types', methods=['GET'])
def get_report_types():
    """
    获取支持的报表类型
    
    Returns:
        报表类型列表
    """
    return jsonify({
        'success': True,
        'data': {
            'types': [
                {
                    'id': 'summary',
                    'name': '汇总报表',
                    'description': '包含关键指标和趋势数据'
                },
                {
                    'id': 'detailed',
                    'name': '详细报表',
                    'description': '包含完整日志列表的详细报表'
                },
                {
                    'id': 'daily',
                    'name': '日报',
                    'description': '最近24小时的统计数据'
                },
                {
                    'id': 'weekly',
                    'name': '周报',
                    'description': '最近7天的统计数据'
                }
            ],
            'formats': ['json', 'text']
        }
    })
