# -*- coding: utf-8 -*-
"""
文物档案路由模块
提供文物档案的增删改查API接口
"""

import logging
from flask import Blueprint, request, jsonify
from app import db
from app.models import Artifact

artifacts_bp = Blueprint('artifacts', __name__)
logger = logging.getLogger(__name__)


@artifacts_bp.route('/', methods=['GET'])
def get_artifacts():
    """
    获取文物档案列表
    支持分页和关键词搜索
    
    返回:
        文物档案列表的JSON响应
    """
    try:
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 10, type=int)
        keyword = request.args.get('keyword', '', type=str)
        
        query = Artifact.query
        
        if keyword:
            query = query.filter(
                (Artifact.name.like(f'%{keyword}%')) |
                (Artifact.era.like(f'%{keyword}%')) |
                (Artifact.category.like(f'%{keyword}%'))
            )
        
        pagination = query.order_by(Artifact.created_at.desc()).paginate(
            page=page, per_page=per_page, error_out=False
        )
        
        artifacts = [artifact.to_dict() for artifact in pagination.items]
        
        logger.info(f'获取文物列表成功，共{len(artifacts)}条记录')
        
        return jsonify({
            'code': 200,
            'message': '获取成功',
            'data': {
                'items': artifacts,
                'total': pagination.total,
                'page': page,
                'per_page': per_page,
                'pages': pagination.pages
            }
        })
    except Exception as e:
        logger.error(f'获取文物列表失败: {str(e)}')
        return jsonify({'code': 500, 'message': '获取失败', 'data': None}), 500


@artifacts_bp.route('/<int:artifact_id>', methods=['GET'])
def get_artifact(artifact_id):
    """
    获取单个文物档案详情
    
    参数:
        artifact_id: 文物ID
        
    返回:
        文物档案详情的JSON响应
    """
    try:
        artifact = Artifact.query.get(artifact_id)
        
        if not artifact:
            logger.warning(f'文物不存在，ID: {artifact_id}')
            return jsonify({'code': 404, 'message': '文物不存在', 'data': None}), 404
        
        logger.info(f'获取文物详情成功，ID: {artifact_id}')
        
        return jsonify({
            'code': 200,
            'message': '获取成功',
            'data': artifact.to_dict()
        })
    except Exception as e:
        logger.error(f'获取文物详情失败: {str(e)}')
        return jsonify({'code': 500, 'message': '获取失败', 'data': None}), 500


@artifacts_bp.route('/', methods=['POST'])
def create_artifact():
    """
    创建新的文物档案
    
    返回:
        创建结果的JSON响应
    """
    try:
        data = request.get_json()
        
        if not data or 'name' not in data:
            return jsonify({'code': 400, 'message': '文物名称不能为空', 'data': None}), 400
        
        artifact = Artifact(
            name=data.get('name'),
            era=data.get('era'),
            category=data.get('category'),
            dimensions=data.get('dimensions'),
            material=data.get('material'),
            preservation_status=data.get('preservation_status'),
            disease_description=data.get('disease_description')
        )
        
        db.session.add(artifact)
        db.session.commit()
        
        logger.info(f'创建文物档案成功，ID: {artifact.id}')
        
        return jsonify({
            'code': 200,
            'message': '创建成功',
            'data': artifact.to_dict()
        })
    except Exception as e:
        db.session.rollback()
        logger.error(f'创建文物档案失败: {str(e)}')
        return jsonify({'code': 500, 'message': '创建失败', 'data': None}), 500


@artifacts_bp.route('/<int:artifact_id>', methods=['PUT'])
def update_artifact(artifact_id):
    """
    更新文物档案信息
    
    参数:
        artifact_id: 文物ID
        
    返回:
        更新结果的JSON响应
    """
    try:
        artifact = Artifact.query.get(artifact_id)
        
        if not artifact:
            logger.warning(f'文物不存在，ID: {artifact_id}')
            return jsonify({'code': 404, 'message': '文物不存在', 'data': None}), 404
        
        data = request.get_json()
        
        if data.get('name'):
            artifact.name = data.get('name')
        if data.get('era') is not None:
            artifact.era = data.get('era')
        if data.get('category') is not None:
            artifact.category = data.get('category')
        if data.get('dimensions') is not None:
            artifact.dimensions = data.get('dimensions')
        if data.get('material') is not None:
            artifact.material = data.get('material')
        if data.get('preservation_status') is not None:
            artifact.preservation_status = data.get('preservation_status')
        if data.get('disease_description') is not None:
            artifact.disease_description = data.get('disease_description')
        
        db.session.commit()
        
        logger.info(f'更新文物档案成功，ID: {artifact_id}')
        
        return jsonify({
            'code': 200,
            'message': '更新成功',
            'data': artifact.to_dict()
        })
    except Exception as e:
        db.session.rollback()
        logger.error(f'更新文物档案失败: {str(e)}')
        return jsonify({'code': 500, 'message': '更新失败', 'data': None}), 500


@artifacts_bp.route('/<int:artifact_id>', methods=['DELETE'])
def delete_artifact(artifact_id):
    """
    删除文物档案
    
    参数:
        artifact_id: 文物ID
        
    返回:
        删除结果的JSON响应
    """
    try:
        artifact = Artifact.query.get(artifact_id)
        
        if not artifact:
            logger.warning(f'文物不存在，ID: {artifact_id}')
            return jsonify({'code': 404, 'message': '文物不存在', 'data': None}), 404
        
        db.session.delete(artifact)
        db.session.commit()
        
        logger.info(f'删除文物档案成功，ID: {artifact_id}')
        
        return jsonify({
            'code': 200,
            'message': '删除成功',
            'data': None
        })
    except Exception as e:
        db.session.rollback()
        logger.error(f'删除文物档案失败: {str(e)}')
        return jsonify({'code': 500, 'message': '删除失败', 'data': None}), 500
