"""
任务服务模块单元测试
"""

import pytest
from datetime import datetime, timedelta

from core.models.task import TaskType, TaskStatus
from core.services.task_service import TaskService


class TestTaskService:
    """
    任务服务类测试
    """

    def test_create_cron_task(self, db_manager):
        """
        测试创建Cron任务
        """
        service = TaskService(db_manager)
        
        task = service.create_task(
            name="测试Cron任务",
            func_path="tests.test_helpers.sample_success_func",
            task_type=TaskType.CRON,
            description="这是一个测试任务",
            cron_expression="* * * * *",
        )
        
        assert task is not None
        assert task["name"] == "测试Cron任务"
        assert task["task_type"] == "cron"
        assert task["cron_expression"] == "* * * * *"
        assert task["status"] == "pending"
        assert task["enabled"] is True

    def test_create_interval_task(self, db_manager):
        """
        测试创建间隔任务
        """
        service = TaskService(db_manager)
        
        task = service.create_task(
            name="测试Interval任务",
            func_path="tests.test_helpers.sample_success_func",
            task_type=TaskType.INTERVAL,
            interval_seconds=60,
        )
        
        assert task is not None
        assert task["task_type"] == "interval"
        assert task["interval_seconds"] == 60

    def test_create_date_task(self, db_manager):
        """
        测试创建一次性任务
        """
        service = TaskService(db_manager)
        future_time = datetime.utcnow() + timedelta(minutes=5)
        
        task = service.create_task(
            name="测试Date任务",
            func_path="tests.test_helpers.sample_success_func",
            task_type=TaskType.DATE,
            run_date=future_time,
        )
        
        assert task is not None
        assert task["task_type"] == "date"
        assert task["run_date"] is not None

    def test_create_task_validation_error(self, db_manager):
        """
        测试任务参数验证错误
        """
        service = TaskService(db_manager)
        
        with pytest.raises(ValueError):
            service.create_task(
                name="测试任务",
                func_path="tests.test_helpers.sample_success_func",
                task_type=TaskType.CRON,
            )
        
        with pytest.raises(ValueError):
            service.create_task(
                name="测试任务",
                func_path="tests.test_helpers.sample_success_func",
                task_type=TaskType.INTERVAL,
            )
        
        with pytest.raises(ValueError):
            service.create_task(
                name="测试任务",
                func_path="tests.test_helpers.sample_success_func",
                task_type=TaskType.DATE,
            )

    def test_get_task(self, db_manager):
        """
        测试获取任务
        """
        service = TaskService(db_manager)
        
        created = service.create_task(
            name="测试任务",
            func_path="tests.test_helpers.sample_success_func",
            task_type=TaskType.CRON,
            cron_expression="* * * * *",
        )
        
        retrieved = service.get_task(created["id"])
        
        assert retrieved is not None
        assert retrieved["id"] == created["id"]
        assert retrieved["name"] == created["name"]

    def test_get_nonexistent_task(self, db_manager):
        """
        测试获取不存在的任务
        """
        service = TaskService(db_manager)
        
        task = service.get_task("nonexistent-id")
        assert task is None

    def test_list_tasks(self, db_manager):
        """
        测试列出任务列表
        """
        service = TaskService(db_manager)
        
        for i in range(5):
            service.create_task(
                name=f"测试任务{i}",
                func_path="tests.test_helpers.sample_success_func",
                task_type=TaskType.CRON,
                cron_expression="* * * * *",
            )
        
        tasks = service.list_tasks()
        
        assert len(tasks) == 5

    def test_list_tasks_with_filters(self, db_manager):
        """
        测试带过滤条件的任务列表
        """
        service = TaskService(db_manager)
        
        service.create_task(
            name="Cron任务",
            func_path="tests.test_helpers.sample_success_func",
            task_type=TaskType.CRON,
            cron_expression="* * * * *",
        )
        
        service.create_task(
            name="Interval任务",
            func_path="tests.test_helpers.sample_success_func",
            task_type=TaskType.INTERVAL,
            interval_seconds=60,
        )
        
        cron_tasks = service.list_tasks(task_type=TaskType.CRON)
        assert len(cron_tasks) == 1
        assert cron_tasks[0]["task_type"] == "cron"

    def test_update_task(self, db_manager):
        """
        测试更新任务
        """
        service = TaskService(db_manager)
        
        task = service.create_task(
            name="原始名称",
            func_path="tests.test_helpers.sample_success_func",
            task_type=TaskType.CRON,
            cron_expression="* * * * *",
            max_retries=3,
        )
        
        updated = service.update_task(
            task["id"],
            name="更新后的名称",
            max_retries=5,
            description="新的描述",
        )
        
        assert updated is not None
        assert updated["name"] == "更新后的名称"
        assert updated["max_retries"] == 5
        assert updated["description"] == "新的描述"

    def test_delete_task(self, db_manager):
        """
        测试删除任务
        """
        service = TaskService(db_manager)
        
        task = service.create_task(
            name="要删除的任务",
            func_path="tests.test_helpers.sample_success_func",
            task_type=TaskType.CRON,
            cron_expression="* * * * *",
        )
        
        result = service.delete_task(task["id"])
        assert result is True
        
        deleted = service.get_task(task["id"])
        assert deleted is None

    def test_update_task_status(self, db_manager):
        """
        测试更新任务状态
        """
        service = TaskService(db_manager)
        
        task = service.create_task(
            name="测试任务",
            func_path="tests.test_helpers.sample_success_func",
            task_type=TaskType.CRON,
            cron_expression="* * * * *",
        )
        
        updated = service.update_task_status(task["id"], TaskStatus.RUNNING)
        assert updated is not None
        assert updated["status"] == "running"

    def test_update_task_run_info(self, db_manager):
        """
        测试更新任务执行信息
        """
        service = TaskService(db_manager)
        
        task = service.create_task(
            name="测试任务",
            func_path="tests.test_helpers.sample_success_func",
            task_type=TaskType.CRON,
            cron_expression="* * * * *",
        )
        
        updated = service.update_task_run_info(
            task["id"],
            last_run_at=datetime.utcnow(),
            success=True,
        )
        
        assert updated is not None
        assert updated["success_count"] == 1
        assert updated["last_run_at"] is not None
