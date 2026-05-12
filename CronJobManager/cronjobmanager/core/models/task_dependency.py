"""
任务依赖关系数据模型
管理任务之间的依赖关系
"""

import enum
from datetime import datetime
from typing import Dict, Any

from sqlalchemy import Column, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship

from core.database import Base


class DependencyCondition(enum.Enum):
    """
    依赖条件枚举
    定义前置任务完成后触发后续任务的条件
    """
    SUCCESS = "success"
    COMPLETION = "completion"
    ALWAYS = "always"


class TaskDependency(Base):
    """
    任务依赖关系数据模型
    """

    __tablename__ = "task_dependencies"

    id = Column(String(36), primary_key=True, nullable=False, comment="依赖关系ID")
    
    dependent_task_id = Column(
        String(36), 
        ForeignKey("tasks.id", ondelete="CASCADE"), 
        nullable=False, 
        index=True,
        comment="依赖任务ID（后续任务）"
    )
    dependency_task_id = Column(
        String(36), 
        ForeignKey("tasks.id", ondelete="CASCADE"), 
        nullable=False, 
        index=True,
        comment="前置任务ID"
    )
    
    condition = Column(
        String(20), 
        default=DependencyCondition.SUCCESS.value, 
        nullable=False,
        comment="触发条件"
    )
    
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False, comment="创建时间")
    
    dependent_task = relationship(
        "Task", 
        foreign_keys=[dependent_task_id],
        backref="dependencies"
    )
    dependency_task = relationship(
        "Task", 
        foreign_keys=[dependency_task_id],
        backref="dependents"
    )
    
    def to_dict(self) -> Dict[str, Any]:
        """
        将依赖关系转换为字典

        :return: 依赖关系字典
        """
        return {
            "id": self.id,
            "dependent_task_id": self.dependent_task_id,
            "dependency_task_id": self.dependency_task_id,
            "condition": self.condition,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }
