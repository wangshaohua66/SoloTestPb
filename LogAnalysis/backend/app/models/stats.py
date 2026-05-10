# -*- coding: utf-8 -*-
"""
统计数据模型
"""
from datetime import datetime

from .. import db


class StatsRecord(db.Model):
    """
    统计记录模型
    存储预计算的日志统计数据，用于快速查询
    """
    
    __tablename__ = 'stats_records'
    
    id = db.Column(db.Integer, primary_key=True)
    
    stats_type = db.Column(db.String(50), nullable=False)
    time_window_start = db.Column(db.DateTime, nullable=False, index=True)
    time_window_end = db.Column(db.DateTime, nullable=False, index=True)
    
    service_name = db.Column(db.String(100), nullable=True)
    level = db.Column(db.String(20), nullable=True)
    module = db.Column(db.String(100), nullable=True)
    
    count_value = db.Column(db.Integer, default=0)
    avg_value = db.Column(db.Float, nullable=True)
    min_value = db.Column(db.Float, nullable=True)
    max_value = db.Column(db.Float, nullable=True)
    
    extra_data = db.Column(db.Text, nullable=True)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    __table_args__ = (
        db.Index('idx_stats_type_window', 'stats_type', 'time_window_start'),
        db.Index('idx_stats_service_window', 'service_name', 'time_window_start'),
    )
    
    def to_dict(self):
        """
        转换为字典格式
        
        Returns:
            字典形式的统计记录
        """
        import json
        
        extra = None
        if self.extra_data:
            try:
                extra = json.loads(self.extra_data)
            except Exception:
                extra = self.extra_data
        
        return {
            'id': self.id,
            'stats_type': self.stats_type,
            'time_window_start': self.time_window_start.isoformat() if self.time_window_start else None,
            'time_window_end': self.time_window_end.isoformat() if self.time_window_end else None,
            'service_name': self.service_name,
            'level': self.level,
            'module': self.module,
            'count_value': self.count_value,
            'avg_value': self.avg_value,
            'min_value': self.min_value,
            'max_value': self.max_value,
            'extra_data': extra,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
