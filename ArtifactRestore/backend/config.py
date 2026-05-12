# -*- coding: utf-8 -*-
"""
系统配置模块
定义数据库连接、服务器端口等配置信息
"""

import os


class Config:
    """
    基础配置类
    包含应用程序的基础配置参数
    """
    
    BASE_DIR = os.path.abspath(os.path.dirname(__file__))
    
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'artifact-restore-secret-key-2024'
    
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        'sqlite:///' + os.path.join(BASE_DIR, 'app.db')
    
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    UPLOAD_FOLDER = os.path.join(BASE_DIR, 'app', 'static', 'images')
    
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024
    
    LOG_DIR = os.path.join(BASE_DIR, 'logs')


class DevelopmentConfig(Config):
    """
    开发环境配置类
    继承基础配置，添加开发环境特定配置
    """
    
    DEBUG = True


class ProductionConfig(Config):
    """
    生产环境配置类
    继承基础配置，添加生产环境特定配置
    """
    
    DEBUG = False


config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}
