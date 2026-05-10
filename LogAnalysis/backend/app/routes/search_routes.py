# -*- coding: utf-8 -*-
"""
日志搜索API路由
"""
import json
from flask import Blueprint, request, jsonify
from datetime import datetime

from .. import db
from ..models import LogEntry

search_bp = Blueprint('search', __name__)


@search_bp.route('', methods=['GET', 'POST'])
def search_logs():
    """
    搜索日志
    支持关键词搜索、时间范围过滤、多条件组合查询
    
    Query Parameters:
        keyword: 搜索关键词
        level: 日志级别过滤
        service_name: 服务名称过滤
        module: 模块过滤
        start_time: 开始时间（ISO格式）
        end_time: 结束时间（ISO格式）
        page: 页码
        page_size: 每页数量
    
    Returns:
        搜索结果JSON
    """
    if request.method == 'POST':
        data = request.get_json() or {}
    else:
        data = {
            'keyword': request.args.get('keyword'),
            'level': request.args.get('level'),
            'service_name': request.args.get('service_name'),
            'module': request.args.get('module'),
            'start_time': request.args.get('start_time'),
            'end_time': request.args.get('end_time'),
            'conditions': request.args.getlist('conditions')
        }
    
    keyword = data.get('keyword')
    level = data.get('level')
    service_name = data.get('service_name')
    module = data.get('module')
    start_time_str = data.get('start_time')
    end_time_str = data.get('end_time')
    conditions = data.get('conditions', [])
    
    page = data.get('page', 1) if isinstance(data, dict) else 1
    page_size = min(data.get('page_size', 50), 500) if isinstance(data, dict) else 50
    
    try:
        page = int(page)
        page_size = int(page_size)
    except Exception:
        page = 1
        page_size = 50
    
    query = LogEntry.query
    
    if keyword:
        search_pattern = f'%{keyword}%'
        query = query.filter(
            db.or_(
                LogEntry.message.like(search_pattern),
                LogEntry.raw_data.like(search_pattern)
            )
        )
    
    if level:
        if isinstance(level, list):
            query = query.filter(LogEntry.level.in_(level))
        else:
            query = query.filter(LogEntry.level == level)
    
    if service_name:
        query = query.filter(LogEntry.service_name == service_name)
    
    if module:
        query = query.filter(LogEntry.module == module)
    
    if start_time_str:
        try:
            start_time = datetime.fromisoformat(start_time_str)
            query = query.filter(LogEntry.timestamp >= start_time)
        except Exception:
            pass
    
    if end_time_str:
        try:
            end_time = datetime.fromisoformat(end_time_str)
            query = query.filter(LogEntry.timestamp <= end_time)
        except Exception:
            pass
    
    if conditions and isinstance(conditions, list):
        for cond in conditions:
            if isinstance(cond, dict):
                field = cond.get('field')
                op = cond.get('op', 'eq')
                value = cond.get('value')
                
                if field == 'message' and value:
                    if op == 'contains':
                        query = query.filter(LogEntry.message.like(f'%{value}%'))
                elif field == 'level' and value:
                    if op == 'eq':
                        query = query.filter(LogEntry.level == value)
                    elif op == 'in' and isinstance(value, list):
                        query = query.filter(LogEntry.level.in_(value))
                elif field == 'service_name' and value:
                    query = query.filter(LogEntry.service_name == value)
    
    pagination = query.order_by(
        LogEntry.timestamp.desc()
    ).paginate(page=page, per_page=page_size, error_out=False)
    
    logs = [log.to_dict() for log in pagination.items]
    
    return jsonify({
        'success': True,
        'data': {
            'logs': logs,
            'pagination': {
                'page': page,
                'page_size': page_size,
                'total': pagination.total,
                'pages': pagination.pages
            }
        }
    })


@search_bp.route('/count', methods=['GET', 'POST'])
def count_logs():
    """
    统计符合条件的日志数量
    
    Returns:
        统计结果JSON
    """
    if request.method == 'POST':
        data = request.get_json() or {}
    else:
        data = {
            'keyword': request.args.get('keyword'),
            'level': request.args.get('level'),
            'service_name': request.args.get('service_name'),
            'start_time': request.args.get('start_time'),
            'end_time': request.args.get('end_time')
        }
    
    keyword = data.get('keyword')
    level = data.get('level')
    service_name = data.get('service_name')
    start_time_str = data.get('start_time')
    end_time_str = data.get('end_time')
    
    query = db.session.query(db.func.count(LogEntry.id))
    
    if keyword:
        search_pattern = f'%{keyword}%'
        query = query.filter(
            db.or_(
                LogEntry.message.like(search_pattern),
                LogEntry.raw_data.like(search_pattern)
            )
        )
    
    if level:
        query = query.filter(LogEntry.level == level)
    if service_name:
        query = query.filter(LogEntry.service_name == service_name)
    
    if start_time_str:
        try:
            start_time = datetime.fromisoformat(start_time_str)
            query = query.filter(LogEntry.timestamp >= start_time)
        except Exception:
            pass
    
    if end_time_str:
        try:
            end_time = datetime.fromisoformat(end_time_str)
            query = query.filter(LogEntry.timestamp <= end_time)
        except Exception:
            pass
    
    count = query.scalar() or 0
    
    return jsonify({
        'success': True,
        'data': {'count': count}
    })


@search_bp.route('/stats', methods=['GET'])
def search_stats():
    """
    获取搜索结果的统计信息
    
    Query Parameters:
        keyword: 搜索关键词
        start_time: 开始时间
        end_time: 结束时间
    
    Returns:
        统计信息JSON
    """
    keyword = request.args.get('keyword')
    start_time_str = request.args.get('start_time')
    end_time_str = request.args.get('end_time')
    
    query = db.session.query(
        LogEntry.level,
        db.func.count(LogEntry.id).label('count')
    )
    
    if keyword:
        search_pattern = f'%{keyword}%'
        query = query.filter(
            db.or_(
                LogEntry.message.like(search_pattern),
                LogEntry.raw_data.like(search_pattern)
            )
        )
    
    if start_time_str:
        try:
            start_time = datetime.fromisoformat(start_time_str)
            query = query.filter(LogEntry.timestamp >= start_time)
        except Exception:
            pass
    
    if end_time_str:
        try:
            end_time = datetime.fromisoformat(end_time_str)
            query = query.filter(LogEntry.timestamp <= end_time)
        except Exception:
            pass
    
    query = query.group_by(LogEntry.level).all()
    
    level_stats = {}
    total = 0
    for row in query:
        level_stats[row[0]] = int(row[1])
        total += int(row[1])
    
    return jsonify({
        'success': True,
        'data': {
            'total': total,
            'by_level': level_stats
        }
    })
