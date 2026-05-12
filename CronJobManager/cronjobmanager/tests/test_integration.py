"""
集成测试模块
验证完整任务流程和重启恢复机制
"""

import os
import time
import tempfile
import pytest
from datetime import datetime, timedelta

from core.config import Config
from core.database import DatabaseManager
from core.scheduler import TaskScheduler
from core.models.task import TaskType, TaskStatus


class TestIntegration:
    """
    集成测试类
    """

    @pytest.fixture
    def file_db_config(self):
        """
        使用文件SQLite的配置fixture

        :return: 测试配置对象和数据库路径
        """
        fd, db_path = tempfile.mkstemp(suffix=".db")
        os.close(fd)
        
        config = Config({
            "database": {
                "url": f"sqlite:///{db_path}",
                "echo": False,
            },
            "scheduler": {
                "timezone": "Asia/Shanghai",
                "max_concurrent_jobs": 50,
                "misfire_grace_time": 30,
            },
            "alert": {
                "enabled": False,
            },
        })
        
        yield config, db_path
        
        if os.path.exists(db_path):
            os.remove(db_path)

    @pytest.fixture(autouse=True)
    def reset_singletons(self):
        """
        在每个测试前后重置单例

        :return: None
        """
        TaskScheduler._instance = None
        DatabaseManager._instance = None
        yield
        TaskScheduler._instance = None
        DatabaseManager._instance = None

    def test_task_crud_operations(self, file_db_config):
        """
        测试任务CRUD操作

        :param file_db_config: 文件数据库配置
        """
        config, db_path = file_db_config
        
        scheduler = TaskScheduler(config)
        scheduler.start()
        
        try:
            task = scheduler.add_task(
                name="CRUD测试任务",
                func_path="tests.test_helpers.success_task",
                task_type=TaskType.CRON,
                cron_expression="* * * * *",
            )
            
            assert task is not None
            task_id = task["id"]
            
            retrieved = scheduler.task_service.get_task(task_id)
            assert retrieved["name"] == "CRUD测试任务"
            
            scheduler.pause_task(task_id)
            paused = scheduler.task_service.get_task(task_id)
            assert paused["enabled"] is False
            
            scheduler.resume_task(task_id)
            resumed = scheduler.task_service.get_task(task_id)
            assert resumed["enabled"] is True
            
            result = scheduler.remove_task(task_id)
            assert result is True
            
            deleted = scheduler.task_service.get_task(task_id)
            assert deleted is None
            
        finally:
            scheduler.stop(wait=False)

    def test_task_execution_and_logging(self, file_db_config):
        """
        测试任务执行和日志记录

        :param file_db_config: 文件数据库配置
        """
        config, db_path = file_db_config
        
        scheduler = TaskScheduler(config)
        scheduler.start()
        
        try:
            task = scheduler.add_task(
                name="日志测试任务",
                func_path="tests.test_helpers.success_task",
                task_type=TaskType.DATE,
                run_date=datetime.utcnow() + timedelta(hours=1),
            )
            
            for i in range(3):
                scheduler.run_task_now(task["id"])
                time.sleep(0.1)
            
            logs = scheduler.log_service.get_task_execution_logs(task_id=task["id"])
            assert len(logs) >= 3
            
            stats = scheduler.log_service.get_task_execution_stats(task["id"])
            assert stats["task_id"] == task["id"]
            assert stats["total_executions"] >= 3
            
        finally:
            scheduler.stop(wait=False)

    def test_task_dependency_creation(self, file_db_config):
        """
        测试任务依赖创建

        :param file_db_config: 文件数据库配置
        """
        config, db_path = file_db_config
        
        scheduler = TaskScheduler(config)
        scheduler.start()
        
        try:
            task_a = scheduler.add_task(
                name="任务A",
                func_path="tests.test_helpers.success_task",
                task_type=TaskType.DATE,
                run_date=datetime.utcnow() + timedelta(hours=1),
            )
            
            task_b = scheduler.add_task(
                name="任务B",
                func_path="tests.test_helpers.success_task",
                task_type=TaskType.DATE,
                run_date=datetime.utcnow() + timedelta(hours=1),
                dependencies=[
                    {
                        "dependency_task_id": task_a["id"],
                        "condition": "success",
                    }
                ],
            )
            
            deps = scheduler.dependency_service.get_dependencies(task_b["id"])
            assert len(deps) == 1
            assert deps[0]["dependency_task_id"] == task_a["id"]
            
        finally:
            scheduler.stop(wait=False)

    def test_retry_mechanism_config(self, file_db_config):
        """
        测试重试机制配置

        :param file_db_config: 文件数据库配置
        """
        config, db_path = file_db_config
        
        scheduler = TaskScheduler(config)
        scheduler.start()
        
        try:
            task = scheduler.add_task(
                name="重试任务",
                func_path="tests.test_helpers.failing_task",
                task_type=TaskType.DATE,
                run_date=datetime.utcnow() + timedelta(hours=1),
                max_retries=2,
                retry_interval=0,
                backoff_factor=1,
            )
            
            assert task["max_retries"] == 2
            assert "retry_count" not in task or task.get("retry_count") == 0
            
        finally:
            scheduler.stop(wait=False)

    def test_scheduler_start_stop(self, file_db_config):
        """
        测试调度器启动和停止

        :param file_db_config: 文件数据库配置
        """
        config, db_path = file_db_config
        
        scheduler = TaskScheduler(config)
        
        try:
            scheduler.start()
            assert scheduler._running is True
            
            task = scheduler.add_task(
                name="启动停止测试任务",
                func_path="tests.test_helpers.success_task",
                task_type=TaskType.INTERVAL,
                interval_seconds=3600,
            )
            
            assert task is not None
            
        finally:
            scheduler.stop(wait=False)
            assert scheduler._running is False

    def test_config_usage(self, file_db_config):
        """
        测试配置对象使用

        :param file_db_config: 文件数据库配置
        """
        config, db_path = file_db_config
        
        scheduler = TaskScheduler(config)
        
        assert scheduler.config is config
        assert scheduler.config.get("database.url") == f"sqlite:///{db_path}"
        
        scheduler.start()
        scheduler.stop(wait=False)

    def test_complete_task_flow_end_to_end(self, file_db_config):
        """
        完整任务流程端到端测试：创建任务→启动调度器→立即执行→验证日志和状态

        :param file_db_config: 文件数据库配置
        """
        config, db_path = file_db_config
        
        scheduler = TaskScheduler(config)
        
        try:
            scheduler.start()
            
            task = scheduler.add_task(
                name="端到端测试任务",
                func_path="tests.test_helpers.success_task",
                task_type=TaskType.DATE,
                run_date=datetime.utcnow() + timedelta(hours=1),
            )
            
            assert task is not None
            task_id = task["id"]
            assert task["enabled"] is True
            assert task["status"] == TaskStatus.PENDING.value
            
            execution_id = scheduler.run_task_now(task_id)
            assert execution_id is not None
            time.sleep(0.5)
            
            task_status = scheduler.task_service.get_task(task_id)
            assert task_status["status"] in [TaskStatus.SUCCESS.value, "completed"]
            
            logs = scheduler.log_service.get_task_execution_logs(task_id=task_id)
            assert len(logs) >= 1
            assert logs[0]["task_id"] == task_id
            
            stats = scheduler.log_service.get_task_execution_stats(task_id)
            assert stats["task_id"] == task_id
            assert stats["total_executions"] >= 1
            assert stats["success_count"] >= 1
            
        finally:
            scheduler.stop(wait=False)

    def test_restart_recovery_mechanism(self, file_db_config):
        """
        重启恢复机制测试：添加任务→停止调度器→重新启动→验证任务仍存在且状态正确

        :param file_db_config: 文件数据库配置
        """
        config, db_path = file_db_config
        
        scheduler1 = TaskScheduler(config)
        scheduler1.start()
        
        enabled_task_id = None
        disabled_task_id = None
        
        try:
            enabled_task = scheduler1.add_task(
                name="启用的持久化任务",
                func_path="tests.test_helpers.success_task",
                task_type=TaskType.INTERVAL,
                interval_seconds=3600,
            )
            enabled_task_id = enabled_task["id"]
            
            disabled_task = scheduler1.add_task(
                name="禁用的持久化任务",
                func_path="tests.test_helpers.failing_task",
                task_type=TaskType.CRON,
                cron_expression="0 0 * * *",
            )
            disabled_task_id = disabled_task["id"]
            
            scheduler1.pause_task(disabled_task["id"])
            
            tasks_before = scheduler1.task_service.list_tasks()
            assert len(tasks_before) == 2
            
            enabled_count_before = sum(1 for t in tasks_before if t["enabled"])
            assert enabled_count_before == 1
            
        finally:
            scheduler1.stop(wait=False)
        
        time.sleep(0.2)
        
        TaskScheduler._instance = None
        DatabaseManager._instance = None
        
        scheduler2 = TaskScheduler(config)
        scheduler2.start()
        
        try:
            tasks_after = scheduler2.task_service.list_tasks()
            assert len(tasks_after) == 2
            
            enabled_count_after = sum(1 for t in tasks_after if t["enabled"])
            assert enabled_count_after == 1
            
            enabled_task_loaded = next(t for t in tasks_after if t["enabled"])
            assert enabled_task_loaded["name"] == "启用的持久化任务"
            assert enabled_task_loaded["func_path"] == "tests.test_helpers.success_task"
            
            disabled_task_loaded = next(t for t in tasks_after if not t["enabled"])
            assert disabled_task_loaded["name"] == "禁用的持久化任务"
            assert disabled_task_loaded["func_path"] == "tests.test_helpers.failing_task"
            
        finally:
            scheduler2.stop(wait=False)
