"""
调度器模块
负责定期执行网站健康检测任务
"""

import logging
from typing import Dict, Any
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.interval import IntervalTrigger
import time
from datetime import datetime

from .config import Config
from .http_checker import HTTPChecker
from .ssl_checker import SSLChecker
from .notifier import NotificationManager
from .reporter import Reporter


class HealthCheckScheduler:
    """
    健康检测调度器类
    负责管理和执行周期性的网站健康检测任务
    """

    def __init__(self, config: Config):
        """
        初始化健康检测调度器

        Args:
            config: 配置管理器实例
        """
        self.config = config
        self.logger = logging.getLogger(__name__)
        self.scheduler = BackgroundScheduler(timezone='Asia/Shanghai')

        self.http_checker = HTTPChecker()
        ssl_config = config.get_ssl_config()
        self.ssl_checker = SSLChecker(alert_days=ssl_config.get('alert_days_before_expiry', 30))
        self.notification_manager = NotificationManager(config.get_notifications())

        report_config = config.get_report_config()
        self.reporter = Reporter(
            output_dir=report_config.get('output_dir', './reports'),
            history_days=report_config.get('history_days', 7)
        )

        self.running = False

    def _check_site(self, site: Dict[str, Any]) -> None:
        """
        执行单个站点的健康检测任务

        Args:
            site: 站点配置字典
        """
        site_name = site.get('name', '未知站点')
        self.logger.info(f"开始检测站点: {site_name}")

        try:
            http_result = self.http_checker.check(site)
            self.reporter.add_result(http_result)

            if not http_result.success:
                self.notification_manager.send_http_alert(http_result)

            if self.config.get_ssl_config().get('check_enabled', True) and site.get('url', '').startswith('https://'):
                ssl_result = self.ssl_checker.check(site)
                if self.ssl_checker.needs_alert(ssl_result):
                    self.notification_manager.send_ssl_alert(ssl_result)

        except Exception as e:
            self.logger.error(f"检测站点 {site_name} 时发生异常: {e}", exc_info=True)

    def _generate_report_job(self) -> None:
        """
        定时生成报告任务
        """
        try:
            self.logger.info("开始执行定时报告生成任务")
            self.reporter.generate_report()
        except Exception as e:
            self.logger.error(f"生成报告时发生异常: {e}", exc_info=True)

    def start(self) -> None:
        """
        启动调度器，开始执行所有检测任务
        """
        if self.running:
            self.logger.warning("调度器已在运行中")
            return

        self.logger.info("正在启动网站健康检测调度器...")

        sites = self.config.get_sites()
        for site in sites:
            site_name = site.get('name', '未知站点')
            interval = site.get('check_interval', 60)
            priority = site.get('priority', 999)

            self.scheduler.add_job(
                self._check_site,
                trigger=IntervalTrigger(seconds=interval),
                args=[site],
                id=f"check_{site_name}_{priority}",
                name=f"检测 {site_name}",
                replace_existing=True
            )

            self.logger.info(f"已添加任务: {site_name}, 检测间隔: {interval}秒, 优先级: {priority}")

        report_config = self.config.get_report_config()
        report_interval = report_config.get('generate_interval', 86400)
        if report_interval > 0:
            self.scheduler.add_job(
                self._generate_report_job,
                trigger=IntervalTrigger(seconds=report_interval),
                id="generate_report",
                name="生成统计报告",
                replace_existing=True
            )
            self.logger.info(f"已添加报告生成任务, 生成间隔: {report_interval}秒")

        self.scheduler.start()
        self.running = True
        self.logger.info("网站健康检测调度器已成功启动")

        for site in sites:
            self._check_site(site)

    def stop(self) -> None:
        """
        停止调度器
        """
        if not self.running:
            return

        self.logger.info("正在停止网站健康检测调度器...")
        try:
            self.scheduler.shutdown()
        except Exception as e:
            self.logger.warning(f"关闭调度器时发生异常: {e}")
        try:
            self.http_checker.close()
        except Exception as e:
            self.logger.warning(f"关闭HTTP检测器时发生异常: {e}")
        self.running = False
        self.logger.info("网站健康检测调度器已停止")

    def run_once(self) -> None:
        """
        执行一次所有站点的检测
        """
        self.logger.info("开始执行一次所有站点的检测")

        sites = self.config.get_sites()
        for site in sites:
            self._check_site(site)

        self.logger.info("所有站点检测完成")

    def wait(self) -> None:
        """
        保持程序运行
        """
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            self.logger.info("收到停止信号")
            self.stop()
