"""
日志服务模块
负责任务执行日志的记录和查询
"""

import uuid
from datetime import datetime
from typing import Optional, List, Dict, Any

from core.database import DatabaseManager
from core.models.execution_log import ExecutionLog, ExecutionStatus
from core.utils.logger import get_logger


logger = get_logger(__name__)


class LogService:
    """
    日志服务类
    负责任务执行日志的记录和查询
    """

    def __init__(self, db_manager: DatabaseManager = None):
        """
        初始化日志服务

        :param db_manager: 数据库管理器
        """
        self.db_manager = db_manager or DatabaseManager()

    def create_execution_log(
        self,
        task_id: str,
        execution_id: str = None,
        status: ExecutionStatus = ExecutionStatus.RUNNING,
    ) -> ExecutionLog:
        """
        创建执行日志

        :param task_id: 任务ID
        :param execution_id: 执行实例ID
        :param status: 执行状态
        :return: 创建的执行日志
        """
        log = ExecutionLog(
            id=str(uuid.uuid4()),
            task_id=task_id,
            execution_id=execution_id or str(uuid.uuid4()),
            status=status,
            start_time=datetime.utcnow(),
        )

        with self.db_manager.get_session() as session:
            session.add(log)
            session.flush()
            log_dict = log.to_dict()
        
        return log_dict

    def update_execution_log(
        self,
        execution_id: str,
        status: ExecutionStatus = None,
        output: str = None,
        error_message: str = None,
        error_traceback: str = None,
        retry_count: int = None,
    ) -> Optional[ExecutionLog]:
        """
        更新执行日志

        :param execution_id: 执行实例ID
        :param status: 执行状态
        :param output: 执行输出
        :param error_message: 错误信息
        :param error_traceback: 错误堆栈
        :param retry_count: 重试次数
        :return: 更新后的执行日志
        """
        with self.db_manager.get_session() as session:
            log = session.query(ExecutionLog).filter(
                ExecutionLog.execution_id == execution_id
            ).first()
            
            if not log:
                return None

            if status is not None:
                log.status = status
            if output is not None:
                log.output = output
            if error_message is not None:
                log.error_message = error_message
            if error_traceback is not None:
                log.error_traceback = error_traceback
            if retry_count is not None:
                log.retry_count = retry_count

            if status in [ExecutionStatus.SUCCESS, ExecutionStatus.FAILED,
                         ExecutionStatus.SKIPPED, ExecutionStatus.TIMEOUT]:
                log.end_time = datetime.utcnow()
                if log.start_time:
                    duration = log.end_time - log.start_time
                    log.duration_ms = int(duration.total_seconds() * 1000)

            updated_log = log.to_dict()
        
        return updated_log

    def get_execution_log(self, execution_id: str) -> Optional[ExecutionLog]:
        """
        根据执行ID获取执行日志

        :param execution_id: 执行实例ID
        :return: 执行日志
        """
        with self.db_manager.get_session() as session:
            log = session.query(ExecutionLog).filter(
                ExecutionLog.execution_id == execution_id
            ).first()
            if log:
                return log.to_dict()
        return None

    def get_task_execution_logs(
        self,
        task_id: str,
        status: ExecutionStatus = None,
        limit: int = 100,
        offset: int = 0,
    ) -> List[ExecutionLog]:
        """
        获取任务的执行日志列表

        :param task_id: 任务ID
        :param status: 执行状态过滤
        :param limit: 限制数量
        :param offset: 偏移量
        :return: 执行日志列表
        """
        with self.db_manager.get_session() as session:
            query = session.query(ExecutionLog).filter(
                ExecutionLog.task_id == task_id
            )

            if status:
                query = query.filter(ExecutionLog.status == status)

            logs = query.order_by(
                ExecutionLog.start_time.desc()
            ).limit(limit).offset(offset).all()
            
            return [log.to_dict() for log in logs]

    def get_recent_execution_logs(
        self,
        limit: int = 100,
        status: ExecutionStatus = None,
    ) -> List[ExecutionLog]:
        """
        获取最近的执行日志

        :param limit: 限制数量
        :param status: 执行状态过滤
        :return: 执行日志列表
        """
        with self.db_manager.get_session() as session:
            query = session.query(ExecutionLog)

            if status:
                query = query.filter(ExecutionLog.status == status)

            logs = query.order_by(
                ExecutionLog.start_time.desc()
            ).limit(limit).all()
            
            return [log.to_dict() for log in logs]

    def get_task_execution_stats(self, task_id: str) -> Dict[str, Any]:
        """
        获取任务的执行统计信息

        :param task_id: 任务ID
        :return: 统计信息字典
        """
        with self.db_manager.get_session() as session:
            total = session.query(ExecutionLog).filter(
                ExecutionLog.task_id == task_id
            ).count()

            success = session.query(ExecutionLog).filter(
                ExecutionLog.task_id == task_id,
                ExecutionLog.status == ExecutionStatus.SUCCESS,
            ).count()

            failed = session.query(ExecutionLog).filter(
                ExecutionLog.task_id == task_id,
                ExecutionLog.status.in_([
                    ExecutionStatus.FAILED,
                    ExecutionStatus.TIMEOUT,
                ]),
            ).count()

            from sqlalchemy import func
            
            avg_duration_result = session.query(
                func.avg(ExecutionLog.duration_ms)
            ).filter(
                ExecutionLog.task_id == task_id,
                ExecutionLog.duration_ms.isnot(None)
            ).scalar()

            return {
                "task_id": task_id,
                "total_executions": total,
                "success_count": success,
                "failed_count": failed,
                "success_rate": (success / total * 100) if total > 0 else 0,
                "avg_duration_ms": avg_duration_result if avg_duration_result else 0,
            }

    def delete_old_logs(self, days: int = 30) -> int:
        """
        删除指定天数前的旧日志

        :param days: 保留天数
        :return: 删除的日志数量
        """
        from datetime import timedelta

        cutoff_date = datetime.utcnow() - timedelta(days=days)

        with self.db_manager.get_session() as session:
            old_logs = session.query(ExecutionLog).filter(
                ExecutionLog.created_at < cutoff_date
            ).all()

            count = len(old_logs)
            for log in old_logs:
                session.delete(log)

        if count > 0:
            logger.info(f"删除了 {count} 条 {days} 天前的旧日志")
        
        return count
