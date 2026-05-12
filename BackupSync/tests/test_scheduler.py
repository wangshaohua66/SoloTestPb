# -*- coding: utf-8 -*-
"""
BackupScheduler 定时任务单元测试
"""
import pytest
import schedule
from backupsync import BackupScheduler


class TestBackupScheduler:
    """
    BackupScheduler 类的测试用例
    """
    
    @pytest.fixture(autouse=True)
    def setup_and_teardown(self):
        """
        每个测试用例前后清理 schedule
        """
        schedule.clear()
        yield
        schedule.clear()
    
    def test_initialization(self):
        """
        测试初始化功能
        """
        def mock_backup_func():
            return {'added_count': 0, 'modified_count': 0, 'deleted_count': 0}
        
        scheduler = BackupScheduler(backup_func=mock_backup_func)
        
        assert scheduler.backup_func == mock_backup_func
        assert not scheduler.is_running()
        
        stats = scheduler.get_stats()
        assert stats['running'] == False
        assert stats['last_run_time'] is None
        assert stats['run_count'] == 0
        assert stats['pending_jobs'] == 0
    
    def test_schedule_daily(self):
        """
        测试每日定时任务
        """
        scheduler = BackupScheduler(backup_func=lambda: {})
        scheduler.schedule_daily('02:00')
        
        stats = scheduler.get_stats()
        assert stats['pending_jobs'] == 1
    
    def test_schedule_hourly(self):
        """
        测试每小时定时任务
        """
        scheduler = BackupScheduler(backup_func=lambda: {})
        scheduler.schedule_hourly(minute=30)
        
        stats = scheduler.get_stats()
        assert stats['pending_jobs'] == 1
    
    def test_schedule_minutely(self):
        """
        测试每分钟定时任务
        """
        scheduler = BackupScheduler(backup_func=lambda: {})
        scheduler.schedule_minutely(interval=5)
        
        stats = scheduler.get_stats()
        assert stats['pending_jobs'] == 1
    
    def test_schedule_weekly(self):
        """
        测试每周定时任务
        """
        scheduler = BackupScheduler(backup_func=lambda: {})
        scheduler.schedule_weekly('monday', '02:00')
        
        stats = scheduler.get_stats()
        assert stats['pending_jobs'] == 1
    
    def test_schedule_weekly_invalid_day(self):
        """
        测试每周定时任务 - 无效的星期几
        """
        scheduler = BackupScheduler(backup_func=lambda: {})
        
        with pytest.raises(ValueError, match='无效的星期几'):
            scheduler.schedule_weekly('invalid_day', '02:00')
    
    def test_clear_schedule(self):
        """
        测试清除定时任务
        """
        scheduler = BackupScheduler(backup_func=lambda: {})
        
        scheduler.schedule_daily('02:00')
        scheduler.schedule_hourly(minute=0)
        scheduler.schedule_minutely(interval=5)
        
        assert scheduler.get_stats()['pending_jobs'] == 3
        
        scheduler.clear_schedule()
        
        assert scheduler.get_stats()['pending_jobs'] == 0
    
    def test_run_backup_success(self, capsys):
        """
        测试备份任务执行成功
        """
        backup_called = []
        
        def mock_backup():
            backup_called.append(True)
            return {
                'added_count': 2,
                'modified_count': 1,
                'deleted_count': 0
            }
        
        scheduler = BackupScheduler(backup_func=mock_backup)
        scheduler._run_backup()
        
        assert len(backup_called) == 1
        
        stats = scheduler.get_stats()
        assert stats['run_count'] == 1
        assert stats['last_run_time'] is not None
    
    def test_run_backup_failure(self, capsys):
        """
        测试备份任务执行失败
        """
        def mock_backup():
            raise Exception("备份失败测试")
        
        scheduler = BackupScheduler(backup_func=mock_backup)
        scheduler._run_backup()
        
        stats = scheduler.get_stats()
        assert stats['run_count'] == 0
        assert stats['last_run_time'] is None
    
    def test_stop(self):
        """
        测试停止调度器
        """
        scheduler = BackupScheduler(backup_func=lambda: {})
        scheduler._running = True
        
        assert scheduler.is_running()
        
        scheduler.stop()
        
        assert not scheduler.is_running()
