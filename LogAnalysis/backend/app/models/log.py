# -*- coding: utf-8 -*-
"""
日志相关数据库模型
"""
from datetime import datetime

from .. import db


class LogSource(db.Model):
    """
    日志来源模型
    存储日志收集的来源配置
    """
    
    __tablename__ = 'log_sources'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False, unique=True)
    source_type = db.Column(db.String(50), nullable=False)
    config = db.Column(db.Text, nullable=True)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_collected_at = db.Column(db.DateTime, nullable=True)
    
    logs = db.relationship('LogEntry', backref='source', lazy=True)
    
    def to_dict(self):
        """
        转换为字典格式
        
        Returns:
            字典形式的日志来源信息
        """
        return {
            'id': self.id,
            'name': self.name,
            'source_type': self.source_type,
            'config': self.config,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'last_collected_at': self.last_collected_at.isoformat() if self.last_collected_at else None
        }


class LogEntry(db.Model):
    """
    日志条目模型
    存储解析后的日志数据
    """
    
    __tablename__ = 'log_entries'
    
    id = db.Column(db.Integer, primary_key=True)
    source_id = db.Column(db.Integer, db.ForeignKey('log_sources.id'), nullable=True)
    
    timestamp = db.Column(db.DateTime, nullable=False, index=True)
    level = db.Column(db.String(20), nullable=False, default='INFO')
    module = db.Column(db.String(100), nullable=True)
    message = db.Column(db.Text, nullable=False)
    
    service_name = db.Column(db.String(100), nullable=True)
    host = db.Column(db.String(100), nullable=True)
    trace_id = db.Column(db.String(100), nullable=True)
    
    raw_data = db.Column(db.Text, nullable=True)
    parsed = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    
    __table_args__ = (
        db.Index('idx_log_timestamp_level', 'timestamp', 'level'),
        db.Index('idx_log_service_timestamp', 'service_name', 'timestamp'),
    )
    
    def to_dict(self):
        """
        转换为字典格式
        
        Returns:
            字典形式的日志条目
        """
        return {
            'id': self.id,
            'source_id': self.source_id,
            'timestamp': self.timestamp.isoformat() if self.timestamp else None,
            'level': self.level,
            'module': self.module,
            'message': self.message,
            'service_name': self.service_name,
            'host': self.host,
            'trace_id': self.trace_id,
            'raw_data': self.raw_data,
            'parsed': self.parsed,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }


class ParseRule(db.Model):
    """
    日志解析规则模型
    存储用户定义的日志解析规则
    """
    
    __tablename__ = 'parse_rules'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False, unique=True)
    pattern = db.Column(db.Text, nullable=False)
    format_description = db.Column(db.Text, nullable=True)
    is_active = db.Column(db.Boolean, default=True)
    priority = db.Column(db.Integer, default=10)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        """
        转换为字典格式
        
        Returns:
            字典形式的解析规则
        """
        return {
            'id': self.id,
            'name': self.name,
            'pattern': self.pattern,
            'format_description': self.format_description,
            'is_active': self.is_active,
            'priority': self.priority,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
