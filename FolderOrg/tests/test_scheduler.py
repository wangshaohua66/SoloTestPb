"""
定时任务模块单元测试
"""

import time
import pytest
from folder_organizer.scheduler import Scheduler


class TestScheduler:
    """
    定时任务调度器测试类
    """

    def test_init(self):
        """
        测试初始化
        """
        call_count = [0]
        
        def mock_organize():
            call_count[0] += 1
            return {"moved_files": 0}
        
        scheduler = Scheduler(mock_organize)
        
        assert scheduler.organize_func == mock_organize
        assert scheduler.running is False
        assert scheduler.schedule_thread is None

    def test_set_logger(self):
        """
        测试设置日志记录器
        """
        class MockLogger:
            def __init__(self):
                self.messages = []
            
            def info(self, msg):
                self.messages.append(("info", msg))
            
            def warning(self, msg):
                self.messages.append(("warning", msg))
            
            def error(self, msg):
                self.messages.append(("error", msg))
        
        def mock_organize():
            return {"moved_files": 0}
        
        scheduler = Scheduler(mock_organize)
        mock_logger = MockLogger()
        
        scheduler.set_logger(mock_logger)
        assert scheduler.logger == mock_logger

    def test_schedule_daily(self):
        """
        测试配置每日定时任务
        """
        class MockLogger:
            def __init__(self):
                self.messages = []
            
            def info(self, msg):
                self.messages.append(("info", msg))
            
            def warning(self, msg):
                self.messages.append(("warning", msg))
        
        def mock_organize():
            return {"moved_files": 0}
        
        scheduler = Scheduler(mock_organize)
        mock_logger = MockLogger()
        scheduler.set_logger(mock_logger)
        
        scheduler.schedule_daily("02:00")
        
        jobs = scheduler.get_pending_jobs()
        assert len(jobs) == 1
        
        log_messages = [msg for level, msg in mock_logger.messages if level == "info"]
        assert any("每日" in msg and "02:00" in msg for msg in log_messages)

    def test_schedule_hourly(self):
        """
        测试配置每小时定时任务
        """
        class MockLogger:
            def __init__(self):
                self.messages = []
            
            def info(self, msg):
                self.messages.append(("info", msg))
        
        def mock_organize():
            return {"moved_files": 0}
        
        scheduler = Scheduler(mock_organize)
        mock_logger = MockLogger()
        scheduler.set_logger(mock_logger)
        
        scheduler.schedule_hourly(interval=2)
        
        jobs = scheduler.get_pending_jobs()
        assert len(jobs) == 1
        
        log_messages = [msg for level, msg in mock_logger.messages if level == "info"]
        assert any("2 小时" in msg for msg in log_messages)

    def test_schedule_minutes(self):
        """
        测试配置每分钟定时任务
        """
        class MockLogger:
            def __init__(self):
                self.messages = []
            
            def info(self, msg):
                self.messages.append(("info", msg))
        
        def mock_organize():
            return {"moved_files": 0}
        
        scheduler = Scheduler(mock_organize)
        mock_logger = MockLogger()
        scheduler.set_logger(mock_logger)
        
        scheduler.schedule_minutes(interval=30)
        
        jobs = scheduler.get_pending_jobs()
        assert len(jobs) == 1
        
        log_messages = [msg for level, msg in mock_logger.messages if level == "info"]
        assert any("30 分钟" in msg for msg in log_messages)

    def test_schedule_weekly(self):
        """
        测试配置每周定时任务
        """
        class MockLogger:
            def __init__(self):
                self.messages = []
            
            def info(self, msg):
                self.messages.append(("info", msg))
        
        def mock_organize():
            return {"moved_files": 0}
        
        scheduler = Scheduler(mock_organize)
        mock_logger = MockLogger()
        scheduler.set_logger(mock_logger)
        
        scheduler.schedule_weekly(day="monday", time_str="09:00")
        
        jobs = scheduler.get_pending_jobs()
        assert len(jobs) == 1
        
        log_messages = [msg for level, msg in mock_logger.messages if level == "info"]
        assert any("monday" in msg.lower() and "09:00" in msg for msg in log_messages)

    def test_schedule_weekly_invalid_day(self):
        """
        测试配置每周定时任务时使用无效的星期几
        """
        class MockLogger:
            def __init__(self):
                self.messages = []
            
            def info(self, msg):
                self.messages.append(("info", msg))
            
            def error(self, msg):
                self.messages.append(("error", msg))
        
        def mock_organize():
            return {"moved_files": 0}
        
        scheduler = Scheduler(mock_organize)
        mock_logger = MockLogger()
        scheduler.set_logger(mock_logger)
        
        scheduler.schedule_weekly(day="invalid_day", time_str="09:00")
        
        jobs = scheduler.get_pending_jobs()
        assert len(jobs) == 0
        
        error_messages = [msg for level, msg in mock_logger.messages if level == "error"]
        assert any("invalid_day" in msg for msg in error_messages)

    def test_is_running(self):
        """
        测试检查定时任务是否在运行
        """
        def mock_organize():
            return {"moved_files": 0}
        
        scheduler = Scheduler(mock_organize)
        
        assert scheduler.is_running() is False
        
        scheduler.running = True
        assert scheduler.is_running() is True

    def test_get_pending_jobs(self):
        """
        测试获取待执行的任务列表
        """
        def mock_organize():
            return {"moved_files": 0}
        
        scheduler = Scheduler(mock_organize)
        
        jobs = scheduler.get_pending_jobs()
        assert isinstance(jobs, list)
        
        scheduler.schedule_hourly(interval=1)
        
        jobs = scheduler.get_pending_jobs()
        assert len(jobs) == 1

    def test_execute_organize(self):
        """
        测试执行整理任务
        """
        call_count = [0]
        
        def mock_organize():
            call_count[0] += 1
            return {"moved_files": 5, "failed_files": 0}
        
        scheduler = Scheduler(mock_organize)
        
        result = scheduler._execute_organize()
        
        assert call_count[0] == 1
        assert result["moved_files"] == 5
        assert result["failed_files"] == 0

    def test_execute_organize_with_exception(self):
        """
        测试执行整理任务时发生异常
        """
        def mock_organize():
            raise Exception("Test error")
        
        scheduler = Scheduler(mock_organize)
        
        result = scheduler._execute_organize()
        
        assert "error" in result
        assert "Test error" in result["error"]
