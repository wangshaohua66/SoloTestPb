"""
依赖服务模块单元测试
"""

import pytest
from datetime import datetime, timedelta

from core.models.task import TaskType, TaskStatus
from core.models.task_dependency import DependencyCondition
from core.services.task_service import TaskService
from core.services.dependency_service import DependencyService


class TestDependencyService:
    """
    依赖服务类测试
    """

    def _create_test_task(self, service, name):
        """
        创建测试任务的辅助方法
        """
        return service.create_task(
            name=name,
            func_path="tests.test_helpers.sample_success_func",
            task_type=TaskType.CRON,
            cron_expression="* * * * *",
        )

    def test_add_dependency(self, db_manager):
        """
        测试添加依赖关系
        """
        task_service = TaskService(db_manager)
        dep_service = DependencyService(db_manager)
        
        task_a = self._create_test_task(task_service, "任务A")
        task_b = self._create_test_task(task_service, "任务B")
        
        dependency = dep_service.add_dependency(
            dependent_task_id=task_b["id"],
            dependency_task_id=task_a["id"],
            condition=DependencyCondition.SUCCESS,
        )
        
        assert dependency is not None
        assert dependency["dependent_task_id"] == task_b["id"]
        assert dependency["dependency_task_id"] == task_a["id"]

    def test_add_self_dependency_error(self, db_manager):
        """
        测试任务不能依赖自身
        """
        task_service = TaskService(db_manager)
        dep_service = DependencyService(db_manager)
        
        task = self._create_test_task(task_service, "测试任务")
        
        with pytest.raises(ValueError, match="任务不能依赖自身"):
            dep_service.add_dependency(
                dependent_task_id=task["id"],
                dependency_task_id=task["id"],
            )

    def test_circular_dependency_error(self, db_manager):
        """
        测试检测循环依赖
        """
        task_service = TaskService(db_manager)
        dep_service = DependencyService(db_manager)
        
        task_a = self._create_test_task(task_service, "任务A")
        task_b = self._create_test_task(task_service, "任务B")
        task_c = self._create_test_task(task_service, "任务C")
        
        dep_service.add_dependency(
            dependent_task_id=task_b["id"],
            dependency_task_id=task_a["id"],
        )
        
        dep_service.add_dependency(
            dependent_task_id=task_c["id"],
            dependency_task_id=task_b["id"],
        )
        
        with pytest.raises(ValueError, match="检测到循环依赖"):
            dep_service.add_dependency(
                dependent_task_id=task_a["id"],
                dependency_task_id=task_c["id"],
            )

    def test_get_dependencies(self, db_manager):
        """
        测试获取任务的前置依赖
        """
        task_service = TaskService(db_manager)
        dep_service = DependencyService(db_manager)
        
        task_a = self._create_test_task(task_service, "任务A")
        task_b = self._create_test_task(task_service, "任务B")
        task_c = self._create_test_task(task_service, "任务C")
        
        dep_service.add_dependency(
            dependent_task_id=task_c["id"],
            dependency_task_id=task_a["id"],
        )
        dep_service.add_dependency(
            dependent_task_id=task_c["id"],
            dependency_task_id=task_b["id"],
        )
        
        dependencies = dep_service.get_dependencies(task_c["id"])
        
        assert len(dependencies) == 2

    def test_get_dependents(self, db_manager):
        """
        测试获取依赖此任务的后续任务
        """
        task_service = TaskService(db_manager)
        dep_service = DependencyService(db_manager)
        
        task_a = self._create_test_task(task_service, "任务A")
        task_b = self._create_test_task(task_service, "任务B")
        task_c = self._create_test_task(task_service, "任务C")
        
        dep_service.add_dependency(
            dependent_task_id=task_b["id"],
            dependency_task_id=task_a["id"],
        )
        dep_service.add_dependency(
            dependent_task_id=task_c["id"],
            dependency_task_id=task_a["id"],
        )
        
        dependents = dep_service.get_dependents(task_a["id"])
        
        assert len(dependents) == 2

    def test_remove_dependency(self, db_manager):
        """
        测试删除依赖关系
        """
        task_service = TaskService(db_manager)
        dep_service = DependencyService(db_manager)
        
        task_a = self._create_test_task(task_service, "任务A")
        task_b = self._create_test_task(task_service, "任务B")
        
        dependency = dep_service.add_dependency(
            dependent_task_id=task_b["id"],
            dependency_task_id=task_a["id"],
        )
        
        result = dep_service.remove_dependency(dependency["id"])
        assert result is True
        
        dependencies = dep_service.get_dependencies(task_b["id"])
        assert len(dependencies) == 0

    def test_remove_all_dependencies(self, db_manager):
        """
        测试删除与任务相关的所有依赖关系
        """
        task_service = TaskService(db_manager)
        dep_service = DependencyService(db_manager)
        
        task_a = self._create_test_task(task_service, "任务A")
        task_b = self._create_test_task(task_service, "任务B")
        task_c = self._create_test_task(task_service, "任务C")
        
        dep_service.add_dependency(
            dependent_task_id=task_b["id"],
            dependency_task_id=task_a["id"],
        )
        dep_service.add_dependency(
            dependent_task_id=task_a["id"],
            dependency_task_id=task_c["id"],
        )
        
        count = dep_service.remove_all_dependencies(task_a["id"])
        
        assert count == 2
        assert len(dep_service.get_dependencies(task_b["id"])) == 0
        assert len(dep_service.get_dependents(task_c["id"])) == 0

    def test_check_dependencies_ready_success_condition(self, db_manager):
        """
        测试检查依赖是否满足（SUCCESS条件）
        """
        task_service = TaskService(db_manager)
        dep_service = DependencyService(db_manager)
        
        task_a = self._create_test_task(task_service, "任务A")
        task_b = self._create_test_task(task_service, "任务B")
        
        dep_service.add_dependency(
            dependent_task_id=task_b["id"],
            dependency_task_id=task_a["id"],
            condition=DependencyCondition.SUCCESS,
        )
        
        assert dep_service.check_dependencies_ready(task_b["id"]) is False
        
        task_service.update_task_status(task_a["id"], TaskStatus.SUCCESS)
        
        assert dep_service.check_dependencies_ready(task_b["id"]) is True

    def test_check_dependencies_ready_completion_condition(self, db_manager):
        """
        测试检查依赖是否满足（COMPLETION条件）
        """
        task_service = TaskService(db_manager)
        dep_service = DependencyService(db_manager)
        
        task_a = self._create_test_task(task_service, "任务A")
        task_b = self._create_test_task(task_service, "任务B")
        
        dep_service.add_dependency(
            dependent_task_id=task_b["id"],
            dependency_task_id=task_a["id"],
            condition=DependencyCondition.COMPLETION,
        )
        
        assert dep_service.check_dependencies_ready(task_b["id"]) is False
        
        task_service.update_task_status(task_a["id"], TaskStatus.FAILED)
        
        assert dep_service.check_dependencies_ready(task_b["id"]) is True

    def test_check_dependencies_ready_always_condition(self, db_manager):
        """
        测试检查依赖是否满足（ALWAYS条件）
        """
        task_service = TaskService(db_manager)
        dep_service = DependencyService(db_manager)
        
        task_a = self._create_test_task(task_service, "任务A")
        task_b = self._create_test_task(task_service, "任务B")
        
        dep_service.add_dependency(
            dependent_task_id=task_b["id"],
            dependency_task_id=task_a["id"],
            condition=DependencyCondition.ALWAYS,
        )
        
        assert dep_service.check_dependencies_ready(task_b["id"]) is True

    def test_check_dependencies_ready_no_dependencies(self, db_manager):
        """
        测试没有依赖的任务总是准备就绪
        """
        task_service = TaskService(db_manager)
        dep_service = DependencyService(db_manager)
        
        task = self._create_test_task(task_service, "任务A")
        
        assert dep_service.check_dependencies_ready(task["id"]) is True
