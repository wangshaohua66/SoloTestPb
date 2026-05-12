"""
任务服务模块
负责任务的增删改查操作
"""

import uuid
from datetime import datetime
from typing import Optional, List, Dict, Any

from sqlalchemy.orm import Session

from core.database import DatabaseManager
from core.models.task import Task, TaskType, TaskStatus
from core.utils.logger import get_logger


logger = get_logger(__name__)


class TaskService:
    """
    任务服务类
    提供任务的CRUD操作
    """

    def __init__(self, db_manager: DatabaseManager = None):
        """
        初始化任务服务

        :param db_manager: 数据库管理器
        """
        self.db_manager = db_manager or DatabaseManager()

    def create_task(
        self,
        name: str,
        func_path: str,
        task_type: TaskType,
        description: str = None,
        args: list = None,
        kwargs: dict = None,
        cron_expression: str = None,
        interval_seconds: int = None,
        run_date: datetime = None,
        max_retries: int = 3,
        retry_interval: int = 5,
        backoff_factor: int = 2,
        timeout: int = None,
        metadata: Dict[str, Any] = None,
    ) -> Task:
        """
        创建新任务

        :param name: 任务名称
        :param func_path: 执行函数路径
        :param task_type: 任务类型
        :param description: 任务描述
        :param args: 函数位置参数
        :param kwargs: 函数关键字参数
        :param cron_expression: Cron表达式（Cron任务必需）
        :param interval_seconds: 间隔秒数（Interval任务必需）
        :param run_date: 执行时间（Date任务必需）
        :param max_retries: 最大重试次数
        :param retry_interval: 重试间隔秒数
        :param backoff_factor: 退避因子
        :param timeout: 超时时间
        :param metadata: 额外元数据
        :return: 创建的任务对象
        """
        self._validate_task_params(task_type, cron_expression, interval_seconds, run_date)

        task = Task(
            id=str(uuid.uuid4()),
            name=name,
            description=description,
            task_type=task_type,
            func_path=func_path,
            args=args or [],
            kwargs=kwargs or {},
            cron_expression=cron_expression,
            interval_seconds=interval_seconds,
            run_date=run_date,
            max_retries=max_retries,
            retry_interval=retry_interval,
            backoff_factor=backoff_factor,
            timeout=timeout,
            metadata_=metadata or {},
        )

        with self.db_manager.get_session() as session:
            session.add(task)
            session.flush()
            task_dict = task.to_dict()
        
        logger.info(f"任务创建成功: {task_dict['id']} ({task_dict['name']})")
        return task_dict

    def _validate_task_params(
        self,
        task_type: TaskType,
        cron_expression: str,
        interval_seconds: int,
        run_date: datetime,
    ) -> None:
        """
        验证任务参数

        :param task_type: 任务类型
        :param cron_expression: Cron表达式
        :param interval_seconds: 间隔秒数
        :param run_date: 执行时间
        :raises ValueError: 参数验证失败时抛出
        """
        if task_type == TaskType.CRON and not cron_expression:
            raise ValueError("Cron任务需要提供cron_expression参数")
        if task_type == TaskType.INTERVAL and not interval_seconds:
            raise ValueError("Interval任务需要提供interval_seconds参数")
        if task_type == TaskType.DATE and not run_date:
            raise ValueError("Date任务需要提供run_date参数")

    def get_task(self, task_id: str) -> Optional[Task]:
        """
        根据ID获取任务

        :param task_id: 任务ID
        :return: 任务对象，如果不存在返回None
        """
        with self.db_manager.get_session() as session:
            task = session.query(Task).filter(Task.id == task_id).first()
            if task:
                return task.to_dict()
        return None

    def get_task_by_name(self, name: str) -> Optional[Task]:
        """
        根据名称获取任务

        :param name: 任务名称
        :return: 任务对象，如果不存在返回None
        """
        with self.db_manager.get_session() as session:
            task = session.query(Task).filter(Task.name == name).first()
            if task:
                return task.to_dict()
        return None

    def list_tasks(
        self,
        status: TaskStatus = None,
        task_type: TaskType = None,
        enabled: bool = None,
        limit: int = 100,
        offset: int = 0,
    ) -> List[Task]:
        """
        列出任务列表

        :param status: 任务状态过滤
        :param task_type: 任务类型过滤
        :param enabled: 是否启用过滤
        :param limit: 限制数量
        :param offset: 偏移量
        :return: 任务列表
        """
        with self.db_manager.get_session() as session:
            query = session.query(Task)
            
            if status:
                query = query.filter(Task.status == status)
            if task_type:
                query = query.filter(Task.task_type == task_type)
            if enabled is not None:
                query = query.filter(Task.enabled == enabled)
            
            tasks = query.order_by(Task.created_at.desc()).limit(limit).offset(offset).all()
            return [task.to_dict() for task in tasks]

    def update_task(self, task_id: str, **kwargs) -> Optional[Task]:
        """
        更新任务

        :param task_id: 任务ID
        :param kwargs: 要更新的字段
        :return: 更新后的任务对象，如果不存在返回None
        """
        update_fields = {
            key: value
            for key, value in kwargs.items()
            if key in [
                "name", "description", "func_path", "args", "kwargs",
                "cron_expression", "interval_seconds", "run_date",
                "max_retries", "retry_interval", "backoff_factor",
                "timeout", "enabled", "metadata_",
            ]
        }

        if not update_fields:
            return None

        with self.db_manager.get_session() as session:
            task = session.query(Task).filter(Task.id == task_id).first()
            if not task:
                return None
            
            for key, value in update_fields.items():
                setattr(task, key, value)
            
            task.updated_at = datetime.utcnow()
            updated_task = task.to_dict()
        
        logger.info(f"任务更新成功: {task_id}")
        return updated_task

    def delete_task(self, task_id: str) -> bool:
        """
        删除任务

        :param task_id: 任务ID
        :return: 是否删除成功
        """
        with self.db_manager.get_session() as session:
            task = session.query(Task).filter(Task.id == task_id).first()
            if not task:
                return False
            
            session.delete(task)
        
        logger.info(f"任务删除成功: {task_id}")
        return True

    def update_task_status(self, task_id: str, status: TaskStatus) -> Optional[Task]:
        """
        更新任务状态

        :param task_id: 任务ID
        :param status: 新状态
        :return: 更新后的任务对象
        """
        with self.db_manager.get_session() as session:
            task = session.query(Task).filter(Task.id == task_id).first()
            if not task:
                return None
            
            task.status = status
            task.updated_at = datetime.utcnow()
            updated_task = task.to_dict()
        
        return updated_task

    def update_task_run_info(
        self,
        task_id: str,
        last_run_at: datetime = None,
        next_run_at: datetime = None,
        success: bool = True,
    ) -> Optional[Task]:
        """
        更新任务执行信息

        :param task_id: 任务ID
        :param last_run_at: 上次执行时间
        :param next_run_at: 下次执行时间
        :param success: 是否执行成功
        :return: 更新后的任务对象
        """
        with self.db_manager.get_session() as session:
            task = session.query(Task).filter(Task.id == task_id).first()
            if not task:
                return None
            
            if last_run_at:
                task.last_run_at = last_run_at
            if next_run_at:
                task.next_run_at = next_run_at
            
            if success:
                task.success_count += 1
            else:
                task.failure_count += 1
            
            task.updated_at = datetime.utcnow()
            updated_task = task.to_dict()
        
        return updated_task
