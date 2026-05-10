# -*- coding: utf-8 -*-
"""
后端应用包初始化
"""
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS

from backend.config import config


db = SQLAlchemy()


def create_app(config_name='default'):
    """
    创建并配置Flask应用
    
    Args:
        config_name: 配置名称（development/production/default）
    
    Returns:
        Flask应用实例
    """
    app = Flask(__name__)
    app.config.from_object(config[config_name])
    
    CORS(app, resources={r"/api/*": {"origins": "*"}})
    
    db.init_app(app)
    
    from backend.app.routes import (
        log_bp,
        search_bp,
        stats_bp,
        alert_bp,
        report_bp,
        collect_bp
    )
    
    app.register_blueprint(log_bp, url_prefix='/api/logs')
    app.register_blueprint(search_bp, url_prefix='/api/search')
    app.register_blueprint(stats_bp, url_prefix='/api/stats')
    app.register_blueprint(alert_bp, url_prefix='/api/alerts')
    app.register_blueprint(report_bp, url_prefix='/api/reports')
    app.register_blueprint(collect_bp, url_prefix='/api/collect')
    
    with app.app_context():
        db.create_all()
    
    return app
