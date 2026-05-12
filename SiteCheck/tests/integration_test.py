"""
集成测试模块
验证调度器任务触发和报告自动生成功能
"""

import sys
import os
import time
import tempfile
import shutil
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.config import Config
from src.scheduler import HealthCheckScheduler


def test_scheduler_task_trigger():
    """
    测试调度器任务按时触发
    使用2秒间隔验证调度器能够按配置执行检测任务
    """
    print("=" * 60)
    print("开始测试调度器任务触发功能")
    print("=" * 60)
    
    # 创建临时配置
    mock_config = Mock()
    mock_config.get_sites.return_value = [
        {
            'name': '测试站点1',
            'url': 'https://example1.com',
            'priority': 1,
            'check_interval': 2,
            'timeout': 10
        }
    ]
    mock_config.get_notifications.return_value = {}
    mock_config.get_ssl_config.return_value = {
        'check_enabled': True,
        'alert_days_before_expiry': 30
    }
    mock_config.get_report_config.return_value = {
        'output_dir': tempfile.mkdtemp(),
        'history_days': 7,
        'generate_interval': 5
    }
    mock_config.get_logging_config.return_value = {
        'level': 'INFO',
        'file': None
    }
    
    call_counter = {'count': 0}
    
    # 模拟HTTPChecker
    original_check = MagicMock(return_value=Mock(
        site_name='测试站点1',
        url='https://example1.com',
        success=True,
        status_code=200,
        response_time=100.5,
        error_message=None,
        timestamp=datetime.now()
    ))
    
    def counting_check(*args, **kwargs):
        call_counter['count'] += 1
        print(f"  [{datetime.now().strftime('%H:%M:%S')}] 检测任务被触发 (第{call_counter['count']}次)")
        return original_check()
    
    with patch('src.scheduler.HTTPChecker') as mock_http_checker, \
         patch('src.scheduler.SSLChecker') as mock_ssl_checker, \
         patch('src.scheduler.NotificationManager') as mock_notifier, \
         patch('src.scheduler.Reporter') as mock_reporter:
        
        # 设置mock
        mock_http_instance = Mock()
        mock_http_instance.check.side_effect = counting_check
        mock_http_checker.return_value = mock_http_instance
        
        mock_ssl_instance = Mock()
        mock_ssl_checker.return_value = mock_ssl_instance
        
        mock_reporter_instance = Mock()
        mock_reporter.return_value = mock_reporter_instance
        
        # 创建并启动调度器
        scheduler = HealthCheckScheduler(mock_config)
        scheduler.start()
        
        print(f"  [{datetime.now().strftime('%H:%M:%S')}] 调度器已启动，等待5秒观察任务触发...")
        
        # 等待5秒观察任务触发
        time.sleep(5)
        
        scheduler.stop()
        print(f"  [{datetime.now().strftime('%H:%M:%S')}] 调度器已停止")
        
        # 验证任务至少触发了2次（初始检测+至少1次定时检测）
        print(f"\n  任务触发次数: {call_counter['count']}")
        
        if call_counter['count'] >= 2:
            print("  ✓ 任务按时触发验证通过")
            return True
        else:
            print("  ✗ 任务按时触发验证失败 - 触发次数不足")
            return False


