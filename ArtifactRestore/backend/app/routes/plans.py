# -*- coding: utf-8 -*-
"""
修复计划路由模块
提供修复计划的增删改查API接口
"""

import logging
from flask import Blueprint, request, jsonify
from app import db
from app.models import RepairPlan, Artifact

plans_bp = Blueprint('plans', __name__)
logger = logging.getLogger(__name__)


@plans_bp.route('/', methods=['GET'])
def get_plans():
    """
    获取修复计划列表
    支持按文物ID筛选
    
    返回:
        修复计划列表的JSON响应
    """
    try:
        artifact_id = request.args.get('artifact_id', type=int)
        
        query = RepairPlan.query
        
        if artifact_id:
            query = query.filter_by(artifact_id=artifact_id)
        
        plans = query.order_by(RepairPlan.created_at.desc()).all()
        plans_list = [plan.to_dict() for plan in plans]
        
        logger.info(f'获取修复计划列表成功，共{len(plans_list)}条记录')
        
        return jsonify({
            'code': 200,
            'message': '获取成功',
            'data': plans_list
        })
    except Exception as e:
        logger.error(f'获取修复计划列表失败: {str(e)}')
        return jsonify({'code': 500, 'message': '获取失败', 'data': None}), 500


@plans_bp.route('/<int:plan_id>', methods=['GET'])
def get_plan(plan_id):
    """
    获取单个修复计划详情
    
    参数:
        plan_id: 修复计划ID
        
    返回:
        修复计划详情的JSON响应
    """
    try:
        plan = RepairPlan.query.get(plan_id)
        
        if not plan:
            logger.warning(f'修复计划不存在，ID: {plan_id}')
            return jsonify({'code': 404, 'message': '修复计划不存在', 'data': None}), 404
        
        logger.info(f'获取修复计划详情成功，ID: {plan_id}')
        
        return jsonify({
            'code': 200,
            'message': '获取成功',
            'data': plan.to_dict()
        })
    except Exception as e:
        logger.error(f'获取修复计划详情失败: {str(e)}')
        return jsonify({'code': 500, 'message': '获取失败', 'data': None}), 500


@plans_bp.route('/', methods=['POST'])
def create_plan():
    """
    创建新的修复计划
    
    返回:
        创建结果的JSON响应
    """
    try:
        data = request.get_json()
        
        if not data or 'artifact_id' not in data:
            return jsonify({'code': 400, 'message': '文物ID不能为空', 'data': None}), 400
        
        artifact = Artifact.query.get(data.get('artifact_id'))
        if not artifact:
            return jsonify({'code': 404, 'message': '关联的文物不存在', 'data': None}), 404
        
        plan = RepairPlan(
            artifact_id=data.get('artifact_id'),
            goal=data.get('goal'),
            method=data.get('method'),
            materials=data.get('materials'),
            estimated_duration=data.get('estimated_duration')
        )
        
        db.session.add(plan)
        db.session.commit()
        
        logger.info(f'创建修复计划成功，ID: {plan.id}')
        
        return jsonify({
            'code': 200,
            'message': '创建成功',
            'data': plan.to_dict()
        })
    except Exception as e:
        db.session.rollback()
        logger.error(f'创建修复计划失败: {str(e)}')
        return jsonify({'code': 500, 'message': '创建失败', 'data': None}), 500


@plans_bp.route('/<int:plan_id>', methods=['PUT'])
def update_plan(plan_id):
    """
    更新修复计划信息
    
    参数:
        plan_id: 修复计划ID
        
    返回:
        更新结果的JSON响应
    """
    try:
        plan = RepairPlan.query.get(plan_id)
        
        if not plan:
            logger.warning(f'修复计划不存在，ID: {plan_id}')
            return jsonify({'code': 404, 'message': '修复计划不存在', 'data': None}), 404
        
        data = request.get_json()
        
        if data.get('goal') is not None:
            plan.goal = data.get('goal')
        if data.get('method') is not None:
            plan.method = data.get('method')
        if data.get('materials') is not None:
            plan.materials = data.get('materials')
        if data.get('estimated_duration') is not None:
            plan.estimated_duration = data.get('estimated_duration')
        
        db.session.commit()
        
        logger.info(f'更新修复计划成功，ID: {plan_id}')
        
        return jsonify({
            'code': 200,
            'message': '更新成功',
            'data': plan.to_dict()
        })
    except Exception as e:
        db.session.rollback()
        logger.error(f'更新修复计划失败: {str(e)}')
        return jsonify({'code': 500, 'message': '更新失败', 'data': None}), 500


@plans_bp.route('/<int:plan_id>', methods=['DELETE'])
def delete_plan(plan_id):
    """
    删除修复计划
    
    参数:
        plan_id: 修复计划ID
        
    返回:
        删除结果的JSON响应
    """
    try:
        plan = RepairPlan.query.get(plan_id)
        
        if not plan:
            logger.warning(f'修复计划不存在，ID: {plan_id}')
            return jsonify({'code': 404, 'message': '修复计划不存在', 'data': None}), 404
        
        db.session.delete(plan)
        db.session.commit()
        
        logger.info(f'删除修复计划成功，ID: {plan_id}')
        
        return jsonify({
            'code': 200,
            'message': '删除成功',
            'data': None
        })
    except Exception as e:
        db.session.rollback()
        logger.error(f'删除修复计划失败: {str(e)}')
        return jsonify({'code': 500, 'message': '删除失败', 'data': None}), 500
