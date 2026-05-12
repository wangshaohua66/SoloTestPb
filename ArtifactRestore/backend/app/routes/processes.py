# -*- coding: utf-8 -*-
"""
修复过程路由模块
提供修复过程记录的增删改查API接口
"""

import logging
from datetime import datetime
from flask import Blueprint, request, jsonify
from app import db
from app.models import RepairProcess, Artifact

processes_bp = Blueprint('processes', __name__)
logger = logging.getLogger(__name__)


@processes_bp.route('/', methods=['GET'])
def get_processes():
    """
    获取修复过程记录列表
    支持按文物ID筛选
    
    返回:
        修复过程记录列表的JSON响应
    """
    try:
        artifact_id = request.args.get('artifact_id', type=int)
        
        query = RepairProcess.query
        
        if artifact_id:
            query = query.filter_by(artifact_id=artifact_id)
        
        processes = query.order_by(RepairProcess.record_time.desc()).all()
        processes_list = [process.to_dict() for process in processes]
        
        logger.info(f'获取修复过程列表成功，共{len(processes_list)}条记录')
        
        return jsonify({
            'code': 200,
            'message': '获取成功',
            'data': processes_list
        })
    except Exception as e:
        logger.error(f'获取修复过程列表失败: {str(e)}')
        return jsonify({'code': 500, 'message': '获取失败', 'data': None}), 500


@processes_bp.route('/<int:process_id>', methods=['GET'])
def get_process(process_id):
    """
    获取单个修复过程记录详情
    
    参数:
        process_id: 修复过程记录ID
        
    返回:
        修复过程记录详情的JSON响应
    """
    try:
        process = RepairProcess.query.get(process_id)
        
        if not process:
            logger.warning(f'修复过程记录不存在，ID: {process_id}')
            return jsonify({'code': 404, 'message': '修复过程记录不存在', 'data': None}), 404
        
        logger.info(f'获取修复过程详情成功，ID: {process_id}')
        
        return jsonify({
            'code': 200,
            'message': '获取成功',
            'data': process.to_dict()
        })
    except Exception as e:
        logger.error(f'获取修复过程详情失败: {str(e)}')
        return jsonify({'code': 500, 'message': '获取失败', 'data': None}), 500


@processes_bp.route('/', methods=['POST'])
def create_process():
    """
    创建新的修复过程记录
    
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
        
        record_time = data.get('record_time')
        if record_time:
            try:
                record_time = datetime.strptime(record_time, '%Y-%m-%d %H:%M:%S')
            except ValueError:
                record_time = datetime.utcnow()
        else:
            record_time = datetime.utcnow()
        
        process = RepairProcess(
            artifact_id=data.get('artifact_id'),
            operation_steps=data.get('operation_steps'),
            used_materials=data.get('used_materials'),
            tools=data.get('tools'),
            problems=data.get('problems'),
            record_time=record_time
        )
        
        db.session.add(process)
        db.session.commit()
        
        logger.info(f'创建修复过程记录成功，ID: {process.id}')
        
        return jsonify({
            'code': 200,
            'message': '创建成功',
            'data': process.to_dict()
        })
    except Exception as e:
        db.session.rollback()
        logger.error(f'创建修复过程记录失败: {str(e)}')
        return jsonify({'code': 500, 'message': '创建失败', 'data': None}), 500


@processes_bp.route('/<int:process_id>', methods=['PUT'])
def update_process(process_id):
    """
    更新修复过程记录信息
    
    参数:
        process_id: 修复过程记录ID
        
    返回:
        更新结果的JSON响应
    """
    try:
        process = RepairProcess.query.get(process_id)
        
        if not process:
            logger.warning(f'修复过程记录不存在，ID: {process_id}')
            return jsonify({'code': 404, 'message': '修复过程记录不存在', 'data': None}), 404
        
        data = request.get_json()
        
        if data.get('operation_steps') is not None:
            process.operation_steps = data.get('operation_steps')
        if data.get('used_materials') is not None:
            process.used_materials = data.get('used_materials')
        if data.get('tools') is not None:
            process.tools = data.get('tools')
        if data.get('problems') is not None:
            process.problems = data.get('problems')
        if data.get('record_time'):
            try:
                process.record_time = datetime.strptime(
                    data.get('record_time'), '%Y-%m-%d %H:%M:%S'
                )
            except ValueError:
                pass
        
        db.session.commit()
        
        logger.info(f'更新修复过程记录成功，ID: {process_id}')
        
        return jsonify({
            'code': 200,
            'message': '更新成功',
            'data': process.to_dict()
        })
    except Exception as e:
        db.session.rollback()
        logger.error(f'更新修复过程记录失败: {str(e)}')
        return jsonify({'code': 500, 'message': '更新失败', 'data': None}), 500


@processes_bp.route('/<int:process_id>', methods=['DELETE'])
def delete_process(process_id):
    """
    删除修复过程记录
    
    参数:
        process_id: 修复过程记录ID
        
    返回:
        删除结果的JSON响应
    """
    try:
        process = RepairProcess.query.get(process_id)
        
        if not process:
            logger.warning(f'修复过程记录不存在，ID: {process_id}')
            return jsonify({'code': 404, 'message': '修复过程记录不存在', 'data': None}), 404
        
        db.session.delete(process)
        db.session.commit()
        
        logger.info(f'删除修复过程记录成功，ID: {process_id}')
        
        return jsonify({
            'code': 200,
            'message': '删除成功',
            'data': None
        })
    except Exception as e:
        db.session.rollback()
        logger.error(f'删除修复过程记录失败: {str(e)}')
        return jsonify({'code': 500, 'message': '删除失败', 'data': None}), 500
