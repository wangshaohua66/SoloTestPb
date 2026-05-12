# -*- coding: utf-8 -*-
"""
日志收集相关API路由
"""
import os
import json
from flask import Blueprint, request, jsonify

from .. import db
from ..models import LogSource, ParseRule
from ..modules.log_collector import collector_manager

collect_bp = Blueprint('collect', __name__)


def _parse_config(source):
    """
    解析日志来源配置
    
    Args:
        source: LogSource对象
    
    Returns:
        配置字典
    """
    if not source.config:
        return {}
    try:
        return json.loads(source.config)
    except Exception:
        return {}


def _start_collector(source):
    """
    启动日志收集器
    
    Args:
        source: LogSource对象
    
    Returns:
        是否启动成功
    """
    try:
        config = _parse_config(source)
        source_id = str(source.id)
        
        if source.source_type == 'file':
            file_path = config.get('file_path')
            if file_path:
                return collector_manager.start_file_collector(source_id, file_path)
        elif source.source_type == 'network':
            port = config.get('port', 9999)
            protocol = config.get('protocol', 'tcp')
            host = config.get('host', '0.0.0.0')
            return collector_manager.start_network_collector(source_id, host, port, protocol)
        
        return False
    except Exception as e:
        print(f"启动收集器失败: {e}")
        return False


def _stop_collector(source):
    """
    停止日志收集器
    
    Args:
        source: LogSource对象
    
    Returns:
        是否停止成功
    """
    try:
        return collector_manager.stop_collector(str(source.id))
    except Exception as e:
        print(f"停止收集器失败: {e}")
        return False


@collect_bp.route('/sources', methods=['GET'])
def get_log_sources():
    """
    获取日志来源配置列表
    
    Returns:
        日志来源列表JSON
    """
    sources = LogSource.query.order_by(LogSource.id.desc()).all()
    
    return jsonify({
        'success': True,
        'data': {'sources': [source.to_dict() for source in sources]}
    })


@collect_bp.route('/sources', methods=['POST'])
def create_log_source():
    """
    创建日志来源配置
    
    Request Body:
        name: 来源名称
        source_type: 来源类型（file/network/api）
        config: 配置信息（JSON字符串或对象）
        is_active: 是否激活
    
    Returns:
        创建结果JSON
    """
    data = request.get_json() or {}
    
    if not data.get('name') or not data.get('source_type'):
        return jsonify({
            'success': False,
            'error': '缺少必要参数：name 或 source_type'
        }), 400
    
    existing = LogSource.query.filter_by(name=data['name']).first()
    if existing:
        return jsonify({
            'success': False,
            'error': f'日志来源已存在: {data["name"]}'
        }), 409
    
    source_type = data['source_type']
    config = data.get('config')
    is_active = data.get('is_active', True)
    
    if source_type == 'file':
        if not config or not config.get('file_path'):
            return jsonify({
                'success': False,
                'error': '文件来源需要指定 file_path'
            }), 400
        file_path = config.get('file_path')
        if not os.path.exists(file_path):
            return jsonify({
                'success': False,
                'error': f'文件不存在: {file_path}'
            }), 400
    elif source_type == 'network':
        if not config or not config.get('port'):
            return jsonify({
                'success': False,
                'error': '网络来源需要指定 port'
            }), 400
    
    source = LogSource(
        name=data['name'],
        source_type=source_type,
        config=json.dumps(config, ensure_ascii=False) if config else None,
        is_active=is_active
    )
    
    db.session.add(source)
    db.session.commit()
    
    if is_active and source_type in ['file', 'network']:
        _start_collector(source)
    
    return jsonify({
        'success': True,
        'data': {'source': source.to_dict()}
    }), 201


@collect_bp.route('/sources/<int:source_id>', methods=['GET'])
def get_log_source_detail(source_id: int):
    """
    获取日志来源详情
    
    Args:
        source_id: 来源ID
    
    Returns:
        来源详情JSON
    """
    source = LogSource.query.get_or_404(source_id)
    return jsonify({
        'success': True,
        'data': {'source': source.to_dict()}
    })


@collect_bp.route('/sources/<int:source_id>', methods=['PUT'])
def update_log_source(source_id: int):
    """
    更新日志来源配置
    
    Args:
        source_id: 来源ID
    
    Returns:
        更新结果JSON
    """
    source = LogSource.query.get_or_404(source_id)
    data = request.get_json() or {}
    
    if 'name' in data:
        source.name = data['name']
    if 'source_type' in data:
        source.source_type = data['source_type']
    if 'config' in data:
        config = data['config']
        source.config = json.dumps(config, ensure_ascii=False) if config else None
    if 'is_active' in data:
        source.is_active = data['is_active']
    
    db.session.commit()
    
    return jsonify({
        'success': True,
        'data': {'source': source.to_dict()}
    })


@collect_bp.route('/sources/<int:source_id>', methods=['DELETE'])
def delete_log_source(source_id: int):
    """
    删除日志来源配置
    
    Args:
        source_id: 来源ID
    
    Returns:
        删除结果JSON
    """
    source = LogSource.query.get_or_404(source_id)
    
    _stop_collector(source)
    
    db.session.delete(source)
    db.session.commit()
    
    return jsonify({'success': True})


