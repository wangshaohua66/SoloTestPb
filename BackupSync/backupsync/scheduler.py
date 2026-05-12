# -*- coding: utf-8 -*-
"""
定时任务调度模块
提供定时自动执行备份任务的功能
"""
import time
import schedule
from datetime import datetime
from typing import Callable, Optional, Dict, Any


class BackupScheduler:
    """
    备份调度器类，用于设置和管理定时备份任务
    """
    
    def __init__(self, backup_func: Callable[[], Dict[str, Any]]):
        """
        初始化备份调度器
        
        参数:
            backup_func: 执行备份的函数，返回备份统计信息
        """
        self.backup_func = backup_func
        self._running = False
        self._last_run_time: Optional[datetime] = None
        self._run_count = 0
    
    def schedule_daily(self, time_str: str) -> None:
        """
        设置每日定时备份
        
        参数:
            time_str: 执行时间，格式为"HH:MM"（24小时制）
        """
        schedule.every().day.at(time_str).do(self._run_backup)
    
    def schedule_hourly(self, minute: int = 0) -> None:
        """
        设置每小时定时备份
        
        参数:
            minute: 每小时的第几分钟执行（0-59）
        """
        schedule.every().hour.at(f":{minute:02d}").do(self._run_backup)
    
    def schedule_minutely(self, interval: int = 1) -> None:
        """
        设置每隔几分钟执行备份
        
        参数:
            interval: 间隔分钟数
        """
        schedule.every(interval).minutes.do(self._run_backup)
    
    def schedule_weekly(self, day: str, time_str: str) -> None:
        """
        设置每周定时备份
        
        参数:
            day: 星期几，可选值: monday, tuesday, wednesday, thursday, friday, saturday, sunday
            time_str: 执行时间，格式为"HH:MM"
        """
        week_days = {
            'monday': schedule.every().monday,
            'tuesday': schedule.every().tuesday,
            'wednesday': schedule.every().wednesday,
            'thursday': schedule.every().thursday,
            'friday': schedule.every().friday,
            'saturday': schedule.every().saturday,
            'sunday': schedule.every().sunday
        }
        
        if day.lower() not in week_days:
            raise ValueError(f"无效的星期几: {day}")
        
        week_days[day.lower()].at(time_str).do(self._run_backup)
    
    def clear_schedule(self) -> None:
        """
        清除所有已设置的定时任务
        """
        schedule.clear()
    
    def _run_backup(self) -> None:
        """
        执行备份任务的内部方法
        """
        try:
            stats = self.backup_func()
            self._last_run_time = datetime.now()
            self._run_count += 1
            print(f"[{self._last_run_time.strftime('%Y-%m-%d %H:%M:%S')}] 备份完成: "
                  f"新增{stats.get('added_count', 0)}个, "
                  f"修改{stats.get('modified_count', 0)}个, "
                  f"删除{stats.get('deleted_count', 0)}个")
        except Exception as e:
            print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] 备份失败: {e}")
    
    def run_pending(self) -> None:
        """
        运行所有到期的定时任务
        """
        schedule.run_pending()
    
    def start(self, check_interval: int = 1) -> None:
        """
        启动定时任务调度器（阻塞运行）
        
        参数:
            check_interval: 检查任务是否到期的间隔秒数
        """
        self._running = True
        print(f"定时备份调度器已启动，检查间隔: {check_interval}秒")
        
        try:
            while self._running:
                self.run_pending()
                time.sleep(check_interval)
        except KeyboardInterrupt:
            print("\n定时备份调度器已停止")
            self._running = False
    
    def stop(self) -> None:
        """
        停止定时任务调度器
        """
        self._running = False
    
    def is_running(self) -> bool:
        """
        检查调度器是否正在运行
        
        返回:
            如果调度器正在运行则返回True，否则返回False
        """
        return self._running
    
    def get_stats(self) -> Dict[str, Any]:
        """
        获取调度器统计信息
        
        返回:
            包含调度器状态的字典
        """
        return {
            'running': self._running,
            'last_run_time': self._last_run_time.strftime('%Y-%m-%d %H:%M:%S') if self._last_run_time else None,
            'run_count': self._run_count,
            'pending_jobs': len(schedule.get_jobs())
        }
