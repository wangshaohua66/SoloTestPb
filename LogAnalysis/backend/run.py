# -*- coding: utf-8 -*-
"""
日志聚合分析平台 - 后端启动入口
"""
import os
import sys
import signal

current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(current_dir)
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from backend.app import create_app
from backend.config import Config

app = create_app('default')


def _shutdown(signal_num, frame):
    """
    优雅关闭服务
    
    Args:
        signal_num: 信号编号
        frame: 栈帧
    """
    print("\n正在关闭服务...")
    
    from backend.app.modules.log_collector import collector_manager
    from backend.app.modules.alert_engine import alert_engine
    
    print("停止日志收集器...")
    collector_manager.stop_all()
    
    print("停止告警引擎...")
    alert_engine.stop()
    
    print("服务已关闭")
    sys.exit(0)


def _init_alert_engine():
    """
    初始化并启动告警引擎
    """
    from backend.app.modules.alert_engine import alert_engine
    
    alert_engine.start(check_interval=30, app=app)
    print(f"告警引擎已启动，检查间隔: 30秒")


def _init_collector_manager():
    """
    初始化日志收集器管理器，恢复已激活的日志来源
    """
    from backend.app.models import LogSource
    from backend.app.routes.collect_routes import _start_collector
    from backend.app.modules.log_collector import collector_manager
    
    collector_manager.set_app(app)
    
    active_sources = LogSource.query.filter_by(is_active=True).all()
    if active_sources:
        print(f"发现 {len(active_sources)} 个已激活的日志来源")
        for source in active_sources:
            if source.source_type in ['file', 'network']:
                success = _start_collector(source)
                status = "成功" if success else "失败"
                print(f"  - [{source.name}] ({source.source_type}) 启动{status}")


if __name__ == '__main__':
    print("=" * 60)
    print("日志聚合分析平台 - 后端服务")
    print("=" * 60)
    print(f"监听地址: {Config.BACKEND_HOST}")
    print(f"监听端口: {Config.BACKEND_PORT}")
    print(f"数据库: {Config.SQLALCHEMY_DATABASE_URI}")
    print("=" * 60)
    
    signal.signal(signal.SIGINT, _shutdown)
    signal.signal(signal.SIGTERM, _shutdown)
    
    with app.app_context():
        _init_collector_manager()
        _init_alert_engine()
    
    print("=" * 60)
    print("服务已就绪")
    print("=" * 60)
    
    app.run(
        host=Config.BACKEND_HOST,
        port=Config.BACKEND_PORT,
        debug=Config.DEBUG,
        threaded=True,
        use_reloader=False
    )
