"""
日志服务模块单元测试
"""

import pytest
from datetime import datetime, timedelta

from core.models.task import TaskType
from core.models.execution_log import ExecutionStatus
from core.services.task_service import TaskService
from core.services.log_service import LogService


class TestLogService:
    """
    日志服务类测试
    """

    def _create_test_task(self, service):
        """
        创建测试任务的辅助方法
        """
        return service.create_task(
            name="测试任务",
            func_path="tests.test_helpers.sample_success_func",
            task_type=TaskType.CRON,
            cron_expression="* * * * *",
        )

    def test_create_execution_log(self, db_manager):
        """
        测试创建执行日志
        """
        task_service = TaskService(db_manager)
        log_service = LogService(db_manager)
        
        task = self._create_test_task(task_service)
        
        log = log_service.create_execution_log(
            task_id=task["id"],
            status=ExecutionStatus.RUNNING,
        )
        
        assert log is not None
        assert log["task_id"] == task["id"]
        assert log["status"] == "running"
        assert log["start_time"] is not None

    def test_update_execution_log_success(self, db_manager):
        """
        测试更新执行日志（成功状态）
        """
        task_service = TaskService(db_manager)
        log_service = LogService(db_manager)
        
        task = self._create_test_task(task_service)
        
        log = log_service.create_execution_log(task["id"])
        
        updated = log_service.update_execution_log(
            log["execution_id"],
            status=ExecutionStatus.SUCCESS,
            output="测试输出",
            retry_count=0,
        )
        
        assert updated is not None
        assert updated["status"] == "success"
        assert updated["output"] == "测试输出"
        assert updated["end_time"] is not None
        assert updated["duration_ms"] is not None

    def test_update_execution_log_failed(self, db_manager):
        """
        测试更新执行日志（失败状态）
        """
        task_service = TaskService(db_manager)
        log_service = LogService(db_manager)
        
        task = self._create_test_task(task_service)
        
        log = log_service.create_execution_log(task["id"])
        
        updated = log_service.update_execution_log(
            log["execution_id"],
            status=ExecutionStatus.FAILED,
            error_message="测试错误",
            error_traceback="Traceback...",
            retry_count=2,
        )
        
        assert updated is not None
        assert updated["status"] == "failed"
        assert updated["error_message"] == "测试错误"
        assert updated["error_traceback"] == "Traceback..."
        assert updated["retry_count"] == 2

    def test_get_execution_log(self, db_manager):
        """
        测试获取执行日志
        """
        task_service = TaskService(db_manager)
        log_service = LogService(db_manager)
        
        task = self._create_test_task(task_service)
        
        created = log_service.create_execution_log(task["id"])
        
        retrieved = log_service.get_execution_log(created["execution_id"])
        
        assert retrieved is not None
        assert retrieved["execution_id"] == created["execution_id"]

    def test_get_task_execution_logs(self, db_manager):
        """
        测试获取任务的执行日志列表
        """
        task_service = TaskService(db_manager)
        log_service = LogService(db_manager)
        
        task = self._create_test_task(task_service)
        
        for i in range(5):
            log = log_service.create_execution_log(task["id"])
            log_service.update_execution_log(
                log["execution_id"],
                status=ExecutionStatus.SUCCESS if i < 3 else ExecutionStatus.FAILED,
            )
        
        logs = log_service.get_task_execution_logs(task["id"])
        assert len(logs) == 5
        
        success_logs = log_service.get_task_execution_logs(task["id"], status=ExecutionStatus.SUCCESS)
        assert len(success_logs) == 3

    def test_get_recent_execution_logs(self, db_manager):
        """
        测试获取最近的执行日志
        """
        task_service = TaskService(db_manager)
        log_service = LogService(db_manager)
        
        task = self._create_test_task(task_service)
        
        for i in range(10):
            log = log_service.create_execution_log(task["id"])
            log_service.update_execution_log(
                log["execution_id"],
                status=ExecutionStatus.SUCCESS,
            )
        
        logs = log_service.get_recent_execution_logs(limit=5)
        assert len(logs) == 5

    def test_get_task_execution_stats(self, db_manager):
        """
        测试获取任务执行统计信息
        """
        task_service = TaskService(db_manager)
        log_service = LogService(db_manager)
        
        task = self._create_test_task(task_service)
        
        for i in range(5):
            log = log_service.create_execution_log(task["id"])
            status = ExecutionStatus.SUCCESS if i < 3 else ExecutionStatus.FAILED
            log_service.update_execution_log(log["execution_id"], status=status)
        
        stats = log_service.get_task_execution_stats(task["id"])
        
        assert stats["total_executions"] == 5
        assert stats["success_count"] == 3
        assert stats["failed_count"] == 2
        assert stats["success_rate"] == 60.0

    def test_get_task_execution_stats_empty(self, db_manager):
        """
        测试获取空任务的执行统计
        """
        task_service = TaskService(db_manager)
        log_service = LogService(db_manager)
        
        task = self._create_test_task(task_service)
        
        stats = log_service.get_task_execution_stats(task["id"])
        
        assert stats["total_executions"] == 0
        assert stats["success_count"] == 0
        assert stats["failed_count"] == 0
        assert stats["success_rate"] == 0

    def test_delete_old_logs(self, db_manager):
        """
        测试删除旧日志
        """
        task_service = TaskService(db_manager)
        log_service = LogService(db_manager)
        
        task = self._create_test_task(task_service)
        
        for i in range(5):
            log = log_service.create_execution_log(task["id"])
            log_service.update_execution_log(
                log["execution_id"],
                status=ExecutionStatus.SUCCESS,
            )
        
        count = log_service.delete_old_logs(days=30)
        assert count == 0
