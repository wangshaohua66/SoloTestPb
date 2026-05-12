"""
调度器模块。

提供定时生成报表和邮件发送功能。
"""

import smtplib
import time
from email import encoders
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from typing import Any, Callable, Dict, List, Optional

import schedule


class ReportScheduler:
    """
    报表调度器类。

    提供定时执行报表生成和邮件发送的功能。
    """

    def __init__(self):
        """
        初始化报表调度器。
        """
        self.jobs = []
        self._running = False

    def add_daily_job(
        self,
        time_str: str,
        job_func: Callable,
        *args,
        **kwargs,
    ) -> schedule.Job:
        """
        添加每日定时任务。

        Args:
            time_str: 执行时间，格式为'HH:MM'。
            job_func: 要执行的函数。
            *args: 传递给函数的位置参数。
            **kwargs: 传递给函数的关键字参数。

        Returns:
            schedule.Job对象。
        """
        job = schedule.every().day.at(time_str).do(job_func, *args, **kwargs)
        self.jobs.append(job)
        return job

    def add_hourly_job(
        self,
        interval: int = 1,
        job_func: Callable = None,
        *args,
        **kwargs,
    ) -> schedule.Job:
        """
        添加每小时定时任务。

        Args:
            interval: 间隔小时数，默认为1。
            job_func: 要执行的函数。
            *args: 传递给函数的位置参数。
            **kwargs: 传递给函数的关键字参数。

        Returns:
            schedule.Job对象。
        """
        job = schedule.every(interval).hours.do(job_func, *args, **kwargs)
        self.jobs.append(job)
        return job

    def add_weekly_job(
        self,
        day: str,
        time_str: str,
        job_func: Callable,
        *args,
        **kwargs,
    ) -> schedule.Job:
        """
        添加每周定时任务。

        Args:
            day: 执行日期，如'monday'、'tuesday'等。
            time_str: 执行时间，格式为'HH:MM'。
            job_func: 要执行的函数。
            *args: 传递给函数的位置参数。
            **kwargs: 传递给函数的关键字参数。

        Returns:
            schedule.Job对象。
        """
        days = {
            "monday": schedule.every().monday,
            "tuesday": schedule.every().tuesday,
            "wednesday": schedule.every().wednesday,
            "thursday": schedule.every().thursday,
            "friday": schedule.every().friday,
            "saturday": schedule.every().saturday,
            "sunday": schedule.every().sunday,
        }

        if day.lower() not in days:
            raise ValueError(f"无效的日期: {day}，有效日期为: {', '.join(days.keys())}")

        job = days[day.lower()].at(time_str).do(job_func, *args, **kwargs)
        self.jobs.append(job)
        return job

    def add_interval_job(
        self,
        minutes: int,
        job_func: Callable,
        *args,
        **kwargs,
    ) -> schedule.Job:
        """
        添加间隔分钟定时任务。

        Args:
            minutes: 间隔分钟数。
            job_func: 要执行的函数。
            *args: 传递给函数的位置参数。
            **kwargs: 传递给函数的关键字参数。

        Returns:
            schedule.Job对象。
        """
        job = schedule.every(minutes).minutes.do(job_func, *args, **kwargs)
        self.jobs.append(job)
        return job

    def clear_all_jobs(self):
        """
        清除所有定时任务。
        """
        schedule.clear()
        self.jobs = []

    def run_pending(self):
        """
        运行所有待执行的任务。
        """
        schedule.run_pending()

    def start(self, check_interval: int = 1):
        """
        启动调度器。

        Args:
            check_interval: 检查间隔（秒），默认为1秒。
        """
        self._running = True
        while self._running:
            schedule.run_pending()
            time.sleep(check_interval)

    def stop(self):
        """
        停止调度器。
        """
        self._running = False

    def send_email(
        self,
        smtp_host: str,
        smtp_port: int,
        sender: str,
        password: str,
        recipients: List[str],
        subject: str,
        body: str,
        attachments: Optional[List[str]] = None,
        use_ssl: bool = True,
    ) -> bool:
        """
        发送电子邮件。

        Args:
            smtp_host: SMTP服务器地址。
            smtp_port: SMTP服务器端口。
            sender: 发件人邮箱。
            password: 邮箱密码或授权码。
            recipients: 收件人邮箱列表。
            subject: 邮件主题。
            body: 邮件正文。
            attachments: 附件文件路径列表，默认为None。
            use_ssl: 是否使用SSL加密，默认为True。

        Returns:
            发送成功返回True，失败返回False。

        Raises:
            ValueError: 邮件发送失败时抛出。
        """
        try:
            msg = MIMEMultipart()
            msg["From"] = sender
            msg["To"] = ", ".join(recipients)
            msg["Subject"] = subject

            msg.attach(MIMEText(body, "plain", "utf-8"))

            if attachments:
                for attachment_path in attachments:
                    with open(attachment_path, "rb") as attachment:
                        part = MIMEBase("application", "octet-stream")
                        part.set_payload(attachment.read())

                    encoders.encode_base64(part)
                    filename = attachment_path.split("/")[-1].split("\\")[-1]
                    part.add_header(
                        "Content-Disposition",
                        f"attachment; filename= {filename}",
                    )
                    msg.attach(part)

            if use_ssl:
                server = smtplib.SMTP_SSL(smtp_host, smtp_port)
            else:
                server = smtplib.SMTP(smtp_host, smtp_port)

            server.login(sender, password)
            server.sendmail(sender, recipients, msg.as_string())
            server.quit()

            return True
        except Exception as e:
            raise ValueError(f"邮件发送失败: {str(e)}")

    def send_report_email(
        self,
        email_config: Dict[str, Any],
        report_path: str,
        report_name: str,
    ) -> bool:
        """
        发送报表邮件。

        Args:
            email_config: 邮件配置字典，包含smtp_host、smtp_port、sender、password、recipients等。
            report_path: 报表文件路径。
            report_name: 报表名称。

        Returns:
            发送成功返回True，失败返回False。
        """
        subject = f"报表: {report_name}"
        body = f"您好，\n\n附件是{report_name}，请查收。\n\n此邮件由系统自动发送，请勿回复。"

        return self.send_email(
            smtp_host=email_config["smtp_host"],
            smtp_port=email_config["smtp_port"],
            sender=email_config["sender"],
            password=email_config["password"],
            recipients=email_config["recipients"],
            subject=subject,
            body=body,
            attachments=[report_path],
            use_ssl=email_config.get("use_ssl", True),
        )
