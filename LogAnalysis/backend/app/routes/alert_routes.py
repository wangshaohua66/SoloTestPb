# -*- coding: utf-8 -*-
"""
告警相关API路由
"""
import json
from flask import Blueprint, request, jsonify
from datetime import datetime, timedelta

from .. import db
from ..models import Alert, AlertRule

alert_bp = Blueprint('alert', __name__)


@alert_bp.route('/rules', methods=['GET'])
def get_alert_rules():
    """
    获取告警规则列表
    
    Query Parameters:
        is_active: 是否只获取激活的规则
    
    Returns:
        告警规则列表JSON
    """
    is_active = request.args.get('is_active')
    
    query = AlertRule.query
    
    if is_active is not None:
        is_active_bool = is_active.lower() == 'true'
        query = query.filter_by(is_active=is_active_bool)
    
    rules = query.order_by(AlertRule.id.desc()).all()
    
    return jsonify({
        'success': True,
        'data': {'rules': [rule.to_dict() for rule in rules]}
    })


@alert_bp.route('/rules', methods=['POST'])
def create_alert_rule():
    """
    创建告警规则
    
    Request Body:
        name: 规则名称
        condition_type: 条件类型（keyword/level_threshold/error_rate/custom_query）
        condition_value: 条件值（字典）
        level: 告警级别
        description: 描述
        check_interval: 检查间隔（秒）
        is_active: 是否激活
    
    Returns:
        创建结果JSON
    """
    data = request.get_json()
    
    if not data or not data.get('name') or not data.get('condition_type'):
        return jsonify({
            'success': False,
            'error': '缺少必要参数：name 或 condition_type'
        }), 400
    
    condition_value = data.get('condition_value')
    if not condition_value:
        return jsonify({
            'success': False,
            'error': '缺少必要参数：condition_value'
        }), 400
    
    if isinstance(condition_value, str):
        try:
            condition_value = json.loads(condition_value)
        except Exception:
            return jsonify({
                'success': False,
                'error': 'condition_value 必须是有效的JSON'
            }), 400
    
    existing = AlertRule.query.filter_by(name=data['name']).first()
    if existing:
        return jsonify({
            'success': False,
            'error': f'告警规则已存在: {data["name"]}'
        }), 409
    
    rule = AlertRule(
        name=data['name'],
        condition_type=data['condition_type'],
        condition_value=json.dumps(condition_value, ensure_ascii=False),
        level=data.get('level', 'WARNING'),
        description=data.get('description'),
        check_interval=data.get('check_interval', 60),
        is_active=data.get('is_active', True)
    )
    
    db.session.add(rule)
    db.session.commit()
    
    return jsonify({
        'success': True,
        'data': {'rule': rule.to_dict()}
    }), 201


@alert_bp.route('/rules/<int:rule_id>', methods=['GET'])
def get_alert_rule_detail(rule_id: int):
    """
    获取告警规则详情
    
    Args:
        rule_id: 规则ID
    
    Returns:
        告警规则详情JSON
    """
    rule = AlertRule.query.get_or_404(rule_id)
    return jsonify({
        'success': True,
        'data': {'rule': rule.to_dict()}
    })


@alert_bp.route('/rules/<int:rule_id>', methods=['PUT'])
def update_alert_rule(rule_id: int):
    """
    更新告警规则
    
    Args:
        rule_id: 规则ID
    
    Returns:
        更新结果JSON
    """
    rule = AlertRule.query.get_or_404(rule_id)
    data = request.get_json() or {}
    
    if 'name' in data:
        rule.name = data['name']
    if 'condition_type' in data:
        rule.condition_type = data['condition_type']
    if 'condition_value' in data:
        cond = data['condition_value']
        if isinstance(cond, dict):
            rule.condition_value = json.dumps(cond, ensure_ascii=False)
        else:
            rule.condition_value = cond
    if 'level' in data:
        rule.level = data['level']
    if 'description' in data:
        rule.description = data['description']
    if 'check_interval' in data:
        rule.check_interval = data['check_interval']
    if 'is_active' in data:
        rule.is_active = data['is_active']
    
    db.session.commit()
    
    return jsonify({
        'success': True,
        'data': {'rule': rule.to_dict()}
    })


@alert_bp.route('/rules/<int:rule_id>', methods=['DELETE'])
def delete_alert_rule(rule_id: int):
    """
    删除告警规则
    
    Args:
        rule_id: 规则ID
    
    Returns:
        删除结果JSON
    """
    rule = AlertRule.query.get_or_404(rule_id)
    
    db.session.delete(rule)
    db.session.commit()
    
    return jsonify({'success': True})


