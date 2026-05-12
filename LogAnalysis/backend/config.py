# -*- coding: utf-8 -*-
"""
系统配置文件
包含数据库配置、日志级别等全局配置
"""
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))


class Config:
    """
    基础配置类
    """
    
    SECRET_KEY = 'log-analysis-platform-secret-key-2026'
    DEBUG = False
    
    SQLALCHEMY_DATABASE_URI = f"sqlite:///{os.path.join(BASE_DIR, 'data', 'log_analysis.db')}"
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    BACKEND_HOST = '0.0.0.0'
    BACKEND_PORT = 5001
    
    FRONTEND_PORT = 8001
    
    LOG_STDOUT_LISTENER_PORT = 9000
    
    LOG_FILE_WATCH_INTERVAL = 5
    
    ALERT_CHECK_INTERVAL = 30
    
    DEFAULT_TIME_WINDOW_MINUTES = 5
    
    MAX_LOG_RESULTS_PER_PAGE = 50
    
    MAX_STATS_CACHE_TTL = 60


class DevelopmentConfig(Config):
    """
    开发环境配置
    """
    DEBUG = True


class ProductionConfig(Config):
    """
    生产环境配置
    """
    DEBUG = False


config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}
