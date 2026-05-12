# -*- coding: utf-8 -*-
"""
档案导出路由模块
提供修复档案的导出功能
"""

import logging
import json
from io import StringIO
from datetime import datetime
from flask import Blueprint, request, jsonify, make_response
from urllib.parse import quote
from app import db
from app.models import (
    Artifact, RepairPlan, RepairProcess, ImageRecord, Material, ExportHistory
)

export_bp = Blueprint('export', __name__)
logger = logging.getLogger(__name__)


@export_bp.route('/stats', methods=['GET'])
def get_stats():
    """
    获取系统统计数据
    用于首页显示统计信息
    
    返回:
        各模块统计数量的JSON响应
    """
    try:
        artifact_count = db.session.query(db.func.count(Artifact.id)).scalar()
        plan_count = db.session.query(db.func.count(RepairPlan.id)).scalar()
        process_count = db.session.query(db.func.count(RepairProcess.id)).scalar()
        image_count = db.session.query(db.func.count(ImageRecord.id)).scalar()
        material_count = db.session.query(db.func.count(Material.id)).scalar()
        
        logger.info('获取系统统计数据成功')
        
        return jsonify({
            'code': 200,
            'message': '获取成功',
            'data': {
                'artifacts': artifact_count or 0,
                'plans': plan_count or 0,
                'processes': process_count or 0,
                'images': image_count or 0,
                'materials': material_count or 0
            }
        })
    except Exception as e:
        logger.error(f'获取系统统计数据失败: {str(e)}')
        return jsonify({
            'code': 500,
            'message': '获取失败',
            'data': None
        }), 500


@export_bp.route('/artifact/<int:artifact_id>', methods=['GET'])
def export_artifact_report(artifact_id):
    """
    导出单个文物的完整修复档案报告
    支持txt和json格式
    
    参数:
        artifact_id: 文物ID
        format: 导出格式，txt或json
        
    返回:
        档案报告文件
    """
    try:
        format_type = request.args.get('format', 'txt')
        
        artifact = Artifact.query.get(artifact_id)
        
        if not artifact:
            logger.warning(f'文物不存在，ID: {artifact_id}')
            return jsonify({'code': 404, 'message': '文物不存在', 'data': None}), 404
        
        plans = RepairPlan.query.filter_by(artifact_id=artifact_id).order_by(
            RepairPlan.created_at.asc()
        ).all()
        
        processes = RepairProcess.query.filter_by(artifact_id=artifact_id).order_by(
            RepairProcess.record_time.asc()
        ).all()
        
        images = ImageRecord.query.filter_by(artifact_id=artifact_id).order_by(
            ImageRecord.created_at.asc()
        ).all()
        
        materials = Material.query.filter_by(artifact_id=artifact_id).order_by(
            Material.created_at.asc()
        ).all()
        
        if format_type == 'json':
            report = generate_artifact_report_json(
                artifact, plans, processes, images, materials
            )
            content_type = 'application/json; charset=utf-8'
            ext = 'json'
        else:
            report = generate_artifact_report(
                artifact, plans, processes, images, materials
            )
            content_type = 'text/plain; charset=utf-8'
            ext = 'txt'
        
        save_export_history([artifact], format_type)
        
        filename = f'repair_report_{artifact.id}_{datetime.now().strftime("%Y%m%d")}.{ext}'
        display_name = f'修复报告_{artifact.name}_{datetime.now().strftime("%Y%m%d")}.{ext}'
        encoded_name = quote(display_name, encoding='utf-8')
        
        response = make_response(report)
        response.headers['Content-Type'] = content_type
        response.headers['Content-Disposition'] = (
            f"attachment; filename=\"{filename}\"; filename*=UTF-8''{encoded_name}"
        )
        
        logger.info(f'导出文物修复报告成功，文物ID: {artifact_id}，格式: {format_type}')
        
        return response
    except Exception as e:
        logger.error(f'导出文物修复报告失败: {str(e)}')
        return jsonify({'code': 500, 'message': '导出失败', 'data': None}), 500