@collect_bp.route('/sources/<int:source_id>/toggle', methods=['POST'])
def toggle_log_source(source_id: int):
    """
    切换日志来源激活状态
    
    Args:
        source_id: 来源ID
    
    Returns:
        切换结果JSON
    """
    source = LogSource.query.get_or_404(source_id)
    source.is_active = not source.is_active
    
    if source.is_active:
        _start_collector(source)
    else:
        _stop_collector(source)
    
    db.session.commit()
    
    return jsonify({
        'success': True,
        'data': {'is_active': source.is_active}
    })


@collect_bp.route('/parse-rules', methods=['GET'])
def get_parse_rules():
    """
    获取解析规则列表
    
    Returns:
        解析规则列表JSON
    """
    rules = ParseRule.query.order_by(ParseRule.priority, ParseRule.id).all()
    
    return jsonify({
        'success': True,
        'data': {'rules': [rule.to_dict() for rule in rules]}
    })


@collect_bp.route('/parse-rules', methods=['POST'])
def create_parse_rule():
    """
    创建解析规则
    
    Request Body:
        name: 规则名称
        pattern: 正则表达式
        format_description: 格式描述
        is_active: 是否激活
        priority: 优先级（越小越优先）
    
    Returns:
        创建结果JSON
    """
    import re
    
    data = request.get_json() or {}
    
    if not data.get('name') or not data.get('pattern'):
        return jsonify({
            'success': False,
            'error': '缺少必要参数：name 或 pattern'
        }), 400
    
    try:
        re.compile(data['pattern'])
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'正则表达式无效: {e}'
        }), 400
    
    existing = ParseRule.query.filter_by(name=data['name']).first()
    if existing:
        return jsonify({
            'success': False,
            'error': f'解析规则已存在: {data["name"]}'
        }), 409
    
    rule = ParseRule(
        name=data['name'],
        pattern=data['pattern'],
        format_description=data.get('format_description'),
        is_active=data.get('is_active', True),
        priority=data.get('priority', 10)
    )
    
    db.session.add(rule)
    db.session.commit()
    
    return jsonify({
        'success': True,
        'data': {'rule': rule.to_dict()}
    }), 201


@collect_bp.route('/parse-rules/<int:rule_id>', methods=['PUT'])
def update_parse_rule(rule_id: int):
    """
    更新解析规则
    
    Args:
        rule_id: 规则ID
    
    Returns:
        更新结果JSON
    """
    import re
    
    rule = ParseRule.query.get_or_404(rule_id)
    data = request.get_json() or {}
    
    if 'pattern' in data:
        try:
            re.compile(data['pattern'])
        except Exception as e:
            return jsonify({
                'success': False,
                'error': f'正则表达式无效: {e}'
            }), 400
    
    if 'name' in data:
        rule.name = data['name']
    if 'pattern' in data:
        rule.pattern = data['pattern']
    if 'format_description' in data:
        rule.format_description = data['format_description']
    if 'is_active' in data:
        rule.is_active = data['is_active']
    if 'priority' in data:
        rule.priority = data['priority']
    
    db.session.commit()
    
    return jsonify({
        'success': True,
        'data': {'rule': rule.to_dict()}
    })


@collect_bp.route('/parse-rules/<int:rule_id>', methods=['DELETE'])
def delete_parse_rule(rule_id: int):
    """
    删除解析规则
    
    Args:
        rule_id: 规则ID
    
    Returns:
        删除结果JSON
    """
    rule = ParseRule.query.get_or_404(rule_id)
    
    db.session.delete(rule)
    db.session.commit()
    
    return jsonify({'success': True})


@collect_bp.route('/test-parse', methods=['POST'])
def test_parse():
    """
    测试日志解析
    
    Request Body:
        log_line: 日志行
        pattern: 可选的自定义正则表达式
    
    Returns:
        解析结果JSON
    """
    from ..modules.log_parser import LogParser
    import re
    
    data = request.get_json() or {}
    log_line = data.get('log_line', '')
    custom_pattern = data.get('pattern')
    
    parser = LogParser()
    
    if custom_pattern:
        try:
            regex = re.compile(custom_pattern)
            match = regex.match(log_line)
            if match:
                groups = match.groupdict()
                return jsonify({
                    'success': True,
                    'data': {
                        'matched': True,
                        'groups': groups,
                        'log_line': log_line
                    }
                })
            else:
                return jsonify({
                    'success': True,
                    'data': {
                        'matched': False,
                        'log_line': log_line,
                        'message': '正则表达式不匹配'
                    }
                })
        except Exception as e:
            return jsonify({
                'success': False,
                'error': f'正则表达式无效: {e}'
            }), 400
    
    parsed = parser.parse(log_line)
    detected_format = parser.detect_format(log_line)
    
    return jsonify({
        'success': True,
        'data': {
            'log_line': log_line,
            'detected_format': detected_format,
            'parsed': parsed
        }
    })


@collect_bp.route('/source-types', methods=['GET'])
def get_source_types():
    """
    获取支持的日志来源类型
    
    Returns:
        来源类型列表JSON
    """
    return jsonify({
        'success': True,
        'data': {
            'types': [
                {
                    'id': 'file',
                    'name': '文件',
                    'description': '从日志文件实时收集',
                    'required_config': ['file_path']
                },
                {
                    'id': 'network',
                    'name': '网络端口',
                    'description': '通过TCP/UDP端口接收日志',
                    'required_config': ['port', 'protocol']
                },
                {
                    'id': 'api',
                    'name': 'API',
                    'description': '通过HTTP API接收日志',
                    'required_config': []
                }
            ]
        }
    })
