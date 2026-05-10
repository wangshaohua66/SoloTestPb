# -*- coding: utf-8 -*-
"""
日志相关API路由
"""
import json
from flask import Blueprint, request, jsonify
from datetime import datetime, timedelta

from .. import db
from ..models import LogEntry

log_bp = Blueprint('log', __name__)


@log_bp.route('', methods=['GET'])
def get_logs():
    """
    获取日志列表
    
    Query Parameters:
        page: 页码（默认1）
        page_size: 每页数量（默认50）
        level: 日志级别过滤
        service_name: 服务名称过滤
        start_time: 开始时间（ISO格式）
        end_time: 结束时间（ISO格式）
    
    Returns:
        日志列表JSON
    """
    page = request.args.get('page', 1, type=int)
    page_size = min(request.args.get('page_size', 50, type=int), 500)
    level = request.args.get('level')
    service_name = request.args.get('service_name')
    start_time_str = request.args.get('start_time')
    end_time_str = request.args.get('end_time')
    
    query = LogEntry.query
    
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


@log_bp.route('/<int:log_id>', methods=['GET'])
def get_log_detail(log_id: int):
    """
    获取日志详情
    
    Args:
        log_id: 日志ID
    
    Returns:
        日志详情JSON
    """
    log = LogEntry.query.get_or_404(log_id)
    return jsonify({
        'success': True,
        'data': log.to_dict()
    })


@log_bp.route('', methods=['POST'])
def ingest_log():
    """
    接收单条日志（API方式）
    
    Request Body:
        日志数据，可以是：
        - 已解析的日志对象
        - 原始日志行字符串
        - JSON格式的日志
    
    Returns:
        处理结果JSON
    """
    data = request.get_json()
    
    if not data:
        return jsonify({'success': False, 'error': '无效的请求数据'}), 400
    
    from ..modules.log_parser import LogParser
    parser = LogParser()
    
    if isinstance(data, str):
        parsed = parser.parse(data)
    elif isinstance(data, dict):
        if 'message' in data and 'timestamp' not in data:
            log_line = data.get('raw_data', '') or json.dumps(data)
            parsed = parser.parse(log_line)
            for key in ['level', 'module', 'service_name', 'host', 'trace_id']:
                if data.get(key):
                    parsed[key] = data[key]
        else:
            parsed = data
    else:
        return jsonify({'success': False, 'error': '不支持的数据格式'}), 400
    
    timestamp = parsed.get('timestamp')
    if isinstance(timestamp, str):
        try:
            timestamp = datetime.fromisoformat(timestamp)
        except Exception:
            timestamp = datetime.utcnow()
    elif not timestamp:
        timestamp = datetime.utcnow()
    
    entry = LogEntry(
        timestamp=timestamp,
        level=parsed.get('level', 'INFO'),
        module=parsed.get('module'),
        message=parsed.get('message', ''),
        service_name=parsed.get('service_name'),
        host=parsed.get('host'),
        trace_id=parsed.get('trace_id'),
        raw_data=parsed.get('raw_data') or json.dumps(data, ensure_ascii=False),
        parsed=parsed.get('parsed', True)
    )
    
    db.session.add(entry)
    db.session.commit()
    
    return jsonify({
        'success': True,
        'data': {'id': entry.id}
    }), 201


@log_bp.route('/batch', methods=['POST'])
def ingest_batch_logs():
    """
    批量接收日志
    
    Request Body:
        logs: 日志列表
    
    Returns:
        处理结果JSON
    """
    data = request.get_json()
    logs_data = data.get('logs', []) if isinstance(data, dict) else []
    
    from ..modules.log_parser import LogParser
    parser = LogParser()
    
    count = 0
    for log_data in logs_data:
        try:
            if isinstance(log_data, str):
                parsed = parser.parse(log_data)
            else:
                parsed = log_data
            
            timestamp = parsed.get('timestamp')
            if isinstance(timestamp, str):
                try:
                    timestamp = datetime.fromisoformat(timestamp)
                except Exception:
                    timestamp = datetime.utcnow()
            elif not timestamp:
                timestamp = datetime.utcnow()
            
            entry = LogEntry(
                timestamp=timestamp,
                level=parsed.get('level', 'INFO'),
                module=parsed.get('module'),
                message=parsed.get('message', ''),
                service_name=parsed.get('service_name'),
                host=parsed.get('host'),
                trace_id=parsed.get('trace_id'),
                raw_data=parsed.get('raw_data') or (json.dumps(log_data, ensure_ascii=False) if isinstance(log_data, dict) else str(log_data)),
                parsed=parsed.get('parsed', True)
            )
            db.session.add(entry)
            count += 1
        except Exception:
            continue
    
    db.session.commit()
    
    return jsonify({
        'success': True,
        'data': {'ingested_count': count}
    }), 201


@log_bp.route('/levels', methods=['GET'])
def get_available_levels():
    """
    获取所有日志级别
    
    Returns:
        日志级别列表
    """
    levels = ['DEBUG', 'INFO', 'WARNING', 'ERROR', 'FATAL', 'TRACE']
    return jsonify({
        'success': True,
        'data': {'levels': levels}
    })


@log_bp.route('/services', methods=['GET'])
def get_available_services():
    """
    获取所有服务名称
    
    Returns:
        服务名称列表
    """
    query = db.session.query(
        LogEntry.service_name,
        db.func.count(LogEntry.id).label('count')
    ).filter(
        LogEntry.service_name.isnot(None)
    ).group_by(
        LogEntry.service_name
    ).all()
    
    services = [
        {'name': row[0] or 'unknown', 'count': row[1]}
        for row in query
    ]
    
    return jsonify({
        'success': True,
        'data': {'services': services}
    })
