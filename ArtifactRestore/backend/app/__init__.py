# -*- coding: utf-8 -*-
"""
Flask应用程序初始化模块
创建Flask应用实例、初始化数据库、注册蓝图
"""

import os
import logging
from datetime import datetime
from flask import Flask
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from config import config

db = SQLAlchemy()


def setup_logging(app):
    """
    设置日志配置
    将日志输出到控制台和文件
    
    参数:
        app: Flask应用实例
    """
    log_dir = app.config['LOG_DIR']
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)
    
    log_file = os.path.join(log_dir, f'app_{datetime.now().strftime("%Y%m%d")}.log')
    
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_file, encoding='utf-8'),
            logging.StreamHandler()
        ]
    )
    
    logger = logging.getLogger(__name__)
    logger.info('日志系统初始化完成')


def create_app(config_name='default'):
    """
    应用工厂函数
    创建并配置Flask应用实例
    
    参数:
        config_name: 配置名称，默认为'default'
        
    返回:
        配置好的Flask应用实例
    """
    app = Flask(__name__)
    app.config.from_object(config[config_name])
    
    CORS(app, supports_credentials=True)
    
    db.init_app(app)
    
    setup_logging(app)
    
    from app.routes.artifacts import artifacts_bp
    from app.routes.plans import plans_bp
    from app.routes.processes import processes_bp
    from app.routes.images import images_bp
    from app.routes.materials import materials_bp
    from app.routes.export import export_bp
    
    app.register_blueprint(artifacts_bp, url_prefix='/api/artifacts')
    app.register_blueprint(plans_bp, url_prefix='/api/plans')
    app.register_blueprint(processes_bp, url_prefix='/api/processes')
    app.register_blueprint(images_bp, url_prefix='/api/images')
    app.register_blueprint(materials_bp, url_prefix='/api/materials')
    app.register_blueprint(export_bp, url_prefix='/api/export')
    
    with app.app_context():
        from app import models
        db.create_all()
    
    logger = logging.getLogger(__name__)
    logger.info('Flask应用初始化完成')
    
    return app
