"""
任务依赖服务模块
管理任务之间的依赖关系
"""

import uuid
from typing import Optional, List

from core.database import DatabaseManager
from core.models.task import Task, TaskStatus
from core.models.task_dependency import TaskDependency, DependencyCondition
from core.utils.logger import get_logger


logger = get_logger(__name__)


class DependencyService:
    """
    任务依赖服务类
    管理任务之间的依赖关系
    """

    def __init__(self, db_manager: DatabaseManager = None):
        """
        初始化依赖服务

        :param db_manager: 数据库管理器
        """
        self.db_manager = db_manager or DatabaseManager()

    def add_dependency(
        self,
        dependent_task_id: str,
        dependency_task_id: str,
        condition: DependencyCondition = DependencyCondition.SUCCESS,
    ) -> TaskDependency:
        """
        添加任务依赖关系

        :param dependent_task_id: 依赖任务ID（后续任务）
        :param dependency_task_id: 前置任务ID
        :param condition: 触发条件
        :return: 创建的依赖关系
        :raises ValueError: 当循环依赖检测失败时抛出
        """
        if dependent_task_id == dependency_task_id:
            raise ValueError("任务不能依赖自身")

        if self._check_circular_dependency(dependent_task_id, dependency_task_id):
            raise ValueError(f"检测到循环依赖: {dependent_task_id} -> {dependency_task_id}")

        if isinstance(condition, DependencyCondition):
            condition_value = condition.value
        else:
            condition_value = condition

        dependency = TaskDependency(
            id=str(uuid.uuid4()),
            dependent_task_id=dependent_task_id,
            dependency_task_id=dependency_task_id,
            condition=condition_value,
        )

        with self.db_manager.get_session() as session:
            session.add(dependency)
            session.flush()
            dep_dict = dependency.to_dict()
        
        logger.info(f"添加依赖关系: {dependency_task_id} -> {dependent_task_id}")
        return dep_dict

    def _check_circular_dependency(
        self,
        dependent_task_id: str,
        dependency_task_id: str,
    ) -> bool:
        """
        检查是否存在循环依赖

        :param dependent_task_id: 依赖任务ID
        :param dependency_task_id: 前置任务ID
        :return: 是否存在循环依赖
        """
        visited = set()
        to_visit = [dependency_task_id]

        while to_visit:
            current = to_visit.pop(0)
            if current == dependent_task_id:
                return True
            if current in visited:
                continue
            visited.add(current)

            with self.db_manager.get_session() as session:
                dependencies = session.query(TaskDependency).filter(
                    TaskDependency.dependent_task_id == current
                ).all()
                for dep in dependencies:
                    if dep.dependency_task_id not in visited:
                        to_visit.append(dep.dependency_task_id)

        return False

    def get_dependencies(self, task_id: str) -> List[TaskDependency]:
        """
        获取任务的所有前置依赖

        :param task_id: 任务ID
        :return: 依赖关系列表
        """
        with self.db_manager.get_session() as session:
            dependencies = session.query(TaskDependency).filter(
                TaskDependency.dependent_task_id == task_id
            ).all()
            return [dep.to_dict() for dep in dependencies]

    def get_dependents(self, task_id: str) -> List[TaskDependency]:
        """
        获取依赖此任务的所有后续任务

        :param task_id: 任务ID
        :return: 依赖关系列表
        """
        with self.db_manager.get_session() as session:
            dependents = session.query(TaskDependency).filter(
                TaskDependency.dependency_task_id == task_id
            ).all()
            return [dep.to_dict() for dep in dependents]

    def remove_dependency(self, dependency_id: str) -> bool:
        """
        删除依赖关系

        :param dependency_id: 依赖关系ID
        :return: 是否删除成功
        """
        with self.db_manager.get_session() as session:
            dependency = session.query(TaskDependency).filter(
                TaskDependency.id == dependency_id
            ).first()
            if not dependency:
                return False
            
            session.delete(dependency)
        
        logger.info(f"删除依赖关系: {dependency_id}")
        return True

    def remove_all_dependencies(self, task_id: str) -> int:
        """
        删除与任务相关的所有依赖关系

        :param task_id: 任务ID
        :return: 删除的依赖关系数量
        """
        with self.db_manager.get_session() as session:
            dependencies = session.query(TaskDependency).filter(
                (TaskDependency.dependent_task_id == task_id) |
                (TaskDependency.dependency_task_id == task_id)
            ).all()
            
            count = len(dependencies)
            for dep in dependencies:
                session.delete(dep)
        
        if count > 0:
            logger.info(f"删除任务 {task_id} 的所有依赖关系，共 {count} 个")
        return count

    def check_dependencies_ready(self, task_id: str) -> bool:
        """
        检查任务的所有前置依赖是否已满足

        :param task_id: 任务ID
        :return: 所有依赖是否已满足
        """
        with self.db_manager.get_session() as session:
            dependencies = session.query(TaskDependency).filter(
                TaskDependency.dependent_task_id == task_id
            ).all()

            if not dependencies:
                return True

            for dep in dependencies:
                dependency_task = session.query(Task).filter(
                    Task.id == dep.dependency_task_id
                ).first()

                if not dependency_task:
                    return False

                if dep.condition == DependencyCondition.SUCCESS.value:
                    if dependency_task.status != TaskStatus.SUCCESS:
                        return False
                elif dep.condition == DependencyCondition.COMPLETION.value:
                    if dependency_task.status not in [
                        TaskStatus.SUCCESS,
                        TaskStatus.FAILED,
                        TaskStatus.COMPLETED,
                    ]:
                        return False
                elif dep.condition == DependencyCondition.ALWAYS.value:
                    continue

            return True
