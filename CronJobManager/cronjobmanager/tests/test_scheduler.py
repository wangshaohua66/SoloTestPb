"""
调度器模块单元测试
"""

import pytest
import time
from datetime import datetime, timedelta

from core.models.task import TaskType, TaskStatus
from core.database import DatabaseManager
from core.scheduler import TaskScheduler


class TestTaskScheduler:
    """
    任务调度器类测试
    """

    @pytest.fixture(autouse=True)
    def setup_scheduler(self, test_config):
        """
        每个测试前重置调度器单例
        """
        TaskScheduler._instance = None
        DatabaseManager._instance = None
        
        self.scheduler = TaskScheduler(test_config)
        yield
        
        if self.scheduler.running:
            self.scheduler.stop(wait=False)
        
        TaskScheduler._instance = None
        DatabaseManager._instance = None

    def test_scheduler_singleton(self, test_config):
        """
        测试调度器单例模式
        """
        scheduler1 = TaskScheduler(test_config)
        scheduler2 = TaskScheduler(test_config)
        
        assert scheduler1 is scheduler2

    def test_start_and_stop(self):
        """
        测试调度器启动和停止
        """
        assert self.scheduler.running is False
        
        self.scheduler.start()
        assert self.scheduler.running is True
        
        self.scheduler.stop(wait=False)
        assert self.scheduler.running is False

    def test_start_already_running(self):
        """
        测试重复启动调度器
        """
        self.scheduler.start()
        original_state = self.scheduler.running
        
        self.scheduler.start()
        
        assert self.scheduler.running == original_state

    def test_add_cron_task(self):
        """
        测试添加Cron任务
        """
        self.scheduler.start()
        
        task = self.scheduler.add_task(
            name="测试Cron任务",
            func_path="tests.test_helpers.sample_success_func",
            task_type=TaskType.CRON,
            cron_expression="* * * * *",
        )
        
        assert task is not None
        assert task["task_type"] == "cron"
        assert task["name"] == "测试Cron任务"

    def test_add_interval_task(self):
        """
        测试添加间隔任务
        """
        self.scheduler.start()
        
        task = self.scheduler.add_task(
            name="测试Interval任务",
            func_path="tests.test_helpers.sample_success_func",
            task_type=TaskType.INTERVAL,
            interval_seconds=60,
        )
        
        assert task is not None
        assert task["task_type"] == "interval"

    def test_add_date_task(self):
        """
        测试添加一次性任务
        """
        self.scheduler.start()
        future_time = datetime.utcnow() + timedelta(minutes=5)
        
        task = self.scheduler.add_task(
            name="测试Date任务",
            func_path="tests.test_helpers.sample_success_func",
            task_type=TaskType.DATE,
            run_date=future_time,
        )
        
        assert task is not None
        assert task["task_type"] == "date"

    def test_add_task_with_dependencies(self):
        """
        测试添加带依赖关系的任务
        """
        self.scheduler.start()
        
        task_a = self.scheduler.add_task(
            name="任务A",
            func_path="tests.test_helpers.sample_success_func",
            task_type=TaskType.CRON,
            cron_expression="* * * * *",
        )
        
        task_b = self.scheduler.add_task(
            name="任务B",
            func_path="tests.test_helpers.sample_success_func",
            task_type=TaskType.CRON,
            cron_expression="* * * * *",
            dependencies=[
                {
                    "dependency_task_id": task_a["id"],
                    "condition": "success",
                }
            ],
        )
        
        dependencies = self.scheduler.dependency_service.get_dependencies(task_b["id"])
        assert len(dependencies) == 1
        assert dependencies[0]["dependency_task_id"] == task_a["id"]

    def test_get_task_status(self):
        """
        测试获取任务状态
        """
        self.scheduler.start()
        
        created = self.scheduler.add_task(
            name="测试任务",
            func_path="tests.test_helpers.sample_success_func",
            task_type=TaskType.CRON,
            cron_expression="* * * * *",
        )
        
        status = self.scheduler.get_task_status(created["id"])
        
        assert status is not None
        assert status["id"] == created["id"]
        assert status["name"] == "测试任务"

    def test_list_tasks(self):
        """
        测试列出任务
        """
        self.scheduler.start()
        
        for i in range(3):
            self.scheduler.add_task(
                name=f"任务{i}",
                func_path="tests.test_helpers.sample_success_func",
                task_type=TaskType.CRON,
                cron_expression="* * * * *",
            )
        
        tasks = self.scheduler.list_tasks()
        
        assert len(tasks) == 3

    def test_pause_and_resume_task(self):
        """
        测试暂停和恢复任务
        """
        self.scheduler.start()
        
        task = self.scheduler.add_task(
            name="测试任务",
            func_path="tests.test_helpers.sample_success_func",
            task_type=TaskType.CRON,
            cron_expression="* * * * *",
        )
        
        self.scheduler.pause_task(task["id"])
        
        paused_task = self.scheduler.get_task_status(task["id"])
        assert paused_task["enabled"] is False
        assert paused_task["status"] == "paused"
        
        self.scheduler.resume_task(task["id"])
        
        resumed_task = self.scheduler.get_task_status(task["id"])
        assert resumed_task["enabled"] is True
        assert resumed_task["status"] == "pending"

    def test_remove_task(self):
        """
        测试移除任务
        """
        self.scheduler.start()
        
        task = self.scheduler.add_task(
            name="测试任务",
            func_path="tests.test_helpers.sample_success_func",
            task_type=TaskType.CRON,
            cron_expression="* * * * *",
        )
        
        result = self.scheduler.remove_task(task["id"])
        assert result is True
        
        removed = self.scheduler.get_task_status(task["id"])
        assert removed is None

    def test_run_task_now(self):
        """
        测试立即执行任务
        """
        self.scheduler.start()
        
        task = self.scheduler.add_task(
            name="测试立即执行任务",
            func_path="tests.test_helpers.sample_success_func",
            task_type=TaskType.CRON,
            cron_expression="* * * * *",
            args=["test_param"],
            kwargs={"param2": 123},
        )
        
        execution_id = self.scheduler.run_task_now(task["id"])
        
        assert execution_id is not None
        
        time.sleep(0.1)
        
        logs = self.scheduler.log_service.get_task_execution_logs(task["id"])
        assert len(logs) >= 1
