# -*- coding: utf-8 -*-
"""
影像管理路由模块
提供影像记录的增删改查API接口
"""

import os
import logging
import uuid
from flask import Blueprint, request, jsonify, current_app, send_from_directory
from werkzeug.utils import secure_filename
from app import db
from app.models import ImageRecord, Artifact

images_bp = Blueprint('images', __name__)
logger = logging.getLogger(__name__)

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'bmp'}


def allowed_file(filename):
    """
    检查文件类型是否允许上传
    
    参数:
        filename: 文件名
        
    返回:
        是否允许上传的布尔值
    """
    return '.' in filename and \
        filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@images_bp.route('/', methods=['GET'])
def get_images():
    """
    获取影像记录列表
    支持按文物ID和阶段筛选
    
    返回:
        影像记录列表的JSON响应
    """
    try:
        artifact_id = request.args.get('artifact_id', type=int)
        stage = request.args.get('stage', type=str)
        
        query = ImageRecord.query
        
        if artifact_id:
            query = query.filter_by(artifact_id=artifact_id)
        if stage:
            query = query.filter_by(stage=stage)
        
        images = query.order_by(ImageRecord.created_at.desc()).all()
        images_list = [image.to_dict() for image in images]
        
        logger.info(f'获取影像列表成功，共{len(images_list)}条记录')
        
        return jsonify({
            'code': 200,
            'message': '获取成功',
            'data': images_list
        })
    except Exception as e:
        logger.error(f'获取影像列表失败: {str(e)}')
        return jsonify({'code': 500, 'message': '获取失败', 'data': None}), 500


@images_bp.route('/<int:image_id>', methods=['GET'])
def get_image(image_id):
    """
    获取单个影像记录详情
    
    参数:
        image_id: 影像记录ID
        
    返回:
        影像记录详情的JSON响应
    """
    try:
        image = ImageRecord.query.get(image_id)
        
        if not image:
            logger.warning(f'影像记录不存在，ID: {image_id}')
            return jsonify({'code': 404, 'message': '影像记录不存在', 'data': None}), 404
        
        logger.info(f'获取影像详情成功，ID: {image_id}')
        
        return jsonify({
            'code': 200,
            'message': '获取成功',
            'data': image.to_dict()
        })
    except Exception as e:
        logger.error(f'获取影像详情失败: {str(e)}')
        return jsonify({'code': 500, 'message': '获取失败', 'data': None}), 500


@images_bp.route('/', methods=['POST'])
def create_image():
    """
    创建新的影像记录
    支持上传文件和仅记录描述两种方式
    
    返回:
        创建结果的JSON响应
    """
    try:
        artifact_id = request.form.get('artifact_id', type=int)
        stage = request.form.get('stage')
        description = request.form.get('description')
        
        if not artifact_id or not stage:
            return jsonify({'code': 400, 'message': '文物ID和阶段不能为空', 'data': None}), 400
        
        artifact = Artifact.query.get(artifact_id)
        if not artifact:
            return jsonify({'code': 404, 'message': '关联的文物不存在', 'data': None}), 404
        
        if stage not in ['before', 'during', 'after']:
            return jsonify({'code': 400, 'message': '阶段参数无效', 'data': None}), 400
        
        file_path = None
        file_name = None
        
        if 'file' in request.files:
            file = request.files['file']
            if file and file.filename:
                if allowed_file(file.filename):
                    upload_folder = current_app.config['UPLOAD_FOLDER']
                    if not os.path.exists(upload_folder):
                        os.makedirs(upload_folder)
                    
                    ext = file.filename.rsplit('.', 1)[1].lower()
                    new_filename = f'{uuid.uuid4().hex}.{ext}'
                    save_path = os.path.join(upload_folder, new_filename)
                    file.save(save_path)
                    
                    file_path = f'/static/images/{new_filename}'
                    file_name = secure_filename(file.filename)
                else:
                    return jsonify({'code': 400, 'message': '不支持的文件类型', 'data': None}), 400
        
        image = ImageRecord(
            artifact_id=artifact_id,
            stage=stage,
            description=description,
            file_path=file_path,
            file_name=file_name
        )
        
        db.session.add(image)
        db.session.commit()
        
        logger.info(f'创建影像记录成功，ID: {image.id}')
        
        return jsonify({
            'code': 200,
            'message': '创建成功',
            'data': image.to_dict()
        })
    except Exception as e:
        db.session.rollback()
        logger.error(f'创建影像记录失败: {str(e)}')
        return jsonify({'code': 500, 'message': '创建失败', 'data': None}), 500


@images_bp.route('/<int:image_id>', methods=['PUT'])
def update_image(image_id):
    """
    更新影像记录信息
    
    参数:
        image_id: 影像记录ID
        
    返回:
        更新结果的JSON响应
    """
    try:
        image = ImageRecord.query.get(image_id)
        
        if not image:
            logger.warning(f'影像记录不存在，ID: {image_id}')
            return jsonify({'code': 404, 'message': '影像记录不存在', 'data': None}), 404
        
        data = request.get_json()
        
        if data.get('description') is not None:
            image.description = data.get('description')
        if data.get('stage') and data.get('stage') in ['before', 'during', 'after']:
            image.stage = data.get('stage')
        
        db.session.commit()
        
        logger.info(f'更新影像记录成功，ID: {image_id}')
        
        return jsonify({
            'code': 200,
            'message': '更新成功',
            'data': image.to_dict()
        })
    except Exception as e:
        db.session.rollback()
        logger.error(f'更新影像记录失败: {str(e)}')
        return jsonify({'code': 500, 'message': '更新失败', 'data': None}), 500


@images_bp.route('/<int:image_id>', methods=['DELETE'])
def delete_image(image_id):
    """
    删除影像记录
    
    参数:
        image_id: 影像记录ID
        
    返回:
        删除结果的JSON响应
    """
    try:
        image = ImageRecord.query.get(image_id)
        
        if not image:
            logger.warning(f'影像记录不存在，ID: {image_id}')
            return jsonify({'code': 404, 'message': '影像记录不存在', 'data': None}), 404
        
        if image.file_path:
            upload_folder = current_app.config['UPLOAD_FOLDER']
            filename = os.path.basename(image.file_path)
            file_full_path = os.path.join(upload_folder, filename)
            if os.path.exists(file_full_path):
                os.remove(file_full_path)
        
        db.session.delete(image)
        db.session.commit()
        
        logger.info(f'删除影像记录成功，ID: {image_id}')
        
        return jsonify({
            'code': 200,
            'message': '删除成功',
            'data': None
        })
    except Exception as e:
        db.session.rollback()
        logger.error(f'删除影像记录失败: {str(e)}')
        return jsonify({'code': 500, 'message': '删除失败', 'data': None}), 500
