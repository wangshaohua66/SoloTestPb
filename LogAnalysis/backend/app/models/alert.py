# -*- coding: utf-8 -*-
"""
告警相关数据库模型
"""
from datetime import datetime

from .. import db


class AlertRule(db.Model):
    """
    告警规则模型
    存储用户定义的告警检测规则
    """
    
    __tablename__ = 'alert_rules'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False, unique=True)
    
    condition_type = db.Column(db.String(50), nullable=False)
    condition_value = db.Column(db.Text, nullable=False)
    
    level = db.Column(db.String(20), default='WARNING')
    description = db.Column(db.Text, nullable=True)
    
    is_active = db.Column(db.Boolean, default=True)
    check_interval = db.Column(db.Integer, default=60)
    last_checked_at = db.Column(db.DateTime, nullable=True)
    
    notify_methods = db.Column(db.Text, nullable=True)
    notify_targets = db.Column(db.Text, nullable=True)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    alerts = db.relationship('Alert', backref='rule', lazy=True)
    
    def to_dict(self):
        """
        转换为字典格式
        
        Returns:
            字典形式的告警规则
        """
        return {
            'id': self.id,
            'name': self.name,
            'condition_type': self.condition_type,
            'condition_value': self.condition_value,
            'level': self.level,
            'description': self.description,
            'is_active': self.is_active,
            'check_interval': self.check_interval,
            'last_checked_at': self.last_checked_at.isoformat() if self.last_checked_at else None,
            'notify_methods': self.notify_methods,
            'notify_targets': self.notify_targets,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }


class Alert(db.Model):
    """
    告警实例模型
    存储触发的告警记录
    """
    
    __tablename__ = 'alerts'
    
    id = db.Column(db.Integer, primary_key=True)
    rule_id = db.Column(db.Integer, db.ForeignKey('alert_rules.id'), nullable=True)
    
    title = db.Column(db.String(200), nullable=False)
    message = db.Column(db.Text, nullable=True)
    level = db.Column(db.String(20), default='WARNING')
    
    is_acknowledged = db.Column(db.Boolean, default=False)
    acknowledged_at = db.Column(db.DateTime, nullable=True)
    acknowledged_by = db.Column(db.String(100), nullable=True)
    
    is_resolved = db.Column(db.Boolean, default=False)
    resolved_at = db.Column(db.DateTime, nullable=True)
    resolved_note = db.Column(db.Text, nullable=True)
    
    trigger_count = db.Column(db.Integer, default=1)
    first_triggered_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_triggered_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    logs = db.Column(db.Text, nullable=True)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    
    __table_args__ = (
        db.Index('idx_alert_created', 'created_at'),
        db.Index('idx_alert_level_resolved', 'level', 'is_resolved'),
    )
    
    def to_dict(self):
        """
        转换为字典格式
        
        Returns:
            字典形式的告警实例
        """
        return {
            'id': self.id,
            'rule_id': self.rule_id,
            'title': self.title,
            'message': self.message,
            'level': self.level,
            'is_acknowledged': self.is_acknowledged,
            'acknowledged_at': self.acknowledged_at.isoformat() if self.acknowledged_at else None,
            'acknowledged_by': self.acknowledged_by,
            'is_resolved': self.is_resolved,
            'resolved_at': self.resolved_at.isoformat() if self.resolved_at else None,
            'resolved_note': self.resolved_note,
            'trigger_count': self.trigger_count,
            'first_triggered_at': self.first_triggered_at.isoformat() if self.first_triggered_at else None,
            'last_triggered_at': self.last_triggered_at.isoformat() if self.last_triggered_at else None,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
