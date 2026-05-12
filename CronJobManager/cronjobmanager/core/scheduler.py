"""
任务调度器模块
负责任务的调度和执行
"""

import uuid
import time
import traceback
from datetime import datetime, timedelta
from typing import Optional, Dict, Any, List
from threading import RLock

from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from apscheduler.triggers.interval import IntervalTrigger
from apscheduler.triggers.date import DateTrigger
from apscheduler.jobstores.memory import MemoryJobStore
from apscheduler.executors.pool import ThreadPoolExecutor

from core.config import Config
from core.database import DatabaseManager
from core.models.task import Task, TaskType, TaskStatus
from core.models.execution_log import ExecutionStatus
from core.services.task_service import TaskService
from core.services.dependency_service import DependencyService
from core.services.log_service import LogService
from core.services.alert_service import AlertService
from core.utils.function_loader import load_function, execute_function, FunctionLoadError, FunctionTimeoutError, shutdown_executor
from core.utils.logger import get_logger


logger = get_logger(__name__)


class TaskScheduler:
    """
    任务调度器类
    负责任务的调度、执行和管理
    """

    _instance: Optional["TaskScheduler"] = None
    _lock = RLock()

    def __new__(cls, config: Config = None):
        """
        单例模式，确保只有一个调度器实例

        :param config: 配置对象
        :return: 调度器实例
        """
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
                    cls._instance._initialized = False
        return cls._instance

    def __init__(self, config: Config = None):
        """
        初始化任务调度器

        :param config: 配置对象
        """
        if self._initialized:
            return
        self._initialized = True
        
        self.config = config or Config()
        self.db_manager = DatabaseManager(self.config)
        
        self.task_service = TaskService(self.db_manager)
        self.dependency_service = DependencyService(self.db_manager)
        self.log_service = LogService(self.db_manager)
        self.alert_service = AlertService(self.config)
        
        self._scheduler = None
        self._running = False
        self._job_map: Dict[str, str] = {}
        self._async_executor = ThreadPoolExecutor(max_workers=20)

    def _create_scheduler(self) -> BackgroundScheduler:
        """
        创建APScheduler调度器实例

        :return: 调度器实例
        """
        timezone = self.config.get("scheduler.timezone", "Asia/Shanghai")
        max_concurrent_jobs = self.config.get("scheduler.max_concurrent_jobs", 100)
        misfire_grace_time = self.config.get("scheduler.misfire_grace_time", 30)

        jobstores = {
            "default": MemoryJobStore(),
        }

        executors = {
            "default": ThreadPoolExecutor(max_workers=max_concurrent_jobs),
        }

        job_defaults = {
            "coalesce": True,
            "max_instances": 1,
            "misfire_grace_time": misfire_grace_time,
        }

        return BackgroundScheduler(
            jobstores=jobstores,
            executors=executors,
            job_defaults=job_defaults,
            timezone=timezone,
        )

    def start(self) -> None:
        """
        启动调度器
        """
        if self._running:
            logger.warning("调度器已经在运行中")
            return

        self.db_manager.create_tables()
        self._scheduler = self._create_scheduler()
        self._scheduler.start()
        self._running = True
        
        self._reload_persisted_jobs()
        
        logger.info("任务调度器已启动")

    def stop(self, wait: bool = True) -> None:
        """
        停止调度器

        :param wait: 是否等待当前任务执行完成
        """
        if not self._running:
            return

        if self._scheduler:
            self._scheduler.shutdown(wait=wait)
        
        if self._async_executor:
            self._async_executor.shutdown(wait=wait)
        
        shutdown_executor()
        
        self._running = False
        self._job_map.clear()
        self.db_manager.close()
        
        logger.info("任务调度器已停止")

    def _reload_persisted_jobs(self) -> None:
        """
        重新加载持久化的任务
        """
        enabled_tasks = self.task_service.list_tasks(enabled=True)
        
        for task in enabled_tasks:
            try:
                self._register_job(task)
                logger.info(f"重新加载任务: {task['name']} ({task['id']})")
            except Exception as e:
                logger.error(f"重新加载任务失败 {task['id']}: {str(e)}")

    def add_task(
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
        dependencies: List[Dict[str, Any]] = None,
    ) -> Task:
        """
        添加新任务

        :param name: 任务名称
        :param func_path: 执行函数路径
        :param task_type: 任务类型
        :param description: 任务描述
        :param args: 函数位置参数
        :param kwargs: 函数关键字参数
        :param cron_expression: Cron表达式
        :param interval_seconds: 间隔秒数
        :param run_date: 执行时间
        :param max_retries: 最大重试次数
        :param retry_interval: 重试间隔秒数
        :param backoff_factor: 退避因子
        :param timeout: 超时时间
        :param dependencies: 依赖关系列表
        :return: 创建的任务对象
        """
        task = self.task_service.create_task(
            name=name,
            func_path=func_path,
            task_type=task_type,
            description=description,
            args=args,
            kwargs=kwargs,
            cron_expression=cron_expression,
            interval_seconds=interval_seconds,
            run_date=run_date,
            max_retries=max_retries,
            retry_interval=retry_interval,
            backoff_factor=backoff_factor,
            timeout=timeout,
        )

        if dependencies:
            for dep in dependencies:
                self.dependency_service.add_dependency(
                    dependent_task_id=task["id"],
                    dependency_task_id=dep["dependency_task_id"],
                    condition=dep.get("condition", "success"),
                )

        if self._running and task["enabled"]:
            self._register_job(task)

        return task

    def _register_job(self, task: Dict[str, Any]) -> None:
        """
        注册任务到APScheduler

        :param task: 任务字典
        """
        task_id = task["id"]
        trigger = self._create_trigger(task)

        if not trigger:
            logger.error(f"无法创建触发器，任务类型无效: {task['task_type']}")
            return

        job = self._scheduler.add_job(
            func=self._execute_task,
            trigger=trigger,
            id=task_id,
            name=task["name"],
            args=[task_id],
            replace_existing=True,
        )

        self._job_map[task_id] = job.id
        logger.info(f"任务已注册: {task['name']} ({task_id})")

    def _create_trigger(self, task: Dict[str, Any]):
        """
        根据任务类型创建触发器

        :param task: 任务字典
        :return: APScheduler触发器
        """
        task_type = task["task_type"]
        timezone = self.config.get("scheduler.timezone", "Asia/Shanghai")

        if task_type == TaskType.CRON.value:
            return CronTrigger.from_crontab(task["cron_expression"], timezone=timezone)
        
        elif task_type == TaskType.INTERVAL.value:
            return IntervalTrigger(seconds=task["interval_seconds"], timezone=timezone)
        
        elif task_type == TaskType.DATE.value:
            run_date = task["run_date"]
            if isinstance(run_date, str):
                from dateutil import parser
                run_date = parser.isoparse(run_date)
            return DateTrigger(run_date=run_date, timezone=timezone)
        
        return None

    def _execute_task(self, task_id: str) -> None:
        """
        执行任务

        :param task_id: 任务ID
        """
        execution_id = str(uuid.uuid4())
        
        task = self.task_service.get_task(task_id)
        if not task:
            logger.error(f"任务不存在: {task_id}")
            return

        if not self.dependency_service.check_dependencies_ready(task_id):
            logger.info(f"任务依赖未满足，跳过执行: {task['name']}")
            return

        if not task["enabled"]:
            logger.info(f"任务已禁用，跳过执行: {task['name']}")
            return

        self._execute_with_retry(task, execution_id)

    def _execute_with_retry(
        self,
        task: Dict[str, Any],
        execution_id: str,
    ) -> None:
        """
        执行任务，带重试机制

        :param task: 任务字典
        :param execution_id: 执行实例ID
        """
        task_id = task["id"]
        max_retries = task["max_retries"]
        retry_interval = task["retry_interval"]
        backoff_factor = task["backoff_factor"]
        
        self.log_service.create_execution_log(task_id, execution_id)
        self.task_service.update_task_status(task_id, TaskStatus.RUNNING)

        retry_count = 0
        last_error = None

        while retry_count <= max_retries:
            try:
                result = self._run_task_function(task)
                
                self.log_service.update_execution_log(
                    execution_id,
                    status=ExecutionStatus.SUCCESS,
                    output=str(result) if result is not None else "",
                    retry_count=retry_count,
                )
                
                self.task_service.update_task_run_info(
                    task_id,
                    last_run_at=datetime.utcnow(),
                    success=True,
                )
                
                if task["task_type"] == TaskType.DATE.value:
                    self.task_service.update_task_status(task_id, TaskStatus.COMPLETED)
                else:
                    self.task_service.update_task_status(task_id, TaskStatus.SUCCESS)

                logger.info(f"任务执行成功: {task['name']} (执行ID: {execution_id}, 重试次数: {retry_count})")
                
                self._trigger_dependent_tasks(task_id, success=True)
                return

            except Exception as e:
                last_error = e
                retry_count += 1
                
                error_traceback = traceback.format_exc()
                
                if retry_count <= max_retries:
                    sleep_time = retry_interval * (backoff_factor ** (retry_count - 1))
                    logger.warning(
                        f"任务执行失败，准备重试 ({retry_count}/{max_retries}): "
                        f"{task['name']}, 错误: {str(e)}, 等待 {sleep_time} 秒"
                    )
                    time.sleep(sleep_time)
                else:
                    logger.error(f"任务执行失败，已达最大重试次数: {task['name']}, 错误: {str(e)}")
                    
                    self.log_service.update_execution_log(
                        execution_id,
                        status=ExecutionStatus.FAILED,
                        error_message=str(e),
                        error_traceback=error_traceback,
                        retry_count=retry_count - 1,
                    )
                    
                    self.task_service.update_task_run_info(
                        task_id,
                        last_run_at=datetime.utcnow(),
                        success=False,
                    )
                    self.task_service.update_task_status(task_id, TaskStatus.FAILED)
                    
                    self.alert_service.send_task_failure_alert(
                        task["name"],
                        task_id,
                        str(e),
                        retry_count - 1,
                    )
                    
                    self._trigger_dependent_tasks(task_id, success=False)
                    return

    def _run_task_function(self, task: Dict[str, Any]) -> Any:
        """
        实际执行任务函数

        :param task: 任务字典
        :return: 函数执行结果
        :raises FunctionTimeoutError: 当任务执行超时时抛出
        """
        func = load_function(task["func_path"])
        args = task.get("args", [])
        kwargs = task.get("kwargs", {})
        timeout = task.get("timeout")

        return execute_function(func, args, kwargs, timeout)

    def _trigger_dependent_tasks(self, task_id: str, success: bool) -> None:
        """
        触发依赖此任务的后续任务（异步执行）

        :param task_id: 任务ID
        :param success: 任务是否执行成功
        """
        dependents = self.dependency_service.get_dependents(task_id)
        
        for dep in dependents:
            dependent_task_id = dep["dependent_task_id"]
            condition = dep["condition"]
            
            should_trigger = False
            if condition == "success" and success:
                should_trigger = True
            elif condition == "completion":
                should_trigger = True
            elif condition == "always":
                should_trigger = True

            if should_trigger and self.dependency_service.check_dependencies_ready(dependent_task_id):
                dependent_task = self.task_service.get_task(dependent_task_id)
                if dependent_task and dependent_task["enabled"]:
                    logger.info(f"异步触发依赖任务: {dependent_task['name']} (ID: {dependent_task_id})")
                    try:
                        self._async_executor.submit(self._execute_task, dependent_task_id)
                    except Exception as e:
                        logger.error(
                            f"异步提交依赖任务失败: {dependent_task['name']} (ID: {dependent_task_id}), "
                            f"错误: {str(e)}"
                        )

    def remove_task(self, task_id: str) -> bool:
        """
        移除任务

        :param task_id: 任务ID
        :return: 是否移除成功
        """
        if task_id in self._job_map:
            try:
                self._scheduler.remove_job(task_id)
            except Exception as e:
                logger.warning(f"从调度器移除任务失败: {str(e)}")
            del self._job_map[task_id]

        self.dependency_service.remove_all_dependencies(task_id)
        return self.task_service.delete_task(task_id)

    def pause_task(self, task_id: str) -> bool:
        """
        暂停任务

        :param task_id: 任务ID
        :return: 是否暂停成功
        """
        if task_id in self._job_map:
            try:
                self._scheduler.pause_job(task_id)
            except Exception as e:
                logger.warning(f"暂停任务失败: {str(e)}")
        
        self.task_service.update_task(task_id, enabled=False)
        self.task_service.update_task_status(task_id, TaskStatus.PAUSED)
        logger.info(f"任务已暂停: {task_id}")
        return True

    def resume_task(self, task_id: str) -> bool:
        """
        恢复任务

        :param task_id: 任务ID
        :return: 是否恢复成功
        """
        task = self.task_service.get_task(task_id)
        if not task:
            return False

        if task_id in self._job_map:
            try:
                self._scheduler.resume_job(task_id)
            except Exception:
                if self._running:
                    self._register_job(task)
        elif self._running:
            self._register_job(task)

        self.task_service.update_task(task_id, enabled=True)
        self.task_service.update_task_status(task_id, TaskStatus.PENDING)
        logger.info(f"任务已恢复: {task_id}")
        return True

    def run_task_now(self, task_id: str) -> str:
        """
        立即执行任务

        :param task_id: 任务ID
        :return: 执行ID
        """
        execution_id = str(uuid.uuid4())
        self._execute_task(task_id)
        return execution_id

    def get_task_status(self, task_id: str) -> Optional[Dict[str, Any]]:
        """
        获取任务状态

        :param task_id: 任务ID
        :return: 任务状态信息
        """
        return self.task_service.get_task(task_id)

    def list_tasks(self, **kwargs) -> List[Dict[str, Any]]:
        """
        列出任务列表

        :param kwargs: 过滤参数
        :return: 任务列表
        """
        return self.task_service.list_tasks(**kwargs)

    @property
    def running(self) -> bool:
        """
        调度器是否正在运行

        :return: 是否正在运行
        """
        return self._running