@export_bp.route('/batch', methods=['GET', 'POST'])
def export_batch():
    """
    批量导出多个文物的修复档案
    
    参数:
        ids: 文物ID列表，逗号分隔或JSON数组
        format: 导出格式，txt或json
        
    返回:
        合并的档案报告文件
    """
    try:
        if request.method == 'POST':
            data = request.get_json()
            artifact_ids = data.get('ids', [])
            format_type = data.get('format', 'txt')
        else:
            ids_param = request.args.get('ids', '')
            artifact_ids = [int(id) for id in ids_param.split(',') if id.strip()]
            format_type = request.args.get('format', 'txt')
        
        if not artifact_ids:
            return jsonify({'code': 400, 'message': '请选择要导出的文物', 'data': None}), 400
        
        artifacts = Artifact.query.filter(Artifact.id.in_(artifact_ids)).all()
        
        if not artifacts:
            return jsonify({'code': 404, 'message': '未找到指定的文物', 'data': None}), 404
        
        if format_type == 'json':
            report_data = []
            for artifact in artifacts:
                plans = RepairPlan.query.filter_by(artifact_id=artifact.id).order_by(
                    RepairPlan.created_at.asc()
                ).all()
                processes = RepairProcess.query.filter_by(artifact_id=artifact.id).order_by(
                    RepairProcess.record_time.asc()
                ).all()
                images = ImageRecord.query.filter_by(artifact_id=artifact.id).order_by(
                    ImageRecord.created_at.asc()
                ).all()
                materials = Material.query.filter_by(artifact_id=artifact.id).order_by(
                    Material.created_at.asc()
                ).all()
                report_data.append(generate_artifact_report_dict(
                    artifact, plans, processes, images, materials
                ))
            report = json.dumps(report_data, ensure_ascii=False, indent=2)
            content_type = 'application/json; charset=utf-8'
            ext = 'json'
        else:
            output = StringIO()
            for i, artifact in enumerate(artifacts, 1):
                plans = RepairPlan.query.filter_by(artifact_id=artifact.id).order_by(
                    RepairPlan.created_at.asc()
                ).all()
                processes = RepairProcess.query.filter_by(artifact_id=artifact.id).order_by(
                    RepairProcess.record_time.asc()
                ).all()
                images = ImageRecord.query.filter_by(artifact_id=artifact.id).order_by(
                    ImageRecord.created_at.asc()
                ).all()
                materials = Material.query.filter_by(artifact_id=artifact.id).order_by(
                    Material.created_at.asc()
                ).all()
                
                if i > 1:
                    output.write('\n\n')
                output.write(f'{"=" * 70}\n')
                output.write(f'                      文物 {i} - {artifact.name}\n')
                output.write(f'{"=" * 70}\n\n')
                output.write(generate_artifact_report(
                    artifact, plans, processes, images, materials
                ))
            
            report = output.getvalue()
            content_type = 'text/plain; charset=utf-8'
            ext = 'txt'
        
        save_export_history(artifacts, format_type)
        
        filename = f'repair_report_batch_{datetime.now().strftime("%Y%m%d%H%M%S")}.{ext}'
        display_name = f'批量修复报告_{datetime.now().strftime("%Y%m%d")}.{ext}'
        encoded_name = quote(display_name, encoding='utf-8')
        
        response = make_response(report)
        response.headers['Content-Type'] = content_type
        response.headers['Content-Disposition'] = (
            f"attachment; filename=\"{filename}\"; filename*=UTF-8''{encoded_name}"
        )
        
        logger.info(f'批量导出修复报告成功，共{len(artifacts)}个文物，格式: {format_type}')
        
        return response
    except Exception as e:
        logger.error(f'批量导出修复报告失败: {str(e)}')
        return jsonify({'code': 500, 'message': '导出失败', 'data': None}), 500


