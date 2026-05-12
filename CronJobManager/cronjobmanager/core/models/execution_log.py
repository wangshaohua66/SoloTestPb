"""
执行日志数据模型
记录任务执行的详细信息
"""

import enum
from datetime import datetime
from typing import Dict, Any

from sqlalchemy import Column, String, Integer, Text, DateTime, ForeignKey, Enum as SAEnum
from sqlalchemy.orm import relationship

from core.database import Base


class ExecutionStatus(enum.Enum):
    """
    执行状态枚举
    """
    RUNNING = "running"
    SUCCESS = "success"
    FAILED = "failed"
    SKIPPED = "skipped"
    TIMEOUT = "timeout"


class ExecutionLog(Base):
    """
    执行日志数据模型
    """

    __tablename__ = "execution_logs"

    id = Column(String(36), primary_key=True, nullable=False, comment="日志ID")
    task_id = Column(String(36), ForeignKey("tasks.id", ondelete="CASCADE"), nullable=False, index=True, comment="任务ID")
    execution_id = Column(String(36), nullable=False, unique=True, index=True, comment="执行实例ID")
    
    status = Column(SAEnum(ExecutionStatus), nullable=False, comment="执行状态")
    start_time = Column(DateTime, nullable=False, comment="开始时间")
    end_time = Column(DateTime, nullable=True, comment="结束时间")
    duration_ms = Column(Integer, nullable=True, comment="执行耗时（毫秒）")
    
    retry_count = Column(Integer, default=0, nullable=False, comment="重试次数")
    
    output = Column(Text, nullable=True, comment="执行输出")
    error_message = Column(Text, nullable=True, comment="错误信息")
    error_traceback = Column(Text, nullable=True, comment="错误堆栈")
    
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False, comment="创建时间")
    
    task = relationship("Task", backref="execution_logs")
    
    def to_dict(self) -> Dict[str, Any]:
        """
        将执行日志转换为字典

        :return: 执行日志字典
        """
        return {
            "id": self.id,
            "task_id": self.task_id,
            "execution_id": self.execution_id,
            "status": self.status.value if self.status else None,
            "start_time": self.start_time.isoformat() if self.start_time else None,
            "end_time": self.end_time.isoformat() if self.end_time else None,
            "duration_ms": self.duration_ms,
            "retry_count": self.retry_count,
            "output": self.output,
            "error_message": self.error_message,
            "error_traceback": self.error_traceback,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }
