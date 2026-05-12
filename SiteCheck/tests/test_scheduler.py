"""
调度器模块测试
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime
from src.scheduler import HealthCheckScheduler
from src.http_checker import CheckResult


class TestHealthCheckScheduler:
    """
    HealthCheckScheduler类测试
    """

    @pytest.fixture
    def mock_config(self):
        """创建模拟配置"""
        config = Mock()
        config.get_sites.return_value = [
            {
                'name': '测试站点1',
                'url': 'https://example1.com',
                'priority': 1,
                'check_interval': 60,
                'timeout': 10
            }
        ]
        config.get_notifications.return_value = {}
        config.get_ssl_config.return_value = {
            'check_enabled': True,
            'alert_days_before_expiry': 30
        }
        config.get_report_config.return_value = {
            'output_dir': './reports',
            'history_days': 7,
            'generate_interval': 86400
        }
        config.get_logging_config.return_value = {
            'level': 'INFO',
            'file': './logs/test.log'
        }
        return config

    @patch('src.scheduler.HTTPChecker')
    @patch('src.scheduler.SSLChecker')
    @patch('src.scheduler.NotificationManager')
    @patch('src.scheduler.Reporter')
    def test_scheduler_init(self, mock_reporter, mock_notifier_manager, mock_ssl_checker, mock_http_checker, mock_config):
        """测试调度器初始化"""
        scheduler = HealthCheckScheduler(mock_config)
        
        assert scheduler.config == mock_config
        assert scheduler.running is False
        assert scheduler.http_checker is not None
        assert scheduler.ssl_checker is not None
        assert scheduler.notification_manager is not None
        assert scheduler.reporter is not None

    @patch('src.scheduler.HTTPChecker')
    @patch('src.scheduler.SSLChecker')
    @patch('src.scheduler.NotificationManager')
    @patch('src.scheduler.Reporter')
    def test_run_once(self, mock_reporter, mock_notifier_manager, mock_ssl_checker, mock_http_checker, mock_config):
        """测试执行一次检测"""
        mock_http_instance = Mock()
        mock_http_instance.check.return_value = CheckResult(
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
        mock_ssl_instance.check.return_value = Mock(valid=True, days_until_expiry=60)
        mock_ssl_instance.needs_alert.return_value = False
        mock_ssl_checker.return_value = mock_ssl_instance
        
        scheduler = HealthCheckScheduler(mock_config)
        scheduler.run_once()
        
        assert mock_http_instance.check.called
        assert scheduler.running is False

    @patch('src.scheduler.HTTPChecker')
    @patch('src.scheduler.SSLChecker')
    @patch('src.scheduler.NotificationManager')
    @patch('src.scheduler.Reporter')
    def test_check_site_success(self, mock_reporter, mock_notifier_manager, mock_ssl_checker, mock_http_checker, mock_config):
        """测试成功检测单个站点"""
        mock_http_instance = Mock()
        mock_http_instance.check.return_value = CheckResult(
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
        mock_ssl_result = Mock(valid=True, days_until_expiry=60)
        mock_ssl_instance.check.return_value = mock_ssl_result
        mock_ssl_instance.needs_alert.return_value = False
        mock_ssl_checker.return_value = mock_ssl_instance
        
        mock_notifier_instance = Mock()
        mock_notifier_manager.return_value = mock_notifier_instance
        
        scheduler = HealthCheckScheduler(mock_config)
        site = {'name': '测试站点1', 'url': 'https://example1.com'}
        scheduler._check_site(site)
        
        assert scheduler.reporter.add_result.called
        assert not mock_notifier_instance.send_http_alert.called

    @patch('src.scheduler.HTTPChecker')
    @patch('src.scheduler.SSLChecker')
    @patch('src.scheduler.NotificationManager')
    @patch('src.scheduler.Reporter')
    def test_check_site_failed_with_alert(self, mock_reporter, mock_notifier_manager, mock_ssl_checker, mock_http_checker, mock_config):
        """测试站点检测失败发送告警"""
        mock_http_instance = Mock()
        mock_http_instance.check.return_value = CheckResult(
            site_name='测试站点1',
            url='https://example1.com',
            success=False,
            status_code=500,
            response_time=100.5,
            error_message='服务器错误',
            timestamp=datetime.now()
        )
        mock_http_checker.return_value = mock_http_instance
        
        mock_ssl_instance = Mock()
        mock_ssl_instance.needs_alert.return_value = False
        mock_ssl_checker.return_value = mock_ssl_instance
        
        mock_notifier_instance = Mock()
        mock_notifier_manager.return_value = mock_notifier_instance
        
        scheduler = HealthCheckScheduler(mock_config)
        site = {'name': '测试站点1', 'url': 'https://example1.com'}
        scheduler._check_site(site)
        
        assert scheduler.reporter.add_result.called
        assert mock_notifier_instance.send_http_alert.called

    @patch('src.scheduler.HTTPChecker')
    @patch('src.scheduler.SSLChecker')
    @patch('src.scheduler.NotificationManager')
    @patch('src.scheduler.Reporter')
    def test_check_site_ssl_alert(self, mock_reporter, mock_notifier_manager, mock_ssl_checker, mock_http_checker, mock_config):
        """测试SSL证书需要告警"""
        mock_http_instance = Mock()
        mock_http_instance.check.return_value = CheckResult(
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
        mock_ssl_result = Mock(valid=True, days_until_expiry=10)
        mock_ssl_instance.check.return_value = mock_ssl_result
        mock_ssl_instance.needs_alert.return_value = True
        mock_ssl_checker.return_value = mock_ssl_instance
        
        mock_notifier_instance = Mock()
        mock_notifier_manager.return_value = mock_notifier_instance
        
        scheduler = HealthCheckScheduler(mock_config)
        site = {'name': '测试站点1', 'url': 'https://example1.com'}
        scheduler._check_site(site)
        
        assert mock_notifier_instance.send_ssl_alert.called

    @patch('src.scheduler.HTTPChecker')
    @patch('src.scheduler.SSLChecker')
    @patch('src.scheduler.NotificationManager')
    @patch('src.scheduler.Reporter')
    def test_check_site_exception(self, mock_reporter, mock_notifier_manager, mock_ssl_checker, mock_http_checker, mock_config):
        """测试检测站点时发生异常"""
        mock_http_instance = Mock()
        mock_http_instance.check.side_effect = Exception('测试异常')
        mock_http_checker.return_value = mock_http_instance
        
        scheduler = HealthCheckScheduler(mock_config)
        site = {'name': '测试站点1', 'url': 'https://example1.com'}
        
        scheduler._check_site(site)

    @patch('src.scheduler.HTTPChecker')
    @patch('src.scheduler.SSLChecker')
    @patch('src.scheduler.NotificationManager')
    @patch('src.scheduler.Reporter')
    @patch('src.scheduler.BackgroundScheduler')
    def test_start_scheduler(self, mock_bg_scheduler, mock_reporter, mock_notifier_manager, mock_ssl_checker, mock_http_checker, mock_config):
        """测试启动调度器"""
        mock_scheduler_instance = Mock()
        mock_bg_scheduler.return_value = mock_scheduler_instance
        
        mock_http_instance = Mock()
        mock_http_instance.check.return_value = CheckResult(
            site_name='测试站点1',
            url='https://example1.com',
            success=True,
            status_code=200,
            response_time=100.5,
            error_message=None,
            timestamp=datetime.now()
        )
        mock_http_checker.return_value = mock_http_instance
        
        scheduler = HealthCheckScheduler(mock_config)
        scheduler.start()
        
        assert scheduler.running is True
        assert mock_scheduler_instance.start.called
        assert mock_scheduler_instance.add_job.called

    @patch('src.scheduler.HTTPChecker')
    @patch('src.scheduler.SSLChecker')
    @patch('src.scheduler.NotificationManager')
    @patch('src.scheduler.Reporter')
    @patch('src.scheduler.BackgroundScheduler')
    def test_start_scheduler_already_running(self, mock_bg_scheduler, mock_reporter, mock_notifier_manager, mock_ssl_checker, mock_http_checker, mock_config):
        """测试调度器已在运行时再次启动"""
        mock_scheduler_instance = Mock()
        mock_bg_scheduler.return_value = mock_scheduler_instance
        
        scheduler = HealthCheckScheduler(mock_config)
        scheduler.running = True
        scheduler.start()
        
        assert not mock_scheduler_instance.start.called

    @patch('src.scheduler.HTTPChecker')
    @patch('src.scheduler.SSLChecker')
    @patch('src.scheduler.NotificationManager')
    @patch('src.scheduler.Reporter')
    @patch('src.scheduler.BackgroundScheduler')
    def test_stop_scheduler(self, mock_bg_scheduler, mock_reporter, mock_notifier_manager, mock_ssl_checker, mock_http_checker, mock_config):
        """测试停止调度器"""
        mock_scheduler_instance = Mock()
        mock_bg_scheduler.return_value = mock_scheduler_instance
        
        scheduler = HealthCheckScheduler(mock_config)
        scheduler.running = True
        scheduler.stop()
        
        assert scheduler.running is False
        assert mock_scheduler_instance.shutdown.called

    @patch('src.scheduler.HTTPChecker')
    @patch('src.scheduler.SSLChecker')
    @patch('src.scheduler.NotificationManager')
    @patch('src.scheduler.Reporter')
    def test_stop_scheduler_not_running(self, mock_reporter, mock_notifier_manager, mock_ssl_checker, mock_http_checker, mock_config):
        """测试停止未运行的调度器"""
        scheduler = HealthCheckScheduler(mock_config)
        scheduler.running = False
        
        scheduler.stop()
        
        assert scheduler.running is False

    @patch('src.scheduler.HTTPChecker')
    @patch('src.scheduler.SSLChecker')
    @patch('src.scheduler.NotificationManager')
    @patch('src.scheduler.Reporter')
    def test_generate_report_job(self, mock_reporter, mock_notifier_manager, mock_ssl_checker, mock_http_checker, mock_config):
        """测试定时生成报告任务"""
        scheduler = HealthCheckScheduler(mock_config)
        scheduler._generate_report_job()
        
        assert scheduler.reporter.generate_report.called

    @patch('src.scheduler.HTTPChecker')
    @patch('src.scheduler.SSLChecker')
    @patch('src.scheduler.NotificationManager')
    @patch('src.scheduler.Reporter')
    def test_generate_report_job_exception(self, mock_reporter, mock_notifier_manager, mock_ssl_checker, mock_http_checker, mock_config):
        """测试生成报告时发生异常"""
        mock_reporter_instance = Mock()
        mock_reporter_instance.generate_report.side_effect = Exception('生成报告失败')
        mock_reporter.return_value = mock_reporter_instance
        
        scheduler = HealthCheckScheduler(mock_config)
        scheduler._generate_report_job()

    @patch('src.scheduler.HTTPChecker')
    @patch('src.scheduler.SSLChecker')
    @patch('src.scheduler.NotificationManager')
    @patch('src.scheduler.Reporter')
    def test_check_http_site_only(self, mock_reporter, mock_notifier_manager, mock_ssl_checker, mock_http_checker, mock_config):
        """测试HTTP站点不进行SSL检测"""
        mock_http_instance = Mock()
        mock_http_instance.check.return_value = CheckResult(
            site_name='测试站点1',
            url='http://example1.com',
            success=True,
            status_code=200,
            response_time=100.5,
            error_message=None,
            timestamp=datetime.now()
        )
        mock_http_checker.return_value = mock_http_instance
        
        mock_ssl_instance = Mock()
        mock_ssl_checker.return_value = mock_ssl_instance
        
        scheduler = HealthCheckScheduler(mock_config)
        site = {'name': '测试站点1', 'url': 'http://example1.com'}
        scheduler._check_site(site)
        
        assert not mock_ssl_instance.check.called

    @patch('src.scheduler.HTTPChecker')
    @patch('src.scheduler.SSLChecker')
    @patch('src.scheduler.NotificationManager')
    @patch('src.scheduler.Reporter')
    def test_ssl_check_disabled(self, mock_reporter, mock_notifier_manager, mock_ssl_checker, mock_http_checker, mock_config):
        """测试SSL检测禁用时跳过SSL检测"""
        mock_config.get_ssl_config.return_value = {
            'check_enabled': False
        }
        
        mock_http_instance = Mock()
        mock_http_instance.check.return_value = CheckResult(
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
        
        scheduler = HealthCheckScheduler(mock_config)
        site = {'name': '测试站点1', 'url': 'https://example1.com'}
        scheduler._check_site(site)
        
        assert not mock_ssl_instance.check.called

    @patch('src.scheduler.HTTPChecker')
    @patch('src.scheduler.SSLChecker')
    @patch('src.scheduler.NotificationManager')
    @patch('src.scheduler.Reporter')
    @patch('time.sleep', side_effect=KeyboardInterrupt)
    def test_wait_with_keyboard_interrupt(self, mock_sleep, mock_reporter, mock_notifier_manager, mock_ssl_checker, mock_http_checker, mock_config):
        """测试键盘中断停止等待"""
        scheduler = HealthCheckScheduler(mock_config)
        scheduler.running = True
        mock_scheduler_instance = Mock()
        scheduler.scheduler = mock_scheduler_instance
        
        scheduler.wait()
        
        assert scheduler.running is False
        assert mock_scheduler_instance.shutdown.called
