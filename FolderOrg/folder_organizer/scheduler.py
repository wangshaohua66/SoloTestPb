"""
定时任务模块
负责定时执行文件整理任务
"""

import time
import threading
from typing import Callable, Optional, Dict, Any
import schedule


class Scheduler:
    """
    定时任务调度器类
    基于schedule库实现定时文件整理功能
    """

    def __init__(self, organize_func: Callable[[], Dict[str, Any]]):
        """
        初始化定时任务调度器

        Args:
            organize_func: 执行文件整理的函数，返回整理结果字典
        """
        self.organize_func = organize_func
        self.schedule_thread: Optional[threading.Thread] = None
        self.running = False
        self.logger: Optional[Any] = None

    def set_logger(self, logger: Any) -> None:
        """
        设置日志记录器

        Args:
            logger: 日志记录器实例
        """
        self.logger = logger

    def _log(self, message: str, level: str = "info") -> None:
        """
        记录日志

        Args:
            message: 日志消息
            level: 日志级别
        """
        if self.logger:
            log_method = getattr(self.logger, level, None)
            if log_method:
                log_method(message)

    def _run_schedule(self) -> None:
        """
        运行定时任务循环
        """
        while self.running:
            schedule.run_pending()
            time.sleep(1)

    def start(self) -> bool:
        """
        启动定时任务

        Returns:
            是否成功启动
        """
        if self.running:
            self._log("定时任务已经在运行中", "warning")
            return False
        
        self.running = True
        self._log("定时整理任务已启动")
        self.schedule_thread = threading.Thread(target=self._run_schedule, daemon=True)
        self.schedule_thread.start()
        return True

    def stop(self) -> bool:
        """
        停止定时任务

        Returns:
            是否成功停止
        """
        if not self.running:
            self._log("定时任务已经停止", "warning")
            return False
        
        self.running = False
        schedule.clear()
        self._log("定时整理任务已停止")
        return True

    def schedule_daily(self, time_str: str = "00:00") -> None:
        """
        配置每日定时任务

        Args:
            time_str: 执行时间，格式为 "HH:MM"
        """
        schedule.clear()
        schedule.every().day.at(time_str).do(self._execute_organize)
        self._log(f"已配置每日 {time_str} 执行整理任务")

    def schedule_hourly(self, interval: int = 1) -> None:
        """
        配置每小时定时任务

        Args:
            interval: 间隔小时数
        """
        schedule.clear()
        schedule.every(interval).hours.do(self._execute_organize)
        self._log(f"已配置每 {interval} 小时执行整理任务")

    def schedule_minutes(self, interval: int = 30) -> None:
        """
        配置每分钟定时任务

        Args:
            interval: 间隔分钟数
        """
        schedule.clear()
        schedule.every(interval).minutes.do(self._execute_organize)
        self._log(f"已配置每 {interval} 分钟执行整理任务")

    def schedule_weekly(self, day: str = "monday", time_str: str = "00:00") -> None:
        """
        配置每周定时任务

        Args:
            day: 星期几（monday, tuesday, ...）
            time_str: 执行时间，格式为 "HH:MM"
        """
        schedule.clear()
        weekly_jobs = {
            "monday": schedule.every().monday,
            "tuesday": schedule.every().tuesday,
            "wednesday": schedule.every().wednesday,
            "thursday": schedule.every().thursday,
            "friday": schedule.every().friday,
            "saturday": schedule.every().saturday,
            "sunday": schedule.every().sunday,
        }
        
        if day.lower() in weekly_jobs:
            weekly_jobs[day.lower()].at(time_str).do(self._execute_organize)
            self._log(f"已配置每周 {day} {time_str} 执行整理任务")
        else:
            self._log(f"无效的星期几: {day}", "error")

    def _execute_organize(self) -> Dict[str, Any]:
        """
        执行文件整理任务

        Returns:
            整理结果字典
        """
        self._log("开始执行定时整理任务...")
        try:
            result = self.organize_func()
            self._log(f"定时整理任务执行完成: 移动 {result.get('moved_files', 0)} 个文件")
            return result
        except Exception as e:
            self._log(f"定时整理任务执行失败: {e}", "error")
            return {"error": str(e)}

    def is_running(self) -> bool:
        """
        检查定时任务是否在运行

        Returns:
            是否在运行
        """
        return self.running

    def get_pending_jobs(self) -> list:
        """
        获取待执行的任务列表

        Returns:
            待执行任务列表
        """
        return schedule.get_jobs()
