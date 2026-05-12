"""
数据库管理模块
负责数据库连接和会话管理
"""

from typing import Optional
from contextlib import contextmanager

from sqlalchemy import create_engine, MetaData
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.ext.declarative import declarative_base

from core.config import Config


Base = declarative_base()
metadata = MetaData()


class DatabaseManager:
    """
    数据库管理类
    负责管理数据库连接和会话
    """

    _instance: Optional["DatabaseManager"] = None

    def __new__(cls, config: Config = None):
        """
        单例模式，确保只有一个数据库管理器实例

        :param config: 配置对象
        :return: 数据库管理器实例
        """
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self, config: Config = None):
        """
        初始化数据库管理器

        :param config: 配置对象
        """
        if self._initialized:
            return
        self._initialized = True
        self.config = config or Config()
        self._engine = None
        self._SessionLocal = None

    def _create_engine(self):
        """
        创建数据库引擎
        """
        db_url = self.config.get("database.url")
        echo = self.config.get("database.echo", False)
        self._engine = create_engine(
            db_url,
            echo=echo,
            connect_args={"check_same_thread": False} if "sqlite" in db_url else {},
        )

    def _create_session_factory(self):
        """
        创建会话工厂
        """
        self._SessionLocal = sessionmaker(
            autocommit=False,
            autoflush=False,
            bind=self._engine,
        )

    @property
    def engine(self):
        """
        获取数据库引擎
        """
        if self._engine is None:
            self._create_engine()
        return self._engine

    @property
    def SessionLocal(self):
        """
        获取会话工厂
        """
        if self._SessionLocal is None:
            self._create_session_factory()
        return self._SessionLocal

    def create_tables(self):
        """
        创建所有数据表
        """
        from core.models.task import Task
        from core.models.execution_log import ExecutionLog
        from core.models.task_dependency import TaskDependency
        Base.metadata.create_all(bind=self.engine)

    def drop_tables(self):
        """
        删除所有数据表
        """
        from core.models.task import Task
        from core.models.execution_log import ExecutionLog
        from core.models.task_dependency import TaskDependency
        Base.metadata.drop_all(bind=self.engine)

    @contextmanager
    def get_session(self):
        """
        获取数据库会话的上下文管理器

        :yield: 数据库会话
        """
        session: Session = self.SessionLocal()
        try:
            yield session
            session.commit()
        except Exception:
            session.rollback()
            raise
        finally:
            session.close()

    def close(self):
        """
        关闭数据库连接
        """
        if self._engine:
            self._engine.dispose()
            self._engine = None
            self._SessionLocal = None
