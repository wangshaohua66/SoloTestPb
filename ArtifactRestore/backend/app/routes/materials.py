# -*- coding: utf-8 -*-
"""
材料管理路由模块
提供修复材料的增删改查API接口
"""

import logging
from flask import Blueprint, request, jsonify
from app import db
from app.models import Material, Artifact

materials_bp = Blueprint('materials', __name__)
logger = logging.getLogger(__name__)


@materials_bp.route('/', methods=['GET'])
def get_materials():
    """
    获取修复材料列表
    支持按文物ID筛选
    
    返回:
        修复材料列表的JSON响应
    """
    try:
        artifact_id = request.args.get('artifact_id', type=int)
        
        query = Material.query
        
        if artifact_id:
            query = query.filter_by(artifact_id=artifact_id)
        
        materials = query.order_by(Material.created_at.desc()).all()
        materials_list = [material.to_dict() for material in materials]
        
        logger.info(f'获取材料列表成功，共{len(materials_list)}条记录')
        
        return jsonify({
            'code': 200,
            'message': '获取成功',
            'data': materials_list
        })
    except Exception as e:
        logger.error(f'获取材料列表失败: {str(e)}')
        return jsonify({'code': 500, 'message': '获取失败', 'data': None}), 500


@materials_bp.route('/<int:material_id>', methods=['GET'])
def get_material(material_id):
    """
    获取单个材料详情
    
    参数:
        material_id: 材料ID
        
    返回:
        材料详情的JSON响应
    """
    try:
        material = Material.query.get(material_id)
        
        if not material:
            logger.warning(f'材料记录不存在，ID: {material_id}')
            return jsonify({'code': 404, 'message': '材料记录不存在', 'data': None}), 404
        
        logger.info(f'获取材料详情成功，ID: {material_id}')
        
        return jsonify({
            'code': 200,
            'message': '获取成功',
            'data': material.to_dict()
        })
    except Exception as e:
        logger.error(f'获取材料详情失败: {str(e)}')
        return jsonify({'code': 500, 'message': '获取失败', 'data': None}), 500


@materials_bp.route('/', methods=['POST'])
def create_material():
    """
    创建新的材料记录
    
    返回:
        创建结果的JSON响应
    """
    try:
        data = request.get_json()
        
        if not data or 'artifact_id' not in data or 'name' not in data:
            return jsonify({'code': 400, 'message': '文物ID和材料名称不能为空', 'data': None}), 400
        
        artifact = Artifact.query.get(data.get('artifact_id'))
        if not artifact:
            return jsonify({'code': 404, 'message': '关联的文物不存在', 'data': None}), 404
        
        material = Material(
            artifact_id=data.get('artifact_id'),
            name=data.get('name'),
            source=data.get('source'),
            usage=data.get('usage'),
            notes=data.get('notes')
        )
        
        db.session.add(material)
        db.session.commit()
        
        logger.info(f'创建材料记录成功，ID: {material.id}')
        
        return jsonify({
            'code': 200,
            'message': '创建成功',
            'data': material.to_dict()
        })
    except Exception as e:
        db.session.rollback()
        logger.error(f'创建材料记录失败: {str(e)}')
        return jsonify({'code': 500, 'message': '创建失败', 'data': None}), 500


@materials_bp.route('/<int:material_id>', methods=['PUT'])
def update_material(material_id):
    """
    更新材料记录信息
    
    参数:
        material_id: 材料ID
        
    返回:
        更新结果的JSON响应
    """
    try:
        material = Material.query.get(material_id)
        
        if not material:
            logger.warning(f'材料记录不存在，ID: {material_id}')
            return jsonify({'code': 404, 'message': '材料记录不存在', 'data': None}), 404
        
        data = request.get_json()
        
        if data.get('name') is not None:
            material.name = data.get('name')
        if data.get('source') is not None:
            material.source = data.get('source')
        if data.get('usage') is not None:
            material.usage = data.get('usage')
        if data.get('notes') is not None:
            material.notes = data.get('notes')
        
        db.session.commit()
        
        logger.info(f'更新材料记录成功，ID: {material_id}')
        
        return jsonify({
            'code': 200,
            'message': '更新成功',
            'data': material.to_dict()
        })
    except Exception as e:
        db.session.rollback()
        logger.error(f'更新材料记录失败: {str(e)}')
        return jsonify({'code': 500, 'message': '更新失败', 'data': None}), 500


@materials_bp.route('/<int:material_id>', methods=['DELETE'])
def delete_material(material_id):
    """
    删除材料记录
    
    参数:
        material_id: 材料ID
        
    返回:
        删除结果的JSON响应
    """
    try:
        material = Material.query.get(material_id)
        
        if not material:
            logger.warning(f'材料记录不存在，ID: {material_id}')
            return jsonify({'code': 404, 'message': '材料记录不存在', 'data': None}), 404
        
        db.session.delete(material)
        db.session.commit()
        
        logger.info(f'删除材料记录成功，ID: {material_id}')
        
        return jsonify({
            'code': 200,
            'message': '删除成功',
            'data': None
        })
    except Exception as e:
        db.session.rollback()
        logger.error(f'删除材料记录失败: {str(e)}')
        return jsonify({'code': 500, 'message': '删除失败', 'data': None}), 500