@export_bp.route('/history', methods=['GET'])
def export_history():
    """
    获取导出历史记录
    
    返回:
        导出历史记录列表的JSON响应
    """
    try:
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 10, type=int)
        
        query = ExportHistory.query.order_by(ExportHistory.created_at.desc())
        pagination = query.paginate(page=page, per_page=per_page, error_out=False)
        
        history_list = [h.to_dict() for h in pagination.items]
        
        logger.info(f'获取导出历史记录成功，共{pagination.total}条')
        
        return jsonify({
            'code': 200,
            'message': '获取成功',
            'data': {
                'items': history_list,
                'total': pagination.total,
                'page': page,
                'per_page': per_page,
                'pages': pagination.pages
            }
        })
    except Exception as e:
        logger.error(f'获取导出历史记录失败: {str(e)}')
        return jsonify({'code': 500, 'message': '获取失败', 'data': None}), 500


def save_export_history(artifacts, format_type):
    """
    保存导出历史记录
    
    参数:
        artifacts: 文物对象列表
        format_type: 导出格式
    """
    try:
        history = ExportHistory(
            artifact_ids=','.join([str(a.id) for a in artifacts]),
            artifact_names=','.join([a.name for a in artifacts]),
            format_type=format_type,
            count=len(artifacts)
        )
        db.session.add(history)
        db.session.commit()
    except Exception as e:
        logger.error(f'保存导出历史记录失败: {str(e)}')


def generate_artifact_report(artifact, plans, processes, images, materials):
    """
    生成文物修复档案报告文本内容
    
    参数:
        artifact: 文物对象
        plans: 修复计划列表
        processes: 修复过程列表
        images: 影像记录列表
        materials: 材料列表
        
    返回:
        格式化的报告文本
    """
    output = StringIO()
    
    output.write('=' * 70 + '\n')
    output.write('                      文物修复档案报告\n')
    output.write('=' * 70 + '\n\n')
    output.write(f'生成时间: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}\n\n')
    
    output.write('-' * 70 + '\n')
    output.write('【一】文物基本信息\n')
    output.write('-' * 70 + '\n\n')
    output.write(f'文物名称: {artifact.name}\n')
    output.write(f'年    代: {artifact.era or "-"}\n')
    output.write(f'类    别: {artifact.category or "-"}\n')
    output.write(f'尺    寸: {artifact.dimensions or "-"}\n')
    output.write(f'材    质: {artifact.material or "-"}\n')
    output.write(f'保存状态: {artifact.preservation_status or "-"}\n')
    output.write(f'病害描述: {artifact.disease_description or "-"}\n')
    output.write(f'建档时间: {artifact.created_at.strftime("%Y-%m-%d %H:%M:%S")}\n\n')
    
    output.write('-' * 70 + '\n')
    output.write('【二】修复计划\n')
    output.write('-' * 70 + '\n\n')
    
    if plans:
        for idx, plan in enumerate(plans, 1):
            output.write(f'>>> 计划 {idx}\n')
            output.write(f'修复目标: {plan.goal or "-"}\n')
            output.write(f'修复方法: {plan.method or "-"}\n')
            output.write(f'使用材料: {plan.materials or "-"}\n')
            output.write(f'预计工期: {plan.estimated_duration or "-"}\n')
            output.write(f'制定时间: {plan.created_at.strftime("%Y-%m-%d %H:%M:%S")}\n\n')
    else:
        output.write('暂无修复计划记录\n\n')
    
    output.write('-' * 70 + '\n')
    output.write('【三】修复过程记录\n')
    output.write('-' * 70 + '\n\n')
    
    if processes:
        for idx, process in enumerate(processes, 1):
            output.write(f'>>> 记录 {idx}\n')
            output.write(f'记录时间: {process.record_time.strftime("%Y-%m-%d %H:%M:%S")}\n')
            output.write(f'操作步骤: {process.operation_steps or "-"}\n')
            output.write(f'使用材料: {process.used_materials or "-"}\n')
            output.write(f'工具设备: {process.tools or "-"}\n')
            output.write(f'遇到问题: {process.problems or "-"}\n\n')
    else:
        output.write('暂无修复过程记录\n\n')
    
    output.write('-' * 70 + '\n')
    output.write('【四】影像资料\n')
    output.write('-' * 70 + '\n\n')
    
    stage_map = {'before': '修复前', 'during': '修复中', 'after': '修复后'}
    
    if images:
        for idx, image in enumerate(images, 1):
            output.write(f'>>> 影像 {idx}\n')
            output.write(f'阶    段: {stage_map.get(image.stage, image.stage)}\n')
            output.write(f'描    述: {image.description or "-"}\n')
            output.write(f'文件名称: {image.file_name or "-"}\n')
            output.write(f'记录时间: {image.created_at.strftime("%Y-%m-%d %H:%M:%S")}\n\n')
    else:
        output.write('暂无影像资料记录\n\n')
    
    output.write('-' * 70 + '\n')
    output.write('【五】材料使用记录\n')
    output.write('-' * 70 + '\n\n')
    
    if materials:
        for idx, material in enumerate(materials, 1):
            output.write(f'>>> 材料 {idx}\n')
            output.write(f'材料名称: {material.name}\n')
            output.write(f'材料来源: {material.source or "-"}\n')
            output.write(f'用    量: {material.usage or "-"}\n')
            output.write(f'备    注: {material.notes or "-"}\n')
            output.write(f'记录时间: {material.created_at.strftime("%Y-%m-%d %H:%M:%S")}\n\n')
    else:
        output.write('暂无材料使用记录\n\n')
    
    output.write('=' * 70 + '\n')
    output.write('                         报告结束\n')
    output.write('=' * 70 + '\n')
    
    return output.getvalue()