def test_report_generation():
    """
    测试报告自动生成功能
    """
    print("\n" + "=" * 60)
    print("开始测试报告自动生成功能")
    print("=" * 60)
    
    temp_dir = tempfile.mkdtemp()
    
    try:
        # 创建测试数据
        mock_config = Mock()
        mock_config.get_sites.return_value = [
            {
                'name': '测试站点1',
                'url': 'https://example1.com',
                'priority': 1,
                'check_interval': 60,
                'timeout': 10
            }
        ]
        mock_config.get_notifications.return_value = {}
        mock_config.get_ssl_config.return_value = {
            'check_enabled': True,
            'alert_days_before_expiry': 30
        }
        mock_config.get_report_config.return_value = {
            'output_dir': temp_dir,
            'history_days': 7,
            'generate_interval': 2
        }
        mock_config.get_logging_config.return_value = {
            'level': 'INFO',
            'file': None
        }
        
        report_counter = {'count': 0}
        
        # 模拟报告生成
        def counting_generate_report():
            report_counter['count'] += 1
            print(f"  [{datetime.now().strftime('%H:%M:%S')}] 报告生成任务被触发 (第{report_counter['count']}次)")
            return os.path.join(temp_dir, f"report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.html")
        
        with patch('src.scheduler.HTTPChecker') as mock_http_checker, \
             patch('src.scheduler.SSLChecker') as mock_ssl_checker, \
             patch('src.scheduler.NotificationManager') as mock_notifier, \
             patch('src.scheduler.Reporter') as mock_reporter:
            
            # 设置mock
            mock_http_instance = Mock()
            mock_http_instance.check.return_value = Mock(
                site_name='测试站点1',
                url='https://example1.com',
                success=True,
                status_code=200,
                response_time=100.5,
                error_message=None,
                timestamp=datetime.now()
            )
            mock_http_checker.return_value = mock_http_instance
            
            mock_ssl_instance = Mock()
            mock_ssl_checker.return_value = mock_ssl_instance
            
            mock_reporter_instance = Mock()
            mock_reporter_instance.generate_report.side_effect = counting_generate_report
            mock_reporter.return_value = mock_reporter_instance
            
            # 创建并启动调度器
            scheduler = HealthCheckScheduler(mock_config)
            scheduler.start()
            
            print(f"  [{datetime.now().strftime('%H:%M:%S')}] 调度器已启动，等待4秒观察报告生成...")
            
            # 等待4秒观察报告生成
            time.sleep(4)
            
            scheduler.stop()
            print(f"  [{datetime.now().strftime('%H:%M:%S')}] 调度器已停止")
            
            # 验证报告至少生成了1次
            print(f"\n  报告生成次数: {report_counter['count']}")
            
            if report_counter['count'] >= 1:
                print("  ✓ 报告自动生成验证通过")
                return True
            else:
                print("  ✗ 报告自动生成验证失败")
                return False
    finally:
        shutil.rmtree(temp_dir, ignore_errors=True)


def test_end_to_end_single_mode():
    """
    端到端测试：单次检测模式
    """
    print("\n" + "=" * 60)
    print("开始端到端测试：单次检测模式")
    print("=" * 60)
    
    # 使用实际的配置文件
    try:
        config = Config()
        scheduler = HealthCheckScheduler(config)
        
        print(f"  [{datetime.now().strftime('%H:%M:%S')}] 执行单次检测...")
        scheduler.run_once()
        print(f"  [{datetime.now().strftime('%H:%M:%S')}] 单次检测完成")
        
        print("  ✓ 单次检测模式验证通过")
        return True
    except Exception as e:
        print(f"  ✗ 单次检测模式验证失败: {e}")
        return False


def main():
    """运行所有集成测试"""
    print("\n" + "=" * 60)
    print("网站健康检测工具 - 集成测试套件")
    print(f"测试时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60 + "\n")
    
    results = []
    
    # 运行所有测试
    results.append(("调度器任务按时触发", test_scheduler_task_trigger()))
    results.append(("报告自动生成", test_report_generation()))
    results.append(("单次检测模式端到端", test_end_to_end_single_mode()))
    
    # 打印测试结果汇总
    print("\n" + "=" * 60)
    print("集成测试结果汇总")
    print("=" * 60)
    
    passed = 0
    failed = 0
    
    for test_name, result in results:
        status = "✓ 通过" if result else "✗ 失败"
        print(f"  {test_name}: {status}")
        if result:
            passed += 1
        else:
            failed += 1
    
    print(f"\n总计: {len(results)}个测试, {passed}个通过, {failed}个失败")
    print("=" * 60)
    
    return failed == 0


if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)