@alert_bp.route('/rules/<int:rule_id>/toggle', methods=['POST'])
def toggle_alert_rule(rule_id: int):
    """
    切换告警规则激活状态
    
    Args:
        rule_id: 规则ID
    
    Returns:
        切换结果JSON
    """
    rule = AlertRule.query.get_or_404(rule_id)
    rule.is_active = not rule.is_active
    db.session.commit()
    
    return jsonify({
        'success': True,
        'data': {'is_active': rule.is_active}
    })


@alert_bp.route('', methods=['GET'])
def get_alerts():
    """
    获取告警列表
    
    Query Parameters:
        is_resolved: 是否已解决
        is_acknowledged: 是否已确认
        level: 告警级别
        page: 页码
        page_size: 每页数量
    
    Returns:
        告警列表JSON
    """
    is_resolved = request.args.get('is_resolved')
    is_acknowledged = request.args.get('is_acknowledged')
    level = request.args.get('level')
    page = request.args.get('page', 1, type=int)
    page_size = min(request.args.get('page_size', 50, type=int), 200)
    
    query = Alert.query
    
    if is_resolved is not None:
        resolved = is_resolved.lower() == 'true'
        query = query.filter_by(is_resolved=resolved)
    
    if is_acknowledged is not None:
        acked = is_acknowledged.lower() == 'true'
        query = query.filter_by(is_acknowledged=acked)
    
    if level:
        query = query.filter_by(level=level)
    
    pagination = query.order_by(
        Alert.created_at.desc()
    ).paginate(page=page, per_page=page_size, error_out=False)
    
    alerts = [alert.to_dict() for alert in pagination.items]
    
    return jsonify({
        'success': True,
        'data': {
            'alerts': alerts,
            'pagination': {
                'page': page,
                'page_size': page_size,
                'total': pagination.total,
                'pages': pagination.pages
            }
        }
    })


@alert_bp.route('/<int:alert_id>', methods=['GET'])
def get_alert_detail(alert_id: int):
    """
    获取告警详情
    
    Args:
        alert_id: 告警ID
    
    Returns:
        告警详情JSON
    """
    alert = Alert.query.get_or_404(alert_id)
    return jsonify({
        'success': True,
        'data': {'alert': alert.to_dict()}
    })


@alert_bp.route('/<int:alert_id>/acknowledge', methods=['POST'])
def acknowledge_alert(alert_id: int):
    """
    确认告警
    
    Args:
        alert_id: 告警ID
    
    Returns:
        确认结果JSON
    """
    alert = Alert.query.get_or_404(alert_id)
    
    data = request.get_json() or {}
    acknowledged_by = data.get('acknowledged_by', 'admin')
    
    alert.is_acknowledged = True
    alert.acknowledged_at = datetime.utcnow()
    alert.acknowledged_by = acknowledged_by
    
    db.session.commit()
    
    return jsonify({
        'success': True,
        'data': {'alert': alert.to_dict()}
    })


@alert_bp.route('/<int:alert_id>/resolve', methods=['POST'])
def resolve_alert(alert_id: int):
    """
    解决告警
    
    Args:
        alert_id: 告警ID
    
    Returns:
        解决结果JSON
    """
    alert = Alert.query.get_or_404(alert_id)
    
    data = request.get_json() or {}
    resolved_note = data.get('resolved_note')
    
    alert.is_resolved = True
    alert.resolved_at = datetime.utcnow()
    alert.resolved_note = resolved_note
    
    db.session.commit()
    
    return jsonify({
        'success': True,
        'data': {'alert': alert.to_dict()}
    })


@alert_bp.route('/stats', methods=['GET'])
def get_alert_stats():
    """
    获取告警统计
    
    Returns:
        告警统计JSON
    """
    hours = request.args.get('hours', 24, type=int)
    start_time = datetime.utcnow() - timedelta(hours=hours)
    
    total = Alert.query.filter(Alert.created_at >= start_time).count()
    active = Alert.query.filter(
        Alert.created_at >= start_time,
        Alert.is_resolved == False
    ).count()
    unacknowledged = Alert.query.filter(
        Alert.created_at >= start_time,
        Alert.is_acknowledged == False
    ).count()
    
    level_stats = db.session.query(
        Alert.level,
        db.func.count(Alert.id).label('count')
    ).filter(
        Alert.created_at >= start_time
    ).group_by(Alert.level).all()
    
    by_level = {}
    for row in level_stats:
        by_level[row[0]] = int(row[1])
    
    return jsonify({
        'success': True,
        'data': {
            'time_range': {
                'hours': hours,
                'start': start_time.isoformat(),
                'end': datetime.utcnow().isoformat()
            },
            'total': total,
            'active': active,
            'unacknowledged': unacknowledged,
            'by_level': by_level
        }
    })