def generate_artifact_report_dict(artifact, plans, processes, images, materials):
    """
    生成文物修复档案报告字典格式
    
    参数:
        artifact: 文物对象
        plans: 修复计划列表
        processes: 修复过程列表
        images: 影像记录列表
        materials: 材料列表
        
    返回:
        字典格式的报告数据
    """
    stage_map = {'before': '修复前', 'during': '修复中', 'after': '修复后'}
    
    return {
        'artifact': artifact.to_dict(),
        'plans': [p.to_dict() for p in plans],
        'processes': [p.to_dict() for p in processes],
        'images': [{
            **i.to_dict(),
            'stage_label': stage_map.get(i.stage, i.stage)
        } for i in images],
        'materials': [m.to_dict() for m in materials]
    }


def generate_artifact_report_json(artifact, plans, processes, images, materials):
    """
    生成文物修复档案报告JSON内容
    
    参数:
        artifact: 文物对象
        plans: 修复计划列表
        processes: 修复过程列表
        images: 影像记录列表
        materials: 材料列表
        
    返回:
        JSON格式的报告内容
    """
    report_dict = generate_artifact_report_dict(
        artifact, plans, processes, images, materials
    )
    return json.dumps(report_dict, ensure_ascii=False, indent=2)


@export_bp.route('/list', methods=['GET'])
def export_list():
    """
    获取所有可导出的文物列表
    用于在前端选择要导出的文物
    
    返回:
        可导出文物列表的JSON响应
    """
    try:
        keyword = request.args.get('keyword', '')
        category = request.args.get('category', '')
        
        query = Artifact.query
        
        if keyword:
            query = query.filter(
                db.or_(
                    Artifact.name.like(f'%{keyword}%'),
                    Artifact.era.like(f'%{keyword}%'),
                    Artifact.category.like(f'%{keyword}%')
                )
            )
        if category:
            query = query.filter(Artifact.category.like(f'%{category}%'))
        
        artifacts = query.order_by(Artifact.created_at.desc()).all()
        artifacts_list = [{'id': a.id, 'name': a.name, 'era': a.era, 'category': a.category} for a in artifacts]
        
        logger.info(f'获取可导出文物列表成功，共{len(artifacts_list)}条')
        
        return jsonify({
            'code': 200,
            'message': '获取成功',
            'data': artifacts_list
        })
    except Exception as e:
        logger.error(f'获取可导出文物列表失败: {str(e)}')
        return jsonify({'code': 500, 'message': '获取失败', 'data': None}), 500
