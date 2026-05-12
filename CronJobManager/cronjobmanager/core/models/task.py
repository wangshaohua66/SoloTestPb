"""
任务数据模型
定义定时任务的数据结构
"""

import enum
from datetime import datetime
from typing import Optional, Dict, Any

from sqlalchemy import Column, String, Integer, Boolean, Text, DateTime, JSON, Enum as SAEnum

from core.database import Base


class TaskType(enum.Enum):
    """
    任务类型枚举
    """
    CRON = "cron"
    INTERVAL = "interval"
    DATE = "date"


class TaskStatus(enum.Enum):
    """
    任务状态枚举
    """
    PENDING = "pending"
    RUNNING = "running"
    SUCCESS = "success"
    FAILED = "failed"
    PAUSED = "paused"
    COMPLETED = "completed"


class Task(Base):
    """
    任务数据模型
    """

    __tablename__ = "tasks"

    id = Column(String(36), primary_key=True, nullable=False, comment="任务ID")
    name = Column(String(100), nullable=False, index=True, comment="任务名称")
    description = Column(String(500), nullable=True, comment="任务描述")
    task_type = Column(SAEnum(TaskType), nullable=False, comment="任务类型")
    
    func_path = Column(String(500), nullable=False, comment="执行函数路径")
    args = Column(JSON, nullable=True, default=list, comment="函数位置参数")
    kwargs = Column(JSON, nullable=True, default=dict, comment="函数关键字参数")
    
    cron_expression = Column(String(100), nullable=True, comment="Cron表达式")
    interval_seconds = Column(Integer, nullable=True, comment="间隔执行秒数")
    run_date = Column(DateTime, nullable=True, comment="一次性任务执行时间")
    
    status = Column(SAEnum(TaskStatus), default=TaskStatus.PENDING, nullable=False, comment="任务状态")
    enabled = Column(Boolean, default=True, nullable=False, comment="是否启用")
    
    max_retries = Column(Integer, default=3, nullable=False, comment="最大重试次数")
    retry_interval = Column(Integer, default=5, nullable=False, comment="重试间隔秒数")
    backoff_factor = Column(Integer, default=2, nullable=False, comment="退避因子")
    
    timeout = Column(Integer, nullable=True, comment="超时时间（秒）")
    
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False, comment="创建时间")
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False, comment="更新时间")
    last_run_at = Column(DateTime, nullable=True, comment="上次执行时间")
    next_run_at = Column(DateTime, nullable=True, comment="下次执行时间")
    
    success_count = Column(Integer, default=0, nullable=False, comment="成功执行次数")
    failure_count = Column(Integer, default=0, nullable=False, comment="失败执行次数")
    
    metadata_ = Column("metadata", JSON, nullable=True, default=dict, comment="额外元数据")
    
    def to_dict(self) -> Dict[str, Any]:
        """
        将任务转换为字典

        :return: 任务字典
        """
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "task_type": self.task_type.value if self.task_type else None,
            "func_path": self.func_path,
            "args": self.args,
            "kwargs": self.kwargs,
            "cron_expression": self.cron_expression,
            "interval_seconds": self.interval_seconds,
            "run_date": self.run_date.isoformat() if self.run_date else None,
            "status": self.status.value if self.status else None,
            "enabled": self.enabled,
            "max_retries": self.max_retries,
            "retry_interval": self.retry_interval,
            "backoff_factor": self.backoff_factor,
            "timeout": self.timeout,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
            "last_run_at": self.last_run_at.isoformat() if self.last_run_at else None,
            "next_run_at": self.next_run_at.isoformat() if self.next_run_at else None,
            "success_count": self.success_count,
            "failure_count": self.failure_count,
            "metadata": self.metadata_,
        }
