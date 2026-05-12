# -*- coding: utf-8 -*-
"""
数据库模型模块
定义所有数据库表的ORM模型
"""

from datetime import datetime
from app import db


class Artifact(db.Model):
    """
    文物档案模型
    存储文物的基本信息
    """
    
    __tablename__ = 'artifacts'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(100), nullable=False, comment='文物名称')
    era = db.Column(db.String(50), comment='年代')
    category = db.Column(db.String(50), comment='类别')
    dimensions = db.Column(db.String(200), comment='尺寸')
    material = db.Column(db.String(200), comment='材质')
    preservation_status = db.Column(db.Text, comment='保存状态')
    disease_description = db.Column(db.Text, comment='病害描述')
    created_at = db.Column(db.DateTime, default=datetime.utcnow, comment='创建时间')
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, comment='更新时间')
    
    plans = db.relationship('RepairPlan', backref='artifact', lazy=True, cascade='all, delete-orphan')
    processes = db.relationship('RepairProcess', backref='artifact', lazy=True, cascade='all, delete-orphan')
    images = db.relationship('ImageRecord', backref='artifact', lazy=True, cascade='all, delete-orphan')
    
    def to_dict(self):
        """
        将模型对象转换为字典格式
        用于API响应
        
        返回:
            包含对象属性的字典
        """
        return {
            'id': self.id,
            'name': self.name,
            'era': self.era,
            'category': self.category,
            'dimensions': self.dimensions,
            'material': self.material,
            'preservation_status': self.preservation_status,
            'disease_description': self.disease_description,
            'created_at': self.created_at.strftime('%Y-%m-%d %H:%M:%S') if self.created_at else None,
            'updated_at': self.updated_at.strftime('%Y-%m-%d %H:%M:%S') if self.updated_at else None
        }


class RepairPlan(db.Model):
    """
    修复计划模型
    存储文物修复方案的信息
    """
    
    __tablename__ = 'repair_plans'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    artifact_id = db.Column(db.Integer, db.ForeignKey('artifacts.id'), nullable=False, comment='关联文物ID')
    goal = db.Column(db.Text, comment='修复目标')
    method = db.Column(db.Text, comment='修复方法')
    materials = db.Column(db.Text, comment='使用材料')
    estimated_duration = db.Column(db.String(100), comment='预计工期')
    created_at = db.Column(db.DateTime, default=datetime.utcnow, comment='创建时间')
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, comment='更新时间')
    
    def to_dict(self):
        """
        将模型对象转换为字典格式
        用于API响应
        
        返回:
            包含对象属性的字典
        """
        return {
            'id': self.id,
            'artifact_id': self.artifact_id,
            'goal': self.goal,
            'method': self.method,
            'materials': self.materials,
            'estimated_duration': self.estimated_duration,
            'created_at': self.created_at.strftime('%Y-%m-%d %H:%M:%S') if self.created_at else None,
            'updated_at': self.updated_at.strftime('%Y-%m-%d %H:%M:%S') if self.updated_at else None
        }


class RepairProcess(db.Model):
    """
    修复过程记录模型
    按时间顺序记录修复过程的详细信息
    """
    
    __tablename__ = 'repair_processes'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    artifact_id = db.Column(db.Integer, db.ForeignKey('artifacts.id'), nullable=False, comment='关联文物ID')
    operation_steps = db.Column(db.Text, comment='操作步骤')
    used_materials = db.Column(db.Text, comment='使用材料')
    tools = db.Column(db.Text, comment='工具设备')
    problems = db.Column(db.Text, comment='遇到问题')
    record_time = db.Column(db.DateTime, default=datetime.utcnow, comment='记录时间')
    created_at = db.Column(db.DateTime, default=datetime.utcnow, comment='创建时间')
    
    def to_dict(self):
        """
        将模型对象转换为字典格式
        用于API响应
        
        返回:
            包含对象属性的字典
        """
        return {
            'id': self.id,
            'artifact_id': self.artifact_id,
            'operation_steps': self.operation_steps,
            'used_materials': self.used_materials,
            'tools': self.tools,
            'problems': self.problems,
            'record_time': self.record_time.strftime('%Y-%m-%d %H:%M:%S') if self.record_time else None,
            'created_at': self.created_at.strftime('%Y-%m-%d %H:%M:%S') if self.created_at else None
        }


class ImageRecord(db.Model):
    """
    影像记录模型
    存储修复前后的影像资料信息
    """
    
    __tablename__ = 'image_records'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    artifact_id = db.Column(db.Integer, db.ForeignKey('artifacts.id'), nullable=False, comment='关联文物ID')
    stage = db.Column(db.String(20), nullable=False, comment='阶段：before/during/after')
    description = db.Column(db.Text, comment='影像描述')
    file_path = db.Column(db.String(300), comment='文件路径')
    file_name = db.Column(db.String(200), comment='文件名称')
    created_at = db.Column(db.DateTime, default=datetime.utcnow, comment='创建时间')
    
    def to_dict(self):
        """
        将模型对象转换为字典格式
        用于API响应
        
        返回:
            包含对象属性的字典
        """
        return {
            'id': self.id,
            'artifact_id': self.artifact_id,
            'stage': self.stage,
            'description': self.description,
            'file_path': self.file_path,
            'file_name': self.file_name,
            'created_at': self.created_at.strftime('%Y-%m-%d %H:%M:%S') if self.created_at else None
        }


class Material(db.Model):
    """
    修复材料模型
    存储修复使用的材料信息
    """
    
    __tablename__ = 'materials'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    artifact_id = db.Column(db.Integer, db.ForeignKey('artifacts.id'), nullable=False, comment='关联文物ID')
    name = db.Column(db.String(100), nullable=False, comment='材料名称')
    source = db.Column(db.String(200), comment='材料来源')
    usage = db.Column(db.String(100), comment='用量')
    notes = db.Column(db.Text, comment='备注')
    created_at = db.Column(db.DateTime, default=datetime.utcnow, comment='创建时间')
    
    def to_dict(self):
        """
        将模型对象转换为字典格式
        用于API响应
        
        返回:
            包含对象属性的字典
        """
        return {
            'id': self.id,
            'artifact_id': self.artifact_id,
            'name': self.name,
            'source': self.source,
            'usage': self.usage,
            'notes': self.notes,
            'created_at': self.created_at.strftime('%Y-%m-%d %H:%M:%S') if self.created_at else None
        }


class ExportHistory(db.Model):
    """
    导出历史记录模型
    存储档案导出的历史记录
    """
    
    __tablename__ = 'export_history'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    artifact_ids = db.Column(db.Text, comment='导出的文物ID列表，逗号分隔')
    artifact_names = db.Column(db.Text, comment='导出的文物名称列表，逗号分隔')
    format_type = db.Column(db.String(20), default='txt', comment='导出格式：txt/json')
    count = db.Column(db.Integer, default=1, comment='导出数量')
    created_at = db.Column(db.DateTime, default=datetime.utcnow, comment='创建时间')
    
    def to_dict(self):
        """
        将模型对象转换为字典格式
        用于API响应
        
        返回:
            包含对象属性的字典
        """
        return {
            'id': self.id,
            'artifact_ids': self.artifact_ids,
            'artifact_names': self.artifact_names,
            'format_type': self.format_type,
            'count': self.count,
            'created_at': self.created_at.strftime('%Y-%m-%d %H:%M:%S') if self.created_at else None
        }
